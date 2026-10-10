# -*- coding: utf-8 -*-
"""core/ansamblu.py — ce arată „Ce cuprinde aplicația” (prezentarea de ansamblu), după rol. [deficiența 5, retestul Costin 09.10.2026:
„Ana vede în catalog funcții de administrator”]

Catalogul vine din registru (`FUNCTIONALITATI.csv`, grupele `genereaza_grupe_functii.repartizeaza`). Două filtre, fără listă paralelă
de drepturi:
  · funcționalitățile cu nivelul `admin` în registru sunt ale PLATFORMEI (Admin iConta): le vede numai administratorul platformei;
  · funcționalitățile administratorului de CABINET își poartă ruta (`RUTA_FUNCTIONALITATE`, aceeași formă ca `data-actiune`), iar ecranul o
    marchează pe rând — mecanismul de drepturi existent (`/eu/drepturi`, `drepturi.js`) le ascunde celui căruia serverul îi refuză
    ruta. Cine primește ce rămâne decis de gărzile rutelor (`core/drepturi.py`), nu de aici.
Gardul `core/test_ansamblu.py` cere ca orice funcționalitate de cabinet accesată din Setări / Asistenți să-și aibă ruta aici, iar
fiecare rută de aici să existe și să fie refuzată asistentului.
"""
import re

#: funcționalitate (ID din registru) -> acțiunea care o face, „METODĂ /cale” ca în main.py
RUTA_FUNCTIONALITATE = {
    "F005": "POST /cabinet/api-chei",        # Chei API publice per cabinet (Setări cont > Chei API)
    "F006": "POST /asistenti",               # Contabilii și asistenții cabinetului (card Asistenți)
    "F204": "GET /gdpr/export-cabinet",      # Autoservire export date cabinet (Setări > Datele cabinetului)
    "F205": "POST /gdpr/cerere-stergere",    # Cerere de ștergere cont (Setări > Datele cabinetului)
}
NIVEL_PLATFORMA = "admin"
ROL_PLATFORMA = "superadmin"


def functii(grupe, randuri, rol, cu_ajutor):
    """[{titlu, icon, functii:[{nume, id, are_ajutor, actiune}]}] — `randuri` = {nume: (id, nivel)} din registru."""
    out = []
    for gr in grupe:
        ff = []
        for n in gr["functii"]:
            fid, nivel = randuri.get(n, (None, None))
            if nivel == NIVEL_PLATFORMA and rol != ROL_PLATFORMA:
                continue
            ff.append({"nume": n, "id": fid, "are_ajutor": bool(fid and fid in cu_ajutor), "actiune": RUTA_FUNCTIONALITATE.get(fid)})
        if ff:
            out.append({"titlu": gr["titlu"], "icon": gr["icon"], "functii": ff})
    return out


#: [deficiența 201, retestul Costin 09.10.2026: „limbaj de programator (pull->push, F163v2, «Dispatch», v9) și titluri fără diacritice”]
#: pe lângă regulile ecranului (`core/limba_ecran.py`): codurile interne ale registrului și jargonul englezesc de dezvoltator
_TEHNIC = re.compile(r"->|\bF\d{3}\w*|\bv\d+\b|\b(?:dispatch|push|pull|finding\w*|matching|landed|parser|forecast|self-service|crud|"
                     r"read-only|magic-link|onboarding|setabil\w*|management|kpi|ui|in-app|în-app|engine|wizard|stub|fallback)\b", re.I)


def limbaj_tehnic(text):
    """[(fel, fragment)] — ce nu e limba contabilului într-un nume / titlu din catalog: regulile ecranului + `_TEHNIC`."""
    from core import limba_ecran as _le
    return [d for d in _le.defecte(text) if d[0] in ("cod", "jargon", "diacritice", "majuscule")] + [
        ("tehnic", m.group(0)) for m in _TEHNIC.finditer(text or "")]

