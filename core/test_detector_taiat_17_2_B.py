# -*- coding: utf-8 -*-
"""Lotul 17.2-B (unelte) — detectorul de text tăiat și matricea lui (scripts/text_taiat_masuri.js, scripts/matrice_text_taiat.py). Fără 8019 și fără Chromium."""
import csv
import hashlib
import json
import os
import subprocess
import sys

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import matrice_16_7  # noqa: E402
import matrice_text_taiat as M  # noqa: E402

FISIERE_VERIFICATOR = ("scripts/verificator_design.py", "scripts/verificator_design_masuri.js", "scripts/matrice_16_7.py", "scripts/calibreaza_16_7.py")


def _js_sintetic(numar_pe_tip=None, stare="ok", eroare=None):
    """JSON-ul unui ecran, cum îl scrie verificator_design.ecran, cu rezultatul detectorului în `masuri_alt`."""
    taiate = [{"tip": t, "selector": "div.x", "text": "t", "w": 1, "sw": 2, "h": 3, "sh": 4, "proba": False} for t, n in (numar_pe_tip or {}).items() for _ in range(n)]
    return {"pica": {}, "eroare_deschidere": eroare, "masuri_alt": {"taiate": taiate, "numar": len(taiate), "numar_fara_proba": len(taiate), "ferestre": 1}}


def _randuri_sintetice(n):
    randuri = []
    for i in range(n):
        rez = M.REZOLUTII[i % len(M.REZOLUTII)]
        js = _js_sintetic({"lat": i % 3, "inalt": 1, "iesit": 0})
        if i == 1:
            js = M.STARE_TIMEOUT
        if i == 2:
            js = _js_sintetic(eroare="butonul nu există")
        if i == 4:
            js = None
        randuri.append(M.rand_ecran("Ecran %d" % (i // 3), rez, js))
    return randuri


def test_detectorul_e_o_singura_expresie_cu_cele_trei_tipuri():
    js = open(M.JS, encoding="utf-8").read().strip()
    assert js.startswith("//") or js.startswith("(")
    corp = "\n".join(ln for ln in js.splitlines() if not ln.lstrip().startswith("//")).strip()
    assert corp.startswith("(() => {") and corp.endswith("})()")
    for tip in ('"lat"', '"inalt"', '"iesit"'):
        assert tip in js
    assert "data-proba-17-2-b" in js
    assert not corp.startswith("const ") and "export " not in corp


def test_csv_si_rezumat_se_scriu_din_json_sintetic_iar_timeout_si_nedeschis_sunt_numarate(tmp_path):
    randuri = _randuri_sintetice(315)
    assert M.scrie_rezultate(randuri, str(tmp_path), "proba-eticheta", 12) == 0
    rows = list(csv.reader(open(tmp_path / "baza_text_taiat.csv", encoding="utf-8")))
    assert rows[0] == ["ecran", "rezoluție", "număr", "lat", "inalt", "iesit", "stare", "motiv"] and len(rows) == 316
    pe_stare = {s: sum(1 for r in rows[1:] if r[6] == s) for s in ("ok", "timeout", "nedeschis")}
    assert pe_stare["timeout"] == sum(1 for r in randuri if r["stare"] == "timeout") > 0
    assert pe_stare["nedeschis"] == sum(1 for r in randuri if r["stare"] == "nedeschis") > 0
    assert all(r[7] for r in rows[1:] if r[6] != "ok")   # niciun nedeschis/timeout fără motiv
    rez = open(tmp_path / "rezumat.txt", encoding="utf-8").read().splitlines()
    assert rez[0] == "proba-eticheta"
    for rz in M.REZOLUTII:
        linie = next(ln for ln in rez if ln.startswith(rz + ":"))
        pe = [r for r in rows[1:] if r[1] == rz]
        assert "tăieturi=%d " % sum(int(r[2] or 0) for r in pe) in linie
        assert "nedeschis=%d" % sum(1 for r in pe if r[6] == "nedeschis") in linie and "timeout=%d" % sum(1 for r in pe if r[6] == "timeout") in linie
    assert any(ln.strip().endswith("butonul nu există") for ln in rez)
    json_ = json.load(open(tmp_path / "baza_text_taiat.json", encoding="utf-8"))
    assert len(json_) == 315


def test_jsonul_taie_la_50_de_intrari_pe_ecran_dar_csv_pastreaza_numarul_complet(tmp_path):
    randuri = [M.rand_ecran("E%d" % (i // 3), M.REZOLUTII[i % 3], _js_sintetic({"lat": 70})) for i in range(315)]
    M.scrie_rezultate(randuri, str(tmp_path), "x", 1)
    assert all(len(r["taiate"]) == 50 for r in json.load(open(tmp_path / "baza_text_taiat.json", encoding="utf-8")))
    assert list(csv.reader(open(tmp_path / "baza_text_taiat.csv", encoding="utf-8")))[1][2] == "70"


@pytest.mark.parametrize("n", [0, 314, 316, 210])
def test_refuz_cu_1_cand_numarul_de_randuri_nu_e_315(tmp_path, n):
    assert M.scrie_rezultate(_randuri_sintetice(n), str(tmp_path), "x", 1) == 1


def test_rezolutiile_sunt_cele_trei_iar_matricea_16_7_ramane_neschimbata():
    assert M.REZOLUTII == ("603x590", "1366x768", "2133x1111")
    assert matrice_16_7.REZOLUTII == ("1920x1080", "1366x768")


def test_scriptul_nu_modifica_fisierele_verificatorului(tmp_path):
    def hash_uri():
        return {f: hashlib.sha256(open(os.path.join(RAD, f), "rb").read()).hexdigest() for f in FISIERE_VERIFICATOR}
    inainte = hash_uri()
    M.scrie_rezultate(_randuri_sintetice(315), str(tmp_path), "x", 1)
    assert hash_uri() == inainte
    for f in FISIERE_VERIFICATOR:   # și față de blob-ul din git de la HEAD
        blob = subprocess.run(["git", "rev-parse", "HEAD:" + f], cwd=RAD, capture_output=True, text=True).stdout.strip()
        assert blob == subprocess.run(["git", "hash-object", f], cwd=RAD, capture_output=True, text=True).stdout.strip()


def test_iesire_si_eticheta_sunt_respectate_iar_calibrarea_se_citeste_din_acelasi_director(tmp_path, monkeypatch):
    sha = M.git("rev-parse", "HEAD").strip()
    (tmp_path / "calibrare.txt").write_text("x\nabateri: 0 sha=%s\n" % sha, encoding="utf-8")
    capturat = {}
    import calibreaza_16_7 as C
    monkeypatch.setattr(C, "ruleaza_pe_server", lambda nume, corp, scrie_sha=None: corp())
    monkeypatch.setattr(M, "matrice", lambda iesire, eticheta: capturat.update(iesire=iesire, eticheta=eticheta) or 0)
    assert M.main(["matrice", "--iesire", str(tmp_path), "--eticheta", "dupa"]) == 0
    assert capturat == {"iesire": str(tmp_path), "eticheta": "dupa"}
    monkeypatch.undo()
    M.scrie_rezultate(_randuri_sintetice(315), str(tmp_path / "alt"), "eticheta-mea", 1)
    assert open(tmp_path / "alt" / "rezumat.txt", encoding="utf-8").readline().strip() == "eticheta-mea"
    assert M.calibrare_la_zi(str(tmp_path)) is None


@pytest.mark.parametrize("continut", [None, "calibrare\nabateri: 1 sha=%(sha)s\n", "calibrare\nabateri: 0 sha=0000000\n", "calibrare\nabateri: 0 sha=%(sha)s\nîn plus\n"])
def test_matricea_refuza_cu_1_fara_nicio_deschidere_daca_calibrarea_nu_e_la_zi(tmp_path, monkeypatch, continut):
    if continut:
        (tmp_path / "calibrare.txt").write_text(continut % {"sha": M.git("rev-parse", "HEAD").strip()}, encoding="utf-8")
    import calibreaza_16_7 as C
    deschideri = []
    monkeypatch.setattr(C, "ruleaza_pe_server", lambda *a, **k: deschideri.append(1) or 0)
    monkeypatch.setattr(M, "deschide", lambda *a, **k: deschideri.append(1))
    assert M.main(["matrice", "--iesire", str(tmp_path)]) == 1
    assert deschideri == []


def test_jsonul_vechi_al_unui_ecran_se_sterge_inaintea_deschiderii(tmp_path, monkeypatch):
    import verificator_design as VD
    cale = tmp_path / ("%s_603x590.json" % VD.slug("Ecran de probă"))
    cale.write_text("{}", encoding="utf-8")
    vazut = {}

    class Fals:
        pid = 1

        def __init__(self, cmd, **k):
            vazut["exista_la_pornire"] = cale.exists()

        def wait(self, timeout=None):
            return 0
    monkeypatch.setattr(M.subprocess, "Popen", Fals)
    assert M.deschide("Ecran de probă", "603x590", str(tmp_path)) is None
    assert vazut == {"exista_la_pornire": False}


def _rau(tipuri, texte=None):
    texte = texte or M.TEXT_PROBA
    taiate = [{"tip": t, "selector": "x", "text": texte[t] + " …", "w": 1, "sw": 2, "h": 3, "sh": 4, "proba": True} for t in tipuri]
    return {"masuri_alt": {"taiate": taiate, "numar": len(taiate), "numar_fara_proba": 0, "ferestre": 1}}


def test_calibrarea_pozitiva_prinde_un_detector_stricat():
    assert M.compara_pozitiv(_rau(["lat", "inalt", "iesit"]))[0]
    assert not M.compara_pozitiv(_rau(["lat", "iesit"]))[0]     # detector fără tipul „inalt”
    assert not M.compara_pozitiv(_rau(["lat", "inalt"]))[0]     # detector fără tipul „iesit”
    assert not M.compara_pozitiv(_rau(["lat", "inalt", "iesit", "lat"]))[0]
    gresit = dict(M.TEXT_PROBA, iesit="Altceva")
    assert not M.compara_pozitiv(_rau(["lat", "inalt", "iesit"], gresit))[0]   # intrare pe alt element decât cel cu atributul „iesit”


def test_calibrarea_negativa_cere_zero_probe_si_acelasi_numar_fara_proba():
    bun = {"masuri_alt": {"taiate": [{"tip": "lat", "proba": False}] * 2}}
    assert M.compara_negativ(bun, 2)[0]
    assert not M.compara_negativ(bun, 3)[0]
    assert not M.compara_negativ(_rau(["lat"]), 0)[0]


def test_stari_nedeschis_si_timeout_au_mereu_motiv():
    assert M.stare_deschidere(M.STARE_TIMEOUT)[0] == "timeout"
    for js in (None, {"eroare_deschidere": "x", "masuri_alt": {}}, {"pica": {"a": [M.NEDESCHIS_FARA_FEREASTRA]}, "masuri_alt": {}}, {"pica": {}}):
        stare, motiv = M.stare_deschidere(js)
        assert stare == "nedeschis" and motiv
    assert M.stare_deschidere(_js_sintetic())[0] == "ok"
