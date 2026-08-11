# -*- coding: utf-8 -*-
"""core/ajutor.py — ajutor contextual pentru contabil (coloana `ajutor` din FUNCTIONALITATI.csv).
Serveste textul de ajutor per functionalitate (ID F###) catre semnul "?" din UI.
Sursa unica = registrul; citit ca raportari_ai (csv.reader, utf-8-sig). Cache in memorie,
invalidat la restart (ca _BAZA din raportari_ai)."""
import csv
import pathlib

_CACHE = None
_CALE = pathlib.Path(__file__).resolve().parent.parent / "FUNCTIONALITATI.csv"


def _incarca():
    global _CACHE
    if _CACHE is None:
        d = {}
        with open(_CALE, encoding="utf-8-sig") as f:
            r = csv.reader(f)
            antet = next(r)
            i_id = antet.index("ID")
            i_nume = antet.index("Functionalitate")
            i_aj = antet.index("ajutor") if "ajutor" in antet else -1
        with open(_CALE, encoding="utf-8-sig") as f:
            r = csv.reader(f)
            next(r)
            for rand in r:
                if len(rand) <= max(i_id, i_nume, i_aj):
                    continue
                fid = (rand[i_id] or "").strip()
                aj = (rand[i_aj] or "").strip() if i_aj >= 0 else ""
                if fid:
                    d[fid] = {"id": fid, "titlu": (rand[i_nume] or "").strip(), "ajutor": aj}
        _CACHE = d
    return _CACHE


def pentru(fid):
    """Intoarce {id, titlu, ajutor} pentru o functionalitate, sau None daca nu are ajutor scris."""
    x = _incarca().get((fid or "").strip())
    if not x or not x["ajutor"]:
        return None
    return x


def cu_ajutor():
    """Setul de ID-uri care AU text de ajutor (pt UI: arata "?" doar unde exista)."""
    return {k for k, v in _incarca().items() if v["ajutor"]}
