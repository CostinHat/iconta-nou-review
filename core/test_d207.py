"""Teste D207 (informativa impozit retinut la sursa - beneficiari nerezidenti).
Structura din validatorul oficial (D207Validator.jar, v2 in vigoare) + semantica din anaf_surse
(structura_D207_2025 + OPANAF_179_2022_D207). Proba pe DUKIntegrator -v D207."""
import os
import pytest
from core import d207

_JAR = "/home/costin/duk/dist/lib/D207Validator.jar"


class _P:
    def cursor(self): return self
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def execute(self, q): pass
    def fetchone(self):
        return ("TEST SRL", "14399840", "Str Test 1 Bucuresti", "POPESCU", "ION", "ADMINISTRATOR",
                "0211234567", "t@t.ro")


def _manual():
    return {"beneficiari": [
        {"tip_venit": "01", "den": "Nonresident Ltd", "stat": "DE", "cif_strain": "DE123",
         "baza": 10000, "imp": 800, "imp_suportat": 0, "act_n": "1"},
        {"tip_venit": "02", "den": "Bank AG", "stat": "AT", "cif_strain": "AT999",
         "baza": 5000, "imp": 250, "imp_suportat": 0, "act_n": "1"}]}


def test_d207_sectiuni_si_control():
    """Sect_II agregat pe tip_venit; totalPlata_A = sum(nrben+Tscutit+Tbaza+Timp+Timps) (struct rd.16)."""
    c = d207.calcul_d207(_manual())
    assert len(c["sectiuni"]) == 2
    s01 = [s for s in c["sectiuni"] if s["tip_venit"] == "01"][0]
    assert s01["nrben"] == 1 and s01["Tbaza"] == 10000 and s01["Timp"] == 800 and s01["Tscutit"] == 0
    # total = (1+0+10000+800+0) + (1+0+5000+250+0)
    assert c["totalPlata_A"] == 16052


def test_d207_scutit_forteaza_impozit_zero():
    """tip_venit scutit (12-21): baza -> Tscutit, impozit retinut = 0 (regula din act)."""
    m = {"beneficiari": [{"tip_venit": "12", "den": "X", "stat": "FR", "cif_strain": "FR1",
                          "baza": 3000, "imp": 999, "act_n": "2"}]}
    c = d207.calcul_d207(m)
    s = c["sectiuni"][0]
    assert s["Tscutit"] == 3000 and s["Tbaza"] == 0 and s["Timp"] == 0
    xml = d207.build_xml({"cui": "1", "den": "F", "declarant_nume": "A", "declarant_prenume": "B",
                          "declarant_functie": "C"}, 2025, 12, m, c)
    assert 'imp1="0"' in xml   # scutit -> impozit 0, nu 999


def test_d207_erori():
    prof = {"cui": "14399840", "den": "F", "declarant_nume": "A", "declarant_prenume": "B", "declarant_functie": "C"}
    assert any("un beneficiar" in e for e in d207.erori_generare(prof, {"beneficiari": []}))
    # cod de venit invalid (09 exclus din nomenclator) -> mesaj de CONTABIL, fara numele intern al campului
    bad = {"beneficiari": [{"tip_venit": "09", "den": "X", "stat": "DE", "cif_strain": "1", "act_n": "1"}]}
    err = d207.erori_generare(prof, bad)
    assert any("tipul de venit" in e for e in err), err
    assert not any("tip_venit" in e or "Stat_R" in e or "Act_N" in e for e in err), err


@pytest.mark.skipif(not os.path.exists(_JAR), reason="Validatorul D207 nu e instalat in DUK.")
def test_d207_valid_pe_validatorul_oficial():
    from core import duk
    from core.common import Perioada
    xml, res = d207.genereaza(_P(), "s", Perioada(2025, luna=12), _manual())
    rez = duk.valideaza(xml, "d207", an=2025, luna=12)
    assert rez["stare"] == "valid", rez.get("erori")
