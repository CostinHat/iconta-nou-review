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
from w_auth import BAZA, deschide_firma  # noqa: F401  (INIT aplicat de deschide_firma via context)


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
]
