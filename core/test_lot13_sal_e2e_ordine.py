# -*- coding: utf-8 -*-
"""GARD lotul 13 (C89 pe e2e-ul integrat, 26.10.2026): compoziția netului se citește din fereastra salariatului, deschisă din rândul
statului de plată (677). Un pas e2e care pleacă de pe stat (D112 generată, alt ecran) și abia apoi cere compoziția (`_bani_net(patron,
"…")`, `_compozitie`, `coloane`, `text_compozitie`, `_concedii`, `deschide_salariat`) caută rândul statului pe ecranul declarației și
așteaptă 30 de secunde degeaba — pățit la `e2e_lot11_s9.py::test_def_c89_*`: compoziția se recitea după `_d112_xml`.

CE FACE IMPOSIBIL: o funcție din `frontend_test/e2e/e2e_*.py` care, după ce a navigat (`_d112_xml(`, `_genereaza(`, `nav_meniu`,
`_mergi(`, `.goto(`), cere din nou compoziția din fereastra salariatului. Forma corectă: compoziția se citește O DATĂ, înainte de
plecare, iar netul se ia din ea (`_bani_net(patron, eticheta, coloane)`). CALIBRARE: forma veche a lui C89 e prinsă.
"""
import glob
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_NAV = re.compile(r"_d112_xml\(|_genereaza\(|nav_meniu|_mergi\(|\.goto\(")
_CITIRE = re.compile(r"_bani_net\(patron, \"[^\"]*\"\)|_compozitie\(|\bcoloane\(|text_compozitie\(|_concedii\(|_salariat_deschis\(|"
                     r"deschide_salariat")
_FUNCTIE = re.compile(r"\ndef (\w+)\(.*?(?=\ndef |\Z)", re.S)


def citiri_dupa_plecare(surse=None):
    if surse is None:
        surse = {os.path.relpath(f, RAD): io.open(f, encoding="utf-8").read()
                 for f in sorted(glob.glob(os.path.join(RAD, "frontend_test", "e2e", "e2e_*.py")))}
    rele = []
    for cale, s in surse.items():
        for m in _FUNCTIE.finditer(s):
            plecat = False
            for linie in m.group(0).split("\n"):
                t = linie.strip()
                if t.startswith("#"):
                    continue
                if _NAV.search(t):
                    plecat = True
                elif plecat and _CITIRE.search(t):
                    rele.append("%s::%s" % (cale, m.group(1)))
                    break
    return rele


def test_compozitia_nu_se_reciteste_dupa_plecarea_de_pe_stat():
    assert len(glob.glob(os.path.join(RAD, "frontend_test", "e2e", "e2e_*.py"))) > 50, "ANTI-VACUU: e2e-urile nu se văd"
    rele = citiri_dupa_plecare()
    assert not rele, "compoziția recitită după plecarea de pe statul de plată (se citește o dată, înainte): %s" % rele


def test_CALIBRARE_forma_veche_a_lui_c89_e_prinsa():
    vechi = ('\ndef test_def_c89_x(patron, firma_c89):\n'
             '    comp = _randuri_compozitie(_compozitie(patron))\n'
             '    a = _singurul(_d112_xml(patron, firma_c89))\n'
             '    assert _bani_net(patron, "Indemnizație concediu medical") == 500 - ret_cm\n')
    nou = vechi.replace('_bani_net(patron, "Indemnizație concediu medical")', '_bani_net(patron, "Indemnizație concediu medical", coloane)')
    assert citiri_dupa_plecare({"x.py": vechi}) == ["x.py::test_def_c89_x"]
    assert citiri_dupa_plecare({"x.py": nou}) == []
