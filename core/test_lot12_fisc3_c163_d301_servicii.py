# -*- coding: utf-8 -*-
"""[lotul 12, pachetul fisc3, C163, decizia Costin 12.3 pct.3: „serviciile primite din UE intră în D301”] D301 — calendarul și generatorul
— cuprind serviciile primite de la prestatori din UE de firma NEPLĂTITOARE (obligată la plata taxei).

Înainte: faptul D301 pe facturi (`control_incrucisat.d301_luni_facturi_ic`) și verificarea generatorului (`d301.genereaza`, D301 „pe zero”)
citeau `control_incrucisat.facturi_ic` FĂRĂ servicii (axa „servicii” se scotea, ca la compararea bunurilor din D390): luna cu numai un
serviciu primit din DE nu era lună D301 în Control fiscal, iar generatorul spunea „nicio operațiune cu exigibilitate în perioadă”. Acum
amândouă le iau și pe ele (aceeași sursă): luna e datorată, iar generatorul numește factura neintrodusă în ecranul D301 (tipul 5).

Temei (anaf_surse/cod_fiscal_227_2015_consolidat.txt), citat pe linia aserțiunii. Judecătorul structurii: validatorul DUK local
(`core/duk.py`, `valideaza(xml, "d301", an=, luna=)`). Schemă efemeră din `tenant_template.sql`, tranzacție anulată, date sintetice în
2097. CUI firmei: 14399840 (cifra de control verificată cu algoritmul din CLAUDE.md); prestatorul DE811907980 (`d390.checksum_vies` -> ok)."""
import datetime
import io
import os

import pytest

from core import db as _db, tenant_provisioning as _tp

SCH = "tenant_test_lot12_fisc3_c163"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COD_PRESTATOR = "DE811907980"
AZI = datetime.date(2097, 10, 24)   # D301 pe 09/2097: termenul 25.10.2097 (CF art.324 alin.(2)), în fereastra Control fiscal

#: (plătitor, înregistrat art.317): CF art.307 alin.(2) — „orice persoană impozabilă”, înregistrată art.317 sau nu
FIRME = {"art317": (False, True), "neinregistrat": (False, False)}


class _P:
    """Conexiunea testului: commit / rollback nu închid tranzacția testului (o anulează fixture-ul)."""
    def __init__(s, c): s._c = c
    def commit(s): pass
    def rollback(s): pass
    def __getattr__(s, n): return getattr(s._c, n)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture(params=sorted(FIRME))
def conn(request):
    if not _db_ok():
        pytest.skip("DB indisponibil")
    platitor, art317 = FIRME[request.param]
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,telefon,platitor_tva,tip_decont,"
                            "inreg_art317,operatiuni_ic,regim_fiscal,tip_firma,declarant_nume,declarant_prenume,declarant_functie,"
                            "forma_juridica,capital_subscris,serie_factura,metoda_stoc) VALUES (1,'X SRL','14399840','Str 1','Cluj-Napoca',"
                            "'CJ','6201','BCR','RO49RNCB0000000000000001','0700000000',%s,NULL,%s,true,'micro','srl','Popescu','Ion',"
                            "'ADMINISTRATOR','SRL',200,'SDC','global_valoric')", (platitor, art317))
            yield _P(c)
        finally:
            c.rollback()


def _sql(c, q, args=()):
    with c.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        cur.execute(q, args)
        return cur.fetchall() if cur.description else None


def _serviciu_primit(c, numar="AIS-1", data="2097-09-12", valoare="300"):
    """Factura primită de la prestatorul din DE, serviciu (axa „servicii”), fără operațiunea D301 scrisă de Operațiuni (`achizitie_ic`):
    ce rămâne în evidență când serviciul s-a înregistrat ca factură primită."""
    from core import facturi_api
    _sql(c, "SELECT 1")
    return facturi_api.creeaza_factura(c, numar, data, "primita",
                                       [{"descriere": "Servicii software", "cantitate": 1, "pret_unitar": valoare, "cota_tva": 0}],
                                       tert_nume="LIEFERANT GMBH", tert_cui=COD_PRESTATOR, tert_tara="DE", axa_ic="servicii",
                                       status="importata")["factura_id"]


def _d301_in_calendar(c):
    from core import control_fiscal_api as cf
    _sql(c, "SELECT 1")
    r = cf.evalueaza_firma(c, c, 999999, SCH, AZI, cu_reconciliere=False)
    randuri = [x for k in ("lipsa", "urmarit", "confirmate", "cu_intarziere", "inainte_de_preluare") for x in (r.get(k) or [])]
    return [(x["an"], x["luna"]) for x in randuri if x.get("tip") == "d301" and x.get("an") == 2097]


def test_c163_serviciul_primit_din_ue_face_luna_datorata_pentru_d301(conn):
    """Numai un serviciu primit (300 lei) de la prestatorul din DE, în 09/2097: luna e D301 datorată (faptul pe facturi și Control fiscal).
    MUTAȚIE: `cu_servicii=True` scos din `control_incrucisat.d301_luni_facturi_ic` -> faptul gol, nicio lună D301 -> ROȘU."""
    from core import control_incrucisat as ci
    _serviciu_primit(conn)
    # CF art.307 alin.(2): „Taxa este datorată de orice persoană impozabilă [...] care este beneficiar al serviciilor care au locul
    # prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe
    # teritoriul României”; CF art.324 alin.(1) lit.d: decontul special se depune de persoanele neînregistrate conform art.316 „pentru
    # operațiunile și de către persoanele obligate la plata taxei, conform art. 307 alin. (2)-(4) și (6)”
    assert ci.d301_luni_facturi_ic(conn, SCH, 2097) == {9}
    assert _d301_in_calendar(conn) == [(2097, 9)]


def test_c163_prestarea_emisa_nu_e_luna_d301(conn):
    """Anti-vacuu: serviciul PRESTAT (factură emisă către clientul din DE) nu face lună D301 — D301 e pentru taxa datorată de beneficiar."""
    from core import control_incrucisat as ci, facturi_api, uc_comun
    _sql(conn, "SELECT 1")
    facturi_api.emite_factura(conn, [{"descriere": "Servicii de consultanta IT", "cantitate": 1, "um": "serv.", "pret_unitar": "500",
                                      "cota_tva": 0}], tert_nume="KUNDE GMBH", tert_cui=COD_PRESTATOR, tert_tara="DE",
                              data_emitere="2097-09-10", platitor_tva=uc_comun._platitor_tva_firma(conn))
    assert ci.d301_luni_facturi_ic(conn, SCH, 2097) == set()
    assert _d301_in_calendar(conn) == []


def test_c163_generatorul_numeste_serviciul_neintrodus(conn):
    """Generatorul D301 pe 09/2097 fără operațiuni în ecranul D301, dar cu serviciul primit ca factură: refuzul numește factura (cu tipul 5),
    nu „nicio operațiune cu exigibilitate în perioadă”.
    MUTAȚIE: `cu_servicii=True` scos din `d301.genereaza` -> „D301 nu se generează pe zero: nicio operațiune” -> ROȘU."""
    from core import d301
    from core.common import Perioada
    _serviciu_primit(conn)
    _sql(conn, "SELECT 1")
    with pytest.raises(ValueError) as e:
        d301.genereaza(conn, SCH, Perioada(2097, luna=9))
    # OPANAF 592/2016 (instrucțiunile formularului 301): decontul special se depune pentru perioadele în care ia naștere exigibilitatea
    # taxei — iar serviciul primit e o asemenea operațiune (CF art.307 alin.(2), art.324 alin.(1) lit.d); refuzul întreg:
    assert str(e.value) == (
        "D301 pe zero, dar în perioadă există achiziții intracomunitare (bunuri sau servicii) înregistrate ca facturi și neintroduse în "
        "operațiunile D301 (1): LIEFERANT GMBH (fact. AIS-1, 300,00 lei). Introdu-le în ecranul D301 înainte de generare (serviciile la "
        "tipul 5): obligația D301 se naște din achiziția intracomunitară."), str(e.value)


def test_c163_d301_cu_serviciul_introdus_trece_validatorul_duk(conn):
    """Serviciul primit introdus în D301 (tipul 5, secțiunea 4.1, TVA 21% = 63 lei, cum îl scrie `achizitie_ic`): declarația e validă pe
    DUK. Operațiunile sunt cele citite din bază pe 09/2097; declarația se construiește pe 09/2026, o perioadă pe care validatorul o
    acceptă — aceleași operațiuni, aceeași firmă."""
    from core import d301, duk
    from core.common import Perioada
    from core import repo_d301_operatiuni_api as _r
    if not duk.poate_valida("d301"):
        pytest.skip("DUK d301 indisponibil")
    fid = _serviciu_primit(conn)
    with conn.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        _r.insert_d301_operatiuni(cur, SCH, 2097, 9, 5, "AIS-1", "12.09.2097", 300, "RON", 1, 63, "DE", "811907980", "LIEFERANT GMBH",
                                  None, factura_id=fid)
    _sql(conn, "SELECT 1")
    prof, ops = d301.pull(conn, SCH, Perioada(2097, luna=9))
    assert [(o["tip"], o["nr_doc"]) for o in ops] == [(5, "AIS-1")]
    res = d301.calcul_d301(prof, Perioada(2026, luna=9), [dict(o, data_doc="12.09.2026") for o in ops])
    # OPANAF 592/2016: „În secțiunea 4.1 se preiau din secțiunea 4 doar achizițiile de servicii intracomunitare pentru care beneficiarul e
    # obligat la plata TVA cf. art. 307 alin. (2)” -> serviciul în S4 și în S4.1
    assert (res.totaluri[4], res.totaluri[5]) == ((300, 63), (300, 63)), res.totaluri
    rez = duk.valideaza(d301.build_xml(res), "d301", an=2026, luna=9)
    assert rez["stare"] == "valid", rez


def test_c163_clasa_serviciul_de_la_prestatorul_din_afara_ue_se_introduce_la_tipul_4(conn):
    """Clasa lui C163 (deficiență nouă, găsită de Code): serviciul primit de la un prestator din AFARA UE (aici CH) se declară tot în D301,
    secțiunea 4 (art.307 alin.(2)), dar nu în 4.1 și nu în D390. Până azi tipul 4 cerea temeiul alin.(3)/(5)/(6), deci operațiunea se
    refuza. Acum: introducerea trece cu temeiul „servicii_extra_ue”, D390 o arată exclusă cu motivul, iar D301 e valid pe DUK.
    MUTAȚIE: intrarea „servicii_extra_ue” scoasă din `d301_operatiuni_api.TEMEI_307` -> introducerea se refuză -> ROȘU."""
    from core import d301, d301_operatiuni_api as op, d390, duk
    from core.common import Perioada
    _sql(conn, "SELECT 1")
    r = op.adauga(conn, SCH, 2026, 9, {"tip": 4, "tip_valuta": "CHF", "val_valuta": "100", "curs": "5.5", "cota": 21, "nr_doc": "CH-SRV-1",
                                       "data_doc": "12.09.2026", "partener_tara": "CH", "partener_den": "ANBIETER AG",
                                       "temei_307": "servicii_extra_ue"})
    assert r.get("ok") is True, r
    # OPANAF 592/2016, instrucțiunile D301: „Secţiunea 4 «Operaţiuni prevăzute la art. 307 alin. (2), (3), (5) şi (6) din Codul fiscal» se
    # completează de către: - persoanele impozabile obligate la plata taxei conform art. 307 alin. (2) din Codul fiscal [...] care sunt
    # beneficiare ale serviciilor care au locul prestării în România conform art. 278 alin. (2) din Codul fiscal şi care sunt furnizate de
    # către persoane impozabile care nu sunt stabilite pe teritoriul României”
    assert (r["baza"], r["tva"]) == (550, 116), r     # 100 CHF × 5,5 = 550 lei; 21% = 115,5 -> 116 (ROUND_HALF_UP)
    ex = d390.excluse_d301(conn, SCH, 2026, 9)
    # CF art.325 alin.(1) lit.e: D390 cuprinde achizițiile de servicii „de la persoane impozabile nestabilite în România, dar stabilite în
    # Uniunea Europeană” -> prestatorul din CH nu intră în D390
    assert [(x["semnal"], x["motiv"]) for x in ex] == [
        (False, "exclusă din D390: Servicii primite de la un prestator din afara UE (art. 307 alin. 2)")], ex
    if not duk.poate_valida("d301"):
        pytest.skip("DUK d301 indisponibil")
    prof, ops = d301.pull(conn, SCH, Perioada(2026, luna=9))
    res = d301.calcul_d301(prof, Perioada(2026, luna=9), ops)
    assert (res.totaluri[4], res.totaluri[5]) == ((550, 116), (0, 0)), res.totaluri
    rez = duk.valideaza(d301.build_xml(res), "d301", an=2026, luna=9)
    assert rez["stare"] == "valid", rez
