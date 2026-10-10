# -*- coding: utf-8 -*-
"""core/registru_fiscal.py — STAREA și EXPORTUL registrului unic de parametri fiscali (`common.COTE`).

Comanda Costin 08.10.2026 (verbatim în DECIZII), pct.1: „fiecare valoare fiscală folosită de iConta […] stă într-un singur registru.
Fiecare intrare are valoarea, temeiul (obiect Temei, citat verbatim din corpus), perioada de valabilitate (de la / până la) și starea
(propus / verificat / aprobat, cu cine și când). […] Registrul existent COTE devine acest registru (se extinde, nu se face unul
paralel).” Pct.4: „în registru intră doar propunerile cu verdictul APROB din fișierul de verificare al arhitectului (formatul de la
verif_temeiuri.json, 01.10.2026).” Pct.7: „Exportă tot registrul într-un singur fișier pentru verificarea arhitectului […]; până la
verdict, starea intrărilor rămâne «propus».”

Registrul e `common.COTE`; modulul ăsta nu ține valori, ci le DESCRIE:
  · STAREA unei intrări se derivă, nu se scrie de mână (o a doua scriere ar fi a doua sursă de adevăr):
      aprobat   — verdictul APROB al arhitectului pentru parametrul ei, în `registru_fiscal_verdicte.json` (cine = arhitectul, când =
                  data verdictului);
      verificat — `Temei` cu citat (`text_citat`), confirmat la sursă (`verificat_la`, `de_cine`), fără verdict încă;
      propus    — orice altceva: o intrare adăugată fără confirmare la sursă așteaptă verdictul.
    *INTERPRETARE CU TEMEI (de proces):* „verificat” = confirmarea executorului la sursă (forma pe care registrul o avea deja, cu cine și
    când), „aprobat” = verdictul arhitectului. Intrările noi ale migrării nu primesc `verificat_la` — rămân „propus” până la verdict
    (pct.7). De reconfirmat dacă „verificat” trebuie să însemne altceva.
  · EXPORTUL, în formatul fișierului de verificare (`temeiuri: [{parametru, unde_in_cod, folosire_in_iconta, verdict, temei_final,
    atom, verbatim, valabilitate}]`), cu starea fiecărei intrări; `verdict` gol, de completat de arhitect.
  · VERDICTELE se citesc numai din fișierul versionat în repo; nimic nu se aplică automat dintr-un fișier venit din afară.
"""
import io
import json
import os
from datetime import date

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALE_VERDICTE = os.path.join(RAD, "registru_fiscal_verdicte.json")
STARI = ("propus", "verificat", "aprobat")
APROB = "APROB"


def parametru(nume, din):
    """Cheia unei intrări în fișierul de verificare: `COTE/<nume>@<data_in>`."""
    return "COTE/%s@%s" % (nume, din.isoformat() if isinstance(din, date) else din)


def verdicte(cale=None):
    """{parametru: {"verdict", "de_cine", "data"}} — numai verdictele APROB din fișierul versionat (lipsa fișierului = niciun verdict)."""
    cale = cale or CALE_VERDICTE
    if not os.path.exists(cale):
        return {}
    d = json.load(io.open(cale, encoding="utf-8"))
    out = {}
    for t in d.get("temeiuri", []):
        if t.get("verdict") == APROB and t.get("parametru"):
            out[t["parametru"]] = {"verdict": APROB, "de_cine": t.get("de_cine") or d.get("de_cine"),
                                   "data": t.get("data") or d.get("data")}
    return out


def stare(nume, din, temei, ver=None):
    """{"stare", "de_cine", "la"} a unei intrări (derivată — vezi docstringul modulului)."""
    ver = verdicte() if ver is None else ver
    v = ver.get(parametru(nume, din))
    if v:
        return {"stare": "aprobat", "de_cine": v["de_cine"], "la": v["data"]}
    if getattr(temei, "text_citat", None) and getattr(temei, "verificat_la", None) and getattr(temei, "de_cine", None):
        return {"stare": "verificat", "de_cine": temei.de_cine, "la": temei.verificat_la.isoformat()}
    return {"stare": "propus", "de_cine": None, "la": None}


def _atom(temei):
    url = getattr(temei, "url", None) or ""
    baza = os.path.splitext(os.path.basename(url))[0] if url else ""
    parti = ["art%s" % temei.art] if getattr(temei, "art", None) else []
    if getattr(temei, "alin", None):
        parti.append("alin%s" % temei.alin)
    if getattr(temei, "lit", None):
        parti.append("lit%s" % temei.lit)
    return "%s#%s" % (baza, "/".join(parti)) if baza else "/".join(parti)


def _unde(nume):
    """Unde stă intrarea: o constantă ancorată (`<modul>.<NUME>`) în modulul ei, cu numele ei; o cheie istorică în `common.COTE`."""
    if "." in nume:
        modul, const = nume.split(".", 1)
        return "core/%s.py %s (common.ancoreaza -> COTE[%r])" % (modul, const, nume)
    return "core/common.py COTE[%r]" % nume


def exporta(cote=None, ver=None, cod_verificat=None):
    """Tot registrul, în formatul fișierului de verificare al arhitectului, cu starea fiecărei intrări."""
    from core import common as c
    cote = c.registru_complet() if cote is None else cote
    ver = verdicte() if ver is None else ver
    temeiuri = []
    for nume in sorted(cote):
        for din, valoare, temei in sorted(cote[nume], key=lambda r: r[0]):
            st = stare(nume, din, temei, ver)
            out = getattr(temei, "data_out", None)
            temeiuri.append({
                "parametru": parametru(nume, din),
                "valoare": str(valoare),
                "unde_in_cod": _unde(nume),
                "folosire_in_iconta": c.ETICHETE_COTE.get(nume),
                "verdict": None,
                "temei_final": str(temei),
                "atom": _atom(temei),
                "verbatim": getattr(temei, "text_citat", None),
                "valabilitate": "%s – %s" % (din.isoformat(), out.isoformat() if out else "în vigoare"),
                "nivel_sursa": getattr(temei, "nivel_sursa", None),
                "lant_acte": getattr(temei, "lant_acte", None),
                "stare": st["stare"], "stare_de": st["de_cine"], "stare_la": st["la"],
            })
    sumar = {s: sum(1 for t in temeiuri if t["stare"] == s) for s in STARI}
    return {"_ce": "Registrul unic de parametri fiscali iConta (common.COTE), exportat pentru verificarea arhitectului",
            "data": date.today().isoformat(), "cod_verificat": cod_verificat, "sumar": sumar, "temeiuri": temeiuri}


def _main():
    import subprocess
    import sys
    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=RAD).stdout.strip() or None
    d = exporta(cod_verificat=sha)
    cale = sys.argv[sys.argv.index("--scrie") + 1] if "--scrie" in sys.argv else None
    if cale:
        json.dump(d, io.open(cale, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("scris %s: %d intrări, %s" % (cale, len(d["temeiuri"]), d["sumar"]))
    else:
        print(json.dumps(d["sumar"]), len(d["temeiuri"]))


if __name__ == "__main__":
    _main()
