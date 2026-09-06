# -*- coding: utf-8 -*-
"""DOCUMENTUL PE CARE ÎL CITEAZĂ UN TEMEI CONȚINE ARTICOLUL PE CARE ÎL NUMEȘTE?

**CONVENȚIA DE MODELARE, care se aplică ÎNAINTE de a căuta** — declarată la interdicția **50**,
23.08.2026, cu opt zile înaintea instrumentului ăstuia:

> *„`Temei` reține **actul care a schimbat regula** și **numărul articolului din actul schimbat** —
> `Legea 141/2025 art. 97` înseamnă «CF art. 97, așa cum l-a modificat Legea 141/2025». … un
> instrument care le-ar lua literal ar căuta art. 97 în Legea 141/2025 și n-ar găsi nimic."*

**Prima formă a instrumentului ăstuia le-a luat literal, și a raportat șase perechi „negăsite" ca
DEFECT DE DATE.** Nu erau. Erau exact eșecul pe care registrul îl scrisese înainte. *Un instrument
care nu cunoaște convențiile de modelare ale datelor pe care le măsoară nu măsoară datele, ci
propria lui naivitate.* De-aceea rezolvarea articolului se face aici, o dată, prin `document_tinta`.

**Ce rămâne, după convenție:** perechile în care articolul e chiar al actului citat și tot nu se
găsește, plus cele al căror document e un **ciot**. Alea sunt întrebări reale.

**Nu e același lucru cu interdicția 59.** Aceea compară verificarea *pe act* cu cea *pe articol*.
Aici se întreabă doar dacă documentul în care TREBUIE căutat articolul chiar îl conține.

**Nu e același lucru cu interdicția 53.** Aceea întreabă dacă **citatul** conține valoarea — și
răspunde da pe 34 din 34. Un temei poate avea citatul potrivit și actul greșit: citatul e copiat de
noi, actul e o trimitere. Două întrebări, două răspunsuri, iar al doilea n-avea instrument.

CELE TREI FELURI DE „NU POT SPUNE", deosebite — un singur „nu" le-ar topi într-unul:
  - **NEGASIT**  — actul e adus și are articole, dar nu pe ăsta. *Ăsta e defectul.*
  - **CIOT**     — documentul citat are sub două titluri de articol (extras de PDF, formă parțială).
                   Nu se poate afirma nimic; e o problemă de **corpus**, nu de temei.
  - **FISIER_LIPSA** — `url`-ul temeiului nu duce nicăieri.

MODURILE DE EȘEC ALE INSTRUMENTULUI, scrise înainte de prima rulare:
  1. **Plafon INFERIOR.** Un temei fără `art` nu se poate verifica deloc — se numără separat, nu se
     trece la „bine".
  2. **Nu vede potrivirea GREȘITĂ.** Dacă actul citat conține din întâmplare un articol cu același
     număr, perechea trece — chiar dacă articolul acela e despre altceva. Ar cere o citire.
  3. **Depinde de corpus.** Un `CIOT` nu spune că temeiul e greșit; spune că nu s-a putut întreba.
"""
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)

from core import articol_in_act as A  # noqa: E402

#: Stările în care perechea NU se poate confirma. Nomenclator ÎNCHIS.
NECONFIRMATE = ("NEGASIT", "CIOT", "FISIER_LIPSA", "FARA_ART")

#: Numerele de articol care aparțin **Codului fiscal**, oricare ar fi actul citat alături de ele.
#: Scrise ca date fiindcă sunt o convenție, nu o deducție — v. interdicția 50. Aceeași mulțime e
#: folosită de `core/test_vigoare_articole_registru.py`, care o importă de aici: o convenție ținută
#: în două locuri se desparte în tăcere.
#: 322 adaugat 06.09.2026 (R167): perioada fiscala a TVA. Citit la sursa in
#: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, „Articolul 322 / Perioada fiscală".
ART_DE_COD_FISCAL = {"97", "28", "282", "291", "322"}

#: Forma consolidată a Codului fiscal din corpus — documentul în care se caută articolele de mai sus.
CF_CORPUS = "anaf_surse/cod_fiscal_227_2015_consolidat.html"


def cheie_articol(tip, nr, an, art):
    """(act, articol) DUPĂ convenție: articolele de Cod fiscal se rezolvă la `CF`, oricine le-ar cita."""
    tip = str(tip or "")
    art = str(art or "")
    if tip.upper() in ("CF", "CODUL FISCAL"):
        return ("CF", art)
    if art in ART_DE_COD_FISCAL:
        return ("CF", art)
    return ("%s %s/%s" % (tip, nr, an), art)


def document_tinta(t):
    """Documentul în care TREBUIE căutat articolul, nu neapărat cel citat de temei.

    Pentru o pereche care se rezolvă la `CF`, documentul e forma consolidată a Codului fiscal —
    fiindcă acolo **este** articolul. `url`-ul temeiului rămâne ce a fost: actul care a schimbat
    regula, adică proba pentru VALOARE. Cele două întrebări sunt diferite și au voie să aibă
    răspunsuri în documente diferite.
    """
    act, _art = cheie_articol(getattr(t, "tip", None), getattr(t, "nr", None),
                              getattr(t, "an", None), getattr(t, "art", None))
    url = CF_CORPUS if act == "CF" else getattr(t, "url", None)
    return _cale(url) if url else None


def _cale(url):
    return url if os.path.isabs(str(url)) else os.path.join(RAD, str(url))


def inventar():
    """[{cale, temei, act, art, url, stare}] — o intrare per temei unic din registrul de cote."""
    from core import scan_citate
    out = []
    for cale, t, _v in scan_citate.inventar():
        art = getattr(t, "art", None)
        url = getattr(t, "url", None)
        rand = {"cale": cale, "temei": str(t), "art": art, "url": url,
                "act": "%s %s/%s" % (getattr(t, "tip", "?"), getattr(t, "nr", "?"),
                                     getattr(t, "an", "?"))}
        tinta = document_tinta(t)
        rand["document_tinta"] = tinta
        rand["dupa_conventie"] = bool(tinta and tinta != _cale(url or ""))
        if not art:
            rand["stare"] = "FARA_ART"
        elif not tinta:
            rand["stare"] = "FISIER_LIPSA"
        else:
            rand["stare"] = A.cauta(tinta, art)["stare"]
        out.append(rand)
    return out


def neconfirmate(inv=None):
    """Perechile care NU se pot confirma, fără cele fără articol — clasa propriu-zisă plus ciotul."""
    return [x for x in (inv if inv is not None else inventar())
            if x["stare"] in ("NEGASIT", "CIOT", "FISIER_LIPSA")]


def pe_stare(inv=None):
    d = {}
    for x in (inv if inv is not None else inventar()):
        d[x["stare"]] = d.get(x["stare"], 0) + 1
    return d


def _main():
    inv = inventar()
    for x in sorted(inv, key=lambda y: (y["stare"], y["act"], str(y["art"]))):
        print("  %-13s %-26s art.%-8s %-34s  <- %s"
              % (x["stare"], x["act"][:26], str(x["art"])[:8],
                 os.path.basename(str(x["url"]))[:34], x["cale"][:34]))
    print()
    print("PE STARE: %s" % pe_stare(inv))
    ver = [x for x in inv if x["stare"] != "FARA_ART"]
    print("verificabile: %d · confirmate: %d · NECONFIRMATE: %d"
          % (len(ver), sum(1 for x in ver if x["stare"] in ("GASIT", "ABROGAT")),
             len(neconfirmate(inv))))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
