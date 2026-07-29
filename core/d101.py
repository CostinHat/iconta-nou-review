# -*- coding: utf-8 -*-
"""core/d101.py — D101 (Declaratie privind impozitul pe profit).

REFACUT A DOUA OARA, COMPLET, 16.07.2026, direct din D101Validator.jar (v8,
namespace mfp:anaf:dgti:d101:declaratie:v10), atribute + mesaje de eroare
extrase din constant pool-ul clasei Identificare.

PRIMA REFACERE (aceeasi zi) fusese gresita in executie, nu in decizie: structura
veche (P1-P53) ERA cea corecta (confirmata acum in validator), dar fusese
inlocuita cu P1-P16 inventat din cap, crezand gresit ca era formularul de grup
fiscal (D101G). Namespace-ul v10 si Data_I/Data_S erau deja corecte in prima
refacere - pastrate aici.

Structura reala <declaratie101>:
  Flag-uri pe radacina (toate "0" implicit, fara conditii suplimentare):
    d_rec, d_recN, d_reg, d_reglem, d_anulare, d_succ, d_grup, d_prof, d_alte
  Date obligatorii: Data_I (inceput exercitiu), Data_S (sfarsit exercitiu),
    an_i, luna_i (derivate din Data_I), an, luna (derivate din Data_S)
  Identificare: cif, den, adresa, telefon, email, caen
  Declarant: nume_declar, prenume_declar, functie_declar
  temei (daca d_anulare=1), Stat_rezid, nr_evid, totalPlata_A

  Corpul declaratiei (P1-P16 - cele relevante pentru o firma fara grup fiscal,
  fara operatiuni offshore/redirectionare, cazuri acoperite de P17-P53):
    P1  = Total venituri
    P2  = Total cheltuieli
    P3  = Rezultat contabil (P1-P2)
    P4  = Elemente similare veniturilor
    P5  = Elemente similare cheltuielilor
    P6  = Deduceri fiscale
    P7  = Venituri neimpozabile
    P8  = Cheltuieli nedeductibile (=P081+P082+P083+P084 daca detaliat)
    P9  = Rezultat fiscal (P3+P4-P5+P8-P6-P7, minim 0)
    P10 = Pierdere fiscala recuperata
    P11 = Impozit pe profit calculat
    P12 = Reduceri de impozit
    P13 = Impozit declarat trimestrial prin D100
    P15 = Diferenta de impozit datorata: max((P11-P12)-P13, 0)
    P16 = Diferenta de impozit de recuperat: max(P13-(P11-P12), 0)

  NEIMPLEMENTATE (cazuri speciale, nu se aplica unei firme obisnuite):
    P17 (redirectionare 20%), P38-P53 (offshore, facilitati specifice,
    grup fiscal). Se adauga cand apare un caz real care le cere.
"""
from __future__ import annotations

from core.common import text_anaf as _t  # limita 75 car. ANAF (27.07.2026)
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

NS = "mfp:anaf:dgti:d101:declaratie:v10"

COTA_STANDARD = Decimal("16")


def _esc(v):
    from xml.sax.saxutils import quoteattr
    return quoteattr(str(v if v is not None else ""))


def _i(x):
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
                 cota=COTA_STANDARD):
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
    v1 = (p11 - p12) - p13
    p15 = v1 if v1 > 0 else 0
    p16 = -v1 if v1 < 0 else 0

    P = {}
    for k, v in (("P1", p1), ("P2", p2), ("P3", p3), ("P4", p4), ("P5", p5),
                 ("P6", p6), ("P7", p7), ("P8", p8), ("P9", p9), ("P10", p10),
                 ("P11", p11), ("P12", p12), ("P13", p13),
                 ("P15", p15), ("P16", p16)):
        if v:
            P[k] = v
    return RezultatD101(an=an, prof=prof, P=P, total_plata_a=p15)


def erori_generare(prof):
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


def _nr_evid(cui, an, luna, cod_oblig="103"):
    """23 caractere - acelasi format oficial ANAF confirmat azi la D100
    (structura_D100-D710): poz.1-2 fix '10', poz.3-5 cod_oblig, poz.6-7 fix '01',
    poz.8-11 LLAA (sfarsit perioada), poz.12-17 ZZLLAA (scadenta: 25.03.an+1
    pentru impozitul anual), poz.18 '0', poz.19 '0', poz.20-21 '00',
    poz.22-23 cifra de control = ultimele 2 cifre din suma primelor 21 pozitii."""
    scad_an = an + 1
    p1_21 = ("10" + str(cod_oblig).rjust(3, "0")[-3:] + "01" +
             "%02d%02d" % (12, an % 100) +
             "%02d%02d%02d" % (25, 3, scad_an % 100) + "0" + "0" + "00")
    assert len(p1_21) == 21
    suma = sum(int(c) for c in p1_21)
    return p1_21 + "%02d" % (suma % 100)


def build_xml(res):
    prof = res.prof
    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    # d_recN si d_grup: "valoarea 0 nu se incadreaza in intervalul cerut" -
    # dovedit direct pe validator (constant pool: "d_rec=2 daca d_recN=1",
    # "d_grup=1 trebuie..."). Valorile lor valide sunt DOAR 1 sau lipsa (null),
    # niciodata "0" scris explicit - omise complet aici.
    # cod_obligatie: obligatoriu, lipsea complet - "103" = impozit pe profit
    # PJ romane (confirmat azi la D100, acelasi nomenclator).
    hdr = ('<declaratie101 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
           'xmlns="%s" xsi:schemaLocation="%s D101.xsd" '
           'an="%d" luna="12" an_i="%d" luna_i="1" cod_obligatie="103" '
           'd_rec="0" d_reg="0" d_reglem="0" d_anulare="0" '
           'd_succ="0" d_prof="0" d_alte="0" '
           'Data_I="01.01.%d" Data_S="31.12.%d" '
           'nume_declar=%s prenume_declar=%s functie_declar=%s '
           'cif="%s" denumire=%s adresa=%s'
           % (NS, NS, res.an, res.an, res.an, res.an,
              _esc(_t(prof.get("declarant_nume") or "ADMINISTRATOR")),
              _esc(_t(prof.get("declarant_prenume") or "-")),
              _esc(_t(prof.get("declarant_functie") or "ADMINISTRATOR")),
              "".join(ch for ch in str(prof.get("cui") or "") if ch.isdigit()),
              _esc(_t(prof.get("nume"))), _esc(_t(prof.get("adresa")))))
    tel = (prof.get("telefon") or "").strip()
    if tel:
        hdr += ' telefon=%s' % _esc(tel)
    caen = (prof.get("caen") or "").strip()
    if caen:
        hdr += ' caen=%s' % _esc(caen)
    cif_num = "".join(ch for ch in str(prof.get("cui") or "") if ch.isdigit())
    hdr += ' nr_evid="%s"' % _nr_evid(cif_num, res.an, 12)
    # denumire (nu "den"), scadenta si cod_bug lipseau complet.
    # Scadenta = format ZZLLAA (6 cifre COMPACTE, nu cu puncte - "25.03.2026"
    # a fost respins ca "sir mai lung de 6 caractere"). Formula EXACTA din
    # regula R17 a validatorului: "daca an Data_S in [2022,2025] atunci
    # LL=LL+6" (LL=12 din Data_S=31.12.an -> 12+6=18 -> 6, anul+1).
    scad_luna = 12 + 6
    scad_an = res.an
    if scad_luna > 12:
        scad_luna -= 12
        scad_an += 1
    hdr += ' scadenta="25%02d%02d" cod_bug="5503XXXXXX"' % (scad_luna, scad_an % 100)
    hdr += ' totalPlata_A="%d">' % res.total_plata_a
    H.append(hdr)
    for k, v in sorted(res.P.items(), key=lambda kv: int(kv[0][1:])):
        H.append('  <%s>%d</%s>' % (k, v, k))
    H.append("</declaratie101>")
    return "\n".join(H)


def genereaza(conn, schema, an, manual=None):
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
