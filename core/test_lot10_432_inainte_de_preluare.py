# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 432, comanda Costin 10.1 pct.12, verbatim în DECIZII „Comanda 10.1”] „la F6 (preluată din 10/2026), lista
„Datorate de firmă” include D112, D300, D394, D406 pe 09/2026 fără mențiunea „înainte de preluare” (regula de la 157). Rămân vizibile,
pentru că termenul cade după preluare, dar marcate separat.”

Cauza: lista „Datorate de firmă” (Declarații, pasul 1) și ecranul Termene vin din `firma_rezumat._termene_una_firma` ->
`termene_api.termene_firma`, care nu citeau luna preluării; Control fiscal o citea (`control_fiscal_api.separa_inainte_de_preluare`).
Acum un singur predicat, `luna_preluare.inainte`, folosit de amândouă.

Schemă efemeră; `public.declaratii_depuse` numai cu un tenant_id SINTETIC (991432), curățat la ieșire.
MUTAȚII: marcajul scos din `_termene_una_firma` -> `test_datoratele_dinaintea_preluarii_raman_si_sunt_marcate` pică;
`(an, luna or 12) < preluare` înlocuit cu `<=` în `luna_preluare.inainte` -> `test_predicatul_unic` pică.
"""
import datetime
import io
import os

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_lot10_432"
TID = 991432
AZI = datetime.date(2026, 10, 20)
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:  # noqa: BLE001
        return False


def test_predicatul_unic():
    from core import luna_preluare as lp
    # regula de la 157 (decizia U2, 08.10): perioada dinaintea lunii preluării; trimestrul / anul pe luna de ancoră
    assert lp.inainte(2026, 9, (2026, 10)) is True
    assert lp.inainte(2026, 10, (2026, 10)) is False
    assert lp.inainte(2026, 9, (2026, 9)) is False          # T3 (ancora 09) cuprinde luna preluării 09 -> nu e „înainte”
    assert lp.inainte(2025, None, (2026, 1)) is True        # anuala 2025 (ancora 12/2025) la preluarea din 01/2026
    assert lp.inainte(2026, 9, None) is False               # luna preluării necunoscută -> nimic „înainte”


@pytest.fixture()
def firma():
    sablon = io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(sablon, SCH))
            cur.execute("INSERT INTO %s.firma_profil (id, nume, cui, platitor_tva, tip_decont, regim_fiscal, tip_firma, "
                        "platitor_tva_anaf_inceput, luna_preluare) VALUES (1, 'MIGRARE TEST SRL', '14399840', true, 'L', 'profit', "
                        "'srl', '2020-01-01', '2026-10-01')" % SCH)
            cur.execute("DELETE FROM public.declaratii_depuse WHERE tenant_id = %s", (TID,))
        c.commit()
    try:
        yield
    finally:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute("DELETE FROM public.declaratii_depuse WHERE tenant_id = %s", (TID,))
            c.commit()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_datoratele_dinaintea_preluarii_raman_si_sunt_marcate(firma, monkeypatch):
    from core import auth_api, firma_rezumat as fr, termene_api
    monkeypatch.setattr(auth_api, "schema_tenant", lambda c, uid, tid: SCH if tid == TID else None)
    ev, neev = fr._termene_una_firma({"id": TID, "nume": "MIGRARE TEST SRL"}, {"uid": 1}, AZI)
    assert neev is None and ev, neev
    termene = {(t["tip"], t["an"], t["luna"]): t for t in ev["termene"]}
    print("432 termene:", sorted((k, t["inainte_de_preluare"]) for k, t in termene.items()))
    # „Rămân vizibile, pentru că termenul cade după preluare, dar marcate separat.”
    assert ("d300", 2026, 9) in termene, termene.keys()
    assert termene[("d300", 2026, 9)]["inainte_de_preluare"] is True
    # octombrie (luna preluării) nu e „înainte”; dacă e în fereastra de 60 de zile, rămâne nemarcată
    assert all(not t["inainte_de_preluare"] for k, t in termene.items() if (k[1], k[2] or 12) >= (2026, 10))
    # Termene (portofoliul) poartă marcajul pe firmă
    port = termene_api.portofoliu([ev], AZI, [])
    marcate = [f for g in port["grupuri"] for it in g["items"] for f in it["firme"] if f["inainte_de_preluare"]]
    assert marcate and all(f["perioada"] for f in marcate)
