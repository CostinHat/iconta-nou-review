# -*- coding: utf-8 -*-
"""[lotul 12, deficiența 252] GARDA: facturile deschise PRELUATE (`facturi.tip = 'preluata'`, `nomenclator_status_factura.TIP_SOLD_PRELUAT`)
stau în același tabel cu facturile firmei, dar NU sunt documente ale perioadei din iConta.eu: soldul lor e în soldurile inițiale. Fiecare
cititor al tabelului `facturi` care adună / listează facturi trebuie deci să spună ce face cu ele — să filtreze documentul fiscal
(`clauza_tip_document`, `tip = 'factura'` …), să le scoată (`clauza_fara_sold_preluat`), să le ia cu intenție (`clauza_tip_cu_incasare`:
scadențarul, potrivirea) sau să fie în lista de mai jos, cu motivul. Un cititor nou fără filtru pică aici — nu ajunge tăcut în D300, D394,
Istoric facturi sau controlul încrucișat.

Clasa (căutată cu `grep -rnE "(FROM|JOIN) [^ ]*facturi\\b" core/*.py main.py`, fără teste și migrări): 109 locuri în 45 de fișiere;
cele care citesc o factură anume (după id, după stornare, prin legătura notei) nu adună nimic și se sar (`UNU`)."""
import ast
import glob
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RE_TABEL = re.compile(r"""(FROM|JOIN)\s+(\{schema\}\.|\{s\}\.?|\{p\}|\{q\}|%s|"\s*\+\s*q\s*\+\s*"|"%s"\.)?facturi\b(?!_)""")
#: filtrul pe tipul documentului, în fereastra instrucțiunii
FILTRU = re.compile(r"clauza_tip_document|clauza_fara_sold_preluat|clauza_tip_cu_incasare|_doc_fiscal|tip\s*=\s*'(factura|borderou|preluata)'|"
                    r"tip,\s*'factura'\)\s*(=|IN|<>)|_FACTURI_FEL|tip\s*=\s*%s")
#: o factură anume (după id, prin legătura notei / a liniei / a stornării): nimic adunat
UNU = re.compile(r"WHERE\s+(\w+\.)?id\s*=\s*%|id\s*=\s*ANY|id=ANY|WHERE\s+(\w+\.)?id=%|storno_din_id\s*=\s*(%s|ANY|\w+\.id|\{a\}\.id)|"
                 r"ON\s+\w+\.id\s*=\s*\w+\.(factura_id|factura_emisa_id|factura_primita_id)|ON\s+\w+\.id\s+IN|\w+\.id\s*=\s*\{a\}\.storno_din_id|"
                 r"f2\.id\s*=\s*facturi\.transformat_in_id|WHERE\s+id\s*=\s*%%s")
#: (fișier, funcție) -> de ce citește fără filtru pe tip. Fiecare intrare e verificată că mai există (o intrare moartă pică).
PERMISE = {
    ("core/facturi_api.py", "lista_facturi"): "filtrul e în `cond` (`clauza_fara_sold_preluat`), compus înaintea instrucțiunii",
    ("core/clienti_api.py", "sterge_client"): "după `client_id`: facturile preluate n-au client_id",
    ("core/clienti_api.py", "_surse"): "lista partenerilor firmei, cu documentele lor: factura preluată apare, numită „Factură preluată” "
                                       "(`_fel_factura`)",
    ("core/repo_d406.py", "parteneri_si_localitati"): "numai localitatea partenerilor cunoscuți (factura preluată n-are localitate)",
    ("core/repo_main.py", "select_facturi_2"): "numai ciornele / documentele de recunoscut (factura preluată e „importată”)",
    ("core/repo_main.py", "select_facturi_3"): "dublura la importul e-Factura: factura din SPV deja preluată NU se mai importă (soldul ei "
                                               "e în soldurile inițiale; contarea o refuză numit)",
    ("core/repo_tva_incasare.py", "anulat_prin_stornari"): "stornările unei facturi anume (după `storno_din_id`)",
    ("core/woocommerce.py", "deja_importata"): "după `sursa_externa` „WC-…” (factura preluată are „preluare”)",
    # cerute deținătorilor în raportul p252 (lotul 12): până la aplicare, numărătorile „facturi emise necontabilizate” le numără
}


def _functia(arbore, linie):
    best = None
    for n in ast.walk(arbore):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.lineno <= linie <= n.end_lineno:
            if best is None or n.lineno > best.lineno:
                best = n
    return best.name if best else "<modul>"


def _instructiunea(arbore, src, linie):
    """Textul celei mai mici instrucțiuni (`ast.stmt` simplă: apel, atribuire, return) care cuprinde `linie` — fereastra filtrului e
    exact instrucțiunea SQL, nu și cele de după ea."""
    best = None
    for n in ast.walk(arbore):
        if isinstance(n, (ast.Expr, ast.Assign, ast.AugAssign, ast.AnnAssign, ast.Return)) and n.lineno <= linie <= n.end_lineno:
            if best is None or (n.end_lineno - n.lineno) < (best.end_lineno - best.lineno):
                best = n
    return ast.get_source_segment(src, best) if best is not None else src.splitlines()[linie - 1]


def cititori_fara_filtru(src, rel):
    """PURĂ. [(rel, funcția, linia, textul)] — instrucțiunile din `src` care citesc `facturi` în agregat fără filtru pe tip."""
    linii, arbore, out = src.splitlines(), ast.parse(src), []
    for i, l in enumerate(linii, 1):
        if l.lstrip().startswith("#") or not RE_TABEL.search(l):
            continue
        if UNU.search("\n".join(linii[i - 1:i + 2])):
            continue
        # lipiturile șirurilor SQL scrise pe mai multe rânduri („…') " \n "= 'factura'…”) nu despart filtrul
        if FILTRU.search(re.sub(r'"\s*\n\s*f?"', "", _instructiunea(arbore, src, i))):
            continue
        out.append((rel, _functia(arbore, i), i, l.strip()))
    return out


def _toate():
    out = []
    for f in sorted(glob.glob(os.path.join(RAD, "core", "*.py"))) + [os.path.join(RAD, "main.py")]:
        b = os.path.basename(f)
        if b.startswith(("test_", "migrare_")):
            continue
        out += cititori_fara_filtru(open(f, encoding="utf-8").read(), os.path.relpath(f, RAD))
    return out


def test_def_252_fiecare_cititor_al_facturilor_spune_ce_face_cu_facturile_preluate():
    """Niciun cititor nou al tabelului `facturi` fără filtru pe tip (sau fără motivul scris în PERMISE)."""
    noi = ["%s:%d %s :: %s" % (r, i, fn, t[:100]) for r, fn, i, t in _toate() if (r, fn) not in PERMISE]
    assert noi == [], "cititori ai `facturi` fără filtru pe tip (facturile preluate ar intra):\n" + "\n".join(noi)


def test_252_lista_permiselor_nu_are_intrari_moarte():
    vazute = {(r, fn) for r, fn, _i, _t in _toate()}
    assert sorted(set(PERMISE) - vazute) == []


def test_252_garda_e_calibrata():
    """Calibrarea: un SELECT agregat fără filtru e prins; cu filtrul / după id / cu clauza nomenclatorului, nu."""
    rau = 'def f(cur):\n    cur.execute("SELECT count(*) FROM facturi WHERE directie = \'emisa\'")\n'
    assert [x[1] for x in cititori_fara_filtru(rau, "x.py")] == ["f"]
    for bun in ('def f(cur):\n    cur.execute("SELECT * FROM facturi WHERE id = %s", (1,))\n',
                'def f(cur):\n    cur.execute("SELECT count(*) FROM facturi WHERE " + _nsf.clauza_tip_document("f"))\n',
                'def f(cur):\n    cur.execute(f"SELECT 1 FROM {schema}.facturi f WHERE {_nsf.clauza_fara_sold_preluat(\'f\')}")\n',
                "def f(cur):\n    cur.execute(\"SELECT 1 FROM facturi WHERE COALESCE(tip, 'factura') = 'factura'\")\n"):
        assert cititori_fara_filtru(bun, "x.py") == [], bun
