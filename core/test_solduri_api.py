# -*- coding: utf-8 -*-
"""Teste gardian pentru solduri_api (partea PURA).

Modulul n-a avut niciun test. Bugul de mai jos a fost gasit prin migrare reala,
nu de teste: ecranul afisa "neechilibrat" rosu, iar importul scria oricum.
"""
import pytest
from core.solduri_api import verifica_echilibru, importa, _numar


def test_balanta_echilibrata():
    ok, td, tc, dif = verifica_echilibru([
        {"cont": "4111", "debit": 1000, "credit": 0},
        {"cont": "401", "debit": 0, "credit": 1000},
    ])
    assert ok and td == 1000 and tc == 1000 and dif == 0


def test_balanta_neechilibrata_e_prinsa():
    ok, td, tc, dif = verifica_echilibru([
        {"cont": "4111", "debit": 1000, "credit": 0},
        {"cont": "401", "debit": 0, "credit": 900},
    ])
    assert not ok and dif == 100


def test_importa_REFUZA_balanta_neechilibrata():
    """Semnalarea fara oprire e mai rea decat tacerea: da impresia ca s-a verificat.
    Regresie 15.07.2026: importa() scria orice, iar migrarea marca stratul 'gata' verde."""
    with pytest.raises(ValueError) as e:
        importa(None, [{"cont": "4111", "debit": 1000, "credit": 0},
                       {"cont": "401", "debit": 0, "credit": 900}])
    m = str(e.value)
    assert "echilibr" in m.lower()
    assert "100" in m          # spune diferenta
    assert "debit" in m.lower() and "credit" in m.lower()


def test_toleranta_de_un_ban():
    """Rotunjirile de bani nu blocheaza o balanta corecta."""
    ok, _, _, _ = verifica_echilibru([
        {"cont": "4111", "debit": 1000.004, "credit": 0},
        {"cont": "401", "debit": 0, "credit": 1000},
    ])
    assert ok


def test_balanta_goala_e_echilibrata():
    assert verifica_echilibru([])[0]
    assert verifica_echilibru(None)[0]


def test_numar_accepta_formatele_din_export():
    assert _numar("1.234,56") == 1234.56       # RO
    assert _numar("1,234.56") == 1234.56       # EN
    assert _numar("1 000") == 1000
    assert _numar("") == 0
    assert _numar(None) == 0
    assert _numar(-12.5) == -12.5


def test_parantezele_sunt_suma_negativa():
    """Format contabil (SAGA/Ciel/Excel): (500) = -500. Inainte cadea pe float() si
    devenea 0.0 TACUT - soldul disparea, iar totalurile pareau corecte."""
    assert _numar("(500)") == -500
    assert _numar("(1.234,56)") == -1234.56


def test_sufixele_de_moneda_nu_anuleaza_suma():
    """Exporturile scriu '500 lei' / '1.234,56 RON'."""
    assert _numar("500 lei") == 500
    assert _numar("1.234,56 RON") == 1234.56


def test_strict_nu_transforma_gunoiul_in_zero():
    """Un sold care devine 0 in tacere e mai periculos decat un import refuzat."""
    assert _numar("N/A") == 0                  # implicit: tolerant (comportament vechi)
    with pytest.raises(ValueError):
        _numar("N/A", strict=True)


def test_conturile_din_balanta_intra_in_plan(monkeypatch):
    """Ecranul promite: 'conturile analitice (clienti, furnizori) intra automat in plan'.
    Pana la 15.07.2026 importa() nu atingea deloc plan_conturi (grep = 0), desi si
    docstringul modulului promitea acelasi lucru. O balanta cu analitice reale
    (4111.01 DEDEMAN) lasa soldurile pe conturi inexistente in nomenclator."""
    from core import solduri_api
    scrise = []

    class _Cur:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def executemany(self, q, vals):
            assert "plan_conturi" in q and "ON CONFLICT" in q
            scrise.extend(vals)
        rowcount = 0

    class _Conn:
        def cursor(self): return _Cur()

    solduri_api._adauga_conturi_lipsa(_Conn(), [
        {"cont": "4111.01", "denumire": "Client DEDEMAN SRL", "debit": 100, "credit": 0},
        {"cont": "401.05", "denumire": "Furnizor ORANGE SA", "debit": 0, "credit": 100},
    ])
    assert ("4111.01", "Client DEDEMAN SRL") in scrise
    assert ("401.05", "Furnizor ORANGE SA") in scrise


def test_contul_fara_denumire_primeste_simbolul():
    from core import solduri_api
    scrise = []

    class _Cur:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def executemany(self, q, vals): scrise.extend(vals)
        rowcount = 0

    class _Conn:
        def cursor(self): return _Cur()

    solduri_api._adauga_conturi_lipsa(_Conn(), [{"cont": "5121", "debit": 0, "credit": 0}])
    assert scrise == [("5121", "5121")]


# ---- Poarta "balanta valida" (09.08.2026): fisier strain / gol nu trece ca "echilibrat" ----
# Constatare de ecran: istoric_declaratii.csv incarcat din greseala la solduri -> "D394" citit ca
# cont, debit/credit 0 -> verifica_echilibru zicea "echilibrat" (0==0) cu bulina verde, iar importul
# salva o balanta goala. Paralela lipsa fata de importul de parteneri (care compara cu balanta).
from core.solduri_api import balanta_valida


def test_fisier_strain_nu_e_balanta_valida():
    strain = [{"cont": "D394", "debit": 0, "credit": 0}, {"cont": "D100", "debit": 0, "credit": 0}]
    assert verifica_echilibru(strain)[0] is True   # bugul vechi: 0=0 = "echilibrat"
    ok, motiv = balanta_valida(strain)
    assert ok is False and "cont" in motiv.lower()


def test_balanta_goala_toate_zero_nu_e_valida():
    zero = [{"cont": "5121", "debit": 0, "credit": 0}]
    ok, motiv = balanta_valida(zero)
    assert ok is False and "0" in motiv


def test_balanta_reala_e_valida():
    reala = [{"cont": "5121", "debit": 1000, "credit": 0}, {"cont": "1012", "debit": 0, "credit": 1000}]
    assert balanta_valida(reala) == (True, "")


def test_importa_refuza_fisier_strain_inainte_de_db():
    # importa cheama balanta_valida INAINTE sa atinga conn -> ridica ValueError fara DB.
    # Mutatie: fara poarta, verifica_echilibru trece (0=0) si se ajunge la asigura_tabel(None) -> alt tip de eroare.
    strain = [{"cont": "D394", "debit": 0, "credit": 0}]
    with pytest.raises(ValueError):
        importa(None, strain)
