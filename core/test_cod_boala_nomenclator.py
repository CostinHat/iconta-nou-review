# -*- coding: utf-8 -*-
"""GARDĂ: codul de indemnizație se ia din NOMENCLATORUL 9, nu din enumerarea XSD. (22.08.2026)

DE CE (decizia lui Costin, I1): *„Codurile de boală se unifică pe Nomenclatorul 9, cu XSD-ul ca a
doua constrângere. Contradicția nu se semnalează, se elimină: azi blochează depunerea unui D112 pe
coduri legale."*

CE S-A MĂSURAT, ÎNAINTE DE REPARAȚIE (nu din proză — de la ARBITRU, pe declarație generată):
  D_9=91 -> DUK **VALID**.  Codul NU e în `Str_codBoalaSType` ('01'..'15'), și totuși validatorul îl
           acceptă. Enumerarea XSD e mai îngustă decât validatorul însuși.
  D_9=51 -> DUK: `S101.1: dacă D_9='51' atunci D_12 trebuie să aibă o valoare din nomenclatorul de
           boli infecto-contagioase`. Nu „cod necunoscut" — o regulă de fond PE codul 51.
  D_9=17 -> DUK: `S97: pe cod de indemnizație 17 trebuie completat CNP-ul pentru care a fost
           eliberat certificatul`. Iar o regulă de fond, deci codul e cunoscut.
Iar documentul de structură ANAF (`anaf_surse/d112_struct_anaf.txt`, rândul 98) scrie pentru D_9:
*„Nomenclator 9 – Cod indemnizatie boala (certificate medicale) – cod 01-17"*, cu reguli explicite
pe D_9=51 și pe 91/92.

CE FACE IMPOSIBIL: ca un cod legal (Nomenclatorul 9) să fie respins de NOI cu motivul fals „nu e în
nomenclatorul acceptat de ANAF" — și ca enumerarea XSD să redevină tăcut autoritatea.

CE NU FACE, declarat: nu verifică dacă declarația trece DUK pe fiecare cod. Un cod legal poate cădea
pe o regulă de FOND (D_8 lipsă la 17, D_12 lipsă la 51) — asta e altceva decât respingerea codului,
și e treaba regulilor de completitudine, nu a nomenclatorului.
"""
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import nomenclator_cm as ncm  # noqa: E402

# Codurile pe care ARBITRUL le-a dovedit cunoscute, dar care NU sunt în enumerarea XSD instalată.
# Sunt cazul de calibrare al acestei gărzi: dacă vreunul dispare din nomenclator, garda cade.
DOVEDITE_LA_ARBITRU = ("16", "17", "51", "91")


def test_nomenclatorul_contine_codurile_dovedite_la_arbitru():
    """ANTI-VACUU + calibrare. Nomenclatorul trebuie să conțină exact codurile pe care le-am probat
    la validator. Fără asta, un nomenclator golit ar face restul gărzii verde pe nimic."""
    # Clichet pe NUMĂR, nu prag larg: cu `>= 18` din prima formă, ștergerea unui cod legal trecea
    # neobservată (mutația M6). Un nomenclator poate CREȘTE; scăderea cere decizie scrisă.
    assert len(ncm.CODURI) >= 20, (
        "nomenclatorul are %d coduri, sub cele 20 măsurate pe 22.08 — un cod legal a dispărut, "
        "sau sursa s-a schimbat și atunci se rescrie și temeiul" % len(ncm.CODURI))
    lipsa = [c for c in DOVEDITE_LA_ARBITRU if c not in ncm.CODURI]
    assert not lipsa, (
        "coduri probate la DUK, absente din nomenclator: %s. Vezi capul fișierului — D_9=91 a "
        "ieșit VALID, iar 51 și 17 au primit reguli de fond (S101.1, S97), deci sunt cunoscute." % lipsa)


def test_fiecare_cod_are_temei():
    """Un nomenclator fără temei la sursă e o listă. P8: valoarea normativă poartă temeiul."""
    fara = [c for c, d in ncm.CODURI.items() if not (d.get("temei") or "").strip()]
    assert not fara, "coduri fără temei: %s" % fara


def test_codurile_legale_nu_mai_sunt_respinse_ca_necunoscute():
    """REPARAȚIA. `d112` valida contra enumerării XSD ('01'..'15'), deci un certificat cu cod 16/17/
    51/91 era respins de NOI, cu mesajul fals „nu e în nomenclatorul acceptat de ANAF".

    RED pe HEAD înainte de reparație: `accepta('51')` întorcea False."""
    for cod in DOVEDITE_LA_ARBITRU:
        assert ncm.accepta(cod), (
            "codul %s e legal (Nomenclatorul 9) și cunoscut de validator, dar aplicația îl respinge "
            "— asta blochează depunerea unui D112 pe un certificat real" % cod)


def test_d112_nu_mai_respinge_codul_legal():
    """Garda pe COMPORTAMENTUL lui d112, nu doar pe nomenclator. Un test care afirmă doar
    `ncm.accepta('51')` ar trece și dacă `d112` ar continua să întrebe XSD-ul — a doua logică,
    paralelă, exact ce nu are voie să existe. Deci se probează poarta pe care o folosește chiar
    generatorul."""
    import ast
    import inspect
    from core import d112
    # Poarta trebuie să fie CHIAR cea folosită de generator. Prima formă a acestei gărzi a picat
    # proba: `genereaza` chema `_ncm.accepta` direct, iar garda proba `_cod_boala_acceptat` — două
    # căi paralele, deci mutația care întorcea `d112` la enumerarea XSD TRECEA verde.
    _arb = ast.parse(inspect.getsource(d112))
    _gen = next((f for f in ast.walk(_arb) if isinstance(f, ast.FunctionDef)
                 and f.name == "_d112_genereaza"), None)
    assert _gen is not None, "`_d112_genereaza` nu mai există — garda și-a pierdut subiectul"
    _chemate = {n.func.id for n in ast.walk(_gen)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "_cod_boala_acceptat" in _chemate, (
        "generatorul nu mai trece prin `_cod_boala_acceptat` — garda ar proba o cale pe care "
        "generatorul n-o folosește (logică paralelă)")
    # și direcția inversă: nicăieri altundeva în modul nu se întreabă nomenclatorul direct
    _direct = [n.lineno for n in ast.walk(_arb) if isinstance(n, ast.Call)
               and isinstance(n.func, ast.Attribute) and n.func.attr == "accepta"
               and getattr(n.func.value, "id", "") == "_ncm"
               and not any(f.name == "_cod_boala_acceptat" for f in ast.walk(_arb)
                           if isinstance(f, ast.FunctionDef) and n in ast.walk(f))]
    assert not _direct, (
        "`_ncm.accepta` chemat direct în d112, în afara porții (liniile %s) — a doua cale, "
        "care poate diverge tăcut de cea probată" % _direct)
    for cod in DOVEDITE_LA_ARBITRU:
        assert d112._cod_boala_acceptat(cod), (
            "d112 respinge codul %s — un certificat real nu se poate depune" % cod)
    assert not d112._cod_boala_acceptat("99"), "un cod inexistent trebuie să rămână respins"


def test_niciun_cod_inventat():
    """Direcția inversă: nomenclatorul nu poate crește cu ce vrem noi. Un cod care nu apare în
    documentul de structură ANAF n-are ce căuta aici."""
    doc = open(os.path.join(_RAD, "anaf_surse", "d112_struct_anaf.txt"),
               encoding="utf-8", errors="replace").read()
    # cod 01-17 e enunțat ca INTERVAL în document; codurile din afara intervalului se cer NUMITE
    nenumite = [c for c in ncm.CODURI if not (1 <= int(c) <= 17) and ("D_9 = '%s'" % c) not in doc
                and ("D_9=%s" % c) not in doc and ("D_9 =%s" % c) not in doc
                and (",%s," % c) not in doc.replace(" ", "")]
    assert not nenumite, (
        "coduri în afara intervalului 01-17 care NU sunt numite în documentul ANAF: %s" % nenumite)


def test_xsd_ul_e_a_doua_constrangere_nu_autoritatea():
    """Enumerarea XSD rămâne CITITĂ și DECLARATĂ ca mai îngustă — dar nu mai decide. Dacă cineva o
    repune ca autoritate, cele patru coduri probate ar dispărea din mulțimea acceptată."""
    ingust = ncm.doar_in_xsd()
    if ingust is None:
        pytest.skip("XSD-ul nu se poate citi — nimic de comparat")
    assert set(ingust) < set(ncm.CODURI), (
        "enumerarea XSD nu mai e o submulțime STRICTĂ a nomenclatorului: ori XSD-ul s-a lărgit "
        "(bine — atunci se rescrie interpretarea), ori nomenclatorul s-a îngustat (rău)")
    assert "51" not in ingust, "XSD-ul instalat n-ar mai fi cel măsurat pe 22.08 — recalibrează"
