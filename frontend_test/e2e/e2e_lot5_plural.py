# -*- coding: utf-8 -*-
"""Lotul 5, comanda 3 (Costin 15.10.2026, verbatim în DECIZII „Lotul 5 — comanda 3”), pct.2d: „261, 263 și «1 angajați» din Panou Admin →
Cabinete: plural fix după număr («1 note», «1 facturi»). Corectezi clasa peste tot.”

261 = Registrul jurnal: „Luna 10/2026 · 1 note”. 263 = „1 facturi”: rândul cabinetului din Panou Admin → Cabinete („1 facturi emise”),
același rând cu „1 angajați”, și bara superadminului care le adună. Pe fiecare: o situație cu exact 1 (date reale, puse pe drumul
aplicației), apoi 20 și peste („20 de note”, „21 de facturi emise”). Numeralul îl acordă un singur helper (`static/js/plural.js::cate`,
oglinda lui `core/common.py::cate`, gard `core/test_plural_dupa_numar.py`); testul compară cu `common.cate`, nu cu un text scris aici.
Pe aplicația din index, pe baza de TEST."""
import datetime
import json
import os
import re
import sys

import pytest

from conftest import BAZA, _ecran, _scoate_firmele_e2e, firma_noua, sql

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_bloc_d import PATRON, _api   # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.common import cate   # noqa: E402

SUPERADMIN = "admin@prisma-cont.test"
CABINET = "E2E Plural Cabinet Probă"
EMAIL_ANGAJAT = "e2e.plural.angajat@exemplu.ro"


@pytest.fixture()
def superadmin(browser, request):
    yield from _ecran(browser, request, SUPERADMIN)


# ── 261: Registrul jurnal ──────────────────────────────────────────────────────────────────────────────────────────────────────
def _nota(tid, i):
    st, r = _api(PATRON, "POST", "/tenants/%d/jurnal" % tid, {
        "data": datetime.date.today().isoformat(), "descriere": "Probă plural %d" % i, "document_ref": "PL%d" % i,
        "linii": [{"debit": "6022", "credit": "5311", "suma": 10 + i}]})
    assert st == 200 and r.get("id"), (st, r)


def _intro_jurnal(e, nume):
    e.firma(nume)
    e.pg.click("#fa-jurnal")
    e.pg.wait_for_selector("#j-nota-noua", timeout=20000)
    luna = datetime.date.today().strftime("%m/%Y")
    intro = e.pg.locator(".fereastra p.pf-intro", has_text="Luna " + luna).last
    intro.wait_for(timeout=20000)
    return intro.inner_text()


def test_def_261_registrul_jurnal_acorda_numarul_notelor(patron, firma_e2e):
    """261. Registrul jurnal, o firmă cu o singură notă în lună: antetul spune „Luna 10/2026 · 1 notă” (era „1 note”); cu 20 de note,
    „20 de note” (era „20 note”). MUTAȚIE: `${cate(note.length, …)}` înapoi la `${note.length} note` -> „1 note” -> pică."""
    tid = firma_e2e["tenant_id"]
    _nota(tid, 0)
    t = _intro_jurnal(patron, firma_e2e["nume"])
    assert "· %s" % cate(1, "notă", "note") in t and "1 note" not in t, t
    patron.captura("o_nota")
    for i in range(1, 20):
        _nota(tid, i)
    t = _intro_jurnal(patron, firma_e2e["nume"])
    assert "· %s" % cate(20, "notă", "note") in t, t          # „20 de note”
    assert not re.search(r"\b20 note\b", t), t
    patron.captura()


# ── 263 și „1 angajați”: Panou Admin → Cabinete ───────────────────────────────────────────────────────────────────────────────
def _curata_cabinet():
    uids = [r[0] for r in sql("SELECT id FROM public.users WHERE email = %s", (EMAIL_ANGAJAT,))]
    if uids:
        sql("DELETE FROM public.audit_log WHERE user_id = ANY(%s)", (uids,))
        sql("DELETE FROM public.users WHERE id = ANY(%s)", (uids,))
    sql("DELETE FROM public.accounting_firms WHERE nume = %s", (CABINET,))


@pytest.fixture()
def cabinet_cu_cate_unul():
    """Un cabinet sintetic cu exact: 1 firmă, 1 angajat activ, 1 factură emisă, 1 declarație depusă, 1 recomandare — numărate de
    `repo_admin.activitate_pe_cabinete` din tabelele lor (firma = o firmă nouă pe drumul aplicației, mutată la cabinetul sintetic;
    acțiunile = rândurile din jurnalul de audit pe care le scrie middleware-ul la emitere, depunere, recomandare)."""
    _curata_cabinet()
    gen = firma_noua()
    firma = next(gen)
    (patron_cab,) = sql("SELECT accounting_firm_id FROM public.tenants WHERE id = %s", (firma["tenant_id"],))[0]
    try:
        (cab,) = sql("INSERT INTO public.accounting_firms (nume) VALUES (%s) RETURNING id", (CABINET,))[0]
        (uid,) = sql("INSERT INTO public.users (email, password_hash, rol, activ, accounting_firm_id) VALUES (%s, 'x', 'angajat', true, %s) "
                     "RETURNING id", (EMAIL_ANGAJAT, cab))[0]
        sql("UPDATE public.tenants SET accounting_firm_id = %s WHERE id = %s", (cab, firma["tenant_id"]))
        for act in ("POST /tenants/%d/facturi/emite" % firma["tenant_id"], "POST /coada/1/depune", "POST /recomanda"):
            sql("INSERT INTO public.audit_log (actiune, user_id, tenant_id) VALUES (%s, %s, %s)", (act, uid, firma["tenant_id"]))
        yield {"id": cab, "tenant_id": firma["tenant_id"]}
    finally:
        sql("UPDATE public.tenants SET accounting_firm_id = %s WHERE id = %s", (patron_cab, firma["tenant_id"]))
        _curata_cabinet()
        _scoate_firmele_e2e(firma["tenant_id"])


#: rândul cabinetului (Panou Admin → Cabinete) și bara superadminului: (câmpul din răspuns, singular, plural)
FORME = (("nr_firme", "firmă", "firme"), ("nr_angajati", "angajat", "angajați"), ("nr_facturi", "factură emisă", "facturi emise"),
         ("nr_declaratii", "declarație depusă", "declarații depuse"), ("nr_recomandari", "recomandare", "recomandări"))


def _cabinete(pg):
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-grila", timeout=30000)
    pg.click("button.cab-card:has([data-cheie='activitate'])")
    rand = pg.locator(".pf-frand", has_text=CABINET)
    rand.wait_for(timeout=60000)                                            # interogarea ia ~5 s pe baza de test
    return rand.locator(".pf-frand-sub").inner_text()


def _cu_numere(pg, cab_id, numere):
    """Răspunsul real al `/admin/activitate/cabinete`, cu numerele cabinetului sintetic înlocuite (20 și peste: atâtea facturi și
    declarații nu se fabrică într-un test) și numai el în listă (bara superadminului le adună pe toate)."""
    def h(route):
        r = route.fetch()
        d = r.json()
        d["cabinete"] = [dict(c, **numere) for c in d["cabinete"] if c["id"] == cab_id]
        route.fulfill(response=r, body=json.dumps(d), content_type="application/json")
    pg.route("**/admin/activitate/cabinete", h)


def test_def_263_panou_admin_cabinete_acorda_facturile_si_angajatii(superadmin, cabinet_cu_cate_unul):
    """263 și „1 angajați”. Panou Admin → Cabinete, un cabinet cu câte unul din fiecare: rândul spune „1 firmă · 1 angajat · 1 factură
    emisă · 1 declarație depusă · 1 recomandare” (era „1 firme · 1 angajați · 1 facturi emise · 1 declarații depuse · 1 recomandări”);
    cu 20, 21, 100, 101, 119: „20 de firme · 21 de angajați · 100 de facturi emise · 101 declarații depuse · 119 recomandări”. Bara
    superadminului (aceleași cifre, adunate) — la fel. MUTAȚIE: `cate(c.nr_angajati …)` înapoi la `${c.nr_angajati ?? 0} angajați` ->
    „1 angajați” -> pică."""
    pg = superadmin.pg
    sub = _cabinete(pg)
    for camp, s, p in FORME:
        assert cate(1, s, p) in sub, (camp, sub)
    assert not re.search(r"\b1 (?:firme|angajați|facturi|declarații|recomandări)\b", sub), sub
    superadmin.captura("cate_unul")

    numere = {"nr_firme": 20, "nr_angajati": 21, "nr_facturi": 100, "nr_declaratii": 101, "nr_recomandari": 119}
    _cu_numere(pg, cabinet_cu_cate_unul["id"], numere)
    sub = _cabinete(pg)
    for camp, s, p in FORME:
        assert cate(numere[camp], s, p) in sub, (camp, sub)
    bara = pg.locator("[data-sumar-admin]")
    pg.wait_for_function("() => /cabinet/.test((document.querySelector('[data-sumar-admin]') || {}).textContent || '')", timeout=30000)
    t = bara.inner_text()
    assert cate(1, "cabinet activ", "cabinete active") in t, t
    for camp, s, p in FORME:
        assert cate(numere[camp], s, p) in t, (camp, t)
    superadmin.captura()
