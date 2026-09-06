# -*- coding: utf-8 -*-
"""CATEGORIA DE REVERIFICARE — interdicția 55, calculată, nu atribuită.

**Ce lipsea.** Măsurat 23.08.2026: *„53 din 53 fără categorie de reverificare — fiindcă **câmpul nu
există**."* Există în schimb un **prag global unic** (6 luni, `CONFIRMARE_COTE_PRAG_LUNI`), aplicat
identic tuturor articolelor. O cotă de TVA care se poate schimba la fiecare rectificare bugetară și o
definiție neatinsă din 2015 au azi **același** prag: definițiile stabile se reconfirmă inutil, iar
valorile volatile se reconfirmă prea rar.

**Axa, decisă de Costin 23.08:** *frecvența istorică de modificare a **articolului**, ponderată de
**consecința** unei valori expirate.* Volatilitatea **actului** a fost respinsă, cu motiv măsurat:
OUG 89/2025 are șase marcaje de consolidare, iar art. III — cel care poartă valorile — **niciunul**.
O axă pe act ar declara suspecte permanent toate valorile sprijinite pe acte mari, iar un semnal
permanent se ignoră.

**Amândouă măsurile sunt mecanice** — asta face categoriile *calculabile*, nu *atribuibile*.

  A. frecvența ← marcajele de consolidare ale articolului (`core/articol_in_act.py`), citite în
     documentul pe care îl indică **convenția** de la interdicția 50
     (`scan_pereche_act_articol.document_tinta`), nu în actul citat literal.
  B. consecința ← unde ajunge valoarea (`core/dependenti_act.py`): dacă atinge un modul de
     declarație (`d1xx`/`d3xx`/`d4xx`), greșeala pleacă la ANAF.

**NECUNOSCUT NU E O CLASĂ DE REZERVĂ, E UN RĂSPUNS** *(Costin, 31.08)*: *„perechile neconfruntabile
primesc NECUNOSCUT declarat. Orice implicit minte — STABIL tăcut, VOLATIL zgomotos."* O pereche fără
axă A nu primește prag. Absența pragului e vizibilă, nu tăcută.

CE NU FACE, declarat:
  - **`INFORMATIV` nu se poate atribui mecanic azi**, și clasa e declarată **VIDĂ**, cu motivul:
    `dependenti_act` vede funcții Python, nu ecrane, deci nu poate deosebi *„intră într-o cifră
    arătată omului"* de *„apare ca informație"*. Consecința e scrisă, nu ascunsă: **pragurile
    INFORMATIV (6/12/18) nu se atribuie niciodată azi.** Rămân în tabel fiindcă tabelul e decizia
    lui Costin, nu a instrumentului — și pentru ziua în care apare o cale de a le atribui.
  - **nu confirmă că marcajul atinge VALOAREA.** Un articol modificat la alineatul (9) e clasat
    volatil chiar dacă valoarea stă la alineatul (2). Deci frecvența e **plafon SUPERIOR** pentru
    volatilitatea reală a valorii — direcție aleasă deliberat: mai des verificat, nu mai rar.
  - **nu citește portalul.** Se uită în corpus, la forma adusă și amprentată. Un act modificat azi
    și neadus încă nu se vede — e chiar clasa pe care o măsoară interdicția 52.
"""
import datetime
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)

from core import articol_in_act as A  # noqa: E402
from core import scan_pereche_act_articol as S  # noqa: E402

#: LIMITELE de reverificare — **nu sunt valori fiscale**, și de-aia stau împreună, sub un nume care
#: le declară ca atare. Au sursă, dar **alta decât legea** și cu altă cadență de revizuire: sunt
#: **decizia lui Costin din 23.08.2026**, scrisă în `CONFORMITATE.md` la interdicția **55**. Un
#: `Temei(...)` aici ar fi o minciună — nu există act care să spună la câte luni se recitește un
#: articol. *`core/scan_constante.py` clasifică după nume (`NOM`) exact pentru cazul ăsta: „are și el
#: sursă, dar ALTA".*
#:
#: `fereastra_ani`: *suficientă ca să prindă un articol modificat de două ori, scurtă cât să nu
#: conteze modificări care n-au mai revenit.*
#: `praguri_luni`: tabelul 3×3. Pragul global de azi — 6 luni pentru tot — e chiar căsuța din mijloc.
LIMITE_REVERIFICARE = {
    "fereastra_ani": 3,
    "praguri_luni": {
        ("VOLATIL", "DEPUS"): 1,   ("VOLATIL", "CALCULAT"): 3,   ("VOLATIL", "INFORMATIV"): 6,
        ("MISCATOR", "DEPUS"): 3,  ("MISCATOR", "CALCULAT"): 6,  ("MISCATOR", "INFORMATIV"): 12,
        ("STABIL", "DEPUS"): 6,    ("STABIL", "CALCULAT"): 12,   ("STABIL", "INFORMATIV"): 18,
    },
}

#: **CADENȚA LUNARĂ E CONFIRMATĂ, nu tolerată** *(Costin, 01.09.2026)*. Căsuța `("VOLATIL","DEPUS")`
#: = 1 lună produce azi trei alerte pe lună — `impozit_dividend`, `impozit_micro`, `impozit_venit` —
#: și asta e **decizia**, nu un efect secundar de reglat: *„sunt valorile care se mișcă și intră în
#: declarații — categoria care poate produce o cifră validă și falsă."* Tabelul 3×3 **rămâne
#: neatins**. Se scrie aici fiindcă zgomotul lunar e exact felul de lucru pe care cineva îl
#: „optimizează" mai târziu fără să știe că a fost ales; cine vrea să-l lărgească are nevoie de o
#: decizie nouă, nu de un argument despre volum.
FEREASTRA_ANI = LIMITE_REVERIFICARE["fereastra_ani"]

CLASE_FRECVENTA = ("VOLATIL", "MISCATOR", "STABIL", "NECUNOSCUT")
CLASE_CONSECINTA = ("DEPUS", "CALCULAT", "INFORMATIV", "NECUNOSCUT")

#: Tabelul e al lui Costin; instrumentul îl aplică, nu îl alege. Valorile stau în
#: `LIMITE_REVERIFICARE` de mai sus, împreună cu fereastra și cu proveniența lor.
PRAGURI = LIMITE_REVERIFICARE["praguri_luni"]

#: Modulele de declarație: `d100.py`, `d300.py`, `d406_active.py`… Dacă valoarea ajunge acolo,
#: greșeala pleacă la ANAF.
_RE_MODUL_DECLARATIE = re.compile(r"^d\d{3}[a-z0-9_]*\.py::")

_RE_DATA = re.compile(r"^(\d{2})-(\d{2})-(\d{4})$")


def _azi(azi=None):
    return azi or datetime.date.today()


def date_marcaje(frag):
    """Datele marcajelor de consolidare, ca obiecte `date`. Cele nevalide se ignoră, dar se numără
    separat de «niciun marcaj» — v. `frecventa`, care nu confundă «n-am găsit» cu «nu există»."""
    out = []
    for d, _ce in A.marcaje(frag or ""):
        m = _RE_DATA.match(d)
        if m:
            try:
                out.append(datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1))))
            except ValueError:
                pass
    return sorted(out)


def frecventa(date_mod, azi=None):
    """Clasa A, din datele de modificare ale ARTICOLULUI.

    | clasă | criteriu (decis 23.08.2026) |
    |---|---|
    | VOLATIL  | modificat în cel puțin **2 din ultimii 3 ani** |
    | MISCATOR | modificat **o dată sau de două ori** în fereastră, dar nu în doi ani distincți |
    | STABIL   | **niciun** marcaj în fereastră |

    **O GAURĂ A TABELULUI, ASTUPATĂ DECLARAT:** *trei sau mai multe* modificări în **același** an nu
    intră în niciuna dintre cele trei rânduri, cum sunt scrise. Se clasează **VOLATIL** — direcția
    care verifică mai des, nu mai rar. *Se scrie aici fiindcă e o alegere a instrumentului peste o
    decizie care n-a prevăzut cazul, nu o citire a ei.*
    """
    azi = _azi(azi)
    inceput = azi.replace(year=azi.year - FEREASTRA_ANI)
    in_fereastra = [d for d in (date_mod or []) if d > inceput]
    if not in_fereastra:
        return "STABIL"
    if len({d.year for d in in_fereastra}) >= 2:
        return "VOLATIL"
    return "MISCATOR" if len(in_fereastra) <= 2 else "VOLATIL"


def consecinta(tip, nr, an, art, cale=None, temei=None):
    """Clasa B, din unde ajunge valoarea.

    `DEPUS` dacă atinge un modul de declarație · `CALCULAT` dacă atinge cod, dar nicio declarație ·
    `NECUNOSCUT` dacă n-o atinge nimic — atunci nu se poate spune ce consecință are o valoare
    expirată, iar tăcerea nu e „inofensiv".

    *`INFORMATIV` nu se atribuie niciodată de aici; vezi antetul modulului.*

    **DOUĂ DRUMURI, în ordine** *(06.09.2026, R171)*:
      1. `dependenti_act` — lanțul `articol → cheie din COTE → funcții care cheamă cota()`. Merge
         numai pentru valorile din registrul de cote.
      2. `consumatori_temei` — `temei → numele lui în modul → funcții care îl citesc → cine le
         cheamă`. Pentru temeiurile care trăiesc în **modulul regulii**, unde le pune decizia 73.

    Al doilea drum n-a fost o îmbunătățire, a fost o gaură: **19 din 42** de temeiuri fără prag
    ieșeau NECUNOSCUT *prin construcție*, fiindcă primul lanț se rupe la primul pas pentru orice
    temei din afara lui `COTE`. Aceeași formă de orbire ca la R169, în alt instrument.

    **Pragul nu se ghicește de aici.** Funcția asta răspunde doar la „unde ajunge valoarea"; pragul
    rămâne tabelul din `PRAGURI`, pe perechea (frecvență, consecință). Fără consumator cunoscut,
    consecința rămâne `NECUNOSCUT` **declarat**, iar valoarea rămâne fără prag.
    """
    from core import dependenti_act as da
    try:
        d = da.dependenti(tip=tip, nr=nr, an=an, art=art) or {}
    except Exception:
        d = {}
    fn = d.get("functii") or []
    if fn:
        return "DEPUS" if any(_RE_MODUL_DECLARATIE.match(f) for f in fn) else "CALCULAT"
    if cale:
        from core import consumatori_temei as ct
        try:
            return ct.consumatori(cale, temei)["verdict"]
        except Exception:  # noqa: BLE001
            return "NECUNOSCUT"
    return "NECUNOSCUT"


def categorie(t, azi=None, cale=None):
    """{frecventa, consecinta, prag_luni, motiv, articol, document} pentru un `Temei`.

    `prag_luni` e `None` când oricare axă e `NECUNOSCUT`. **Nu se cade pe pragul global** — asta ar
    fi exact implicitul care minte.
    """
    tip, nr = getattr(t, "tip", None), getattr(t, "nr", None)
    an, art = getattr(t, "an", None), getattr(t, "art", None)
    doc = S.document_tinta(t)
    r = {"articol": S.cheie_articol(tip, nr, an, art), "document": doc,
         "frecventa": "NECUNOSCUT", "consecinta": "NECUNOSCUT", "prag_luni": None, "motiv": None}
    if not art:
        r["motiv"] = "temeiul n-are articol — nu se poate citi frecvența unui articol care nu e numit"
        return r
    if not doc:
        r["motiv"] = "temeiul n-are document — nu se poate citi niciun marcaj"
        return r
    g = A.cauta(doc, art)
    if g["stare"] not in ("GASIT", "ABROGAT"):
        r["motiv"] = ("articolul nu se poate confrunta cu documentul (%s) — v. R107 pentru ciot"
                      % g["stare"])
        return r
    marcaje_art = date_marcaje(g["frag"])
    if not marcaje_art and not A.inregistreaza_modificari(doc):
        r["motiv"] = (
            "documentul nu înregistrează NICIO modificare (zero marcaje de consolidare în tot corpul "
            "lui), deci «niciun marcaj în articol» nu deosebește «nemodificat» de «nu se consemnează "
            "aici» — iar a-l citi ca STABIL ar însemna verificat mai rar dintr-o sursă care nu poate "
            "răspunde")
        return r
    r["frecventa"] = frecventa(marcaje_art, azi)
    r["consecinta"] = consecinta(tip, nr, an, art, cale=cale, temei=t)
    if r["consecinta"] == "NECUNOSCUT":
        r["motiv"] = "nimic din cod nu atinge valoarea — consecința unei expirări nu se poate numi"
        return r
    r["prag_luni"] = PRAGURI[(r["frecventa"], r["consecinta"])]
    return r


def inventar(azi=None):
    """[{cale, temei, ...categorie}] — o intrare per temei unic din registrul de cote."""
    from core import scan_citate
    out = []
    for cale, t, _v in scan_citate.inventar():
        r = {"cale": cale, "temei": str(t)}
        r.update(categorie(t, azi, cale=cale))
        out.append(r)
    return out


def pe_clasa(inv=None, azi=None):
    d = {}
    for x in (inv if inv is not None else inventar(azi)):
        k = (x["frecventa"], x["consecinta"])
        d[k] = d.get(k, 0) + 1
    return d


def fata_de_pragul_global(inv=None, azi=None, global_luni=None):
    """Ce se schimbă față de pragul unic de azi: {mai_strict, mai_larg, la_fel, fara_prag}.

    Pragul global **nu se scrie aici**: se citește de unde trăiește, `expirare_cote._prag_luni()`
    (variabila `CONFIRMARE_COTE_PRAG_LUNI`). Prima formă îl avea ca `6` implicit — un al doilea loc
    pentru aceeași cifră, exact clasa pe care o deschide **R108** două ecrane mai jos.
    """
    if global_luni is None:
        from core.expirare_cote import _prag_luni
        global_luni = _prag_luni()
    d = {"mai_strict": 0, "mai_larg": 0, "la_fel": 0, "fara_prag": 0}
    for x in (inv if inv is not None else inventar(azi)):
        p = x["prag_luni"]
        if p is None:
            d["fara_prag"] += 1
        elif p < global_luni:
            d["mai_strict"] += 1
        elif p > global_luni:
            d["mai_larg"] += 1
        else:
            d["la_fel"] += 1
    return d


def _main():
    inv = inventar()
    for x in sorted(inv, key=lambda y: (y["frecventa"], y["consecinta"], y["temei"])):
        print("  %-11s %-11s prag %-5s  %-30s  %s"
              % (x["frecventa"], x["consecinta"],
                 x["prag_luni"] if x["prag_luni"] is not None else "—",
                 x["temei"][:30], (x["motiv"] or "")[:52]))
    print()
    print("PE CLASA: %s" % {("%s/%s" % k): v for k, v in sorted(pe_clasa(inv).items())})
    print("FATA DE PRAGUL GLOBAL (6 luni): %s" % fata_de_pragul_global(inv))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
