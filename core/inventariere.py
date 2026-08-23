# -*- coding: utf-8 -*-
"""Inventariere anuala - motor PUR (OMFP 2861/2009 + OMFP 1802 + art. 304 CF).
Rezultatele inventarierii (dupa compensari plus/minus sortimente confundabile
si perisabilitati legale):
- PLUS la inventar: stocuri 3xx = 60x corespondent (371=607, 301=601,
  345=711 produse); mijloace fixe 21x = 4754 (subventii asimilate);
- MINUS NEIMPUTABIL: 60x = 3xx; daca neasigurat si nedovedit distrus ->
  ajustare TVA 635 = 4426 (art. 304);
- MINUS IMPUTABIL: 60x = 3xx + imputare persoanei vinovate la valoarea de
  inlocuire: 4282 = 7581 + 4427 (salariat) / 461 = 7581 + 4427 (tert);
- CASARE MF (comisie, proces-verbal): % = 21x: 28xx amortizarea cumulata +
  6583 valoarea neamortizata (deductibila daca valorificata/dezmembrata)."""
from decimal import Decimal, ROUND_HALF_UP

B = Decimal("0.01")
CORESPONDENT = {"371": "607", "301": "601", "302": "602", "303": "603",
                "345": "711", "381": "608"}

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def nota_plus(valoare, cont_stoc="371"):
    v = _d(valoare)
    if v <= 0:
        raise ValueError("Valoarea introdusă e invalidă (trebuie un număr pozitiv).")
    c = CORESPONDENT.get(str(cont_stoc))
    if not c:
        raise ValueError("cont stoc: " + "|".join(CORESPONDENT))
    return {"linii": [(str(cont_stoc), c, v)]}

def nota_plus_mf(valoare, cont_imobilizare="2131"):
    v = _d(valoare)
    if v <= 0:
        raise ValueError("Valoarea introdusă e invalidă (trebuie un număr pozitiv).")
    return {"linii": [(str(cont_imobilizare), "4754", v)]}


def pregateste_mf_plus(corp):
    """[ruptura mijloc-fix post-migrare 14.08.2026] Valideaza si normalizeaza un mijloc fix corporal
    adaugat prin 'Plus la inventar', ca sa fie inscris in registrul mijloace_fixe. Altfel nota 21x=4754
    nu ajunge la amortizare/D406 (activul e invizibil pentru tenant_amortizare si /d406-active). Refuza
    (ValueError) metoda pe care legea NU o permite pe categoria activului (CF art.28 alin.5/8^1),
    reutilizand gardul din d406_active. dnf_luni si data punerii in functiune sunt obligatorii (fara ele
    activul nu se poate amortiza)."""
    from datetime import date as _date
    from core import d406_active as _d406a
    v = _d(corp.get("valoare") or 0)
    if v <= 0:
        raise ValueError("Valoarea mijlocului fix trebuie sa fie un numar pozitiv.")
    try:
        dnf = int(corp.get("dnf_luni"))
    except (TypeError, ValueError):
        dnf = 0
    if dnf <= 0:
        raise ValueError("Durata normala de functionare (luni) e obligatorie pentru amortizare.")
    data_pif = corp.get("data_pif") or corp.get("data")
    if not data_pif:
        raise ValueError("Data punerii in functiune e obligatorie.")
    pif = data_pif if hasattr(data_pif, "year") else _date.fromisoformat(str(data_pif))
    cont_imo = str(corp.get("cont_imobilizare") or "2131")
    metoda = _d406a._norm_metoda(corp.get("metoda") or "liniara")
    _d406a._verifica_categorie({"cod": corp.get("cod"), "cont_imobilizare": cont_imo}, metoda, pif)
    return {"cod": corp.get("cod") or "MF-PLUS",
            "denumire": (corp.get("denumire") or corp.get("descriere") or "Mijloc fix (plus inventar)")[:200],
            "cont_imobilizare": cont_imo,
            "cont_amortizare": str(corp.get("cont_amortizare") or "2813"),
            "valoare": v, "rezidual": _d(corp.get("rezidual") or 0),
            "dnf_luni": dnf, "data_pif": pif, "metoda": metoda}


def nota_minus(valoare, cont_stoc="371", imputabil=False,
               valoare_imputare=None, vinovat="salariat",
               cota_tva=None, asigurat_sau_distrus=False):
    """Minus: descarcare 60x=3xx; imputabil -> imputare la valoarea de
    inlocuire cu TVA; neimputabil neasigurat -> ajustare TVA pe cost."""
    if cota_tva is None:
        raise ValueError("Cota de TVA nu s-a dat. Nu se folosește o valoare implicită: o cotă scrisă în cod se rupe tăcut de lege la prima schimbare, iar o operațiune veche are altă cotă decât una de azi. Declară cota operațiunii.")
    v = _d(valoare)
    if v <= 0:
        raise ValueError("Valoarea introdusă e invalidă (trebuie un număr pozitiv).")
    c = CORESPONDENT.get(str(cont_stoc))
    if not c:
        raise ValueError("cont stoc: " + "|".join(CORESPONDENT))
    linii = [(c, str(cont_stoc), v)]
    if imputabil:
        vi = _d(valoare_imputare if valoare_imputare is not None else v)
        tva = (vi * Decimal(str(cota_tva)) / 100).quantize(B, rounding=ROUND_HALF_UP)
        cont_crt = "4282" if vinovat == "salariat" else "461"
        linii.append((cont_crt, "7581", vi))
        if tva > 0:
            linii.append((cont_crt, "4427", tva))
    elif not asigurat_sau_distrus:
        tva = (v * Decimal(str(cota_tva)) / 100).quantize(B, rounding=ROUND_HALF_UP)
        if tva > 0:
            linii.append(("635", "4426", tva))  # ajustare art. 304
    return {"linii": linii}

def nota_casare_mf(valoare_bruta, amortizare_cumulata,
                   cont_imobilizare="2131", cont_amortizare="2813"):
    """Casare: 28xx + 6583 = 21x (proces-verbal comisie)."""
    vb, am = _d(valoare_bruta), _d(amortizare_cumulata)
    if vb <= 0 or am < 0 or am > vb:
        raise ValueError("Una sau mai multe valori sunt invalide. Verifică sumele și cantitățile introduse.")
    linii = []
    if am > 0:
        linii.append((str(cont_amortizare), str(cont_imobilizare), am))
    ramas = vb - am
    if ramas > 0:
        linii.append(("6583", str(cont_imobilizare), ramas))
    return {"linii": linii, "neamortizat": ramas}
