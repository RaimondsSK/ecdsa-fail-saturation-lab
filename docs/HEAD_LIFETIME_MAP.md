# ECDSA_PHASE4_HEAD_LIFETIME_MAP

**Phase 4A · Workstream 2.** Current-record (HEAD `013f1f7`) active-qubit lifetime map. Derived from the
in-tree `TRACE_PHASE_ACTIVE` / `TRACE_PEAK` replay (`proof/phase3/laneB_trace_raw.txt`,
`laneB_peak_trace.tsv`). **Diagnostic only** — no edits. This is the instrument that routes Phase 4 to the
architecture path.

## 1. Active-qubit profile by phase (max active_q, descending)
| active_q | phase | role | q below peak |
|---:|---|---|---:|
| **1302** | `…tobitvector_shift` | GCD compressed-block shift (widest step) | 0 (PEAK) |
| **1302** | `…tobitvector_compress_block` | write the per-step transcript cell | 0 (PEAK) |
| **1302** | `…tobitvector_reverse_add` | inverse-direction materialized add | 0 (PEAK) |
| 1297 | `apply_chunk_{add,sub}_final_ripple` | chunked materialized add carry ripple | 5 |
| 1285 | `round84_fused_square_xtail_add_double_ox` | λ²→Rx finishing add | 17 |
| 1285 | `dialog_gcd_raw_pa_x_restore` | restore tx ← Rx | 17 |
| 1284 | `round84_inplace_solinas_square_{forward,inverse}` | the schoolbook square (λ²) | 18 |
| 1283 | `dialog_reroll`, `raw_pa_y_output`, `raw_pa_c_ox_minus_rx` | reseed tail / finishing subs | 19 |
| 1281 | `…quotient_tobitvector`, `…ipmul_tobitvector` | the two GCD inversion drivers | 21 |
| 1266 | `apply_chunk_{add,sub}_boundary_clear` | chunked-f boundary clear | 36 |
| 1264 | `apply_chunk_{add,sub}_ripple` | chunked-f ripple | 38 |
| 1164 | `materialized_special_chunked_raw_sum/diff` | the active gated-modular add (Lane C) | 138 |

Full ordered per-region trace: `proof/phase3/laneB_peak_trace.tsv` (787 near-peak rows). The active count
**climbs monotonically `1281→1286→1291→…→1302`** as the `compressed_log` transcript fills across GCD steps,
then holds 1302 continuously through the widest-step tobitvector compute→materialize→uncompute cycle.

## 2. Peak co-residency groups (what is live at 1302q)
At the widest GCD steps the simultaneously-live set is the **resident GCD working state + body scratch**
(Lane B; developer note `compressed.rs:304–342`):
| group | size (approx) | live across the 1302 plateau? | freeable early? |
|---|---|---|---|
| `tx` (target x) | 256 | yes | no — operand of every sub-phase |
| `ty` (target y) | 256 | yes | no — operand |
| `u` / `v` active lanes | ≤256 | yes | no — GCD state |
| **`compressed_log` (transcript)** | grows to ~peak-binding | **yes — the object that pushes active to 1302** | **architectural only (this is the target)** |
| `raw_block` (decompressed current block) | ~step width | yes | no — being operated on |
| `DialogGcdCompositeScratch` (`2·active_width−1`) | the *deficit* lanes | yes | already minimized by all borrows |

## 3. Earliest-free candidates
**None cheap remain.** The only idle-`|0>` cells the design exposes — current-block compressed cells, the
step's `s2`, future-log carries, high `u/v` lanes — are **already folded into the composite scratch** (all
`BORROW_*` / `LATE_BORROW_*` flags ON, Lane B). Phase 1 proved `BORROW_CURRENT_S2` reaches only the `shift`
consumer, not `compress_block`/`reverse_add`. No single cell is provably `|0>` across all 1302 sub-phases.
- **Architectural earliest-free candidates (Workstream 3, not cheap):** (a) retire/shrink `compressed_log`
  slices sooner (the transcript is the GCD's correctness record — retiming it is delicate); (b) `raw_block`
  lifetime; (c) K2-pair-compression restructure.

## 4. Qubits surviving longer than necessary
The diagnostic found **no resident surviving "longer than necessary" in the cheap sense** — every resident is
an operand of the phase that holds the peak. The `compressed_log` is the only object whose *per-step
necessity* is questionable: each step's transcript cell is `|0>` for that block's duration (the borrow already
exploits this within a block), but the **cumulative** transcript across steps is what grows active to 1302.
Reducing the *cumulative* footprint = a transcript-encoding redesign, not an early-free.

## 5. Routing verdict (the sprint plan's decision rule)
> local freeing candidates → micro-prototypes · 1302 binder globally coupled → architecture redesign only.

**The 1302 binder is globally coupled.** No local earliest-free candidate exists; the peak is held by the
resident GCD state + the cumulative `compressed_log` across the entire widest-step tobitvector lifecycle.
→ **route to architecture redesign** (`ECDSA_PHASE4_COMPRESSED_LOG_REDESIGN_SKETCH.md`). This map is the
grounding for that routing and the baseline against which any redesign prototype is measured.
