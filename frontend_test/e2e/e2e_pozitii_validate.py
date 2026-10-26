# -*- coding: utf-8 -*-
"""Pozițiile validate la testare care n-aveau încă un test de capăt la capăt al fluxului lor principal (comanda Costin 11.2 pct.4,
verbatim în DECIZII „Comanda 11.2”): „fiecare poziție validată la testare are un test automat în poartă, iar poarta nu trece dacă vreunul
pică.” Registrul canonic poziție -> test e `POZITII_VALIDATE.csv` (rădăcina depozitului), păzit de `core/test_pozitii_validate.py`.

Fiecare test reface, pe ecran, fluxul principal al funcționalității din `FUNCTIONALITATI.csv` (coloana ID), pe aplicația pornită de
`scripts/e2e_poarta.py` din index, pe baza de TEST, pe firme NOI ale cabinetului de test (`conftest.firma_noua`, scoase la final).
Datele de PORNIRE puse altfel decât din ecranul probat sunt numai cele pe care ecranul probat nu le produce și sunt numite în docstringul
fiecărui test; ele trec prin rutele aplicației (`_api`, aceeași sesiune ca ecranul), niciodată prin INSERT-uri care fabrică rezultatul
probat. Excepții declarate: alocarea asistentului comun pe firma sintetică (`public.user_tenants`, ca la 293) și răspunsurile ANAF ale
plasei (`ICONTA_ANAF_SIMULAT`, `anaf.json` — serviciu extern, ca la 444).

Mutațiile (fiecare test pică pe ea): `frontend_test/e2e/mut_pozitii_validate.json`.
"""
import datetime as _dt
import json
import os
import re
import time
from decimal import ROUND_HALF_UP, Decimal

import pytest

from conftest import BAZA, INALT, LAT, PREFIX_FIRMA, TELEFON_TEST, _scoate_firmele_e2e, ai_pregateste, cui_cu_control, firma_noua
from conftest import alege_perioada, alege_tipul, perioada_incheiata, sql
from e2e_bloc_a import (CLIENT, T_COMERT, _api, _card, _deschide_emiterea, _deschide_factura, _deschide_firme, _ok, _pdf_ok, _pdf_text,
                        _scoate_cont, cont_asistent, ecran_cont, emite_api, pregateste_firma, PRODUS)
from e2e_bloc_b import _cnp
from e2e_bloc_c import _declaratie_pas1, _trimite_si_asteapta
from e2e_bloc_d import LUNA_TRECUTA, _control_firma, _coada, _genereaza, _rand_salariat, firma_sal  # noqa: F401 — firma_sal: fixtura
from e2e_bloc_d import _stat as _stat_luna
from e2e_lot5_migrare import PNG, fire_curate  # noqa: F401 — fire_curate: fixtura (firele de Suport ale testului se scot la final)

AZI = _dt.date.today()
_RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_F = ".fereastra:last-of-type "
_SUPERADMIN = "admin@prisma-cont.test"
_ASISTENT = "asistent@prisma-cont.test"


@pytest.fixture(scope="module")
def firma_poz():
    """Firma NOUĂ a fișierului (`conftest.firma_noua`), scoasă la final."""
    for f in firma_noua():
        yield f


@pytest.fixture()
def firma_proaspata():
    """O firmă NOUĂ numai pentru un test (potrivirea băncii și auditul de preluare nu au voie să vadă facturile / soldurile altui test)."""
    for f in firma_noua():
        yield f


# ── ajutoare ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _anaf_pune(cui, rezultat):
    """Răspunsul ANAF al plasei pentru `cui` (`anaf_api._raspuns_simulat`), adăugat la cele puse de alte teste."""
    d = os.environ["ICONTA_ANAF_SIMULAT"]
    os.makedirs(d, exist_ok=True)
    cale = os.path.join(d, "anaf.json")
    toate = json.load(open(cale, encoding="utf-8")) if os.path.exists(cale) else {}
    toate[str(cui)] = rezultat
    with open(cale, "w", encoding="utf-8") as f:
        json.dump(toate, f, ensure_ascii=False)


def _lei(t):
    """„1.250,00” -> Decimal('1250.00')."""
    return Decimal(t.replace(".", "").replace(",", "."))


def _sume_rand(text):
    """{brut, CAS, CASS, impozit, net: (Decimal, textul de pe ecran)} — prima apariție pe rândul salariatului din statul de plată."""
    out = {}
    for k, v in re.findall(r"\b(brut|CAS|CASS|impozit|net)\s+([\d.]+,\d{2})", text):
        out.setdefault(k, (_lei(v), v))
    assert set(out) == {"brut", "CAS", "CASS", "impozit", "net"}, text
    return out


def _sume_salariat(patron):
    """[lotul 13, 677] {brut, CAS, CASS, impozit, net: (Decimal, textul de pe ecran)} din compoziția netului, în fereastra salariatului
    (deschisă din rândul statului, apoi închisă: înapoi la statul de plată)."""
    from e2e_lot13_sal_ajutor import coloane, deschide_salariat, inchide
    deschide_salariat(patron)
    c = coloane(patron)
    inchide(patron)
    patron.pg.wait_for_selector(_F + "#sp-tabel", timeout=30000)
    ro = lambda v: "{:,.2f}".format(Decimal(str(v))).replace(",", "X").replace(".", ",").replace("X", ".")   # noqa: E731
    return {k: (Decimal(str(c[e][0])).quantize(Decimal("0.01")), ro(c[e][0])) for k, e in (
        ("brut", "Salariu pe zile lucrate"), ("CAS", "CAS (25%)"), ("CASS", "CASS (10%)"), ("impozit", "Impozit pe venit"),
        ("net", "Net de plată"))}


def _iban_ro(banca, cont16):
    """IBAN românesc cu cifrele de control calculate (ISO 13616, mod-97), verificat de validatorul aplicației — nu inventat."""
    from core.salariati_api import iban_valid
    rearanjat = banca + cont16 + "RO00"
    numeric = "".join(str(int(c, 36)) if c.isalpha() else c for c in rearanjat)
    iban = "RO%02d%s%s" % (98 - int(numeric) % 97, banca, cont16)
    assert iban_valid(iban), iban
    return iban


def _fetch(pg, cale, metoda="GET", corp=None):
    """(status, json) — o cerere din pagina contului, cu sesiunea lui."""
    return pg.evaluate("""async ([c, m, b]) => { const t = sessionStorage.getItem('iconta_token');
        const o = {method: m, headers: {Authorization: 'Bearer ' + t}};
        if (b !== null) { o.headers['Content-Type'] = 'application/json'; o.body = JSON.stringify(b); }
        const x = await fetch(c, o); let j = null; try { j = await x.json(); } catch (_) {} return [x.status, j]; }""", [cale, metoda, corp])


def _emite_catre(e, firma, nume, cui, pret):
    """O factură emisă pe ruta formularului (`POST facturi/emite`, payload-ul ecranului), cu o linie de servicii la 21%, către `nume`."""
    corp = {"linii": [{"descriere": PRODUS, "cantitate": 1, "um": "ora", "pret_unitar": pret, "cota_tva": 21, "cota_propusa": 21,
                       "articol_id": None}],
            "tert_nume": nume, "tert_cui": cui, "tert_adresa": "Str. Probei nr. 7", "tert_oras": "București", "tert_judet": "B",
            "moneda": "RON", "tert_tara": "RO", "tip_operatiune": "normal", "bon_fiscal_nr": None, "bon_fiscal_data": None,
            "data_emitere": AZI.isoformat(), "data_scadenta": (AZI + _dt.timedelta(days=30)).isoformat(), "tip": "factura"}
    return _ok(_api(e, "POST", "/tenants/%d/facturi/emite" % firma["tenant_id"], corp), "emitere")


# ── F004 — Validare CUI la ANAF ──────────────────────────────────────────────────────────────────────────────────────────────────
def test_pozitie_f004_adauga_firma_cu_datele_de_la_anaf(patron):
    """F004. Pașii: Firme -> „+ Adaugă firmă” -> CUI-ul firmei: sub câmp „Din ANAF: <denumirea> — verifică…”, iar „Denumire firmă” se
    completează singură din răspunsul ANAF -> tipul SRL -> „Adaugă firma”: „Firma … a fost creată și apare în listă.”; în profilul firmei
    noi stau datele aduse de ANAF (CAEN, adresa, nr. registrul comerțului, plătitor de TVA și data înregistrării în scopuri de TVA), iar
    denumirea ANAF e păstrată lângă cea aleasă. Răspunsul ANAF e al plasei (serviciu extern; `ICONTA_ANAF_SIMULAT`), verificarea rulează
    pe server, prin `/public/verifica-cui` și prin crearea firmei (`tenant_provisioning.date_din_anaf`)."""
    pg = patron.pg
    cui = cui_cu_control(97000000 + int(time.time()) % 999999)
    den = "%s F004 %s SRL" % (PREFIX_FIRMA, cui)
    _anaf_pune(cui, {"denumire": den, "platitor_tva": True, "tva_data_inceput": "2020-02-01", "cod_caen": "6920",
                     "adresa": "Str. Probei nr. 4, București", "nr_reg_com": "J40/4004/2020", "data_inregistrare": "2020-01-15",
                     "inactiv": False, "tva_la_incasare": False})
    try:
        _deschide_firme(patron)
        pg.click("#firme-adauga")
        pg.wait_for_selector("#fn-cui", timeout=10000)
        pg.fill("#fn-cui", cui)
        pg.wait_for_function("() => (document.querySelector('#fn-cui-info') || {textContent: ''}).textContent.startsWith('Din ANAF')",
                             timeout=30000)
        info = pg.inner_text("#fn-cui-info")
        assert info.startswith("Din ANAF: %s" % den), info
        assert pg.input_value("#fn-nume") == den
        pg.select_option("#fn-tip", "srl")
        pg.click("#fn-salveaza")
        pg.wait_for_function("() => document.body.innerText.includes('a fost creată și apare în listă')", timeout=60000)
        pg.wait_for_function("(n) => (document.querySelector('#firme-lista') || {innerText: ''}).innerText.includes(n)", arg=den,
                             timeout=20000)
        patron.captura()
        r = sql("SELECT schema_name, nume, nume_anaf FROM public.tenants WHERE cui = %s", (cui,))
        assert len(r) == 1 and r[0][1:] == (den, den), r
        prof = sql('SELECT caen, adresa, reg_com, platitor_tva, platitor_tva_anaf, platitor_tva_anaf_inceput::text FROM "%s".firma_profil'
                   % r[0][0])
        assert prof == [("6920", "Str. Probei nr. 4, București", "J40/4004/2020", True, True, "2020-02-01")], prof
    finally:
        for (tid,) in sql("SELECT id FROM public.tenants WHERE cui = %s AND nume LIKE %s", (cui, PREFIX_FIRMA + "%")):
            _scoate_firmele_e2e(tid)


# ── F006 — Contabilii și asistenții cabinetului ──────────────────────────────────────────────────────────────────────────────────
def test_pozitie_f006_asistentul_invitat_cu_drepturile_si_firmele_lui(patron, firma_poz):
    """F006. Pașii administratorului: Asistenți -> „Adaugă asistent” -> emailul, numele, „Poate pregăti” (bifat din oficiu), firma bifată
    -> „Trimite invitația”: „Invitație trimisă pe <email>.”, iar în listă cardul colegului: „asistent · 1 firmă”, „✓ Poate pregăti”,
    „· Poate valida”, „· Poate depune” -> „Editează”: firma e bifată; bifează „Poate valida” -> „Salvează” -> „Da, salvează”: cardul
    arată „✓ Poate valida”. În cont: drepturile (pregătește + validează, fără depunere), cabinetul și firma alocată sunt cele alese."""
    pg = patron.pg
    tid = firma_poz["tenant_id"]
    email = "e2e-poz-f006-%d@prisma-cont.test" % (int(time.time() * 1000) % 1000000000)
    nume = "Asistent F006 %d" % (int(time.time()) % 100000)
    try:
        patron.acasa()
        pg.click("button.cab-card:has([data-cheie='asistenti'])")
        pg.wait_for_selector("#asi-adauga", timeout=20000)
        pg.click("#asi-adauga")
        pg.wait_for_selector(".asi-firma-noua[value='%d']" % tid, timeout=20000)
        pg.fill("#asi-email", email)
        pg.fill("#asi-nume", nume)
        assert pg.is_checked("#asi-pregati") and not pg.is_checked("#asi-valida") and not pg.is_checked("#asi-depune")
        pg.check(".asi-firma-noua[value='%d']" % tid)
        pg.click("#asi-trimite")
        pg.wait_for_selector("#asi-confirmare", timeout=30000)
        assert pg.inner_text("#asi-confirmare").strip() == "Invitație trimisă pe %s." % email, pg.inner_text("#asi-confirmare")
        card = pg.locator("#asi-lista .val-card", has_text=nume).first
        assert "asistent · 1 firmă" in card.locator(".asi-rol").inner_text(), card.inner_text()
        perms = card.locator(".asi-perms").inner_text()
        assert "✓ Poate pregăti" in perms and "· Poate valida" in perms and "· Poate depune" in perms, perms
        patron.captura("invitat")
        card.locator("[data-act='edit']").click()
        pg.wait_for_selector("[data-perm='poate_valida']", timeout=20000)
        assert pg.is_checked("[data-tid='%d']" % tid), "firma aleasă la invitație nu e bifată la editare"
        pg.check("[data-perm='poate_valida']")
        pg.click("#asi-salveaza")
        pg.wait_for_selector("#ca-ok", timeout=10000)
        pg.click("#ca-ok")
        pg.wait_for_function("(n) => [...document.querySelectorAll('#asi-lista .val-card')].some((c) => c.innerText.includes(n) && "
                             "c.querySelector('.asi-perms').innerText.includes('✓ Poate valida'))", arg=nume, timeout=30000)
        patron.captura("drepturi")
        u = sql("SELECT id, poate_pregati, poate_valida, COALESCE(poate_depune, false), accounting_firm_id, rol FROM public.users "
                "WHERE email = %s", (email,))
        assert len(u) == 1 and u[0][1:] == (True, True, False, firma_poz["cabinet_id"], "angajat"), u
        assert sql("SELECT tenant_id FROM public.user_tenants WHERE user_id = %s", (u[0][0],)) == [(tid,)]
    finally:
        for (uid,) in sql("SELECT id FROM public.users WHERE email = %s", (email,)):
            sql("DELETE FROM public.user_tenants WHERE user_id = %s", (uid,))
            _scoate_cont(uid)


# ── F008 — Autentificare și sesiuni ──────────────────────────────────────────────────────────────────────────────────────────────
def test_pozitie_f008_autentificarea_deschide_numai_firmele_contului(browser, firma_poz):
    """F008. Pașii: pagina publică -> „Acces” -> „Intră în cont” -> cabinet -> emailul și o parolă greșită -> „Autentificare”: eroarea
    se vede, nicio sesiune nu se deschide -> parola bună: pagina principală a contului; sesiunea poartă rolul contului (asistent:
    „angajat”), iar lista firmelor e numai firma alocată lui; o firmă a cabinetului nealocată lui e refuzată.
    Contul de PORNIRE: un asistent creat pe drumul aplicației (`repo_utilizatori.creeaza_cont_asistent`, cu parola lui), alocat firmei,
    cu prima intrare deja făcută (telefonul și notificările — ca `conftest.sesiune`)."""
    with cont_asistent(firme=(firma_poz["tenant_id"],), eticheta="f008") as a:
        sql("UPDATE public.users SET telefon = %s, notificari_salvate_la = now() WHERE id = %s", (TELEFON_TEST, a["id"]))
        ctx = browser.new_context(viewport={"width": LAT, "height": INALT})
        erori = []
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: erori.append(str(e)))
        try:
            pg.goto(BAZA + "/", wait_until="domcontentloaded")
            pg.wait_for_selector("#pagina-acces-btn", timeout=20000)
            pg.click("#pagina-acces-btn")
            pg.click("#acces-intra")
            pg.click("#lg-cabinet")
            pg.fill("#login-email", a["email"])
            pg.fill("#login-parola", a["parola"] + "-gresita")
            pg.click("#login-buton")
            pg.wait_for_selector("#login-eroare:not([hidden])", timeout=20000)
            assert pg.inner_text("#login-eroare").strip(), "parola greșită fără niciun mesaj"
            assert pg.evaluate("() => sessionStorage.getItem('iconta_token')") is None, "sesiune deschisă cu parola greșită"
            pg.screenshot(path=os.path.join(os.environ.get("E2E_CAPTURI", "/tmp/e2e_capturi"), "pozitie_f008_parola_gresita.png"))
            pg.fill("#login-parola", a["parola"])
            pg.click("#login-buton")
            pg.wait_for_selector(".cab-grila, .cab-card", timeout=30000)
            pg.screenshot(path=os.path.join(os.environ.get("E2E_CAPTURI", "/tmp/e2e_capturi"), "pozitie_f008_intrat.png"))
            assert pg.evaluate("() => sessionStorage.getItem('iconta_token')"), "fără sesiune după parola bună"
            user = json.loads(pg.evaluate("() => sessionStorage.getItem('iconta_user')"))
            assert user.get("rol") == "angajat" and user.get("email") == a["email"], user
            st, r = _fetch(pg, "/tenants")
            assert st == 200 and [t["id"] for t in r["tenants"]] == [firma_poz["tenant_id"]], (st, r)
            st, r = _fetch(pg, "/tenants/%d/solduri" % T_COMERT)
            assert st in (403, 404), "firma nealocată contului a răspuns %s: %s" % (st, r)
        finally:
            ctx.close()
        assert not erori, "erori JavaScript pe ecran: %s" % erori[:3]


# ── F017 — Chitanțe emise ────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pozitie_f017_chitanta_din_factura_are_suma_in_litere_si_intra_in_casa(patron, firma_poz):
    """F017. Pașii: factura emisă de 363,00 lei (2 × 150 + TVA 21%) -> detaliul ei -> „Emite chitanță”: suma propusă e totalul -> „Emite”
    -> „PDF chitanță”: chitanța are suma (363,00) și suma în litere („trei sute șaizeci și trei de lei”), seria și numărul ei; nota
    chitanței e încasarea în casă 5311 = 4111 de 363,00 lei, legată de factură. Factura se emite pe ruta formularului (`emite_api`)."""
    pregateste_firma(patron, firma_poz)
    f = emite_api(patron, firma_poz)
    pg = patron.pg
    _deschide_factura(patron, firma_poz, f["factura_id"])
    pg.click("#fd-chitanta")
    pg.wait_for_selector("#fd-chit-ok", timeout=10000)
    assert pg.input_value("#fd-chit-suma") in ("363", "363.00"), pg.input_value("#fd-chit-suma")
    pg.click("#fd-chit-ok")
    pg.wait_for_selector("[data-chpdf]", timeout=20000)
    with pg.expect_response(lambda r: "/chitante/" in r.url and r.url.endswith("/pdf"), timeout=30000) as rr:
        pg.click("[data-chpdf]")
    text, _titlu = _pdf_text(_pdf_ok(patron, rr))
    patron.captura()
    (serie, numar), = sql('SELECT serie, numar FROM "%s".chitante WHERE factura_id = %%s' % firma_poz["schema"], (f["factura_id"],))
    assert "trei sute șaizeci și trei de lei" in text and "363,00" in text, text[:1500]
    assert str(serie) in text and str(numar) in text, (serie, numar, text[:1500])
    linii = sql('SELECT l.cont_debit, l.cont_credit, l.suma::text FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l '
                "ON l.inregistrare_id = i.id WHERE i.factura_id = %%s AND l.cont_debit = '5311'" % ((firma_poz["schema"],) * 2),
                (f["factura_id"],))
    assert linii == [("5311", "4111", "363.00")], linii


# ── F019 — Coada de validare patru-ochi ──────────────────────────────────────────────────────────────────────────────────────────
def test_pozitie_f019_validarea_in_doi_pregatitorul_nu_aproba_altul_aproba_si_depune(patron, asistent, firma_poz):
    """F019. Pașii, cu validarea în doi pornită (`POST /eu/patru-ochi`, butonul administratorului; cabinetul are doi validatori, deci e
    efectivă): asistentul pregătește D710 pe trimestrul încheiat (obligația 121, 100 -> 150, cota 1%) -> „Trimite în coadă →”: intră în
    coadă, „la validare” -> asistentul deschide „De validat”: pe declarația lui nu e „Aprobă”, ci „ai pregătit-o tu — o validează
    altcineva”, iar aprobarea cerută direct e refuzată (pregătirea și validarea de persoane diferite) -> contabilul-șef deschide coada:
    „Aprobă” -> declarația e aprobată de el -> „Confirmă depunerea” -> indexul SPV -> „— depusă.”: elementul e depus, cu indexul.
    Datele de PORNIRE: asistentul comun alocat firmei sintetice (`user_tenants`, ca la 293); politica validării în doi se readuce la final."""
    tid = firma_poz["tenant_id"]
    pregateste_firma(patron, firma_poz)
    uid_as = sql("SELECT id FROM public.users WHERE email = %s", (_ASISTENT,))[0][0]
    uid_pa = sql("SELECT id FROM public.users WHERE email = 'patron@prisma-cont.test'")[0][0]
    sql("INSERT INTO public.user_tenants (user_id, tenant_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (uid_as, tid))
    era = _ok(_api(patron, "GET", "/eu/patru-ochi"), "starea validării în doi")["activ"]
    # pornirea / oprirea validării în doi memorează și numărul de validatori la care s-a propus educația (`patru_ochi_seteaza`): fără
    # refacerea ei, mesajul „Poți activa validarea în doi” nu mai apare pentru testele de după (C8, comanda 10.10) — scurgere de stare
    edu_era = sql("SELECT educatie_4ochi_la_nr FROM public.accounting_firms WHERE id = %s", (firma_poz["cabinet_id"],))[0][0]
    peste = sql("SELECT COALESCE(max(id), 0) FROM public.declaratii_coada")[0][0]
    p = perioada_incheiata("trimestrial")
    try:
        _ok(_api(patron, "POST", "/eu/patru-ochi", {"activ": True}), "pornirea validării în doi")
        assert _ok(_api(patron, "GET", "/eu/patru-ochi"), "starea")["efectiv"], "validarea în doi nu e efectivă (sub doi validatori)"
        _declaratie_pas1(asistent, firma_poz["nume"], "d710", p.an, luna=p.trim * 3, trim=p.trim)
        pa = asistent.pg
        pa.wait_for_selector("#d710-cod", timeout=60000)
        pa.select_option("#d710-cod", "121")
        pa.fill("#d710-i", "100")
        pa.fill("#d710-c", "150")
        pa.fill("#d710-cota", "1")
        pa.click("#d710-add")
        pa.click("#d710-regen")
        _trimite_si_asteapta(asistent)
        asistent.captura("trimisa")
        assert "Trimisă în coad" in asistent.fereastra(), asistent.fereastra()[:1500]
        (cid, stare, creat), = sql("SELECT id, stare, creat_de_id FROM public.declaratii_coada WHERE tenant_id = %s AND id > %s AND "
                                   "tip = 'd710' ORDER BY id DESC LIMIT 1", (tid, peste))
        assert (stare, creat) == ("la_senior", uid_as), (stare, creat)
        actiuni_rand = ("(n) => [...[...document.querySelectorAll('.fereastra')].pop().querySelectorAll('.val-titlu')]"
                        ".filter((t) => t.innerText.includes('D710') && t.closest('.val-info').innerText.includes(n))"
                        ".map((t) => t.closest('.val-info').parentElement.querySelector('.val-actiuni').innerText)")
        asistent.acasa()
        pa.click("button.cab-card:has([data-cheie='validat'])")
        pa.wait_for_selector(_F + ".val-titlu:has-text('D710')", timeout=30000)
        a_lui = pa.evaluate(actiuni_rand, firma_poz["nume"])
        asistent.captura("coada_pregatitorului")
        assert len(a_lui) == 1 and "ai pregătit-o tu — o validează altcineva" in a_lui[0] and "Aprobă" not in a_lui[0], a_lui
        r = _api(asistent, "POST", "/coada/%d/aproba" % cid, {})
        assert r["status"] >= 400 and "ai pregătit-o tu însuți" in json.dumps(r["json"], ensure_ascii=False), r
        assert sql("SELECT stare FROM public.declaratii_coada WHERE id = %s", (cid,)) == [("la_senior",)]
        pg = patron.pg
        _coada(patron)
        rand = pg.locator(_F + ".val-info", has_text=firma_poz["nume"]).filter(has_text="D710").first.locator("xpath=..")
        rand.locator(".val-aproba").click()
        for _ in range(40):
            if sql("SELECT stare FROM public.declaratii_coada WHERE id = %s", (cid,)) == [("aprobata",)]:
                break
            time.sleep(0.5)
        assert sql("SELECT stare, aprobat_de_id FROM public.declaratii_coada WHERE id = %s", (cid,)) == [("aprobata", uid_pa)]
        patron.captura("aprobata")
        rand = pg.locator(_F + ".val-info", has_text=firma_poz["nume"]).filter(has_text="D710").first.locator("xpath=..")
        rand.locator(".val-depune").wait_for(timeout=30000)   # „Aprobate, de depus”: validată la DUK, aprobată de altcineva
        rand.locator(".val-depune").click()
        pg.wait_for_selector(_F + "#dlg-input", timeout=20000)
        pg.fill(_F + "#dlg-input", "F019-SPV-1")
        pg.click(_F + "#dlg-ok")
        pg.wait_for_function("() => { const t = [...document.querySelectorAll('.fereastra')].pop().innerText; "
                             "return t.includes('— depusă.') || !!document.querySelector('#val-conf-ok'); }", timeout=60000)
        if pg.locator("#val-conf-ok").count():   # constatări certe de confirmat: un motiv pe fiecare, ca orice contabil
            for i in range(pg.locator(".val-conf-motiv").count()):
                pg.locator(".val-conf-motiv").nth(i).fill("proba F019: declarație de probă")
            pg.click("#val-conf-ok")
            pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('— depusă.')", timeout=60000)
        patron.captura("depusa")
        assert sql("SELECT stare, spv_index FROM public.declaratii_coada WHERE id = %s", (cid,)) == [("depusa", "F019-SPV-1")]
    finally:
        _api(patron, "POST", "/eu/patru-ochi", {"activ": bool(era)})
        sql("UPDATE public.accounting_firms SET educatie_4ochi_la_nr = %s WHERE id = %s",   # date-de-pornire: starea cabinetului de dinainte
            (edu_era, firma_poz["cabinet_id"]))
        for (i,) in sql("SELECT id FROM public.declaratii_coada WHERE tenant_id = %s AND id > %s", (tid, peste)):
            sql("DELETE FROM public.notificari WHERE link = %s", ("validat:%d" % i,))


# ── F028 — Declarația D112 ───────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pozitie_f028_d112_din_statul_de_plata_e_valida_la_duk_cu_sumele_statului(patron, firma_sal):
    """F028. Pașii: salariatul (5.000 lei brut, normă întreagă, adăugat pe ruta salariaților) -> Salariați -> statul lunii trecute: CAS,
    CASS, impozit pe rând -> Declarații -> D112 pe luna trecută -> pasul 2: „Validat cu DUKIntegrator (validatorul oficial ANAF rulat
    local), fără erori”, iar rezumatul „D112: 1 salariat - impozit …, CAS …, CASS …” are exact sumele de pe statul de plată."""
    _stat_luna(patron, firma_sal, luni_inapoi=1)
    s = _sume_salariat(patron)
    _genereaza(patron, firma_sal, "d112", LUNA_TRECUTA.year, LUNA_TRECUTA.month)
    pg = patron.pg
    patron.captura()
    ok = pg.locator(_F + ".dec-ok")
    assert ok.count() == 1 and "fără erori" in ok.inner_text(), patron.fereastra()[:3000]
    casete = pg.evaluate("() => [...[...document.querySelectorAll('.fereastra')].pop().querySelectorAll('.caseta-info, .dec-avert')]"
                         ".map((c) => c.innerText.trim())")
    rez = next((c for c in casete if "D112: 1 salariat - impozit" in c), "")
    m = re.search(r"D112: 1 salariat - impozit ([\d.]+,\d{2}), CAS ([\d.]+,\d{2}), CASS ([\d.]+,\d{2})", rez)
    assert m, casete
    assert (m.group(1), m.group(2), m.group(3)) == (s["impozit"][1], s["CAS"][1], s["CASS"][1]), (m.groups(), s)


# ── F080 — Calcul salarizare (de la brut la net) ─────────────────────────────────────────────────────────────────────────────────
def test_pozitie_f080_statul_calculeaza_contributiile_si_netul_din_brut(patron, firma_sal):
    """F080. Pașii: Salariați -> statul lunii trecute, salariatul cu 5.000 lei brut, normă întreagă, funcția de bază, fără persoane în
    întreținere: pe rând CAS = 25% din brut, CASS = 10% din brut, impozitul în lei întregi, iar netul = brut − CAS − CASS − impozit."""
    _stat_luna(patron, firma_sal, luni_inapoi=1)
    s = _sume_salariat(patron)
    patron.captura()
    brut = s["brut"][0]
    assert brut == Decimal("5000.00"), s
    # CF art.138 lit.a: „Cotele de contribuții de asigurări sociale sunt următoarele: a) 25% datorată de către persoanele fizice care au
    # calitatea de angajați” (anaf_surse/cod_fiscal_227_2015_consolidat.txt)
    assert s["CAS"][0] == brut * Decimal("0.25"), s
    # CF art.156: „Cota de contribuție de asigurări sociale de sănătate este de 10% și se datorează de către persoanele fizice care au
    # calitatea de angajați” (același fișier)
    assert s["CASS"][0] == brut * Decimal("0.10"), s
    assert s["impozit"][0] == s["impozit"][0].to_integral_value(), s
    assert s["net"][0] == brut - s["CAS"][0] - s["CASS"][0] - s["impozit"][0], s


# ── F081 — Calculul scadențelor ──────────────────────────────────────────────────────────────────────────────────────────────────
def test_pozitie_f081_termenul_d112_e_25_ale_lunii_urmatoare_pe_zi_lucratoare(patron, firma_sal):
    """F081. Pașii: Control fiscal -> firma cu salariat din ianuarie 2026: fiecare D112 lunar are pe rând „termen ZZ.LL.AAAA” = ziua de 25
    a lunii următoare; când ea cade sâmbăta sau duminica, termenul e prima zi lucrătoare de după (cel puțin un rând de felul ăsta:
    25.04, 25.07 și 25.10.2026 cad în weekend); obligațiile lui noiembrie (25 decembrie) au termenul cel târziu pe 21 decembrie."""
    _control_firma(patron, firma_sal)
    pg = patron.pg
    randuri = pg.eval_on_selector_all(_F + ".cf-decl-item[data-cheie^='d112-']",
                                      "els => els.map((e) => [e.dataset.cheie, (e.querySelector('.cf-termen') || {textContent: ''})"
                                      ".textContent.trim()])")
    patron.captura()
    assert randuri, patron.fereastra()[:2000]
    mutate = 0   # termene nominale căzute în weekend, deci mutate: fără niciunul, regula mutării n-ar fi fost probată
    for cheie, termen in randuri:
        _tip, an, luna = cheie.split("-")
        if not luna:
            continue
        an, luna = int(an), int(luna)
        m = re.search(r"termen (\d\d)\.(\d\d)\.(\d{4})", termen)
        assert m, (cheie, termen)
        t = _dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        # CF art.147 alin.(1): angajatorii „sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care
        # se datorează” (anaf_surse/cod_fiscal_227_2015_consolidat.txt)
        nominala = _dt.date(an + (luna == 12), luna % 12 + 1, 25)
        if (nominala.month, nominala.day) == (12, 25):
            # CPF art.155 alin.(2): „termenul de declarare se împlinesc la 25 decembrie, sunt scadente și/sau se declară până la data de
            # 21 decembrie” (anaf_surse/legea_207_2015_consolidat.txt)
            assert t <= _dt.date(nominala.year, 12, 21) and t.weekday() < 5, (cheie, t)
        elif nominala.weekday() >= 5:
            # CPF art.75 (termenele se calculează potrivit Codului de procedură civilă) + Legea 134/2010 art.181 alin.(2): „Când ultima
            # zi a unui termen cade într-o zi nelucrătoare, termenul se prelungește până în prima zi lucrătoare care urmează.”
            assert nominala < t <= nominala + _dt.timedelta(days=4) and t.weekday() < 5, (cheie, nominala, t)
            mutate += 1
        elif nominala.month in (4, 5, 6):
            assert nominala <= t <= nominala + _dt.timedelta(days=4) and t.weekday() < 5, (cheie, nominala, t)   # Paștele / Rusaliile mobile
        else:
            assert t == nominala, (cheie, nominala, t)
    assert mutate, "niciun D112 cu ziua de 25 în weekend pe ecran (03, 06, 09/2026 o au): %s" % randuri


# ── F134 — Plata salariilor pe card ──────────────────────────────────────────────────────────────────────────────────────────────
def test_pozitie_f134_fisierul_de_plata_pe_card_are_netul_si_iban_ul_salariatului(patron, firma_sal):
    """F134. Pașii: Salariați -> statul lunii trecute -> „IBAN ⚠” la salariat -> IBAN-ul contului de salariu -> „Salvează”: butonul
    devine „IBAN ✓” -> „Fișier plată card (SEPA)”: „1 plată/plăți · total <netul> lei · format SEPA pain.001” -> „Descarcă fișierul”:
    fișierul e valid pe XSD-ul oficial pain.001.001.03 (sepa_surse/), are o plată, de exact netul de pe stat, în IBAN-ul salariatului,
    din IBAN-ul firmei (ordonatorul)."""
    from lxml import etree
    iban = _iban_ro("BTRL", "RONCRT00F1340001")
    _stat_luna(patron, firma_sal, luni_inapoi=1)
    pg = patron.pg
    net = _sume_salariat(patron)["net"]
    # [lotul 13, 673 / 677] fereastra salariatului -> „IBAN ⚠” (fereastra lui); înapoi la stat -> „Fișier plată card” (fereastra lui)
    from e2e_lot13_sal_ajutor import buton, deschide_salariat, inchide
    deschide_salariat(patron)
    buton(patron, "iban")
    pg.fill(_F + "#iban-input", iban)
    pg.click(_F + "#iban-save")
    pg.wait_for_function("() => { const b = [...document.querySelectorAll('.fereastra')].pop().querySelector('#ss-butoane [data-iban]'); "
                         "return b && b.innerText.includes('✓'); }", timeout=30000)
    inchide(patron)
    pg.wait_for_selector(_F + "#sp-plata-card", timeout=30000)
    assert not pg.is_disabled(_F + "#sp-plata-card")
    pg.click(_F + "#sp-plata-card")
    pg.wait_for_selector(_F + "#plata-descarca", timeout=30000)
    zona = " ".join(patron.fereastra().split())
    patron.captura()
    assert "1 plată · total %s lei" % net[1] in zona, zona
    with pg.expect_download(timeout=60000) as dl:
        pg.click(_F + "#plata-descarca")
    xml = open(dl.value.path(), "rb").read()
    xsd = etree.XMLSchema(etree.parse(os.path.join(_RAD, "sepa_surse", "pain.001.001.03.xsd")))
    doc = etree.fromstring(xml)
    assert xsd.validate(doc), str(xsd.error_log)
    ns = {"p": "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03"}
    tx = doc.findall(".//p:CdtTrfTxInf", ns)
    assert doc.findtext("p:CstmrCdtTrfInitn/p:GrpHdr/p:NbOfTxs", namespaces=ns) == "1" and len(tx) == 1, xml[:2000]
    assert Decimal(doc.findtext("p:CstmrCdtTrfInitn/p:GrpHdr/p:CtrlSum", namespaces=ns)) == net[0], xml[:2000]
    assert Decimal(tx[0].findtext("p:Amt/p:InstdAmt", namespaces=ns)) == net[0], xml[:2000]
    assert tx[0].findtext("p:CdtrAcct/p:Id/p:IBAN", namespaces=ns) == iban, xml[:2000]
    assert doc.findtext(".//p:DbtrAcct/p:Id/p:IBAN", namespaces=ns) == "RO49AAAA1B31007593840000", xml[:2000]


# ── F078 — Salariați (adăugare, modificare) ──────────────────────────────────────────────────────────────────────────────────────
def test_pozitie_f078_salariatul_se_adauga_si_se_corecteaza_din_ecran(patron, firma_poz):
    """F078. Pașii: Salariați -> „+ Salariat nou” -> nume, prenume, CNP (cifra de control verificată), data angajării 05.01.2026, normă
    întreagă, salariu brut 4.500, funcția de bază Da, fără scutire, ocupația COR 241107 -> „Salvează”: „Salariat salvat.”, fișa e în
    bază cu ce s-a scris -> „Gata, înapoi la listă”: salariatul e pe statul de plată -> „Corectează datele” -> prenumele nou ->
    „Salvează”: „… datele corectate s-au salvat; statul se calculează cu ele.”, iar fișa are prenumele nou."""
    pregateste_firma(patron, firma_poz)
    cnp = _cnp("285030740011")
    pg = patron.pg
    patron.firma(firma_poz["nume"])
    _card(patron, "salariati", "#sp-salariat-nou")
    pg.click("#sp-salariat-nou")
    pg.wait_for_selector("#sn-salveaza", timeout=20000)
    for sel, v in (("#sn-nume", "POZITIEF078"), ("#sn-prenume", "ANA"), ("#sn-cnp", cnp), ("#sn-data_angajare", "2026-01-05"),
                   ("#sn-salariu_brut", "4500"), ("#sn-persoane_intretinere", "0"), ("#sn-judet_casa", "B")):
        pg.fill(sel, v)
    for sel, v in (("#sn-tip_norma", "intreaga"), ("#sn-declaratie_copii", "false"), ("#sn-functie_baza", "true"),
                   ("#sn-scutit_contrib_minim", "false"), ("#sn-tip_contract", "nedeterminata")):
        pg.click(".alegere-butoane:has(+ %s) button[data-valoare='%s']" % (sel, v))   # [lotul 13, 676] listele scurte = butoane alăturate
    pg.fill("#sn-cor-cauta", "241107")
    pg.wait_for_selector("#sn-cor-rez [data-cod='241107']", timeout=20000)
    pg.click("#sn-cor-rez [data-cod='241107']")
    pg.click("#sn-salveaza")
    pg.wait_for_function("() => (document.querySelector('#sn-mesaj') || {innerText: ''}).innerText.includes('Salariat salvat')",
                         timeout=30000)
    patron.captura("salvat")
    # norma se ține în `part_time` (+ `ore_zi`); „tip_norma” e numai numele câmpului din API / ecran (`salariati_api._api_spre_db`):
    # „întreagă” = part_time false, cu programul implicit de 8 ore pe zi
    fisa = sql('SELECT nume, prenume, part_time, ore_zi::float, functie_baza, cor, data_angajare::text FROM "%s".salariati WHERE cnp = %%s'
               % firma_poz["schema"], (cnp,))
    assert fisa == [("POZITIEF078", "ANA", False, 8.0, True, "241107", "2026-01-05")], fisa
    pg.click("#sn-gata")
    # [lotul 13, 677 / 675] rândul statului -> fereastra salariatului -> „Corectează datele” (fereastra ei)
    from e2e_lot13_sal_ajutor import buton, deschide_salariat
    deschide_salariat(patron, "POZITIEF078")
    with pg.expect_response(lambda r: "/salariati/" in r.url and r.request.method == "GET", timeout=30000):
        buton(patron, "date")   # fișa citită (CIM-ul salvat)
    pg.wait_for_selector(_F + "#ed-pren", timeout=20000)
    pg.fill(_F + "#ed-pren", "ANA-MARIA")
    pg.click(_F + "#ed-save")
    pg.wait_for_function("() => (document.querySelector('#ss-msg') || {innerText: ''}).innerText.includes('datele corectate s-au "
                         "salvat')", timeout=30000)
    patron.captura("corectat")
    assert sql('SELECT prenume FROM "%s".salariati WHERE cnp = %%s' % firma_poz["schema"], (cnp,)) == [("ANA-MARIA",)]


# ── F073 — Reconciliere bancară ──────────────────────────────────────────────────────────────────────────────────────────────────
def test_pozitie_f073_extrasul_se_potriveste_exact_pe_combinatie_si_partial(patron, firma_proaspata):
    """F073. Pașii: trei clienți cu facturi deschise (A: 363,00; B: 121,00 + 242,00; C: 121,00, emise pe ruta formularului) -> Bancă ->
    extrasul cu trei încasări (CUI-ul clientului în descriere): „3 linii importate: 3 potrivite pe facturi, 0 fără potrivire”; A 363,00
    -> „Potrivire exactă” pe factura ei; B 363,00 -> „Potrivire exactă” pe amândouă facturile (121,00 + 242,00); C 60,50 -> „Parțial”, pe
    factura ei cu 60,50 -> „Contează” pe A: nota 5121 = 4111 de 363,00 e creată, iar factura lui A nu mai e deschisă."""
    f = firma_proaspata
    pregateste_firma(patron, f)
    ca, cb, cc = (cui_cu_control(31073000 + i) for i in (1, 2, 3))
    fa = _emite_catre(patron, f, "Client A F073 SRL", ca, 300)
    fb1, fb2 = _emite_catre(patron, f, "Client B F073 SRL", cb, 100), _emite_catre(patron, f, "Client B F073 SRL", cb, 200)
    fc = _emite_catre(patron, f, "Client C F073 SRL", cc, 100)
    zi = AZI.strftime("%d.%m.%Y")
    extras = ("Data;Detalii;Suma\n%s;Incasare F073 CUI %s;363,00\n%s;Incasare F073 CUI %s;363,00\n%s;Incasare F073 CUI %s;60,50\n"
              % (zi, ca, zi, cb, zi, cc))
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "banca", "#bk-fisier")
    pg.set_input_files("#bk-fisier", {"name": "extras_f073_%d.csv" % time.time(), "mimeType": "text/csv", "buffer": extras.encode("utf-8")})
    pg.wait_for_function("() => document.querySelector('#bk-mesaj').innerText.includes('importate')", timeout=30000)
    assert "3 linii importate: 3 potrivite pe facturi, 0 fără potrivire" in pg.inner_text("#bk-mesaj"), pg.inner_text("#bk-mesaj")
    pg.wait_for_selector("#bk-lista tbody.tn-nota:has-text('CUI %s')" % cc, timeout=20000)

    def _rand(cui):
        # [lotul 13, 624] facturile pe care le stinge linia stau în detaliul ei: rândul se deschide, ca la contabil
        r = pg.locator("#bk-lista tbody.tn-nota", has_text="Incasare F073 CUI %s" % cui).first
        r.locator(".tn-deschide").click()
        return r, " ".join(r.inner_text().split())

    _ra, ta = _rand(ca)
    _rb, tb = _rand(cb)
    _rc, tc = _rand(cc)
    patron.captura("potrivire")
    assert "Potrivire exactă" in ta and "Client A F073 SRL · 363,00 lei" in ta, ta
    assert "Potrivire exactă" in tb and "121,00 lei" in tb and "242,00 lei" in tb, tb
    assert "Parțial" in tc and "Client C F073 SRL · 60,50 lei" in tc, tc
    _ra.locator("[data-cont]").click()
    pg.wait_for_function("() => document.querySelector('#bk-mesaj').innerText.includes('creat')", timeout=30000)
    patron.captura("contare")
    linii = sql('SELECT l.cont_debit, l.cont_credit, l.suma::text FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l '
                "ON l.inregistrare_id = i.id WHERE l.cont_debit = '5121' AND left(l.cont_credit, 4) = '4111'" % ((f["schema"],) * 2))
    assert [(d, c[:4], s) for d, c, s in linii] == [("5121", "4111", "363.00")], linii
    deschise = [x["id"] for x in _ok(_api(patron, "GET", "/tenants/%d/banca/reconciliere/facturi-deschise" % f["tenant_id"]),
                                     "facturile deschise")["facturi"]]
    assert fa["factura_id"] not in deschise and {fb1["factura_id"], fb2["factura_id"], fc["factura_id"]} <= set(deschise), deschise


# ── F183 — Audit de preluare ─────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pozitie_f183_auditul_de_preluare_confrunta_partenerii_cu_balanta(patron, firma_proaspata):
    """F183. Pașii: firma preluată luna aceasta, cu balanța de deschidere (4111 debit 1.000, 401 credit 500, 5311 debit 300, 1012 credit 800)
    și soldurile pe parteneri (clientul 1.000 pe 4111; furnizorul 400 pe 401), salvate pe rutele Migrării -> Control fiscal -> firma ->
    „Audit de preluare” -> „Rulează auditul de preluare”: „Primul audit după preluare”, cu „Contul 4111: defalcarea pe parteneri
    (1.000,00 lei) coincide cu balanța.” la Coerent și contul 401 la Divergent; butonul devine „Rerulează auditul”.
    [346, comanda Costin 8.2; neschimbat în lotul 11] salvarea soldurilor pe parteneri NU primește rândurile unui cont care nu dă soldul lui
    din balanță: furnizorul de 400 pe 401 (balanța: 500) e respins numit („rândurile contului nu intră până nu se potrivesc”), deci auditul
    confruntă 401 din balanță cu defalcarea care a intrat — niciun partener: „Contul 401: parteneri 0,00 lei vs balanță … 500,00 lei
    (diferență 500,00 lei)”. (Prima formă a testului aștepta „parteneri 400,00”, adică o defalcare pe care aplicația n-o primește.)"""
    f = firma_proaspata
    tid = f["tenant_id"]
    pregateste_firma(patron, f)
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % tid, {"luna_preluare": AZI.strftime("%Y-%m")}), "luna preluării")
    data_ref = (AZI.replace(day=1) - _dt.timedelta(days=1)).isoformat()
    _ok(_api(patron, "POST", "/tenants/%d/solduri" % tid, {"data_referinta": data_ref, "randuri": [
        {"cont": "4111", "debit": 1000}, {"cont": "401", "credit": 500}, {"cont": "5311", "debit": 300}, {"cont": "1012", "credit": 800}]}),
        "balanța de deschidere")
    rp = _ok(_api(patron, "POST", "/tenants/%d/parteneri" % tid, {"data_referinta": data_ref, "randuri": [
        {"cont": "4111", "cui": cui_cu_control(31183001), "denumire": "Client Audit F183 SRL", "debit": 1000},
        {"cont": "401", "cui": cui_cu_control(31183002), "denumire": "Furnizor Audit F183 SRL", "credit": 400}]}), "soldurile pe parteneri")
    # 4111 intră (1 rând), 401 e respins numit, cu cifrele (`solduri_parteneri_api.respinse_coerenta`)
    assert rp.get("randuri") == 1, rp
    resp = json.dumps(rp.get("respinse"), ensure_ascii=False)
    assert "pe 401, partenerii din fișier dau creditor 400,00 lei" in resp and "rândurile contului nu intră până nu se potrivesc" in resp, rp
    pg = patron.pg
    _control_firma(patron, f)
    pg.wait_for_selector(_F + "#cf-audit-run", timeout=30000)
    pg.click(_F + "#cf-audit-run")
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #cf-audit-istoric') || {innerText: ''}).innerText"
                         ".includes('Primul audit după preluare')", timeout=60000)
    text = " ".join(pg.inner_text(_F + "#cf-audit-istoric").split())
    pg.locator(_F + "#cf-audit-zona").scroll_into_view_if_needed()
    patron.captura()
    assert "Contul 4111: defalcarea pe parteneri (debitor 1.000,00 lei) coincide cu balanța." in text, text   # [C100] soldul cu felul lui
    # [lotul 11, C100] soldul cu felul lui (`pdf_util.sold`), nu „-500,00 lei”
    assert re.search(r"Contul 401: parteneri 0,00 lei vs balanță creditor 500,00 lei \(diferență 500,00 lei\)", text), text
    # titlurile grupelor („Coerent (5)”, „Divergent (1)”, control_verdict.js `grup`) ies cu majuscule din CSS în `inner_text`
    sus = text.upper()
    assert sus.index("COERENT (") < sus.index("CONTUL 4111:") < sus.index("DIVERGENT (") < sus.index("CONTUL 401:"), text
    assert pg.inner_text(_F + "#cf-audit-run").strip() == "Rerulează auditul"


# ── F072 — Canal de sesizări (Raportează) ────────────────────────────────────────────────────────────────────────────────────────
def test_pozitie_f072_sesizarea_cu_captura_primeste_raspunsul_echipei(browser, request, patron, fire_curate):
    """F072. Pașii: contabilul-șef -> Suport (banda „Raportează”) -> textul sesizării + o captură -> „Trimite”: „Sesizare trimisă.” ->
    echipa iConta (superadminul) -> Raportări: sesizarea, cu textul -> răspunsul scris -> „Trimite”: răspunsul e în fir -> contabilul-șef
    redeschide Suport: firul lui spune „răspuns primit”; deschis, arată răspunsul semnat „iConta.eu”, iar răspunsul devine citit.
    Triajul AI al sesizării e simulat de plasă (escaladează la echipă — `ICONTA_AI_SIMULAT`): sesizarea stă la Raportări, în fila
    escaladatelor."""
    ai_pregateste('{"decizie": "escaladez", "motiv": "proba F072"}')
    text = "F072 proba %d: totalul din balanță nu se potrivește cu registrul." % (int(time.time()) % 1000000)
    raspuns = "Răspuns F072: am verificat, totalul se reface la închiderea lunii."
    pg = patron.pg
    patron.acasa()
    pg.click("[data-banda='raport']")
    pg.wait_for_selector("#rap-text", timeout=20000)
    pg.fill("#rap-text", text)
    pg.set_input_files("#rap-file", files=[{"name": "captura_f072.png", "mimeType": "image/png", "buffer": PNG}])
    pg.click("#rap-trimite")
    pg.wait_for_selector("#rap-msg.msg-ok", timeout=20000)
    assert pg.inner_text("#rap-msg") == "Sesizare trimisă."
    (rid,), = sql("SELECT r.id FROM public.raportari r JOIN public.raportari_mesaje m ON m.raportare_id = r.id WHERE m.text = %s", (text,))
    for _ in range(60):   # triajul rulează în fundal (`raportari_ai.proceseaza`): escaladată = pentru echipă
        if sql("SELECT pentru_admin FROM public.raportari WHERE id = %s", (rid,)) == [(True,)]:
            break
        time.sleep(0.5)
    assert sql("SELECT pentru_admin FROM public.raportari WHERE id = %s", (rid,)) == [(True,)], "triajul n-a escaladat sesizarea"
    with ecran_cont(browser, request, _SUPERADMIN) as e:
        sp = e.pg
        e.acasa()
        sp.click("button.cab-card:has([data-cheie='raportari'])")
        sp.wait_for_selector("#rap-lista", timeout=20000)
        sp.click(".rap-tab[data-tab='tine']")   # escaladate de triaj
        sp.wait_for_function("(t) => [...document.querySelectorAll('#rap-lista .rap-rand')].some((r) => r.innerText.includes(t))",
                             arg=text[:40], timeout=20000)
        sp.locator("#rap-lista .rap-rand", has_text=text[:40]).first.click()
        sp.wait_for_function("(t) => (document.querySelector('#rap-mesaje') || {innerText: ''}).innerText.includes(t)", arg=text[:40],
                             timeout=20000)
        sp.fill("#rap-fir #rap-text", raspuns)
        sp.click("#rap-fir #rap-trimite")
        sp.wait_for_function("(t) => (document.querySelector('#rap-mesaje') || {innerText: ''}).innerText.includes(t)", arg=raspuns,
                             timeout=20000)
        e.captura("raspuns_echipei")
    assert sql("SELECT rol_autor FROM public.raportari_mesaje WHERE raportare_id = %s AND text = %s", (rid, raspuns)) == [("admin",)]
    patron.acasa()
    pg.click("[data-banda='raport']")
    fir = pg.locator(".rap-fir[data-id='%d']" % rid)
    fir.wait_for(timeout=20000)
    assert "răspuns primit" in fir.locator(".rap-fir-stare").inner_text(), fir.inner_text()
    assert fir.locator(".rap-badge-pct").count() == 1, "răspunsul echipei nu e marcat necitit"
    fir.locator(".rap-fir-cap").click()
    fir.locator(".rap-msg-admin", has_text=raspuns).wait_for(timeout=20000)
    autor = fir.locator(".rap-msg-admin", has_text=raspuns).locator(".rap-mesaj-cap b").inner_text()
    patron.captura()
    assert autor == "iConta.eu", autor
    for _ in range(40):
        if sql("SELECT citit FROM public.raportari_mesaje WHERE raportare_id = %s AND text = %s", (rid, raspuns)) == [(True,)]:
            break
        time.sleep(0.5)
    assert sql("SELECT citit FROM public.raportari_mesaje WHERE raportare_id = %s AND text = %s", (rid, raspuns)) == [(True,)]


# ── comanda 12.1 pct.7 — pozițiile pilot validate fără test propriu: F026, F087, F252, F254 ────────────────────────────────────────
def _valideaza_notele(e, f, inceput, sfarsit):
    """Date de PORNIRE: notele în ciornă ale perioadei, validate de contabilul-șef pe ruta butonului „Validează” din Registrul jurnal
    (validarea are pasul ei în scenariul pilotului, `e2e_pilot_luna.py::test_pilot_24_notele_lunii_validate`)."""
    for (nid,) in sql('SELECT id FROM "%s".inregistrari WHERE status <> \'validata\' AND data >= %%s AND data <= %%s ORDER BY data, id'
                      % f["schema"], (inceput, sfarsit)):
        _ok(_api(e, "POST", "/tenants/%d/jurnal/%d/valideaza" % (f["tenant_id"], nid), {}), "validarea notei %s" % nid)


def _pas2(e, f, tip, an, luna=None, trim=None):
    """Firma -> Declarații -> tipul -> perioada -> „Continuă →”: pasul 2, fără refuz."""
    pg = e.pg
    e.firma(f["nume"])
    pg.click("#fa-declaratii")
    pg.wait_for_selector(_F + "#dec-tip", timeout=30000)
    alege_tipul(pg, tip, zona=_F)
    alege_perioada(pg, an, luna, trim, zona=_F)
    pg.click(_F + "#dec-continua")
    pg.wait_for_function("() => { const t = [...document.querySelectorAll('.fereastra')].pop().innerText; "
                         "return t.includes('Pasul 2 din 3 — verifică') || !!document.querySelector('.fereastra:last-of-type .dec-eroare'); }",
                         timeout=120000)
    e.captura("%s_pas2" % tip)
    assert not pg.locator(_F + ".dec-eroare").count(), e.fereastra()[:3000]
    ok = pg.locator(_F + ".dec-ok")
    assert ok.count() == 1 and "fără erori" in ok.inner_text(), e.fereastra()[:3000]   # validatorul oficial DUKIntegrator
    return pg.locator(_F + "details.dec-xml:has(summary:text('Vezi XML-ul generat')) pre").first.text_content()


def _atr(xml, nume):
    m = re.search(r'\b%s="([^"]*)"' % nume, xml)
    return m.group(1) if m else None


# ── F026 — Declarația D100 (impozitul micro) ─────────────────────────────────────────────────────────────────────────────────────
def test_pozitie_f026_d100_micro_e_1_la_suta_din_veniturile_trimestrului(patron, firma_proaspata):
    """F026. Pașii: microîntreprinderea (vectorul fiscal: micro) cu două facturi de servicii în trimestrul încheiat (25.000,00 și 12.300,00
    lei pe 704, emise pe ruta formularului, notele validate) -> Declarații -> D100 -> trimestrul -> „Continuă”: validat cu DUKIntegrator,
    fără erori; rezumatul „cont 704: 37.300,00 lei” și „Baza impozabilă: 37.300,00 lei × cota 1% = cod 121: 373 lei (rotunjit la leu).”;
    XML-ul are obligația 121 cu suma 373 și cota 1."""
    f = firma_proaspata
    pregateste_firma(patron, f)
    p = perioada_incheiata("trimestrial")
    for zi, pret in ((p.inceput + _dt.timedelta(days=9), 25000.0), (p.sfarsit - _dt.timedelta(days=4), 12300.0)):
        emite_api(patron, f, linii=[{"descriere": PRODUS, "cantitate": 1, "um": "ora", "pret_unitar": pret, "cota_tva": 21, "cota_propusa": 21,
                                     "articol_id": None}], data_emitere=zi)
    _valideaza_notele(patron, f, p.inceput, p.sfarsit)
    xml = _pas2(patron, f, "d100", p.an, trim=p.trim)
    t = " ".join(patron.fereastra().split())
    baza = Decimal("37300.00")
    # CF art.51 alin.(1): „Cota de impozit pe veniturile microîntreprinderilor este de 1%” (la 01-01-2026, OUG 89/2025 art.I pct.4);
    # CF art.53 alin.(1): baza = veniturile; CF art.56 alin.(1): calculul și plata trimestrial; D100 suma_dat N(15) (d100_struct_anaf.txt)
    impozit = (baza * Decimal("0.01")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    assert "cont 704: 37.300,00 lei" in t, t[:3000]
    assert "Baza impozabilă: 37.300,00 lei × cota 1%% = cod 121: %s lei (rotunjit la leu)." % impozit in t, t[:3000]
    assert re.search(r'cod_oblig="121"[^>]*suma_dat="%s"' % impozit, xml) and 'cota="1"' in xml, xml[:3000]


# ── F087 — Statul de plată și fluturașii ─────────────────────────────────────────────────────────────────────────────────────────
def test_pozitie_f087_fluturasul_si_nota_statului_au_netul_statului(patron, firma_sal):
    """F087. Pașii: Salariați -> statul lunii trecute (salariatul cu 5.000 lei brut) -> „Fluturaș”: PDF-ul „Fluturaș de salariu — LL/AAAA”,
    cu „Salariu brut” = brutul și „Salariu net” = netul de pe rândul statului, CAS (25%) -> „Contabilizează statul”: „Contul 421 se
    soldează exact cu netul fluturașilor (<netul> lei).”"""
    _stat_luna(patron, firma_sal, luni_inapoi=1)
    s = _sume_salariat(patron)
    pg = patron.pg
    from e2e_lot13_sal_ajutor import buton, deschide_salariat, inchide
    deschide_salariat(patron)   # [lotul 13, 677] „Fluturaș” e butonul ferestrei salariatului
    with pg.expect_response(lambda r: "/fluturas/" in r.url, timeout=30000) as rr:
        buton(patron, "flut")
    text, _titlu = _pdf_text(_pdf_ok(patron, rr))
    inchide(patron)
    patron.captura("fluturas")
    assert "Fluturaș de salariu — %02d/%d" % (LUNA_TRECUTA.month, LUNA_TRECUTA.year) in text, text[:1500]
    # CF art.138 lit.a: CAS 25%; netul fluturașului = netul statului (aceeași sumă ca nota și D112)
    assert re.search(r"Salariu brut\s+%s" % re.escape(s["brut"][1]), text) and "CAS (25%)" in text, text[:2000]
    assert re.search(r"Salariu net\s+%s" % re.escape(s["net"][1]), text), text[:2000]
    with pg.expect_response(lambda x: "/salarii-contare/propunere" in x.url, timeout=90000):
        pg.click(_F + "#sp-contare")
    pg.wait_for_selector("#sp-contare-zona table", timeout=30000)
    patron.captura("propunerea")
    assert "Contul 421 se soldează exact cu netul fluturașilor (%s lei)." % s["net"][1] in patron.fereastra(), patron.fereastra()[:3000]


# ── F252 — Clasificare TVA pe factură ────────────────────────────────────────────────────────────────────────────────────────────
def test_pozitie_f252_tara_partenerului_duce_factura_pe_randul_ei_din_d300(patron, firma_proaspata):
    """F252. Pașii: Emite factură -> o zi din luna încheiată -> CUI-ul clientului din Irlanda (IE…): țara se pune singură „IE” -> operațiunea
    „normal” -> serviciul, 1 × 1.000,00, cota 0% -> categoria „serviciu_extern” (prestare cu locul în afara României, CF art.278 alin.(2))
    -> „Emite” -> nota validată -> Declarații -> D300 pe luna: validat cu DUKIntegrator; factura e pe rd.3 (R3_1 = 1.000) și rd.3.1
    (R3_1_1 = 1.000, din care servicii intracomunitare), nu pe rd.9 (21%)."""
    f = firma_proaspata
    pregateste_firma(patron, f)
    L = perioada_incheiata("lunar")
    zi = L.inceput.replace(day=12)
    _deschide_emiterea(patron, f["nume"])
    pg = patron.pg
    pg.fill("#em-data", zi.isoformat())
    pg.dispatch_event("#em-data", "change")
    pg.fill("#em-cui", "IE9999999ZZ")
    pg.dispatch_event("#em-cui", "change")
    pg.wait_for_function("() => document.querySelector('#em-tara').value === 'IE'", timeout=10000)
    pg.fill("#em-nume", "Client Irlanda F252 Ltd")
    pg.fill("#em-adresa", "1 Grand Canal Square")
    pg.fill("#em-oras", "Dublin")
    assert pg.input_value("#em-tipop") == "normal"
    pg.fill("#em-l0-descriere", PRODUS)
    pg.wait_for_function("() => document.querySelector('#em-l0-cota').value !== ''", timeout=20000)
    pg.fill("#em-l0-cantitate", "1")
    pg.fill("#em-l0-pret_unitar", "1000")
    pg.select_option("#em-l0-cota", "0")
    pg.wait_for_selector("#em-l0-categorie", state="visible", timeout=10000)
    pg.select_option("#em-l0-categorie", "serviciu_extern")
    with pg.expect_response(lambda r: r.url.endswith("/facturi/emite"), timeout=60000) as rr:
        pg.click("#em-emite")
    assert rr.value.status == 200, rr.value.text()[:300]
    fid = rr.value.json()["factura_id"]
    pg.wait_for_selector("#em-rezultat.em-bun", timeout=30000)
    patron.captura("emisa")
    assert sql('SELECT tert_tara, tip_operatiune FROM "%s".facturi WHERE id = %%s' % f["schema"], (fid,)) == [("IE", "normal")]
    _valideaza_notele(patron, f, L.inceput, L.sfarsit)
    xml = _pas2(patron, f, "d300", L.an, luna=L.luna)
    # CF art.278 alin.(2) (locul prestării la beneficiarul persoană impozabilă din UE) -> D300 rd.3 / rd.3.1 (OPANAF 174/2026)
    assert (_atr(xml, "R3_1"), _atr(xml, "R3_1_1"), _atr(xml, "R9_1")) == ("1000", "1000", None), xml[:3000]


# ── F254 — Factură emisă pe baza bonului fiscal ──────────────────────────────────────────────────────────────────────────────────
def test_pozitie_f254_factura_pe_bon_nu_se_numara_a_doua_oara(patron, firma_proaspata):
    """F254. Pașii: Raport Z -> o zi din luna încheiată, casa 8000000001, raportul 0254, total 21% 242,00 numerar, 3 bonuri -> „Generează
    notă” -> „Fără marfă din stoc” -> „Da, fără marfă” -> „Validează” -> Emite factură -> aceeași zi, DANTE -> serviciul, 1 × 100,00, 21% -> „Emisă pe baza
    bonului fiscal”: bonul 0002 din ziua Z-ului -> „Emite”: fără „Pleacă marfa acum?”, total 121,00 RON; factura n-are notă -> Declarații ->
    D394 pe luna: validat cu DUKIntegrator; factura e în op1 (L, DANTE, baza 100, TVA 21), iar Î1 (op2) are 1 casă, 3 bonuri și totalul
    242 − 121 = 121 (baza 100, TVA 21)."""
    f = firma_proaspata
    pregateste_firma(patron, f)
    L = perioada_incheiata("lunar")
    zi = L.inceput.replace(day=15)
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-raportz")
    pg.wait_for_selector("#z-salveaza", timeout=30000)
    for sel, v in (("#z-data", zi.isoformat()), ("#z-nui", "8000000001"), ("#z-nr", "0254"), ("#z-21", "242"), ("#z-num", "242"),
                   ("#z-card", "0"), ("#z-bonuri", "3")):
        pg.fill(sel, v)
    pg.click("#z-salveaza")
    pg.wait_for_function("() => (document.querySelector('#z-rezultat') || {innerText: ''}).innerText.includes('Notă generată')", timeout=30000)
    (zid,) = [r[0] for r in sql('SELECT id FROM "%s".inregistrari WHERE numar = %%s' % f["schema"], ("Z-8000000001-0254",))]
    pg.wait_for_selector(".zd-fara[data-z='%d']" % zid, timeout=20000)
    pg.click(".zd-fara[data-z='%d']" % zid)
    pg.click("#ca-ok")   # „Declari că în acest raport Z nu s-a vândut nicio marfă din stoc…?” -> „Da, fără marfă”
    pg.wait_for_selector("#zd-val-%d:not([aria-disabled='true'])" % zid, timeout=20000)   # [lotul 13, 675] butonul e mereu pe rând; activ după descărcare
    pg.click("#zd-val-%d" % zid)
    pg.wait_for_function("(z) => !document.querySelector('#zd-val-' + z)", arg=zid, timeout=30000)
    assert sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % f["schema"], (zid,)) == [("validata",)]
    _deschide_emiterea(patron, f["nume"])
    pg.fill("#em-data", zi.isoformat())
    pg.dispatch_event("#em-data", "change")
    for sel, v in CLIENT.items():
        pg.fill(sel, v)
    pg.fill("#em-l0-descriere", PRODUS)
    pg.wait_for_function("() => document.querySelector('#em-l0-cota').value === '21'", timeout=20000)
    pg.fill("#em-l0-cantitate", "1")
    pg.fill("#em-l0-pret_unitar", "100")
    pg.fill("#em-bon-nr", "0002")
    pg.fill("#em-bon-data", zi.isoformat())
    with pg.expect_response(lambda r: r.url.endswith("/facturi/emite"), timeout=60000) as rr:
        pg.click("#em-emite")
    assert rr.value.status == 200, rr.value.text()[:300]
    fid = rr.value.json()["factura_id"]
    pg.wait_for_selector("#em-rezultat.em-bun", timeout=30000)
    patron.captura("emisa")
    assert pg.locator("#em-poarta-da").count() == 0, "factura pe bon a întrebat „Pleacă marfa acum?”"
    assert "total 121,00 RON" in pg.inner_text("#em-rezultat"), pg.inner_text("#em-rezultat")
    # HG 1/2016 pct.97 alin.(1): factura „conform bon fiscal” — vânzarea e deja în raportul Z, deci nu primește notă de vânzare
    assert sql('SELECT count(*) FROM "%s".inregistrari WHERE factura_id = %%s' % f["schema"], (fid,)) == [(0,)]
    xml = _pas2(patron, f, "d394", L.an, luna=L.luna)
    op1 = [dict(re.findall(r'(\w+)="([^"]*)"', m)) for m in re.findall(r"<op1 ([^>]*?)/?>", xml)]
    assert [(o.get("tip"), o.get("cuiP"), o.get("baza"), o.get("tva")) for o in op1] == [("L", "14399840", "100", "21")], op1
    m = re.search(r"<op2 ([^>]*?)/?>", xml)
    a = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1))) if m else {}
    # OPANAF 2194/2025 anexa D394 lit.G: Î1 = încasările prin AMEF „cu excepția celor pentru care s-au emis facturi”
    assert (a.get("tip_op2"), a.get("nrAMEF"), a.get("nrBF"), a.get("total"), a.get("baza21"), a.get("TVA21")) == (
        "I1", "1", "3", "121", "100", "21"), a

