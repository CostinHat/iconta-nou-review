"""
Gard: liniile TAXABILE cu cotă fără rând D300 valid pentru perioadă (ex. 19/5%) NU
trebuie să dispară tacit din decont. Semnalul trebuie să (a) CUANTIFICE TVA nedeclarată
și (b) NU să sfătuiască adăugarea manuală la rânduri RESPINSE de ANAF (R69/R71/R74/R24 —
probat prin DUK: 'atributul ... nu trebuie sa existe aici').

Dovedit pe firma DELTA (tenant_016): livrare 19% cu TVA 190 lei scăpată din decont cu un
avertisment vag ('... pune-le manual la rândurile potrivite') care DUCE contabilul spre
rânduri invalide.

PRE-FIX (HEAD): un singur avertisment pe direcție, fără sumă, cu sfatul greșit.
POST-FIX: mesaje separate taxabil/zero, cu bază+TVA, cu avertisment explicit să NU se
          adauge manual acolo.
"""
from core.common import Perioada
from core import d300


def _av():
    prof = {"cui": "301111003", "nume": "TEST", "banca": "B", "iban": "RO00", "caen": "6202"}
    facturi = [
        {"directie": "emisa",   "linii": [(1, 1000, 19)]},   # 19% livrare -> TVA 190 nedeclarată
        {"directie": "emisa",   "linii": [(1, 2000, 0)]},    # 0% livrare -> informativ
        {"directie": "primita", "linii": [(1, 500, 5)]},     # 5% achiziție -> TVA 25 deducere pierdută
    ]
    res = d300.calcul_d300(prof, Perioada(2026, luna=8), facturi)
    return " || ".join(res.avertismente)


def test_livrare_taxabila_scapata_e_cuantificata():
    av = _av()
    # TVA colectată nedeclarată trebuie NUMITĂ cantitativ (FAIL pe HEAD: mesajul vechi n-avea suma).
    assert "TVA 190 lei" in av, av


def test_achizitie_taxabila_scapata_e_cuantificata():
    av = _av()
    assert "TVA 25 lei" in av, av


def test_fara_sfat_gresit_de_adaugare_manuala():
    av = _av()
    # Sfatul vechi ducea contabilul la R69/R71/R74/R24 (respinse DUK) -> declarație invalidă.
    assert "pune-le manual la rândurile potrivite" not in av, av
    # Noul mesaj avertizează EXPLICIT să NU se adauge manual (FAIL pe HEAD: lipsea).
    assert "NU le adăuga manual" in av, av


def test_cota_zero_semnalata_distinct_de_taxabil():
    av = _av()
    # 0% (fără impact TVA) raportat separat de taxabilul scăpat (FAIL pe HEAD: lumped fără cotă).
    assert "cotă 0%" in av, av
