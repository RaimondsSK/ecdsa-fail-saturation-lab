# ECDSA_PHASE4C_S1A_CONVERGENCE_PRETEST

**Phase 4C · S1-A pre-test.** Can the early `active_width` schedule be narrowed at the binding steps (8–11)
while the truncated dialog-GCD still stays correct/convergent within ≤258 steps? **Number-theory / classical
only** — no circuit, no `./benchmark.sh`, no score, no nonce, no GPU, no prototype. Diagnostic source edit kept
in the R1 worktree and **reverted** (`git diff -- src/` = 0; bin removed). Main untouched (`013f1f7`).

## VERDICT: **ECDSA_PHASE4C_S1A_CONVERGENCE_REFUTED**

Narrowing `active_width` at the binding steps **increases the hard-input rate** (adds `WidthOverflow`
failures), and narrowing the earliest steps is catastrophic. The early width = 256 is **mathematically
required**: the GCD operands genuinely occupy ~256 bits there, so truncating the window corrupts them. S1-A is
refuted before any circuit prototype.

## Method (faithful — drives the REAL filter)
A gated `active_width` early-trim (3 cfg fields + a 4-line method change) was added to
`src/point_add/dialog_gcd_classical_filter.rs`, plus an analysis bin `src/bin/s1a_convergence.rs` that calls
the **real `check_gcd_factor`** over **400,000 deterministic factors** (splitmix64-seeded, uniform in `[1,p)`).
`check_gcd_factor` = full-width `NonConvergence` check (uses `full_gcd_step`, **schedule-independent**) + the
truncated walk (`truncated_gcd_step`, which returns `WidthOverflow` when `bitlen(u|v) > active_width(step)` —
**the schedule-dependent correctness constraint**). So narrowing `active_width` can only move `WidthOverflow`.
HEAD config replicated exactly (`compare_bits=48`, `width_margin=10`, `width_slope=1.015`,
`band_trims=[0,2,…]`, `pa9024_schedule=1`, `fastpath=1`, `k2=1`, `active_iterations=258`). Raw:
`proof/phase3/ph4_s1a_convergence_400k.tsv`.

### Factor-sample model (grounded)
Uniform random factors in `[1,p)` — the same model Lane D used. The real circuit factors are `dx = px−qx`,
`c = qx−rx (mod p)` from random EC points; x-coordinate differences are ≈uniform mod p. **Validation that the
sample is representative:** baseline `NonConvergence = 162/400k = 0.041%`, matching Lane D's measured
`P(steps>258)=0.043%` — and `NonConvergence` is identical across all schedules (schedule-independent),
confirming the harness isolates the width effect correctly.

## Results (per schedule, N=400,000)
| schedule | trim | touches 9–10 | ok | **width_overflow** | nonconvergence | comparator_mismatch | earliest WOV step |
|---|---|:--:|---:|---:|---:|---:|---:|
| **baseline_HEAD** | — | no | 399,686 | **152** | 162 | 0 | 20 |
| trim1_steps8_11 | −1 @ 8–11 | yes | 399,662 | **176** (+24) | 162 | 0 | 8 |
| trim2_steps8_11 | −2 @ 8–11 | yes | 399,585 | **253** (+101) | 162 | 0 | 8 |
| trim1_steps0_15 | −1 @ 0–15 | yes | 0 | **399,838** (100%) | 162 | 0 | 0 |
| trim2_steps0_15 | −2 @ 0–15 | yes | 0 | **399,838** (100%) | 162 | 0 | 0 |
| cap255_steps0_9 (adaptive) | −1 @ 0–9 | yes | 0 | **399,838** (100%) | 162 | 0 | 0 |

### Per-question reporting
- **max steps / over-258 / tail:** `NonConvergence` (full-width steps > 258) = **162/400k (0.041%)** for every
  schedule (schedule-independent). The full-width step tail is Lane D's: **max 268, mean 242, p99≈258,
  p999≈262** (`laneD_gcd_tail.tsv`). Narrowing `active_width` does **not** change convergence *step count* — it
  changes truncation *correctness* (`WidthOverflow`).
- **does the trim touch steps 9–10:** yes for all trimmed variants (column above).
- **estimated peak effect if used in circuit:** −1 width at steps 8–11 would lower `want=2·body−1` by ~2 →
  peak ~1300–1301 — **but only by accepting +24 hard-input factors** (per 400k) that the circuit would compute
  **wrong**, i.e. a correctness break, not merely an island miss. The two are different: an island miss is a
  clean truncation landing on bad inputs; a `WidthOverflow` is the truncation **corrupting the operand**.
- **worst-case sample:** earliest `WidthOverflow` moves from step 20 (baseline tail) to **step 8** (the trimmed
  region) — direct causal evidence the trim itself induces the overflow. Worst factor hashes in the TSV.

## Why it fails (grounded)
`truncated_gcd_step` (`dialog_gcd_classical_filter.rs:251`) returns `WidthOverflow` when
`bitlen(u) > active_width` or `bitlen(v) > active_width`. Early in the walk the operands are large:
- step 0: `u = p` (always **256-bit**) — so any `active_width < 256` at steps 0–9 overflows **every** factor
  (the 100% columns).
- steps 8–11: most factors' operands still occupy 255–256 bits (the GCD has barely shrunk them), so trimming to
  255/254 overflows the marginal tail → +24 / +101 hard inputs.
The `WIDTH_MARGIN=10` is therefore **load-bearing**: it keeps `active_width ≥ bitlen` through the wide early
steps. Removing it where the peak lives (steps 8–11) breaks correctness on exactly the inputs the circuit must
handle.

## Conclusion for the maintainers
S1-A (early `active_width` ramp) is **REFUTED at zero circuit cost**: it does not preserve the truncated-GCD
correctness envelope — narrowing at steps 8–11 adds `WidthOverflow` hard inputs, and narrowing steps 0–9 fails
100% (because `u=p` is 256-bit). The 1302q peak's `2·active_width−1` demand at the widest steps cannot be cut by
shrinking `active_width` there. Combined with R1 (donor=0) and S1-B (borrow headroom=0), **all local levers on
the early-step scratch deficit are now closed.** The only remaining paths are S1-C (phase split, op-stream-changing,
unmeasured Toffoli cost) or the engine-scale Schrottenloher `apply_bv` layout (`TRAILMIX_LAYOUT_DIFF`, 1169–1191q)
— both research-strategy calls for the maintainers.

## Compliance
classical/number-theory only · no `./benchmark.sh` · no score claim · no nonce search · no GPU · no submission ·
no circuit prototype · R2 not started · S1-C not started · diagnostic edit reverted (`git diff -- src/` = 0,
bin removed) · main branch untouched (`013f1f7`). Raw: `proof/phase3/ph4_s1a_convergence_400k.tsv`,
`ph4_s1a_convergence_log.txt`. Harness: `scripts/s1a_patch_and_bin.py` (reproducible; patches + reverts).
