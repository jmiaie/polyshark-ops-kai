# Status — polyshark-ops-kai

**Updated:** 2026-09-30 (PT)  
**Visibility:** public  
**Maturity:** stalled MVP / specialist fork (team KB + embedded memory snapshot)  
**Canonical team KB (preferred):** [`jmiaie/polyshark-ops`](https://github.com/jmiaie/polyshark-ops)  
**Memory SKU canonical:** [`jmiaie/pliamem`](https://github.com/jmiaie/pliamem) (private) / [`pliamem-public`](https://github.com/jmiaie/pliamem-public)

## Honest positioning

GitHub description: *“Kai's Polyshark team knowledge base — routing maps, keywords, card specs, and ops docs.”*

What is actually on `main`:

| Area | Reality |
|------|---------|
| `team/` | Polyshark / WhaleTrax **ops handoff** notes, checkpoints, Stripe product notes, agent comms — the KB value of this fork |
| Root `README.md` / `SPEC.md` / `package.json` / `src/` / `tests/` / `cloud-ui/` | A **stale pliamem** product tree (package name `pliamem`, same shape as the memory SKU) embedded at repo root |
| `clients/`, `config/`, `docs/adapter-guide.md` | Belong to the embedded pliamem surface |

Same pattern as `polyshark-ops` before its honesty pass: **team KB is primary**; root pliamem tree is **not** the shipping memory product and should not be dual-maintained vs `pliamem`.

**Do not large-delete** the embedded pliamem tree in this wave — needs Jeff confirm that this fork is KB-only (same gate as polyshark-ops).

## POSITIONING

| Repo | Role |
|------|------|
| `polyshark-ops` | Primary team knowledge base |
| `polyshark-ops-kai` | Kai specialist fork / snapshot — prefer syncing from or into `polyshark-ops` |
| `whaletrax` / `whaletrax-kai` | Scanner / router engines — **not** this KB |
| `pliamem` | Canonical memory router SKU — **do not merge** this fork into OMPA/pliamem |

## Offline quickstart (embedded pliamem tests only)

```bash
npm test    # node --test tests/*.test.js
```

Recorded on this box 2026-09-30 PT: **65** tests passed, 0 failed (~0.2s). That re-verifies the **embedded** memory unit tests — it does **not** mean Polyshark routing is shipping from this remote or that live Telegram/router ops are healthy.

## Hygiene / secrets note

Ops handoff markdown under `team/` may reference historical bot/token material. **Do not paste secrets into issues/PRs.** Owner should rotate any credentials that were ever live and prefer secret stores over git. This advance prints **no** credential values.

## What is **not** claimed

- That this fork is ahead of `polyshark-ops`  
- Live whale-alert uptime, subscriber counts, or PnL  
- That root README “npm install -g pliamem” is the supported install path for Polyshark ops

## Next (owner)

1. Confirm KB-only → then strip/archive embedded pliamem (or replace root README permanently and leave tree read-only)  
2. Prefer `polyshark-ops` for shared routing/keyword edits  
3. Optional CI only with a **workflow-scoped** token (not this wave)
