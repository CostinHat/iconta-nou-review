# -*- coding: utf-8 -*-
"""GARD CLASA "cale de fisier construita relativ la radacina" (01.08.2026).

Bug d406 (b845763): plan_oficial construia calea catre d406_nomenclatoare_anaf.properties ca
dirname(dirname(d406.py)) = RADACINA repo, dar fisierul fusese mutat in anaf_surse/ -> cale
inexistenta -> set GOL TACIT -> filtrarea pe norma moarta -> SAF-T respins de DUK ("cont 731").

CICLUL DE NECONFORMITATE: clasa = cod care deschide un fisier de DATE printr-o cale construita
din __file__/radacina. grep 01.08 = 2 instante: d406 (reparat) + plata_salarii.XSD_PATH (era deja
corect, sepa_surse/). Ambele corecte acum. Gardul face reaparitia (fisier mutat, cale ramasa stale)
IMPOSIBILA: fiecare fisier de date de care depinde codul TREBUIE sa existe la calea referita -
altfel testul PICA, nu tace cu set gol / XSD lipsa.
"""
import os
import pytest

from core import plata_salarii, d406


def _cale_d406_nomenclator():
    # aceeasi constructie ca plan_oficial (core/d406.py) - daca una se schimba, cealalta o urmeaza
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(d406.__file__))),
                        "anaf_surse", "d406_nomenclatoare_anaf.properties")


DATE_FISIERE = [
    ("plata_salarii.XSD_PATH (SEPA pain.001)", plata_salarii.XSD_PATH),
    ("d406 nomenclator conturi (plan_oficial)", _cale_d406_nomenclator()),
]


@pytest.mark.parametrize("nume, cale", DATE_FISIERE, ids=[x[0].split()[0] for x in DATE_FISIERE])
def test_fisier_de_date_exista_la_calea_construita(nume, cale):
    """Un fisier de date referit printr-o cale construita din __file__ TREBUIE sa existe acolo.
    Altfel: cale stale dupa mutare (clasa bug d406 01.08) -> esec TACIT (set gol / XSD lipsa)."""
    assert os.path.isfile(cale), "%s: fisier INEXISTENT la %s (cale stale dupa mutare?)" % (nume, cale)
    assert os.path.getsize(cale) > 0, "%s: fisier GOL la %s" % (nume, cale)
