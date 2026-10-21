# -*- coding: utf-8 -*-
"""Decontari asociati (455/456/457/463) - motor PUR.
Surse: Legea 31/1990 art. 67 (dividende trimestriale), OMFP 3067/2018
(cont 463, pct. 423^1-423^2 OMFP 1802), impozit dividende 16% pentru
distribuiri incepand cu 01.01.2026 (Legea 141/2025; 10% anterior).
- dividende ANUALE: 1171=457 brut; impozit 457=446; plata net 457=5121;
- dividende INTERIMARE: 463=456 brut; impozit 456=446; plata net 456=5121;
  regularizare dupa aprobarea situatiilor anuale: 1171=457 + 457=463;
  exces (interimar > anual): NU se inregistreaza la regularizare; restituirea de la asociat (NETUL incasat) si
  impozitul recuperat de la buget se inregistreaza la INCASARE: 5121=463 (nota_restituire_dividend);
- imprumut DE LA asociat (4551): primire 5121=4551; restituire 4551=5121;
  dobanda 666=4551 + impozit 10% pe venitul din dobanda PF retinut 4551=446."""
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from core.common import nomenclator_cerut

B = Decimal("0.01")


def cota_dividend(la_data=None):
    """Cota impozit pe dividende (PROCENT), period-aware din common.COTE. Peticul 'if ref>=2026 else 10'
    (16/10) mutat in registru (PAS 0 versionare, regula 0a: eliminare, nu petic). Vezi common.COTE."""
    from core import common as _c
    q = _c.cota("impozit_dividend", la_data)[0] * 100
    # [lotul 10, deficiența 430e] „16.00%” în loc de 16%: cota se întoarce fără zecimale inutile (Decimal("16"), nu „16.00”)
    return q.quantize(Decimal(1), rounding=ROUND_HALF_UP) if q == q.to_integral_value() else q.normalize()


def procent_text(cota):
    """[lotul 10, deficiența 430e] Cota afișată contabilului: „16%”, nu „16.00%” (cota e procent, `cota_dividend`)."""
    q = Decimal(str(cota))
    q = q.quantize(Decimal(1), rounding=ROUND_HALF_UP) if q == q.to_integral_value() else q.normalize()
    return "%s%%" % str(q).replace(".", ",")


#: [lotul 10, deficiența 430b/431] refuzul fără asociați trimite unde se adaugă (comanda Costin: „mesajul de refuz trimite la ce lipsește”)
FARA_ASOCIATI = ("Firma nu are asociați înregistrați la data hotărârii: adaugă asociații și cotele lor în Date firmă → Asociați. "
                 "Nota de dividende împarte dividendul pe asociați, după cote (Legea 31/1990 art.67 alin.(2)).")


class StructuraAsociati(ValueError):
    """[lotul 10, deficiența 430b] Refuzul care se repară în Date firmă → Asociați (lipsă asociați, cote care nu însumează 100%)."""


def imparte_dividend(brut, structura, cota):
    """[lotul 10, deficiența 430b] Dividendul brut împărțit pe asociați, după structura valabilă la data hotărârii.

    Legea 31/1990 art.67 alin.(1): „Cota-parte din profit ce se plătește fiecărui asociat constituie dividend.” Alin.(2):
    „Dividendele se distribuie asociaților proporțional cu cota de participare la capitalul social vărsat [...] dacă prin actul
    constitutiv nu se prevede altfel.” Impozitul se calculează PE FIECARE asociat, din dividendul lui: CF art.97 alin.(7) —
    „Veniturile sub formă de dividende [...] se impozitează cu o cotă de 16% din suma acestora”, iar „Obligația calculării și
    reținerii impozitului [...] revine persoanelor juridice, odată cu plata dividendelor [...] de către acționari/asociați” —
    rotunjit aritmetic pe asociat (Decimal, ROUND_HALF_UP).

    `structura` = [(cnp, nume, cota_procent)] (`dividende_curs.structura_la`). Cotele trebuie să însumeze 100%: altfel o parte din
    dividend n-ar avea beneficiar. INTERPRETARE CU TEMEI (rotunjirea părților): partea fiecăruia se rotunjește la ban, iar
    diferența de rotunjire (cel mult un ban pe asociat) trece la asociatul cu cota cea mai mare, ca suma părților să fie exact
    dividendul aprobat de adunare; alternativa respinsă — părți care nu însumează dividendul aprobat (nota n-ar mai fi suma din
    hotărâre). De reconfirmat dacă apare o normă care tranșează.
    Întoarce [{cnp, nume, cota, brut, impozit, net}] (Decimal), în ordinea cotelor descrescătoare."""
    b = _d(brut)
    if b <= 0:
        raise ValueError("Dividendul brut trebuie să fie un număr pozitiv.")
    parti = sorted(((str(c or ""), n, Decimal(str(q))) for c, n, q in (structura or ()) if Decimal(str(q)) > 0),
                   key=lambda x: (-x[2], str(x[1] or "")))
    if not parti:
        raise StructuraAsociati(FARA_ASOCIATI)
    total = sum(q for _, _, q in parti)
    if total != 100:
        raise StructuraAsociati("Cotele asociaților valabile la data hotărârii însumează %s, nu 100%%: corectează structura în "
                         "Date firmă → Asociați, ca tot dividendul să aibă beneficiar (Legea 31/1990 art.67 alin.(2))."
                         % procent_text(total))
    sume = [(b * q / 100).quantize(B, rounding=ROUND_HALF_UP) for _, _, q in parti]
    sume[0] += b - sum(sume)
    out = []
    for (cnp, nume, q), s in zip(parti, sume):
        imp = _imp(s, cota)
        out.append({"cnp": cnp, "nume": nume, "cota": q, "brut": s, "impozit": imp, "net": s - imp})
    return out

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def _imp(brut, cota):
    return (_d(brut) * cota / 100).quantize(B, rounding=ROUND_HALF_UP)

def nota_dividend(brut, la_data=None, interimar=False, cu_plata=True, asociati=None, cont_sursa="1171"):
    """Repartizare + impozit + (optional) plata. Anual: <sursa>/457; interimar: 463/456.

    [lotul 10, deficiența 430] Cu `asociati` (structura de la data hotărârii), nota se împarte PE ASOCIAȚI (`imparte_dividend`):
    câte un rând <sursa> = 457, 457 = 446 [și 457 = 5121] pentru fiecare, cu impozitul calculat pe dividendul lui; `parti` poartă
    rândurile fiecăruia. `cont_sursa` = contul care ține profitul nerepartizat (1171 sau, preluat fără analitic, 117) — OMFP
    1802/2014, funcțiunea contului 457: „În creditul contului 457 [...] se înregistrează: – dividendele datorate
    acționarilor/asociaților din profitul realizat în exercițiile precedente (117).” Fără `asociati`: un singur rând pe fiecare cont
    (motorul de dinainte)."""
    b = _d(brut)
    if b <= 0:
        raise ValueError("Dividendul brut trebuie să fie un număr pozitiv.")
    cota = cota_dividend(la_data)
    sursa, dat = ("463", "456") if interimar else (cont_sursa, "457")

    def linii_pentru(s, imp):
        ln = [(sursa, dat, s), (dat, "446", imp)]
        if cu_plata:
            ln.append((dat, "5121", s - imp))
        return [x for x in ln if x[2] > 0]
    if asociati is not None:
        parti = imparte_dividend(b, asociati, cota)
        for p in parti:
            p["linii"] = linii_pentru(p["brut"], p["impozit"])
        imp = sum((p["impozit"] for p in parti), Decimal("0.00"))
        return {"linii": [l for p in parti for l in p["linii"]], "parti": parti, "impozit": imp, "net": b - imp,
                "cota": str(cota)}
    imp = _imp(b, cota)
    return {"linii": linii_pentru(b, imp), "impozit": imp, "net": b - imp, "cota": str(cota)}

def nota_regularizare_interimar(total_interimar, dividend_anual_aprobat, impozit_interimar=None):
    """Dupa aprobarea situatiilor anuale: 1171=457 anual + compensare 457=463 (OMFP 1802/2014 pct.423^2).

    [Lot 19 defect 9, 03.10.2026] Excesul (interimar > anual) NU mai intra in nota de regularizare. Inainte, nota
    purta 5121=463 la BRUT, datata la aprobare: o incasare care nu avusese loc, si mai mare decat cea posibila —
    asociatul a primit NETUL, deci restituie netul. OMFP 1802/2014, functiunea contului 463 (introdusa prin OMFP
    3067/2018): „În creditul contului 463 ... se înregistrează: – suma dividendelor repartizate în cursul exercițiului
    financiar și regularizate pe seama dividendelor anuale (457); – sumele încasate reprezentând restituiri de
    dividende datorate, conform legii (512, 531).” Deci: credit 463 din 512 la INCASARE, cu suma incasata.

    Impozitul aferent excesului se calculeaza din impozitul EFECTIV retinut pe interimare (`impozit_interimar`),
    proportional cu excesul — nu cu cota datei de regularizare (cota se schimba intre ani: 10% 2025, 16% 2026).
    INTERPRETARE CU TEMEI: impozitul ramane in debitul 463 pana il restituie bugetul (CPF art.170^1 alin.(1):
    declaratie de regularizare/cerere de restituire „după restituirea de către asociați”), iar la incasare se
    inchide tot cu 5121=463 — singura corespondenta creditoare a lui 463 in afara de 457. Alternativa respinsa:
    446=463 (functiunea lui 446 nu are aceasta corespondenta debitoare). De reconfirmat daca apare o norma care
    transeaza inregistrarea creantei asupra bugetului."""
    ti, da = _d(total_interimar), _d(dividend_anual_aprobat)
    if ti <= 0 or da < 0:
        raise ValueError("Una sau mai multe valori sunt invalide. Verifică sumele și cantitățile introduse.")
    linii = [("1171", "457", da)] if da > 0 else []
    compensat = min(ti, da)
    if compensat > 0:
        linii.append(("457", "463", compensat))
    exces = ti - da if ti > da else Decimal("0.00")
    rez = {"linii": linii, "compensat": compensat, "exces_de_restituit": exces,
           "impozit_de_recuperat": Decimal("0.00"), "net_de_restituit": Decimal("0.00")}
    if exces > 0:
        # FORMĂ: fara impozitul retinut nu se poate spune cat restituie asociatul (netul) si cat bugetul
        if impozit_interimar in (None, ""):
            raise ValueError("Dividendele interimare depășesc dividendul anual cu %s lei: scrie impozitul reținut pe "
                             "dividendele interimare, ca să se știe cât restituie asociatul (netul) și cât se "
                             "recuperează de la buget." % exces)
        imp = _d(impozit_interimar)
        if imp < 0 or imp > ti:   # FORMĂ: impozitul nu poate fi negativ sau mai mare decat dividendul
            raise ValueError("Impozitul reținut pe dividendele interimare (%s) trebuie să fie între 0 și totalul "
                             "dividendelor interimare (%s)." % (imp, ti))
        rez["impozit_de_recuperat"] = (imp * exces / ti).quantize(B, rounding=ROUND_HALF_UP)
        rez["net_de_restituit"] = exces - rez["impozit_de_recuperat"]
    return rez


def nota_restituire_dividend(suma):
    """Restituire de dividende interimare INCASATA (de la asociat — netul; sau impozitul, de la buget): 5121=463, la
    data incasarii. OMFP 1802/2014, functiunea contului 463: credit 463 cu „sumele încasate reprezentând restituiri
    de dividende datorate, conform legii (512, 531)”."""
    s = _d(suma)
    if s <= 0:   # FORMĂ: suma incasata
        raise ValueError("Suma încasată trebuie să fie un număr pozitiv.")
    return {"linii": [("5121", "463", s)]}

def nota_imprumut_asociat(suma, operatie="primire", dobanda=0,
                          impozit_dobanda_pct=10):
    """4551: primire 5121=4551; restituire 4551=5121 (+ dobanda 666=4551,
    impozit retinut 4551=446)."""
    s = _d(suma)
    if s < 0 or (s == 0 and not dobanda):
        raise ValueError("Suma trebuie să fie un număr pozitiv.")
    if operatie == "primire":
        return {"linii": [("5121", "4551", s)]}
    if operatie == "restituire":
        linii = []
        if s > 0:
            linii.append(("4551", "5121", s))
        d = _d(dobanda)
        if d > 0:
            imp = _imp(d, Decimal(str(impozit_dobanda_pct)))
            linii.append(("666", "4551", d))
            if imp > 0:
                linii.append(("4551", "446", imp))
            linii.append(("4551", "5121", d - imp))
        return {"linii": linii}
    raise ValueError(nomenclator_cerut("operatie", "primire|restituire"))
