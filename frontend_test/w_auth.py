# -*- coding: utf-8 -*-
"""Helper comun: auth mintuit + navigare la firma tenant_003. Import: from w_auth import *

[LOTUL 10, 04.09.2026] RECONSTRUIT din `__pycache__/w_auth.cpython-312.pyc`. Sursa fusese stearsa
de pe disc pe 26.08 odata cu `b87dad49` („Scoate din urmarire cele 234 de artefacte maturate din
greseala"), iar de atunci **24 de fisiere** — printre ele `interactiune_scan`, `axe_scan`,
`mobil_scan` si `nav_ecrane`, adica toata infrastructura vizuala gardata — se importau dintr-un
bytecode de 4,6 KB. Nimic nu era rosu: Python incarca `.pyc`-ul fara sa-i ceara sursa. *Un
`find -name __pycache__ -delete` — curatenia obisnuita — ar fi oprit tacut tot ce se sprijina
aici.* Vezi `core/test_infra_vizuala.py`, care de acum cere SURSA, nu doar importul.

[LOTUL 12, 04.09.2026] DOUA SCHIMBARI, amandoua cerute de aceeasi masuratoare.

**(1) Sesiunea nu se mai construieste de mana.** Pana azi `_utilizator()` cladea dictionarul
`iconta_user` camp cu camp, si TREI dintre campuri erau INVENTATE: `nume_tenant: None`,
`tenant_are_cabinet: False`, `bun_venit_vazut: True`. Pe rolul `admin_firma` cele trei se
nimereau adevarate, deci nimic n-a cazut vreodata. Pe rolul `client` sunt FALSE prin
constructie — `navigator.contextBara` randeaza chiar `nume_tenant` in bara —, deci prima proba
de portal ar fi masurat o bara goala si ar fi numit-o defect de ecran. Acum sesiunea vine din
`auth_api.sesiune_pentru_user`, adica exact functia pe care o cheama aplicatia la magic-link:
aceleasi campuri, acelasi SELECT, aceeasi verificare de `activ`. *O sonda care isi fabrica
singura intrarea dovedeste ca ecranul merge pe intrarea pe care i-o dai TU — R125.*

**(2) Firma nu mai e scrisa in cod.** `deschide_firma` avea „Comert Micro TVA" hardcodat, deci
orice unealta vizuala vedea numai starile pe care le produc datele acelei firme. Instanta care
a fortat schimbarea: `#fa-rip` NU se randeaza pe ea — cardul e al partidei simple, iar firma
campaniei e SRL —, deci ecranul RIP era nu „fara defect", ci NEATINS. *Punctul orb e FIRMA, nu
ecranul.* Numele ramane implicit acelasi, ca cele 24 de importuri sa nu se schimbe.
"""
import json
import os

from playwright.sync_api import sync_playwright  # noqa: F401  (reexportat: probele il importa de aici)

from core import db, auth_api

# [LOTUL 11, 04.09.2026] Adresa se poate schimba din afara. Regula casei spune ca reprobarea
# NU se face pe productie — procesul viu tine codul vechi pana la repornire, iar repornirea
# nu e a mea —, deci se ridica o instanta proaspata pe alt port. Pana azi asta era imposibil
# pentru orice unealta vizuala: adresa era scrisa in cod. Numele variabilei e cel pe care il
# foloseste deja hamul campaniei (`PROBA_BAZA`), ca sa fie una singura, nu doua.
BAZA = os.environ.get("PROBA_BAZA", "http://127.0.0.1:8010")
OUT = os.path.dirname(os.path.abspath(__file__))

# Subiectul implicit al infrastructurii vizuale, de la nasterea ei. Numit, nu presarat prin cod.
EMAIL_IMPLICIT = "patron@prisma-cont.test"
FIRMA_IMPLICITA = "Comert Micro TVA"


class ContInactiv(Exception):
    """Ridicata cand `sesiune_pentru_user` refuza — cont inexistent, inactiv, cabinet suspendat.

    DE CE O EXCEPTIE si nu un `return None`: un `None` s-ar fi scurs in `json.dumps` si ar fi
    produs un `sessionStorage` cu `null`, adica un ecran de login. Proba ar fi raportat „ecranul
    nu randeaza nimic" despre un CONT, nu despre un ecran. Masurat azi: din cele 14 conturi ale
    bazei, **4 sunt inactive** — printre ele singurul `angajat`, deci desktopul asistentului nu
    are subiect viu. Un refuz care numeste motivul se citeste; unul care randeaza login, nu.
    """


def _sesiune(email):
    """Token + user pentru un email, pe calea aplicatiei (`auth_api.sesiune_pentru_user`).

    Nu prin `/auth/login`: probele vizuale nu masoara autentificarea, iar o parola in fisier ar
    fi al doilea loc in care traieste un secret. Dar nici prin dictionar scris de mana — v.
    antetul, schimbarea (1)."""
    import psycopg2.extras as E
    try:
        db.init_pool()
    except Exception:  # noqa: BLE001
        pass
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=E.RealDictCursor) as cur:
            cur.execute("SELECT id FROM public.users WHERE email=%s", (email,))
            u = cur.fetchone()
        if not u:
            conn.rollback()
            raise ContInactiv("nu exista niciun cont cu emailul %r" % email)
        s = auth_api.sesiune_pentru_user(conn, u["id"])
        conn.rollback()
    if not s or not s.get("ok"):
        raise ContInactiv("%s: %s (%s)" % (email, (s or {}).get("mesaj", "refuz fara mesaj"),
                                           (s or {}).get("cod", "fara cod")))
    return s["token"], s["user"]


def init_pentru(email):
    """Scriptul de initializare a sesiunii pentru un anume cont — se da lui `add_init_script`.

    Fiecare ROL cere propriul context de browser: `app.js` alege desktopul din `sesiune.rol()`
    la pornire, deci un token schimbat in aceeasi fila nu schimba desktopul."""
    tok, user = _sesiune(email)
    return ("sessionStorage.setItem('iconta_token'," + json.dumps(tok) + ");"
            "sessionStorage.setItem('iconta_user'," + json.dumps(json.dumps(user)) + ");")


# Compatibilitate cu cele 24 de importuri: `INIT` ramane sesiunea patronului de cabinet.
INIT = init_pentru(EMAIL_IMPLICIT)


def new_page(pw, email=EMAIL_IMPLICIT):
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1200, "height": 1800})
    ctx.add_init_script(INIT if email == EMAIL_IMPLICIT else init_pentru(email))
    return b, ctx.new_page()


def deschide_firma(pg, nume=FIRMA_IMPLICITA):
    """Cabinet -> Firme -> Firme existente -> firma cu numele dat (implicit: tenant_003)."""
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000)
    pg.wait_for_timeout(300)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000)
    pg.wait_for_timeout(300)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000)
    pg.wait_for_timeout(300)
    pg.get_by_text(nume, exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-import, #fa-datefirma", timeout=12000)
    pg.wait_for_timeout(400)


def shot(pg, nume):
    pg.screenshot(path=os.path.join(OUT, "t003_" + nume + ".png"), full_page=True)


def txt(pg, sel):
    """Textul primului element care se potriveste, sau „" daca nu exista."""
    e = pg.query_selector(sel)
    return (e.inner_text() or "").strip() if e else ""
