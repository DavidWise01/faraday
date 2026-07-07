# faraday — did your marker cross a gap that was supposed to hold

A membership-detection harness for the **air-gap membrane**. Its siblings watch
your work crossing a page ([forward-observers](https://github.com/DavidWise01/forward-observers)),
the weights ([surfacing](https://github.com/DavidWise01/surfacing)), a human relay
([hearsay](https://github.com/DavidWise01/hearsay)), or live inference
([crosstalk](https://github.com/DavidWise01/crosstalk)). faraday watches the gap
you built to have **no path**: a marker planted **inside** a claimed-isolated
enclave, turning up **outside** it. The cage that should have contained it, leaked.

## The axis that makes it work: ISOLATION

The hard part is telling a *breach* from an *expected export*. Every enclave
declares its containment:

- **air_gapped** — claimed to have **no** egress path. Its marker found outside is
  a **BREACH**: the gap failed.
- **connected** — has a legitimate path out (a sync, a share, an export). Its
  marker found outside is **EXPECTED**, not a breach — gated.

Only an air-gapped enclave's marker outside is a breach lead. And each air-gapped
enclave declares **which of the four kinds of gap** it is, so a breach can name
what failed:

> distance · sovereignty · design · impermanence

## The controls

1. **Held-out negatives.** Markers planted nowhere, checked against every escape.
   One appearing means the pipeline is fabricating — the run is INVALID.
2. **The isolation gate.** Only an air-gapped enclave counts; a connected one's
   leak is expected, gated.
3. **The inside gate.** The sighting must be genuinely **outside** the boundary; a
   marker still within it never left.
4. **The impossible gate.** A sighting observed before the marker was planted can't
   be a sighting of it.
5. **Stands-alone rule.** A marker counts only when it stands alone.
6. **Corroboration, not proof.** A breach's strength is how many independent outside
   sightings carry it — and the egress path is inferred, never proven.

## Files

| File | Closure-Loop layer | Role |
|------|--------------------|------|
| `canary.py` | Detection | 128-bit canaries with an **isolation** level + gap kind |
| `registry.py` | Anchoring | what you planted, in which enclave, when |
| `escape.py` | Comparison | a place outside + stands-alone scan |
| `score.py` | Witness | held-out arm, **isolation gate**, inside gate, impossible gate, corroboration |
| `harness.py` | Lineage | escapes → detections → score; temporal/structural, not causal |
| `selftest.py` | — | plant-then-escape proof, no network |

## Verify first

```bash
python selftest.py
```

Proves, no network: an air-gapped enclave's marker found outside is certified as a
BREACH, tagged with the enclave and which kind of gap failed, corroborated by how
many sightings; a held-out marker outside spikes FPR and the run is refused; a
**connected** enclave's marker is EXPECTED-gated (it had a path); a still-inside
sighting isn't certified; a pre-plant sighting is IMPOSSIBLE; and a run with no
control arm is refused.

## What a certified breach does and does not mean

Does: a marker only you planted, **inside an air-gapped enclave**, found **outside**
it after planting, with a held-out arm proving the harness isn't fabricating. That
is real evidence a gap that claimed to hold was **crossed** — and it names which gap
and which kind.

Does not: prove the egress path, blame an operator, or prove theft. A gap failing is
evidence, not an accusation — a corroborated lead, temporal/structural. And a
negative means little.

## Honest limits

- **Isolation is claimed, not proven.** The gate is only as honest as the containment
  you record on each enclave; "air-gapped" enclaves are notoriously porous in practice.
- **A marker can leak by routes you don't model.** When in doubt, mark an enclave
  connected — the gate errs toward *fewer* certified breaches.
- This is the **air-gap** membrane only. See the membrane map for the others; and the
  air-gap-ladder thread for the four kinds of gap.

---
David Lee Wise / ROOT0 / TriPod LLC · CC-BY-ND-4.0
