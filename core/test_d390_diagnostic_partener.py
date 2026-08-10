# -*- coding: utf-8 -*-
"""[TURA 3] D390 - diagnoza EU-VAT PER-PARTENER, pre-DUK (T1/T3/T2/T6).

FLAGSHIP: azi (HEAD 8b74ccb) un cod TVA UE checksum-invalid dar bine-format se emite FARA nicio
diagnoza (utilizatorul afla abia din DUK R24.1 brut), iar o tara mistypata (CR pt HR, GR pt EL)
face partenerul sa DISPARA intr-un count agregat anonim. Aici: fiecare partener problematic e NUMIT
(denumire + CUI + factura + motiv), iar operatiunea obligatorie NU dispare tacit (principiu Costin).

Gard: aceste teste PICA pe HEAD (silent/agregat/trunchiat) si TREC dupa fix.
"""
import pytest
from core import d390
from core.d390 import calcul_d390, valideaza, build_xml, checksum_vies


def _prof(**kw):
    p = {"cui": "14399840", "nume": "DANTE INTERNATIONAL SA",
         "adresa": "Bd. Timisoara 26Z", "telefon": "0212345678"}
    p.update(kw)
    return p


def _oib_valid(base10="1234567890"):
    x = 10
    for ch in base10:
        x = (x + int(ch)) % 10
        if x == 0:
            x = 10
        x = (x * 2) % 11
    return base10 + str((11 - x) % 10)


# ── VIES checksum (subset ancorat pe DUK) ────────────────────────────────────────
def test_checksum_vies_valori_acceptate_de_duk_sunt_ok():
    """Valorile pe care DUK-ul instalat le ACCEPTA (proba boundary 10.08.2026) trec offline."""
    assert checksum_vies("DE", "136695976")[0] == "ok"      # DE seed valid (MOD 11,10)
    assert checksum_vies("FR", "40303265045")[0] == "ok"    # FR seed valid (cheia SIREN)
    assert checksum_vies("HR", _oib_valid())[0] == "ok"     # HR OIB valid (MOD 11,10)


def test_checksum_vies_de_gresit_e_invalid():
    """DE cu ultima cifra gresita (136695975 in loc de ...976) -> checksum invalid, offline."""
    assert checksum_vies("DE", "136695975")[0] == "invalid"
    assert checksum_vies("FR", "99303265045")[0] == "invalid"


def test_checksum_vies_tara_neimplementata_e_neverificat_nu_fals_pozitiv():
    """Fara fals-pozitiv pe tari neimplementate offline (IT/ES...) - se lasa pe DUK."""
    assert checksum_vies("IT", "00905811006")[0] == "neverificat"
    assert checksum_vies("ES", "A12345678")[0] == "neverificat"


# ── FLAGSHIP (i): checksum-bad DE VAT -> per-partener, nu tacit ───────────────────
def test_checksum_bad_de_numeste_partenerul_nu_tacit():
    """OLD (HEAD): DE checksum-invalid emis fara nicio diagnoza (-> DUK R24.1). NEW: avertisment
    per-partener care numeste denumirea + CUI-ul, cu motivul (cifra de control)."""
    fac = [{"cui": "DE136695975", "nume": "KUNDE FALSCH GMBH",
            "directie": "emisa", "total": 2000, "tva": 0}]
    res = calcul_d390(_prof(), 2026, 8, fac)
    # operatiunea NU dispare (Costin: raportata cu CUI invalid > disparuta tacit)
    assert res.nr_opi == 1
    msg = " ".join(res.avertismente)
    assert "KUNDE FALSCH GMBH" in msg and "DE136695975" in msg, msg
    assert "invalid" in msg.lower(), msg
    # e in diag ca checksum, NU blocant (nu iese pe valideaza)
    assert any(d["categorie"] == "checksum" for d in res.diag)
    assert not any("KUNDE FALSCH" in e for e in valideaza(res))


def test_checksum_bun_de_fr_nu_produce_avertisment():
    """Baseline valid: DE/FR cu checksum bun NU produc niciun avertisment de checksum."""
    fac = [{"cui": "DE136695976", "nume": "KUNDE DE GMBH", "directie": "emisa", "total": 2000, "tva": 0},
           {"cui": "FR40303265045", "nume": "FOURNISSEUR FR", "directie": "primita", "total": 1500, "tva": 0}]
    res = calcul_d390(_prof(), 2026, 8, fac)
    assert res.nr_opi == 2
    assert not any(d["categorie"] == "checksum" for d in res.diag)
    assert valideaza(res) == []


# ── FLAGSHIP (ii): tara mistypata -> partenerul NU dispare, e numit + sugestie ─────
def test_tara_mistypata_CR_numeste_partenerul_si_sugereaza_HR():
    """OLD (HEAD): 'CR' (Croatia mistypata) -> partenerul cade in skip_dom, count agregat anonim.
    NEW: partener NUMIT + reason + sugestie HR; valideaza il face BLOCANT (nu dispare tacit)."""
    fac = [{"cui": "CR" + _oib_valid(), "nume": "ZAGREB DOO",
            "directie": "emisa", "total": 5000, "tva": 0}]
    res = calcul_d390(_prof(), 2026, 8, fac)
    assert res.nr_opi == 0                                  # nu poate intra (tara ne-nomenclator)
    msg = " ".join(res.avertismente)
    assert "ZAGREB DOO" in msg and "HR" in msg, msg        # numit + sugestie HR
    er = valideaza(res)
    assert any("ZAGREB DOO" in e and "HR" in e for e in er), er   # BLOCANT, numeste partenerul


def test_tara_mistypata_GR_sugereaza_EL():
    fac = [{"cui": "GR123456789", "nume": "ATHENS AE", "directie": "emisa", "total": 1000, "tva": 0}]
    res = calcul_d390(_prof(), 2026, 8, fac)
    er = valideaza(res)
    assert any("ATHENS AE" in e and "EL" in e for e in er), er


# ── T6: codO > 12 NU se trunchiaza tacit (ar corupe VAT-ul) ───────────────────────
def test_codO_peste_12_nu_se_trunchiaza_ci_blocheaza_numind_partenerul():
    """OLD (HEAD): cod[:12] -> trunchiere TACITA care CORUPE numarul de TVA. NEW: NU trunchia;
    valideaza blocheaza numind partenerul (cod pastrat intreg in ops, nu ciuntit)."""
    long_cod = "DE12345678901234"   # 14 caractere dupa prefix -> >12
    fac = [{"cui": long_cod, "nume": "LANG GMBH", "directie": "emisa", "total": 1000, "tva": 0}]
    res = calcul_d390(_prof(), 2026, 8, fac)
    # codul NU e trunchiat la 12 in ops
    assert any(len(cod) > 12 for (_t, _ta, cod, _d) in res.ops), res.ops
    assert any(d["categorie"] == "codO_lung" for d in res.diag)
    er = valideaza(res)
    assert any("LANG GMBH" in e and "12" in e for e in er), er


def test_codO_manual_peste_12_blocheaza():
    man = [{"tip": "S", "tara": "DE", "cod": "1234567890123456", "den": "SERVICE LANG", "baza": 100}]
    res = calcul_d390(_prof(), 2026, 8, [], manual=man)
    assert any(d["categorie"] == "codO_lung" for d in res.diag)
    assert any("codO manual" in e for e in valideaza(res))


# ── T6: telefon > 15 (clamp + avertisment) / cui firma > 10 (blocant) ─────────────
def test_telefon_peste_15_clamp_cu_avertisment_nu_tacit():
    res = calcul_d390(_prof(telefon="0" * 20), 2026, 8,
                      [{"cui": "DE136695976", "nume": "X", "directie": "emisa", "total": 100, "tva": 0}])
    assert any("Telefon" in a and "15" in a for a in res.avertismente)
    xml = build_xml(res)
    # emis clampat la 15 (nu 20)
    import re
    m = re.search(r'telefon="([^"]*)"', xml)
    assert m and len(m.group(1)) == 15, m and m.group(1)


def test_cui_firma_peste_10_cifre_blocheaza():
    res = calcul_d390(_prof(cui="123456789012"), 2026, 8,
                      [{"cui": "DE136695976", "nume": "X", "directie": "emisa", "total": 100, "tva": 0}])
    assert any("CUI firma" in e and "10" in e for e in valideaza(res))


# ── T2: valideaza(res) e CABLAT in genereaza (era cod mort) ───────────────────────
def _fake_pull(monkeypatch, facturi, prof=None):
    prof = prof or _prof()
    monkeypatch.setattr(d390, "pull", lambda *a, **k: (prof, facturi))
    monkeypatch.setattr(d390, "pull_manual", lambda *a, **k: [])
    monkeypatch.setattr(d390, "pull_reclasificari", lambda *a, **k: {})


def test_genereaza_ridica_pe_tara_mistypata_numind_partenerul(monkeypatch):
    """T2: genereaza cheama valideaza -> ValueError cu partenerul NUMIT, PRE-DUK (nu XML respins)."""
    _fake_pull(monkeypatch, [{"cui": "CR" + _oib_valid(), "nume": "ZAGREB DOO",
                              "directie": "emisa", "total": 5000, "tva": 0}])
    with pytest.raises(ValueError) as e:
        d390.genereaza(None, "x", 2026, 8)
    assert "ZAGREB DOO" in str(e.value) and "HR" in str(e.value), str(e.value)


def test_genereaza_ridica_pe_codO_lung(monkeypatch):
    _fake_pull(monkeypatch, [{"cui": "DE12345678901234", "nume": "LANG GMBH",
                              "directie": "emisa", "total": 1000, "tva": 0}])
    with pytest.raises(ValueError) as e:
        d390.genereaza(None, "x", 2026, 8)
    assert "LANG GMBH" in str(e.value), str(e.value)


def test_genereaza_baseline_valid_trece(monkeypatch):
    """Baseline valid (DE/FR checksum bun) genereaza XML fara sa ridice."""
    _fake_pull(monkeypatch, [{"cui": "DE136695976", "nume": "KUNDE DE GMBH", "directie": "emisa", "total": 2000, "tva": 0},
                             {"cui": "FR40303265045", "nume": "FOURNISSEUR FR", "directie": "primita", "total": 1500, "tva": 0}])
    xml, res = d390.genereaza(None, "x", 2026, 8)
    assert res.nr_opi == 2 and "<operatie" in xml


# ── build_xml: codO gol OMIS (A/S) - nu emite codO="" (respins structural de DUK) ──
def test_codO_gol_omis_pentru_A_nu_emite_atribut_vid():
    """A/S: codO POATE lipsi; build_xml OMITE atributul cand e gol (codO="" e respins de DUK
    'prezent dar vid nepermis'). L,T,P,R gol e blocat separat de valideaza."""
    man = [{"tip": "A", "tara": "DE", "cod": "", "den": "ACHIZ FARA COD", "baza": 500}]
    res = calcul_d390(_prof(), 2026, 8, [], manual=man)
    xml = build_xml(res)
    assert 'codO=""' not in xml, xml
    assert "ACHIZ FARA COD" in xml


# ── domestic (RO/fara CUI) ramane exclus, dar NU inundam cu per-partener ──────────
def test_parteneri_domestici_raman_sumar_scurt_nu_per_partener():
    fac = [{"cui": "143000000", "nume": "CLIENT RO", "directie": "emisa", "total": 1210, "tva": 210},
           {"cui": "", "nume": "PFA LOCALA", "directie": "primita", "total": 300, "tva": 0},
           {"cui": "DE136695976", "nume": "KUNDE DE", "directie": "emisa", "total": 2000, "tva": 0}]
    res = calcul_d390(_prof(), 2026, 8, fac)
    assert res.nr_opi == 1                                  # doar DE intra
    assert any("interni" in a and "excluse" in a for a in res.avertismente)
    # domesticele NU produc erori blocante
    assert valideaza(res) == []
