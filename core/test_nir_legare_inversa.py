# -*- coding: utf-8 -*-
"""GARDA deciziei Costin 08.10.2026, pct.2 — D2 în ordinea inversă (verbatim în DECIZII 08.10.2026):

  „la contarea facturii se propune legarea cu NIR-ul nelegat de la același furnizor (preselecție permisă — dedusă din date,
  vizibilă, modificabilă). Dacă contabilul nu leagă, confirmă explicit «altă livrare»; nu se blochează. Se elimină astfel dubla
  încărcare a lui 371.”

CE FACE IMPOSIBIL:
  * ca o factură primită de marfă (371, global-valoric) să se conteze tăcut peste un NIR „fără factură” al aceluiași furnizor —
    fără alegere, contarea se refuză structurat (`NIR_DE_LEGAT`) și NU scrie nimic, pe ambele căi (ruta și validarea din SPV);
  * ca legarea să lase 371 / 401 / 4426 încărcate de două ori — după legare, soldurile sunt EXACT cele ale ordinii directe
    (NIR legat la creare, decizia 07.10 pct.2);
  * ca un NIR cu alt cost, de la alt furnizor, din alt exercițiu sau respins să fie propus / legat.
[08.10 §6, deciziile Costin] Forma nouă (408 / 4428.01): legarea pe ambele metode, între exerciții cât timp 408 e deschis, cu
diferența de preț în perioada facturii; forma veche (401): stornarea în roșu, numai în exercițiul curent.

Schemă efemeră din `tenant_template.sql`, ștearsă la ieșire; date în 2099. Nimic în tabele partajate.
"""
import io
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_nir_legare_0810"
CUI_A, CUI_B = "14399840", "40372003"   # CUI-uri reale, cifra de control verificată (CLAUDE.md)
_L = {"cantitate": 10, "pret_achizitie": 55, "cota_tva": 21, "denumire": "Marfa A", "pret_vanzare": 80}


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def conn():
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, metoda_stoc) "
                        "VALUES (1, 'NIR LEGARE SRL', 'RO14399840', true, 'global_valoric')")
        c.commit()
    with _db.get_conn(SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _nir(conn, numar="1", cui=CUI_A, data="2099-10-07", pa=55, **extra):
    from core import stocuri_api as s
    r = s.adauga_nir(conn, SCH, {"numar": numar, "data": data, "furnizor": "FURNIZOR", "cui": cui,
                                 "linii": [dict(_L, pret_achizitie=pa)], **extra})
    assert "eroare" not in r, r
    return r


def _factura(conn, numar="FP1", cui=CUI_A, pret=55):
    from core import facturi_api as fa
    r = fa.creeaza_factura(conn, numar, "2099-10-07", "primita",
                           [{"descriere": "Marfa A", "cantitate": 10, "pret_unitar": pret, "cota_tva": 21}],
                           tert_nume="FURNIZOR", tert_cui="RO" + cui)
    return r["factura_id"] if isinstance(r, dict) else r


def _conteaza(conn, fid, nir_legat=None):
    from core import contare_facturi as cf
    with cf.cursor_dict(conn) as cur:
        return cf.contabilizeaza(cur, SCH, fid, automat=False, nir_legat=nir_legat)


def _solduri(conn, ids):
    """{cont: (debit, credit)} pe notele date — rulajele, cu liniile în roșu cu minus."""
    out = {}
    with conn.cursor() as cur:
        cur.execute("SELECT cont_debit, cont_credit, suma FROM inregistrari_linii WHERE inregistrare_id = ANY(%s)", (list(ids),))
        for d, c, s in cur.fetchall():
            out.setdefault(d, [Decimal(0), Decimal(0)])[0] += s
            out.setdefault(c, [Decimal(0), Decimal(0)])[1] += s
    return {k: (str(v[0]), str(v[1])) for k, v in out.items() if v != [0, 0]}


def _nr_note(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM inregistrari")
        return cur.fetchone()[0]


def _ids_nir(conn, nir_id):
    from core import stocuri_api as s
    with conn.cursor() as cur:
        cur.execute("SELECT inregistrari_ids, factura_id FROM nir WHERE id = %s", (nir_id,))
        r = cur.fetchone()
    return s.note_nir({"inregistrari_ids": r[0]}), r[1]


def test_fara_alegere_contarea_se_refuza_structurat_si_nu_scrie_nimic(conn):
    """„se propune legarea cu NIR-ul nelegat de la același furnizor (preselecție permisă — dedusă din date)”. MUTAȚIE: ramura
    `nir_legat in (None, "")` scoasă din `contabilizeaza` -> factura se contează peste NIR -> pică."""
    from core import contare_facturi as cf, nir_legare as nl
    n = _nir(conn)
    fid = _factura(conn)
    inainte = _nr_note(conn)
    with pytest.raises(cf.RefuzContare) as e:
        _conteaza(conn, fid)
    assert e.value.cod == nl.COD_DE_ALES
    d = e.value.detalii
    assert (d["propus"], d["camp"], d["alta_livrare"]) == (n["id"], "nir-legat", "alta_livrare")   # dedusă: același cost
    assert [(c["id"], c["cost"], c["acelasi_cost"]) for c in d["candidati"]] == [(n["id"], "550.00", True)]
    assert _nr_note(conn) == inainte                       # nimic scris


def _sold_net(r):
    """{cont: sold net (debit − credit)} fără conturile închise."""
    out = {k: Decimal(v[0]) - Decimal(v[1]) for k, v in r.items()}
    return {k: str(v) for k, v in out.items() if v}


def _forma_veche(conn, nir):
    """NIR-ul în FORMA VECHE (scris înainte de 08.10 §6: 371 = 401, 4426 = 401) — ca NIR 2 / NIR 3 de pe F1."""
    with conn.cursor() as cur:
        cur.execute("UPDATE inregistrari_linii SET cont_credit = '401' WHERE inregistrare_id = ANY(%s) AND cont_credit = '408'",
                    (nir["inregistrari"],))
        cur.execute("UPDATE inregistrari_linii SET cont_debit = '4426' WHERE inregistrare_id = ANY(%s) AND cont_debit = '4428.01'",
                    (nir["inregistrari"],))


def test_legarea_aduce_soldurile_ordinii_directe(conn):
    """„Se elimină astfel dubla încărcare a lui 371.” Ordinea inversă cu legare = ordinea directă (NIR legat la creare), cont cu
    cont, pe SOLDURI. [08.10 §6 pct.1–3] Forma nouă: NIR-ul pe 408 / 4428.01, factura închide 408 = 401 și trece TVA-ul 4428 -> 4426
    (CF art.299 alin.(1) lit.a: deducerea cere factura) — nicio stornare; 371 debit o singură dată (K). MUTAȚIE: `note_factura_legata`
    necheamată -> 371 D 1350 -> pică."""
    fb = _factura(conn, numar="FB1", cui=CUI_B)
    from core import stocuri_api as s
    rb = s.adauga_nir(conn, SCH, {"numar": "9", "data": "2099-10-07", "factura_id": fb, "linii": [dict(_L)]})
    directa = _solduri(conn, rb["inregistrari"] + [_conteaza(conn, fb)["inregistrare_id"]])
    n = _nir(conn)
    fa = _factura(conn)
    r = _conteaza(conn, fa, nir_legat=n["id"])
    ids, legat = _ids_nir(conn, n["id"])
    inversa = _solduri(conn, ids + [r["inregistrare_id"]])
    assert _sold_net(inversa) == _sold_net(directa)
    assert inversa["371"] == ("800.00", "0")                                              # rulajul debitor citit de K: o dată
    assert (inversa["408"], inversa["4428.01"]) == (("665.50", "665.50"), ("115.50", "115.50"))   # închise
    assert legat == fa and r["nir_legat"]["stornare_id"] is None and r["nir_legat"]["forma_noua"] is True
    assert r["linii"] == [{"debit": "408", "credit": "401", "suma": "665.50"}, {"debit": "4426", "credit": "4428.01", "suma": "115.50"}]
    assert "nir_legat" not in _conteaza(conn, _factura(conn, numar="FP2"))   # a doua factură nu mai vede NIR-ul (e legat)


def test_forma_veche_se_leaga_prin_stornare_in_rosu(conn):
    """NIR-urile scrise înainte de 08.10 §6 (371 = 401) se leagă tot prin stornarea în ROȘU a costului lor — OMFP 1802/2014 pct.69:
    „Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu
    semnul minus a operațiunii inițiale (stornare în roșu)…”. MUTAȚIE: `leaga` necheamat -> 371 D 1350 -> pică."""
    n = _nir(conn)
    _forma_veche(conn, n)
    fa = _factura(conn)
    r = _conteaza(conn, fa, nir_legat=n["id"])
    ids, _l = _ids_nir(conn, n["id"])
    inversa = _solduri(conn, ids + [r["inregistrare_id"]])
    assert inversa["371"] == ("800.00", "0") and inversa["401"] == ("0", "665.50") and inversa["4426"] == ("115.50", "0")
    with conn.cursor() as cur:
        cur.execute("SELECT cont_debit, cont_credit, suma::text FROM inregistrari_linii WHERE inregistrare_id = %s ORDER BY id",
                    (r["nir_legat"]["stornare_id"],))
        assert cur.fetchall() == [("371", "401", "-550.00"), ("4426", "401", "-115.50")]   # roșu, nu negru


def test_alta_livrare_confirmata_conteaza_normal_si_o_consemneaza(conn):
    """„Dacă contabilul nu leagă, confirmă explicit «altă livrare»; nu se blochează.” MUTAȚIE: mențiunea scoasă din descriere
    -> pică."""
    from core import nir_legare as nl
    n = _nir(conn)
    fid = _factura(conn)
    r = _conteaza(conn, fid, nir_legat=nl.ALTA_LIVRARE)
    assert r["stare"] == "contata" and r.get("alta_livrare") is True
    with conn.cursor() as cur:
        cur.execute("SELECT descriere FROM inregistrari WHERE id = %s", (r["inregistrare_id"],))
        assert cur.fetchone()[0].count(nl.MENTIUNE_ALTA_LIVRARE) == 1
    assert _ids_nir(conn, n["id"])[1] is None              # NIR-ul rămâne nelegat


def test_candidatii_forma_noua_intre_exercitii_forma_veche_numai_in_exercitiu(conn):
    """[08.10 §6 pct.2] „NIR din exercițiul trecut: se propune la legare și între exerciții, cât timp 408 e deschis. Exercițiul închis
    nu se modifică” — forma veche se stornează, deci numai în exercițiul curent (OMFP 1802/2014 pct.69: „aferente exercițiului
    financiar curent”). Alt furnizor nu e candidat. Costul diferit: propus nu, dar legabil (diferența intră în perioada facturii).
    MUTAȚIE: condiția de formă scoasă din `candidati` -> NIR-ul vechi din 2098 e propus -> pică."""
    from core import contare_facturi as cf, nir_legare as nl
    n60 = _nir(conn, numar="1", pa=60)                    # alt cost, forma nouă
    _nir(conn, numar="2", cui=CUI_B)                       # alt furnizor
    _nir(conn, numar="3", data="2098-12-30")               # exercițiul trecut, forma nouă: 408 deschis
    _forma_veche(conn, _nir(conn, numar="4", data="2098-12-29"))   # exercițiul trecut, forma veche
    fid = _factura(conn)
    with pytest.raises(cf.RefuzContare) as e:
        _conteaza(conn, fid)
    assert sorted(c["numar"] for c in e.value.detalii["candidati"]) == ["1", "3"] and e.value.detalii["propus"] == 3
    with pytest.raises(cf.RefuzContare) as e:
        _conteaza(conn, fid, nir_legat=999999)
    assert e.value.cod == nl.COD_NELEGABIL
    r = _conteaza(conn, fid, nir_legat=n60["id"])         # 600 pe NIR, 550 pe factură: −50 pe adaos (global-valoric)
    assert {"debit": "378", "credit": "401", "suma": "-50.00"} in r["linii"]


def test_forma_veche_cu_alt_cost_se_refuza(conn):
    """Forma veche: costul NIR-ului = netul facturii, la ban (stornarea trebuie să fie exact operațiunea inițială)."""
    from core import contare_facturi as cf, nir_legare as nl
    n = _nir(conn, pa=60)
    _forma_veche(conn, n)
    with pytest.raises(cf.RefuzContare) as e:
        _conteaza(conn, _factura(conn), nir_legat=n["id"])
    assert e.value.cod == nl.COD_COST


def test_nir_respins_nu_e_candidat(conn, monkeypatch):
    """Un NIR respins la validare se reface (R1); NIR-ul refăcut e cel care se leagă. MUTAȚIE: excluderea respinselor scoasă
    -> NIR-ul respins e propus -> pică."""
    from core import coada_api as cq, nir_legare as nl
    n = _nir(conn)
    fid = _factura(conn)
    monkeypatch.setattr(nl, "_tenant", lambda cur, schema: 1)
    monkeypatch.setattr(cq, "stari_note", lambda c, t, ids: {i: {"stare_coada": "respinsa"} for i in ids})
    assert "nir_legat" not in _conteaza(conn, fid) and n


def test_pe_alt_cont_nu_se_cere_alegerea_la_cost_se_cere(conn):
    """Numai factura care încarcă 371 (`facturi.ACHIZITIE["marfa"]`). [08.10 §6 pct.1] La cantitativ-valoric: „aceeași alegere ca la
    celelalte metode — la contarea facturii se leagă de NIR-ul deschis (408 = 401), fără a doua intrare în stoc. Fără refuz.”
    MUTAȚIE: `METODE` înapoi la global-valoric -> la cost factura se contează tăcut peste NIR -> pică."""
    from core import contare_facturi as cf, nir_legare as nl
    _nir(conn)
    with cf.cursor_dict(conn) as cur:
        r = cf.contabilizeaza(cur, SCH, _factura(conn), automat=False, cont_cheltuiala="628")
    assert r["stare"] == "contata"
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET metoda_stoc = 'cantitativ_valoric'")
    with pytest.raises(cf.RefuzContare) as e:
        _conteaza(conn, _factura(conn, numar="FP2"))
    assert e.value.cod == nl.COD_DE_ALES


_UBL = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
  <cbc:ID>FSPV-1</cbc:ID>
  <cbc:IssueDate>2099-10-07</cbc:IssueDate>
  <cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
  <cac:AccountingSupplierParty><cac:Party>
    <cac:PartyLegalEntity><cbc:RegistrationName>FURNIZOR</cbc:RegistrationName></cac:PartyLegalEntity>
    <cac:PartyTaxScheme><cbc:CompanyID>RO14399840</cbc:CompanyID></cac:PartyTaxScheme>
  </cac:Party></cac:AccountingSupplierParty>
  <cac:AccountingCustomerParty><cac:Party>
    <cac:PartyLegalEntity><cbc:RegistrationName>NIR LEGARE SRL</cbc:RegistrationName></cac:PartyLegalEntity>
    <cac:PartyTaxScheme><cbc:CompanyID>RO40372003</cbc:CompanyID></cac:PartyTaxScheme>
  </cac:Party></cac:AccountingCustomerParty>
  <cac:TaxTotal><cbc:TaxAmount>115.50</cbc:TaxAmount></cac:TaxTotal>
  <cac:LegalMonetaryTotal><cbc:TaxInclusiveAmount>665.50</cbc:TaxInclusiveAmount></cac:LegalMonetaryTotal>
  <cac:InvoiceLine>
    <cbc:InvoicedQuantity>10</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount>550</cbc:LineExtensionAmount>
    <cac:Price><cbc:PriceAmount>55</cbc:PriceAmount></cac:Price>
    <cac:Item><cbc:Name>Marfa A</cbc:Name>
      <cac:ClassifiedTaxCategory><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
  </cac:InvoiceLine>
</Invoice>"""


def test_validarea_din_spv_cere_alegerea_inainte_si_nu_lasa_factura_validata(conn, monkeypatch):
    """Pe calea SPV contarea e automată: fără alegere, TOT actul se anulează (factura nu rămâne validată fără notă) și răspunsul
    poartă candidații. Cu alegerea, factura se validează și NIR-ul se leagă. MUTAȚIE: `conn.rollback()` scos din ramura
    `NIR_DE_LEGAT` din `factura_primita_valideaza` -> factura rămâne validată -> pică."""
    import main
    from core import erori
    n = _nir(conn)
    conn.commit()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO efactura_primite (id_mesaj_anaf, cif_emitent, cif_beneficiar, xml_brut, xml_sha256, status) "
                    "VALUES ('MSG-NIR-0810', 'RO14399840', 'RO40372003', %s, 'sha-nir-0810', 'descarcata') RETURNING id", (_UBL,))
        pid = cur.fetchone()[0]
    conn.commit()
    monkeypatch.setattr(main.auth_api, "schema_tenant", lambda c, uid, tid: SCH)
    with pytest.raises(erori.DateInvalide) as e:
        main._uc_tenants.factura_primita_valideaza(1, pid, {"cont": "371"}, {"uid": 1})
    assert (e.value.detaliu["cod"], e.value.detaliu["propus"]) == ("NIR_DE_LEGAT", n["id"])
    with conn.cursor() as cur:
        cur.execute("SELECT status, factura_id FROM efactura_primite WHERE id = %s", (pid,))
        assert cur.fetchone() == ("descarcata", None)
        cur.execute("SELECT count(*) FROM facturi")
        assert cur.fetchone()[0] == 0
    r = main._uc_tenants.factura_primita_valideaza(1, pid, {"cont": "371", "nir_id": n["id"]}, {"uid": 1})
    assert r["stare"] == "validata" and r["contare"]["nir_legat"]["nir_id"] == n["id"]
