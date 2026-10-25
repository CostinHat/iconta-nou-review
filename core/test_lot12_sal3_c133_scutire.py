# -*- coding: utf-8 -*-
"""Lotul 12, pachetul sal3 — C133: „Scutit” și „Motiv” se pot corecta, cu jurnal (comanda Costin 12.3 pct.8, verbatim în DECIZII: „C133:
«Scutit» și «Motiv» se pot corecta, cu jurnal (cine, când, vechi → nou); motivul e obligatoriu când e bifat «Scutit».”).

SURSE (citite la sursă):
- OPANAF 605/2026 anexa 2, „Date de identificare ale asiguratului” (`anaf_surse/opanaf_605_2026_d112.pdf`, text extras cu
  `pdftotext -layout`), pct.12: „Motivul exceptării - se completează în cazul în care caseta de la pct.11 a fost completată cu valoarea
  "1", astfel : "1" - pentru persoana fizică prevăzută la art.146 alin. (5^7) lit.a) din Codul fiscal […] elevi şi studenţi, cu vârsta
  până la 26 de ani […]; "2" - […] lit. b) […] ucenicii, cu vârstă de până la 18 ani […]; "3" - […] lit. c) […] persoana cu dizabilităţi
  sau alte categorii de persoane cărora prin lege li se recunoaşte posibilitatea de a lucra mai puţin de 8 ore pe zi; "4" - […] lit.d)
  […] salariaţii care au calitatea de pensionari pentru limită de vârstă în sistemul public de pensii; "5" - […] lit.e) […] două sau mai
  multe contracte individuale de muncă, a căror baza lunară cumulate […] este cel puţin egală cu salariul de bază minim brut pe ţară”.
- Structura D112 (`anaf_surse/structura_D112_0726_070926.txt`, 9cc `motivExc`): „daca asigExc=1 atunci motivExc = (1-5,null) altfel
  motivExc = null”; XSD-ul D112 (`anaf_surse/d112_06082026.xsd`): `motivExc` de tipul `IntInt1_5SType`.
CNP-urile de probă au cifra de control verificată (algoritmul din CLAUDE.md). Schemă efemeră din template, ștearsă la ieșire; perioada
D112 depuse din proba efectului e sintetică (2099), în ROLLBACK.
"""
import io
import os
import re
import xml.etree.ElementTree as ET

import pytest

from core import autor_cerere, db as _db, salariati_api as sa, salariati_import_api as si, tenant_provisioning as _tprov

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = "efemer_l12_sal3_c133"
CNP1 = "1900101410011"      # cifra de control verificată (test_412_cim_salariat)
UID = 990133                # utilizator sintetic al cererii (jurnalul nu cere rândul lui în public.users, ca `firma_profil_jurnal`)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


db_necesar = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def conn_sal():
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
        c.commit()
    try:
        with _db.get_conn(SCH) as c:
            yield c
            c.rollback()
    finally:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            c.commit()


@pytest.fixture()
def autor():
    tok = autor_cerere.seteaza(UID)
    try:
        yield UID
    finally:
        autor_cerere.reseteaza(tok)


def _salariat(cur, scutit=False, motiv=None, de_verificat="{}"):
    cur.execute("INSERT INTO salariati (cnp, nume, prenume, data_angajare, scutit_contrib_minim, motiv_exceptare, de_verificat) "
                "VALUES (%s, 'POP', 'ANA', '2024-01-01', %s, %s, %s::text[]) RETURNING id", (CNP1, scutit, motiv, de_verificat))
    return cur.fetchone()[0]


def _jurnal(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT salariat_id, camp, valoare_veche, valoare_noua, user_id, la IS NOT NULL FROM salariati_jurnal ORDER BY id")
        return cur.fetchall()


def _fisa(conn, sid):
    with conn.cursor() as cur:
        cur.execute("SELECT scutit_contrib_minim, motiv_exceptare FROM salariati WHERE id = %s", (sid,))
        return cur.fetchone()


def _campuri_refuzate(ei):
    return [(e["camp"], e["mesaj"]) for e in getattr(ei.value, "erori_campuri", [])]


# ── valorile permise ale motivului, confruntate cu sursa ─────────────────────────────────────────────────────────────────────────
def test_c133_motivele_permise_sunt_cele_din_d112():
    """`MOTIVE_EXCEPTARE` = motivele D112, citite din XSD-ul instalat (tipul atributului `motivExc`), nu scrise din memorie."""
    xsd = io.open(os.path.join(_RAD, "anaf_surse", "d112_06082026.xsd"), encoding="utf-8").read()
    rad = ET.fromstring(xsd.encode("utf-8"))
    ns = {"xs": "http://www.w3.org/2001/XMLSchema"}
    tip = rad.find(".//xs:attribute[@name='motivExc']", ns).get("type")
    st = rad.find(".//xs:simpleType[@name='%s']" % tip, ns)
    mn = int(st.find(".//xs:minInclusive", ns).get("value"))
    mx = int(st.find(".//xs:maxInclusive", ns).get("value"))
    # XSD D112: motivExc de tipul IntInt1_5SType; OPANAF 605/2026 anexa 2 pct.12: motivele "1"–"5" (CF art.146 alin.(5^7) lit.a–e)
    assert tuple(range(mn, mx + 1)) == sa.MOTIVE_EXCEPTARE == (1, 2, 3, 4, 5), (tip, mn, mx)
    struct = io.open(os.path.join(_RAD, "anaf_surse", "structura_D112_0726_070926.txt"), encoding="utf-8").read()
    # structura D112, 9cc `motivExc`: „daca asigExc=1 atunci motivExc = (1-5,null)” — capetele intervalului, citite din regulă
    regula = re.search(r"daca asigExc=1 atunci motivExc = \((\d)-(\d),null\)", struct)
    assert regula is not None and tuple(range(int(regula.group(1)), int(regula.group(2)) + 1)) == sa.MOTIVE_EXCEPTARE


# ── corectura, cu jurnalul ei ────────────────────────────────────────────────────────────────────────────────────────────────────
@db_necesar
def test_c133_scutirea_corectata_se_consemneaza_cine_cand_vechi_nou(conn_sal, autor):
    """Fișa salvată nescutită devine scutită cu motivul 4 din „Corectează datele”: două rânduri în jurnal (Scutit Nu -> Da, Motiv — -> 4),
    cu utilizatorul cererii și ora. ROȘU înainte: nicio urmă (jurnalul nu exista)."""
    with conn_sal.cursor() as cur:
        sid = _salariat(cur)
    r = sa.actualizeaza_salariat(conn_sal, sid, scutit_contrib_minim=True, motiv_exceptare=4)
    assert r["ok"] and r["scutire_corectata"] is True, r
    assert _fisa(conn_sal, sid) == (True, 4)
    assert _jurnal(conn_sal) == [(sid, "scutit_contrib_minim", "false", "true", UID, True),
                                 (sid, "motiv_exceptare", None, "4", UID, True)]
    # motivul corectat 4 -> 1: un rând; aceeași valoare din nou: nimic de consemnat, răspunsul fără efect
    sa.actualizeaza_salariat(conn_sal, sid, motiv_exceptare=1)
    assert sa.actualizeaza_salariat(conn_sal, sid, scutit_contrib_minim=True, motiv_exceptare=1) == {"ok": True}
    # scutirea pusă pe „Nu” golește motivul — ambele consemnate
    sa.actualizeaza_salariat(conn_sal, sid, scutit_contrib_minim=False)
    assert _fisa(conn_sal, sid) == (False, None)
    assert [x[1:4] for x in _jurnal(conn_sal)[2:]] == [("motiv_exceptare", "4", "1"), ("scutit_contrib_minim", "true", "false"),
                                                         ("motiv_exceptare", "1", None)]
    # detaliile fișei („Corectează datele”) aduc jurnalul, cel mai nou primul
    j = sa.detalii_salariat(conn_sal, sid)["jurnal_scutire"]
    assert [(x["camp"], x["vechi"], x["nou"]) for x in j][:2] == [("motiv_exceptare", "1", None), ("scutit_contrib_minim", "true", "false")]
    assert all(x["la"] for x in j) and len(j) == 5


@db_necesar
def test_c133_cine_e_numele_persoanei(conn_sal):
    """„Cine” = prenume + nume din `public.users` (ca jurnalul Date firmă), nu id-ul."""
    with conn_sal.cursor() as cur:
        cur.execute("SELECT id, TRIM(CONCAT_WS(' ', prenume, nume)) FROM public.users WHERE COALESCE(prenume, '') <> '' "
                    "AND COALESCE(nume, '') <> '' ORDER BY id LIMIT 1")
        u = cur.fetchone()
        sid = _salariat(cur)
    if not u:
        pytest.skip("niciun utilizator cu nume în baza de test")
    tok = autor_cerere.seteaza(u[0])
    try:
        sa.actualizeaza_salariat(conn_sal, sid, scutit_contrib_minim=True, motiv_exceptare=2)
    finally:
        autor_cerere.reseteaza(tok)
    assert {x["cine"] for x in sa.detalii_salariat(conn_sal, sid)["jurnal_scutire"]} == {u[1]}


@db_necesar
def test_c133_corectura_fara_autor_se_refuza_si_nu_se_scrie(conn_sal):
    """Fără utilizatorul cererii corectura nu se face: n-ar fi consemnată (ca la cota produsului, 472). Fișa rămâne cum era."""
    with conn_sal.cursor() as cur:
        sid = _salariat(cur)
    with pytest.raises(ValueError, match="utilizatorul care o face"):
        sa.actualizeaza_salariat(conn_sal, sid, scutit_contrib_minim=True, motiv_exceptare=4)
    # refuzul pleacă înaintea oricărei scrieri (tranzacția e întreagă): fișa e cea de dinainte, jurnalul gol
    assert _fisa(conn_sal, sid) == (False, None) and _jurnal(conn_sal) == []
    # o salvare care nu schimbă scutirea nu cere autor (nimic de consemnat)
    assert sa.actualizeaza_salariat(conn_sal, sid, scutit_contrib_minim=False) == {"ok": True}


# ── motivul e obligatoriu când e bifat „Scutit” (refuz pe server, pe câmpul motivului) ───────────────────────────────────────────
@db_necesar
def test_c133_scutit_fara_motiv_se_refuza_pe_campul_motivului(conn_sal, autor):
    """Starea REZULTATĂ (fișa + ce s-a trimis) e judecată, nu numai cererea: (a) „Scutit” = Da peste o fișă fără motiv; (b) motivul golit
    pe o fișă scutită; (c) motivul ales pe o fișă nescutită. Fiecare refuz stă pe `motiv_exceptare` (ecranul îl pune lângă câmp), nimic
    nu se scrie. ROȘU înainte la (b) și (c): (b) golea motivul și lăsa fișa scutită fără motiv (D112 se oprea), (c) scria motivul pe o
    fișă nescutită."""
    with conn_sal.cursor() as cur:
        sid = _salariat(cur)
    with pytest.raises(ValueError) as ei:
        sa.actualizeaza_salariat(conn_sal, sid, scutit_contrib_minim=True)
    assert _campuri_refuzate(ei) == [("motiv_exceptare", sa.MESAJ_MOTIV_LIPSA)]
    with pytest.raises(ValueError) as ei:
        sa.actualizeaza_salariat(conn_sal, sid, motiv_exceptare=3)
    assert _campuri_refuzate(ei) == [("motiv_exceptare", sa.MESAJ_MOTIV_FARA_SCUTIRE)]
    sa.actualizeaza_salariat(conn_sal, sid, scutit_contrib_minim=True, motiv_exceptare=5)
    with pytest.raises(ValueError) as ei:
        sa.actualizeaza_salariat(conn_sal, sid, _golite=("motiv_exceptare",))
    assert _campuri_refuzate(ei) == [("motiv_exceptare", sa.MESAJ_MOTIV_LIPSA)]
    # motivul în afara listei D112 (OPANAF 605/2026 anexa 2 pct.12: "1"–"5")
    with pytest.raises(ValueError) as ei:
        sa.actualizeaza_salariat(conn_sal, sid, motiv_exceptare=6)
    assert [c for c, _m in _campuri_refuzate(ei)] == ["motiv_exceptare"]
    assert _fisa(conn_sal, sid) == (True, 5)
    assert [x[1:4] for x in _jurnal(conn_sal)] == [("scutit_contrib_minim", "false", "true"), ("motiv_exceptare", None, "5")]


# ── reimportul care schimbă scutirea: același jurnal ────────────────────────────────────────────────────────────────────────────
@db_necesar
def test_c133_reimportul_care_schimba_scutirea_se_consemneaza(conn_sal, autor):
    """Fișa scutită (motiv 4) reimportată dintr-un fișier care spune „scutit: nu”: fișa devine nescutită, motivul se golește, iar ambele
    schimbări intră în jurnal — ca o corectură de pe ecran. Un reimport care nu schimbă scutirea nu scrie nimic."""
    with conn_sal.cursor() as cur:
        sid = _salariat(cur, True, 4)
    f = ("nume;prenume;cnp;data angajare;brut;judet;persoane in intretinere;scutit contributie minima;norma;functie de baza;cor\n"
         "POP;ANA;%s;2024-01-01;3000;B;0;nu;intreaga;da;251401\n" % CNP1).encode("utf-8")
    randuri = si.extrage(f, "s.csv")
    assert randuri[0]["scutit_contrib_minim"] is False, randuri[0]
    si.importa(conn_sal, randuri, inlocuieste=True)
    assert _fisa(conn_sal, sid) == (False, None)
    assert [x[:5] for x in _jurnal(conn_sal)] == [(sid, "scutit_contrib_minim", "true", "false", UID), (sid, "motiv_exceptare", "4", None, UID)]
    si.importa(conn_sal, si.extrage(f, "s.csv"), inlocuieste=True)
    assert len(_jurnal(conn_sal)) == 2


# ── efectul în D112 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
@db_necesar
def test_c133_efectul_spune_de_la_ce_luna_intra_si_ca_ce_e_depus_nu_se_rescrie():
    """Cu o D112 depusă pe 03/2099 (sintetic, ROLLBACK): corectura intră în D112 de la 04/2099; ce e depus sau emis nu se rescrie. Fără
    nicio D112 depusă: intră în statul și în D112 calculate de acum înainte."""
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("SELECT id, schema_name FROM public.tenants WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY id LIMIT 1")
                t = cur.fetchone()
                if not t:
                    pytest.skip("nicio firmă în baza de test")
                cur.execute('SET LOCAL search_path TO "%s", public' % t[1])
                cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip) VALUES (%s, 2099, 3, 'd112')", (t[0],))
                assert sa.efect_corectura_d112(cur) == (
                    "Corectura scutirii intră în D112 de la luna 04/2099 (ultima D112 depusă e pe luna 03/2099). D112 deja depuse nu se "
                    "rescriu: o lună depusă se corectează numai printr-o rectificativă, pe care o generezi tu din Declarații. Fluturașii "
                    "deja emiși rămân cum au fost tipăriți.")
                cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip) VALUES (%s, 2099, 12, 'd112')", (t[0],))
                # luna de după decembrie e ianuarie anului următor
                assert sa.efect_corectura_d112(cur) == (
                    "Corectura scutirii intră în D112 de la luna 01/2100 (ultima D112 depusă e pe luna 12/2099). D112 deja depuse nu se "
                    "rescriu: o lună depusă se corectează numai printr-o rectificativă, pe care o generezi tu din Declarații. Fluturașii "
                    "deja emiși rămân cum au fost tipăriți.")
                cur.execute('SET LOCAL search_path TO "%s", public' % "schema_fara_firma_c133")
                assert sa.efect_corectura_d112(cur) == ("Corectura scutirii intră în statul de plată și în D112 calculate de acum înainte. "
                                                        "Fluturașii deja emiși rămân cum au fost tipăriți.")
        finally:
            c.rollback()


@pytest.fixture
def d112_mod(monkeypatch):
    """Fixtura D112 a pachetului ctrl (`test_lot12_ctrl_d112_cm_pensionar`), pe o schemă proprie."""
    from core import test_lot12_ctrl_d112_cm_pensionar as m
    monkeypatch.setattr(m, "_SCHEMA", "test_lot12_sal3_d112")
    return m


@db_necesar
def test_c133_d112_generata_dupa_corectura_declara_scutirea(d112_mod, autor):
    """PENSIONAR salvat nescutit -> D112 10/2026: `asigExc` 0, fără `motivExc`. Corectat pe ecran (Scutit = Da, motiv 4) -> D112 generată
    după corectură: `asigExc` 1, `motivExc` 4 (OPANAF 605/2026 anexa 2 pct.11–12; structura: „daca asigExc=1 atunci motivExc = (1-5,null)”).
    D112 citește scutirea de pe fișă la generare: corectura intră în prima D112 generată după ea."""
    from core import d112
    from core.common import Perioada
    ns = "{mfp:anaf:dgti:declaratie_unica:declaratie:v7}"
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            xml, _r = d112_mod._genereaza(c, [d112_mod._ION, {**d112_mod._PENS, "scutit": False, "motiv": None}])

            def _asig(x):
                a = next(e for e in ET.fromstring(x.encode("utf-8")).findall(ns + "asigurat") if e.get("cnpAsig") == d112_mod._PENS["cnp"])
                return a.get("asigExc"), a.get("motivExc")
            assert _asig(xml) == ("0", None)
            with c.cursor() as cur:
                cur.execute("SET LOCAL search_path TO %s, public" % d112_mod._SCHEMA)   # în tranzacție, nu pe conexiunea din pool
                cur.execute("SELECT id FROM salariati WHERE cnp = %s", (d112_mod._PENS["cnp"],))
                pid = cur.fetchone()[0]
            r = sa.actualizeaza_salariat(c, pid, scutit_contrib_minim=True, motiv_exceptare=4)
            assert r["scutire_corectata"] and re.search(r"Corectura scutirii intră", r["efect_d112"]), r
            c.commit()
            xml2 = d112.genereaza(c, d112_mod._SCHEMA, Perioada(an=2026, luna=10))[0]
            assert _asig(xml2) == ("1", "4")
        finally:
            c.rollback()
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % d112_mod._SCHEMA)
            c.commit()


# ── structura: sursa unică ──────────────────────────────────────────────────────────────────────────────────────────────────────
def test_c133_jurnalul_e_in_sablonul_firmei():
    """Sursa unică a structurii: blocul din tenant_template.sql = `migrare_salariati_jurnal.bloc_template()`."""
    from core import migrare_salariati_jurnal as m
    assert m.bloc_template() in io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read()


@db_necesar
def test_c133_migrarea_e_idempotenta(conn_sal):
    from core import migrare_salariati_jurnal as m
    with conn_sal.cursor() as cur:
        cur.execute("DROP TABLE salariati_jurnal")
    assert m.verifica(conn_sal, SCH) is False
    m.aplica(conn_sal, SCH)
    m.aplica(conn_sal, SCH)
    assert m.verifica(conn_sal, SCH) is True
