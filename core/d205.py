# -*- coding: utf-8 -*-
"""core/d205.py — D205 (Declaratie informativa privind impozitul retinut la sursa
si castigurile/pierderile realizate, pe beneficiari de venit).

REFACUT DE LA ZERO 16.07.2026, din ANAF structura D205 (OPANAF 102/2025)
(structura_D205_2025_120226.pdf, modif. 12.02.2026), citita INTEGRAL (461 linii,
dupa o prima incercare care citise doar primele ~180 si a ratat atributele reale
ale sect_II/benef - gasite mai departe in document).

Structura reala:
  <declaratie205 luna="12" an="AAAA" d_rec="0" cui="..." nume_declar="..."
                 prenume_declar="..." functie_declar="..." den="..." adresa="..."
                 totalPlata_A="...">
    <sect_II tip_venit="25" nrben="N" Tcastig="..." Tpierd="..." T_VB="..."
             T_GAR="..." Tbaza="..." Timp="...">   (1 per tip_venit, 1-n aparitii)
      <benef categ="1.a" nume1="..." rezid="1" cif="..." tip_plata="2"
             castig1/divid_D1="..." pierdere1/divid_P1="..." baza1="..."
             imp1="..."/>   (1-n aparitii)
    </sect_II>
  </declaratie205>

Reguli de calcul (din ANAF structura D205 (OPANAF 102/2025)):
  Tcastig = SUMA(castig1) pt. beneficiarii cu tip_venit1=25
  Tpierd  = SUMA(pierdere1) pt. beneficiarii cu tip_venit1=25
  Tbaza   = SUMA(baza1) pt. toti beneficiarii sectiunii
  Timp    = SUMA(imp1) pt. toti beneficiarii sectiunii
  nrben   = COUNT(beneficiari) din sectiune

tip_venit pt. DIVIDENDE = 08 (nomenclator ANAF "08 1.a) venituri din dividende"); codul emite
08. "25" (castiguri din aurul de investitie) intr-o versiune veche a acestui comentariu era
GRESIT (comentariu-credinta, infirmat la audit tura 25). Tcastig/Tpierd se aduna doar pt.
beneficiarii cu tip_venit1=25 (castiguri), deci = 0 pt. o declaratie de dividende.

DIVIDENDE distribuite vs. platite (col. 7.V divid_D / 8.V divid_P din structura ANAF, rand
39.a/39.b): contul 457 "Dividende de plata" e bifunctional. CREDIT 457 = dividend DISTRIBUIT
(se creeaza datoria: 117/121 = 457) -> divid_D. DEBIT 457 = dividend PLATIT (se stinge datoria:
457 = 5121/446) -> divid_P. baza1/imp1 se calculeaza pe dividendul PLATIT (impozitul pe
dividende se retine la PLATA; aliniat cu calea 2 de reconciliere care recalculeaza din Σ debit
457). Regula fully-paid (documentata): divid_D >= divid_P mereu (nu poti plati cumulat mai mult
decat s-a distribuit); daca fereastra anului nu contine creditul de distribuire (dividend
distribuit intr-un an anterior, platit in anul curent), Σ credit 457 in fereastra = 0 < platit
=> divid_D = platit (dividend integral platit).

Rezid (col. 2 Rezident/Nerezident, rand 32) se DERIVA din identitate: CNP romanesc valid ->
Rezid=1 (rezident); NIF strain / pasaport / cod invalid -> Rezid=2 (nerezident). Pentru
DIVIDENDE (tip_venit1=08) validatorul oficial admite DOAR Rezid=1 (DUK regula R32: Rezid=2 e
permis doar pentru tip_venit1 in (04,16,18,25,26,27,28,29,30)); dividendele catre nerezidenti
se declara pe D207, nu pe D205. Un beneficiar nerezident de dividende e REFUZAT la generare.
statR/cifS raman goale pentru rezidenti (cifS=null la Rezid=1); pentru un nerezident structura
cere Stat_R (DUK regula R33), camp inexistent in tabelul `asociati` (vezi build_xml).
"""
from __future__ import annotations

from core.common import text_anaf as _t, cheie_manual, LIMITE_TEXT_ANAF as _LIM  # limite text per-camp (03.08.2026)
from core.identitate import valideaza_cui, valideaza_cnp  # T1: checksum CUI/CNP pre-DUK, read-only (LEAF, fara import circular)
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

NS = "mfp:anaf:dgti:d205:declaratie:v3"


def _esc(v):
    from xml.sax.saxutils import quoteattr
    return quoteattr(str(v if v is not None else ""))


def _i(x):
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _cnp_rezident(cif):
    """CNP romanesc de PERSOANA REZIDENTA (structural): exact 13 cifre, cu prima cifra (S = sex/
    secol) in 1..8. 1-6 = cetateni romani; 7,8 = persoane straine cu RESEDINTA in Romania (deci
    rezidenti fiscal). Prima cifra 9 = persoana fizica straina (nerezident); pasaport / NIF de
    nerezident = non-numeric sau lungime <> 13 -> NU e CNP de rezident.

    NU se verifica cifra de control aici INTENTIONAT: validarea cifR (checksum CNP/NIF) e treaba
    validatorului ANAF (structura: 'Verificare cifR ... ERR campul 4.CNP/NIF invalid'); pentru
    DERIVAREA rezidentei e nevoie doar de distinctia CNP-de-rezident vs. cod-de-nerezident, iar un
    checksum strict ar respinge inutil CNP-uri de test cu control fictiv (care oricum sunt prinse
    de DUK)."""
    d = "".join(ch for ch in str(cif or "") if ch.isdigit())
    return len(d) == 13 and d[0] in "12345678"


def _rezid(cif):
    """Rezidenta beneficiarului DERIVATA din identitate (nu hardcodata): CNP romanesc de rezident
    -> '1' (rezident); orice altceva (CNP cu prima cifra 9, NIF strain, pasaport, cod cu lungime
    gresita) -> '2' (nerezident)."""
    return "1" if _cnp_rezident(cif) else "2"


@dataclass
class Beneficiar:
    categ: str
    nume1: str
    cif: str
    baza1: int = 0
    imp1: int = 0
    castig1: int = 0
    pierdere1: int = 0
    divid_d: int = 0   # 7.V divid_D dividend DISTRIBUIT (Σ credit 457)
    divid_p: int = 0   # 8.V divid_P dividend PLATIT (Σ debit 457)
    tip_plata: str = "2"
    rezid: str = "1"


@dataclass
class RezultatD205:
    an: int
    prof: dict = field(default_factory=dict)
    beneficiari: list = field(default_factory=list)
    total_plata_a: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d205(prof, an, beneficiari):
    """`beneficiari` = [{categ, nume, cif, baza?, imp?, castig?, pierdere?, divid_d?, divid_p?}].

    divid_d/divid_p = dividend distribuit/platit (tip_venit1=08). COMPAT: daca apelantul da doar
    castig/pierdere (forma dict veche, unde 'castig' purta suma bruta a dividendului), divid_d
    cade pe castig si divid_p pe pierdere - astfel golden vechi (divid_D=castig) ramane valid."""
    benef = []
    total_imp = 0
    for b in beneficiari or []:
        baza = _i(b.get("baza", 0))
        imp = _i(b.get("imp", 0))
        castig = _i(b.get("castig", 0))
        pierdere = _i(b.get("pierdere", 0))
        divid_d = _i(b.get("divid_d", b.get("castig", 0)))
        divid_p = _i(b.get("divid_p", b.get("pierdere", 0)))
        if (baza <= 0 and imp <= 0 and castig <= 0 and pierdere <= 0
                and divid_d <= 0 and divid_p <= 0):
            continue
        benef.append(Beneficiar(
            categ=str(b["categ"]), nume1=str(b.get("nume", "")).strip(),
            cif=str(b.get("cif", "")).strip(), baza1=baza, imp1=imp,
            castig1=castig, pierdere1=pierdere, divid_d=divid_d, divid_p=divid_p,
            tip_plata=str(b.get("tip_plata", "2"))))
        total_imp += imp
    # totalPlata_A = checksum ANAF (OPANAF 102/2025): nrben+Tcastig+Tpierd+T_VB+T_GAR+Tbaza+Timp.
    # La dividende (tip_venit 08) Tcastig/Tpierd/T_VB/T_GAR=0 (niciun tip_venit1=25), deci
    # checksum = nrben+Tbaza+Timp. SURSA UNICA (aliniat la d100 R11b): calcul_d205 il calculeaza,
    # build_xml il EMITE din res.total_plata_a - res.total_plata_a == totalPlata_A emis, mereu.
    _nrben = len(benef)
    _Tbaza = sum(b.baza1 for b in benef)
    _Timp = sum(b.imp1 for b in benef)
    _checksum = _nrben + _Tbaza + _Timp
    return RezultatD205(an=an, prof=prof, beneficiari=benef, total_plata_a=_checksum)


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
    if not (prof.get("declarant_nume") and prof.get("declarant_functie")):
        res.avertismente.append("D205: declarantul (nume/functie) lipseste din profil -> emis implicit "
                                "\"ADMINISTRATOR\". Completeaza declarantul in Date firma.")
    if not res.beneficiari:
        raise ValueError("D205 fara niciun beneficiar de venit - nu se genereaza "
                         "declaratie fara continut.")

    # c2 (T1 - CATALOG_INVALIDITATE.md): CUI platitor pre-validat pe CIFRA DE CONTROL, nu doar
    # non-gol (erori_generare verifica doar non-gol). Un CUI cu control gresit / lungime gresita
    # era emis TACIT si respins abia de DUK (atribut "cui: CUI invalid"; structura ANAF rand 9
    # "Verificare cui" -> "ERR - CIF platitor de venit invalid"). valideaza_cui = validatorul
    # canonic OFFLINE (core.identitate), refolosit read-only.
    _ok_cui, _motiv_cui = valideaza_cui(prof.get("cui"))
    if not _ok_cui:
        raise ValueError(
            "D205: CUI platitor %s invalid (%s) - se corecteaza, nu se emite declaratie respinsa "
            "de ANAF (validarea DUK de atribut 'cui: CUI invalid'; structura ANAF rand 9 "
            "'Verificare cui')." % (
                "".join(ch for ch in str(prof.get("cui") or "") if ch.isdigit()) or "-", _motiv_cui))

    # Campuri OBLIGATORII pe beneficiar in structura ANAF (anaf_surse/d205_struct_anaf.txt):
    # cifR "4.CNP/NIF din Romania" N(13) DA (rand 34, "ERR - ... necompletat"; DUK: "cifR:
    # atribut prezent dar vid nepermis") si den1 "1.Nume ... / Denumire" C(100) DA (rand 31).
    # Un asociat cu cota>0 si dividende dar fara CNP (asociati.cnp NULL) ar emite cifR="" ->
    # declaratie respinsa de ANAF. Refuzam la generare, nu producem un XML invalid.
    for b in res.beneficiari:
        if not any(ch.isdigit() for ch in (b.cif or "")):
            raise ValueError(
                "D205: beneficiarul %r are CNP/NIF (cifR) necompletat - camp "
                "obligatoriu N(13) in structura ANAF; declaratia ar fi respinsa "
                "de validator." % (b.nume1 or "necunoscut"))
        if not (b.nume1 or "").strip():
            raise ValueError(
                "D205: beneficiarul cu CNP %s are numele (den1) necompletat - "
                "camp obligatoriu in structura ANAF."
                % "".join(ch for ch in b.cif if ch.isdigit()))
        # Rezid (rand 32) DERIVAT din identitate, NU hardcodat "1". Pentru dividende
        # (tip_venit1=08) validatorul admite DOAR Rezid=1 (DUK regula R32: Rezid=2 e permis
        # doar pentru tip_venit1 in (04,16,18,25,26,27,28,29,30)). Un beneficiar de dividende
        # fara CNP romanesc valid = nerezident -> se declara pe D207, NU pe D205. In plus,
        # DUK regula R33 cere Stat_R pentru Rezid=2 (camp inexistent in tabelul `asociati`).
        b.rezid = _rezid(b.cif)
        if b.rezid != "1":
            raise ValueError(
                "D205: beneficiarul %r (CNP/NIF %s) nu are CNP romanesc valid = NEREZIDENT "
                "(Rezid=2). Dividendele (tip_venit1=08) catre nerezidenti NU se declara pe D205 "
                "(DUK regula R32 admite Rezid=2 doar pt. tip_venit1 in 04,16,18,25-30); se "
                "declara pe D207. In plus DUK regula R33 cere Stat_R (statul de rezidenta), camp "
                "inexistent in tabelul `asociati`." % (
                    b.nume1 or "necunoscut",
                    "".join(ch for ch in (b.cif or "") if ch.isdigit()) or "-"))

        # c1 (T1): beneficiar REZIDENT (CNP-shaped, rezid==1) - checksum CNP pre-validat. _rezid()
        # stabileste DOAR forma (13 cifre, prima 1-8); un CNP cu cifra de control gresita trecea
        # TACIT si era respins abia de DUK (R29: "cif1(...) este invalid"). valideaza_cnp =
        # validatorul canonic (core.identitate), refolosit read-only. NU inlocuieste refuzul de
        # nerezident de mai sus (prefix-9 / cod strain) - il COMPLETEAZA cu checksum-ul rezidentilor.
        _ok_cnp, _motiv_cnp = valideaza_cnp("".join(ch for ch in (b.cif or "") if ch.isdigit()))
        if not _ok_cnp:
            raise ValueError(
                "D205: beneficiarul %s are CNP invalid (%s: %s) - se corecteaza, nu se emite "
                "declaratie respinsa de ANAF (DUK regula R29)." % (
                    b.nume1 or "necunoscut",
                    "".join(ch for ch in (b.cif or "") if ch.isdigit()), _motiv_cnp))

    # c3 (T1): (tip_venit1+cifR) trebuie UNIC (structura ANAF "Validari suplimentare" pct.2
    # "unicitate (tip_venit1+cifR) pt. tip_venit1#25"; DUK regula R41b: "combinatia 08_<cnp> nu
    # este unica"). Doi asociati cu acelasi CNP (toti tip_venit1=08) colapsau pe cheia cif in
    # reconciliere (dict pe cif) si scapau nedetectati -> respinsi abia de DUK. Hard-block care
    # numeste CNP-ul, inainte de emitere.
    _cifr_vazute = set()
    for _b in res.beneficiari:
        _cheie_cifr = "".join(ch for ch in (_b.cif or "") if ch.isdigit())
        if _cheie_cifr in _cifr_vazute:
            raise ValueError(
                "D205: beneficiarul cu CNP %s apare de 2 ori - (tip_venit1+CNP) trebuie unic "
                "(DUK regula R41b). Comaseaza sau corecteaza." % _cheie_cifr)
        _cifr_vazute.add(_cheie_cifr)

    # Tcastig/Tpierd, conform formulei oficiale, se calculeaza DOAR din
    # beneficiarii cu tip_venit1=25 ("Tcastig = suma(castig1) pt. tip_venit1=25").
    # La tip_venit=08 (dividende), NICIUN beneficiar nu are tip_venit1=25, deci
    # Tcastig/Tpierd raman 0.
    nrben = len(res.beneficiari)
    Tcastig = 0
    Tpierd = 0
    T_VB = 0
    T_GAR = 0
    Tbaza = sum(b.baza1 for b in res.beneficiari)
    Timp = sum(b.imp1 for b in res.beneficiari)
    # totalPlata_A = suma(nrben)+suma(Tcastig)+suma(Tpierd)+suma(T_VB)+
    # suma(T_GAR)+suma(Tbaza)+suma(Timp) - formula EXACTA din ANAF structura D205 (OPANAF 102/2025)
    # (nu doar Timp, cum pusesem prima data - DUK regula R15 respinsese exact asta:
    # cerea 11001, primea 1000).
    # SURSA UNICA: checksum-ul e calculat in calcul_d205 si tinut in res.total_plata_a;
    # aici il EMITEM din res (nu-l recalculam independent - capcana latenta d100). Gardul
    # golden test_total_plata_a_res_egal_checksum_emis leaga res == header == nrben+Tbaza+Timp.
    total_control = res.total_plata_a

    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    hdr = ('<declaratie205 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
           'xmlns="%s" xsi:schemaLocation="%s D205.xsd" '
           'luna="12" an="%d" d_rec="0" '
           'nume_declar=%s prenume_declar=%s functie_declar=%s '
           'cui="%s" den=%s adresa=%s totalPlata_A="%d">'
           % (NS, NS, res.an,
              _esc(_t(prof.get("declarant_nume") or "ADMINISTRATOR", _LIM["d205"]["nume_declar"])),
              _esc(_t(prof.get("declarant_prenume") or "-", _LIM["d205"]["prenume_declar"])),
              _esc(_t(prof.get("declarant_functie") or "ADMINISTRATOR", _LIM["d205"]["functie_declar"])),  # C(50) ANAF (DUK: 51 respins)
              "".join(ch for ch in str(prof.get("cui") or "") if ch.isdigit()),
              _esc(_t(prof.get("nume"), _LIM["d205"]["den"])), _esc(_t(prof.get("adresa"), _LIM["d205"]["adresa"])), total_control))  # den C(200)/adresa C(1000) ANAF (DUK 201/1001 respinse)
    H.append(hdr)
    # sect_II se INCHIDE (linia 26 din ANAF structura D205 (OPANAF 102/2025)) INAINTE de <benef>
    # (linia 27) - sunt elemente FRATI, ambele copii ai radacinii, nu benef in
    # interiorul lui sect_II. Gresit prima data: pusesem benef in interiorul lui
    # sect_II. "sectiunea benef este gresit pozitionata" - eroarea validatorului
    # spunea exact asta.
    # tip_venit "08" = dividende (categ 1.a), NU "25" (alta categorie, unde
    # baza1/imp1 sunt interzise - R44/R45 respinsesera exact asta). Confirmat
    # din ANAF structura D205 (OPANAF 102/2025): "08 1.a) venituri din dividende".
    H.append('  <sect_II tip_venit="08" nrben="%d" Tcastig="%d" Tpierd="%d" '
             'T_VB="%d" T_GAR="%d" Tbaza="%d" Timp="%d"/>'
             % (nrben, Tcastig, Tpierd, T_VB, T_GAR, Tbaza, Timp))
    # den1 (nu nume1), cifR (nu cif), Rezid cu majuscula, tip_venit1 pe FIECARE
    # beneficiar, id_inreg secvential. "categ" NU e atribut valid - respins ca
    # necunoscut de validator; categoria (1.a) e implicita in tip_venit1=08.
    # La tip_venit1=08 se completeaza divid_D (dividend DISTRIBUIT, Σ credit 457) si
    # divid_P (dividend PLATIT, Σ debit 457) pe langa baza1/imp1 - confirmat din structura
    # ANAF (rand 39.a/39.b) si din formatul oficial de import: "categ(1.a),...,2,divid_D,
    # divid_P,baza,imp". Rezid emis din b.rezid (derivat), nu hardcodat.
    for idx, b in enumerate(res.beneficiari, start=1):
        H.append('  <benef id_inreg="%d" den1=%s tip_venit1="08" '
                 'Rezid="%s" cifR="%s" tip_plata="%s" '
                 'divid_D="%d" divid_P="%d" baza1="%d" imp1="%d"/>'
                 % (idx, _esc(_t(b.nume1, _LIM["d205"]["den1"])),  # den1 C(100) ANAF (DUK: 101 respins)
                    b.rezid,
                    "".join(ch for ch in b.cif if ch.isdigit()),
                    b.tip_plata, b.divid_d, b.divid_p, b.baza1, b.imp1))
    H.append("</declaratie205>")
    return "\n".join(H)


def pull(conn, schema, perioada):
    """Profil + asociatii cu cota>0 + dividende din contul 457 (note VALIDATE) in fereastra
    anului [inceput, sfarsit) din perioada.interval():
      total_distribuit = Σ CREDIT 457 (se creeaza datoria: 117/121 = 457) -> divid_D
      total_platit     = Σ DEBIT  457 (se stinge datoria: 457 = 5121/446) -> divid_P
    Intoarce (prof, asoc, total_distribuit, total_platit)."""
    import psycopg2.extras as _E
    _inc, _sf = perioada.interval()
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, "
                    "declarant_nume, declarant_prenume, declarant_functie "
                    "FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        if prof.get("oras"):
            prof["adresa"] = " ".join(x for x in
                (prof.get("adresa"), prof.get("oras"), prof.get("judet")) if x)
        cur.execute("SELECT nume, cnp, cota FROM asociati WHERE cota > 0")
        asoc = cur.fetchall()
        cur.execute(
            "SELECT "
            "COALESCE(SUM(CASE WHEN l.cont_credit LIKE '457%%' THEN l.suma ELSE 0 END),0) AS distribuit, "
            "COALESCE(SUM(CASE WHEN l.cont_debit  LIKE '457%%' THEN l.suma ELSE 0 END),0) AS platit "
            "FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
            "WHERE i.status='validata' "
            "AND (l.cont_credit LIKE '457%%' OR l.cont_debit LIKE '457%%') "
            "AND i.data >= %s AND i.data < %s", (_inc.isoformat(), _sf.isoformat()))
        row = cur.fetchone() or {"distribuit": 0, "platit": 0}
        total_distribuit = _i(row["distribuit"] or 0)
        total_platit = _i(row["platit"] or 0)
    return prof, asoc, total_distribuit, total_platit


def genereaza(conn, schema, perioada, manual=None):
    """D205 anual (contract uniform A1). `manual` cu cheia 'beneficiari' suprascrie lista calculata
    automat din dividendele asociatilor (cota din tabelul `asociati`, sume din notele VALIDATE pe
    contul 457: divid_D=distribuit credit 457, divid_P=platit debit 457; impozit pe dividende
    PERIOD-AWARE - cota("impozit_dividend"): 10% pana in 2025, 16% de la 01.01.2026 (Legea
    141/2025, CF art.97). Foloseste perioada.an."""
    from core.common import cota as _cota205
    from datetime import date as _date205
    manual = cheie_manual(manual, "beneficiari")
    prof, asoc, total_distribuit, total_platit = pull(conn, schema, perioada)

    erori = erori_generare(prof)
    if erori:
        raise ValueError(" ".join(erori))

    beneficiari = manual.get("beneficiari")
    if beneficiari is None:
        beneficiari = []
        if total_platit > 0 and asoc:
            for a in asoc:
                platit = _i(Decimal(total_platit) * Decimal(str(a["cota"])) / Decimal(100))
                distribuit = _i(Decimal(total_distribuit) * Decimal(str(a["cota"])) / Decimal(100))
                if platit > 0:
                    # impozit pe dividende PERIOD-AWARE: 8% (2023-2024), 10% (2025, OUG 156/2024), 16% de la
                    # 01.01.2026 (Legea 141/2025, CF art.97 - "cota de impozit de 16% asupra
                    # dividendului brut"). baza1/imp1 se calculeaza pe dividendul PLATIT
                    # (impozitul se retine la plata; aliniat cu calea 2 de reconciliere care
                    # recalculeaza din Σ debit 457).
                    _cota_div = _cota205("impozit_dividend", _date205(perioada.an, 12, 31))[0]
                    impozit = _i(Decimal(platit) * _cota_div)
                    # divid_D = dividend DISTRIBUIT (Σ credit 457 x cota); divid_P = dividend
                    # PLATIT (Σ debit 457 x cota). Regula fully-paid documentata: divid_D >=
                    # divid_P mereu (nu poti plati cumulat mai mult decat s-a distribuit); daca
                    # fereastra anului nu contine creditul de distribuire (distribuit intr-un an
                    # anterior), distribuit=0 < platit => divid_D = platit (integral platit).
                    divid_d = max(distribuit, platit)
                    beneficiari.append({"categ": "1.a", "nume": a["nume"],
                                        "cif": a.get("cnp") or "", "baza": platit,
                                        "imp": impozit, "castig": 0, "pierdere": 0,
                                        "divid_d": divid_d, "divid_p": platit,
                                        "tip_plata": "2"})

    res = calcul_d205(prof, perioada.an, beneficiari)
    # POARTA A DOUA CALE (gard continut, 05.08.2026, pas 6/6): recalcul INDEPENDENT al bazei/
    # impozitului pe dividende din 457 (NU cross-check cu D100 = same-source trap).
    from core.d205_reconciliere import verifica_reconciliere as _vr205
    _vr205(conn, schema, perioada, res, manual)
    xml = build_xml(res)
    from core.reconciliere_emis import verifica_total_plata_a as _vte
    _vte("d205", xml, res.total_plata_a)   # poarta pe ARTEFACT: totalPlata_A parsat din emis == res
    return xml, res
