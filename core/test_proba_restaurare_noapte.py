# -*- coding: utf-8 -*-
"""Proba de restaurare de noapte (decizia Costin 15.10.2026, pct.4, verbatim în DECIZII „Lotul 3 — C35”: „Proba de restaurare automată
în fiecare noapte: da, pe o bază separată ștearsă după probă; în jurnal numai cifre.”) — `core/proba_restaurare_noapte.py` +
`scripts/proba_restaurare.py`. Fără baza de producție și fără dump-ul ei: proba reală rulează din crontab, iar cifrele ei sunt în raport.

MUTAȚII: verificarea codului de ieșire scoasă din `proba()` -> pică `test_proba_picata_alerteaza_si_iese_cu_1`; textul excepției
străine tipărit înapoi (`print("PICAT: %s" % e)`) -> pică `test_in_jurnal_numai_cifre_si_la_esec`; `(?!DATA )` scos din numărătoare ->
pică `test_numara_tabelele_din_cuprins_fara_datele_lor`."""
import os
import sys

import pytest

from core import cron, proba_restaurare_noapte as noapte

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import proba_restaurare as pr   # noqa: E402

_CUPRINS = ("; Archive created at 2099-01-01 03:00:01 EET\n"
            "223; 1259 27388 TABLE public tabela_a rol\n"
            "275; 1259 150271 TABLE tenant_9 tabela_b rol\n"
            "5001; 0 27388 TABLE DATA public tabela_a rol\n"
            "5002; 0 150271 TABLE DATA tenant_9 tabela_b rol\n"
            "4001; 2606 27390 CONSTRAINT public tabela_a tabela_a_pkey rol\n")


def test_numara_tabelele_din_cuprins_fara_datele_lor():
    assert pr.numara_tabele(_CUPRINS) == 2
    assert pr.numara_tabele("") == 0


def test_ultimul_dump_e_cel_mai_nou_iar_lipsa_lui_e_eroare(tmp_path):
    with pytest.raises(RuntimeError, match="Niciun backup local"):
        noapte.ultimul_dump(str(tmp_path))
    for i, nume in enumerate(("iconta_v2_20991230_030001.dump", "iconta_v2_20991231_030001.dump")):
        f = tmp_path / nume
        f.write_bytes(b"x")
        os.utime(f, (1000 + i, 1000 + i))
    assert noapte.ultimul_dump(str(tmp_path)).endswith("iconta_v2_20991231_030001.dump")


def test_proba_picata_alerteaza_si_iese_cu_1(tmp_path, monkeypatch, capsys):
    (tmp_path / "iconta_v2_20991231_030001.dump").write_bytes(b"x")
    chemari, alerte = [], []
    monkeypatch.setattr(pr, "main", lambda argv: chemari.append(argv) or 1)
    from core import observare
    monkeypatch.setattr(observare, "alerteaza", lambda cheie, subiect, corp: alerte.append((cheie, subiect, corp)))
    with pytest.raises(SystemExit) as e:
        cron.ruleaza("proba_restaurare_noapte", lambda: noapte.proba(str(tmp_path)))
    assert e.value.code == 1
    assert chemari == [["proba_restaurare", "--dump", str(tmp_path / "iconta_v2_20991231_030001.dump")]]
    assert [a[0] for a in alerte] == ["cron_esec_proba_restaurare_noapte"]


def test_proba_reusita_bate(tmp_path, monkeypatch):
    (tmp_path / "iconta_v2_20991231_030001.dump").write_bytes(b"x")
    batai = []
    monkeypatch.setattr(pr, "main", lambda argv: 0)
    monkeypatch.setattr(cron, "bate", lambda nume, durata=None: batai.append(nume))
    assert cron.ruleaza("proba_restaurare_noapte", lambda: noapte.proba(str(tmp_path))).startswith("restaurat")
    assert batai == ["proba_restaurare_noapte"] and cron.RITMURI.get("proba_restaurare_noapte") == 50


def test_in_jurnal_numai_cifre_si_la_esec(monkeypatch, capsys):
    """O eroare a driverului poartă text (gazdă, valori); în jurnal ajunge numai tipul ei. Baza de probă se șterge oricum."""
    import psycopg2
    def _conn(env, baza):
        raise psycopg2.OperationalError("TEXT-SECRET 4242 din eroare")
    monkeypatch.setattr(pr, "_conn", _conn)
    monkeypatch.setattr(pr, "_sterge", lambda: "0")
    monkeypatch.setenv("DB_HOST", "h"); monkeypatch.setenv("DB_NAME", "baza_sintetica"); monkeypatch.setenv("DB_USER", "rol_sintetic")
    monkeypatch.setenv("DB_PASSWORD", "p")
    assert pr.main(["proba_restaurare", "--dump", "/nu/exista.dump"]) == 1
    assert capsys.readouterr().out.splitlines() == ["PICAT: OperationalError", "baza de probă după DROP: 0 (0 = ștearsă)"]
