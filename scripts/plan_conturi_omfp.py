# -*- coding: utf-8 -*-
"""scripts/plan_conturi_omfp.py — generează `core/plan_conturi_omfp.py` (planul de conturi general OMFP 1802/2014, pct.594, în forma în
vigoare) și rescrie planul cu care pornește orice firmă nouă (`tenant_template.sql`, blocul „[p97_plan_seed]”).

[deficiența 387, comanda Costin 9.1, 19.10.2026] „Plan de conturi: lipsește 609 (Reduceri comerciale primite). Planul are 184 de conturi —
compară-l integral cu OMFP 1802/2014.” Planul firmelor era o listă scrisă de mână (184 de conturi, 14 denumiri prescurtate); acum e textul
ordinului.

Sursa (nivel 1, Monitorul Oficial): `anaf_surse/omfp_1802_2014_reglementari_consolidat.html` — Reglementările contabile aprobate prin OMFP
1802/2014, forma consolidată de pe legislatie.just.ro, pct.594 „Planul de conturi general este următorul:”, cu modificările ulterioare
(OMFP 4160/2015, 166/2017, 895/2017, 470/2018, 1243/2018, 2531/2018, 3067/2018, 2493/2019, 58/2021, 85/2022, 4291/2022, 2649/2023, 981/2024,
6670/2024 — notele „(la …)” ale portalului). Se iau conturile sintetice de gradul I (3 cifre) și II (4 cifre); grupele (2 cifre) și clasele
nu sunt conturi. Funcțiunea tipărită „(A)” / „(P)” / „(A/P)” se păstrează în `core/plan_conturi_omfp.py`; conturile „Eliminat” nu intră.

Corecturile sunt o listă ÎNCHISĂ (`CORECTURI`), fiecare confruntată cu forma din Monitorul Oficial nr. 963 / 30.12.2014
(`anaf_surse/omfp_1802_2014.pdf`, scos cu `pdftotext -layout`): portalul a pierdut rândul „6651. Diferențe nefavorabile de curs valutar
legate de elementele” — continuarea lui („monetare exprimate în valută*20)”) s-a lipit de 665. Contul 6651 nu are notă de eliminare, iar
Capitolul 15 al aceluiași text consolidat îl listează („6651 Diferențe nefavorabile de curs valutar legate de elementele monetare exprimate
în valută — Cont nou”).

Uz: python scripts/plan_conturi_omfp.py            -> rescrie core/plan_conturi_omfp.py și blocul din tenant_template.sql
    python scripts/plan_conturi_omfp.py --verifica -> 0 identice / 1 diferă (garda: core/test_plan_conturi_omfp.py)
"""
import html
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURSA = os.path.join(RAD, "anaf_surse", "omfp_1802_2014_reglementari_consolidat.html")
IESIRE = os.path.join(RAD, "core", "plan_conturi_omfp.py")
SABLON = os.path.join(RAD, "tenant_template.sql")

#: (simbol, denumire, funcțiune) — rândurile pe care portalul le-a stricat la consolidare, așa cum sunt în MO 963/2014 (vezi antetul)
CORECTURI = (("665", "Cheltuieli din diferențe de curs valutar", ""),
             ("6651", "Diferențe nefavorabile de curs valutar legate de elementele monetare exprimate în valută", ""))

#: analiticele pe care aplicația le creează în planul fiecărei firme (nu sunt în ordin; OMFP pct.593 alin.(1): „Conturile sintetice din
#: planul de conturi se pot dezvolta pe conturi analitice”) — 4428.01 (NIR fără factură, DECIZII 08.10 §6) și 4428.02 (TVA din prețul de
#: raft, retest 08.10)
ANALITICE_APLICATIE = (("4428.01", "TVA neexigibilă — achiziții fără factură (NIR)"),
                       ("4428.02", "TVA neexigibilă aferentă mărfurilor (preț de vânzare)"))

_MARCAJ = "-- [p97_plan_seed] Populare automata plan de conturi OMFP la creare firma (fix radacina 10.07.2026)"
_INSERT = "INSERT INTO TENANT_PLACEHOLDER.plan_conturi (simbol, denumire, tip) VALUES\n"


def _blocuri(text_html):
    a = text_html.index("Clasa 1 - Conturi de capitaluri, provizioane")
    z = text_html.index("Capitolul 15", a)
    s = re.sub(r'<span class="(S_[A-Z_]+)"[^>]*>', lambda m: "\n@@%s@@" % m.group(1), text_html[a - 200:z])
    s = html.unescape(re.sub(r"<[^>]+>", "", s))
    return [(m.group(1), " ".join(m.group(2).split())) for m in re.finditer(r"@@(S_[A-Z_]+)@@([^@]*)", s)]


def _curata(n):
    """(denumire, funcțiune) fără notele portalului, trimiterile la note de subsol și exponenți."""
    n = re.sub(r"\s*\(la \d{2}-\d{2}-\d{4}.*$", "", n)          # nota de modificare a portalului
    n = re.sub(r"\s*-{5,}.*$", "", n)                            # nota veche „---------- Contul … a fost introdus …”
    n = re.sub(r"\*(\d+)\)\s+\*\1\).*$", "", n)                 # 4318: textul notei *1) tipărit pe rând
    f = re.search(r"\((A|P|A/P)\)", n)
    n = re.sub(r"\s*\((A|P|A/P)\)", "", n)
    n = re.sub(r"\*\d+\)|\^\d+", "", n)
    n = re.sub(r"\s*\+\s*$", "", n).strip().rstrip(".").strip()
    return n, (f.group(1) if f else "")


def extrage(text_html):
    """{simbol: (denumire, funcțiune)} — conturile de gradul I și II din pct.594, cu ultimul rând al fiecărui simbol (8031 apare o dată
    „Eliminat” și o dată cu denumirea nouă)."""
    items, cur = [], None
    for cls, b in _blocuri(text_html):
        if not b or cls.startswith("S_NTA"):
            continue
        m = re.match(r"^(\d{1,4})\.?\s+(.*)$", b)
        if m and cls == "S_PAR":
            cur = [m.group(1), m.group(2)]
            items.append(cur)
        elif b.startswith("Clasa"):
            cur = None
        elif cur is not None:
            cur[1] += " " + b
    plan = {}
    for simbol, text in items:
        if len(simbol) not in (3, 4):
            continue
        den, fn = _curata(text)
        if den.startswith("Eliminat"):
            plan.pop(simbol, None)
            continue
        plan[simbol] = (den, fn)
    for simbol, den, fn in CORECTURI:
        plan[simbol] = (den, fn)
    return dict(sorted(plan.items()))


def randeaza(plan):
    linii = ['# -*- coding: utf-8 -*-',
             '"""core/plan_conturi_omfp.py — GENERAT de `scripts/plan_conturi_omfp.py` din OMFP 1802/2014 pct.594 (forma consolidată,',
             '`anaf_surse/omfp_1802_2014_reglementari_consolidat.html`); nu se editează de mână — garda `core/test_plan_conturi_omfp.py` îl compară',
             'cu regenerarea. [deficiența 387, comanda Costin 9.1] {simbol: (denumire, funcțiunea tipărită: "A" / "P" / "A/P" / "")}."""',
             '',
             'PLAN = {']
    for s, (d, f) in plan.items():
        linii.append("    %r: (%r, %r)," % (s, d, f))
    return "\n".join(linii + ["}", ""])


def sql_plan(plan):
    randuri = [(s, d) for s, (d, _f) in plan.items()] + list(ANALITICE_APLICATIE)
    randuri.sort(key=lambda r: r[0])
    return _INSERT + ",\n".join("(%s, %s, 'Bifunctional')" % (_q(s), _q(d)) for s, d in randuri) + ";\n"


def _q(v):
    return "'%s'" % v.replace("'", "''")


def sablon_nou(sablon, plan):
    a = sablon.index(_MARCAJ + "\n") + len(_MARCAJ) + 1
    if not sablon.startswith(_INSERT, a):
        raise SystemExit("tenant_template.sql: după marcajul [p97_plan_seed] nu urmează INSERT-ul planului")
    z = sablon.index(";\n", a) + 2
    return sablon[:a] + sql_plan(plan) + sablon[z:]


def main(argv):
    plan = extrage(open(SURSA, encoding="utf-8", errors="ignore").read())
    modul = randeaza(plan)
    sablon = open(SABLON, encoding="utf-8").read()
    nou = sablon_nou(sablon, plan)
    if "--verifica" in argv:
        vechi = open(IESIRE, encoding="utf-8").read() if os.path.exists(IESIRE) else ""
        ok = vechi == modul and sablon == nou
        print("identice" if ok else "diferă — regenerează: python scripts/plan_conturi_omfp.py")
        return 0 if ok else 1
    open(IESIRE, "w", encoding="utf-8").write(modul)
    open(SABLON, "w", encoding="utf-8").write(nou)
    print("scris %s (%d conturi) și planul din %s (%d rânduri)" % (IESIRE, len(plan), SABLON, len(plan) + len(ANALITICE_APLICATIE)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
