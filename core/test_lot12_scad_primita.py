# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.1 (verbatim în DECIZII „Comanda 12.1”), pachetul `scad` — factura primită.

  477 (grav, cerută explicit, pct.8) „Facturi primite: lipsește introducerea manuală a facturilor primite.” Factura de pe hârtie / PDF:
      furnizorul (CUI cu cifra de control, statutul la ANAF la data facturii), seria / numărul, data, scadența, liniile cu cotele în vigoare
      (registrul de parametri fiscali, `common.cote_tva_in_vigoare`), moneda și cursul BNR, contul — validată pe ACELAȘI drum ca factura din
      XML (`uc_factura_primita.valideaza`).
  Decizia Costin „cursul vechi la validare (a)”: factura primită în valută validată cu un curs mai vechi decât cel comunicat înaintea datei
      ei primește anunțul, ca la emitere (`curs_bnr.cursul_zilei_lipsa`, act „validare”).
  C104 Importul XML pierdea unitatea de măsură (BT-130 `unitCode`): linia și articolul nou din stoc intrau în „buc”.

Temei (verbatim, anaf_surse/): CF art.290 alin.(2) „cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a
României [...] valabil la data la care intervine exigibilitatea taxei pentru operațiunea în cauză”; HG 1/2016 pct.35 alin.(1) „prin ultimul
curs de schimb comunicat de Banca Națională a României se înțelege cursul de schimb comunicat de respectiva bancă în ziua anterioară și care
este valabil pentru operațiunile care se vor desfășura în ziua următoare.” Structură (EN 16931, nu normă): BT-130 „Invoiced quantity unit of
measure code”, codurile UN/ECE Rec 20 (H87 bucată, MTR metru, KGM kilogram, C62 „one”).
Schemă efemeră din template, în tranzacție anulată (fixtura lui 417); zilele sunt SINTETICE (2099). CUI 14399840: cifra de control verificată."""
import datetime
from decimal import Decimal as D

import pytest

from core import curs_bnr, erori, uc_factura_primita as ufp
from core.test_417_storno_trimitere import _SCHEMA, _db_ok, conn  # noqa: F401 — fixtura

DB = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
_STATUT = {"platitor_tva": True, "tva_la_incasare": False}


class _FaraCommit:
    """Conexiunea fixturii fără `commit` (actul de validare comite; testul rămâne în tranzacția anulată)."""
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, k):
        return getattr(self._c, k)


def _corp(**k):
    c = {"tert_tara": "RO", "tert_cui": "14399840", "tert_nume": "DANTE INTERNATIONAL SA", "serie": "DNT", "numar": "1077",
         "data_emitere": "2099-04-01", "data_scadenta": "2099-05-01", "moneda": "RON", "cont": "628",
         "linii": [{"descriere": "Servicii curierat", "cantitate": "2", "um": "buc", "pret_unitar": "50", "cota_tva": "21"}],
         "destinatii": ["taxabil"], "conturi": [""]}
    c.update(k)
    return c


# ── pur ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_477_formularul_refuza_toate_campurile_deodata():
    """Toate lipsurile deodată, fiecare lângă câmpul ei (DS cap.6): furnizor, CUI greșit (cifra de control), număr, dată, cont, linia."""
    with pytest.raises(erori.DateInvalide) as e:
        ufp.factura_din_formular({"tert_tara": "RO", "tert_cui": "14399841", "moneda": "RON",
                                  "linii": [{"descriere": "", "cantitate": "0", "um": "", "pret_unitar": "x", "cota_tva": None}]})
    campuri = {c["camp"] for c in e.value.args[0]["erori_campuri"]}
    assert campuri == {"pm-furnizor", "pm-cui", "pm-numar", "pm-data", "pr-cont", "pm-l1-descriere", "pm-l1-cantitate", "pm-l1-um",
                       "pm-l1-pret", "pm-l1-cota"}, campuri


def test_def_477_cota_din_registru_la_data_facturii():
    """Cota care nu era în vigoare la data facturii se refuză lângă ea (registrul de parametri fiscali: 19% nu mai e în 2099)."""
    with pytest.raises(erori.DateInvalide) as e:
        ufp.factura_din_formular(_corp(linii=[{"descriere": "x", "cantitate": "1", "um": "buc", "pret_unitar": "10", "cota_tva": "19"}]))
    assert [c["camp"] for c in e.value.args[0]["erori_campuri"]] == ["pm-l1-cota"], e.value.args[0]


def test_def_477_factura_de_mana_are_forma_facturii_din_xml():
    """Același drum: dict-ul facturii de mână are cheile lui `efactura_import.parseaza_xml` (pe care le citește `_factura_importata`), iar
    TVA-ul e regula unică (BR-CO-17): 2 × 50 = 100, TVA 21, total 121."""
    import io
    from core import efactura_import
    xml = io.open("/home/costin/ghid_incoming/lot12_fisiere_proba/F1_efactura_DANTE_DNT-RT-1020.xml", encoding="utf-8").read()
    chei_xml = set(efactura_import.parseaza_xml(xml, "401002001"))
    f = ufp.factura_din_formular(_corp())
    lipsa = {k for k in chei_xml if k not in f and not k.startswith(("furnizor_", "cumparator_"))}
    assert not lipsa, lipsa
    assert (f["total"], f["tva"], f["directie"], f["serie"], f["xml"], f["manuala"]) == (D("121.00"), D("21.00"), "primita", "DNT", None, True)


def test_cursul_vechi_la_validare_spune_validarea():
    """Decizia „cursul vechi la validare (a)”: anunțul spune că factura VALIDATĂ păstrează cursul (nu „emisă”); la emitere, neschimbat."""
    from core import curs_bnr as cb
    z = datetime.date
    v = cb.cursul_zilei_lipsa(z(2026, 10, 22), z(2026, 10, 19), azi=z(2026, 10, 22), act="validare")
    assert v["mesaj"].endswith("din 19.10.2026, iar factura validată acum îl păstrează (se fixează la validare)."), v["mesaj"]
    e = cb.cursul_zilei_lipsa(z(2026, 10, 22), z(2026, 10, 19), azi=z(2026, 10, 22))
    assert e["mesaj"].endswith("iar factura emisă acum îl păstrează (se fixează la emitere)."), e["mesaj"]


def test_def_c104_codul_unitatii_devine_unitatea_aplicatiei():
    """C104. BT-130 -> unitatea iConta, din harta e-Factura (`efactura_send._UM`, sursa unică): H87 buc, MTR m, KGM kg, C62 buc; un cod
    necunoscut rămâne codul (nu „buc” ghicit)."""
    from core import efactura_send as es
    assert [es.um_din_unece(c) for c in ("H87", "MTR", "kgm", "C62", "XBX", "", None)] == ["buc", "m", "kg", "buc", "XBX", None, None]


def test_def_c104_importul_citeste_unitatea_liniei():
    """C104. Fișierul de probă real (F1, DANTE DNT-RT-1020): 20 H87 / 50 MTR / 12,5 KGM / 1 C62 -> buc, m, kg, buc pe linii."""
    import io
    from core import efactura_import
    xml = io.open("/home/costin/ghid_incoming/lot12_fisiere_proba/F1_efactura_DANTE_DNT-RT-1020.xml", encoding="utf-8").read()
    f = efactura_import.parseaza_xml(xml, "401002001")
    assert [(l["descriere"], l.get("um")) for l in f["linii"]] == [("Marfa A", "buc"), ("Cablu electric cupru 3x1,5 mm", "m"),
                                                                   ("Detergent pudra vrac", "kg"), ("Transport marfa", "buc")], f["linii"]


# ── pe bază ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _valideaza(conn, corp, statut=_STATUT):
    return ufp.valideaza(_FaraCommit(conn), _SCHEMA, ufp.factura_din_formular(corp), dict(corp), statut)


@DB
def test_def_477_factura_de_mana_intra_cu_nota_ca_cea_din_xml(conn):
    """477. Factura DNT nr. 1077 (2 × 50 lei, 21%) pe 628: intră primită, cu seria separat, tipul furnizorului aflat (ANAF), nota 628 = 401
    100,00 + 4426 = 401 21,00 — aceeași contare ca factura din XML. MUTAȚIE: `valideaza` fără `contabilizeaza` -> pică."""
    r = _valideaza(conn, _corp())
    assert r["stare"] == "validata" and r["contare"].get("stare") not in ("refuzata", "neaplicabil"), r
    with conn.cursor() as cur:
        cur.execute("SELECT directie, serie, numar, total, tva, tert_platitor_tva, xml IS NULL FROM facturi WHERE id = %s", (r["factura_id"],))
        assert cur.fetchone() == ("primita", "DNT", "1077", D("121.00"), D("21.00"), True, True)
        cur.execute("SELECT l.cont_debit, l.cont_credit, l.suma FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                    "WHERE i.factura_id = %s ORDER BY l.cont_debit", (r["factura_id"],))
        assert cur.fetchall() == [("4426", "401", D("21.00")), ("628", "401", D("100.00"))]


@DB
def test_def_477_aceeasi_factura_a_doua_oara_se_refuza(conn):
    """Aceeași factură (furnizor, serie, număr, dată) introdusă a doua oară: refuz numit, nimic scris a doua oară."""
    _valideaza(conn, _corp())
    with pytest.raises(erori.Conflict) as e:
        _valideaza(conn, _corp())
    # refuzul dublurii (`DUBLURA`), cu factura, furnizorul și data ei — nu alt conflict
    assert str(e.value) == ufp.DUBLURA % ("DNT nr. 1077", "DANTE INTERNATIONAL SA", "01.04.2099"), e.value
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM facturi WHERE numar = '1077'")
        assert cur.fetchone()[0] == 1


@DB
def test_def_477_tipul_furnizorului_necunoscut_se_cere(conn):
    """Furnizorul din altă țară (ANAF nu-l are): fără alegere, refuzul cere tipul lui lângă câmp (`pr-platitor`); cu ea, intră."""
    corp = _corp(tert_tara="DE", tert_cui="DE811569869")
    with pytest.raises(erori.DateInvalide) as e:
        _valideaza(conn, corp, statut={"platitor_tva": None, "tva_la_incasare": None})
    assert e.value.args[0]["cod"] == "TERT_PLATITOR_DE_COMPLETAT" and e.value.args[0]["erori_campuri"][0]["camp"] == "pr-platitor"
    r = _valideaza(conn, dict(corp, tert_platitor_tva=True), statut={"platitor_tva": None, "tva_la_incasare": None})
    with conn.cursor() as cur:
        cur.execute("SELECT tert_tara, tert_platitor_tva FROM facturi WHERE id = %s", (r["factura_id"],))
        assert cur.fetchone() == ("DE", True)


@DB
def test_def_477_valuta_cu_cursul_zilei_lipsa_e_anuntata(conn, monkeypatch):
    """Factura de 100 EUR din 01.04.2099; cursul comunicat pe 31.03 lipsește, se folosește cel din 27.03 (5,0000): factura primește cursul
    și sumele în lei (CF art.290 alin.(2)), iar răspunsul poartă anunțul „factura validată acum îl păstrează”. MUTAȚIE: `_anunt_curs` ->
    None -> pică."""
    from core import facturi_api
    monkeypatch.setattr(facturi_api, "curs_automat", lambda c, m, z: (D("5.0000"), datetime.date(2099, 3, 27), "bnr"))
    corp = _corp(moneda="EUR", numar="1078", linii=[{"descriere": "Licență", "cantitate": "1", "um": "buc", "pret_unitar": "100",
                                                      "cota_tva": "21"}])
    r = _valideaza(conn, corp)
    with conn.cursor() as cur:
        cur.execute("SELECT curs_bnr, data_curs, total_lei, tva_lei FROM facturi WHERE id = %s", (r["factura_id"],))
        assert cur.fetchone() == (D("5.000000"), datetime.date(2099, 3, 27), D("605.00"), D("105.00"))
    a = r["curs_zilei_lipsa"]
    assert a and a["asteptat"] == "2099-03-31" and a["folosit"] == "2099-03-27", a
    # anunțul e cel al VALIDĂRII (`act="validare"`: „factura validată acum îl păstrează (se fixează la validare)”), nu al emiterii
    assert curs_bnr.ACT_FIXARE["validare"] == ("factura validată acum", "se fixează la validare")
    assert a == curs_bnr.cursul_zilei_lipsa(datetime.date(2099, 4, 1), datetime.date(2099, 3, 27), act="validare"), a
    assert a != curs_bnr.cursul_zilei_lipsa(datetime.date(2099, 4, 1), datetime.date(2099, 3, 27), act="emitere"), a


@DB
def test_def_c104_marfa_in_kg_intra_in_stoc_in_kg(conn):
    """C104. Linia de 12,5 kg pe 371 intră în stoc cu articolul nou în „kg” (nu „buc”); linia facturii poartă „kg”."""
    corp = _corp(numar="1079", cont="371", linii=[{"descriere": "Detergent pudra vrac", "cantitate": "12.5", "um": "kg",
                                                   "pret_unitar": "8.40", "cota_tva": "21"}])
    r = _valideaza(conn, corp)
    with conn.cursor() as cur:
        cur.execute("SELECT um FROM factura_linii WHERE factura_id = %s", (r["factura_id"],))
        assert cur.fetchall() == [("kg",)]
        cur.execute("SELECT a.denumire, a.um, m.cantitate FROM miscari_stoc m JOIN articole a ON a.id = m.articol_id WHERE m.factura_id = %s",
                    (r["factura_id"],))
        assert cur.fetchall() == [("Detergent pudra vrac", "kg", D("12.5000"))], r


@DB
def test_def_c104_migrarea_pune_unitatea_din_xml_pe_facturile_vechi(conn):
    """C104, datele existente: factura importată înainte de reparație (liniile pe „buc”) primește unitatea din XML-ul păstrat (m, kg);
    o linie a cărei unitate n-o spune XML-ul rămâne; articolul din stoc rămas în „buc” se NUMEȘTE, nu se schimbă. MUTAȚIE: `aplica` fără
    `UPDATE … SET um` -> pică."""
    import io
    from core import migrare_um_linii_xml as mig
    xml = io.open("/home/costin/ghid_incoming/lot12_fisiere_proba/F1_efactura_DANTE_DNT-RT-1020.xml", encoding="utf-8").read()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva, tert_nume, tert_cui, status, xml, tip) VALUES "
                    "('DNT-RT-1020', '2099-04-01', 'primita', 1694, 294, 'DANTE INTERNATIONAL SA', '14399840', 'importata', %s, 'factura') "
                    "RETURNING id", (xml,))
        fid = cur.fetchone()[0]
        for den in ("Marfa A", "Cablu electric cupru 3x1,5 mm", "Detergent pudra vrac", "Transport marfa"):
            cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva) VALUES (%s, %s, 1, 1, 21)", (fid, den))
        cur.execute("INSERT INTO articole (denumire, um, cont_stoc, cont_cheltuiala) VALUES ('Cablu electric cupru 3x1,5 mm', 'buc', '371', "
                    "'607') RETURNING id")
        aid = cur.fetchone()[0]
        cur.execute("INSERT INTO miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document, factura_id) VALUES "
                    "(%s, '2099-04-01', 'intrare', 50, 4.2, 210, 'DNT-RT-1020', %s)", (aid, fid))
    r = mig.aplica(conn, _SCHEMA)
    assert r["linii"] == 2 and r["sarite"] == [], r
    assert r["articole"] == [(aid, "Cablu electric cupru 3x1,5 mm", "buc", "m", "DNT-RT-1020")], r
    with conn.cursor() as cur:
        cur.execute("SELECT um FROM factura_linii WHERE factura_id = %s ORDER BY id", (fid,))
        assert [x[0] for x in cur.fetchall()] == ["buc", "m", "kg", "buc"]
    assert mig.aplica(conn, _SCHEMA)["linii"] == 0   # idempotentă
