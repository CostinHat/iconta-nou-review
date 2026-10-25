# -*- coding: utf-8 -*-
"""[lotul 12, deficiența 642 — comanda Costin 12.2 pct.19, verbatim: „23.10, 14:15: la înregistrarea «Cabinet Test Inregistrare» cu CUI
12345678 contul s-a creat, firma proprie a cabinetului nu (emailul «Eșec pe cale secundară: provisionare tenant la register»), iar
emailul de bun venit spune că firma există”]

CAUZA (în cod, `uc_auth` de dinainte): contul (cu acordul și invitația / cererea folosită) se comitea ÎNTÂI; apoi `_dupa_cont_nou`
trimitea bun venitul cu fraza fixă „Firma proprie a cabinetului este deja adăugată în portofoliu.” — înainte să încerce firma — și abia
apoi crea firma, într-o a doua tranzacție, a cărei cădere se înghițea în `esec_secundar`. CUI-ul 12345678 are cifra de control greșită
(algoritmul din CLAUDE.md: 0·7+0·5+1·3+2·2+3·1+4·7+5·5+6·3+7·2 = 95; 950 mod 11 = 4 ≠ 8): o cerere scrisă înaintea verificării de la
formular (459) ajungea la confirmare și cădea la provizionare (`CuiInvalid`), cu contul deja comis.

REPARAȚIA: `uc_auth._firma_proprie` creează firma în TRANZACȚIA CONTULUI (împreună sau deloc), iar bun venitul pleacă după commit și
spune ce s-a creat (`text_bun_venit`). Precompletarea din ANAF stă sub un punct de revenire: căderea ei nu mai strică tranzacția.

Probele rulează pe baza de TEST, într-o singură conexiune întoarsă la capăt: `db.get_conn` e înlocuit cu un bloc cu punct de revenire
care face exact ce face cel real (commit la ieșire = păstrează; excepție = anulează blocul), deci „deloc” se vede ca în producție.

Temei: N/A — integritatea înregistrării (regulă de produs, CLAUDE.md §9; comanda 12.2 pct.19).
"""
import contextlib
import itertools
import secrets
import types

import pytest

from core import db as _db

#: CUI-ul din înregistrarea de pe 23.10 — cifra de control GREȘITĂ (vezi antetul), deci refuzat de `provision_tenant`
CUI_GRESIT = "12345678"


def _cui_valid(baza):
    """CUI cu cifra de control calculată după algoritmul oficial (CLAUDE.md, „Date de test”)."""
    ch, corp = [7, 5, 3, 2, 1, 7, 5, 3, 2], str(baza).rjust(9, "0")
    r = sum(int(corp[i]) * ch[i] for i in range(9)) * 10 % 11
    return "%d%d" % (baza, 0 if r == 10 else r)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="baza de test indisponibilă")


class _Bloc:
    """Conexiunea dată de `get_conn` simulat: `commit` = păstrează (la ieșirea din bloc), `rollback` = anulează blocul până aici."""

    def __init__(self, real, nume):
        object.__setattr__(self, "_real", real)
        object.__setattr__(self, "_nume", nume)

    def __getattr__(self, n):
        return getattr(self._real, n)

    def commit(self):
        pass

    def rollback(self):
        with self._real.cursor() as c:
            c.execute("ROLLBACK TO SAVEPOINT " + self._nume)


@pytest.fixture
def lume(contor_schema_pastrat, monkeypatch):
    from core import uc_auth, uc_comun, tenant_provisioning as tp
    _db.init_pool()
    conn = _db.pool().getconn()
    nr = itertools.count()

    @contextlib.contextmanager
    def get_conn(schema=None):
        nume = "bloc_%d" % next(nr)
        with conn.cursor() as c:
            c.execute("SAVEPOINT " + nume)
            if schema:
                c.execute('SET LOCAL search_path TO "%s", public' % schema)
        try:
            yield _Bloc(conn, nume)
        except BaseException:
            with conn.cursor() as c:
                c.execute("ROLLBACK TO SAVEPOINT " + nume)
            raise
        with conn.cursor() as c:
            c.execute("RELEASE SAVEPOINT " + nume)

    emailuri, esecuri = [], []
    monkeypatch.setattr(_db, "get_conn", get_conn)
    monkeypatch.setattr(uc_comun, "_TENANT_TEMPLATE", open("tenant_template.sql", encoding="utf-8").read())
    monkeypatch.setattr(tp, "date_din_anaf", lambda cui: None)          # ANAF nu se cheamă dintr-o probă
    monkeypatch.setattr(uc_auth, "_anunta_cabinet_nou", lambda *a: True)
    monkeypatch.setattr(uc_auth._obs, "trimite_email_html_sau_semnaleaza", lambda et, catre, subiect, html, **k: emailuri.append(
        (et, catre, html)) or True)
    monkeypatch.setattr(uc_auth._obs, "esec_secundar", lambda et, e, alerta=False: esecuri.append((et, type(e).__name__, alerta)))

    def numara(email, cui=None):
        with conn.cursor() as c:
            c.execute("SELECT (SELECT count(*) FROM public.users WHERE email = %s), (SELECT count(*) FROM public.accounting_firms af "
                      "WHERE af.id IN (SELECT accounting_firm_id FROM public.users WHERE email = %s)), "
                      "(SELECT count(*) FROM public.tenants WHERE cui = %s)", (email, email, cui or "-"))
            return c.fetchone()

    try:
        yield types.SimpleNamespace(conn=conn, emailuri=emailuri, esecuri=esecuri, numara=numara)
    finally:
        conn.rollback()
        _db.pool().putconn(conn)


def _formular(email, cui, invitatie):
    return types.SimpleNamespace(email=email, parola="Parola.642-" + secrets.token_hex(4), nume_cabinet="Cabinet Proba 642 " + email[:12],
                                 cui=cui, nume="Proba", prenume=None, accept_termeni=True, invitatie=invitatie, turnstile=None,
                                 telefon=None)


def _invitatie(conn, email):
    from core import invitatii
    with conn.cursor() as cur:
        return invitatii.creeaza(cur, email, None)


def _cerere_libera(conn, email, cui):
    from core import inregistrare_libera as il, nucleu
    with conn.cursor() as cur:
        return il.creeaza(cur, {"email": email, "nume_cabinet": "Cabinet Proba 642 liber", "nume": "Proba", "prenume": None, "cui": cui},
                          nucleu.hash_parola(secrets.token_urlsafe(12)), "v-proba", None)


def test_def_642_cererea_cu_cui_gresit_nu_lasa_cont_fara_firma(lume):
    """Cazul din 23.10: cererea liberă cu CUI 12345678 (scrisă înaintea verificării de la formular) -> clic pe link: contul NU se creează,
    refuzul spune de ce și ce e de făcut, linkul rămâne neconsumat, niciun bun venit. ROȘU înainte: contul (1, 1, 0) + bun venitul cu
    „Firma proprie a cabinetului este deja adăugată în portofoliu.” + `esec_secundar('provisionare tenant la register')`. MUTAȚIA:
    `firma = _firma_proprie(...)` scos din `confirma_inregistrarea` (sau provizionarea mutată după commit) -> pică."""
    from core import uc_auth, erori, tenant_provisioning as tp, inregistrare_libera as il
    email = "ztest_642_liber_%s@exemplu.ro" % secrets.token_hex(3)
    tok = _cerere_libera(lume.conn, email, CUI_GRESIT)
    with pytest.raises(erori.CerereGresita) as e:
        uc_auth.confirma_inregistrarea(tok, ip="203.0.113.242")
    mesaj = str(e.value.detaliu)
    # refuzul întreg, nu fragmente din el: de ce (cifra de control) și ce e de făcut (înregistrarea din nou)
    assert mesaj == ("Contul nu s-a creat: firma proprie a cabinetului (CUI 12345678) nu se poate adăuga. " + tp.MESAJ_CUI_CONTROL % CUI_GRESIT
                     + " Corectează CUI-ul (sau lasă-l gol și adaugă firma după intrarea în cont), apoi înregistrează-te din nou, cu CUI-ul "
                       "corect sau fără CUI."), mesaj
    assert lume.numara(email, CUI_GRESIT) == (0, 0, 0), "contul a rămas fără firmă"
    assert lume.emailuri == [], lume.emailuri                     # niciun bun venit pentru un cont care nu există
    with lume.conn.cursor() as cur:
        assert il.ia_pentru_confirmare(cur, tok)["valida"] is True, "linkul s-a consumat deși contul nu s-a creat"


def test_def_642_invitatia_cu_firma_care_cade_tehnic_nu_lasa_cont(lume, monkeypatch):
    """Invitația, CUI valabil, provizionarea cade DUPĂ ce a scris (schema, rândul firmei) -> nimic nu rămâne: nici contul, nici firma,
    invitația rămâne folosibilă; refuzul spune „Contul nu s-a creat …”; operatorul primește alerta. MUTAȚIA: `raise _erori.EsecIntern`
    înlocuit cu `return None` în `_firma_proprie` -> contul rămâne -> pică."""
    from core import uc_auth, erori, tenant_provisioning as tp, invitatii
    email = "ztest_642_inv_%s@exemplu.ro" % secrets.token_hex(3)
    cui = _cui_valid(64200 + secrets.randbelow(900))
    tok = _invitatie(lume.conn, email)
    real = tp.provision_tenant

    def cade_dupa_scriere(*a, **k):
        real(*a, **k)
        raise RuntimeError("defect injectat după crearea schemei")
    monkeypatch.setattr(tp, "provision_tenant", cade_dupa_scriere)
    with pytest.raises(erori.EsecIntern) as e:
        uc_auth.register(_formular(email, cui, tok))
    assert str(e.value.detaliu).startswith("Contul nu s-a creat: firma proprie a cabinetului (CUI %s)" % cui), e.value.detaliu
    assert lume.numara(email, cui) == (0, 0, 0), "contul sau firma au rămas după cădere"
    assert lume.emailuri == [], lume.emailuri
    assert any(a for _et, _t, a in lume.esecuri), lume.esecuri   # alerta operatorului (cădere tehnică)
    with lume.conn.cursor() as cur:
        assert invitatii.stare(cur, tok)["valida"] is True, "invitația s-a consumat deși contul nu s-a creat"


def test_def_642_cu_cui_contul_si_firma_impreuna_iar_bun_venitul_o_spune(lume):
    """Fără defect: contul + firma proprie (cu CUI-ul pe cabinet), iar bun venitul numește firma; fără CUI: contul singur, iar bun
    venitul NU spune că firma există. ROȘU înainte (fără CUI): „Firma proprie a cabinetului este deja adăugată în portofoliu.” MUTAȚIA:
    fraza fixă din `_dupa_cont_nou` pusă la loc -> pică."""
    from core import uc_auth
    email = "ztest_642_ok_%s@exemplu.ro" % secrets.token_hex(3)
    cui = _cui_valid(64300 + secrets.randbelow(900))
    r = uc_auth.register(_formular(email, cui, _invitatie(lume.conn, email)))
    assert lume.numara(email, cui) == (1, 1, 1), "contul și firma lui trebuiau create împreună"
    with lume.conn.cursor() as cur:
        cur.execute("SELECT cui FROM public.accounting_firms WHERE id = %s", (r["firm_id"],))
        assert cur.fetchone()[0] == cui
    (_et, catre, html), = lume.emailuri
    assert catre == email and "Firma proprie a cabinetului (CUI %s) a fost adăugată în portofoliu." % cui in html, html

    email2 = "ztest_642_fara_%s@exemplu.ro" % secrets.token_hex(3)
    uc_auth.register(_formular(email2, "", _invitatie(lume.conn, email2)))
    assert lume.numara(email2)[:2] == (1, 1)
    html2 = lume.emailuri[-1][2]
    assert "deja adăugată" not in html2 and "a fost adăugată în portofoliu" not in html2, html2
    assert "le adaugi după intrarea în cont, din ecranul Firme" in html2, html2


def test_def_642_precompletarea_anaf_cazuta_nu_strica_tranzactia(lume, monkeypatch):
    """Precompletarea din ANAF cade cu o eroare de BAZĂ (tranzacția Postgres stricată): firma și contul rămân (punctul de revenire),
    căderea se consemnează. ROȘU înainte: fără punct de revenire, `commit` pe tranzacția stricată anula totul tăcut, cu „firma creată”
    în răspuns. MUTAȚIA: SAVEPOINT-ul scos din `_firma_proprie` -> pică."""
    from core import uc_auth, tenant_provisioning as tp

    def cade_in_baza(conn, schema, d, **k):
        with conn.cursor() as c:
            c.execute("SELECT * FROM tabela_care_nu_exista_642")
    monkeypatch.setattr(tp, "precompleteaza_din_anaf", cade_in_baza)
    email = "ztest_642_anaf_%s@exemplu.ro" % secrets.token_hex(3)
    cui = _cui_valid(64400 + secrets.randbelow(900))
    uc_auth.register(_formular(email, cui, _invitatie(lume.conn, email)))
    assert lume.numara(email, cui) == (1, 1, 1)
    assert ("precompletare ANAF la register", "UndefinedTable", False) in lume.esecuri, lume.esecuri


def test_def_642_firma_proprie_e_in_tranzactia_contului_pe_ambele_cai():
    """Garda de structură: ambele căi care creează un cont (invitația, confirmarea înregistrării libere) cheamă `_firma_proprie` ÎN blocul
    `with db.get_conn()` al contului, iar bun venitul (`_dupa_cont_nou`) vine DUPĂ bloc; `_dupa_cont_nou` nu mai provizionează și nu mai
    are fraza fixă. MUTAȚIA: `_firma_proprie` mutat după bloc -> pică."""
    import ast
    import os
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "uc_auth.py"), encoding="utf-8").read()
    arb = ast.parse(src)
    fn = {n.name: n for n in arb.body if isinstance(n, ast.FunctionDef)}

    def apeluri(nod, nume):
        return [c for c in ast.walk(nod) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == nume]

    for cale in ("_register_cu_invitatie", "confirma_inregistrarea"):
        blocuri = [w for w in ast.walk(fn[cale]) if isinstance(w, ast.With)
                   and any(isinstance(c, ast.Call) and getattr(c.func, "attr", getattr(c.func, "id", None)) == "inregistreaza_cabinet"
                           for x in w.body for c in ast.walk(x))]
        assert len(blocuri) == 1, (cale, "blocul contului")
        assert apeluri(blocuri[0], "_firma_proprie"), "%s: firma proprie în afara tranzacției contului" % cale
        dupa = [c for c in apeluri(fn[cale], "_dupa_cont_nou") if c.lineno > blocuri[0].end_lineno]
        assert dupa, "%s: bun venitul trebuie să vină după tranzacția contului" % cale
    corp = ast.unparse(fn["_dupa_cont_nou"])
    assert "provision_tenant" not in corp and "deja adăugată" not in corp, corp


def test_def_642_clasa_precompletarea_cazuta_lasa_tranzactia_intreaga(monkeypatch):
    """Clasa (C, găsită la 642): `tenant_provisioning.precompleteaza_sau_semnaleaza` — o eroare de bază în precompletare se anulează
    singură (punctul de revenire), iar ce scrisese tranzacția înainte rămâne și se poate comite. Probat pe Postgres: fără punct de
    revenire, `commit` pe tranzacția stricată nu ridică și anulează tot. MUTAȚIA: SAVEPOINT / ROLLBACK TO scoase din ajutor -> pică."""
    from core import tenant_provisioning as tp
    semnalate = []
    monkeypatch.setattr(tp, "precompleteaza_din_anaf", lambda conn, *a, **k: conn.cursor().execute("SELECT * FROM tabela_care_nu_exista_642"))
    from core import observare
    monkeypatch.setattr(observare, "esec_secundar", lambda et, e, alerta=False: semnalate.append((et, type(e).__name__)))
    conn = _db.pool().getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE TEMP TABLE z642 (x int) ON COMMIT DROP")
            cur.execute("INSERT INTO z642 VALUES (1)")
        assert tp.precompleteaza_sau_semnaleaza(conn, "tenant_inexistent", {}, "proba 642") is None
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM z642")
            assert cur.fetchone()[0] == 1, "tranzacția creării s-a stricat"
    finally:
        conn.rollback()
        _db.pool().putconn(conn)
    assert semnalate == [("proba 642", "UndefinedTable")], semnalate


def test_def_642_clasa_toate_caile_de_creare_precompleteaza_sub_punct_de_revenire():
    """Garda clasei: în afara lui `tenant_provisioning`, nicio cale nu cheamă `precompleteaza_din_anaf` direct (în tranzacția creării
    firmei, fără punct de revenire): toate trec prin `precompleteaza_sau_semnaleaza`. Cele trei căi: înregistrarea (`uc_auth`), „Adaugă
    firmă” (`uc_tenants.tenant_creeaza`), importul firmelor (`uc_migrare`). MUTAȚIA: un apel direct pus la loc -> pică."""
    import ast
    import os
    rad = os.path.dirname(os.path.abspath(__file__))
    directe, prin_ajutor = [], set()
    for f in sorted(os.listdir(rad)):
        if not f.endswith(".py") or f.startswith("test_") or f == "tenant_provisioning.py":
            continue
        for c in ast.walk(ast.parse(open(os.path.join(rad, f), encoding="utf-8").read())):   # APELURILE, din AST (nu pomenirile din text)
            nume = getattr(c.func, "attr", getattr(c.func, "id", None)) if isinstance(c, ast.Call) else None
            if nume == "precompleteaza_din_anaf":
                directe.append("%s:%d" % (f, c.lineno))
            elif nume == "precompleteaza_sau_semnaleaza":
                prin_ajutor.add(f)
    assert directe == [], "precompletare fără punct de revenire: %s" % directe
    assert prin_ajutor >= {"uc_auth.py", "uc_migrare.py", "uc_tenants.py"}, prin_ajutor
