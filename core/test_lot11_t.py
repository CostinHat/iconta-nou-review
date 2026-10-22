# -*- coding: utf-8 -*-
"""Lotul 11 (comanda Costin 11.1), subagentul T — gărzile pentru 428 (TVA la încasare: ce spune ecranul de emitere la DATA facturii) și
C76 (lipsa de la inventar — și orice ajustare a taxei deductibile scrisă ca notă — ajunge în D300, rd.34; notele cu TVA pe care nicio cale a
decontului nu le duce în D300 se numesc).

Temeiurile (citate verbatim, sursa locală `anaf_surse/`):
  * CF art.282 alin.(3): „exigibilitatea taxei intervine la data încasării contravalorii integrale sau parțiale [...], în cazul persoanelor
    impozabile care optează în acest sens”; alin.(7) lit.a): „în cazul facturilor pentru contravaloarea totală [...] emise înainte de data
    intrării în sistemul de TVA la încasare [...] nu se aplică prevederile alin. (3) și (5)”; CF art.319 alin.(20) lit.p): „mențiunea «TVA
    la încasare»” (cod_fiscal_227_2015_consolidat.txt).
  * HG 1/2016 titlul VII pct.78 alin.(1): „Ajustarea se evidențiază în decontul de taxă aferent perioadei fiscale în care a intervenit
    evenimentul care a generat ajustarea”; alin.(6) lit.a): ajustare negativă la „bunuri lipsă în gestiune din alte cauze decât cele
    prevăzute la art. 304 alin. (2)” (hg_1_2016_norme_cod_fiscal.txt).
  * OPANAF 174/2026, instrucțiunile D300, rândul 34: „diferenţele de taxă pe valoarea adăugată rezultate ca urmare a ajustării taxei
    deductibile, cu semnul plus sau minus, după caz” (opanaf_174_2026_d300.txt). În XML, rândul 34 e R31 (`d300_randuri.RAND_FORMULAR`).

Probele pe bază rulează pe o schemă EFEMERĂ din tenant_template, în tranzacție anulată. Notele de ajustare se scriu direct aici (forma pe
care o scrie inventarul, `stocuri_cv_api._incadreaza_lipsa`: 635 = 4427) — drumul ecranului e în `frontend_test/e2e/e2e_lot11_t.py`.
"""
import datetime as _dt
from decimal import Decimal

import pytest

from core import d300 as _d300
from core import db as _db
from core import tenant_provisioning as _tp
from core import tva_incasare as _tvi
from core.common import Perioada

_SCHEMA = "tenant_test_lot11_t"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════ 428 — textul regimului la data facturii (pur)
_P_NOV = [{"de_la": _dt.date(2026, 11, 1), "pana_la": _dt.date(2028, 12, 31)}]

# Mesajele întregi, pe câmpul `mesaj` (core/test_garzi_pe_text.py: câmpul are valoarea asta, nu „fragmentul apare undeva”).
_M_INAINTE_21_10 = ("Factura din 21.10.2026: firma aplică sistemul TVA la încasare abia de la 01.11.2026. O factură emisă înainte de intrarea "
                    "în sistem rămâne pe regulile generale: TVA exigibil la emitere (4427), fără mențiunea „TVA la încasare” (Cod fiscal art. 282 "
                    "alin. (7) lit. a)). Dacă firma aplica sistemul și la această dată, corectează perioada în Date firmă.")
_M_IN_SISTEM = ("firma aplică sistemul TVA la încasare. TVA-ul facturii se înregistrează pe 4428 (neexigibil) și devine exigibil la încasare; "
                "pe factură apare mențiunea „TVA la încasare” (Cod fiscal art. 282 alin. (3), art. 319 alin. (20) lit. p)). Rămân pe regulile "
                "generale taxarea inversă, livrările scutite și clientul afiliat (art. 282 alin. (6)).")
_M_IN_SISTEM_03_11 = "Factura din 03.11.2026: " + _M_IN_SISTEM
_M_IESIRE = ("Factura din 05.01.2029: firma a ieșit din sistemul TVA la încasare la 31.12.2028. TVA-ul facturii e exigibil la emitere (4427), "
             "fără mențiunea „TVA la încasare”; facturile emise în sistem rămân în sistem până la încasare (Cod fiscal art. 282 alin. (7) lit. b)).")


def test_428_factura_inainte_de_intrare_spune_regulile_generale():
    t = _tvi.text_regim_emitere(_dt.date(2026, 10, 21), False, _P_NOV)
    # CF art.282 alin.(7) lit.a): factura emisă înainte de intrarea în sistem -> regulile generale (4427, fără mențiune)
    assert t["aplica"] is False and t["mesaj"] == _M_INAINTE_21_10, t


def test_428_factura_in_sistem_spune_4428_si_mentiunea():
    t = _tvi.text_regim_emitere(_dt.date(2026, 11, 3), True, _P_NOV)
    # CF art.282 alin.(3) + art.319 alin.(20) lit.p): TVA pe 4428, exigibil la încasare, mențiunea „TVA la încasare”
    assert t["aplica"] is True and t["mesaj"] == _M_IN_SISTEM_03_11, t


def test_428_factura_dupa_iesire_si_firma_fara_sistem():
    t = _tvi.text_regim_emitere(_dt.date(2029, 1, 5), False, _P_NOV)
    assert t["aplica"] is False and t["mesaj"] == _M_IESIRE, t
    assert _tvi.text_regim_emitere(_dt.date(2026, 10, 21), False, []) is None   # firma n-are nimic de-a face cu sistemul


def test_428_indicatorul_fara_data_cere_perioada():
    t = _tvi.text_regim_emitere(_dt.date(2026, 10, 21), True, [], fara_data=True)
    assert t["aplica"] and t["mesaj"] == ("Factura din 21.10.2026: " + _M_IN_SISTEM
                                          + " Data de la care firma aplică sistemul nu e scrisă în Date firmă: scrie-o acolo."), t


# ══════════════════════════════════════════════════════════════════ C76 — clasificarea notelor cu TVA fără factură (pur)
def test_c76_lipsa_neimputabila_e_ajustare_negativa_pe_rd34():
    # HG 1/2016 titlul VII pct.78 alin.(6) lit.a) + OPANAF 174/2026 rd.34 („cu semnul plus sau minus”): 635 = 4427 -> R31 cu minus
    assert _d300.clasifica_nota_tva({"debit": "635", "credit": "4427", "sursa": "stocuri"}) == ("rand", "R31", -1)
    assert _d300.clasifica_nota_tva({"debit": "635", "credit": "4426", "sursa": "operatiuni"}) == ("rand", "R31", -1)


def test_c76_ce_e_declarat_din_alta_sursa_nu_se_numara_a_doua_oara():
    acoperit = [{"debit": "4427", "credit": "4426"}, {"debit": "4427", "credit": "4423"}, {"debit": "4424", "credit": "4426"},
                {"debit": "707", "credit": "4427", "sursa": "horeca_z"}, {"debit": "5311", "credit": "4427", "din_chitanta": True},
                {"debit": "4426", "credit": "401", "sursa": "stocuri"}, {"debit": "4428.01", "credit": "408", "sursa": "stocuri"},
                {"debit": "371", "credit": "4428.02", "sursa": "stocuri"}, {"debit": "4427", "credit": "121", "sursa": "migrare"}]
    assert [(_d300.clasifica_nota_tva(r)[0]) for r in acoperit] == ["acoperit"] * len(acoperit)


def test_c76_nota_cu_tva_fara_cale_spre_decont_e_nedeclarata():
    # chiria încasată din Operațiuni (4111 = 4427), exigibilitatea manuală (4428 = 4427 fără factură), autolichidarea fără factură
    for r in ({"debit": "4111", "credit": "4427", "sursa": "operatiuni"}, {"debit": "4428", "credit": "4427", "sursa": "operatiuni"},
              {"debit": "4426", "credit": "4427", "sursa": "operatiuni"}):
        assert _d300.clasifica_nota_tva(r) == ("nedeclarat", None), r


def _prof():
    return {"nume": "T76 SRL", "cui": "14399840", "adresa": "Str Test 1", "oras": "Bucuresti", "judet": "B", "caen": "4711",
            "banca": "BCR", "iban": "RO49AAAA1B31007593840000", "tip_decont": "L", "tva_la_incasare": False,
            "declarant_nume": "Popescu", "declarant_prenume": "Ion", "declarant_functie": "ADMINISTRATOR"}


def _cu_toate(texte, *fragmente):
    """Mesajele care conțin TOATE fragmentele. Testele cer EXACT unul (nu „oricare”): o listă goală pică, iar două mesaje care ar
    spune același lucru de două ori pică și ele (core/test_garzi_pe_text.py: premisa se verifică, nu se presupune)."""
    return [t for t in texte if all(f in t for f in fragmente)]


def test_c76_calcul_pune_ajustarea_pe_rd34_cu_minus_si_marimea_platii():
    aj = {"ajustare_taxa": True, "rand": "R31", "tva": Decimal("-43.24"), "nota_id": 171, "eticheta": "nr. crt. 34", "linie": "635 = 4427 43,24"}
    fac = [{"directie": "emisa", "id": 1, "total": 1210, "tva": 210, "linii": [(1, 1000, 21)], "tert_tara": "RO", "cui": "18547290"}]
    fara = _d300.calcul_d300(_prof(), Perioada(2026, luna=7), fac)
    cu = _d300.calcul_d300(_prof(), Perioada(2026, luna=7), fac + [aj])
    # OPANAF 174/2026 rd.34: ajustarea negativă a taxei deductibile -> R31_2 = -43; TVA de plată crește cu 43
    assert "R31_2" not in fara.R and cu.R["R31_2"] == -43 and cu.ajustari_taxa == {"R31_2": -43}
    assert cu.tva_de_plata == fara.tva_de_plata + 43 == 253
    assert len(_cu_toate(cu.note_rezultat, "Rândul 34", "635 = 4427 43,24")) == 1, cu.note_rezultat
    # rândul introdus și manual: se spune riscul dublei numărări
    cu_m = _d300.calcul_d300(_prof(), Perioada(2026, luna=7), fac + [aj], manual={"R31_2": -43})
    assert cu_m.R["R31_2"] == -86 and len(_cu_toate(cu_m.avertismente, "aceeași ajustare de două ori")) == 1, cu_m.avertismente


def test_c76_nota_nedeclarata_se_numeste_in_avertismente():
    n = {"nota_tva_nedeclarata": True, "nota_id": 9, "descriere": "Chirie incasata 4111=706", "eticheta": "nr. crt. 9 din 05.07.2026",
         "linie": "4111 = 4427 21,00"}
    res = _d300.calcul_d300(_prof(), Perioada(2026, luna=7), [n])
    assert len(_cu_toate(res.avertismente, "nu intră în decont", "nr. crt. 9 din 05.07.2026", "4111 = 4427 21,00")) == 1, res.avertismente


# ══════════════════════════════════════════════════════════════════ C76 — pe bază: generatorul și a doua cale
@pytest.fixture
def conn_t():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)   # pe tranzacție: nu rămâne pe conexiunea din pool (core/test_lot10_search_path_pool.py)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, regim_fiscal, platitor_tva, tip_decont, "
                    "tva_la_incasare, declarant_nume, declarant_prenume, declarant_functie) VALUES (1,'T76 SRL','14399840','Str Test 1',"
                    "'Bucuresti','B','4711','BCR','RO49AAAA1B31007593840000','real',true,'L',false,'Popescu','Ion','ADMINISTRATOR')")
            yield conn
        finally:
            conn.rollback()


def _nota(conn, data, linii, sursa="stocuri", descriere="Încadrarea lipsei de la inventar: neimputabila", validata=True):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES (%s,%s,%s,'ciorna','Lista de "
                    "inventariere 1') RETURNING id", (data, descriere, sursa))
        nid = cur.fetchone()[0]
        for d, c, s in linii:
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)", (nid, d, c, s))
        if validata:
            cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (nid,))
    return nid


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c76_lipsa_validata_intra_in_d300_si_a_doua_cale_o_confirma(conn_t):
    _nota(conn_t, "2026-07-19", [("607", "371", Decimal("205.90")), ("635", "4427", Decimal("43.24"))])
    _nota(conn_t, "2026-07-20", [("635", "4427", Decimal("7.35"))], validata=False)   # ciorna nu e evidență (R36): nu intră
    _nota(conn_t, "2026-08-02", [("635", "4427", Decimal("5.00"))])                    # altă perioadă: nu intră
    xml, res = _d300.genereaza(conn_t, _SCHEMA, Perioada(2026, luna=7))
    # HG 1/2016 pct.78 alin.(1) „în decontul [...] perioadei fiscale în care a intervenit evenimentul”; OPANAF 174/2026 rd.34 cu minus
    import xml.etree.ElementTree as _ET
    assert res.R.get("R31_2") == -43 and _ET.fromstring(xml).get("R31_2") == "-43", (res.R, xml[:2000])   # atributul declarației, nu un sub-șir
    from core.d300_reconciliere import reconciliaza
    assert reconciliaza(conn_t, Perioada(2026, luna=7), res)["divergente"] == []


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c76_a_doua_cale_prinde_generatorul_care_uita_ajustarea(conn_t, monkeypatch):
    """Non-tautologie: dacă generatorul pierde ajustarea (exact defectul C76), reconcilierea — SQL propriu — refuză declarația."""
    _nota(conn_t, "2026-07-19", [("635", "4427", Decimal("43.24"))])
    monkeypatch.setattr(_d300, "AJUSTARI_TAXA", {})
    from core.d300_reconciliere import ReconciliereD300
    with pytest.raises(ReconciliereD300) as e:
        _d300.genereaza(conn_t, _SCHEMA, Perioada(2026, luna=7))
    m = e.value.args[0]   # mesajul refuzului reconcilierii (câmpul lui), nu reprezentarea excepției
    assert m.replace("−", "-") == (
        "D300: totalurile din decont nu se potrivesc cu recalculul făcut separat din liniile facturilor. Diferențe: rândul 34, coloana TVA "
        "(ajustări ale taxei deductibile din note — lipsa la inventar, 635 = 4427): în declarație 0,00 lei, recalculat -43,00 lei (diferență "
        "43,00 lei). Declarația nu se generează: aplicația nu alege singură care dintre cele două calcule e corect. Verifică datele perioadei; "
        "dacă sunt corecte, anunță echipa iConta."), e.value.args


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c76_nota_cu_tva_fara_cale_e_numita_la_generare(conn_t):
    _nota(conn_t, "2026-07-05", [("4111", "706", Decimal("100.00")), ("4111", "4427", Decimal("21.00"))], sursa="operatiuni",
          descriere="Chirie incasata 4111=706")
    _xml, res = _d300.genereaza(conn_t, _SCHEMA, Perioada(2026, luna=7))
    assert len(_cu_toate(res.avertismente, "nu intră în decont", "4111 = 4427 21,00")) == 1, res.avertismente


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c76_d300_cu_ajustarea_trece_duk(conn_t):
    from core import duk
    _nota(conn_t, "2026-07-19", [("635", "4427", Decimal("43.24"))])
    xml, _res = _d300.genereaza(conn_t, _SCHEMA, Perioada(2026, luna=7))
    v = duk.valideaza(xml, "d300", an=2026, luna=7)
    assert v["stare"] in ("valid", "gri"), v   # „gri” = validatorul nu e instalat pe mașina care rulează; aici nu e „invalid”
    if v["stare"] == "gri":
        pytest.skip("DUK indisponibil: %s" % v.get("temei"))


# ══════════════════════════════════════════════════════════════════ 428 — pe bază: regimul la data facturii și refuzul notei din Operațiuni
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_428_regim_emitere_si_refuzul_notei_citesc_perioada_firmei(conn_t):
    with conn_t.cursor() as cur:
        cur.execute("INSERT INTO tva_incasare_perioade (de_la, pana_la, sursa) VALUES ('2026-11-01', '2028-12-31', 'manual')")
        inainte = _tvi.regim_emitere_la(cur, None, _dt.date(2026, 10, 21))
        dupa = _tvi.regim_emitere_la(cur, None, _dt.date(2026, 11, 3))
        assert inainte["aplica"] is False and inainte["mesaj"] == _M_INAINTE_21_10, inainte
        assert dupa["aplica"] is True, dupa
        # CF art.282 alin.(3): la o firmă în sistem, livrarea cu TVA intră pe drumul facturii, nu ca notă pe 4427
        assert _tvi.refuz_nota_tva_la_emitere(cur, None, _dt.date(2026, 10, 21), "chiria încasată") is None
        m = _tvi.refuz_nota_tva_la_emitere(cur, None, _dt.date(2026, 11, 3), "chiria încasată")
        assert m == ("Firma aplică sistemul TVA la încasare la 03.11.2026: chiria încasată se înregistrează ca factură emisă (Emite factură, "
                     "sau factura emisă în alt program adăugată în Facturi), nu ca notă. Pe factură TVA-ul merge pe 4428, devine exigibil la "
                     "încasare și intră în D300 și D394 (Cod fiscal art. 282 alin. (3)); nota de aici l-ar pune direct pe 4427, exigibil la "
                     "emitere."), m
        from core import regim_tva_incasare as _rg
        assert _rg.stare(cur, azi=_dt.date(2026, 10, 21))["text"] == "de la 01.11.2026 până la 31.12.2028"


# ══════════════════════════════════════════════════════════════════ BT-48 — codul de TVA al clientului român numai dacă e plătitor
_FZ = {"nume": "Firma SRL", "cui": "14399840", "platitor_tva": True, "adresa": "Str. A 1", "oras": "Sector 1", "judet": "B", "tara": "RO"}
_LINIE = [{"descriere": "Servicii", "cantitate": 1, "pret_unitar": "100", "cota_tva": 21, "um": "buc"}]


def _xml_client(platitor):
    from core import efactura_send as _es
    cl = {"nume": "Client SRL", "cui": "18547290", "adresa": "Str. B 2", "oras": "Sector 2", "judet": "B", "tara": "RO",
          "platitor_tva": platitor}
    return _es.genereaza_xml({"serie": "T", "numar": "T1", "data_emitere": "2026-10-21", "data_scadenta": "2026-11-20", "moneda": "RON"},
                             _LINIE, _FZ, cl)


_NS_UBL = {"cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
           "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"}


def _cumparator(xml):
    """Elementul `cac:Party` al cumpărătorului (AccountingCustomerParty), din arborele XML — nu un fragment de text."""
    import xml.etree.ElementTree as _ET
    p = _ET.fromstring(xml).findall("cac:AccountingCustomerParty/cac:Party", _NS_UBL)
    assert len(p) == 1, xml
    return p[0]


def _coduri(party, cale):
    return [e.text for e in party.findall(cale, _NS_UBL)]


def test_bt48_numai_la_clientul_platitor_de_tva():
    # EN 16931 BR-CO-09: BT-48 e „Buyer VAT identifier” (cu prefixul țării); CF art.319 alin.(20) lit.f): „codul de înregistrare în
    # scopuri de TVA sau codul de identificare fiscală al beneficiarului” -> neplătitorul / necunoscutul: numai CUI-ul, la BT-47
    pl = _cumparator(_xml_client(True))
    assert _coduri(pl, "cac:PartyTaxScheme/cbc:CompanyID") == ["RO18547290"]
    def _fara_cod_tva(st):
        c = _cumparator(_xml_client(st))
        assert c.findall("cac:PartyTaxScheme", _NS_UBL) == [], st
        assert _coduri(c, ".//cbc:CompanyID") == ["18547290"], (st, _coduri(c, ".//cbc:CompanyID"))
    _fara_cod_tva(False)   # neplătitor
    _fara_cod_tva(None)    # stare necunoscută


def test_bt48_clientul_neplatitor_trece_validatorul_anaf_fact1():
    """Judecătorul de structură: validatorul oficial ANAF (FACT1, public, fără token). Fără rețea -> sărit (nu verde fals)."""
    from core import efactura_send as _es
    try:
        ok, mesaje = _es.valideaza(_xml_client(False))
    except Exception as e:   # noqa: BLE001 — rețea indisponibilă: testul nu poate judeca, deci se sare, cu motivul
        pytest.skip("validatorul ANAF FACT1 indisponibil: %s" % e)
    assert ok, mesaje


# ══════════════════════════════════════════════════════════════════ D394 — județul din fișa partenerului; refuzul trimite la fișă
def test_d394_refuzul_judetului_trimite_la_fisa_partenerului():
    from core import d394 as _d394
    from core.erori import RefuzGenerare
    k = ("L", _d394.P_NEINREG, 21, None, "Ion Popescu")
    with pytest.raises(RefuzGenerare) as e:
        _d394.judete_partener({k: {}}, {}, {})
    # decizia Costin 10.3 pct.4: „refuzul declarației trimite direct acolo” — fișa clientului, câmpul județului
    assert (e.value.ecran, e.value.camp_ecran) == ("clienti", "partener:nume-ION_POPESCU:judet"), (e.value.ecran, e.value.camp_ecran)
    assert e.value.args[0] == (
        "D394 nu se poate genera: lipsește județul pe factură la 1 partener fără cod de TVA (persoane fizice sau firme neînregistrate) — D394 "
        "îl cere pentru fiecare partener fără cod (structura ANAF a declarației îl face obligatoriu): Ion Popescu (operațiunea L). Completează "
        "județul în fișa partenerului (Clienți / Furnizori) sau pe factura lui (ori la operațiunea adăugată manual) și generează din nou."), e.value.args


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d394_citeste_judetul_din_fisa_cand_factura_nu_il_are(conn_t):
    from core import repo_d394
    import psycopg2.extras as _E
    with conn_t.cursor() as cur:
        cur.execute("INSERT INTO clienti (nume, cui, judet) VALUES ('Ion Popescu', NULL, 'CJ') RETURNING id")
        cid = cur.fetchone()[0]
        cur.execute("INSERT INTO facturi (numar, data_emitere, directie, tip, total, tva, tert_nume, tert_cui, client_id, status) "
                    "VALUES ('T1', '2026-07-10', 'emisa', 'factura', 121, 21, 'Ion Popescu', NULL, %s, 'de_preluat') RETURNING id", (cid,))
        fid = cur.fetchone()[0]
    with conn_t.cursor(cursor_factory=_E.RealDictCursor) as cur:
        r = [x for x in repo_d394.select_facturi(cur, "2026-07-01", "2026-08-01") if x["id"] == fid]
    assert r and r[0]["tert_judet"] == "CJ", r


def test_c76_controlul_incrucisat_nu_numara_ajustarea_la_tva_colectata():
    """[lotul 11, C76 — patch-ul T §10.2] 635 = 4427 creditează 4427, dar D300 o declară la rd.34 (R31): comparația „TVA colectată”
    (R17_2 față de rulajul creditor 4427) o scade, altfel arată o diferență egală cu ajustarea (HG 1/2016 titlul VII pct.78 alin.(6)
    lit.a). MUTAȚIE: scăderea scoasă din `compara_tva` -> pică."""
    from decimal import Decimal as _D
    from core import control_incrucisat as ci
    rulaje = {"4427": {"debit": _D("0"), "credit": _D("1265.24")}, "4426": {"debit": _D("0"), "credit": _D("0")}}
    rez = ci.compara_tva({"R17_2": 1222, "R27_2": 0}, rulaje, 2099, 10, [], ajustari_4427=_D("43.24"))
    col = [r for r in rez if r.get("cont") == "4427"][0]
    assert col["contabil"] == _D("1222.00") and col["diferenta"] == 0, col   # rd.17 1.222 = 1.265,24 − 43,24
