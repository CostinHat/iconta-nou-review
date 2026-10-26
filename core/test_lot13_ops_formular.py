# -*- coding: utf-8 -*-
"""[lotul 13, pachetul `ops`] Gărzile formularelor din Operațiuni speciale, Mijloace fixe și Reevaluarea în valută.

504 (comanda Costin 13.1, verbatim): „Câmpurile nu au voie să arate valori gri sau precompletate care induc în eroare (Costin: «nu trebuie să
fie precompletat nimic care să inducă în eroare»). Ex.: Cota TVA arată «21» gri, dar e gol și formularul refuză; la Ajustare stocuri contul
vine precompletat cu 397. Câmpul rămâne gol.” — motorul formularului nu pune nicio valoare și niciun text gri (placeholder) din `sugestie`.
Întrebările pe care aplicația le stabilește singură nu mai stau în formular: „Dobânda a fost înregistrată deja pe 666” (524, din sold),
„Furnizor plătitor TVA” (544, de la ANAF), „Bunul lipsă era asigurat sau a fost distrus” (520, înlocuită cu criteriul legal), rezerva 105 și
pierderea 655 (511, din reevaluările activului), capitalul / rezervele / profitul la partaj (533, din solduri).
631: moneda reevaluării în valută se alege din lista facturii, nu se scrie (fără `maxlength="3"`)."""
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _js(nume):
    return open(os.path.join(RAD, "static", "js", "ecrane", nume), encoding="utf-8").read()


def niciun_camp_precompletat(js):
    """Locurile din motor care ar pune `sugestie` ca valoare sau ca text gri. Goală = conform."""
    rele = []
    for tipar in (r'value="\$\{esc\(c\.sugestie\)\}"', r'placeholder="\$\{c\.sugestie', r'placeholder="\$\{sc\.sugestie', r"CONT_PRECOMPLETAT"):
        rele += re.findall(tipar, js)
    return rele


def test_niciun_camp_precompletat_sau_gri():
    js = _js("operatiuni_ecran.js")
    assert niciun_camp_precompletat(js) == []
    assert "De regulă ${c.sugestie}." in js   # contul uzual rămâne spus, în explicația câmpului


def test_CALIBRARE_textul_gri_e_prins():
    js = _js("operatiuni_ecran.js")
    a = '<input type="number" step="0.01" id="op-${c.nume}" class="camp-input" aria-label="${esc(c.eticheta)}">'
    assert js.count(a) == 1
    assert niciun_camp_precompletat(js.replace(a, a[:-1] + ' placeholder="${c.sugestie || ""}">'))


def test_intrebarile_stabilite_de_aplicatie_nu_mai_sunt_in_formular():
    js = _js("operatiuni_ecran.js")
    for camp in ("dobanda_angajata", "furnizor_platitor_tva", "asigurat_sau_distrus", "sold_105_activ", "pierdere_655_anterioara",
                 "capital_social", "cifra_afaceri", "impozit_profit", "curs_evidenta", "valoare_activ", "amortizare_lunara"):
        assert not re.search(r'(?:C|DN)\("%s"' % camp, js), camp


def test_decontul_are_salariatul_zilele_deplasarea_si_cota_fiecarei_cheltuieli():
    """670 (a)-(d): salariatul din listă, zilele și deplasarea, cota transportului și a cazării (opționale, fără precompletare)."""
    js = _js("operatiuni_ecran.js")
    i = js.index('cheie: "decont", titlu: "Decont deplasare / diurnă"')
    bloc = js[i:js.index("] },", i)]
    for camp in ('C("salariat_id", "Salariatul", "salariat")', 'C("zile", ', 'C("deplasare", ', 'C("cota_transport", ', 'C("cota_cazare", '):
        assert camp in bloc, camp
    assert re.search(r'C\("transport", [^\n]*optional: true', bloc) and re.search(r'C\("cazare", [^\n]*optional: true', bloc)
    assert '["plafon",' not in bloc   # calculul separat al plafonului a ieșit: îl face decontul


def test_moneda_reevaluarii_se_alege_din_lista():
    js = _js("reevaluare_ecran.js")
    assert 'maxlength="3"' not in js and "selectMoneda(" in js and 'from "./operatiuni_ecran.js' in js


def test_registrul_mf_are_aceleasi_butoane_pe_fiecare_rand():
    """674 / 675 (clasele DS): pe rândul activului, butoane (nu meniul `<details>`), aceleași în aceeași ordine; cel care nu se aplică e
    inactiv, cu motivul în `title`."""
    js = _js("mijloace_ecran.js")
    assert "details class=\"dec-xml\"" not in js
    ordine = [js.index(x) for x in ('buton(m, "casare"', 'buton(m, "reeval"', 'buton(m, "lipsa"', 'buton(m, "cd"')]
    assert ordine == sorted(ordine)
    assert 'disabled title="${esc(motiv)}"' in js
