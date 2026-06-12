# ecdsa-fail-saturation-lab

**An architecture-saturation / negative-result / methodology report around the ecdsa.fail frontier circuit
(commit `013f1f7`).**

Suggested release tag: `v0.1-saturation-report`.

> **No new score-improving submission landed in this sprint.** This repository documents a systematic survey
> that **mapped and refuted the surveyed local, hybrid, and apply-reuse routes** around the ecdsa.fail frontier
> commit `013f1f7`. It is a reproducible record of *why* a family of optimization ideas does not improve the
> score — not a claim of any improvement.

## What this is
ecdsa.fail is a competitive challenge to minimize `score = average(Toffoli/shot) × peak_qubits` for a reversible
quantum circuit computing one secp256k1 point addition (the inner loop of Shor's attack), under strict
0/0/0 validation over 9024 Fiat-Shamir-seeded shots. The current frontier this work studied is commit
`013f1f7`: **score 1,899,562,014** (avg Toffoli 1,458,957 × peak 1,302 qubits), validated 0/0/0.

This package is the consolidated analysis of a multi-phase effort that searched for — and did not find — a
configuration scoring below that frontier. Every surveyed route was driven to a grounded refutation or
impossibility, with traces, measurements, and (where decidable) mechanical proofs. The result is a **high-confidence saturation report**: under the evidence gathered, no surveyed local,
hybrid, or apply-reuse route carries positive expected value.

## What is claimed — and what is NOT
**Claimed (the only claim made):** we mapped and refuted the surveyed **local, hybrid, and apply-reuse** routes
around the ecdsa.fail frontier commit `013f1f7`, with reproducible diagnostics.

**Explicitly NOT claimed:**
- not a claim of **beating the frontier** or any score improvement;
- not a claim of a **leaderboard improvement** of any kind;
- not a claim of **ownership** of the external submission `ea8a7716` that established commit `013f1f7` (it was
  landed by an external party and inherited here as the study baseline).

## Headline findings (all reproducible)
1. **No blind nonce path.** The Fiat-Shamir tail-nonce fail-count distribution is flat; a short-shot (2048)
   prefilter does not predict full 9024-shot survival.
2. **Op-count-changing local edits hit a Fiat-Shamir island wall** — any change to the hashed op stream reseeds
   the 9024 test inputs, invalidating otherwise-correct truncations.
3. **The 1,302-qubit peak is the GCD walk** at the widest early steps (operands + transcript-write + a
   `2·active_width−1` body-scratch deficit, all co-resident). Measured: at the peak steps the idle-operand
   donor count is 0 and the reusable-`|0>` borrow headroom is 0.
4. **Narrowing the early operand width breaks correctness** (operands overflow the truncation window), not
   merely the nonce island — refuted over 400k deterministic factors.
5. **Transcript-only reconstruction is exact** (the Bezout recurrence is operand-independent) — but
   **apply-register reuse already exists at the frontier**, and the peak is the *walk*, not the apply, so the
   pack/apply "split" does not lower the peak.
6. **A full Schrottenloher-style engine has a lower peak but higher Toffoli**, so it likely *worsens* the score —
   it is not a frontier-preserving hybrid.

## Layout
| path | contents |
|---|---|
| `docs/FINAL_VERDICT.md` | the saturation verdict + full evidence index (start here) |
| `docs/FULL_HISTORY_MATRIX.md`, `SCORE_EPOCH_MAP.md`, `NONCE_RANGE_MAP.md` | history, score epochs, nonce map |
| `docs/HEAD_LIFETIME_MAP.md`, `CURRENT_ENGINE_ANATOMY.md` | the frontier engine's register lifecycles + peak |
| `docs/TRAILMIX_LAYOUT_DIFF.md`, `TRAILMIX_ENGINE_ANATOMY.md` | reference comparison to a Schrottenloher-style layout |
| `docs/R1_DONOR_MAP.md`, `S1_EARLY_SCRATCH_DEFICIT_MAP.md`, `S1A_CONVERGENCE_PRETEST.md` | the local-lever refutations |
| `docs/R3A_TOY_LIFECYCLE_RESULT.md`, `R3A_APPLY_REGISTER_REUSE_ANALYSIS.md`, `REDESIGN_ROUTE_MATRIX.md` | the engine-redesign scout |
| `proof/*.tsv` | representative measurement tables (peak trace, GCD tail, scratch deficit, convergence, accounting) |
| `scripts/r3a_lifecycle_model.py` | the self-contained toy lifecycle-accounting model (reproducible) |
| `archive/phase0-4/PHASE0-2_BACKGROUND.md` | the earlier optimization history |
| `MANIFEST.sha256` | SHA256 of every packaged file |

## Reproducibility / methodology note
- Measurements were produced with the challenge's own in-tree instrumentation (`TRACE_PEAK` /
  `TRACE_PHASE_ACTIVE` register-lifetime counters) and small, gated, **diagnostic-only** source probes that were
  reverted after measurement (the challenge source was never modified for optimization, and its main branch was
  never mutated).
- The convergence pre-test (`S1A_CONVERGENCE_PRETEST.md`) and the toy lifecycle model
  (`scripts/r3a_lifecycle_model.py`) are **pure number theory** and run standalone (no circuit build), over
  deterministic seeded samples — re-runnable to reproduce the reported tables.
- `HYPOTHESIS` tags mark every claim that is inferred rather than measured/proven; they are preserved verbatim.
- Paths, environment specifics, and internal workflow markers have been removed; technical content is unchanged.

## When to reopen this line of work
This is archived at saturation, not abandoned. Reopen if any of:
1. a new paper / community idea surfaces an inversion primitive that is **both** low-iteration **and** low-peak;
2. a new **upstream commit** changes the challenge architecture (or a full-history fetch enables deeper
   archaeology than the single squashed commit available here);
3. the missing **PR4 / full-history** data is provided;
4. a **concrete low-Toffoli / low-peak primitive** is identified.

## License / attribution
Analysis and documentation are original to this work. The ecdsa.fail challenge, its harness, and the upstream
`zkp_ecc` simulator are the property of their respective authors under their own licenses; this report studies
the public frontier commit `013f1f7` and claims no ownership of it or of external submission `ea8a7716`.
