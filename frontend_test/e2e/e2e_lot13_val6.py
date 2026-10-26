# -*- coding: utf-8 -*-
"""Lotul 13 (comanda Costin 13.1), pachetul `val6` — deficiența 683 (a lui Code): Casă › „Avans spre decontare” nu punea salariatul pe
rândul notei, deci 542 nu se urmărea pe persoană (pe drumul Operațiunilor era reparat, 670 a).

Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ (`firma_noua` + `pregateste_firma`). DATE DE PORNIRE scrise pe
drumul aplicației, declarate: salariatul (Salarizare, ruta lui) și numerarul din casă (ridicare din bancă, ruta Casei) — proba e avansul.

Mutațiile care fac testul ROȘU: `mut_lot13_val6.json`."""
import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import AZI, _api, _card, _ok, pregateste_firma
from e2e_lot13_ops import _linii, _note_noi, _salariat, _ultima


@pytest.fixture()
def firma_val6(patron):
    for f in firma_noua():
        pregateste_firma(patron, f, regim_fiscal="profit")
        yield f


def test_def_683_avansul_spre_decontare_se_da_unui_salariat(patron, firma_val6):
    """683. Pașii: salariatul Ionescu Vasile (în Salarizare) și 1.000 lei în casă (ridicare din bancă) -> „Casă” -> „+ Dispoziție nouă”: Tip
    „Avans spre decontare”, 300 lei -> câmpurile Partener și CUI dispar, apare „Salariatul” (listă cu căutare, nimic ales) -> „Adaugă” fără
    salariat: lângă câmp „Alege o valoare”, nimic scris -> salariatul ales din listă -> „Adaugă”: „Dispoziția a fost salvată”; nota are
    542 = 5311 300, rândul 542 pe salariat (nume și CNP), iar registrul îl numește pe salariat la partener. Înainte: partenerul se scria de
    mână, rândul 542 rămânea fără persoană.
    MUTAȚIA: `casa_api.adauga` scrie rândul 542 fără salariat -> rândul n-are partener -> ROȘU."""
    f = firma_val6
    s = f["schema"]
    sid, cnp = _salariat(patron, f)
    # date-de-pornire: numerarul din care se dă avansul (ruta Casei, ridicare din bancă)
    _ok(_api(patron, "POST", "/tenants/%d/casa/operatiuni" % f["tenant_id"],
             {"data": AZI.replace(day=1).isoformat(), "categorie": "ridicare_banca", "suma": 1000, "document": "DI-E2E683"}), "numerarul din casă")
    patron.firma(f["nume"])
    pg = patron.pg
    _card(patron, "casa", "#c-toggle")
    pg.click("#c-toggle")
    pg.fill("#c-data", AZI.isoformat())
    pg.select_option("#c-cat", "avans_decontare")
    pg.fill("#c-suma", "300")
    # partenerul scris de mână nu mai există la acest tip: salariatul se alege din evidență
    pg.wait_for_selector("#c-zona-salariat", state="visible", timeout=10000)
    assert not pg.is_visible("#c-part") and not pg.is_visible("#c-cui")
    pg.wait_for_function("(v) => [...document.querySelector('#c-salariat').options].some((o) => o.value === v)", arg=str(sid), timeout=20000)
    assert pg.input_value("#c-salariat") == ""   # nimic precompletat
    ultima = _ultima(f)
    pg.click("#c-adauga")
    pg.wait_for_selector('.msg-eroare[data-camp="c-salariat"]', timeout=15000)
    assert "Alege" in pg.inner_text('.msg-eroare[data-camp="c-salariat"]')
    patron.captura("fara_salariat")
    assert _note_noi(f, ultima) == []
    pg.select_option("#c-salariat", str(sid))
    pg.click("#c-adauga")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('Dispoziția a fost salvată')", timeout=30000)
    patron.captura("avans_salvat")
    (nid,) = _note_noi(f, ultima)
    assert _linii(f, nid) == [("542", "5311", "300.00", "Ionescu Vasile")]
    assert sql('SELECT partener_cui FROM "%s".inregistrari_linii WHERE inregistrare_id = %%s' % s, (nid,)) == [(cnp,)]
    assert sql('SELECT partener, cui FROM "%s".casa_operatiuni WHERE inregistrare_id = %%s' % s, (nid,)) == [("Ionescu Vasile", cnp)]
    assert "Ionescu Vasile" in patron.fereastra()   # registrul îl numește pe salariat la partener
