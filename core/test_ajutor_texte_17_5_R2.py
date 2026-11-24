from pathlib import Path
from frontend_test.e2e.e2e_ajutor_17_5_R2 import director_date, observa_static, rezultat


def test_cele_210_texte_integrale():
    repo = Path(__file__).resolve().parents[1]
    m = observa_static(repo, director_date(repo))["e.2"]
    assert rezultat("e.2", m), m
