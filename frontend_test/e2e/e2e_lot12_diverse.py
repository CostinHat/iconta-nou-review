# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.1 (verbatim în DECIZII „Comanda 12.1”), pachetul `diverse`: C123, C117, 214, 263. Pașii contabilului pe
aplicația din index, pe baza de TEST, pe firme NOI de test (`conftest.firma_noua`, scoase la final).

  * C123 — asistentul rămas fără nicio firmă se dezactivează (regula „zero firme” a cabinetului, `asistenti_api.aplica_regula_zero_firme`)
    pe AMBELE drumuri care îi rup legătura cu firmele: „Scoate firma” (`tenant_stergere.sterge`) și scoaterea ultimei firme din ecranul
    colegului (Asistenți -> Editează); înainte, „Scoate firma” îl lăsa activ, fără firme;
  * C117 — Operațiuni -> Inventariere anuală -> Casare nu mai cere „Valoare” (valoarea și amortizarea vin din mijlocul fix ales din
    registru); la Plus / Minus câmpul rămâne;
  * 214 — o ciornă de amortizare scrisă de codul vechi (ziua 28) se arată depășită în Registrul jurnal și se reface în ultima zi a lunii;
  * 263 — „Scoate firma” numără evidența acordat („1 notă contabilă”, nu „1 note contabile”).

DATE DE PORNIRE fără ecran, declarate: contul de asistent al probei (`e2e_bloc_b._cont_asistent`, scrierea din care îl creează invitația)
și mijlocul fix din registru (`e2e_bloc_e._mf`, scrierea registrului); la 214, ciorna veche cum o scria codul de dinainte de reparație
(ziua 28) — aplicația de azi nu o mai poate produce, tocmai ea e defectul. Tot restul e pe ecran.

Temei 214 (INTERPRETARE CU TEMEI, decizia Costin 08.10.2026 pct.7 „dacă nu are, data e ultima zi a lunii”): OMFP 1802/2014 pct.238
alin.(2) „Amortizarea imobilizărilor corporale se calculează începând cu luna următoare punerii în funcțiune” — amortizarea e a LUNII, iar
documentul ei (tabloul de amortizare al lunii) acoperă luna întreagă; norma nu numește ziua.
C117, C123, 263: N/A — reguli de produs (CLAUDE.md §9), nu fiscale."""
import datetime as _dt
import os
import re
import sys

import pytest

from conftest import firma_noua, sql

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_bloc_b import _cont_asistent, _deschide_rand, _firma_gata, _nota_jn, _nota_prin_ecran, _scoate_cont   # noqa: E402
from e2e_bloc_e import _asteapta_text, _card, _la_luna, _mf   # noqa: E402

AZI = _dt.date.today()


@pytest.fixture()
def firma_d():
    for f in firma_noua():
        yield f


def _scoate_asistentul(uid):
    sql("DELETE FROM public.user_tenants WHERE user_id = %s", (uid,))
    _scoate_cont(uid)


def _starea_contului(uid):
    return sql("SELECT activ, poate_pregati, poate_valida, poate_depune FROM public.users WHERE id = %s", (uid,))[0]


def _ecranul_scoaterii(e, f):
    e.firma(f["nume"])
    e.pg.locator("#firma-scoate").scroll_into_view_if_needed(timeout=20000)
    e.pg.click("#firma-scoate")
    e.pg.wait_for_selector("#sf-corp .caseta-atentie", timeout=30000)


def _asistentii(e):
    e.acasa()
    e.pg.click("button.cab-card:has([data-cheie='asistenti'])")
    e.pg.wait_for_selector("#asi-lista .val-card, #asi-lista .stare-goala", timeout=30000)


def _randul_dezactivat(e, nume):
    """Rândul colegului în lista „dezactivați” (deschisă cu „Arată dezactivați (N)”)."""
    pg = e.pg
    pg.wait_for_selector("#asi-toggle-dez", timeout=20000)
    pg.click("#asi-toggle-dez")
    rand = pg.locator("#asi-lista-dez .val-card", has_text=nume).first
    rand.wait_for(timeout=20000)
    return " ".join(rand.inner_text().split())


# ── C123: „Scoate firma” ────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c123_scoate_firma_dezactiveaza_asistentul_ramas_fara_firme(patron, firma_d):
    """C123. Pașii: firma nouă (fără niciun document), lucrată de un asistent numai pe ea -> fereastra firmei -> „Scoate firma din portofoliu”:
    previzualizarea spune că asistentul rămâne fără nicio firmă și că i se dezactivează contul -> CUI-ul -> „Scoate firma definitiv” ->
    Asistenți -> „Arată dezactivați”: asistentul e acolo, „dezactivat”, cu 0 firme; contul lui e inactiv, fără competențe (rămâne în
    istoric, nu se șterge)."""
    f = firma_d
    a = _cont_asistent(f, "c123s")
    nume = "Ana Probă c123s"
    try:
        assert _starea_contului(a["id"])[0] is True
        _ecranul_scoaterii(patron, f)
        pg = patron.pg
        prev = " ".join(pg.inner_text("#sf-asistenti").split())
        patron.captura("previzualizare")
        assert nume in prev and "rămâne fără nicio firmă" in prev and "contul se dezactivează" in prev, prev
        cui = sql("SELECT cui FROM public.tenants WHERE id = %s", (f["tenant_id"],))[0][0]
        pg.fill("#sf-cui", str(cui))
        pg.dispatch_event("#sf-cui", "input")
        pg.click("#sf-sterge")
        pg.wait_for_function("() => document.body.innerText.includes('scoasă definitiv din portofoliu')", timeout=60000)
        assert sql("SELECT count(*) FROM public.tenants WHERE id = %s", (f["tenant_id"],)) == [(0,)]
        # regula „zero firme” (`asistenti_api.aplica_regula_zero_firme`): competențele golite, contul dezactivat, nu șters
        assert _starea_contului(a["id"]) == (False, False, False, False), _starea_contului(a["id"])
        _asistentii(patron)
        rand = _randul_dezactivat(patron, nume)
        patron.captura("asistenti_dezactivat")
        assert "dezactivat" in rand and "0 firme" in rand, rand
    finally:
        _scoate_asistentul(a["id"])


# ── C123: ecranul colegului (aceeași regulă, al doilea drum din clasă) ───────────────────────────────────────────────────────────
def test_def_c123_ultima_firma_scoasa_din_ecranul_colegului_dezactiveaza_contul(patron, firma_d):
    """C123, al doilea drum. Pașii: Asistenți -> asistentul (o singură firmă) -> „Editează” -> debifează firma -> „Salvează”: caseta „…
    rămâne fără nicio firmă. Competențele se șterg și contul se dezactivează (rămâne în istoric)” -> „Da, salvează” -> „Arată dezactivați”:
    asistentul e acolo, „dezactivat”."""
    f = firma_d
    a = _cont_asistent(f, "c123e")
    nume = "Ana Probă c123e"
    try:
        _asistentii(patron)
        pg = patron.pg
        card = pg.locator("#asi-lista .val-card", has_text=nume).first
        card.wait_for(timeout=20000)
        card.locator("[data-act='edit']").click()
        cb = pg.locator("[data-tid='%d']" % f["tenant_id"])
        cb.wait_for(timeout=20000)
        assert cb.is_checked()
        cb.uncheck()
        pg.click("#asi-salveaza")
        pg.wait_for_selector("#ca-ok", timeout=20000)
        caseta = " ".join(pg.inner_text("#caseta-atentie-activa").split())
        patron.captura("confirmare")
        assert "rămâne fără nicio firmă" in caseta and "contul se dezactivează" in caseta, caseta
        pg.click("#ca-ok")
        rand = _randul_dezactivat(patron, nume)
        patron.captura("dezactivat")
        assert "dezactivat" in rand, rand
        assert _starea_contului(a["id"]) == (False, False, False, False), _starea_contului(a["id"])
    finally:
        _scoate_asistentul(a["id"])


# ── 263: „Scoate firma” — pluralul după număr ────────────────────────────────────────────────────────────────────────────────────
def test_def_263_scoate_firma_numara_evidenta_acordat(patron, firma_d):
    """263. Pașii: firma nouă cu O notă contabilă (Registru jurnal -> Notă nouă -> Salvează) -> „Scoate firma din portofoliu”: „Firma nu se
    poate șterge … Ce s-a găsit: 1 notă contabilă” (nu „1 note contabile”) -> a doua notă -> „2 note contabile”."""
    f = firma_d
    _firma_gata(f)
    _nota_prin_ecran(patron, f, "Nota E2E 263 a", AZI.isoformat())
    _ecranul_scoaterii(patron, f)
    pg = patron.pg
    t = " ".join(pg.inner_text("#sf-corp .caseta-atentie").split())
    patron.captura("o_nota")
    assert "nu se poate șterge" in t and "1 notă contabilă" in t and "1 note" not in t, t
    _nota_prin_ecran(patron, f, "Nota E2E 263 b", AZI.isoformat())
    _ecranul_scoaterii(patron, f)
    t = " ".join(pg.inner_text("#sf-corp .caseta-atentie").split())
    patron.captura("doua_note")
    assert "2 note contabile" in t, t


# ── C117: Inventariere › Casare fără „Valoare” ───────────────────────────────────────────────────────────────────────────────────
def _vizibil(pg, sel):
    return pg.evaluate("(s) => { const el = document.querySelector(s); const c = el && el.closest('.camp'); "
                       "return !!c && getComputedStyle(c).display !== 'none'; }", sel)


def test_def_c117_casarea_nu_cere_valoarea_mijlocului_fix(patron, firma_d):
    """C117. Pașii: firma cu un mijloc fix în registru (1.200 lei, 12 luni, PIF 10.01.2026) -> Operațiuni -> „Inventariere anuală” ->
    Operație: Plus stoc: „Valoare” se cere -> Operație: Casare: „Valoare” nu se mai arată, se cere „Mijlocul fix” din registru -> alege
    mijlocul fix, data -> „Generează nota (ciornă)”: „Notă generată”, cu 2131 creditat cu toată valoarea mijlocului fix (1.200,00), fără
    „Completează: Valoare”."""
    f = firma_d
    _firma_gata(f)
    mid = _mf(f, "MF117", "1200", 12, "2026-01-10")
    # [lotul 13, 518] date de pornire: amortizarea lunilor de dinaintea casării, înregistrată pe activ (note validate, cu activul pe rând) —
    # fără ea casarea se refuză (lunile lipsă nu trec prin 6811)
    for luna in range(2, AZI.month):
        # ciornă -> rândul (cu activul, `mf_linii`) -> validată: rândurile unei note validate nu se mai scriu (`trg_regula_linii_nota`)
        (nid,) = sql('INSERT INTO "%s".inregistrari (data, descriere, sursa, status, document_ref) VALUES (%%s, %%s, %%s, %%s, %%s) RETURNING id'
                     % f["schema"], ("2026-%02d-28" % luna, "Amortizare E2E C117", "operatiuni", "ciorna", "Tablou E2E"))[0]
        (lid,) = sql('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, %%s, %%s, %%s) RETURNING id'
                     % f["schema"], (nid, "6811", "2813", 100))[0]
        sql('INSERT INTO "%s".mf_linii (linie_id, mijloc_fix_id) VALUES (%%s, %%s)' % f["schema"], (lid, mid))
        sql('UPDATE "%s".inregistrari SET status = \'validata\' WHERE id = %%s' % f["schema"], (nid,))
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-operatiuni")
    pg.wait_for_selector("button[data-op='inventariere']", timeout=25000)
    pg.click("button[data-op='inventariere']")
    pg.wait_for_selector("#op-operatie", timeout=20000)
    pg.select_option("#op-operatie", "plus")
    assert _vizibil(pg, "#op-valoare"), "la Plus stoc valoarea trebuie cerută"
    pg.select_option("#op-operatie", "casare")
    assert not _vizibil(pg, "#op-valoare"), "la Casare „Valoare” se arată, deși serverul o ia din registru"
    assert _vizibil(pg, "#op-mijloc_fix_id")
    pg.wait_for_function("(id) => [...document.querySelectorAll('#op-mijloc_fix_id option')].some(o => o.value === String(id))",
                         arg=mid, timeout=20000)
    pg.select_option("#op-mijloc_fix_id", str(mid))
    pg.fill("#op-data", AZI.isoformat())
    pg.dispatch_event("#op-data", "change")
    patron.captura("casare")
    pg.click("#op-trimite")
    pg.wait_for_selector("#op-mesaj [data-dupa-generare], #op-mesaj .msg-eroare", timeout=30000)
    m = " ".join(pg.inner_text("#op-mesaj").split())
    patron.captura("nota_casare")
    assert "Notă generată" in m and "Completează: Valoare" not in m, m
    # nota casării: sursa „operatiuni” (`repo_contabilitate.nota_operatiune_ciorna`), descrierea „Casare <mijlocul fix> (PV comisie, …)”
    linii = sql('SELECT l.cont_debit, l.cont_credit, l.suma FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l '
                "ON l.inregistrare_id = i.id WHERE i.sursa = 'operatiuni' AND i.descriere LIKE %%s ORDER BY l.cont_debit"
                % (f["schema"], f["schema"]), ("Casare Utilaj de probă MF117 %",))
    # 2131 creditat cu toată valoarea (amortizarea pe 2813 + restul pe 6583); [518] luna casării prin 6811
    assert linii and sum(s for _d, c, s in linii if c == "2131") == 1200 and any(d == "6811" for d, _c, _s in linii), linii


# ── 214: ciorna veche de amortizare (ziua 28) ───────────────────────────────────────────────────────────────────────────────────
def test_def_214_ciorna_veche_de_amortizare_datata_28_se_reface_in_ultima_zi(patron, firma_d):
    """214, datele existente. Pașii: firma cu un mijloc fix (6.000 lei, 60 de luni, PIF 10.05.2026) și ciorna amortizării 06/2026 scrisă de
    codul vechi (28.06.2026, 6811 = 2813 100,00) -> Registru jurnal, 06/2026: pe rândul ciornei, caseta „… după o regulă care s-a schimbat
    … data 30.06.2026 (pe ciornă: 28.06.2026)”, „Validează” inactiv -> „Refă nota din registrul mijloacelor fixe”: nota nouă e datată
    30.06.2026, cu „Document justificativ: Tablou de amortizare nr N din 30.06.2026” (documentul intern al notei) -> „Validează”: Validată."""
    f = firma_d
    _firma_gata(f)
    s = f["schema"]
    _mf(f, "MF214V", "6000", 60, "2026-05-10")
    # date-de-pornire: ciorna amortizării cum o scria codul de dinainte de reparație (ziua 28) — antetul
    veche = sql('INSERT INTO "%s".inregistrari (data, numar, descriere, sursa, status) VALUES (\'2026-06-28\', \'AMORT-2026-06\', '
                "'Amortizare 06/2026', 'amortizare', 'ciorna') RETURNING id" % s)[0][0]
    # date-de-pornire: rândul aceleiași ciorne vechi (6811 = 2813 100,00), cum îl scria codul de dinainte de reparație
    sql('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, \'6811\', \'2813\', 100)' % s,
        (veche,))
    pg = patron.pg
    _card(patron, f, "jurnal", "#j-amort")
    _la_luna(patron, "#j-prev", 2026, 6)
    # [lotul 12, 617] caseta „depășită” stă în detaliul rândului: rândul ciornei, deschis
    pg.wait_for_selector("tbody.tn-nota[data-nota-id='%d']" % veche, timeout=30000)
    _deschide_rand(patron, _nota_jn(patron, veche))
    pg.wait_for_selector("#jn-depasita-%d" % veche, timeout=30000)
    t = " ".join(pg.inner_text("tbody.tn-nota[data-nota-id='%d']" % veche).split())
    patron.captura("vechi_ciorna_28")
    assert "după o regulă care s-a schimbat" in t and "30.06.2026" in t and "28.06.2026" in t, t
    assert pg.is_disabled("[data-val='%d']" % veche)
    pg.click("[data-reface='%d']" % veche)
    _asteapta_text(patron, "Nota a fost refăcută")
    noi = sql('SELECT id, data FROM "%s".inregistrari WHERE numar = \'AMORT-2026-06\' ORDER BY id' % s)
    assert len(noi) == 1 and noi[0][0] != veche and str(noi[0][1]) == "2026-06-30", noi
    nou = noi[0][0]
    pg.wait_for_selector("tbody.tn-nota[data-nota-id='%d']" % nou, timeout=30000)
    # [lotul 12, 617] „Document justificativ: …” stă în detaliul rândului: rândul notei refăcute, deschis
    _deschide_rand(patron, _nota_jn(patron, nou))
    rand = " ".join(pg.inner_text("tbody.tn-nota[data-nota-id='%d']" % nou).split())
    patron.captura("vechi_refacuta")
    # documentul notei refăcute: tabloul de amortizare intern, numerotat și datat în ultima zi (ca notele noi de pe F2: „Tablou de amortizare
    # nr 8 din 31.08.2026”) — nu „nederivat”
    assert "30.06.2026" in rand and re.search(r"Document justificativ: Tablou de amortizare nr \d+ din 30\.06\.2026", rand) \
        and "nederivat" not in rand, rand
    assert pg.locator("#jn-depasita-%d" % nou).count() == 0
    pg.click("[data-val='%d']" % nou)
    pg.wait_for_function("(id) => { const r = document.querySelector(`[data-nota-id='${id}']`); return r && r.innerText.includes('Validată'); }",
                         arg=nou, timeout=30000)
    assert sql('SELECT status, data FROM "%s".inregistrari WHERE id = %%s' % s, (nou,)) == [("validata", _dt.date(2026, 6, 30))]


# ── C128: achiziția intracomunitară de la un furnizor din România ────────────────────────────────────────────────────────────────
def _operatiunea(e, f, cheie):
    e.firma(f["nume"])
    e.pg.click("#fa-operatiuni")
    e.pg.wait_for_selector("button[data-op='%s']" % cheie, timeout=25000)
    e.pg.click("button[data-op='%s']" % cheie)
    e.pg.wait_for_selector("#op-trimite", timeout=20000)


def test_def_c128_achizitia_intracomunitara_refuza_furnizorul_din_romania(patron, firma_d):
    """C128. Pașii: Operațiuni -> „Achiziție intracomunitară” -> data, valoarea 1.000, codul de TVA al furnizorului RO14399840 (DANTE
    INTERNATIONAL SA, cifra de control verificată), nr. factură, contul 371, Bunuri, cota 21, data faptului generator -> „Generează nota”:
    sub câmpul codului „Codul de TVA al furnizorului începe cu RO … nu e achiziție intracomunitară …”, nicio factură, nicio notă; cu
    DE123456789 nota se generează. Temei: CF art.273 alin.(1) („către un stat membru, altul decât cel de plecare”), art.307 alin.(2)."""
    from core.intracomunitar import MESAJ_AIC_RO
    f = firma_d
    _firma_gata(f)
    pg = patron.pg
    _operatiunea(patron, f, "achizitie_ic")
    for camp, v in (("data", AZI.isoformat()), ("valoare", "1000"), ("cod_tva_furnizor", "RO14399840"), ("numar", "AIC-C128"),
                    ("cota", "21"), ("data_faptului_generator", AZI.isoformat())):
        pg.fill("#op-%s" % camp, v)
    pg.select_option("#op-moneda", "RON")   # [lotul 13, 537] moneda facturii se alege
    pg.fill("#op-cont_destinatie", "371")
    pg.select_option("#op-tip", "bunuri")
    pg.click("#op-trimite")
    pg.wait_for_selector('.msg-eroare[data-camp="op-cod_tva_furnizor"]', timeout=30000)
    sub = " ".join(pg.inner_text('.msg-eroare[data-camp="op-cod_tva_furnizor"]').split())
    patron.captura("furnizor_ro")
    assert sub == MESAJ_AIC_RO, sub
    assert sql('SELECT count(*) FROM "%s".facturi WHERE numar = %%s' % f["schema"], ("AIC-C128",)) == [(0,)]
    pg.fill("#op-cod_tva_furnizor", "DE123456789")
    pg.click("#op-trimite")
    pg.wait_for_selector("#op-mesaj [data-dupa-generare]", timeout=30000)
    patron.captura("furnizor_de")
    assert sql('SELECT tert_tara FROM "%s".facturi WHERE numar = %%s' % f["schema"], ("AIC-C128",)) == [("DE",)]


# ── C129: reevaluarea pe o fișă fără contul de imobilizare ──────────────────────────────────────────────────────────────────────
def test_def_c129_reevaluarea_refuza_fisa_fara_cont_de_imobilizare(patron, firma_d):
    """C129. Date de pornire: o fișă în registru cu contul de imobilizare GOL, cum o scrie importul registrului când rândul n-are cont
    (`mijloace_fixe_import_api`: „gol = neclasificat”). Pașii: Operațiuni -> „Reevaluare imobilizări (105)” -> Reevaluare MF -> fișa ->
    data, valoarea justă 15.000 -> „Generează nota”: „Mijlocul fix … nu are contul de imobilizare în registru … Completează ce
    lipsește din Migrare → Mijloace fixe …”, nicio notă (înainte: nota cu „ = 105”, fără contul activului)."""
    from core.amortizare_lunii import UNDE_SE_COMPLETEAZA
    f = firma_d
    _firma_gata(f)
    mid = _mf(f, "MF129", "12000", 60, "2026-01-10", cont="")
    pg = patron.pg
    _operatiunea(patron, f, "reevaluare")
    pg.select_option("#op-operatie", "reevaluare")
    pg.wait_for_function("(id) => [...document.querySelectorAll('#op-mijloc_fix_id option')].some(o => o.value === String(id))",
                         arg=mid, timeout=20000)
    pg.select_option("#op-mijloc_fix_id", str(mid))
    pg.fill("#op-data", AZI.isoformat())
    pg.fill("#op-valoare_justa", "15000")   # [lotul 13, 511] rezerva 105 și pierderea 655 nu se mai cer: le ia aplicația
    pg.click("#op-trimite")
    pg.wait_for_selector("#op-mesaj.msg-eroare, #op-mesaj [data-dupa-generare]", timeout=30000)   # `arataMesaj`: clasa e pe zonă
    m = " ".join(pg.inner_text("#op-mesaj").split())
    patron.captura("fara_cont")
    assert "msg-eroare" in (pg.get_attribute("#op-mesaj", "class") or ""), m
    assert "Utilaj de probă MF129" in m and "nu are contul de imobilizare în registru" in m and UNDE_SE_COMPLETEAZA in m, m
    assert sql('SELECT count(*) FROM "%s".inregistrari WHERE descriere LIKE %%s' % f["schema"], ("Reevaluare %MF129%",)) == [(0,)]


# ── C136: „Scoate firma” / „Firme scoase” fără numele tabelelor din bază ─────────────────────────────────────────────────────────
def test_def_c136_scoate_firma_spune_ce_dispare_in_cuvintele_contabilului(patron, firma_d):
    """C136. Pașii: firma nouă (fără documente) -> „Scoate firma din portofoliu”: „Dispar și: …” în cuvintele contabilului (ex. „1 acces al
    unui utilizator la firmă”), exact textul serverului (`tenant_stergere.ce_dispare`), fără „×”, fără `audit_log` / `user_tenants`, fără
    „schema” -> CUI -> „Scoate firma definitiv” -> Firme -> „Firme scoase”: rândul firmei spune ce s-a curățat la fel, fără numele schemei."""
    import re as _re
    from core import db, tenant_stergere as ts
    f = firma_d
    with db.get_conn() as c:
        asteptat = ts.previzualizare(c, f["tenant_id"])["ce_dispare"]
        c.rollback()
    assert asteptat, "firma nouă n-are nimic de curățat în afara datelor ei — proba n-ar arăta textul"
    _ecranul_scoaterii(patron, f)
    pg = patron.pg
    t = " ".join(pg.inner_text("#sf-ce-dispare").split())
    patron.captura("previzualizare")
    assert all(x in t for x in asteptat) and "×" not in t and not _re.search(r"\b[a-z]+_[a-z_]+\b", t) and "schema" not in t, t
    cui = sql("SELECT cui FROM public.tenants WHERE id = %s", (f["tenant_id"],))[0][0]
    pg.fill("#sf-cui", str(cui))
    pg.dispatch_event("#sf-cui", "input")
    pg.click("#sf-sterge")
    pg.wait_for_function("() => document.body.innerText.includes('scoasă definitiv din portofoliu')", timeout=60000)
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='firme'])")
    pg.wait_for_timeout(600)
    if pg.query_selector("#opt-existente"):   # ca `conftest.Ecran.firma`: alegerea „firme existente” vine înaintea listei
        pg.click("#opt-existente")
    pg.wait_for_selector("#firme-vezi-scoase", timeout=30000)
    pg.click("#firme-vezi-scoase")
    rand = pg.locator(".firme-rand", has_text=f["nume"]).first
    rand.wait_for(timeout=20000)
    r = " ".join(rand.inner_text().split())
    patron.captura("firme_scoase")
    assert "S-au curățat:" in r and "×" not in r and f["schema"] not in r and not _re.search(r"\b[a-z]+_[a-z_]+\b", r), r
