# -*- coding: utf-8 -*-
"""GARD — raportul Search Console „Nu a fost găsită (404)” (lotul 9 pct.D2, comanda Costin 19.10.2026, verbatim în DECIZII „Comanda 9.1”).

Exportul din 18.10.2026 (`~/ghid_incoming/sc_404.zip`, 17 adrese, ultima accesare 30.07.2026) e copiat mai jos, cum l-a cules Google
(cu interogarea trunchiată: `/tva?an`). Două lucruri trebuie să țină împreună, altfel reparația nu ajunge la Google:

  1. fiecare adresă răspunde 410 (n-a fost niciodată o pagină și n-are succesor — `main.ADRESE_RETRASE`);
  2. Googlebot are VOIE s-o ceară: în spatele lui `Disallow: /` nu o mai cere, deci nu vede niciodată 410, iar raportul stă pe loc
     (17 adrese, neschimbat din 08.08 până la 12.10 în diagrama exportului).

Regula de potrivire din `robots.txt` e cea a lui Google (RFC 9309 §2.2.2): câștigă regula cea mai lungă; la egalitate, `Allow`; `$` = sfârșitul
căii, `*` = orice. Permisiunea e strict pe adresele retrase: rutele aplicației rămân `Disallow`.
"""
import re

import pytest

#: exportul „Nu a fost găsită (404)”, 18.10.2026 — cele 17 adrese, în ordinea din Tabel.csv
EXPORT_404_20261018 = ("/depune", "/functie", "/pachet/trimite?an", "/feedback/cabinet", "/auth/change-password", "/recomandari",
                       "/d205-beneficiari?an", "/facturi/primita", "/tva?an", "/inchidere?an", "/portal/documents/list", "/cost",
                       "/salariati", "/d406-mapare", "/d301-valideaza?an", "/situatii?an", "/nota-manuala")

#: rutele aplicației care trebuie să rămână închise crawlerului (vecine ale adreselor retrase, prefixe, resursa JS)
INCHISE = ("/tenants/2/salariati", "/coada/1/depune", "/tvaX", "/costuri", "/salariati/1", "/auth/me", "/auth/change-password/x",
           "/static/js/app.js", "/admin/versiune", "/portal/documents/list/2", "/migrare/salariati")


def _regex(regula):
    corp = re.escape(regula[:-1] if regula.endswith("$") else regula).replace(r"\*", ".*")
    return re.compile(corp + ("$" if regula.endswith("$") else ""))


def permis(robots, cale):
    """Google: regula cea mai lungă care se potrivește la începutul căii; la egalitate câștigă `Allow`; fără potrivire = permis."""
    reguli = re.findall(r"^(Allow|Disallow): (\S+)$", robots, re.M)
    potriviri = [(len(r), tip == "Allow") for tip, r in reguli if _regex(r).match(cale)]
    return max(potriviri)[1] if potriviri else True


@pytest.fixture(scope="module")
def c():
    from fastapi.testclient import TestClient
    import main
    return TestClient(main.app), main


def test_fiecare_adresa_din_export_raspunde_410(c):
    """MUTAȚIE: `/situatii` scos din `ADRESE_RETRASE` -> `/situatii?an` răspunde 404 -> ROȘU."""
    cl, _main = c
    coduri = {a: cl.get(a, follow_redirects=False).status_code for a in EXPORT_404_20261018}
    assert {a: k for a, k in coduri.items() if k != 410} == {}


def test_googlebot_are_voie_sa_vada_410(c):
    """MUTAȚIE: rândurile `Allow` ale adreselor retrase scoase din `public_robots` -> toate 17 blocate -> ROȘU."""
    cl, main = c
    t = cl.get("/robots.txt").text
    assert [a for a in EXPORT_404_20261018 if not permis(t, a)] == []
    assert [a for a in main.ADRESE_RETRASE if not permis(t, a)] == []


def test_rutele_aplicatiei_raman_inchise_crawlerului(c):
    """Permisiunea e numai pe calea exactă și pe forma ei cu interogare. MUTAȚIE: `$` scos din `Allow: %s$` -> `/tvaX`, `/costuri`,
    `/salariati/1` devin permise -> ROȘU."""
    cl, _main = c
    t = cl.get("/robots.txt").text
    assert [a for a in INCHISE if permis(t, a)] == []
    assert permis(t, "/") and permis(t, "/ghid/x") and not permis(t, "/tenants")


def test_potrivirea_robots_dupa_google():
    """Unealta de mai sus, pe exemplele din RFC 9309 / documentația Google (cea mai lungă regulă; `$`; egalitate -> Allow)."""
    r = "Allow: /p$\nDisallow: /\nAllow: /folder\nDisallow: /folder/x\n"
    assert permis(r, "/p") and not permis(r, "/p2") and not permis(r, "/a")
    assert permis(r, "/folder/page") and not permis(r, "/folder/x/y")
    assert permis("Allow: /a\nDisallow: /a\n", "/a")
