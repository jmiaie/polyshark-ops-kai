# polyshark-ops-kai

**Kai’s Polyshark team knowledge-base fork** — ops handoffs, routing/ops notes, and related team docs under `team/`.

> **Status (2026-09-30):** stalled specialist fork. Prefer the primary KB [`jmiaie/polyshark-ops`](https://github.com/jmiaie/polyshark-ops).  
> Full honesty: [`STATUS.md`](STATUS.md) · [`POSITIONING.md`](POSITIONING.md).

## What to read first

| Path | Use |
|------|-----|
| [`team/`](team/) | Polyshark / WhaleTrax ops notes and handoffs |
| [`STATUS.md`](STATUS.md) | Maturity, pliamem-embed warning, test notes |
| [`POSITIONING.md`](POSITIONING.md) | vs `polyshark-ops` / `pliamem` / `whaletrax*` |

## Embedded `pliamem` tree (stale)

The repo **root** still contains a **pliamem** package snapshot (`package.json` name `pliamem`, `src/`, `tests/`, `SPEC.md`, `cloud-ui/`). That is **not** the product this GitHub description advertises, and it is **not** the canonical memory SKU.

- Canonical memory work: [`jmiaie/pliamem`](https://github.com/jmiaie/pliamem)
- Optional local re-verify of the **embedded** unit tests only:

```bash
npm test
```

Do **not** `npm install -g pliamem` from this fork as if it were the publishing source.

## License

See [`LICENSE`](LICENSE).
