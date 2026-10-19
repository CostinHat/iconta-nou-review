# -*- coding: utf-8 -*-
"""Lotul 5 — rolurile (DEFICIENTE.md 262, 265, 266), probate în browser, pe aplicația pornită de `scripts/e2e_poarta.py`.

Conturile cu drepturi anume (asistent doar cu „Poate pregăti”, asistent cu „Poate valida” fără „Poate depune”) se creează pe drumul
aplicației (`e2e_bloc_a.cont_asistent`) și se scot în același test; datele stau pe firma sintetică a rulării (`firma_e2e`). Bifele
contului se schimbă DIRECT în bază (ca administratorul din alt browser, din ecranul Asistenți), iar fila deschisă a asistentului nu
se reîncarcă și nu se re-autentifică.
"""
from conftest import sql
from e2e_bloc_a import AZI, _api, _ok, cont_asistent, ecran_cont, pregateste_firma


def _vizibil(pg, selector):
    """Elementul există și se vede (poarta drepturilor îl scoate cu `display: none`, deci `offsetParent` e null)."""
    return pg.evaluate("(s) => { const e = document.querySelector(s); return !!(e && e.offsetParent !== null); }", selector)


def _fereastra_firmei(e, firma):
    e.firma(firma["nume"])
    e.pg.wait_for_selector(".fereastra:last-of-type .firme-scoatere", state="attached", timeout=20000)


def _deschide_card(e, card, asteptat):
    e.pg.click(card)
    e.pg.wait_for_selector(asteptat, state="attached", timeout=30000)
    e.pg.wait_for_timeout(400)


# ── 262 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def test_def_262_asistentul_nu_vede_scoaterea_firmei(browser, request, patron, firma_e2e):
    """262. Asistentul vede „Scoate firma din portofoliu” în fereastra firmei; se ascunde, ca în lista de firme.
    Pașii: asistentul (cu „Poate pregăti”), pe firma alocată -> fereastra firmei: blocul „Scoate firma din portofoliu” (butonul și nota
    lui) nu se vede, ca rândul „Scoate” din lista de firme. Clasa (butoane spre ecrane ale căror acțiuni sunt toate ale
    administratorului): în „Acces client” nu se vede „Invită client nou” (previzualizarea portalului, da), în „Magazin online” nu se
    vede „Configurează magazinul”. Contabilul-șef le vede pe toate."""
    tid = firma_e2e["tenant_id"]
    with cont_asistent(firme=(tid,), eticheta="r262") as a, ecran_cont(browser, request, a["email"]) as e:
        pg = e.pg
        _fereastra_firmei(e, firma_e2e)
        bloc_scoatere = _vizibil(pg, ".fereastra:last-of-type .firme-scoatere")
        buton_scoatere = _vizibil(pg, "#firma-scoate")
        text_firma = e.fereastra()
        motiv_firma = _vizibil(pg, ".fereastra:last-of-type .drept-motiv")
        e.captura("asistent_fereastra_firmei", intreaga=True)
        _deschide_card(e, "#fa-acces", "#ac-btn-invita")
        pg.wait_for_function("() => !document.querySelector('#ac-lista').innerText.includes('Se încarcă')", timeout=20000)
        invita, previzualizare = _vizibil(pg, "#ac-btn-invita"), _vizibil(pg, "#ac-btn-preview")
        motiv_acces = pg.inner_text(".fereastra:last-of-type .drept-motiv")
        e.captura("asistent_acces_client")
        pg.click(".fereastra:last-of-type .nav-inapoi")
        _deschide_card(e, "#fa-magazin", "#wc-btn-config")
        configurare = _vizibil(pg, "#wc-btn-config")
        e.captura("asistent_magazin")
    assert not bloc_scoatere and not buton_scoatere, "asistentul vede scoaterea firmei"
    assert "Scoate firma din portofoliu" not in text_firma and "Două acte diferite" not in text_firma, text_firma[-600:]
    # motivul porții stă în blocul ascuns: deasupra cardurilor firmei nu apare „Acțiunile de aici nu se afișează”
    assert not motiv_firma and "nu se afișează" not in text_firma, text_firma[:300]
    assert not invita and previzualizare, ("Invită client nou", invita, "Previzualizează portalul", previzualizare)
    assert motiv_acces.startswith("Unele acțiuni de aici nu se afișează") and "doar administratorul cabinetului" in motiv_acces, motiv_acces
    assert not configurare, "asistentul vede „Configurează magazinul”"
    # contabilul-șef: aceleași elemente, vizibile (anti-vacuu: selectorii de mai sus chiar găsesc ce caută)
    _fereastra_firmei(patron, firma_e2e)
    assert _vizibil(patron.pg, "#firma-scoate") and "Două acte diferite" in patron.fereastra()
    _deschide_card(patron, "#fa-acces", "#ac-btn-invita")
    assert _vizibil(patron.pg, "#ac-btn-invita")
    patron.captura("patron_acces_client")


# ── 265 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _semnal_vizibilitate(pg):
    """Revenirea în filă (`visibilitychange`), momentul în care aplicația își recitește drepturile — ca la întoarcerea omului."""
    pg.evaluate("() => document.dispatchEvent(new Event('visibilitychange'))")


def _stare_265(pg, nota_id):
    return pg.evaluate("""(id) => {
      const et = document.querySelector('[data-functie-asistent]');
      const b = document.querySelector('button[data-val="' + id + '"]');
      return {eticheta: et ? et.textContent.trim() : null, valideaza: !!(b && b.offsetParent !== null),
              aceeasi_pagina: window.__fara_relogare === 265, jurnal_deschis: !!document.querySelector('.fereastra [data-nota-id]'),
              card_validat: !!document.querySelector("button.cab-card [data-cheie='validat']")};
    }""", nota_id)


def _asteapta_265(pg, nota_id, **cerut):
    pg.wait_for_function("""([id, c]) => {
      const et = document.querySelector('[data-functie-asistent]');
      const b = document.querySelector('button[data-val="' + id + '"]');
      const st = {eticheta: et ? et.textContent.trim() : null, valideaza: !!(b && b.offsetParent !== null),
                  card_validat: !!document.querySelector("button.cab-card [data-cheie='validat']")};
      return Object.keys(c).every((k) => st[k] === c[k]);
    }""", arg=[nota_id, cerut], timeout=20000)


def test_def_265_ecranul_urmeaza_drepturile_fara_reautentificare(browser, request, patron, firma_e2e):
    """265. O schimbare de drepturi nu se vede în sesiunea deschisă până la re-autentificare (Ana a rămas „junior” după ce a primit
    „Poate valida”; după retragere, butonul „Validează” a rămas afișat, deși serverul refuză corect).
    Pașii: Ana („Poate pregăti”) scrie o notă și deschide Registrul jurnal: „Asistent junior”, fără „Validează” -> administratorul îi
    dă „Poate valida”; Ana revine în filă: „Asistent senior” și „Validează” pe notă, în aceeași fereastră, fără reîncărcare și fără
    re-autentificare -> dreptul i se ia: „Validează” dispare, eticheta revine la „junior” -> i se dă din nou, Ana închide fereastra:
    pagina principală are cardul „De validat” -> dreptul i se ia cât stă pe pagina principală: cardul dispare."""
    tid = firma_e2e["tenant_id"]
    pregateste_firma(patron, firma_e2e)
    with cont_asistent(firme=(tid,), eticheta="r265") as a, ecran_cont(browser, request, a["email"]) as e:
        pg = e.pg
        e.acasa()
        nota = _ok(_api(e, "POST", "/tenants/%d/jurnal" % tid,
                        {"data": AZI.isoformat(), "descriere": "Nota D265", "document_ref": "D265",
                         "linii": [{"debit": "5311", "credit": "4111", "suma": 26.5, "partener_nume": "PARTENER PROBA SRL"}]}), "nota Anei")
        try:
            e.firma(firma_e2e["nume"])
            pg.click("#fa-jurnal")
            pg.wait_for_selector('.fereastra:last-of-type button[data-val="%s"]' % nota["id"], state="attached", timeout=30000)
            pg.evaluate("() => { window.__fara_relogare = 265; }")
            inainte = _stare_265(pg, nota["id"])
            e.captura("junior")

            sql("UPDATE public.users SET poate_valida = true WHERE id = %s", (a["id"],))
            _semnal_vizibilitate(pg)
            _asteapta_265(pg, nota["id"], eticheta="Asistent senior", valideaza=True)
            dat = _stare_265(pg, nota["id"])
            e.captura("senior_in_jurnal")

            sql("UPDATE public.users SET poate_valida = false WHERE id = %s", (a["id"],))
            _semnal_vizibilitate(pg)
            _asteapta_265(pg, nota["id"], eticheta="Asistent junior", valideaza=False)
            luat = _stare_265(pg, nota["id"])
            st_refuz = _api(e, "POST", "/tenants/%d/jurnal/%d/valideaza" % (tid, nota["id"]), {})["status"]

            sql("UPDATE public.users SET poate_valida = true WHERE id = %s", (a["id"],))
            _semnal_vizibilitate(pg)
            _asteapta_265(pg, nota["id"], eticheta="Asistent senior", valideaza=True)
            pg.click(".fereastra:last-of-type .nav-x")
            _asteapta_265(pg, nota["id"], card_validat=True)
            acasa_senior = _stare_265(pg, nota["id"])
            e.captura("senior_acasa")

            sql("UPDATE public.users SET poate_valida = false WHERE id = %s", (a["id"],))
            _semnal_vizibilitate(pg)
            _asteapta_265(pg, nota["id"], eticheta="Asistent junior", card_validat=False)
            acasa_junior = _stare_265(pg, nota["id"])
            e.captura("junior_acasa")
        finally:
            sql('DELETE FROM "%s".inregistrari WHERE id = %%s' % firma_e2e["schema"], (nota["id"],))
    assert inainte["eticheta"] == "Asistent junior" and not inainte["valideaza"] and inainte["jurnal_deschis"], inainte
    assert dat == {"eticheta": "Asistent senior", "valideaza": True, "aceeasi_pagina": True, "jurnal_deschis": True,
                   "card_validat": False}, dat
    assert luat["eticheta"] == "Asistent junior" and not luat["valideaza"] and luat["aceeasi_pagina"] and luat["jurnal_deschis"], luat
    assert st_refuz == 403, "serverul trebuie să refuze validarea fără „Poate valida”: %s" % st_refuz
    assert acasa_senior["card_validat"] and acasa_senior["aceeasi_pagina"], acasa_senior
    assert not acasa_junior["card_validat"] and acasa_junior["eticheta"] == "Asistent junior" and acasa_junior["aceeasi_pagina"], acasa_junior


# ── 266 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def test_def_266_coada_spune_dreptul_real_si_vorbeste_de_note(browser, request, patron, firma_e2e):
    """266. Coada de validare îi spune asistentului fără „Poate depune” că „Declarațiile le pregătești și le depui tu”; cardul promite
    „Declarații și note de validat”, iar ecranul vorbește doar de declarații.
    Pașii: un asistent junior scrie o notă (intră la validare) -> Ana („Poate valida”, fără „Poate depune”) deschide „De validat”: nota
    e în „Note de validat”, cu „Validează”; textul vorbește de note și de declarații, spune că declarațiile le depune un coleg cu
    „Poate depune” și nicio frază nu-i spune că depune ea."""
    tid = firma_e2e["tenant_id"]
    pregateste_firma(patron, firma_e2e)
    with cont_asistent(firme=(tid,), eticheta="r266j") as j, ecran_cont(browser, request, j["email"]) as ej:
        ej.acasa()
        nota = _ok(_api(ej, "POST", "/tenants/%d/jurnal" % tid,
                        {"data": AZI.isoformat(), "descriere": "Nota D266", "document_ref": "D266",
                         "linii": [{"debit": "5311", "credit": "4111", "suma": 26.6, "partener_nume": "PARTENER PROBA SRL"}]}), "nota juniorului")
    try:
        with cont_asistent(valida=True, depune=False, firme=(tid,), eticheta="r266") as a, ecran_cont(browser, request, a["email"]) as e:
            pg = e.pg
            e.acasa()
            pg.click("button.cab-card:has([data-cheie='validat'])")
            pg.wait_for_selector(".fereastra:last-of-type #val-titlu", timeout=60000)
            pg.wait_for_selector(".fereastra:last-of-type .val-card", timeout=30000)
            pg.wait_for_timeout(600)
            text = e.fereastra()
            intro = pg.eval_on_selector_all(".fereastra:last-of-type .mig-intro", "es => es.map(x => x.innerText)")
            valideaza = pg.evaluate("() => [...document.querySelectorAll('.fereastra:last-of-type .val-aproba')]"
                                    ".filter(b => b.offsetParent !== null).length")
            e.captura("coada_fara_depunere")
    finally:
        sql('DELETE FROM "%s".inregistrari WHERE id = %%s' % firma_e2e["schema"], (nota["id"],))
    low = text.lower()
    assert "note de validat (" in low and "Nota D266" in text and valideaza >= 1, (valideaza, text[:600])
    for fals in ("le depui tu", "depui singur", "pregătești și depui", "le pregătești și le depui"):
        assert fals not in text, "coada îi spune celui fără „Poate depune” că depune: %r în %s" % (fals, intro)
    toate = " ".join(intro)
    assert "Notele de mai sus le-au pregătit asistenții: le validezi sau le respingi." in toate, intro
    assert "Declarațiile" in toate and "«Poate depune»" in toate, intro
