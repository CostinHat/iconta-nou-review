# -*- coding: utf-8 -*-
"""Teste job lunar de avertizare expirare valori fiscale (core/expirare_cote.py).

Poarta: lista goala -> tacut, iese 0; lista nevida -> alerta o data, cu nume+temei+data expirarii
si CE se strica; garda de acoperire prinde o valoare cu expirare ramasa fara eticheta (mutatie)."""
from datetime import date

from core import expirare_cote as ec
from core.common import EXPIRA_DUPA_LUNI, cota


def test_lista_goala_nu_alerteaza_iese_zero():
    apeluri = []
    r = ec.ruleaza(prag_zile=1, la_data=date(2020, 1, 1),
                   alerteaza=lambda *a: apeluri.append(a) or True)
    assert r["expira"] == 0 and r["alerte_trimise"] == 0
    assert apeluri == []   # in 2020 nimic nu expira in urmatoarea zi -> nu se alerteaza


def test_lista_nevida_o_singura_alerta_cu_toate_valorile():
    apeluri = []
    def _mock(cheie, subiect, mesaj):
        apeluri.append((cheie, subiect, mesaj))
        return True
    r = ec.ruleaza(prag_zile=400, la_data=date(2026, 7, 29), alerteaza=_mock)
    assert r["expira"] >= 3
    assert r["alerte_trimise"] == 1 and len(apeluri) == 1   # O SINGURA alerta pe rulare, nu per valoare
    cheie, subiect, mesaj = apeluri[0]
    assert "valori fiscale expiră" in subiect and str(r["expira"]) in subiect and "400" in subiect
    # corpul grupeaza TOATE valorile in acelasi email
    assert "Salariul minim" in mesaj
    assert "Facilitatea la salariul minim" in mesaj
    assert "Plafonul facilității la salariul minim" in mesaj
    # detaliile pe salariu_minim: temei (din sursa), data expirarii, ce se strica
    _, temei = cota("salariu_minim", date(2026, 7, 1))
    assert temei in mesaj and "2027-07-01" in mesaj
    assert "Monitorul Oficial" in mesaj and "actualiz" in mesaj.lower() and "REFUZA" in mesaj
    assert cheie.startswith("expirare_cote:")   # o singura cheie de throttling pe rulare


def test_acoperire_completa_fiecare_valoare_cu_expirare_are_eticheta():
    fara, straine = ec.acoperire_lipsa()
    assert fara == [] and straine == [], (
        "valori cu expirare fara eticheta: %s; etichete fara valoare: %s" % (fara, straine))


def test_mutatie_scoate_din_expira_garda_de_acoperire_pica(monkeypatch):
    # scoate o intrare din EXPIRA_DUPA_LUNI (ramane in ETICHETE) -> garda prinde eticheta straina.
    # Dovada ca garda chiar prinde drift; altfel ar da o falsa acoperire.
    cheie = next(iter(EXPIRA_DUPA_LUNI))
    monkeypatch.delitem(EXPIRA_DUPA_LUNI, cheie)
    fara, straine = ec.acoperire_lipsa()
    assert cheie in straine, "garda de acoperire nu prinde eticheta ramasa fara valoare cu expirare"
