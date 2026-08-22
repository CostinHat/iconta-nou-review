# -*- coding: utf-8 -*-
"""NOMENCLATORUL 9 — codul indemnizației de pe certificatul de concediu medical (D_9).

SURSA E NORMATIVĂ, nu validatorul. Documentul de structură ANAF `anaf_surse/d112_struct_anaf.txt`,
rândul 98 (câmp D_9): *„Nomenclator 9 – Cod indemnizatie boala (certificate medicale) – cod 01-17"*,
plus regulile care NUMESC explicit coduri din afara intervalului: `D_9=51 daca D_5>=30.10.2020`,
`Daca D_9 = (08,09,91,92,10,15,17) atunci D_20=0`.

DE CE EXISTĂ FIȘIERUL ĂSTA (decizia lui Costin, 22.08.2026): nomenclatorul se lua din enumerarea
XSD-ului (`Str_codBoalaSType` = '01'..'15'), care e **mai îngustă decât realitatea**. Consecința nu
era teoretică: un certificat cu cod 16, 17, 51 sau 91 — coduri legale, pe care ecranul le OFERĂ —
era respins de aplicație, cu mesajul fals *„nu e în nomenclatorul acceptat de ANAF"*. Nu se putea
depune D112.

CE A SPUS ARBITRUL (22.08.2026, pe declarație generată, nu pe proză):
    D_9=91 -> DUK **VALID**            (cod absent din enumerarea XSD, acceptat de validator)
    D_9=51 -> DUK `S101.1: daca D_9 = '51' atunci D_12 ... nomenclatorul de boli infecto-contagioase`
    D_9=17 -> DUK `S97: pe cod de indemnizatie 17 trebuie sa se completeze CNP-ul ...`
Ultimele două sunt reguli de FOND pe cod, deci codul e cunoscut. Enumerarea XSD nu e autoritatea.

XSD-UL RĂMÂNE A DOUA CONSTRÂNGERE, nu sursă: `doar_in_xsd()` îl citește în continuare, iar
dezacordul dintre el și nomenclator e declarat în `core/registru_interpretari.py`
(`nomenclator_cm_sursa`), nu ascuns.
"""
import os

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_T_INTERVAL = ("d112_struct_anaf.txt rând 98 (D_9): «Nomenclator 9 – Cod indemnizatie boala "
               "(certificate medicale) – cod 01-17»")
_T_NUMIT = ("d112_struct_anaf.txt: cod NUMIT explicit în regulile D_9 (S101.1 / D_20=0), în afara "
            "intervalului 01-17")

# cod -> {eticheta, temei}. Eticheta e cea de pe certificat; procentele NU stau aici — ele au altă
# sursă (OUG 158/2005) și altă dată de valabilitate, iar amestecarea lor ar face nomenclatorul să
# îmbătrânească din două motive deodată.
CODURI = {
    "01": {"eticheta": "Boală obișnuită", "temei": _T_INTERVAL},
    "02": {"eticheta": "Accident de muncă", "temei": _T_INTERVAL},
    "03": {"eticheta": "Accident în afara muncii", "temei": _T_INTERVAL},
    "04": {"eticheta": "Boală profesională", "temei": _T_INTERVAL},
    "05": {"eticheta": "Boală infectocontagioasă grupa A", "temei": _T_INTERVAL},
    "06": {"eticheta": "Urgență medico-chirurgicală", "temei": _T_INTERVAL},
    "07": {"eticheta": "Carantină", "temei": _T_INTERVAL},
    "08": {"eticheta": "Maternitate", "temei": _T_INTERVAL},
    "09": {"eticheta": "Îngrijire copil bolnav", "temei": _T_INTERVAL},
    "10": {"eticheta": "Reducere timp de muncă cu 1/4 (art. 19)", "temei": _T_INTERVAL},
    "11": {"eticheta": "Trecere temporară în altă muncă", "temei": _T_INTERVAL},
    "12": {"eticheta": "Tuberculoză", "temei": _T_INTERVAL},
    "13": {"eticheta": "Boli cardiovasculare", "temei": _T_INTERVAL},
    "14": {"eticheta": "Neoplazii / SIDA", "temei": _T_INTERVAL},
    "15": {"eticheta": "Risc maternal", "temei": _T_INTERVAL},
    "16": {"eticheta": "Boală infectocontagioasă", "temei": _T_INTERVAL},
    "17": {"eticheta": "Reducere cu 1/4 (oncologic)", "temei": _T_INTERVAL},
    # Formularea ANAF, verbatim, stă AICI și nu în câmpul `temei`: `temei` e text afișabil, iar
    # citatul e ASCII („daca", „Daca") fiindcă așa e scris în document. A-l diacritiza ar falsifica
    # citatul; a-l lăsa în câmp ar sparge garda de diacritice. Deci referința e în câmp, litera e în
    # comentariu:
    #   51 -> «D_9=51 daca D_5>=30.10.2020»
    #   91, 92 -> «Daca D_9 = (08,09,91,92,10,15,17) atunci D_20=0»
    "51": {"eticheta": "Izolare", "temei": _T_NUMIT + " — regula pe D_9=51 (data acordării)"},
    "91": {"eticheta": "Îngrijire copil bolnav (situație specială)",
           "temei": _T_NUMIT + " — regula D_20=0 pentru D_9 din (08,09,91,92,10,15,17)"},
    "92": {"eticheta": "Îngrijire copil cu handicap (situație specială)",
           "temei": _T_NUMIT + " — regula D_20=0 pentru D_9 din (08,09,91,92,10,15,17)"},
}


def normalizeaza(cod):
    """'1' -> '01'. Un cod se scrie pe două caractere (C(2) în structura ANAF)."""
    return str(cod or "").strip().zfill(2)


def accepta(cod):
    """Codul e în Nomenclatorul 9? ASTA e întrebarea de nomenclator — și singura pe care o pune
    aplicația înainte de a genera. Completitudinea câmpurilor pe care un cod le cere (D_8 la 09/17,
    D_12 la 51) se verifică separat; a le confunda ar transforma «lipsește un câmp» în «cod
    inexistent», adică exact mesajul fals de dinainte."""
    return normalizeaza(cod) in CODURI


def eticheta(cod):
    d = CODURI.get(normalizeaza(cod))
    return d["eticheta"] if d else ""


def optiuni():
    """[(cod, text)] în ordinea codului — pentru ecran, ca lista să aibă O SINGURĂ sursă."""
    return [(c, "%s — %s" % (c, CODURI[c]["eticheta"])) for c in sorted(CODURI)]


def doar_in_xsd():
    """Enumerarea `Str_codBoalaSType` din XSD-ul instalat, sau None dacă nu se poate citi.

    E A DOUA CONSTRÂNGERE, mai îngustă decât nomenclatorul, și se citește ca să rămână VIZIBILĂ —
    NU ca să decidă. Fără fallback pe un interval ghicit: dacă XSD-ul nu se poate citi, răspunsul e
    «nu știu», nu «1..15»."""
    try:
        from core.d112 import _enum_xsd
    except Exception:
        return None
    s = _enum_xsd("Str_codBoalaSType")
    return sorted(s) if s else None
