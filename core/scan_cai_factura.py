# -*- coding: utf-8 -*-
"""CÂTE CĂI POT NAȘTE O FACTURĂ — instrumentul (HHH1, 29.08.2026).

Garda care îl folosește: `core/test_cai_creare_factura.py`. Scanul stă SEPARAT fiindcă
calibrarea lui are nevoie de mostre de SQL, iar mostrele într-un fișier `test_*` se aprind în
două gărzi care n-au nicio treabă cu subiectul: `test_garzi_pe_text` (aserțiuni pe text) și
`test_schema_coloane` (coloane inexistente într-un SQL de probă).

DE CE EXISTĂ. R87 a legat nota contabilă de **actul** care creează factura, punând-o în
`facturi_api.creeaza_factura` — punctul unic prin care trec toate emiterile aplicației. Afirmația
*„unic"* e adevărată doar cât timp nimeni nu mai deschide o a doua ușă. Întrebarea lui Costin (HHH1)
a fost exact asta: **`_factura_din_parsat` e singura cale prin care o factură poate intra fără să
treacă prin `creeaza_factura`?** Răspunsul de azi e DA — iar gardul ăsta îl ține adevărat.

CUM MĂSOARĂ, și de ce pe AST și nu pe text: se caută nodurile `Call` către `execute` al căror prim
argument e un literal (sau o concatenare de literali) care conține `INSERT INTO` și numele tabelei
`facturi`. O căutare pe text ar fi prins și `factura_linii`, `facturi_recurente`, `efactura_primite`
și comentariile care le pomenesc. **Calibrarea o dovedește în ambele direcții**, mai jos.

CELE TREI DOMENII, numărate separat, fiindcă înseamnă lucruri diferite:
  * **PRODUCȚIE** (`core/`, `main.py`) — aici e regula. Clichet: **2**.
  * **SEED** (`date_test/seed/`) — fixturi care scriu direct în tabele. Ele sunt chiar motivul pentru
    care 19 note din 34 n-au `sursa` (măsurat la R36). Nu sunt un defect, dar nu sunt nici aplicația.
  * **TESTE** — schele. Nu se numără: un test care inserează o factură ca să verifice altceva n-are
    de ce să treacă prin actul de emitere.

CE NU FACE, DECLARAT: nu verifică dacă o cale nouă **ar trebui** să contabilizeze automat — asta e o
decizie (R91). Verifică doar că nu apare una **tăcut**.
"""
import ast
import io
import os

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _literal(nod):
    """Textul unui argument, dacă e literal sau concatenare/f-string de literali. Altfel „"."""
    if isinstance(nod, ast.Constant) and isinstance(nod.value, str):
        return nod.value
    if isinstance(nod, ast.JoinedStr):
        return "".join(v.value for v in nod.values
                       if isinstance(v, ast.Constant) and isinstance(v.value, str))
    if isinstance(nod, ast.BinOp) and isinstance(nod.op, ast.Add):
        return _literal(nod.left) + _literal(nod.right)
    if isinstance(nod, ast.BinOp) and isinstance(nod.op, ast.Mod):
        return _literal(nod.left)
    return ""


def e_insert_in_facturi(sql):
    """True dacă SQL-ul inserează în tabela `facturi` — nu în `factura_linii`, nu în
    `facturi_recurente`, nu în `efactura_primite`."""
    s = " ".join(sql.split()).upper()
    if "INSERT INTO" not in s:
        return False
    dupa = s.split("INSERT INTO", 1)[1].lstrip()
    # numele poate fi calificat: `{schema}.facturi`, `"%s".facturi`, `TENANT.facturi`
    nume = dupa.split("(")[0].split()[0] if dupa.split("(")[0].split() else ""
    nume = nume.strip('"').split(".")[-1].strip('"')
    return nume == "FACTURI"


def cai(radacina, doar=None):
    """[(fisier_relativ, functie)] pentru fiecare INSERT INTO facturi."""
    out = []
    for rad, dirs, fis in os.walk(radacina):
        if "__pycache__" in rad or "/venv" in rad:
            continue
        for f in sorted(fis):
            if not f.endswith(".py"):
                continue
            cale = os.path.join(rad, f)
            rel = os.path.relpath(cale, _RAD).replace(os.sep, "/")
            if doar and not doar(rel):
                continue
            try:
                arb = ast.parse(io.open(cale, encoding="utf-8").read())
            except SyntaxError:
                continue
            fn_de_linie = {}
            for fn in ast.walk(arb):
                if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for ln in range(fn.lineno, (fn.end_lineno or fn.lineno) + 1):
                        fn_de_linie.setdefault(ln, fn.name)
            for n in ast.walk(arb):
                if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                        and n.func.attr == "execute" and n.args):
                    continue
                if e_insert_in_facturi(_literal(n.args[0])):
                    out.append((rel, fn_de_linie.get(n.lineno, "<modul>")))
    return sorted(set(out))




# ── CALIBRAREA, cu mostrele ei. Stă aici, nu în gardă: un SQL de probă într-un fișier `test_*` se
# aprinde în `test_schema_coloane` (`facturi_recurente.nume` nu există) și în `test_garzi_pe_text`.
# Mostrele folosesc coloane REALE, ca proba să nu ceară o excepție într-o gardă vecină.
MOSTRE_DA = (
    "INSERT INTO facturi (numar) VALUES (%s)",
    "INSERT INTO {schema}.facturi (numar) VALUES (%s)",
    'INSERT INTO "%s".facturi (numar, serie) VALUES (%s,%s)',
)
MOSTRE_NU = (
    # tabelele VECINE, dintre care două încep chiar cu `facturi`
    "INSERT INTO factura_linii (factura_id) VALUES (%s)",
    "INSERT INTO facturi_recurente (tert_nume) VALUES (%s)",
    "INSERT INTO {schema}.efactura_primite (status) VALUES (%s)",
    # și ce nu e o inserare deloc
    "SELECT numar FROM facturi",
    "UPDATE facturi SET numar = %s WHERE id = %s",
)


def calibrare():
    """(cate DA recunoscute, cate NU respinse). Ambele direcții, la fiecare rulare a gărzii."""
    da = sum(1 for s in MOSTRE_DA if e_insert_in_facturi(s))
    nu = sum(1 for s in MOSTRE_NU if not e_insert_in_facturi(s))
    return da, nu
