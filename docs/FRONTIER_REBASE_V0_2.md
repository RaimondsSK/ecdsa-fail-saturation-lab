# Frontier Rebase — v0.2 Note (dated)

**Date:** 2026-06-12. **Scope:** a transparency/correction note appended to the v0.1 saturation report. This
note **does not rewrite or delete v0.1**; it records that the public frontier moved and corrects one
over-strong claim. Analysis-only.

## Status of v0.1
- **v0.1 remains valid** as an analysis of the ecdsa.fail frontier **commit `013f1f7`** (score
  1,899,562,014). Its measurements and refutations of the surveyed levers *at that commit* stand unchanged.
- **v0.1 is superseded as a "current frontier" analysis.** The public leaderboard has since advanced to commit
  **`0d1d1e7`**, score **≈1,701,048,104** (avg Toffoli 1,404,664 × peak 1,211 qubits), reached through roughly
  **40 accepted submissions** after `013f1f7` over ~4.5 days.

## Claim correction
- **Too-strong claim in v0.1:** that the 1,302-qubit peak was *globally* "structurally bound."
- **Corrected claim:** the **surveyed local and hybrid levers at commit `013f1f7` were exhausted** (the
  donor-recycle, borrow-headroom, early-width-trim, and apply-register-reuse routes were each measured and
  refuted *at that commit*). That conclusion was about the levers and compute available in that sprint — **not a
  proof that the task is globally saturated.** The public frontier subsequently demonstrated further headroom.

## What the new frontier used (observed from the public diff `013f1f7 → 0d1d1e7`)
A multi-technique, engine-scale, Kaliski-preserving advance (13 files, ≈+3,749/−384 lines), combining lever
families **not present at `013f1f7`**:
- **Peak/register-layout teardown:** `BINDER_NOTCH_*`, `FREE_SCRATCH_BEFORE_SHIFT`, `FOLD_FREED_TAIL`,
  `BORROW_ZERO_RAW_FUTURE`, `CTRL_BODY_VENTED` (the dominant contributor; ≈65% of the score gain came from the
  −91-qubit peak reduction).
- **Selective jump-GCD:** `DIALOG_GCD_SELECTIVE_K3_STEP` — depth-3 jumps at *selected* steps (avoiding the
  transcript-width growth that uniform jump-3 would incur).
- **Measured-carry square primitive:** `SQUARE_ROW_WINDOW_MEASURED_CARRY_CLEAR` — a Toffoli cut in the square.
- **Nonce-island search:** large per-landing nonce searches (the public note references 300,000+ candidate
  nonces).

A more detailed breakdown is in the (non-published) lab analysis; this note records the headline facts.

## What this work claims — and does not
- **No new score-improving submission was produced by this work.**
- **No leaderboard claim is made** — this work is not on the leaderboard and does not claim to have beaten,
  matched, or reproduced any submission. The frontier commits referenced (`ea8a7716` / `013f1f7`, `03a15501` /
  `0d1d1e7`) are **external parties' submissions**; no ownership is claimed.
- The new-frontier metrics quoted here are taken from a public screenshot and the public repository diff; they
  were **not re-measured** by this work (no benchmark was run).

## Implication for future work
Any attempt to chase the moving frontier would require lever families and **compute** (notably large nonce
searches) beyond the scope of the v0.1 sprint. **Future work therefore requires an explicit, bounded
compute/nonce policy agreed in advance** — wall-time, candidate caps, CPU/GPU posture, and a hard rule that no
score is claimed without a full 9,024-shot 0/0/0 validation and no submission is made without explicit
authorization. No such compute has been run for this note.

## Reproducibility
The new-frontier code is public at commit `0d1d1e7`; this note is based on a read-only comparison of the public
commits `013f1f7..0d1d1e7` and a public screenshot. No private/authenticated session was used.
