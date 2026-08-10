# -*- coding: utf-8 -*-
"""GARD D394 codPR cereale (10.08.2026) - SPEC OFICIAL anaf_surse/d394_struct_anaf.txt poz.68-70:
   "op11(codPR) = bun pt bun<>21 SAU lung(op11(codPR))>2 pt bun=21".
Adica: la op11, pentru cereale (bun=21) codPR TREBUIE sa fie subcodul NC (lung>2: 1001 grau, 1005 porumb),
NU centralizatorul '21'. DUKIntegrator D394_31 (reguli 2026.1) respinge codPR='21' la op11:
  "op11 eroare atribut: codPR: valoarea '21' nu se afla in lista" + R63/R80/R81 (DUK-dovedit pe ALFA/tenant_013).

Doua defecte reparate in core/d394.py, ambele pe date pornind de la categoria art.331 de pe factura:
  (A) op11 nu mai emite centralizatorul '21' (bun=21 & lung(cod)<=2) -> exclus cu AVERTISMENT
      (contabilul adauga subcodul NC pe factura). Cod vechi emitea codPR='21' (invalid la DUK).
  (B) calea N (achizitii de la persoane fizice, tip_partener=2) recunoaste subcodul NC direct
      (oglinda caii art.331). Cod vechi: codpr_N_din_categorie('1005') -> None -> operatiunea era
      EXCLUSA -> nu se putea emite niciun op11 valid pentru cereale-N.

MUTATIE (un gard care nu pica pe codul vechi nu e gard):
  - COARSE 'cereale' -> cod vechi emitea codPR='21' -> `"21" not in codpr` PICA.
  - SUBCOD '1005'   -> cod vechi excludea operatiunea (codpr_N=None) -> `"1005" in codpr` PICA.

Seam PUR: core.d394.calcul_d394(prof, perioada, {"facturi":[...]}) - fara DB (deterministic in poarta verde).
Context date: pe ALFA/tenant_013 factura PF-01 e achizitie de cereale de la IONESCU MARIA PFA (persoana fizica
FARA CUI) cu categorie_331='cereale' (coarsa). Reproduce exact operatiunea care pica la DUK.
"""
from core import d394
from core.common import Perioada


def _fact(cat):
    """Achizitie de cereale de la o persoana fizica fara CUI (tip_partener=2, tip N)."""
    return {"cui": "", "platitor_tva": None, "nume": "IONESCU MARIA PFA",
            "directie": "primita", "taxare_inversa": False,
            "cota": 0, "baza": 300, "tva": 0, "categorie_331": cat}


_PROF = {"tva_la_incasare": False}
_PER = Perioada(2026, luna=8)


def test_op11_cereale_coarse_nu_emite_centralizatorul_21():
    """Categorie coarsa 'cereale' (fara subcod NC in date) -> op11 NU emite '21';
    operatiunea e exclusa cu avertisment. Cod vechi emitea codPR='21' (DUK: 'nu se afla in lista')."""
    r = d394.calcul_d394(_PROF, _PER, {"facturi": [_fact("cereale")]})
    codpr = [o["codPR"] for o in r.op11.values()]
    assert "21" not in codpr, "op11 a emis centralizatorul '21' (invalid la op11 - spec poz.68-70): %r" % codpr
    assert any("cereale" in a.lower() and "subcod" in a.lower() for a in r.avertismente), \
        "lipseste avertismentul de subcod NC lipsa la cereale: %r" % r.avertismente


def test_op11_cereale_cu_subcod_NC_emite_codPR_valid():
    """Subcod NC pe factura ('1005' porumb) -> op11 emite codPR='1005' (lung>2, valid la DUK),
    inclusiv pe calea N (persoana fizica). Cod vechi: codpr_N_din_categorie('1005')=None -> exclus."""
    r = d394.calcul_d394(_PROF, _PER, {"facturi": [_fact("1005")]})
    codpr = [o["codPR"] for o in r.op11.values()]
    assert "1005" in codpr, "op11 nu a emis subcodul NC valid '1005' pe calea N: %r" % codpr
    assert all(len(c) > 2 for c in codpr), "codPR la cereale trebuie sa aiba lung>2 (subcod NC): %r" % codpr


def test_codpr_N_din_categorie_recunoaste_subcod_NC():
    """Regresie fix (B): calea N recunoaste subcodul NC direct (nu doar cuvinte-categorie).
    Cod vechi intorcea None pentru '1005' -> operatiunea N era pierduta."""
    assert d394.codpr_N_din_categorie("1005") == "1005"
    assert d394.codpr_N_din_categorie("cereale") == "21"   # cuvantul ramane centralizator (exclus la op11)
