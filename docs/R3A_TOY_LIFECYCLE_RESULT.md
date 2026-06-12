# ECDSA_PHASE4D_R3A_TOY_LIFECYCLE_RESULT

**Phase 4D · R3a.** Toy classical register-lifetime accounting: does a pack/apply **split** lower the peak
simultaneous-live register count vs the current **co-resident** layout, at toy widths n=16/32/64, while
reconstructing the correct modular inverse? **THIS IS AN ACCOUNTING MODEL, NOT A REVERSIBLE-CIRCUIT RESULT.**
Pure lab-side Python; no challenge source, no circuit, no benchmark, no score, no nonce/GPU.
Model: `proof/phase4d/r3a_lifecycle_model.py` · raw: `proof/phase4d/r3a_peak_accounting.tsv`.

## VERDICT: **ECDSA_PHASE4D_R3A_TOY_LIFECYCLE_INCONCLUSIVE**

The model **proves the reconstruction mechanism is exact** but **cannot decide the peak comparison** — it flips
between two framings, and the deciding assumption cannot be grounded back to ecdsa.fail's Kaliski engine at the
accounting level. Per the task's own criterion ("INCONCLUSIVE iff … assumptions can't ground back").

## What IS proven (clean, exact — not hypothesis)
**Transcript-only reconstruction works perfectly.** The Kaliski Bezout `(r,s)` recurrence depends **only on the
per-step branch case**, not on the operand values — so a separate apply phase replays the transcript to compute
the inverse with operands freed. Verified `inv == pow(v,-1,p)` for **2000/2000 samples at every width (16/32/64),
0 reconstruction failures, 0 non-invertibles**. The pack/apply split is **mathematically sound** — the apply
phase genuinely needs only the transcript, not the operands. This is the load-bearing premise of R2, and it holds.

## What is NOT decided (the peak comparison flips)
| width n | model-as-written | optimistic (grounded by TrailMix apply_bv) |
|---|---|---|
| | co_resident vs split | co_noborrow vs split_optimistic |
| 16 | 113 < **126** (split worse) | **141 > 94** (split better) |
| 32 | 212 < **241** (split worse) | **272 > 177** (split better) |
| 64 | 401 < **462** (split worse) | **525 > 334** (split better) |
| trend | split loses, gap grows | split wins, gap **scales** (47→95→191) |

Reconstruction is clean in **both** framings; only the peak flips. The two framings differ on **two assumptions
the toy accounting cannot resolve**:

1. **Apply-phase register reuse (the dominant factor).** *Model-as-written* assumes the apply phase allocates
   **new** Bezout registers `R=2n`. *Optimistic* assumes it reconstructs **into existing registers** (no new
   operand-sized allocation). **TrailMix's real `apply_bv` does the latter** — it reconstructs into the existing
   point registers `x2,y2` (`schrottenloher_status.md`: peak = `670 tape + 257 x2 + 257 y2`), allocating no fresh
   2n Bezout register. So the optimistic framing is the **TrailMix-grounded** one. **But whether ecdsa.fail's
   Kaliski `raw_quotient`/`raw_ipmul` can be re-organized to free its own `u,tmp` (mod.rs:1664/1743) and
   reconstruct into `tx,ty` is the open R2 question — NOT decidable by this accounting.**
2. **Co-resident scratch-borrow credit.** ecdsa.fail hosts body scratch in *unwritten transcript* cells
   (`future-log borrow`). *Model-as-written* fully credits this (co-resident very efficient); reality is partial
   (measured `owned` deficit = 123/509 at the peak, i.e. ~24% un-borrowed). The credit level shifts the
   co-resident peak.

**Robustness:** the flip is identical across the full HYPOTHESIS sweep (transcript density ∈ {1.6, 2.5}
bits/step; apply-scratch ∈ {0.5n, n, 3n}) — all six runs give **INCONCLUSIVE**. The model-as-written's
"split worse" is an **artifact of the new-register assumption that TrailMix's actual `apply_bv` contradicts**;
the optimistic framing's "split better, scaling" matches TrailMix's empirical 1191q < 1302q in spirit but
cannot be proven for ecdsa.fail's Kaliski here.

## Accounting table (canonical run: density 2.5, apply-scratch n; HYPOTHESIS params)
| n | co_resident_peak | split_peak | delta | transcript | operand_live | scratch_live | apply_peak | pack_peak | recon_ok | recon_fail | non-inv | samples |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 16 | 113 | 126 | −13 | 78 | 32 | 31 | 126 | 85 | 2000 | 0 | 0 | 2000 |
| 32 | 212 | 241 | −29 | 145 | 64 | 63 | 241 | 150 | 2000 | 0 | 0 | 2000 |
| 64 | 401 | 462 | −61 | 270 | 128 | 127 | 462 | 279 | 2000 | 0 | 0 | 2000 |
| *(optimistic framing)* | co_noborrow | split_opt | | | | | | | | | | |
| 16 | 141 | 94 | **+47** | | | | | | | | | |
| 32 | 272 | 177 | **+95** | | | | | | | | | |
| 64 | 525 | 334 | **+191** | | | | | | | | | |

*(This is an accounting of logical register lifetimes; it does not model the actual reversible-circuit op stream,
the per-phase scratch micro-structure, or the Fiat-Shamir layer. It is a mechanism screen, not a peak prediction.)*

## Missing assumptions to resolve (the path out of INCONCLUSIVE)
| # | unresolved assumption | how to ground it |
|---|---|---|
| 1 | Can ecdsa.fail's **Kaliski apply** reconstruct into existing registers (free `u,tmp`, write into `tx,ty`)? | **R3b reversible toy** — implement the toy split in a real reversible-circuit builder module and *measure* the apply peak with register reuse; OR a structural read of whether `raw_ipmul` can be re-seeded from the transcript without `u` |
| 2 | Apply-phase **scratch profile** (Cuccaro 3n? vented?) | read TrailMix `bezout_unpack.rs` apply scratch; or R3b measures it |
| 3 | Real **co-resident scratch-borrow** fraction at the 256-bit peak | already measured: `owned`=123/509 (≈24% un-borrowed) — feed the real fraction into a refined model |

## Route recommendation (INCONCLUSIVE → do NOT start R3b/R2 yet)
- **Reconstruction is sound** (the R2 premise holds), so the mechanism is not dead — but the **peak benefit is
  unproven and assumption-dependent**, so do **not** commit to R3b or R2 on this evidence alone.
- **Recommended next step (smallest):** resolve assumption #1 cheaply first — a **structural source analysis**
  of whether ecdsa.fail's `raw_quotient`→`raw_ipmul` can be reorganized into pack(free operands)→apply(into
  `tx,ty`), reading `bezout_unpack.rs` for the apply register-reuse pattern. Only if that says "plausible"
  should the research lead authorize the **R3b reversible toy** to *measure* the split peak. The toy accounting has done
  its job: it confirmed reconstruction and isolated the single deciding question (apply register reuse).
- **Do NOT** read this as a green light for the 256-bit R2 engine.

## Compliance
accounting model only (explicitly stated) · no challenge source edit · no `./benchmark.sh` · no score claim ·
no nonce search · no GPU · no submission · no R3b started · no full R2 256-bit started · model assumptions
HYPOTHESIS-tagged · result is an accounting result (stated) · main branch untouched (`013f1f7`).
