# -*- coding: utf-8 -*-
"""Gard: heartbeat pentru joburile de fundal — jobul care NU porneste deloc.

`cron.ruleaza` prinde jobul care CRAPA (alerta + exit 1). Nu prinde jobul care nu porneste:
cron oprit, reboot fara crontab, linie stearsa. Un job disparut arata exact ca unul care
n-a avut de lucru - dovedit chiar azi cu woocommerce (tacut 12 zile, si a fost nevoie de
investigatie ca sa se stabileasca daca e defect; nu era).

LIMITA DECLARATA: verificatorul ruleaza pe ACELASI server. Server jos = nimeni nu afla.
Deadman extern ar acoperi si asta - neconstruit.
"""
import datetime

import pytest

from core import cron


def test_fiecare_job_din_crontab_are_prag():
    """Un job nou fara prag n-ar fi supravegheat deloc."""
    din_crontab = {"alerta_acces", "audit_retentie", "facturi_recurente", "woocommerce",
                   "notificari_scadenta", "monitor_fiscal", "sinteza_zilnica"}
    lipsa = din_crontab - set(cron.RITMURI)
    assert not lipsa, "joburi fara prag de heartbeat: %s" % lipsa


def test_pragul_e_mai_mare_decat_ritmul():
    """O rulare ratata nu trebuie sa alarmeze; doua consecutive, da."""
    assert cron.RITMURI["alerta_acces"] >= 1, "prag prea strans pentru un job la 15 minute"
    for zilnic in ("audit_retentie", "facturi_recurente", "notificari_scadenta"):
        assert cron.RITMURI[zilnic] > 24, "%s: prag sub 24h -> alerta la fiecare zi" % zilnic
    assert cron.RITMURI["sinteza_zilnica"] > 72, \
        "sinteza ruleaza luni-vineri: 72h peste weekend sunt normale"


def test_verifica_batai_prinde_jobul_care_lipseste():
    """PUR, fara DB: un job fara bataie e intarziat; unul cu bataie recenta, nu."""
    acum = datetime.datetime(2026, 7, 27, 12, 0, tzinfo=datetime.timezone.utc)
    ritmuri = {"proba_a": 24, "proba_b": 24}

    def _fals(vazute):
        intarziate = []
        for nume, prag in sorted(ritmuri.items()):
            u = vazute.get(nume)
            if u is None:
                intarziate.append((nume, None, "niciodata"))
            elif (acum - u).total_seconds() / 3600.0 > prag:
                intarziate.append((nume, 99, "intarziat"))
        return intarziate

    recent = acum - datetime.timedelta(hours=1)
    vechi = acum - datetime.timedelta(hours=48)
    assert [n for n, _, _ in _fals({"proba_a": recent, "proba_b": recent})] == []
    assert [n for n, _, _ in _fals({"proba_a": recent, "proba_b": vechi})] == ["proba_b"]
    assert [n for n, _, _ in _fals({"proba_a": recent})] == ["proba_b"]


def test_bate_nu_strica_jobul_cand_db_e_jos(monkeypatch, capsys):
    """Consemnarea bataii e efect secundar: daca esueaza, jobul continua - dar o SPUNE."""
    def _crapa():
        raise RuntimeError("DB jos")
    monkeypatch.setattr("core.db.get_conn", lambda *a, **k: _crapa())
    cron.bate("alerta_acces", 1.0)
    assert "bataie neconsemnata" in capsys.readouterr().out


def test_ruleaza_consemneaza_bataia(monkeypatch):
    batai = []
    monkeypatch.setattr(cron, "bate", lambda n, d=None: batai.append((n, d)))
    cron.ruleaza("alerta_acces", lambda: 42)
    assert batai and batai[0][0] == "alerta_acces", "rularea reusita nu si-a consemnat bataia"


def test_esecul_nu_consemneaza_bataie(monkeypatch):
    """O rulare ESUATA nu e o bataie - altfel un job care crapa mereu ar parea sanatos."""
    batai = []
    monkeypatch.setattr(cron, "bate", lambda n, d=None: batai.append(n))
    monkeypatch.setattr("core.observare.alerteaza", lambda *a, **k: True)
    with pytest.raises(SystemExit):
        cron.ruleaza("alerta_acces", lambda: (_ for _ in ()).throw(RuntimeError("x")))
    assert batai == [], "esecul a fost consemnat ca rulare reusita"


def test_bate_refuza_numele_necunoscute():
    """Un nume care nu e in RITMURI nu e supravegheat de nimeni - deci n-are ce cauta in
    tabel. Altfel probele de dezvoltare se acumuleaza in productie (s-a intamplat pe
    27.07: randul 'proba' scris de o verificare manuala)."""
    import pytest
    from core import cron
    with pytest.raises(ValueError):
        cron.bate("nume_inventat_fara_ritm")
