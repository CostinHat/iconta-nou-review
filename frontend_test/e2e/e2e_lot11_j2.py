# -*- coding: utf-8 -*-
"""Lotul 11 (comanda Costin 11.1), subagentul J2 — 8c pe ecranele Mijloace fixe (casare, reevaluare).

8c (decizia 10.3: „8c: reparația centrală, cu DS cap. 6 actualizat.”; clasa din comanda 10.2 pct.8c: „După generare, titlul «Notă
generată» e roșu, conturile notei nu se văd, iar «Generează notă» rămâne activ.”). Pe Mijloace fixe confirmarea casării / reevaluării
se scria în zona de mesaj de DINAINTEA redesenării registrului: redesenarea o scotea din pagină, deci contabilul nu vedea nimic. Acum
trece prin `api.dupaGenerare`, în zona ecranului refăcut: caseta verde, cu rândurile notei citite din Registrul jurnal.

Pașii contabilului pe aplicația din index, pe baza de TEST. Date de PORNIRE scrise direct (declarate): mijlocul fix din registru, pe
scrierea din care îl adaugă aplicația (`e2e_bloc_e._mf`, `repo_mijloace_fixe.adauga_cu_reevaluare`). PIF-ul e în luna curentă: amortizarea
începe din luna următoare PIF (`d406_active.amortizat_la_data`, „Amortizarea incepe luna urmatoare PIF”), deci valoarea netă = valoarea
de intrare, iar casarea / reevaluarea nu cer amortizarea lunilor trecute înregistrată.
"""
from decimal import Decimal

from conftest import sql
from e2e_bloc_e import AZI, _mf, _mijloace, firma_gv  # noqa: F401 — firma global-valorică a rulării


def _lei(x):
    """Suma în formatul ecranului (`api.bani`): 1.234,56."""
    s = "{:,.2f}".format(Decimal(str(x)))
    return s.replace(",", " ").replace(".", ",").replace(" ", ".")


def _randuri_notei(f, nid):
    """Rândurile notei din bază, cum le scrie confirmarea („debit = credit · sumă lei”)."""
    return ["%s = %s · %s lei" % (d, c, _lei(s)) for d, c, s in
            sql('SELECT cont_debit, cont_credit, suma FROM "%s".inregistrari_linii WHERE inregistrare_id = %%s ORDER BY id' % f["schema"],
                (nid,))]


def _ultima_nota(f):
    return sql('SELECT coalesce(max(id), 0) FROM "%s".inregistrari' % f["schema"])[0][0]


def _randul(pg, cod):
    rand = pg.locator(".fereastra:last-of-type table.fd-tabel tbody tr", has_text="Utilaj de probă %s" % cod).first
    rand.locator("details summary", has_text="Acțiuni").click()
    return rand


def _confirmarea(pg):
    pg.wait_for_selector(".fereastra:last-of-type #mf-mesaj .caseta-ok .cok-linii", timeout=30000)
    return [" ".join(x.split()) for x in pg.inner_text(".fereastra:last-of-type #mf-mesaj .cok-linii").split("\n") if x.strip()]


def test_def_8c_casarea_mijlocului_fix_confirmare_verde_cu_conturile_notei(patron, firma_gv):
    """8c. Pașii: Mijloace fixe -> „Utilaj de probă MFJ2C” (6.000 lei, PIF în luna curentă) -> Acțiuni -> „Casează” -> „Casează” (confirmare).
    Registrul se redesenează (mijlocul devine casat) și, deasupra lui, caseta verde „Casare înregistrată (ciornă)” cu rândurile notei de
    casare exact ca în Registrul jurnal. Înainte: mesajul se scria în zona scoasă din pagină de redesenare — nu se vedea nimic."""
    f = firma_gv
    pg = patron.pg
    _mf(f, "MFJ2C", "6000", 60, AZI.replace(day=1).isoformat())
    inainte = _ultima_nota(f)
    _mijloace(patron, f)
    _randul(pg, "MFJ2C").locator("[data-caseaza]").click()
    pg.click("#ca-ok")
    linii = _confirmarea(pg)
    patron.captura("casare")
    nid = _ultima_nota(f)
    assert nid > inainte, "casarea n-a scris nota"
    assert linii == _randuri_notei(f, nid), (linii, _randuri_notei(f, nid))
    titlu = pg.inner_text(".fereastra:last-of-type #mf-mesaj .cok-titlu")
    assert titlu.startswith("Casare înregistrată (") and "msg-" not in (pg.get_attribute(".fereastra:last-of-type #mf-mesaj", "class") or ""), titlu


def test_def_8c_reevaluarea_mijlocului_fix_confirmare_verde_si_fara_diferenta_fara_nota(patron, firma_gv):
    """8c. Pașii: Mijloace fixe -> „Utilaj de probă MFJ2R” (6.000 lei, PIF în luna curentă) -> Acțiuni -> valoarea justă 6.000 (= valoarea
    netă) -> „Reevaluează”: „Nicio diferență de reevaluat … Nu s-a generat nicio notă.” (nu „Reevaluare înregistrată”, nicio notă în
    bază) -> valoarea justă 7.000 -> „Reevaluează”: caseta verde „Reevaluare înregistrată (ciornă)”, cu rândurile notei ca în Registrul
    jurnal (OMFP 1802/2014 pct.111-116: reevaluarea la valoarea justă)."""
    f = firma_gv
    pg = patron.pg
    mid = _mf(f, "MFJ2R", "6000", 60, AZI.replace(day=1).isoformat())
    inainte = _ultima_nota(f)
    _mijloace(patron, f)
    rand = _randul(pg, "MFJ2R")
    pg.fill("#mf-reeval-%d" % mid, "6000")
    rand.locator("[data-reeval]").click()
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #mf-mesaj') || {innerText: ''}).innerText"
                         ".includes('Nicio diferență de reevaluat')", timeout=30000)
    patron.captura("fara_diferenta")
    assert pg.locator(".fereastra:last-of-type #mf-mesaj .caseta-ok").count() == 0
    assert _ultima_nota(f) == inainte, "fără diferență nu se scrie nicio notă"
    rand = _randul(pg, "MFJ2R")
    pg.fill("#mf-reeval-%d" % mid, "7000")
    rand.locator("[data-reeval]").click()
    linii = _confirmarea(pg)
    patron.captura("reevaluare")
    nid = _ultima_nota(f)
    assert nid > inainte, "reevaluarea n-a scris nota"
    assert linii == _randuri_notei(f, nid), (linii, _randuri_notei(f, nid))
    assert pg.inner_text(".fereastra:last-of-type #mf-mesaj .cok-titlu").startswith("Reevaluare înregistrată (")
