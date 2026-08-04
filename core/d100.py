# -*- coding: utf-8 -*-
"""core/d100.py — D100 (Declaratie privind obligatiile de plata la bugetul de stat).

REFACUT DE LA ZERO 16.07.2026, a doua oara: prima rescriere ("de la zero") a
completat goluri din presupunere (d_rec inventat, obligatii lipsa pentru regim
profit) in loc sa extraga TOATE regulile din validator inainte de a scrie vreo
linie. A doua oara: toate atributele SI toate regulile de validare (mesajele de
eroare incorporate in D100Validator.jar v9) au fost citite complet, apoi s-a
scris codul o singura data.

REGULI EXTRASE DIN VALIDATOR (constant pool, D100Validator.jar v9):
  Declaratie100:
    - d_anulare, d_succ, d_dizolv, d_bonif, d_nInf, d_energie: flag-uri 0/1
    - "daca d_succ!=0 atunci cifS trebuie completat"
    - "daca d_anulare!=0 atunci temei trebuie completat"
    - implicit toate = "0" -> nu se cere nimic suplimentar
    - NU exista atribut d_rec pe D100 (spre deosebire de D300/D390) - eliminat
  Obligatie (element repetabil, unul per cod din Nomenclator):
    - cod_oblig, cod_bugetar, cui, luna, cota, Data_I, scadenta, tip_oblig,
      suma_dat, suma_ded, suma_plata, suma_rest, suma_bonif, suma_spons, nr_evid
    - "cod obligatie (X) necesita raportare trimestriala si luna (Y) trebuie sa
      fie 3, 6, 9 sau 12" -> luna pe Obligatie trebuie sa fie explicit 3/6/9/12
    - "nr_evid (X) trebuie sa aibe lungimea de 23 caractere" -> OBLIGATORIU,
      format fix
    - "cod bugetar (X) trebuie sa fie = Y pt. acest cod_oblig" -> cod_bugetar
      NU e liber, e determinat de cod_oblig (nomenclator)
    - "suma_spons trebuie sa fie <= 20% din suma_dat"
    - "Pt cod obligatie 121, cota trebuie sa fie = 1"
"""
from __future__ import annotations

from datetime import date
from core import common as _common
from core.common import text_anaf as _t, cheie_manual, LIMITE_TEXT_ANAF as _LIM  # limite text per-camp din structura (03.08.2026)
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import datetime as _dt

NS = "mfp:anaf:dgti:d100:declaratie:v2"

# Nomenclator ANAF partial - cod_oblig -> cod_bugetar (validatorul cere corespondenta
# EXACTA: "cod bugetar trebuie sa fie = X pt. acest cod_oblig"). Extins pe masura ce
# se adauga obligatii noi.
# Nomenclator ANAF (https://static.anaf.ro/.../NomBugetStat.htm, verificat 16.07.2026)
# + coduri XML reale confirmate prin structura_D100-D710 si intrebari reale de
# contabili (accountable.ro, portalsalarizare.ro): pozitia din nomenclator NU e
# codul XML - "poz.2" din tabelul oficial corespunde cod_oblig "103".
COD_BUGETAR = {
    # cod_oblig e CODUL din nomenclator (N(3)), NU pozitia din tabel. Impozit micro =
    # poz.5 in tabel, dar cod_oblig REAL = 121 (dovedit: d100_struct_anaf.txt "5. 121
    # (poz.5)" + validator "valoarea '5' nu se afla in lista"). cod bugetar = cont unic
    # 5503 X-padat la 10 caractere (ANAF C(10)), cont unic ca impozitul pe profit; contul 20470101
    # a fost inlocuit oficial cu 5503 din 26.07.2018 (d100_struct_anaf.txt:562); d101/d112 emit deja "5503XXXXXX".
    "121": "5503XXXXXX",     # poz.5 Nomenclator: impozit pe veniturile microintreprinderilor (cont unic 5503)
    "103": "5503XXXXXX",     # poz.2 Nomenclator: impozit pe profit/plati anticipate PJ romane
                             # (altele decat institutii de credit) - cont unic 5503
}


def _esc(v):
    from xml.sax.saxutils import quoteattr
    return quoteattr(str(v if v is not None else ""))


def _i(x):
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _rata_impozit_default(regim, an, luna):
    """Rata default (micro 1% / profit 16%) din registrul de cote - nume UNIC ca graful sa vada dependenta
    (genereaza se ciocneste pe nume cu alte module -> ar fi invizibila). Contabilul o poate da explicit
    prin manual; asta e doar fallback-ul. TEMEI: CF art.51 (micro), art.17 (profit). nivel_sursa: REDARE."""
    d = date(an, luna, 1)
    # chei LITERALE (nu variabila) ca graful sa vada ambele dependente
    if regim == "micro":
        return _common.cota("impozit_micro", d)[0] * 100
    return _common.cota("impozit_profit", d)[0] * 100


def _nr_evid(cod_oblig, luna, an, zi_scadenta, luna_scadenta, an_scadenta, tip_oblig="1"):
    """23 caractere. Format oficial ANAF (structura_D100-D710, ex.
    10602010611250711000035), verificat 16.07.2026 din documentul oficial:
      Poz.1-2  : "10" (fix - cod document, declaratie fiscala)
      Poz.3-5  : cod_oblig (nomenclator), 3 cifre
      Poz.6-7  : "01" (fix)
      Poz.8-11 : LLAA - luna+an (2 cifre) de SFARSIT de perioada raportare
      Poz.12-17: ZZLLAA - data scadentei
      Poz.18   : 1 daca tip_oblig=1, 0 daca tip_oblig=2
      Poz.19   : "0"
      Poz.20-21: "00"
      Poz.22-23: suma de control = ultimele 2 cifre din suma primelor 21 pozitii
    """
    # Poz.18: exemplul oficial (obligatia 602, cont unic) are "0" - deci "0" e
    # valoarea uzuala/implicita, nu "1 daca tip_oblig=1". Corectat dupa eroarea
    # R16 pe validator: "1" respins ca "pozitii fixe eronate".
    p1_21 = ("10" + str(cod_oblig).rjust(3, "0")[-3:] + "01" +
             "%02d%02d" % (luna, an % 100) +
             "%02d%02d%02d" % (zi_scadenta, luna_scadenta, an_scadenta % 100) +
             "0" + "0" + "00")
    assert len(p1_21) == 21, "nr_evid: %d pozitii, asteptam 21" % len(p1_21)
    suma = sum(int(c) for c in p1_21)
    control = "%02d" % (suma % 100)
    return p1_21 + control


@dataclass
class Obligatie:
    cod_oblig: str
    suma_dat: int
    cod_bugetar: str = ""
    scadenta: str = ""
    nr_evid: str = ""
    cota: str = ""          # doar pt. cod_oblig 121 (micro): validator cere cota="1"


@dataclass
class RezultatD100:
    an: int
    luna: int
    prof: dict = field(default_factory=dict)
    obligatii: list = field(default_factory=list)
    total_plata_a: int = 0


def calcul_d100(prof, an, luna, obligatii):
    """`luna` trebuie sa fie 3, 6, 9 sau 12 (raportare trimestriala) - dovedit
    obligatoriu de validator. `obligatii` = [{cod_oblig, suma_dat, cod_bugetar?}]."""
    if luna not in (3, 6, 9, 12):
        raise ValueError("D100 trimestrial: luna trebuie sa fie 3, 6, 9 sau 12 (primit %r)." % luna)
    cui = prof.get("cui")
    obl = []
    total = 0
    for o in obligatii or []:
        suma = _i(o.get("suma_dat", 0))
        if suma <= 0:
            continue
        cod = str(o["cod_oblig"])
        cod_bug = o.get("cod_bugetar") or COD_BUGETAR.get(cod, "")
        if not cod_bug:
            raise ValueError("D100: cod_oblig %r fara cont bugetar (nu e in nomenclatorul COD_BUGETAR); "
                             "atributul cod_bugetar e OBLIGATORIU (ANAF C(10)), nu se omite tacit." % cod)
        zi_s, luna_s, an_s = _scadenta_zile(an, luna)
        # scadenta manuala (override): nr_evid EMBEDA scadenta (poz.12-17), verificata de DUK regula R16
        # fata de atributul scadenta - deci nr_evid TREBUIE derivat din ACEEASI data, nu din cea calculata
        # (acelasi footgun ca la d710, generalizat pe clasa d100/d710 la 04.08.2026).
        scad_manual = o.get("scadenta")
        if scad_manual:
            parti = str(scad_manual).strip().split(".")
            if (len(parti) != 3 or not all(x.isdigit() for x in parti)
                    or len(parti[0]) != 2 or len(parti[1]) != 2 or len(parti[2]) != 4):
                raise ValueError("D100: scadenta manuala %r nu e in formatul ZZ.LL.AAAA." % scad_manual)
            zi_s, luna_s, an_s = int(parti[0]), int(parti[1]), int(parti[2])
        scad_str = "%02d.%02d.%04d" % (zi_s, luna_s, an_s)
        obl.append(Obligatie(
            cod_oblig=cod, suma_dat=suma, cod_bugetar=cod_bug, scadenta=scad_str,
            nr_evid=_nr_evid(cod, luna, an, zi_s, luna_s, an_s),
            cota=str(o.get("cota") or "")))
        total += suma
    # total_plata_a = SUMA DE CONTROL (DUK R11b): sum(suma_dat + suma_ded + suma_plata + suma_rest) pe
    # obligatii. La obligatia simpla suma_ded=suma_rest=0 si suma_plata=suma_dat -> 2 x sum(suma_dat).
    # Stocat pe rezultat (ca la d101/d300/d390/d710) si EMIS de build_xml din res - o singura sursa.
    return RezultatD100(an=an, luna=luna, prof=prof, obligatii=obl, total_plata_a=total * 2)


def _scadenta_zile(an, luna):
    """(zi, luna, an) scadentei standard: 25 a lunii urmatoare."""
    luna_urm = luna + 1
    an_urm = an
    if luna_urm > 12:
        luna_urm = 1
        an_urm += 1
    return 25, luna_urm, an_urm


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
    # d_anulare/d_succ/d_dizolv/d_bonif/d_nInf/d_energie = "0": fara ele bifate,
    # validatorul NU cere campurile suplimentare (temei, cifS etc.) - dovedit
    # din regulile "daca X!=0 atunci Y trebuie completat".
    hdr = ('<declaratie100 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
           'xmlns="%s" xsi:schemaLocation="%s D100.xsd" '
           'luna="%d" an="%d" d_anulare="0" d_succ="0" '
           'nume_declar=%s prenume_declar=%s functie_declar=%s '
           'cui=%s den=%s adresa=%s'
           % (NS, NS, res.luna, res.an,
              _esc(_t(prof.get("declarant_nume") or "ADMINISTRATOR", _LIM["d100"]["nume_declar"])),
              _esc(_t(prof.get("declarant_prenume") or "-", _LIM["d100"]["prenume_declar"])),
              _esc(_t(prof.get("declarant_functie") or "ADMINISTRATOR", _LIM["d100"]["functie_declar"])),
              _esc(prof.get("cui")), _esc(_t(prof.get("nume"), _LIM["d100"]["den"])), _esc(_t(prof.get("adresa"), _LIM["d100"]["adresa"]))))
    tel = (prof.get("telefon") or "").strip()
    if tel:
        hdr += ' telefon=%s' % _esc(_t(tel, _LIM["d100"]["telefon"]))
    # totalPlata_A = suma de control DUK R11b, calculata in calcul_d100 (res.total_plata_a =
    # 2 x sum(suma_dat) la obligatia simpla) si EMISA de aici - o singura sursa, ca la d101/d390/d710.
    hdr += ' totalPlata_A="%d">' % res.total_plata_a
    H.append(hdr)
    for o in res.obligatii:
        # cui/luna/tip_oblig: NU apartin sectiunii <obligatie> - dovedit de trei
        # ori pe validatorul oficial ("atribut necunoscut"), desi apar in constant
        # pool-ul clasei (sunt folosite intern, nu scrise in XML).
        linie = ('  <obligatie cod_oblig="%s" scadenta="%s" suma_dat="%d" '
                 'suma_plata="%d" nr_evid="%s"'
                 % (o.cod_oblig, o.scadenta, o.suma_dat, o.suma_dat, o.nr_evid))
        if o.cod_bugetar:
            linie += ' cod_bugetar=%s' % _esc(o.cod_bugetar)
        # cota: OBLIGATORIU si NUMAI pt. cod_oblig 121 (micro), valoare "1" (struct D100 poz.17a:
        # "daca cod_oblig=121 atunci cota=1 altfel cota=null"; ERR cota micro invalida). Gard bidirectional
        # - face imposibil un XML respins de validator (121 fara cota / cota pe alt cod).
        if str(o.cod_oblig) == "121":
            if str(o.cota) != "1":
                raise ValueError("D100: cod_oblig 121 (micro) CERE cota=1 (are %r) - validator ERR cota micro." % (o.cota,))
            linie += ' cota=%s' % _esc(o.cota)
        elif o.cota:
            raise ValueError("D100: cota se completeaza NUMAI pentru cod_oblig 121 (micro); cod_oblig %r are cota=%r." % (o.cod_oblig, o.cota))
        linie += "/>"
        H.append(linie)
    H.append("</declaratie100>")
    return "\n".join(H)


def pull(conn, schema, perioada):
    """Citeste profilul firmei si veniturile (cont 70x, note VALIDATE) din fereastra
    trimestrului. Fereastra [inceput, sfarsit) din perioada.interval() = identica cu
    intervalul vechi (trim*3, luna-2..luna+1)."""
    import psycopg2.extras as _E
    _inc, _sf = perioada.interval()
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, regim_fiscal, "
                    "declarant_nume, declarant_prenume, declarant_functie "
                    "FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        if prof.get("oras"):
            prof["adresa"] = " ".join(x for x in
                (prof.get("adresa"), prof.get("oras"), prof.get("judet")) if x)
        cur.execute(
            "SELECT COALESCE(SUM(l.suma),0) AS venituri FROM inregistrari_linii l "
            "JOIN inregistrari i ON i.id = l.inregistrare_id "
            "WHERE i.status='validata' AND l.cont_credit LIKE '70%%' "
            "AND i.data >= %s AND i.data < %s", (_inc.isoformat(), _sf.isoformat()))
        r = cur.fetchone() or {"venituri": 0}
    return prof, r["venituri"]


def genereaza(conn, schema, perioada, manual=None):
    """D100 trimestrial (contract uniform A1). `perioada.trim` (1-4) -> luna raportare = trim*3.
    `manual` accepta DOAR cheia 'cota' (procent impozit; micro implicit 1, profit implicit 16)."""
    if perioada.trim is None or not (1 <= perioada.trim <= 4):
        raise ValueError("D100 trimestrial: trim invalid: %r" % perioada.trim)
    cota = cheie_manual(manual, "cota").get("cota")
    an, luna = perioada.an, perioada.trim * 3
    prof, venituri = pull(conn, schema, perioada)
    # POARTA (27.07.2026): profil incomplet -> STOP cu mesaj clar, nu XML respins de ANAF.
    erori = erori_generare(prof)
    if erori:
        raise ValueError(" ".join(erori))

    obligatii = []
    regim = (prof.get("regim_fiscal") or "").lower()
    if regim == "micro":
        # rata default din registru (impozit_micro=1%), NU literal; contabilul o poate da explicit prin manual
        c = Decimal(str(cota)) if cota is not None else _rata_impozit_default("micro", an, luna)
        suma = _i(Decimal(str(venituri)) * c / Decimal(100))
        if suma > 0:
            obligatii.append({"cod_oblig": "121", "suma_dat": suma, "cota": "1"})
    elif regim == "profit":
        c = Decimal(str(cota)) if cota is not None else _rata_impozit_default("profit", an, luna)
        suma = _i(Decimal(str(venituri)) * c / Decimal(100))
        if suma > 0:
            obligatii.append({"cod_oblig": "103", "suma_dat": suma})

    res = calcul_d100(prof, an, luna, obligatii)
    xml = build_xml(res)
    return xml, res
