"""
Modul D301 — Decont special de TVA (ANAF v1, OPANAF 592/2016, structură din 2013).

REFĂCUT DE LA ZERO după ANAF structura D301 20130327 (structura_D301_20130327).

D301 se depune de persoane NEînregistrate în scopuri de TVA normal (art.316),
dar care fac achiziții intracomunitare sau operațiuni cu plata TVA prin taxare inversă.

Tipuri operațiune (oficial):
  1 = achiziții intracomunitare de bunuri taxabile (altele decât transport nou/accizabile)
  2 = achiziții intracomunitare de mijloace de transport noi
  3 = achiziții intracomunitare de produse accizabile
  4 = operațiuni art.150 alin.(2),(3),(5),(6) (servicii pentru care benef. e obligat la plata)
  5 = achiziții servicii intracomunitare (art.150) — subsecțiunea 4.1

baza = round(val_valuta × curs_valutar, 0). totalPlata_A = INT(Σbaze + Σtva).

Separare strictă: calcul pur / validare / XML / DB / orchestrare.
"""

from core.common import text_anaf as _t  # limita 75 car. ANAF (27.07.2026)
import re
from core import common as c
from core.pdf_util import bani
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

NS = "mfp:anaf:dgti:d301:declaratie:v1"
REGULI = "2026.1"
_NEDIGIT = re.compile(r"\D")
TIPURI_OP = (1, 2, 3, 4, 5)
VALUTE = {"EUR", "USD", "AUD", "CAD", "CHF", "CZK", "DKK", "EGP", "GBP", "HUF",
          "JPY", "MDL", "NOK", "PLN", "RON", "SEK", "TRY", "XDR", "BGN"}


def _esc(v):
    s = "" if v is None else str(v)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))


def _clean_bc(v):
    return ("" if v is None else str(v)).replace(",", " ").replace("#", " ").strip()


def _r0(x):
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def calc_baza(val_valuta, curs):
    """baza = round(val_valuta × curs, 0) — formula oficială."""
    return _r0(Decimal(str(val_valuta)) * Decimal(str(curs)))


def nr_evidenta(an, luna, mij_transp=0):
    """C(23): poz1-2=10, 3-5=301, 6-7=01, 8-11=LLAA, 12-17=ZZLLAA scadență,
    poz18=mij_transp, 19-21=000, 22-23=sumă control."""
    ll = "%02d" % luna
    aa = "%02d" % (an % 100)
    dm, dy = luna + 1, an
    if dm > 12:
        dm, dy = 1, dy + 1
    scad = "25" + "%02d" % dm + "%02d" % (dy % 100)
    s = "10" + "301" + "01" + ll + aa + scad + ("%d" % (1 if mij_transp else 0)) + "000"
    return s + "%02d" % (sum(int(c) for c in s) % 100)


@dataclass
class Operatiune:
    tip: int
    nr_doc: str
    data_doc: str
    val_valuta: float
    tip_valuta: str
    curs: float
    baza: int = 0
    tva: int = 0


@dataclass
class Rezultat:
    an: int
    luna: int
    prof: dict
    operatiuni: list = field(default_factory=list)
    totaluri: dict = field(default_factory=dict)   # tip -> (baza, tva)
    total_plata_a: int = 0
    mij_transp: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d301(prof, an, luna, operatiuni_raw):
    """PUR. operatiuni_raw: listă de dict {tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, tva}."""
    ops = []
    tot = {t: [0, 0] for t in TIPURI_OP}
    mij = 0
    for r in operatiuni_raw:
        tip = int(r.get("tip") or 1)
        baza = calc_baza(r.get("val_valuta") or 0, r.get("curs") or 1)
        tva = _r0(r.get("tva") or 0)
        op = Operatiune(tip=tip, nr_doc=r.get("nr_doc") or "", data_doc=r.get("data_doc") or "",
                        val_valuta=float(r.get("val_valuta") or 0),
                        tip_valuta=(r.get("tip_valuta") or "EUR").upper(),
                        curs=float(r.get("curs") or 1), baza=baza, tva=tva)
        ops.append(op)
        if tip in tot:
            tot[tip][0] += baza; tot[tip][1] += tva
        # OPANAF 592/2016, instructiunile formularului 301: "In sectiunea 4.1 se preiau DIN
        # sectiunea 4 doar achizitiile de servicii intracomunitare pentru care beneficiarul e
        # obligat la plata TVA cf. art. 307 alin. (2)". S4.1 (tip 5) e SUBSET al S4 (structura
        # ANAF d301: baza4 = "Total S4 (S4=S4.1+S4.2)"), deci fiecare operatiune tip 5 se preia
        # SI in totalul S4. Fara asta baza4=0 cand exista servicii si declaratia e respinsa
        # (DUK R32: "4.1 fara 4"). E regula FISCALA, nu ocolire de validator. totalPlata_A
        # ramane formula oficiala (baza1..5 + tva1..5) - suma de control, nu TVA datorat.
        if tip == 5:
            tot[4][0] += baza; tot[4][1] += tva
        if tip == 2:
            mij = 1

    # totalPlata_A e SUMA DE CONTROL (checksum), NU TVA-ul datorat. Structura ANAF (d301 poz.28)
    # o defineste EXPLICIT: totalPlata_A = INT(baza1+..+baza5 + tva1+..+tva5), iar DUKIntegrator
    # o impune (DUK regula R28: respinge orice alta valoare). Cu rollup-ul S4.1->S4, serviciul apare
    # in baza4 SI in baza5, deci checksum-ul il numara de doua ori PRIN DEFINITIE - nu e dubla
    # impozitare: TVA-ul datorat ramane tva4 (serviciul o singura data, prin rollup). Un total pe
    # sectiunile 1-4 (6022) e respins de ANAF (dovedit: DUK regula R28 cere 12044). DUK = judecatorul final.
    total_plata = sum(tot[t][0] + tot[t][1] for t in TIPURI_OP)
    res = Rezultat(an=an, luna=luna, prof=prof, operatiuni=ops,
                   totaluri={t: tuple(tot[t]) for t in TIPURI_OP},
                   total_plata_a=total_plata, mij_transp=mij)
    res.avertismente.append("D301 %d/%d: %d operațiuni, TVA total %s."
                            % (luna, an, len(ops), bani(sum(tot[t][1] for t in TIPURI_OP), "lei")))
    return res


def erori_generare(prof):
    """Campurile de PROFIL obligatorii pentru D301. Lista goala = se poate genera.

    Acelasi nume si aceeasi semnatura ca la d100/d101/d205/d710 - aceeasi situatie,
    aceeasi rezolvare. Verificarile EXISTAU de mult in `valideaza(res)`, dar valideaza()
    NU era chemata niciodata din genereaza(): XML-ul iesea cu banca="" si cont="", iar
    ANAF il respingea cu "atribut prezent dar vid nepermis". Contabilul primea eroarea
    criptica a validatorului in loc de "completeaza IBAN-ul". Acelasi defect ca la D300, acelasi fisier-frate.

    Sursa UNICA: valideaza() cheama tot functia asta, nu-si repeta verificarile.
    """
    erori = []
    if not _NEDIGIT.sub("", prof.get("cui") or ""):
        erori.append("LIPSĂ CIF persoană impozabilă.")
    if not str(prof.get("nume") or "").strip():
        erori.append("LIPSĂ denumire.")
    if not _clean_bc(prof.get("banca")):
        erori.append("LIPSĂ bancă (obligatorie la D301).")
    if not _clean_bc(prof.get("iban") or prof.get("cont")):
        erori.append("LIPSĂ cont (obligatoriu la D301).")
    return erori

def valideaza(res):
    erori = []
    prof = res.prof
    if res.luna < 1 or res.luna > 12:
        erori.append("Lună invalidă.")
    # Campurile de profil: sursa unica e erori_generare (chemata si din genereaza).
    erori.extend(erori_generare(prof))
    for op in res.operatiuni:
        if op.tip not in TIPURI_OP:
            erori.append("Tip operațiune %s invalid." % op.tip)
        if op.tip_valuta not in VALUTE:
            erori.append("Valută %s neacceptată (nomenclator ANAF)." % op.tip_valuta)
        if not op.nr_doc:
            erori.append("Operațiune fără număr document.")
    return erori


def build_xml(res):
    prof = res.prof
    cif = _NEDIGIT.sub("", prof.get("cui") or "")
    den = prof.get("nume") or ""
    adr = " ".join(x for x in [prof.get("adresa"), prof.get("oras"), prof.get("judet")] if x).strip()
    t = res.totaluri
    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    # temei — OBLIGATORIU (validator: "temei: atributul trebuie sa existe"); lipsea
    # complet, deci D301 nu s-a validat niciodata. E temeiul legal pentru depunerea
    # declaratiei DUPA anularea rezervei verificarii ulterioare (art. 105 alin.(6) din
    # Legea 207/2015, Codul de procedura fiscala). La o depunere obisnuita = 0.
    H.append('<declaratie301 xmlns="%s" luna="%d" an="%d" d_rec="0" temei="0" mijl_trans="%d" '
             'cif="%s" denumire="%s" adresa="%s" banca="%s" cont="%s" pers_inreg="1" '
             'nr_evid="%s" baza1="%d" tva1="%d" baza2="%d" tva2="%d" baza3="%d" tva3="%d" '
             'baza4="%d" tva4="%d" baza5="%d" tva5="%d" totalPlata_A="%d" '
             'nume_declarant="%s" prenume_declarant="%s" functia_declarant="%s">'
             % (NS, res.luna, res.an, res.mij_transp, _esc(cif), _esc(_t(den)), _esc(_t(adr)),
                _esc(_clean_bc(prof.get("banca"))), _esc(_clean_bc(prof.get("iban") or prof.get("cont"))),
                nr_evidenta(res.an, res.luna, res.mij_transp),
                t[1][0], t[1][1], t[2][0], t[2][1], t[3][0], t[3][1],
                t[4][0], t[4][1], t[5][0], t[5][1], res.total_plata_a,
                _esc(_t(prof.get("declarant_nume") or "ADMINISTRATOR")),
                _esc(_t(prof.get("declarant_prenume") or "-")),
                _esc(_t(prof.get("declarant_functie") or "ADMINISTRATOR"))))
    for op in res.operatiuni:
        # OPANAF 592/2016: serviciile (tip 5 = S4.1) se preiau DIN S4 -> apar ca operatiune de
        # sectiune 4 SI ca detaliu 4.1. DUK cere baza4=suma(sectiuni tip 4) (R24/R25) si o
        # sectiune 4 cand exista 4.1 (R32), deci o operatiune tip 5 emite AMBELE randuri.
        for tp in ((4, 5) if op.tip == 5 else (op.tip,)):
            H.append('  <sectiune tip_operatie="%d" nr_doc="%s" data_doc="%s" val_valuta="%.2f" '
                     'tip_valuta="%s" curs_valutar="%.4f" baza="%d" tva="%d"/>'
                     % (tp, _esc(op.nr_doc), _esc(op.data_doc), op.val_valuta,
                        op.tip_valuta, op.curs, op.baza, op.tva))
    H.append('</declaratie301>')
    return "\n".join(H)


# [d301_canonic 23.07] ensure_tabel (CREATE TABLE IF NOT EXISTS lazy) ELIMINAT: d301_operatiuni traieste acum
# in tenant_template.sql (o singura sursa, aliniat cu decizia 22.07 anti-lazy). pull() e read-only pe tabela
# garantata de template/backfill. Vezi DECIZII 23.07.
def pull(conn, schema, an, luna):
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, banca, iban, "
                    "declarant_nume, declarant_prenume, declarant_functie "
                    "FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        cur.execute("SELECT tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, tva "
                    "FROM d301_operatiuni WHERE an=%s AND luna=%s ORDER BY id", (an, luna))
        ops = [dict(r) for r in cur.fetchall()]
    return prof, ops


def genereaza(conn, schema, an, luna):
    if luna < 1 or luna > 12:
        raise ValueError("Luna invalidă: %r" % luna)
    prof, ops = pull(conn, schema, an, luna)
    # POARTA (27.07.2026): profil incomplet -> STOP cu mesaj clar, nu XML respins de ANAF.
    erori = erori_generare(prof)
    if erori:
        raise ValueError("D301 nu se poate genera: " + " ".join(erori))
    res = calcul_d301(prof, an, luna, ops)
    return build_xml(res), res
