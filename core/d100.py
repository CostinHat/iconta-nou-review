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

#: [07.09.2026] denumirea OFICIALA (cu diacritice) - se afiseaza pe ecranul public,
#: derivata de scripts/genereaza_declaratii_lista.py. Corectura ORTOGRAFICA peste
#: denumirea deja consemnata in modul; NU o re-verificare la ANAF.
DENUMIRE_OFICIALA = 'Declarație privind obligațiile de plată la bugetul de stat'

from datetime import date
from core import common as _common
from core.common import text_anaf as _t, cheie_manual, LIMITE_TEXT_ANAF as _LIM  # limite text per-camp din structura (03.08.2026)
from core.identitate import valideaza_cui  # T1 (CATALOG_INVALIDITATE.md): sursa CANONICA checksum CUI, import READ-ONLY (LEAF, fara db)
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from core import repo_d100 as _repo

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
    #: «Suma de plata» a obligatiei — CAMP, nu valoare derivata la emitere.
    #:
    #: **De ce e camp (02.09.2026).** Pana azi traia numai in `build_xml`, care emitea
    #: `suma_plata="%d" % o.suma_dat`. XML-ul o declara, dar `randuri` — dict-ul persistat in
    #: `public.declaratii_depuse` prin `coada_api.randuri_din_res` — **nu o continea**, fiindca
    #: `dataclasses.asdict` vede numai campuri. Iar perechea orizontala D101 rd.50 ↔ Σ D100
    #: (`control_incrucisat._plati_anticipate_din_d100`) citeste exact `suma_plata`: pe orice
    #: depunere facuta prin aplicatie aduna **0**, deci compara randul 50 cu zero si numeste
    #: „divergenta" propria ei orbire. *Masurat pe calea reala, nu dedus: un D100 de 3.000 lei
    #: emite `suma_plata="3000"` in XML si persista o obligatie fara cheia aia.*
    #:
    #: Perechea era calibrata in amandoua directiile — dar pe dictionare scrise de mana, cu o cheie
    #: pe care generatorul n-o scrie. *Un gard care se uita exact unde codul e corect raporteaza
    #: verde despre o lume pe care n-o vede.*
    suma_plata: int = 0
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
    # [deficiența 295] „Rezumat” ca la D112: baza de calcul (veniturile perioadei pe conturi, ce se scade) și calculul impozitului
    sinteza: list = field(default_factory=list)
    # [376–378, 18.10.2026] la impozitul pe profit: calculul pe rezultatul fiscal cumulat (`profit_trimestru`), pentru a doua cale și ecran
    profit: dict = field(default_factory=dict)
    # [lotul 11, C77] o D100 peste una deja depusă pe trimestru: textul de pe ecran și depunerea pe care s-a sprijinit (D100 n-are d_rec)
    rectificativa: object = None
    depunere_anterioara_nr: object = None


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
        cod = str(o["cod_oblig"])
        if suma < 0 or (suma == 0 and cod not in COD_ZERO_DECLARAT):   # [376/378] impozitul pe profit se declară și cu 0
            continue
        cod_bug = o.get("cod_bugetar") or COD_BUGETAR.get(cod, "")
        if not cod_bug:
            raise ValueError("D100: obligația cu codul %r nu are cont bugetar în nomenclatorul aplicației, iar ANAF cere "
                             "contul bugetar pe fiecare obligație; declarația nu se generează fără el." % cod)
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
            cod_oblig=cod, suma_dat=suma, suma_plata=suma, cod_bugetar=cod_bug, scadenta=scad_str,
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
        erori.append("Lipsă CUI (obligatoriu).")
    else:
        # T1 (CATALOG_INVALIDITATE.md): checksum/format CUI validat PRE-DUK cu sursa canonica
        # core.identitate. Pana aici un CUI non-numeric / lungime gresita / cifra de control
        # gresita era emis TACIT si il prindea doar DUK (mesaj brut la depunere).
        valid, motiv = valideaza_cui(cui)
        if not valid:
            erori.append("D100: CUI firmă invalid (%s: %s). Corectează în Profil firmă." % (cui, motiv))
    if not (prof.get("nume") or "").strip():
        erori.append("Lipsă denumire firmă (obligatorie).")
    if not (prof.get("adresa") or "").strip():
        erori.append("Lipsă adresă domiciliu fiscal (obligatorie).")
    from core.firma_profil_api import erori_declarant as _ed   # [R101] sursa unica
    erori += _ed(prof)
    return erori


def build_xml(res):
    prof = res.prof
    # [31.08.2026] ABSENȚĂ DECLARATĂ, nu tăcere. OPANAF 602/2026 a adăugat poziția 116
    # «Contribuție de solidaritate» în nomenclatorul obligațiilor D100, declarabilă LUNAR. Nu o
    # construim (zero firme purtătoare, deci zero instanțe pe care s-o probăm) — dar nici nu tăcem:
    # dacă apare o firmă care ar putea fi purtătoare, se află AICI, nu la depunere.
    from core import d100_pozitia_116 as _p116
    _av116 = _p116.avertisment(prof)
    if _av116:
        res.avertismente.append(_av116)
    # T6 (CATALOG_INVALIDITATE.md): text_anaf trunchiaza TACIT den/adresa la limita oficiala C(n)
    # (LIMITE_TEXT_ANAF). Pierderea de date era silentioasa; emitem un avertisment NON-blocant care
    # numeste campul cand valoarea reala depaseste limita si a fost taiata pentru XML.
    for _cheie, _et, _lim_c in (("nume", "denumirea firmei", _LIM["d100"]["den"]),
                                ("adresa", "adresa domiciliului fiscal", _LIM["d100"]["adresa"])):
        _real = " ".join(str(prof.get(_cheie) or "").split())
        if len(_real) > _lim_c:
            res.avertismente.append(
                "D100: %s depășește %s și a fost trunchiată pentru XML - verifică." % (_et, _common.cate(_lim_c, "caracter", "caractere")))
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
              _esc(_t(prof.get("declarant_nume"), _LIM["d100"]["nume_declar"])),   # [C69] fără implicit: `erori_declarant` a blocat deja lipsa
              _esc(_t(prof.get("declarant_prenume"), _LIM["d100"]["prenume_declar"])),
              _esc(_t(prof.get("declarant_functie"), _LIM["d100"]["functie_declar"])),
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
                 % (o.cod_oblig, o.scadenta, o.suma_dat, o.suma_plata, o.nr_evid))
        if o.cod_bugetar:
            linie += ' cod_bugetar=%s' % _esc(o.cod_bugetar)
        # cota: OBLIGATORIU si NUMAI pt. cod_oblig 121 (micro), valoare "1" (struct D100 poz.17a:
        # "daca cod_oblig=121 atunci cota=1 altfel cota=null"; ERR cota micro invalida). Gard bidirectional
        # - face imposibil un XML respins de validator (121 fara cota / cota pe alt cod).
        if str(o.cod_oblig) == "121":
            if str(o.cota) != "1":
                raise ValueError("D100: la impozitul pe veniturile microîntreprinderilor (codul 121) cota se completează cu 1 (este %r); altfel validatorul ANAF respinge declarația." % (o.cota,))
            linie += ' cota=%s' % _esc(o.cota)
        elif o.cota:
            raise ValueError("D100: cota se completează numai la impozitul pe veniturile microîntreprinderilor (codul 121); obligația cu codul %r are cota %r." % (o.cod_oblig, o.cota))
        linie += "/>"
        H.append(linie)
    H.append("</declaratie100>")
    return "\n".join(H)


def pull(conn, schema, perioada):
    """Citește profilul firmei și veniturile / cheltuielile TRIMESTRULUI din notele validate (micro: baza impozitului 121 = veniturile
    70x/75x/76x − 709). [deficiențele 376–378, 18.10.2026] Impozitul pe profit nu mai pleacă de aici: are calculul lui pe rezultatul
    fiscal cumulat, `profit_trimestru` (A8 — cumulul de la 01.01 — rămâne, acum pe rezultatul fiscal, nu pe profitul contabil)."""
    import psycopg2.extras as _E
    _inc, _sf = perioada.interval()
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        prof = _repo.select_firma_profil(cur) or {}
        if prof.get("oras"):
            prof["adresa"] = " ".join(x for x in
                (prof.get("adresa"), prof.get("oras"), prof.get("judet")) if x)
        r = _repo.select_inregistrari_linii(cur, _inc, _sf) or {"venituri": 0, "cheltuieli": 0}
    return prof, r["venituri"], r["cheltuieli"]


def deriva_obligatii(prof, venituri, cheltuieli, an, luna, cota=None):
    """Derivarea obligatiilor D100 micro (121 pe venituri; profitul are `profit_trimestru`),
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
        # [deficiențele 376–378, 18.10.2026] impozitul pe profit nu se derivă din venituri / cheltuieli: se calculează pe rezultatul
        # fiscal cumulat, minus ce s-a declarat deja (`profit_trimestru`, cu conexiune). O cale care ar ajunge aici ar calcula vechea bază.
        raise RuntimeError("D100 pe impozitul pe profit se calculează cu `profit_trimestru` (rezultatul fiscal cumulat), nu din venituri.")
    return obligatii, avert


#: [deficiențele 376 + 378, 18.10.2026] codurile impozitului pe profit se declară și cu 0. OPANAF 587/2016 anexa 4 pct.3.1.2 alin.(1):
#: „În situația în care, în perioada de raportare s-a înregistrat pierdere fiscală sau scăderea profitului impozabil, la rândul 1 din
#: formular se va înscrie cifra 0 (zero).” Validatorul DUK acceptă secțiunea `<obligatie>` cu 0 (probat 18.10.2026: cod 103, suma 0 ->
#: „valid”); respinge numai declarația FĂRĂ secțiune — de unde refuzul pe zero, care rămâne la micro (121).
COD_ZERO_DECLARAT = ("102", "103", "105")


class _DeLaInceputulAnului:
    """Fereastra 01.01 – sfârșitul trimestrului `trim`, cu interfața lui `Perioada` (`an`, `interval()`), pentru `d101.pull`."""

    def __init__(self, an, trim):
        from core.common import Perioada as _Per
        self.an, self.trim = an, trim
        self._sf = _Per(an, trim=trim).interval()[1]

    def interval(self):
        import datetime as _dt
        return _dt.date(self.an, 1, 1), self._sf


def _impozit_cumulat(conn, schema, an, trim, cota=None):
    """Impozitul pe profit stabilit CUMULAT de la 01.01 la sfârșitul trimestrului `trim`, pe REZULTATUL FISCAL (CF art.19 alin.(1)):
    aceleași rânduri și aceleași reguli ca D101 (`d101.calcul_d101` — o singură aritmetică), din contabilitate (rd.1–7, rezerva legală
    rd.13) plus ajustările fiscale scrise de contabil (`ajustari_fiscale`, cumulate până la trimestru); pierderea anilor anteriori
    recuperată în limita a 70% (CF art.31 alin.(1)); creditul de sponsorizare în plafonul CF art.25 alin.(4) lit.i)."""
    from core import ajustari_fiscale as _aj, d101 as _d101
    fer = _DeLaInceputulAnului(an, trim)
    prof101, r = _d101.pull(conn, schema, fer)
    with conn.cursor() as cur:
        aj = _aj.cumulat(cur, schema, an, trim)
    intrari = {"P1": r.get("ven_expl", 0), "P2": r.get("chelt_expl", 0), "P4": r.get("ven_fin", 0), "P5": r.get("chelt_fin", 0)}
    rezerva = {"capital": r.get("capital", 0), "rezerva_existenta": r.get("rezerva_existenta", 0),
               "chelt_impozit": r.get("chelt_impozit", 0)}
    res, x = _d101.calcul_cu_ajustari(prof101, an, intrari, aj, fer.interval()[1], cota=cota, cifra_afaceri=r.get("cifra_afaceri", 0),
                                      rezerva=rezerva, din_conturi=_aj.din_conturi(r))
    P = res.P
    pierdere, recuperata, sponsorizare, credit = x["pierdere"], x["recuperata"], x["sponsorizare"], x["credit_sponsorizare"]
    return {"trim": trim, "P": P, "impozit": _i(P.get("P48", 0)), "ajustari": aj, "pierdere": pierdere, "recuperata": recuperata,
            "sponsorizare": sponsorizare, "credit_sponsorizare": credit, "chelt_impozit": _i(r.get("chelt_impozit", 0) or 0),
            "din_conturi": x["din_conturi"],
            "interval": fer.interval()}


def _suma_profit(randuri):
    """Suma declarată pe codurile impozitului pe profit dintr-o depunere D100, sau None dacă depunerea n-are rândurile păstrate."""
    if not randuri:
        return None
    obl = [o for o in ((randuri or {}).get("obligatii") or []) if str((o or {}).get("cod_oblig") or "") in COD_ZERO_DECLARAT]
    if not obl:
        return 0
    return sum(_i(o.get("suma_plata", o.get("suma_dat", 0)) or 0) for o in obl)


def profit_trimestru(conn, schema, perioada, cota=None):
    """[deficiențele 376–378, 18.10.2026] D100 pe impozitul pe profit, pentru trimestrul de raportare (I–III; IV se definitivează în D101,
    CF art.41 alin.(1)): impozitul stabilit cumulat la sfârșitul trimestrului (`_impozit_cumulat`) minus impozitul DEJA DECLARAT pe
    trimestrele anterioare ale anului — prin iConta sau preluat din istoric la migrare (377: „D100 scade impozitul deja declarat, indiferent
    dacă a fost depus prin iConta sau înainte de preluare, și arată de unde vine cifra”). Un trimestru anterior nedepus nu se mută aici: i se
    scade diferența stabilită (OPANAF 587/2016 anexa 4 pct.3.1.2: fiecare D100 declară diferența cumulatului față de trimestrul precedent)
    și se semnalează restanța; unul depus fără suma păstrată oprește calculul (impozitul lui s-ar cere încă o dată).
    -> {"suma", "cumulat", "anterioare": [{trim, suma, sursa, data, fel}], "linii", "avertismente"}."""
    import datetime as _dt
    from core.pdf_util import bani as _bani, data_ro as _data_ro
    from core import ajustari_fiscale as _aj, d101 as _d101
    trim = perioada.trim
    if trim not in (1, 2, 3):
        raise ValueError("D100 pe impozitul pe profit se depune pentru trimestrele I–III; trimestrul IV se definitivează în D101 (CF art.41 "
                         "alin.(1): „[...] trimestrial, până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III”).")
    cumul = [_impozit_cumulat(conn, schema, perioada.an, q, cota) for q in range(1, trim + 1)]
    with conn.cursor() as cur:
        depuse = {int(l): (rd, s, d) for l, rd, s, d in _repo.d100_depuse_an(cur, schema, perioada.an)}
    anterioare, avert = [], []
    for q in range(1, trim):
        dep = depuse.get(q * 3)
        if dep is None:
            stabilit = max(0, cumul[q - 1]["impozit"] - (cumul[q - 2]["impozit"] if q > 1 else 0))
            anterioare.append({"trim": q, "suma": stabilit, "sursa": None, "data": None, "fel": "nedepus"})
            avert.append("D100 pe T%d/%d nu e depus: impozitul stabilit pe T%d/%d (%s lei) se declară pe T%d/%d, nu aici — e restanță pe T%d/%d."
                         % (q, perioada.an, q, perioada.an, _bani(stabilit), q, perioada.an, q, perioada.an))
            continue
        randuri, sursa, data = dep
        suma = _suma_profit(randuri)
        if suma is None:
            raise ValueError(
                "D100 pe T%d/%d e consemnat ca depus%s, dar fără suma declarată, deci nu se poate scădea din cumulat — impozitul de pe T%d/%d "
                "s-ar cere încă o dată. Adaugă suma de plată declarată în Migrare › Istoric declarații (coloana „suma de plată”)."
                % (q, perioada.an, " (preluat din istoric la migrare)" if sursa == "migrare" else "", q, perioada.an))
        anterioare.append({"trim": q, "suma": suma, "sursa": sursa, "data": data.isoformat() if data else None, "fel": "depus"})
    c = cumul[-1]
    deja = sum(a["suma"] for a in anterioare)
    suma = max(0, c["impozit"] - deja)
    P = c["P"]
    inc, sf = c["interval"]
    per = "%s – %s" % (_data_ro(inc), _data_ro(sf - _dt.timedelta(days=1)))
    linii = ["Rezultatul fiscal cumulat %s (CF art.19 alin.(1); aceleași rânduri ca D101):" % per,
             "rezultatul contabil: %s lei (venituri %s − cheltuieli %s)" % (
                 _bani(P.get("P7", 0)), _bani(P.get("P1", 0) + P.get("P4", 0)), _bani(P.get("P2", 0) + P.get("P5", 0))),
             "deduceri: %s lei%s; venituri neimpozabile: %s lei; cheltuieli nedeductibile: %s lei%s" % (
                 _bani(P.get("P16", 0)), (" (din care rezerva legală %s lei)" % _bani(P.get("P13", 0))) if P.get("P13") else "",
                 _bani(P.get("P21", 0)), _bani(P.get("P34", 0)),
                 "".join(" (din care %s, din %s: %s lei — scrie rândul în Registrul de evidență fiscală dacă o parte e deductibilă)"
                         % (_aj.RANDURI[k][0], _aj.DIN_CONTURI[k][1], _bani(v)) for k, v in c["din_conturi"].items()))]
    if c["pierdere"]:
        linii.append("pierderea fiscală din anii anteriori: %s lei de recuperat, recuperată acum %s lei (cel mult 70%%, CF art.31 alin.(1))"
                     % (_bani(c["pierdere"]), _bani(c["recuperata"])))
    linii.append("profitul impozabil cumulat: %s lei; impozitul cumulat: %s lei%s" % (
        _bani(P.get("P40", 0)), _bani(P.get("P41", 0)),
        (" − creditul de sponsorizare %s lei = %s lei" % (_bani(c["credit_sponsorizare"]), _bani(c["impozit"]))) if c["credit_sponsorizare"] else ""))
    for a in anterioare:
        unde = ("depus prin iConta%s" % (" pe %s" % _data_ro(a["data"]) if a["data"] else "")) if a["fel"] == "depus" and a["sursa"] != "migrare" \
            else ("preluat din istoric la migrare%s" % (" (depus pe %s)" % _data_ro(a["data"]) if a["data"] else "")) if a["fel"] == "depus" \
            else "nedepus — diferența stabilită pe trimestrul lui"
        linii.append("deja declarat pe T%d/%d: %s lei (%s)" % (a["trim"], perioada.an, _bani(a["suma"]), unde))
    linii.append("de plată pe T%d/%d: %s lei − %s lei = %s lei%s" % (
        trim, perioada.an, _bani(c["impozit"]), _bani(deja), _bani(suma),
        " (pierdere sau scădere față de cumulatul declarat: se declară 0, OPANAF 587/2016 pct.3.1.2)" if c["impozit"] <= deja else ""))
    if c["chelt_impozit"] > 0 and not P.get("P23"):
        avert.append("Contul 691 are rulaj debitor %s lei în %s (cheltuiala cu impozitul pe profit), iar ajustarea „rd.23 — cheltuieli cu "
                     "impozitul pe profit” lipsește. Cheltuiala e nedeductibilă (CF art.25 alin.(4) lit.a)) — fără ajustare, impozitul "
                     "cumulat iese mai mic. Scrie-o în Registrul de evidență fiscală." % (_bani(c["chelt_impozit"]), per))
    # [deficiența 382, lotul 9] fereastra calculului e CUMULATĂ (01.01 – sfârșitul trimestrului): ce e în afara evidenței validate se spune
    avert.extend(_d101.avertismente_evidenta(conn, schema, inc, sf, "D100 pe T%d/%d" % (trim, perioada.an)))
    # [lotul 10, deficiența 425] cumulul de la 01.01 fără rulajele dinainte de preluare: se spune (`rulaje_preluate.avertisment`)
    from core import rulaje_preluate as _rp
    with conn.cursor() as cur:
        _av_rul = _rp.avertisment(cur, schema, perioada.an, "d100")
    if _av_rul:
        avert.append(_av_rul["motiv"])
    return {"suma": suma, "cumulat": c["impozit"], "anterioare": anterioare, "linii": linii, "avertismente": avert, "P": P}


def sinteza_d100(conn, prof, perioada, venituri, cheltuieli, obligatii, cota=None):
    """[deficiența 295, comanda Costin 16.10.2026, verbatim în DECIZII] „D100 pasul 2 arată doar obligația (cod 121, 10 lei, cota 1), fără
    baza de calcul: veniturile perioadei pe conturi și eventualele deduceri. Adaugă «Rezumat» ca la D112.” Rândurile Rezumatului, din
    ACEEAȘI sursă ca obligația (micro: `repo_d100.venituri_pe_conturi`, aceleași note ca `select_inregistrari_linii`; profit: cumulatul
    din `pull`) — nu un al doilea calcul."""
    from core.pdf_util import bani as _bani
    per = "T%d/%d" % (perioada.trim, perioada.an)
    regim = (prof.get("regim_fiscal") or "").lower()
    oblig = "; ".join("cod %s: %s lei" % (o["cod_oblig"], format(int(o["suma_dat"]), ",").replace(",", ".")) for o in obligatii)
    if regim == "micro":
        _inc, _sf = perioada.interval()
        with conn.cursor() as cur:
            conturi = _repo.venituri_pe_conturi(cur, _inc, _sf)
        c = Decimal(str(cota)) if cota is not None else _rata_impozit_default("micro", perioada.an, perioada.trim * 3)
        out = ["Baza de calcul %s: veniturile trimestrului din notele validate (conturile 70x, 75x, 76x; reducerile acordate 709 se "
               "scad)." % per]
        out += ["cont %s%s: %s lei" % (cont, " (se scade)" if str(cont).startswith("709") else "", _bani(suma)) for cont, suma in conturi]
        scazute = [s_ for cont, s_ in conturi if str(cont).startswith("709")]
        out.append("Deduceri din bază: %s." % (("709, %s lei" % _bani(-sum(scazute))) if scazute else "niciuna"))
        out.append("Baza impozabilă: %s lei × cota %s%% = %s (rotunjit la leu)." % (_bani(venituri), c.normalize(), oblig or "0 lei"))
        return out
    return []


def obligatii_perioada(conn, schema, perioada, prof=None, venituri=None, cheltuieli=None, cota=None):
    """SURSA UNICĂ a obligațiilor D100 ale perioadei — generatorul, a doua cale din controlul încrucișat și poarta de fapt a semaforului:
    micro -> `deriva_obligatii` pe veniturile trimestrului; profit -> `profit_trimestru` (rezultatul fiscal cumulat − ce s-a declarat).
    -> (obligatii, detaliu); detaliu["profit"] = rezultatul lui `profit_trimestru` la profit."""
    if prof is None:
        prof, venituri, cheltuieli = pull(conn, schema, perioada)
    if (prof.get("regim_fiscal") or "").lower() == "profit":
        p = profit_trimestru(conn, schema, perioada, cota)
        return [{"cod_oblig": "103", "suma_dat": p["suma"]}], {"profit": p}
    obligatii, _ = deriva_obligatii(prof, venituri, cheltuieli, perioada.an, perioada.trim * 3, cota)
    return obligatii, {}


def coduri_declarate(xmls):
    """[lotul 11, C77] {cod_oblig: suma_dat} din D100-urile depuse pe trimestru (ultima depunere care declară codul câștigă)."""
    import xml.etree.ElementTree as _ET
    decl = {}
    for x in xmls:
        for el in _ET.fromstring(x.encode("utf-8") if isinstance(x, str) else x).iter():
            if el.tag.rsplit("}", 1)[-1] == "obligatie":
                decl[str(el.attrib.get("cod_oblig"))] = int(el.attrib.get("suma_dat") or 0)
    return decl


def _peste_depusa(conn, schema, perioada, res, prof):
    """[lotul 11, C77] D100 pe un trimestru cu D100 deja înregistrată: obligațiile DECLARATE se corectează numai prin D710 (OPANAF
    587/2016 anexa nr.4: „Corectarea obligațiilor declarate eronat în formular se face prin depunerea formularului 710 «Declarație
    rectificativă»”; anexa nr.5 cap.I: D710 corectează impozitele „declarate în formularul 100”). D100 nu are bifă de rectificativă:
    o a doua D100 cu aceleași obligații le-ar declara de două ori. Ce poate cuprinde = numai obligațiile încă nedeclarate pe trimestru
    (o obligație omisă e nedeclarată: anexa nr.4, „echivalează cu nedeclararea obligației respective”). Fără conținutul depunerii,
    obligațiile declarate nu se pot afla -> refuz numit."""
    from core import rectificativa as _rect
    from core.erori import RefuzGenerare
    from core.pdf_util import bani as _bani
    st = _rect.stabileste(conn, schema, "d100", perioada.an, trim=perioada.trim)
    if st.dep is None:
        return res
    per = "T%d/%d" % (perioada.trim, perioada.an)
    deps = st.dep["toate"]
    fara = [d for d in deps if not d.get("xml")]
    if fara:
        raise RefuzGenerare(
            "D100 pe %s e deja înregistrată: %s, iar conținutul ei nu e în iConta.eu. O obligație declarată se corectează numai prin "
            "D710 (OPANAF 587/2016, instrucțiunile formularului 100); fără declarația depusă, iConta.eu nu știe ce obligații conține, "
            "deci nu generează o a doua D100 care le-ar declara din nou." % (per, _rect.descriere_depunere(fara[-1])))
    decl = coduri_declarate([d["xml"] for d in deps])
    noi = [o for o in res.obligatii if o.cod_oblig not in decl]
    if not noi:
        dif = ["codul %s: declarat %s, acum %s" % (o.cod_oblig, _bani(decl[o.cod_oblig], "lei"), _bani(o.suma_dat, "lei"))
               for o in res.obligatii if decl.get(o.cod_oblig) != o.suma_dat]
        raise RefuzGenerare(
            "D100 pe %s e deja depusă (%s) cu toate obligațiile de acum. %s O obligație declarată se corectează numai prin D710 "
            "(OPANAF 587/2016, instrucțiunile formularului 100), nu printr-o a doua D100." % (
                per, _rect.descriere_depunere(st.dep),
                ("Diferențe: %s; se corectează în D710." % "; ".join(dif)) if dif else "Nicio sumă nu diferă: nu e nimic de corectat."))
    vechi = [o.cod_oblig for o in res.obligatii if o.cod_oblig in decl]
    nou = calcul_d100(prof, res.an, res.luna, [{"cod_oblig": o.cod_oblig, "suma_dat": o.suma_dat, "cod_bugetar": o.cod_bugetar,
                                                 "scadenta": o.scadenta, "cota": o.cota} for o in noi])
    res.obligatii, res.total_plata_a = nou.obligatii, nou.total_plata_a
    res.rectificativa = ("D100 numai cu obligațiile încă nedeclarate pe %s (codurile %s), peste %s%s." % (
        per, ", ".join(o.cod_oblig for o in noi), _rect.descriere_depunere(st.dep),
        ("; codurile %s, declarate acolo, se corectează numai prin D710" % ", ".join(vechi)) if vechi else ""))
    res.depunere_anterioara_nr = st.nr
    return res


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

    obligatii, detaliu = obligatii_perioada(conn, schema, perioada, prof, venituri, cheltuieli, cota)

    # [zero_base_refuz_v1 10.08.2026] D100 FĂRĂ secțiunea <obligatie> = XML respins de DUKIntegrator („lipsa sectiune obligatorie”).
    # La micro, trimestrul fără venituri n-are ce declara -> refuz. [376/378, 18.10.2026] La profit nu se ajunge aici: obligația 103 se
    # declară și cu 0 (`COD_ZERO_DECLARAT`), deci are mereu secțiunea.
    if not obligatii:
        _inc, _sf = perioada.interval()
        with conn.cursor() as _cur:
            _nf = _repo.select_facturi(_cur, _inc, _sf)[0]
        _hint = (" Există %s în perioada - contabilizează-le întâi." % _common.cate(_nf, "factură emisă necontabilizată", "facturi emise necontabilizate")) if _nf else ""
        raise ValueError("D100 nu se depune pe zero: nicio obligație (venituri contabilizate cont 70x = 0)." + _hint)
    res = calcul_d100(prof, an, luna, obligatii)
    if detaliu.get("profit"):
        res.profit = detaliu["profit"]
        res.avertismente.extend(detaliu["profit"]["avertismente"])
        res.sinteza = list(detaliu["profit"]["linii"])
    else:
        res.sinteza = sinteza_d100(conn, prof, perioada, venituri, cheltuieli, obligatii, cota)
        # [deficiența 382, lotul 9] micro: notele de venit nevalidate ale trimestrului se spun (amortizarea nu schimbă impozitul micro)
        from core import d101 as _d101
        _inc, _sf = perioada.interval()
        res.avertismente.extend(_d101.avertismente_evidenta(conn, schema, _inc, _sf, "D100 pe T%d/%d" % (perioada.trim, perioada.an),
                                                            cu_amortizare=False))
    # POARTA A DOUA CALE (gard continut, pas 4/4 lant reconciliere): recalcul INDEPENDENT al
    # obligatiei din SURSA (venituri cont 70x, note validate) x cota din registru, confruntat
    # cu suma_dat a generatorului. Prinde CATALOG #31 aggregation-loss (venit scapat din pull ->
    # suma_dat gresita, azi DUK-valid). NU alege singur cine are dreptate; NU repara tacit.
    from core.d100_reconciliere import verifica_reconciliere as _vr100
    _vr100(conn, perioada, res, manual)
    _peste_depusa(conn, schema, perioada, res, prof)   # [lotul 11, C77] după reconciliere: ea privește trimestrul întreg
    xml = build_xml(res)
    from core.reconciliere_emis import verifica_total_plata_a as _vte
    _vte("d100", xml, res.total_plata_a)   # poarta pe ARTEFACT: totalPlata_A parsat din emis == res
    return xml, res
