# -*- coding: utf-8 -*-
"""core/d114.py — D114: Declaratie privind obligatiile de plata a contributiei asiguratorii
pentru munca (CAM), pentru situatiile care NU se declara prin D112.

Contributia asiguratorie pentru munca (CAM) — Cod fiscal Titlul V, Cap.IX (art.220^1..220^7).
Declaratia se depune de persoanele care, potrivit legii, datoreaza CAM dar nu o declara prin
D112 (ex. anumite categorii fara declaratia unica lunara privind veniturile din salarii). D114
a fost aprobata prin OPANAF care stabileste modelul si continutul; periodicitate LUNARA.

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (D114Validator.jar, pachet d114validator/v0),
CITITA din bytecode (numele campurilor pe clasele D114 / Contracte / DbAccessImpl /
Parameters_v0) si PROBATA pe DUKIntegrator. Namespace: mfp:anaf:dgti:d114:declaratie:v1.
Radacina XML = <declaratie> (confirmat din bytecode). Element repetabil copil = <contracte>.

CAMPURI CITITE DIN VALIDATOR:
  <declaratie> (clasa D114): luna, an, d_rec, d_anulare, cod_obligatie, cont_bugetar,
    Nr_evid, Scadenta, total_venit, suma_datorata, totalPlata_A, cif_declarant, den_declarant,
    adresa_declarant, telefon_declarant, fax_declarant, email_declarant, functia_intocmit,
    den_intocmit, si (optional) blocul imputernicit (cif/den/adresa/telefon/fax/email_imputernicit),
    cif_suc/tipDec_suc, tipDec_insp.
  <contracte> (clasa Contracte, repetabil): cui_lucrator, den_lucrator, nui_lucrator,
    nr_contract, data_contract, venit_lucrator, contributie_lucrator.

PARAMETRI FICSI (Parameters_v0, dovediti din bytecode):
  cod_obligatie = 489  (singura constanta Long din _listaCodObligatie; coincide cu Nr_evid poz.3-5)
  cont_bugetar  = "20A470300XX"  (din _listaContBugetar; XX = placeholder LITERAL, ca la D100 "5503XXXXXX")

REGULI DE VALIDARE (mesaje incorporate in bytecode, probate pe DUK):
  R_Nr_evid (23 caractere):
    poz.1-2  = "10"           (fix — cod document, declaratie fiscala)
    poz.3-5  = "489"          (cod_obligatie CAM)
    poz.6-7  = "01"           (fix)
    poz.8-11 = LLAA           (luna raportare + ultimele 2 cifre din an)
    poz.12-17= ZZLLAA         (data scadentei)
    poz.18-21= "0000"         (fix)
    poz.22-23= suma de control (ultimele 2 cifre din suma primelor 21 de cifre)
  R_Scadenta: ZZ=25; daca luna<12 => LL=luna+1, AAAA=an; daca luna=12 => LL=1, AAAA=an+1.
  R_total_venit: total_venit = suma tuturor venit_lucrator (peste <contracte>).
  R32 (suma_datorata / contributie_lucrator): suma_datorata = total_venit * cota/100 si
    contributie_lucrator = venit_lucrator * cota/100. ATENTIE: versiunea instalata a validatorului
    (J1.0.1, 2024-01-25) enforce-uieste cota = 1/100 in mesajul R32 ("venit_lucrator * 1 / 100").
    Modulul NU hardcodeaza cota: baza (venit_lucrator) SI suma (contributie_lucrator) vin din `manual`
    — contabilul le furnizeaza consistent cu cota impusa de validator. total_venit = suma venit_lucrator
    si suma_datorata = suma contributie_lucrator (agregari pure, fara cota).
  R4 (totalPlata_A): totalPlata_A = suma CIFRELOR din cif_declarant (cod_solicitant) — cheie de
    control, NU suma banilor (dovedit pe DUK: "totalPlata_A trebuie sa fie egal cu suma cifrelor
    cod_solicitant"). Se calculeaza determinist din CUI, nu vine din input.
  R_cif_suc: daca tipDec_suc completat => cif_suc obligatoriu.

RADACINA XML = <D114> (case-sensitive, = numele clasei handler; DUK respinge <declaratie> ca
"element necunoscut"). Element repetabil copil = <contracte> (lowercase). Rotunjire half-up
(Decimal.quantize), nu rotunjirea bancara.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

NS = "mfp:anaf:dgti:d114:declaratie:v1"

COD_OBLIGATIE = "489"          # Parameters_v0._listaCodObligatie (Long 489); = Nr_evid poz.3-5
CONT_BUGETAR = "20A470300XX"   # Parameters_v0._listaContBugetar; XX = placeholder LITERAL

_NEDIGIT = re.compile(r"\D")


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _i(x):
    """Intreg cu rotunjire half-up (Decimal.quantize) — NU rotunjirea bancara."""
    return int(Decimal(str(x if x not in (None, "") else 0)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _scadenta(an, luna):
    """(zi, luna, an) scadentei CAM: ziua 25.
    luna<12 => 25 a lunii urmatoare (acelasi an); luna=12 => 25.01 an+1 (LL=1, AAAA=an+1)."""
    if luna < 12:
        return 25, luna + 1, an
    return 25, 1, an + 1


def _nr_evid(luna, an, zi_s, luna_s, an_s):
    """23 caractere, format fix D114 (dovedit din bytecode D114.class):
      poz.1-2 '10' | poz.3-5 '489' | poz.6-7 '01' | poz.8-11 LLAA (raportare) |
      poz.12-17 ZZLLAA (scadenta) | poz.18-21 '0000' | poz.22-23 suma control (last2 din sum poz.1-21)."""
    p1_21 = ("10" + COD_OBLIGATIE + "01" +
             "%02d%02d" % (luna, an % 100) +
             "%02d%02d%02d" % (zi_s, luna_s, an_s % 100) +
             "0000")
    assert len(p1_21) == 21, "Nr_evid: %d pozitii, asteptam 21" % len(p1_21)
    control = "%02d" % (sum(int(c) for c in p1_21) % 100)
    return p1_21 + control


@dataclass
class Contract:
    cui_lucrator: str
    den_lucrator: str
    venit_lucrator: int
    contributie_lucrator: int
    nui_lucrator: str = ""
    nr_contract: str = ""
    data_contract: str = ""


@dataclass
class RezultatD114:
    an: int
    luna: int
    contracte: list = field(default_factory=list)
    total_venit: int = 0
    suma_datorata: int = 0
    total_plata_a: int = 0
    scadenta: str = ""
    nr_evid: str = ""
    avertismente: list = field(default_factory=list)


def _suma_cifre(cui):
    """Suma cifrelor unui CUI/cod (DUK regula R4: totalPlata_A = suma cifrelor cod_solicitant)."""
    return sum(int(c) for c in _cif(cui))


def calcul_d114(manual, an, luna):
    """Agrega <contracte> din `manual`. total_venit = suma venit_lucrator;
    suma_datorata = suma contributie_lucrator; totalPlata_A = suma cifrelor cif_declarant (R4)."""
    contracte = []
    total_venit = 0
    suma_datorata = 0
    for c in manual.get("contracte") or []:
        venit = _i(c.get("venit_lucrator", 0))
        contrib = _i(c.get("contributie_lucrator", 0))
        contracte.append(Contract(
            cui_lucrator=_cif(c.get("cui_lucrator")),
            den_lucrator=str(c.get("den_lucrator") or ""),
            venit_lucrator=venit,
            contributie_lucrator=contrib,
            nui_lucrator=str(c.get("nui_lucrator") or ""),
            nr_contract=str(c.get("nr_contract") or ""),
            data_contract=str(c.get("data_contract") or ""),
        ))
        total_venit += venit
        suma_datorata += contrib
    zi_s, luna_s, an_s = _scadenta(an, luna)
    return RezultatD114(
        an=an, luna=luna, contracte=contracte,
        total_venit=total_venit, suma_datorata=suma_datorata,
        total_plata_a=_suma_cifre(manual.get("cif_declarant")),   # R4: suma cifrelor cod_solicitant
        scadenta="%02d.%02d.%04d" % (zi_s, luna_s, an_s),
        nr_evid=_nr_evid(luna, an, zi_s, luna_s, an_s))


def pull(conn, schema, perioada):
    """D114 = declaratie MANUALA pentru situatiile care nu se declara prin D112. Aplicatia nu are
    registrul contractelor din acest scenariu — toate valorile (baza, suma, lucratori) vin din `manual`.
    Contractul dXXX cere `pull`; intoarce {}."""
    return {}


def erori_generare(prof, manual):
    er = []
    if not (2 <= len(_cif(manual.get("cif_declarant"))) <= 10):
        er.append("CIF declarant (cif_declarant) invalid — aștept 2..10 cifre.")
    if not str(manual.get("den_declarant") or "").strip():
        er.append("Lipsă denumire declarant (den_declarant).")
    if not str(manual.get("adresa_declarant") or "").strip():
        er.append("Lipsă adresa declarant (adresa_declarant).")
    # OBLIGATORII pe radacina (dovedit pe DUK: 'atributul trebuie sa existe').
    if not str(manual.get("functia_intocmit") or "").strip():
        er.append("Lipsă funcția intocmit (functia_intocmit) - obligatoriu.")
    if not str(manual.get("den_intocmit") or "").strip():
        er.append("Lipsă nume intocmit (den_intocmit) - obligatoriu.")
    contracte = manual.get("contracte") or []
    if not contracte:
        er.append("D114 nu se depune pe zero: cel putin un <contracte> (lucrator) e obligatoriu.")
    for idx, c in enumerate(contracte, 1):
        # cui_lucrator, den_lucrator, venit, contributie, nui_lucrator, nr_contract, data_contract:
        # TOATE obligatorii pe <contracte> (dovedit pe DUK).
        if not (2 <= len(_cif(c.get("cui_lucrator"))) <= 13):
            er.append("Contract %d: cui_lucrator invalid." % idx)
        if not str(c.get("den_lucrator") or "").strip():
            er.append("Contract %d: lipsă den_lucrator." % idx)
        if _i(c.get("venit_lucrator", 0)) <= 0:
            er.append("Contract %d: venit_lucrator (baza) trebuie > 0." % idx)
        if _i(c.get("contributie_lucrator", 0)) <= 0:
            er.append("Contract %d: contributie_lucrator (suma CAM) trebuie > 0." % idx)
        if not str(c.get("nui_lucrator") or "").strip():
            er.append("Contract %d: lipsă nui_lucrator - obligatoriu." % idx)
        if not str(c.get("nr_contract") or "").strip():
            er.append("Contract %d: lipsă nr_contract - obligatoriu." % idx)
        if not str(c.get("data_contract") or "").strip():
            er.append("Contract %d: lipsă data_contract - obligatoriu." % idx)
    return er


def build_xml(prof, res, manual):
    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    hdr = ('<D114 xmlns="%s" '
           'luna="%d" an="%d" d_rec="%s" d_anulare="%s" '
           'cod_obligatie="%s" cont_bugetar="%s" '
           'Nr_evid="%s" Scadenta="%s" '
           'total_venit="%d" suma_datorata="%d" totalPlata_A="%d" '
           'cif_declarant="%s" den_declarant="%s" adresa_declarant="%s" '
           'functia_intocmit="%s" den_intocmit="%s"'
           % (NS, res.luna, res.an,
              _esc(manual.get("d_rec") or "0"), _esc(manual.get("d_anulare") or "0"),
              COD_OBLIGATIE, CONT_BUGETAR,
              res.nr_evid, res.scadenta,
              res.total_venit, res.suma_datorata, res.total_plata_a,
              _cif(manual.get("cif_declarant")),
              _esc(manual.get("den_declarant"), 200),
              _esc(manual.get("adresa_declarant"), 200),
              _esc(manual.get("functia_intocmit"), 100),
              _esc(manual.get("den_intocmit"), 200)))
    # OPTIONALE pe radacina (acceptate de validator, dar neobligatorii).
    for cheie, lim in (("telefon_declarant", 15), ("fax_declarant", 15),
                       ("email_declarant", 100)):
        if manual.get(cheie):
            hdr += ' %s="%s"' % (cheie, _esc(manual.get(cheie), lim))
    hdr += ">"
    H.append(hdr)
    for c in res.contracte:
        # Toate cele 7 atribute sunt OBLIGATORII pe <contracte> (dovedit pe DUK).
        linie = ('  <contracte cui_lucrator="%s" den_lucrator="%s" nui_lucrator="%s" '
                 'nr_contract="%s" data_contract="%s" '
                 'venit_lucrator="%d" contributie_lucrator="%d"/>'
                 % (c.cui_lucrator, _esc(c.den_lucrator, 200), _esc(c.nui_lucrator, 20),
                    _esc(c.nr_contract, 30), _esc(c.data_contract, 10),
                    c.venit_lucrator, c.contributie_lucrator))
        H.append(linie)
    H.append("</D114>")
    return "\n".join(H)


def genereaza(conn, schema, perioada, manual=None):
    """D114 lunar. `perioada.an`/`perioada.luna` = perioada de raportare.
    `manual` obligatoriu: cif_declarant, den_declarant, adresa_declarant, contracte=[{...}].
    Fiecare contract da baza (venit_lucrator) SI suma CAM (contributie_lucrator) — cota NU se hardcodeaza."""
    manual = dict(manual or {})
    an, luna = int(perioada.an), int(perioada.luna)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D114 nu se poate genera: " + " ".join(er))
    res = calcul_d114(manual, an, luna)
    xml = build_xml(prof, res, manual)
    return xml, res
