"""[712, comanda 14.2] Țara partenerului urmează codul lui fiscal. Un client cu cod „RO…” e în România; un cod de TVA cu prefixul altui stat al
Uniunii („DE…”, „EL…”, „IE…”) e al acelui stat. Țara pusă altfel (lista se poate schimba cu mâna, ecranul o deduce doar la tastarea codului)
ar duce factura în rândul greșit din D300 / D390 / D394, așa că emiterea se oprește cu motiv. [712.1] Un cod numai din cifre, cu cifra de
control de CUI corectă, e codul unei firme românești (cel verificat la ANAF se scrie și fără „RO”): țara lui e România. Un cod numeric fără
cifra de control de CUI nu spune țara: fără verdict."""
import re

from core.d390 import TARI_UE
from core.identitate import valideaza_cui

_PREFIXE = set(TARI_UE) | {"RO"}
_COD = re.compile(r"^([A-Z]{2})[0-9A-Z+*.\-]{2,}$")


def tara_din_cod(cui):
    """Țara codului de TVA: prefixul („RO”, „DE”, „EL”…) sau „RO” pentru un CUI numeric valid; None (alt stat decât ale Uniunii, ori numeric fără cifra de control de CUI)."""
    c = re.sub(r"\s+", "", str(cui or "")).upper()
    m = _COD.match(c)
    if m and m.group(1) in _PREFIXE:
        return m.group(1)
    if c.isdigit() and valideaza_cui(c)[0]:
        return "RO"
    return None


def nepotrivire(cui, tara):
    """Motivul refuzului când țara aleasă nu e a codului fiscal, altfel None."""
    din_cod = tara_din_cod(cui)
    aleasa = (tara or "RO").strip().upper() or "RO"
    if din_cod and din_cod != aleasa:
        return ("Țara partenerului (%s) nu se potrivește cu codul fiscal %s, care e al țării %s. Alege țara %s sau corectează codul fiscal."
                % (aleasa, re.sub(r"\s+", "", str(cui)).upper(), din_cod, din_cod))
    return None
