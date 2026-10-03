# -*- coding: utf-8 -*-
"""ANCORAREA NOMENCLATOARELOR PE NORMĂ (25.08.2026, decizia lui Costin la C6).

PLAN_ARHITECTURA, Partea 0, Pasul 4 — ierarhia surselor:

    | 1 | Monitorul Oficial — textul legii                                  |
    | 2 | Interpretarea oficială a autorității — norme, structuri publicate |
    | 3 | Practica validatorului — ce acceptă efectiv instrumentul          |

    *„Validatorul nu e o sursă alternativă de adevăr. Ce acceptă sau respinge el e o CONSTRÂNGERE,
    nu o normă. Nomenclatorul se ia din sursa normativă. Dacă validatorul acceptă mai puțin decât
    prevede norma, sau altceva, aceea e o constrângere a arbitrului — se declară ca dezacord marcat,
    nu se rescrie nomenclatorul după ea."*

CE ERA ÎNAINTE, ȘI DE CE SE SCHIMBĂ. Campania din 04.08.2026 a ancorat nomenclatoarele pe
VALIDATORUL INSTALAT și a interzis explicit ancorarea pe document (`test_nomenclatoare_ancorate.py`).
Intuiția ei era bună — divergența față de validator ascunsese două defecte reale (ASI mort în cod,
HRK respins deși validatorul îl accepta) — dar concluzia inversa ierarhia: făcea nivelul 3
obligatoriu și nivelul 1–2 insuficient. Un nomenclator ancorat pe arbitru nu mai poate DETECTA
că arbitrul e mai îngust decât legea; îl copiază.

Aici nu se șterge proba pe validator — se adaugă deasupra ei sursa. Fiecare nomenclator poartă:

  - `norma`      — actul, cu citat verbatim rezolvabil în corpus (nivel 1–2). SURSA.
  - `enumerare`  — ce enumeră norma, sau `None` când norma NU închide lista (`deschis=True`).
  - `constrangere` — ce acceptă validatorul instalat, cu proba lui (nivel 3). CONSTRÂNGERE.
  - `dezacord`   — obligatoriu când norma e deschisă sau când enumerarea diferă de valorile din cod.

Cele patru intrări de mai jos sunt MĂSURATE la sursă pe 25.08.2026, nu preluate din comentariile
vechi. Ce a ieșit din măsurătoare, pe scurt:

  d390.TIPURI  — norma ENUMERĂ exact cele șase. Codul coincide. Validatorul e de acord. Fără dezacord;
                 ce era „confirmat pe validator" e de fapt scris în ordin.
  d394.TIPURI  — norma ENUMERĂ exact cele opt, dar norma în vigoare NU e cea citată în cod: OPANAF
                 77/2022 e forma din 2022, iar OPANAF 2194/2025 (MO 852/17.09.2025, aplicabil
                 operațiunilor de la 1.08.2025) e în corpus și nu era citit nicăieri. Vocabularul e
                 identic, citarea nu era. Eliminarea lui ASI, decisă atunci pe autoritatea
                 validatorului, e susținută de normă — nimeni nu verificase.
  d390.TARI_UE — norma NU enumeră: trimite la „codul țării care a emis codul de înregistrare în
                 scopuri de TVA". Deschisă. Setul din cod e o închidere construită de noi.
  d301.VALUTE  — norma NU enumeră: „tipul valutei (de exemplu: USD, euro…)". Deschisă. Cele 20 sunt
                 ale arbitrului. O valută legală din afara lor nu se poate depune — și asta e o
                 constrângere a instrumentului, nu o regulă a legii.
"""
from datetime import date

from core.common import Temei


class Constrangere(object):
    """Ce acceptă efectiv arbitrul (nivel 3). NU e sursă — e limita prin care trebuie să treacă."""

    def __init__(self, instrument, valori, proba, masurat_la):
        self.instrument = instrument          # ex. "DUKIntegrator D301_9"
        self.valori = frozenset(valori)       # setul acceptat, enumerat prin probă
        self.proba = proba                    # testul care îl reprobează
        self.masurat_la = masurat_la


class Dezacord(object):
    """O abatere de la normă impusă de arbitru, SCRISĂ. Cele trei câmpuri nu sunt decorative:
    `cine` leagă dezacordul de constrângerea care îl produce (identitate de obiect, nu nume în
    proză), iar `consecinta` cere să spui CE NU SE POATE FACE din cauza lui — partea care lipsea
    cel mai des din comentariile vechi, fiindcă e singura incomodă."""

    def __init__(self, cine, ce, consecinta):
        self.cine = cine              # Constrangere
        self.ce = ce                  # în ce constă abaterea
        self.consecinta = consecinta  # ce devine imposibil din cauza ei


class Ancora(object):
    """Un nomenclator, cu sursa lui normativă și constrângerea arbitrului, separate."""

    def __init__(self, norma, enumerare, constrangere, deschis=False, dezacord=None):
        self.norma = norma
        self.enumerare = None if enumerare is None else frozenset(enumerare)
        self.constrangere = constrangere
        self.deschis = deschis                # norma NU închide lista
        self.dezacord = dezacord


# Ancorele MĂSURATE. O intrare nouă cere citat verbatim din corpus - gardul îl rezolvă în fișier.
ANCORE_NORMA = {
    ("d390", "TIPURI"): Ancora(
        norma=Temei(
            "OPANAF", 705, 2020, art="5", nivel_sursa="MO", data_in="2020-02-01",
            url="anaf_surse/opanaf_705_2020_d390.txt",
            verificat_la="2026-08-25", de_cine="Code/Costin",
            text_citat="L - pentru livrări intracomunitare de bunuri către alte state membre",
        ),
        # Ordinul enumeră, la instrucțiunile de completare: L, T, A, P, S, R. Șase, exact.
        enumerare=("L", "T", "A", "P", "S", "R"),
        constrangere=Constrangere(
            instrument="DUKIntegrator D390_11",
            valori=("L", "T", "A", "P", "S", "R"),
            proba="test_nomenclatoare_d390_ancorate_pe_validator_nu_pe_pdf_2020",
            masurat_la=date(2026, 8, 4),
        ),
        # Fără dezacord: norma și arbitrul spun același lucru. Ce s-a schimbat e de unde se ia.
    ),

    ("d394", "TIPURI"): Ancora(
        norma=Temei(
            "OPANAF", 2194, 2025, nivel_sursa="MO", data_in="2025-08-01",
            url="anaf_surse/opanaf_2194_2025_d394.txt",
            verificat_la="2026-08-25", de_cine="Code/Costin",
            lant_acte="OPANAF 3769/2015 modificat de OPANAF 77/2022, apoi de OPANAF 2194/2025 "
                      "(MO 852/17.09.2025, art.III: se aplică operațiunilor de la 1.08.2025). "
                      "Codul cita forma 77/2022; vocabularul e identic, citarea era la o formă depășită.",
            text_citat='Coloana "Tip L/A/LS/AS/AÎ/V/C/N/Î1/Î2"',
        ),
        # Norma scrie AÎ; formatul XML scrie AI. Î1/Î2 sunt secțiunile op2 (tip_op2), nu tipuri de op1 —
        # produse de d394.py: Î1 din rapoartele Z (02.10.2026), Î2 din chitanțele fără factură (03.10.2026).
        enumerare=("L", "A", "LS", "AS", "AI", "V", "C", "N"),
        constrangere=Constrangere(
            instrument="DUKIntegrator D394 (versiune curentă)",
            valori=("L", "A", "LS", "AS", "AI", "V", "C", "N"),
            proba="test_TIPURI_e_setul_validatorului_curent",
            masurat_la=date(2026, 8, 3),
        ),
    ),

    ("d390", "TARI_UE"): Ancora(
        norma=Temei(
            "OPANAF", 705, 2020, art="5", nivel_sursa="MO", data_in="2020-02-01",
            url="anaf_surse/opanaf_705_2020_d390.txt",
            verificat_la="2026-08-25", de_cine="Code/Costin",
            text_citat="codul ţării care a emis codul de înregistrare în scopuri de TVA",
        ),
        enumerare=None,
        deschis=True,
        constrangere=Constrangere(
            instrument="DUKIntegrator D390_11",
            valori=("AT", "BE", "BG", "CZ", "CY", "HR", "DK", "EE", "DE", "EL", "FI", "FR",
                    "IE", "IT", "LV", "LU", "LT", "MT", "GB", "NL", "PL", "PT", "SI", "SK",
                    "ES", "SE", "HU", "XI"),
            proba="test_nomenclatoare_d390_ancorate_pe_validator_nu_pe_pdf_2020",
            masurat_la=date(2026, 8, 4),
        ),
    ),

    ("d301", "VALUTE"): Ancora(
        norma=Temei(
            "OPANAF", 592, 2016, nivel_sursa="MO", data_in="2016-02-01",
            url="anaf_surse/opanaf_592_2016_d301.txt",
            verificat_la="2026-08-25", de_cine="Code/Costin",
            text_citat="se menţionează tipul valutei (de exemplu: USD, euro",
        ),
        enumerare=None,
        deschis=True,
        constrangere=Constrangere(
            instrument="DUKIntegrator D301_9",
            valori=("EUR", "USD", "AUD", "CAD", "CHF", "CZK", "DKK", "EGP", "GBP", "HUF",
                    "JPY", "MDL", "NOK", "PLN", "RON", "SEK", "TRY", "XDR", "BGN", "HRK"),
            proba="test_valute_ancorate_pe_validator_nu_pe_pdf_2013",
            masurat_la=date(2026, 8, 4),
        ),
    ),

    # [lot 19 defectul 10, 03.10.2026] Coloanele rândurilor D300: formularul din OPANAF 174/2026 are rândurile, dar
    # extragerea din corpus a pierdut grila „Valoare / TVA” pe rând — norma NU se poate citi ca listă închisă.
    ("d300", "RANDURI_FARA_COL1"): Ancora(
        norma=Temei(
            "OPANAF", 174, 2026, nivel_sursa="MO", data_in="2026-01-01",
            url="anaf_surse/opanaf_174_2026_d300.txt",
            verificat_la="2026-10-03", de_cine="Code",
            text_citat="34 Ajustări conform pro-rata/ajustări de taxă",
        ),
        enumerare=None,
        deschis=True,
        constrangere=Constrangere(
            instrument="DUKIntegrator D300 (structura v12)",
            valori=("R29", "R31", "R35", "R36", "R38", "R39", "R43", "R44"),
            proba="test_coloanele_inexistente_sunt_respinse_de_duk",
            masurat_la=date(2026, 10, 3),
        ),
    ),
    ("d300", "RANDURI_FARA_COL2"): Ancora(
        norma=Temei(
            "OPANAF", 174, 2026, nivel_sursa="MO", data_in="2026-01-01",
            url="anaf_surse/opanaf_174_2026_d300.txt",
            verificat_la="2026-10-03", de_cine="Code",
            text_citat="Achiziţii de bunuri şi servicii scutite de taxă sau neimpozabile, din care:",
        ),
        enumerare=None,
        deschis=True,
        constrangere=Constrangere(
            instrument="DUKIntegrator D300 (structura v12)",
            valori=("R1", "R2", "R3", "R4", "R13", "R14", "R15", "R26"),
            proba="test_coloanele_inexistente_sunt_respinse_de_duk",
            masurat_la=date(2026, 10, 3),
        ),
    ),
}

# Clichetul pe câte nomenclatoare probate n-au încă ancoră de normă stă în GARDĂ
# (core/test_nomenclator_pe_norma.py), nu aici: e o cifră de măsurare, nu una a producției.

# ── DEZACORDURILE, legate prin IDENTITATE de constrângerea care le produce ──
# Se atașează după construcție ca fiecare să poată arăta spre `constrangere` fără s-o redeclare;
# gardul asertează `d.cine is a.constrangere`, deci un dezacord atribuit greșit nu poate trece.

def _dez(cheie, ce, consecinta):
    a = ANCORE_NORMA[cheie]
    a.dezacord = Dezacord(a.constrangere, ce, consecinta)


_dez(("d394", "TIPURI"),
     ce="Norma scrie tipul cu diacritică — AÎ; structura tehnică și XML-ul îl scriu ASCII, AI. "
        "Al doilea, de structură: norma enumeră în aceeași coloană și Î1/Î2, care în XML nu sunt tipuri de op1, ci "
        "secțiunile op2 (`tip_op2`); iConta le produce pe amândouă — Î1 din rapoartele Z (02.10.2026), Î2 din "
        "chitanțele fără factură ale firmei exceptate de la AMEF (03.10.2026).",
     consecinta="Pe transliterare, niciuna practică — arbitrul cere forma ASCII, deci abaterea de la "
                "litera normei e impusă, nu aleasă; se consemnează ca să nu fie confundată cu o "
                "citire greșită a ordinului. Î1/Î2 lipsesc din `enumerare` fiindcă nu sunt valori ale lui op1.tip, ci ale "
                "lui op2.tip_op2 (D394Validator v5) — secțiune separată, produsă și ea.")

_dez(("d390", "TARI_UE"),
     ce="Norma NU enumeră țările: trimite la codul care a emis codul de TVA, adică la prefixul de TVA "
        "al statului membru. Lista din cod e o ÎNCHIDERE construită de noi peste o normă deschisă, "
        "iar limita ei efectivă e ce acceptă arbitrul.",
     consecinta="Două întrebări rămân deschise, și niciuna nu are azi răspuns în cod: (1) GB e în "
                "listă deși Regatul Unit nu mai e stat membru din 2021 — se păstrează pentru perioade "
                "istorice și rectificări, dar valabilitatea prefixului NU e legată de perioada "
                "declarată, deci o livrare din 2026 către GB trece; (2) XI (Irlanda de Nord) e în "
                "listă pe temeiul Protocolului, care nu e citat nicăieri.")

_dez(("d301", "VALUTE"),
     ce="Norma NU închide lista — spune «de exemplu: USD, euro…». Cele 20 de valute sunt ale "
        "ARBITRULUI, enumerate prin probă DUK, nu ale legii.",
     consecinta="O operațiune făcută legal într-o valută din afara celor 20 nu se poate depune prin "
                "acest instrument. E o limită a validatorului, nu o interdicție fiscală, și nu se "
                "poate repara în cod — se poate doar numi. Cazul invers, care a produs regula de "
                "clasă: codul avea 19 (structura tehnică 2013) și respingea HRK, pe care arbitrul îl "
                "accepta — cod mai strict decât ambele niveluri de deasupra lui.")

_DEZ_D300 = ("Formularul 300 din OPANAF 174/2026 are pe fiecare rând coloanele „Valoare” și „TVA”, dar textul din corpus "
             "nu păstrează grila — din normă nu se poate citi pe rând ce coloană există. Setul vine de la ARBITRU: "
             "structura ANAF v12 (Rn_1 / Rn_2 inexistent) și DUK, care respinge fiecare coloană absentă ca „atribut "
             "necunoscut” (probat pe fiecare rând).")
_DEZ_D300_CONSECINTA = ("O sumă pe o coloană pe care structura n-o are nu se poate declara: rândul manual e refuzat la "
                        "introducere (d300_manual_api.adauga) și la calcul (calcul_d300), cu numele coloanei — altfel "
                        "decontul întreg ar fi respins la DUK. Dacă ANAF adaugă o coloană, setul se schimbă la noua "
                        "structură și proba DUK pică întâi.")
_dez(("d300", "RANDURI_FARA_COL1"), ce=_DEZ_D300, consecinta=_DEZ_D300_CONSECINTA)
_dez(("d300", "RANDURI_FARA_COL2"), ce=_DEZ_D300, consecinta=_DEZ_D300_CONSECINTA)
