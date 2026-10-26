# -*- coding: utf-8 -*-
"""Lotul 13 (comanda 13.1), deficiența 681 — căutarea globală din antet (decizia Costin 25.10.2026, excepție de la „fără funcții noi”).

Verbatim: „Căsuță de căutare în antet, mereu vizibilă; scrii o funcție, o declarație sau un nume («diurnă», «tichet», «D112», un salariat)
și te duce în fereastra potrivită, pentru firma în lucru. Proba: «Decont deplasare / diurnă» nu se găsește azi fără să știi că e în
Operațiuni → Personal și deconturi.”

CE FACE IMPOSIBIL:
  1. sursele să se rupă tăcut: cardurile ferestrei firmei și operațiunile speciale se citesc din `firme.js` / `operatiuni_ecran.js`; un
     registru redenumit sau mutat lasă căutarea fără ele -> pică (anti-vacuu: numărul lor, și „decont” cu titlul lui);
  2. proba lui Costin: „diurnă” / „diurna” / „decont deplasare” găsesc „Decont deplasare / diurnă” întâi;
  3. „D112” găsește declarația firmei, „tichet” Salariații, numele unui salariat pe salariat;
  4. firma altui cabinet să se poată citi prin căutare (ruta refuză ca orice rută a firmei).

Temei: N/A — funcție de interfață (DS cap.9 „Căutarea globală”).
"""
import pytest

from core import cautare as C

FIRMA = {"tenant_id": 1, "tip_firma": "srl", "salariati": [{"id": 7, "nume": "Ionescu", "prenume": "Vasile"}]}


def test_sursele_se_citesc_din_ecrane():
    """1. MUTAȚIE: `const REGISTRU = [` redenumit în `operatiuni_ecran.js` -> nicio operațiune -> pică."""
    carduri = {c["cheie"]: c for c in C.carduri_firma()}
    assert len(carduri) >= 30, len(carduri)
    assert carduri["casa"]["titlu"] == "Casă" and carduri["salariati"]["grup_titlu"] == "Zilnic", carduri["casa"]
    ops = {o["cheie"]: o for o in C.operatiuni()}
    assert len(ops) >= 25, len(ops)
    assert ops["decont"]["titlu"] == "Decont deplasare / diurnă" and ops["decont"]["cat"] == "Personal și deconturi", ops["decont"]
    # etichetele câmpurilor decontului (formularul îl schimbă zona OPS — 670): se caută pe ele, nu pe o etichetă anume
    assert any(c.startswith("Diurna") for c in ops["decont"]["campuri"]) and len(ops["decont"]["campuri"]) >= 8, ops["decont"]["campuri"]


@pytest.mark.parametrize("q", ["diurnă", "diurna", "DIURNA", "decont deplasare", "Diurnă acordată"])
def test_proba_lui_costin_decontul_de_deplasare_se_gaseste(q):
    """2. Proba lui Costin, scrisă cum o scrie contabilul (cu / fără diacritice, cu majuscule, pe eticheta unui câmp)."""
    r = C.cauta(q, FIRMA)
    assert r and r[0]["fel"] == "operatiune" and r[0]["cheie"] == "decont", r
    assert r[0]["unde"] == "Operațiuni speciale › Personal și deconturi"
    assert r[0]["ruta"] == "nota-decont-deplasare"


def test_declaratia_tichetul_si_salariatul():
    """3. MUTAȚIE: `SINONIME` golit -> „tichet” nu găsește Salariați -> pică."""
    d = C.cauta("D112", FIRMA)
    assert d[0]["fel"] == "declaratie" and d[0]["tip"] == "d112" and "contribuțiilor sociale" in d[0]["titlu"], d[:2]
    t = C.cauta("tichet", FIRMA)
    assert t[0]["fel"] == "card" and t[0]["cheie"] == "salariati", t
    s = C.cauta("ionescu", FIRMA)
    assert s == [{"fel": "salariat", "id": 7, "titlu": "Ionescu Vasile", "unde": "Salariați", "actiune": None}], s
    assert C.cauta("casa", FIRMA)[0]["cheie"] == "casa"        # „casa” la început de cuvânt: Casă, nu „încasare”
    assert C.cauta("a", FIRMA) == []                            # un caracter nu caută
    # diacriticele din MIJLOCUL cuvântului: „decontari asociati” găsește „Decontări asociați”. MUTAȚIE: `normalizeaza` fără scoaterea
    # semnelor diacritice -> pică (prefixul „diurna” din „diurnă” trecea și fără ea)
    assert C.cauta("decontari asociati", FIRMA)[0]["cheie"] == "asociati"


def test_pfa_nu_primeste_operatiunile_partidei_duble():
    """Cardurile cu regimul altei partide nu apar (DS cap.18): la PFA, nici „Operațiuni speciale” (partidă dublă), nici operațiunile lui."""
    r = C.cauta("diurnă", dict(FIRMA, tip_firma="pfa"))
    assert all(x["fel"] != "operatiune" for x in r), r


def _sesiune(email):
    from core import auth_api, db
    try:
        db.init_pool()
    except Exception:  # noqa: BLE001 — deja inițializat
        pass
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, accounting_firm_id FROM public.users WHERE email = %s", (email,))
            u = cur.fetchone()
            if not u:
                pytest.fail("contul de test %s lipsește din baza de test" % email)
            cur.execute("SELECT id FROM public.tenants WHERE accounting_firm_id = %s ORDER BY id LIMIT 1", (u[1],))
            al_lui = cur.fetchone()
            cur.execute("SELECT id FROM public.tenants WHERE accounting_firm_id IS DISTINCT FROM %s ORDER BY id LIMIT 1", (u[1],))
            strain = cur.fetchone()
        s = auth_api.sesiune_pentru_user(conn, u[0])
        conn.rollback()
    return {"Authorization": "Bearer " + s["token"]}, al_lui and al_lui[0], strain and strain[0]


def test_ruta_citeste_numai_firma_cabinetului():
    """4. Ruta reală, cu contul contabilului-șef de test: firma lui -> rezultate; firma altui cabinet -> 404, ca orice rută a firmei.
    MUTAȚIE: `_schema_sau_404` scos din `cauta_pentru` -> firma străină se citește -> pică."""
    import main
    from fastapi.testclient import TestClient
    h, al_lui, strain = _sesiune("patron@prisma-cont.test")
    c = TestClient(main.app)
    r = c.get("/eu/cautare", params={"q": "diurnă", "tenant_id": al_lui}, headers=h)
    assert r.status_code == 200 and r.json()["rezultate"][0]["cheie"] == "decont", r.text[:300]
    fara = c.get("/eu/cautare", params={"q": "diurnă"}, headers=h)
    assert fara.status_code == 200 and fara.json()["rezultate"][0]["cheie"] == "decont", fara.text[:300]
    if strain:
        r2 = c.get("/eu/cautare", params={"q": "diurnă", "tenant_id": strain}, headers=h)
        assert r2.status_code == 404, r2.text[:300]
    assert c.get("/eu/cautare", params={"q": "diurnă"}).status_code in (401, 403)
