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
    """[lotul 13, clasele 674 / 675] butoanele stau direct pe rând (nu mai sunt sub „Acțiuni”)."""
    return pg.locator(".fereastra:last-of-type table.fd-tabel tbody tr", has_text="Utilaj de probă %s" % cod).first


def fereastra_mf(pg, cod, fel, data, justa=None):
    """[lotul 13, deficiența 518 + clasa 673] Casarea / reevaluarea se fac într-o fereastră nouă, cu data cerută (și valoarea justă)."""
    _randul(pg, cod).locator("[data-caseaza]" if fel == "casare" else "[data-reeval]").click()
    pg.wait_for_selector(".fereastra:last-of-type #mf-f-data", timeout=20000)
    pg.fill(".fereastra:last-of-type #mf-f-data", data)
    if justa is not None:
        pg.fill(".fereastra:last-of-type #mf-f-justa", str(justa))
    pg.click(".fereastra:last-of-type #mf-f-genereaza")


def _confirmarea(pg):
    pg.wait_for_selector(".fereastra:last-of-type #mf-f-mesaj .caseta-ok .cok-linii", timeout=30000)
    return [" ".join(x.split()) for x in pg.inner_text(".fereastra:last-of-type #mf-f-mesaj .cok-linii").split("\n") if x.strip()]


def test_def_8c_casarea_mijlocului_fix_confirmare_verde_cu_conturile_notei(patron, firma_gv):
    """8c. Pașii: Mijloace fixe -> „Utilaj de probă MFJ2C” (6.000 lei, PIF în luna curentă) -> „Casează” -> [lotul 13, 518] fereastra
    casării: data casării -> „Generează nota de casare”: caseta verde „Nota de casare (ciornă)” cu rândurile notei exact ca în Registrul
    jurnal; registrul arată activul „casare în ciornă” până la validare (519)."""
    f = firma_gv
    pg = patron.pg
    _mf(f, "MFJ2C", "6000", 60, AZI.replace(day=1).isoformat())
    inainte = _ultima_nota(f)
    _mijloace(patron, f)
    fereastra_mf(pg, "MFJ2C", "casare", AZI.isoformat())
    linii = _confirmarea(pg)
    patron.captura("casare")
    nid = _ultima_nota(f)
    assert nid > inainte, "casarea n-a scris nota"
    assert linii == _randuri_notei(f, nid), (linii, _randuri_notei(f, nid))
    titlu = pg.inner_text(".fereastra:last-of-type #mf-f-mesaj .cok-titlu")
    assert titlu.startswith("Nota de casare (") and "msg-" not in (pg.get_attribute(".fereastra:last-of-type #mf-f-mesaj", "class") or ""), titlu


def test_def_8c_reevaluarea_mijlocului_fix_confirmare_verde_si_fara_diferenta_fara_nota(patron, firma_gv):
    """8c. Pașii: Mijloace fixe -> „Utilaj de probă MFJ2R” (6.000 lei, PIF în luna curentă) -> „Reevaluează” -> fereastra reevaluării:
    data, valoarea justă 6.000 (= valoarea netă) -> „Nicio diferență de reevaluat … Nu s-a generat nicio notă.” -> valoarea justă 7.000 ->
    caseta verde „Nota de reevaluare (ciornă)”, cu rândurile notei ca în Registrul jurnal (OMFP 1802/2014 pct.111-116)."""
    f = firma_gv
    pg = patron.pg
    _mf(f, "MFJ2R", "6000", 60, AZI.replace(day=1).isoformat())
    inainte = _ultima_nota(f)
    _mijloace(patron, f)
    fereastra_mf(pg, "MFJ2R", "reevaluare", AZI.isoformat(), 6000)
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #mf-f-mesaj') || {innerText: ''}).innerText"
                         ".includes('Nicio diferență de reevaluat')", timeout=30000)
    patron.captura("fara_diferenta")
    assert pg.locator(".fereastra:last-of-type #mf-f-mesaj .caseta-ok").count() == 0
    assert _ultima_nota(f) == inainte, "fără diferență nu se scrie nicio notă"
    pg.fill(".fereastra:last-of-type #mf-f-justa", "7000")
    pg.click(".fereastra:last-of-type #mf-f-genereaza")
    linii = _confirmarea(pg)
    patron.captura("reevaluare")
    nid = _ultima_nota(f)
    assert nid > inainte, "reevaluarea n-a scris nota"
    assert linii == _randuri_notei(f, nid), (linii, _randuri_notei(f, nid))
    assert pg.inner_text(".fereastra:last-of-type #mf-f-mesaj .cok-titlu").startswith("Nota de reevaluare (")
