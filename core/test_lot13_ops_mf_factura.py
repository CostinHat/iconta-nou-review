# -*- coding: utf-8 -*-
"""[lotul 13, deficiența 601, decizia Costin (a)] Mijlocul fix cumpărat pe factură: linia facturii primite pe un cont de imobilizare
amortizabilă cere datele fișei (codul din catalog și durata în plaja lui, data punerii în funcțiune, metoda) și aduce activul în
registru, legat de nota facturii — activ numai după validarea notei (`core/mf_din_factura.py`, cârligul din `uc_factura_primita.valideaza`).

TEMEI: OMFP 1802/2014 pct.226 alin.(1) („O imobilizare corporală recunoscută ca activ trebuie evaluată inițial la costul său […]”) și
pct.8 pct.6 („costul de achiziție al bunurilor cuprinde prețul de cumpărare […]”); HG 2139/2004 anexa cap.I pct.4 (durata în plaja
catalogului)."""
import pytest

from core import erori, mf_din_factura
from core.test_lot13_ops_schema import CTX, SCH, schema_ops


def _campuri(e):
    d = e.value.detaliu
    return {x["camp"]: x["mesaj"] for x in d["erori_campuri"]}


def test_contul_de_imobilizare():
    assert [c for c in ("2131", "2133", "214", "205", "208", "212", "211", "231", "2813", "604", "371") if mf_din_factura.e_imobilizare(c)] == [
        "2131", "2133", "214", "205", "208", "212"]


def test_linia_de_imobilizare_cere_toate_datele_fisei_deodata_langa_ea():
    """Factura de mână, linia 1 pe 2131 fără date, linia 2 pe cheltuială: toate cele patru câmpuri ale liniei 1, nimic pe linia 2."""
    f = {"manuala": True, "linii": [{"descriere": "Laptop"}, {"descriere": "Hârtie"}]}
    with pytest.raises(erori.DateInvalide) as e:
        mf_din_factura.cere(f, {"conturi": ["2131", ""], "imobilizari": [{}, None]}, "604")
    assert set(_campuri(e)) == {"pm-mf1-cod_catalog", "pm-mf1-dnf_luni", "pm-mf1-data_pif", "pm-mf1-metoda"}


def test_durata_in_plaja_catalogului_si_factura_din_xml_numara_de_la_zero():
    """HG 2139/2004 anexa cap.I pct.4: 2.2.9 (calculatoare) are plaja 2–4 ani; 12 luni se refuză lângă durata liniei (factura din XML:
    `pr-mf0-…`)."""
    f = {"linii": [{"descriere": "Laptop"}]}
    with pytest.raises(erori.DateInvalide) as e:
        mf_din_factura.cere(f, {"imobilizari": [{"cod_catalog": "2.2.9", "dnf_luni": 12, "data_pif": "2026-10-15", "metoda": "liniara"}]}, "2131")
    c = _campuri(e)
    assert list(c) == ["pr-mf0-dnf_luni"] and "între 24 și 48 de luni" in c["pr-mf0-dnf_luni"], c
    r = mf_din_factura.cere(f, {"imobilizari": [{"cod_catalog": "2.2.9", "dnf_luni": 36, "data_pif": "2026-10-15", "metoda": "liniara"}]}, "2131")
    assert [(i, x["cont_imobilizare"], x["dnf_luni"], x["denumire"]) for i, x in r] == [(0, "2131", 36, "Laptop")]


def test_factura_de_mana_cu_linia_de_imobilizare_aduce_activul_la_validarea_notei(monkeypatch):
    """601. Factura primită de mână: „Laptop Dell” 1 × 6.000 lei, cota 21, pe 2131 (fișa: 2.2.9, 36 de luni, PIF 15.10.2026, liniar) și
    „Hârtie” 1 × 100 pe 604 -> nota 2131 = 401 6.000, 604 = 401 100, 4426 = 401; activul MF-001 „Laptop Dell” 6.000 lei e în registru,
    „intră la validarea notei” -> nota validată -> activ.
    MUTAȚIE: activul nelegat de notă (`mf_note.leaga` scos din `inscrie`) -> rămâne inactiv după validare -> pică."""
    from core import uc_factura_primita as ufp
    with schema_ops(monkeypatch) as (c, cur, uc):
        corp = {"tert_nume": "DANTE INTERNATIONAL SA", "tert_cui": "14399840", "tert_tara": "RO", "numar": "MF-601", "data_emitere": "2026-10-15",
                "moneda": "RON", "cont": "604",
                "linii": [{"descriere": "Laptop Dell", "cantitate": 1, "um": "buc", "pret_unitar": 6000, "cota_tva": 21},
                          {"descriere": "Hârtie", "cantitate": 1, "um": "buc", "pret_unitar": 100, "cota_tva": 21}],
                "conturi": ["2131", ""], "destinatii": ["taxabil", "taxabil"],
                "imobilizari": [{"cod_catalog": "2.2.9", "dnf_luni": "36", "data_pif": "2026-10-15", "metoda": "liniara"}, None]}
        f = ufp.factura_din_formular(corp)
        with uc.db.get_conn() as conn:
            r = ufp.valideaza(conn, SCH, f, corp, {"platitor_tva": True, "tva_la_incasare": False})
        nid = r["contare"]["inregistrare_id"]
        assert [(m["cod"], m["denumire"], m["valoare"]) for m in r["mijloace_fixe"]] == [("MF-001", "Laptop Dell", "6000.00")]
        cur.execute("SELECT cont_debit, cont_credit, suma::text FROM inregistrari_linii WHERE inregistrare_id = %s ORDER BY cont_debit", (nid,))
        linii = cur.fetchall()
        assert ("2131", "401", "6000.00") in linii and ("604", "401", "100.00") in linii, linii
        mid = r["mijloace_fixe"][0]["id"]
        cur.execute("SELECT cont_imobilizare, cont_amortizare, valoare::text, dnf_luni, data_pif::text, metoda, cod_catalog, activ "
                    "FROM mijloace_fixe WHERE id = %s", (mid,))
        assert cur.fetchone() == ("2131", "2813", "6000.00", 36, "2026-10-15", "liniara", "2.2.9", False)
        reg = {m["cod"]: m for m in uc.tenant_mijloace_fixe(1, CTX)["mijloace"]}
        assert reg["MF-001"]["stare"] == "intrare_in_asteptare", reg["MF-001"]
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (nid,))
        cur.execute("SELECT activ FROM mijloace_fixe WHERE id = %s", (mid,))
        assert cur.fetchone()[0] is True
