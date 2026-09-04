# -*- coding: utf-8 -*-
"""Operatiuni intracomunitare - motor PUR + client VIES.
Surse: Cod fiscal art. 268 (AIC), 278 al. 2 (servicii B2B locul beneficiarului),
294 al. 2 lit. a (LIC scutita cu drept de deducere - conditii: cod TVA valid al
cumparatorului comunicat furnizorului + dovada transportului in alt SM),
308-309 (obligat la plata = beneficiarul la AIC/servicii primite), norme pct. 109
(taxare inversa 4426=4427, valabil pentru orice situatie de taxare inversa).
VIES REST oficial: https://ec.europa.eu/taxation_customs/vies/rest-api/ms/{MS}/vat/{nr}."""
import json
import re
import urllib.request
from decimal import Decimal, ROUND_HALF_UP

B = Decimal("0.01")
VIES_URL = "https://ec.europa.eu/taxation_customs/vies/rest-api/ms/{ms}/vat/{vat}"
TARI_UE = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR",
           "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO",
           "SE", "SI", "SK", "XI"}  # XI = Irlanda de Nord (VIES post-Brexit)

def desparte_cod_tva(cod):
    """'DE 123456789' -> ('DE', '123456789'). Grecia pe VIES = EL."""
    c = re.sub(r"[^A-Z0-9]", "", (cod or "").upper())
    tara, nr = c[:2], c[2:]
    if tara == "GR":
        tara = "EL"
    if tara not in TARI_UE:
        raise ValueError(f"tara '{tara}' nu este stat membru UE (VIES)")
    if not nr:
        raise ValueError("numar TVA lipsa dupa codul de tara")
    return tara, nr

def verifica_vies(cod_tva, timeout=15):
    """Interogheaza VIES oficial. Returneaza {valid, nume, adresa, tara, numar}."""
    tara, nr = desparte_cod_tva(cod_tva)
    req = urllib.request.Request(VIES_URL.format(ms=tara, vat=nr),
                                 headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    return {"valid": bool(d.get("isValid")), "nume": d.get("name") or "",
            "adresa": (d.get("address") or "").strip(), "tara": tara, "numar": nr,
            "eroare": d.get("userError") if not d.get("isValid") else None}

def tva_taxare_inversa(baza, cota=None):
    """AIC bunuri/servicii primite: TVA prin taxare inversa 4426 = 4427."""
    if cota is None:
        raise ValueError("Cota de TVA nu s-a dat. Nu se folosește o valoare implicită: o cotă scrisă în cod se rupe tăcut de lege la prima schimbare, iar o operațiune veche are altă cotă decât una de azi. Declară cota operațiunii.")
    b = Decimal(str(baza))
    if b <= 0:
        raise ValueError("Valoarea achiziției trebuie să fie un număr pozitiv — o achiziție "
                         "consemnează o operațiune efectuată. Pentru o corecție în minus se face "
                         "o stornare, nu o valoare negativă.")
    return (b * Decimal(str(cota)) / 100).quantize(B, rounding=ROUND_HALF_UP)

def valideaza_lic(cod_tva_client, cod_valid_vies, are_dovada_transport):
    """Livrare IC scutita (art. 294 al. 2 lit. a): cod TVA valid din alt SM
    + dovada transportului. Altfel -> regim normal cu TVA."""
    tara, _ = desparte_cod_tva(cod_tva_client)
    if tara == "RO":
        raise ValueError("clientul e din RO - nu e livrare intracomunitara")
    if not cod_valid_vies:
        raise ValueError("cod TVA client INVALID in VIES - scutirea art. 294(2)a nu se "
                         "aplica, factureaza cu TVA romanesc")
    if not are_dovada_transport:
        raise ValueError("fara dovada transportului in alt stat membru scutirea nu se "
                         "aplica (art. 294(2)a) - factureaza cu TVA")
    return True, "scutit cu drept de deducere - art. 294 alin. (2) lit. a) Cod fiscal (LIC)"

def valideaza_prestare_ic(cod_tva_client, cod_valid_vies):
    """Prestare servicii B2B catre PI din alt SM (art. 278 al. 2): neimpozabila
    in RO, locul = beneficiarul; se declara in D390 (S)."""
    tara, _ = desparte_cod_tva(cod_tva_client)
    if tara == "RO":
        raise ValueError("clientul e din RO - regim normal")
    if not cod_valid_vies:
        raise ValueError("cod TVA client INVALID in VIES - nu e PI dovedita, "
                         "serviciul se factureaza cu TVA romanesc (B2C art. 278(3))")
    return True, "neimpozabil in RO - art. 278 alin. (2) Cod fiscal (locul = beneficiarul)"
