# ECDSA_PHASE4_TRAILMIX_LAYOUT_DIFF

**Phase 4A · Workstream 3.** Register-layout diff: ecdsa.fail's compressed_log/GCD layout vs TrailMix's
closest secp256k1 point-add layout. Reference, not copy-paste. Source: `_external/trailmix`
(`kmx_circuit_summaries.md`, `schrottenloher_status.md`, `gcd_pack.rs`, `bezout_unpack.rs`) + Phase 3 traces.

## The headline: same algorithm family, different *where the peak lives*
| | **ecdsa.fail HEAD `013f1f7`** | **TrailMix low-qubit** |
|---|---|---|
| inversion | Kaliski binary almost-inverse / dialog (raw_quotient + raw_ipmul) | Schrottenloher EEA dialog (`gcd_pack` → `apply_bv`) |
| transcript | `compressed_log` (per-step `(b0,b0&b1)` cells, K2 base-?) | garbage bit-vector, M=5 base-3, 8 bits / 5 windows |
| **peak** | **1302q — during the GCD walk** (widest-step tobitvector) | **1191q — during `apply_bv`** (Bezout reconstruction) |
| **what is co-resident at peak** | transcript **+ full GCD operands** `tx+ty+u+raw_block` + composite scratch | transcript **+ reconstruction regs only** (x2+y2 ≈ 514) — GCD operands already freed |
| GCD operand lifetime | live at the peak (the walk *is* the peak) | **shrinks on a schedule**; freed `u/v` bits **feed the garbage allocator** (`gcd_pack.rs`) |
| adder at peak | composite-scratch-bound; all venting/borrows ON | `apply_bv` on Cuccaro 3n (no vent); GCD below peak uses Gidney 2n |

## The structural difference that costs ecdsa.fail ~111 qubits
TrailMix **separates the two heavy phases in time**:
1. **GCD walk** — operand-heavy (`u/v`), transcript being *written*, but `u/v` **shrinks each iteration** and
   the freed bits are **recycled into the transcript/garbage allocator** → the walk runs *below* the peak.
2. **`apply_bv`** — transcript-heavy (read in reverse) + only `x2/y2` reconstruction registers → this is the
   peak, but the GCD operands are **gone** by now.

ecdsa.fail **interleaves** them: the compressed-block tobitvector *writes the transcript while the full GCD
operands are still live at the widest step* → transcript **+** operands **+** scratch are all co-resident →
1302q (Phase 3 Lane B). The borrow levers recycle a *little* idle space within a block, but they do not
achieve TrailMix's *schedule-based operand shrink → transcript reuse*.

## TrailMix pattern portability (the WS3 classification)
| TrailMix pattern | portability to ecdsa.fail | why |
|---|---|---|
| **operand-shrink → freed-bits-feed-transcript** (`gcd_pack` allocator) | **conceptually portable — the key idea** | attacks exactly ecdsa.fail's co-residency; requires restructuring the compressed-block tobitvector to free `u/v` lanes into the transcript as the GCD narrows |
| **separate GCD-walk from a reconstruction phase** | conceptually portable / TOO_LARGE | ecdsa.fail's Kaliski raw_quotient/ipmul is not split into pack→apply_bv; adopting the split ≈ engine replacement |
| ghost / spooky-pebble move-only ownership + `prove_zero` frees | conceptually portable (de-risks any redesign) | gives a *systematic* earliest-free discipline ecdsa.fail lacks |
| phase-lattice correctness gate | useful-as-diagnostic | structural clean-proof for aggressive early-free |
| Gidney 2n / clean-vent adders | ALREADY in ecdsa.fail | `venting.rs`, all flags ON |
| Wallace square | incompatible-as-upgrade | ecdsa.fail already at ~n² floor (Lane E) |
| jump-GCD depth | ALREADY (depth-2); deeper widens transcript | Lane D |

## What this diff tells Phase 4
The lower-peak existence proof is real (1191q standalone / 1169q jump) and its mechanism is identifiable:
**peak-time separation of transcript from GCD operands, via schedule-based operand shrink + bit recycling.**
That mechanism — not a primitive swap — is the redesign target. See
`ECDSA_PHASE4_COMPRESSED_LOG_REDESIGN_SKETCH.md`. Caveat: TrailMix's numbers are for the *Schrottenloher EEA*
structure; porting the *idea* to ecdsa.fail's Kaliski dialog is a layout redesign of unknown net size, which
is precisely the Phase 4B/4C question.
