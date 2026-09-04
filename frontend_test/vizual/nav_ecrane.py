# -*- coding: utf-8 -*-
"""Navigare reutilizabila la cele 5 ecrane problematice, pentru uneltele vizuale
(axe / mobil / baseline). Fiecare functie primeste pagina Playwright si o lasa pe
ecranul cerut, RANDAT (asteapta un marker DOM specific ecranului, nu doar timeout).

Sursa navigarii:
  - w_auth.deschide_firma  -> Firme -> Firme existente -> "Comert Micro TVA" (tenant_003)
  - #fa-import  -> meniuMigrarePerFirma -> cardurile de strat (static/js/ecrane/migrare.js)
  - #fa-salariati -> ecranSalariati, care randeaza "Stat de plata" (firme.js:499, h2.pf-titlu)
  - #fa-declaratii -> declaratiiPerFirma (firme.js:307)

Le foloseste axe_scan.py, mobil_scan.py, interactiune_scan.py -> UN SINGUR loc de adevar
pentru "ce inseamna ecranul X".
"""
from w_auth import BAZA, EMAIL_IMPLICIT, deschide_firma  # noqa: F401  (INIT aplicat via context)


def _import_strat(pg, eticheta):
    """Din firma deschisa: intra pe Import date si deschide stratul cu eticheta data."""
    pg.click("#fa-import")
    pg.wait_for_selector(".mig-card, .mig-strat, [class*='mig']", timeout=12000)
    pg.wait_for_timeout(500)
    pg.get_by_text(eticheta, exact=False).first.click(timeout=8000)
    pg.wait_for_timeout(1100)


def ecran_import_mijloace_fixe(pg):
    deschide_firma(pg)
    _import_strat(pg, "Mijloace fixe")


def ecran_vector_fiscal(pg):
    deschide_firma(pg)
    _import_strat(pg, "Vector fiscal")


def ecran_plan_conturi(pg):
    deschide_firma(pg)
    _import_strat(pg, "Plan de conturi")


def ecran_solduri_parteneri(pg):
    deschide_firma(pg)
    _import_strat(pg, "Solduri parteneri")


def ecran_stat_plata(pg):
    deschide_firma(pg)
    pg.click("#fa-salariati")
    pg.wait_for_selector("h2.pf-titlu, .ecran-nota", timeout=14000)
    pg.wait_for_timeout(1400)


def ecran_declaratii(pg):
    deschide_firma(pg)
    pg.click("#fa-declaratii")
    pg.wait_for_selector(".fereastra, .ecran-nota, h2", timeout=14000)
    pg.wait_for_timeout(1200)


# ordinea = ordinea din comanda lui Costin

def _ecran_shell(pg, fid):
    deschide_firma(pg)
    pg.click("#" + fid)
    pg.wait_for_timeout(1600)


def ecran_stocuri(pg): _ecran_shell(pg, "fa-stocuri")
def ecran_registratura(pg): _ecran_shell(pg, "fa-registratura")
def ecran_banca(pg): _ecran_shell(pg, "fa-banca")
def ecran_rapoarte(pg): _ecran_shell(pg, "fa-rapoarte")
def ecran_etransport(pg): _ecran_shell(pg, "fa-etransport")
def ecran_centrecost(pg): _ecran_shell(pg, "fa-centrecost")
def ecran_casa(pg): _ecran_shell(pg, "fa-casa")


# [R33 b'', 26.08.2026] Ecranul «Verificari» lipsea din inventarul vizual, desi e chiar ecranul
# pe care se randeaza verdictul de echilibru. Poarta verde vizuala (CLAUDE.md 2.3 pct.11) cere
# uneltele pe ECRANELE ATINSE — iar un ecran care nu e in lista nu poate fi atins de ele, deci
# regula trecea vid. Se asteapta randarea listei, nu doar un timeout.
# [LOTUL 11, 04.09.2026] «Date firma» a trecut din `ECRANE_CAMPANIE` in inventarul portii
# vizuale, prin chiar regula scrisa mai jos: lotul i-a ATINS JS-ul (R136 — ordinea celor trei
# scrieri). Un ecran atins primeste cele trei unelte pe el; unul doar probat, nu.
def ecran_datefirma(pg):
    deschide_firma(pg)
    pg.click("#fa-datefirma")
    pg.wait_for_selector("#df-salveaza, .ecran-nota", timeout=14000)
    pg.wait_for_timeout(1200)


def ecran_verificari(pg):
    deschide_firma(pg)
    pg.click("#fa-verificari")
    pg.wait_for_selector(".pf-lista, .pf-frand, .ecran-nota", timeout=14000)
    pg.wait_for_timeout(1200)

# [supervizor, 01.09.2026] PRIMUL ecran de CABINET din inventarul vizual — toate celelalte sunt de
# firma (deschide_firma + #fa-*). Nu se intra intr-o firma: se ramane pe desktopul cabinetului si se
# apasa cardul. Poarta verde vizuala (CLAUDE.md 2.3 pct.11) cere uneltele pe ecranele ATINSE, iar un
# ecran care nu e in lista nu poate fi atins de ele — regula ar trece VID, exact ca la «Verificari».
def ecran_supervizor(pg):
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000)
    pg.wait_for_timeout(300)
    pg.click("button.cab-card:has([data-cheie='supervizor'])", timeout=8000)
    # se asteapta RANDAREA (antetul supervizorului sau starea goala), nu doar un timeout
    pg.wait_for_selector(".sv-antet, .stare-goala", timeout=20000)
    pg.wait_for_timeout(800)


ECRANE = [
    ("supervizor", ecran_supervizor),
    ("import_mijloace_fixe", ecran_import_mijloace_fixe),
    ("vector_fiscal", ecran_vector_fiscal),
    ("plan_conturi", ecran_plan_conturi),
    ("solduri_parteneri", ecran_solduri_parteneri),
    ("stat_plata", ecran_stat_plata),
    ("declaratii", ecran_declaratii),
    ("stocuri", ecran_stocuri),
    ("registratura", ecran_registratura),
    ("banca", ecran_banca),
    ("rapoarte", ecran_rapoarte),
    ("etransport", ecran_etransport),
    ("centrecost", ecran_centrecost),
    ("casa", ecran_casa),
    ("verificari", ecran_verificari),
    ("datefirma", ecran_datefirma),
]


# ── LOTUL 11 (04.09.2026): cele 21 de ecrane de firma ramase ─────────────────
# DE CE O A DOUA LISTA, si nu `ECRANE` marita — masurat, nu presupus. Fiecare nume din `ECRANE` e
# cerut de `test_acoperire_vizuala.test_toate_ecranele_scanate` in artefactul vizual, iar
# `test_fara_violari` cade pe orice violare axe (desktop SI mobil), tinta de atingere sub 24px,
# revarsare la 393px sau eroare de consola. A muta cele 21 de mai jos in `ECRANE` ar fi, prin
# constructie, o campanie de ACCESIBILITATE — nu campania „vorbeste aplicatia cand primeste date
# gresite?". Sunt doua intrebari, cu doua costuri, si nu se decid una prin cealalta.
#
# CE RAMANE ADEVARAT: locul de adevar e tot UNUL — fisierul asta. Ce se declara e la ce raspunde
# fiecare lista. Iar regula portii verzi vizuale nu se schimba: **un ecran al carui JS se ATINGE
# trece in `ECRANE`, cu cele trei unelte rulate pe el.** Lista de mai jos e pentru ecranele pe care
# campania le PROBEAZA fara sa le atinga.
#
# Navigarea lor e aceeasi — deschide firma, apasa cardul —, deci se genereaza, nu se scrie de 21
# de ori. Un ecran care cere mai mult de o apasare primeste functie proprie, ca `_import_strat`.
_FA_CAMPANIE = [
    "fa-acces", "fa-balanta", "fa-bilant", "fa-bonuri", "fa-contracte", "fa-control",
    "fa-facturi", "fa-fisacont", "fa-jurnal", "fa-magazin", "fa-marja",
    "fa-mijloace", "fa-operatiuni", "fa-produse", "fa-raportz", "fa-regfiscal",
    "fa-reginventar", "fa-registre321", "fa-rip", "fa-solicitari",
]


def _fa_card(fid):
    """Inchide `fid` pe functie, nu pe variabila de bucla — altfel toate cele 21 ar deschide
    ultimul ecran, si raportul ar arata 21 de ecrane parcurse cu un singur ecran probat."""
    def f(pg):
        _ecran_shell(pg, fid)
    f.__name__ = "ecran_" + fid.replace("-", "_")
    return f


ECRANE_CAMPANIE = [(fid[3:].replace("-", "_"), _fa_card(fid)) for fid in _FA_CAMPANIE]

# ── LOTUL 12 (04.09.2026): ecranele care NU sunt ale unei firme ──────────────
# Cele doua liste de mai sus au acelasi drum de intrare: `deschide_firma` + un card `#fa-*`.
# Cele 33 de unitati ramase in campanie (`#462`–`#501`) sunt de alta natura: traiesc pe DESKTOPUL
# unui rol — cabinet, admin, portal — si nu se ajunge la ele prin nicio firma.
#
# DE CE POARTA FIECARE ECRAN UN CONT. `app.js` alege desktopul din `sesiune.rol()` **la pornire**
# (`randeaza()`, switch pe rol), deci rolul nu e un parametru al navigarii: e o proprietate a
# FILEI. Un `admin_*` cerut in aceeasi fila ca un ecran de cabinet ar randa desktopul cabinetului
# si sonda ar raporta „navigare esuata" despre un ecran care functioneaza. De-aia intrarile de
# aici sunt de TREI campuri, nu doua — iar hamul deschide cate un context per cont.
#
# MASURAT AZI, si de-aia lipseste desktopul asistentului (`asistent.js`): din cele 14 conturi ale
# bazei, singurul cu rol `angajat` e INACTIV, deci `sesiune_pentru_user` il refuza. Ecranul nu e
# „fara defect": e fara subiect. Se probeaza cand exista un asistent activ, prin calea aplicatiei
# (`/asistenti/{id}/reactiveaza`), nu printr-un UPDATE.
CONT_CABINET = EMAIL_IMPLICIT              # admin_firma, cabinetul 1968
CONT_ADMIN = "admin@prisma-cont.test"      # superadmin
CONT_TEST = "fir-intrare@prisma-cont.test"  # admin_firma al cabinetului de test 4163

# [LOTUL 12, `DECIZII.md` 31] A DOUA FIRMA, si de ce era obligatorie.
# `#fa-rip` — Registrul de incasari si plati — se randeaza numai la `regim_contabil == "simpla"`
# (`firme.js`, cardul `rip`), iar regimul se deriva din `tip_firma` (`migrare_api.regim_contabil`:
# `pfa` -> simpla, orice altceva -> dubla). Masurat INAINTE de a construi ceva: **toate cele 19
# firme din baza erau `srl`**. Deci nu era un ecran neprobat — era un ecran pe care nimeni nu-l
# putuse deschide vreodata, si toata ramura de partida simpla cu el.
#
# Firma s-a facut prin LANTUL APLICATIEI (`POST /tenants` cu `tip_firma: "pfa"`), nu printr-un
# `INSERT`, si la cabinetul declarat de TEST (4163), ca sa nu miste numaratoarea firmelor reale.
# CUI-ul ei trece cifra de control ANAF — cerinta `core/test_cui_cnp_test_valid.py`.
FIRMA_PFA = "PFA TEST PARTIDA SIMPLA"


def _desktop(pg, cont_marker=".cab-card"):
    """Desktopul rolului, RANDAT. Nu intra in nicio firma."""
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(cont_marker, timeout=15000)
    pg.wait_for_timeout(400)


def _card(pg, cheie, asteapta=".fereastra-corp"):
    """Desktop -> cardul cu `data-cheie` dat -> fereastra lui, randata."""
    _desktop(pg)
    pg.click("button.cab-card:has([data-cheie='%s'])" % cheie, timeout=8000)
    pg.wait_for_selector(asteapta, timeout=20000)
    pg.wait_for_timeout(900)


def _card_fn(cheie):
    """Inchide `cheie` pe functie, nu pe variabila de bucla — v. `_fa_card`."""
    def f(pg):
        _card(pg, cheie)
    f.__name__ = "ecran_card_" + cheie
    return f


def ecran_cab_desktop(pg):
    """Desktopul cabinetului insusi (`cabinet.js`) — nu deschide nicio fereastra."""
    _desktop(pg)


def ecran_admin_desktop(pg):
    """Desktopul de admin (`admin.js`). Markerul e cardul, ca la cabinet."""
    _desktop(pg)


def ecran_ansamblu(pg):
    """Semnul „?" din bara albastra — prezentarea de ansamblu, aceeasi pentru toate rolurile."""
    _desktop(pg)
    pg.click("#nav-ghid", timeout=8000)
    pg.wait_for_selector(".ans-continut, .ecran-nota", timeout=15000)
    pg.wait_for_timeout(800)


def ecran_clopot(pg):
    """Clopotelul de notificari din bara (`navigator.js`) — al doilea chirias al cojii."""
    _desktop(pg)
    pg.click("#nav-clopot", timeout=8000)
    pg.wait_for_timeout(1200)


def ecran_activitate_cabinet(pg):
    """Card «Activitate» -> meniu -> «Activitatea echipei» (`activitate_cabinet.js`)."""
    _card(pg, "activitate")
    pg.click("#opt-jurnal", timeout=8000)
    pg.wait_for_timeout(1400)


def ecran_tipare(pg):
    """Acelasi meniu, a doua optiune: «Tipare de erori» (`tipare.js`)."""
    _card(pg, "activitate")
    pg.click("#opt-tipare", timeout=8000)
    pg.wait_for_timeout(1400)


def ecran_recomanda(pg):
    """Cardul mic «Recomanda», singurul care nu e in grila (`#cab-recomanda-mic`)."""
    _desktop(pg)
    pg.click("#cab-recomanda-mic", timeout=8000)
    pg.wait_for_selector(".fereastra-corp", timeout=15000)
    pg.wait_for_timeout(900)


def ecran_admin_anunturi(pg):
    """Admin -> «Anunturi» -> pasul «Mesaj» (`admin.js::pasMesaj`).

    Meniul are doua optiuni: «Cabinete» (bifezi destinatarii) si «Mesaj». A doua duce DIRECT la
    formular — „nimic bifat = anuntul merge la toti" —, deci nu e nevoie de doua apasari. Scris de
    mana si nu lasat pe seama deschizatoarelor: acelea cauta „adauga/nou/emite", iar aici butonul
    se cheama «Mesaj». *Un deschizator gasit dupa nume n-ar fi ajuns niciodata aici, iar ecranul ar
    fi ramas cu `campuri=0` — adica NEPROBAT purtand numele unuia probat.*"""
    _card(pg, "anunturi")
    pg.click("#an-op-msg", timeout=8000)
    pg.wait_for_selector("#an-mesaj", timeout=12000)
    pg.wait_for_timeout(700)


def ecran_rip_pfa(pg):
    """Firma de PARTIDA SIMPLA -> «Incasari/plati» (`rip_ecran.js`, #492 / #455).

    Singurul ecran pe care lotul il probeaza pe a doua firma: comanda cere „doar ce nu se randeaza
    pe firma curenta", iar restul cardurilor sunt aceleasi. Ce DISPARE la partida simpla (Operatiuni
    speciale, Mijloace fixe, Centre de cost) se masoara si se scrie in registru, nu se probeaza aici
    — sunt ecrane deja parcurse pe firma de partida dubla."""
    deschide_firma(pg, FIRMA_PFA)
    pg.click("#fa-rip", timeout=8000)
    pg.wait_for_timeout(1800)


def ecran_control_verdict(pg):
    """Control fiscal -> PRIMA firma din lista -> corpul verdictului (`control_verdict.js`).

    Lista e sortata rosu-galben-verde-gri de `control.js`, deci „prima" e cea mai incarcata —
    ceea ce e exact ce vrem: un verdict gol n-ar avea ce randa."""
    _card(pg, "control")
    pg.wait_for_selector(".mig-frand", timeout=20000)
    pg.locator(".mig-frand").first.click(timeout=8000)
    pg.wait_for_timeout(1600)


def ecran_emitere(pg):
    """Firma -> «Facturi» -> deschizatorul de emitere (`emitere_ecran.js`, ecran propriu — #478).

    Lotul 11 a raportat `campuri=0` pe `fa-facturi` tocmai fiindca emiterea nu traieste acolo."""
    deschide_firma(pg)
    pg.click("#fa-facturi", timeout=8000)
    pg.wait_for_timeout(1400)
    pg.get_by_text("Emite", exact=False).first.click(timeout=8000)
    pg.wait_for_timeout(1600)


def ecran_flux_concediu(pg):
    """Firma -> «Salariați» -> fluxul de concediu (`flux_concediu.js`)."""
    deschide_firma(pg)
    pg.click("#fa-salariati", timeout=8000)
    pg.wait_for_selector("h2.pf-titlu, .ecran-nota", timeout=14000)
    pg.wait_for_timeout(1200)
    pg.get_by_text("Concedi", exact=False).first.click(timeout=8000)
    pg.wait_for_timeout(1500)


# (nume, cont, functie) — numele e cel al FISIERULUI din lista campaniei, ca sa se poata lega
# verdictul de randul `#nr` fara traducere.
ECRANE_CABINET = [
    ("cabinet_desktop", CONT_CABINET, ecran_cab_desktop),          # 472
    ("activitate_cabinet", CONT_CABINET, ecran_activitate_cabinet),  # 463
    ("tipare", CONT_CABINET, ecran_tipare),                        # 497
    ("asistenti", CONT_CABINET, _card_fn("asistenti")),            # 471
    ("capacitate", CONT_CABINET, _card_fn("capacitate")),          # 473
    # numele e «_portofoliu», nu «control»: `fa-control` din ECRANE_CAMPANIE e ecranul UNEI
    # firme (#436), asta e semaforul intregului portofoliu (#474). Coliziunea a fost prinsa de
    # aserțiunea de mai jos la prima rulare — doua ecrane diferite cu acelasi nume scurt.
    ("control_portofoliu", CONT_CABINET, _card_fn("control")),     # 474
    ("control_verdict", CONT_CABINET, ecran_control_verdict),      # 475
    ("pachete", CONT_CABINET, _card_fn("pachete")),                # 486
    ("raporteaza", CONT_CABINET, _card_fn("raport")),              # 490
    ("recomanda", CONT_CABINET, ecran_recomanda),                  # 491
    ("termene", CONT_CABINET, _card_fn("termene")),                # 496
    ("validat", CONT_CABINET, _card_fn("validat")),                # 498
    ("ansamblu", CONT_CABINET, ecran_ansamblu),                    # 469
    ("navigator_clopot", CONT_CABINET, ecran_clopot),              # 500
    ("emitere", CONT_CABINET, ecran_emitere),                      # 478
    ("flux_concediu", CONT_CABINET, ecran_flux_concediu),          # 481
    ("admin_desktop", CONT_ADMIN, ecran_admin_desktop),            # 464
    ("admin_anunturi", CONT_ADMIN, ecran_admin_anunturi),          # 464 (formularul)
    ("admin_raportari", CONT_ADMIN, _card_fn("raportari")),        # 467
    ("admin_activitate", CONT_ADMIN, _card_fn("activitate")),      # 465
    ("admin_analytics", CONT_ADMIN, _card_fn("analytics")),        # 466
    ("admin_sanatate", CONT_ADMIN, _card_fn("sanatate")),          # 468
    ("rip_pfa", CONT_TEST, ecran_rip_pfa),                         # 492 · 455
]

# ANTI-VACUU, aici si nu intr-un test: daca listele s-ar suprapune, un ecran ar fi parcurs de
# doua ori si ar parea acoperit de doua instrumente cand e acoperit de unul.
# [LOTUL 12] Perechea a devenit un TRIPLET, si aserțiunea numara perechile, nu una singura:
# scrisa cu doua nume, a treia lista ar fi intrat fara sa fie verificata de nimic.
_NUME = {"ECRANE": [n for n, _ in ECRANE],
         "ECRANE_CAMPANIE": [n for n, _ in ECRANE_CAMPANIE],
         "ECRANE_CABINET": [n for n, _, _ in ECRANE_CABINET]}
for _a in _NUME:
    assert len(_NUME[_a]) == len(set(_NUME[_a])), "nume repetat in %s" % _a
    for _b in _NUME:
        if _a < _b:
            assert not (set(_NUME[_a]) & set(_NUME[_b])), \
                "acelasi ecran in %s si %s: %s" % (_a, _b, set(_NUME[_a]) & set(_NUME[_b]))
