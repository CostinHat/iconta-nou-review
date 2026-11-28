# -*- coding: utf-8 -*-
"""core/consultanta_fiscala.py — funcția 502 (lotul 17.5-F5): „Consultanță fiscală” pe firmă, cinci măsuri M1–M5, în ordinea fixă.

Comanda 17.5-F5 pct.8–15. Fiecare măsură are: numele, starea exactă („Se aplică”, „Nu se aplică” cu motivul demonstrat, „Lipsesc date” cu
lista precisă și locul completării, „Lipsesc date — temei neverificat” când valoarea legală nu e în registrul datat), suma în lei cu sensul
ei economic și perioada, pașii de calcul, ipotezele, condițiile și temeiul (act, articol, alineat, citat scurt verificat, data de aplicare).
Nimic nu se scrie: nici note, nici salarii, plăți, declarații, cereri D177, regim ori profil (toate citirile sunt pe o conexiune care se
închide cu rollback). Cotele și plafoanele vin numai din registrul datat (`core.common.cota`); calculele monetare din motoarele existente
(`salarizare.calcul_salariu`, `sponsorizari.credit_sponsorizare`, `d101.genereaza`), cu Decimal și ROUND_HALF_UP.

„Aplicația semnalează și calculează; decizia și consilierea clientului aparțin contabilului.”

Limitele v1 (în afara ferestrei): PFA, nerezidenți, IMCA, holding, căutarea generală a cheltuielilor deductibile omise.
"""
import datetime as _dt
from decimal import Decimal, ROUND_HALF_UP

from core import common as _c
from core.pdf_util import bani, data_ro

FRAZA = "Aplicația semnalează și calculează; decizia și consilierea clientului aparțin contabilului."
MASURI = (("M1", "Salariu sau dividende"), ("M2", "Beneficii pentru salariați"), ("M3", "Sponsorizări"), ("M4", "Plafonul micro"),
          ("M5", "Profit reinvestit"))
SE_APLICA, NU_SE_APLICA, LIPSESC, LIPSESC_TEMEI = "Se aplică", "Nu se aplică", "Lipsesc date", "Lipsesc date — temei neverificat"
STARI = (SE_APLICA, NU_SE_APLICA, LIPSESC, LIPSESC_TEMEI)
#: sensurile sumelor; numai „economie de impozit a firmei” se adună în rezumatul cabinetului (pct.8: nu se adună economii incompatibile)
SENS_ECONOMIE_FIRMA = "economie de impozit pentru firmă"
SENS_NET_ASOCIAT = "net în plus pentru asociat"
SENS_NET_SALARIATI = "net în plus pentru salariați, la același cost"
SENS_MARJA = "marjă până la plafon"
#: [17.5-F6, corecția 1 pct.5] M5 nu e «Se aplică»: suma e numai o estimare, cu condiția scrisă (nu intră în economia cabinetului)
SENS_ESTIMARE_M5 = "estimare a economiei de impozit, numai dacă activele sunt noi, din lista specială și puse în funcțiune"
B = Decimal("0.01")


def _q(x):
    return Decimal(str(x)).quantize(B, rounding=ROUND_HALF_UP)


def _lei(x):
    return bani(x) + " lei"


class _Temei(Exception):
    """Valoarea legală nu are temei în registru la data cerută."""


def _cota(nume, la):
    try:
        v, t = _c.cota(nume, la)
    except (ValueError, KeyError) as e:
        raise _Temei("%s la %s: %s" % (_c.ETICHETE_COTE.get(nume, nume) if hasattr(_c, "ETICHETE_COTE") else nume, data_ro(la), e))
    return Decimal(str(v)), t


def _masura(cod, stare, motiv=None, suma=None, sens=None, perioada="", valori=None, pasi=(), ipoteze=(), conditii=(), temei=(),
            lipsuri=(), ce_poti=""):
    nume = dict(MASURI)[cod]
    assert stare in STARI
    return {"cod": cod, "nume": nume, "stare": stare, "motiv": motiv, "suma": None if suma is None else str(_q(suma)), "sens": sens,
            "perioada": perioada, "valori": valori or {}, "pasi": list(pasi), "ipoteze": list(ipoteze), "conditii": list(conditii),
            "temei": [dict(zip(("act", "articol", "citat", "aplicare"), t)) for t in temei], "lipsuri": [dict(zip(("ce", "unde"), x)) for x in lipsuri],
            "ce_poti_face": ce_poti}


# ───────────────────────── citirile ─────────────────────────
def _unu(cur):
    r = cur.fetchone()
    if r is None:
        return None
    return list(r.values())[0] if isinstance(r, dict) else r[0]


def profil(cur, schema):
    cur.execute('SELECT nume, cui, regim_fiscal, tip_firma, forma_juridica, capital_subscris FROM "%s".firma_profil WHERE id = 1' % schema)
    r = cur.fetchone()
    return dict(r) if r else {}


def _evidenta_intreaga(cur, schema, an):
    """Evidența anului e întreagă în aplicație (soldurile preluate sunt la cel mult 31.12 al anului precedent)."""
    from core import bilant_api as _ba
    ref = _ba.data_soldurilor(cur, schema)
    return ref is None or ref < _dt.date(an, 1, 1), ref


def _rulaj(cur, schema, prefix, parte, an, pana_la):
    col_plus, col_minus = ("cont_credit", "cont_debit") if parte == "credit" else ("cont_debit", "cont_credit")
    cur.execute('SELECT COALESCE(sum(CASE WHEN l.%s LIKE %%s THEN l.suma ELSE 0 END), 0) - COALESCE(sum(CASE WHEN l.%s LIKE %%s THEN l.suma '
                'ELSE 0 END), 0) FROM "%s".inregistrari_linii l JOIN "%s".inregistrari i ON i.id = l.inregistrare_id WHERE i.status = '
                '\'validata\' AND i.data BETWEEN %%s AND %%s' % (col_plus, col_minus, schema, schema),
                (prefix + "%", prefix + "%", _dt.date(an, 1, 1), pana_la))
    return Decimal(str(_unu(cur) or 0))


def _asociati(cur, schema):
    cur.execute('SELECT nume, cnp, cota FROM "%s".asociati ORDER BY id' % schema)
    return [dict(r) for r in cur.fetchall()]


def _salariati_activi(cur, schema, la):
    cur.execute('SELECT s.id, s.nume, s.prenume, s.part_time, s.functie_baza, (SELECT h.salariu_brut FROM "%s".salariu_istoric h WHERE '
                'h.salariat_id = s.id AND h.valabil_din <= %%s ORDER BY h.valabil_din DESC LIMIT 1) AS brut FROM "%s".salariati s WHERE '
                's.data_angajare <= %%s AND (s.data_incetare IS NULL OR s.data_incetare >= %%s) ORDER BY s.id' % (schema, schema), (la, la, la))
    return [dict(r) for r in cur.fetchall()]


def _curs_eur(cur, zi):
    cur.execute("SELECT curs FROM public.curs_bnr_zilnic WHERE moneda = 'EUR' AND data = %s", (zi,))
    v = _unu(cur)
    return Decimal(str(v)) if v is not None else None


def _regim(p):
    r = (p.get("regim_fiscal") or "").strip().lower()
    return "micro" if r.startswith("micro") else "profit" if r.startswith("profit") else r


# ───────────────────────── M1 · salariu sau dividende ─────────────────────────
def _cass_dividende(venit, sm):
    """CASS pe veniturile din dividende (CF art. 170): baza = plafonul atins (6 / 12 / 24 de salarii minime), cota din registru."""
    for k in (24, 12, 6):
        if venit >= sm * k:
            return sm * k, k
    return Decimal("0"), 0


def m1(cur, schema, p, la):
    regim = _regim(p)
    tip = (p.get("tip_firma") or "").strip().lower()
    if not tip:
        return _masura("M1", LIPSESC, "Tipul firmei nu e completat: simularea privește asociații unui SRL.",
                       lipsuri=[("tipul firmei", "Date firmă → Profil")])
    if tip != "srl":
        return _masura("M1", NU_SE_APLICA, "Simularea privește asociații unui SRL; firma e «%s» (PFA și celelalte forme sunt în afara "
                       "acestei versiuni)." % tip)
    if regim not in ("micro", "profit"):
        return _masura("M1", NU_SE_APLICA, "Regimul fiscal al firmei («%s») nu e micro sau impozit pe profit." % (regim or "necompletat"))
    toti = [a for a in _asociati(cur, schema) if Decimal(str(a.get("cota") or 0)) > 0]
    if len(toti) > 1:
        # [17.5-F6, corecția 1 pct.4, decizia lui Costin 28.11.2026] simularea e pe un singur asociat: cu mai mulți asociați nu se arată o
        # sumă (împărțirea pe fiecare, pragurile CASS / D212 ale fiecăruia și salariul minim pe lună nu sunt calculate) — limita F6b
        return _masura("M1", LIPSESC, "Firma are %d asociați: aplicația face simularea salariu / dividende numai pentru un asociat unic. Cu mai "
                       "mulți asociați nu calculează partea fiecăruia, pragurile CASS și declarația unică (D212) ale fiecăruia și salariul "
                       "minim pe fiecare lună, deci nu arată o sumă. Fă simularea pentru fiecare asociat în afara aplicației." % len(toti),
                       lipsuri=[("simularea pentru fiecare asociat (pragurile CASS și D212, salariul minim pe fiecare lună)", "verificare manuală")])
    asoc = [a for a in toti if a.get("cnp")]
    if not asoc:
        return _masura("M1", LIPSESC, "Firma nu are asociați persoane fizice înregistrați: simularea salariu / dividende se face pe asociat. "
                       "Adaugă asociații și cotele lor în Date firmă → Asociați.", lipsuri=[("asociații persoane fizice, cu CNP și cotă",
                                                                                            "Date firmă → Asociați")])
    from core import salarizare as _s, hotarare_dividende as _hd, decontari_asociati as _da
    # [17.5-F6] regula de disponibilitate a funcției 501, una singură (`hotarare_dividende.profit_disponibil`): 117 / 1171 la zi minus
    # dividendele deja propuse în note nevalidate, inclusiv reclasificarea 117 = 1171
    disponibil = _hd.profit_disponibil(cur, schema, la)
    if disponibil is None or disponibil <= 0:
        return _masura("M1", LIPSESC, "Profitul disponibil pentru distribuire la %s nu e pozitiv în evidență (conturile 117 / 1171): "
                       "simularea pornește de la bugetul disponibil al firmei." % data_ro(la),
                       lipsuri=[("profitul nerepartizat (117 / 1171) la zi", "Registru jurnal (nota de închidere a anului) sau Import date → Solduri inițiale")])
    try:
        cota_div, t_div = _cota("impozit_dividend", la)
        sm, t_sm = _cota("salariu_minim", _dt.date(la.year, 1, 1))
        cass, _ = _cota("cass", la)
        cam, _ = _cota("cam", la)
    except _Temei as e:
        return _masura("M1", LIPSESC_TEMEI, "Valoare legală fără temei în registru: %s." % e)
    a = asoc[0]
    procent_asociat = Decimal(str(a["cota"]))
    buget = _q(disponibil * procent_asociat / 100)   # partea asociatului din distribuirea către toți asociații, conform propunerii 501 (proporțional)
    # varianta dividende
    imp_div = _q(buget * cota_div)
    net_div = buget - imp_div
    baza_cass, k = _cass_dividende(net_div, sm)
    cass_div = _q(baza_cass * cass)
    net_final_div = net_div - cass_div
    # varianta salariu: costul firmei = bugetul; brutul anual = buget / (1 + CAM), pe 12 luni
    brut_luna = _q(buget / (1 + cam) / 12)
    r = _s.calcul_salariu(brut_luna, la_data=la, cm_impozabil=None)
    net_sal = _q(Decimal(str(r["net"])) * 12)
    cost_sal = _q(Decimal(str(r["cost_angajator"])) * 12)
    # varianta mixtă: salariul minim + restul ca dividende
    r_min = _s.calcul_salariu(sm, la_data=la, cm_impozabil=None)
    cost_min = _q(Decimal(str(r_min["cost_angajator"])) * 12)
    variante = [("dividende", net_final_div, buget, imp_div + cass_div), ("salariu", net_sal, cost_sal, cost_sal - net_sal)]
    if buget >= cost_min:
        rest = buget - cost_min
        imp_r = _q(rest * cota_div)
        b2, _k2 = _cass_dividende(rest - imp_r, sm)
        net_mixt = _q(Decimal(str(r_min["net"])) * 12) + rest - imp_r - _q(b2 * cass)
        variante.append(("salariu minim + dividende", net_mixt, buget, buget - net_mixt))
    best = max(variante, key=lambda v: v[1])
    dif = best[1] - net_final_div
    # [17.5-F6, corecția 1 pct.6, C246] cota prin funcția de format a cotelor (`decontari_asociati.procent_text`): „60%”, nu „6E+1%”
    pasi = ["Bugetul asociatului %s: %s × %s = %s (profitul nerepartizat la %s, sursa: contul 117 / 1171)." % (
        a["nume"], _lei(disponibil), _da.procent_text(a["cota"]), _lei(buget), data_ro(la))]
    pasi += ["Varianta %s: net %s, taxe %s, cost firmă %s." % (n, _lei(net), _lei(tx), _lei(cost)) for n, net, cost, tx in variante]
    if buget < cost_min:
        pasi.append("Varianta salariu minim + dividende nu e fezabilă: costul anual al salariului minim (%s) depășește bugetul." % _lei(cost_min))
    return _masura("M1", SE_APLICA, suma=dif, sens=SENS_NET_ASOCIAT, perioada="anul %d" % la.year,
                   valori={"buget": str(buget), "varianta_maxima": best[0], "net_dividende": str(net_final_div)},
                   pasi=pasi,
                   ipoteze=["Asociatul nu are alte venituri extrasalariale (pentru pragurile CASS 6 / 12 / 24 de salarii minime, CF art. 170).",
                            "Bugetul vine din profitul deja impozitat (117 / 1171): impozitul pe profit nu se mai socotește a doua oară.",
                            "Salariul se simulează pe 12 luni, normă întreagă, funcție de bază, fără deduceri personale."],
                   conditii=["Asociatul poate deveni salariat (contract individual de muncă real, cu atribuții); un drept salarial deja "
                             "datorat nu se înlocuiește cu dividende.", "Distribuirea respectă profitul legal disponibil și cota asociatului (funcția 501)."],
                   temei=[("Codul fiscal", "art. 43, art. 97 alin. (7)", "cota impozitului pe dividende %s" % _c.cota("impozit_dividend", la)[1], "de la 01.01.2026"),
                          ("Codul fiscal", "art. 170", "CASS pe veniturile din dividende, plafoanele de 6, 12 și 24 de salarii minime", "anul %d" % la.year),
                          ("Codul fiscal", "art. 78, 138, 156, 220³", "impozitul pe salarii, CAS, CASS, CAM", "anul %d" % la.year)],
                   ce_poti="Discută cu asociatul varianta cu netul cel mai mare; decizia e a contabilului și a clientului.")


# ───────────────────────── M2 · beneficii pentru salariați ─────────────────────────
def m2(cur, schema, p, la):
    from core import salarizare as _s, scadente as _sc   # simulările nu au concediu medical în lună: cm_impozabil=None, explicit
    sal = _salariati_activi(cur, schema, la)
    if not sal:
        return _masura("M2", NU_SE_APLICA, "Firma nu are salariați activi la %s: beneficiile se acordă salariaților." % data_ro(la))
    try:
        plafon_t, t_tichet = _cota("tichet_masa_plafon", la)
        plafon_cadou, t_cadou = _cota("plafon_cadou_ocazie", la)
        cam, _ = _cota("cam", la)
    except _Temei as e:
        return _masura("M2", LIPSESC_TEMEI, "Valoare legală fără temei în registru: %s." % e)
    zile = _sc.zile_lucratoare_luna(la.year, la.month)
    fara_brut = [s for s in sal if s.get("brut") is None]
    if fara_brut:
        return _masura("M2", LIPSESC, "Salariul brut nu e completat la %s: efectul se calculează pe statul de plată al fiecărui salariat."
                       % ", ".join(("%s %s" % (s["nume"], s["prenume"] or "")).strip() for s in fara_brut),
                       lipsuri=[("salariul brut", "Salarizare → Salariați")])
    total, pasi = Decimal("0"), []
    for s in sal:
        brut = Decimal(str(s["brut"]))
        a = _s.calcul_salariu(brut, la_data=la, cm_impozabil=None, tichet_valoare=plafon_t, tichet_zile=zile)
        cost_a = Decimal(str(a["cost_angajator"]))
        b = _s.calcul_salariu(brut, la_data=la, cm_impozabil=None)
        # majorarea de brut la același cost pentru firmă: brutul crește cu valoarea tichetelor împărțită la (1 + CAM)
        brut_maj = _q(brut + (cost_a - Decimal(str(b["cost_angajator"]))) / (1 + cam))
        m = _s.calcul_salariu(brut_maj, la_data=la, cm_impozabil=None)
        net_a = Decimal(str(a["net"])) + Decimal(str(a["tichete_nominal"]))
        dif = net_a - Decimal(str(m["net"]))
        total += dif
        pasi.append("%s %s, %s: tichete %d × %s = %s; net în numerar %s + tichete %s, față de majorarea brutului la %s cu net %s; "
                    "diferență %s pe lună." % (s["nume"], s["prenume"] or "", data_ro(la), zile, _lei(plafon_t), _lei(a["tichete_nominal"]),
                                               _lei(a["net"]), _lei(a["tichete_nominal"]), _lei(brut_maj), _lei(m["net"]), _lei(dif)))
    pasi.append("Cadouri: %s pe persoană și ocazie (Paște, Crăciun și sărbători similare, 1 iunie pentru copiii minori, 8 martie pentru "
                "angajate) sunt neimpozabile și fără contribuții; depășirea se impune ca salariu." % _lei(plafon_cadou))
    return _masura("M2", SE_APLICA, suma=total * 12, sens=SENS_NET_SALARIATI, perioada="estimare anuală pe luna %02d/%d" % (la.month, la.year),
                   valori={"zile_lucratoare_luna": zile, "plafon_tichet": str(plafon_t), "plafon_cadou": str(plafon_cadou)},
                   pasi=pasi,
                   ipoteze=["Tichetele se acordă pentru toate zilele lucrătoare ale lunii (zilele efectiv lucrate pot fi mai puține).",
                            "Estimarea anuală = diferența lunii × 12.", "Voucherele de vacanță nu sunt calculate: plafonul lor nu e în registrul datat."],
                   conditii=["Tichetele și voucherele se acordă potrivit legii speciale și contractului / regulamentului intern.",
                             "Cadourile se acordă numai la ocaziile din Codul fiscal art. 76 alin. (4) lit. a)."],
                   temei=[("Codul fiscal", "art. 76 alin. (4) lit. a)", "cadourile ... nu depășește %s" % _lei(plafon_cadou), "regimul anului %d" % la.year),
                          ("Legea 165/2018, Legea 201/2025", "art. I", "tichet de masă cel mult %s (%s)" % (_lei(plafon_t), t_tichet), "de la 01.11.2025"),
                          ("Codul fiscal", "art. 76, 142, 157, 220⁴–220⁵", "tichetele: impozit și CASS, în afara bazelor CAS și CAM", "anul %d" % la.year)],
                   ce_poti="Compară cu clientul tichetele / cadourile cu o majorare de salariu la același cost.")


# ───────────────────────── M3 · sponsorizări ─────────────────────────
def _d101_an(conn, schema, an):
    """Rezultatul D101 al anului prin `d101.genereaza` (aceeași cale ca declarația): (impozit, cifra_afaceri) sau mesajul refuzului."""
    from core import d101 as _d1
    from core.common import Perioada
    try:
        _xml, res = _d1.genereaza(conn, schema, Perioada(an))
    except Exception as e:   # noqa: BLE001 — orice refuz al generatorului e o lipsă de date, spusă cu textul lui
        return None, str(e)
    return res, None


def m3(conn, cur, schema, p, la):
    regim = _regim(p)
    if regim == "micro":
        return _masura("M3", NU_SE_APLICA, "Microîntreprinderea nu mai poate scădea sponsorizarea din impozit începând cu 2024: art. 56 "
                       "alin. (1¹) din Codul fiscal a fost abrogat prin OUG 115/2023; ultimul an cu această facilitate este 2023. "
                       "Sponsorizarea rămâne doar cheltuială.",
                       temei=[("OUG 115/2023", "art. III (CF art. 56 alin. (1¹) abrogat)", "facilitatea micro pentru sponsorizare, eliminată", "de la 01.01.2024")])
    if regim != "profit":
        return _masura("M3", NU_SE_APLICA, "Regimul fiscal al firmei («%s») nu e impozit pe profit." % (regim or "necompletat"))
    from core import sponsorizari as _sp
    res, err = _d101_an(conn, schema, la.year)
    if res is None:
        return _masura("M3", LIPSESC, "Impozitul pe profit al anului %d nu se poate calcula din D101: %s" % (la.year, err),
                       lipsuri=[("rezultatul fiscal al anului (D101)", "Declarații → D101")])
    impozit = Decimal(str(res.P.get("P41", 0) or 0))
    intreg, _ = _evidenta_intreaga(cur, schema, la.year)
    if not intreg:
        return _masura("M3", LIPSESC, "Evidența anului %d nu e întreagă în aplicație (soldurile preluate sunt din cursul anului): cifra de "
                       "afaceri și impozitul anului nu se cunosc." % la.year, lipsuri=[("rulajele anului dinaintea preluării", "Import date → Balanță")])
    ca = _rulaj(cur, schema, "70", "credit", la.year, la)
    sp = _rulaj(cur, schema, "6582", "debit", la.year, la)
    if impozit <= 0:
        return _masura("M3", NU_SE_APLICA, "Fără impozit pe profit datorat în %d (D101 rd. 41 = 0): creditul de sponsorizare nu are din ce se scădea."
                       % la.year)
    r = _sp.credit_sponsorizare(ca, impozit, sp, la_data=la)
    ramas = Decimal(str(r["plafon"])) - Decimal(str(r["credit"]))
    stare = SE_APLICA if ramas > 0 else NU_SE_APLICA
    return _masura("M3", stare, None if stare == SE_APLICA else "Plafonul anului %d e consumat de sponsorizările deja înregistrate." % la.year,
                   suma=ramas, sens=SENS_ECONOMIE_FIRMA, perioada="anul %d, până la %s" % (la.year, data_ro(la)),
                   valori={"plafon": str(r["plafon"]), "credit": str(r["credit"]), "ramas": str(ramas), "cifra_afaceri": str(ca),
                           "impozit": str(impozit)},
                   pasi=["Plafon = min(0,75%% × %s; 20%% × %s) = %s." % (_lei(ca), _lei(impozit), _lei(r["plafon"])),
                         "Sponsorizări înregistrate (6582): %s; credit utilizat %s." % (_lei(sp), _lei(r["credit"])),
                         "Rămâne de folosit: %s (scade impozitul; ieșirea de bani prin sponsorizare e separată)." % _lei(ramas)],
                   conditii=["Beneficiarul entitate nonprofit / unitate de cult e înscris în Registrul entităților la data contractului.",
                             "Suma nefolosită se poate redirecționa prin D177 până la termenul D101 (OPANAF 3562/2024); redirecționarea nu "
                             "aduce economie suplimentară de numerar firmei."],
                   temei=[("Codul fiscal", "art. 25 alin. (4) lit. i)", "minimul dintre 0,75% din cifra de afaceri și 20% din impozitul pe profit datorat",
                           "forma în vigoare de la 01.01.2024"), ("OPANAF 3562/2024", "D177", "redirecționarea impozitului", "de la 2024")],
                   ce_poti="Propune clientului sponsorizarea până la plafon; nicio cerere nu se transmite din această fereastră.")


# ───────────────────────── M4 · plafonul micro ─────────────────────────
def m4(cur, schema, p, la):
    regim = _regim(p)
    if regim != "micro":
        return _masura("M4", NU_SE_APLICA, "Firma e plătitoare de impozit pe %s: plafonul veniturilor privește microîntreprinderile."
                       % ("profit" if regim == "profit" else "«%s»" % (regim or "necompletat")))
    an = la.year
    try:
        eur, t = _cota("plafon_micro_eur", _dt.date(an, 1, 1))
    except _Temei as e:
        return _masura("M4", LIPSESC_TEMEI, "Plafonul micro al anului %d nu are temei în registru: %s." % (an, e),
                       valori={"an": an})
    zi_curs = _dt.date(an - 1, 12, 31)
    curs = _curs_eur(cur, zi_curs)
    if curs is None:
        return _masura("M4", LIPSESC, "Lipsește cursul BNR EUR din %s (închiderea exercițiului precedent, CF art. 52 alin. (5)): echivalentul "
                       "în lei al plafonului nu se poate calcula." % data_ro(zi_curs), lipsuri=[("cursul BNR EUR din %s" % data_ro(zi_curs),
                                                                                             "Setări → Cursuri BNR (actualizarea cursurilor)")])
    plafon = _q(eur * curs)
    intreg, ref = _evidenta_intreaga(cur, schema, an)
    ca = _rulaj(cur, schema, "70", "credit", an, la)
    valori = {"plafon_eur": str(eur), "curs": str(curs), "plafon_lei": str(plafon), "an": an, "cifra_afaceri": str(ca),
              "marja": str(plafon - ca) if intreg else None}
    pasi = ["Plafonul anului %d: %s euro × %s (cursul BNR din %s) = %s." % (an, bani(eur), str(curs).replace(".", ","), data_ro(zi_curs), _lei(plafon))]
    conditii = ["Veniturile întreprinderilor legate (art. 47 alin. (1¹), art. 52 alin. (5¹)) se adună la plafon; nu sunt în aplicație.",
                "Transferurile de active din aceeași subgrupă și de terenuri (art. 54 alin. (1)) intră în baza plafonului la ieșirea în cursul anului.",
                "Celelalte condiții ale art. 47 (capital deținut, salariat, activități) rămân de verificat de contabil."]
    temei = [("Codul fiscal", "art. 52 alin. (1) și (5)", "venituri mai mari de 100.000 euro … cursul … la închiderea exercițiului financiar precedent",
              "de la 01.01.2026 (OUG 156/2024, OUG 89/2025, OUG 8/2026 art. 6)")]
    if not intreg:
        pasi.append("Veniturile din aplicație (cont 70x) de la preluare (%s) până la %s: %s." % (data_ro(ref), data_ro(la), _lei(ca)))
        return _masura("M4", LIPSESC, "Veniturile de la 01.01.%d până la preluarea în aplicație (%s) nu sunt în evidență, iar veniturile "
                       "întreprinderilor legate nu se pot introduce: marja până la plafon nu se poate calcula." % (an, data_ro(ref)),
                       perioada="plafonul anului %d" % an, valori=valori, pasi=pasi, conditii=conditii, temei=temei,
                       lipsuri=[("rulajele anului dinaintea preluării", "Import date → Balanță"), ("veniturile întreprinderilor legate", "verificare manuală")])
    marja = plafon - ca
    pasi.append("Cifra de afaceri contabilă (70x) de la 01.01.%d până la %s: %s; marja: %s." % (an, data_ro(la), _lei(ca), _lei(marja)))
    if marja < 0:
        tr = (la.month - 1) // 3 + 1
        pasi.append("Plafonul e depășit: impozitul pe profit se datorează din trimestrul în care s-a depășit (art. 52 alin. (1), (6)); "
                    "continuarea în micro nu mai e o opțiune legală.")
        valori["trimestru"] = tr
    return _masura("M4", LIPSESC, "Veniturile întreprinderilor legate nu sunt în aplicație: marja e calculată numai pe veniturile firmei.",
                   suma=marja, sens=SENS_MARJA, perioada="plafonul anului %d" % an, valori=valori, pasi=pasi, conditii=conditii, temei=temei,
                   lipsuri=[("veniturile întreprinderilor legate", "verificare manuală")])


# ───────────────────────── M5 · profit reinvestit ─────────────────────────
#: subgrupa 2.1 și clasa 2.2.9 din Catalogul HG 2139/2004 (CF art. 22 alin. (1)); programele informatice se judecă pe cont (208)
_ELIGIBIL = ("2.1.", "2.2.9")


def m5(conn, cur, schema, p, la):
    regim = _regim(p)
    if regim == "micro":
        return _masura("M5", NU_SE_APLICA, "Scutirea profitului reinvestit (CF art. 22) se aplică plătitorilor de impozit pe profit; firma e "
                       "microîntreprindere.", temei=[("Codul fiscal", "art. 22 alin. (1)", "profitul investit … este scutit de impozit",
                                                      "contribuabilii plătitori de impozit pe profit")])
    if regim != "profit":
        return _masura("M5", NU_SE_APLICA, "Regimul fiscal al firmei («%s») nu e impozit pe profit." % (regim or "necompletat"))
    cur.execute('SELECT denumire, cod_catalog, valoare, data_pif, cont_imobilizare FROM "%s".mijloace_fixe WHERE data_pif BETWEEN %%s AND %%s '
                'ORDER BY data_pif' % schema, (_dt.date(la.year, 1, 1), la))
    mf = [dict(r) for r in cur.fetchall()]
    elig = [m for m in mf if str(m.get("cod_catalog") or "").startswith(_ELIGIBIL) or str(m.get("cont_imobilizare") or "").startswith("208")]
    if not elig:
        return _masura("M5", NU_SE_APLICA, "Niciun activ din subgrupa 2.1, clasa 2.2.9 sau program informatic nu a fost pus în funcțiune în "
                       "%d până la %s (registrul mijloacelor fixe)." % (la.year, data_ro(la)),
                       ipoteze=["Un cod din catalog sau un cont singure nu confirmă eligibilitatea; activele second-hand nu sunt eligibile."])
    res, err = _d101_an(conn, schema, la.year)
    if res is None:
        return _masura("M5", LIPSESC, "Profitul contabil și impozitul anului %d nu se pot calcula din D101: %s" % (la.year, err),
                       lipsuri=[("rezultatul anului (D101)", "Declarații → D101")])
    try:
        cota, _ = _cota("impozit_profit", la)
    except _Temei as e:
        return _masura("M5", LIPSESC_TEMEI, "Valoare legală fără temei în registru: %s." % e)
    from core import decontari_asociati as _da
    investit = sum((Decimal(str(m["valoare"])) for m in elig), Decimal("0"))
    profit = max(Decimal(str(res.P.get("P38a", 0) or res.P.get("P38", 0) or 0)), Decimal("0"))
    scutit = min(investit, profit)
    impozit_ec = _q(scutit * cota)
    # [17.5-F6, corecția 1 pct.5, decizia lui Costin 28.11.2026] aplicația nu știe dacă activele sunt noi (nu second-hand), din lista specială
    # și puse în funcțiune: M5 nu e «Se aplică», ci «Lipsesc date», iar suma apare numai ca estimare, cu condiția scrisă (sensul
    # SENS_ESTIMARE_M5 nu intră în economia compatibilă a cabinetului) — limita F6b
    estimare = impozit_ec > 0
    return _masura("M5", LIPSESC if estimare else NU_SE_APLICA,
                   ("Aplicația nu știe dacă activele sunt noi (nu second-hand), din lista specială a echipamentelor tehnologice și puse în "
                    "funcțiune: suma de mai jos e numai o estimare, valabilă dacă activele îndeplinesc toate aceste condiții.") if estimare
                   else "Fără profit impozabil în %d: scutirea nu economisește impozit." % la.year,
                   suma=impozit_ec, sens=SENS_ESTIMARE_M5 if estimare else SENS_ECONOMIE_FIRMA,
                   perioada="anul %d, până la %s" % (la.year, data_ro(la)),
                   valori={"investit": str(investit), "profit": str(profit), "scutit": str(scutit)},
                   pasi=["Active puse în funcțiune: %s (%s)." % (", ".join(m["denumire"] for m in elig), _lei(investit)),
                         # [17.5-F6, corecția 1 pct.6, C247] cota prin funcția de format a cotelor: „16%”, nu „0.16”
                         "Profit scutit = min(investiția, profitul) = %s; impozit economisit estimat = %s × %s." % (
                             _lei(scutit), _lei(scutit), _da.procent_text(cota * 100))],
                   lipsuri=[("activele sunt noi (nu second-hand), din lista specială a echipamentelor tehnologice și puse în funcțiune",
                             "verificare manuală (documentele de achiziție și procesul-verbal de punere în funcțiune)")] if estimare else [],
                   conditii=["Activele sunt noi, puse în funcțiune și folosite în activitatea economică; se păstrează cel puțin durata legală.",
                             "Profitul scutit se repartizează la rezerve; în 2026 rezervele au restricțiile art. 26 alin. (9¹).",
                             "Amortizarea accelerată e permisă; amortizarea super-accelerată (art. 22 alin. (9)) e o excepție distinctă."],
                   temei=[("Codul fiscal", "art. 22", "profitul investit în echipamente tehnologice … este scutit de impozit", "anul %d" % la.year)],
                   ce_poti="Verifică cu clientul dovezile punerii în funcțiune și rezerva.")


# ───────────────────────── fereastra ─────────────────────────
def masuri(conn, schema, la=None):
    """Cele cinci măsuri, în ordinea M1–M5, pentru firma din `schema`, la data `la` (implicit azi). Numai citiri."""
    import psycopg2.extras as _E
    la = la or _dt.date.today()
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute('SET LOCAL search_path TO "%s", public' % schema)
        pr = profil(cur, schema)
        out = [m1(cur, schema, pr, la), m2(cur, schema, pr, la), m3(conn, cur, schema, pr, la), m4(cur, schema, pr, la), m5(conn, cur, schema, pr, la)]
    conn.rollback()
    return {"firma": {"nume": pr.get("nume"), "cui": pr.get("cui"), "regim": _regim(pr)}, "data": la.isoformat(), "an": la.year,
            "masuri": out, "fraza": FRAZA}


def economie_compatibila(rez):
    """Suma economiilor compatibile (numai „economie de impozit pentru firmă”, M3 și M5, din măsurile „Se aplică”) — rezumatul cabinetului."""
    return sum((Decimal(m["suma"]) for m in rez["masuri"] if m["stare"] == SE_APLICA and m["sens"] == SENS_ECONOMIE_FIRMA and m["suma"]),
               Decimal("0"))


def rezumat_cabinet(conn, schema, la=None):
    """[17.5-F6, Cabinet 3 b)] Rezumatul pe firmă al funcției 502 pentru secțiunea «Consultanță» a cabinetului: firma intră în lista
    «Consultanță fiscală» când are cel puțin o măsură în starea «Se aplică». Economia arătată adună numai economiile compatibile
    (`economie_compatibila`: economie de impozit a firmei, M3 și M5); măsurile «Lipsesc date» se arată cu starea lor. Firmele în partidă
    simplă (PFA) sunt în afara v1, ca în meniul firmei (cardul are regimul «dubla»). Numai citiri."""
    from core import migrare_api as _ma
    r = masuri(conn, schema, la)
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        pr = profil(cur, schema)
    conn.rollback()
    if _ma.regim_contabil(pr.get("tip_firma")) != "dubla":
        return {"eligibil": False, "motiv": "partidă simplă (PFA) — în afara v1", "data": r["data"], "se_aplica": [], "lipsesc": [],
                "economie": "0.00"}
    se = [{"cod": m["cod"], "nume": m["nume"], "suma": m["suma"], "sens": m["sens"]} for m in r["masuri"] if m["stare"] == SE_APLICA]
    lips = [{"cod": m["cod"], "nume": m["nume"], "stare": m["stare"]} for m in r["masuri"] if m["stare"] in (LIPSESC, LIPSESC_TEMEI)]
    return {"eligibil": bool(se), "motiv": None if se else "nicio măsură în starea «Se aplică»", "data": r["data"], "se_aplica": se,
            "lipsesc": lips, "economie": str(_q(economie_compatibila(r)))}
