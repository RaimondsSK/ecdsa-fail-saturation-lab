# ECDSA_PHASE4D_CURRENT_ENGINE_ANATOMY

**Phase 4D · Stage A.** Anatomy of the ecdsa.fail HEAD `013f1f7` point-add engine, with the lifecycles that
produce the 1302q peak. Grounded in source + Phase 3/4 traces (`laneB_*`, `laneC_*`, `ph4_r1_*`, `ph4_s1_*`).
**Diagnostic/analysis only.** No score, no benchmark.

## 1. Top-level structure (`emit_dialog_gcd_raw_pa`, COSTMAP §1)
```
build_builder() (mod.rs:1375) → configure_ecdsafail_submission_route() → declare tx,ty,ox,oy (256 each)
  mod_sub_qb(tx,ox,p); mod_sub_qb(ty,oy,p)                       # translate by −Q
  emit_dialog_gcd_raw_pa(tx,ty,ox,oy,p)  (rounds/dialog/mod.rs:1768):
    pair1_quotient = emit_dialog_gcd_raw_quotient(tx,ty,p)       # 1st Kaliski inversion (λ = dy/dx)  ← PEAK lives here
    round84_emit_fused_square_xtail(...)                         # λ², Solinas mod p; writes Rx
    c_ox_minus_rx                                                # tx ← Qx − Rx
    pair2_product  = emit_dialog_gcd_raw_ipmul(tx,ty,p)          # 2nd Kaliski inversion (uncompute λ)
    y_output; x_restore
  optional DIALOG_TAIL_NONCE identity tail                       # Fiat-Shamir island selector (0 Toffoli)
```

## 2. The GCD inversion (`emit_dialog_gcd_raw_quotient`, mod.rs:1654)
Kaliski binary almost-inverse with K2 (jump depth-2). Allocates its **own** working registers:
`u = alloc_qubits(N=256)` (mod.rs:1664), `tmp = alloc_qubits(N)` (mod.rs:1743) — **not aliased to tx/ty**. The
inner walk is the **tobitvector** lifecycle:
- forward: `emit_dialog_gcd_compressed_sidecar_tobitvector_steps_block_lifecycle` (compressed.rs:674) — runs
  `active_iterations=258` steps; each step: `branch_bits → cswap → subtract → shift (+K2 2nd shift)` then
  **`compress_block`** writes the step's transcript symbol into `compressed_log`.
- reverse: `…_reverse_block_lifecycle` (compressed.rs:848) — **`decompress`** reads the transcript back, then
  `reverse_add`.

## 3. The four lifecycles that co-reside at the peak

### (a) compressed_log (the transcript) — `compressed_sidecar_bits = blocks × block_bits`
- **size at HEAD: 645 qubits** (measured, `ph4_s1_decomp`). Allocated up front for the whole inversion.
- **write:** `compress_block` after each forward step (one symbol/step).
- **read:** `decompress` before each reverse step (inverse pass), and as the **future-log borrow source**
  (its *unwritten* tail is reused as body scratch — `RAW_TOBITVECTOR_BORROW_FUTURE_LOG_CARRIES=1`).
- **lifetime:** the whole inversion (write forward → read reverse). **This is the object that climbs active
  1281→1302 as it fills** (Lane B).

### (b) raw_block — `2 × sidecar_group_size` (measured **6q** at HEAD)
- the decompressed current block (`b0`, `b0_and_b1`, `s2` slots) operated on per step; per-block lifetime.

### (c) composite scratch — `want ≈ 2·active_width − 1` (`dialog_gcd_build_composite_scratch`, compressed.rs:349)
- the body add/sub clean-lane demand (carries `n−1` + gated-host `n`). At step 9 (aw=256): **want=509**.
- filled by a borrow ladder (all flags ON): runway-safe future-log prefix + current-block cells +
  `u/v[active_width..]` (=0 at aw=256) + `s2`; the remainder is **fresh `owned`** = `alloc_qubits(want−borrowed)`.
- **at step 9: borrowed=386, owned deficit=123** (the only freshly-additive scratch).

### (d) active_width schedule (`active_width(step)`, classical_filter.rs:123)
- `≈ N − step·1.015 + 10`, clamped `[1,256]` (`WIDTH_SLOPE_X1000=1015`, `WIDTH_MARGIN=10`, `VARIABLE_WIDTH=1`).
- **operands stay full-width (256) for steps 0–~10, then shrink.** `WIDTH_MARGIN=10` is load-bearing — it keeps
  `active_width ≥ bitlen(u|v)` (S1-A test: trimming it breaks correctness via `WidthOverflow`).

## 4. Where the 1302 peak happens (measured)
- **Steps 9–10 of the FIRST GCD inversion (`pair1_quotient`)**, in the `tobitvector` compress_block/shift/
  reverse_add phases at `active_width=256` (`laneB_peak_trace.tsv`, `ph4_r1_donor_map.tsv`).
- decomposition at step 9 (active=1302): residents (tx,ty,ox,oy + GCD u,tmp) + **compressed_log 645** +
  raw_block 6 + composite-scratch **owned 123** (borrowed 386 reused). The peak tips 1301→1302 because the
  runway-safe borrow pool drops by exactly 1 at step 9.

## 5. The structural root cause (why local levers all failed)
**The GCD operands, the growing transcript, and the body scratch are all live simultaneously at the widest
early steps.** The forward tobitvector *computes the GCD AND writes the transcript in the same phase, with full
operands resident.* Phase 3/4 proved every local escape closed:
| lever | result | doc |
|---|---|---|
| u/v high-lane donor → transcript (R1) | freed_uv=0 at the peak | `…R1_DONOR_MAP` |
| smarter borrow at peak (S1-B) | borrow headroom=0 | `…S1_EARLY_SCRATCH_DEFICIT_MAP` |
| narrow active_width early (S1-A) | breaks correctness (WidthOverflow) | `…S1A_CONVERGENCE_PRETEST` |

## 6. Files / functions per phase (for the redesign bridge)
| phase | file:fn |
|---|---|
| top build | `rounds/dialog/mod.rs:1375 build_builder`, `:1768 emit_dialog_gcd_raw_pa` |
| GCD inversion | `rounds/dialog/mod.rs:1654 emit_dialog_gcd_raw_quotient`, ipmul counterpart |
| tobitvector forward/reverse | `rounds/dialog/compressed.rs:674 / :848 block_lifecycle` |
| compress/decompress | `compressed.rs` `compress_block` / `decompress` phases |
| composite scratch | `compressed.rs:349 dialog_gcd_build_composite_scratch` |
| future-log borrow | `compressed.rs:573 future_carry_slice`, `:280 runway_safe_future_prefix` |
| active_width / truncated step | `dialog_gcd_classical_filter.rs:123 active_width`, `:251 truncated_gcd_step` |
| adders / square | `arith/{adder,modular,multiply}.rs`, `venting.rs` |

**The redesign target (Stage C):** break the **forward-walk co-residency** — free the GCD operands before the
transcript-heavy work, the way TrailMix's pack→apply_bv split does (`ECDSA_PHASE4D_TRAILMIX_ENGINE_ANATOMY.md`).
