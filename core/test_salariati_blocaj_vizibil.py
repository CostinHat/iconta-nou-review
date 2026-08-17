# -*- coding: utf-8 -*-
"""core/test_salariati_blocaj_vizibil.py — GARD: pe Stat de plata, butoanele dezactivate SEPA
(„Fișier plată card") si „Răspunsuri REGES" NU livreaza motivul DOAR prin atributul `title`
(invizibil pe touch/mobil, nedescoperibil) — motivul apare VIZIBIL, ca `.caseta-info`.

DEFECT (audit tenant_001, 17.08.2026, provocat pe ecran): butonul SEPA era `disabled` cu
`title="Niciun salariat nu are IBAN..."` si „Răspunsuri REGES" cu `title="Configurează cheile
REGES..."` — singura explicatie era title-ul. Pe tenant_001 (toti salariatii cu IBAN=NULL) butonul
aparea gri fara niciun text vizibil despre motiv sau remediu.

TEMEI: Regula 14 addendum (informatie livrata EXCLUSIV prin `title` = defect; mobil_scan o semnaleaza) +
DS cap.5 v2.12 (`.caseta-info` pentru nota informativa permanenta, `.ci-mesaj`).
"""
import io


def _read(p):
    return io.open(p, encoding="utf-8").read()


def test_sepa_reges_motiv_nu_doar_title():
    src = _read("static/js/ecrane/firme.js")
    assert 'title="Niciun salariat nu are IBAN' not in src, \
        "SEPA: motivul (fara IBAN) inca livrat DOAR prin title — invizibil pe touch (Regula 14 addendum)"
    assert 'title="Configureaz' not in src, \
        "Raspunsuri REGES: motivul (chei neconfigurate) inca livrat DOAR prin title"


def test_sepa_reges_au_nota_vizibila():
    src = _read("static/js/ecrane/firme.js")
    # doua note .caseta-info (SEPA + REGES), fiecare cu „... e indisponibil: <motiv> ... <remediu>"
    assert src.count("e indisponibil") >= 2, \
        "lipsesc notele vizibile (.caseta-info) pentru SEPA/REGES cand butoanele sunt dezactivate"
    assert 'class="caseta-info"' in src
