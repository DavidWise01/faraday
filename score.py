#!/usr/bin/env python3
"""Scoring + controls. The held-out arm and the ISOLATION GATE do the epistemic
work.

A DETECTION is one (canary, escape) pair where the canary stands alone in text
found OUTSIDE. Each is tiered:

  BREACH    : an AIR-GAPPED enclave's marker, found OUTSIDE, after it was planted
              -> a gap that claimed no path was crossed. A strong LEAD, tagged
              with the enclave and which of the four kinds of gap failed.
  EXPECTED  : a CONNECTED enclave's marker found outside -> that enclave had a
              legitimate path out, so this is not a breach. Gated.
  INSIDE    : found still within the boundary -> the marker never left.
  IMPOSSIBLE: observed outside BEFORE it was planted inside -> provenance error.
  CONTROL   : a HELD-OUT marker found anywhere -> fabrication -> run INVALID.

Certification: BREACH leads certify only if a held-out control arm ran and its
false-positive rate is 0. A breach is a LEAD -- it says the marker crossed a gap
that claimed to hold; the egress path is inferred, not proven, and no operator is
blamed. Corroboration = distinct outside sightings.
"""
from __future__ import annotations
from canary import HEX_LEN


def _before(a, b):
    if not a or not b:
        return False
    return a[:19] < b[:19]


def tier(d):
    if d["held_out"]:
        return "CONTROL"
    if d["where"] == "inside":
        return "INSIDE"
    if _before(d["observed_utc"], d["planted_utc"]):
        return "IMPOSSIBLE"
    if d["isolation"] == "connected":
        return "EXPECTED"          # had a path out -> not a breach
    if d["isolation"] == "air_gapped":
        return "BREACH"
    return "OTHER"


def score(detections, registry_entries):
    held_total = [e for e in registry_entries if e["held_out"]]
    n_held = len(held_total)

    for d in detections:
        d["tier"] = tier(d)

    control_hits = {d["value"] for d in detections if d["tier"] == "CONTROL"}
    fpr = (len(control_hits) / n_held) if n_held else None

    breach = {}
    for d in detections:
        if d["tier"] == "BREACH":
            breach.setdefault(d["value"], {"relays": set(),
                                           "enclave": d.get("enclave", ""),
                                           "gap_kind": d.get("gap_kind", "")})
            breach[d["value"]]["relays"].add(d.get("escape_id", id(d)))
    expected = {d["value"] for d in detections if d["tier"] == "EXPECTED"}
    impossible = {d["value"] for d in detections if d["tier"] == "IMPOSSIBLE"}

    checks = max(1, len(detections))
    base_rate = checks * (2 ** -(HEX_LEN * 4))

    if n_held == 0:
        verdict = "INVALID: no held-out control arm was run (performative)"
        certified = {}
    elif fpr and fpr > 0:
        verdict = (f"INVALID: control FPR={fpr:.2f} -- the harness is manufacturing "
                   f"escapes; no breach is trustworthy")
        certified = {}
    else:
        certified = breach
        verdict = (f"CLEAN: control FPR=0 over {n_held} held-out; "
                   f"{len(certified)} breach lead(s) -- the gap failed, path inferred not proven")

    return {
        "verdict": verdict,
        "certified_breaches": {v: {"sightings": len(b["relays"]), "enclave": b["enclave"],
                                   "gap_kind": b["gap_kind"]} for v, b in certified.items()},
        "expected_gated": sorted(expected),
        "impossible": sorted(impossible),
        "control_hits": sorted(control_hits),
        "control_fpr": fpr,
        "held_out_n": n_held,
        "base_rate": base_rate,
    }
