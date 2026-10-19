# -*- coding: utf-8 -*-
"""GARD — denumirea oficială a rândurilor D300 / D101 („Din ce e făcută declarația”) vine din textul formularelor ANAF (deficiența 379,
comanda Costin 8.2: „Fiecare rând se afișează cu denumirea lui oficială din formular, la toate declarațiile”).

`core/denumiri_randuri.py` e GENERAT de `scripts/denumiri_randuri.py` din `anaf_surse/opanaf_174_2026_d300.txt` și
`anaf_surse/opanaf_206_2025_d101.txt`; garda cere: (1) fișierul = regenerarea; (2) fiecare atribut pe care îl scriu generatoarele D300 /
D101 și care are rând în formular are o denumire; (3) componentele declarației pleacă cu denumirea, lângă număr.
"""
import io
import os
import re
import subprocess
import sys

from core import declaratii_componente as dc
from core.d101_randuri import denumire_d101, rand_d101
from core.d300_randuri import RAND_FORMULAR, denumire_rand, rand_formular

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_fisierul_e_regenerarea_din_formulare():
    """MUTAȚIA: o denumire din `core/denumiri_randuri.py` editată de mână -> ROȘU (`--verifica` iese 1)."""
    r = subprocess.run([sys.executable, os.path.join(RAD, "scripts", "denumiri_randuri.py"), "--verifica"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def _atribute(fisier, tipar):
    return sorted(set(re.findall(tipar, io.open(os.path.join(RAD, "core", fisier), encoding="utf-8").read())))


def test_fiecare_atribut_d300_cu_rand_in_formular_are_denumire():
    atr = [a for a in _atribute("d300.py", r'"(R\d+(?:_\d+)*_[12])"') if int(a[1:].split("_")[0]) in RAND_FORMULAR]
    assert len(atr) > 40, "anti-vacuu: %d atribute" % len(atr)
    fara = [a for a in atr if not denumire_rand(a)]
    assert not fara, "atribute D300 fără denumirea din formular: %s" % fara


def test_fiecare_atribut_d101_scris_are_denumire():
    """Excepția: P141 (subrândul 14.1, netipărit ca rând separat în formularul extras — vezi `test_d101_rand_formular.NECONFRUNTABILE`)."""
    atr = [a for a in _atribute("d101.py", r'"(P\d+[a-z]?)"') if a != "P141"]
    assert len(atr) > 60, "anti-vacuu: %d atribute" % len(atr)
    fara = [a for a in atr if not denumire_d101(a)]
    assert not fara, "atribute D101 fără denumirea din formular: %s" % fara


def test_denumirile_din_deficienta_si_exponentii():
    # OPANAF 174/2026, anexa 1, D300 rd.9: „Livrări de bunuri şi prestări de servicii, taxabile cu cota 21%”
    assert rand_formular("R9_1") == "rândul 9, coloana Valoare"
    assert denumire_rand("R9_1") == "Livrări de bunuri şi prestări de servicii, taxabile cu cota 21%"
    # D300 rd.19 (atributul R17): „TOTAL TAXĂ COLECTATĂ (sumă de la rd. 1 până la rd. 18 [...])”
    assert denumire_rand("R17_2").startswith("TOTAL TAXĂ COLECTATĂ")
    # D300 rd.17: exponentul pierdut la extragere („art. 2781”) e art.278^1 CF (verificat în cod_fiscal_227_2015_consolidat.html)
    assert denumire_rand("R64_1").endswith("pentru care locul livrării/prestării este în România, conform art. 278^1 alin. (1) din Codul fiscal")
    # OPANAF 206/2025, D101 rd.38^1 = atributul P38a (d101_struct_anaf.txt: „rd.40^1=rd.38^1”, P40a = -P38a)
    assert rand_d101("P38a") == "rândul 38^1"
    assert denumire_d101("P38a") == "Profit impozabil/pierdere fiscală, înainte de reportarea pierderii din anii precedenţi"
    # D101 rd.42.2.2: art.22^1 CF (scutirea contribuabililor din cercetare-inovare), nu art.221 (nerezidenți)
    assert denumire_d101("P4222") == "Impozit pe profit scutit, potrivit art. 22^1 din Codul fiscal"


def test_componentele_pleaca_cu_denumirea_langa_numar():
    """MUTAȚIA: `chei_om` scos din secțiunea D300 a `COMPONENTE` -> ROȘU (rândul pleacă fără denumire)."""
    sec = dc.COMPONENTE["d300"][0]
    rand = dc._rand_din_dict("R9_1", 5000, sec)
    assert rand["rând"] == "rândul 9, coloana Valoare" and rand["denumire în formular"].endswith("cota 21%"), rand
    sec = dc.COMPONENTE["d101"][0]
    rand = dc._rand_din_dict("P081", 100, sec)
    assert rand["rând"] == "rândul 8.1" and rand["denumire în formular"].startswith("Elemente similare veniturilor potrivit art. 46"), rand
