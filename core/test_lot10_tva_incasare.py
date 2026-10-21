# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 428, comanda Costin 10.1, PRIORITAR] TVA la încasare (CF art.282) — motorul, de la factură la D300 / D394.

Comanda, verbatim: „facturile emise poartă mențiunea obligatorie și înregistrează TVA pe 4428; fiecare încasare (bancă, casă,
compensare) legată de factură mută automat partea încasată în 4427; D300 și D394 urmează exigibilitatea; ieșirea din sistem face
regularizarea. Verifică și partea de cumpărare (furnizor cu TVA la încasare). Formularul manual rămâne doar pentru cazuri speciale.”

Temeiul e citat verbatim pe linie, lângă fiecare assert (`anaf_surse/cod_fiscal_227_2015_consolidat.txt`).

Profilul de probă, într-o schemă efemeră din `tenant_template.sql` (ROLLBACK la final), firma în sistem din 01.10.2026 până la
30.11.2026 (ieșirea, CF art.282 alin.(5): „Radierea [...] începând cu prima zi a perioadei fiscale următoare”):
  F0  emisă 20.09 (înainte de intrare) 1.000 + 210, încasată în casă 25.10          -> regulile generale (4427)
  F1  emisă 10.10 1.000 + 210, încasată 605 în casă pe 20.10 și 605 prin bancă pe 05.11 -> 105 în octombrie, 105 în noiembrie
  F2  emisă 12.10 1.000 + 210, încasată 605 pe 15.10, stornată integral pe 18.10      -> alin.(10): 105 anulat pe 4428, 105 exigibil
  P1  primită 08.10 de la un furnizor normal 1.000 + 210, plătită în casă pe 22.10    -> art.297 alin.(3): 210 deductibil în octombrie
  P2  primită 09.10 de la un furnizor în sistem 500 + 105, plătită 302,50 prin bancă   -> art.297 alin.(2): 52,50 deductibil (AI)
  F3  emisă 15.11 (în sistem) 2.000 + 420, încasată în casă pe 10.12 (după ieșire)    -> alin.(7) lit.b: rămâne în sistem
  F4  emisă 05.12 (după ieșire) 1.000 + 210                                            -> regulile generale (4427)
CUI-urile: firma 14399840, clientul 18547290, furnizorii 1590082 / 24736200 — cifra de control verificată cu algoritmul din CLAUDE.md.
"""
import re
import xml.etree.ElementTree as ET
from decimal import Decimal

import pytest

from core import db as _db, tenant_provisioning as _tp
from core import tva_incasare as _tvi
from core.common import Perioada

_SCHEMA = "test_lot10_tva_incasare"
D = Decimal


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _duk(tip):
    try:
        from core import duk
        return duk if duk.poate_valida(tip) else None
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════ PUR: regimul facturii
def _f(**k):
    b = {"id": 1, "tip": "factura", "directie": "emisa", "tva": 210, "data_emitere": "2026-10-10"}
    b.update(k)
    return b


def test_emisa_in_sistem_la_data_ei_merge_la_incasare():
    # CF art.282 alin.(3): „exigibilitatea taxei intervine la data încasării contravalorii integrale sau parțiale”
    assert _tvi.regim_din_date(_f(), [21], True) == _tvi.REGIM_INCASARE
    # alin.(7) lit.a): factura emisă înainte de intrare (firma nu era în sistem la data ei) -> regulile generale
    assert _tvi.regim_din_date(_f(), [21], False) == _tvi.REGIM_GENERAL


def test_excluderile_alin_6_raman_pe_regulile_generale():
    # CF art.282 alin.(6): „nu aplică sistemul respectiv pentru [...] a) [...] art. 307 alin. (2)-(6) sau art. 331”
    assert _tvi.regim_din_date(_f(taxare_inversa=True), [21], True) == _tvi.REGIM_GENERAL
    # „b) livrările de bunuri/prestările de servicii care sunt scutite de TVA”
    assert _tvi.regim_din_date(_f(tva=0), [0], True) == _tvi.REGIM_GENERAL
    assert _tvi.motiv_excludere(_f(), [0, 0]) is not None
    # „d) [...] beneficiarul este o persoană afiliată furnizorului/prestatorului potrivit art. 7 pct. 26”
    assert _tvi.regim_din_date(_f(beneficiar_afiliat=True), [21], True) == _tvi.REGIM_GENERAL
    # factura mixtă (21% + 0%): partea taxabilă e în sistem
    assert _tvi.regim_din_date(_f(), [21, 0], True) == _tvi.REGIM_INCASARE


def test_primita_deducere_amanata_furnizor_sau_firma():
    p = _f(directie="primita")
    # CF art.297 alin.(2): „de la o persoană impozabilă care aplică sistemul TVA la încasare [...] este amânat până la data la care
    # taxa [...] a fost plătită furnizorului”
    assert _tvi.regim_din_date(dict(p, furnizor_tva_incasare=True), None, False) == _tvi.REGIM_INCASARE
    # alin.(3): „achizițiilor efectuate de o persoană impozabilă care aplică sistemul TVA la încasare”
    assert _tvi.regim_din_date(p, None, True) == _tvi.REGIM_INCASARE
    assert _tvi.regim_din_date(p, None, False) == _tvi.REGIM_GENERAL
    # alin.(3) teza finală: „nu se aplică pentru achizițiile intracomunitare de bunuri, pentru importuri, [...] taxare inversă”
    assert _tvi.regim_din_date(dict(p, tert_tara="DE"), None, True) == _tvi.REGIM_GENERAL
    assert _tvi.regim_din_date(dict(p, taxare_inversa=True), None, True) == _tvi.REGIM_GENERAL


def test_stornarea_urmeaza_factura_stornata():
    # CF art.282 alin.(10): „regimul de impozitare, cotele aplicabile și cursul de schimb valutar sunt aceleași ca și ale operațiunii
    # de bază”
    s = _f(storno_din_id=7, tva=-210)
    assert _tvi.regim_din_date(s, None, False, _tvi.REGIM_INCASARE) == _tvi.REGIM_STORNO
    assert _tvi.regim_din_date(s, None, True, _tvi.REGIM_GENERAL) == _tvi.REGIM_GENERAL


def test_parte_exigibila_suta_marita_si_plafonul_restului():
    # CF art.282 alin.(8): „fiecare încasare totală sau parțială se consideră că include și taxa aferentă” — 605 din 1.210 -> 105
    assert _tvi.parte_exigibila(210, 1210, 605, 210) == D("105.00")
    assert _tvi.parte_exigibila(210, 1210, 605, 210) == _tvi.tva_din_incasare(605, 21)
    # ultima încasare nu depășește ce a rămas pe 4428
    assert _tvi.parte_exigibila(210, 1210, 1210, D("104.99")) == D("104.99")
    assert _tvi.parte_exigibila(210, 1210, 605, 0) == 0


def test_anularea_reduce_intai_taxa_neexigibila():
    # CF art.282 alin.(10) lit.a) pct.2: „se operează reducerea taxei neexigibile [...] iar în situația în care cuantumul taxei aferente
    # anulării depășește taxa neexigibilă, pentru diferență exigibilitatea taxei intervine la data anulării operațiunii”
    assert _tvi.imparte_anulare(-210, 105) == (D(105), D(105))
    assert _tvi.imparte_anulare(-100, 105) == (D(100), D(0))
    note = [{"debit": "4111", "credit": "707", "suma": D(-1000)}, {"debit": "4111", "credit": "4428", "suma": D(-210)}]
    out = _tvi.note_storno(note, "emisa", 105)
    assert [(n["debit"], n["credit"], n["suma"]) for n in out] == [
        ("4111", "707", D(-1000)), ("4111", "4428", D(-105)), ("4111", "4427", D(-105))]


# ═══════════════════════════════════════════════════════════════════════ PROFILUL DE PROBĂ (bază de test)
_CLIENT, _FURN, _FURN_TVAI = "18547290", "1590082", "24736200"


def _factura(cur, numar, data, directie="emisa", baza=1000, cota=21, cui=_CLIENT, furnizor_tvai=False, storno_din=None):
    tva = D(baza) * cota / 100
    cur.execute("INSERT INTO facturi (numar, serie, data_emitere, directie, total, tva, total_lei, tva_lei, tert_nume, tert_cui, tert_tara, "
                "tert_platitor_tva, tert_adresa, tert_oras, tert_judet, furnizor_tva_incasare, storno_din_id, status) "
                "VALUES (%s,'TV',%s,%s,%s,%s,%s,%s,'PARTENER PROBA SRL',%s,'RO',true,'Str. Probei 1','Sector 1','B',%s,%s,'emisa') "
                "RETURNING id", (numar, data, directie, D(baza) + tva, tva, D(baza) + tva, tva, cui, furnizor_tvai, storno_din))
    fid = cur.fetchone()[0]
    cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva, cont_cheltuiala) "
                "VALUES (%s,'servicii',%s,1000,%s,%s)", (fid, D(baza) / 1000, cota, None if directie == "emisa" else "628"))
    return fid


def _conteaza(conn, fid):
    from core import contare_facturi as _cf
    with _cf.cursor_dict(conn) as cur:
        return _cf.contabilizeaza(cur, "", fid, automat=True, cont_cheltuiala=None)


def _linii(conn, iid):
    with conn.cursor() as cur:
        cur.execute("SELECT cont_debit, cont_credit, suma FROM inregistrari_linii WHERE inregistrare_id = %s ORDER BY id", (iid,))
        return [(d, c, D(s)) for d, c, s in cur.fetchall()]


def _casa(conn, data, cat, fid, suma, cui=_CLIENT):
    from core import casa_api
    r = casa_api.adauga(conn, _SCHEMA, {"data": data, "categorie": cat, "suma": suma, "document": "D-%s" % fid, "partener": "PARTENER",
                                        "cui": cui, "facturi": [{"factura_id": fid, "suma": suma}]})
    assert not r.get("eroare"), r
    return r["inregistrare_id"]


def _banca(conn, data, tip, fid, suma):
    from core import reconciliere_api
    with conn.cursor() as cur:
        cur.execute("INSERT INTO extras_linii (data, descriere, suma, tip) VALUES (%s,'plata factura',%s,%s) RETURNING id", (data, suma, tip))
        lid = cur.fetchone()[0]
    r = reconciliere_api.conteaza(conn, _SCHEMA, lid, alocari=[{"factura_id": fid, "suma": suma}])
    return r["inregistrari"][0]


@pytest.fixture(scope="module")
def prob():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, telefon, banca, iban, regim_fiscal, platitor_tva, "
                    "tip_decont, tva_la_incasare, declarant_nume, declarant_prenume, declarant_functie, cont_venit_implicit) "
                    "VALUES (1,'INCASARE SRL','14399840','Str Test 1','Sector 1','B','6920','0722000000','BCR','RO49AAAA1B31007593840000',"
                    "'real',true,'L',true,'Popescu','Ion','ADMINISTRATOR','704')")
                # intrarea în sistem pe 01.10.2026, ieșirea la sfârșitul lui noiembrie (CF art.282 alin.(3^1), (5))
                cur.execute("INSERT INTO tva_incasare_perioade (de_la, pana_la) VALUES ('2026-10-01', '2026-11-30')")
                ids = {k: _factura(cur, *a, **kw) for k, a, kw in (
                    ("F0", ("1", "2026-09-20"), {}), ("F1", ("2", "2026-10-10"), {}), ("F2", ("3", "2026-10-12"), {}),
                    ("P1", ("P1", "2026-10-08", "primita"), {"cui": _FURN}),
                    ("P2", ("P2", "2026-10-09", "primita", 500), {"cui": _FURN_TVAI, "furnizor_tvai": True}),
                    ("F3", ("4", "2026-11-15", "emisa", 2000), {}), ("F4", ("5", "2026-12-05"), {}))}
            note = {k: _conteaza(conn, ids[k])["inregistrare_id"] for k in ("F0", "F1", "F2", "P1", "P2", "F3", "F4")}
            note["F2_inc"] = _casa(conn, "2026-10-15", "incasare_client", ids["F2"], 605)
            with conn.cursor() as cur:
                ids["F2S"] = _factura(cur, "6", "2026-10-18", baza=-1000, storno_din=ids["F2"])
            note["F2S"] = _conteaza(conn, ids["F2S"])["inregistrare_id"]
            note["F1_casa"] = _casa(conn, "2026-10-20", "incasare_client", ids["F1"], 605)
            note["P1_casa"] = _casa(conn, "2026-10-22", "plata_furnizor", ids["P1"], 1210, cui=_FURN)
            note["F0_casa"] = _casa(conn, "2026-10-25", "incasare_client", ids["F0"], 1210)
            note["P2_banca"] = _banca(conn, "2026-10-28", "plata", ids["P2"], D("302.50"))
            note["F1_banca"] = _banca(conn, "2026-11-05", "incasare", ids["F1"], 605)
            note["F3_casa"] = _casa(conn, "2026-12-10", "incasare_client", ids["F3"], 2420)
            with conn.cursor() as cur:
                cur.execute("UPDATE inregistrari SET status = 'validata'")
            yield conn, ids, note
        finally:
            conn.rollback()


pytestmark_db = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytestmark_db
def test_emiterea_in_sistem_pune_tva_pe_4428_pe_data_facturii(prob):
    conn, ids, note = prob
    # [428] „facturile emise [...] înregistrează TVA pe 4428” — CF art.282 alin.(3); F1 emisă pe 10.10, în sistem
    assert _linii(conn, note["F1"]) == [("4111", "704", D("1000.00")), ("4111", "4428", D("210.00"))]
    # alin.(7) lit.a): F0, emisă pe 20.09, înainte de intrare -> regulile generale (4427), chiar încasată în sistem
    assert _linii(conn, note["F0"]) == [("4111", "704", D("1000.00")), ("4111", "4427", D("210.00"))]
    # F4 emisă după ieșire (05.12) -> 4427
    assert ("4111", "4427", D("210.00")) in _linii(conn, note["F4"])
    # F3 emisă pe 15.11, încă în sistem -> 4428
    assert ("4111", "4428", D("420.00")) in _linii(conn, note["F3"])


@pytestmark_db
def test_incasarea_prin_casa_si_banca_muta_partea_incasata(prob):
    conn, ids, note = prob
    # CF art.282 alin.(8): „fiecare încasare totală sau parțială se consideră că include și taxa aferentă” — 605 -> 105, în casă
    assert _linii(conn, note["F1_casa"]) == [("5311", "4111", D("605.00")), ("4428", "4427", D("105.00"))]
    # și prin bancă (aceeași funcție): restul de 105
    assert _linii(conn, note["F1_banca"]) == [("5121", "4111", D("605.00")), ("4428", "4427", D("105.00"))]
    # F0 (emisă înainte de intrare) încasată în sistem: nimic de mutat (alin.(7) lit.a)
    assert _linii(conn, note["F0_casa"]) == [("5311", "4111", D("1210.00"))]
    # alin.(7) lit.b): F3, emisă în sistem, încasată DUPĂ ieșire -> „se continuă aplicarea sistemului”
    assert _linii(conn, note["F3_casa"]) == [("5311", "4111", D("2420.00")), ("4428", "4427", D("420.00"))]


@pytestmark_db
def test_plata_furnizorului_muta_deducerea(prob):
    conn, ids, note = prob
    # CF art.297 alin.(3): firma în sistem -> deducerea amânată până la plată; P1 contată pe 4428, plata în casă o mută pe 4426
    assert ("4428", "401", D("210.00")) in _linii(conn, note["P1"])
    assert _linii(conn, note["P1_casa"]) == [("401", "5311", D("1210.00")), ("4426", "4428", D("210.00"))]
    # alin.(2): furnizorul în sistem; plata parțială 302,50 din 605 -> 52,50
    assert ("4428", "401", D("105.00")) in _linii(conn, note["P2"])
    assert _linii(conn, note["P2_banca"]) == [("401", "5121", D("302.50")), ("4426", "4428", D("52.50"))]


@pytestmark_db
def test_stornarea_anuleaza_intai_tva_neexigibil(prob):
    conn, ids, note = prob
    # F2: 605 încasat (105 exigibil), apoi stornată integral. CF art.282 alin.(10) lit.a) pct.1: „exigibilitatea taxei intervine la data
    # anulării operațiunii, pentru contravaloarea pentru care a intervenit exigibilitatea taxei. Pentru contravaloarea pentru care nu a
    # intervenit exigibilitatea taxei se operează anularea taxei neexigibile aferente”
    assert sorted(_linii(conn, note["F2S"])) == sorted([("4111", "704", D("-1000.00")), ("4111", "4428", D("-105.00")),
                                                       ("4111", "4427", D("-105.00"))])


def _atribut(xml, nume):
    """Valorile atributului `nume` pe elementele XML-ului (parsat), în ordine."""
    return [e.get(nume) for e in ET.fromstring(xml).iter() if e.get(nume) is not None]


def _note(xml_ubl):
    """Textele `cbc:Note` de pe factură (copii direcți ai rădăcinii UBL — BT-22), în ordine."""
    return [n.text for n in ET.fromstring(xml_ubl).findall("{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Note")]


def _d300(conn, luna):
    from core import d300 as _d300
    prof, fac = _d300.pull(conn, _SCHEMA, Perioada(2026, luna=luna))
    res = _d300.calcul_d300(prof, Perioada(2026, luna=luna), fac)
    return res, _d300.build_xml(res)


@pytestmark_db
def test_d300_urmeaza_exigibilitatea(prob):
    conn, ids, note = prob
    res, xml = _d300(conn, 10)
    # octombrie: F1 605 (105) + F2 605 (105) − stornarea F2, partea exigibilă (105) = 105 la rd.9 (21%); F0 e din septembrie
    assert (res.R.get("R9_1"), res.R.get("R9_2")) == (500, 105), res.R
    # deductibil: P1 plătit integral (210) + P2 plătit 302,50 (52,50) — CF art.297 alin.(2)-(3)
    assert (res.R.get("R22_1"), res.R.get("R22_2")) == (1250, 263), res.R
    # secțiunea „TVA neexigibilă” (OPANAF 174/2026, rd.A): la 31.10 rămân pe 4428 F1 105 (încasat jumătate) — F2 e stornată
    assert (res.neexigibil.get("tva_a"), res.neexigibil.get("valoare_a")) == (105, 500), res.neexigibil
    # rd.B: P2 neplătit 52,50 (baza 250)
    assert (res.neexigibil.get("tva_b"), res.neexigibil.get("valoare_b")) == (53, 250), res.neexigibil
    # ajung în XML: structura D300 v12, atributele valoare_a / tva_a / valoare_b / tva_b (validatorul D300, v10)
    a = ET.fromstring(xml).attrib
    assert (a.get("valoare_a"), a.get("tva_a"), a.get("valoare_b"), a.get("tva_b")) == ("500", "105", "250", "53"), a
    res11, xml11 = _d300(conn, 11)
    # noiembrie: restul F1 (605 prin bancă) -> 105; F3 emisă în sistem, neîncasată -> nimic exigibil, dar rămâne la rd.A (420)
    assert (res11.R.get("R9_1"), res11.R.get("R9_2")) == (500, 105), res11.R
    assert res11.neexigibil.get("tva_a") == 105 + 420 - 105, res11.neexigibil
    res12, xml12 = _d300(conn, 12)
    # decembrie (după ieșire): F4 pe regulile generale (1.000 / 210) + F3 încasată (2.000 / 420) — alin.(7) lit.b
    assert (res12.R.get("R9_1"), res12.R.get("R9_2")) == (3000, 630), res12.R
    duk = _duk("d300")
    if duk is not None:
        for luna, x in ((10, xml), (11, xml11), (12, xml12)):
            v = duk.valideaza(x, "d300", an=2026, luna=luna, timeout=180)
            assert v.get("stare") == "valid", (luna, v)


@pytestmark_db
def test_d394_sistem_tva_si_cotele_la_decontare(prob):
    conn, ids, note = prob
    from core import d394 as _d394
    xml, res = _d394.genereaza(conn, _SCHEMA, Perioada(2026, luna=10))
    # OPANAF 2194/2025: „e) sistem de TVA la încasare - se completează în cazul în care persoana impozabilă [...] a optat”
    assert _atribut(xml, "sistemTVA") == ["1"], xml[:400]
    inf = res.informatii
    # pct.5.1 „TVA colectată aferentă facturilor încasate în perioada de raportare” — F1 105 + F2 105
    assert inf["tvaCol21"] == 210, inf
    # pct.5.2 de la furnizori în sistemul normal (P1 210), pct.5.3 de la furnizori în sistem (P2 52,50 -> 53)
    assert (inf["tvaDed21"], inf["tvaDedAI21"]) == (210, 53), inf
    duk = _duk("d394")
    if duk is not None:
        v = duk.valideaza(xml, "d394", an=2026, luna=10, timeout=180)
        assert v.get("stare") == "valid", v
    # decembrie, după ieșire: sistemTVA = 0
    xml12, _r = _d394.genereaza(conn, _SCHEMA, Perioada(2026, luna=12))
    assert _atribut(xml12, "sistemTVA") == ["0"], xml12[:400]


@pytestmark_db
def test_mentiunea_pe_pdf_si_in_xml(prob):
    conn, ids, note = prob
    from core import facturi_api, factura_pdf, firma_profil_api, efactura_trimitere
    f1 = facturi_api.detalii_factura(conn, ids["F1"])
    # CF art.319 alin.(20) lit.p): „în cazul în care exigibilitatea TVA intervine la data încasării [...], mențiunea «TVA la încasare»”
    assert f1["tva_la_incasare"] is True
    assert facturi_api.detalii_factura(conn, ids["F0"])["tva_la_incasare"] is False   # emisă înainte de intrare
    assert facturi_api.detalii_factura(conn, ids["F4"])["tva_la_incasare"] is False   # emisă după ieșire
    import io
    import pypdf
    pdf = factura_pdf.genereaza_pdf(firma_profil_api.citeste_profil(conn), f1)
    text = "".join(p.extract_text() for p in pypdf.PdfReader(io.BytesIO(pdf)).pages)
    # mențiunea e un rând al facturii (exact „TVA la încasare”), nu un sub-șir al altui text
    assert [r.strip() for r in text.splitlines() if r.strip() == "TVA la încasare"] == ["TVA la încasare"], text
    xml, _f = efactura_trimitere.genereaza_din_factura(conn, _SCHEMA, ids["F1"])
    assert _note(xml) == ["TVA la încasare"], xml           # BT-22 (cbc:Note al facturii), ghidul MF v2.9 (RO_CIUS)
    xml0, _f0 = efactura_trimitere.genereaza_din_factura(conn, _SCHEMA, ids["F0"])
    assert _note(xml0) == [], xml0                          # emisă înainte de intrarea în sistem: fără mențiune
    # exporturile (SAGA FacturaTVAIncasare, WinMentor TVAINCASARE) poartă regimul FACTURII, nu bifa firmei de azi (care e „da” aici)
    from core import export_saga
    assert export_saga.date_factura(conn, _SCHEMA, ids["F1"])[1]["tva_la_incasare"] is True
    assert export_saga.date_factura(conn, _SCHEMA, ids["F0"])[1]["tva_la_incasare"] is False


@pytestmark_db
def test_iesirea_arata_facturile_ramase_pe_4428_fara_sa_mute(prob):
    conn, ids, note = prob
    from core import nomenclator_status_factura as _nsf
    with conn.cursor() as cur:
        lista = _tvi.neexigibile_la(cur, None, "2026-11-30", _nsf.clauza_sql("f"))
    pe = {r["factura_id"]: r for r in lista}
    # la ieșire (30.11) rămân pe 4428: F3 (420, neîncasată); F1 e încasată integral, F2 stornată, P1 plătită; P2 52,50 nededus
    assert set(pe) == {ids["F3"], ids["P2"]}, lista
    assert D(pe[ids["F3"]]["rest_neexigibil"]) == D("420.00")
    # CF art.282 alin.(7) lit.b): „se continuă aplicarea sistemului” — lista spune asta, nu mută nimic
    assert {k: r["ce_se_intampla"] for k, r in pe.items()} == {ids["F3"]: _tvi.CE_SE_INTAMPLA_EMISA, ids["P2"]: _tvi.CE_SE_INTAMPLA_PRIMITA}
    assert re.findall(r"CF art\.(\d+) alin\.\((\d+)\) lit\.(\w)", _tvi.CE_SE_INTAMPLA_EMISA) == [("282", "7", "b")]   # temeiul citat
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
                    "WHERE i.factura_id = %s AND l.cont_debit = '4428' AND l.cont_credit = '4427' AND i.data <= '2026-11-30'", (ids["F3"],))
        assert cur.fetchone()[0] == 0


@pytestmark_db
def test_achizitia_necorporala_a_firmei_in_sistem_merge_pe_4428(monkeypatch):
    """[428, generalizarea clasei „TVA-ul facturii primite pus direct pe 4426”] Achiziția necorporală (ruta ei scrie nota singură): la o
    firmă în sistem, CF art.297 alin.(3) — „Dreptul de deducere a TVA aferente achizițiilor efectuate de o persoană impozabilă care aplică
    sistemul TVA la încasare [...] este amânat până în momentul în care taxa [...] a fost plătită” -> 4428, nu 4426."""
    import main
    sch = "test_lot10_tvai_necorporala"
    _db.init_pool()
    try:
        with _db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % sch)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), sch))
                cur.execute("SET LOCAL search_path TO %s" % sch)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, platitor_tva, tip_decont) "
                            "VALUES (1,'TEST SRL','14399840','Str 1','Sector 1','B', true, 'L')")
                cur.execute("INSERT INTO tva_incasare_perioade (de_la) VALUES ('2026-01-01')")
            conn.commit()
        monkeypatch.setattr(main.auth_api, "schema_tenant", lambda conn, uid, tid: sch)
        r = main.achizitie_necorporala(1, {"data": "2026-06-10", "denumire": "Licenta X", "valoare": 5000, "tip": "software", "cota": 21,
                                           "furnizor_cui": _FURN, "furnizor_nume": "SOFT SRL", "numar": "F-SOFT-1"}, {"uid": 1})
        with _db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT cont_debit, cont_credit, suma FROM %s.inregistrari_linii WHERE inregistrare_id = %%s ORDER BY id" % sch,
                        (r["inregistrare_id"],))
            assert [(d, c, D(s)) for d, c, s in cur.fetchall()][1] == ("4428", "404", D("1050.00"))
    finally:
        with _db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % sch)
            conn.commit()
