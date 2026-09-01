# -*- coding: utf-8 -*-
"""Teste RAPORT INTERN de vechime a confirmarii (core/expirare_cote.py, Modelul de temei 01.08 pct.2).

Fost job de expirare (EXPIRA_DUPA_LUNI scos): acum semnaleaza valorile care n-au mai fost CONFIRMATE
la sursa de peste N luni. Poarta: toate confirmate recent -> tacut, 0; unele vechi -> o alerta
grupata, cu nume+temei+vechime+ce sa faci; garda de acoperire prinde o cheie COTE fara eticheta."""
import re
from datetime import date

from core import expirare_cote as ec


def test_toate_confirmate_recent_nu_alerteaza_iese_zero():
    apeluri = []
    r = ec.ruleaza(prag_luni=6, la_data=date(2026, 8, 1),
                   alerteaza=lambda *a: apeluri.append(a) or True)
    assert r["neconfirmate"] == 0 and r["alerte_trimise"] == 0
    assert apeluri == []   # toate verificat_la=2026-07-31, la 2026-08-01 => sub 6 luni => nimic


def test_neconfirmate_o_singura_alerta_cu_toate_valorile():
    apeluri = []
    def _mock(cheie, subiect, mesaj):
        apeluri.append((cheie, subiect, mesaj))
        return True
    r = ec.ruleaza(prag_luni=6, la_data=date(2028, 1, 1), alerteaza=_mock)   # >6 luni de la 2026-07-31
    assert r["neconfirmate"] >= 3
    assert r["alerte_trimise"] == 1 and len(apeluri) == 1   # O SINGURA alerta pe rulare
    cheie, subiect, mesaj = apeluri[0]
    # PRAGUL A IESIT DIN SUBIECT (01.09.2026, R109) si nu e o slabire a probei: nu mai exista UN
    # prag: fiecare valoare are al ei, iar subiectul ar fi trebuit sa poarte o cifra care nu descrie
    # nimic. Pragul se verifica acum PE RAND, mai jos — acolo unde chiar difera.
    assert "n-au mai fost confirmate" in subiect and str(r["neconfirmate"]) in subiect
    assert re.search(r"prag \d+ luni \((per articol|global)", mesaj), (
        "randurile nu mai spun ce prag s-a aplicat si de unde vine — cine citeste raportul nu poate "
        "deosebi o valoare stramtata de una lasata pe podeaua globala")
    assert "Salariul minim brut" in mesaj and "Cota standard TVA" in mesaj
    assert re.search(r"\d{4}-\d{2}-\d{2}", mesaj)   # verificat_la (o data ISO in alerta; nu hardcodat - se bumpeaza la re-verificare)
    assert "Monitorul Oficial" in mesaj and "actualiz" in mesaj.lower()
    assert cheie.startswith("confirmare_cote:")   # o singura cheie de throttling pe rulare


def test_acoperire_completa_fiecare_cheie_cota_are_eticheta():
    fara, straine = ec.acoperire_lipsa()
    assert fara == [] and straine == [], (
        "chei COTE fara eticheta: %s; etichete fara cheie COTE: %s" % (fara, straine))


def test_mutatie_scoate_eticheta_garda_de_acoperire_pica(monkeypatch):
    # scoate o eticheta (cheia COTE ramane) -> garda prinde cheia fara eticheta. Dovada ca prinde drift.
    cheie = "cas"
    monkeypatch.delitem(ec.ETICHETE, cheie)
    fara, straine = ec.acoperire_lipsa()
    assert cheie in fara, "garda de acoperire nu prinde cheia COTE ramasa fara eticheta"
