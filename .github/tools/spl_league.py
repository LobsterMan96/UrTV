#!/usr/bin/env python3
"""The Saudi Pro League from its own source, spl.com.sa, instead of TheSportsDB.

The free TheSportsDB key caps the table at five clubs, has no matchday number and lags on fixtures.
The league's own API has all of it in two calls: the full eighteen-club table with the official
acronyms (HIL, NAS, QAD...), and all 306 matches of the season with their matchday.

    python3 .github/tools/spl_league.py            writes leagues/saudi-arabian-pro-league.json
    LEAGUES_OUT=dir python3 ...                    somewhere else

The file keeps the shape the page already reads (TheSportsDB-named event fields), so nothing else
has to change, and adds: clubs (code -> name and crest), matchday (current and total) and a table
whose rows carry the official acronym.
"""
import json, os, pathlib, sys, urllib.parse, urllib.request
from datetime import datetime, timezone

API = "https://api-sdp.spl.com.sa/v1/spl/football"
MEDIA = "https://media-sdp.spl.com.sa/"
COMPETITION = "spl::Football_Competition::47d9987fd5044e0dba6c6c1df7d6cfa8"
LEAGUE = "Saudi-Arabian Pro League"
SLUG = "saudi-arabian-pro-league"
UA = {"User-Agent": "UrTV league collector (github.com/LobsterMan96/UrTV)", "Accept": "application/json"}
OUT = pathlib.Path(os.environ.get("LEAGUES_OUT", "leagues"))


def get(path):
    url = API + path
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)


def q(ident):
    return urllib.parse.quote(ident, safe="")


def current_season():
    """The season the site itself is showing: the newest one the competition lists."""
    rows = get(f"/competitions/{q(COMPETITION)}/seasons?locale=en-GB").get("seasons") or []
    if not rows:
        raise SystemExit("no seasons returned")
    # every season is called "Saudi League" and carries no dates, but the list is newest first:
    # the site itself asks for rows[0]. Do not sort it, there is nothing to sort on.
    return rows[0]


def club_of(side):
    """A match side or a table row -> the bits we show."""
    logo = ((side.get("imagery") or {}).get("teamLogo") or "").strip()
    return {
        "code": (side.get("acronymName") or "").strip().upper(),
        "name": (side.get("officialName") or side.get("shortName") or "").strip(),
        "logo": MEDIA + logo if logo else "",
    }


def build():
    season = current_season()
    sid = season["seasonId"]
    name = (season.get("seasonName") or season.get("name") or "").strip()

    days = get(f"/seasons/{q(sid)}/matchdays?locale=en-GB").get("matchdays") or []
    total = len(days)

    matches = get(f"/seasons/{q(sid)}/matches?matchDayId=&locale=en-GB").get("matches") or []
    table_sets = get(f"/seasons/{q(sid)}/standings/overall?locale=en-GB").get("standings") or []
    overall = next((s for s in table_sets if s.get("type") == "table"), None)

    clubs, events = {}, []
    played_rounds = set()
    for m in matches:
        home, away = club_of(m.get("home") or {}), club_of(m.get("away") or {})
        if not home["code"] or not away["code"]:
            continue
        for c in (home, away):
            clubs.setdefault(c["code"], {"name": c["name"], "logo": c["logo"]})
        rnd = ((m.get("matchSet") or {}).get("name") or "").replace("Matchday", "").strip()
        done = (m.get("status") or "").upper() == "FINISHED"
        if done and rnd.isdigit():
            played_rounds.add(int(rnd))
        when = (m.get("matchDateUtc") or "").strip()
        if len(when) == 11 and when.endswith("Z"):      # a date with no kick-off time yet
            when = when[:-1] + "T00:00:00Z"
        events.append({
            "idEvent": (m.get("matchId") or "").rsplit("::", 1)[-1],
            "strHomeTeam": home["name"], "strAwayTeam": away["name"],
            "homeCode": home["code"], "awayCode": away["code"],
            "intHomeScore": m.get("providerHomeScore") if done else None,
            "intAwayScore": m.get("providerAwayScore") if done else None,
            "strTimestamp": when,
            "strStatus": "FT" if done else "",
            "strSport": "Soccer",
            "intRound": rnd or None,
        })

    rows = []
    for t in (overall or {}).get("teams") or []:
        s = {x.get("statsId"): x.get("statsValue") for x in (t.get("stats") or [])}
        c = club_of(t)
        clubs.setdefault(c["code"], {"name": c["name"], "logo": c["logo"]})
        if c["logo"]:
            clubs[c["code"]]["logo"] = c["logo"]
        rows.append({
            "intRank": s.get("rank"), "code": c["code"], "strTeam": c["name"],
            "intPlayed": s.get("matches-played"), "intWin": s.get("win"),
            "intDraw": s.get("draw"), "intLoss": s.get("lose"),
            "intGoalDifference": s.get("goal-difference"), "intPoints": s.get("points"),
        })
    rows.sort(key=lambda r: int(r["intRank"] or 999))

    # the matchday the table reflects: the highest with a finished game. The next one is the
    # first with a game still to play, which is what the fixtures card is showing.
    nxt = sorted({int(e["intRound"]) for e in events
                  if str(e.get("intRound") or "").isdigit() and e["strStatus"] != "FT"})
    current = max(played_rounds) if played_rounds else (nxt[0] if nxt else 1)
    upcoming = next((r for r in nxt if r >= current), nxt[0] if nxt else current)

    out = {
        "league": LEAGUE,
        "source": "spl.com.sa",
        "season": name,
        "updated": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "matchday": {"current": current, "next": upcoming, "total": total},
        "clubs": clubs,
        "table": rows,
        "events": events,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{SLUG}.json").write_text(
        json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"{LEAGUE}: season {name}, matchday {current} of {total}, "
          f"next {upcoming}, {len(rows)} in the table, {len(events)} matches, {len(clubs)} clubs")
    return out


if __name__ == "__main__":
    try:
        build()
    except Exception as e:
        print(f"!! {e}", file=sys.stderr)
        raise
