"""
Modul D300 — Decont de TVA (ANAF v12, conform OPANAF 174/2026 + Legea 141/2025).

REFĂCUT DE LA ZERO după ANAF structura D300 v12.0.0 (structura_D300_v12.0.0_10022026).

Separare strictă:
  - CALCUL PUR : calcul_d300(prof, an, luna, facturi, manual=None) -> Rezultat
  - VALIDARE   : valideaza(rezultat) -> listă erori (regulile ANAF)
  - XML        : build_xml(rezultat) -> str
  - CITIRE DB  : pull(conn, schema, an, luna) -> (prof, facturi)
  - ORCHESTRARE: genereaza(conn, schema, an, luna) -> (xml, rezultat)

COTE (de la 1 aug 2025, Legea 141/2025):
  - standard 21% -> R9  (livrări col1/col2), R22 (achiziții deductibile)
  - redusă  11% -> R10 (livrări), R24.1 (achiziții)
  - tranzitorie 9% locuințe -> R11 (livrări), R24.4 (achiziții)
  - 5% -> R24.5 deductibilă (livrări 5% R71 doar prin manual)
Cotele vechi (19/9/5) rămân pentru regularizări — suportate prin `manual`.

Maparea automată din facturi: emisă->colectată, primită->deductibilă, pe cotă.
Operațiunile speciale (intracomunitar, taxare inversă, regularizări, scutiri)
se pun prin dict-ul `manual` (rânduri introduse de contabil), nu derivate din facturi.
"""

from core.common import text_anaf as _t, LIMITE_TEXT_ANAF as _LIM  # limite text per-camp (03.08.2026)
import re
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from core import common as c
from core.identitate import valideaza_cui   # validator partajat CUI (read-only) - T1 MARKER_T2_T1_WIRED

NS = "mfp:anaf:dgti:d300:declaratie:v12"
REGULI = "2026.1"
_NEDIGIT = re.compile(r"\D")
_TIP_COD = {"L": "301", "T": "302", "S": "303", "A": "304"}

# cotele tratate automat din facturi (col bază, col tva) -> rândul de livrare/achiziție
# livrări: 21->R9, 11->R10, 9->R11 ; achiziții deductibile: 21->R22(Rd.24), 11->R23(Rd.25), 9->R75(Rd.25.1)
_LIVRARE_RAND = {21: "R9", 11: "R10", 9: "R11"}
_ACHIZ_RAND = {21: "R22", 11: "R23"}   # R22=Rd.24(21%), R23=Rd.25(11%). 9% deductibil: fara rand DUK-valid (vezi mai jos)


def _esc(v):
    s = "" if v is None else str(v)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))


def _int(x):
    # MASCA SCOASA 27.07.2026 (vezi core.common.numar_fiscal).
    from core.numere import numar_fiscal
    return int(numar_fiscal(x, "D300").quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _digits(x):
    return _NEDIGIT.sub("", x or "")


def _clean_bc(v):
    """Bancă/cont: ANAF interzice virgulă și #."""
    return ("" if v is None else str(v)).replace(",", " ").replace("#", " ").strip()


def tip_decont(prof):
    t = str(prof.get("tip_decont") or "").strip().lower()
    if t in ("l", "t", "s", "a"):
        return t.upper()
    if "trim" in t:
        return "T"
    if "sem" in t:
        return "S"
    if t.startswith("an"):
        return "A"
    return "L"


def nr_evidenta(an, luna, tip):
    """C(23) cu cifră de control. Poz.1-2=10, 3-5=cod tip, 6-7=01,
    8-11=LLAA, 12-17=ZZLLAA scadență, 18-21=0000, 22-23=sumă control."""
    cod = _TIP_COD.get(tip, "301")
    ll = "%02d" % luna
    aa = "%02d" % (an % 100)
    dm, dy = luna + 1, an
    if dm > 12:
        dm, dy = 1, dy + 1
    scad = "25" + "%02d" % dm + "%02d" % (dy % 100)
    s = "10" + cod + "01" + ll + aa + scad + "0000"
    return s + "%02d" % (sum(int(c) for c in s) % 100)


@dataclass
class Rezultat:
    an: int
    luna: int
    prof: dict
    R: dict = field(default_factory=dict)          # {"R9_1": int, "R9_2": int, ...}
    tva_de_plata: int = 0
    tva_de_recuperat: int = 0
    total_plata_a: int = 0
    avertismente: list = field(default_factory=list)


def _segmente(f):
    """[(cota_int|None, baza_Decimal), ...] dintr-o factură."""
    linii = f.get("linii") or []
    if linii:
        out = []
        for (cant, pret, cota) in linii:
            baza = Decimal(str(cant)) * Decimal(str(pret))
            ci = None if cota is None else int(round(float(cota)))  # ROTUNJIRE PE COTA (nu pe suma): cotele fiscale RO sunt intregi (21/11/9/5/0), bancar==aritmetic
            out.append((ci, baza))
        return out
    baza = Decimal(str(f.get("total") or 0)) - Decimal(str(f.get("tva") or 0))
    tva = Decimal(str(f.get("tva") or 0))
    ci = int(round(float(tva) / float(baza) * 100)) if (baza and tva) else None  # ROTUNJIRE PE COTA (nu pe suma): cotele fiscale RO sunt intregi (21/11/9/5/0), bancar==aritmetic
    return [(ci, baza)]


def calcul_d300(prof, perioada, facturi, manual=None):
    """
    Calcul PUR al decontului după structura ANAF v12.
    manual: dict opțional {rând: valoare} pentru operațiuni speciale introduse
            de contabil (ex. {"R5_1": 1000, "R5_2": 210} pt achiziții intracom).
    """
    manual = manual or {}
    _bad = [k for k in manual if not str(k).startswith("R")]
    if _bad:
        raise ValueError("D300: chei 'manual' necunoscute (asteptate Rxx_y): %s" % sorted(_bad))
    an, luna = perioada.an, perioada.luna
    Z = lambda: [Decimal(0), Decimal(0)]
    # colectată pe cote (livrări taxabile)
    col = {21: Z(), 11: Z(), 9: Z()}
    # deductibilă pe cote (achiziții)
    ded = {21: Z(), 11: Z(), 9: Z()}
    # Linii cu cotă fără rând D300 auto. Separate: TAXABILE (cotă>0 => TVA dispare din decont,
    # SUB-DECLARARE) vs COTĂ-ZERO (scutit/export/neimpozabil, doar informativ). Cuantificate
    # (bază+TVA) si semnalate distinct jos - un contabil nu trebuie sa rateze o vanzare taxabila
    # scapata din decont (probat pe firma DELTA: livrare 19% cu TVA scapata tacit).
    drop_l_tax_b = drop_l_tax_t = Decimal(0); drop_l_tax_n = 0
    drop_a_tax_b = drop_a_tax_t = Decimal(0); drop_a_tax_n = 0
    # [Task1 10.08.2026 - cota ZERO, NU se arunca tacit]
    # Livrari 0%: natura scutirii (R14 scutit CU drept/export art.294 vs R15 scutit FARA drept) NU e
    #   capturata in factura -> per-linie avertisment (NU se inventeaza clasificarea; camp lipsa raportat).
    # Achizitii 0% CURATE (fara TVA orfan forfetar, fara categorie_331): scutite/neimpozabile -> DERIVATE
    #   la R26_1 (rd.26, informativ, fara TVA) - apar in decont, nu dispar tacit.
    # Achizitii 0% cu categorie_331 (art.331 taxare inversa cu rata pierduta): avertisment dedicat.
    zero_livr = []      # [Decimal] baze livrari 0% (nu se clasifica auto)
    zero_achiz = []     # [Decimal] baze achizitii 0% scutite/neimpozabile -> R26_1
    achiz_331_0 = []    # [Decimal] baze achizitii 0% cu categorie art.331 (rata pierduta)

    # TVA la incasare (art.282 alin.3 CF, OUG 8/2026): pentru firmele care aplica sistemul,
    # exigibilitatea intervine la INCASARE (colectata) / PLATA (deductibila), proportional cu
    # suma decontata (art.282 alin.8: suta marita - fiecare decontare include TVA). Sursa
    # decontarilor = notele contabile legate de factura (nu emiterea) - vezi pull(). Fara acest
    # regim: exigibilitate la faptul generator (emitere), comportament neschimbat.
    tvai = bool(prof.get("tva_la_incasare"))
    livrare_ti_base = Decimal(0)   # rd.13: baza livrarilor cu taxare inversa (furnizor art.331), fara TVA
    # [Task2 10.08.2026] beneficiar taxare inversa PRIMITA (art.331, masuri de simplificare): anterior
    # se arunca tacit (`continue`). Acum se DERIVA rd.12 colectat + rd.25 deductibil (net zero).
    ti_ben_baza = Decimal(0); ti_ben_tva = Decimal(0); ti_ben_n = 0
    # [C-4 T2] TVA din ANTETUL facturilor primite neacoperit de randurile pe cota (ex: compensatia
    # forfetara agricultor art.315^1 al.17). NU se auto-deduce (nu se forteaza - lipsa flag Registrul
    # agricultorilor), dar NU se pierde tacit -> se masoara si se semnaleaza cantitativ (avertisment jos).
    orphan_ded = Decimal(0)
    for f in facturi:
        emisa = (f.get("directie") == "emisa")
        ti = bool(f.get("taxare_inversa"))
        cat331 = f.get("categorie_331")   # [Task1] natura art.331 (taxare inversa) pt achizitii 0%
        f_zero_b = Decimal(0)             # [Task1] baza cotelor 0% pe ACEASTA factura primita
        if tvai:
            from core import tva_incasare as _tvi
            segmente = []
            for d in (f.get("decontari") or []):
                cd = d.get("cota")
                ci = None if cd is None else int(round(float(cd)))  # ROTUNJIRE PE COTA (nu pe suma): cotele fiscale RO sunt intregi (21/11/9/5/0), bancar==aritmetic
                gross = Decimal(str(d.get("suma") or 0))
                if gross <= 0:
                    continue
                tva = _tvi.tva_din_incasare(gross, ci) if ci else Decimal(0)
                segmente.append((ci, gross - tva, tva))   # (cota, baza exigibila, tva exigibil)
        else:
            segmente = [(ci, baza, (baza * Decimal(ci) / Decimal(100) if ci else Decimal(0)))
                        for (ci, baza) in _segmente(f)]
        for (ci, baza, tva) in segmente:
            if ti:
                # [decizie Costin 06.08.2026 + Task2 10.08.2026] Taxare inversa art.331 (masuri de
                # simplificare): FURNIZORUL (emisa) raporteaza livrarea in rd.13 (baza, FARA TVA).
                # BENEFICIARUL (primita) declara rd.12 colectat + rd.25 deductibil (net zero) - ACUM
                # DERIVAT automat (inainte disparea tacit prin `continue`; cerinta Costin: fara drop tacit).
                if emisa:
                    livrare_ti_base += baza
                else:
                    ti_ben_baza += baza; ti_ben_tva += tva; ti_ben_n += 1
                continue
            if emisa:
                if ci in col:
                    col[ci][0] += baza; col[ci][1] += tva
                elif ci:   # cotă taxabilă fără rând colectat auto (ex. 19/5%): TVA ar dispărea
                    drop_l_tax_b += baza; drop_l_tax_t += tva; drop_l_tax_n += 1
                else:      # cotă 0% livrare (scutit/export/neimpozabil): clasificare manuala R14/R15
                    zero_livr.append(baza)
            else:
                if ci in ded:
                    ded[ci][0] += baza; ded[ci][1] += tva
                elif ci:   # cotă taxabilă fără rând deductibil auto (ex. 19/5%)
                    drop_a_tax_b += baza; drop_a_tax_t += tva; drop_a_tax_n += 1
                else:      # cotă 0% achizitie: se clasifica per-factura mai jos (R26 vs art.331 vs forfait)
                    f_zero_b += baza
        # [C-4 T2] TVA orfan: antetul facturii primite depaseste TVA-ul rezultat din cote (compensatie
        # forfetara agricultor art.315^1 al.17). Se masoara aici, se semnaleaza jos; nu se deduce tacit.
        if not emisa and not ti and not tvai:
            _antet = Decimal(str(f.get("tva") or 0))
            _linii_tva = sum((s[2] for s in segmente), Decimal(0))
            _orfan = _antet - _linii_tva
            if _orfan >= 1:
                orphan_ded += _orfan
            # [Task1] rutarea achizitiilor 0% de pe ACEASTA factura:
            if f_zero_b > 0:
                if cat331:
                    achiz_331_0.append(f_zero_b)       # art.331 taxare inversa, rata pierduta -> avertisment
                elif _orfan >= 1:
                    pass                                # forfait agricol (TVA orfan): semnalat de avert orfan, NU e scutit -> NU R26
                else:
                    zero_achiz.append(f_zero_b)         # scutit/neimpozabil curat -> R26_1

    R = {}
    def setr(name, val):
        v = _int(val)
        if v:
            R[name] = v

    # --- COLECTATĂ: livrări 21/11/9 ---
    setr("R9_1", col[21][0]);  setr("R9_2", col[21][1])     # 21%
    setr("R10_1", col[11][0]); setr("R10_2", col[11][1])    # 11%
    setr("R11_1", col[9][0]);  setr("R11_2", col[9][1])     # 9% tranzitoriu

    # rânduri manuale (intracomunitar, taxare inversă, regularizări, scutiri colectate)
    # [GARD CLASA] _aplicate = cheile manual chiar aplicate. Orice cheie manual care nu ajunge in _aplicate
    # produce eroare vizibila la final (vezi mai jos) - un rand introdus de contabil NU dispare tacit din
    # decont. Asta face allow-list-urile incomplete SA STRIGE, nu sa inghita (bug R12/R29/R30/R35/R36/R38/R39/R43/R44).
    _aplicate = set()
    for k, v in manual.items():
        if k.startswith(("R1_", "R2_", "R3_", "R4_", "R5_", "R6_", "R7_", "R8_",
                         "R12_",  # taxare inversa colectata (rd.12, auto-taxare beneficiar art.331) - se declara manual
                         "R13_", "R14_", "R15_", "R16_", "R64_", "R65_")):
            setr(k, v); _aplicate.add(k)

    # rd.13 = livrari cu taxare inversa (furnizor art.331): baza AUTO-derivata din facturi emise cu
    # taxare_inversa, FARA TVA (intra in R17_1 baza, nu in R17_2). [decizie Costin 06.08.2026]
    # Anti-dubla-numarare: daca vine SI manual R13_1 -> EROARE (nu insumare tacita).
    _r13 = _int(livrare_ti_base)
    if _r13:
        if "R13_1" in manual:
            raise ValueError(
                "D300 rd.13 (livrari taxare inversa): derivat AUTOMAT din facturi emise cu flag "
                "taxare_inversa (=%d) SI introdus manual (R13_1) - dubla numarare. Pastreaza o singura "
                "sursa: elimina R13_1 din manual SAU scoate taxare_inversa de pe facturi." % _r13)
        R["R13_1"] = _r13

    # [Task2 10.08.2026] rd.12 colectat + rd.25 deductibil = beneficiar taxare inversa primita (art.331,
    # masuri de simplificare), DERIVAT din facturi primite cu flag taxare_inversa. Confruntat cu sursa
    # ANAF (anaf_surse/d300_struct_anaf.txt): rd.12 (R12_1/R12_2) "Achizitii de bunuri si servicii supuse
    # masurilor de simplificare pentru care beneficiarul este obligat la plata TVA (taxare inversa)" =
    # COLECTAT; rd.25 (R25_1/R25_2) acelasi text = DEDUCTIBIL. Net zero: R12_2 intra in R17_2 (colectata),
    # R25_2 in R27_2 (deductibila) -> se anuleaza pe rezultat. DUK-validat (net zero acceptat). rd.7 NU se
    # foloseste: DUK impune V13/V14 R20_x = R7_x (alta familie, achizitii altele decat masuri de simplificare).
    # Anti-dubla-numarare: daca vin SI manual (R12/R25) -> EROARE (o singura sursa), ca la rd.13.
    _tib = _int(ti_ben_baza); _tit = _int(ti_ben_tva)
    if _tib or _tit:
        _dbl = sorted(k for k in ("R12_1", "R12_2", "R25_1", "R25_2") if k in manual)
        if _dbl:
            raise ValueError(
                "D300 taxare inversa primita (rd.12/rd.25): derivata AUTOMAT din facturi primite cu flag "
                "taxare_inversa (baza=%d, TVA=%d) SI introdusa manual (%s) - dubla numarare. Pastreaza o "
                "singura sursa: elimina cheile din manual SAU scoate taxare_inversa de pe facturi."
                % (_tib, _tit, ", ".join(_dbl)))
        R["R12_1"] = _tib; R["R12_2"] = _tit   # colectat (rd.12)
        R["R25_1"] = _tib; R["R25_2"] = _tit   # deductibil (rd.25)

    # R17 = TOTAL TAXĂ COLECTATĂ (formula oficială: sumă rd.1-18 cu excepții)
    # col.1 (bază) și col.2 (TVA) — pentru firma simplă: R9_1+R10_1+R11_1, R9_2+R10_2+R11_2
    r17_1 = sum(R.get(k, 0) for k in (
        "R1_1", "R2_1", "R3_1", "R4_1", "R5_1", "R6_1", "R7_1", "R8_1",
        "R9_1", "R10_1", "R11_1", "R12_1", "R13_1", "R14_1", "R15_1", "R16_1",
        "R64_1", "R65_1"))
    r17_2 = sum(R.get(k, 0) for k in (
        "R5_2", "R6_2", "R7_2", "R8_2", "R9_2", "R10_2", "R11_2", "R12_2",
        "R16_2", "R64_2", "R65_2"))
    if r17_1 or r17_2:
        R["R17_1"], R["R17_2"] = r17_1, r17_2

    # --- DEDUCTIBILĂ: achiziții 21/11/9 ---
    setr("R22_1", ded[21][0]); setr("R22_2", ded[21][1])    # 21% -> Rd.24 (DUK valid)
    setr("R23_1", ded[11][0]); setr("R23_2", ded[11][1])    # 11% -> Rd.25 (DUK valid; era gresit R74=19% legacy)
    # 9% deductibil: structura v12 il pune la Rd.25.1 (R75), dar validatorul DUK INSTALAT il RESPINGE
    # ("R75_1 nu trebuie sa exista aici"); R76 e taxare inversa (Rd.27.4, legat de R72). Nu emitem un
    # atribut care invalideaza intreaga declaratie - il semnalam pentru declarare manuala (avertisment mai jos).

    for k, v in manual.items():
        if k.startswith(("R18_", "R19_", "R20_", "R21_", "R23_", "R25_", "R26_",
                         "R29_", "R30_",  # ajustari/regularizari deductibila: R29 restituiri cumparatori straini, R30 regularizari taxa dedusa (feed R32)
                         "R35_", "R36_",  # regularizari rezultat: R35 sold reportat neachitat, R36 diferente inspectie fiscala (feed R37)
                         "R38_", "R39_",  # rezultat: R38 sold negativ reportat (fara rambursare), R39 diferente negative inspectie (feed R40)
                         "R43_", "R44_",  # ajustari deductibila incluse in totalul R27
                         "R72_", "R73_", "R75_")):
            setr(k, v); _aplicate.add(k)

    # [GARD CLASA] orice rand manual care nu s-a aplicat = EROARE VIZIBILA, nu drop tacit (cerinta Costin 03.08).
    _necunoscute = [k for k in manual if k not in _aplicate]
    if _necunoscute:
        raise ValueError(
            "D300: randuri 'manual' neacceptate: %s. Un rand introdus de contabil care nu e in lista de "
            "randuri de intrare valide trebuie sa produca eroare vizibila, NU sa dispara tacut din decont "
            "(cauze: typo in numele randului; sau rand COMPUTAT care nu se seteaza manual - ex. R17/R27/R28/"
            "R32/R33/R34/R37/R40/R41/R42). Daca e un rand de intrare legitim, adauga-l in allow-list." % sorted(_necunoscute))

    # R27 = TOTAL TAXA DEDUCTIBILA (col.1 baza, col.2 TVA). Formula oficiala
    # (structura_D300_v12.0.0_10022026.pdf, randul 101-102):
    #   R27_1 = R18_1+R19_1+R20_1+R21_1+R22_1+R23_1+R24_1+R25_1+R74_1+R75_1
    #   R27_2 = R18_2+R19_2+R20_2+R21_2+R22_2+R23_2+R24_2+R25_2+R43_2+R44_2+R74_2+R75_2
    # LIPSEA COMPLET pana la 16.07.2026: modulul calcula R30/R31/R40 direct din R22,
    # sarind peste tot lantul R27->R32->R34->R37->R40 pe care validatorul il cere si
    # verifica formula cu formula. Descoperit prin audit pe date reale, nu pe XML gol.
    r27_1 = sum(R.get(k, 0) for k in (
        "R18_1", "R19_1", "R20_1", "R21_1", "R22_1", "R23_1", "R24_1", "R25_1",
        "R74_1", "R75_1"))
    r27_2 = sum(R.get(k, 0) for k in (
        "R18_2", "R19_2", "R20_2", "R21_2", "R22_2", "R23_2", "R24_2", "R25_2",
        "R43_2", "R44_2", "R74_2", "R75_2"))
    if r27_1 or r27_2:
        R["R27_1"], R["R27_2"] = r27_1, r27_2

    # R28_2 = SUB-TOTAL TAXA DEDUSA conform art.297/298 - la o firma simpla,
    # egal cu R27_2 (nimic de scazut la acest nivel: nu avem TVA restituita
    # cumparatori straini (R29) inca).
    r28_2 = r27_2
    if r28_2:
        R["R28_2"] = r28_2

    # pro-rata pe deductibila -> R31_2 (Ajustari conform pro-rata / ajustari de taxa).
    # NU e "taxa deductibila x pro-rata direct" (asa calcula gresit modulul vechi) -
    # e o AJUSTARE separata, aditionala la R28. La pro_rata=100% (cazul uzual),
    # ajustarea e 0 - nu exista de ajustat.
    # Pro-rata ABSENTA = 100% (cazul uzual, fara activitate mixta). Dar o valoare
    # PREZENTA si invalida nu mai devine tacit 100% - ar declara deducere integrala
    # acolo unde firma are drept partial. Absenta e legitima, invalidul e eroare.
    from core.numere import numar_fiscal
    _pr = prof.get("pro_rata")
    pro_rata = 100.0 if _pr is None or (isinstance(_pr, str) and not _pr.strip()) \
        else float(numar_fiscal(_pr, "pro_rata"))
    r31_2 = 0
    if pro_rata < 100:
        r31_2 = _int(Decimal(str(r28_2)) * Decimal(str(100 - pro_rata)) / Decimal(100) * -1)
    if r31_2:
        R["R31_2"] = r31_2

    # R32 = TOTAL TAXA DEDUSA (rd.31+rd.32+rd.33+rd.34 in numerotarea veche = R28+R29+R30+R31)
    r32_2 = r28_2 + R.get("R29_2", 0) + R.get("R30_2", 0) + r31_2
    if r32_2:
        R["R32_2"] = r32_2

    # --- REZULTAT: lantul complet R33->R42, formule oficiale exacte ---
    r17_2_val = R.get("R17_2", 0)
    r33_2 = max(r32_2 - r17_2_val, 0)          # Suma negativa TVA in perioada
    r34_2 = max(r17_2_val - r32_2, 0)          # Taxa de plata in perioada
    if r33_2:
        R["R33_2"] = r33_2
    if r34_2:
        R["R34_2"] = r34_2

    r35_2 = R.get("R35_2", 0)   # sold de plata reportat din perioada precedenta
    r36_2 = R.get("R36_2", 0)   # diferente stabilite de inspectie fiscala
    r37_2 = r34_2 + r35_2 + r36_2   # TVA de plata cumulat
    if r37_2:
        R["R37_2"] = r37_2

    r38_2 = R.get("R38_2", 0)   # sold suma negativa reportata, fara rambursare ceruta
    r39_2 = R.get("R39_2", 0)   # diferente negative stabilite de inspectie fiscala
    r40_2 = r33_2 + r38_2 + r39_2   # Suma negativa TVA cumulata
    if r40_2:
        R["R40_2"] = r40_2

    r41_2 = max(r37_2 - r40_2, 0)   # Sold TVA de plata la sfarsitul perioadei
    r42_2 = max(r40_2 - r37_2, 0)   # Soldul sumei negative la sfarsitul perioadei
    if r41_2:
        R["R41_2"] = r41_2
    if r42_2:
        R["R42_2"] = r42_2

    de_plata = r41_2
    de_recuperat = r42_2

    # [Task1 10.08.2026] rd.26 (R26_1) = "Achizitii de bunuri si servicii scutite de taxa sau
    # neimpozabile" (sursa ANAF anaf_surse/d300_struct_anaf.txt, nr.crt.99). Achizitiile 0% CURATE
    # (fara taxare inversa, fara categorie_331, fara TVA orfan forfetar) se DECLARA aici - informativ,
    # fara TVA, NU intra in R27 (deductibila) - apar in decont, nu dispar tacit. Anti-dubla cu manual R26.
    _r26 = _int(sum(zero_achiz, Decimal(0)))
    if _r26:
        if "R26_1" in manual:
            raise ValueError(
                "D300 rd.26 (achizitii scutite/neimpozabile): derivat AUTOMAT din achizitii cu cota 0%% "
                "(=%d) SI introdus manual (R26_1) - dubla numarare. Pastreaza o singura sursa." % _r26)
        R["R26_1"] = _r26

    res = Rezultat(an=an, luna=luna, prof=prof)
    res.R = R
    res.tva_de_plata = de_plata
    res.tva_de_recuperat = de_recuperat
    # totalPlata_A = suma câmpurilor 27-124 (toate rândurile R emise)
    res.total_plata_a = sum(R.values())

    _f = lambda x: format(int(x), ",").replace(",", ".")
    # Livrări TAXABILE fără rând valid pentru perioadă (19/5% etc): TVA-ul lor DISPARE din decont
    # (sub-declarare). ANAF (DUK v12, 2026) RESPINGE rândurile 19/5% (colectat R69/R71) — probat —
    # deci NU sunt auto-emise si NU trebuie adaugate manual acolo (ar invalida declaratia).
    if drop_l_tax_n:
        res.avertismente.append(
            "%d linii livrare cu cotă în afara 21/11/9 (bază %s lei, TVA %s lei) — TVA colectată NEDECLARATĂ "
            "(sub-declarare). Cotele 19/5%% nu au rând acceptat de ANAF în decontul v12 — NU le adăuga manual "
            "la R69/R71 (respinse); corectează cota facturii sau tratează ca regularizare (R16)."
            % (drop_l_tax_n, _f(drop_l_tax_b), _f(drop_l_tax_t)))
    for _b in zero_livr:
        res.avertismente.append(
            "Livrare cu cotă 0%% (bază %s lei) — nu se clasifică automat: decontul cere distincţia scutit "
            "CU drept de deducere (R14, ex. export/art.294) vs scutit FĂRĂ drept (R15), iar natura scutirii "
            "NU e capturată în factură. Clasific-o manual la R14/R15 (altfel nu apare în decont)."
            % _f(_b))
    if drop_a_tax_n:
        res.avertismente.append(
            "%d linii achiziție cu cotă în afara 21/11/9 (bază %s lei, TVA %s lei) — deducere NEINCLUSĂ. "
            "Cotele 19/5%% nu au rând deductibil acceptat de ANAF în decontul v12 — NU le adăuga manual la "
            "R74/R24 (respinse); corectează cota facturii sau tratează ca regularizare."
            % (drop_a_tax_n, _f(drop_a_tax_b), _f(drop_a_tax_t)))
    if zero_achiz:
        res.avertismente.append(
            "%d achiziţii cu cotă 0%% (bază %s lei) — raportate automat la R26 (scutite de taxă sau "
            "neimpozabile), fără impact pe TVA. Verifică: dacă sunt achiziţii intracomunitare, "
            "reclasifică-le la taxare inversă (R5/R18)."
            % (len(zero_achiz), _f(sum(zero_achiz, Decimal(0)))))
    if achiz_331_0:
        res.avertismente.append(
            "%d achiziţii cu categorie art.331 (taxare inversă) dar cotă 0%% (bază %s lei) — cota aplicabilă "
            "nu e capturată, deci rd.12/rd.25 (colectat+deductibil) NU se pot deriva. Declar-o manual la "
            "R12/R25 sau completează cota (altfel taxarea inversă nu apare în decont)."
            % (len(achiz_331_0), _f(sum(achiz_331_0, Decimal(0)))))
    if ti_ben_n:
        res.avertismente.append(
            "%d achiziţii cu taxare inversă primită (bază %s lei, TVA %s lei) — derivate automat: rd.12 "
            "colectat + rd.25 deductibil (net zero, art.331). Anterior dispăreau tacit din decont."
            % (ti_ben_n, _f(ti_ben_baza), _f(ti_ben_tva)))
    if ded[9][0]:
        res.avertismente.append(
            "Achiziții deductibile 9%% (bază %s lei, TVA %s lei) — NEINCLUSE automat: rândul deductibil 9%% "
            "(Rd.25.1/R75 din structura v12) e RESPINS de validatorul DUK instalat 2026 (probat). NU există rând "
            "deductibil 9%% valid pentru perioadă — NU-l declara MANUAL la R75 (respins); corectează cota sau "
            "tratează ca regularizare, altfel TVA de plată e supraevaluată." % (_f(ded[9][0]), _f(ded[9][1])))
    if orphan_ded >= 1:
        res.avertismente.append(
            "Achiziții cu TVA în antet neacoperit de rândurile pe cotă (%s lei) — ex. compensația "
            "forfetară agricultor (art.315^1 al.17 CF): NU se auto-deduce (regim special, lipsă flag "
            "Registrul agricultorilor), dar NU se pierde tacit. Declar-o MANUAL la rândul deductibil, "
            "altfel TVA de plată e supraevaluată." % _f(orphan_ded))
    rez = ("de plată " + _f(de_plata)) if de_plata else (("de recuperat " + _f(de_recuperat)) if de_recuperat else "0")
    res.avertismente.append("Rezultat TVA %s lei." % rez)
    return res


def erori_generare(prof):
    """Campurile de PROFIL obligatorii pentru D300. Lista goala = se poate genera.

    Acelasi nume si aceeasi semnatura ca la d100/d101/d205/d710 - aceeasi situatie,
    aceeasi rezolvare. Verificarile EXISTAU de mult in `valideaza(res)`, dar valideaza()
    NU era chemata niciodata din genereaza(): XML-ul iesea cu banca="" si cont="", iar
    ANAF il respingea cu "atribut prezent dar vid nepermis". Contabilul primea eroarea
    criptica a validatorului in loc de "completeaza IBAN-ul". Dovedit 27.07.2026 pe tenant_002 si tenant_003 (2 din 3 firme).

    [T1 10.08.2026] Pe langa non-gol se verifica si CONTINUTUL, tot pre-DUK:
      - CUI: cifra de control (validator partajat core.identitate), nu doar prezenta;
      - CAEN: forma C(4) din structura ANAF (4 cifre);
      - pro_rata: interval [0,100] cand e prezent (absent = 100%, legitim).

    Sursa UNICA: valideaza() cheama tot functia asta, nu-si repeta verificarile.
    """
    erori = []
    _cui = prof.get("cui")
    if not _digits(_cui):
        erori.append("LIPS\u0102 CUI firm\u0103.")
    else:
        _ok_cui, _motiv_cui = valideaza_cui(_cui)   # T1: cifra de control, pre-DUK
        if not _ok_cui:
            erori.append("CUI firm\u0103 invalid (%s): %s." % (_digits(_cui), _motiv_cui))
    if not str(prof.get("nume") or "").strip():
        erori.append("LIPS\u0102 denumire firm\u0103.")
    if not _clean_bc(prof.get("banca")):
        erori.append("LIPS\u0102 banc\u0103 \u2014 obligatorie la D300.")
    if not _clean_bc(prof.get("iban") or prof.get("cont")):
        erori.append("LIPS\u0102 cont/IBAN \u2014 obligatoriu la D300.")
    _caen = _digits(prof.get("caen"))
    if not _caen:
        erori.append("LIPS\u0102 CAEN \u2014 obligatoriu la D300.")
    elif len(_caen) != 4:
        erori.append("COD CAEN invalid: '%s' \u2014 trebuie 4 cifre (structura ANAF caen C(4))." % _caen)
    _pr = prof.get("pro_rata")   # T1: pro_rata prezent trebuie in [0,100]; absent = 100% (legitim)
    if _pr is not None and str(_pr).strip():
        from core.numere import numar_fiscal
        try:
            _prv = float(numar_fiscal(_pr, "pro_rata"))
        except Exception:
            erori.append("pro_rata invalid: %r \u2014 trebuie num\u0103r in [0,100]." % _pr)
        else:
            if not (0.0 <= _prv <= 100.0):
                erori.append("pro_rata in afara intervalului [0,100]: %s (structura ANAF pro_rata N(7.2))." % _prv)
    return erori

def _blocante_pre_duk(res):
    """Motive care INVALIDEAZ\u0102 decontul, semnalate PRE-DUK ca ValueError (nu R18 brut la upload).
    Aici doar corela\u021bia tip_decont \u2194 luna (DUK regula R18); c\u00e2mpurile de profil sunt gardate
    de erori_generare (poarta din genereaza)."""
    prof = res.prof
    luna = res.luna
    tip = tip_decont(prof)
    erori = []
    if tip == "A" and luna != 12:
        erori.append("tip_decont=A (anual) cere luna=12 (DUK regula R18).")
    if tip == "S" and luna not in (6, 12):
        erori.append("tip_decont=S (semestrial) cere luna 06 sau 12 (DUK regula R18).")
    if tip == "T" and luna not in (2, 3, 5, 6, 8, 9, 11, 12):
        erori.append("tip_decont=T (trimestrial) cere luna in (02,03,05,06,08,09,11,12) (DUK regula R18).")
    return erori


def _avertismente_marja(res):
    """\u00b11% pe r\u00e2ndurile pe cot\u0103 cu valori. DUK doar ATEN\u021aIONEAZ\u0102 (decontul r\u0103m\u00e2ne
    uploadabil), deci se raporteaz\u0103 ca avertisment, NU blocheaz\u0103 generarea."""
    av = []
    cota_std_dec, _ = c.cota("tva_standard", date(res.an, res.luna, 1))
    cota_std = int(round(float(cota_std_dec) * 100))  # ROTUNJIRE PE COTA (nu pe suma): cotele fiscale RO sunt intregi (21/11/9/5/0), bancar==aritmetic

    def marja(baza_k, tva_k, cota):
        b = res.R.get(baza_k, 0)
        t = res.R.get(tva_k, 0)
        if b and t:
            lo = round((cota - 1) / 100 * b)
            hi = round((cota + 1) / 100 * b)
            if not (lo <= t <= hi):
                av.append("TVA %s (%d) nu se \u00eencadreaz\u0103 in %d%%\u00b11%% din baza %d (DUK: aten\u021bionare, uploadabil)."
                          % (tva_k, t, cota, b))
    marja("R9_1", "R9_2", cota_std)
    marja("R10_1", "R10_2", 11)
    marja("R11_1", "R11_2", 9)
    marja("R22_1", "R22_2", cota_std)
    return av


def valideaza(res):
    """Verific\u0103 regulile ANAF. \u00centoarce lista COMPLET\u0102 (blocante + avertismente marj\u0103) - compat.
    erori_generare(prof) r\u0103m\u00e2ne sursa unic\u0103 pentru c\u00e2mpurile de profil.
    genereaza() ruteaz\u0103 separat: blocantele -> ValueError, marja -> avertisment."""
    prof = res.prof
    erori = _blocante_pre_duk(res)
    erori.extend(erori_generare(prof))
    erori.extend(_avertismente_marja(res))
    return erori

def build_xml(res):
    prof = res.prof
    tip = tip_decont(prof)
    cui = _digits(prof.get("cui"))
    den = prof.get("nume") or ""
    adr = " ".join(x for x in [prof.get("adresa"), prof.get("oras"), prof.get("judet")] if x).strip() or den
    A = [
        'luna="%d"' % res.luna, 'an="%d"' % res.an,
        'depusReprezentant="0"', 'bifa_interne="0"', 'temei="0"',
        'nume_declar="%s"' % _esc(_t(prof.get("declarant_nume") or den or "ADMINISTRATOR", _LIM["d300"]["nume_declar"])),
        'prenume_declar="%s"' % _esc(_t(prof.get("declarant_prenume") or "-", _LIM["d300"]["prenume_declar"])),
        'functie_declar="%s"' % _esc(_t(prof.get("declarant_functie") or "ADMINISTRATOR", _LIM["d300"]["functie_declar"])),
        'cui="%s"' % _esc(cui),
        'den="%s"' % _esc(_t(den, _LIM["d300"]["den"])),
        'adresa="%s"' % _esc(_t(adr, _LIM["d300"]["adresa"])),
        'banca="%s"' % _esc(_t(_clean_bc(prof.get("banca")), _LIM["d300"]["banca"])),
        'cont="%s"' % _esc(_t(_clean_bc(prof.get("iban") or prof.get("cont")), _LIM["d300"]["cont"])),
        'caen="%s"' % _esc(_digits(prof.get("caen")) or "0"),
        'tip_decont="%s"' % tip,
        'pro_rata="%s"' % ("%.2f" % (float(prof.get("pro_rata")) if str(prof.get("pro_rata") or "").strip() else 100.0)),
        'bifa_cereale="N"', 'bifa_mob="N"', 'bifa_disp="N"', 'bifa_cons="N"',
        'solicit_ramb="N"',
        'nr_evid="%s"' % nr_evidenta(res.an, res.luna, tip),
        'totalPlata_A="%d"' % res.total_plata_a,
    ]
    for k in sorted(res.R.keys()):
        A.append('%s="%d"' % (k, res.R[k]))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<declaratie300 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xmlns="%s" xsi:schemaLocation="%s D300.xsd" ' % (NS, NS)
            + ' '.join(A) + '/>')


def _aloca_pe_cote(gross, linii, total_tva):
    """Imparte suma DECONTATA (gross, incl. TVA) pe cotele facturii, proportional cu ponderea
    gross a fiecarei cote (baza_cota x (100+cota)/100). Corecteaza limita multi-cota a postarilor
    din reconciliere (care foloseau prima cota). Fallback fara linii: o cota din total/tva."""
    if linii:
        g = {}
        for (cant, pret, cota) in linii:
            if cota is None:
                continue
            ci = int(round(float(cota)))  # ROTUNJIRE PE COTA (nu pe suma): cotele fiscale RO sunt intregi (21/11/9/5/0), bancar==aritmetic
            baza = Decimal(str(cant)) * Decimal(str(pret))
            g[ci] = g.get(ci, Decimal(0)) + baza * (100 + ci) / 100
        tg = sum(g.values(), Decimal(0))
        if tg > 0:
            return [{"suma": gross * gc / tg, "cota": ci} for ci, gc in g.items()]
    total, tva = (total_tva or (0, 0))
    base = Decimal(str(total or 0)) - Decimal(str(tva or 0))
    ci = int(round(float(tva) / float(base) * 100)) if (base and tva) else None  # ROTUNJIRE PE COTA (nu pe suma): cotele fiscale RO sunt intregi (21/11/9/5/0), bancar==aritmetic
    return [{"suma": gross, "cota": ci}] if ci else []


def _pull_incasare(cur, inceput, sfarsit):
    """Facturi cu DECONTARE (incasare cont 4111 / plata cont 401) VALIDATA in perioada. Pentru
    fiecare, suma decontata alocata pe cote -> `decontari`. Exigibilitatea D300 se calculeaza din
    aceste decontari (art.282 alin.3 CF), nu din emitere."""
    cur.execute(
        "SELECT i.factura_id AS fid, f.directie AS directie, SUM(l.suma) AS settled "
        "FROM inregistrari i "
        "JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
        "JOIN facturi f ON f.id = i.factura_id "
        "WHERE i.status = 'validata' AND i.factura_id IS NOT NULL "
        "AND COALESCE(f.taxare_inversa, false) = false "  # art.282(6)/297(3): taxare inversa = regim general, nu la incasare
        "AND i.data >= %s AND i.data < %s "
        "AND ((f.directie = 'emisa' AND l.cont_credit = '4111') "
        "  OR (f.directie = 'primita' AND l.cont_debit = '401')) "
        "GROUP BY i.factura_id, f.directie", (inceput, sfarsit))
    settle = cur.fetchall()
    if not settle:
        return []
    fids = [r["fid"] for r in settle]
    cur.execute("SELECT f.id AS fid, f.total, f.tva, l.cantitate, l.pret_unitar, l.cota_tva "
                "FROM facturi f LEFT JOIN factura_linii l ON l.factura_id = f.id "
                "WHERE f.id = ANY(%s)", (fids,))
    linii, totaluri = {}, {}
    for r in cur.fetchall():
        totaluri[r["fid"]] = (r["total"], r["tva"])
        if r["cantitate"] is not None and r["cota_tva"] is not None:
            linii.setdefault(r["fid"], []).append((r["cantitate"], r["pret_unitar"], r["cota_tva"]))
    out = []
    for r in settle:
        gross = Decimal(str(r["settled"] or 0))
        if gross <= 0:
            continue
        dec = _aloca_pe_cote(gross, linii.get(r["fid"]), totaluri.get(r["fid"]))
        out.append({"directie": r["directie"], "decontari": dec})
    return out


def pull(conn, schema, perioada):
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, caen, banca, iban, tip_decont, pro_rata, "
                    "COALESCE(tva_la_incasare, false) AS tva_la_incasare, "
                    "declarant_nume, declarant_prenume, declarant_functie "
                    "FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        # [06.08.2026] Fereastra de date urmeaza PERIOADA FISCALA TVA (tip_decont din vectorul
        # firmei), nu luna-ancora: un platitor trimestrial agrega TOT trimestrul. Eticheta XML
        # (perioada.luna) ramane separata (build_xml). Fara default tacit: tip_decont lipsa -> eroare.
        _inc, _sf = c.fereastra_tva(perioada, c.perioada_tva_tip(prof))
        inceput = _inc.isoformat()
        sfarsit = _sf.isoformat()
        if prof.get("tva_la_incasare"):
            # TVA la incasare: exigibilitate pe DECONTARI (incasari/plati validate in perioada),
            # nu pe emitere. Vezi _pull_incasare.
            return prof, _pull_incasare(cur, inceput, sfarsit)
        cur.execute("SELECT f.id, f.directie, f.total, f.tva, "
                    "COALESCE(f.taxare_inversa, false) AS taxare_inversa, f.categorie_331, "
                    "l.cantitate, l.pret_unitar, l.cota_tva "
                    "FROM facturi f LEFT JOIN factura_linii l ON l.factura_id = f.id "
                    "WHERE f.data_emitere >= %s AND f.data_emitere < %s ORDER BY f.id",
                    (inceput, sfarsit))
        rows = cur.fetchall()
    fmap = {}
    for r in rows:
        f = fmap.setdefault(r["id"], {"directie": r["directie"],
                                      "taxare_inversa": r["taxare_inversa"],
                                      "categorie_331": r["categorie_331"],
                                      "total": r["total"] if r["total"] is not None else 0,
                                      "tva": r["tva"] if r["tva"] is not None else 0, "linii": []})
        if r["cantitate"] is not None and r["pret_unitar"] is not None:
            f["linii"].append((r["cantitate"], r["pret_unitar"], r["cota_tva"]))
    return prof, list(fmap.values())


def genereaza(conn, schema, perioada, manual=None):
    if perioada.luna is None or not (1 <= perioada.luna <= 12):
        raise ValueError("D300 lunar: luna invalidă: %r" % perioada.luna)
    prof, facturi = pull(conn, schema, perioada)
    # POARTA (27.07.2026): profil incomplet -> STOP cu mesaj clar, nu XML respins de ANAF.
    erori = erori_generare(prof)
    if erori:
        raise ValueError("D300 nu se poate genera: " + " ".join(erori))
    res = calcul_d300(prof, perioada, facturi, manual)
    # [T2 10.08.2026] valideaza(res) era COD MORT: genereaza chema doar erori_generare(prof).
    # Cablam verificarile prietenoase aici, rutate pe severitate:
    #  - blocante (tip_decont <-> luna, DUK regula R18) -> ValueError cu motiv EXACT, pre-DUK
    #    (contabilul nu mai primeste eroarea bruta a validatorului la upload);
    #  - marja +-1% pe rand pe cota -> DUK doar atentioneaza => avertisment, nu blocaj.
    _blocante = _blocante_pre_duk(res)
    if _blocante:
        raise ValueError("D300 nu se poate genera: " + " ".join(_blocante))
    res.avertismente.extend(_avertismente_marja(res))
    # POARTA A DOUA CALE (gard de continut, 05.08.2026): reconciliere pe totaluri dintr-un
    # recalcul INDEPENDENT al liniilor brute. Divergenta = eroare vizibila care numeste ambele
    # valori; NU repara tacit. Vezi core/d300_reconciliere.py + GARZI cat.4 (limita declarata).
    from core.d300_reconciliere import verifica_reconciliere
    verifica_reconciliere(conn, perioada, res, manual)
    _xml = build_xml(res)
    from core.reconciliere_emis import verifica_total_plata_a as _vte
    _vte("d300", _xml, res.total_plata_a)   # poarta pe ARTEFACT: totalPlata_A parsat din emis == res
    # [zero_base_v1 10.08.2026] Decont pe zero care POATE fi defect != nil legal: R tot zero DAR facturi in
    # perioada (necontabilizate / TVA la incasare nedecontata) -> semnaleaza (NU blocheaza; nil-ul e legal).
    if not any(res.R.values()):
        from core import common as _c
        _inc, _sf = _c.fereastra_tva(perioada, _c.perioada_tva_tip(prof))
        with conn.cursor() as _cur:
            _cur.execute("SELECT count(*) FROM facturi WHERE data_emitere >= %s AND data_emitere < %s",
                         (_inc.isoformat(), _sf.isoformat()))
            _nf = _cur.fetchone()[0]
        if _nf:
            res.avertismente.append(
                "Decont pe zero: nicio valoare declarata, dar exista %d facturi in perioada "
                "(necontabilizate sau TVA la incasare nedecontata). Nil-ul e legal - confirma ca nu lipsesc date." % _nf)
    return _xml, res
