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
from core.identitate import valideaza_cui  # T1 (CATALOG_INVALIDITATE.md): sursa CANONICA checksum CUI, import READ-ONLY (LEAF, fara db)
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
    avertismente: list = field(default_factory=list)


def calcul_d100(prof, an, luna, obligatii):
    """`luna` trebuie sa fie 3, 6, 9 sau 12 (raportare trimestriala) - dovedit
    obligatoriu de validator. `obligatii` = [{cod_oblig, suma_dat, cod_bugetar?}]."""
    if luna not in (3, 6, 9, 12):
        raise ValueError("D100 trimestrial: luna trebuie să fie 3, 6, 9 sau 12 (primit %r)." % luna)
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
            raise ValueError("D100: cod_oblig %r fără cont bugetar (nu e în nomenclatorul COD_BUGETAR); "
                             "atributul cod_bugetar e OBLIGATORIU (ANAF C(10)), nu se omite tacit." % cod)
        zi_s, luna_s, an_s = _scadenta_cod(cod, an, luna)
        # scadenta manuala (override): nr_evid EMBEDA scadenta (poz.12-17), verificata de DUK regula R16
        # fata de atributul scadenta - deci nr_evid TREBUIE derivat din ACEEASI data, nu din cea calculata
        # (acelasi footgun ca la d710, generalizat pe clasa d100/d710 la 04.08.2026).
        scad_manual = o.get("scadenta")
        if scad_manual:
            parti = str(scad_manual).strip().split(".")
            if (len(parti) != 3 or not all(x.isdigit() for x in parti)
                    or len(parti[0]) != 2 or len(parti[1]) != 2 or len(parti[2]) != 4):
                raise ValueError("D100: scadență manuală %r nu e în formatul ZZ.LL.AAAA." % scad_manual)
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


def _scadenta_cod(cod, an, luna):
    """Scadenta pe cod_oblig + luna de raportare, cf. anaf_surse/d100_struct_anaf.txt
    (nomenclator scadente) SI validatorul oficial DUK regula R15.1:
      - cod 121 (micro), trim IV (luna=12): scadenta = 25.06 an+1. Validatorul v9 (raportare
        an 2026) RESPINGE 25.01.an+1 cu R15.1 ('scadenta ar fi trebuit sa fie 25.06.AAAA pt.
        cod obligatie=121') - dovedit pe date populate. Nota 'pana in anul 2025 inclusiv' din
        structura (linia 807-811) e superseda de comportamentul validatorului curent (acelasi
        tipar de comentariu invechit ca la d394 - de aici prioritatea validatorului).
      - cod 102/103/105 (impozit pe profit / plati anticipate), luna = luna de sfarsit de an
        fiscal (calendaristic = 12): scadenta = 25.LS = 25.12.an (structura linia 258-260;
        definitia '25LS' linia 3286).
      - restul (trim I/II/III): 25 a lunii urmatoare perioadei de raportare (default).
    """
    if cod == "121" and luna == 12:
        return 25, 6, an + 1
    if cod in ("102", "103", "105") and luna == 12:
        return 25, 12, an
    return _scadenta_zile(an, luna)


def erori_generare(prof):
    erori = []
    cui = (prof.get("cui") or "").strip()
    if not cui:
        erori.append("LIPSĂ CUI (obligatoriu).")
    else:
        # T1 (CATALOG_INVALIDITATE.md): checksum/format CUI validat PRE-DUK cu sursa canonica
        # core.identitate. Pana aici un CUI non-numeric / lungime gresita / cifra de control
        # gresita era emis TACIT si il prindea doar DUK (mesaj brut la depunere).
        valid, motiv = valideaza_cui(cui)
        if not valid:
            erori.append("D100: CUI firmă invalid (%s: %s). Corectează în Profil firmă." % (cui, motiv))
    if not (prof.get("nume") or "").strip():
        erori.append("LIPSĂ denumire firmă (obligatorie).")
    if not (prof.get("adresa") or "").strip():
        erori.append("LIPSĂ adresă domiciliu fiscal (obligatorie).")
    return erori


def build_xml(res):
    prof = res.prof
    if not (prof.get("declarant_nume") and prof.get("declarant_functie")):
        res.avertismente.append("D100: declarantul (nume/funcție) lipsește din profil -> emis implicit "
                                "\"ADMINISTRATOR\". Completează declarantul în Date firma.")
    # T6 (CATALOG_INVALIDITATE.md): text_anaf trunchiaza TACIT den/adresa la limita oficiala C(n)
    # (LIMITE_TEXT_ANAF). Pierderea de date era silentioasa; emitem un avertisment NON-blocant care
    # numeste campul cand valoarea reala depaseste limita si a fost taiata pentru XML.
    for _cheie, _et, _lim_c in (("nume", "denumirea firmei", _LIM["d100"]["den"]),
                                ("adresa", "adresa domiciliului fiscal", _LIM["d100"]["adresa"])):
        _real = " ".join(str(prof.get(_cheie) or "").split())
        if len(_real) > _lim_c:
            res.avertismente.append(
                "D100: %s depășește %d caractere și a fost trunchiată pentru XML - verifică." % (_et, _lim_c))
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
            raise ValueError("D100: cota se completează NUMAI pentru cod_oblig 121 (micro); cod_oblig %r are cota=%r." % (o.cod_oblig, o.cota))
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
            "SELECT COALESCE(SUM(CASE WHEN l.cont_credit LIKE '70%%' THEN l.suma ELSE 0 END),0) AS venituri, "
            "COALESCE(SUM(CASE WHEN l.cont_debit LIKE '6%%' THEN l.suma ELSE 0 END),0) AS cheltuieli "
            "FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
            "WHERE i.status='validata' AND i.data >= %s AND i.data < %s", (_inc.isoformat(), _sf.isoformat()))
        r = cur.fetchone() or {"venituri": 0, "cheltuieli": 0}
    return prof, r["venituri"], r["cheltuieli"]


def deriva_obligatii(prof, venituri, cheltuieli, an, luna, cota=None):
    """Derivarea obligatiilor D100 (micro 121 pe venituri; profit 103 pe PROFIT = venituri - cheltuieli),
    GATE-FREE: fara poarta erori_generare, fara refuz-pe-zero. SURSA UNICA a derivarii - o folosesc si
    genereaza (care aplica poarta + refuz-pe-zero + reconciliere peste), SI reconcilierea din
    control_incrucisat._thunk_d100 (a doua cale, expusa pe semafor). Un singur loc -> thunk-ul NU mai
    poate drifta de la generator nici in ARITATE (pull intoarce prof, venituri, cheltuieli), nici in
    FORMULA (baza profit = venituri - cheltuieli). Intoarce (obligatii, avert): avert = mesajul de
    avertisment profit (adaugat la res.avertismente de genereaza), sau "LOSS" (semnal pierdere in
    trimestru pentru refuzul-pe-zero), sau None."""
    obligatii = []
    avert = None
    regim = (prof.get("regim_fiscal") or "").lower()
    if regim == "micro":
        # rata default din registru (impozit_micro=1%), NU literal; contabilul o poate da explicit prin manual
        c = Decimal(str(cota)) if cota is not None else _rata_impozit_default("micro", an, luna)
        suma = _i(Decimal(str(venituri)) * c / Decimal(100))
        if suma > 0:
            obligatii.append({"cod_oblig": "121", "suma_dat": suma, "cota": "1"})
    elif regim == "profit":
        # [profit base fix 16.08] Impozitul pe PROFIT (103) se aplica pe PROFIT (venituri - cheltuieli),
        # NU pe venituri. Anterior venituri x 16% -> supra-declarare grosolana (SRL cu venituri 1M si
        # profit 100k primea 160k in loc de 16k). Baza = profit CONTABIL (venituri 70x - cheltuieli 6xx);
        # ajustarile fiscale (nedeductibile/neimpozabile art.19+ CF) si regularizarea anuala se fac la D101
        # (avertizat). Profit <= 0 (pierdere in trimestru) -> fara avans de impozit pe profit.
        c = Decimal(str(cota)) if cota is not None else _rata_impozit_default("profit", an, luna)
        _profit = Decimal(str(venituri)) - Decimal(str(cheltuieli))
        suma = _i(_profit * c / Decimal(100)) if _profit > 0 else 0
        if suma > 0:
            obligatii.append({"cod_oblig": "103", "suma_dat": suma})
            avert = ("D100 profit: baza = profit contabil (venituri %d - cheltuieli %d = %d) x %s%%. "
                     "Impozitul pe profit se aplică pe PROFIT, nu pe venituri. Ajustările fiscale "
                     "(nedeductibile/neimpozabile art.19+ CF) și regularizarea anuală se fac la D101." %
                     (_i(Decimal(str(venituri))), _i(Decimal(str(cheltuieli))), _i(_profit), c))
        elif Decimal(str(venituri)) > 0:
            avert = "LOSS"  # semnal pt mesajul de refuz (pierdere in trimestru)
    return obligatii, avert


def genereaza(conn, schema, perioada, manual=None):
    """D100 trimestrial (contract uniform A1). `perioada.trim` (1-4) -> luna raportare = trim*3.
    `manual` accepta DOAR cheia 'cota' (procent impozit; micro implicit 1, profit implicit 16)."""
    if perioada.trim is None or not (1 <= perioada.trim <= 4):
        raise ValueError("D100 trimestrial: trim invalid: %r" % perioada.trim)
    cota = cheie_manual(manual, "cota").get("cota")
    an, luna = perioada.an, perioada.trim * 3
    prof, venituri, cheltuieli = pull(conn, schema, perioada)
    # POARTA (27.07.2026): profil incomplet -> STOP cu mesaj clar, nu XML respins de ANAF.
    erori = erori_generare(prof)
    if erori:
        raise ValueError(" ".join(erori))

    # Derivarea obligatiilor traieste o SINGURA data in deriva_obligatii (aceeasi sursa ca thunk-ul de
    # reconciliere din control_incrucisat._thunk_d100) - genereaza aplica poarta + refuz-pe-zero +
    # reconciliere peste. Elimina copia de mana care driftase (aritate 2 vs 3 + baza profit pe venituri).
    obligatii, _avert_profit = deriva_obligatii(prof, venituri, cheltuieli, an, luna, cota)

    # [zero_base_refuz_v1 10.08.2026] D100 pe zero = XML STRUCTURAL INVALID la DUKIntegrator (sectiunea
    # <obligatie> e OBLIGATORIE, >=1 - verificat la sursa anaf_surse/d100_struct_anaf.txt + DUK: 'lipsa
    # sectiune obligatorie'). Nil-ul D100 NU e depozitabil -> REFUZAM (ca D390 'nu se depune pe zero'),
    # nu emitem XML invalid. Superseda avertismentul din tura 22 (care emitea XML invalid + doar avertiza);
    # DUK a dovedit ca golul D100 nu e un nil legal. D300 ramane pe avertisment - nil-ul D300 E valid.
    if not obligatii:
        _inc, _sf = perioada.interval()
        with conn.cursor() as _cur:
            _cur.execute("SELECT count(*) FROM facturi WHERE directie='emisa' "
                         "AND data_emitere >= %s AND data_emitere < %s", (_inc.isoformat(), _sf.isoformat()))
            _nf = _cur.fetchone()[0]
        _hint = (" Există %d facturi emise necontabilizate în perioada - contabilizează-le întâi." % _nf) if _nf else ""
        if _avert_profit == "LOSS":
            raise ValueError("D100 nu se depune pe zero: regim profit cu PIERDERE în trimestru (venituri %d - "
                             "cheltuieli %d <= 0) -> fără avans de impozit pe profit. Regularizarea se face la D101."
                             % (_i(Decimal(str(venituri))), _i(Decimal(str(cheltuieli)))))
        raise ValueError("D100 nu se depune pe zero: nicio obligație (venituri contabilizate cont 70x = 0)." + _hint)
    res = calcul_d100(prof, an, luna, obligatii)
    if _avert_profit and _avert_profit != "LOSS":
        res.avertismente.append(_avert_profit)
    # POARTA A DOUA CALE (gard continut, pas 4/4 lant reconciliere): recalcul INDEPENDENT al
    # obligatiei din SURSA (venituri cont 70x, note validate) x cota din registru, confruntat
    # cu suma_dat a generatorului. Prinde CATALOG #31 aggregation-loss (venit scapat din pull ->
    # suma_dat gresita, azi DUK-valid). NU alege singur cine are dreptate; NU repara tacit.
    from core.d100_reconciliere import verifica_reconciliere as _vr100
    _vr100(conn, perioada, res, manual)
    xml = build_xml(res)
    from core.reconciliere_emis import verifica_total_plata_a as _vte
    _vte("d100", xml, res.total_plata_a)   # poarta pe ARTEFACT: totalPlata_A parsat din emis == res
    return xml, res
