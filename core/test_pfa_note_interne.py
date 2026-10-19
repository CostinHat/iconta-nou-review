# -*- coding: utf-8 -*-
"""GARD — deficiența 368, notele unei firme în partidă simplă (decizia Costin 19.10.2026, verbatim în DECIZII „Închiderea lotului 9”):
„Se validează automat — la PFA nota scrisă în fundal (Casă, Bancă, facturi, Z, salarii) se validează automat la scriere, ca «notă
internă», cu documentul ei (regula R3); actul omului rămâne operațiunea din registrul de încasări și plăți.”  # TEMEI LIBER: citat verbatim al deciziei
Plus cele două defecte găsite
pe drum: Z-ul unei PFA rămânea ciornă și lipsea din D300 rd.9/10 și D394; `nevalidate_acum` numea note și la D212, care nu le citește.

Ce fac imposibil:
- nota cererii, la o PFA, rămasă ciornă fără motiv: middleware-ul (`main._autor_si_note_in_coada`) cheamă `uc_coada.note_interne`
  ÎNAINTEA cozii, iar acolo notele cererii (`coada_api.ciorne_din_cerere`, oricine e autorul) trec prin `jurnal_api.valideaza_interne`
  — ACELAȘI drum ca validarea omului (`valideaza`), cu toate regulile lui;
- validarea internă care ocolește o regulă: R3 (documentul) și casa sub zero (406) refuză și aici; nota refuzată rămâne ciornă, cu
  motivul, iar celelalte se validează;
- validarea internă la partidă dublă (nota SRL-ului rămâne a contabilului);
- D300 al unei PFA fără TVA-ul Z-ului (proba: schema efemeră, ruta reală `uc_tenants.horeca_raport_z`, D300 generat);
- notele nevalidate numite la D212.
Temei: OMFP 170/2015 (partida simplă: evidența e registrul de încasări și plăți); CF art.282 alin.(1) și instrucțiunile D300 (OPANAF
174/2026) rd.9/10 — „informațiile preluate din jurnalul de vânzări pentru operațiuni a căror exigibilitate intervine în perioada de
raportare”. Probele DB rulează pe o schemă efemeră din tenant_template, în tranzacție anulată.
"""
import contextlib
import datetime as _dt
import io
import os
import re
from decimal import Decimal, ROUND_HALF_UP

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_pfa_note_interne"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


class _FaraCommit:
    """Conexiunea fixturii, cu `commit()` neutralizat: rutele comit, testul anulează."""

    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


class _Z:
    """Raportul Z tastat (aceleași cifre ca `core/test_d300_rapoarte_z.py::_Z`)."""
    data = "2026-07-10"
    nui = "8000000002"
    nr_raport = "0007"
    nr_bonuri = 42
    total_11 = 111.0
    total_21 = 1210.0
    numerar = 1321.0
    card = 0.0


def _schema(cur, tip_firma):
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
    cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
    cur.execute("SET search_path TO %s, public" % SCH)
    # `now()` e începutul tranzacției fixturii (schema e creată în ea); în producție fiecare scriere își are tranzacția ei, deci `creat_la` e
    # momentul scrierii — aici la fel, ca proba să nu depindă de cât a durat crearea schemei (marja `uc_coada._MARJA_CEAS_SECUNDE`)
    cur.execute("ALTER TABLE inregistrari ALTER COLUMN creat_la SET DEFAULT clock_timestamp()")
    cur.execute(
        "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, regim_fiscal, platitor_tva, tip_decont, "
        "tva_la_incasare, declarant_nume, declarant_prenume, declarant_functie, tip_firma) "
        "VALUES (1,'PFA PROBA NOTE INTERNE','14399840','Str Test 1','Bucuresti','B','5610','BCR','RO49AAAA1B31007593840000',"
        "'real',true,'L',false,'Popescu','Ion','TITULAR',%s)", (tip_firma,))


def _lume(tip_firma, monkeypatch):
    """(conn, uid): schema efemeră a unei firme `tip_firma`, autorul cererii pe conexiune (ca middleware-ul), rutele cu conexiunea
    fixturii (comiterea neutralizată)."""
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM public.users WHERE email='patron@prisma-cont.test'")
                r = cur.fetchone()
                if not r:
                    pytest.skip("utilizatorul de test lipsește")
                uid = r[0]
                _schema(cur, tip_firma)
                cur.execute("SELECT set_config('iconta.utilizator', %s, false)", (str(uid),))
            proxy = _FaraCommit(conn)
            from core import uc_tenants, auth_api, uc_comun as _uc, uc_coada, repo_declaratii
            monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(proxy))
            monkeypatch.setattr(uc_coada.db, "get_conn", lambda *a, **k: contextlib.nullcontext(proxy))
            monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: SCH)
            monkeypatch.setattr(repo_declaratii, "schema_firmei_cabinetului", lambda *a, **k: SCH)
            monkeypatch.setattr(_uc, "_cere_luna_deschisa", lambda *a, **k: None)
            yield conn, uid
        finally:
            conn.rollback()
            with conn.cursor() as cur:
                cur.execute("RESET iconta.utilizator")
                cur.execute("RESET search_path")
            conn.commit()


@pytest.fixture()
def lume(monkeypatch):
    yield from _lume("pfa", monkeypatch)


@pytest.fixture()
def lume_srl(monkeypatch):
    yield from _lume("srl", monkeypatch)


def _q(x):
    return int(Decimal(x).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _inceput():
    return _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(seconds=2)


def _stari(conn, ids):
    with conn.cursor() as cur:
        cur.execute("SELECT id, status FROM inregistrari WHERE id = ANY(%s) ORDER BY id", (list(ids),))
        return dict(cur.fetchall())


# ── Z-ul PFA: validat automat ca intern -> intră în D300 rd.9/10 ───────────────────────────────────────────────────────────
def test_z_la_pfa_se_valideaza_intern_si_intra_in_d300(lume):
    """Ruta reală a raportului Z (`horeca_raport_z`) la o PFA scrie nota-ciornă (TVA-ul pe cote) și încasarea în RIP; middleware-ul
    (`uc_coada.note_interne`) o validează ca notă internă; D300 07/2026 are TVA-ul Z-ului la rd.9 (21%) și rd.10 (11%).
    Tastat: 21% 1210 cu TVA -> TVA 1210×21/121 = 210,00, baza 1000,00; 11% 111 -> TVA 11,00, baza 100,00 (CF art.291; rotunjire
    aritmetică). MUTAȚIA: `if not coada_api.partida_simpla(cur):` -> `if True:` în `uc_coada.note_interne` -> nota rămâne ciornă,
    D300 fără rd.9 -> ROȘU."""
    from core import d300 as _d300, uc_coada, uc_tenants
    from core.common import Perioada
    conn, uid = lume
    t0 = _inceput()
    r = uc_tenants.horeca_raport_z(1, _Z(), {"uid": uid})
    assert r.get("registru") == "rip", r                      # [368] la PFA numerarul Z-ului intră în registrul de încasări și plăți
    with conn.cursor() as cur:
        cur.execute("SELECT id, status FROM inregistrari WHERE sursa = 'horeca_z'")
        (zid, st), = cur.fetchall()
    assert st == "ciorna"
    rez = uc_coada.note_interne(1, uid, 1, t0)
    assert len(rez["interne"]) == 1 and rez["refuzate"] == [], rez
    assert _stari(conn, [zid]) == {zid: "validata"}
    _xml, res = _d300.genereaza(conn, SCH, Perioada(2026, luna=7))
    print("368 Z la PFA:", rez, {k: res.R.get(k) for k in ("R9_1", "R9_2", "R10_1", "R10_2")})
    # CF art.282 alin.(1) + instrucțiuni D300 (OPANAF 174/2026) rd.9 (21%) / rd.10 (11%): livrările din jurnalul de vânzări, pe cotă
    assert (res.R.get("R9_1"), res.R.get("R9_2")) == (_q("1000.00"), _q("210.00")) == (1000, 210), res.R
    assert (res.R.get("R10_1"), res.R.get("R10_2")) == (_q("100.00"), _q("11.00")) == (100, 11), res.R
    # D394 (OPANAF 2194/2025, op2 — rapoartele Z) citește aceleași note validate (`repo_d394.select_rapoarte_z`)
    from core import d394 as _d394
    _prof, date394 = _d394.pull(conn, SCH, Perioada(2026, luna=7))
    print("368 D394 rapoarte_z:", date394.get("rapoarte_z"))
    assert sorted({z["id"] for z in date394["rapoarte_z"]}) == [zid], date394.get("rapoarte_z")


def test_z_refuzat_se_reincearca_dupa_fara_marfa(lume):
    """Firma ține stocul cantitativ-valoric: Z-ul PFA e refuzat la validarea internă (nedescărcat — OMFP 1802/2014 pct.287 alin.(1)-(2),
    `z_descarcare.refuz_validare`) și rămâne ciornă. Cererea care rezolvă cauza („fără marfă din stoc”) îl înscrie de reîncercat
    (`autor_cerere.reincearca_interna`), iar middleware-ul (`uc_coada.note_interne`, `in_plus`) îl validează ca notă internă.
    MUTAȚIA: `z_descarcare.deblocat` fără efect -> Z-ul rămâne ciornă după „fără marfă” -> ROȘU."""
    from core import autor_cerere, uc_coada, uc_tenants
    conn, uid = lume
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET metoda_stoc = 'cantitativ_valoric'")
    t0 = _inceput()
    uc_tenants.horeca_raport_z(1, _Z(), {"uid": uid})
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM inregistrari WHERE sursa = 'horeca_z'")
        (zid,), = cur.fetchall()
    rez = uc_coada.note_interne(1, uid, 1, t0)
    assert rez["interne"] == [] and len(rez["refuzate"]) == 1 and "descărcarea mărfii vândute" in rez["refuzate"][0]["motiv"], rez
    assert _stari(conn, [zid]) == {zid: "ciorna"}
    tok = autor_cerere.porneste_reincercarea()
    try:
        t1 = _inceput()
        uc_tenants.horeca_z_fara_marfa(1, zid, {"fara_marfa": True}, {"uid": uid})
        de_reincercat = autor_cerere.de_reincercat()
    finally:
        autor_cerere.opreste_reincercarea(tok)
    assert de_reincercat == [zid]
    rez = uc_coada.note_interne(1, uid, 1, t1, de_reincercat)
    assert len(rez["interne"]) == 1 and rez["refuzate"] == [], rez
    assert _stari(conn, [zid]) == {zid: "validata"}


# ── regulile validării se aplică: R3 și casa sub zero refuză, nota rămâne ciornă cu motivul ──────────────────────────────────
def test_refuzul_lasa_nota_ciorna_cu_motivul_iar_celelalte_se_valideaza(lume):
    """Trei note ale cererii: una cu document (se validează), una fără document (R3, regula din bază: „n-are documentul
    justificativ”), o plată din casă fără sold validat (406: casa sub zero). MUTAȚIA: `cur.execute("ROLLBACK TO SAVEPOINT
    nota_interna")` scos din ramura excepției în `jurnal_api.valideaza_interne` -> tranzacția rămâne întreruptă -> ROȘU."""
    from core import jurnal_api, uc_coada
    conn, uid = lume
    t0 = _inceput()
    ok = jurnal_api.creeaza(conn, SCH, "Chirie iulie", "2026-07-05",
                            [{"debit": "612", "credit": "401", "suma": 500, "partener_nume": "PARTENER PROBA SRL"}],
                            document_ref="Factura CH 12 din 05.07.2026")["id"]
    fara_doc = jurnal_api.creeaza(conn, SCH, "Fără document", "2026-07-06",
                                  [{"debit": "612", "credit": "401", "suma": 50, "partener_nume": "PARTENER PROBA SRL"}])["id"]
    # încasarea din casă e a ALTUI autor (nu e a cererii, deci rămâne ciornă): soldul validat al casei rămâne 0
    with conn.cursor() as cur:
        cur.execute("SELECT set_config('iconta.utilizator', '', false)")
    jurnal_api.creeaza(conn, SCH, "Încasare numerar", "2026-07-01", [{"debit": "5311", "credit": "704", "suma": 300}],
                       document_ref="Chitanța 1 din 01.07.2026")
    with conn.cursor() as cur:
        cur.execute("SELECT set_config('iconta.utilizator', %s, false)", (str(uid),))
    plata = jurnal_api.creeaza(conn, SCH, "Plată furnizor", "2026-07-07",
                               [{"debit": "401", "credit": "5311", "suma": 200, "partener_nume": "PARTENER PROBA SRL"}],
                               document_ref="Dispoziția de plată 3 din 07.07.2026")["id"]
    rez = uc_coada.note_interne(1, uid, 1, t0)
    assert _stari(conn, [ok, fara_doc, plata]) == {ok: "validata", fara_doc: "ciorna", plata: "ciorna"}
    assert len(rez["interne"]) == 1, rez
    print("368 refuzuri:", rez)
    # în ordinea Registrului jurnal (06.07, apoi 07.07); textele sunt ale regulilor, întregi
    assert [x["motiv"] for x in rez["refuzate"]] == [
        # R3, regula de fond din bază (`core/migrare_reguli_fond.py`; Legea 82/1991 art.6 alin.(1): documentul justificativ)
        "Nota din 06.07.2026 n-are documentul justificativ: o notă nu se validează fără documentul din care provine.",
        # 406, `casa_sold.refuz_iesire` cu `doar_validate=True` (OMFP 1802/2014, funcțiunea contului 531)
        "Nota de 200,00 lei nu încape în casă (contul 5311): soldul casei pe 07.07.2026, în evidența validată, e 0,00 lei, iar după ea "
        "casa ar ajunge la -200,00 lei pe 07.07.2026. Numerarul din casă nu poate fi negativ. Înregistrează întâi încasarea sau "
        "ridicarea de numerar din care s-a plătit (și valideaz-o)."], rez


def test_notele_altei_cereri_nu_se_ating(lume):
    """`ciorne_din_cerere`: numai ciornele autorului cererii, născute de la începutul ei. MUTAȚIA: `AND creat_la >= %s "` ->
    `AND creat_la >= %s - interval '1 day' "` în `coada_api.ciorne_din_cerere` -> nota veche intră -> ROȘU."""
    from core import coada_api, jurnal_api
    conn, uid = lume
    veche = jurnal_api.creeaza(conn, SCH, "Veche", "2026-07-02", [{"debit": "612", "credit": "401", "suma": 10,
                                                                  "partener_nume": "PARTENER PROBA SRL"}], document_ref="F 1")["id"]
    with conn.cursor() as cur:
        cur.execute("UPDATE inregistrari SET creat_la = now() - interval '1 hour' WHERE id = %s", (veche,))
        noua = jurnal_api.creeaza(conn, SCH, "Nouă", "2026-07-03", [{"debit": "612", "credit": "401", "suma": 10,
                                                                    "partener_nume": "PARTENER PROBA SRL"}], document_ref="F 2")["id"]
        assert coada_api.ciorne_din_cerere(cur, uid, _inceput()) == [noua]


def test_la_partida_dubla_nota_ramane_a_contabilului(lume_srl):
    """La SRL (partidă dublă) nimic nu se validează singur. MUTAȚIA: `== "simpla"` -> `!= "simpla"` în `coada_api.partida_simpla`
    -> ROȘU."""
    from core import jurnal_api, uc_coada
    conn, uid = lume_srl
    t0 = _inceput()
    n = jurnal_api.creeaza(conn, SCH, "Chirie", "2026-07-05", [{"debit": "612", "credit": "401", "suma": 5,
                                                              "partener_nume": "PARTENER PROBA SRL"}], document_ref="F 9")["id"]
    assert uc_coada.note_interne(1, uid, 1, t0) == {"interne": [], "refuzate": []}
    assert _stari(conn, [n]) == {n: "ciorna"}


# ── D212 nu numește note ─────────────────────────────────────────────────────────────────────────────────────────────────
def test_d212_nu_numeste_notele_nevalidate(lume):
    """D212 se face din registrul de încasări și plăți, nu din note: o ciornă a perioadei nu se numește la D212 (se numește la D300).
    MUTAȚIA: `note = [] if tip in DECLARATII_FARA_NOTE else …` -> `note = note_nevalidate(…)` -> ROȘU."""
    from core import coada_api, jurnal_api
    conn, _uid = lume
    jurnal_api.creeaza(conn, SCH, "Ciornă", "2026-07-05", [{"debit": "612", "credit": "401", "suma": 5,
                                                          "partener_nume": "PARTENER PROBA SRL"}], document_ref="F 9")
    with conn.cursor() as cur:
        n212, _f, nev212 = coada_api.nevalidate_acum(cur, SCH, "d212", "2026-01-01", "2027-01-01")
        n300, _f, _nev = coada_api.nevalidate_acum(cur, SCH, "d300", "2026-07-01", "2026-08-01")
    assert n212 == [] and nev212 is None, (n212, nev212)
    assert len(n300) == 1, n300


def test_d212_nu_citeste_note():
    """`DECLARATII_FARA_NOTE` e adevărat numai cât timp generatorul D212 nu citește `inregistrari` (azi: date manuale + registrul de
    încasări și plăți). Dacă începe s-o facă, D212 iese din listă. MUTAȚIA: `inregistrari` scris în `d212.pull` -> ROȘU."""
    from core import coada_api
    for tip in coada_api.DECLARATII_FARA_NOTE:
        for f in sorted(os.listdir(os.path.join(RAD, "core"))):
            if re.fullmatch(r"(repo_)?%s(_\w+)?\.py" % tip, f):
                assert "inregistrari" not in io.open(os.path.join(RAD, "core", f), encoding="utf-8").read(), f


# ── locurile centrale: middleware-ul și textul ecranului ─────────────────────────────────────────────────────────────────
def test_middleware_valideaza_intern_inaintea_cozii_si_pune_antetele():
    """`_autor_si_note_in_coada` cheamă `note_interne` ÎNAINTEA lui `note_in_coada` (nota refuzată intră apoi în coadă, ca orice
    ciornă) și pune cele două antete (nodurile AST). MUTAȚIA: antetul `X-Iconta-Note-Interne-Refuzate` scos din main.py -> ROȘU."""
    import ast
    src = io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read()
    fn = next(n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.AsyncFunctionDef) and n.name == "_autor_si_note_in_coada")
    linii = {x.attr: x.lineno for x in ast.walk(fn) if isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name)
             and x.value.id == "_uc_coada"}
    assert linii.get("note_interne", 10 ** 9) < linii.get("note_in_coada", 0), linii
    chei = [t.slice.value for n in ast.walk(fn) if isinstance(n, ast.Assign) for t in n.targets
            if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Attribute) and t.value.attr == "headers"
            and isinstance(t.slice, ast.Constant)]
    assert sorted(chei) == ["X-Iconta-La-Validare", "X-Iconta-Note-Interne", "X-Iconta-Note-Interne-Refuzate"], chei


def _js_stare_nota(cazuri):
    """Rulează cu node, pe răspunsuri cu antetele middleware-ului, funcțiile din api.js care spun starea notei (`_cuLaValidare`,
    `stareNota`, `pasNota` și ce folosesc ele), copiate din sursă — comportamentul, nu textul lor."""
    import json
    import shutil
    import subprocess
    node = shutil.which("node")
    if not node:
        pytest.skip("node lipsește")
    js = io.open(os.path.join(RAD, "static", "js", "api.js"), encoding="utf-8").read()
    bucati = []
    for nume in ("esc", "_cuLaValidare", "_numar", "refuzuriInterne", "stareNota", "pasNota"):
        m = re.search(r"^(?:export )?function %s\(.*?^\}" % re.escape(nume), js, re.S | re.M)
        assert m, nume
        bucati.append(m.group(0).replace("export ", "", 1))
    m = re.search(r"^export const TEXT_NOTA_INTERNA = .*?;$", js, re.M)
    assert m, "TEXT_NOTA_INTERNA"
    bucati.append(m.group(0).replace("export ", "", 1))
    prog = "\n".join(bucati) + """
const cazuri = JSON.parse(process.argv[1]);
console.log(JSON.stringify(cazuri.map((antete) => {
  const r = _cuLaValidare({headers: new Map(Object.entries(antete).map(([k, v]) => [k, encodeURIComponent(JSON.stringify(v))]))}, {});
  return [stareNota(r), pasNota(r)];
})));"""
    out = subprocess.run([node, "-e", prog, json.dumps(cazuri)], capture_output=True, text=True, timeout=30)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_ecranul_spune_nota_interna_si_refuzul():
    """`api.js`: antetele middleware-ului ajung pe rezultat, iar `stareNota` / `pasNota` spun, după starea reală: „notă internă” + ce e
    ea; refuzul validării interne cu motivul („rămâne ciornă și nu intră în D300 / D394”); fără antete, ca înainte („ciornă”).
    MUTAȚIA: `["X-Iconta-Note-Interne", "interne"]` scos din `_cuLaValidare` -> ROȘU."""
    rez = _js_stare_nota([
        {"X-Iconta-Note-Interne": ["nr. crt. 1 din 10.07.2026"]},
        {"X-Iconta-Note-Interne-Refuzate": [{"eticheta": "din 06.07.2026", "motiv": "n-are documentul justificativ."}]},
        {},
    ])
    assert rez == [
        ["notă internă", "Poartă TVA-ul pentru D300 / D394; evidența PFA e registrul de încasări și plăți."],
        ["ciornă", "Nota din 06.07.2026 nu s-a validat ca notă internă: n-are documentul justificativ. Până atunci rămâne ciornă și nu "
                   "intră în D300 / D394."],
        ["ciornă", "O validezi din Registrul jurnal."],
    ], rez
