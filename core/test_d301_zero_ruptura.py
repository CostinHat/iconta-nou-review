# -*- coding: utf-8 -*-
"""GARD D301 (16.08.2026, campanie rețeta D300, pas 3/8) — trei remedieri, verificate la sursă
anaf_surse/opanaf_592_2016_d301.txt:

(1) ZERO-BASE + RUPTURA facturi IC. Sursa (instr. II, l.312): "Decontul special se depune NUMAI pentru
    perioadele in care ia nastere exigibilitatea taxei". COD VECHI: genereaza() emitea XML cu baza1..5=0 pe
    zero (fara refuz). Mai grav (ruptura seed<->consumator, regula 10): obligatia D301 se naste si din
    ACHIZITII IC inregistrate ca FACTURI, dar generatorul citeste DOAR tabelul manual d301_operatiuni ->
    o achizitie IC din facturi neintrodusa manual dispare din declaratie. FIX: genereaza() REFUZA pe zero;
    daca exista facturi IC in perioada neintroduse in D301, mesajul le NUMESTE (nu refuz generic tacut).

(2) SECTIUNEA 1 -> art.317 (instr. I, l.220): "Sectiunea 1 ... se completeaza NUMAI de catre persoanele
    inregistrate conform art. 317". O operatiune tip 1 cu pers_inreg=1 (firma fara marcaj art.317) = declaratie
    contradictorie. Marcajul nu e populat fiabil -> AVERTISMENT (nu blocaj care ar opri orice D301 sectiunea 1).

(3) DECLARANT fabricat tacit (regula 4): build_xml emitea tacit nume/functie declarant = "ADMINISTRATOR".
    FIX 16.08: implicitul ramane DAR e ANUNTAT prin avertisment. RASTURNAT de lotul 10, C69: lipsa declarantului
    OPRESTE generarea, cu refuzul numit (structura D301 „29. nume_declarant … DA”, „30. prenume_declarant … DA”,
    „31. functia_declarant … DA”, toate „ERR- camp necompletat”).

Aserturi/markere ASCII.
"""
import pytest

from core.common import Perioada
from core import d301


# ============================================================
#  (3) declarant lipsa -> refuz numit (PUR) [lotul 10, C69]
# ============================================================
def test_declarant_lipsa_refuz_numit_nu_implicit():
    """[lotul 10, C69] Profil fara declarant -> D301 NU se genereaza: cele trei campuri ale declarantului sunt refuzate NUMIT
    (`firma_profil_api.erori_declarant`, sursa unica), nu completate cu „ADMINISTRATOR” / „-”. Forma veche (implicit + avertisment)
    a fost RASTURNATA de C69: structura D301 „29. nume_declarant Nume Declarant C(75) DA ERR- camp necompletat” (la fel
    prenume_declarant / functia_declarant) — un document ANAF semnat in numele cuiva care n-a declarat."""
    from core.firma_profil_api import erori_declarant
    prof = {"cui": "14399840", "nume": "PROBA SRL", "adresa": "Str 1", "oras": "Buc", "judet": "B",
            "banca": "BCR", "iban": "RO49AAAA1B31007593840000", "inreg_art317": False}
    refuzuri = erori_declarant(prof)
    # structura D301 „29. nume_declarant … DA”, „30. prenume_declarant … DA”, „31. functia_declarant … DA”: trei refuzuri, unul per camp
    assert len(refuzuri) == 3, refuzuri
    # profilul e altfel complet: refuzurile D301 sunt EXACT cele trei ale declarantului (nimic implicit, nimic in plus)
    assert d301.erori_generare(prof) == refuzuri


# ============================================================
#  DB: zero-base + ruptura + tip1 art.317 + DUK
# ============================================================
from core import db as _db, tenant_provisioning as _tp
_SCHEMA = "test_d301_zero_ruptura"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _setup(cur, art317=False, declarant=True):
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
    cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
    cur.execute("SET search_path TO %s, public" % _SCHEMA)
    dnume = "'POPESCU'" if declarant else "NULL"
    dfct = "'ADMINISTRATOR'" if declarant else "NULL"
    cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,regim_fiscal,"
                "platitor_tva,tip_decont,inreg_art317,declarant_nume,declarant_prenume,declarant_functie) "
                "VALUES (1,'PROBA D301 SRL','14399840','Str 1','Buc','B','4711','BCR',"
                "'RO49AAAA1B31007593840000','real',false,'L',%s,%s,'I',%s)" % (
                    'true' if art317 else 'false', dnume, dfct))


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            yield c
        finally:
            c.rollback()


def _op1(cur, an=2026, luna=8):
    cur.execute("INSERT INTO d301_operatiuni (an,luna,tip,nr_doc,data_doc,val_valuta,tip_valuta,curs,tva) "
                "VALUES (%s,%s,1,'AIC-1','2026-08-05',1000,'EUR',4.97,200)", (an, luna))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_zero_base_fara_operatiuni_si_fara_facturi_refuza(conn):
    """Nicio operatiune, nicio factura IC -> genereaza REFUZA pe zero (nu XML gol).
    RED pre-fix: genereaza emitea XML cu baza=0."""
    with conn.cursor() as cur:
        _setup(cur)
    conn.commit()
    with pytest.raises(ValueError) as ei:
        d301.genereaza(conn, _SCHEMA, Perioada(2026, luna=8))
    assert "nu se generează pe zero" in str(ei.value), str(ei.value)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ruptura_factura_ic_neintrodusa_refuza_cu_lista(conn):
    """Achizitie IC inregistrata ca FACTURA (primita DE) DAR neintrodusa in d301_operatiuni -> genereaza
    REFUZA numind factura (ruptura seed<->consumator). RED pre-fix: D301 se genera pe zero, pierzand achizitia."""
    with conn.cursor() as cur:
        _setup(cur)
        cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,total,tva) "
                    "VALUES ('FIC','2026-08-10','primita','DE811569869','FURNIZOR DE GMBH',1190,190)")
    conn.commit()
    with pytest.raises(ValueError) as ei:
        d301.genereaza(conn, _SCHEMA, Perioada(2026, luna=8))
    msg = str(ei.value)
    assert "achiziții intracomunitare" in msg and "FURNIZOR DE GMBH" in msg, msg
    assert "neintroduse în operațiunile D301" in msg, msg


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_tip1_fara_art317_avertisment(conn):
    """Operatiune Sectiunea 1 (tip 1) + firma FARA marcaj art.317 -> genereaza reuseste DAR avertizeaza
    (sectiunea 1 = art.317). RED pre-fix: pers_inreg=1 emis tacit cu operatiune de sectiunea 1."""
    with conn.cursor() as cur:
        _setup(cur, art317=False)
        _op1(cur)
    conn.commit()
    _xml, res = d301.genereaza(conn, _SCHEMA, Perioada(2026, luna=8))
    assert any("Secțiunea 1" in a and "art.317" in a for a in res.avertismente), \
        "operațiune de secțiunea 1 fără art.317 trebuie ANUNTATA: %r" % res.avertismente


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_tip1_cu_art317_fara_avertisment_sectiune1(conn):
    """CONTROL: firma cu marcaj art.317 -> operatiune tip 1 NU mai declanseaza avertismentul de sectiunea 1,
    iar pers_inreg=2 in XML."""
    with conn.cursor() as cur:
        _setup(cur, art317=True)
        _op1(cur)
    conn.commit()
    xml, res = d301.genereaza(conn, _SCHEMA, Perioada(2026, luna=8))
    assert not any("Secțiunea 1" in a and "art.317" in a for a in res.avertismente)
    assert 'pers_inreg="2"' in xml, "firma art.317 -> pers_inreg=2"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d301_normal_ramane_duk_valid(conn):
    """Proba DUK: D301 cu operatiune reala (art.317) e valid la DUKIntegrator (poarta zero-base nu blocheaza
    o declaratie cu operatiuni)."""
    from core import duk
    if not duk.poate_valida("d301"):
        pytest.skip("DUK d301 indisponibil")
    with conn.cursor() as cur:
        _setup(cur, art317=True)
        _op1(cur)
    conn.commit()
    xml, _res = d301.genereaza(conn, _SCHEMA, Perioada(2026, luna=8))
    rez = duk.valideaza(xml, "d301", an=2026, luna=8)
    assert rez["stare"] == "valid", "D301 normal trebuie DUK-valid; rez=%r" % rez


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_genereaza_fara_declarant_refuza(conn):
    """[lotul 10, C69] Pe calea contabilului (`genereaza`, din Date firmă), declarantul lipsă OPRESTE D301 cu refuzul numit —
    nu mai iese un XML cu nume_declarant="ADMINISTRATOR". Structura D301 „29. nume_declarant Nume Declarant C(75) DA”."""
    with conn.cursor() as cur:
        _setup(cur, art317=True, declarant=False)   # nume / functie NULL in Date firma
        _op1(cur)
    conn.commit()
    with pytest.raises(ValueError) as ei:
        d301.genereaza(conn, _SCHEMA, Perioada(2026, luna=8))
    msg = str(ei.value)
    prof, _ops = d301.pull(conn, _SCHEMA, Perioada(2026, luna=8))
    er = d301.erori_generare(prof)
    # structura D301 „29. nume_declarant … DA”, „31. functia_declarant … DA”: refuzul numit, nu un XML cu implicit
    assert [e.split(" (", 1)[0] for e in er] == ["Lipsă numele declarantului", "Lipsă funcția declarantului"], er
    assert msg.split(": ", 1) == ["D301 nu se poate genera", " ".join(er)], msg
