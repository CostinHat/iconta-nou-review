# -*- coding: utf-8 -*-
"""GARD — validatoarele DUK instalate sunt cele PUBLICATE de ANAF (comanda Costin 07.10.2026, C3).

Instanța: D112 instalat J27.0.1, publicat J27.0.6 (14.09.2026) — regula salariului minim se corectase în J27.0.2, iar validatorul
vechi semnala un D112 corect (B4_5P 4.125 pe 09/2026, OUG 89/2025 art.III alin.(5) lit.b); încă 4 validatoare erau în urmă.
CE FACE IMPOSIBIL: (1) un jar de validator schimbat sau înlocuit fără manifest; (2) un manifest care spune altă versiune decât
copia oficială `anaf_surse/versiuni.xml`; (3) o comparație cu ANAF mai veche de `ZILE_MAX` zile. LIMITA: poarta n-are rețea — un
validator publicat AZI poate rămâne neinstalat cel mult `ZILE_MAX` zile, până când garda (3) cere `verifica_duk_publicat.py`.
"""
import datetime
import io
import json
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import verifica_duk_publicat as V  # noqa: E402

MAN = json.load(io.open(V.MANIFEST, encoding="utf-8"))


def test_manifestul_acopera_toate_validatoarele_instalate():
    """MUTAȚIE: un validator scos din manifest -> pică (nu se poate instala unul nou „pe lângă”)."""
    in_manifest = {v["jar"] for v in MAN["validatoare"].values()}
    assert len(V.instalate()) > 50                          # premisă: directorul DUK chiar s-a citit
    assert sorted(set(V.instalate()) - in_manifest) == []


def test_jarurile_instalate_sunt_cele_din_manifest():
    """MUTAȚIE: un jar înlocuit (de ex. copia veche D112 J27.0.1 pusă la loc) -> sha256 diferit -> pică."""
    diferite = sorted(t for t, v in MAN["validatoare"].items() if V.sha(os.path.join(V.LIB, v["jar"])) != v["sha256"])
    assert diferite == []


def test_manifestul_spune_versiunile_din_copia_oficiala():
    """MUTAȚIE: versiunea D112 din manifest dată înapoi la J27.0.1 -> pică."""
    oficial = V.versiuni(io.open(V.VERSIUNI_LOCAL, encoding="utf-8").read())
    diferite = sorted(t for t, v in MAN["validatoare"].items() if oficial.get(t, ("?",))[0] != v["versiuneJ"])
    assert diferite == []


def test_comparatia_cu_anaf_nu_e_mai_veche_de_o_luna():
    """Pică singur după ZILE_MAX zile fără `scripts/verifica_duk_publicat.py --scrie` — asta e chiar garda."""
    zile = (datetime.date.today() - datetime.date.fromisoformat(MAN["verificat_la"])).days
    assert zile <= V.ZILE_MAX, ("comparația validatoarelor DUK cu ANAF are %d zile — rulează scripts/verifica_duk_publicat.py, "
                                "instalează ce e în urmă, apoi --scrie" % zile)
