# -*- coding: utf-8 -*-
"""Lotul 11 — testele de capăt la capăt ale deficiențelor găsite de Code și reparate în lot: C85, C87, C98, C100 (DEFICIENTE.md: starea
„rezolvată” cere testul în browser, cu captura și mutația — `mut_lot11_c85.json`, `mut_lot11_c87.json`, `mut_lot11_c98.json`,
`mut_lot11_c100.json`).

Pe aplicația pornită de `scripts/e2e_poarta.py` din index, pe baza de TEST:
  · C85 — „Configurare emitere” deschisă din formularul facturii („Schimbă seria”) arată sistemul TVA la încasare: pașii testului 428
    (`e2e_lot11_d3.py`), refolosiți întregi, pe o firmă NOUĂ numai a lui;
  · C87 — Asistenți -> colegul -> „Vizualizează” -> „Declarații lucrate” arată declarația pe care colegul a pregătit-o;
  · C98 — „Primii pași” nu cad cu 500 când o firmă a cabinetului e ștearsă în timpul cererii: cererea e prinsă exact între verificarea
    tabelului firmei și citirea lui (o blocare ținută pe `solduri_initiale`, apoi ștergerea firmei pe aceeași tranzacție);
  · C100 — refuzul importului soldurilor pe parteneri și auditul de preluare spun soldul 401 la fel: „creditor 500,00 lei”, fără minus.
Date de pornire fără ecran: C98 — firma cabinetului nou creată pe drumul aplicației (`provision_tenant`, ca la 319) și ștearsă prin
ștergerea plasei (`curatenie.scoate`), pe tranzacția care ține blocarea; restul pe rutele ecranelor (`_api`). Temei: N/A — afișare și
robustețe (C85 citează CF art.282 alin.(3^1) lit.a prin testul 428).
"""
import contextlib
import io
import os
import re
import time

import pytest

from conftest import PREFIX_FIRMA, _db, cui_cu_control, firma_noua, sql
from e2e_bloc_a import _api, _asteapta, _ok, ecran_cont, emite_api, pregateste_firma
from e2e_bloc_d import _control_firma
from e2e_lot11_d3 import test_def_428_schimba_seria_arata_sistemul_tva_la_incasare as _pasii_428
from e2e_lot72_cont import _card as _card_inceput
from e2e_lot72_cont import _facut, cabinet_nou  # noqa: F401 — cabinet_nou: fixtura (cabinetul și firmele lui se scot la final)
from e2e_lot72_declaratii import ZI, _curata, _in_coada, _peste, _valideaza_notele

_F = ".fereastra:last-of-type "


@pytest.fixture()
def firma_proprie():
    """O firmă NOUĂ numai pentru un test (`conftest.firma_noua`, scoasă la final): numerotarea, regimul TVA la încasare și soldurile
    preluate ale unui test nu au voie să ajungă la altul."""
    for f in firma_noua():
        yield f


# ── C85 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c85_schimba_seria_arata_sistemul_tva_la_incasare(patron, firma_proprie):
    """C85. „Configurare emitere” deschisă din formularul facturii („Schimbă seria”) arăta numai „Regim TVA: plătitoare de TVA (din
    profilul firmei).”, fără sistemul TVA la încasare: `emitere_ecran.js` cheamă `configureazaNumerotare` pe două drumuri, iar al doilea
    (butonul „Schimbă seria”) nu primea `tvaIncasare`.
    Pașii contabilului (cei ai testului 428, refolosiți întregi): Date firmă + numerotarea configurată -> Date firmă -> „Aplică sistemul
    TVA la încasare”: Da, de la prima zi a lunii viitoare -> Salvează -> Facturi -> „Emite factură” -> „Schimbă seria”. Se verifică pe
    fereastra „Configurare emitere”: regimul firmei (plătitoare) ȘI sistemul TVA la încasare, cu data de la care se aplică.
    MUTAȚIE (`mut_lot11_c85.json`): `opt.tvaIncasare` scos din formular -> rândul revine la „plătitoare de TVA (din profilul firmei).”."""
    _pasii_428(patron, firma_proprie)          # pașii + aserțiunea „TVA la încasare de la 01.LL.AAAA … azi nu se aplică”
    regim = " ".join(patron.pg.inner_text(_F + "#em-config-regim").split())
    patron.captura("regimul_din_schimba_seria")
    assert regim.startswith("Regim TVA: plătitoare de TVA"), regim
    assert regim != "Regim TVA: plătitoare de TVA (din profilul firmei).", "C85: fără sistemul TVA la încasare"
    assert re.search(r"TVA la încasare de la \d{2}\.\d{2}\.\d{4}", regim), regim


# ── C87 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
ACTIVITATE = """() => [...document.querySelectorAll('.fereastra:last-of-type #asi-activitate .asi-act-rand')].map((r) => ({
    tip: (r.querySelector('.asi-act-tip') || {}).innerText || '', meta: (r.querySelector('.asi-act-meta') || {}).innerText || ''}))"""


def test_def_c87_declaratii_lucrate_arata_declaratia_pregatita_de_coleg(patron, asistent, firma_e2e):
    """C87. Asistenți -> coleg -> „Vizualizează” -> „Declarații lucrate” era goală pe orice cabinet („Nicio activitate înregistrată.”),
    deci semnalul „patru ochi” nu se putea aprinde: `asistenti_api._identificatori` căuta lucrările după email și nume, iar coada scrie
    în `creat_de` id-ul omului (`str(uid)`).
    Pașii contabilului: contabilul-șef emite o factură în luna încheiată și îi validează nota; îi dă asistentei firma (ruta ecranului
    Asistenți); asistenta trimite D300 pe luna încheiată în coadă (ruta „Trimite în coadă”) -> contabilul-șef: pagina principală ->
    Asistenți -> rândul asistentei -> „Vizualizează”: la „Declarații lucrate” e declarația, pe firma ei, cu rolul „pregatit”.
    MUTAȚIE (`mut_lot11_c87.json`): id-ul scos din `_identificatori` -> lista e iar goală."""
    pregateste_firma(patron, firma_e2e)
    tid = firma_e2e["tenant_id"]
    uid_a, prenume, nume, email = sql("SELECT id, prenume, nume, email FROM public.users WHERE email = 'asistent@prisma-cont.test'")[0]
    nume_rand = " ".join(x for x in (prenume, nume) if x) or email          # cum îl scrie lista Asistenți (`randActor`)
    peste = _peste()
    try:
        f1 = emite_api(patron, firma_e2e, data_emitere=ZI)
        _valideaza_notele(patron, firma_e2e, f1["factura_id"])
        _ok(_api(patron, "POST", "/asistenti/%d/firme/%d" % (uid_a, tid), {}), "alocarea firmei")
        r = _in_coada(asistent, firma_e2e)
        assert r["status"] == 200, r
        pg = patron.pg
        patron.acasa()
        pg.click("button.cab-card:has([data-cheie='asistenti'])")
        pg.wait_for_selector("#asi-lista .val-card", timeout=30000)
        al_ei = pg.locator(".asi-nume").filter(has_text=re.compile(r"^\s*%s\s*$" % re.escape(nume_rand)))   # numele întreg, nu un sub-șir
        pg.locator("#asi-lista .val-card", has=al_ei).first.locator("[data-act='vezi']").click()
        pg.wait_for_selector(_F + "#asi-activitate", timeout=30000)
        pg.wait_for_timeout(300)
        randuri = pg.evaluate(ACTIVITATE)
        lista = " ".join(pg.inner_text(_F + "#asi-activitate").split())
        pg.locator(_F + "#asi-activitate").scroll_into_view_if_needed()
        patron.captura("declaratii_lucrate")
        assert lista != "Nicio activitate înregistrată.", "C87: „Declarații lucrate” goală, deși asistenta a pregătit D300"
        ale_firmei = [x for x in randuri if x["meta"].startswith(firma_e2e["nume"] + " · ")]
        assert len(ale_firmei) == 1, randuri
        assert ale_firmei[0]["meta"].split(" · ")[1] == "a pregătit", ale_firmei   # ea a pregătit-o; n-a validat-o, n-a respins-o (C87.1: cu diacritice)
        assert "300" in ale_firmei[0]["tip"], ale_firmei
    finally:
        _curata(firma_e2e, peste)
        sql("DELETE FROM public.user_tenants WHERE user_id = %s AND tenant_id = %s", (uid_a, tid))


# ── C98 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
class _PeTranzactiaBlocarii:
    """`db` pentru `curatenie.scoate` (ștergerea firmelor plasei — o singură definiție), pe conexiunea care ține deja blocarea: ștergerea
    și blocarea sunt aceeași tranzacție, deci cererea blocată vede firma ștearsă în clipa în care blocarea se ridică."""

    def __init__(self, conn, db):
        self._conn, self.schema_valida = conn, db.schema_valida

    def get_conn(self):
        return contextlib.nullcontext(self._conn)


def _cererea_asteapta_balanta(schema):
    """O cerere a aplicației a verificat că tabelul balanței firmei există și așteaptă acum să-l citească (`repo_inceput.preluare_facuta`:
    `SELECT EXISTS (SELECT 1 FROM "<schema>".solduri_initiale)`): blocare neacordată pe tabel, cu interogarea ei."""
    return sql("SELECT count(*) FROM pg_locks l JOIN pg_stat_activity a ON a.pid = l.pid WHERE NOT l.granted AND l.relation = "
               "to_regclass(%s) AND a.query LIKE %s", ('"%s".solduri_initiale' % schema, "%EXISTS%solduri_initiale%"))[0][0] > 0


def test_def_c98_primii_pasi_nu_cad_cand_firma_e_stearsa_in_timpul_cererii(browser, request, cabinet_nou):
    """C98. „Primii pași” (`/eu/inceput`) cădea cu 500 când o firmă a cabinetului era ștearsă în timpul cererii: `preluare_facuta` vedea
    tabelul firmei (`to_regclass`), apoi îl citea după ce schema dispăruse — UndefinedTable (găsit în plasa din 22.10.2026, de 3 ori în
    uvicorn.log, când curățenia altui test ștergea firma lui).
    Pașii administratorului unui cabinet nou, cu o singură firmă: pagina principală -> „Primii pași” (trei carduri, nefăcute) -> „Lucrez
    singur” pe cardul „Adaugă echipa”, iar cererea lui, care recitește cardurile, ajunge la balanța firmei exact când firma e ștearsă ->
    cardul „Adaugă echipa” devine verde, „Adu firmele” rămâne nefăcut (firma nu mai e a cabinetului), niciun mesaj de eroare, nicio cerere
    5xx. Cum se prinde clipa: o tranzacție a testului ține blocarea pe `solduri_initiale` al firmei; cererea verifică tabelul (fără
    blocare), apoi așteaptă s-o citească; testul șterge firma pe aceeași tranzacție și o comite — cererea găsește tabelul dispărut.
    MUTAȚIE (`mut_lot11_c98.json`): ramura `UndefinedTable` din `preluare_facuta` scoasă -> „Lucrez singur” răspunde 500."""
    from core import tenant_provisioning as tp
    import curatenie
    db = _db()
    rad = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    with db.get_conn() as c:
        t = tp.provision_tenant(c, PREFIX_FIRMA + " C98 SRL", cui_cu_control(70000000 + int(time.time()) % 9000000),
                                cabinet_nou["firm_id"], cabinet_nou["uid"], io.open(os.path.join(rad, "tenant_template.sql"),
                                                                                    encoding="utf-8").read())
        c.commit()
    tid, s = t["tenant_id"], t["schema_name"]
    os.makedirs(os.path.dirname(curatenie.registru_firme()), exist_ok=True)
    with open(curatenie.registru_firme(), "a") as fr:          # rulatorul o scoate încă o dată după oprirea aplicației
        fr.write("%s %s\n" % (tid, s))
    with ecran_cont(browser, request, cabinet_nou["email"]) as e:
        pg = e.pg
        e.acasa()
        pg.wait_for_selector(_card_inceput(pg, "echipa") + " [data-inceput='lucrez_singur']", timeout=30000)
        pg.wait_for_timeout(1000)                                # cererile paginii (și citirea cardurilor) s-au încheiat
        assert not any(_facut(pg, k) for k in ("preluare", "anaf", "echipa"))
        e.captura("inainte")
        with db.get_conn() as h, h.cursor() as cur:
            cur.execute("SET LOCAL lock_timeout = '20s'")
            # date-de-pornire: blocarea (nu o scriere) care ține cererea între verificarea tabelului firmei și citirea lui
            cur.execute('LOCK TABLE "%s".solduri_initiale IN ACCESS EXCLUSIVE MODE' % s)
            pg.click(_card_inceput(pg, "echipa") + " [data-inceput='lucrez_singur']")
            _asteapta(lambda: _cererea_asteapta_balanta(s), 30)
            # date-de-pornire: firma ștearsă cum o șterge plasa (`curatenie.scoate`), pe tranzacția blocării; comite și ridică blocarea
            curatenie.scoate(_PeTranzactiaBlocarii(h, db), [(tid, s)])
        assert sql("SELECT count(*) FROM public.tenants WHERE id = %s", (tid,))[0][0] == 0, "firma n-a fost ștearsă"
        pg.wait_for_function("([s, m]) => (document.querySelector(s) || {className: ''}).className.includes('inceput-facut')"
                             " || !!(document.querySelector(m) || {innerText: ''}).innerText.trim()",
                             arg=[_card_inceput(pg, "echipa"), "#inceput-msg"], timeout=30000)
        pg.wait_for_timeout(500)
        mesaj = pg.inner_text("#inceput-msg").strip() if pg.locator("#inceput-msg").count() else ""
        e.captura("dupa_stergere")
        assert not e.cereri_rele, "C98: „Primii pași” au căzut cu 5xx: %s" % e.cereri_rele[:3]
        assert mesaj == "", "C98: mesaj de eroare pe cardurile de început: %s" % mesaj
        assert _facut(pg, "echipa"), "„Lucrez singur” n-a bifat cardul „Adaugă echipa”"
        assert not _facut(pg, "preluare"), "firma ștearsă nu face preluarea"


# ── C100 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c100_soldul_creditor_se_spune_cu_felul_lui_la_import_si_la_audit(patron, firma_proprie):
    """C100. Auditul de preluare spunea soldul creditor cu semn („Contul 401: parteneri 0,00 lei vs balanță -500,00 lei”), iar refuzul
    importului aceluiași cont spunea „creditor 500,00 lei”: contabilul vedea un sold negativ pe 401. Acum amândouă trec prin
    `pdf_util.sold`: „debitor / creditor X lei” (zero: „0,00 lei”).
    Pașii contabilului: firma preluată luna aceasta, cu balanța de deschidere (4111 debit 1.000, 401 credit 500, 5311 debit 300, 1012
    credit 800; rutele Migrării) -> fereastra firmei -> Import date -> Solduri parteneri -> fișierul (clientul 1.000 pe 4111, furnizorul
    400 pe 401) -> Salvează: „Un partener salvat.”, iar rândul 401 nu intră, cu „partenerii din fișier dau creditor 400,00 lei, iar
    balanța de deschidere … are creditor 500,00 lei” -> Control fiscal -> firma -> „Rulează auditul de preluare”: „Contul 401: parteneri
    0,00 lei vs balanță creditor 500,00 lei (diferență 500,00 lei)” și „Contul 4111: defalcarea pe parteneri (debitor 1.000,00 lei)
    coincide cu balanța.”. Niciun sold cu minus, pe niciunul din ecrane.
    MUTAȚIE (`mut_lot11_c100.json`): `_lei` repus pe soldul balanței în `audit_preluare.constatare_parteneri` -> „balanță -500,00 lei”."""
    import datetime as _dt
    f = firma_proprie
    tid = f["tenant_id"]
    pregateste_firma(patron, f)
    luna = _dt.date.today().replace(day=1)
    data_ref = luna - _dt.timedelta(days=1)                    # ultima zi a lunii dinaintea preluării
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % tid, {"luna_preluare": luna.strftime("%Y-%m")}), "luna preluării")
    _ok(_api(patron, "POST", "/tenants/%d/solduri" % tid, {"data_referinta": data_ref.isoformat(), "randuri": [
        {"cont": "4111", "debit": 1000}, {"cont": "401", "credit": 500}, {"cont": "5311", "debit": 300}, {"cont": "1012", "credit": 800}]}),
        "balanța de deschidere")
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-import")
    pg.wait_for_selector(".mig-frand", timeout=20000)
    pg.locator(".mig-frand", has_text="Solduri parteneri").first.click()
    pg.wait_for_selector("#mig-file", state="attached", timeout=10000)
    fisier = ("cont;cui;denumire;sold debitor;sold creditor\n4111;%s;CLIENT C100 SRL;1000;0\n401;%s;FURNIZOR C100 SRL;0;400\n"
              % (cui_cu_control(31100001), cui_cu_control(31100002)))
    pg.set_input_files("#mig-file", files=[{"name": "parteneri.csv", "mimeType": "text/csv", "buffer": fisier.encode("utf-8")}])
    pg.wait_for_selector("#mig-salveaza-part", timeout=30000)
    patron.captura("previzualizare")
    pg.click("#mig-salveaza-part")
    if pg.locator("#ca-ok").count():
        pg.click("#ca-ok")
    pg.wait_for_function("() => document.body.innerText.includes('Un partener salvat')", timeout=60000)   # nu „Salvez…” (butonul în lucru)
    refuz = " ".join(pg.inner_text("body").split())
    patron.captura("refuzul_401")
    assert "Un partener salvat." in refuz, refuz
    assert ("pe 401, partenerii din fișier dau creditor 400,00 lei, iar balanța de deschidere la %s are creditor 500,00 lei (diferență "
            "100,00 lei)" % data_ref.strftime("%d.%m.%Y")) in refuz, refuz
    _control_firma(patron, f)
    pg.wait_for_selector(_F + "#cf-audit-run", timeout=30000)
    pg.click(_F + "#cf-audit-run")
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #cf-audit-istoric') || {innerText: ''}).innerText"
                         ".includes('Primul audit după preluare')", timeout=60000)
    audit = " ".join(pg.inner_text(_F + "#cf-audit-istoric").split())
    pg.locator(_F + "#cf-audit-zona").scroll_into_view_if_needed()
    patron.captura("auditul")
    assert "Contul 401: parteneri 0,00 lei vs balanță creditor 500,00 lei (diferență 500,00 lei)." in audit, audit   # ca refuzul
    assert "Contul 4111: defalcarea pe parteneri (debitor 1.000,00 lei) coincide cu balanța." in audit, audit
    assert not re.search(r"-\s?\d[\d.]*,\d\d lei", audit), "C100: sold cu minus în auditul de preluare: %s" % audit
