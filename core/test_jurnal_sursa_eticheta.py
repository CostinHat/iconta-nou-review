# -*- coding: utf-8 -*-
"""GARD — deficiența 245 (retestul Costin 13.10.2026, comanda 14.10 pct.2, verbatim în DECIZII): „pe note apare «sursa: inchidere_an».
Scrie «sursa: închiderea anului» și verifică toate sursele de note afișate.”

CE FACE IMPOSIBIL: (1) o sursă de notă nouă scrisă de aplicație (`INSERT INTO … inregistrari (… sursa …)` în `core/` sau `main.py`) fără
etichetă în `jurnal_api.ETICHETE_SURSA` — scanarea citește TOATE scrierile; o sursă dată ca parametru (`%s`) trebuie rezolvată mai jos
(`_PARAMETRIZATE`), altfel testul pică și cere s-o numești; (2) ecranul care afișează codul sursei în loc de etichetă.
CE NU VEDE: o scriere construită dinamic (numele tabelului dintr-o variabilă) — azi nu există niciuna (le numără `test_scrierile_
gasite`)."""
import glob
import os
import re

from core import inchidere_an, jurnal_api

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_INSERT = re.compile(r"inregistrari \(([^)]*)\)\s*(?:\"\"\"|\")?\s*(?:\"\s*)?VALUES\s*\(([^)]*)\)")


def _apelanti_nota_cu_sursa():
    """Sursa dată ca al cincilea argument lui `repo_contabilitate.nota_cu_sursa_si_status`, la fiecare apel."""
    out = set()
    for f in _fisiere():
        t = open(f, encoding="utf-8").read()
        for m in re.finditer(r"nota_cu_sursa_si_status\(\s*([^()]*(?:\([^()]*\)[^()]*)*)\)", t):
            arg = [a.strip() for a in re.split(r",(?![^(]*\))", m.group(1))]
            if len(arg) >= 5 and not t[:m.start()].endswith("def "):          # apelurile, nu definiția
                out.add(arg[4].strip("'\""))
    return out


#: scrierile cu sursa ca parametru: fișierul -> sursele pe care le scrie (rezolvate din cod, nu presupuse)
_PARAMETRIZATE = {
    "core/inchidere_an.py": lambda: {inchidere_an.SURSA},
    "core/repo_contabilitate.py": _apelanti_nota_cu_sursa,
}


def _fisiere():
    return [f for f in sorted(glob.glob(os.path.join(RAD, "core", "*.py"))) + [os.path.join(RAD, "main.py")]
            if not os.path.basename(f).startswith("test_")]


def surse_scrise(fisiere=None):
    """{sursa: [fișier:linie]} — fiecare sursă de notă pe care o scrie codul; o sursă `%s` necunoscută -> cheia `?<fișier>:<linie>`."""
    out = {}
    for f in fisiere or _fisiere():
        rel = os.path.relpath(f, RAD)
        t = open(f, encoding="utf-8").read()
        for m in _INSERT.finditer(t):
            cols = [c.strip() for c in m.group(1).split(",")]
            if "sursa" not in cols:
                continue
            v = [x.strip() for x in m.group(2).split(",")][cols.index("sursa")]
            loc = "%s:%d" % (rel, t[:m.start()].count("\n") + 1)
            if re.fullmatch(r"'[a-z_0-9]+'", v):
                surse = {v.strip("'")}
            elif rel in _PARAMETRIZATE:
                surse = _PARAMETRIZATE[rel]()
            else:
                surse = {"?" + loc}
            for s in surse:
                out.setdefault(s, []).append(loc)
    return out


def test_scrierile_gasite():
    """Calibrare: scanarea găsește scrierile cunoscute (facturi, închiderea anului, salariile prin parametru)."""
    s = surse_scrise()
    assert {"facturi", "inchidere_an", "salarii", "manual", "horeca_z"} <= set(s) and sum(len(v) for v in s.values()) >= 25, s


def test_fiecare_sursa_scrisa_are_eticheta():
    """MUTAȚIE: `inchidere_an` scos din `ETICHETE_SURSA` -> pică."""
    fara = {s: loc for s, loc in surse_scrise().items() if s not in jurnal_api.ETICHETE_SURSA}
    assert fara == {}, fara
    assert jurnal_api.eticheta_sursa("inchidere_an") == "închiderea anului"


def test_CALIBRARE_o_scriere_noua_fara_eticheta_pica(tmp_path):
    f = tmp_path / "proba.py"
    f.write_text('cur.execute("INSERT INTO x.inregistrari (data, sursa, status) VALUES (%s, \'export_nou\', \'ciorna\')")\n'
                 'cur.execute("INSERT INTO x.inregistrari (data, sursa, status) VALUES (%s, %s, \'ciorna\')")\n', encoding="utf-8")
    s = surse_scrise([str(f)])
    assert sorted(k for k in s if k not in jurnal_api.ETICHETE_SURSA) == sorted(["?%s:2" % os.path.relpath(str(f), RAD), "export_nou"]), s


def test_ecranul_afiseaza_eticheta_nu_codul():
    """Niciun ecran nu scrie codul sursei notei (`n.sursa`) — Registrul jurnal arată `sursa_eticheta`. MUTAȚIE: `esc(n.sursa)` repus în
    firme.js -> pică."""
    rele = []
    for f in glob.glob(os.path.join(RAD, "static", "js", "**", "*.js"), recursive=True):
        for i, ln in enumerate(open(f, encoding="utf-8"), 1):
            if re.search(r"sursa: \"\s*\+\s*esc\(n\.sursa\)|esc\(n\.sursa\)", ln):
                rele.append("%s:%d" % (os.path.relpath(f, RAD), i))
    assert rele == [], rele                    # ce afișează ecranul în loc: e2e `test_def_245_sursa_notei_se_scrie_in_cuvinte`
