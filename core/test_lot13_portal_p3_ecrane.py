# -*- coding: utf-8 -*-
"""[lotul 13, comanda 13.1, subagentul PORTAL — partea Date firmă / SPV] Ecranele reale, în Chromium, cu rutele simulate (harness-ul din
`core/test_lot12_ui2_ecrane.py`: `navigator.js`, `date_firma.js`, `ecran_destinatie.js`, `spv_stare.js`, `stil.css` din arbore, la 1280×720).
Se măsoară ecranul, nu scrierea în bază (aceea o fac testele de logică `core/test_lot13_portal_p3_*.py` și e2e-ul
`frontend_test/e2e/e2e_lot13_portal_p3.py`).

Deficiențele, verbatim din comanda 13.1 (`~/ghid_incoming/comanda_13_1.txt`):
  525:   „Trimiteri între ferestre | «Deschide Date firmă» de la refuzul dividendelor deschide fereastra de la început, nu la secțiunea
          Asociați; după Salvează fereastra sare la început. Trimiterea duce la locul de completat, iar după salvare rămâi unde lucrai.”
  C71.1: „La F4 PFA caseta «Profil incomplet» cere corect doar Banca și IBAN, dar formularul marchează cu * câmpuri de SRL «cerute la
          bilanț» (Nr. registrul comerțului, Mare contribuabil, Forma de proprietate, Entitate de interes public) și oferă Regim fiscal
          micro/profit (D100/D101), care nu privesc un PFA.”
  661:   „Fereastra firmei / SPV | La F7 (CUI inventat) scrie «SPV: conectat»; conexiunea e a cabinetului, iar certificatul nu acoperă
          acest CUI. Trebuie spus dacă certificatul acoperă CUI-ul firmei (clasa 289).”
  541:   (partea de ecran) „Jurnalul perioadelor există (de la / până la / sursă / verificat ANAF), dar nu arată cine și când a schimbat, iar
          «Șterge» scoate perioada fără urmă.”

Mutațiile (raportul `l13_raport/portal_p3.md`): poziționarea pe câmpul cerut mutată înapoi înaintea tabelului asociaților / redesenarea
de după salvare fără `peLoc` (525); `*` din nou static (C71.1); ramura „neverificat” cu „SPV: conectat” (661); coloana „Cine / când”
scoasă (541) -> ROȘU.

Temei: 525 / C71.1 / 661 — N/A, reguli de interfață (CLAUDE.md §9; DS cap.6 v2.74 „Refuzul care trimite în alt ecran”, cap.9 v2.102
„fereastra rămâne pe loc”); C71.1 — excluderea prin formă din `control_fiscal_api.neaplicabile_forma` (Legea 82/1991 art.28 alin.(1), deja
citat acolo); 541 — CF art.282 alin.(3^1) lit.a), citat în `core/regim_tva_incasare.py`.
"""
import json

from core.test_lot12_ui2_ecrane import _pagina, browser  # noqa: F401 — fixture-ul harness-ului (Chromium + server static)


def _asociati(n=6):
    return {"asociati": [{"id": i, "nume": "Asociat %d" % i, "cnp": "", "cota": "10", "tip": ""} for i in range(1, n + 1)],
            "total_cota": "60", "valabila_de_la": None, "istoric": []}


def _profil(tip_firma="srl", **x):
    p = {"cui": "14399840", "cui_afisat": "14399840", "reg_com": "J40/1/2020", "caen": "6920", "adresa": "Str. Probă 1", "oras": "București",
         "judet": "B", "banca": "Banca Probă", "iban": "RO49AAAA1B31007593840000", "telefon": "0700000000", "declarant_nume": "Pop",
         "declarant_prenume": "Ion", "declarant_functie": "Administrator", "tip_firma": tip_firma, "cont_venit_implicit": "704",
         "luna_preluare": {}}
    p.update(x)
    return p


def _date(profil, **x):
    d = {"profil": profil, "lipsuri": [], "blocaje": [], "conturi_venit": {"704": "Venituri din servicii"}, "forme_juridice": [],
         "activitati_amef": [], "forme_proprietate": [["10", "Proprietate privată"]], "metode_stoc": [], "jurnal": []}
    d.update(x)
    return d


def _vector(tip_firma="srl", **x):
    v = {"ok": True, "regim_fiscal": None if tip_firma == "pfa" else "micro", "platitor_tva": True, "tip_decont": "lunar",
         "operatiuni_ic": False, "inreg_art317": False, "tva_data_inceput": "2020-01-01", "partida_simpla": tip_firma == "pfa",
         "completat": True, "tva_incasare": {"aplica_azi": False, "fara_data": False, "curenta": None, "perioade": [], "avertismente": []}}
    v.update(x)
    return v


def _rute(date, vector, asociati, cereri=None):
    """Toate cererile ferestrei Date firmă printr-o singură funcție (calea întreagă decide; `_pagina` potrivește pe sufix)."""
    def t(metoda, cale, _q, corp):
        if cereri is not None:
            cereri.append((metoda, cale, json.loads(corp) if corp else None))
        if cale.endswith("/firma-profil/date"):
            return date if metoda == "GET" else {"ok": True, "lipsuri": []}
        if cale.endswith("/vector"):
            return vector if metoda == "GET" else {"ok": True}
        if cale.endswith("/asociati"):
            return asociati if metoda == "GET" else dict(asociati, ok=True)
        if cale.rstrip("/").endswith("/tenants/1"):
            return {"id": 1, "nume": "Firma Probă SRL", "nume_anaf": "Firma Probă SRL"}
        return {}
    return {"/tenants": t}


_CORP = "() => [...document.querySelectorAll('.fereastra-corp')].pop()"
# elementul e în zona vizibilă a ferestrei (între marginile corpului ei, sub nimic din bara lipită de jos)
_IN_VEDERE = """(sel) => { const c = [...document.querySelectorAll('.fereastra-corp')].pop(), e = c.querySelector(sel);
  const r = e.getBoundingClientRect(), k = c.getBoundingClientRect(), b = c.querySelector('.bara-fixa');
  const jos = b ? Math.min(k.bottom, b.getBoundingClientRect().top) : k.bottom; return r.top >= k.top && r.bottom <= jos; }"""


def _deschide_din_refuz(pg, camp):
    """Ca butonul „Deschide Date firmă” al unui refuz (`ecran_destinatie.butonSpreEcran` -> `ECRANE.date_firma.deschide`), cu câmpul cerut
    de refuz (`detail.camp_ecran`, la dividende `as-adauga` — `core/mesaje.CAMP_ECRAN_PE_COD`)."""
    pg.evaluate("""async (camp) => { const d = await import('/static/js/ecrane/ecran_destinatie.js');
      window._nav.deschide('Operațiuni speciale', (c) => { c.innerHTML = '<h2>Operațiuni speciale</h2><p>formularul dividendului</p>'; });
      const z = document.createElement('div'); [...document.querySelectorAll('.fereastra-corp')].pop().appendChild(z);
      const b = d.butonSpreEcran(z, 'date_firma', window._nav, 1, { camp }); b.click(); }""", camp)
    pg.wait_for_selector("#df-salveaza", timeout=15000)
    pg.wait_for_timeout(600)   # cât lucrează observatoarele ferestrei (titlul, lățimea) și cadrele de animație


# ── 525 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_525_deschide_date_firma_din_refuz_duce_la_asociati(browser):
    """ROȘU înainte: câmpul cerut se aducea în vedere ÎNAINTE ca tabelul asociaților (și secțiunile ascunse ale vectorului) să se
    deseneze, deci „+ Asociat” ajungea sub fereastră; contabilul vedea capul ferestrei."""
    pg, erori = _pagina(browser, _rute(_date(_profil()), _vector(), _asociati()))
    try:
        _deschide_din_refuz(pg, "as-adauga")
        in_vedere = pg.evaluate(_IN_VEDERE, "#as-adauga")
        sus = pg.evaluate("() => (" + _CORP + ")().scrollTop")
    finally:
        pg.close()
    assert not erori, erori
    assert sus > 0 and in_vedere, (sus, in_vedere)


def test_def_525_dupa_salveaza_fereastra_ramane_unde_lucrai(browser):
    """ROȘU înainte: „Salvează” redesena fereastra prin „Se încarcă…”, deci derularea cădea la 0 — omul era dus la începutul ferestrei,
    departe de Asociați, unde lucra."""
    cereri = []
    pg, erori = _pagina(browser, _rute(_date(_profil()), _vector(), _asociati(), cereri))
    try:
        _deschide_din_refuz(pg, "as-adauga")
        inainte = pg.evaluate("() => (" + _CORP + ")().scrollTop")
        pg.click("#df-salveaza")
        pg.wait_for_function("() => /alvat/.test((document.querySelector('#df-msg') || {}).innerText || '')", timeout=15000)
        pg.wait_for_timeout(600)
        dupa = pg.evaluate("() => (" + _CORP + ")().scrollTop")
        in_vedere = pg.evaluate(_IN_VEDERE, "#as-adauga")
    finally:
        pg.close()
    assert not erori, erori
    assert any(m == "POST" and c.endswith("/firma-profil/date") for m, c, _b in cereri), cereri   # anti-vacuu: s-a salvat
    assert inainte > 0 and abs(dupa - inainte) < 40 and in_vedere, (inainte, dupa, in_vedere)


# ── C71.1 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _eticheta(pg, camp):
    """Eticheta + ajutorul câmpului din Date firmă (textul casetei lui), sau None dacă nu e pe ecran."""
    return pg.evaluate("""(id) => { const e = document.querySelector('#' + id); if (!e) return null;
      const l = e.closest('.camp'); return l ? l.innerText : ''; }""", camp)


def _date_firma_forma(browser, tip_firma):
    from core.firma_profil_api import campuri_forma   # ce trimite serverul pentru forma firmei (`citeste_date`)
    pg, erori = _pagina(browser, _rute(_date(_profil(tip_firma), **campuri_forma(tip_firma)), _vector(tip_firma), _asociati(2)))
    pg.evaluate("""async () => { const d = await import('/static/js/ecrane/date_firma.js');
      window._nav.deschide('Date firmă', (c, n) => d.randeazaDateFirma(c, n, 1)); }""")
    pg.wait_for_selector("#df-salveaza", timeout=15000)
    return pg, erori


def test_def_c71_1_pfa_fara_campurile_bilantului_si_fara_regim_micro_profit(browser):
    """ROȘU înainte: la PFA, „Nr. registrul comerțului *” („Cerut la bilanț.”), „Mare contribuabil *”, „Forma de proprietate *”,
    „Entitate de interes public *” și lista „Regim fiscal” cu micro / profit."""
    pg, erori = _date_firma_forma(browser, "pfa")
    try:
        bilant = {k: _eticheta(pg, "df-" + k) for k in ("mare_contribuabil", "forma_proprietate", "interes_public")}
        reg_com, caen, iban = _eticheta(pg, "df-reg_com"), _eticheta(pg, "df-caen"), _eticheta(pg, "df-iban")
        regim_tag = pg.evaluate("() => document.querySelector('#vf-regim_fiscal').tagName")
        regim_text = pg.inner_text("#vf-camp-regim_fiscal")
    finally:
        pg.close()
    assert not erori, erori
    assert bilant == {"mare_contribuabil": None, "forma_proprietate": None, "interes_public": None}, bilant
    assert "*" not in reg_com and "Cerut la bilanț" not in reg_com, reg_com
    assert "*" in caen and "*" in iban, (caen, iban)          # anti-vacuu: ce datorează PFA (D112 / D300 / D394) rămâne cerut
    assert regim_tag == "INPUT" and "Nu se aplică" in regim_text and "D212" in regim_text, (regim_tag, regim_text)
    assert "Microîntreprindere" not in regim_text, regim_text


def test_def_c71_1_srl_pastreaza_campurile_bilantului(browser):
    """Anti-vacuu: la SRL, aceleași câmpuri rămân cerute („*”, „Cerut la bilanț.”), iar „Regim fiscal” are lista micro / profit."""
    pg, erori = _date_firma_forma(browser, "srl")
    try:
        reg_com, mc = _eticheta(pg, "df-reg_com"), _eticheta(pg, "df-mare_contribuabil")
        optiuni = pg.eval_on_selector_all("#vf-regim_fiscal option", "os => os.map(o => o.value)")
    finally:
        pg.close()
    assert not erori, erori
    assert "*" in reg_com and "Cerut la bilanț." in reg_com, reg_com
    assert mc is not None and "*" in mc, mc
    assert "micro" in optiuni and "profit" in optiuni, optiuni


# ── 661 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _stare_spv(**x):
    """Răspunsul `GET /tenants/{id}/spv/stare` (`spv_conector.stare_firma`), cu `acoperire` clasificată de server (`acoperire_cui`)."""
    from core.spv_conector import acoperire_cui
    st = {"conectat": True, "cui": "49123456", "verificat_la": None, "are_drept": None, "eroare": None, "mesaje": None}
    st.update(x)
    st["acoperire"] = acoperire_cui(st["conectat"], st["verificat_la"], st["are_drept"])
    return st


def test_def_661_conectat_e_al_cabinetului_firma_spune_daca_certificatul_acopera_cui_ul(browser):
    """ROȘU înainte: firma necitită încă („SPV: conectat. Firma n-a fost încă verificată…”) și cea cu răspuns ANAF neclar („SPV: conectat;
    ultima verificare…”) — pentru F7 (CUI inventat) ecranul spunea „SPV: conectat”, deși certificatul nu acoperă CUI-ul."""
    stari = {
        "neverificat": _stare_spv(),
        "neconfirmat": _stare_spv(verificat_la="2026-10-25T10:17:00+03:00", eroare="CIF introdus nu este valid", eroare_de_la_anaf=True),
        "neacoperit": _stare_spv(verificat_la="2026-10-25T10:17:00+03:00", are_drept=False, eroare="Nu aveti drept in SPV pentru CIF=49123456",
                                 mesaj="Certificatul conectat al cabinetului nu are drept în SPV pentru CUI-ul acestei firme (49123456)."),
        "acoperit": _stare_spv(verificat_la="2026-10-25T10:17:00+03:00", are_drept=True, mesaje=2),
        "neconectat": {"conectat": False, "cui": "", "verificat_la": None, "are_drept": None, "eroare": None, "mesaje": None},
    }
    pg, erori = _pagina(browser, {})
    try:
        texte = pg.evaluate("""async (stari) => { const m = await import('/static/js/ecrane/spv_stare.js'); const o = {};
          for (const [k, st] of Object.entries(stari)) o[k] = m.textStareSpv(st); return o; }""", stari)
    finally:
        pg.close()
    assert not erori, erori
    for k in ("neverificat", "neconfirmat", "neacoperit", "neconectat"):
        assert "SPV: conectat" not in texte[k]["text"] and texte[k]["tip"] == "avert", (k, texte[k])
    assert "încă nu se știe dacă certificatul cabinetului are drept pe CUI-ul acestei firme (49123456)" in texte["neverificat"]["text"]
    assert "nu e confirmat" in texte["neconfirmat"]["text"] and "„CIF introdus nu este valid”" in texte["neconfirmat"]["text"]
    assert texte["neacoperit"]["text"].startswith("SPV: fără drept pentru această firmă.") and texte["neacoperit"]["spreConectare"]
    assert texte["acoperit"]["tip"] == "ok" and "are drept pe CUI-ul acestei firme (49123456)" in texte["acoperit"]["text"], texte["acoperit"]
    assert "2 facturi primite" in texte["acoperit"]["text"], texte["acoperit"]


# ── 541 (ecranul) ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_541_perioadele_arata_cine_si_cand_iar_cea_stearsa_ramane(browser):
    """ROȘU înainte: tabelul perioadelor avea numai De la / Până la / Sursa / Verificat la ANAF; perioada ștearsă dispărea."""
    tvai = {"aplica_azi": True, "fara_data": False, "text": "de la 01.10.2026",
            "curenta": {"id": 3, "de_la": "2026-10-01", "pana_la": None, "sursa": "manual", "data_optiune": None, "creat_la": "2026-10-22T19:12:21+03:00"},
            "perioade": [{"id": 3, "de_la": "2026-10-01", "pana_la": None, "sursa": "manual", "verificat_anaf_la": None, "data_optiune": None,
                          "creat_la": "2026-10-22T19:12:21+03:00", "scrisa": {"cine": "Ana Probă", "la": "2026-10-22T19:12:21+03:00"}}],
            "scoase": [{"text": "de la 01.07.2026", "cine": "Ion Pop", "la": "2026-10-21T09:00:00+03:00", "inlocuita_cu": None}],
            "avertismente": ["Perioada de la 01.10.2026 a fost scrisă pe 22.10.2026, în aceeași perioadă fiscală (trimestrul IV 2026), fără data "
                             "notificării: […] data corectă e 01.01.2027 […]."]}
    pg, erori = _pagina(browser, _rute(_date(_profil()), _vector(tip_decont="trimestrial", tva_incasare=tvai), _asociati(2)))
    try:
        pg.evaluate("""async () => { const d = await import('/static/js/ecrane/date_firma.js');
          window._nav.deschide('Date firmă', (c, n) => d.randeazaDateFirma(c, n, 1)); }""")
        pg.wait_for_selector("#vf-tva-incasare-perioade", timeout=15000)
        cap = pg.eval_on_selector_all("#vf-tva-incasare-perioade thead th", "ths => ths.map(t => t.innerText)")
        rand = pg.inner_text("#vf-tva-incasare-perioade tr[data-perioada-rand]")
        scoasa = pg.inner_text("#vf-tva-incasare-perioade tr[data-perioada-scoasa]")
        camp_opt = pg.is_visible("#vf-tva_incasare_data_optiune")
        bloc = pg.inner_text("#vf-camp-tva_incasare")
    finally:
        pg.close()
    assert not erori, erori
    assert "Scrisă de, când" in cap and "Data notificării" in cap, cap
    assert "Ana Probă" in rand and "22.10.2026" in rand, rand
    assert "de la 01.07.2026" in scoasa and "Ion Pop" in scoasa and "ștearsă" in scoasa, scoasa
    assert camp_opt and "01.01.2027" in bloc, bloc

