# -*- coding: utf-8 -*-
"""Teste gardian pentru duk (partea pura, fara java)."""
import os
from core.duk import CHEIE_DUK, validatoare_instalate, poate_valida, valideaza


def _fals_dist(tmp, jars):
    lib = os.path.join(tmp, "lib")
    os.makedirs(lib, exist_ok=True)
    for j in jars:
        open(os.path.join(lib, j), "w").close()
    return tmp


def test_biblioteca_de_baza_nu_e_declaratie(tmp_path):
    d = _fals_dist(str(tmp_path), ["Validator.jar", "D112Validator.jar"])
    assert validatoare_instalate(d) == {"D112"}
    assert poate_valida("", d) is False


def test_backup_nu_conteaza_ca_instalat(tmp_path):
    d = _fals_dist(str(tmp_path), ["D300Validator.jar.bak_pre22042026"])
    assert validatoare_instalate(d) == set()


def test_validator_neinstalat_da_gri_nu_valid(tmp_path):
    """Un XML nevalidat NU se declara valid."""
    d = _fals_dist(str(tmp_path), [])
    r = valideaza("<x/>", "d300", dist=d)
    assert r["stare"] == "gri"
    assert "nu e instalat" in r["temei"]


def test_tip_necunoscut_da_gri(tmp_path):
    r = valideaza("<x/>", "d999", dist=str(tmp_path))
    assert r["stare"] == "gri"


def test_toate_declaratiile_din_dispecer_au_cheie():
    from core.declaratii_api import DECLARATII
    for tip in DECLARATII:
        assert tip in CHEIE_DUK, "tipul %s nu are cheie DUK" % tip


GUNOI = '<?xml version="1.0"?><aiurea xmlns="mfp:anaf:dgti:inventat:v99" x="1"/>'


def test_niciun_validator_nu_accepta_gunoi():
    """Un validator care nu poate spune NU nu e validator.

    15.07.2026: D406 raporta 'valid' pentru ORICE XML, inclusiv <aiurea/> cu namespace
    inventat - pentru ca era chemat cu jar-ul si parametrii altei declaratii ("-v D406"
    in loc de DUKIntegrator_AnLunaUI "-p D406 ... an= luna="), iesea tacut, fara fisier
    de erori, iar "fara erori" era interpretat drept "valid". Un fals verde e mai
    periculos decat o eroare: spune ca poti depune ceva ce ANAF respinge.
    """
    for tip in ("d100", "d101", "d112", "d205", "d300", "d301", "d390", "d394"):
        r = valideaza(GUNOI, tip)
        assert r["stare"] != "valid", "%s accepta gunoi ca valid" % tip


def test_d406_nu_accepta_gunoi_si_cere_an_luna():
    r = valideaza(GUNOI, "d406", an=2026, luna=6)
    assert r["stare"] != "valid"
    fara = valideaza(GUNOI, "d406")
    assert fara["stare"] == "gri" and "an si luna" in fara["temei"]


def test_saft_are_jar_propriu():
    """D406 e SAF-T: alt jar (AnLunaUI), -p in loc de -v, cu an=/luna=."""
    from core.duk import TIPURI_SAFT, JAR_SAFT
    assert "d406" in TIPURI_SAFT
    assert "AnLunaUI" in JAR_SAFT
def _apeluri_valideaza(src):
    """Extrage apelurile _duk.valideaza(...) cu paranteze ECHILIBRATE.
    Un regex [^)]* se opreste la prima paranteza inchisa - deci ar rata argumentele
    care contin apeluri (body.get("an")) si ar da fals-negativ. Dovedit 27.07.2026:
    prima versiune a acestei garzi picase pe cod CORECT, exact asa."""
    import re
    out = []
    for m in re.finditer(r"_duk\.valideaza\(", src):
        i = m.end(); adanc = 1
        while i < len(src) and adanc:
            if src[i] == "(": adanc += 1
            elif src[i] == ")": adanc -= 1
            i += 1
        out.append(src[m.start():i])
    return out


def test_ruta_valideaza_trimite_an_si_luna():
    """D406 (SAF-T) se valideaza cu jar separat care CERE an/luna ca parametri.
    Ruta care cheama duk.valideaza fara ele primeste GRI garantat - o validare care
    nu se intampla niciodata, fara ca nimic sa semnaleze. Dovedit 27.07.2026: asa a
    fost din constructie, desi XML-ul trecea la ANAF cand era rulat manual."""
    import pathlib
    src = (pathlib.Path(__file__).resolve().parent.parent / "main.py").read_text(encoding="utf-8")
    apeluri = _apeluri_valideaza(src)
    assert apeluri, "nu mai exista apel _duk.valideaza in main.py - actualizeaza garda"
    for a in apeluri:
        assert "an=" in a and "luna=" in a, "apel fara an/luna: %s" % a


def test_garda_apeluri_prinde_apelul_fara_an_luna():
    """Mutatie: pe un apel FARA an/luna garda trebuie sa vada lipsa; pe unul cu
    argumente imbricate trebuie sa le vada pe amandoua."""
    assert _apeluri_valideaza("rez = _duk.valideaza(xml, tip)") == ["_duk.valideaza(xml, tip)"]
    a = _apeluri_valideaza('_duk.valideaza(xml, tip, an=body.get("an"), luna=body.get("luna"))')[0]
    assert "an=" in a and "luna=" in a
