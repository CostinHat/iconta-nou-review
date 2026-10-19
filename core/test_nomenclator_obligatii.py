# -*- coding: utf-8 -*-
"""GARD — denumirea obligațiilor de plată D100 / D710 / D112 vine din nomenclatorul oficial, nu din texte scrise de mână (comanda
Costin 9.1, A.3, 19.10.2026: „Denumirile obligațiilor D100/D112: descarcă nomenclatorul oficial ANAF și leagă-l.”).

`core/nomenclator_obligatii.py` e GENERAT de `scripts/nomenclator_obligatii.py`: denumirea din ordin (OPANAF 587/2016 anexa nr. 3; Ordinul
comun 605/2026 anexa nr. 2), codul XML al poziției din structurile ANAF (`structura_D100-D710_0126_140926`, `structura_D112_0726_070926`).
Garda cere: (1) fișierul = regenerarea; (2) fiecare cod pe care îl emite aplicația (D100, D710, D112) e în nomenclator; (3) componentele
declarației („Din ce e făcută declarația”) și formularul D710 arată denumirea din nomenclator; (4) ecranul nu mai ține o listă proprie.
"""
import io
import os
import re
import subprocess
import sys

from core import d100, d710, declaratii_componente as dc, nomenclator_obligatii as nom
from core.d112 import calcul_d112

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cnp_valid(baza12):
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    c = sum(int(baza12[i]) * ch[i] for i in range(12)) % 11
    return baza12 + str(1 if c == 10 else c)


def _calc_d112():
    prof = {"nume": "FIRMA TEST SRL", "cui": "14399840", "caen": "4711", "judet": "B", "declarant_nume": "POPESCU",
            "declarant_prenume": "Ion", "declarant_functie": "ADMINISTRATOR"}
    sal = [{"nume": "IONESCU", "prenume": "Maria", "cnp": cnp_valid("290010145001"), "brut": 5000, "cas": 1250, "cass": 500,
            "impozit": 325, "part_time": False, "ore_zi": 8, "persoane_intretinere": 0, "judet_casa": "B", "cor": "263501",
            "data_angajare": "2024-01-15", "activ": True}]
    return calcul_d112(prof, sal, 2026, 6)


def test_fisierul_e_regenerarea_din_ordine():
    """MUTAȚIA: o denumire din `core/nomenclator_obligatii.py` editată de mână -> ROȘU (`--verifica` iese 1)."""
    r = subprocess.run([sys.executable, os.path.join(RAD, "scripts", "nomenclator_obligatii.py"), "--verifica"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_pozitiile_si_denumirile_citate_din_ordin():
    # OPANAF 587/2016 anexa nr. 3 poz.2: „Impozit pe profit/plăți anticipate în contul impozitului pe profit anual datorat/datorate de
    # persoane juridice române, altele decât cele de la pct. 1, …”; structura D100-D710: „103 (poz.2)”
    assert nom.NOMENCLATOR_D100["103"][0] == 2 and nom.NOMENCLATOR_D100["103"][1].startswith("Impozit pe profit/plăți anticipate în contul impozitului pe profit")
    # OPANAF 587/2016 anexa nr. 3 poz.5: „Impozit pe veniturile microîntreprinderilor”; structura: „121 (poz.5)”
    assert nom.NOMENCLATOR_D100["121"] == (5, "Impozit pe veniturile microîntreprinderilor")
    # Ordinul comun 605/2026 anexa nr. 2 poz.1: „Impozit pe veniturile din salarii şi/sau asimilate salariilor”; Nomenclator 3: 602 / 1
    assert nom.NOMENCLATOR_D112["602"] == (1, "Impozit pe veniturile din salarii şi/sau asimilate salariilor")
    # Ordinul comun 605/2026 anexa nr. 2 poz.6: „Contribuţia asiguratorie pentru muncă datorată de către persoanele fizice şi juridice
    # care au calitatea de angajatori sau sunt asimilate acestora”; Nomenclator 3: 480 / 6
    assert nom.NOMENCLATOR_D112["480"] == (6, "Contribuţia asiguratorie pentru muncă datorată de către persoanele fizice şi juridice care au calitatea "
                                  "de angajatori sau sunt asimilate acestora")
    # anti-vacuu: ordinul 587 are 104 poziții nereatrase cu cod în structură; ordinul 605 are 29 de poziții (19 nu există)
    assert len(nom.NOMENCLATOR_D100) >= 100 and len(nom.NOMENCLATOR_D112) >= 29


def test_pozitiile_retrase_nu_intra():
    """Ordinul 587 arată poz.21 „Eliminat” și poz.64 „Abrogată”; structura le mai listează (638 / poz.21, 701 / poz.64). 701 rămâne, dar
    pe poziția lui în vigoare (poz.112 „Impozit pe construcții”), iar 638 nu are denumire oficială."""
    assert "638" not in nom.NOMENCLATOR_D100
    assert nom.NOMENCLATOR_D100["701"] == (112, "Impozit pe construcții")


def test_fiecare_cod_emis_de_aplicatie_are_denumire():
    emise_d100 = set(d100.COD_BUGETAR) | set(d100.COD_ZERO_DECLARAT)
    emise_d112 = {o.cod_oblig for o in _calc_d112().rezultat.obligatii}
    assert emise_d112 >= {"602", "412", "432", "480"}, emise_d112
    fara = sorted(["d100:" + c for c in emise_d100 if not nom.denumire("d100", c)] +
                  ["d710:" + c for c in d710.COD_BUGETAR if not nom.denumire("d710", c)] +
                  ["d112:" + c for c in emise_d112 if not nom.denumire("d112", c)])
    assert not fara, "coduri de obligație emise de aplicație fără denumire în nomenclatorul oficial: %s" % fara


def test_componentele_d112_poarta_denumirea_din_nomenclator():
    c = dc.componente("d112", _calc_d112().rezultat)
    randuri = c["sectiuni"][0]["randuri"]
    assert randuri and all(r["denumire obligație"] == nom.NOMENCLATOR_D112[r["cod obligație"]][1] for r in randuri), randuri
    assert list(randuri[0])[:2] == ["cod obligație", "denumire obligație"]


def test_componentele_d100_si_d710_poarta_denumirea_din_nomenclator():
    r100 = d100.RezultatD100(an=2026, luna=9, obligatii=[d100.Obligatie(cod_oblig="103", suma_dat=736)])
    r = dc.componente("d100", r100)["sectiuni"][0]["randuri"][0]
    assert r["denumire obligație"] == nom.NOMENCLATOR_D100["103"][1], r
    r710 = type("R", (), {"obligatii": [d710.ObligatieRect(cod_oblig="121", suma_dat_i=100, suma_dat_c=120)]})()
    r = dc.componente("d710", r710)["sectiuni"][0]["randuri"][0]
    assert r["denumire obligație"] == "Impozit pe veniturile microîntreprinderilor", r


def test_formularul_d710_primeste_codurile_cu_denumirea_de_la_server():
    from core import uc_declaratii
    assert uc_declaratii._obligatii_d710() == [{"cod": c, "denumire": nom.NOMENCLATOR_D100[c][1]} for c in sorted(d710.COD_BUGETAR, key=int)]
    js = io.open(os.path.join(RAD, "static", "js", "ecrane", "declaratii.js"), encoding="utf-8").read()
    # că ecranul chiar folosește lista primită o probează, pe browser, `frontend_test/e2e/e2e_lot6.py` (alege codul 121 din `#d710-cod`,
    # ale cărui opțiuni vin numai din `obligatii_d710`)
    # nicio denumire de obligație scrisă de mână în ecran: textele vechi („Impozit pe profit (103)”) nu mai există
    assert not re.search(r"Impozit pe (profit|veniturile microîntreprinderilor) \(\d{3}\)", js)
