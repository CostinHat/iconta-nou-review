# -*- coding: utf-8 -*-
"""Lotul 13, comanda 13.1, zona `fact` — C199 (decizia Costin, verbatim: „C199: cu un cod TVA invalid în VIES se refuză scutirea; factura se
emite doar cu TVA românesc. VIES indisponibil = avertisment și reîncercare, nu refuz (550).”).

Temei: CF art.294 alin.(2) lit.a) — scutirea livrării intracomunitare de bunuri „către o persoană impozabilă [...] care îi comunică
furnizorului un cod valabil de înregistrare în scopuri de TVA, atribuit de autoritățile fiscale din alt stat membru”.
Răspunsul VIES e dat de probă (fără rețea): `stare` = valid | invalid | indisponibil (câmpul lui `intracomunitar.verifica_vies`, lotul 13).
Schemă efemeră din template, în tranzacție anulată (fixtura lui 417). Codul de TVA DE123456789 e numai forma unui cod german (VIES nu e
întrebat)."""
import pytest

from core import facturi_api, intracomunitar
from core.test_417_storno_trimitere import _db_ok, conn  # noqa: F401 — fixtura

DB = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
LINIE_LIC = {"descriere": "Marfă livrată în Germania", "cantitate": 1, "pret_unitar": 10000, "cota_tva": 0, "categorie_tva": "livrare_ic"}


def _emite(conn, vies):
    return facturi_api.emite_factura(conn, [dict(LINIE_LIC)], tert_nume="Kunde GmbH", tert_cui="DE123456789", tert_tara="DE",
                                     data_emitere="2099-03-10", platitor_tva=True, dovada_transport=True, pleaca_marfa=False, vies=vies)


def test_def_c199_numai_factura_cu_livrare_intracomunitara_cere_vies():
    assert facturi_api.cere_vies("factura", [LINIE_LIC]) is True
    assert facturi_api.cere_vies("proforma", [LINIE_LIC]) is False
    assert facturi_api.cere_vies("factura", [{"categorie_tva": "export"}]) is False


def test_def_c199_un_raspuns_fara_stare_nu_e_niciodata_invalid():
    """550: un răspuns VIES fără `stare` (sau căderea) e „indisponibil”, nu „invalid” — numai codul spus invalid de VIES refuză scutirea."""
    assert facturi_api.stare_vies({"stare": "invalid"}) == "invalid"
    assert facturi_api.stare_vies({"valid": False, "eroare": "MS_UNAVAILABLE"}) == "indisponibil"
    assert facturi_api.stare_vies({"valid": True}) == "valid"
    assert facturi_api.stare_vies(None) == "indisponibil"


def test_def_c199_vies_cazut_la_emitere_e_indisponibil(monkeypatch):
    """VIES nu răspunde (excepție de rețea) -> „indisponibil” (avertisment), nu refuz; codul fără prefix primește țara clientului."""
    cerute = []

    def _cade(cod, timeout=15):
        cerute.append(cod)
        raise TimeoutError("VIES nu răspunde")
    monkeypatch.setattr(intracomunitar, "verifica_vies", _cade)
    assert facturi_api.verifica_vies_emitere("123456789", "DE") == {"stare": "indisponibil", "valid": False}
    assert cerute == ["DE123456789"]


def test_def_c199_codul_fara_forma_de_cod_ue_e_invalid_cu_motivul(monkeypatch):
    """Codul care nu are forma unui cod de TVA din UE (`intracomunitar.verifica_vies` ridică ValueError) -> verdictul „invalid”, cu motivul
    spus (nu un dict tăcut — garda `core/test_gard_masca_zero.py`, masca succes-shaped).
    MUTAȚIE: `"eroare": str(e)` scos din `verifica_vies_emitere` -> pică. [lotul 13, reparațiile finale] cheia e `eroare`, ca în
    răspunsul lui `intracomunitar.verifica_vies` (`motiv` era numărat drept afirmație netipată despre firmă — core/test_afirmatii_tipate.py)."""
    def _forma(cod, timeout=15):
        raise ValueError("Codul %s nu are forma unui cod de TVA din UE." % cod)
    monkeypatch.setattr(intracomunitar, "verifica_vies", _forma)
    r = facturi_api.verifica_vies_emitere("XX12", None)
    assert (r["stare"], r["valid"]) == ("invalid", False) and facturi_api.stare_vies(r) == "invalid"
    assert r["eroare"].startswith("Codul XX12 ") and r["eroare"].endswith(" nu are forma unui cod de TVA din UE."), r   # motivul, nu egalitatea fragilă


@DB
def test_def_c199_cod_invalid_in_vies_refuza_scutirea(conn):
    """Codul invalid în VIES -> refuzul scutirii (VIES_INVALID, lângă codul clientului), nicio factură scrisă.
    MUTAȚIE: fără refuzul `_stare_vies == "invalid"` din `emite_factura` -> factura se emite scutită -> pică."""
    with pytest.raises(ValueError) as e:
        _emite(conn, {"stare": "invalid", "valid": False})
    assert getattr(e.value, "cod", None) == facturi_api.COD_VIES_INVALID and e.value.camp == "em-cui"
    assert str(e.value) == facturi_api.MESAJ_VIES_INVALID % "DE123456789"
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM facturi WHERE tert_cui = 'DE123456789'")
        assert cur.fetchone()[0] == 0


@DB
def test_def_c199_vies_indisponibil_emite_cu_avertisment(conn):
    """550: VIES indisponibil -> factura se emite (scutită), cu avertismentul și codul de reverificat (ecranul oferă reîncercarea).
    MUTAȚIE: avertismentul scos -> pică."""
    r = _emite(conn, {"stare": "indisponibil", "valid": False})
    assert r.get("factura_id") and r.get("vies_de_reverificat") == "DE123456789", r
    assert (r.get("avertismente") or []).count(facturi_api.AVERTISMENT_VIES_INDISPONIBIL % "DE123456789") == 1, r.get("avertismente")


@DB
def test_def_c199_cod_valid_emite_fara_avertisment_vies(conn):
    r = _emite(conn, {"stare": "valid", "valid": True})
    assert r.get("factura_id") and not r.get("vies_de_reverificat")
    assert (r.get("avertismente") or []).count(facturi_api.AVERTISMENT_VIES_INDISPONIBIL % "DE123456789") == 0
