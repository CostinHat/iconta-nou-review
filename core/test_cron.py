# -*- coding: utf-8 -*-
"""Teste core/cron.py — ambalajul joburilor de fundal.

Gardul de fond: un job care crapa TREBUIE sa alerteze si sa iasa cu cod != 0.
Fara asta, esecul e vizibil doar intr-un fisier de log pe care nu-l citeste nimeni
(crontab fara MAILTO, server fara MTA - dovedit 27.07.2026).
"""
import pytest
from core import cron


def test_succes_intoarce_rezultatul_si_nu_alerteaza(monkeypatch, capsys):
    trimise = []
    monkeypatch.setattr("core.observare.alerteaza",
                        lambda *a, **k: trimise.append(a) or True)
    assert cron.ruleaza("proba", lambda: {"ok": 1}) == {"ok": 1}
    assert trimise == []
    assert "job OK: proba" in capsys.readouterr().out


def test_esec_alerteaza_si_iese_cu_cod_1(monkeypatch, capsys):
    trimise = []
    monkeypatch.setattr("core.observare.alerteaza",
                        lambda *a, **k: trimise.append(a) or True)

    def crapa():
        raise RuntimeError("defect fabricat")

    with pytest.raises(SystemExit) as e:
        cron.ruleaza("proba", crapa)
    assert e.value.code == 1, "esecul trebuie sa iasa cu cod != 0"
    assert len(trimise) == 1, "esecul trebuie sa alerteze exact o data"
    cheie, subiect, mesaj = trimise[0]
    assert cheie == "cron_esec_proba"
    assert "proba" in subiect
    assert "defect fabricat" in mesaj, "alerta trebuie sa poarte cauza, nu doar numele"
    out = capsys.readouterr().out
    assert "JOB ESUAT" in out and "defect fabricat" in out


def test_alerta_care_crapa_nu_ascunde_esecul(monkeypatch, capsys):
    """Daca insusi canalul de alertare crapa, jobul tot iese cu 1 si o spune."""
    def alerta_stricata(*a, **k):
        raise OSError("Brevo indisponibil")
    monkeypatch.setattr("core.observare.alerteaza", alerta_stricata)

    def crapa():
        raise RuntimeError("defect fabricat")

    with pytest.raises(SystemExit) as e:
        cron.ruleaza("proba", crapa)
    assert e.value.code == 1
    assert "ALERTA NETRIMISA" in capsys.readouterr().out


def test_toate_joburile_din_crontab_sunt_ambalate():
    """Garda: fiecare modul rulat din cron trebuie sa treaca prin cron.ruleaza.
    Altfel esecul lui redevine tacut. Lista e cea din crontab (27.07.2026)."""
    import pathlib
    rad = pathlib.Path(__file__).resolve().parent
    for m in ("sinteza_zilnica", "facturi_recurente", "woocommerce", "monitor_fiscal",
              "notificari_scadenta", "audit_retentie", "alerta_acces"):
        s = (rad / ("%s.py" % m)).read_text(encoding="utf-8")
        assert "cron.ruleaza(" in s, "%s nu e ambalat in cron.ruleaza" % m
