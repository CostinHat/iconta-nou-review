# -*- coding: utf-8 -*-
"""296 — alertele de sănătate server prea dese (comanda Costin 16.10.2026, răspunsul la raportul lotului 6 pct.5, verbatim în DECIZII):
„se trimit numai cele care cer o acțiune”. Și C42 (găsit la proba SPV din aceeași comandă): un termen depășit la ANAF pe o firmă oprea
citirea SPV a tuturor firmelor și trimitea alerta „job eșuat”.

Ce se păzește:
  1. un rând de alertă de sănătate se compune numai prin `alerta_load.rand` (categorie cu acțiune scrisă în `ACTIUNI`) — o categorie
     fără acțiune nu poate pleca;
  2. condițiile trecătoare (RAM, conexiuni, încărcare) pleacă numai ținute, fără rulări de teste (`alerta_load.tinut`);
  3. eșecul de rețea al unui job (ANAF / BNR / Brevo) nu trimite alertă — îl prinde heartbeat-ul dacă persistă; orice alt eșec, da;
  4. `spv_receive`: ANAF fără răspuns la o firmă se consemnează pe firma ei, iar celelalte se citesc.
"""
import ast
import datetime
import io
import os

import pytest
import requests

from core import alerta_load as al
from core import cron

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T0 = datetime.datetime(2026, 10, 16, 20, 0)


def _ist(valori, teste=()):
    n = len(valori)
    return [(T0 - datetime.timedelta(minutes=5 * (n - 1 - i)), v, i in teste) for i, v in enumerate(valori)]


def _corp_alerte():
    src = io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read()
    return [n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef) and n.name == "_verifica_si_alerta"][0]


def test_296_fiecare_rand_de_alerta_are_actiunea_lui():
    """MUTAȚIE: `alerte.append(_alerta_load.rand("disc", …))` -> `alerte.append(f"Disc folosit …")` -> pică."""
    fn = _corp_alerte()
    adaugari = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "append"]
    assert len(adaugari) >= 6
    fara = [ast.unparse(a)[:80] for a in adaugari
            if not (isinstance(a.args[0], ast.Call) and ast.unparse(a.args[0].func) == "_alerta_load.rand")]
    assert fara == [], fara
    categorii = {a.args[0].args[0].value for a in adaugari}
    rezervate = {n.args[0].value for n in ast.walk(fn) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "_poate_alerta"}
    assert categorii == set(al.ACTIUNI) and rezervate == categorii - {"p2_infrastructura"}, (categorii, rezervate)
    with pytest.raises(KeyError):
        al.rand("fara_actiune", "x")


def test_296_ram_si_conexiunile_alerteaza_numai_tinute():
    """MUTAȚIE: în `main._verifica_si_alerta` RAM-ul pe măsurătoarea curentă (`m["ram_procent"] >= …`) -> pică testul de mai sus (rândul
    nu mai trece prin `tinut`); aici: pragul se aplică pe toată fereastra, iar o rulare de teste o oprește."""
    assert al.tinut(_ist([40, 40, 40, 40, 40, 40, 90]), 75, T0)[0] is False             # un vârf trece singur
    assert al.tinut(_ist([40, 40, 40, 40, 80, 85, 90]), 75, T0) == (
        True, "valoarea peste 75 la 3 măsurători la rând, din 5 în 5 minute: 80.00, 85.00, 90.00")
    assert al.tinut(_ist([90] * 7, teste={5}), 75, T0)[0] is False                      # rularea de teste ține RAM-ul
    src = io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read()
    corp = ast.get_source_segment(src, _corp_alerte())
    assert corp.count('m["ram_procent"]') == 0 and corp.count('m["conexiuni_db"]') == 0, "RAM / conexiuni pe o singură măsurătoare"


@pytest.mark.parametrize("exc, alerta", [(requests.exceptions.ReadTimeout("60 s"), False),
                                         (requests.exceptions.ConnectionError("reset"), False),
                                         (ValueError("defect"), True)])
def test_296_jobul_cazut_din_retea_nu_trimite_alerta(monkeypatch, exc, alerta):
    """MUTAȚIE: `if tranzitoriu(exc):` -> `if False:` -> timeout-ul ANAF trimite alerta -> pică."""
    from core import observare
    trimise = []
    monkeypatch.setattr(observare, "alerteaza", lambda *a, **k: trimise.append(a[0]))

    def job():
        raise exc
    with pytest.raises(SystemExit) as e:
        cron.ruleaza("spv_receive", job)
    assert e.value.code == 1 and trimise == (["cron_esec_spv_receive"] if alerta else []), trimise


def test_c42_anaf_fara_raspuns_la_o_firma_nu_opreste_citirea(monkeypatch):
    """MUTAȚIE: `except requests.exceptions.RequestException` scos din `citeste_firma` -> excepția urcă -> pică."""
    import contextlib
    from core import spv_receive as sr
    monkeypatch.setattr(sr.db, "get_conn", lambda *a, **k: contextlib.nullcontext(_Conn()))
    monkeypatch.setattr(sr.spv_conector, "principal_pentru_schema", lambda c, s: "P")
    monkeypatch.setattr(sr.spv_conector, "ia_token_activ", lambda c, p: {"id": 7})
    monkeypatch.setattr(sr, "_citire_anterioara", lambda c, t, cif: datetime.datetime.now())
    scrise = []
    monkeypatch.setattr(sr, "_inregistreaza_citire", lambda c, t, cif, err, n: scrise.append((cif, err, n)))

    def lista(*a, **k):
        raise requests.exceptions.ReadTimeout("HTTPSConnectionPool(host='api.anaf.ro', port=443): Read timed out. (read timeout=60)")
    monkeypatch.setattr(sr.efs, "lista_mesaje", lista)
    stat = sr._stat_nou()
    r = sr.citeste_firma("tenant_x", stat)
    assert (r["mesaje"], stat["anaf_fara_raspuns"]) == (0, 1) and r["eroare"].startswith("ANAF n-a răspuns la timp (ReadTimeout)"), r
    assert scrise == [("55229657", r["eroare"], 0)], "răspunsul (lipsa lui) se ține minte pe firmă"


def test_c42_o_firma_cazuta_nu_le_opreste_pe_celelalte(monkeypatch):
    """MUTAȚIE: `try/except` din bucla lui `ruleaza` scos -> a doua firmă nu se mai citește -> pică."""
    import contextlib
    from core import spv_receive as sr
    monkeypatch.setattr(sr.db, "init_pool", lambda: None)
    monkeypatch.setattr(sr.db, "get_conn", lambda *a, **k: contextlib.nullcontext(_Conn([("tenant_001",), ("tenant_002",)])))
    citite = []

    def citeste(schema, stat, _dormi):
        citite.append(schema)
        if schema == "tenant_001":
            raise KeyError("profil")
    monkeypatch.setattr(sr, "citeste_firma", citeste)
    with pytest.raises(RuntimeError) as e:
        sr.ruleaza()
    assert citite == ["tenant_001", "tenant_002"] and [c[:2] for c in e.value.cazute] == [("tenant_001", "KeyError")], (citite, e.value)


class _Conn:
    """Conexiune falsă: cursorul întoarce CUI-ul firmei (sau lista schemelor)."""
    def __init__(self, randuri=None):
        self.randuri = randuri

    def cursor(self):
        return _Cur(self.randuri)


class _Cur:
    def __init__(self, randuri):
        self.randuri = randuri

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, *a):
        pass

    def fetchone(self):
        return ("RO55229657",)

    def fetchall(self):
        return self.randuri or []
