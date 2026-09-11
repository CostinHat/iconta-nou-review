# -*- coding: utf-8 -*-
"""core/test_gazda_productie.py — o verificare care loveste ALT domeniu nu e o verificare.

**Instanta, si e a mea.** Pe 11.09.2026, la construirea frontierei R68, scriptul meu verifica dupa
fiecare pas ca «site-ul raspunde 200». Lovea `iconta.ro`. Aplicatia e pe `iconta.eu`. `iconta.ro`
raspundea 200 tot timpul — inclusiv in cele doua ore in care aplicatia era CAZUTA cu 502. Am avut
patru verificari verzi la rand despre o lume pe care n-o vedeam.

Poarta care nu se uita la lucrul pazit e mai rea decat lipsa portii: lipsa se vede, verdele fals nu.

**Ce pazeste garda asta.** Gazda de productie e DECLARATA intr-un singur loc si comparata pe HOST,
nu pe subsir — `https://iconta.eu.atacator.tld` contine «iconta.eu» si nu e ea. Si orice fisier de
verificare din depozit care cere un domeniu public diferit pica.

**De ce esantionul de calibrare se compune la rulare** (`"iconta" + ".ro"`): daca l-as scrie
intreg, scanul si-ar gasi propria calibrare si ar trebui sa se excluda pe sine — iar o garda care
se exclude pe sine nu se mai poate proba pe sine.
"""
from __future__ import annotations

import io
import os
import re
from urllib.parse import urlsplit

import pytest

from core import sonda_web

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: fisierele care VERIFICA ceva: daca ele cer un domeniu, ala e domeniul pe care il cred adevarat
DIRECTOARE = ("scripts", "frontend_test", "core")

_URL = re.compile(r"https?://[A-Za-z0-9.\-]+")


def gazde_cerute(text):
    """Multimea HOST-urilor din text, ca host-uri — nu ca subsiruri.

    `urlsplit` da `netloc`, deci `https://iconta.eu.altceva.tld` iese cu host-ul lui adevarat, iar
    un `in` pe sir l-ar fi luat drept gazda noastra.
    """
    return {urlsplit(u).netloc.lower() for u in _URL.findall(text)}


def straine(text, gazda_buna):
    """Host-urile din text care par ale noastre dar NU sunt gazda declarata.

    «par ale noastre» = al doilea nivel de domeniu e acelasi (`iconta`), oricare ar fi extensia.
    Asa se prinde exact greseala mea — alt TLD pe acelasi nume —, fara sa se aprinda pe `anaf.ro`
    sau pe orice alt domeniu strain, care n-are ce cauta in comparatia asta.
    """
    bun = urlsplit(gazda_buna).netloc.lower()
    radacina_buna = ".".join(bun.split(".")[:-1]) if "." in bun else bun
    out = set()
    for g in gazde_cerute(text):
        if g == bun or not g:
            continue
        parti = g.split(".")
        if len(parti) >= 2 and ".".join(parti[:-1]).endswith(radacina_buna):
            out.add(g)
    return out


def _fisiere():
    for d in DIRECTOARE:
        rad = os.path.join(RADACINA, d)
        for dirpath, dirnames, filenames in os.walk(rad):
            dirnames[:] = [x for x in dirnames if x not in ("__pycache__", "venv", ".git")]
            for f in filenames:
                if f.endswith((".py", ".sh")):
                    yield os.path.join(dirpath, f)


# ============================================================
#  CALIBRARE — in ambele directii (METODA §22)
# ============================================================
def test_calibrare_prinde_alt_tld_pe_acelasi_nume():
    """Directia 1: exact greseala mea — `iconta` cu alt TLD — e prinsa."""
    gresit = "curl -s -o /dev/null -w '%%{http_code}' https://%s/" % ("iconta" + ".ro")
    assert straine(gresit, sonda_web.GAZDA_PRODUCTIE), (
        "scanul NU vede alt TLD pe acelasi nume — atunci n-ar fi prins nimic pe 11.09")


def test_calibrare_nu_se_aprinde_pe_gazda_buna_si_nici_pe_domenii_straine():
    """Directia 2. Fara asta, o garda care raporteaza ORICE ar trece prima proba degeaba."""
    assert straine("GET https://iconta.eu/ si https://anaf.ro/ si http://127.0.0.1:8010/",
                   sonda_web.GAZDA_PRODUCTIE) == set()


def test_calibrare_hostul_se_citeste_ca_host_nu_ca_subsir():
    """`https://iconta.eu.atacator.tld` CONTINE gazda buna si nu e ea. Pe subsir ar fi trecut."""
    g = gazde_cerute("https://iconta.eu.atacator.tld/x")
    assert g == {"iconta.eu.atacator.tld"}, g
    assert "iconta.eu" not in g


# ============================================================
#  GARDA
# ============================================================
def test_gazda_de_productie_e_declarata_intr_un_singur_loc():
    """Pe camp, nu pe text: constanta exista si e chiar gazda aplicatiei."""
    assert sonda_web.GAZDA_PRODUCTIE == "https://iconta.eu"
    assert urlsplit(sonda_web.GAZDA_PRODUCTIE).scheme == "https"


def test_sonda_locala_ramane_pe_proces_nu_pe_domeniu():
    """Sonda deadman cere procesul LOCAL, nu domeniul public — si asa trebuie sa ramana.

    Un `GET` prin nginx ar putea raspunde 200 dintr-un cache sau de la alt upstream, deci ar putea
    fi verde peste un proces mort. Cele doua intrebari sunt diferite si raman separate."""
    assert urlsplit(sonda_web.BAZA).hostname in ("127.0.0.1", "localhost")
    assert urlsplit(sonda_web.BAZA).port == 8010


@pytest.mark.parametrize("cale", sorted(_fisiere()))
def test_niciun_fisier_de_verificare_nu_cere_alt_domeniu_al_nostru(cale):
    """Clichet 0: niciun instrument de verificare nu are voie sa ceara alt domeniu de-al nostru."""
    text = io.open(cale, encoding="utf-8", errors="replace").read()
    gasite = straine(text, sonda_web.GAZDA_PRODUCTIE)
    assert not gasite, (
        "%s cere %s, dar gazda de productie e %s. O verificare care loveste alt domeniu poate fi "
        "verde peste o aplicatie cazuta — s-a intamplat pe 11.09."
        % (os.path.relpath(cale, RADACINA), sorted(gasite), sonda_web.GAZDA_PRODUCTIE))


def test_domeniul_public_chiar_raspunde():
    """ANTI-VACUU pentru garda de mai sus: daca lista de fisiere ar fi goala, toate probele de mai
    sus ar trece fara sa fi verificat nimic."""
    assert len(list(_fisiere())) > 50, "domeniul de cautare e prea mic — garda ar fi vida"
