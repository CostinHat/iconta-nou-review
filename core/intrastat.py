# -*- coding: utf-8 -*-
"""Intrastat - verificator praguri (Ordinul INS 1604/2025, MO 1022/05.11.2025).
Praguri 2026: 1.000.000 lei expedieri si 1.000.000 lei introduceri (separat pe
flux). Obligatia de declarare incepe cu LUNA in care valoarea CUMULATA de la
inceputul anului depaseste pragul, separat pe flux. Declaratia se depune lunar
la INS (intrastat.ro) cu coduri NC8 - aici doar monitorizam pragurile."""
from datetime import date
from decimal import Decimal

from core.common import AVERTISMENT, cota

# PRAGUL NU MAI E SCRIS AICI (01.09.2026). Statea ca literal, deci era invizibil pentru orice regula
# de domeniu ancorata pe registru — si asa a devenit singura constanta fiscala reala ramasa in afara
# acoperirii, cunoscuta doar dintr-un raport. Se citeste acum din `COTE["plafon_intrastat"]`.
#
# `PRAG_ATENTIE` RAMANE AICI, si nu e o scapare: 80%% nu e o valoare din lege, e pragul NOSTRU de
# avertizare timpurie. O valoare de produs nu are ce cauta in registrul de cote — v. `DECIZII` 20.2,
# unde aceeasi deosebire a decis unde stau limitele de reverificare.
PRAG_ATENTIE = Decimal("0.80")


def prag_intrastat(la_data=None):
    """Pragul Intrastat la data ceruta, din registru. Acelasi pe ambele fluxuri (Ordin INS 1604/2025)."""
    val, _t = cota("plafon_intrastat", la_data=la_data or date.today())
    return Decimal(str(val))

# status -> nivel de verdict declarat de MOTOR (severitatea nu se alege la randare). Depasirea pragului
# naste OBLIGATIE de declarare lunara la INS = situatie determinata, legal dar riscanta -> AVERTISMENT.
# atentie (>=80%) = obligatie iminenta, tot AVERTISMENT. NICIODATA BLOCANT (nu opreste contabilizarea, e o
# obligatie EXTERNA la INS, nu la ANAF) si NICIODATA gri (pragul e determinat, nu incertitudine de verificare).
NIVEL_STATUS = {"depasit": AVERTISMENT, "atentie": AVERTISMENT}

PREFIXE_UE = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "GR", "ES",
              "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL",
              "PL", "PT", "SE", "SI", "SK", "XI"}

def e_partener_ue(cui):
    """CUI cu prefix de stat membru UE (nu RO) -> operatiune intracomunitara."""
    c = (cui or "").strip().upper().replace(" ", "")
    return c[:2] in PREFIXE_UE

def analiza_flux(valori_lunare, prag=None):
    """valori_lunare: {luna(int): suma}. Returneaza cumulat, status
    (sub_prag|atentie|depasit), luna_depasirii, procent, nivel (AVERTISMENT pe atentie/depasit, altfel None)."""
    prag = prag if prag is not None else prag_intrastat()
    cumulat = Decimal("0")
    luna_dep = None
    for luna in sorted(valori_lunare):
        cumulat += Decimal(str(valori_lunare[luna] or 0))
        if luna_dep is None and cumulat > prag:
            luna_dep = luna
    procent = (cumulat / prag * 100).quantize(Decimal("0.1")) if prag else Decimal("0")
    if luna_dep:
        status = "depasit"
    elif cumulat >= prag * PRAG_ATENTIE:
        status = "atentie"
    else:
        status = "sub_prag"
    return {"cumulat": cumulat, "status": status, "luna_depasirii": luna_dep,
            "procent": procent, "prag": prag, "nivel": NIVEL_STATUS.get(status)}
