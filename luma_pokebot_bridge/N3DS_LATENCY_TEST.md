# New 3DS bridge latency test

Targeted test branch for the New 3DS-only ~100–150 ms UDP bridge latency seen in the 2026-08-24 support probe.

Changes are intentionally limited to the bridge worker scheduling/receive loop. RAM read limits and controller protocol framing remain unchanged.
