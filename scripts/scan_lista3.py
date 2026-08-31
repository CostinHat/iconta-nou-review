# -*- coding: utf-8 -*-
"""scripts/scan_lista3.py — lista 3, DERIVATA din registru, nu numarata cu mana.

Cerut de Costin, 31.08.2026: *«Cifra "opt artefacte" vine din premisa care a cazut: e un numar
derivat reafirmat in proza, care nu se mai regenereaza din nimic — aceeasi clasa ca antetul T02. Se
aplica regula ei propriei liste: ori se genereaza, ori se sterge.»*

Aici raspunsul e SE GENEREAZA. Titlul listei e util — spune dintr-o privire cat a mai ramas — deci
nu se sterge; se produce din coloana `stare` a tabelelor, care e singurul loc unde starea fiecarui
artefact se scrie o data.

CE CITESTE, exact: tabelele din `CONFORMITATE.md` care au capul
`| artefact | A producator | B ruta | C ecran | stare |`. Coloana a cincea da starea; primul cuvant
al ei (dupa curatarea ingrosarii) e verdictul.

MODURILE DE ESEC, scrise inainte de prima rulare:
  1. **Vede doar tabelele cu cele CINCI coloane.** Tabelul vechi de cauze are doua coloane si NU se
     numara — el pastreaza cauza masurata la descoperire, nu starea de azi. Daca cineva scrie un
     artefact NOU doar acolo, scanul nu-l vede. Deci cifra e plafon INFERIOR pe artefacte.
  2. **Nu deosebeste «DESCHIS» de «DESCHIS pe o firma».** `R3` e reparat ca derivare si deschis ca
     proba — starea lui e o propozitie, nu o eticheta. Se numara dupa primul cuvant, iar restul
     propozitiei ramane de citit de om.
  3. **Nu verifica daca starea scrisa e ADEVARATA.** Un rand care zice REPARAT fara sa fie n-are cum
     sa fie prins de aici; pentru asta sunt gardile fiecarui artefact.
"""
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONF = os.path.join(RAD, "CONFORMITATE.md")

CAP = "| artefact | A producător | B rută | C ecran | stare |"

#: Nomenclator INCHIS al verdictelor. Un al cincilea cuvant in coloana `stare` pica, in loc sa fie
#: numarat tacut ca «altceva» — o stare noua e o decizie, nu o scapare de tipar.
VERDICTE = ("DESCHIS", "REPARAT", "FALS")


def _curata(s):
    return re.sub(r"[*`_]", "", s).strip()


def randuri(text=None):
    """[{artefact, stare, verdict}] — din toate tabelele cu cele cinci coloane."""
    t = text if text is not None else io.open(CONF, encoding="utf-8").read()
    out = []
    for m in re.finditer(re.escape(CAP), t):
        p = m.start()
        capat = t.index("\n\n", p)
        for ln in t[p:capat].split("\n")[2:]:
            col = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(col) != 5:
                continue
            stare = _curata(col[4])
            cuv = re.split(r"[\s.,·]", stare)[0].upper() if stare else ""
            out.append({"artefact": _curata(col[0]), "stare": stare, "verdict": cuv})
    return out


def capete_de_tabel(text=None):
    """{tuplu de coloane} — capetele TUTUROR tabelelor din registru.

    Exista ca aserttiunile despre tabele sa se poata face pe o MULTIME calculata, nu cautand un sir
    in document: `"| artefact | cauza |" in doc` intreaba «apare undeva», iar un cap citat intr-un
    paragraf ar trece la fel de bine ca unul real (clichet 50 / METODA §23).
    """
    t = text if text is not None else io.open(CONF, encoding="utf-8").read()
    out = set()
    linii = t.split(chr(10))
    for i, ln in enumerate(linii[:-1]):
        s, urm = ln.strip(), linii[i + 1].strip()
        if not (s.startswith("|") and urm.startswith("|")):
            continue
        if not set(urm) <= set("|-: "):      # a doua linie e separatorul de tabel
            continue
        col = tuple(_curata(c) for c in s.strip("|").split("|"))
        if len(col) >= 2:
            out.add(col)
    return out


def proba_datelor():
    """Tabelul de proba a datelor pentru randurile DESCHISE, GENERAT din masuratoare.

    Costin, 31.08.2026: *«O afirmatie al carei adevar depinde de un calificativ masurat ori se
    regenereaza din instrument, ori nu se scrie.»* Tabelul asta a fost scris de mana o data si a
    purtat, in aceeasi zi, un calificativ cazut: «niciuna n-are doua exercitii consecutive» — adevarat
    doar cu «CU RULAJE», care lipsea. Nu numarul era gresit, ci ce anume numara.

    Se masoara pe firmele reale. Cere baza; fara ea nu se poate produce, si atunci NU SE SCRIE nimic
    — un tabel de proba generat pe zero firme ar fi o afirmatie despre o lume goala.
    """
    from core import bilant_api as _ba
    from core import categorie_marime as _cm
    from core import db
    from psycopg2.extras import RealDictCursor

    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants WHERE activ ORDER BY id")
        scheme = [r[0] for r in cur.fetchall()]
    if not scheme:
        raise ValueError("zero firme active — proba datelor n-are pe ce se masura")

    cu_rulaje, cu_note, incadrate = [], [], []
    for s in scheme:
        with db.get_conn(s) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                ani_rulaje = [a for a in range(2023, 2028) if _ba._rulaje_67(cur, s, a)]
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT EXTRACT(YEAR FROM data)::int FROM {}.inregistrari "
                            "WHERE status = 'validata'".format(s))
                ani_note = sorted(r[0] for r in cur.fetchall())
            cat = _cm.categorie(conn, s, max(ani_rulaje) if ani_rulaje else 2026)
        if any(a - 1 in ani_rulaje for a in ani_rulaje):
            cu_rulaje.append(s)
        if any(a - 1 in ani_note for a in ani_note):
            cu_note.append(s)
        if (cat.get("categorie") if isinstance(cat, dict) else cat) != "nedeterminata":
            incadrate.append(s)

    return {"firme": len(scheme), "cu_doua_exercitii_cu_rulaje": cu_rulaje,
            "cu_doua_exercitii_cu_note": cu_note, "incadrate": incadrate}


def proba_md(p=None):
    """Tabelul, ca markdown. Un singur loc care spune cat de departe sunt randurile deschise."""
    p = proba_datelor() if p is None else p
    n = p["firme"]
    return "\n".join([
        "| rândul | ce cere ca să se poată delimita | măsurat acum | distanța |",
        "|---|---|---|---|",
        "| **Note explicative** | categoria de mărime a entității (OMFP 1802/2014 pct. 20-21: "
        "microentitățile sunt scutite) | **%d din %d** firme se pot încadra | aceeași ca rândul de "
        "mai jos — categoria e precondiția lui |" % (len(p["incadrate"]), n),
        "| **categoria de mărime / R3** | două exerciții consecutive **cu rulaje de clasă 6/7** "
        "(pct. 13 alin. (2)-(3)) | **%d din %d** firme le au. *Cu NOTE validate în două exerciții "
        "consecutive, dar fără rulaje: %d* | un exercițiu de rulaje 6/7 pe oricare dintre cele %d "
        "firme cu note |" % (len(p["cu_doua_exercitii_cu_rulaje"]), n, len(p["cu_doua_exercitii_cu_note"]),
                             len(p["cu_doua_exercitii_cu_note"])),
    ])


def numara(text=None):
    """{verdict: n} + `total`. Verdictele sunt un nomenclator INCHIS."""
    rs = randuri(text)
    d = {v: 0 for v in VERDICTE}
    necunoscute = []
    for r in rs:
        if r["verdict"] in d:
            d[r["verdict"]] += 1
        else:
            necunoscute.append((r["artefact"], r["verdict"]))
    d["total"] = len(rs)
    d["necunoscute"] = necunoscute
    return d


def titlu(text=None):
    """Titlul listei 3, GENERAT. Un singur loc care spune cat a mai ramas."""
    d = numara(text)
    if d["necunoscute"]:
        raise ValueError("verdicte în afara nomenclatorului: %r" % d["necunoscute"])
    if d["DESCHIS"] == 0:
        cat = "**niciun artefact deschis**"
    elif d["DESCHIS"] == 1:
        cat = "**un artefact deschis**"
    else:
        cat = "**%d artefacte deschise**" % d["DESCHIS"]
    return ("#### Lista 3 — nu ies, DIN VINA APLICAȚIEI — %s din %d urmărite "
            "*(cifra e generată din coloana `stare`, cu `scripts/scan_lista3.py`)*"
            % (cat, d["total"]))


def _main():
    d = numara()
    print(titlu())
    print()
    for r in randuri():
        print("  %-9s %s" % (r["verdict"], r["artefact"][:66]))
    print("\nDESCHIS %d · REPARAT %d · FALS %d · total %d"
          % (d["DESCHIS"], d["REPARAT"], d["FALS"], d["total"]))
    if d["necunoscute"]:
        print("VERDICTE NECUNOSCUTE:", d["necunoscute"])
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
