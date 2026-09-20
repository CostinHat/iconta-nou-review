# -*- coding: utf-8 -*-
"""Helper comun Sesiunea B / F1: auth prin UI (login-first, cont creat la etapa 1-2) + navigare la F1.

NU importa w_auth (acela mintuieste la import o sesiune pentru un user care nu mai exista). Aici totul
prin UI real. Reutilizat de probele pe etape (proba_f1_etapa3.py, ...)."""
import os

BAZA = os.environ.get("PROBA_BAZA", "http://127.0.0.1:8010")
OUT = os.path.dirname(os.path.abspath(__file__))

EMAIL = "contabil.b@sesiuneab.test"
PAROLA = "TestF1parola!2026"
F1_NUME = "F1 Comert Stoc SRL"


def shot(pg, nume):
    try:
        pg.screenshot(path=os.path.join(OUT, "f1_" + nume + ".png"), full_page=True)
    except Exception:
        pass


def login(pg):
    """Autentificare prin UI: Acces -> Intra in cont -> Sunt cabinet de contabilitate -> email+parola.
    Inchide modalul de bun-venit daca apare."""
    pg.goto(BAZA + "/", wait_until="domcontentloaded"); pg.wait_for_timeout(800)
    pg.wait_for_selector("#pagina-acces-btn", timeout=8000)
    pg.click("#pagina-acces-btn"); pg.wait_for_timeout(500)
    pg.wait_for_selector("#acces-intra", timeout=8000)
    pg.click("#acces-intra"); pg.wait_for_timeout(500)
    pg.get_by_text("Sunt cabinet de contabilitate", exact=False).first.click(timeout=8000)
    pg.wait_for_timeout(400)
    pg.wait_for_selector("#login-email", timeout=8000)
    pg.fill("#login-email", EMAIL); pg.fill("#login-parola", PAROLA)
    pg.click("#login-buton")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(600)
    for _ in range(3):
        pg.keyboard.press("Escape"); pg.wait_for_timeout(200)


def deschide_f1(pg):
    """Din dashboard: Firme -> Firme existente -> F1 -> ecran firma (carduri #fa-*)."""
    pg.goto(BAZA + "/", wait_until="domcontentloaded"); pg.wait_for_timeout(800)
    for _ in range(2):
        pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
    pg.wait_for_selector(".cab-card", timeout=10000)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(700)
    fe = pg.query_selector("text=Firme existente")
    if fe and fe.is_visible():
        fe.click(); pg.wait_for_timeout(700)
    pg.get_by_text(F1_NUME, exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-import, #fa-datefirma", timeout=12000); pg.wait_for_timeout(500)
