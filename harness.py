#!/usr/bin/env python3
"""Orchestrator: registry + escapes -> detections -> score -> report.

Lineage-claim language is temporal/structural, not causal: a certified BREACH
says 'a marker only you planted inside an air-gapped enclave turned up outside it
after planting' -- so a gap that claimed to hold was crossed. It names the enclave
and which of the four kinds of gap failed; it does NOT prove the egress path or
blame an operator. A gap failing is evidence, not an accusation.
"""
from __future__ import annotations
from registry import Registry
from escape import Escape
from score import score


def collect_detections(registry: Registry, escapes):
    values = [e["value"] for e in registry.entries]
    by_value = registry.by_value()
    detections = []
    for eidx, esc in enumerate(escapes):
        for v in esc.canaries_in(values):
            a = by_value[v]
            detections.append({
                "value": v,
                "hash": a["hash"],
                "held_out": a["held_out"],
                "isolation": a["isolation"],
                "enclave": a["enclave"],
                "gap_kind": a["gap_kind"],
                "planted_utc": a["planted_utc"],
                "where": esc.where,
                "observed_utc": esc.observed_utc,
                "escape_id": eidx,
            })
    return detections


def run_panel(registry: Registry, escapes):
    detections = collect_detections(registry, escapes)
    return score(detections, registry.entries)


def report(v: dict) -> str:
    lines = [
        "# Faraday report", "", v["verdict"], "",
        f"held-out controls run  : {v['held_out_n']}",
        f"control FPR            : {v['control_fpr']}",
        f"expected-gated (had a path): {len(v['expected_gated'])}",
        f"impossible (pre-plant) : {len(v['impossible'])}",
        f"base-rate (chance)     : {v['base_rate']:.2e}",
        f"certified breaches     : {len(v['certified_breaches'])}",
    ]
    for val, b in sorted(v["certified_breaches"].items()):
        lines.append(f"  - {val[:16]}... enclave '{b['enclave']}' "
                     f"({b['gap_kind']} gap) in {b['sightings']} sighting(s)")
    return "\n".join(lines)
