"""Génère assets/contributions.svg depuis le calendrier GraphQL GitHub.
Usage : python3 contributions.py calendar.json assets/contributions.svg
"""
import json
import sys
from datetime import date

MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
LEVELS = {"NONE": "#F3EBD3", "FIRST_QUARTILE": "#FFE9A3", "SECOND_QUARTILE": "#FFD95C",
          "THIRD_QUARTILE": "#F6BE12", "FOURTH_QUARTILE": "#C88D00"}
INK, OCHRE, BG, BORDER, MARK = "#2B1A0C", "#6B5200", "#FFF8E1", "#F2DFA0", "#FFD23F"
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"


def streaks(counts):
    """(série actuelle, meilleure série). Aujourd'hui à 0 ne casse pas la série : la journée n'est pas finie."""
    best = run = 0
    for c in counts:
        run = run + 1 if c else 0
        best = max(best, run)
    tail = counts[:-1] if counts and not counts[-1] else counts
    cur = 0
    for c in reversed(tail):
        if not c:
            break
        cur += 1
    return cur, best


assert streaks([1, 1, 0, 1]) == (1, 2)
assert streaks([1, 1, 1, 0]) == (3, 3)
assert streaks([0, 0]) == (0, 0)


def fr(d):
    return f"{d.day} {MOIS[d.month - 1]} {d.year}"


def main(src, out):
    cal = json.load(open(src))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    total = cal["totalContributions"]
    cur, best = streaks([d["contributionCount"] for d in days])
    top = max(days, key=lambda d: d["contributionCount"])

    W, PAD, CELL, PITCH = 868, 36, 12, 15
    hy = 196  # haut de la grille
    H = hy + 7 * PITCH + 54
    num = f"{total:,}".replace(",", " ")
    num_w = int(len(num) * 88 * 0.6)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="{FONT}" role="img" aria-label="{total} contributions sur les 12 derniers mois">',
         f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{BG}" stroke="{BORDER}"/>',
         f'<text x="{PAD}" y="54" font-size="13" font-weight="700" letter-spacing="1.6" fill="{OCHRE}">'
         'CONTRIBUTIONS · 12 DERNIERS MOIS</text>',
         f'<rect x="{PAD - 4}" y="104" width="{num_w + 8}" height="30" rx="4" fill="{MARK}"/>',
         f'<text x="{PAD}" y="132" font-size="88" font-weight="800" letter-spacing="-2" fill="{INK}">{num}</text>',
         f'<text x="{PAD + num_w + 16}" y="130" font-size="24" font-weight="600" fill="{INK}">contributions</text>']

    stats = [("Série actuelle", f"{cur} j"), ("Meilleure série", f"{best} j"),
             ("Record en un jour", str(top["contributionCount"]))]
    for i, (label, value) in enumerate(stats):
        cx = W - PAD - 60 - (len(stats) - 1 - i) * 135
        s.append(f'<text x="{cx}" y="102" text-anchor="middle" font-size="30" font-weight="800" fill="{INK}">{value}</text>')
        s.append(f'<text x="{cx}" y="126" text-anchor="middle" font-size="12" fill="{OCHRE}">{label}</text>')

    last_month = None
    for wi, w in enumerate(weeks):
        x = PAD + wi * PITCH
        first = date.fromisoformat(w["contributionDays"][0]["date"])
        if first.month != last_month and wi < len(weeks) - 2:
            s.append(f'<text x="{x}" y="{hy - 10}" font-size="11" fill="{OCHRE}">{MOIS[first.month - 1]}</text>')
            last_month = first.month
        for d in w["contributionDays"]:
            y = hy + date.fromisoformat(d["date"]).isoweekday() % 7 * PITCH
            s.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{LEVELS[d["contributionLevel"]]}">'
                     f'<title>{d["contributionCount"]} le {fr(date.fromisoformat(d["date"]))}</title></rect>')

    ly = hy + 7 * PITCH + 24
    s.append(f'<text x="{PAD}" y="{ly + 10}" font-size="11" fill="{OCHRE}">Mis à jour le {fr(date.fromisoformat(days[-1]["date"]))}</text>')
    lx = W - PAD - 5 * PITCH - 34
    s.append(f'<text x="{lx - 8}" y="{ly + 10}" text-anchor="end" font-size="11" fill="{OCHRE}">Moins</text>')
    for i, color in enumerate(LEVELS.values()):
        s.append(f'<rect x="{lx + i * PITCH}" y="{ly}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"/>')
    s.append(f'<text x="{lx + 5 * PITCH + 4}" y="{ly + 10}" font-size="11" fill="{OCHRE}">Plus</text>')
    s.append("</svg>")
    open(out, "w", encoding="utf-8").write("\n".join(s) + "\n")
    print(f"{total} contributions, série {cur} j, meilleure {best} j -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
