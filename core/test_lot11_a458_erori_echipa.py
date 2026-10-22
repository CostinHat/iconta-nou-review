# -*- coding: utf-8 -*-
"""[lotul 11, deficiența 458 — comanda Costin 11.3 pct.6] „în Erori — echipa: text suprapus peste nume; regenerările automate ale
aplicației apar ca greșeli ale administratorului; numerele de respingeri nu se adună cu rândurile.”

Aici: părțile (2) și (3), pe server (partea (1), așezarea, e în `core/test_lot11_a458_erori_ecran.py`).

CAUZA (2), măsurată pe cabinetul de test „Cabinet Test Sesiunea B SRL”, producție, numai citire, 22.10.2026: „Generează din nou” /
„Înlocuiește” (`uc_coada.coada_adauga` -> `coada_api.inlocuieste`) scoate declarația veche din coadă scriindu-i `stare = 'respinsa'`,
`respins_de_id` = cine a generat-o din nou și motivul „Înlocuită de declarația generată din nou (…)”. `asistenti_api.calitate` număra
orice rând `respinsa` ca respingere a pregătitorului: administratorul apărea cu „Înlocuită de declarația generată din nou … 3×
sistematic”. Autorul NU deosebește înlocuirea (e același câmp, același om); o deosebește structura deja existentă: elementul înlocuit
are un urmaș pe aceeași declarație (firmă, tip, perioadă) creat în ACEEAȘI tranzacție — `creat_la` al urmașului = `respins_la` al
lui (`now()` e ora tranzacției) — iar înlocuirea atinge numai declarații, niciodată note (`fel IS DISTINCT FROM 'nota'`, ca
`inlocuieste`). Respingerea omului e o cerere separată: nu are urmaș în aceeași tranzacție.

CAUZA (3): numărul de lângă nume („5 respinse”) număra PREGĂTIRI respinse (`sql_cheie_pregatire`), iar rândurile numărau RÂNDURI de
coadă pe motiv (un NIR = 4 note = 4 rânduri) și pe alt interval (`creat_la` al rândului, nu al pregătirii): Ana 5 vs Σ rânduri 8,
administratorul 1 vs Σ 4. Acum totalul și rândurile vin din aceeași listă de pregătiri (o singură interogare): fiecare pregătire
respinsă e un rând al motivului ULTIMEI ei respingeri, iar totalul = Σ rândurilor.

Temei: N/A — indicator intern al cabinetului (nu regulă fiscală).
"""
import ast
import io
import os
import re

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_lot11_a458"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOTIV_INLOCUIRE = "Înlocuită de declarația generată din nou (Probă)."


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def tx():
    """Schema efemeră din `tenant_template.sql`, firma ei în cabinetul de test, totul într-o tranzacție ANULATĂ."""
    if not _db_ok():
        pytest.skip("DB indisponibil")
    p = _db.pool()
    conn = p.getconn()
    cur = conn.cursor()
    cur.execute("SELECT id, accounting_firm_id FROM public.users WHERE email='asistent@prisma-cont.test'")
    r = cur.fetchone()
    if not r:
        p.putconn(conn)
        pytest.skip("utilizatorul de test lipsește")
    asist, cab = r
    cur.execute("SELECT id FROM public.users WHERE accounting_firm_id=%s AND poate_valida AND id<>%s ORDER BY id LIMIT 1", (cab, asist))
    valid = cur.fetchone()[0]
    cur.execute("UPDATE public.users SET poate_pregati=true, poate_valida=false, activ=true WHERE id=%s", (asist,))
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
    cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
    cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id) VALUES (%s,'ZT Lot 11 A458 SRL',%s) RETURNING id",
                (SCH, cab))
    tid = cur.fetchone()[0]
    cur.execute('SET LOCAL search_path TO "%s", public' % SCH)
    try:
        yield conn, cur, tid, cab, asist, valid
    finally:
        conn.rollback()
        cur = conn.cursor()
        cur.execute("RESET iconta.utilizator")
        cur.execute("RESET search_path")
        conn.commit()
        p.putconn(conn)


def _ca(cur, uid):
    cur.execute("SELECT set_config('iconta.utilizator', %s, false)", (str(uid),))


def _nota(conn, desc, suma, doc):
    from core import jurnal_api
    return jurnal_api.creeaza(conn, SCH, desc, "2026-10-05", [{"debit": "4111", "credit": "707", "suma": suma,
                                                               "partener_nume": "PARTENER PROBA SRL"}], document_ref=doc)["id"]


def _declaratie(conn, cab, tid, uid, luna):
    """O declarație în coadă pe drumul aplicației (`coada_api.adauga_in_coada`, ca `uc_coada.coada_adauga`); an sintetic 2099."""
    from core import coada_api as c
    r = c.adauga_in_coada(conn, cab, tid, "d300", 2099, {"xml": "<x/>"}, creat_de=str(uid), creat_de_id=uid, luna=luna)
    assert r["ok"], r
    return r["coada_id"]


def _genereaza_din_nou(conn, cab, tid, uid, coada_id, luna):
    """„Generează din nou”: exact pașii din `uc_coada.coada_adauga` — elementul vechi iese (`inlocuieste`) și cel nou intră, în ACEEAȘI
    tranzacție (garda structurală e `test_inlocuirea_si_urmasul_sunt_in_aceeasi_tranzactie`)."""
    from core import coada_api as c
    with conn.cursor() as cur:
        assert c.inlocuieste(cur, coada_id, cab, uid, MOTIV_INLOCUIRE)
    return _declaratie(conn, cab, tid, uid, luna)


def _suma(cal):
    return sum(t["nr"] for t in cal["tipare"])


def test_def_458_generarea_din_nou_nu_e_o_respingere(tx):
    """ROȘU înainte: `calitate` număra elementul înlocuit ca respingere a pregătitorului (respinse +1, rândul „Înlocuită de declarația
    generată din nou” în tipare); centralizatorul îl număra la „respinse”; jurnalul îl arăta „a respins”. MUTAȚIA: `sql_inlocuita` ->
    `FALSE` (orice `respinsa` e respingere) -> pică."""
    from core import asistenti_api as A
    conn, cur, tid, cab, asist, valid = tx
    c0, cen0 = A.calitate(conn, cab, asist), A.centralizator(conn, cab)["totaluri"]["respinse"]
    vechi = _declaratie(conn, cab, tid, asist, 1)
    nou = _genereaza_din_nou(conn, cab, tid, asist, vechi, 1)
    nou2 = _genereaza_din_nou(conn, cab, tid, asist, nou, 1)
    cal = A.calitate(conn, cab, asist)
    assert cal["respinse"] - c0["respinse"] == 0, cal                   # „regenerările … apar ca greșeli”
    assert not [t for t in cal["tipare"] if t["motiv"] == MOTIV_INLOCUIRE], cal["tipare"]
    assert cal["evaluate"] - c0["evaluate"] == 0                         # o înlocuire nu e o decizie asupra lucrării
    assert cal["pregatite"] - c0["pregatite"] == 1                       # aceeași pregătire (firmă, tip, perioadă)
    assert A.centralizator(conn, cab)["totaluri"]["respinse"] - cen0 == 0
    ev = [e for e in A.jurnal(conn, cab)["evenimente"] if e["coada_id"] in (vechi, nou, nou2)]
    assert not [e for e in ev if e["actiune"] == "respins"], ev          # nu „a respins”: a generat din nou
    act = [r for r in A.activitate(conn, cab, asist)["activitate"] if r["id"] in (vechi, nou)]
    assert act and not [r for r in act if r["a_respins"]], act


def test_def_458_respingerea_omului_ramane_respingere(tx):
    """Contraproba: o declarație respinsă de cel care validează (`coada_api.respinge`, cererea lui separată) rămâne respingere, cu
    motivul ei. MUTAȚIA: `sql_inlocuita` -> `TRUE` -> pică."""
    from core import asistenti_api as A, coada_api as c
    conn, cur, tid, cab, asist, valid = tx
    c0 = A.calitate(conn, cab, asist)
    d = _declaratie(conn, cab, tid, asist, 2)
    assert c.respinge(conn, d, str(valid), "lipsește F1A5", respins_de_id=valid, cabinet_id_apelant=cab)["ok"]
    cal = A.calitate(conn, cab, asist)
    assert cal["respinse"] - c0["respinse"] == 1
    assert [t["nr"] for t in cal["tipare"] if t["motiv"] == "lipsește F1A5"] == [1]


def test_def_458_totalul_respingerilor_e_suma_randurilor(tx):
    """ROȘU înainte: o factură cu două note respinsă o dată = 1 pregătită respinsă, dar rândul motivului număra 2 (rândurile de coadă);
    retrimisă și respinsă din nou cu alt motiv, rândurile erau 2 + 1 = 3 lângă „1 respinsă”. Acum: un rând, al ultimei respingeri, iar
    totalul = Σ rândurilor (aceeași listă). MUTAȚIA: totalul din altă numărătoare decât rândurile -> pică."""
    from core import asistenti_api as A, coada_api as c
    from core.test_lot0710_p2 import _factura_cu_doua_note as _f2
    import core.test_lot0710_p2 as _p2
    conn, cur, tid, cab, asist, valid = tx
    _ca(cur, asist)
    vechi_sch, _p2.SCH = _p2.SCH, SCH            # ajutorul celuilalt fișier scrie pe schema lui; aici, pe a noastră
    try:
        _fid, n1, n2 = _f2(conn, cur)
    finally:
        _p2.SCH = vechi_sch
    cid = c.pune_notele_in_coada(conn, cab, tid, asist)[0]["coada_id"]
    _declaratie(conn, cab, tid, asist, 4)        # o lucrare încă nedecisă: totalul nu e „pregătite − aprobate”
    assert c.respinge(conn, cid, str(valid), "lipsește avizul", respins_de_id=valid, cabinet_id_apelant=cab)["ok"]
    cal1 = A.calitate(conn, cab, asist)
    assert cal1["respinse"] == _suma(cal1), (cal1["respinse"], cal1["tipare"])
    assert [t["nr"] for t in cal1["tipare"] if t["motiv"] == "lipsește avizul"] == [1]   # un document, nu două note
    cid2 = c.retrimite_nota(conn, cab, tid, n2, asist, confirma=True)["coada_id"]
    assert c.respinge(conn, cid2, str(valid), "data greșită", respins_de_id=valid, cabinet_id_apelant=cab)["ok"]
    cal = A.calitate(conn, cab, asist)
    assert cal["respinse"] - cal1["respinse"] == 0                       # aceeași lucrare, respinsă de două ori
    assert cal["respinse"] == _suma(cal), (cal["respinse"], cal["tipare"])
    mot = {t["motiv"]: t["nr"] for t in cal["tipare"]}
    assert mot.get("data greșită") == 1 and "lipsește avizul" not in mot, mot   # rândul ultimei respingeri
    # și ecranul „Erori — echipa” (același calcul): numărul de lângă nume = Σ rândurilor lui. Premisa întâi: pregătitorul probei e pe
    # ecran (o listă goală ar trece comparația de mai jos fără să compare nimic)
    ech = A.erori_echipa(conn, cab)["asistenti"]
    assert {a["id"] for a in ech} >= {asist}, ech
    assert [(a["id"], a["respinse"]) for a in ech] == [(a["id"], sum(t["nr"] for t in a["tipare"])) for a in ech], ech


def _in_aceeasi_tranzactie(src):
    """`coada_api.inlocuieste` și `coada_api.adauga_in_coada` chemate în ACELAȘI bloc `with db.get_conn()` din `coada_adauga`."""
    fn = next(n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef) and n.name == "coada_adauga")

    def _apel(n, nume):
        return isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == nume

    blocuri = [w for w in ast.walk(fn) if isinstance(w, ast.With) and any(_apel(i.context_expr, "get_conn") for i in w.items)]
    return any(any(_apel(x, "inlocuieste") for x in ast.walk(w)) and any(_apel(x, "adauga_in_coada") for x in ast.walk(w))
               for w in blocuri)


def test_garda_tranzactiei_vede_despartirea():
    """Mutația gărzii de mai jos, permanentă: aceleași două apeluri în DOUĂ tranzacții -> garda spune „nu”."""
    despartit = ("def coada_adauga(date, ctx):\n    with db.get_conn() as conn:\n        coada_api.inlocuieste(cur, 1, 2, 3, 'm')\n"
                 "    with db.get_conn() as conn:\n        coada_api.adauga_in_coada(conn, 1, 2, 'd300', 2099, {}, '3')\n")
    impreuna = despartit.replace("    with db.get_conn() as conn:\n        coada_api.adauga", "        coada_api.adauga")
    assert not _in_aceeasi_tranzactie(despartit) and _in_aceeasi_tranzactie(impreuna)


def test_inlocuirea_si_urmasul_sunt_in_aceeasi_tranzactie():
    """GARDA structurală a deosebirii (2): în `uc_coada.coada_adauga`, `coada_api.inlocuieste` și `coada_api.adauga_in_coada` stau în
    ACELAȘI bloc `with db.get_conn() as conn` — de aici `creat_la` al urmașului = `respins_la` al celui înlocuit. Dacă cineva le
    desparte în două tranzacții, `asistenti_api.sql_inlocuita` n-ar mai recunoaște înlocuirea: garda pică înainte."""
    src = io.open(os.path.join(RAD, "core", "uc_coada.py"), encoding="utf-8").read()
    assert _in_aceeasi_tranzactie(src), "inlocuieste și adauga_in_coada nu mai sunt în aceeași tranzacție (același `with db.get_conn()`)"


def test_inlocuirea_nu_atinge_notele(tx):
    """Înlocuirea atinge numai declarațiile (deosebirea din `sql_inlocuita` presupune asta) — pe RÂNDUL din coadă, nu pe textul SQL-ului:
    `inlocuieste` pe un element-notă activ întoarce False, iar rândul rămâne cum era. Contraproba: pe o declarație activă iese.
    MUTAȚIA: `AND fel IS DISTINCT FROM 'nota'` scos din `coada_api.inlocuieste` -> nota iese din coadă -> pică."""
    from core import coada_api as c
    conn, cur, tid, cab, asist, valid = tx
    _ca(cur, asist)
    _nota(conn, "Notă probă A458", 100, "A458-1")
    puse = c.pune_notele_in_coada(conn, cab, tid, asist)
    assert len(puse) == 1, puse
    cid = puse[0]["coada_id"]
    cur.execute("SELECT fel, stare, respins_la FROM public.declaratii_coada WHERE id = %s", (cid,))
    inainte = cur.fetchone()
    assert inainte[0] == "nota" and inainte[1] in c.STARI_ACTIVE and inainte[2] is None, inainte
    assert c.inlocuieste(cur, cid, cab, asist, MOTIV_INLOCUIRE) is False
    cur.execute("SELECT fel, stare, respins_la FROM public.declaratii_coada WHERE id = %s", (cid,))
    assert cur.fetchone() == inainte
    d = _declaratie(conn, cab, tid, asist, 5)
    assert c.inlocuieste(cur, d, cab, asist, MOTIV_INLOCUIRE) is True
    cur.execute("SELECT stare FROM public.declaratii_coada WHERE id = %s", (d,))
    assert cur.fetchone()[0] == "respinsa"


def test_activitatea_gaseste_lucrarile_dupa_id(tx):
    """[găsit la 458, același ecran] Coada scrie în `creat_de` / `respins_de` id-ul omului (`str(uid)`), iar „Declarații lucrate” căuta
    numai emailul și numele: lista era goală pe orice cabinet (cabinetul de test, producție, citire 22.10.2026: 0 rânduri pentru ambii
    oameni, din 39 de rânduri ale lor), iar semnalul „patru ochi” nu se putea aprinde. MUTAȚIA: `str(actor["id"])` scos din
    `_identificatori` -> pică."""
    from core import asistenti_api as A, coada_api as c
    conn, cur, tid, cab, asist, valid = tx
    d = _declaratie(conn, cab, tid, asist, 3)
    assert c.respinge(conn, d, str(valid), "motiv probă", respins_de_id=valid, cabinet_id_apelant=cab)["ok"]
    mea = [r for r in A.activitate(conn, cab, asist)["activitate"] if r["id"] == d]
    assert len(mea) == 1 and mea[0]["a_pregatit"] and not mea[0]["a_respins"], mea
    a_lui = [r for r in A.activitate(conn, cab, valid)["activitate"] if r["id"] == d]
    assert len(a_lui) == 1 and a_lui[0]["a_respins"] and not a_lui[0]["a_pregatit"], a_lui


#: [458, generalizare] numărătorile de respingeri pe declarații din fișierele altor subagenți, care încă nu deosebesc înlocuirea (patch-ul
#: exact e în raportul lotului 11, A458). Clichet: un loc nou pică; un loc reparat pică până e scos de aici.
DE_REPARAT = set()   # [lotul 11, T2] capacitate / sinteza_cabinet / tipare reparate (`coada_api.sql_inlocuita`)
_RESPINGERE = __import__("re").compile(r"respins_la IS NOT NULL|respins_la::date|respins_la\s*>=|stare\s*=\s*'respinsa'")


def test_orice_numaratoare_de_respingeri_pe_declaratii_deosebeste_inlocuirea():
    """GARDA de clasă (458 (2)): orice funcție din `core/` care citește din `declaratii_coada` o respingere (`respins_la` / `stare =
    'respinsa'`) pe declarații folosește `asistenti_api.sql_inlocuita` — altfel „Generează din nou” se numără ca greșeală. Scutite: cele
    numai pe note (înlocuirea nu atinge notele) și scrierile (`UPDATE … SET`). MUTAȚIA: `sql_inlocuita` scos din `calitate` -> pică."""
    import glob
    gasite, citiri = _numaratori_de_respingeri(sorted(glob.glob(os.path.join(RAD, "core", "*.py"))))
    # premisa: garda vede citirile de respingeri pe declarații (altfel `gasite == set()` ar trece pe un scan care nu vede nimic)
    assert citiri >= {("asistenti_api.py", "calitate"), ("asistenti_api.py", "centralizator")}, citiri
    assert gasite == DE_REPARAT, ("noi (de reparat acum)", gasite - DE_REPARAT, "reparate (scoate-le din DE_REPARAT)", DE_REPARAT - gasite)


def _nume_apel(x):
    return getattr(x.func, "attr", None) or getattr(x.func, "id", None)


def _sql_uri(fn):
    """Textele SQL din funcție, pe NOD (constantele șir și f-string-urile), fără docstringuri: o respingere pomenită într-un comentariu
    sau în documentație nu e o citire."""
    doc = {id(s.value) for s in ast.walk(fn) if isinstance(s, ast.Expr) and isinstance(s.value, (ast.Constant, ast.JoinedStr))}
    sub_f = {id(v) for j in ast.walk(fn) if isinstance(j, ast.JoinedStr) for v in j.values}
    for x in ast.walk(fn):
        if id(x) in doc or id(x) in sub_f:
            continue
        if isinstance(x, ast.JoinedStr):
            yield "".join(v.value if isinstance(v, ast.Constant) else "{}" for v in x.values)
        elif isinstance(x, ast.Constant) and isinstance(x.value, str):
            yield x.value


def _numaratori_de_respingeri(fisiere):
    """-> (funcțiile care NUMĂRĂ respingeri pe declarații fără `sql_inlocuita`, toate funcțiile care citesc o respingere din coadă).

    Pe structură: o funcție citește coada dacă unul din SQL-urile ei (nod șir) numește tabelul `declaratii_coada`; o respingere = un SQL
    al ei care se potrivește cu `_RESPINGERE`. Scutite: funcția care cheamă `sql_inlocuita(...)` (nod `Call`) sau e chiar ea; SQL-ul care e
    o scriere (`UPDATE …`); SQL-ul restrâns la note (`fel = 'nota'`, înlocuirea nu atinge notele)."""
    gasite, citiri = set(), set()
    for f in fisiere:
        b = os.path.basename(f)
        if b.startswith(("test_", "migrare_")):
            continue
        for n in ast.walk(ast.parse(io.open(f, encoding="utf-8").read())):
            if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            sql = list(_sql_uri(n))
            if not any(re.search(r"\bdeclaratii_coada\b", s) for s in sql):
                continue
            resp = [s for s in sql if _RESPINGERE.search(s)]
            if not resp:
                continue
            citiri.add((b, n.name))
            if n.name == "sql_inlocuita" or any(isinstance(x, ast.Call) and _nume_apel(x) == "sql_inlocuita" for x in ast.walk(n)):
                continue
            if all(re.match(r"\s*UPDATE\b", s, re.I) or re.search(r"\bfel\s*=\s*'nota'", s) for s in resp):
                continue                        # scrierea respingerii, sau numai notele
            gasite.add((b, n.name))
    return gasite, citiri


def test_garda_numaratorii_prinde_forma_veche():
    """Garda de clasă nu e tautologică: o numărătoare fără `sql_inlocuita` e prinsă; scrierea, numărătoarea pe note și cea cu
    `sql_inlocuita` nu sunt; o respingere pomenită numai în docstring nu e citire."""
    import tempfile
    cod = ('def rau(cur):\n    cur.execute("SELECT count(*) FROM public.declaratii_coada WHERE stare = \'respinsa\'")\n'
           'def scrie(cur):\n    cur.execute("UPDATE public.declaratii_coada SET stare = \'respinsa\' WHERE id = 1")\n'
           'def note(cur):\n    cur.execute("SELECT count(*) FROM public.declaratii_coada WHERE fel = \'nota\' AND stare = \'respinsa\'")\n'
           'def bun(cur, a):\n    cur.execute("SELECT count(*) FROM public.declaratii_coada WHERE stare = \'respinsa\' AND NOT " + sql_inlocuita(a))\n'
           'def doc(cur):\n    """declaratii_coada: stare = \'respinsa\'"""\n    return 1\n')
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "kpi_proba.py")
        io.open(p, "w", encoding="utf-8").write(cod)
        gasite, citiri = _numaratori_de_respingeri([p])
    assert (gasite, citiri) == ({("kpi_proba.py", "rau")},
                                {("kpi_proba.py", "rau"), ("kpi_proba.py", "scrie"), ("kpi_proba.py", "note"), ("kpi_proba.py", "bun")})
