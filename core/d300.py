"""
Modul D300 — Decont de TVA (ANAF v12, conform OPANAF 174/2026 + Legea 141/2025).

REFĂCUT DE LA ZERO după ANAF structura D300 v12.0.0 (structura_D300_v12.0.0_10022026).

Separare strictă:
  - CALCUL PUR : calcul_d300(prof, perioada, facturi, manual=None, reclasificari=None) -> Rezultat
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

# [B1 D300] Exigibilitatea in regim normal: faptul generator (art.282 alin.1 CF) =
# COALESCE(data_faptului_generator, data_emitere); EXCEPTIE avansul (art.282 alin.2 lit.b) =
# data_emitere (exigibil la EMITEREA facturii de avans). Data faptului generator nu mai e cod mort.
_EXIG_NORMAL = ("(CASE WHEN f.tip_operatiune = 'avans' THEN f.data_emitere "
                "ELSE COALESCE(f.data_faptului_generator, f.data_emitere) END)")
# [B1 D300] Facturi DECLARABILE in decont. Lista NU mai traieste aici: vine din
# `core/nomenclator_status_factura.py` — un adevar, un loc (P1). Pana la 22.08.2026 lista era scrisa
# textual in TREI locuri (aici, la :1095, si in d300_reconciliere:80), iar `de_preluat` era clasat
# staging DESI calea de emitere a aplicatiei il produce — 4 facturi emise, 3.052,00 lei TVA colectata,
# nu intrau in decont. Vezi decizia de interpretare din antetul nomenclatorului.
from core import nomenclator_status_factura as _nsf
_STATUS_FINAL = _nsf.clauza_sql("f")


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
    # CANAL SEPARAT note_rezultat vs avertismente.
    # CONSTATARE = fapt NEUTRU despre rezultatul produs, fara nimic de facut de contabil
    #   (ex. "Rezultat TVA X lei.", decont nul asumat, operatiuni derivate automat net-zero).
    # AVERTISMENT = ceva ce contabilul TREBUIE sa verifice/corecteze (sub-declarare, clasificare
    #   manuala R14/R15, cota in afara 21/11/9 lipsa, reclasificare T/R neacoperita etc.).
    avertismente: list = field(default_factory=list)
    note_rezultat: list = field(default_factory=list)   # fapte neutre despre rezultat (fara actiune)
    nula_asumata: bool = False   # [B1 zero_base] decont nul ASUMAT explicit (nicio valoare declarata)


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


def calcul_d300(prof, perioada, facturi, manual=None, reclasificari=None):
    """
    Calcul PUR al decontului după structura ANAF v12.
    manual: dict opțional {rând: valoare} pentru operațiuni speciale introduse
            de contabil (ex. {"R5_1": 1000, "R5_2": 210} pt achiziții intracom).
    reclasificari: SURSA UNICĂ partajată cu D390 (tabelul d390_reclasificare, scris prin panoul
            D390). Bun-vs-serviciu e proprietate a OPERAȚIUNII, nu a declarației: contabilul
            reclasifică O DATĂ, D300 și D390 CITESC amândouă. Cheie identică cu D390:
            (directie, tara, cod) derivate din PREFIXUL CUI via core.d390._clasifica_partener.
            Forme acceptate: {(an, luna, directie, tara, cod): tip} (per lună — necesar la
            trimestru, unde același partener poate fi reclasificat diferit în luni diferite) SAU
            {(directie, tara, cod): tip} (o singură lună). RECLASIFICĂ (mută), nu adaugă → fără
            dublă numărare. Emisă tip P -> rd.3 (R3_1 + R3_1_1) în loc de rd.1; primită tip S ->
            rd.7 colectat (R7_1/R7_2 + R7_1_1/R7_1_2) + oglindă rd.20 deductibil
            (R20_1/R20_2 + R20_1_1/R20_1_2), net zero, în loc de rd.5+rd.18. Vezi DECIZII 21.07 F125.
    """
    manual = manual or {}
    _bad = [k for k in manual if not str(k).startswith("R")]
    if _bad:
        raise ValueError("D300: chei 'manual' necunoscute (așteptate Rxx_y): %s" % sorted(_bad))
    an, luna = perioada.an, perioada.luna
    # [F125 reclasificare] Normalizez cheile in doua forme: per-luna {(an,luna): {(dir,tara,cod):tip}}
    # (trimestru) + flat {(dir,tara,cod):tip} (o luna). Import regula de tranzitie din D390 (SURSA
    # UNICA - NU o redefinesc): _reclasificare_tip valideaza tipul contra directiei (ca la scriere).
    from core.d390 import _reclasificare_tip as _recl_tip, _clasifica_partener as _clas_part
    _recl_by_luna = {}
    _recl_flat = {}
    for _k, _v in (reclasificari or {}).items():
        if len(_k) == 5:
            _a, _l, _d, _t, _c = _k
            _recl_by_luna.setdefault((_a, _l), {})[(_d, _t, _c)] = _v
        elif len(_k) == 3:
            _recl_flat[_k] = _v
        else:
            raise ValueError("D300: cheie 'reclasificări' invalidă %r - aștept (an,luna,direcție,țară,cod) "
                             "sau (direcție,țară,cod)." % (_k,))

    def _recl_luna(an_f, luna_f):
        """Override-urile 3-tuple aplicabile unei facturi (luna ei de exigibilitate): flat +
        specificul lunii (specificul lunii are prioritate)."""
        m = dict(_recl_flat)
        m.update(_recl_by_luna.get((an_f, luna_f), {}))
        return m
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
    # [B1 D300] IC/export via tert_tara (nu doar cota). Refoloseste TARI_UE din core/d390.
    from core.d390 import TARI_UE as _TARI_UE
    from datetime import date as _date_ic
    _cota_std_ic_dec, _ = c.cota("tva_standard", _date_ic(an, luna, 1))
    cota_std_ic = int(round(float(_cota_std_ic_dec) * 100))  # ROTUNJIRE PE COTA (procent intreg RO 21/11/9/5/0, nu pe suma): autolichidarea IC se face la cota interna standard
    ic_livr_bunuri = Decimal(0)          # rd.1 (R1): livrari IC de bunuri catre UE (0%, art.294 alin.2)
    export_livr = Decimal(0)             # rd.14 (R14): export catre non-UE (scutit cu drept de deducere)
    ic_ach_b = Decimal(0); ic_ach_t = Decimal(0); ic_ach_n = 0   # rd.5 colectat + rd.18 deductibil (taxare inversa IC, net zero)
    # [F125 reclasificare bun->serviciu, sursa unica D390] Servicii IC (reclasificate P/S in D390):
    #   emisa tip P -> rd.3 (R3_1 baza col.1, fara TVA) + sub-rand rd.3.1 (R3_1_1 "din care servicii IC").
    #   primita tip S -> rd.7 colectat (R7_1/R7_2 + R7_1_1/R7_1_2) + OGLINDA rd.20 deductibil
    #       (R20_1/R20_2 + R20_1_1/R20_1_2), autolichidare la cota interna, net zero (DUK V_13-V_16: R20=R7).
    ic_prest_serv = Decimal(0)                                    # rd.3 (R3_1): prestari servicii IC (emisa, tip P), 0%
    ic_serv_b = Decimal(0); ic_serv_t = Decimal(0); ic_serv_n = 0 # rd.7 colectat + rd.20 deductibil (achizitii servicii IC, tip S, net zero)
    tr_reclas = []                       # [(directie, tip)] operatiuni reclasificate T/R in D390 (triangulatie/regim) - NEACOPERIT D300, semnalat
    foreign_pos = []                     # [(tara, baza, tva)] factura straina cu cota interna pozitiva (probabil eroare) -> avertisment, nu R9
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
        # [B1] tara partenerului (INGHETATA pe factura): partener non-RO -> ruta IC/export, nu cota interna.
        tara = (f.get("tert_tara") or "RO").upper()
        strain = (tara != "RO")
        ue = (tara in _TARI_UE)
        # [F125 reclasificare bun->serviciu] Tipul operatiunii IC (default bunuri L/A) sau overridat prin
        # SURSA UNICA D390 (d390_reclasificare). CHEIE IDENTICA cu D390: (directie, tara, cod) derivate din
        # PREFIXUL CUI via core.d390._clasifica_partener (NU din tert_tara - ca lookup-ul sa coincida cu ce
        # a scris panoul D390). Doar partenerii clasificati "ic" au override; fara CUI IC valid ramane bunuri.
        directie = "emisa" if emisa else "primita"
        tip_def_ic = "L" if emisa else "A"
        _cat_p, _ptara, _pcod, _motiv_p = _clas_part(f.get("cui"))
        if _cat_p == "ic":
            _an_f = f.get("an_exig", an); _luna_f = f.get("luna_exig", luna)
            tip_ic = _recl_tip(directie, _ptara, _pcod, _recl_luna(_an_f, _luna_f), tip_def_ic)
        else:
            tip_ic = tip_def_ic
        if (tvai or f.get("exigibil_la_decontare")) and not ti:
            # taxarea inversa e exigibila la faptul generator (art.282 alin.6 CF), NU la incasare:
            # ramane pe calea de emitere (_segmente) chiar sub tva_la_incasare - vezi _pull_taxare_inversa.
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
            if strain:
                # [B1] partener non-RO: rutare pe TARA, nu pe cota interna.
                if ci:   # cota interna POZITIVA pe factura straina = probabil eroare -> NU tacit in R9
                    foreign_pos.append((tara, baza, tva)); continue
                if emisa:
                    if ue:
                        # [F125] tip din SURSA UNICA D390: L=bunuri->rd.1; P=servicii->rd.3; T/R=triangulatie
                        # /regim (NU axa bun-serviciu) -> ramane bunuri (rd.1) DAR se semnaleaza (limita declarata).
                        if tip_ic == "P":
                            ic_prest_serv += baza    # rd.3 prestari servicii IC (0%)
                        else:
                            ic_livr_bunuri += baza   # rd.1 livrare IC bunuri (0%) [L, sau T/R nemapate]
                            if tip_ic in ("T", "R"):
                                tr_reclas.append((directie, tip_ic))
                    else:
                        export_livr += baza          # rd.14 export (scutit cu drept)
                else:
                    if ue:
                        # [F125] tip din SURSA UNICA D390: A=bunuri->rd.5+rd.18; S=servicii->rd.7+rd.20 (oglinda).
                        if tip_ic == "S":
                            ic_serv_b += baza                                      # rd.7 baza (taxare inversa servicii IC)
                            ic_serv_t += baza * Decimal(cota_std_ic) / Decimal(100)  # autolichidare la cota interna
                            ic_serv_n += 1
                        else:
                            ic_ach_b += baza             # rd.5 baza (taxare inversa IC bunuri)
                            ic_ach_t += baza * Decimal(cota_std_ic) / Decimal(100)  # autolichidare la cota interna
                            ic_ach_n += 1
                    else:
                        f_zero_b += baza             # import non-UE 0% -> ruta scutite/neimpozabile (rd.26)
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
                "D300 rd.13 (livrări taxare inversa): derivat AUTOMAT din facturi emise cu flag "
                "taxare_inversa (=%d) ȘI introdus manual (R13_1) - dublă numărare. Pastreaza o singură "
                "sursa: elimină R13_1 din manual SAU scoate taxare_inversa de pe facturi." % _r13)
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
                "D300 taxare inversa primită (rd.12/rd.25): derivată AUTOMAT din facturi primite cu flag "
                "taxare_inversa (baza=%d, TVA=%d) ȘI introdusă manual (%s) - dublă numărare. Pastreaza o "
                "singură sursa: elimină cheile din manual SAU scoate taxare_inversa de pe facturi."
                % (_tib, _tit, ", ".join(_dbl)))
        R["R12_1"] = _tib; R["R12_2"] = _tit   # colectat (rd.12)
        R["R25_1"] = _tib; R["R25_2"] = _tit   # deductibil (rd.25)

    # [B1 D300] IC/export derivate din tert_tara. Livrari IC bunuri -> rd.1 (0%); export non-UE -> rd.14;
    # achizitii IC bunuri -> rd.5 colectat + rd.18 deductibil (taxare inversa, net zero: R18=R5, DUK V_7/V_8).
    # Anti-dubla-numarare: derivat AUTOMAT + introdus manual pe acelasi rand -> EROARE (o singura sursa), ca la rd.13.
    _r1 = _int(ic_livr_bunuri)
    if _r1:
        if "R1_1" in manual:
            raise ValueError(
                "D300 rd.1 (livrări IC bunuri): derivat AUTOMAT din facturi emise către UE (tert_tara, "
                "=%d) plus introdus manual (R1_1) - dublă numărare. Pastreaza o singură sursa." % _r1)
        R["R1_1"] = _r1
    _r14 = _int(export_livr)
    if _r14:
        if "R14_1" in manual:
            raise ValueError(
                "D300 rd.14 (export/livrări scutite cu drept): derivat AUTOMAT din facturi emise către "
                "non-UE (tert_tara, =%d) plus introdus manual (R14_1) - dublă numărare." % _r14)
        R["R14_1"] = _r14
    _r5b = _int(ic_ach_b); _r5t = _int(ic_ach_t)
    if _r5b or _r5t:
        _dbl_ic = sorted(k for k in ("R5_1", "R5_2", "R18_1", "R18_2") if k in manual)
        if _dbl_ic:
            raise ValueError(
                "D300 achiziții IC bunuri (rd.5 colectat + rd.18 deductibil, taxare inversa): derivate "
                "AUTOMAT din facturi primite din UE (tert_tara, baza=%d, TVA=%d) plus introduse manual "
                "(%s) - dublă numărare. Pastreaza o singură sursa." % (_r5b, _r5t, ", ".join(_dbl_ic)))
        R["R5_1"] = _r5b; R["R5_2"] = _r5t     # colectat (rd.5)
        R["R18_1"] = _r5b; R["R18_2"] = _r5t   # deductibil (rd.18) - oglinda rd.5, net zero (DUK V_7/V_8)

    # [F125 reclasificare bun->serviciu, SURSA UNICA D390] Servicii IC reclasificate (MUTA, nu adauga).
    # rd.3 (emisa tip P): R3_1 baza (col.1, 0% fara TVA) + sub-rand rd.3.1 R3_1_1 "din care servicii IC".
    # rd.3/rd.3.1 sunt in allow-list-ul manual (colectata) -> gard anti-dubla auto+manual, ca la rd.1.
    _r3 = _int(ic_prest_serv)
    if _r3:
        _dbl_p = sorted(k for k in ("R3_1", "R3_1_1") if k in manual)
        if _dbl_p:
            raise ValueError(
                "D300 rd.3 (prestări servicii IC): derivat AUTOMAT din facturi emise către UE reclasificate "
                "serviciu (P) în D390 (=%d) plus introdus manual (%s) - dublă numărare. Pastreaza o singură "
                "sursa: reclasifică în panoul D390 SAU introdu manual, nu ambele." % (_r3, ", ".join(_dbl_p)))
        R["R3_1"] = _r3
        R["R3_1_1"] = _r3                      # din care servicii IC (toata baza rd.3 e serviciu IC)
    # rd.7 colectat (primita tip S): R7_1/R7_2 + sub-rand rd.7.1 R7_1_1/R7_1_2, autolichidare la cota interna.
    # OGLINDA rd.20 deductibil: R20_1/R20_2 + R20_1_1/R20_1_2, net zero (DUK V_13-V_16: R20_x==R7_x, R20_1_x==R7_1_x).
    # rd.7/rd.20 sunt in allow-list-ul manual (colectata/deductibila) -> gard anti-dubla auto+manual, ca la rd.5/rd.18.
    _r7b = _int(ic_serv_b); _r7t = _int(ic_serv_t)
    if _r7b or _r7t:
        _dbl_s = sorted(k for k in ("R7_1", "R7_2", "R7_1_1", "R7_1_2",
                                    "R20_1", "R20_2", "R20_1_1", "R20_1_2") if k in manual)
        if _dbl_s:
            raise ValueError(
                "D300 achiziții servicii IC (rd.7 colectat + rd.20 deductibil, taxare inversa): derivate "
                "AUTOMAT din facturi primite din UE reclasificate serviciu (S) în D390 (baza=%d, TVA=%d) plus "
                "introduse manual (%s) - dublă numărare. Pastreaza o singură sursa." % (_r7b, _r7t, ", ".join(_dbl_s)))
        R["R7_1"] = _r7b; R["R7_2"] = _r7t         # colectat (rd.7)
        R["R7_1_1"] = _r7b; R["R7_1_2"] = _r7t     # din care servicii IC (rd.7.1)
        R["R20_1"] = _r7b; R["R20_2"] = _r7t       # deductibil (rd.20) - oglinda rd.7, net zero (DUK V_13/V_14)
        R["R20_1_1"] = _r7b; R["R20_1_2"] = _r7t   # din care servicii IC (rd.20.1) - oglinda rd.7.1 (DUK V_15/V_16)

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
            "D300: rânduri 'manual' neacceptate: %s. Un rând introdus de contabil care nu e în lista de "
            "rânduri de intrare valide trebuie să producă eroare vizibilă, NU să dispară tacut din decont "
            "(cauze: typo în numele randului; sau rând COMPUTAT care nu se setează manual - ex. R17/R27/R28/"
            "R32/R33/R34/R37/R40/R41/R42). Dacă e un rând de intrare legitim, adaugă-l în allow-list." % sorted(_necunoscute))

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
                "D300 rd.26 (achiziții scutite/neimpozabile): derivat AUTOMAT din achiziții cu cota 0%% "
                "(=%d) ȘI introdus manual (R26_1) - dublă numărare. Pastreaza o singură sursa." % _r26)
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
            "%d linii livrare cu cotă în afară 21/11/9 (bază %s lei, TVA %s lei) — TVA colectată NEDECLARATĂ "
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
            "%d linii achiziție cu cotă în afară 21/11/9 (bază %s lei, TVA %s lei) — deducere NEINCLUSĂ. "
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
            "nu e capturată, deci rd.12/rd.25 (colectat+deductibil) NU se pot derivă. Declar-o manual la "
            "R12/R25 sau completează cota (altfel taxarea inversă nu apare în decont)."
            % (len(achiz_331_0), _f(sum(achiz_331_0, Decimal(0)))))
    if ti_ben_n:
        res.note_rezultat.append(
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
    if foreign_pos:
        _fpb = sum((x[1] for x in foreign_pos), Decimal(0))
        _fpt = sum((x[2] for x in foreign_pos), Decimal(0))
        res.avertismente.append(
            "%d facturi cu partener străin (%s) dar cotă internă POZITIVĂ (bază %s lei, TVA %s lei) — "
            "probabil eroare: o operațiune IC/export nu poartă cotă internă. NU s-a inclus tacit în R9; "
            "corectează cota (0%%) sau țara partenerului."
            % (len(foreign_pos), ", ".join(sorted({x[0] for x in foreign_pos})), _f(_fpb), _f(_fpt)))
    if ic_livr_bunuri:
        res.avertismente.append(
            "Livrări intracomunitare de bunuri către UE (bază %s lei) — declarate la rd.1 (0%%, art.294 "
            "alin.2). Dacă sunt PRESTĂRI de servicii intracomunitare, reclasifică operațiunea ca serviciu "
            "în panoul D390 (sursă unică) — se mută automat la rd.3." % _f(ic_livr_bunuri))
    if export_livr:
        res.note_rezultat.append(
            "Livrări către partener non-UE (export, bază %s lei) — declarate la rd.14 (scutite cu drept "
            "de deducere)." % _f(export_livr))
    if ic_ach_n:
        res.avertismente.append(
            "%d achiziții intracomunitare de bunuri din UE (bază %s lei, TVA autolichidat %s lei la %d%%) — "
            "declarate la rd.5 colectat + rd.18 deductibil (taxare inversă, net zero). Dacă sunt SERVICII, "
            "reclasifică operațiunea ca serviciu în panoul D390 (sursă unică) — se mută automat la rd.7 "
            "colectat + rd.20 deductibil."
            % (ic_ach_n, _f(ic_ach_b), _f(ic_ach_t), cota_std_ic))
    # [F125] Servicii IC reclasificate prin SURSA UNICA D390 (MUTATE, nu adaugate).
    if ic_prest_serv:
        res.note_rezultat.append(
            "Prestări de servicii intracomunitare către UE (bază %s lei) — reclasificate ca serviciu (P) în "
            "D390, declarate la rd.3 + rd.3.1 (locul prestării în afară României, 0%%). Mutate din rd.1 "
            "(livrări de bunuri), nu adăugate — fără dublă numărare." % _f(ic_prest_serv))
    if ic_serv_n:
        res.note_rezultat.append(
            "%d achiziții de servicii intracomunitare din UE (bază %s lei, TVA autolichidat %s lei la %d%%) — "
            "reclasificate ca serviciu (S) în D390, declarate la rd.7 colectat + rd.7.1 + oglindă rd.20 "
            "deductibil + rd.20.1 (taxare inversă, net zero). Mutate din rd.5+rd.18, nu adăugate."
            % (ic_serv_n, _f(ic_serv_b), _f(ic_serv_t), cota_std_ic))
    if tr_reclas:
        # LIMITA DECLARATA (marker ASCII intern MARKER_TR_D300_NEACOPERIT): T/R nu e axa bun-serviciu;
        # maparea D300 pt triangulatie (T)/regularizari-regim (R) NU e acoperita de acest lot. Operatiunea
        # ramane rutata numeric (bunuri, rd.1) DAR se semnaleaza explicit - limita declarata, nu tacere.
        _tipuri_tr = ", ".join(sorted({t for _d, t in tr_reclas}))
        res.avertismente.append(
            "%d operațiuni reclasificate T/R (%s) în D390 — maparea D300 pentru triangulație (T) / regim "
            "special (R) NU e acoperită de acest lot: au rămas rutate numeric ca bunuri (rd.1). Verifică "
            "manual încadrarea în decont — limită declarată, nu omisiune tacită."
            % (len(tr_reclas), _tipuri_tr))
    res.note_rezultat.append("Rezultat TVA %s lei." % rez)
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
            erori.append("pro_rata invalid: %r \u2014 trebuie num\u0103r în [0,100]." % _pr)
        else:
            if not (0.0 <= _prv <= 100.0):
                erori.append("pro_rata în afară intervalului [0,100]: %s (structura ANAF pro_rata N(7.2))." % _prv)
    from core.firma_profil_api import erori_declarant as _ed   # [R101] sursa unica
    erori += _ed(prof)
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
        erori.append("tip_decont=T (trimestrial) cere luna în (02,03,05,06,08,09,11,12) (DUK regula R18).")
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
            lo = round((cota - 1) / 100 * b)  # round-ok: margine de verificare, nu suma persistata
            hi = round((cota + 1) / 100 * b)  # round-ok: margine de verificare
            if not (lo <= t <= hi):
                av.append("TVA %s (%d) nu se \u00eencadreaz\u0103 în %d%%\u00b11%% din baza %d (DUK: aten\u021bionare, uploadabil)."
                          % (tva_k, t, cota, b))
    marja("R9_1", "R9_2", cota_std)
    marja("R10_1", "R10_2", 11)
    marja("R11_1", "R11_2", 9)
    marja("R22_1", "R22_2", cota_std)
    return av


def _oglinda_r12_r25(res):
    """[Task4 CR-5/T8 10.08.2026] Cross-total: rd.12 (colectat, taxare inversa primita / masuri de
    simplificare art.331) TREBUIE oglindit integral de rd.25 (deductibil) -> net zero.

    Sursa oficiala (anaf_surse/d300_struct_anaf.txt): V_19 \"R25_1= R12_1\" (ERR: rd.25<>rd.12 col.1)
    si V_20 \"R25_2= R12_2\" (ERR: rd.25<>rd.12 col.2). Auto-derivarea din facturi cu flag taxare_inversa
    (calcul_d300) le seteaza deja egale; dar calea MANUALA poate pune R12 fara R25 (sau inegal/invers) ->
    colectat supra-declarat, net != 0, TVA de plata umflata. Validatorul DUK INSTALAT nu impune V19/V20
    (probat: R12 fara R25 = valid) si reconcilierea a-doua-cale SARE randurile manuale (limita 1) -> gard
    propriu, la aceeasi poarta ca reconcilierea, ridicat inainte de build_xml (iesire catre autoritati).
    Numeste AMBELE valori, nu repara tacit.
    """
    R = res.R
    r12_1 = R.get("R12_1", 0); r25_1 = R.get("R25_1", 0)
    r12_2 = R.get("R12_2", 0); r25_2 = R.get("R25_2", 0)
    if r12_1 != r25_1 or r12_2 != r25_2:
        raise ValueError(
            "D300 oglindă taxare inversa rd.12<->rd.25 (măsuri de simplificare): colectatul rd.12 trebuie "
            "oglindit integral de deductibilul rd.25 (net zero). R12_1=%d vs R25_1=%d (col.1); "
            "R12_2=%d vs R25_2=%d (col.2). DUK regula V19/V20 (neimpusă de validatorul instalat)."
            % (r12_1, r25_1, r12_2, r25_2))


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
    if not (prof.get("declarant_nume") and prof.get("declarant_functie")):
        res.avertismente.append("D300: declarantul (nume/funcție) lipsește din profil -> emis implicit "
                                "\"ADMINISTRATOR\". Completează declarantul în Date firma.")
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
        "AND " + _STATUS_FINAL + " "  # [B1] doar facturi contabilizabile
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


def _pull_taxare_inversa(cur, inceput, sfarsit):
    """Facturi cu taxare inversa EMISE in [inceput, sfarsit) pe faptul generator (emitere), cu linii.
    Folosit DOAR pe calea tva_la_incasare: _pull_incasare EXCLUDE taxarea inversa (art.282 alin.6 CF:
    exigibila la faptul generator, nu la incasare) - o aducem separat ca sa NU dispara tacit din decont
    (rd.13 pt emise / rd.12+rd.25 pt primite). Aceeasi forma de dict ca pull() normal."""
    cur.execute("SELECT f.id, f.directie, f.total, f.tva, "
                "COALESCE(f.taxare_inversa, false) AS taxare_inversa, f.categorie_331, "
                "COALESCE(f.tert_tara, 'RO') AS tert_tara, "
                "l.cantitate, l.pret_unitar, l.cota_tva "
                "FROM facturi f LEFT JOIN factura_linii l ON l.factura_id = f.id "
                "WHERE " + _EXIG_NORMAL + " >= %s AND " + _EXIG_NORMAL + " < %s "
                "AND " + _STATUS_FINAL + " "
                "AND COALESCE(f.taxare_inversa, false) = true ORDER BY f.id",
                (inceput, sfarsit))
    fmap = {}
    for r in cur.fetchall():
        f = fmap.setdefault(r["id"], {"directie": r["directie"],
                                      "taxare_inversa": r["taxare_inversa"],
                                      "categorie_331": r["categorie_331"],
                                      "tert_tara": r["tert_tara"],
                                      "total": r["total"] if r["total"] is not None else 0,
                                      "tva": r["tva"] if r["tva"] is not None else 0, "linii": []})
        if r["cantitate"] is not None and r["pret_unitar"] is not None:
            f["linii"].append((r["cantitate"], r["pret_unitar"], r["cota_tva"]))
    return list(fmap.values())


def _pull_furnizor_incasare(cur, inceput, sfarsit):
    """[B1 art.297 alin.2] Facturi PRIMITE de la furnizor care aplica TVA la incasare: deducerea se
    amana pana la PLATA (cont 401 decontat), CHIAR daca firma proprie e in regim normal. Aceeasi cale
    de decontare ca _pull_incasare (suma platita alocata pe cote), dar filtrata pe furnizor_tva_incasare.
    Marcheaza dict-urile cu exigibil_la_decontare=True ca sa fie tratate pe decontari in calcul_d300."""
    cur.execute(
        "SELECT i.factura_id AS fid, SUM(l.suma) AS settled "
        "FROM inregistrari i "
        "JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
        "JOIN facturi f ON f.id = i.factura_id "
        "WHERE i.status = 'validata' AND i.factura_id IS NOT NULL "
        "AND f.directie = 'primita' AND COALESCE(f.furnizor_tva_incasare, false) = true "
        "AND COALESCE(f.taxare_inversa, false) = false "
        "AND " + _STATUS_FINAL + " "
        "AND i.data >= %s AND i.data < %s AND l.cont_debit = '401' "
        "GROUP BY i.factura_id", (inceput, sfarsit))
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
        out.append({"directie": "primita", "decontari": dec, "exigibil_la_decontare": True})
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
            # nu pe emitere. Vezi _pull_incasare. EXCEPTIE: taxarea inversa e exigibila la faptul
            # generator (art.282 alin.6 CF), nu la incasare - _pull_incasare o EXCLUDE; o aducem pe
            # calea de emitere (_pull_taxare_inversa) ca sa NU dispara tacit (rd.13 / rd.12+rd.25).
            return prof, _pull_incasare(cur, inceput, sfarsit) + _pull_taxare_inversa(cur, inceput, sfarsit)
        cur.execute(
            "SELECT f.id, f.directie, f.total, f.tva, "
            "COALESCE(f.taxare_inversa, false) AS taxare_inversa, f.categorie_331, "
            "COALESCE(f.tert_tara, 'RO') AS tert_tara, f.tert_cui, "
            # [F125] LUNA de exigibilitate (aceeasi expresie pe care se face fereastra): cheia
            # reclasificarii D390 e per-luna (acelasi partener poate fi reclasificat diferit in luni
            # diferite - trimestru). Fara ea D300 nu poate potrivi factura pe luna corecta.
            + _EXIG_NORMAL + " AS exig, "
            "l.cantitate, l.pret_unitar, l.cota_tva "
            "FROM facturi f LEFT JOIN factura_linii l ON l.factura_id = f.id "
            # [B1] fereastra pe EXIGIBILITATE (COALESCE(data_faptului_generator, data_emitere); avans->emitere)
            "WHERE " + _EXIG_NORMAL + " >= %s AND " + _EXIG_NORMAL + " < %s "
            # [B1] doar facturi contabilizabile (exclude ciorna/de_preluat/descarcata/anulata/stornata)
            "AND " + _STATUS_FINAL + " "
            # [B1] deducere amanata (art.297 alin.2): primita de la furnizor la incasare -> exclusa din
            # calea de EMITERE, adusa separat pe calea de PLATA (_pull_furnizor_incasare)
            "AND NOT (f.directie = 'primita' AND COALESCE(f.furnizor_tva_incasare, false) = true) "
            "ORDER BY f.id",
            (inceput, sfarsit))
        rows = cur.fetchall()
        deferred = _pull_furnizor_incasare(cur, inceput, sfarsit)
    fmap = {}
    for r in rows:
        _exig = r.get("exig")
        f = fmap.setdefault(r["id"], {"directie": r["directie"],
                                      "taxare_inversa": r["taxare_inversa"],
                                      "categorie_331": r["categorie_331"],
                                      "tert_tara": r["tert_tara"],
                                      # [F125] CUI partener: cheia reclasificarii (directie,tara,cod) se
                                      # deriva din PREFIXUL CUI via d390._clasifica_partener, identic cu D390.
                                      "cui": (r.get("tert_cui") or "").strip(),
                                      # [F125] luna de exigibilitate (potrivirea reclasificarii per-luna)
                                      "an_exig": (_exig.year if _exig is not None else None),
                                      "luna_exig": (_exig.month if _exig is not None else None),
                                      "total": r["total"] if r["total"] is not None else 0,
                                      "tva": r["tva"] if r["tva"] is not None else 0, "linii": []})
        if r["cantitate"] is not None and r["pret_unitar"] is not None:
            f["linii"].append((r["cantitate"], r["pret_unitar"], r["cota_tva"]))
    return prof, list(fmap.values()) + deferred


def _incarca_reclasificari(conn, schema, prof, perioada):
    """[F125] SURSA UNICA partajata cu D390: incarca override-urile de tip (d390_reclasificare) pentru
    TOATE lunile din fereastra fiscala D300 (la trimestru: 3 luni) si le cheiaza per-luna
    {(an,luna,directie,tara,cod): tip}. NU dubleaza loaderul - refoloseste d390.pull_reclasificari
    (acelasi tabel scris de panoul D390). Mirror pe d390.calculeaza (incarca daca None)."""
    from core import d390 as _d390
    _inc, _sf = c.fereastra_tva(perioada, c.perioada_tva_tip(prof))
    out = {}
    _y, _m = _inc.year, _inc.month
    while (_y, _m) < (_sf.year, _sf.month):
        for (d, t, cod), tip in _d390.pull_reclasificari(conn, schema, _y, _m).items():
            out[(_y, _m, d, t, cod)] = tip
        _m += 1
        if _m > 12:
            _m = 1; _y += 1
    return out


def genereaza(conn, schema, perioada, manual=None, reclasificari=None):
    if perioada.luna is None or not (1 <= perioada.luna <= 12):
        raise ValueError("D300 lunar: luna invalidă: %r" % perioada.luna)
    prof, facturi = pull(conn, schema, perioada)
    # [F125] SURSA UNICA D390: daca nu s-a dat explicit, se incarca din d390_reclasificare (via
    # d390.pull_reclasificari) pentru lunile ferestrei D300 - ca D300 si D390 sa CITEASCA aceeasi
    # clasificare bun/serviciu (fara loader paralel). Param explicit are prioritate (preview/test).
    if reclasificari is None and conn is not None:
        reclasificari = _incarca_reclasificari(conn, schema, prof, perioada)
    # [B2/B3 10.08.2026] Randurile manuale PERSISTATE (tabel d300_manual) sunt sursa pe calea de
    # DEPUNERE: pas3 /coada regenereaza server-side FARA body.manual (manual=None). Le incarcam din
    # DB ca XML-ul de depunere sa fie IDENTIC cu preview-ul (paritate preview<->depunere). Cand
    # `manual` vine prin PARAM (preview programatic / test), param-ul are PRIORITATE integrala si NU
    # se combina cu DB (deterministic; frontendul NU trimite manual, deci ambele cai citesc din DB).
    if manual is None and conn is not None:
        from core import d300_manual_api as _dm
        manual = _dm.incarca_manual(conn, schema, perioada.an, perioada.luna)
    # POARTA (27.07.2026): profil incomplet -> STOP cu mesaj clar, nu XML respins de ANAF.
    erori = erori_generare(prof)
    if erori:
        raise ValueError("D300 nu se poate genera: " + " ".join(erori))
    res = calcul_d300(prof, perioada, facturi, manual, reclasificari)
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
    # [Task4 CR-5/T8] OGLINDA rd.12<->rd.25 (DUK V19/V20, neimpusa de validatorul instalat; reconcilierea
    # a-doua-cale sare randurile manuale) - poarta pe totaluri inainte de reconciliere si build_xml.
    _oglinda_r12_r25(res)
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
            _cur.execute("SELECT count(*) FROM facturi WHERE data_emitere >= %s AND data_emitere < %s "
                         "AND " + _nsf.clauza_sql(None),
                         (_inc.isoformat(), _sf.isoformat()))
            _nf = _cur.fetchone()[0]
        # [zero_base_v1 extins B1] Decont complet gol -> NU XML gol tacit: afirmatie EXPLICITA surfatata
        # (flag res.nula_asumata + mesaj). Acopera si cazul FARA nicio factura (un platitor depune nul pe
        # luna fara activitate) - depunerea NU se refuza, dar nulul e ASUMAT explicit.
        res.nula_asumata = True
        if _nf:
            res.avertismente.append(
                "DECLARAȚIE NULĂ ASUMATĂ: niciun rând declarat, dar există %d facturi contabilizabile (rezultat TVA zero) în "
                "perioadă (posibil necontabilizate sau TVA la încasare nedecontată) — confirmă că nu lipsesc date." % _nf)
        else:
            res.note_rezultat.append(
                "DECLARAȚIE NULĂ ASUMATĂ: nicio factură în perioadă şi niciun rând declarat. Un plătitor "
                "depune nul pe luna fără activitate — depunerea nu se refuză, dar nulul e afirmat explicit.")
    return _xml, res
