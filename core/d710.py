# -*- coding: utf-8 -*-
"""core/d710.py — D710 (Declaratie rectificativa).

Corecteaza obligatiile de plata la bugetul de stat declarate initial prin D100
(autoimpunere / retinere la sursa). MOTOR PROPRIU: namespace si structura XML
proprii (declaratie710, mfp:anaf:dgti:d710:declaratie:v2), NU o extensie a d100.py.
Reutilizeaza din d100 DOAR ce e identic la sursa (verificat 20.07.2026): nomenclatorul
COD_BUGETAR (cod bugetar per cod_oblig) si utilitarele _nr_evid / _scadenta_zile
(structura nr_evid 23 caractere e comuna D100/D710).

STRUCTURA + REGULI extrase din D710Validator.jar (parameters v10, versiuni.xml D710_56),
constant pool + mesajele de validare, 20.07.2026:
  declaratie710 (namespace mfp:anaf:dgti:d710:declaratie:v2):
    - d_anulare/d_succ/d_dizolv/d_bonif/d_nInf/d_energie: flag-uri 0/1 (ca D100)
    - d_recN: flag rectificare ("diferit de null incepand cu perioada 12.2025")
    - "daca d_succ!=0 atunci cifS trebuie completat"
  obligatie (repetabil): FIECARE suma are pereche Initial (_I) / Corectat (_C) —
    esenta rectificarii ("am declarat X initial, corect e Y"):
    - cod_oblig, cod_bugetar, luna, scadenta, nr_evid, cota (doar cod_oblig 121)
    - suma_dat_I/_C, suma_ded_I/_C, suma_plata_I/_C, suma_rest_I/_C
    - regula model 6#/7#: suma_plata = Maximum(suma_dat - suma_ded, 0);
      suma_rest = Maximum(suma_ded - suma_dat, 0); una dintre ele e 0 (nu se completeaza)
    - nr_evid 23 caractere, poz 3-5 = cod_oblig (identic D100)
    - cod bugetar determinat de cod_oblig (nomenclator, nu liber)
    - cota se completeaza DACA SI NUMAI DACA cod_oblig=121
    - luna raportare 3/6/9/12 (trimestrial, ca D100 pe care il corecteaza)

LIMITA (scop v1, decis 20.07.2026): motorul acopera rectificarea sumei DATORATE
(suma_dat_I -> suma_dat_C, cu suma_plata = suma_dat). Deducerile/reducerile/
sponsorizarile/AMEF (model 8# al validatorului: suma_ded/suma_redu/suma_spons/
suma_AMEF) au reguli DIFERITE per cod_oblig si per model (ex. la cod 103 "suma_plata =
suma_dat - suma_redu iar suma_ded nu se completeaza") - nu se acopera speculativ, se
adauga la primul caz real de rectificare cu deducere, extras iterativ pe validator.
Cazul dominant (contabilul a declarat gresit suma datorata si o corecteaza) e acoperit.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from core.d100 import COD_BUGETAR, _nr_evid, _scadenta_zile

NS = "mfp:anaf:dgti:d710:declaratie:v2"


def _esc(v):
    from xml.sax.saxutils import quoteattr
    return quoteattr(str(v if v is not None else ""))


def _i(x):
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


@dataclass
class ObligatieRect:
    """O obligatie corectata: suma initiala (asa cum a fost declarata gresit in D100)
    si suma corectata (valoarea corecta pt perioada). Rectificare a sumei DATORATE:
    suma de plata = suma datorata (fara deduceri/reduceri - vezi LIMITA in modul)."""
    cod_oblig: str
    suma_dat_i: int
    suma_dat_c: int
    cod_bugetar: str = ""
    scadenta: str = ""
    nr_evid: str = ""
    cota: str = ""

    @property
    def suma_plata_i(self):
        return self.suma_dat_i

    @property
    def suma_plata_c(self):
        return self.suma_dat_c


@dataclass
class RezultatD710:
    an: int
    luna: int
    prof: dict = field(default_factory=dict)
    obligatii: list = field(default_factory=list)
    total_plata_a: int = 0


def _scadenta_d710(cod, an, luna):
    """(zi, luna, an) scadentei per cod_oblig. Standard = 25 a lunii urmatoare
    (_scadenta_zile). EXCEPTIE cod 121 (impozit micro) trim4 (luna 12): scadenta e
    25.06 an urmator - termenul special de definitivare (regula R15 validator D710)."""
    if cod == "121" and luna == 12:
        return 25, 6, an + 1
    return _scadenta_zile(an, luna)


def calcul_d710(prof, an, luna, obligatii):
    """`luna` = 3/6/9/12 (trimestrial, ca D100). `obligatii` = lista de dict-uri
    {cod_oblig, suma_dat_i, suma_dat_c, cod_bugetar?, cota?, suma_ded_i?, suma_ded_c?}."""
    if luna not in (3, 6, 9, 12):
        raise ValueError("D710 (corectie D100 trimestrial): luna trebuie 3/6/9/12 (primit %r)." % luna)
    obl = []
    total = 0
    for o in obligatii or []:
        cod = str(o["cod_oblig"])
        di, dc = _i(o.get("suma_dat_i", 0)), _i(o.get("suma_dat_c", 0))
        if di <= 0 and dc <= 0:
            continue
        zi_s, luna_s, an_s = _scadenta_d710(cod, an, luna)
        scad = o.get("scadenta") or ("%02d.%02d.%04d" % (zi_s, luna_s, an_s))
        r = ObligatieRect(
            cod_oblig=cod, suma_dat_i=di, suma_dat_c=dc,
            cod_bugetar=o.get("cod_bugetar") or COD_BUGETAR.get(cod, ""),
            scadenta=scad, nr_evid=_nr_evid(cod, luna, an, zi_s, luna_s, an_s),
            cota=str(o.get("cota") or ""))
        obl.append(r)
        # totalPlata_A = suma de control ceruta de validator (R11b): SUMA sumelor
        # datorat + plata pe fiecare obligatie, ambele laturi (initial + corectat).
        # Dovedit pe validator: 100(dat_I)+100(plata_I)+150(dat_C)+150(plata_C)=500.
        total += (r.suma_dat_i + r.suma_plata_i + r.suma_dat_c + r.suma_plata_c)
    return RezultatD710(an=an, luna=luna, prof=prof, obligatii=obl, total_plata_a=total)


def erori_generare(prof):
    erori = []
    if not (prof.get("cui") or "").strip():
        erori.append("LIPSĂ CUI (obligatoriu).")
    if not (prof.get("nume") or "").strip():
        erori.append("LIPSĂ denumire firmă (obligatorie).")
    if not (prof.get("adresa") or "").strip():
        erori.append("LIPSĂ adresă domiciliu fiscal (obligatorie).")
    return erori


def build_xml(res):
    prof = res.prof
    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    # d_recN: atribut introdus de la perioada de raportare 12.2025 (regula validator
    # "d_recN diferit de null incepand cu perioada 12.2025"). Pentru perioade anterioare
    # NU se pune (validatorul il respinge). Se completeaza "1" (declaratie rectificativa).
    d_recn = ' d_recN="1"' if (res.an * 100 + res.luna) >= 202512 else ''
    hdr = ('<declaratie710 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
           'xmlns="%s" xsi:schemaLocation="%s D710.xsd" '
           'luna="%d" an="%d" d_anulare="0" d_succ="0" d_dizolv="0" '
           'd_bonif="0" d_nInf="0" d_energie="0"%s '
           'nume_declar=%s prenume_declar=%s functie_declar=%s '
           'cui=%s den=%s adresa=%s'
           % (NS, NS, res.luna, res.an, d_recn,
              _esc((prof.get("declarant_nume") or "ADMINISTRATOR")[:74]),
              _esc((prof.get("declarant_prenume") or "-")[:74]),
              _esc((prof.get("declarant_functie") or "ADMINISTRATOR")[:74]),
              _esc(prof.get("cui")), _esc(prof.get("nume")), _esc(prof.get("adresa"))))
    tel = (prof.get("telefon") or "").strip()
    if tel:
        hdr += ' telefon=%s' % _esc(tel)
    hdr += ' totalPlata_A="%d">' % res.total_plata_a
    H.append(hdr)
    for o in res.obligatii:
        linie = ('  <obligatie cod_oblig="%s" scadenta="%s" nr_evid="%s" '
                 'suma_dat_I="%d" suma_dat_C="%d" '
                 'suma_plata_I="%d" suma_plata_C="%d"'
                 % (o.cod_oblig, o.scadenta, o.nr_evid,
                    o.suma_dat_i, o.suma_dat_c, o.suma_plata_i, o.suma_plata_c))
        if o.cod_bugetar:
            linie += ' cod_bugetar=%s' % _esc(o.cod_bugetar)
        if o.cota:
            linie += ' cota=%s' % _esc(o.cota)
        linie += "/>"
        H.append(linie)
    H.append("</declaratie710>")
    return "\n".join(H)


def genereaza(conn, schema, an, trim, obligatii):
    """Genereaza D710 pt corectarea D100 pe trimestrul `trim` (1-4). `obligatii` =
    lista de corectii {cod_oblig, suma_dat_i, suma_dat_c, cota?, ...}, aduse de apelant
    (contabilul stie ce a declarat gresit vs corect - nu se recalculeaza aici)."""
    import psycopg2.extras as _E
    luna = trim * 3
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, "
                    "declarant_nume, declarant_prenume, declarant_functie "
                    "FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        if prof.get("oras"):
            prof["adresa"] = " ".join(x for x in
                (prof.get("adresa"), prof.get("oras"), prof.get("judet")) if x)
    erori = erori_generare(prof)
    if erori:
        raise ValueError(" ".join(erori))
    res = calcul_d710(prof, an, luna, obligatii)
    xml = build_xml(res)
    return xml, res
