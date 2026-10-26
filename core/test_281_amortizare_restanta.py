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
        # [lotul 13, 522] nota veche (fără activ pe rând) trece prin migrarea care o leagă de activ, ca pe firmele existente
        from core import migrare_mf_note
        migrare_mf_note.aplica(c, SCH)
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
    # a doua apăsare nu dublează: ciornele cu aceleași sume rămân (tenant_amortizare: „deja generată”); [312] și nu le mai numără „generate”
    r2 = uc_tenants.tenant_amortizare_restanta(1, 2099, 6, {"uid": 1, "firm": 1})
    assert (r2["generate"], r2["deja_generate"]) == (0, 4), r2
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT count(*) FROM \"%s\".inregistrari WHERE sursa = 'amortizare'" % SCH)
            assert cur.fetchone()[0] == 5


def test_312_dupa_generare_inchiderea_spune_de_validat_si_a_doua_apasare_nu_mai_numara(firma):
    """312 (comanda Costin 17.10.2026 7.2, verbatim în DECIZII): „după «Generează amortizarea restantă» motivul rămâne «neînregistrată»,
    butonul rămâne activ, iar a doua apăsare spune iar «8 note generate» [...] Trebuie «8 note generate, de validat».”
    MUTAȚII: `de_validat=generata` -> `de_validat=False` (butonul rămâne) -> pică; `not x.get("deja_generata")` scos -> a doua apăsare
    numără iar -> pică."""
    from core import uc_comun, uc_tenants
    r1 = uc_tenants.tenant_amortizare_restanta(1, 2099, 6, {"uid": 1, "firm": 1})
    assert (r1["generate"], r1["deja_generate"]) == (4, 0), r1
    with _db.get_conn() as c:
        ctl = uc_comun.controale_inchidere(c, SCH, 2099, 6)
    am = [b for b in ctl["blocaje"] if b["cod"].startswith("AMORTIZARE")]
    assert [(b["cod"], b["de_validat"]) for b in am] == [
        ("AMORTIZARE_NEINREGISTRATA", True), ("AMORTIZARE_ANTERIOARA_NEINREGISTRATA", True)], ctl["blocaje"]
    ctl = {"blocaje": am}
    assert ctl["blocaje"][0]["mesaj"].startswith("amortizarea lunii e generată pe contul 2813 (200,00 lei), de validat"), ctl["blocaje"]
    assert (ctl["blocaje"][1]["luni"], ctl["blocaje"][1]["mesaj"]) == (
        ["2099-02", "2099-03", "2099-04"],
        "amortizarea lunilor anterioare e generată pe contul 2813: 3 luni (02–04/2099), de validat în Registrul jurnal — sau închide luna "
        "confirmând explicit: amortizarea lipsă schimbă profitul (D100/D101)"), ctl["blocaje"]
    r2 = uc_tenants.tenant_amortizare_restanta(1, 2099, 6, {"uid": 1, "firm": 1})
    assert (r2["generate"], r2["deja_generate"]) == (0, 4), r2


def test_311_generarea_amortizarii_cere_poate_pregati_validarea_ramane_la_poate_valida():
    """311: „generarea amortizării (lunară și restantă) la «Poate pregăti», validarea rămâne la «Poate valida»”. Garda rutelor citită din
    aplicația vie. MUTAȚIE: `cere_drept(_drepturi.PREGATI)` -> `VALIDA` pe `/amortizare/restanta` -> pică."""
    import main
    from core import drepturi
    niv = {}
    for r in main.app.routes:
        for dep in getattr(getattr(r, "dependant", None), "dependencies", []):
            n = getattr(dep.call, "nivel_drept", None)
            if n:
                niv[(sorted(r.methods)[0], r.path)] = n
    assert niv.get(("POST", "/tenants/{tenant_id}/amortizare")) == drepturi.PREGATI, niv.get(("POST", "/tenants/{tenant_id}/amortizare"))
    assert niv.get(("POST", "/tenants/{tenant_id}/amortizare/restanta")) == drepturi.PREGATI
    assert niv.get(("POST", "/tenants/{tenant_id}/jurnal/{nota_id}/valideaza")) == drepturi.VALIDA


def test_c48_conturile_de_avans_ale_aplicatiei_sunt_in_planul_firmelor_noi_si_se_adauga_celor_existente():
    """C48: `avansuri.CONT_AVANS` (4091, 4092, 4093, 4094) și contul propus la 401 debitor (312) există în planul șablonului; migrarea le
    adaugă firmelor existente fără să atingă un cont pe care firma îl are deja. MUTAȚIE: rândul 4092 scos din `tenant_template.sql` -> pică."""
    import re
    from core import avansuri, migrare_plan_avansuri as mpa
    sablon = io.open("tenant_template.sql", encoding="utf-8").read()
    seed = sablon[sablon.index("INSERT INTO TENANT_PLACEHOLDER.plan_conturi"):]
    seed = seed[:seed.index(";")]
    in_plan = set(re.findall(r"\('(\d+)'", seed))
    assert set(avansuri.CONT_AVANS.values()) <= in_plan, set(avansuri.CONT_AVANS.values()) - in_plan
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(sablon, SCH))
            cur.execute('DELETE FROM "%s".plan_conturi WHERE simbol IN (\'4092\', \'4094\')' % SCH)
            cur.execute('UPDATE "%s".plan_conturi SET denumire = \'Avansuri imobilizări (SAGA)\' WHERE simbol = \'4093\'' % SCH)
            assert mpa.aplica(c, SCH) == 2 and mpa.aplica(c, SCH) == 0
            cur.execute('SELECT simbol, denumire FROM "%s".plan_conturi WHERE simbol LIKE \'409_\' ORDER BY simbol' % SCH)
            assert cur.fetchall()[1:] == [("4092", "Furnizori - debitori pentru prestări de servicii"), ("4093", "Avansuri imobilizări (SAGA)"),
                                          ("4094", "Avansuri acordate pentru imobilizări necorporale")]
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()
