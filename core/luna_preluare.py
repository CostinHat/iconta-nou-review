# -*- coding: utf-8 -*-
"""LUNA PRELUĂRII firmei în iConta — de la ea se numără restanțele în Control fiscal (decizia Costin 08.10.2026 U2) — PUR.

[08.10.2026, decizia Costin §6 pct.4, verbatim în DECIZII] „Luna preluării: editabilă în Date firmă, cu valoarea dedusă ca propunere,
dar niciodată după luna primei note. Recalculează propunerea pentru F3 (are note din iunie). Schimbarea se jurnalizează.”

  * DEDUSĂ: ziua de după data soldurilor de preluare (`solduri_initiale.data_referinta` — soldurile sunt „la” acea dată, deci evidența
    în iConta începe a doua zi), iar fără ea luna în care firma a fost adăugată în iConta (`tenants.creat_la`).
    *INTERPRETARE CU TEMEI (de produs, nu fiscală):* cele două date sunt singurele fapte care descriu preluarea.
  * PROPUNEREA = dedusa, dar niciodată după luna PRIMEI NOTE: o notă scrisă în iConta dovedește că evidența era deja aici (F3: adăugată
    în octombrie, note din iunie -> 06/2026). „Prima notă” = cea mai veche notă din jurnal, oricare i-ar fi starea — și ciorna e scrisă
    în iConta.
  * EFECTIVĂ = luna salvată în Date firmă (`firma_profil.luna_preluare`), altfel propunerea.
  * Luna salvată nu poate fi după luna primei note (refuz lângă câmp, `eroare`). Jurnalul: `firma_profil_api.CAMPURI_JURNAL`.
"""
import datetime

CAMP = "luna_preluare"


def _luna(d):
    return (d.year, d.month) if d else None


def deduse(creat_la, data_solduri=None):
    """(an, luna) dedusă din soldurile de preluare sau din data adăugării; None dacă nu se știe niciuna."""
    if data_solduri:
        return _luna(data_solduri + datetime.timedelta(days=1))
    return _luna(creat_la)


def propunere(creat_la, data_solduri=None, prima_nota=None):
    """Dedusa, plafonată la luna primei note."""
    d, p = deduse(creat_la, data_solduri), _luna(prima_nota)
    if d and p:
        return min(d, p)
    return d or p


def efectiva(salvata, creat_la, data_solduri=None, prima_nota=None):
    """Luna salvată în Date firmă, altfel propunerea."""
    return _luna(salvata) or propunere(creat_la, data_solduri, prima_nota)


def eroare(luna, prima_nota):
    """Mesajul refuzului, sau None: luna preluării nu poate fi după luna primei note."""
    if luna and prima_nota and _luna(luna) > _luna(prima_nota):
        return ("Luna preluării nu poate fi după luna primei note din jurnal (%02d/%d): nota arată că evidența era deja în iConta.eu. "
                "Alege %02d/%d sau o lună mai veche." % (prima_nota.month, prima_nota.year, prima_nota.month, prima_nota.year))
    return None


def din_text(v):
    """„AAAA-LL” (câmpul lună) -> prima zi a lunii; gol -> None; altfel ValueError."""
    v = str(v or "").strip()
    if not v:
        return None
    try:
        return datetime.date(int(v[:4]), int(v[5:7]), 1) if len(v) == 7 and v[4] == "-" else datetime.date.fromisoformat(v).replace(day=1)
    except ValueError:
        raise ValueError("Luna preluării se scrie ca lună și an (ex. 06/2026).")


def stare(fapte):
    """`fapte` = `repo_firma_profil.fapte_preluare` -> {salvata, propunere, efectiva, prima_nota} ca „AAAA-LL” (pentru ecran)."""
    s, c, d, p = fapte.get("salvata"), fapte.get("creat_la"), fapte.get("data_solduri"), fapte.get("prima_nota")
    t = (lambda x: "%04d-%02d" % x if x else None)
    return {"salvata": t(_luna(s)), "propunere": t(propunere(c, d, p)), "efectiva": t(efectiva(s, c, d, p)),
            "prima_nota": t(_luna(p))}
