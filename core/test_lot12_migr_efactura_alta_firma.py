# -*- coding: utf-8 -*-
"""[lotul 12, clasa deficienței 599 (comanda Costin 12.1: „compară firma din fișier cu firma aleasă și cere confirmare când diferă, la
toate importurile”), găsită la generalizare] Importul manual al unei facturi e-Factura (XML UBL) primea și o factură între ALTE două firme:
`parseaza_xml` o socotea „primită” (furnizorul nu e firma), deci intra ca factură de la furnizor, cu TVA-ul ei de dedus. Docstringul lui
`spv_receive.importa_xml_manual` spunea „Beneficiarul din XML trebuie să fie firma”, dar nimic nu verifica.

Acum `efactura_import.alta_firma` refuză numit factura în care firma nu e nici furnizor, nici cumpărător; o cheamă importul manual
(`uc_tenants.import_efactura`). Decizia: refuz, nu confirmare — o factură între alte două firme nu poate fi în evidența firmei.

TEMEI: N/A — regulă de produs (comanda 12.1). Structura (EN 16931, nu normă): BT-27/BT-31 vânzătorul, BT-44/BT-48 cumpărătorul. CUI-urile
din fixtură au cifra de control verificată: 14399840 (DANTE INTERNATIONAL SA), 9010105 (ORANGE ROMANIA SA), 4221306."""
import contextlib

from core import efactura_import as _ef
from core.test_418_import_efactura import _XML


def test_def_599_factura_intre_alte_doua_firme_e_refuzata_numit():
    """ROȘU înainte: `alta_firma` nu exista, iar factura DANTE -> ORANGE intra la firma cu CUI 4221306 ca „primită”. MUTAȚIA: `return None`
    la începutul lui `alta_firma` -> pică."""
    f = _ef.parseaza_xml(_XML.encode(), "4221306")
    assert (f["directie"], f["cumparator_cui"], f["furnizor_cui"]) == ("primita", "RO9010105", "RO14399840")
    assert _ef.alta_firma(f, "4221306") == (
        "Factura DNT-TEST-1019 nu e a firmei: e emisă de DANTE INTERNATIONAL SA (CUI 14399840) către F1 SRL (CUI 9010105), iar firma aleasă "
        "are CUI 4221306. Încarcă numai facturile emise sau primite de firmă.")


def test_599_factura_primita_sau_emisa_de_firma_intra():
    assert _ef.alta_firma(_ef.parseaza_xml(_XML.encode(), "RO9010105"), "RO9010105") is None      # firma e cumpărătorul
    assert _ef.alta_firma(_ef.parseaza_xml(_XML.encode(), "14399840"), "14399840") is None        # firma e furnizorul (emisă)
    fara = _ef.parseaza_xml(_XML.replace("RO9010105", "").encode(), "4221306")
    assert _ef.alta_firma(fara, "4221306") is None      # cumpărătorul fără cod fiscal în XML: nu se poate confrunta, nu se refuză


class _Cur:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _Conn:
    comise = 0

    def cursor(self, *a, **k):
        return _Cur()

    def commit(self):
        _Conn.comise += 1


def test_599_importul_manual_nu_scrie_factura_altei_firme(monkeypatch):
    """`POST /tenants/{id}/import-efactura`: factura între alte două firme -> eroarea numită, 0 importate, nicio scriere. MUTAȚIA:
    chemarea lui `alta_firma` scoasă din `uc_tenants.import_efactura` -> `_factura_importata` ar fi chemată (aici: pică)."""
    import json
    from core import uc_tenants

    @contextlib.contextmanager
    def _gc(schema=None):
        yield _Conn()

    def _nu_scrie(*a, **k):
        raise AssertionError("factura altei firme a ajuns la scriere")

    monkeypatch.setattr(uc_tenants.db, "get_conn", _gc)
    monkeypatch.setattr(uc_tenants.auth_api, "schema_tenant", lambda conn, uid, tid: "ztest_efactura_alta_firma")
    monkeypatch.setattr(uc_tenants.repo_firma_profil, "cui_firma_3", lambda cur, schema: ("4221306",))
    monkeypatch.setattr(uc_tenants, "_factura_importata", _nu_scrie)
    r = uc_tenants.import_efactura(1, [(_XML.encode(), "dante_orange.xml")], {"uid": 1})
    d = json.loads(r.body)
    assert d["importate"] == 0 and d["duplicate"] == 0
    assert d["erori"] == ["dante_orange.xml: Factura DNT-TEST-1019 nu e a firmei: e emisă de DANTE INTERNATIONAL SA (CUI 14399840) către "
                          "F1 SRL (CUI 9010105), iar firma aleasă are CUI 4221306. Încarcă numai facturile emise sau primite de firmă."]
