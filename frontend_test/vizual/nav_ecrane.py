# -*- coding: utf-8 -*-
"""Navigare reutilizabila la cele 5 ecrane problematice, pentru uneltele vizuale
(axe / mobil / baseline). Fiecare functie primeste pagina Playwright si o lasa pe
ecranul cerut, RANDAT (asteapta un marker DOM specific ecranului, nu doar timeout).

Sursa navigarii:
  - w_auth.deschide_firma  -> Firme -> Firme existente -> "Comert Micro TVA" (tenant_003)
  - #fa-import  -> meniuMigrarePerFirma -> cardurile de strat (static/js/ecrane/migrare.js)
  - #fa-salariati -> ecranSalariati, care randeaza "Stat de plata" (firme.js:499, h2.pf-titlu)
  - #fa-declaratii -> declaratiiPerFirma (firme.js:307)

Le foloseste axe_scan.py, mobil_scan.py, baseline_scan.py -> UN SINGUR loc de adevar
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
ECRANE = [
    ("import_mijloace_fixe", ecran_import_mijloace_fixe),
    ("vector_fiscal", ecran_vector_fiscal),
    ("plan_conturi", ecran_plan_conturi),
    ("solduri_parteneri", ecran_solduri_parteneri),
    ("stat_plata", ecran_stat_plata),
    ("declaratii", ecran_declaratii),
]
