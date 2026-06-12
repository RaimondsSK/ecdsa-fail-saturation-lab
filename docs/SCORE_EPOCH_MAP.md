# ECDSA_PHASE4_SCORE_EPOCH_MAP

**Phase 4A · Workstream 1.** Algorithmic epochs of the ecdsa.fail frontier — the architectural eras, what
binds each, and the boundary that opens the next. `score = avg(Toffoli/shot) × peak_qubits`, lower better.
No score claim; numbers are validated runs / cited frontier points.

## Epoch timeline
| epoch | representative | avg Toffoli | qubits | score | what bound it | boundary that ended it |
|---|---|---|---|---|---|---|
| **E0 — textbook (2715q)** | `fa473ea` | 3,942,753 | 2715 | 1.07×10¹⁰ | naive double-and-add + full-width inversion | switch to Kaliski/dialog GCD inversion + comparator tuning |
| **E1 — comparator/iteration (1309q)** | `83e3b66`→`436b516`→`a66b042`→`lowq0` | ~1.50M | 1309 | ~1.96–1.97×10⁹ | the 1309q peak; gains came from `APPLY_CLEAN_COMPARE_BITS` width + `ACTIVE_ITERATIONS` + nonce islands | a coupled **peak break to 1302q** (landed in `013f1f7`) |
| **E2 — compressed/binder (1302q) — CURRENT** | `013f1f7` (ea8a7716) | 1,458,957 | 1302 | **1,899,562,014** | the **compressed_log + composite-scratch deficit** at the widest GCD steps (Phase 3 Lane B) | **open** — requires breaking the compressed_log/GCD register layout |
| **E3 — compressed_log / GCD-layout (target)** | *(none yet)* | ? | <1302 target | <1,899,562,014 | — | Phase 4 objective |

## Epoch-boundary mechanics
- **E0→E1:** algorithm replacement (textbook → Kaliski binary almost-inverse / dialog GCD) + peak collapse
  2715→1309. A *register-layout* era change, not a knob. ~5.5× score drop.
- **E1→E2:** the largest single jump on record — **1309→1302 peak AND a Toffoli drop simultaneously**
  (`ea8a7716`). Per Phase 3 this is a coupled change to the compressed-block tobitvector layout, not a
  separable lever. ~3.5% score drop. **We inherited it for free.**
- **E2→E3 (the open frontier):** every *local* lever inside E2 is exhausted (Phase 3 A–E). The next boundary
  is again a **register-layout era change** — shrink/retire the `compressed_log` transcript or restructure the
  GCD operand co-residency so fewer registers are live at the widest step. This is the E0→E1 / E1→E2 pattern
  repeating: **frontier jumps have always been register-layout era changes, never knob loops.**

## Quantified targets for E3 (what "below 1,899,562,014" requires)
Using `d(score) = qubits·dToffoli + Toffoli·dqubits`:
| lever | unit | score delta | note |
|---|---|---|---|
| −1 peak qubit (1302→1301), Toffoli flat | −1 q | **−1,458,957** (−0.077%) | Lane B: no cheap path; needs layout redesign |
| −1% avg Toffoli (−14,590), peak flat | −14,590 T | **−19.0M** (−1.0%) | needs a real Toffoli surface; Phase 3 found none local |
| TrailMix-class layout (e.g. peak 1169q) | −133 q | up to **−194M** if Toffoli held | full engine replacement (Workstream 3) |

## Reading the map for Phase 4
The score is **peak-dominated within an epoch** (−1q ≈ −1.46M) but **epoch jumps come from layout changes
that move both axes at once**. Chasing −1q or −1% Toffoli *inside* E2 is what Phase 3 exhausted. **E3 must be
entered by a layout change**, exactly as E0→E1 and E1→E2 were. Reference existence proof that a lower-peak
layout exists: TrailMix's jump-lowqubit at **1169q** (peak = `apply_bv`, not the GCD transcript) — see
`ECDSA_PHASE4_TRAILMIX_LAYOUT_DIFF.md`.
