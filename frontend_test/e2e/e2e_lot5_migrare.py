# -*- coding: utf-8 -*-
"""Lotul 5 (comanda Costin 15.10.2026, verbatim în DECIZII): 270 — „Migrare cabinet” cu butoanele aplicațiilor (SAGA activ, WinMentor,
Ciel, SmartBill inactive), textul de sub ele și pașii adaptați SAGA; 270d — „Suport” → „Cerere import din altă aplicație”, cu fișierele
văzute doar de echipa iConta și de autor, șterse de cabinet; C36 — captura unei sesizări nu mai e publică la /static/raportari, ci în
depozitul privat (`core/fisiere_private.py`), descărcată numai prin ruta autentificată. Pe aplicația din index, pe baza de TEST.
Fișierele de import sunt cele inventate din `core/test_import_saga.py` (antetele din manualul SAGA C)."""
import os
import struct
import sys
import urllib.error
import urllib.request
import zlib

import pytest

from conftest import BAZA, Ecran, LAT, INALT, ai_pregateste, firma_noua, sesiune, sql

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_bloc_d import _api, _token   # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.test_import_saga import BALANTA_SAGA, _cp1250   # noqa: E402

PATRON, SUPERADMIN, ALT_CABINET = "patron@prisma-cont.test", "admin@prisma-cont.test", "fir-intrare@prisma-cont.test"

TEXT_B = [
    "Dacă aplicația ta nu are buton activ:",
    "Trimite-ne din «Suport» → «Cerere import din altă aplicație» o captură cu meniul de export din aplicația ta și exportul unei "
    "singure firme (balanța de verificare, partenerii cu soldurile lor, salariații, mijloacele fixe).",
    "Analizăm exportul și îți răspundem dacă și când îl putem prelua automat.",
    "Până atunci, poți începe preluarea cu pașii de mai jos, folosind șabloanele CSV sau Excel.",
    "Fișierele trimise sunt văzute doar de echipa iConta.eu, se folosesc numai pentru import și le poți șterge oricând.",
]
# [371, comanda Costin 8.2] Migrare cabinet arată toate straturile (și cele care erau numai în meniul firmei), din sursa unică
PASI = ["Firme", "Vector fiscal", "Solduri inițiale", "Solduri parteneri", "Salariați", "Asociați", "Mijloace fixe", "Istoric declarații",
        "Plan de conturi", "Import RIP (PFA)", "Articole și stoc inițial", "Rețete (HoReCa)"]
CSV_EXPORT = "Simbol cont;Denumirea contului;Sold final debitor;Sold final creditor\n5311;Casa în lei;300;0\n".encode("utf-8")


def _png():
    """O captură PNG adevărată, 2×2 px (se desenează în browser)."""
    def bloc(tip, date):
        return struct.pack(">I", len(date)) + tip + date + struct.pack(">I", zlib.crc32(tip + date) & 0xffffffff)
    pixeli = b"".join(b"\x00" + b"\x3d\x8f\xd6" * 2 for _ in range(2))
    return (b"\x89PNG\r\n\x1a\n" + bloc(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0)) + bloc(b"IDAT", zlib.compress(pixeli))
            + bloc(b"IEND", b""))


PNG = _png()


def _get(cale, email=None):
    """(status, octeți) — o descărcare pe ruta aplicației, ca `email` (sau fără autentificare)."""
    h = {"Authorization": "Bearer " + _token(email)} if email else {}
    try:
        with urllib.request.urlopen(urllib.request.Request(BAZA + cale, headers=h), timeout=60) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def _dir_fisiere():
    return os.environ["ICONTA_FISIERE_DIR"]


def _pe_disc(cale_rel):
    return os.path.isfile(os.path.join(_dir_fisiere(), cale_rel))


@pytest.fixture(scope="module")
def firma_270():
    for f in firma_noua():
        yield f


@pytest.fixture()
def superadmin(browser, request):
    ctx = browser.new_context(viewport={"width": LAT, "height": INALT})
    ctx.add_init_script(sesiune(SUPERADMIN))
    e = Ecran(ctx.new_page(), request.node.name + "_echipa")
    yield e
    ctx.close()
    assert not e.erori, e.erori[:3]


@pytest.fixture()
def fire_curate():
    """Firele de Suport puse de test se scot la final (mesajele și rândurile fișierelor cad în cascadă; fișierele de pe disc sunt ale
    plasei, în `ICONTA_FISIERE_DIR`)."""
    inainte = sql("SELECT coalesce(max(id), 0) FROM public.raportari")[0][0]
    yield
    sql("DELETE FROM public.raportari WHERE id > %s AND autor_id = (SELECT id FROM public.users WHERE email = %s)", (inainte, PATRON))


def _migrare(patron):
    pg = patron.pg
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='firme'])")
    pg.click("#opt-migrare")
    pg.wait_for_selector("#mig-aplicatii button[data-aplicatie]", timeout=20000)
    pg.wait_for_selector("#mig-meniu .mig-op", timeout=20000)


def _pas_firma(patron, titlu, firma):
    pg = patron.pg
    pg.locator("#mig-meniu .mig-op", has_text=titlu).first.click()
    pg.wait_for_selector(".mig-frand", timeout=20000)
    pg.locator(".mig-frand", has_text=firma["nume"]).first.click()
    pg.wait_for_selector("#mig-file", state="attached", timeout=10000)


def test_def_270_migrare_cabinet_butoanele_aplicatiilor_si_pasii_saga(patron, firma_270):
    """270 a–c. Firme → Migrare cabinet: sus patru butoane (SAGA, WinMentor, Ciel, SmartBill), numai SAGA activ, celelalte inactive cu
    motivul scris; dedesubt textul (b), cuvânt cu cuvânt; apoi pașii, ca până acum. SAGA → „Solduri inițiale” spune ce se scoate din SAGA
    și primește direct balanța SAGA (fără model); „Asociați” (SAGA n-are export citit) oferă modelul CSV, ca acum.
    MUTAȚIA din plasă: registrul aplicațiilor cu SAGA fără pași -> butonul SAGA inactiv -> ROȘU."""
    pg = patron.pg
    _migrare(patron)
    butoane = pg.eval_on_selector_all("#mig-aplicatii button[data-aplicatie]", "els => els.map(b => [b.textContent.trim(), b.disabled])")
    assert butoane == [["SAGA", False], ["WinMentor", True], ["Ciel", True], ["SmartBill", True]], butoane
    assert pg.inner_text("#mig-apl-inactive").strip() == ("WinMentor, Ciel și SmartBill: iConta.eu nu le citește încă exporturile. "
                                                          "Butonul devine activ când începe să le citească.")
    pg.click("#mig-apl-cum > summary")                 # [394] textul (b) stă pliat sub „Cum se face”: contabilul îl deschide
    text = pg.eval_on_selector_all("#mig-apl-text p, #mig-apl-text li", "els => els.map(e => e.innerText.trim())")
    assert text == TEXT_B, text
    assert pg.eval_on_selector_all("#mig-meniu .mig-op .mig-op-titlu", "els => els.map(e => e.textContent.trim())") == PASI
    patron.captura("butoane")

    pg.click("#mig-aplicatii button[data-aplicatie='saga']")
    pg.wait_for_selector("#mig-aplicatii button[data-aplicatie='saga'].buton-activ", timeout=20000)
    sub = pg.locator("#mig-meniu .mig-op", has_text="Solduri inițiale").first.inner_text()
    assert "Scoate din SAGA: balanța de verificare analitică (Situații › Contabile › Balanțe" in sub, sub
    assert "Scoate din SAGA" not in pg.locator("#mig-meniu .mig-op", has_text="Asociați").first.inner_text()
    patron.captura("saga_pasi")

    _pas_firma(patron, "Solduri inițiale", firma_270)
    assert pg.locator("#mig-model").count() == 0
    assert pg.inner_text("[data-export-pas='solduri']").startswith("Scoate din SAGA: balanța de verificare analitică")
    pg.set_input_files("#mig-file", files=[{"name": "balanta_saga.csv", "mimeType": "text/csv", "buffer": _cp1250(BALANTA_SAGA)}])
    pg.wait_for_selector("#mig-salveaza-sold", timeout=20000)
    t = patron.fereastra()
    assert "Soldurile s-au citit din coloanele „Solduri finale Debit” și „Solduri finale Credit”." in t, t[:1200]
    patron.captura("saga_balanta")

    _migrare(patron)                                   # alegerea se ține cât e deschisă fereastra; una nouă pornește fără aplicație
    assert pg.locator("#mig-aplicatii button.buton-activ").count() == 0
    pg.click("#mig-aplicatii button[data-aplicatie='saga']")
    pg.wait_for_selector("#mig-aplicatii button[data-aplicatie='saga'].buton-activ", timeout=20000)
    _pas_firma(patron, "Asociați", firma_270)
    assert pg.locator("[data-export-pas]").count() == 0
    with pg.expect_download() as d:
        pg.click("#mig-model")
    assert d.value.suggested_filename == "model_asociati.csv"
    patron.captura("saga_asociati_model")


def test_def_270_cerere_import_din_alta_aplicatie(patron, superadmin, fire_curate):
    """270 d. Suport → „Cerere import din altă aplicație”: aplicația + un export CSV + o captură → cererea apare în firul cabinetului și la
    echipa iConta (Panou Admin → Raportări), care descarcă exportul; un alt cabinet primește 404 la descărcare și la ștergere; cabinetul
    șterge exportul (din fir și de pe disc). MUTAȚIA din plasă: ștergerea care nu scoate fișierul de pe disc -> ROȘU."""
    pg = patron.pg
    patron.acasa()
    pg.click("[data-banda='raport']")
    pg.wait_for_selector(".rap-tab[data-tab='import']", timeout=20000)
    pg.click(".rap-tab[data-tab='import']")
    pg.fill("#imp-aplicatie", "WinMentor")
    pg.set_input_files("#imp-file", files=[{"name": "balanta_winmentor.csv", "mimeType": "text/csv", "buffer": CSV_EXPORT},
                                           {"name": "meniu_export.png", "mimeType": "image/png", "buffer": PNG}])
    pg.click("#imp-trimite")
    pg.wait_for_function("() => document.body.innerText.includes('Cererea de import a fost trimisă. Îți răspundem aici.')", timeout=20000)
    patron.captura("trimisa")
    (rid, tip, apl), = sql("SELECT id, tip, aplicatie FROM public.raportari WHERE autor_id = (SELECT id FROM public.users WHERE email=%s) "
                           "ORDER BY id DESC LIMIT 1", (PATRON,))
    assert (tip, apl) == ("cerere_import", "WinMentor")
    fis = sql("SELECT f.id, f.nume_orig, f.tip, f.cale, f.cabinet_id FROM public.fisiere_private f JOIN public.raportari_mesaje m "
              "ON m.id = f.mesaj_id WHERE m.raportare_id = %s ORDER BY f.id", (rid,))
    assert [(x[1], x[2]) for x in fis] == [("balanta_winmentor.csv", "csv"), ("meniu_export.png", "png")], fis
    cab = sql("SELECT accounting_firm_id FROM public.users WHERE email = %s", (PATRON,))[0][0]
    assert all(x[4] == cab and x[3].startswith("%d/" % cab) and _pe_disc(x[3]) for x in fis), fis
    csv_id, csv_cale = fis[0][0], fis[0][3]

    sp = superadmin.pg                                  # echipa iConta: Panou Admin -> Raportări -> cererea -> descarcă exportul
    sp.goto(BAZA + "/", wait_until="domcontentloaded")
    sp.wait_for_selector(".cab-grila", timeout=30000)
    sp.click("button.cab-card:has([data-cheie='raportari'])")
    sp.wait_for_selector(".rap-rand", timeout=20000)
    sp.locator(".rap-rand", has_text="Cerere import din WinMentor").first.click()
    sp.wait_for_selector("[data-descarca-fisier='%d']" % csv_id, timeout=20000)
    sp.wait_for_function("() => [...document.querySelectorAll('img[data-captura]')].some(i => i.naturalWidth > 0)", timeout=20000)
    with sp.expect_download() as d:
        sp.click("[data-descarca-fisier='%d']" % csv_id)
    assert d.value.suggested_filename == "balanta_winmentor.csv" and open(d.value.path(), "rb").read() == CSV_EXPORT
    superadmin.captura()

    assert _get("/raportari/fisiere/%d" % csv_id, ALT_CABINET)[0] == 404
    assert _api(ALT_CABINET, "DELETE", "/raportari/fisiere/%d" % csv_id)[0] == 404
    assert _get("/raportari/fisiere/%d" % csv_id)[0] == 401

    patron.acasa()                                      # cabinetul: firul -> „Șterge” pe export -> confirmă
    pg.click("[data-banda='raport']")
    pg.wait_for_selector(".rap-fir[data-id='%d']" % rid, timeout=20000)
    pg.click(".rap-fir[data-id='%d'] .rap-fir-cap" % rid)
    pg.click(".rap-fir[data-id='%d'] [data-sterge-fisier='%d']" % (rid, csv_id))
    pg.click("#ca-ok")
    pg.wait_for_function("(id) => !document.querySelector(`[data-sterge-fisier='${id}']`)", arg=csv_id, timeout=20000)
    assert pg.locator(".rap-fir[data-id='%d'] [data-fisier]" % rid).count() == 1
    patron.captura("sters")
    assert sql("SELECT count(*) FROM public.fisiere_private WHERE id = %s", (csv_id,)) == [(0,)]
    assert not _pe_disc(csv_cale)
    assert _get("/raportari/fisiere/%d" % csv_id, SUPERADMIN)[0] == 404


def test_def_c36_captura_sesizarii_nu_mai_e_publica(patron, fire_curate):
    """C36 (găsită de Code). Suport → „Sesizare nouă” + o captură: până azi captura se scria în `<static>/raportari/` și se deschidea la
    `/static/raportari/<nume>` fără autentificare. Acum: în directorul servit nu se scrie nimic, adresa veche dă 404, iar captura se
    deschide numai prin ruta autentificată — autorul și echipa iConta da, alt cabinet 404, fără autentificare 401; în fir se vede.
    MUTAȚIA din plasă: capturile scrise din nou în directorul servit -> ROȘU."""
    ai_pregateste('{"decizie": "escaladez", "motiv": "proba C36"}')
    pg = patron.pg
    patron.acasa()
    pg.click("[data-banda='raport']")
    pg.wait_for_selector("#rap-text", timeout=20000)
    pg.fill("#rap-text", "Proba C36: captura nu trebuie să fie publică.")
    pg.set_input_files("#rap-file", files=[{"name": "captura_c36.png", "mimeType": "image/png", "buffer": PNG}])
    pg.click("#rap-trimite")
    pg.wait_for_selector("#rap-msg.msg-ok", timeout=20000)
    assert pg.inner_text("#rap-msg") == "Sesizare trimisă."
    (fid, cale), = sql("SELECT f.id, f.cale FROM public.fisiere_private f JOIN public.raportari_mesaje m ON m.id = f.mesaj_id "
                       "JOIN public.raportari r ON r.id = m.raportare_id WHERE r.autor_id = (SELECT id FROM public.users WHERE email=%s) "
                       "ORDER BY f.id DESC LIMIT 1", (PATRON,))
    assert _pe_disc(cale)
    servit = os.path.join(os.path.dirname(_dir_fisiere()), "iconta_publicat", "static", "raportari")   # directorul servit de plasă
    assert not os.path.exists(servit), "s-a scris în directorul servit: %s" % os.listdir(servit)
    assert _get("/static/raportari/" + os.path.basename(cale))[0] == 404
    assert _get("/raportari/fisiere/%d" % fid)[0] == 401
    assert _get("/raportari/fisiere/%d" % fid, PATRON) == (200, PNG)
    assert _get("/raportari/fisiere/%d" % fid, SUPERADMIN) == (200, PNG)
    assert _get("/raportari/fisiere/%d" % fid, ALT_CABINET)[0] == 404
    pg.wait_for_selector(".rap-fir .rap-fir-cap", timeout=20000)
    pg.locator(".rap-fir .rap-fir-cap", has_text="Proba C36").first.click()
    pg.wait_for_function("(id) => { const i = document.querySelector(`img[data-captura='${id}']`); return i && i.naturalWidth > 0; }",
                         arg=fid, timeout=20000)
    patron.captura()
