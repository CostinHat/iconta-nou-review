# -*- coding: utf-8 -*-
"""281 — Mijloace fixe / închidere (comanda Costin 16.10.2026, „Lotul 6, comanda 1” pct.9, verbatim în DECIZII): „lunile de amortizare
restante după preluare (01–08/2026) se generează cu o singură acțiune, cu câte o notă pe lună, nu lună cu lună. La închiderea lunii,
amortizarea lunilor anterioare neînregistrată oprește închiderea sau cere confirmare explicită, pentru că schimbă profitul (D100/D101).”
PIVOT față de 215 (semnal): acum blocaj CONFIRMABIL.

Temei: OMFP 1802/2014 — amortizarea e cheltuială a perioadei (contul 6811 = 281x, lunar), deci lipsa ei schimbă rezultatul (profitul pe
care se calculează D100 / D101). Aici nu se schimbă calculul ratei (`d406_active.amortizare_luna`), ci drumul: câte acțiuni și ce oprește
închiderea. Perioade sintetice 2099, schemă efemeră din template, ștearsă la ieșire.
"""
import datetime
import io
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov

SCH = "efemer_281"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def firma(monkeypatch):
    """MF: 12.000 lei, 60 de luni, PIF 15.01.2099 -> 200 lei pe lună din 02.2099. Validată numai amortizarea lui 05.2099."""
    from core import auth_api, common
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'F SRL', 'RO14399840')")
            cur.execute("INSERT INTO mijloace_fixe (cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual, dnf_luni, data_pif, "
                        "metoda, activ) VALUES ('MF-281', 'Utilaj', '2131', '2813', 12000, 0, 60, '2099-01-15', 'liniar', true)")
            cur.execute("INSERT INTO inregistrari (data, numar, descriere, status, sursa, document_ref) VALUES ('2099-05-31', "
                        "'AMORT-2099-05', 'Amortizare 05/2099', 'validata', 'amortizare', 'T') RETURNING id")
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '6811', '2813', 200)",
                        (cur.fetchone()[0],))
        c.commit()
    monkeypatch.setattr(common, "azi_ro", lambda: datetime.date(2099, 12, 31))
    monkeypatch.setattr(auth_api, "schema_tenant", lambda conn, uid, tid: SCH)
    yield SCH
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def test_281_amortizarea_lunilor_anterioare_opreste_inchiderea_dar_se_poate_confirma(firma):
    """MUTAȚIE: `blocaje.append(_ctl("AMORTIZARE_ANTERIOARA_NEINREGISTRATA"` -> `semnale.append(` (cum era la 215) -> pică."""
    from core import uc_comun, uc_tenants, erori
    with _db.get_conn() as c:
        ctl = uc_comun.controale_inchidere(c, SCH, 2099, 5)
    assert [(b["cod"], b.get("confirmabil"), b.get("luni")) for b in ctl["blocaje"]] == [
        ("AMORTIZARE_ANTERIOARA_NEINREGISTRATA", True, ["2099-02", "2099-03", "2099-04"])], ctl["blocaje"]
    ctx = {"uid": 1, "firm": 1}
    with pytest.raises(erori.DateInvalide):
        uc_tenants.perioada_blocheaza(1, 2099, 5, ctx)
    r = uc_tenants.perioada_blocheaza(1, 2099, 5, ctx, confirma_amortizare=True)
    assert r["blocat"] == "05/2099" and len(r["confirmate"]) == 1
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute('SELECT actiune, motiv FROM "%s".perioade_inchideri' % SCH)
            (act, motiv), = cur.fetchall()
    assert act == "inchisa" and motiv.startswith("închisă cu confirmare explicită: amortizarea lunilor anterioare"), motiv


def test_281_confirmarea_nu_trece_peste_blocajele_neconfirmabile(firma):
    """Luna 06 n-are nici ea amortizarea: blocajul lunii însăși nu se confirmă (W2), doar cel al lunilor anterioare."""
    from core import uc_tenants, erori
    with pytest.raises(erori.DateInvalide) as e:
        uc_tenants.perioada_blocheaza(1, 2099, 6, {"uid": 1, "firm": 1}, confirma_amortizare=True)
    assert [b["cod"] for b in e.value.detaliu["blocaje"]] == ["AMORTIZARE_NEINREGISTRATA"]


def test_281_restanta_se_genereaza_dintr_o_actiune_o_nota_pe_luna(firma):
    """MUTAȚIE: `luni.add((an, luna))` scos din `tenant_amortizare_restanta` -> luna 06 nu se generează -> pică."""
    from core import uc_tenants
    r = uc_tenants.tenant_amortizare_restanta(1, 2099, 6, {"uid": 1, "firm": 1})
    assert [(x["an"], x["luna"], x["ok"]) for x in r["luni"]] == [(2099, 2, True), (2099, 3, True), (2099, 4, True), (2099, 6, True)]
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute('SELECT i.numar, i.status, sum(l.suma) FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l ON l.inregistrare_id '
                        "= i.id WHERE i.sursa = 'amortizare' GROUP BY i.id ORDER BY i.data" % (SCH, SCH))
            note = cur.fetchall()
    assert note == [("AMORT-2099-02", "ciorna", Decimal("200.00")), ("AMORT-2099-03", "ciorna", Decimal("200.00")),
                    ("AMORT-2099-04", "ciorna", Decimal("200.00")), ("AMORT-2099-05", "validata", Decimal("200.00")),
                    ("AMORT-2099-06", "ciorna", Decimal("200.00"))], note
    # a doua apăsare nu dublează: ciornele cu aceleași sume rămân (tenant_amortizare: „deja generată”)
    assert uc_tenants.tenant_amortizare_restanta(1, 2099, 6, {"uid": 1, "firm": 1})["generate"] == 4
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT count(*) FROM \"%s\".inregistrari WHERE sursa = 'amortizare'" % SCH)
            assert cur.fetchone()[0] == 5
