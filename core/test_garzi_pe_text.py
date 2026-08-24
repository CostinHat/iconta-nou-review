# -*- coding: utf-8 -*-
"""GARD PESTE GĂRZI — o gardă asertează pe STRUCTURĂ, nu pe text.

Regula, dată de Costin 24.08.2026. Motivul, cu instanțele — trei într-o singură zi, toate de forma
„caut un șir în ceva", toate în gărzi scrise de mine:

  1. două aserțiuni din `test_registru_jurnal_14_1_1` găseau `nr_curent` și `note_fara_document` în
     **docstringul rutei, scris de mine** — gardul trecea verde fără ca ruta să producă ceva;
  2. curățarea de docstring, la prima formă, ștergea și **SQL-ul din același f-string**, iar gardul
     acuza fals că numerotarea dispăruse — deci greșea în **ambele** direcții (METODA §22);
  3. a treia a fost **auto-referențială**: gardul citea documentația lucrului pe care îl păzea.

CLICHETUL E PE FIȘIER, NU GLOBAL. Un plafon global pe **fișiere** nu constrânge nimic înăuntru: un
fișier nou cu 40 de aserțiuni pe text ar urca numărul cu **unu** și ar trece. Aici fiecare fișier își
poartă cifra în `core/clichet_garzi_pe_text.json`, iar un fișier **nou pornește de la zero**.

CELE TREI SUB-CATEGORII SE NUMĂRĂ SEPARAT, fiindcă nu sunt același defect:
  - **sursa** (113) — se caută un șir în codul păzit; nu deosebește *implementat* de *descris*;
  - **randare** (6) — se caută în HTML; un `<div>` dintr-un comentariu trece la fel;
  - **reprezentare** (250) — `"x" in str(d)`. **Cea mai insidioasă**: *arată ca apartenență la o cheie
    și e sub-șir pe reprezentare.* `"total" in str(d)` trece și când `d = {"subtotal_vechi": 1}`.

CE NU VEDE, NUMĂRAT: din 1339 de aserțiuni, **899 (67%) rămân `nedeterminat`** — nu s-a putut
rezolva ce stă în dreapta lui `in`. Ele **nu** sunt raportate ca trecute. Deci **369 e un plafon
inferior**, nu un inventar, și se scrie cu semnul lui (METODA §22).

CIFRA 369 ȘI CIFRA 13 NU MĂSOARĂ ACELAȘI LUCRU. Interdicția 18 număra o clasă **îngustă** — gărzi
care își iau dovada din **documentația codului**. Asta e clasa **largă**: *orice aserțiune care poate
trece dintr-un motiv străin*. Două clase, iar cea largă n-a fost măsurată până azi.
"""
import io
import json
import os

import pytest

from core import scan_garzi_pe_text as _s

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLICHET = os.path.join(RAD, "core", "clichet_garzi_pe_text.json")


@pytest.fixture(scope="module")
def pin():
    return json.load(io.open(CLICHET, encoding="utf-8"))


@pytest.fixture(scope="module")
def acum():
    return _s.pe_fisier()


# ── clichetul, pe fișier ─────────────────────────────────────────────────────
def test_niciun_fisier_nu_creste(pin, acum):
    """Miezul. Fiecare fișier își păzește propria cifră — creșterea nu se poate ascunde în total."""
    pinat = pin["fisiere"]
    crescute = ["  %-58s %d -> %d" % (f, pinat.get(f, 0), k)
                for f, k in sorted(acum.items()) if k > pinat.get(f, 0)]
    assert not crescute, (
        "aserțiuni pe text în creștere:\n%s\n\nO gardă nouă care caută un șir într-un fișier, "
        "într-o randare sau în reprezentarea unei structuri păzește motivul străin de lângă lucru, "
        "nu lucrul. Asertează pe structură — câmp de JSON, element de XML, nod de AST — sau scrie "
        "lângă gardă de ce nu se poate." % "\n".join(crescute))


def test_un_fisier_NOU_porneste_de_la_zero(pin, acum):
    """Partea pe care un plafon global n-o poate face. Un fișier care nu e în pin are voie cu 0."""
    noi = ["  %-58s %d aserțiuni" % (f, k)
           for f, k in sorted(acum.items()) if f not in pin["fisiere"]]
    assert not noi, (
        "fișiere-gardă NOI care asertează pe text:\n%s\n\nUn fișier nou nu moștenește toleranța "
        "celor vechi." % "\n".join(noi))


def test_clichetul_nu_ramane_umflat(pin, acum):
    """Dacă se repară gărzi, cifrele coboară — altfel pinul devine loc gol pentru regresii tăcute."""
    scazute = [(f, k, acum.get(f, 0)) for f, k in pin["fisiere"].items() if acum.get(f, 0) < k]
    total_scapat = sum(k - n for _f, k, n in scazute)
    assert total_scapat <= 6, (
        "%d aserțiuni au fost reparate fără să coboare pinul (%d fișiere). Regenerează "
        "`core/clichet_garzi_pe_text.json`." % (total_scapat, len(scazute)))


# ── cele trei sub-categorii, numărate separat ────────────────────────────────
def test_cele_trei_categorii_se_numara_separat(pin):
    """Nu sunt același defect, deci nu se topesc într-o cifră."""
    acum = _s.pe_categorie()
    for cat in _s.CLASA:
        assert acum.get(cat, 0) <= pin["_categorii"][cat], (
            "categoria «%s» a crescut: %d -> %d" % (cat, pin["_categorii"][cat], acum.get(cat, 0)))


def test_reprezentarea_e_masurata_separat_fiindca_e_cea_insidioasa(pin):
    """`"x" in str(d)` arată ca apartenență la o cheie și e sub-șir. Dacă ar fi topită în total,
    n-ar exista nicio pârghie s-o ataci pe ea, care e cea mai mare dintre cele trei."""
    assert pin["_categorii"]["reprezentare"] > pin["_categorii"]["sursa"], (
        "presupunerea din antet nu mai ține — reordonează categoriile în text înainte de a le pina")


def test_ce_nu_se_vede_e_NUMARAT_nu_aruncat():
    """Zgomotul se numără. 67% nedeterminat înseamnă că 369 e plafon inferior, și se spune."""
    cat = _s.pe_categorie()
    assert cat.get("nedeterminat", 0) > 0, (
        "toate aserțiunile sunt rezolvate — dacă e adevărat, scoate avertismentul din antet")
    assert cat.get("container", 0) > 0, (
        "nicio aserțiune nu mai e recunoscută ca apartenență adevărată — clasificatorul s-a rupt "
        "și ar acuza forma corectă")


def test_anti_vacuu_domeniul_chiar_se_vede(acum):
    assert len(acum) >= 90, "scanul vede doar %d fișiere — domeniul s-a rupt" % len(acum)


# ── calibrare, AMBELE direcții (METODA §22) ──────────────────────────────────
def _scrie(tmp_path, nume, cod):
    d = tmp_path / "core"
    d.mkdir(exist_ok=True)
    io.open(str(d / nume), "w", encoding="utf-8").write(cod)
    return [str(d)]


def _categorii(rad):
    return {a["categorie"] for a in _s.aserțiuni(rad)}


def test_CALIBRARE_POZITIVA_sursa(tmp_path):
    """Direcția «ratează», categoria 1."""
    r = _scrie(tmp_path, "test_a.py", (
        "import io\n"
        "def test_x():\n"
        "    t = io.open('static/js/ecrane/cabinet.js').read()\n"
        "    assert 'pct-verde' in t\n"))
    assert _categorii(r) == {"sursa"}, _categorii(r)


def test_CALIBRARE_POZITIVA_reprezentare(tmp_path):
    """Categoria 3 — cea insidioasă. `d` chiar e un dict, dar `in` cade pe reprezentarea lui."""
    r = _scrie(tmp_path, "test_b.py", (
        "def test_x():\n"
        "    d = {'subtotal_vechi': 1}\n"
        "    assert 'total' in str(d)\n"))
    assert _categorii(r) == {"reprezentare"}, _categorii(r)


def test_CALIBRARE_POZITIVA_randare(tmp_path):
    r = _scrie(tmp_path, "test_c.py", (
        "def test_x(client):\n"
        "    html = client.get('/').text\n"
        "    assert '<main' in html\n"))
    assert _categorii(r) == {"randare"}, _categorii(r)


def test_CALIBRARE_NEGATIVA_apartenenta_adevarata_NU_e_acuzata(tmp_path):
    """Direcția «revendică». `in` pe un set CHIAR e apartenență — forma corectă nu se pedepsește,
    altfel clichetul s-ar putea trece mutând codul, nu reparându-l."""
    r = _scrie(tmp_path, "test_d.py", (
        "def test_x():\n"
        "    chei = {'nr_curent', 'document'}\n"
        "    assert 'nr_curent' in chei\n"))
    assert _categorii(r) == {"container"}, _categorii(r)


def test_CALIBRARE_operatorul_de_multime_iese_complet_din_domeniu(tmp_path):
    """Forma recomandată. `chei >= {"x"}` CRAPĂ pe un șir, în loc să treacă tăcut ca `in` — de aceea
    e ținta reparațiilor, și de aceea nu mai e nici măcar numărată."""
    r = _scrie(tmp_path, "test_e.py", (
        "def test_x():\n"
        "    chei = {'nr_curent'}\n"
        "    assert chei >= {'nr_curent'}\n"))
    assert not _s.aserțiuni(r), "forma pe operator de mulțime e încă numărată ca aserțiune pe text"
