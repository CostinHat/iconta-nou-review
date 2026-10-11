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

#: funcționalitate (ID din registru) -> acțiunea care o face, „METODĂ /cale” ca în main.py. [deficiența 223, comanda Costin 10.10.2026:
#: „Catalogul trebuie să arate doar ce poate folosi rolul lui. Acesta e și parțialul nr. 5”] Măsurat pe gărzile serverului: rutele
#: refuzate unui asistent cu numai „Poate pregăti” (`drepturi.interzise`), legate de funcția din catalog pe care o fac; o funcție
#: care are și o acțiune permisă asistentului (coada, pachetele, magazinul) rămâne vizibilă și nu e aici.
RUTA_FUNCTIONALITATE = {
    "F005": "POST /cabinet/api-chei",        # Chei API publice per cabinet (Setări cont > Chei API)
    "F006": "POST /asistenti",               # Contabilii și asistenții cabinetului (card Asistenți)
    "F204": "GET /gdpr/export-cabinet",      # Autoservire export date cabinet (Setări > Datele cabinetului)
    "F205": "POST /gdpr/cerere-stergere",    # Cerere de ștergere cont (Setări > Datele cabinetului)
    "F199": "GET /gdpr/export-cabinet",      # Export GDPR complet cabinet (aceeași rută ca F204)
    "F014": "GET /capacitate",               # Panoul de capacitate (administrator)
    "F094": "GET /tipare",                   # Tiparele de respingere ale declarațiilor (Activitate > Tipare de erori)
    "F120": "GET /tipare/ai",                # Analiza AI a tiparelor de respingere
    "F058": "POST /migrare/status",          # Starea migrării pe straturi (migrarea cabinetului)
    "F188": "POST /tenants",                 # Precompletarea din ANAF la adăugarea firmei — adăugarea firmei e a administratorului
    "F114": "POST /cabinet/api-chei",        # API public pentru integrări — merge numai cu o cheie, pe care o creează administratorul
    "F118": "POST /tenants/{tenant_id}/perioade-blocate",   # Blocare perioade — „Poate valida”
    "F075": "POST /tenants/{tenant_id}/reges-trimite-salariat",   # Conexiunea cu REGES — trimiterea și răspunsurile: „Poate depune”
    "F107": "POST /tenants/{tenant_id}/client-acces",       # Intrarea clientului în portal — accesul îl dă administratorul
}
#: [deficiența 223] funcții fără acțiune refuzată (rutele lor sunt deschise oricărui membru al cabinetului), dar al căror ecran e
#: numai pe pagina contabilului-șef: asistentul nu le poate deschide. Gard: cardul există în `cabinet.js` și lipsește din `asistent.js`.
NUMAI_PAGINA_CABINETULUI = {
    "F083": "brief",                         # Sinteza zilnică — cardul „Sinteza zilei”
}
#: [deficiența 223] funcțiile de nivel cabinet din catalog pe care asistentul le FOLOSEȘTE, cu motivul (măsurat pe gărzi). Gardul cere ca
#: fiecare funcție de nivel cabinet sau portal din catalog să fie într-una din cele trei liste: refuzată, numai la cabinet, folosită.
FOLOSITE_DE_ASISTENT = {
    "F162": "Control fiscal — detaliul firmei se citește cu `cere_cabinet` (firmele alocate)",
    "F163": "Control fiscal — detaliul firmei se citește cu `cere_cabinet`",
    "F169": "Control fiscal — detaliul firmei se citește cu `cere_cabinet`",
    "F184": "Control fiscal — detaliul firmei se citește cu `cere_cabinet`",
    "F164": "clopoțelul primește constatările firmelor alocate (destinatarii sunt contabilii cabinetului)",
    "F065": "pachetul lunar se generează și se scrie cu «Poate pregăti» (aprobarea și trimiterea cer «Poate valida»)",
    "F197": "previzualizarea portalului e o citire (`CITIRE`), fără bifă",
    "F093": "cardul Termene e pe pagina asistentului",
    # portalul clientului: rutele `/portal/*` sunt ale clientului (refuzate oricui din cabinet, deci și contabilului-șef); cabinetul
    # vede ce primește clientul prin previzualizare (F197, `CITIRE`) — legate de o rută de portal, ar fi dispărut și din catalogul șefului
    "F068": "portalul clientului, văzut de cabinet prin previzualizare (F197)",
    "F042": "portalul clientului, văzut de cabinet prin previzualizare (F197)",
    "F055": "portalul clientului, văzut de cabinet prin previzualizare (F197)",
    "F016": "portalul clientului, văzut de cabinet prin previzualizare (F197)",
    "F113": "portalul clientului, văzut de cabinet prin previzualizare (F197)",
}
ROL_ASISTENT = "angajat"
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
            if rol == ROL_ASISTENT and fid in NUMAI_PAGINA_CABINETULUI:
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

