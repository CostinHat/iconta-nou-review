# -*- coding: utf-8 -*-
"""Blocul F (DEFICIENTE.md 171–188, retestul lotului 08.10 din 09.10.2026) — deficiențele probate în browser, pe aplicația pornită de
`scripts/e2e_poarta.py`. Testele care scriu date scriu pe firma sintetică a rulării (`firma_e2e`); cele care citesc firmele de test
comune („Comert Micro TVA SRL”, „Achizitii IC Neplatitor SRL”, „Coafor Micro Neplatitor SRL”) nu scriu nimic pe ele."""
import datetime as _dt
import io
import re
from decimal import Decimal

from conftest import sql

FIRMA_TVA = "Comert Micro TVA SRL"              # tenant_003, plătitoare de TVA
FIRMA_NEPLATITOARE = "Coafor Micro Neplatitor SRL"   # tenant_002
FIRMA_IC_NEPLATITOARE = "Achizitii IC Neplatitor SRL"  # tenant_006, neplătitoare cu achiziții intracomunitare


# ── ajutoare ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _api(ecran, cale, metoda="GET", corp=None):
    """O cerere a aplicației cu sesiunea contului din `ecran` (aceeași cale pe care o folosește ecranul): (status, json)."""
    return ecran.pg.evaluate("""async ([c, m, b]) => { const t = sessionStorage.getItem('iconta_token');
      const r = await fetch(c, {method: m, headers: {'Authorization': 'Bearer ' + t, 'Content-Type': 'application/json'},
        body: b === null ? undefined : JSON.stringify(b)}); let d = null; try { d = await r.json(); } catch (e) {} return [r.status, d]; }""",
                             [cale, metoda, corp])


def _ro(v):
    """Suma în forma de pe ecran (`bani` din api.js, ro-RO): 1250 -> „1.250,00”."""
    s = "{:,.2f}".format(Decimal(str(v)))
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _azi():
    from core.common import azi_ro
    return azi_ro()


def _tenant(nume):
    r = sql("SELECT id, schema_name, cui FROM public.tenants WHERE nume = %s", (nume,))
    assert r, "firma de test %s lipsește din baza de test" % nume
    return r[0]


def _fata(pg):
    return ".fereastra:last-of-type"


def _control_fiscal(ecran):
    pg = ecran.pg
    ecran.acasa()
    pg.click("button.cab-card:has([data-cheie='control'])")
    pg.wait_for_selector("#cf-lista .mig-frand", timeout=60000)


def _detaliu_fiscal(ecran, nume):
    """Control fiscal -> clic pe rândul firmei -> detaliul ei fiscal (așteaptă corpul verdictului)."""
    pg = ecran.pg
    _control_fiscal(ecran)
    pg.locator("#cf-lista .mig-frand", has_text=nume).first.click()
    pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); "
                         "return f && f.querySelector('#cf-audit-run'); }", timeout=90000)


def _nota(ecran, tid, descriere, suma, debit="5311", credit="4111", document=None):
    """O notă manuală, ciornă, scrisă de contul din `ecran` pe drumul aplicației (POST /tenants/{id}/jurnal)."""
    st, r = _api(ecran, "/tenants/%s/jurnal" % tid, "POST",
                 {"data": _azi().isoformat(), "descriere": descriere, "document_ref": document,
                  "linii": [{"debit": debit, "credit": credit, "suma": str(suma)}]})
    assert st == 200 and r and r.get("id"), (st, r)
    return r["id"]


# ── 171 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def test_def_171_marcarea_lasa_grupul_deschis_si_ecranul_pe_rand(patron, firma_e2e):
    """171. Control fiscal: după „Salvează”/„Anulează marcarea” grupul se pliază și ecranul sare (159 nereparat).
    Pașii contabilului: Control fiscal -> firma -> deschide grupul „Înainte de preluare” -> pe rândul D205 2025 „Marchează depusă în
    afara iConta.eu”, scrie data, „Salvează” -> grupul rămâne deschis și rândul stă în același loc pe ecran; apoi „Anulează marcarea”
    -> confirmă -> la fel."""
    pg = patron.pg
    _detaliu_fiscal(patron, firma_e2e["nume"])
    grup = _fata(pg) + " details.cf-inainte"
    rand = grup + " [data-cheie='d205-2025-12']"
    pg.click(grup + " > summary")
    pg.wait_for_selector(rand + " .cf-extern-btn", timeout=20000)
    pg.eval_on_selector(rand, "e => e.scrollIntoView({block: 'center'})")
    y0 = pg.eval_on_selector(rand, "e => e.getBoundingClientRect().top")
    patron.captura("inainte")
    pg.click(rand + " .cf-extern-btn")
    pg.fill(rand + " .cf-extern-form input[type=date]", "2026-02-20")
    pg.click(rand + " .cf-extern-salveaza")
    pg.wait_for_selector(rand + " .cf-extern-anuleaza", timeout=60000)
    assert pg.eval_on_selector(grup, "d => d.open"), "grupul „Înainte de preluare” s-a pliat după „Salvează”"
    y1 = pg.eval_on_selector(rand, "e => e.getBoundingClientRect().top")
    assert abs(y1 - y0) <= 4, "rândul atins a sărit pe ecran după „Salvează”: %s -> %s px" % (y0, y1)
    patron.captura("dupa_salveaza")
    pg.click(rand + " .cf-extern-anuleaza")
    pg.click("#ca-ok")
    pg.wait_for_function("(s) => { const r = document.querySelector(s); return r && !r.querySelector('.cf-extern-anuleaza') "
                         "&& r.innerText.includes('Marchează depusă'); }", arg=rand, timeout=60000)
    assert pg.eval_on_selector(grup, "d => d.open"), "grupul „Înainte de preluare” s-a pliat după „Anulează marcarea”"
    y2 = pg.eval_on_selector(rand, "e => e.getBoundingClientRect().top")
    assert abs(y2 - y0) <= 4, "rândul atins a sărit pe ecran după „Anulează marcarea”: %s -> %s px" % (y0, y2)
    patron.captura("dupa_anuleaza")


# ── 173 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def test_def_173_contoarele_de_sus_numara_dupa_aceeasi_regula_ca_randurile(patron):
    """173. Control fiscal: contoarele cu două reguli; cifrele raportului nu sunt pe ecran.
    Pașii contabilului: Control fiscal -> citește contoarele de sus și numără, pe rândurile firmelor de dedesubt, câte au restanțe,
    câte au declarații de urmărit și câte nu se pot verifica -> fiecare contor e egal cu numărătoarea lui de pe rânduri (o regulă:
    firma care ARE faptul)."""
    pg = patron.pg
    _control_fiscal(patron)
    d = pg.evaluate("""() => { const f = [...document.querySelectorAll('.fereastra')].pop();
      return {pastile: [...f.querySelectorAll('.cf-sumar .cf-pastila')].map(e => e.innerText.trim()),
              nota: (f.querySelector('.cf-sumar + .ecran-nota') || {}).innerText || '',
              randuri: [...f.querySelectorAll('#cf-lista .mig-frand')].map(r => ({
                sub: r.querySelector('.mig-frand-sub').innerText, stare: r.querySelector('.cf-stare').innerText}))}; }""")
    patron.captura()
    cont = {}
    for p in d["pastile"]:
        m = re.match(r"(\d+)\s+(.*)", p)
        cont[m.group(2)] = int(m.group(1))
    rr = d["randuri"]
    nsv = lambda r: any(x in r["sub"] + " " + r["stare"] for x in ("nu se pot verifica", "nu se poate verifica"))  # noqa: E731
    pe_randuri = {"cu restanțe": sum(1 for r in rr if re.search(r"\d+ restanț", r["sub"])),
                  "cu declarații de urmărit": sum(1 for r in rr if re.search(r"\d+ de urmărit", r["sub"])),
                  "nu se pot verifica": sum(1 for r in rr if nsv(r))}
    assert "Din %d firme" % len(rr) in d["nota"], d["nota"]
    for eticheta, n in pe_randuri.items():
        assert cont.get(eticheta) == n, "contorul „%s” arată %s, rândurile de dedesubt au %d" % (eticheta, cont.get(eticheta), n)
    assert pe_randuri["nu se pot verifica"] > sum(1 for r in rr if r["stare"].strip().endswith(("nu se poate verifica",
                                                                                                 "nu se pot verifica"))), \
        "proba n-are o firmă cu necunoscute și altă stare principală — nu deosebește cele două reguli"


# ── 175 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def test_def_175_amortizarea_calculata_merge_pana_la_ultima_luna_incheiata(patron, firma_e2e):
    """175. Mijloace fixe: amortizarea calculată include luna în curs.
    Pașii contabilului: firma -> Mijloace fixe -> mijlocul fix pus în funcțiune pe 10.12.2025 (12.000 lei, 24 de luni, liniar: 500
    lei/lună) -> „Amortizat (calculat)” = lunile de la 01/2026 până la ultima lună ÎNCHEIATĂ, nu și luna în curs; antetul spune luna."""
    from core import db, repo_mijloace_fixe
    s = firma_e2e["schema"]
    with db.get_conn() as c, c.cursor() as cur:
        repo_mijloace_fixe.adauga(cur, s, "MF-E2E-175", "Laptop probă E2E", "2131", "2813", Decimal("12000.00"), 24,
                                  "2025-12-10")
        c.commit()
    azi = _azi()
    pana = azi.replace(day=1) - _dt.timedelta(days=1)
    luni = min(24, (pana.year - 2025) * 12 + pana.month - 12)
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    pg.click("#fa-mijloace")
    rand = _fata(pg) + " tr:has-text('MF-E2E-175')"
    pg.wait_for_selector(rand, timeout=30000)
    patron.captura()
    text, rand_text = patron.fereastra(), pg.inner_text(rand)
    assert "până la %02d/%d" % (pana.month, pana.year) in text, "antetul nu spune ultima lună încheiată"
    assert _ro(500 * luni) in rand_text, "amortizarea calculată nu e %s (= %d luni × 500): %s" % (_ro(500 * luni), luni, rand_text)
    assert _ro(500 * (luni + 1)) not in rand_text, "amortizarea calculată include luna în curs: %s" % rand_text
    assert "%d luni: 01–%02d/%d" % (luni, pana.month, pana.year) in rand_text, rand_text


# ── 176 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def test_def_176_totalul_registrului_jurnal_fara_ciorne(patron, firma_e2e):
    """176. Registru jurnal: „Total sume” include ciornele.
    Pașii contabilului: firma -> Registru jurnal (luna curentă) cu o notă validată (100 lei) și o ciornă (50 lei) -> „Total sume
    debitoare / creditoare (note validate)” = numai notele validate; ciornele stau separat, pe rândul lor."""
    tid, s = firma_e2e["tenant_id"], firma_e2e["schema"]
    patron.acasa()
    v = _nota(patron, tid, "Depunere numerar probă E2E 176", "100.00", document="Chitanța E2E-176/1")
    st, r = _api(patron, "/tenants/%s/jurnal/%s/valideaza" % (tid, v), "POST", {})
    assert st == 200, (st, r)
    _nota(patron, tid, "Ciornă probă E2E 176", "50.00", document="Chitanța E2E-176/2")
    azi = _azi()
    tot = dict(sql('SELECT i.status, COALESCE(SUM(l.suma), 0) FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l ON '
                   "l.inregistrare_id = i.id WHERE date_trunc('month', i.data) = %%s GROUP BY i.status" % (s, s),
                   (azi.replace(day=1),)))
    nr_ciorne = sql('SELECT count(*) FROM "%s".inregistrari WHERE status <> \'validata\' AND date_trunc(\'month\', data) = %%s' % s,
                    (azi.replace(day=1),))[0][0]
    validat, ciorne = tot.get("validata", Decimal(0)), sum(v for k, v in tot.items() if k != "validata")
    assert validat > 0 and ciorne > 0
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    pg.click("#fa-jurnal")
    pg.wait_for_selector(_fata(pg) + " .fd-totaluri", timeout=30000)
    patron.captura()
    randuri = {e.split("\n")[0].strip(): e for e in pg.eval_on_selector_all(_fata(pg) + " .fd-totaluri .fd-tot-rand",
                                                                            "es => es.map(e => e.innerText)")}
    deb = next(v for k, v in randuri.items() if k.startswith("Total sume debitoare"))
    cre = next(v for k, v in randuri.items() if k.startswith("Total sume creditoare"))
    cio = next(v for k, v in randuri.items() if k.startswith("Ciorne în lună"))
    assert _ro(validat) + " lei" in deb and _ro(validat) + " lei" in cre, (deb, cre, validat)
    assert "%d · %s lei" % (nr_ciorne, _ro(ciorne)) in cio, (cio, nr_ciorne, ciorne)
    assert _ro(validat + ciorne) not in deb, "totalul include ciornele: %s" % deb


# ── 177 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def test_def_177_nota_de_stornare_din_coada_arata_rulajul(patron, asistent, firma_e2e):
    """177. Coadă: notele de stornare + reînregistrare cu „total 0,00 lei”.
    Pașii: asistentul încasează 1.250 lei în Casă (nota merge în coadă); contabilul o validează; asistentul stornează operațiunea
    (nota în roșu merge în coadă) -> contabilul deschide „De validat”: cardul notei de stornare arată rulajul ei
    („stornare −1.250,00 lei”), nu totalul algebric al liniilor."""
    tid = firma_e2e["tenant_id"]
    uid_a, *drepturi = sql("SELECT id, poate_pregati, poate_valida, poate_depune FROM public.users "
                           "WHERE email = 'asistent@prisma-cont.test'")[0]
    patron.acasa()
    st, r = _api(patron, "/asistenti/%s/firme/%s" % (uid_a, tid), "POST", {})
    assert st == 200, (st, r)
    # nota intră în coadă numai dacă autorul NU validează (coada_api.e_validator): asistentul e „Poate pregăti” pe durata probei
    st, r = _api(patron, "/asistenti/%s/permisiuni" % uid_a, "POST",
                 {"poate_pregati": True, "poate_valida": False, "poate_depune": bool(drepturi[2])})
    assert st == 200, (st, r)
    try:
        _proba_177(patron, asistent, firma_e2e)
    finally:
        st, r = _api(patron, "/asistenti/%s/permisiuni" % uid_a, "POST",
                     {"poate_pregati": bool(drepturi[0]), "poate_valida": bool(drepturi[1]), "poate_depune": bool(drepturi[2])})
        assert st == 200, (st, r)


def _proba_177(patron, asistent, firma_e2e):
    tid = firma_e2e["tenant_id"]
    asistent.acasa()
    azi = _azi().isoformat()
    st, op = _api(asistent, "/tenants/%s/casa/operatiuni" % tid, "POST",
                  {"data": azi, "tip": "incasare", "categorie": "incasare_client", "suma": "1250.00",
                   "partener": "Client Proba E2E SRL", "document": "CH E2E 177"})
    assert st == 200 and op.get("id"), (st, op)
    patron.acasa()
    st, coada = _api(patron, "/coada")
    el = [x for x in (coada.get("coada") if isinstance(coada, dict) else coada) or []
          if x.get("fel") == "nota" and x.get("tenant_id") == tid and x.get("stare") == "la_senior"]
    assert el, "nota asistentului nu a intrat în coadă: %s" % coada
    for x in el:
        st, r = _api(patron, "/coada/%s/aproba" % x["id"], "POST", {})
        assert st == 200, (st, r)
    st, r = _api(asistent, "/tenants/%s/casa/operatiuni/%s/storneaza" % (tid, op["id"]), "POST", {"data": azi})
    assert st == 200, (st, r)
    pg = patron.pg
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='validat'])")
    card = _fata(pg) + " .val-card:has-text('%s')" % firma_e2e["nume"]
    pg.wait_for_selector(card, timeout=30000)
    text = pg.inner_text(card)
    patron.captura()
    assert "stornare −1.250,00 lei" in text, text
    assert "total 0,00" not in text and "rulaj 0,00" not in text, text


# ── 178 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def test_def_178_clic_pe_firma_din_control_fiscal_deschide_detaliul_fiscal(patron):
    """178. Control fiscal: click pe firmă duce în meniul general.
    Pașii contabilului: Control fiscal -> clic pe o firmă din listă -> se deschide detaliul ei fiscal (grupurile de declarații,
    verificările), nu meniul general al firmei (cardurile Facturi, Casă …)."""
    pg = patron.pg
    _detaliu_fiscal(patron, FIRMA_TVA)
    patron.captura()
    fata = _fata(pg)
    assert pg.locator(fata + " .cf-grup-titlu").count() > 0, "detaliul fiscal n-are grupurile de verificare"
    assert pg.locator(fata + " .firme-optiune").count() == 0, "clicul a deschis meniul general al firmei"
    assert FIRMA_TVA in pg.inner_text(fata + " .mig-intro")
    assert "Detaliu firmă" in patron.fereastra()


# ── 179 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def test_def_179_neplatitorul_vede_nu_se_aplica_si_temeiul_restantei_d390(patron, firma_e2e):
    """179. Control fiscal: F3 (D301) verificată față de D300; restanțele D390 fără temei.
    Pașii contabilului: firmă neplătitoare de TVA, înregistrată art.317, cu o achiziție intracomunitară în 06/2026 (D301), preluată
    din 01/2026 -> Control fiscal -> detaliul firmei: „D300 față de contabilitate” și „D390 față de D300” spun „nu se aplică”, iar
    restanța D390 06/2026 spune pe ce se bazează („operațiuni intracomunitare înregistrate în 06/2026”)."""
    tid, s = firma_e2e["tenant_id"], firma_e2e["schema"]
    vechi = sql('SELECT platitor_tva, operatiuni_ic, inreg_art317, luna_preluare FROM "%s".firma_profil WHERE id = 1' % s)[0]
    sql('UPDATE "%s".firma_profil SET platitor_tva = false, operatiuni_ic = true, inreg_art317 = true, luna_preluare = %%s '
        "WHERE id = 1" % s, (_dt.date(2026, 1, 1),))
    try:
        patron.acasa()
        st, r = _api(patron, "/tenants/%s/d301-operatiuni" % tid, "POST",
                     {"an": 2026, "luna": 6, "tip": 1, "nr_doc": "FE-E2E-179", "data_doc": "15.06.2026", "val_valuta": "1000",
                      "tip_valuta": "EUR", "curs": "5.0000", "cota": 21})
        assert st == 200, (st, r)
        pg = patron.pg
        _detaliu_fiscal(patron, firma_e2e["nume"])
        patron.captura(intreaga=True)
        text = patron.fereastra()
        assert "D300 față de contabilitate: nu se aplică — firma nu e plătitoare de TVA" in text, text
        rand = _fata(pg) + " .cf-decl-item[data-cheie='d390-2026-6']"
        assert pg.locator(rand).count() == 1, "restanța D390 06/2026 lipsește din detaliu"
        assert "operațiuni intracomunitare înregistrate în 06/2026" in pg.inner_text(rand), pg.inner_text(rand)
    finally:
        sql('UPDATE "%s".firma_profil SET platitor_tva = %%s, operatiuni_ic = %%s, inreg_art317 = %%s, luna_preluare = %%s '
            "WHERE id = 1" % s, tuple(vechi))
        sql('DELETE FROM "%s".d301_operatiuni WHERE nr_doc = \'FE-E2E-179\'' % s)
    _detaliu_fiscal(patron, FIRMA_IC_NEPLATITOARE)
    patron.captura("neplatitoare_comuna", intreaga=True)
    assert "D390 față de D300 depus: nu se aplică — firma nu e plătitoare de TVA" in patron.fereastra()


def test_def_195_nu_se_aplica_si_fara_declarant(patron, firma_e2e):
    """195. Control fiscal: pe o firmă fără declarant, rândul „D390 față de D300: nu se aplică” lipsește; în locul lui apare „D390 nu se
    poate genera: lipsă declarant”.
    Pașii: firmă nouă, neplătitoare de TVA, fără declarant în Date firmă -> Control fiscal: „D390 față de D300 depus: nu se aplică —
    firma nu e plătitoare de TVA” e pe ecran, chiar dacă D390 nu se poate calcula."""
    s = firma_e2e["schema"]
    vechi = sql('SELECT platitor_tva, declarant_nume FROM "%s".firma_profil WHERE id = 1' % s)[0]
    sql('UPDATE "%s".firma_profil SET platitor_tva = false, declarant_nume = NULL WHERE id = 1' % s)
    try:
        _detaliu_fiscal(patron, firma_e2e["nume"])
        text = patron.fereastra()
        patron.captura(intreaga=True)
    finally:
        sql('UPDATE "%s".firma_profil SET platitor_tva = %%s, declarant_nume = %%s WHERE id = 1' % s, tuple(vechi))
    assert "D390 față de D300 depus: nu se aplică — firma nu e plătitoare de TVA" in text, text[-2500:]


def test_def_196_d390_dinaintea_preluarii_isi_pastreaza_faptul(patron):
    """196. Control fiscal: rândurile D390 dinaintea preluării pierd faptul pe care se sprijină (de ex. „operațiuni intracomunitare
    înregistrate în 06/2026”) — au doar motivul generic al preluării, deși faptul e în răspunsul serverului.
    Pașii: „Achizitii IC Neplatitor SRL” (preluată în 08/2026, achiziții intracomunitare în 06/2026) -> Control fiscal -> „Înainte de
    preluare”: rândul D390 06/2026 spune „operațiuni intracomunitare înregistrate în 06/2026”."""
    pg = patron.pg
    _detaliu_fiscal(patron, FIRMA_IC_NEPLATITOARE)
    pg.click(_fata(pg) + " details.cf-inainte > summary")
    rand = _fata(pg) + " details.cf-inainte .cf-decl-item[data-cheie='d390-2026-6']"
    pg.wait_for_selector(rand, timeout=30000)
    txt = pg.inner_text(rand)
    patron.captura()
    assert "operațiuni intracomunitare înregistrate în 06/2026" in txt, txt


def test_def_197_blocheaza_luna_inactiv_cat_timp_ceva_opreste_inchiderea(patron):
    """197. Închidere lună: „Blochează luna” e activ deși „Ce oprește închiderea” are un blocaj (22 de ciorne pe Comert Micro TVA).
    Pașii: „Comert Micro TVA SRL” -> Închidere lună -> pe luna curentă și pe cele două dinainte: oriunde „Ce oprește închiderea” are
    ceva, „Blochează luna” e inactiv și spune de ce — și rămâne inactiv după ce ecranul s-a terminat de desenat."""
    pg = patron.pg
    patron.firma(FIRMA_TVA)
    pg.click("#fa-inchidere")
    pg.wait_for_selector(_fata(pg) + " #il-prev", timeout=30000)
    gata = ("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); const z = f.querySelector('#il-controale');"
            " return z && z.querySelector('.caseta-info, .caseta-atentie'); }")
    vazute = []
    for i in range(3):
        pg.wait_for_function(gata, timeout=90000)
        pg.wait_for_timeout(1500)   # ce se mai desenează după controale (dreptul, legarea blocării) a avut timp să ruleze
        st = pg.evaluate("""() => { const f = [...document.querySelectorAll('.fereastra')].pop(); const b = f.querySelector('#il-lock');
          const z = f.querySelector('#il-controale');
          return {luna: f.querySelector('.pf-intro').innerText.slice(0, 40), blocaj: !!z.querySelector('.caseta-atentie'),
                  activ: !!b && b.isConnected && !b.disabled && !b.hidden && b.offsetParent !== null, text: b ? b.innerText : null}; }""")
        vazute.append(st)
        if i < 2:
            pg.click(_fata(pg) + " #il-prev")
            pg.wait_for_timeout(300)
    patron.captura()
    assert any(v["blocaj"] for v in vazute), ("anti-vacuu: nicio lună cu blocaj", vazute)
    assert not [v for v in vazute if v["blocaj"] and v["activ"] and "Deblochează" not in (v["text"] or "")], vazute
    # al doilea loc al butonului: antetul Registrului jurnal, pe luna curentă
    azi = _azi()
    st, r = _api(patron, "/tenants/%s/perioade-blocate?an=%d&luna=%d" % (_tenant(FIRMA_TVA)[0], azi.year, azi.month))
    patron.firma(FIRMA_TVA)
    pg.click("#fa-jurnal")
    pg.wait_for_selector(_fata(pg) + " #j-lock", timeout=30000)
    pg.wait_for_timeout(1500)
    j = pg.evaluate("() => { const b = [...document.querySelectorAll('.fereastra')].pop().querySelector('#j-lock'); return b ? {text: b.innerText, dez: b.disabled} : null; }")
    patron.captura("jurnal")
    if j and (r.get("controale") or {}).get("blocaje") and "Deblochează" not in j["text"]:
        assert j["dez"], (j, r["controale"]["blocaje"][:2])


# ── 180 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def test_def_180_inainte_de_preluare_rand_cu_perioada_termen_si_buton(patron):
    """180. Control fiscal: D100/D406/D205 înainte de preluare — termen fără dată, fără perioadă, fără buton.
    Pașii contabilului: Control fiscal -> „Achizitii IC Neplatitor SRL” (preluată în 08/2026) -> deschide „Înainte de preluare” ->
    fiecare rând D100 / D406 / D205 are perioada, termenul cu dată și butonul lui „Marchează depusă în afara iConta.eu”."""
    pg = patron.pg
    _detaliu_fiscal(patron, FIRMA_IC_NEPLATITOARE)
    grup = _fata(pg) + " details.cf-inainte"
    pg.click(grup + " > summary")
    randuri = pg.eval_on_selector_all(grup + " .cf-decl-item", """es => es.map(e => ({cheie: e.dataset.cheie,
        tip: (e.querySelector('.mig-sold-cont') || {}).innerText, perioada: (e.querySelector('.cf-perioada') || {}).innerText || '',
        termen: (e.querySelector('.cf-termen') || {}).innerText || '', buton: !!e.querySelector('.cf-extern-btn')}))""")
    patron.captura(intreaga=True)
    vazute = {}
    for r in randuri:
        if r["tip"] in ("D100", "D406", "D205"):
            vazute.setdefault(r["tip"], []).append(r)
            assert r["perioada"].strip(), "rând fără perioadă: %s" % r
            assert re.fullmatch(r"termen \d{2}\.\d{2}\.\d{4}", r["termen"].strip()), "rând fără dată de termen: %s" % r
            assert r["buton"], "rând fără butonul de marcare: %s" % r
    assert set(vazute) == {"D100", "D406", "D205"}, "lipsesc din grup: %s" % ({"D100", "D406", "D205"} - set(vazute))
    d205 = [r for r in vazute["D205"] if r["cheie"] == "d205-2025-12"]
    assert d205 and d205[0]["perioada"] == "2025" and d205[0]["termen"] == "termen 02.03.2026", d205


# ── 181 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def test_def_181_inchiderea_lunii_avertizeaza_declaratiile_lunii_nedepuse(patron, firma_e2e):
    """181. Închidere lună: fără avertisment pentru declarații nedepuse cu termen în lună.
    [retestul Costin 09.10, cuvânt cu cuvânt] „pe F2 09/2026 nu apare avertismentul pentru declarațiile nedepuse.” Situația F2: plătitoare
    de TVA cu decont trimestrial, impozit pe profit, preluată în luna închisă; declarațiile perioadei care se încheie cu luna închisă
    (D300 / D394 / D406 pe T3/2026) au termenul în luna URMĂTOARE, deci regula „termen în lună” nu le vedea — nimic nu avertiza la
    închidere. Pașii: firma cu acest profil -> Închidere lună -> luna trecută -> sub „Semnale” apare fiecare declarație nedepusă a
    perioadei care se încheie cu luna, cu perioada și termenul ei; nu e printre ce oprește închiderea.
    [testul vechi trecea pe defect: căuta numai o declarație cu termen în lună, pe o firmă care avea una]"""
    tid, pg = firma_e2e["tenant_id"], patron.pg
    luna_inch = _azi().replace(day=1) - _dt.timedelta(days=1)
    patron.acasa()
    st, r = _api(patron, "/tenants/%d/vector" % tid, "POST",
                 {"regim_fiscal": "profit", "platitor_tva": True, "operatiuni_ic": False, "inreg_art317": False,
                  "tip_decont": "trimestrial" if luna_inch.month % 3 == 0 else "lunar", "tva_data_inceput": "2025-01-01"})
    assert st == 200 and (r or {}).get("ok") is not False, (st, r)
    st, r = _api(patron, "/tenants/%d/firma-profil/date" % tid, "POST", {"luna_preluare": luna_inch.strftime("%Y-%m")})
    assert st == 200, (st, r)
    st, d = _api(patron, "/control-fiscal/%s" % tid)
    assert st == 200, st
    ale_lunii = [x for x in (d.get("lipsa") or []) + (d.get("urmarit") or [])
                 if (x.get("an"), x.get("luna")) == (luna_inch.year, luna_inch.month)]
    assert any(x["tip"] == "d300" for x in ale_lunii), ("profilul F2 n-a produs D300-ul perioadei", d.get("urmarit"), d.get("lipsa"))
    patron.firma(firma_e2e["nume"])
    pg.click("#fa-inchidere")
    pg.wait_for_selector(_fata(pg) + " #il-prev", timeout=30000)
    gata = ("(l) => { const f = [...document.querySelectorAll('.fereastra')].pop(); const z = f.querySelector('#il-controale');"
            " return f.querySelector('.pf-intro').innerText.includes('Luna ' + l) && z && z.querySelector('.caseta-info, .caseta-atentie'); }")
    azi = _dt.date.today()
    pg.wait_for_function(gata, arg="%02d/%d" % (azi.month, azi.year), timeout=90000)
    pg.click(_fata(pg) + " #il-prev")
    pg.wait_for_function(gata, arg=luna_inch.strftime("%m/%Y"), timeout=90000)
    patron.captura()
    zona = pg.inner_text(_fata(pg) + " #il-controale")
    semnale = zona.split("Semnale (", 1)[1] if "Semnale (" in zona else ""
    for x in ale_lunii:
        t = _dt.date.fromisoformat(x["termen"][:10]).strftime("%d.%m.%Y")
        fraza = "%s pentru %s, cu termen pe %s, nu e depusă" % (x["tip"].upper(), x["perioada"], t)
        assert fraza in semnale, "lipsește semnalul „%s” în: %s" % (fraza, zona)
        assert fraza not in zona.split("Semnale (", 1)[0], "declarația nedepusă blochează închiderea: %s" % zona


def test_def_172_control_fiscal_vorbeste_limba_contabilului(patron, firma_e2e):
    """172. Texte: limbajul de programator a rămas (incasare_client, plata_furnizor, liniara, sold initial, Rezumat D406, „decizia Costin”).
    [partea rămasă, registrul: „Încă în textele care ajung pe ecran în Control fiscal … «(rânduri persistate) … -> nimic de comparat.
    GRI, nu roșu.», «-> nu am ce confrunta. GRI, nu roșu», limitele «Verificat: D300 depus (rândurile persistate la depunere)» și
    «Verificat: totalurile din XML-ul D112 (cod 602/412+458/432+459/480)» … Verificat în cod, nu în browser.”] Pașii: firmă plătitoare
    de TVA, cu impozit pe profit, fără nicio declarație depusă prin aplicație (ramura „nu am cu ce compara”) -> Control fiscal, cu
    toate grupurile deschise -> textul ferestrei, judecat cu regulile ecranului (`core/limba_ecran.py`), nu are jargon de
    programator, săgeți sau stări interne („GRI”, „rânduri persistate”, „->”); „Nu există o perioadă cu ambele declarații depuse”
    apare (ramura e chiar pe ecran)."""
    from core import limba_ecran
    from e2e_bloc_e import _completeaza
    tid, pg = firma_e2e["tenant_id"], patron.pg
    _completeaza(firma_e2e, "global_valoric")   # Date firmă complete: declarațiile se pot genera, deci verificările chiar rulează
    patron.acasa()
    st, r = _api(patron, "/tenants/%d/vector" % tid, "POST", {"regim_fiscal": "profit", "platitor_tva": True, "operatiuni_ic": True,
                 "inreg_art317": True, "tip_decont": "lunar", "tva_data_inceput": "2025-01-01"})
    assert st == 200 and (r or {}).get("ok") is not False, (st, r)
    # D300 depus prin aplicație pe luna trecută, fără rândurile salvate (o depunere de dinainte ca aplicația să le păstreze)
    luna = _azi().replace(day=1) - _dt.timedelta(days=1)
    sql("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, sursa, randuri) VALUES (%s, %s, %s, 'd300', 'iconta', NULL)",
        (tid, luna.year, luna.month))
    try:
        patron.firma(firma_e2e["nume"])
        pg.click("#fa-control")
        pg.wait_for_selector(_fata(pg) + " .cf-stare-mare", timeout=90000)
        pg.evaluate("() => [...document.querySelectorAll('.fereastra:last-of-type details')].forEach(d => { d.open = true; })")
        pg.wait_for_timeout(300)
        text = pg.inner_text(_fata(pg))
        patron.captura()
    finally:
        sql("DELETE FROM public.declaratii_depuse WHERE tenant_id = %s AND tip = 'd300'", (tid,))
    assert "D300 depus fără rândurile salvate — nu se poate compara." in text, text[-3000:]
    rele = [d for d in limba_ecran.defecte(text, date_excluse=(firma_e2e["nume"],)) if d[0] in ("cod", "jargon")]
    assert not rele, rele


def test_def_211_tva_fata_de_balanta_nu_se_aplica_la_neplatitor(patron):
    """211. Control fiscal, firmă neplătitoare de TVA: „TVA vs sold balanță” cu bulină verde; trebuie „nu se aplică”.
    Pașii: „Coafor Micro Neplatitor SRL” (neplătitoare de TVA) -> Control fiscal -> „Coerență TVA (balanță)”: spune „nu se aplică —
    firma nu e plătitoare de TVA”, fără bulină verde."""
    pg = patron.pg
    _detaliu_fiscal(patron, FIRMA_NEPLATITOARE)
    sect = pg.evaluate("""() => { const f = [...document.querySelectorAll('.fereastra')].pop();
      const t = [...f.querySelectorAll('.cf-grup-titlu')].find(x => x.textContent.trim().startsWith('Coerență TVA'));
      if (!t) return null; const d = t.nextElementSibling;
      return {text: d.innerText, verde: [...d.querySelectorAll('.cf-verif-dot')].length}; }""")
    patron.captura()
    assert sect and "nu se aplică" in sect["text"] and sect["verde"] == 0, sect


# ── 182 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def test_def_182_ciornele_proprii_se_vad_in_fereastra_de_validat(patron, firma_e2e):
    """182. Coadă: ciornele contabilului nu apar în nicio coadă.
    Pașii contabilului: scrie o notă (rămâne ciornă) pe firmă -> ecranul principal -> „De validat” -> la capătul ferestrei,
    „Notele tale în ciornă” arată firma, nota cu rulajul ei și starea („nevalidată, netrimisă”)."""
    patron.acasa()
    _nota(patron, firma_e2e["tenant_id"], "Ciornă proprie probă E2E 182", "75.00", document="Chitanța E2E-182")
    pg = patron.pg
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='validat'])")
    pg.wait_for_selector(_fata(pg) + " #val-ciorne .val-ciorne-firma", timeout=30000)
    zona = pg.inner_text(_fata(pg) + " #val-ciorne")
    pg.eval_on_selector(_fata(pg) + " #val-ciorne", "e => e.scrollIntoView()")
    patron.captura()
    assert zona.lower().startswith("notele tale în ciornă ("), zona
    bloc = [b for b in pg.eval_on_selector_all(_fata(pg) + " #val-ciorne .val-ciorne-firma", "es => es.map(e => e.innerText)")
            if firma_e2e["nume"] in b]
    assert bloc, "firma cu ciorna nu apare: %s" % zona
    assert "Ciornă proprie probă E2E 182 · rulaj 75,00 lei · nevalidată, netrimisă" in bloc[0], bloc[0]


# ── 183 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def test_def_183_planul_de_conturi_are_ecran_cu_cautare_analitic_si_stergere_pazita(patron, firma_e2e):
    """183. Plan de conturi: doar import, fără ecran.
    Pașii contabilului: firma -> „Plan de conturi” -> caută „4111” -> „Adaugă analitic” pe 4111 -> 4111.07 „Client probă E2E” ->
    „Adaugă”: analiticul apare sub sintetic; un analitic nefolosit se șterge; după o notă pe 4111.07, contul nu mai are „Șterge”."""
    pg = patron.pg
    tid = firma_e2e["tenant_id"]
    patron.firma(firma_e2e["nume"])
    pg.click("#fa-planconturi")
    f = _fata(pg)
    pg.wait_for_selector(f + " #pcf-lista .pf-frand", timeout=30000)
    pg.fill(f + " #pcf-cauta", "4111")
    pg.wait_for_selector(f + " #pcf-lista [data-simbol='4111'] [data-analitic='4111']", timeout=10000)
    pg.click(f + " #pcf-lista [data-analitic='4111']")
    assert pg.input_value(f + " #pcf-simbol") == "4111."
    pg.fill(f + " #pcf-simbol", "4111.07")
    pg.fill(f + " #pcf-denumire", "Client probă E2E")
    pg.click(f + " #pcf-adauga")
    pg.wait_for_selector(f + " #pcf-lista [data-simbol='4111.07']", timeout=20000)
    ordine = pg.eval_on_selector_all(f + " #pcf-lista .pf-frand", "es => es.map(e => e.dataset.simbol)")
    assert ordine.index("4111.07") == ordine.index("4111") + 1 or "4111" not in ordine, ordine
    assert "analitic" in pg.inner_text(f + " #pcf-lista [data-simbol='4111.07']")
    patron.captura("adaugat")
    # analitic nefolosit -> se șterge
    pg.fill(f + " #pcf-simbol", "4111.08")
    pg.fill(f + " #pcf-denumire", "Analitic de șters E2E")
    pg.click(f + " #pcf-adauga")
    pg.wait_for_selector(f + " #pcf-lista [data-simbol='4111.08'] [data-sterge]", timeout=20000)
    pg.click(f + " #pcf-lista [data-simbol='4111.08'] [data-sterge]")
    pg.click("#ca-ok")
    pg.wait_for_selector(f + " #pcf-lista [data-simbol='4111.08']", state="detached", timeout=20000)
    # analitic folosit într-o notă -> fără „Șterge”, iar serverul refuză ștergerea
    _nota(patron, tid, "Încasare pe analitic probă E2E 183", "40.00", debit="5311", credit="4111.07", document="Chitanța E2E-183")
    patron.firma(firma_e2e["nume"])
    pg.click("#fa-planconturi")
    f = _fata(pg)
    pg.wait_for_selector(f + " #pcf-lista .pf-frand", timeout=30000)
    pg.fill(f + " #pcf-cauta", "4111.07")
    pg.wait_for_selector(f + " #pcf-lista [data-simbol='4111.07']", timeout=10000)
    rand = f + " #pcf-lista [data-simbol='4111.07']"
    assert "folosit în note" in pg.inner_text(rand), pg.inner_text(rand)
    assert pg.locator(rand + " [data-sterge]").count() == 0, "contul folosit în note are „Șterge”"
    st, r = _api(patron, "/tenants/%s/plan-conturi/4111.07" % tid, "DELETE")
    assert st >= 400, "serverul a șters un cont folosit în note: %s %s" % (st, r)
    patron.captura("folosit")


def _plan(patron, firma_e2e, cauta):
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    pg.click("#fa-planconturi")
    f = _fata(pg)
    pg.wait_for_selector(f + " #pcf-lista .pf-frand", timeout=30000)
    pg.fill(f + " #pcf-cauta", cauta)
    pg.wait_for_timeout(300)
    return f


def test_def_218_sinteticele_legale_si_conturile_cu_sold_nu_se_sterg(patron, firma_e2e):
    """218. Plan de conturi: „Șterge” pe conturile sintetice din planul legal și pe conturi cu sold (1012). Sinteticele legale nu se
    șterg; niciun cont cu sold sau rulaj nu se șterge.
    Pașii: firma cu sold inițial pe 1012 -> Plan de conturi -> „1012” și „4111” (sintetice ale planului general): fără „Șterge”; un
    analitic nou, nefolosit și fără sold, are „Șterge” -> cererea directă de ștergere a lui 1012 e refuzată, cu motivul."""
    pg = patron.pg
    patron.acasa()   # sesiunea (sessionStorage) există numai pe pagina aplicației
    tid, s = firma_e2e["tenant_id"], firma_e2e["schema"]
    sql('INSERT INTO "%s".solduri_initiale (cont, sold_debitor, sold_creditor, data_referinta) VALUES (\'1012\', 0, 200, \'2026-01-01\')'
        % s)
    try:
        for an in ("4111.21", "4111.22"):
            st, r = _api(patron, "/tenants/%s/plan-conturi" % tid, "POST", {"simbol": an, "denumire": "Analitic 218"})
            assert st == 200, (st, r)
        sql('INSERT INTO "%s".solduri_initiale (cont, sold_debitor, sold_creditor, data_referinta) VALUES (\'4111.22\', 50, 0, '
            '\'2026-01-01\')' % s)
        f = _plan(patron, firma_e2e, "")
        stare = pg.evaluate("""(ss) => ss.map(x => { const r = document.querySelector(`#pcf-lista [data-simbol='${x}']`);
            return [x, !!r, !!(r && r.querySelector('[data-sterge]'))]; })""", ["1012", "4111", "611", "4111.21", "4111.22"])
        patron.captura("plan")
        # 611: sintetic legal fără sold, fără analitice și nefolosit — nu se șterge NUMAI fiindcă e în planul legal;
        # 4111.22: analitic al firmei, cu sold inițial — nu se șterge NUMAI fiindcă are sold
        assert stare == [["1012", True, False], ["4111", True, False], ["611", True, False], ["4111.21", True, True],
                         ["4111.22", True, False]], stare
        st, r = _api(patron, "/tenants/%s/plan-conturi/1012" % tid, "DELETE")
        assert st == 409 and "nu se poate șterge" in str(r), (st, r)
    finally:
        sql('DELETE FROM "%s".solduri_initiale WHERE cont IN (\'1012\', \'4111.22\')' % s)
        for an in ("4111.21", "4111.22"):
            _api(patron, "/tenants/%s/plan-conturi/%s" % (tid, an), "DELETE")


def test_def_219_cautarea_dupa_simbol_potriveste_inceputul(patron, firma_e2e):
    """219. Plan de conturi: căutarea „73” găsește și 473; căutarea după simbol potrivește începutul.
    Pașii: Plan de conturi -> caută „11” (planul are 117/1171, care încep cu 11, și 4111/5311/411, care îl conțin în interior —
    „73” nu mai discriminează: 731–738 au ieșit din plan, 05ba1345): în listă sunt numai conturile care încep cu 11; caută „clienți”:
    se caută în denumire."""
    pg = patron.pg
    f = _plan(patron, firma_e2e, "11")
    simboluri = pg.eval_on_selector_all(f + " #pcf-lista .pf-frand", "es => es.map(e => e.dataset.simbol)")
    patron.captura("cauta_11")
    assert "117" in simboluri and all(x.startswith("11") for x in simboluri), simboluri   # 4111 / 5311 nu
    pg.fill(f + " #pcf-cauta", "clienți")
    pg.wait_for_timeout(300)
    assert "4111" in pg.eval_on_selector_all(f + " #pcf-lista .pf-frand", "es => es.map(e => e.dataset.simbol)")


# ── 186 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _pdf_balanta(ecran, nume):
    pg = ecran.pg
    ecran.firma(nume)
    pg.click("#fa-balanta")
    pg.wait_for_selector(_fata(pg) + " #b-pdf", timeout=30000)
    with pg.expect_download(timeout=60000) as dl:
        pg.click(_fata(pg) + " #b-pdf")
    from pypdf import PdfReader
    return PdfReader(io.BytesIO(open(dl.value.path(), "rb").read())).pages[0].extract_text()


def test_def_186_pdf_balanta_cod_tva_cu_ro_la_platitor(patron):
    """186. Balanță: CUI fără „RO” în PDF la plătitor de TVA.
    Pașii contabilului: „Comert Micro TVA SRL” (plătitoare) -> Balanță de verificare -> „Descarcă PDF” -> antetul scrie „Cod TVA RO…”;
    la „Coafor Micro Neplatitor SRL” (neplătitoare) antetul scrie „CIF …”, fără RO (CF art.318 alin.(1))."""
    cui_p = "".join(ch for ch in _tenant(FIRMA_TVA)[2] if ch.isdigit())
    cui_n = "".join(ch for ch in _tenant(FIRMA_NEPLATITOARE)[2] if ch.isdigit())
    t1 = _pdf_balanta(patron, FIRMA_TVA)
    patron.captura("platitor")
    assert "Cod TVA RO%s" % cui_p in t1.replace("\n", " "), t1[:400]
    t2 = _pdf_balanta(patron, FIRMA_NEPLATITOARE)
    assert "CIF %s" % cui_n in t2.replace("\n", " ") and "RO%s" % cui_n not in t2, t2[:400]

