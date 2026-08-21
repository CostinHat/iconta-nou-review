# -*- coding: utf-8 -*-
"""GARDĂ: o respingere de rând la import e o AFIRMAȚIE, cu regulă numită. (P8/C, 21.08.2026)

DECIZIA (Costin, 21.08): validările de rând la import intră în aceeași decizie și primesc același
tip. Sunt afirmații despre datele care intră în evidența firmei — „rândul 7: CNP invalid" — și au
exact boala pe care o vânăm: textul poartă tot, iar cine le consumă trebuie să ghicească.

MĂSURAT ÎNAINTE (21.08): 46 de respingeri în 12 module. 27 poartă DEJA un cod mașinal lângă textul
uman (`cnp_invalid`, `cod_duplicat`, `norma_lipsa`) — alea sunt pe jumătate structurate. 9 au doar
proză. Zero coliziuni de cod între module, deci nomenclatorul se poate ÎNCHIDE fără să cimenteze o
ambiguitate; verificat cu `masoara_coliziuni`, nu presupus.

DE CE CONTEAZĂ, cu o instanță: `static/js/ecrane/migrare.js` numără duplicatele așa —
`erori.filter(e => (e.mesaj || "").includes("există deja"))`. O clasificare prin potrivire de PROZĂ.
Cine reformulează mesajul strică tăcut numărătoarea, iar ecranul spune „0 firme erau deja în
portofoliu" despre un import în care erau. Codul închis îl repară la sursă.
"""
import pytest

from core import migrare_api

CU_COD = ["salariati_import_api", "mijloace_fixe_import_api", "istoric_declaratii_import_api",
          "solduri_parteneri_api", "asociati_import_api"]


def test_exista_un_nomenclator_inchis_de_reguli():
    """Roșu pe HEAD. Fără nomenclator, `regula` ar fi un șir liber — adică proză cu alt nume."""
    assert hasattr(migrare_api, "REGULI"), (
        "core/migrare_api.py nu declară `REGULI` — nomenclatorul închis al motivelor de respingere. "
        "Fără el, `regula` din afirmație e tot un șir liber.")
    assert len(migrare_api.REGULI) >= 15, (
        "nomenclator prea mic (%d) — cele 27 de coduri măsurate n-au intrat toate"
        % len(migrare_api.REGULI))


def test_fiecare_regula_spune_ce_inseamna():
    """Un cod fără explicație e un cod pe care nimeni nu-l poate folosi corect. Iar cel care randează
    trebuie să poată alege un text propriu fără să ghicească din nume."""
    for cod, spec in migrare_api.REGULI.items():
        assert cod == cod.lower() and " " not in cod, "cod neconform: %r" % cod
        assert spec.get("inseamna"), "regula %r nu spune ce înseamnă" % cod
        assert spec.get("fel") in ("lipsa", "invalid", "duplicat", "incoerent", "esec"), (
            "regula %r n-are o formă declarată (lipsa/invalid/duplicat/incoerent/esec): %r"
            % (cod, spec.get("fel")))


def test_respinge_construieste_o_afirmatie_valida():
    """Constructorul unic. `unde` = pe ce anume; `regula` = de ce nu ține."""
    a = migrare_api.respinge("salariat", 7, "cnp_invalid",
                             "CNP invalid (cifra de control nu se verifică)")
    assert a["fel"] == "neconformitate" and a["tip"] == "salariat"
    assert a["rand"] == 7 and a["regula"] == "cnp_invalid"
    assert a["forma"] == "invalid", "forma respingerii nu ajunge la randor"
    assert a["mesaj"] == a["motiv"], "textul s-a despărțit în două surse"


def test_o_regula_din_afara_nomenclatorului_e_refuzata():
    """ANTI-VACUU pe închidere: dacă orice șir ar trece, nomenclatorul n-ar închide nimic."""
    with pytest.raises(ValueError):
        migrare_api.respinge("salariat", 7, "cod_inventat_pe_loc", "ceva")


def test_respingerea_cere_randul_si_textul():
    """`rand` e domeniul: o respingere fără el e un repros fără adresă."""
    with pytest.raises((ValueError, TypeError)):
        migrare_api.respinge("salariat", None, "cnp_invalid", "CNP invalid")
    with pytest.raises(ValueError):
        migrare_api.respinge("salariat", 7, "cnp_invalid", "")


@pytest.mark.parametrize("modul", CU_COD)
def test_modulele_cu_cod_trec_prin_constructor(modul):
    """Cele 27 măsurate poartă deja un cod; trebuie să treacă prin nomenclator, nu pe lângă el."""
    import importlib
    m = importlib.import_module("core." + modul)
    import inspect
    sursa = inspect.getsource(m)
    assert "respinge(" in sursa, (
        "%s încă produce respingeri fără constructorul unic — codul lui nu e verificat contra "
        "nomenclatorului, deci o greșeală de tastare trece tăcut" % modul)


def test_codurile_folosite_sunt_toate_in_nomenclator():
    """CONFRUNTAREA celor două instrumente (ca scan↔verificator): scanul citește codurile CHIAR
    FOLOSITE în module; nomenclatorul le declară. O despărțire înseamnă că unul minte."""
    from core import scan_respingeri
    folosite = set(scan_respingeri.coduri_folosite())
    assert folosite, "scanul nu vede niciun cod — s-a rupt, nu s-au terminat codurile"
    lipsa = sorted(folosite - set(migrare_api.REGULI))
    assert not lipsa, (
        "coduri folosite în module dar nedeclarate în REGULI: %s" % lipsa)
    # CEALALTA DIRECTIE: un cod declarat și nefolosit e greutate moartă într-un nomenclator care
    # pretinde că închide ceva. `denumire_lipsa` a fost exact asta la instalare — l-am scos, nu l-am
    # lăsat să pară o categorie disponibilă.
    moarte = sorted(set(migrare_api.REGULI) - folosite)
    assert not moarte, (
        "coduri declarate în REGULI dar nefolosite nicăieri: %s. Scoate-le sau folosește-le — un "
        "nomenclator cu intrări moarte nu mai spune ce categorii există cu adevărat." % moarte)


def test_codurile_calculate_sunt_numarate_nu_ignorate():
    """CE NU POATE SPUNE scanul: un cod construit dintr-o expresie (`"a" if x else "b"`) nu e literal,
    deci confruntarea nu-l poate verifica. Alea se NUMĂRĂ, nu se ascund — iar `respinge` le prinde
    oricum la rulare, fiindcă nomenclatorul e verificat acolo."""
    from core import scan_respingeri
    n = scan_respingeri.nerezolvate()
    assert len(n) <= 3, (
        "prea multe coduri calculate (%d) — confruntarea scan↔nomenclator vede tot mai puțin: %s"
        % (len(n), n))


def test_frontendul_nu_mai_clasifica_dupa_proza():
    """Instanța care a motivat conversia: `migrare.js` număra duplicatele cu
    `(e.mesaj || "").includes("există deja")`. O reformulare a mesajului rupea tăcut numărătoarea."""
    import io
    import os

    from core import scan_ancore
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cale = os.path.join(rad, "static", "js", "ecrane", "migrare.js")
    # `fara_proza` (din #14, construit azi-dimineață) scoate comentariile. Fără el, gardul se aprindea
    # pe COMENTARIUL care explică de ce clasificarea veche era greșită — a patra oară azi când un gard
    # își citește dovada din proză. Instrumentul exista; nu l-am folosit din prima.
    cod = scan_ancore.fara_proza(io.open(cale, encoding="utf-8").read(), cale)
    assert 'includes("există deja")' not in cod, (
        "migrare.js încă clasifică respingerile după textul uman — comută pe `regula`, care nu se "
        "schimbă când se rescrie mesajul")
    assert 'e.regula === "deja_exista"' in cod, (
        "clasificarea pe cod a dispărut din migrare.js — dacă s-a mutat, actualizează gardul")
