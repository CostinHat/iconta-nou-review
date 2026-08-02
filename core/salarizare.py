"""
core/salarizare.py — calcul salariu brut→net + deduceri + monografie. Calcul PUR, fără DB.
Construit de la zero din Codul fiscal (art. 77, 78, 138, 156, 220^1) + OUG 156/2024.
Cotele (CAS/CASS/impozit/CAM, salariu minim, facilitate) vin din common cu DATĂ de valabilitate.

Conturi salarii (OMFP 1802):
  641 = 421 (brut) ; 421 = 4315 (CAS) ; 421 = 4316 (CASS) ; 421 = 444 (impozit)
  646 = 436 (CAM angajator) ; 421 = 5121 (plata net)
"""
from __future__ import annotations
from decimal import Decimal
from math import floor

from core import common as c
from core.common import _dec, _q

REGULI = "2026.1"
MODUL = "salarizare"

# deduceri (Cod fiscal art. 77)
# Deducere personala de baza — procent din salariul minim, dupa nr. persoanelor in
# intretinere (Cod fiscal art.77 alin.4). Cheia 4 = "4 sau mai multe persoane".
_PCT_DEDUCERE_BAZA = {
    0: Decimal("0.20"), 1: Decimal("0.25"), 2: Decimal("0.30"),
    3: Decimal("0.35"), 4: Decimal("0.45"),
}
PCT_TINERI = Decimal("0.15")                # +15% × salariu minim, tineri <26
DEDUCERE_COPIL_SCOALA = Decimal("100")      # +100 lei/copil la școală
PRAG_VENIT_DEDUCERE = Decimal("2000")       # plafon = salariu_minim + 2000


def _nota(debit, credit, suma, temei=None):
    n = {"debit": debit, "credit": credit, "suma": _q(suma),
         "modul": MODUL, "reguli": REGULI}
    if temei:
        n["temei"] = temei
    return n


# ============================================================
#  DEDUCERE PERSONALĂ (art. 77)
# ============================================================
def _deducere_personala_2018(brut, persoane=0, sub_26=False, copii_scoala=0,
                             functie_baza=True, *, la_data):
    """Întoarce {baza, tineri, copii, total} — sume scăzute din baza impozitului.

    la_data e OBLIGATORIU (keyword-only): deducerea depinde de salariul minim din LUNA de
    realizare a venitului (pliant ANAF). Fara el nu se ghiceste luna curenta - se ridica.

    TEMEI: CF art.77 alin.(4) (scara degresiva 20/25/30/35/45%, prag salariu minim+2000) + alin.(10) lit.a (deducere 100 lei/copil scolarizat). nivel_sursa: REDARE (scara 45% pt 4+ din redare secundara noulcodfiscal, nu MO).
    """
    if la_data is None:
        raise ValueError("deducere_personala: la_data (luna de salarizare) e obligatoriu; "
                         "nu se ghiceste luna curenta - salariul minim depinde de luna venitului")
    if not functie_baza:
        return {"baza": _q(0), "tineri": _q(0), "copii": _q(0), "total": _q(0)}
    sm, _ = c.cota("salariu_minim", la_data)
    b = _dec(brut)
    plafon = sm + PRAG_VENIT_DEDUCERE

    # — de bază —
    if b > plafon:
        ded_baza = Decimal(0)
    else:
        pct = _PCT_DEDUCERE_BAZA[min(persoane, 4)]
        if b > sm:
            trepte = floor((b - sm) / 50)
            pct = max(Decimal(0), pct - Decimal("0.005") * trepte)
        ded_baza = pct * sm

    # — suplimentar tineri <26 (doar limita superioara: brut <= sm+2000, art.77 alin.10 lit.a) —
    tineri = PCT_TINERI * sm if (sub_26 and b <= plafon) else Decimal(0)
    # — suplimentar copii la școală (indiferent de venit) —
    copii = DEDUCERE_COPIL_SCOALA * _dec(copii_scoala)

    total = ded_baza + tineri + copii
    # Suma deducerii NU se rotunjeste. Art.77 in vigoare nu prevede rotunjirea SUMEI; alin.(8) e
    # despre PERIOADA (deducere pe fiecare luna), nu despre valoare. Rotunjirea la 10 lei a fost
    # confirmata ABSENTA pe pliant ANAF + redarea textului codificat (runda 2 verificare la sursa).
    return {"baza": _q(ded_baza), "tineri": _q(tineri),
            "copii": _q(copii), "total": _q(total)}


# Variante DATATE ale deducerii personale (tiparul cota() pe cod). O singura versiune azi (CF art.77 in
# vigoare din 2018, fara schimbare reala de scara in istoric); o modificare viitoare se adauga ca intrare
# noua cu data_in, iar deducerea pe o luna trecuta ramane calculata cu regula de atunci.
_VARIANTE_DEDUCERE = [
    ("2018-01-01", _deducere_personala_2018,
     c.Temei("CF", art="77", alin="4", data_in="2018-01-01", nivel_sursa="REDARE",
             de_cine="Code/Costin", verificat_la="2026-07-31")),
]


def deducere_personala(brut, persoane=0, sub_26=False, copii_scoala=0, functie_baza=True, *, la_data):
    """Deducerea personala, DISPECER pe la_data (varianta de formula valabila la data venitului).
    TEMEI: CF art.77 alin.(4) (scara degresiva 20/25/30/35/45%, prag salariu minim+2000) + alin.(10) lit.a
    (deducere 100 lei/copil scolarizat). nivel_sursa: REDARE (scara 45% pt 4+ din redare secundara
    noulcodfiscal, nu MO). Versionata in timp: o schimbare de scara -> varianta datata noua, nu 'if data'."""
    if la_data is None:
        raise ValueError("deducere_personala: la_data (luna de salarizare) e obligatoriu; "
                         "nu se ghiceste luna curenta - salariul minim depinde de luna venitului")
    fn, _ = c.alege_varianta(_VARIANTE_DEDUCERE, la_data)
    return fn(brut, persoane, sub_26, copii_scoala, functie_baza, la_data=la_data)


# ============================================================
#  CALCUL SALARIU BRUT → NET
# ============================================================
def _calcul_salariu_2018(brut, persoane=0, sub_26=False, copii_scoala=0,
                   functie_baza=True, la_data=None,
                   norma_intreaga=True, venit_brut_total=None,
                   exceptat_suprataxare=False,
                   tichet_valoare=0, tichet_zile=0, tichet_vacanta=0, data_angajare=None, data_incetare=None,
                   facilitate_prorata=None, tichet_vacanta_exces=0):
    """Întoarce breakdown complet: facilitate, CAS, CASS, deducere, impozit, net, CAM, cost.

    Parametri noi (OUG 89/2025 art.III + art.146 Cod fiscal):
    - norma_intreaga: False pentru part-time. Afecteaza FACILITATEA (HG 146/2026
      o da doar la norma intreaga). NU afecteaza suprataxarea: art. 146(5^6) o
      cere pentru contract "cu norma intreaga SAU cu timp partial".
    - venit_brut_total: venit brut lunar contractual (default = brut), pt plafon facilitate
    - exceptat_suprataxare: elev/student <26, pensionar, multi-contract cu declarație

    TEMEI: CF art.77 (deducere personala), art.146 alin.(5^6)/(5^7) (contributia minima / exceptari
    suprataxare), OUG 89/2025 art.III (facilitate salariu minim); cotele CAS/CASS/impozit/CAM din
    common.COTE (CF art.138/156/78/220^1). nivel_sursa: REDARE.
    """
    b = _dec(brut)
    sm, temei_sm = c.cota("salariu_minim", la_data)
    cota_cas, _ = c.cota("cas", la_data)
    cota_cass, _ = c.cota("cass", la_data)
    cota_imp, _ = c.cota("impozit_venit", la_data)
    cota_cam, _ = c.cota("cam", la_data)
    facilitate_val, _ = c.cota("facilitate_salariu_minim", la_data)
    plafon_fac, _ = c.cota("plafon_facilitate_salariu_minim", la_data)

    # FACILITATE (OUG 89/2025 art.III) - conditii CUMULATIVE:
    #   (a) norma intreaga  (b) functie de baza  (c) salariul de baza CONTRACTUAL = salariul minim
    #   (d) venit brut total (fara tichete) <= plafon (4300 S1 / 4600 S2)
    # (c) se judeca pe brutul CONTRACTUAL (vbt), NU pe `brut` (= brut_lucrat la apelantii care
    # proratesc CM). OUG 156/2024 art.LXVI lit.a: "salariul de baza brut lunar STABILIT POTRIVIT
    # CONTRACTULUI ... EGAL cu ... salariul minim". Un salariat pe minim cu zile de CM are
    # brut_lucrat < sm dar contractual = sm -> pastreaza facilitatea INTREAGA (reparat 29.07; inainte
    # `b == sm` rula pe brut_lucrat si o pierdea complet pe orice luna cu CM).
    # ATENTIE daca se adauga SPORURI in model: (c) cere salariul de baza FARA sporuri, (d) cere
    # venitul brut TOTAL (cu sporuri). Azi coincid (o singura coloana salariu_brut, fara sporuri) ->
    # ambele pe vbt. Cu sporuri separate diverg: (c) ramane pe baza, (d) trece pe baza+sporuri, iar
    # venit_brut_total trebuie redefinit + un parametru nou pentru baza contractuala.
    vbt = _dec(venit_brut_total) if venit_brut_total is not None else b
    # PRORATA luna de ANGAJARE (zile lucrate / zile lucratoare din luna, fara sarbatori) - UN SINGUR loc,
    # folosita SI la facilitate SI la pragul de suprataxare. 1 daca nu e luna de angajare (contract activ tot).
    _prorata = Decimal(1)
    if la_data is not None:
        from datetime import date as _date
        import calendar as _cal
        from core import scadente as _scad
        def _pd(v):
            if v is None:
                return None
            if isinstance(v, _date):
                return v
            try:
                return _date.fromisoformat(str(v)[:10])
            except (ValueError, TypeError):
                return None
        _da, _di = _pd(data_angajare), _pd(data_incetare)
        _prima = _date(la_data.year, la_data.month, 1)
        _ultima = _date(la_data.year, la_data.month, _cal.monthrange(la_data.year, la_data.month)[1])
        # fereastra ACTIVA din luna: [max(prima, angajare), min(ultima, incetare)]. Prorata DOAR daca
        # contractul a fost activ o fractiune (angajare dupa prima zi SAU incetare inainte de ultima).
        _start = _da if (_da is not None and _da > _prima) else _prima
        _end = _di if (_di is not None and _di < _ultima) else _ultima
        if _start > _prima or _end < _ultima:
            _zl = _scad.zile_lucratoare_luna(la_data.year, la_data.month)
            _za = _scad.zile_lucratoare_interval(_start, _end)
            if _zl:
                _prorata = _dec(_za) / _dec(_zl)
    if facilitate_prorata is not None:
        # PASUL 2a (lit.a) - TEXT EXPLICIT (OUG 156/2024 art.LXVI alin.(4) lit.a): "suma de 300/200 lei SE
        # DIMINUEAZA in functie de perioada din luna in care salariul de baza este MENTINUT la nivelul
        # minim". Apelantul (fiscal) a calculat din salariu_istoric fractia de zile ACTIVE si LA MINIM ->
        # facilitate = facilitate_val x acea fractie. Inlocuieste si eligibilitatea (vbt==sm) si proratarea
        # pe fereastra activa (alin.4 lit.b/c/d): pe zilele la minim, minimul <= plafon automat. Norma
        # intreaga ramane conditie (HG 146/2026). Vezi core/salariu_istoric.py.
        facilitate = facilitate_val * _dec(facilitate_prorata) if (norma_intreaga and functie_baza) else Decimal(0)
    else:
        # Forma clasica (fara istoric): eligibilitate vbt==sm + proratare pe fereastra activa (alin.4
        # lit.b) angajare / lit.d) incetare). TEXT EXPLICIT (spre deosebire de prag - vezi baza_podea).
        facilitate = facilitate_val if (
            norma_intreaga and functie_baza and vbt == sm and vbt <= plafon_fac
        ) else Decimal(0)
        facilitate = facilitate * _prorata
    # [D3 02.08.2026] excesul de tichete de vacanta peste plafonul anual (6 sal.minime) = venit
    # SALARIAL integral (CAS+CASS+impozit), in BAZA de contributii - NU linie separata de tichet
    # (31.07: DUK respinge CAS pe exces ca linie separata via B4_7; baza recalc din salariu S731/S74).
    # Cele 3 scutiri sunt conditionate de aceeasi formula 'acordate potrivit legii' (OUG 8/2009 art.1)
    # -> peste plafon cad toate trei (varianta i, DECIZII 31.07). Plafonul (cumulat anual) se verifica
    # de apelant -> aici primim doar portiunea de EXCES a lunii.
    exces_vac = _dec(tichet_vacanta_exces) if _dec(tichet_vacanta_exces) > 0 else Decimal(0)
    # [D3 02.08] excesul intra in VENITUL BRUT impozabil (b_imp), declarat in D112 (S731) - regula DUK
    # S74 recalc B4 din brutul declarat. Atinge tot ce deriva din brut: deducere, CAM, contributii,
    # suprataxare. NET-ul ramane pe CASH (b), excesul e avantaj in natura (tichet), nu numerar.
    b_imp = b + exces_vac
    baza_contrib = b_imp - facilitate

    cas = baza_contrib * cota_cas
    cass = baza_contrib * cota_cass

    ded = deducere_personala(b_imp, persoane, sub_26, copii_scoala, functie_baza, la_data=la_data)

    baza_imp = baza_contrib - cas - cass - _dec(ded["total"])
    if baza_imp < 0:
        baza_imp = Decimal(0)

    # [F133] TICHETE DE MASA: CASS 10% + impozit 10% pe valoarea nominala; FARA CAS, FARA CAM,
    # FARA deducere personala (aceea e pe salariu). Contributia (CASS) e deductibila din baza
    # impozitului (regula Cod fiscal: impozit pe venit-contributii) -> impozit pe (nominal-cass).
    # Nr tichete = zile efectiv lucrate (0 fara pontaj - decis 20.07). Valoarea plafonata la
    # maximul legal (siguranta; inputul e deja validat 0..plafon in salariati_api).
    tichet_val, _ = c.cota("tichet_masa_plafon", la_data)
    tv = _dec(tichet_valoare)
    tv = min(tv, tichet_val) if tv > 0 else Decimal(0)
    tichete_nominal = tv * _dec(tichet_zile)                      # tichete de masa
    # [F133 Faza 2a] tichete de vacanta: suma one-off, ACELASI tratament fiscal ca masa
    # (CASS 10% + impozit 10%, fara CAS/CAM/deducere). Plafonul anual (6 sal.minime) se
    # verifica de apelant (are total_an); calculul taxeaza suma primita.
    tichete_vac = _dec(tichet_vacanta) if _dec(tichet_vacanta) > 0 else Decimal(0)
    bilete_taxabile = tichete_nominal + tichete_vac
    cass_tichete = bilete_taxabile * cota_cass
    baza_imp_tichete = bilete_taxabile - cass_tichete
    if baza_imp_tichete < 0:
        baza_imp_tichete = Decimal(0)
    impozit_tichete = baza_imp_tichete * cota_imp

    # impozitul returnat = TOTAL (salariu + tichete), ca sa fie corect pt net/monografie/D112
    impozit = baza_imp * cota_imp + impozit_tichete
    net = b - cas - cass - cass_tichete - impozit

    cam = b_imp * cota_cam

    # SUPRATAXARE SUB SALARIUL MINIM (art. 146 alin. (5^6) si art. 168 alin. (6^1)
    # Cod fiscal). Verificat la sursa 15.07.2026 (mfinante.gov.ro, text oficial):
    # "in baza unui contract individual de munca CU NORMA INTREAGA SAU CU TIMP PARTIAL
    # ... nu poate fi mai mica decat nivelul contributiei ... asupra salariului de baza
    # minim brut pe tara". CONDITIA LEGALA E VENITUL SUB MINIM, NU NORMA.
    # CORECTIE 15.07.2026: conditia cerea `not norma_intreaga` -> un salariat cu norma
    # intreaga si brut sub minim NU era suprataxat in statul de plata, dar ERA declarat
    # suprataxat in D112 (d112.pull:336 aplica pragul indiferent de norma). Doua cifre
    # diferite pentru acelasi salariat. Divergenta descoperita mecanic, prin control
    # incrucisat nota-vs-declaratie (salarii_contare.control_coerenta).
    # Exceptiile sunt cele de la alin. (5^7): elev/student <26, pensionar, multi-contract
    # cu declaratie pe propria raspundere -> parametrul exceptat_suprataxare.
    # norma_intreaga ramane conditie pentru FACILITATE (HG 146/2026 cere norma intreaga),
    # nu pentru suprataxare.
    # Pragul de suprataxare = nivelul de referinta DIMINUAT, proratat pe luna de angajare cu ACEEASI
    # _prorata ca facilitatea. TEMEI (verificat la sursa 29.07.2026): OUG 156/2024 art.LXVI alin.(5) =
    # OUG 89/2025 art.III - derogarea "NIVELUL... SE DIMINUEAZA cu 300 lei" REDEFINESTE nivelul (3750 in
    # S1 / 4125 in S2); OMF 1855/2022 pct.2 prorateaza "nivelul aferent zilelor lucrate" = nivelul DEJA
    # diminuat. OMF e din 2022, dinaintea facilitatii, si NU tranzeaza combinatia -> aleg B (nivelul
    # diminuat, proratat). Argument: alin.(4) prorateaza EXPLICIT facilitatea (vezi mai sus), alin.(5) doar
    # redefineste nivelul - daca voia 300 intregi peste un prag proratat, ar fi scris-o (ca la alin.4).
    # Alternativa A (sm intreg proratat, apoi 300 intreg) e mai putin fidela literei. De reconfirmat la o
    # norma/ghid ANAF explicit.
    # DIFERENTA DE TEMEI: pragul (alin.5) se prorateaza prin INTERPRETARE; facilitatea (alin.4 lit.b) prin
    # TEXT EXPLICIT. INCETAREA ramane nemodelata (data_incetare lipseste - vezi test_datorie).
    baza_podea = (sm - facilitate_val) * _prorata
    cas_suprataxa = Decimal(0)
    cass_suprataxa = Decimal(0)
    if (not exceptat_suprataxare) and baza_contrib < baza_podea:
        diferenta = baza_podea - baza_contrib
        cas_suprataxa = diferenta * cota_cas
        cass_suprataxa = diferenta * cota_cass

    return {
        "brut": _q(b_imp),   # [D3] gross impozabil (cu exces vacanta) - declarat in D112
        "facilitate": _q(facilitate),
        "cas": _q(cas),
        "cass": _q(cass),
        "deducere": ded,
        "baza_impozabila": _q(baza_imp),
        "impozit": _q(impozit),
        "net": _q(net),
        "cam": _q(cam),
        "cas_suprataxa": _q(cas_suprataxa),
        "cass_suprataxa": _q(cass_suprataxa),
        # [F133] tichete (0 daca nu primeste / fara pontaj). cass/impozit = pe masa + vacanta
        "tichete_nominal": _q(tichete_nominal),    # tichete de MASA (valoare x zile)
        "tichete_vacanta": _q(tichete_vac),        # tichete de VACANTA in plafon (one-off) - Faza 2a
        "tichete_vacanta_exces": _q(exces_vac),    # [D3] exces peste 6 sm -> venit salarial in baza
        "cass_tichete": _q(cass_tichete),          # CASS pe masa + vacanta (inclus in baza CASS D112)
        "impozit_tichete": _q(impozit_tichete),    # impozit pe masa + vacanta (inclus in "impozit")
        # angajatorul suporta valoarea nominala a biletelor (le cumpara) - cost real
        "cost_angajator": _q(b + cam + cas_suprataxa + cass_suprataxa + tichete_nominal + tichete_vac),
    }


# Formula brut->net (prorata + plafonare facilitate + suprataxare + split zi5-6 + tichete) e stabila azi;
# cotele CAS/CASS/impozit/CAM + salariul minim + facilitatea vin period-aware din COTE. O schimbare de
# ALGORITM (nu de cota) -> varianta datata noua, iar o adeverinta/rectificativa pe o luna trecuta o
# recalculeaza cu regula de ATUNCI (bugul campaniei). Azi o singura varianta: comportament neschimbat.
_VARIANTE_CALCUL_SALARIU = [
    ("2018-01-01", _calcul_salariu_2018,
     c.Temei("CF", art="78", data_in="2018-01-01", nivel_sursa="REDARE",
             de_cine="Code/Costin", verificat_la="2026-07-31",
             lant_acte="CF art.77 (deducere), art.146 alin.(5^6)/(5^7) (suprataxare), OUG 89/2025 art.III (facilitate)")),
]


def calcul_salariu(brut, persoane=0, sub_26=False, copii_scoala=0,
                   functie_baza=True, la_data=None,
                   norma_intreaga=True, venit_brut_total=None,
                   exceptat_suprataxare=False,
                   tichet_valoare=0, tichet_zile=0, tichet_vacanta=0, data_angajare=None, data_incetare=None,
                   facilitate_prorata=None, tichet_vacanta_exces=0):
    """Calcul salariu brut->net, DISPECER pe la_data (varianta de formula valabila la luna venitului).
    Dispecer subtire care forwardeaza toti parametrii catre varianta datata; NU duplica corpul.
    TEMEI: CF art.77 (deducere personala), art.146 alin.(5^6)/(5^7) (contributia minima / exceptari
    suprataxare), OUG 89/2025 art.III (facilitate salariu minim); cotele CAS/CASS/impozit/CAM din
    common.COTE (CF art.138/156/78/220^1). nivel_sursa: REDARE. Versionata in timp: o schimbare de
    ALGORITM -> varianta datata noua, nu 'if data' - trecutul (adeverinte/rectificative) ramane corect."""
    from datetime import date as _dt
    fn, _ = c.alege_varianta(_VARIANTE_CALCUL_SALARIU, la_data or _dt.today())
    return fn(brut, persoane=persoane, sub_26=sub_26, copii_scoala=copii_scoala,
              functie_baza=functie_baza, la_data=la_data, norma_intreaga=norma_intreaga,
              venit_brut_total=venit_brut_total, exceptat_suprataxare=exceptat_suprataxare,
              tichet_valoare=tichet_valoare, tichet_zile=tichet_zile, tichet_vacanta=tichet_vacanta,
              data_angajare=data_angajare, data_incetare=data_incetare, facilitate_prorata=facilitate_prorata,
              tichet_vacanta_exces=tichet_vacanta_exces)


# ============================================================
#  MONOGRAFIE SALARII — note cu urmă
# ============================================================
def monografie_salariu(calc):
    """Generează notele din rezultatul calcul_salariu."""
    # [F133] CASS retinut = salariu + tichete (tichetele intra in baza CASS); impozitul
    # returnat e deja TOTAL (salariu+tichete). Reteneri suportate din salariul cash (421).
    cass_total = _dec(calc["cass"]) + _dec(calc.get("cass_tichete", 0))
    note = [
        _nota("641", "421", calc["brut"]),       # cheltuială salarii brute
        _nota("421", "4315", calc["cas"]),        # CAS reținut (angajat)
        _nota("421", "4316", cass_total),         # CASS reținut (salariu + tichete)
        _nota("421", "444", calc["impozit"]),     # impozit pe venit (salariu + tichete)
        _nota("646", "436", calc["cam"]),         # CAM angajator
    ]
    # [F133] acordarea biletelor de valoare (masa + vacanta): cheltuiala (642) din biletele
    # de valoare (5328). Achizitia biletelor (5328=5121/401) e tranzactie separata.
    tichete_nom = _dec(calc.get("tichete_nominal", 0)) + _dec(calc.get("tichete_vacanta", 0))
    if tichete_nom > 0:
        note.append(_nota("642", "5328", tichete_nom))  # cheltuiala tichete (masa + vacanta) acordate
    # suprataxare part-time (art.146 Cod fiscal): diferența CAS/CASS suportată
    # de angajator peste venitul real, până la baza-podea (minim - facilitate)
    cas_supra = calc.get("cas_suprataxa", 0)
    cass_supra = calc.get("cass_suprataxa", 0)
    if _dec(cas_supra) > 0:
        note.append(_nota("6451", "4315", cas_supra))   # CAS suprataxa (cheltuială unitate)
    if _dec(cass_supra) > 0:
        note.append(_nota("6453", "4316", cass_supra))  # CASS suprataxa (cheltuială unitate)
    return note


def monografie_plata(net, cont_trezorerie="5121"):
    """421 = 5121/5311 (plata salariului net)."""
    return _nota("421", cont_trezorerie, net)

# ============================================================
#  CONCEDII MEDICALE — OUG 158/2005 + Legea 141/2025 + OUG 91/2025
#  + Ordinul 506/1030/2026 (diminuare 1 zi PER EPISOD, nu per certificat)
#  Verificat la sursa: legislatie.just.ro, MOF 507/19.06.2026
# ============================================================
def _procent_cm_l141_2025(cod, zile_episod, procent_accident=100):
    """Procent indemnizatie dupa cod (nomenclator Legea 125/2006, art. 17-31 OUG 158/2005).
    01=55/65/75 progresiv (Legea 141/2025); 02/03/04=80 sau 100 (FAAMBP, param);
    05/06/07/12/14/51=100 (07 carantina: art.20(3) OUG 158/2005, 100% permanent prin Legea 136/2020); 13/15=75; 08/09=85. Cod 10 (reducere timp munca) NU are
    procent - formula speciala art. 19 (diferenta venit, max 25% din baza) -> ValueError.
    TEMEI: OUG 158/2005 art.17(1) (progresiv 55/65/75, forma Legea 141/2025); art.20(3) + Legea 136/2020 (carantina 07=100%); art.25(1) (maternitate 08=85%); art.30(1) (ingrijire copil 09=85%). nivel_sursa: REDARE (OUG 158/2005 citita, verbatim necapturat)."""
    cod = str(cod or "01").zfill(2)
    if cod == "01":
        # OUG 158/2005 art.17(1) forma Legea 141/2025 (verbatim: anaf_surse/oug_158_2005_consolidat.html):
        # a) pana la 7 zile = 55%; b) intre 8 si 14 zile = 65%; c) "peste 15 zile" = 75%.
        if zile_episod <= 7: return Decimal("0.55")    # lit.a
        if zile_episod <= 14: return Decimal("0.65")   # lit.b
        # GOL DE REDACTARE: lit.b se opreste la 14, lit.c zice "peste 15" -> ziua 15 nu e acoperita
        # explicit de text. DECIZIE arhitect 02.08.2026: ziua 15 = 75% (favorabil asiguratului). Vezi
        # DECIZII.md (ziua 15) + GARZI.md. Gard: test_cm_ziua15_este_75pct.
        if zile_episod >= 15: return Decimal("0.75")   # lit.c + ziua 15 (decizie 02.08)
        return Decimal("0.75")                          # plasa (zile_episod >= 1)
    if cod == "10":
        raise ValueError("cod 10 (reducere timp munca): formula speciala art. 19 - "
                         "foloseste calcul_cm_cod10")
    if cod in ("02", "03", "04"):  # accidente munca/boala prof: 80% sau 100% (aviz ITM)
        return Decimal(str(procent_accident)) / 100
    if cod in ("05", "06", "07", "12", "14", "51"): return Decimal("1.00")  # infectocontagioase A/urgente/carantina/TBC/neoplazii-SIDA/izolare
    if cod in ("08", "09"): return Decimal("0.85")  # maternitate / ingrijire copil
    return Decimal("0.75")  # 13 cardiovasculare, 15 risc maternal, rest


# Progresivul 55/65/75 (cod 01) e forma Legea 141/2025; scala pre-141 nu e verificata la sursa -> daca
# difera, se adauga o varianta datata cu data_in = intrarea in vigoare a formei vechi (tiparul nu duplica
# logica, o dateaza). Azi o singura varianta: comportament identic pt orice data >= 2018 (fara regresie).
_VARIANTE_PROCENT_CM = [
    ("2018-01-01", _procent_cm_l141_2025,
     c.Temei("OUG", 158, 2005, art="17", data_in="2018-01-01", nivel_sursa="REDARE",
             de_cine="Code/Costin", verificat_la="2026-07-31",
             lant_acte="Legea 141/2025 (forma progresiva 55/65/75 cod 01); Legea 136/2020 (carantina 07=100%)")),
]


def procent_cm(cod, zile_episod, procent_accident=100, la_data=None):
    """Procent indemnizatie CM, DISPECER pe la_data (varianta de formula valabila la data certificatului).
    TEMEI: OUG 158/2005 art.17(1) (progresiv 55/65/75, forma Legea 141/2025); art.20(3)+Legea 136/2020
    (carantina 07=100%); art.25(1) (maternitate 08=85%); art.30(1) (ingrijire copil 09=85%). nivel_sursa:
    REDARE. Versionata in timp: o schimbare de scara -> varianta datata noua, nu 'if data' in corp."""
    from datetime import date as _dt
    fn, _ = c.alege_varianta(_VARIANTE_PROCENT_CM, la_data or _dt.today())
    return fn(cod, zile_episod, procent_accident)


def _calcul_cm_cod10_2018(baza_lunara, venit_realizat):
    """Cod 10 - reducere timp munca cu 1/4 (art. 19 OUG 158/2005):
    indemnizatia = baza de calcul - venitul realizat in noua situatie,
    plafonata la 25% din baza de calcul.
    TEMEI: OUG 158/2005 art.19 (reducere timp munca cod 10; plafon 25% din baza de calcul). nivel_sursa: REDARE."""
    b, v = _dec(baza_lunara), _dec(venit_realizat)
    if b <= 0 or v < 0:
        raise ValueError("baza/venit invalide")
    return _q(min(max(b - v, Decimal("0")), b * Decimal("0.25")))


_VARIANTE_CALCUL_CM_COD10 = [
    ("2018-01-01", _calcul_cm_cod10_2018,
     c.Temei("OUG", 158, 2005, art="19", data_in="2018-01-01", nivel_sursa="REDARE",
             de_cine="Code/Costin", verificat_la="2026-07-31")),
]


def calcul_cm_cod10(baza_lunara, venit_realizat, la_data=None):
    """Cod 10 (reducere timp munca), DISPECER pe la_data.
    TEMEI: OUG 158/2005 art.19 (reducere timp munca cod 10; plafon 25% din baza de calcul). nivel_sursa:
    REDARE. Versionata in timp: o schimbare de plafon -> varianta datata noua, nu 'if data' in corp."""
    from datetime import date as _dt
    fn, _ = c.alege_varianta(_VARIANTE_CALCUL_CM_COD10, la_data or _dt.today())
    return fn(baza_lunara, venit_realizat)

def _calcul_cm_core(venituri_6_luni, zile_lucratoare_6_luni, zile_lucratoare_cm,
                    cod="01", zile_episod=None, prima_zi_din_episod=True,
                    spitalizare=False, la_data=None, exceptat_prima_zi=False,
                    procent_accident=100, venituri_lunare=None, *, diminuare_activa):
    """
    Ci = Mzbci x procent x (NZLCM - diminuare)
    - Mzbci = suma venituri 6 luni / total zile lucratoare 6 luni
    - diminuare 1 zi: certificate 01.02.2026-31.12.2027, O DATA per episod,
      NU la spitalizare, accidente 02/03/04, izolare 51, maternitate 08, oncologic 17, risc maternal 15, PNS 12/13/14
    - rotunjire la leu (norme CNAS)
    TEMEI: OUG 158/2005 (indemnizatie CM: Ci = Mzbci x procent x zile); Ordinul 506/1030/2026
    (MOF 507/2026, diminuare 1 zi certificate 2026-2027); Norme OUG 158/2005 (angajatorul suporta
    zilele 2-6 = primele 5 zile platite, FNUASS din ziua 7). nivel_sursa: REDARE (OUG 158/2005 + Ordinul 506/1030/2026 MOF 507/2026).
    """
    # CM4 - PLAFON 12 salarii minime (OUG 158/2005 art.10 alin.(1), verdict 1 VERDE; OMS 15/2018
    # ART.61 + Exemplul nr.5, verdict 4 VERDE): fiecare venit LUNAR se capeaza la 12 x salariul minim
    # IN LUNA respectiva INAINTE de mediere. Regula "sm in luna" = BLOCAJ MOTIVAT (claim 5 GRI: norma
    # foloseste "an", nu "luna") -> GARZI.md. venituri_lunare = [(venit, zile, data_luna), ...];
    # cand lipseste, comportament vechi (fara plafon, apelanti pe suma).
    if venituri_lunare is not None:
        _suma = Decimal("0"); _zile = 0
        for _venit, _zl, _luna in venituri_lunare:
            _sm, _ = c.cota("salariu_minim", _luna)
            _suma += min(_dec(_venit), Decimal("12") * _dec(_sm))
            _zile += int(_zl)
        venituri_6_luni = _suma
        zile_lucratoare_6_luni = _zile
    mz = _dec(venituri_6_luni) / _dec(zile_lucratoare_6_luni or 1)
    ze = zile_episod if zile_episod is not None else zile_lucratoare_cm
    pct = procent_cm(cod, ze, procent_accident, la_data=la_data)
    diminuare = 0
    # Exceptii diminuare 1 zi verif. la sursa MOF 507/19.06.2026 (Ordinul 506/1030/2026):
    # accidente 02/03/04, izolare 51, maternitate 08, oncologic 17, risc maternal 15, PNS 12/13/14.
    # NU exceptate: urgente 06, carantina 07, boala obisnuita 01, ingrijire copil 09.
    if (diminuare_activa
            and prima_zi_din_episod and not spitalizare and not exceptat_prima_zi
            and str(cod).zfill(2) not in ("02", "03", "04", "08", "12", "13", "14", "15", "17", "51")):
        diminuare = 1
    zile_platite = max(zile_lucratoare_cm - diminuare, 0)
    brut = (mz * pct * zile_platite).quantize(Decimal("1"))  # rotunjit la leu
    # split angajator/FNUASS (Norme OUG 158/2005): angajatorul suporta zilele 2-6 ale
    # concediului = primele 5 zile lucratoare din cele PLATITE (prima zi diminuata e
    # neplatita, nu reduce plafonul de 5 al angajatorului); FNUASS suporta din ziua 7.
    # [D112 D-field] codurile 100% FNUASS nu au portie de angajator (D_20=0); restul: primele 5 zile angajator
    zile_ang = 0 if str(cod).zfill(2) in _CM_COD_FNUASS_INTEGRAL else min(zile_platite, 5)
    zile_fnuass = zile_platite - zile_ang
    brut_ang = (mz * pct * zile_ang).quantize(Decimal("1"))
    brut_fnuass = brut - brut_ang
    return {
        "media_zilnica": _q(mz), "procent": _q(pct * 100),
        "zile_platite": zile_platite, "diminuare": diminuare,
        "zile_ang": zile_ang, "zile_fnuass": zile_fnuass,
        "brut": _q(brut), "brut_ang": _q(brut_ang), "brut_fnuass": _q(brut_fnuass),
    }


def _calcul_cm_2018(*a, **k):
    return _calcul_cm_core(*a, diminuare_activa=False, **k)


def _calcul_cm_2026(*a, **k):
    return _calcul_cm_core(*a, diminuare_activa=True, **k)


def _calcul_cm_2028(*a, **k):
    return _calcul_cm_core(*a, diminuare_activa=False, **k)


# Diminuarea de 1 zi (Ordinul 506/1030/2026) e o regula pe FEREASTRA 01.02.2026-31.12.2027. Peticul
# "if 2026-02 <= ref <= 2027-12" convertit in 3 variante datate (tiparul cota() pe cod): fara diminuare
# pana la 02.2026, cu diminuare in fereastra, fara diminuare de la 2028 (regula expira) - frontierele de
# varianta sunt exact punctele de schimbare. Nimic hardcodat pe data in corp.
_VARIANTE_CALCUL_CM = [
    ("2018-01-01", _calcul_cm_2018, c.Temei("OUG", 158, 2005, nivel_sursa="REDARE", de_cine="Code/Costin", verificat_la="2026-07-31")),
    ("2026-02-01", _calcul_cm_2026, c.Temei("OUG", 158, 2005, nivel_sursa="REDARE", de_cine="Code/Costin", verificat_la="2026-07-31", lant_acte="Ordinul 506/1030/2026 (MOF 507/2026) introduce diminuarea de 1 zi, 01.02.2026-31.12.2027")),
    ("2028-01-01", _calcul_cm_2028, c.Temei("OUG", 158, 2005, nivel_sursa="REDARE", de_cine="Code/Costin", verificat_la="2026-07-31")),
]


def calcul_cm(venituri_6_luni, zile_lucratoare_6_luni, zile_lucratoare_cm,
              cod="01", zile_episod=None, prima_zi_din_episod=True,
              spitalizare=False, la_data=None, exceptat_prima_zi=False,
              procent_accident=100, venituri_lunare=None):
    """Indemnizatia de concediu medical, DISPECER pe la_data - alege varianta valabila la data
    certificatului (diminuarea de 1 zi doar in fereastra 01.02.2026-31.12.2027).
    TEMEI: OUG 158/2005 (indemnizatie CM: Ci = Mzbci x procent x zile); Ordinul 506/1030/2026 (MOF
    507/2026, diminuare 1 zi 2026-2027); Norme OUG 158/2005 (angajator zilele 2-6 = primele 5 platite,
    FNUASS din ziua 7). nivel_sursa: REDARE (OUG 158/2005 + Ordinul 506/1030/2026 MOF 507/2026)."""
    from datetime import date as _dt
    fn, _ = c.alege_varianta(_VARIANTE_CALCUL_CM, la_data or _dt.today())
    return fn(venituri_6_luni, zile_lucratoare_6_luni, zile_lucratoare_cm, cod, zile_episod,
              prima_zi_din_episod, spitalizare, la_data, exceptat_prima_zi, procent_accident,
              venituri_lunare=venituri_lunare)


# Coduri indemnizatie pt care NU se retine CASS (verif. la sursa: art.17(2) OUG 34/2024,
# aplicabil dupa 12.04.2024). CASS se retine DOAR pt 01 (boala obisnuita), 07 (carantina),
# 10 (reducere program). CAS 25% se retine UNIFORM pe indemnizatia CM (CF art.139(1)(o)+140). Impozit 10% mereu.
# Coduri 100% FNUASS (D112 spec, linia 5664: daca D_9 in (08,09,91,92,10,15,17) atunci D_20=0):
# angajatorul NU suporta primele 5 zile - toata indemnizatia din FNUASS. Maternitate/ingrijire/
# risc maternal/reducere program.
_CM_COD_FNUASS_INTEGRAL = ("08", "09", "10", "15", "17", "91", "92")
_CM_COD_CU_CASS = ("01", "07", "10")


def _taxe_cm_2018(brut, cod="01", la_data=None):
    """Retineri pe indemnizatia de concediu medical (OUG 158/2005 + Cod fiscal).
    - CAS 25% UNIFORM pe toate codurile (CF art.139(1)(o)+140; se aplica si maternitate/copil - ghid ANAF)
    - CASS 10% DOAR pentru codurile 01/07/10; scutit pentru rest (08 maternitate,
      15/16/17, 09 ingrijire copil, 05/06/51/91/92/12/13/14 etc.)
    - impozit 10% pe (brut - cass), fara deducere personala pe indemnizatie
    TEMEI: CF art.139(1)(o)+140 (CAS 25% pe indemnizatie); art.155(1) lit.i (CASS 10% cod 01/07/10); art.78 (impozit 10%). nivel_sursa: INTERPRETARE_OFICIALA (CAS 25% pe maternitate/copil = ghid ANAF, nu litera actului).
    Intoarce {cas, cass, impozit, net}."""
    from core import common as _c
    b = _dec(brut)
    cota_cas, _ = _c.cota("cas", la_data)
    cota_cass, _ = _c.cota("cass", la_data)
    cota_imp, _ = _c.cota("impozit_venit", la_data)
    cas = (b * cota_cas).quantize(Decimal("1"))   # CAS 25% UNIFORM pe toate codurile (CF art.139(1)(o)+140)
    cass = (b * cota_cass).quantize(Decimal("1")) if str(cod).zfill(2) in _CM_COD_CU_CASS else Decimal(0)
    impozit = ((b - cas - cass) * cota_imp).quantize(Decimal("1"))
    net = b - cas - cass - impozit
    return {"cas": _q(cas), "cass": _q(cass), "impozit": _q(impozit), "net": _q(net)}


_VARIANTE_TAXE_CM = [
    ("2018-01-01", _taxe_cm_2018,
     c.Temei("CF", art="139", alin="1", lit="o", data_in="2018-01-01", nivel_sursa="INTERPRETARE_OFICIALA",
             de_cine="Code/Costin", verificat_la="2026-07-31",
             lant_acte="OUG 34/2024 art.17(2) (CASS doar cod 01/07/10, dupa 12.04.2024)")),
]


def taxe_cm(brut, cod="01", la_data=None):
    """Retineri pe indemnizatia de concediu medical, DISPECER pe la_data.
    TEMEI: CF art.139(1)(o)+140 (CAS 25% pe indemnizatie); art.155(1) lit.i (CASS 10% cod 01/07/10);
    art.78 (impozit 10%). nivel_sursa: INTERPRETARE_OFICIALA (CAS 25% pe maternitate/copil = ghid ANAF,
    nu litera actului). Versionata in timp: o schimbare de regula -> varianta datata noua, nu 'if data'."""
    from datetime import date as _dt
    fn, _ = c.alege_varianta(_VARIANTE_TAXE_CM, la_data or _dt.today())
    return fn(brut, cod, la_data)
