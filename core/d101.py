# -*- coding: utf-8 -*-
"""core/d101.py — D101 (Declaratie privind impozitul pe profit).

REFACUT DE LA ZERO 16.07.2026, din structura oficiala ANAF
(structura_D101_2024_200225.pdf, conform OPANAF 206/2025), citita integral.

Fisierul vechi genera dupa schema D101G ("Grup fiscal" - declaratie CONSOLIDATA
pentru grupuri fiscale, alta declaratie, cu alt formular) si avea o structura de
calcul (P1-P53) dintr-o versiune veche a formularului, incompatibila cu cea
curenta (P1-P16). O firma individuala (nu grup fiscal) foloseste D101 simplu.

Structura reala <declaratie101>:
  atribute: an, d_rec, nume_declar, prenume_declar, functie_declar, cui, den,
            adresa, telefon, Data_I (inceput exercitiu), Data_S (sfarsit
            exercitiu - OBLIGATORIU, lipsea complet in modulul vechi), caen,
            totalPlata_A
  P1  = Venituri totale
  P2  = Cheltuieli totale
  P3  = Rezultat contabil (P1-P2)
  P4  = Elemente similare veniturilor
  P5  = Elemente similare cheltuielilor
  P6  = Deduceri fiscale
  P7  = Venituri neimpozabile
  P8  = Cheltuieli nedeductibile
  P9  = Rezultat fiscal (P3+P4-P5+P8-P6-P7, minim 0)
  P10 = Pierdere fiscala recuperata
  P11 = Impozit pe profit calculat (cota x baza, rotunjit)
  P12 = Reduceri/credite fiscale
  P13 = Impozit declarat trimestrial prin D100 (plati anticipate)
  P14 = Diferenta de restituit (sponsorizare/bursa/mecenat)
  P15 = Diferenta de impozit datorata: max((P11+P14)-(P12+P13), 0)
  P16 = Diferenta de impozit de recuperat: max((P12+P13)-(P11+P14), 0)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

NS = "mfp:anaf:dgti:d101:declaratie:v10"

COTA_STANDARD = Decimal("16")   # cota standard impozit pe profit


def _esc(v):
    from xml.sax.saxutils import quoteattr
    return quoteattr(str(v if v is not None else ""))


def _i(x):
    """Rotunjire aritmetica la intreg (jumatate in sus)."""
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


@dataclass
class RezultatD101:
    an: int
    prof: dict = field(default_factory=dict)
    P: dict = field(default_factory=dict)
    total_plata_a: int = 0


def calcul_d101(prof, an, venituri_totale=0, cheltuieli_totale=0,
                 venituri_neimpozabile=0, cheltuieli_nedeductibile=0,
                 elemente_similare_venituri=0, elemente_similare_cheltuieli=0,
                 deduceri_fiscale=0, pierdere_recuperata=0,
                 impozit_trimestrial_d100=0, reduceri_credite=0,
                 diferenta_restituire=0, cota=COTA_STANDARD):
    """Calculeaza P1-P16 din datele contabile ale anului. Sume in lei intregi."""
    p1 = _i(venituri_totale)
    p2 = _i(cheltuieli_totale)
    p3 = p1 - p2
    p4 = _i(elemente_similare_venituri)
    p5 = _i(elemente_similare_cheltuieli)
    p6 = _i(deduceri_fiscale)
    p7 = _i(venituri_neimpozabile)
    p8 = _i(cheltuieli_nedeductibile)
    p9 = max(p3 + p4 - p5 + p8 - p6 - p7, 0)
    p10 = min(_i(pierdere_recuperata), p9)
    baza = max(p9 - p10, 0)
    p11 = _i(Decimal(baza) * Decimal(str(cota)) / Decimal(100))
    p12 = _i(reduceri_credite)
    p13 = _i(impozit_trimestrial_d100)
    p14 = _i(diferenta_restituire)
    v1 = (p11 + p14) - (p12 + p13)
    p15 = v1 if v1 > 0 else 0
    p16 = -v1 if v1 < 0 else 0

    P = {}
    for k, v in (("P1", p1), ("P2", p2), ("P3", p3), ("P4", p4), ("P5", p5),
                 ("P6", p6), ("P7", p7), ("P8", p8), ("P9", p9), ("P10", p10),
                 ("P11", p11), ("P12", p12), ("P13", p13), ("P14", p14),
                 ("P15", p15), ("P16", p16)):
        if v:
            P[k] = v

    return RezultatD101(an=an, prof=prof, P=P, total_plata_a=p15)


def erori_generare(prof):
    """Campuri obligatorii de profil, verificate la sursa inainte de generare."""
    erori = []
    if not (prof.get("cui") or "").strip():
        erori.append("LIPSĂ CUI (obligatoriu).")
    if not (prof.get("nume") or "").strip():
        erori.append("LIPSĂ denumire firmă (obligatorie).")
    if not (prof.get("adresa") or "").strip():
        erori.append("LIPSĂ adresă domiciliu fiscal (obligatorie).")
    if not (prof.get("caen") or "").strip():
        erori.append("LIPSĂ cod CAEN (obligatoriu în D101).")
    return erori


def build_xml(res):
    prof = res.prof
    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    hdr = ('<declaratie101 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
           'xmlns="%s" xsi:schemaLocation="%s D101.xsd" '
           'an="%d" d_rec="0" '
           'nume_declar=%s prenume_declar=%s functie_declar=%s '
           'cui=%s den=%s adresa=%s'
           % (NS, NS, res.an,
              _esc((prof.get("declarant_nume") or "ADMINISTRATOR")[:74]),
              _esc((prof.get("declarant_prenume") or "-")[:74]),
              _esc((prof.get("declarant_functie") or "ADMINISTRATOR")[:74]),
              _esc(prof.get("cui")), _esc(prof.get("nume")), _esc(prof.get("adresa"))))
    tel = (prof.get("telefon") or "").strip()
    if tel:
        hdr += ' telefon=%s' % _esc(tel)
    hdr += ' Data_I="01.01.%d"' % res.an
    hdr += ' Data_S="31.12.%d"' % res.an
    caen = (prof.get("caen") or "").strip()
    if caen:
        hdr += ' caen=%s' % _esc(caen)
    hdr += ' totalPlata_A="%d">' % res.total_plata_a
    H.append(hdr)
    for k, v in sorted(res.P.items(), key=lambda kv: int(kv[0][1:])):
        H.append('  <%s>%d</%s>' % (k, v, k))
    H.append("</declaratie101>")
    return "\n".join(H)


def genereaza(conn, schema, an, manual=None):
    """Genereaza D101 pentru anul `an`. `manual` (dict) poate suprascrie oricare
    din argumentele calcul_d101 (ex. venituri_totale, cheltuieli_totale)."""
    import psycopg2.extras as _E
    manual = dict(manual or {})
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, caen, "
                    "declarant_nume, declarant_prenume, declarant_functie "
                    "FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        if prof.get("oras"):
            prof["adresa"] = " ".join(x for x in
                (prof.get("adresa"), prof.get("oras"), prof.get("judet")) if x)
        inceput = "%04d-01-01" % an
        sfarsit = "%04d-01-01" % (an + 1)
        cur.execute(
            "SELECT COALESCE(SUM(CASE WHEN l.cont_credit LIKE '7%%' THEN l.suma "
            "ELSE 0 END),0) AS venituri, "
            "COALESCE(SUM(CASE WHEN l.cont_debit LIKE '6%%' THEN l.suma "
            "ELSE 0 END),0) AS cheltuieli "
            "FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
            "WHERE i.status = 'validata' AND i.data >= %s AND i.data < %s",
            (inceput, sfarsit))
        r = cur.fetchone() or {"venituri": 0, "cheltuieli": 0}

    erori = erori_generare(prof)
    if erori:
        raise ValueError(" ".join(erori))

    args = dict(venituri_totale=r["venituri"], cheltuieli_totale=r["cheltuieli"])
    args.update(manual)
    res = calcul_d101(prof, an, **args)
    xml = build_xml(res)
    return xml, res
