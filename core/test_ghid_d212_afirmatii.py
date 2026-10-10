# -*- coding: utf-8 -*-
"""GARD — afirmațiile RETRASE despre D212 nu mai pot apărea în ghiduri și în ajutorul F246.

De ce (D212 etapa finală, 03.10.2026): după Etapele 2–5, generatorul D212 calculează rândurile (I.1.1 pe categorii,
I.1.2 normă, cap14, Secțiunile 3/4/5/7 și 2.2) din datele contabilului. Ghidurile scrise înainte spuneau, în 65 de fișiere,
contrariul — „D212 e o declarație manuală”, „doar partea de identificare”, „motorul calculează exclusiv sistemul real”,
„nu are modul pentru chirii / CASS pe trepte”, „nu calculează creditul fiscal”, „pragul minim opțional de 6 salarii”.
Corectate pe clasă în același pas; garda de mai jos face IMPOSIBILĂ reapariția FORMELOR lor.

`ghid_poarta` verifică afirmațiile POZITIVE (o funcție pretinsă e LIVE); clasa de aici e cealaltă direcție — o
afirmație NEGATIVĂ („aplicația nu face X”) devenită falsă când X s-a livrat. Nicio altă gardă n-o vedea.

LIMITA, declarată: prinde FORMELE retrase (lista de mai jos), nu orice parafrază nouă a lor; o afirmație negativă scrisă
altfel trece. De aceea lista se extinde la fiecare clasă retrasă, iar calibrarea arată că fiecare formă chiar prinde.
"""
import io
import os
import re

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GHID = os.path.join(RAD, "ghid")

#: (formă retrasă, ce e adevărat acum). Formele se caută fără diferență de majuscule; `\*{0,2}` acoperă îngroșarea markdown.
RETRASE = [
    (r"D212 e o declarație \*{0,2}manual", "D212 se generează din datele contabilului; rândurile le calculează aplicația"),
    (r"declarația unică e o declarație manual", "idem"),
    (r"generează declarația D212 \(Declarația Unică\) ca declarație manual", "idem"),
    (r"(produce|generator)[^.]{0,60}doar (?:pentru )?partea de identificare", "generatorul emite toate capitolele de venit realizat"),
    (r"calculează \*{0,2}exclusiv sistemul real", "norma (cap12) se calculează în generatorul D212"),
    (r"capitolul (?:de venit pe normă|pentru norma de venit)[^.]{0,60}nu se completează încă", "cap12 se completează din aplicație"),
    (r"valorile se introduc gata calculate", "contabilul dă datele; venitul net, impozitul, contribuțiile se calculează"),
    (r"populate manual", "secțiunile se completează din registru / din datele introduse"),
    (r"nu calculează automat creditul fiscal", "creditul fiscal se calculează, plafonat la impozitul român (CF art.131 alin.(4))"),
    (r"pragul minim opțional de 6 salarii", "baza minimă CASS de 6 salarii minime e obligatorie, cu excepțiile art.174 alin.(7)-(8)"),
    (r"nu are un modul (?:separat|dedicat)[^.]{0,80}(?:cedarea folosinței|chirii|venituri pasive)", "chiriile și CASS pe trepte sunt în D212"),
    (r"nu se ocupă de Declarația unică", "aplicația generează D212"),
    (r"nu generează automat Declarația unică", "aplicația generează D212"),
    (r"nu gestionează Declarația unică", "aplicația generează D212"),
    (r"CASS calculată automat de motor poate ieși zero", "sub 6 salarii minime se aplică baza minimă (CF art.174 alin.(6))"),
    (r"„rămân pe trepte 6/12/24 sm\" și nu sunt calculate", "CASS pe trepte e calculată în D212"),
]


def _texte():
    for f in sorted(os.listdir(GHID)):
        if f.endswith(".md"):
            yield "ghid/" + f, io.open(os.path.join(GHID, f), encoding="utf-8").read()
    csv = io.open(os.path.join(RAD, "FUNCTIONALITATI.csv"), encoding="utf-8").read()
    i = csv.index("Declarația D212 (declarația unică)")
    yield "FUNCTIONALITATI.csv (F246)", csv[i:csv.index("\nMijloace fixe (registrul activelor)", i)]


def gaseste(text):
    """[(formă, fragment)] pentru fiecare formă retrasă găsită în text."""
    out = []
    for forma, _adevar in RETRASE:
        for m in re.finditer(forma, text, re.I):
            out.append((forma, text[max(0, m.start() - 60):m.end() + 60].replace("\n", " ")))
    return out


def test_nicio_afirmatie_retrasa_despre_d212():
    rele = ["%s: «…%s…»" % (f, frag) for f, t in _texte() for _forma, frag in gaseste(t)]
    assert rele == [], ("afirmații RETRASE despre D212 (contrazic codul de azi — v. RETRASE pentru ce e adevărat):\n  "
                        + "\n  ".join(rele))


@pytest.mark.parametrize("forma,adevar", RETRASE)
def test_CALIBRARE_fiecare_forma_chiar_prinde(forma, adevar):
    """Cazul CONSTRUIT: un exemplu tipic al fiecărei forme trebuie găsit — altfel garda ar trece pe un regex mort."""
    exemple = {
        RETRASE[0][0]: "D212 e o declarație **manuală** în iConta.eu",
        RETRASE[1][0]: "dar declarația unică e o declarație manuală: iConta",
        RETRASE[2][0]: "iConta.eu generează declarația D212 (Declarația Unică) ca declarație manuală — aplicația",
        RETRASE[3][0]: "Generatorul D212 din aplicație produce deocamdată doar partea de identificare, validată",
        RETRASE[4][0]: "Motorul de calcul calculează **exclusiv sistemul real** — nu conține",
        RETRASE[5][0]: "capitolul de venit pe normă nu se completează încă din ecran",
        RETRASE[6][0]: "Valorile se introduc gata calculate de contabil",
        RETRASE[7][0]: "secțiuni separate, populate manual, folosite",
        RETRASE[8][0]: "și nu calculează automat creditul fiscal extern",
        RETRASE[9][0]: "cu pragul minim opțional de 6 salarii minime brute",
        RETRASE[10][0]: "Aplicația nu are un modul separat pentru veniturile din cedarea folosinței bunurilor",
        RETRASE[11][0]: "Aplicația **nu se ocupă de Declarația unică a persoanei fizice**",
        RETRASE[12][0]: "dar nu generează automat Declarația unică — pregătirea",
        RETRASE[13][0]: "și nu gestionează Declarația unică sau Registrul",
        RETRASE[14][0]: "CASS calculată automat de motor poate ieși zero — ceea ce",
        RETRASE[15][0]: "veniturile pasive „rămân pe trepte 6/12/24 sm\" și nu sunt calculate de acest motor",
    }
    assert re.search(forma, exemple[forma], re.I), "forma %r nu prinde exemplul ei" % forma


def test_CALIBRARE_limitele_reale_nu_sunt_prinse():
    """Direcția inversă: o limită ADEVĂRATĂ, scrisă azi în ghiduri, nu are voie să fie prinsă (fals pozitiv)."""
    adevarate = ["Aplicația nu transmite însă declarația către SPV",
                 "aplicația nu cunoaște singură sursele persoanei din afara ei",
                 "iConta.eu nu preia normele de venit publicate de direcțiile regionale",
                 "opțiunea pentru CAS sub 12 salarii minime nu se poate încă emite din aplicație"]
    for t in adevarate:
        assert gaseste(t) == [], "limită reală prinsă fals: %r" % t
