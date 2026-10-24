# -*- coding: utf-8 -*-
"""[deficiența 494, lotul 12, 23.10.2026] Comparația zilnică a validatoarelor DUK cu ANAF (`scripts/verifica_duk_publicat.py --zilnic`)
și garda din poartă care o citește (`core/test_duk_instalat.py`).

Costin: „manifestul DUKIntegrator expiră pe 07.11.2026 — după acea dată declarațiile nu se mai validează”. Ce expira era comparația:
singura ei dată era `verificat_la` din manifest. Testele de aici, FĂRĂ rețea (versiuni.xml sintetic, `LIB` și fișierul de stare în
directoare temporare), cer ca:
  1. `--zilnic` să scrie starea (data, versiunile publicate, lista celor în urmă) numai în fișierul local, nu în depozit și nu în `LIB`;
  2. un validator în urmă să alerteze administratorul prin canalul existent (`observare.alerteaza`), numind validatorul și pașii;
  3. o descărcare goală sau o rețea căzută să NU scrie o stare (o stare „nimic în urmă” fără comparație ar fi un verde fals);
  4. garda din poartă să ia data cea mai nouă dintre manifest și stare și să pice pe un validator găsit în urmă, dar nu pe unul
     reparat între timp (instalat + `--scrie`).
Temei: N/A — tooling (versiunile validatoarelor sunt structură ANAF, nu normă fiscală).
"""
import datetime
import hashlib
import io
import json
import os
import sys

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import verifica_duk_publicat as V  # noqa: E402
from core import test_duk_instalat as G  # noqa: E402

AZI = datetime.date(2026, 10, 23)
URL_D112 = "http://static.anaf.ro/static/10/Anaf/update5/D112_217/D112Validator.jar"
#: rândurile din `V.mesaj_in_urma` pe care le citește administratorul: validatorul în urmă și pașii 1–2 care repară
_RAND_D112 = "  - D112: instalat %s, publicat de ANAF J27.0.7 (%s)"
_PAS_DESCARCA = "  1. descarcă jarul publicat (adresa de mai sus) în %s, peste cel vechi;" % V.LIB
_PAS_SCRIE = "  2. cd %s && ./venv/bin/python scripts/verifica_duk_publicat.py --scrie   (copia oficială + manifestul);" % V.RAD


def _xml(d112="J27.0.7", d300="J12.0.1"):
    return ("<versiuni>\n<D112>\n<versiuneJ>%s</versiuneJ>\n<versiuneP>P3.0.1</versiuneP>\n<JURL>%s</JURL>\n</D112>\n"
            "<D300>\n<versiuneJ>%s</versiuneJ>\n<JURL>http://static.anaf.ro/static/10/Anaf/update5/D300_1/D300Validator.jar</JURL>\n"
            "</D300>\n</versiuni>\n" % (d112, URL_D112, d300))


@pytest.fixture
def mediu(tmp_path, monkeypatch):
    """LIB cu două jaruri sintetice, manifestul lor (D112 J27.0.6, D300 J12.0.1) și calea stării — toate temporare."""
    lib = tmp_path / "lib"
    lib.mkdir()
    jaruri = {"D112": b"jar d112 J27.0.6", "D300": b"jar d300 J12.0.1"}
    man = {"verificat_la": "2026-10-07", "sursa": V.URL_VERSIUNI, "validatoare": {}}
    for tip, continut in jaruri.items():
        (lib / ("%sValidator.jar" % tip)).write_bytes(continut)
        man["validatoare"][tip] = {"jar": "%sValidator.jar" % tip, "versiuneJ": {"D112": "J27.0.6", "D300": "J12.0.1"}[tip],
                                   "sha256": hashlib.sha256(continut).hexdigest()}
    cale_man = tmp_path / "duk_instalat.json"
    cale_man.write_text(json.dumps(man), encoding="utf-8")
    stare = tmp_path / "cache" / "iconta_duk" / "verificare_anaf.json"
    monkeypatch.setenv(V.ENV_STARE, str(stare))
    alerte = []
    return {"lib": str(lib), "man": str(cale_man), "man_dict": man, "stare": str(stare), "alerte": alerte,
            "alerta": lambda cheie, subiect, mesaj: alerte.append((cheie, subiect, mesaj)) or True}


def _zilnic(m, xml):
    return V.zilnic(publicat=xml, manifest=m["man"], lib=m["lib"], alerta=m["alerta"], azi=AZI)


# ---------------------------------------------------------------- modul zilnic
def test_zilnic_scrie_starea_cu_validatorul_in_urma_si_alerteaza(mediu):
    """MUTAȚIE: apelul `alerta(...)` scos din `zilnic` -> lista de alerte goală -> pică."""
    _zilnic(mediu, _xml(d112="J27.0.7"))
    st = json.load(io.open(mediu["stare"], encoding="utf-8"))
    assert st["verificat_la"] == "2026-10-23"
    assert st["publicate"] == {"D112": "J27.0.7", "D300": "J12.0.1"}
    assert st["in_urma"] == [{"tip": "D112", "jar": "D112Validator.jar", "instalat": "J27.0.6", "publicat": "J27.0.7",
                              "url": URL_D112}]
    assert st["jaruri_schimbate"] == []
    assert len(mediu["alerte"]) == 1, mediu["alerte"]
    cheie, subiect, mesaj = mediu["alerte"][0]
    assert (cheie, subiect) == ("duk_in_urma", "Validatoare DUK în urmă față de ANAF: D112"), (cheie, subiect)
    # rândurile mesajului: validatorul cu cele două versiuni și adresa jarului, apoi comanda care reface manifestul
    assert set(mesaj.splitlines()) >= {_RAND_D112 % ("J27.0.6", URL_D112), _PAS_SCRIE}, mesaj


def test_zilnic_la_zi_scrie_starea_fara_alerta(mediu):
    _zilnic(mediu, _xml(d112="J27.0.6"))
    st = json.load(io.open(mediu["stare"], encoding="utf-8"))
    assert st["in_urma"] == [] and st["verificat_la"] == "2026-10-23"
    assert mediu["alerte"] == []


def test_zilnic_nu_scrie_in_depozit_si_nici_in_LIB(mediu):
    """Modul zilnic e numai-citire față de depozit și `~/duk`: singurul fișier nou e starea, în afara depozitului."""
    inainte_lib = sorted(os.listdir(mediu["lib"]))
    sha_man = hashlib.sha256(open(mediu["man"], "rb").read()).hexdigest()
    mtime_oficial = (os.path.getmtime(V.VERSIUNI_LOCAL), os.path.getmtime(V.MANIFEST))
    _zilnic(mediu, _xml(d112="J27.0.7"))
    assert sorted(os.listdir(mediu["lib"])) == inainte_lib
    assert hashlib.sha256(open(mediu["man"], "rb").read()).hexdigest() == sha_man
    assert (os.path.getmtime(V.VERSIUNI_LOCAL), os.path.getmtime(V.MANIFEST)) == mtime_oficial
    assert not os.path.exists(mediu["stare"] + ".tmp")
    assert not os.path.abspath(V.os.path.expanduser(V.STARE_IMPLICITA)).startswith(RAD + os.sep)


def test_zilnic_un_jar_inlocuit_fara_scrie_alerteaza(mediu):
    with open(os.path.join(mediu["lib"], "D300Validator.jar"), "wb") as f:
        f.write(b"alt jar")
    _zilnic(mediu, _xml(d112="J27.0.6"))
    st = json.load(io.open(mediu["stare"], encoding="utf-8"))
    assert st["jaruri_schimbate"] == ["D300"] and st["in_urma"] == []
    assert [subiect for _c, subiect, _m in mediu["alerte"]] == ["Validatoare DUK în urmă față de ANAF: D300"], mediu["alerte"]


def test_zilnic_versiuni_fara_niciun_validator_nu_scrie_starea(mediu):
    """O pagină schimbată (sau o eroare HTML) nu devine „nimic în urmă”. MUTAȚIE: verificarea `if not pv` scoasă -> starea se scrie
    cu in_urma=[] -> pică."""
    with pytest.raises(RuntimeError, match="niciun validator"):
        _zilnic(mediu, "<html>serviciu indisponibil</html>")
    assert not os.path.exists(mediu["stare"])
    assert mediu["alerte"] == []


def test_zilnic_retea_cazuta_nu_scrie_starea_si_e_tranzitorie(mediu, monkeypatch):
    """Rețeaua spre ANAF căzută: excepția urcă la `cron.ruleaza`, care o recunoaște ca tranzitorie (fără alertă, deficiența 296);
    starea nu se scrie, deci data ei îmbătrânește și poarta o cere la ZILE_MAX."""
    import requests
    from core import cron

    def _cade():
        raise requests.exceptions.ConnectionError("rețea căzută")
    monkeypatch.setattr(V, "descarca", _cade)
    with pytest.raises(requests.exceptions.ConnectionError) as exc:
        V.zilnic(manifest=mediu["man"], lib=mediu["lib"], alerta=mediu["alerta"], azi=AZI)
    assert cron.tranzitoriu(exc.value)
    assert not os.path.exists(mediu["stare"])


def test_cale_stare_din_variabila_de_mediu_si_implicita(monkeypatch, tmp_path):
    """MUTAȚIE: `cale_stare` care ignoră variabila -> pică."""
    monkeypatch.setenv(V.ENV_STARE, str(tmp_path / "s.json"))
    assert V.cale_stare() == str(tmp_path / "s.json")
    monkeypatch.delenv(V.ENV_STARE)
    assert V.cale_stare() == os.path.expanduser("~/.cache/iconta_duk/verificare_anaf.json")


def test_stare_stricata_nu_se_trateaza_ca_lipsa(mediu):
    os.makedirs(os.path.dirname(mediu["stare"]))
    io.open(mediu["stare"], "w", encoding="utf-8").write("{trunchiat")
    with pytest.raises(ValueError):
        V.citeste_stare()


def test_jobul_trece_prin_cron_ruleaza_cu_numele_lui():
    """Structural: `ruleaza_zilnic` cheamă `cron.ruleaza(NUME_JOB, zilnic)` (eșec -> alertă; reușită -> bătaie în heartbeat)."""
    import ast
    arb = ast.parse(io.open(V.__file__, encoding="utf-8").read())
    fn = next(n for n in arb.body if isinstance(n, ast.FunctionDef) and n.name == "ruleaza_zilnic")
    apeluri = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
               and n.func.attr == "ruleaza" and isinstance(n.func.value, ast.Name) and n.func.value.id == "cron"]
    assert len(apeluri) == 1
    a = apeluri[0].args
    assert isinstance(a[0], ast.Name) and a[0].id == "NUME_JOB" and isinstance(a[1], ast.Name) and a[1].id == "zilnic"
    assert V.NUME_JOB == "verificare_duk"


# ---------------------------------------------------------------- garda din poartă
def _stare(verificat_la, instalat="J27.0.6"):
    return {"verificat_la": verificat_la, "in_urma": [{"tip": "D112", "jar": "D112Validator.jar", "instalat": instalat,
                                                       "publicat": "J27.0.7", "url": URL_D112}]}


def test_comparatia_curenta_ia_data_cea_mai_noua(mediu):
    """MUTAȚIE: `max(...)` scos (data numai din manifest) -> pică."""
    man = mediu["man_dict"]
    assert V.comparatia_curenta(man, None)[0] == datetime.date(2026, 10, 7)
    assert V.comparatia_curenta(man, _stare("2026-10-22"))[0] == datetime.date(2026, 10, 22)
    assert V.comparatia_curenta(man, _stare("2026-10-01"))[0] == datetime.date(2026, 10, 7)


def test_comparatia_curenta_pastreaza_numai_ce_e_inca_in_urma(mediu):
    """După instalare + `--scrie` manifestul spune J27.0.7; intrarea veche din stare nu mai oprește poarta.
    MUTAȚIE: filtrul pe versiunea din manifest scos -> intrarea reparată rămâne -> pică."""
    man = mediu["man_dict"]
    assert [e["tip"] for e in V.comparatia_curenta(man, _stare("2026-10-22"))[1]] == ["D112"]
    man["validatoare"]["D112"]["versiuneJ"] = "J27.0.7"
    assert V.comparatia_curenta(man, _stare("2026-10-22"))[1] == []


def test_garda_poartei_pica_numind_validatorul_si_pasii(mediu, monkeypatch):
    """Garda reală din `core/test_duk_instalat.py`, pe o stare zilnică sintetică ce spune D112 în urmă față de manifestul real.
    MUTAȚIE: garda nu mai citește starea (`V.citeste_stare()` -> None) -> poarta verde -> pică."""
    reala = G.MAN["validatoare"]["D112"]["versiuneJ"]
    os.makedirs(os.path.dirname(mediu["stare"]))
    json.dump(_stare(AZI.isoformat(), instalat=reala), io.open(mediu["stare"], "w", encoding="utf-8"))
    with pytest.raises(AssertionError) as exc:
        G.test_comparatia_zilnica_n_a_gasit_niciun_validator_in_urma()
    # rândurile mesajului porții (`V.mesaj_in_urma`): validatorul, versiunea instalată reală și cea publicată, adresa, pașii care repară
    # (pytest indentează rândurile mesajului în textul excepției: se compară rândurile fără marginea lor)
    assert {x.strip() for x in str(exc.value).splitlines()} >= {x.strip() for x in (_RAND_D112 % (reala, URL_D112), _PAS_DESCARCA,
                                                                                      _PAS_SCRIE)}, str(exc.value)


def test_garda_poartei_data_vine_si_din_starea_zilnica(mediu, monkeypatch):
    """Manifest de 40 de zile, stare zilnică de azi -> garda de vechime trece; fără stare -> pică.
    MUTAȚIE: data luată numai din manifest -> pică."""
    vechi = dict(G.MAN, verificat_la=(datetime.date.today() - datetime.timedelta(days=40)).isoformat())
    monkeypatch.setattr(G, "MAN", vechi)
    with pytest.raises(AssertionError, match="40 zile"):
        G.test_comparatia_cu_anaf_nu_e_mai_veche_de_o_luna()
    os.makedirs(os.path.dirname(mediu["stare"]))
    json.dump({"verificat_la": datetime.date.today().isoformat(), "in_urma": []}, io.open(mediu["stare"], "w", encoding="utf-8"))
    G.test_comparatia_cu_anaf_nu_e_mai_veche_de_o_luna()


def test_def_c106_scrie_refuza_versiunea_noua_pe_jarul_vechi():
    """[lotul 12, C106] `--scrie` nu poate trece în manifest o versiune nouă pentru un jar neînlocuit (același sha256).
    MUTAȚIE: condiția pe sha scoasă din `versiuni_noi_pe_jar_vechi` -> pică pe cazul jarului înlocuit."""
    vechi = {"validatoare": {"D112": {"jar": "D112Validator.jar", "versiuneJ": "J27.0.6", "sha256": "aa"}}}
    neschimbat = {"validatoare": {"D112": {"jar": "D112Validator.jar", "versiuneJ": "J27.0.7", "sha256": "aa"}}}
    inlocuit = {"validatoare": {"D112": {"jar": "D112Validator.jar", "versiuneJ": "J27.0.7", "sha256": "bb"}}}
    aceeasi = {"validatoare": {"D112": {"jar": "D112Validator.jar", "versiuneJ": "J27.0.6", "sha256": "aa"}}}
    assert V.versiuni_noi_pe_jar_vechi(vechi, neschimbat) == [("D112", "J27.0.6", "J27.0.7")]
    assert V.versiuni_noi_pe_jar_vechi(vechi, inlocuit) == []
    assert V.versiuni_noi_pe_jar_vechi(vechi, aceeasi) == []
