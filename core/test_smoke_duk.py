# -*- coding: utf-8 -*-
"""SMOKE-SWEEP DUK (01.08.2026) — gardul care lipsea: fiecare declaratie generata cu date
MINIME adecvate trebuie sa treaca validatorul OFICIAL DUK. Motiv: claim-ul din 16.07.2026
"toate 9 valide pe DUK" s-a dovedit NESIGUR - la un sweep pe validatorul curent, 2 din 9 erau
respinse (d101: model P inventat + P ca elemente; d406: cont referit absent din chart). Un test
unitar verde nu prinde asta - doar generarea completa + DUK o prinde. Cele 7 valide sunt aparate
aici; d101 si d406 sunt xfail(strict) - se aprind cand se repara (te anunta), nu se uita.

Fiecare declaratie primeste perioada care se potriveste cu datele ei. ROLLBACK garantat.
"""
import pytest

from core.common import Perioada
from core import db as _db, tenant_provisioning as _tp, duk as _duk
from core import d100, d101, d112, d205, d300, d301, d390, d394, d406

_SCHEMA = "ztest_smoke_duk"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_DBOK = _db_ok()


@pytest.fixture
def conn_smoke():
    """Schema efemera cu profil COMPLET + date minime pentru toate declaratiile:
    1 salariat (d112), note venituri 704/cheltuieli 607 (d100/d101), dividende 457 + asociat
    (d205), o factura UE emisa (d390) si domestica in iunie (d300/d394/d406). ROLLBACK."""
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,email,telefon,"
                    "regim_fiscal,platitor_tva,tip_decont,declarant_nume,declarant_prenume,declarant_functie) VALUES "
                    "(1,'PROBA SRL','14399840','Str. Test 1','Bucuresti','B','6202','BCR','RO49RNCB0000000000000001',"
                    "'a@b.ro','0700000000','profit',true,'L','Pop','Ion','administrator') "
                    "ON CONFLICT (id) DO UPDATE SET nume=EXCLUDED.nume")
                cur.execute("INSERT INTO salariati (cnp,nume,prenume,data_angajare,salariu_brut,ore_zi,judet_casa) "
                            "VALUES ('1900101410011','POPESCU','ION','2024-01-01',5000,8,'B')")
                cur.execute("INSERT INTO asociati (nume,cnp,cota) VALUES ('ASOCIAT UNU','1900101410011',100)")
                # nota venituri (704) + cheltuieli (607) in T2 -> d100 T2, d101 anual
                cur.execute("INSERT INTO inregistrari (data,status,sursa,descriere) VALUES ('2026-05-15','validata','t','Vanzare marfa') RETURNING id")
                i1 = cur.fetchone()[0]
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,suma) VALUES (%s,'4111','704',100000)", (i1,))
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,suma) VALUES (%s,'607','401',60000)", (i1,))
                # nota dividende (457) -> d205
                cur.execute("INSERT INTO inregistrari (data,status,sursa,descriere) VALUES ('2026-03-10','validata','t','Distribuire dividende') RETURNING id")
                i2 = cur.fetchone()[0]
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,suma) VALUES (%s,'457','5121',50000)", (i2,))
                # factura UE emisa iunie -> d390; domestica iunie -> d300/d394/d406
                cur.execute("INSERT INTO facturi (numar,data_emitere,total,tva,directie,tert_nume,tert_cui) "
                            "VALUES ('F001','2026-06-15',10000,0,'emisa','EU GMBH','DE811128135')")
                # factura DOMESTICA emisa iunie (tert RO, TVA 21%) -> d394/d300/d406
                cur.execute("INSERT INTO facturi (numar,data_emitere,total,tva,directie,tert_nume,tert_cui) "
                            "VALUES ('F002','2026-06-20',6050,1050,'emisa','CLIENT RO SRL','RO14399840')")
                # operatiune D301 (tip 4 servicii, fara dependenta art.317) - D301 refuza generarea pe zero
                cur.execute("INSERT INTO d301_operatiuni (an,luna,tip,nr_doc,data_doc,val_valuta,tip_valuta,curs,tva) "
                            "VALUES (2026,6,4,'D301A','2026-06-10',1000,'EUR',4.97,190)")
            yield conn
        finally:
            conn.rollback()


def _valid(xml, tip, **kw):
    r = _duk.valideaza(xml, tip, **kw)
    assert r["stare"] == "valid", "%s respins de DUK: %s" % (tip, (r.get("erori") or "")[:200])


@pytest.mark.skipif(not _DBOK or not _duk.poate_valida("d100"), reason="DB/DUK d100")
def test_smoke_d100(conn_smoke):
    xml, _ = d100.genereaza(conn_smoke, _SCHEMA, Perioada(2026, trim=2), {"cota": "16"})
    _valid(xml, "d100", an=2026, luna=6)


@pytest.mark.skipif(not _DBOK or not _duk.poate_valida("d112"), reason="DB/DUK d112")
def test_smoke_d112(conn_smoke):
    xml, _ = d112.genereaza(conn_smoke, _SCHEMA, 2026, 6)
    _valid(xml, "d112", an=2026, luna=6)


@pytest.mark.skipif(not _DBOK or not _duk.poate_valida("d205"), reason="DB/DUK d205")
def test_smoke_d205(conn_smoke):
    xml, _ = d205.genereaza(conn_smoke, _SCHEMA, Perioada(2026))
    _valid(xml, "d205", an=2026)


@pytest.mark.skipif(not _DBOK or not _duk.poate_valida("d300"), reason="DB/DUK d300")
def test_smoke_d300(conn_smoke):
    xml, _ = d300.genereaza(conn_smoke, _SCHEMA, Perioada(2026, luna=6))
    _valid(xml, "d300", an=2026, luna=6)


@pytest.mark.skipif(not _DBOK or not _duk.poate_valida("d301"), reason="DB/DUK d301")
def test_smoke_d301(conn_smoke):
    xml, _ = d301.genereaza(conn_smoke, _SCHEMA, Perioada(2026, luna=6))
    _valid(xml, "d301", an=2026, luna=6)


@pytest.mark.skipif(not _DBOK or not _duk.poate_valida("d390"), reason="DB/DUK d390")
def test_smoke_d390(conn_smoke):
    xml, _ = d390.genereaza(conn_smoke, _SCHEMA, 2026, 6, None)
    _valid(xml, "d390", an=2026, luna=6)


@pytest.mark.skipif(not _DBOK or not _duk.poate_valida("d394"), reason="DB/DUK d394")
def test_smoke_d394(conn_smoke):
    xml, _ = d394.genereaza(conn_smoke, _SCHEMA, Perioada(2026, luna=6))
    _valid(xml, "d394", an=2026, luna=6)


@pytest.mark.skipif(not _DBOK or not _duk.poate_valida("d101"), reason="DB/DUK d101")
def test_smoke_d101(conn_smoke):
    xml, _ = d101.genereaza(conn_smoke, _SCHEMA, Perioada(2026))
    _valid(xml, "d101", an=2026)


@pytest.mark.skipif(not _DBOK or not _duk.poate_valida("d406"), reason="DB/DUK d406")
def test_smoke_d406(conn_smoke):
    xml, _ = d406.genereaza(conn_smoke, _SCHEMA, 2026, 6)
    _valid(xml, "d406", an=2026, luna=6)


@pytest.mark.skipif(not _DBOK, reason="DB indisponibil")
def test_poarta_artefact_blocheaza_total_corupt(conn_smoke):
    """[poarta pe ARTEFACT, 05.08.2026] Cele 6 declaratii cablate (d100/d101/d205/d300/d394/d112) reconciliaza
    valoarea PARSATA din XML-ul livrat cu res (totalPlata_A==res.total_plata_a; d112: totalPlata_A==suma A_datorat).
    O mutatie pe totalul EMIS (dupa build_xml) = HARD-BLOCK ReconciliereEmis. Inainte poarta reconcilia res PRE-emisie
    -> mutatia pe artefact trecea (sweep 05.08 tura 7). d406 = exceptia lossy declarata (necablata, vezi reconciliere_emis)."""
    import re
    from core.reconciliere_emis import ReconciliereEmis
    def _cor(xml):
        m = re.search(r'totalPlata_A="(\d+)"', xml)
        assert m, "totalPlata_A absent - fixtura nu emite total"
        return xml.replace(m.group(0), 'totalPlata_A="%d"' % (int(m.group(1)) * 2 + 1), 1)
    def _wrap(fn):
        def w(*a, **k):
            r = fn(*a, **k)
            return (_cor(r[0]),) + tuple(r[1:]) if isinstance(r, tuple) else _cor(r)
        return w
    cases = [
        (d100, "build_xml", lambda: d100.genereaza(conn_smoke, _SCHEMA, Perioada(2026, trim=2), {"cota": "16"})),
        (d101, "build_xml", lambda: d101.genereaza(conn_smoke, _SCHEMA, Perioada(2026))),
        (d205, "build_xml", lambda: d205.genereaza(conn_smoke, _SCHEMA, Perioada(2026))),
        (d300, "build_xml", lambda: d300.genereaza(conn_smoke, _SCHEMA, Perioada(2026, luna=6))),
        (d394, "build_xml", lambda: d394.genereaza(conn_smoke, _SCHEMA, Perioada(2026, luna=6))),
        (d112, "_d112_genereaza", lambda: d112.genereaza(conn_smoke, _SCHEMA, 2026, 6)),
    ]
    for mod, attr, gen in cases:
        orig = getattr(mod, attr)
        setattr(mod, attr, _wrap(orig))
        try:
            with pytest.raises(ReconciliereEmis):
                gen()
        finally:
            setattr(mod, attr, orig)
