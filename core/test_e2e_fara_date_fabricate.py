# -*- coding: utf-8 -*-
"""GARD — testul de capăt la capăt nu fabrică prin SQL datele pe care aplicația trebuia să le producă (comanda Costin 11.2 pct.2: „ce
oprește repetarea”, verbatim în DECIZII „Comanda 11.2”).

DE CE: două din cele cinci „rezolvat” false de la retestul lotului 10 au aceeași cauză — testul e2e scria direct în bază exact ce trebuia
să facă aplicația, deci era verde în timp ce drumul contabilului era stricat:
  · 429: e2e-ul lotului 10 insera factura EUR, cursul și validarea notei prin SQL — propunerea reevaluării sărea tăcut facturile cu
    contarea în ciornă, iar pe producție ecranul era neschimbat;
  · 428: e2e-urile scriau perioada TVA la încasare (`INSERT tva_incasare_perioade`) de la începutul lunii și emiteau pe API — lanțul
    Date firmă -> opțiunea de azi -> sistemul de luna viitoare -> Emite factură n-a fost exercitat;
  · (aceeași familie, 439 / 425) fixtura calcula sumele precedente ca „total − rulaj lună”, adică exact presupunerea codului.

CE FACE: citește (AST) fiecare `.py` din `frontend_test/e2e/` și numără instrucțiunile SQL `INSERT INTO` / `UPDATE … SET` (orice șir,
inclusiv f-string, oriunde în fișier: `sql(...)`, `cur.execute(...)`, o variabilă) pe tabelele scrise de aplicație — orice tabel, în afara
celor de infrastructură a plasei (`INFRA`: conturile de test, legătura cont–firmă, tokenurile SPV emulate, setările platformei). Fiecare
apariție poartă, pe linia instrucțiunii (de la linia de deasupra ei până la sfârșitul ei), marcajul
`# date-de-pornire: <motiv>` — datele de PORNIRE pe care aplicația nu le poate produce altfel (un document scris cum îl scria codul de
DINAINTE de reparație, o dată în trecut, o depunere la ANAF, restaurarea stării partajate). Restul se scrie pe drumul real (ecran / API).
  · fișierele de dinainte de lotul 11 au un CLICHET (`PLAFON`, cifrele de la scrierea gărzii): nemarcatele nu cresc;
  · orice fișier care nu e în `PLAFON` (lotul 11 și tot ce vine după) are ZERO nemarcate.

LIMITĂ DECLARATĂ: (a) garda vede SQL scris în fișierele plasei; o funcție a aplicației chemată direct din test (ex. `rc.nota_...`) care
ocolește ecranul nu e SQL și nu se vede; (b) marcajul se judecă de om — garda cere motivul, nu-l poate verifica; (c) `DELETE` (curățenia)
nu se numără.
"""
import ast
import glob
import io
import os
import re

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_E2E = os.path.join(_RAD, "frontend_test", "e2e")
MARCAJ = re.compile(r"#\s*date-de-pornire:\s*(\S.{9,})")
_RE_SCRIERE = re.compile(r'(?<!DO )\b(INSERT\s+INTO|UPDATE)\s+(?:ONLY\s+)?((?:"[^"]*"|%s|\{\}|\w+)\s*\.\s*)?"?(\w+)"?\s', re.I)
#: tabelele de infrastructură a plasei (nu sunt date ale contabilului): conturile e2e, legătura cont–firmă, firma de test (tenants),
#: tokenul SPV emulat (ANAF real nu e accesibil din plasă), setările platformei
INFRA = {"public.users", "public.user_tenants", "public.tenants", "public.spv_token", "public.spv_cui_acoperit", "public.setari_platforma"}
#: [11.2 pct.2] clichetul fișierelor de dinainte de lotul 11: scrieri nemarcate măsurate la scrierea gărzii (22.10.2026); NU cresc
PLAFON = {
    "frontend_test/e2e/conftest.py": 1,
    "frontend_test/e2e/e2e_bloc_a.py": 3,
    "frontend_test/e2e/e2e_bloc_b.py": 1,
    "frontend_test/e2e/e2e_bloc_c.py": 2,
    "frontend_test/e2e/e2e_bloc_d.py": 2,
    "frontend_test/e2e/e2e_bloc_e.py": 5,
    "frontend_test/e2e/e2e_bloc_f.py": 7,
    "frontend_test/e2e/e2e_casa.py": 1,
    "frontend_test/e2e/e2e_comanda_1410.py": 2,
    "frontend_test/e2e/e2e_import_saga.py": 1,
    "frontend_test/e2e/e2e_lot10_balanta.py": 5,
    "frontend_test/e2e/e2e_lot10_c69.py": 12,
    "frontend_test/e2e/e2e_lot10_c73_public.py": 2,
    "frontend_test/e2e/e2e_lot10_compensari.py": 5,
    "frontend_test/e2e/e2e_lot10_d406.py": 1,
    "frontend_test/e2e/e2e_lot10_date_firma.py": 2,
    "frontend_test/e2e/e2e_lot10_dividende.py": 4,
    "frontend_test/e2e/e2e_lot10_inlocuire.py": 10,
    "frontend_test/e2e/e2e_lot10_migrare.py": 3,
    "frontend_test/e2e/e2e_lot10_principal.py": 1,
    "frontend_test/e2e/e2e_lot10_tva_incasare.py": 2,
    "frontend_test/e2e/e2e_lot10b_declaratii.py": 2,
    "frontend_test/e2e/e2e_lot5_plural.py": 2,
    "frontend_test/e2e/e2e_lot7.py": 1,
    "frontend_test/e2e/e2e_lot72_cont.py": 2,
    "frontend_test/e2e/e2e_lot72_contab.py": 5,
    "frontend_test/e2e/e2e_lot72_declaratii.py": 2,
    "frontend_test/e2e/e2e_lot81.py": 4,
    "frontend_test/e2e/e2e_lot82.py": 2,
    "frontend_test/e2e/e2e_lot91.py": 3,
    "frontend_test/e2e/e2e_lot92.py": 4,
    "frontend_test/e2e/e2e_lot93c.py": 1,
    "frontend_test/e2e/e2e_lot93d.py": 2,
    "frontend_test/e2e/e2e_magazin.py": 2,
}


def _text_sir(n):
    """Textul unui șir (f-string: părțile formatate devin `{}`)."""
    if isinstance(n, ast.Constant) and isinstance(n.value, str):
        return n.value
    if isinstance(n, ast.JoinedStr):
        return "".join(v.value if isinstance(v, ast.Constant) else "{}" for v in n.values)
    return None


def scrieri(src):
    """PURĂ. [(linie, tabel, marcat)] — instrucțiunile INSERT / UPDATE din fișier, în afara tabelelor INFRA."""
    t = ast.parse(src)
    linii = src.splitlines()
    parinte = {}
    for p in ast.walk(t):
        for c in ast.iter_child_nodes(p):
            parinte[c] = p
    in_fstring = {v for n in ast.walk(t) if isinstance(n, ast.JoinedStr) for v in n.values}
    out = []
    for n in ast.walk(t):
        if n in in_fstring:
            continue
        s = _text_sir(n)
        if not s:
            continue
        for m in _RE_SCRIERE.finditer(s):
            sch = (m.group(2) or "").strip()
            tabel = ("public." if sch.lower().startswith("public") else "") + m.group(3).lower()
            if tabel in INFRA:
                continue
            st = n
            while st in parinte and not isinstance(st, ast.stmt):
                st = parinte[st]
            a, b = (st.lineno, st.end_lineno) if isinstance(st, ast.stmt) and not isinstance(
                st, (ast.With, ast.For, ast.If, ast.Try, ast.FunctionDef, ast.While)) else (n.lineno, n.end_lineno)
            fereastra = linii[max(0, a - 2):b]
            out.append((n.lineno, tabel, any(MARCAJ.search(x) for x in fereastra)))
    return sorted(out)


def masoara():
    """{fișier: [(linie, tabel)] nemarcate} pe toată plasa."""
    out = {}
    for f in sorted(glob.glob(os.path.join(_E2E, "*.py"))):
        rel = os.path.relpath(f, _RAD)
        out[rel] = [(ln, tb) for ln, tb, mk in scrieri(io.open(f, encoding="utf-8").read()) if not mk]
    return out


def abateri(stare, plafon):
    """PURĂ. Fișierele peste plafon (cele fără plafon: peste zero) + plafoanele stale."""
    rele = []
    for f, lst in sorted(stare.items()):
        p = plafon.get(f, 0)
        if len(lst) > p:
            rele.append("%s: %d scrieri SQL nemarcate (plafon %d): %s — e2e-ul reface pașii contabilului pe ecran / API; o scriere directă e "
                        "admisă numai pentru datele de pornire, cu `# date-de-pornire: <motiv>`" % (
                            f, len(lst), p, ", ".join("linia %d %s" % x for x in lst)))
        elif len(lst) < p:
            rele.append("%s: %d nemarcate, sub plafonul %d — coboară PLAFON (clichetul nu urcă înapoi)" % (f, len(lst), p))
    for f in sorted(set(plafon) - set(stare)):
        rele.append("%s: în PLAFON, dar fișierul nu mai există — scoate-l" % f)
    return rele


def test_e2e_nu_fabrica_prin_sql_datele_aplicatiei():
    """Comanda 11.2 pct.2. MUTAȚIE: un `sql('INSERT INTO "%s".facturi …')` nemarcat într-un e2e_lot11_*.py -> pică."""
    rele = abateri(masoara(), PLAFON)
    assert not rele, "\n".join(rele)


def test_garda_datelor_fabricate_nu_e_vida():
    """Anti-vacuu: pică pe fragmente sintetice rele, trece pe unul bun."""
    bun = ('def t(f):\n'
           '    s = f["schema"]\n'
           '    # date-de-pornire: nota scrisă cum o scria codul de dinainte de 438 (documentul vechi)\n'
           '    sql(\'UPDATE "%s".inregistrari SET document_ref = %%s WHERE id = 1\' % s, ("Bon",))\n'
           '    sql("INSERT INTO public.users (email) VALUES (%s)", ("x",))\n'
           '    sql("INSERT INTO public.declaratii_depuse (tenant_id) VALUES (1)")   # date-de-pornire: depunerea la ANAF, din afara plasei\n'   # fixtura-sintetica-ok: șir dat scanerului, nu se execută
           '    sql(\'DELETE FROM "%s".facturi\' % s)\n'
           '    sql("INSERT INTO x (a) VALUES (1) ON CONFLICT (a) DO UPDATE SET a = 1")  # date-de-pornire: tabelul x, pornire probă\n')
    assert [(t, m) for _, t, m in scrieri(bun)] == [("inregistrari", True), ("public.declaratii_depuse", True), ("x", True)], scrieri(bun)
    rele = {
        "INSERT nemarcat": 'sql(\'INSERT INTO "%s".facturi (numar) VALUES (1)\' % s)\n',
        "UPDATE validare": 'sql(\'UPDATE "%s".inregistrari SET status = \\\'validata\\\' WHERE id = 1\' % s)\n',
        "f-string": 'cur.execute(f\'INSERT INTO "{s}".tva_incasare_perioade (de_la) VALUES (1)\')\n',
        "variabilă": 'Q = (\'INSERT INTO "%s".miscari_stoc \'\n     \'(cantitate) VALUES (1)\')\n',
        "marcaj fără motiv": 'sql(\'INSERT INTO "%s".facturi (n) VALUES (1)\' % s)  # date-de-pornire:\n',
    }
    for ce, src in rele.items():
        assert [x for x in scrieri(src) if not x[2]], "garda trece pe: %s" % ce
    st = {"frontend_test/e2e/e2e_lot11_z.py": [(3, "facturi")], "frontend_test/e2e/e2e_vechi.py": [(1, "facturi"), (2, "facturi")]}
    assert abateri(st, {"frontend_test/e2e/e2e_vechi.py": 2})[0].startswith("frontend_test/e2e/e2e_lot11_z.py"), "fișier nou peste zero"
    assert abateri(dict(st, **{"frontend_test/e2e/e2e_lot11_z.py": []}), {"frontend_test/e2e/e2e_vechi.py": 2}) == []
    assert abateri(dict(st, **{"frontend_test/e2e/e2e_lot11_z.py": []}), {"frontend_test/e2e/e2e_vechi.py": 1}), "peste plafon"
    assert abateri(dict(st, **{"frontend_test/e2e/e2e_lot11_z.py": []}), {"frontend_test/e2e/e2e_vechi.py": 3}), "plafon stale"


if __name__ == "__main__":
    for f, lst in masoara().items():
        if lst:
            print('    "%s": %d,' % (f, len(lst)))
