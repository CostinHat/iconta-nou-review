from pathlib import Path
from frontend_test.e2e.e2e_ajutor_17_5_R2 import director_date, observa_static, rezultat


def test_arhiva_registrului_si_identitatile():
    repo = Path(__file__).resolve().parents[1]
    m = observa_static(repo, director_date(repo))["e.1"]
    assert rezultat("e.1", m), m
