# ECDSA_PHASE4D_R3A_APPLY_REGISTER_REUSE_ANALYSIS

**Phase 4D · R3a follow-up.** Resolve the dominant R3a assumption: can ecdsa.fail's Kaliski
`raw_quotient`→`raw_ipmul` flow be reorganized into a pack/apply lifecycle where (1) operands `u/tmp` are freed
before the apply peak, (2) apply reconstructs into existing `tx/ty`, (3) no fresh 2n Bezout register, (4)
transcript reconstruction stays exact? **Structural source analysis only** — no patch, no prototype, no
benchmark, no score, no nonce/GPU. Main untouched (`013f1f7`).

## VERDICT: **ECDSA_PHASE4D_APPLY_REUSE_NOT_PLAUSIBLE**

**All four properties already exist at HEAD** — the apply-register-reuse R3a's optimistic framing hoped to
introduce is **already ecdsa.fail's live structure**. And it **does not lower the 1302 peak**, because the peak
is the GCD **walk** (operands + transcript-write + scratch, co-resident at the widest early steps), **not** the
apply phase. R3a's "split" was modeling a transition ecdsa.fail has *already made*; the genuine peak (the walk)
is exactly what R1/S1 already proved irreducible. **No R3b; the apply-reuse engine route is closed.**

## Stage A — Current Kaliski flow and register ownership (HEAD `013f1f7`)
Live path (`COMPRESSED_SIDECAR_LOG=1`, `RAW_QUOTIENT_TERMINAL_REUSE=1`):
`emit_dialog_gcd_raw_pa` (mod.rs:1768) → `emit_dialog_gcd_raw_quotient` (mod.rs:1654, routes to) →
`emit_dialog_gcd_compressed_sidecar_quotient_block_lifecycle` (compressed.rs:1695). Sequence:
```
alloc compressed_log(645) + raw_block + u(256)              # u = the GCD operand register (NOT tx/ty)
load u = p
[PHASE: …_quotient_tobitvector]  forward walk:              # writes transcript into compressed_log
    emit_…_tobitvector_steps_block_lifecycle(u, factor=tx, replay_log, raw_block)   ← 1302 PEAK (Lane B)
terminal_reuse branch (ACTIVE):
    release_terminal_u(u)                                    # (1) FREES u  BEFORE the apply  ✅
    apply_bitvector_reverse_exact(replay_log, factor=tx, target=ty, p, raw_block)    # (2) reconstructs INTO target=ty ✅ (3) no fresh 2n Bezout ✅
    swap(target, factor)                                     # move the quotient into place
    reacquire_terminal_u(u)                                  # u needed AGAIN for the uncompute
    [PHASE: …_uncompute_tobitvector] reverse walk(u, factor) # uncompute the forward walk  ← also 1302
    unload p; free u, compressed_log
```
- **Where `u` allocated:** compressed.rs:1710 (`alloc_qubits(N)`), loaded to `p`. `tmp` is the non-compressed
  path's analogue (mod.rs:1743) — not used on the live compressed path; the live path reuses `factor`/`u`.
- **Where `tx/ty` live:** `tx=factor`, `ty=target` are the point coords, live throughout; **the apply writes
  the inverse/quotient into `target=ty`** (an EXISTING register).
- **Is `u` read after the transcript is sufficient?** Yes — `u` is **freed during the apply** (transcript
  suffices for reconstruction) but **reacquired for the reverse-walk uncompute** (to return `u`/`factor`/
  `compressed_log` to `|0>` cleanly).
- **Can `tx/ty` serve as the apply output?** **They already do** — `apply_bitvector_reverse` reconstructs into
  `target=ty`.

**Conclusion (Stage A):** properties (1)(2)(3)(4) are **already realized** at HEAD. R3a's "co-resident" baseline
does not describe ecdsa.fail; ecdsa.fail is **already the split** (forward walk → operand-freed apply →
reverse walk).

## Stage B — TrailMix apply-register reuse pattern
`gcd_pack` (Alg 2) → `bezout_unpack`/`apply_bv` (Alg 3):
- `apply_bv` "runs linear modular updates on `(r,s)` seeded at `(y,0)` … ends at `(0, y·x⁻¹)`" — reconstructs
  **into the existing point registers `x2,y2`** (peak = `670 tape + 257 x2 + 257 y2 ≈ 1191`,
  `schrottenloher_status.md`). **No fresh 2n Bezout register** — same reuse pattern ecdsa.fail already uses.
- **operands freed:** `gcd_pack`'s `u/v` shrink during the forward walk and their freed bits feed the garbage
  tape (register-sharing); by `apply_bv` the operands are gone.
- **Where the peak lives:** `apply_bv` (transcript-heavy, operands freed). **The walk (`gcd_pack`) is BELOW the
  peak.**

**The decisive difference (NOT the apply reuse):** in TrailMix the **walk is cheap** (operand-shrink recycling,
~400 Schrottenloher iters, GCD has full ancilla headroom because the peak is elsewhere) and the **peak is the
apply**. In ecdsa.fail the **walk is the peak** (operands full-width at the early steps + growing transcript +
the `2·aw−1` scratch deficit) and the **apply is below it**. Both reuse existing registers for the apply — that
is **not** where the 111-qubit gap comes from.

## Stage C — feasibility verdict
**NOT_PLAUSIBLE** that introducing/strengthening apply-register-reuse lowers ecdsa.fail's peak:

| R2 property | ecdsa.fail HEAD status |
|---|---|
| operands freed before apply | **already done** (`release_terminal_u`) |
| apply into existing `tx/ty` | **already done** (`apply_bitvector_reverse` → `target=ty`) |
| no fresh 2n Bezout register | **already true** |
| transcript reconstruction exact | **already true** (validated 0/0/0; R3a confirmed the math) |

**Exact source-level obstacle:** the **1302 peak is the forward/reverse tobitvector WALK**
(`…compressed_block_tobitvector_shift/compress_block/reverse_add`, Lane B), **not the apply**. The apply
(`apply_bitvector_reverse`, `u` freed) is already below peak (Lane B apply phases ≤1297; `materialized_special`
1164). The walks **bracket** the apply (forward before, reverse after) and **both need `u`** — so freeing `u`
for the apply cannot lower the global peak. The walk peak is `operands(u+factor) + transcript-being-written +
2·aw−1 scratch`, which **R1 (donor=0), S1-B (borrow headroom=0), S1-A (width-trim breaks correctness)** already
proved irreducible.
- **registers freed before apply:** `u` (then reacquired). **receiving existing register:** `ty` (`target`).
  **required transcript fields:** the per-step branch symbols in `compressed_log` (already sufficient — R3a
  proved transcript-only reconstruction exact).
- **op-stream-changing rewrite?** Moot — there is nothing to rewrite (the structure exists); any attempt to
  *further* free operands would target the **walk**, where operands are inherently required to compute the GCD.
- **still Kaliski low-Toffoli, or drifts to Schrottenloher?** To make the *walk* cheap (TrailMix's actual
  mechanism) requires the operand-shrink-recycling Schrottenloher walk (~400 iters) → **drifts to the full
  Schrottenloher engine → higher Toffoli (2.09M) → worse score** (Stage B of the scout). It does **not** stay
  Kaliski-low-Toffoli.

## Stage D — R3b decision: **NO R3b**
The apply-register-reuse is **already present and is not the lever**; a reversible toy would only re-confirm
what the source shows — ecdsa.fail already frees operands before an existing-register apply, and the peak is the
walk. **Do not build R3b.** The R3a "optimistic framing" is **resolved against itself**: its premise (apply
reuses existing registers) is *true at HEAD*, yet the peak is unaffected, because the peak is the walk — which
R1/S1 closed.

**Engine-route status:** the apply-reuse / pack-apply-split hybrid (R2) route is **archived** — it cannot lower
the 1302 peak because that peak is the GCD walk, not the apply, and the walk is operand+transcript+scratch-bound
(R1/S1). The only layout that makes the *walk* cheap is the full Schrottenloher engine (operand-shrink walk +
apply_bv peak), which **raises Toffoli and worsens the score** (not a Kaliski-preserving hybrid). 

**Recommendation:** close the engine-redesign route as **NOT_PLAUSIBLE for a score win via
apply-reuse**. The remaining options are (a) accept saturation and **archive** ECDSA at 1,899,562,014 (a
high-confidence architectural-impossibility result for all surveyed local + hybrid levers), or (b) a
genuinely **new** research idea outside the apply-reuse / operand-recycle family (e.g. a different inversion
primitive that is simultaneously low-iteration AND low-peak — none identified in TrailMix/papers so far;
HYPOTHESIS that one exists is unsupported). This is a research-strategy decision for the maintainers.

## Compliance
source analysis only · no source optimization patch · no worktree prototype · no benchmark · no score claim ·
no nonce search · no GPU · no submission · R3b NOT started · full R2 NOT started · unproven claims
HYPOTHESIS-tagged · main branch untouched (`013f1f7`).
