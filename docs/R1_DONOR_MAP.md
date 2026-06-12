# ECDSA_PHASE4C_R1_DONOR_MAP

**Phase 4C · R1 Stage B — donor feasibility diagnostic.** Hypothesis
`PH4-R1_OPERAND_NARROW_TRANSCRIPT_RECYCLE`: donate provably-`|0>` freed `u/v` high lanes into `compressed_log`
storage so transcript growth no longer stacks fresh deficit lanes at the 1302q peak.

**Method (diagnostic only).** A gated per-step probe (`DIALOG_GCD_R1_DONORMAP`) inserted into the tobitvector
step loop of `compressed.rs` (R1 worktree, **reverted after measurement** — `git diff -- src/` = 0). It dumps,
per GCD step: `active_width`, `freed_uv = 2·(N − active_width)` (the idle `u/v` high lanes), and the per-step
high-water `active` (captured post-subtract, the step's heaviest instant). Raw: `proof/phase3/ph4_r1_perstep_raw.txt`;
distilled: `proof/phase3/ph4_r1_donor_map.tsv` (259 steps).

## The structural relationship (decisive)
- `active_width(step)` shrinks linearly: `≈ N − step·1.015 + 10`, clamped `[1,256]` (`DIALOG_GCD_WIDTH_SLOPE_X1000=1015`,
  `_WIDTH_MARGIN=10`, `_VARIABLE_WIDTH=1`). So **donor lanes `freed_uv = 2·(256 − active_width)` grow with step.**
- The per-step peak is set by the composite-scratch **deficit `≈ 2·active_width − 1`** (`dialog_gcd_build_composite_scratch`,
  compressed.rs:349; developer note compressed.rs:306–310). So **the peak grows with `active_width`.**
- Therefore **`freed_uv` and the per-step peak are anti-correlated by construction**: high peak ⟺ high
  `active_width` ⟺ **`freed_uv ≈ 0`**.

## Measured per-step donor map (sampled; full table in `ph4_r1_donor_map.tsv`)
| step | active_width | freed_uv (idle u/v high lanes) | per-step active (post-sub) | reaches 1302? |
|---:|---:|---:|---:|:--:|
| 0 | 256 | **0** | 1281 | no |
| 5 | 256 | **0** | 1292 | no |
| **9** | **256** | **0** | **1302** | **YES** |
| **10** | **256** | **0** | **1302** | **YES** |
| 20 | 246 | 20 | 1287 | no |
| 50 | 216 | 80 | 1242 | no |
| 100 | 166 | 180 | 1179 | no |
| 150 | 114 | 284 | 1179 | no |
| 200 | 64 | 384 | 1179 | no |
| 250 | 14 | 484 | 1179 | no |

**Binding steps (per-step active = 1302): exactly steps 9 and 10. Both have `freed_uv = 0`.**
**MAX `freed_uv` over all 1302-reaching steps = 0.** Every step with `freed_uv > 0` runs **below 1302**
(step 20 already down to 1287; ≥step 100 flat at 1179).

## The Stage B questions, answered
| question | finding |
|---|---|
| per GCD step / active_width | measured; `active_width` falls 256→14 over steps 0→250 |
| which `u/v` high lanes are provably `\|0>` | the `u[active_width..]`/`v[active_width..]` lanes — but they exist (`freed_uv>0`) **only from ~step 16 onward** |
| when each lane is last needed by operand logic | a lane above `active_width(k)` is idle from step `k` on (operand width has passed it) |
| when compressed_log cell is written / read | written by `compress_block` at the step (forward); read by `decompress` at the same step in the inverse pass — a long, whole-walk live span |
| does donor lifetime cover compress_block AND reverse_add **peak** phases? | **NO** — the peak phases occur at steps 9–10 where `freed_uv = 0`; donor lanes only appear at later steps that are **not** at the peak |
| collision with raw_block / composite scratch? | **YES** — at the later steps where `freed_uv>0`, those lanes are **already borrowed** by the composite scratch (`DIALOG_GCD_LATE_BORROW_UV_HIGH=1`); they are not idle surplus |

## PASS/FAIL verdict
> PASS condition: ≥1 donor lane provably `|0>`, safe across the transcript-cell live window, **and reaching a
> 1302-binding phase**.
> FAIL condition: **no donor lane reaches the binding phases**, or cannot be proven `|0>`, or transcript
> reconstruction needs an op-stream-changing rewrite.

**VERDICT: FAIL.** At every 1302-binding step (9, 10) the idle `u/v` high-lane count is **0** — no donor lane
exists where the peak is set. Donor lanes appear only at later, narrower steps that already run below 1302 and
are already borrowed by the composite scratch. The donor lanes and the peak are mutually exclusive by the
`freed_uv = 256 − active_width` vs `peak ∝ 2·active_width − 1` anti-correlation. R1 cannot lower the global peak.

→ proceed to `ECDSA_PHASE4C_R1_RESULT.md` (R1_REFUTED). **Stage C (prototype) NOT entered.**
