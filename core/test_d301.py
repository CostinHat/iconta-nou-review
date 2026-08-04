# -*- coding: utf-8 -*-
"""Teste D301 — ancorarea nomenclatoarelor pe VALIDATORUL instalat (nu pe pdf-ul de structura 2013).
Campania "reimprospatarea surselor invechite" (04.08.2026), metoda jar-vs-pdf ca la D394/UoM."""
# ── Reimprospatare surse invechite (04.08.2026): nomenclator tip_valuta D301 ancorat pe validator ──
# Sursa: proba DUK boundary pe D301Validator.jar instalat (D301_9). Metoda ca la UoM/MovementType (d406):
# nu ne bazam pe pdf-ul de structura (2013, INVECHIT), ci pe ce ACCEPTA validatorul.
def test_valute_ancorate_pe_validator_nu_pe_pdf_2013():
    """VALUTE (nomenclatorul tip_valuta D301) ancorat pe VALIDATORUL instalat, nu pe pdf-ul din 2013.
    Setul acceptat de validator, enumerat prin proba DUK boundary 04.08.2026 (fiecare cod ISO trecut prin
    DUKIntegrator): 20 de valute. Codul are 19 (= exact pdf-ul 2013), toate validator-acceptate. TIPARUL ASI
    (cod care urmeaza un document mort, cu valori RESPINSE de validator) NU apare: VALUTE ⊆ setul validatorului.
    Diferenta = HRK (kuna croata, adaugata de ANAF post-2013), validator-acceptata dar absenta din cod =
    acoperire lipsa, DECIZIE DE PRODUS (schimba nomenclatorul de valute pe care il poate declara contabilul)."""
    from core.d301 import VALUTE
    # Setul EXACT acceptat de validatorul D301 instalat, enumerat prin proba DUK 04.08.2026 (NU din pdf-ul 2013).
    VALIDATOR_D301 = {"AUD", "BGN", "CAD", "CHF", "CZK", "DKK", "EGP", "EUR", "GBP", "HRK", "HUF", "JPY", "MDL",
                      "NOK", "PLN", "RON", "SEK", "TRY", "USD", "XDR"}
    # anti-ASI: nicio valuta din cod nu e respinsa de validator (niciun cod mort care urmeaza pdf-ul 2013)
    moarte = VALUTE - VALIDATOR_D301
    assert not moarte, "VALUTE contine coduri RESPINSE de validator (tipar ASI - cod dupa document mort): %s" % sorted(moarte)
    # relatia curenta: codul = validatorul MINUS HRK (decizie de produs deschisa). Daca delta se schimba,
    # se reprobeaza DUK si se re-inregistreaza setul.
    assert VALIDATOR_D301 - VALUTE == {"HRK"}, \
        "delta cod-vs-validator s-a schimbat - reprobeaza DUK boundary: %s" % sorted(VALIDATOR_D301 - VALUTE)


def test_valute_snapshot_validator_confirmat_pe_duk():
    """Dinti pe snapshot: proba DUK vie confirma ca snapshot-ul VALIDATOR_D301 reflecta validatorul instalat -
    HRK e acceptat (in snapshot, absent din cod), un cod inventat e respins. Gated (skip fara DUK)."""
    import pytest
    from core import duk
    if not duk.poate_valida("d301"):
        pytest.skip("DUK d301 indisponibil")
    from core.common import Perioada
    from core import d301
    prof = {"nume": "TEST SRL", "cui": "RO14399840", "banca": "BCR", "iban": "RO49AAAA1B31007593840000",
            "adresa": "Str 1", "oras": "Buc", "judet": "B", "declarant_nume": "POP", "declarant_prenume": "ION",
            "declarant_functie": "ADMIN"}
    def valuta_acceptata(v):
        op = {"tip": 1, "nr_doc": "DOC1", "data_doc": "15.06.2026", "val_valuta": 1000,
              "tip_valuta": v, "curs": 4.9770, "tva": 1045}
        r = duk.valideaza(d301.build_xml(d301.calcul_d301(prof, Perioada(2026, luna=6), [op])), "d301", an=2026, luna=6)
        # acceptata daca NU apare eroare pe tip_valuta (alte erori de profil sunt irelevante aici)
        return r["stare"] == "valid" or not any("tip_valuta" in l for l in r["erori"].splitlines())
    assert valuta_acceptata("HRK"), "validatorul ar trebui sa accepte HRK (snapshot)"
    assert not valuta_acceptata("ZZZ"), "validatorul ar trebui sa respinga ZZZ"
