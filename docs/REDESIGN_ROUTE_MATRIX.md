# ECDSA_PHASE4D_REDESIGN_ROUTE_MATRIX

**Phase 4D · Stage C.** Bridge-feasibility matrix for three engine-redesign routes from ecdsa.fail HEAD
(`1302q / 1.46M Toffoli / score 1,899,562,014`) toward a layout where GCD operands are not co-resident with the
transcript at the peak. **Analysis only — no implementation, no score claim.** All forward-looking quantities
are HYPOTHESIS.

## Framing constraint (from Stage B)
`score = Toffoli × qubits`. **ecdsa.fail already has the low Toffoli (1.46M); the peak (1302) is the problem.**
TrailMix has the low peak (1169) but **higher Toffoli (2.09M) → worse score (2.44e9).** So a viable route must
**preserve ecdsa.fail's ~1.46M Toffoli AND lower the peak** — purely importing Schrottenloher does not.

## Route R1 — full Schrottenloher pack/apply_bv port
| field | assessment |
|---|---|
| mechanism | replace the Kaliski raw_quotient/ipmul engine with TrailMix's `gcd_pack` (operand-shrink → garbage tape) + `apply_bv` (Bezout reconstruction, peak there) |
| files touched | ~all of `rounds/dialog/*` + new `gcd_pack`/`apply_bv`/`gcd_compress5` modules + `arith` glue; effectively a new engine (~3–5k LOC) |
| expected peak | ~1169–1191q class (apply_bv-bound) — **HYPOTHESIS** (TrailMix numbers; not re-measured for ecdsa.fail's harness) |
| **Toffoli risk** | **HIGH — likely WORSE score.** TrailMix's own config is ~2.09M Toffoli (×1169 = 2.44e9 > baseline). The 258-iter Kaliski → ~400-iter Schrottenloher + apply_bv reconstruction *raises* Toffoli. |
| proof obligations | full circuit correctness on 9024 shots; prove-zero on all frees; transcript (garbage) reconstruction exact |
| op-count-invariant? | **IMPOSSIBLE** — entirely new op stream |
| Wall-2 / nonce | full reseed; needs a fresh island hunt (the research lead-gated) on top of an unproven score |
| impl size | **XL (full engine)** |
| stop criteria | stop on first measured score ≥ baseline (very likely given the Toffoli profile) |
| **verdict** | **NOT RECOMMENDED** — low-EV for the score goal; imports the wrong axis. Keep only as a long-horizon reference. |

## Route R2 — hybrid Kaliski-pack / apply split (the real target)
| field | assessment |
|---|---|
| mechanism | **keep ecdsa.fail's Kaliski-K2 GCD math (low Toffoli)** but restructure the tobitvector so the forward walk (a) shrinks operands and **recycles freed operand bits into the transcript** (TrailMix register-sharing, *designed in* rather than the failed local R1 lever), and (b) defers the transcript-heavy work to a **separate apply phase where the operands are already freed** — removing the 1302 transcript+operand co-residency |
| files touched | `rounds/dialog/compressed.rs` (tobitvector lifecycle, composite scratch, compress/decompress), `rounds/dialog/mod.rs` (raw_quotient/ipmul drivers), `dialog_gcd_classical_filter.rs` (width/lifetime model); **deep but within the existing engine** |
| expected peak | ≤1301 (target), ideally lower if the apply phase peak (operands freed) < 1302 — **HYPOTHESIS**; the win is removing operands (≈512q of u/tmp + the scratch deficit) from co-residency with the 645-bit transcript at the widest step |
| **Toffoli risk** | **MEDIUM** — keeps the Kaliski iteration count (258) and adders, so Toffoli ≈ baseline; the recycle/split adds bookkeeping ops (measured-uncompute on recycled lanes, possible re-pack) that must stay under the per-qubit ceiling (~1121 Toffoli/shot per peak qubit) |
| proof obligations | **prove-zero** (recycled operand lane `\|0>` across transcript window) · **ancilla clean** · **transcript reconstruction** (the inverse pass must decode bit-identically after the layout change) · **peak ≤1301** |
| op-count-invariant? | **IMPOSSIBLE in general** (the lifecycle reorder changes ops) — Wall-2-exposed. A *partial* op-count-invariant relabel was already refuted (R1/S1); the full reorder is the only remaining form. |
| Wall-2 / nonce | op-stream-changing → reseed → bounded the research lead-approved nonce confirmation required if it fails only as an island miss (never blind) |
| impl size | **L (large, but within the engine)** — the riskiest single assumption is that the Kaliski walk *can* free operand bits early enough to matter at steps 9–10 (S1-A showed operands are full-width there — so the recycle must come from a *restructured* walk, not the current one). **This is the open feasibility question R3 must answer.** |
| stop criteria | stop if R3 (toy slice) shows the split does NOT lower the toy peak, or transcript reconstruction fails, or Toffoli net ≥ baseline |
| **verdict** | **RECOMMENDED TARGET — but gate it behind R3.** Do not start R2 at 256-bit until the toy slice proves the lifecycle. |

## Route R3 — minimal vertical slice / toy-width proof (the smallest first step)
| field | assessment |
|---|---|
| mechanism | a **standalone, isolated** toy-width (n=16→32→64) module implementing the pack/apply lifecycle: a Kaliski-style GCD whose forward walk recycles shrunk-operand bits into the transcript, then a **separate apply phase** reconstructs from the transcript — measured against a toy version of the **current co-resident** dialog as baseline |
| files touched | **NONE in the live point-add** — a new isolated module + a test harness (a small circuit-builder module or even a classical accounting model first); does not touch `emit_dialog_gcd_raw_pa` |
| expected peak | proves whether the **split lowers the toy peak** (operands freed before transcript) vs the co-resident baseline at the same toy width |
| Toffoli risk | N/A at toy scale (this is a *mechanism* proof, not a score run) |
| proof obligations | (a) toy GCD computes the correct inverse; (b) **transcript reconstruction** exact (apply reproduces); (c) **peak(split) < peak(co-resident)** at toy width |
| op-count-invariant? | N/A (isolated proof) |
| Wall-2 / nonce | N/A (no Fiat-Shamir harness involved) |
| impl size | **S (smallest)** — start with a **classical peak-accounting model** (register-lifetime simulation, no reversible code), then a reversible toy circuit only if the accounting passes |
| stop criteria | stop (→ NO_VIABLE_ENGINE_ROUTE for the hybrid) if even the toy split cannot beat the toy co-resident peak with correct reconstruction |
| **verdict** | **RECOMMENDED FIRST PROTOTYPE** — cheapest decisive test of the R2 premise before any 256-bit commitment. |

## Summary
| route | peak | Toffoli | score effect | size | recommendation |
|---|---|---|---|---|---|
| R1 full port | ~1169–1191 (HYP) | ~2.09M (worse) | **likely worse** | XL | not recommended |
| R2 hybrid split | ≤1301 target (HYP) | ≈baseline (HYP) | **potential win** | L | target, gated by R3 |
| **R3 toy slice** | proves mechanism | — | enables R2 decision | **S** | **start here** |

**Routing:** do **not** start R1 or R2. Build the **R3 vertical slice** (`ECDSA_PHASE4D_VERTICAL_SLICE_PLAN.md`)
to prove the operand-free-before-transcript lifecycle lowers the peak at toy width with exact reconstruction.
Only if R3 passes does R2 become worth its large cost. **the research lead approval required before coding R3.**
