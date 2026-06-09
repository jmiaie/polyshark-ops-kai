# Sports vs. eSports Routing — Maintenance Note

**Why the split matters**
Physical sports team names (Lakers, Celtics, Yankees) can appear in non-sports contexts: "Celtic knots", "Yankees notebook", "Kings of Leon". eSports team names (Cloud9, T1, G2) are almost always gaming context — they don't have that ambiguity.

The split prevents:
- Physical sports misrouting due to false-positive team names
- eSports being swallowed by generic sports keywords

---

## How it works

### Physical Sports (→ PolysharkSports)
- **Keywords**: `SPORTS_KW` — team names, league names, sport types
- **Requires anchor**: A sports market must contain a context anchor word (`vs`, `game`, `score`, `playoff`, `nba`, `nfl`, etc.) alongside the team name
- **Examples**:
  - `"Lakers vs. Rockets"` → matches `lakers` (SPORTS_KW) + `vs` (anchor) → **Sports** ✅
  - `"Celtic knots tutorial"` → matches `celtics` but NO anchor → **NOT Sports** ❌
  - `"Yankees season preview"` → matches `yankees` but `season preview` contains anchor → **Sports** ✅

### eSports (→ PolysharkEsports)
- **Keywords**: `ESPORTS_KW` — org/team names, game titles, esports events
- **No anchor required**: Team org names are inherently esports context
- **Examples**:
  - `"Cloud9 vs. T1"` → matches `cloud9` + `t1` (ESPORTS_KW) → **eSports** ✅
  - `"Valorant Champions 2026"` → matches `valorant` + `champions` (ESPORTS_KW) → **eSports** ✅
  - `"League of Legends Worlds"` → matches `league of legends` + `worlds` (ESPORTS_KW) → **eSports** ✅

---

## Keyword files
- Physical sports teams: `ompa_vault/brain/polyshark/sports_teams.md` (300+ entries)
- eSports teams/orgs: `ompa_vault/brain/polyshark/esports_teams.md` (90+ entries)

---

## Adding new teams

### Physical sports
Add to `ompa_vault/brain/polyshark/sports_teams.md` using the existing format:
```
- [Team Name](description)
```
Then add the team name (and common nicknames) to `SPORTS_KW` in `polyshark_router.py`.

### eSports
Add to `ompa_vault/brain/polyshark/esports_teams.md` using the existing format.
Then add the team/org name to `ESPORTS_KW` in `polyshark_router.py`.

**Critical**: Do NOT add an esports team name to `SPORTS_KW`. They must stay in `ESPORTS_KW` only.

---

## Routing priority
`detect_categories_with_confidence` scores all categories simultaneously. The highest score wins. Sports and eSports are scored independently — a market cannot score in both categories at once (team names are unique to each list).

If a market somehow scores in both, the tie-breaker is alphabetical: `esports` before `sports`.

---

## Monitoring
Check routing quality with:
```bash
grep "Category forward (sports)" /tmp/polyshark_router.log | tail -20
grep "Category forward (esports)" /tmp/polyshark_router.log | tail -20
```

If a sports market is misrouting to eSports (or vice versa), check:
1. Is the team name in the correct keyword list?
2. Does a physical sports market have a qualifying anchor word?
3. Is the esports market using the correct game/team name variant?

*Last updated: 2026-04-25*