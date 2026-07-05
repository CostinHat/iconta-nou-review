# -*- coding: utf-8 -*-
"""Forecast cash-flow 8 saptamani: cash curent + incasari/plati asteptate pe scadente.
Soldul 4111/401 se aloca pe facturi de la cele mai noi spre vechi (FIFO la plata)."""
import datetime


def aloca_sold(facturi, sold):
    """facturi: [{data_scadenta, total}], sold = cat e neincasat/neplatit in balanta.
    Intoarce facturile considerate deschise (cele mai noi), cu suma alocata."""
    ramas = float(sold or 0)
    deschise = []
    for f in sorted(facturi, key=lambda x: str(x.get("data_scadenta") or x.get("data_emitere") or ""), reverse=True):
        if ramas <= 0.005:
            break
        suma = min(float(f.get("total") or 0), ramas)
        if suma <= 0:
            continue
        deschise.append({"data_scadenta": f.get("data_scadenta") or f.get("data_emitere"), "suma": round(suma, 2)})
        ramas -= suma
    return deschise


def forecast(cash, emise_deschise, primite_deschise, azi=None, saptamani=8):
    """Proiectie saptamanala. Scadentele trecute intra in saptamana 1."""
    azi = azi or datetime.date.today()
    sold = float(cash or 0)
    rez = []
    for w in range(saptamani):
        inceput = azi + datetime.timedelta(days=7 * w)
        sfarsit = inceput + datetime.timedelta(days=7)
        def _in(f):
            d = f.get("data_scadenta")
            d = datetime.date.fromisoformat(str(d)[:10]) if d else azi
            if w == 0:
                return d < sfarsit
            return inceput <= d < sfarsit
        inc = round(sum(f["suma"] for f in emise_deschise if _in(f)), 2)
        pla = round(sum(f["suma"] for f in primite_deschise if _in(f)), 2)
        sold = round(sold + inc - pla, 2)
        rez.append({"saptamana": w + 1, "de_la": inceput.isoformat(),
                    "incasari": inc, "plati": pla, "sold": sold})
    return rez


def obligatii_din_balanta(randuri):
    """Solduri creditoare de platit: fiscale (25 ale lunii) + salarii nete (imediat)."""
    def _sc(prefixe):
        return round(sum(r["sf_c"] for r in randuri
                         if any(str(r["cont"]).startswith(p) for p in prefixe)), 2)
    return {"fiscale": _sc(("4423", "431", "436", "444", "4411")),
            "salarii_nete": _sc(("421",))}


def cheltuieli_lunare_cash(randuri, luni_scurse):
    """Media lunara a cheltuielilor cash: cl.6 fara 68x (amortizari) si 641/645 (acoperite de 421/431)."""
    ch = round(sum(r["rul_d"] - r["rul_c"] for r in randuri
                   if str(r["cont"]).startswith("6")
                   and not str(r["cont"]).startswith(("68", "641", "645"))), 2)
    return round(ch / max(luni_scurse, 1), 2)


def plati_estimate(obligatii, medie_lunara, azi=None, saptamani=8):
    """Genereaza lista de plati estimate: [{data_scadenta, suma}]."""
    azi = azi or datetime.date.today()
    plati = []
    if obligatii.get("salarii_nete"):
        plati.append({"data_scadenta": azi.isoformat(), "suma": obligatii["salarii_nete"]})
    urm25 = azi.replace(day=25) if azi.day <= 25 else \
        (azi.replace(day=1) + datetime.timedelta(days=32)).replace(day=25)
    if obligatii.get("fiscale"):
        plati.append({"data_scadenta": urm25.isoformat(), "suma": obligatii["fiscale"]})
    if medie_lunara > 0:
        d = azi
        for _ in range(max(1, saptamani // 4)):
            d = (d.replace(day=1) + datetime.timedelta(days=32)).replace(day=min(azi.day, 28))
            plati.append({"data_scadenta": d.isoformat(), "suma": medie_lunara})
    return plati


def obligatii_din_balanta(randuri):
    """Solduri creditoare de platit: fiscale (25 ale lunii) + salarii nete (imediat)."""
    def _sc(prefixe):
        return round(sum(r["sf_c"] for r in randuri
                         if any(str(r["cont"]).startswith(p) for p in prefixe)), 2)
    return {"fiscale": _sc(("4423", "431", "436", "444", "4411")),
            "salarii_nete": _sc(("421",))}


def cheltuieli_lunare_cash(randuri, luni_scurse):
    """Media lunara a cheltuielilor cash: cl.6 fara 68x (amortizari) si 641/645 (acoperite de 421/431)."""
    ch = round(sum(r["rul_d"] - r["rul_c"] for r in randuri
                   if str(r["cont"]).startswith("6")
                   and not str(r["cont"]).startswith(("68", "641", "645"))), 2)
    return round(ch / max(luni_scurse, 1), 2)


def plati_estimate(obligatii, medie_lunara, azi=None, saptamani=8):
    """Genereaza lista de plati estimate: [{data_scadenta, suma}]."""
    azi = azi or datetime.date.today()
    plati = []
    if obligatii.get("salarii_nete"):
        plati.append({"data_scadenta": azi.isoformat(), "suma": obligatii["salarii_nete"]})
    urm25 = azi.replace(day=25) if azi.day <= 25 else \
        (azi.replace(day=1) + datetime.timedelta(days=32)).replace(day=25)
    if obligatii.get("fiscale"):
        plati.append({"data_scadenta": urm25.isoformat(), "suma": obligatii["fiscale"]})
    if medie_lunara > 0:
        d = azi
        for _ in range(max(1, saptamani // 4)):
            d = (d.replace(day=1) + datetime.timedelta(days=32)).replace(day=min(azi.day, 28))
            plati.append({"data_scadenta": d.isoformat(), "suma": medie_lunara})
    return plati
