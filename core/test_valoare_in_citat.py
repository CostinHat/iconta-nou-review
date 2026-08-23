# -*- coding: utf-8 -*-
"""GARDĂ pentru interdicția 53: citatul conține VALOAREA pe care o justifică.

Planul numește 53 *„cel mai măsurabil din tot planul"* — citatul verbatim conține valoarea, sau nu.
Instrumentul e `core/scan_valoare_in_citat.py`, construit 23.08.2026, și **nu se confundă cu
`scan_citate`**: acela verifică dacă citatul EXISTĂ în documentul citat (citatul e real); acesta, dacă
citatul CONȚINE valoarea (citatul justifică). Un citat poate fi perfect real și să nu justifice nimic.

CALIBRAT PE MODUL PROPRIU DE EȘEC (interdicția 76), fiindcă prima formă a dat **34 din 34** — un
rezultat prea curat ca să fie crezut fără să fie provocat:

  1. **cifrele din ADRESĂ**. Un citat își poartă adresa în el: „art.51 alin.(1): Cota ... este de 1%".
     Valoarea `0.01` produce forma „1", care se potrivea în **„alin.(1)"** — deci `impozit_micro`
     trecea din motiv fals. Găsit prin inspecția contextului fiecărei potriviri, nu prin recitire.
     Reparat: adresele se scot înainte de căutare, iar cazul e pinuit mai jos.
  2. **subșir de număr**. „2.250.000" nu are voie să se potrivească în „12.250.000".
  3. **format diferit**. `Decimal("0.0225")` trebuie să se potrivească pe „2,25%", iar `2250000` pe
     „2.250.000" — altfel scanul ar acuza toate cotele, ceea ce ar fi un fals-pozitiv de masă.
"""
import decimal

from core import scan_valoare_in_citat as sv


def test_valoarea_din_adresa_nu_justifica():
    """CAZ CUNOSCUT. Cifra din «alin.(1)» nu justifică o cotă de 1%; cea din text, da."""
    adevarat = "art.51 alin.(1): Cota de impozit pe veniturile microintreprinderilor este de 1%"
    fals = "art.51 alin.(1): Cota de impozit pe veniturile microintreprinderilor este de 3%"
    assert sv.justifica(decimal.Decimal("0.01"), adevarat) is True, (
        "valoarea reală din substanța citatului nu e văzută")
    assert sv.justifica(decimal.Decimal("0.01"), fals) is False, (
        "cifra din ADRESA articolului a fost luată drept justificare — exact fals-pozitivul care a "
        "făcut prima formă să dea 34 din 34")


def test_nu_se_potriveste_ca_subsir_de_numar():
    """2.250.000 nu are voie să fie găsit în 12.250.000."""
    assert sv.justifica(2250000, "totalul activelor: 2.250.000 lei") is True
    assert sv.justifica(2250000, "totalul activelor: 12.250.000 lei") is False, (
        "valoarea s-a potrivit ca subșir al altui număr")


def test_formatele_romanesti_sunt_recunoscute():
    """FALS-POZITIV DE MASĂ, dacă lipsește: cotele se scriu «2,25%», nu «0.0225»."""
    assert sv.justifica(decimal.Decimal("0.0225"), "contributia ... este de 2,25%") is True
    assert sv.justifica(decimal.Decimal("0.21"), "cota standard TVA 21%") is True
    assert sv.justifica(4325, "la suma de 4.325 lei lunar") is True
    assert sv.justifica(decimal.Decimal("40.18"), "tichet masa 40,18 lei") is True


def test_valoarea_absenta_e_semnalata():
    """Miezul interdicției: un citat care nu conține valoarea nu o justifică."""
    assert sv.justifica(decimal.Decimal("0.19"), "cota standard TVA 21%") is False
    assert sv.justifica(5000, "plafonul zilnic de casa") is False


def test_fara_citat_nu_e_verdict():
    """Absența unui citat nu e o justificare, dar nici o acuzație — se raportează separat."""
    assert sv.justifica(100, None) is None
    assert sv.justifica(None, "orice text") is None


def test_registrul_de_cote_e_masurat_si_nu_e_gol():
    """ANTI-VACUU + clichet. Dacă parsarea registrului se rupe, totalul cade la zero și garda ar
    trece pe o lume goală. Iar numărul de justificate nu are voie să scadă tăcut."""
    r = sv.rezumat()
    assert r["total"] >= 30, "doar %d intrări citite din registrul de cote — parsarea s-a rupt" % r["total"]
    assert r["nejustificate"] == 0, (
        "intrări din registru a căror valoare NU apare în citatul propriu: %d. Nu înseamnă automat "
        "greșit (poate fi parafrază sau valoare în cuvinte), dar cere citire." % r["nejustificate"])
