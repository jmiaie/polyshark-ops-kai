# Esports Teams Database — Polyshark Router
_Built for routing Polymarket esports alerts to the Sports channel_
_Last updated: 2026-04-25_

**Routing rule:** Esports events → Sports channel (NOT World Events).  
Exception: major esports business/news about companies (acquisitions, funding) → World Events.

---

## CS2 / CS:GO (major teams)

- [CS2] NAVI | Natus Vincere
- [CS2] G2 Esports | G2
- [CS2] FaZe Clan | FaZe
- [CS2] Cloud9 | C9
- [CS2] Team Vitality | Vitality
- [CS2] Heroic
- [CS2] ENCE
- [CS2] Team Liquid | Liquid
- [CS2] Complexity Gaming | Complexity
- [CS2] Virtus.pro | VP
- [CS2] Spirit
- [CS2] BIG | Berlin International Gaming
- [CS2] Fnatic
- [CS2] NIP | Ninjas in Pyjamas
- [CS2] OG | Origen
- [CS2] MIBR | Made in Brazil
- [CS2] FURIA Esports | FURIA
- [CS2] Imperial Esports | Imperial
- [CS2] 9z Team
- [CS2] HEAVY

---

## Valorant (major teams)

- [Valorant] Sentinels
- [Valorant] Cloud9
- [Valorant] 100 Thieves | 100T
- [Valorant] Team Liquid
- [Valorant] Fnatic
- [Valorant] G2 Esports
- [Valorant] DRX
- [Valorant] Evil Geniuses | EG
- [Valorant] LEV Gaming | LEV
- [Valorant] Paper Rex | PRX
- [Valorant] Loud
- [Valorant] Titans
- [Valorant] OpTic Gaming | OpTic
- [Valorant] XSET
- [Valorant] Furiat
- [Valorant] KRÜ Esports | KRU
- [Valorant] FunPlus Phoenix | FPX

---

## League of Legends (major teams)

- [LoL] T1 | SK Telecom T1 | Faker
- [LoL] Gen.G | GenG
- [LoL] JD Gaming | JDG
- [LoL] Bilibili Gaming | BLG
- [LoL] Top Esports | TES
- [LoL] G2 Esports
- [LoL] Fnatic
- [LoL] Rogue | Rogue Warriors
- [LoL] Team Liquid
- [LoL] Cloud9
- [LoL] Evil Geniuses
- [LoL] 100 Thieves
- [LoL] Golden Guardians
- [LoL] Dplus KIA | DK
- [LoL] Liiv SANDBOX | LSB
- [LoL] Fredit BRION | BRION
- [LoL] Nongshim RedForce | NS
- [LoL] Sandbox
- [LoL] Freecs

---

## Dota 2 (major teams)

- [Dota2] Team Spirit
- [Dota2] Team Liquid
- [Dota2] OG | Origen
- [Dota2] Team Secret | Secret
- [Dota2] Evil Geniuses
- [Dota2] Nigma Galaxy | Nigma
- [Dota2] Tundra Esports
- [Dota2] Gaimin Gladiators
- [Dota2] BetBoom Team
- [Dota2] Virtus.pro | VP

---

## Overwatch (OWCS major teams)

- [OWCS] Seoul Dynasty
- [OWCS] Shanghai Dragons
- [OWCS] New York Excelsior | NYXL
- [OWCS] Los Angeles Valiant | Valiant
- [OWCS] Guangzhou Charge
- [OWCS] Philadelphia Fusion
- [OWCS] Florida Mayhem
- [OWCS] Houston Outlaws
- [OWCS] London Spitfire
- [OWCS] Toronto Defiant
- [OWCS] Boston Uprising
- [OWCS] Atlanta Reign
- [OWCS] Dallas Fuel
- [OWCS] Los Angeles Gladiators
- [OWCS] Vegas Vanguard
- [OWCS] Seoul Infernal

---

## Rocket League (major teams)

- [RL] Team BDS | BDS
- [RL] NRG Esports | NRG
- [RL] Team Vitality
- [RL] Moist Esports | Moist
- [RL] FaZe Clan
- [RL] OpTic Gaming
- [RL] Rogue
- [RL] Complexity Gaming
- [RL] Giants Organization | Giants
- [RL] Renault Vitalité | Vitalité

---

## Call of Duty (major teams)

- [COD] Atlanta FaZe | FaZe Clan
- [COD] OpTic Texas | OpTic
- [COD] Los Angeles Thieves | Thieves
- [COD] Boston Breach
- [COD] Seattle Surge
- [COD] New York Subliners | Subliners
- [COD] Toronto Ultra
- [COD] Miami Surge
- [COD] Minnesota RØKR | ROKR

---

## Esports Detection Keywords

The following keywords also trigger esports routing:

esports, esports event, esports tournament, cs2, csgo, valorant, league of legends,
dota 2, overwatch, rocket league, call of duty, major tournament, the international,
ti, worlds, champions, blast, iem, esl, epic games, riot games, valve, blizzard,
major championship, esl pro league, blast premier, iem katowice, pgl, epic cyber,
faceit, g2 esports, faze clan, navi, team liquid, sentinels, cloud9, 100 thieves,
league of legends worlds, valorant champions, cs2 major, dota 2 the international

---

## Esports Routing Notes

1. **Route to Sports channel** — All competitive esports match/schedule/outcome events route to Sports
2. **Business exception** — Company acquisitions, funding rounds, layoffs in esports → World Events
3. **Keywords for detection** — The full keyword list is maintained in the router's SPORTS_KW list
4. **Esports vs. weather** — "hurricanes" (no space) is NHL/NCAA team; "hurricane " (with space) is weather

---

_This file is owned by Jeff Milam. Update as team rosters and names change._
