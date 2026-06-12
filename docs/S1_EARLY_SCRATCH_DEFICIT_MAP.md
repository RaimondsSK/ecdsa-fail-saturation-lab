# ECDSA_PHASE4C_S1_EARLY_SCRATCH_DEFICIT_MAP

**Phase 4C · S1 Stage A + B.** Diagnostic decomposition of the early wide-step (steps 8–11) composite-scratch
deficit that pins the 1302q peak, + the source-grounded allocator formula. **Diagnostic only** — all probes
gated, **reverted after** (`git diff -- src/` = 0); main untouched at `013f1f7`. No benchmark, no score, no nonce/GPU.

## Stage A — measured per-step decomposition (steps 8–11, forward quotient walk)
Probe: gated `DIALOG_GCD_S1_DECOMP` / `_S1_BORROW` inside `dialog_gcd_build_composite_scratch`. Raw:
`proof/phase3/ph4_s1_decomp_raw.txt`, `ph4_s1_borrow_raw.txt`.

| step | active_width | want (body clean-lane demand) | borrowed | **owned deficit (fresh)** | compressed_log | raw_block | per-step active |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 8 | 256 | 509 | 387 | **122** | 645 | 6 | 1301 |
| **9** | **256** | **509** | **386** | **123** | 645 | 6 | **1302 (PEAK)** |
| **10** | **256** | **505** | **382** | **123** | 645 | 6 | **1302 (PEAK)** |
| 11 | 256 | 501 | 381 | **120** | 645 | 6 | 1299 |

**The peak tips 1301→1302 at step 9 for one reason: the runway-safe borrow pool drops by exactly 1
(387→386), forcing one extra fresh lane (`owned` 122→123).** Steps 8 and 11 sit at 1301/1299; only 9–10 hit 1302.

### Active-qubit sources at the peak (step 9)
The live registers overlap heavily (borrows reuse already-allocated cells), so they are **not additive** — the
distinct live count is 1302. The components:
| source | size | additive at peak? | note |
|---|---:|---|---|
| point-add operands (tx, ty, ox/oy) + GCD `u`,`tmp` (each `alloc_qubits(N=256)`, mod.rs:1664/1743) | resident | the resident base | the GCD allocates its own `u`/`tmp`; not aliased to tx/ty |
| **compressed_log** (transcript register) | **645** | partly — its *unwritten* tail is borrowed as scratch | `= blocks × block_bits`; the single largest register |
| raw_block | 6 | yes (small) | the decompressed current block (`2·group_size`) |
| composite scratch `want` | **509** | **123 fresh + 386 borrowed** | the body's clean-lane demand `≈ 2·body_width−1` |
| → **`owned` deficit** | **123** | **YES — the only freshly-allocated, additive, reducible part** | `b.alloc_qubits(want − borrowed)`, compressed.rs:450 |
| borrowed lanes | 386 | no (reused `\|0>` cells) | runway-safe future-log prefix (380) + s2 + current-block |

**The one clearly-reducible additive quantity at the peak is the `owned` deficit (123).** Everything else is
either resident operands/transcript or reused borrows. Reaching 1301 requires `owned ≤ 122` at steps 9–10.

## Stage B — source-grounded composite-scratch formula
`dialog_gcd_build_composite_scratch` (`compressed.rs:349`), dev notes `compressed.rs:304–342`.

### Why the demand is `want ≈ 2·active_width − 1`
The selected modular add/sub **body** needs, per the dev note (L306–310), `~2·active_width − 1` clean lanes:
`active_width − 1` **carry** lanes + `active_width` **gated-host** lanes (`host_gated`), for the truncated
ripple. With the `nocin` body trimming it is `2·body_len − 1` capped at `2·active_width − 1` (compressed.rs:375–380),
so `want = 509` at width 256 (body_len 255). **This is a genuine arithmetic demand, not an artifact** — it is
the carries+sums working set of a 256-bit conditional modular add/sub.

### What the cells are
| scratch cell class | required? | source at steps 9–10 |
|---|---|---|
| carry lanes (`active_width − 1`) | **mathematically required** (ripple carries) | borrowed where possible, else fresh |
| gated-host lanes (`active_width`) | required (the `ctrl & a` materialization the body adds in place) | borrowed/fresh |
| (no separate temp-sum register — the body is in-place) | — | — |

### The borrow ladder (all already ON) and why it caps at 386
The allocator fills `want` by `push()`-ing reusable `|0>` cells, in order (compressed.rs:392–448):
1. **future-log carry slice** — the *unwritten* tail of `compressed_log` (`RAW_TOBITVECTOR_BORROW_FUTURE_LOG_CARRIES=1`),
   **clamped to the runway-safe prefix** (`dialog_gcd_runway_safe_future_prefix`, L280): truncated at the first
   future cell that **aliases the active-u operand** (borrowing past it would corrupt `u`).
2. current-block compressed cells (`BORROW_CURRENT_BLOCK=1`).
3. `v[active_width..]`, `u[active_width..]` (`LATE_BORROW_UV_HIGH=1`) — **= 0 at steps 9–10** (active_width=256).
4. `s2` (+ sibling under the trio notch).
5. **`owned = alloc_qubits(want − borrowed)`** — the fresh deficit.

**Measured borrow ceiling (step 9):** `fut_raw=511`, runway-safe prefix `fut_safe=380`, **non-aliasing cells
beyond the safe prefix = 0**. So **every one of the 131 future cells past the safe prefix aliases active-u and
is unborrowable.** The borrow is provably **maximal** — there is no idle `|0>` cell left to claim.

### Can any single cell be removed/borrowed safely at steps 9–10?
- **By smarter borrowing (op-count-invariant relabel): NO.** Borrow headroom = 0 (measured). Every reusable
  `|0>` source is exhausted; the remaining future cells alias the operand. (This refutes the "+1 borrow"
  relabel — the analogue of R1, now closed on the borrow side too.)
- **By reducing `want`: only via an op-stream-changing truncation** (narrower body carries / active_width),
  which changes emitted ops → Wall-2 island risk + correctness risk (the `KAL_FOLD_CARRY_TRUNC_W` /
  `ACTIVE_ITERATIONS=257` failure pattern). Not a local relabel.

## Summary for Stage C/D
The 1302 peak is a **genuine 123-lane body-arithmetic deficit at width 256, with the borrow pool provably
maximal (headroom 0)**. No op-count-invariant relabel reduces it (R1 donor=0; S1 borrow headroom=0). Any
reduction is op-stream-changing (Wall-2-exposed). → candidate evaluation in `ECDSA_PHASE4C_S1_REVISED_QUEUE.md`.
