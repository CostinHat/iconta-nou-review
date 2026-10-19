# -*- coding: utf-8 -*-
"""[C, lotul 9, 19.10.2026] Aplicația de PROBĂ (`scripts/e2e_poarta.py`, pe baza de test) nu primește nicio cheie a unui canal care trimite
mesaje unor oameni. Lista ținută în probă (`CHEI_TRIMITERE`) se compară cu cheile pe care le citesc modulele de trimitere — o cheie nouă
de trimitere (un canal nou, un furnizor nou) fără locul ei în listă oprește poarta.
De ce: comanda 9.1 D1 a mutat cheile WhatsApp în `~/.iconta/api_keys.env`, pe care proba îl citește; lista veche scotea numai Brevo, deci
proba ar fi încercat WhatsApp-ul real spre numărul de test."""
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import e2e_poarta  # noqa: E402

#: modulele care trimit spre oameni (email, WhatsApp)
MODULE_TRIMITERE = ("core/observare.py", "core/whatsapp.py")


def _chei_de_trimitere():
    """Cheile citite cu `cfg("...")` / `os.environ.get("...")` în modulele de trimitere, care deschid trimiterea (tokenul / cheia API);
    tokenul de VERIFICARE al webhook-ului și secretul aplicației nu trimit nimic."""
    chei = set()
    for f in MODULE_TRIMITERE:
        txt = open(os.path.join(RAD, f), encoding="utf-8").read()
        chei |= {k for k in re.findall(r'(?:cfg|environ\.get|getenv)\("([A-Z0-9_]+)"', txt)
                 if re.search(r"(_TOKEN|_API_KEY)$", k) and "VERIFY" not in k}
    return chei


def test_proba_scoate_fiecare_cheie_de_trimitere():
    chei = _chei_de_trimitere()
    assert {"BREVO_API_KEY", "POSTMARK_SERVER_TOKEN", "WHATSAPP_TOKEN"} <= chei, chei   # calibrare: cititorul vede cele trei cunoscute
    lipsa = chei - set(e2e_poarta.CHEI_TRIMITERE)
    assert not lipsa, "cheile de trimitere %s nu sunt scoase din mediul probei (`e2e_poarta.CHEI_TRIMITERE`)" % sorted(lipsa)


def test_mediul_probei_nu_are_cheile(monkeypatch):
    """Funcțional: mediul construit pentru aplicația de probă nu conține cheile, chiar dacă mediul care o pornește le are."""
    if not os.path.exists(os.path.expanduser("~/.iconta/test.env")):
        import pytest
        pytest.skip("fără ~/.iconta/test.env")
    for k in e2e_poarta.CHEI_TRIMITERE:
        monkeypatch.setenv(k, "cheie-de-proba")
    env = e2e_poarta._env_test()
    assert not [k for k in e2e_poarta.CHEI_TRIMITERE if k in env], [k for k in e2e_poarta.CHEI_TRIMITERE if k in env]
