# -*- coding: utf-8 -*-
"""
core/reconciliere_emis.py — poarta pe ARTEFACT (05.08.2026).

Inchide blind-spot-ul "pre-emisie": gardurile de continut reconciliau `res` (calculul), dar NU valoarea
PARSATA INAPOI din XML-ul livrat efectiv. Un bug in build_xml (sau o mutatie pe artefact) trecea. Aici fiecare
generator, DUPA build_xml, reconciliaza `res` cu `parse(emis)` - hard-block pe divergenta (ca gardurile de continut).

CE PRINDE: divergenta LAYER-EMISIE (build_xml transforma/pierde/corupe fata de res) + tampering pe artefact.
CE NU PRINDE (limita, declarata): erori de FORMULA ale generatorului insusi (ex. 2b, rotunjire Sigma(round) vs
ROUND per-rand) - acolo res SI emis folosesc aceeasi formula gresita, deci coincid; alea le prinde cale2 (recalcul
independent) / DUK (formula oficiala), nu aceasta poarta. Aceasta poarta garanteaza: TOTALUL emis la ANAF == totalul calculat (nu se pierde/corupe intre calcul si artefact).

ACOPERIRE: 6 din 7 declaratii au poarta pe artefact cablata (d100/d101/d205/d300/d394 pe totalPlata_A==res;
d112 pe totalPlata_A==suma A_datorat). D406 (SAF-T) e EXCEPTIA DECLARATA: n-are total canonic pe res, iar sumele-s
text 2-zec rotunjit HALF_UP (_dec) -> un assert strict res==parse pe valoarea bruta ar pierde informatie. Invariantul
lossless disponibil (verifica_d406: partida dubla TotalDebit==TotalCredit) EXISTA si prinde imbalanta, dar NU e cablat
in d406.genereaza: fixturile de test au GL neechilibrat pe luna selectata (date artificiale) -> cablarea le-ar rupe;
emisia d406 pe input echilibrat e corecta (probat 15000==15000). Cablarea d406 = curatenie de fixturi separata.
"""
import re


class ReconciliereEmis(Exception):
    """HARD-BLOCK: valoarea din artefactul XML livrat nu se reconciliaza cu calculul (res). Numeste ambele valori."""
    pass


def _iattr(xml, attr):
    m = re.search(r'\b%s="(-?\d+)"' % re.escape(attr), xml)
    return int(m.group(1)) if m else None


def verifica_total_plata_a(tip, xml, res_total):
    """d100/d101/d205/d300/d394: totalPlata_A (int, N(15)) PARSAT din artefact == res.total_plata_a. Hard-block."""
    got = _iattr(xml, "totalPlata_A")
    if got is None:
        raise ReconciliereEmis("%s: totalPlata_A absent din XML EMIS - artefactul nu contine totalul de plata" % tip)
    if got != int(res_total):
        raise ReconciliereEmis(
            "%s: total EMIS in artefact %d != res.total_plata_a %d - divergenta intre calcul si XML-ul livrat"
            % (tip, got, int(res_total)))
    return got


def verifica_d112(xml):
    """d112 (fara `res`): totalPlata_A EMIS (pe <angajator>) == SUMA A_datorat PARSATA din obligatii (<angajatorA>).
    Self-consistency lossless a artefactului: totalul de plata == suma obligatiilor lui. Hard-block pe divergenta."""
    tot = _iattr(xml, "totalPlata_A")
    if tot is None:
        raise ReconciliereEmis("d112: totalPlata_A absent din XML EMIS")
    dats = [int(m) for m in re.findall(r'A_datorat="(-?\d+)"', xml)]
    s = sum(dats)
    if tot != s:
        raise ReconciliereEmis(
            "d112: totalPlata_A EMIS %d != SUMA A_datorat %d din artefact - totalul nu corespunde obligatiilor emise"
            % (tot, s))
    return tot


def verifica_d406(xml):
    """d406/SAF-T: NU are total canonic pe `res`, iar sumele-s text 2-zec rotunjit HALF_UP (_dec) -> un assert strict
    res==parse pe valoarea BRUTA ar pierde informatie (LIMITA declarata). Se verifica ce E lossless si canonic in
    SAF-T: PARTIDA DUBLA pe registru (TotalDebit == TotalCredit), parsata din artefact. Hard-block pe imbalanta.
    Sectiunile GL goale (lunar fara note) -> None (nimic de reconciliat)."""
    from decimal import Decimal
    def _el(tag):
        m = re.search(r'<%s>\s*([\d.]+)\s*</%s>' % (tag, tag), xml)
        return m.group(1) if m else None
    td, tc = _el("TotalDebit"), _el("TotalCredit")
    if td is None or tc is None:
        return None
    if Decimal(td) != Decimal(tc):
        raise ReconciliereEmis(
            "d406: TotalDebit %s != TotalCredit %s in artefact - partida dubla rupta in XML-ul livrat" % (td, tc))
    return td
