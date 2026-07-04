# -*- coding: utf-8 -*-
"""Import/export extracomunitar - motor PUR.
Surse: art. 289 CF (baza = valoarea in vama + taxe/impozite/comisioane datorate
+ cheltuieli accesorii pana la primul loc de destinatie in RO), art. 326 al. 4-5
(certificat amanare plata TVA -> taxare inversa in decont 4426=4427, Ordin MFP
4121/2015), art. 299 al. 1 lit. c (deducere pe baza DVI + dovada platii),
art. 294 al. 1 lit. a-b (export scutit cu drept de deducere, dovada DVE)."""
from decimal import Decimal, ROUND_HALF_UP

B = Decimal("0.01")

def _d(x):
    return Decimal(str(x or 0))

def baza_tva_import(valoare_vamala, taxe_vamale=0, accize=0, accesorii=0):
    """Baza de impozitare TVA la import (art. 289): valoarea in vama + taxe
    vamale + accize + cheltuieli accesorii (transport/asigurare/ambalare)
    pana la primul loc de destinatie, daca nu-s deja in valoarea vamala."""
    vv, tv, ac, ca = _d(valoare_vamala), _d(taxe_vamale), _d(accize), _d(accesorii)
    if vv <= 0 or tv < 0 or ac < 0 or ca < 0:
        raise ValueError("valori invalide")
    return (vv + tv + ac + ca).quantize(B, rounding=ROUND_HALF_UP)

def calcul_import(valoare_vamala, procent_taxa_vamala=0, accize=0, accesorii=0,
                  cota_tva=21, certificat_amanare=False, platitor_tva=True):
    """Returneaza dict complet: taxa vamala, baza TVA, TVA, mod plata TVA.
    - platitor cu certificat (art. 326(4)): TVA in decont 4426=4427 (nu se plateste in vama)
    - platitor fara certificat: TVA platita in vama, 4426=446, deducere pe DVI
    - neplatitor: TVA in vama intra in COST (nu se deduce)."""
    vv = _d(valoare_vamala)
    if vv <= 0:
        raise ValueError("valoare vamala invalida")
    tv = (vv * _d(procent_taxa_vamala) / 100).quantize(B, rounding=ROUND_HALF_UP)
    baza = baza_tva_import(vv, tv, accize, accesorii)
    tva = (baza * _d(cota_tva) / 100).quantize(B, rounding=ROUND_HALF_UP)
    if certificat_amanare and not platitor_tva:
        raise ValueError("certificatul de amanare (art. 326(4)) e doar pentru "
                         "persoane inregistrate in scopuri de TVA art. 316")
    if certificat_amanare:
        mod = "decont"    # 4426=4427, D300 rd. 7+22
    elif platitor_tva:
        mod = "vama"      # 4426=446 + 446=5121, deducere DVI rd. 24
    else:
        mod = "cost"      # TVA nedeductibila -> in costul bunului
    return {"taxa_vamala": tv, "baza_tva": baza, "tva": tva, "mod_tva": mod}

def valideaza_export(tara_client, are_dovada_export):
    """Export scutit cu drept de deducere (art. 294 al. 1 lit. a-b):
    transport in afara UE dovedit cu declaratia vamala de export (DVE/EAD)."""
    if not (tara_client or "").strip():
        raise ValueError("tara client obligatorie")
    if not are_dovada_export:
        raise ValueError("fara declaratia vamala de export (DVE) scutirea art. 294(1)a "
                         "nu se justifica - factureaza cu TVA pana la obtinerea dovezii")
    return True, "scutit cu drept de deducere - art. 294 alin. (1) lit. a) Cod fiscal (export)"
