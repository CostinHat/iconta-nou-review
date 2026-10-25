# -*- coding: utf-8 -*-
"""[lotul 12, C154 + C155] Prestarea intracomunitară de servicii a firmei NEPLĂTITOARE înregistrate în scopuri de TVA după CF art.317.

C154 — „Emite factură” la neplătitor: liniile primesc toate categoria regimului special („neplatitor”, O — `categorii_tva.verifica_linii`),
categorie fără axă, deci `categorii_tva.axa_facturii` nu dădea nimic și factura rămânea cu `axa_ic` NULL. D390 lua atunci implicitul
„bunuri” (`d390._tip_din_axa` -> None -> L): serviciul către clientul din DE ieșea livrare intracomunitară de bunuri (L 500), nu prestare
(P). Pe drumul din Operațiuni (`uc_tenants.vanzare_ic`) axa venea dată de apelant („servicii”) și ieșea corect P. Cauza e locul unde se
naște axa (`facturi_api.creeaza_factura`, punctul unic al emiterii): acum, când categoria nu pune axă și apelantul n-a dat una, axa vine
din felul liniilor (`categorii_tva.axa_neplatitor`: contul de venit, 704 servicii / 701, 703, 707 bunuri — `facturi.VENIT`).

C155 — calendarul D390 al neplătitorului art.317 (`control_fiscal_api.evalueaza_firma`, „restanțele” din Control fiscal) lua faptul pe
facturi din `control_incrucisat.d301_luni_facturi_ic`, adică faptul D301: numai achizițiile de bunuri PRIMITE. Luna cu servicii prestate
intracomunitar (D390 calculat: P 1000) nu era lună datorată. Acum: `control_incrucisat.d390_luni_neplatitor` = lunile cu operațiuni în
D390-ul lunii (`d390.d390_are_operatiuni`, același fapt ca la plătitor) + lunile din ecranul D301.

Temei (anaf_surse/cod_fiscal_227_2015_consolidat.txt):
  · CF art.325 alin.(1) lit.c — „Orice persoană impozabilă înregistrată în scopuri de TVA conform art. 316 sau 317 trebuie să întocmească
    și să depună [...] o declarație recapitulativă în care menționează: [...] c) prestările de servicii prevăzute la art. 278 alin. (2)
    efectuate în beneficiul unor persoane impozabile nestabilite în România, dar stabilite în Uniunea Europeană [...]”;
  · CF art.325 alin.(2) — „Declarația se întocmește pentru fiecare lună calendaristică în care ia naștere exigibilitatea taxei pentru
    operațiunile prevăzute la alin. (1)”;
  · CF art.317 alin.(1) lit.b — înregistrarea neplătitorului care „prestează servicii care au locul în alt stat membru, pentru care
    beneficiarul serviciului este persoana obligată la plata taxei”;
  · CF art.310 alin.(10) lit.b — neplătitorul „nu are voie să menționeze taxa pe factură” (linia rămâne cu 0%).
Judecătorul structurii: validatorul DUK local (`core/duk.py`, `valideaza(xml, "d390", an=, luna=)`).

Schemă efemeră din `tenant_template.sql`, tranzacție anulată, date sintetice în 2097. CUI firmei: 14399840 (cifra de control verificată
cu algoritmul din CLAUDE.md); clientul DE811907980 (cel din proba R187 / C78 / C110). Fiecare caz rulează pe plătitorul art.316 (ca să nu
se strice el) și pe neplătitorul înregistrat art.317 (forma firmei de test F3)."""
import datetime
import io
import os

import pytest

from core import db as _db, tenant_provisioning as _tp

SCH = "tenant_test_lot12_c154"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COD_CLIENT = "DE811907980"
#: ziua „de azi” a calendarului: 24.10.2097 — D390 pe 09/2097 are termenul 25.10.2097 (OPANAF 705/2020 pct.1.2), în fereastra evaluată
AZI = datetime.date(2097, 10, 24)
SERVICIU = "Servicii de consultanta IT"   # felul din denumire („servici” -> 704, `facturi.tip_din_denumire`), ca la emiterea din ecran


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


#: (plătitor, înregistrat art.317, tip decont): plătitorul art.316 și neplătitorul înregistrat art.317 (forma firmei de test F3)
FIRME = {"platitor": (True, False, "lunar"), "neplatitor_art317": (False, True, None)}


class _P:
    """Conexiunea testului, cu starea de plătitor scrisă în profil (pentru aserțiuni); commit / rollback nu închid tranzacția testului."""
    def __init__(s, c, platitor): s._c, s.platitor = c, platitor
    def commit(s): pass
    def rollback(s): pass
    def __getattr__(s, n): return getattr(s._c, n)


@pytest.fixture(params=sorted(FIRME))
def conn(request):
    if not _db_ok():
        pytest.skip("DB indisponibil")
    platitor, art317, decont = FIRME[request.param]
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,telefon,platitor_tva,tip_decont,"
                            "inreg_art317,operatiuni_ic,regim_fiscal,tip_firma,declarant_nume,declarant_prenume,declarant_functie,"
                            "forma_juridica,capital_subscris,serie_factura,metoda_stoc) VALUES (1,'X SRL','14399840','Str 1','Cluj-Napoca',"
                            "'CJ','6201','BCR','RO49RNCB0000000000000001','0700000000',%s,%s,%s,true,'micro','srl','Popescu','Ion',"
                            "'ADMINISTRATOR','SRL',200,'SDC','global_valoric')", (platitor, decont, art317))
            yield _P(c, platitor)
        finally:
            c.rollback()


def _sql(c, q, args=()):
    with c.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        cur.execute(q, args)
        return cur.fetchall()


def _emite(c, descriere=SERVICIU, data="2097-09-10", pret="500", tert_tara="DE", tert_cui=COD_CLIENT, **k):
    """„Emite factură”, cu payload-ul ecranului (`emitere_ecran.trimiteEmitere`: linia fără cont de venit, cota 0; la plătitor categoria
    pe care i-o propune ecranul pentru clientul UE valid în VIES, „serviciu_extern” — deficiența 326; la neplătitor ecranul n-are listă)
    și starea de plătitor citită din profil, ca use-case-ul (`uc_tenants.facturi_emite` -> `uc_comun._platitor_tva_firma`)."""
    from core import facturi_api, uc_comun
    _sql(c, "SELECT 1")
    linie = {"descriere": descriere, "cantitate": 1, "um": "serv.", "pret_unitar": pret, "cota_tva": 0, "cota_propusa": 0,
             "articol_id": None, "categorie_tva": "serviciu_extern" if c.platitor else None}
    linie.update(k.pop("linie", {}))
    r = facturi_api.emite_factura(c, [linie], tert_nume="KUNDE GMBH", tert_cui=tert_cui, tert_tara=tert_tara, data_emitere=data,
                                  platitor_tva=uc_comun._platitor_tva_firma(c), **k)
    return r["factura_id"]


def _d390(c, an=2097, luna=9):
    from core import d390
    _sql(c, "SELECT 1")
    prof, facturi = d390.pull(c, SCH, an, luna)
    return prof, facturi, d390.calcul_d390(prof, an, luna, facturi)


# ── C154 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_c154_serviciul_emis_catre_client_ue_intra_in_d390_ca_prestare(conn):
    """Emite factură: serviciu (500 lei) către clientul din DE. Pe ambele firme: axa „servicii” pe document și D390 = P 500 (CF art.325
    alin.(1) lit.c), niciun L. La neplătitor linia rămâne 0% (CF art.310 alin.(10) lit.b), contul 704 — [C156] cu categoria prestării art.317.
    MUTAȚIE: felul liniei din contul de venit stricat (`categorii_tva._axa_linie` -> None) -> pe neplătitor nici categoria art.317, nici
    axa din felul liniilor: axa NULL și D390 = L 500 -> ROȘU. (De la C156 axa neplătitorului art.317 vine din categoria liniei; ramura
    `axa_neplatitor` rămâne pentru neplătitorul neînregistrat — vezi `test_c154_axa_neplatitor_nu_ghiceste`.)"""
    from core import categorii_tva
    fid = _emite(conn)
    # [lotul 12, C156, decizia Costin 12.3 pct.3] la neplătitorul înregistrat art.317 prestarea către clientul din UE e AE („taxare inversă”,
    # codul RO art.317) — `categorii_tva.PRESTARE_IC_317`, aceeași ca la plătitor; înainte `NEPLATITOR` (O)
    asteptat = "serviciu_extern" if conn.platitor else categorii_tva.PRESTARE_IC_317
    assert _sql(conn, "SELECT categorie_tva, cota_tva::text, cont_venit FROM factura_linii WHERE factura_id = %s", (fid,)) == [
        (asteptat, "0.00", "704")]
    assert _sql(conn, "SELECT axa_ic, tert_tara FROM facturi WHERE id = %s", (fid,)) == [("servicii", "DE")]
    _prof, _f, res = _d390(conn)
    # CF art.325 alin.(1) lit.c: prestarea art.278 alin.(2) către clientul stabilit în UE -> cod P, baza pe client
    assert sorted((k[0], k[1], k[2], v) for k, v in res.ops.items()) == [("P", "DE", "811907980", 500)], res.ops
    assert (res.rezumat["P"], res.rezumat["L"], res.nr_opi) == (500, 0, 1), res.rezumat


def test_c154_d390_cu_prestarea_trece_validatorul_duk(conn):
    """Proba până la validatorul DUK local: D390 cu prestarea emisă din „Emite factură” (P 500) e valid. Operațiunile sunt cele citite
    din bază pe 09/2097 (perioada sintetică a fixture-ului); declarația se construiește pe 09/2026, o perioadă pe care validatorul o
    acceptă — aceleași operațiuni, aceeași firmă."""
    from core import d390, duk
    if not duk.poate_valida("d390"):
        pytest.skip("DUK d390 indisponibil")
    _emite(conn)
    prof, facturi, _res = _d390(conn)
    res = d390.calcul_d390(prof, 2026, 9, facturi)
    assert [k[0] for k in res.ops] == ["P"], res.ops
    rez = duk.valideaza(d390.build_xml(res), "d390", an=2026, luna=9)
    assert rez["stare"] == "valid", rez


def test_c154_bunurile_si_clientul_din_romania_raman_cum_erau(conn):
    """Felul liniilor decide axa numai la neplătitor și numai pentru clientul din altă țară; bunurile (contul 707) rămân L, ca înainte;
    clientul din România nu primește axă intracomunitară. Plătitorul: axa vine numai din categorie (taxabila RO fără axă)."""
    if conn.platitor:
        fid = _emite(conn, descriere="Marfa revanzare", linie={"categorie_tva": "livrare_ic"})
        assert _sql(conn, "SELECT axa_ic FROM facturi WHERE id = %s", (fid,)) == [("bunuri",)]
        fid_ro = _emite(conn, descriere=SERVICIU, tert_tara="RO", tert_cui="RO14399840", data="2097-09-11",
                        linie={"cota_tva": 21, "categorie_tva": None})
    else:
        fid = _emite(conn, descriere="Marfa revanzare")
        assert _sql(conn, "SELECT cont_venit FROM factura_linii WHERE factura_id = %s", (fid,)) == [("707",)]
        assert _sql(conn, "SELECT axa_ic FROM facturi WHERE id = %s", (fid,)) == [("bunuri",)]
        fid_ro = _emite(conn, descriere=SERVICIU, tert_tara="RO", tert_cui="RO14399840", data="2097-09-11")
    assert _sql(conn, "SELECT axa_ic FROM facturi WHERE id = %s", (fid_ro,)) == [(None,)]
    _prof, _f, res = _d390(conn)
    assert sorted(k[0] for k in res.ops) == ["L"], res.ops


def test_c154_axa_data_de_apelant_ramane_a_lui(conn):
    """Prestarea din Operațiuni dă axa explicit (`uc_tenants.vanzare_ic`: `axa_ic=corp["tip"]`), cu contul de venit ales de om: un cont de
    bunuri (707) pe o prestare declarată „servicii” nu schimbă axa și nu produce refuz (ca la plătitor, unde axa vine din categorie)."""
    if conn.platitor:
        pytest.skip("la plătitor axa vine din categoria liniei (serviciu_extern), nu din apelant")
    fid = _emite(conn, axa_ic="servicii", linie={"cont_venit": "707"})
    assert _sql(conn, "SELECT axa_ic FROM facturi WHERE id = %s", (fid,)) == [("servicii",)]


def test_c154_axa_neplatitor_nu_ghiceste():
    """`categorii_tva.axa_neplatitor` — pură: axa numai pentru liniile „neplatitor” cu un fel cunoscut, toate de același fel, către un
    client din altă țară; altfel None (nimic ghicit)."""
    from core import categorii_tva as ct
    n = ct.NEPLATITOR["cod"]

    def l(cont, cat=n):
        return {"categorie_tva": cat, "cont_venit": cont}
    assert ct.axa_neplatitor([l("704")], "DE") == "servicii"
    assert ct.axa_neplatitor([l("704.01")], "de") == "servicii"            # analiticul contului de venit
    assert ct.axa_neplatitor([l("707"), l("701")], "FR") == "bunuri"
    assert ct.axa_neplatitor([l("704"), l("707")], "DE") is None            # feluri diferite: D390 nu le poate despărți pe o factură
    assert ct.axa_neplatitor([l("708")], "DE") is None                      # „activități diverse”: felul nu se știe
    assert ct.axa_neplatitor([l(None)], "DE") is None
    assert ct.axa_neplatitor([l("704")], "RO") is None and ct.axa_neplatitor([l("704")], None) is None
    assert ct.axa_neplatitor([l("704", "serviciu_extern")], "DE") is None   # plătitorul: axa vine din categorie (`axa_facturii`)
    assert ct.axa_neplatitor([], "DE") is None


# ── C155 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _d390_in_calendar(c):
    """Rândurile D390 ale firmei în verdictul Control fiscal (`evalueaza_firma`, toate grupele în care poate sta un rând datorat)."""
    from core import control_fiscal_api as cf
    _sql(c, "SELECT 1")
    r = cf.evalueaza_firma(c, c, 999999, SCH, AZI, cu_reconciliere=False)
    randuri = [x for k in ("lipsa", "urmarit", "confirmate", "cu_intarziere", "inainte_de_preluare") for x in (r.get(k) or [])]
    return [(x["an"], x["luna"], x.get("fapt")) for x in randuri if x.get("tip") == "d390"]


def test_c155_luna_cu_prestare_ic_e_luna_datorata_pentru_d390(conn):
    """Luna 09/2097 are numai prestarea IC emisă (D390: P 500). Neplătitorul art.317: lunile datorate D390 = {9} și verdictul Control
    fiscal are D390 09/2097 cu faptul pe care se sprijină (CF art.325 alin.(1) lit.c + alin.(2)). Plătitorul: la fel (faptul lui, neatins).
    MUTAȚIE: `_d390_luni_neplat` din `control_fiscal_api.evalueaza_firma` înapoi pe `d301_luni_operatiuni | d301_luni_facturi_ic` ->
    neplătitorul n-are niciun D390 -> ROȘU."""
    from core import control_incrucisat as ci
    _emite(conn)
    if not conn.platitor:
        assert ci.d390_luni_neplatitor(conn, SCH, 2097, AZI) == {9}
        assert ci.d301_luni_facturi_ic(conn, SCH, 2097) == set()   # faptul D301 (achiziții primite) rămâne al D301: nu e lună D301
    d390 = [(a, m, f) for a, m, f in _d390_in_calendar(conn) if a == 2097]
    if conn.platitor:
        assert [(a, m) for a, m, _f in d390] == [(2097, 9)], d390
    else:
        assert d390 == [(2097, 9, "operațiuni intracomunitare înregistrate în 09/2097")], d390


def test_c155_achizitia_de_servicii_primita_e_si_ea_luna_d390(conn):
    """Achiziția intracomunitară de servicii (factură primită cu axa „servicii”, D390 cod S — CF art.325 alin.(1) lit.e) face luna
    datorată la neplătitorul art.317; înainte, `facturi_ic` fără servicii o scotea și pe ea."""
    from core import control_incrucisat as ci, facturi_api
    if conn.platitor:
        pytest.skip("la plătitor calendarul D390 vine din `d390_are_operatiuni` (neschimbat)")
    _sql(conn, "SELECT 1")
    facturi_api.creeaza_factura(conn, "AIS-1", "2097-08-12", "primita",
                                [{"descriere": "Servicii software", "cantitate": 1, "pret_unitar": "300", "cota_tva": 0}],
                                tert_nume="LIEFERANT GMBH", tert_cui=COD_CLIENT, tert_tara="DE", axa_ic="servicii", status="importata")
    _p, _f, res = _d390(conn, 2097, 8)
    assert sorted((k[0], v) for k, v in res.ops.items()) == [("S", 300)], res.ops
    assert ci.d390_luni_neplatitor(conn, SCH, 2097, AZI) == {8}


def test_c155_luna_fara_operatiuni_nu_e_datorata(conn):
    """Anti-vacuu: fără nicio operațiune intracomunitară, nicio lună D390 la neplătitor (calendarul nu inventează restanțe)."""
    from core import control_incrucisat as ci
    if conn.platitor:
        pytest.skip("neplătitorul art.317")
    _emite(conn, tert_tara="RO", tert_cui="RO14399840")
    assert ci.d390_luni_neplatitor(conn, SCH, 2097, AZI) == set()
    assert [x for x in _d390_in_calendar(conn) if x[0] == 2097] == []
