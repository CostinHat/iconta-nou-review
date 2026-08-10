"""
Modul D301 — Decont special de TVA (ANAF v1, OPANAF 592/2016, modificat prin OPANAF 779/2024,
MO 374/22.04.2024). Statut temei verificat la MO 04.08.2026: 592/2016 IN VIGOARE, neabrogat; 779/2024
a adaugat un checkbox de rectificare (declaratie rectificativa din notificare de conformare) - NU a atins
nomenclatoarele VALUTE/TIPURI_OP (confirmate separat pe validatorul instalat). Structura pdf din 2013 e INVECHITA;
nomenclatoarele (tip_valuta) sunt ancorate pe VALIDATORUL instalat D301_9 (proba DUK 04.08.2026), nu pe pdf.

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

from core.common import text_anaf as _t, LIMITE_TEXT_ANAF as _LIM  # limite text per-camp (03.08.2026)
import re
from core import common as c
from core.pdf_util import bani
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from core.identitate import valideaza_cui  # T1: validator partajat CUI (read-only) - checksum + lungime pre-DUK

NS = "mfp:anaf:dgti:d301:declaratie:v1"
REGULI = "2026.1"
_NEDIGIT = re.compile(r"\D")
TIPURI_OP = (1, 2, 3, 4, 5)
# Nomenclatorul tip_valuta ANCORAT PE VALIDATORUL INSTALAT (D301_9), nu pe pdf-ul de structura din 2013
# (d301_struct_anaf.txt, marcat INVECHIT). Setul acceptat de validator a fost enumerat prin proba DUK boundary
# 04.08.2026 (fiecare cod ISO trecut prin DUKIntegrator): validatorul accepta 20 de valute. VALUTE de mai jos
# are 20 - cele 19 din pdf-ul 2013 + HRK (kuna croata, adaugata de ANAF post-2013, validator-acceptata).
# HRK a fost adaugat 04.08.2026 cu greenlight Costin: codul respingea HRK desi validatorul o accepta (cod mai
# STRICT decat validatorul -> respingere falsa la achizitii istorice/rectificari din Croatia pre-2023). Acum
# VALUTE == setul validatorului (D301_9), confirmat prin proba DUK. Pazit de
# test_valute_ancorate_pe_validator_nu_pe_pdf_2013 (VALUTE == validator, fara cod mort, fara gap).
VALUTE = {"EUR", "USD", "AUD", "CAD", "CHF", "CZK", "DKK", "EGP", "GBP", "HUF",
          "JPY", "MDL", "NOK", "PLN", "RON", "SEK", "TRY", "XDR", "BGN", "HRK"}


def _esc(v):
    s = "" if v is None else str(v)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))


def _clean_bc(v):
    return ("" if v is None else str(v)).replace(",", " ").replace("#", " ").strip()


def _r0(x):
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def calc_baza(val_valuta, curs):
    """baza = round(val_valuta × curs, 0) — CF art.290 alin.(2): cursul e cel BNR/BCE ori
    al băncii de decontare, valabil la exigibilitate. Curs absent sau <= 0 NU se fabrică:
    un curs=1 pe valută ar subevalua TĂCUT baza declarată la ANAF. Pentru RON cursul e 1,
    dat explicit ca dată; pentru valută trebuie completat de contabil (§8)."""
    try:
        c = Decimal(str(curs)) if curs not in (None, "") else Decimal(0)
    except InvalidOperation:
        c = Decimal(0)
    if c <= 0:
        raise ValueError(
            "D301: curs de schimb absent sau invalid (%r). CF art.290 alin.(2) cere cursul "
            "BNR/BCE valabil la exigibilitate — pentru RON e 1, pentru valută trebuie completat."
            % (curs,))
    return _r0(Decimal(str(val_valuta)) * c)


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
    ops_raw: list = field(default_factory=list)   # T2/T3: valorile BRUTE, pre-coercitie (validate pre-DUK)


def _data_doc_ro(v):
    """data_doc in formatul OFICIAL ANAF ZZ.LL.AAAA, C(10) (anaf_surse/d301_struct_anaf.txt poz.35).
    Normalizeaza din ORICE sursa: date/datetime, ISO 'AAAA-LL-ZZ', sau deja ZZ.LL.AAAA. Generatorul
    emite formatul cerut de ANAF indiferent de ce e stocat (defense-in-depth; ruta valideaza inputul,
    DAR datele pot ajunge pe alte cai - ex. import/backfill). DUK respinge orice != ZZ.LL.AAAA."""
    if v is None:
        return ""
    if hasattr(v, "strftime"):
        # format XML ANAF ZZ.LL.AAAA (spec poz.35); NU data_ro (e formator UI - vezi docstring-ul lui:
        # "NU pentru XML/SAF-T") si NU strftime("%d..") (BACKEND_UI_BRUT: data zi-intai = pt OCHI).
        # data_doc e CONTINUT DE FIR (XML), format dictat de ANAF, nu ales de UI -> il construim explicit.
        return "%02d.%02d.%04d" % (v.day, v.month, v.year)
    t = str(v).strip()
    if not t:
        return ""
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", t)   # ISO AAAA-LL-ZZ -> ZZ.LL.AAAA
    if m:
        return "%s.%s.%s" % (m.group(3), m.group(2), m.group(1))
    return t   # deja ZZ.LL.AAAA (sau alt format - ruta valideaza inputul real la scriere)


def calcul_d301(prof, perioada, operatiuni_raw):
    """PUR. operatiuni_raw: listă de dict {tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, tva}."""
    an, luna = perioada.an, perioada.luna
    ops = []
    tot = {t: [0, 0] for t in TIPURI_OP}
    mij = 0
    for r in operatiuni_raw:
        tip = int(r.get("tip") or 1)
        baza = calc_baza(r.get("val_valuta") or 0, r.get("curs"))
        tva = _r0(r.get("tva") or 0)
        op = Operatiune(tip=tip, nr_doc=r.get("nr_doc") or "", data_doc=_data_doc_ro(r.get("data_doc")),
                        val_valuta=float(r.get("val_valuta") or 0),
                        tip_valuta=(r.get("tip_valuta") or "EUR").upper(),
                        curs=float(r.get("curs")), baza=baza, tva=tva)
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
                   total_plata_a=total_plata, mij_transp=mij,
                   ops_raw=list(operatiuni_raw))
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
    _cif = _NEDIGIT.sub("", prof.get("cui") or "")
    if not _cif:
        erori.append("LIPSĂ CIF persoană impozabilă.")
    else:
        # T1: cifra de control + lungime (validator partajat core.identitate, read-only), nu doar
        # prezenta. Un CIF cu checksum gresit / supra-lung era emis TACIT (doar DUK il prindea, criptic).
        # C(13) e latimea campului ANAF; validatorul respinge deja >10 cifre ("lungime").
        _ok_cif, _motiv_cif = valideaza_cui(prof.get("cui"))
        if not _ok_cif:
            erori.append("CIF persoana impozabila invalid (%s): %s." % (_cif, _motiv_cif))
        elif len(_cif) > 13:
            erori.append("CIF %s depaseste C(13) (structura ANAF d301)." % _cif)
    if not str(prof.get("nume") or "").strip():
        erori.append("LIPSĂ denumire.")
    if not _clean_bc(prof.get("banca")):
        erori.append("LIPSĂ bancă (obligatorie la D301).")
    if not _clean_bc(prof.get("iban") or prof.get("cont")):
        erori.append("LIPSĂ cont (obligatoriu la D301).")
    return erori

def _blocante_pre_duk(res):
    """Motive care INVALIDEAZA D301, semnalate PRE-DUK ca ValueError cu motiv EXACT (nu eroarea
    bruta a validatorului: "atribut prezent dar vid nepermis" / "nu se afla in lista"). Verifica
    valorile BRUTE (res.ops_raw), INAINTE de coercitia din calcul_d301 (tip->1, valuta->EUR):
    o valoare coercita din gunoi trebuie sa iasa la suprafata, nu sa devina tacit un default (T3).
    Acopera: nr_doc gol (T2), data_doc gol (T2), tip out-of-nomenclator (T2/T3), valuta gol sau
    out-of-nomenclator (T2/T3), nr_doc > C(20) passthrough netrunchiat (T6, leak pur pe care DUK
    nu il impune). Campurile de profil (CIF checksum inclus, T1) raman in erori_generare (sursa unica)."""
    b = []
    for i, r in enumerate(res.ops_raw, 1):
        nr_raw = r.get("nr_doc")
        nr = str(nr_raw).strip() if nr_raw is not None else ""
        eticheta = nr if nr else "#%d" % i
        # tip: out-of-nomenclator / gol / negenerabil -> NU se reclasifica tacit in sectiunea 1 (T2/T3)
        tip_raw = r.get("tip")
        try:
            tip = int(tip_raw)
        except (TypeError, ValueError):
            tip = None
        if tip not in TIPURI_OP:
            b.append("Operatiunea %s: tip operatiune %r in afara nomenclatorului (permise 1..5); "
                     "nu se reclasifica tacit in sectiunea 1." % (eticheta, tip_raw))
        # valuta: gol -> NU devine tacit EUR; altfel trebuie in nomenclatorul ancorat pe validator (T2/T3)
        val_raw = r.get("tip_valuta")
        val = str(val_raw).strip().upper() if val_raw is not None else ""
        if not val:
            b.append("Operatiunea %s: valuta lipsa; nu se completeaza tacit EUR." % eticheta)
        elif val not in VALUTE:
            b.append("Operatiunea %s: valuta %r neacceptata (nomenclator ANAF)." % (eticheta, val))
        # nr_doc: gol (T2) sau supra-lung C(20) netrunchiat (T6, leak pur)
        if not nr:
            b.append("Operatiunea #%d: fara numar document (nr_doc gol)." % i)
        elif len(nr) > 20:
            b.append("Operatiunea %s: numar document de %d caractere depaseste C(20) (structura ANAF); "
                     "nu se emite netrunchiat." % (eticheta, len(nr)))
        # data_doc: gol (T2)
        dd_raw = r.get("data_doc")
        dd = str(dd_raw).strip() if dd_raw is not None else ""
        if not dd:
            b.append("Operatiunea %s: fara data document (data_doc gol)." % eticheta)
    return b


def valideaza(res):
    """Revitalizat (T2): era COD MORT - genereaza chema doar erori_generare(prof), deci verificarile
    prietenoase pe operatiuni (nr_doc/data_doc gol, tip/valuta out-of-nomenclator) NU ajungeau la
    contabil; primea eroarea bruta a validatorului la upload. Acum genereaza() ruteaza
    _blocante_pre_duk -> ValueError cu motiv EXACT pre-DUK. Returneaza lista COMPLETA (blocante pe
    operatiuni + campuri de profil); sursa unica pentru profil = erori_generare (T1 inclus)."""
    return _blocante_pre_duk(res) + erori_generare(res.prof)


def _pers_inreg(prof):
    """pers_inreg - atribut OBLIGATORIU N(1), valori admise (1,2)
    (anaf_surse/d301_struct_anaf.txt poz.15 "pers_inreg:=(1,2)"):
      1 = persoana care NU este inregistrata in scopuri de TVA;
      2 = persoana inregistrata conform art. 317 CF (fost art. 153^1) NUMAI pentru
          achizitii intracomunitare.
    Distinctia (1 vs 2) depinde EXCLUSIV de STATUTUL de inregistrare art. 317, NU de faptul
    ca firma face operatiuni intracomunitare. Doctrina interna e explicita (control_fiscal_api.py:
    "art. 317 gri (nu stim daca e inregistrat)"; termene_api.py: "inregistrarea art. 317, pe
    care n-o urmarim - facturile IC nu o dovedesc"): operatiuni_ic e un FLAG DE FAPT, nu o
    proba de inregistrare, deci NU poate decide pers_inreg - o firma cu IC dar neinregistrata
    ramane pers_inreg=1 (are chiar obligatia de a se inregistra). Sursa autoritara ar fi un marcaj
    explicit de inregistrare art. 317 pe profil (propus: firma_profil.inreg_art317 boolean - vezi
    raportul de neconformitate). Cat timp coloana lipseste, cazul STANDARD al depunatorului de D301
    e neinregistrat -> "1". Default EXPLICIT si documentat (nu hardcode tacit): in momentul in care
    profilul poarta marcajul (prof["inreg_art317"]=True), aceasta functie emite "2" fara alte modificari.
    """
    if prof.get("inreg_art317"):
        return "2"
    return "1"


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
             'cif="%s" denumire="%s" adresa="%s" banca="%s" cont="%s" pers_inreg="%s" '
             'nr_evid="%s" baza1="%d" tva1="%d" baza2="%d" tva2="%d" baza3="%d" tva3="%d" '
             'baza4="%d" tva4="%d" baza5="%d" tva5="%d" totalPlata_A="%d" '
             'nume_declarant="%s" prenume_declarant="%s" functia_declarant="%s">'
             % (NS, res.luna, res.an, res.mij_transp, _esc(cif), _esc(_t(den, _LIM["d301"]["denumire"])), _esc(_t(adr, _LIM["d301"]["adresa"])),
                _esc(_t(_clean_bc(prof.get("banca")), _LIM["d301"]["banca"])), _esc(_t(_clean_bc(prof.get("iban") or prof.get("cont")), _LIM["d301"]["cont"])),
                _pers_inreg(prof),
                nr_evidenta(res.an, res.luna, res.mij_transp),
                t[1][0], t[1][1], t[2][0], t[2][1], t[3][0], t[3][1],
                t[4][0], t[4][1], t[5][0], t[5][1], res.total_plata_a,
                _esc(_t(prof.get("declarant_nume") or "ADMINISTRATOR", _LIM["d301"]["nume_declarant"])),
                _esc(_t(prof.get("declarant_prenume") or "-", _LIM["d301"]["prenume_declarant"])),
                _esc(_t(prof.get("declarant_functie") or "ADMINISTRATOR", _LIM["d301"]["functia_declarant"]))))
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
def pull(conn, schema, perioada):
    import psycopg2.extras as _E
    an, luna = perioada.an, perioada.luna
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, banca, iban, "
                    "declarant_nume, declarant_prenume, declarant_functie "
                    "FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        cur.execute("SELECT tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, tva "
                    "FROM d301_operatiuni WHERE an=%s AND luna=%s ORDER BY id", (an, luna))
        ops = [dict(r) for r in cur.fetchall()]
    return prof, ops


def genereaza(conn, schema, perioada, manual=None):
    if manual:
        raise ValueError("D301 nu acceptă 'manual' (chei: %s)" % sorted(manual))
    if perioada.luna is None or not (1 <= perioada.luna <= 12):
        raise ValueError("D301 lunar: luna invalidă: %r" % perioada.luna)
    if perioada.an is None or int(perioada.an) < 2013:
        raise ValueError("D301: an invalid %r - formularul 301 se depune din 2013 (OPANAF 592/2016 si anterioare)." % perioada.an)
    prof, ops = pull(conn, schema, perioada)
    # POARTA (27.07.2026): profil incomplet -> STOP cu mesaj clar, nu XML respins de ANAF.
    erori = erori_generare(prof)
    if erori:
        raise ValueError("D301 nu se poate genera: " + " ".join(erori))
    res = calcul_d301(prof, perioada, ops)
    # [T2 10.08.2026] valideaza(res) era COD MORT: genereaza chema doar erori_generare(prof), deci
    # verificarile prietenoase pe operatiuni (nr_doc/data_doc gol, tip/valuta out-of-nomenclator, T6
    # nr_doc>C(20)) nu ajungeau la contabil - primea eroarea bruta a validatorului la upload. Le cablam
    # aici pe valorile BRUTE (pre-coercitie), rutate ca ValueError cu motiv EXACT pre-DUK.
    _blocante = _blocante_pre_duk(res)
    if _blocante:
        raise ValueError("D301 nu se poate genera: " + " ".join(_blocante))
    return build_xml(res), res
