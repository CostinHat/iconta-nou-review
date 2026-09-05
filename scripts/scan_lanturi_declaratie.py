# -*- coding: utf-8 -*-
"""ETAPA 2 — CARE unitate alimentează CARE declarație, derivat din cod.

DE CE EXISTĂ. Comanda etapei 2 (Costin, 05.09.2026) cere gruparea **pe declarație, nu pe
funcționalitate**: *„toate unitățile care alimentează aceeași declarație se probează într-o
singură generare a ei, cu toate așteptările verificate deodată."* `LISTA_FUNCTIONALITATI.md`
răspunde doar `da/nu/?` la întrebarea *„atinge date care ajung într-o declarație"* — nu spune
**care** declarație. Aici se calculează exact asta.

CUM SE DERIVĂ — aceeași logică ca la coloana `da/nu/?`, dar **per generator**, nu peste tot:

  1. **generatoarele** = numai **cele nouă** pe care aplicația le produce, tăiate de Costin
     (05.09.2026): D100, D101, D112, D205, D300, D301, D390, D394, D406/SAF-T. Modulele-bucată
     (`d300_manual_api`, `d390_clasificare_api`, `d406_active`, `saft`…) se pliază peste
     declarația lor, pe PREFIX. Ce rămâne pe dinafară — `bilant`, `bilant_api`, și cele ~40 de
     module `dNNN` fără generator probat — se **numește** în `in_afara()`, nu se ascunde;
  2. pentru fiecare generator, **tabelele pe care le citește** — el și modulele pe care le importă
     la UN nivel (aceeași închidere ca la coloana existentă, și din același motiv: nivelul 2
     degenerează, `da` la tot);
  3. o unitate **alimentează** generatorul dacă îl cheamă ea însăși, **sau** dacă scrie într-un
     tabel pe care el îl citește.

**Nimic nu se rescrie**: `module_declaratie`, `_importuri_core`, `tabele_declaratie`,
`scrie_unitatea` și `rute` se împrumută de la `scan_functionalitati`, iar tabelele cunoscute și
scrierile de la `scan_trasee`. A doua definiție a aceluiași lucru e începutul unei divergențe
tăcute — regula e deja scrisă în `scripts/curatenie.py`, pe alt obiect.

CE NU VEDE, declarat:
  · o unitate care scrie printr-un SQL construit din bucăți la rulare (limita moștenită de la
    `scan_trasee.RE_W`) — la fel ca în coloana existentă;
  · **suprapunerea e reală, nu o eroare**: `inregistrari` e citit de aproape toate generatoarele,
    deci o rută care scrie o notă apare în mai multe grupuri. Asta ESTE lanțul, nu zgomot;
  · **cele trei rute generice** (`GET /declaratii/tipuri`, `POST /declaratii/{tip}`,
    `POST /declaratii/{tip}/valideaza`) nu alimentează o declarație anume: ele SUNT actul de
    generare, comun tuturor celor nouă. Se raportează separat, ca `ACTUL DE GENERARE`;
  · legătura e „poate ajunge", nu „ajunge sigur": tabelul citit de generator nu înseamnă că
    valoarea scrisă azi apare în declarația de mâine. **De-aia proba scrie așteptarea ÎNAINTE** —
    instrumentul dă lista de probat, nu verdictul.

CUM SE RULEAZĂ:
    ./venv/bin/python scripts/scan_lanturi_declaratie.py            # sumarul pe declarații
    ./venv/bin/python scripts/scan_lanturi_declaratie.py d300       # unitățile unei declarații
    ./venv/bin/python scripts/scan_lanturi_declaratie.py --md       # tabelul, pentru registru
"""
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)

from scripts import scan_functionalitati as F  # noqa: E402
from scripts import scan_trasee as T  # noqa: E402

#: CELE NOUĂ, tăiate de Costin (05.09.2026): *„Etapa 2 se probează doar pe declarațiile pe care
#: aplicația le GENEREAZĂ … doar cele nouă pentru care există generator în cod."* Perimetrul nu se
#: mai ia din nomenclator și nici din tabelele citite: se ia de aici.
CELE_NOUA = ("d100", "d101", "d112", "d205", "d300", "d301", "d390", "d394", "d406")

#: Purtătorii de lanț NU sunt declarații: `declaratii_api` le cheamă pe toate.
PURTATORI = ("declaratii_api", "declaratii_componente")

#: Modulul care poartă SAF-T; se pliază peste D406, fiindcă e aceeași ieșire (D406/SAF-T).
SAFT = "saft"


def declaratia(modul):
    """Cărei declarații îi aparține un modul — pe PREFIX, nu pe listă scrisă de mână.

    `d300_manual_api`, `d300_reconciliere` nu sunt declarații: sunt bucăți ale lanțului D300, și
    tabelele pe care le citesc sunt tot ale lui. Regula e structurală, deci un `d300_ceva` nou
    intră singur. `saft` se pliază peste `d406` (aceeași ieșire)."""
    if modul == SAFT:
        return "d406"
    m = re.match(r"^(d\d+)", modul)
    if not m:
        return None
    baza = m.group(1)
    return baza if baza in CELE_NOUA else None


def generatoare():
    """{declarație: [modulele care o compun]} — numai cele nouă. Restul se numesc, nu se ascund."""
    out = {}
    for m in sorted(F.module_declaratie()):
        if m in PURTATORI:
            continue
        d = declaratia(m)
        if d:
            out.setdefault(d, []).append(m)
    return out


def in_afara():
    """Modulele de declarație care NU intră în etapa 2, cu motivul — nu se trec sub tăcere."""
    out = {}
    for m in sorted(F.module_declaratie()):
        if m in PURTATORI:
            out[m] = "purtător de lanț, nu generator (le cheamă pe toate)"
        elif not declaratia(m):
            out[m] = ("nu e una din cele nouă cu generator probat în etapa 2"
                      if re.match(r"^d\d+", m) else "ieșire proprie, în afara celor nouă")
    return out


def consumatori():
    """Modulele care CITESC declarații ca să le confrunte — nu le hrănesc.

    Un comparator citește tot portofoliul, deci, prin închiderea de un nivel, lipește tot
    portofoliul de fiecare declarație care-l importă. Măsurat în lotul D: nucleul lui D112
    ieșea **81**, cu `/asistenti/*`, `/coada` și `DELETE /tenants/{id}` în el — fiindcă
    `d112.py` importă `control_incrucisat`, nu fiindcă ar citi el `tenants`.

    REGULA E DERIVATĂ, nu o listă: un modul importat de un generator, care nu e el însuși
    parte dintr-un generator și care importă generatoare din **două sau mai multe familii**
    de declarații. Azi întoarce exact unul — `control_incrucisat`. Unul care citește o
    singură familie (`inchidere_luna` → `d390`) NU e prins, și e corect: acela chiar
    hrănește lanțul acelei declarații."""
    gen = generatoare()
    module_gen = {m for lst in gen.values() for m in lst}
    familia = {m: d for d, lst in gen.items() for m in lst}
    out = set()
    for m in sorted(module_gen):
        for imp in F._importuri_core(m):
            if imp in module_gen:
                continue
            if len({familia[x] for x in (F._importuri_core(imp) & module_gen)}) >= 2:
                out.add(imp)
    return out


def tabele_per_generator(cunoscute):
    """{declarație: {tabele citite de modulele ei sau de cele importate la un nivel}}.

    Consumatorii (v. `consumatori()`) se SCOT din închidere: ei confruntă declarații, nu le
    hrănesc. Măsurat: cu ei înăuntru, d112 avea 16 tabele și nucleu 81; fără ei, 7 și 24.
    Nucleul total (unități distincte) trece de la 103 la 72."""
    fara = consumatori()
    out = {}
    for d, module in generatoare().items():
        h = set()
        for m in module:
            h |= F._importuri_core(m)
        out[d] = F.tabele_declaratie(set(module) | (h - fara), cunoscute)
    return out


#: Un tabel citit de MULTE generatoare nu spune nimic despre CARE declarație e alimentată.
#: Pragul e măsurat, nu ales: `inregistrari` și `inregistrari_linii` sunt citite de 30+ generatoare
#: (orice notă contabilă intră, până la urmă, în orice declarație care citește note), în timp ce
#: `d300_manual` sau `d390_reclasificare` sunt citite de câte unul. Sub prag = **specific**.
PRAG_SPECIFIC = 5


def specificitate(tabg):
    """{tabel: câte generatoare îl citesc}. Ce e citit de puține e semnătura unei declarații."""
    n = {}
    for tabele in tabg.values():
        for t in tabele:
            n[t] = n.get(t, 0) + 1
    return n


def lanturi():
    """(unitati, per_declaratie, tabele, specificitate) — unitățile care alimentează fiecare
    generator, fiecare marcată **NUCLEU** sau **PERIFERIE**.

    DE CE DOUĂ FELURI, măsurat înainte de a alege. Atribuirea pe „scrie într-un tabel pe care
    generatorul îl citește" DEGENEREAZĂ: `inregistrari` e citit de aproape toate generatoarele,
    deci orice rută care scrie o notă „alimentează" 30 de declarații. Măsurat: cea mai mare grupă
    are **171** de unități, iar suma apartenențelor e **2204** pentru 194 de unități distincte —
    adică fiecare unitate ar intra, în medie, în unsprezece loturi. *O grupare în care aproape
    totul aparține aproape peste tot nu grupează nimic.*

    Deosebirea se face pe **specificitatea tabelului**, nu pe judecată: o unitate e în **NUCLEUL**
    unei declarații dacă scrie într-un tabel pe care îl citesc mai puțin de `PRAG_SPECIFIC`
    generatoare (sau dacă cheamă chiar generatorul); altfel e în **PERIFERIE** — ajunge acolo, dar
    prin drumul comun al notei contabile.

    *Nucleul dă lotul; periferia se probează prin declarația căreia îi e nucleu.*
    """
    r, _grup, mod, _decl, _tab, _orf, _dub = F.construieste()
    cunoscute = T.tabele_cunoscute()
    tabg = tabele_per_generator(cunoscute)
    spec = specificitate(tabg)
    per = {g: {"nucleu": [], "periferie": []} for g in tabg}
    for x in r:
        if x.get("_decl") != "da":
            continue
        scrise = F.scrie_unitatea(x, mod)
        module_rutei = set(x.get("module") or [])
        x["_gen"] = []
        for g, tabele in tabg.items():
            comune = scrise & tabele
            if not comune and not (set(generatoare()[g]) & module_rutei):
                continue
            fel = ("nucleu" if (set(generatoare()[g]) & module_rutei
                                or any(spec.get(t, 99) < PRAG_SPECIFIC for t in comune))
                   else "periferie")
            per[g][fel].append(x)
            x["_gen"].append((g, fel))
    return r, per, tabg, spec


def _cheie(x):
    return "%s %s" % (x["metoda"], x["cale"])


def main():
    r, per, tabg, spec = lanturi()
    cerute = [a for a in sys.argv[1:] if not a.startswith("--")]
    da = [x for x in r if x.get("_decl") == "da"]
    fara = [x for x in da if not x.get("_gen")]

    if cerute:
        for g in cerute:
            lst = per.get(g)
            if lst is None:
                print("necunoscut: %s — cunoscute: %s" % (g, ", ".join(sorted(per))))
                continue
            print("=== %s — nucleu %d · periferie %d · %d tabele citite"
                  % (g, len(lst["nucleu"]), len(lst["periferie"]), len(tabg[g])))
            print("    tabele (citite de câte generatoare): %s"
                  % ", ".join("%s×%d" % (t, spec.get(t, 0)) for t in sorted(tabg[g])))
            for fel in ("nucleu", "periferie"):
                print("  -- %s (%d)" % (fel.upper(), len(lst[fel])))
                for x in sorted(lst[fel], key=_cheie):
                    print("     %-6s %-56s %s" % (x["metoda"], x["cale"], x["fn"]))
        return 0

    print("UNITĂȚI cu «atinge o declarație» = da: %d" % len(da))
    print("din care ATRIBUITE cel puțin unui generator: %d" % (len(da) - len(fara)))
    nuc = {id(x) for g in per for x in per[g]["nucleu"]}
    print("unități care sunt NUCLEU pentru cel puțin o declarație: %d" % len(nuc))
    print()
    viu = [g for g in per if per[g]["nucleu"] or per[g]["periferie"]]
    for g in sorted(viu, key=lambda k: -len(per[k]["nucleu"])):
        print("  %-22s nucleu %3d · periferie %3d · %2d tabele"
              % (g, len(per[g]["nucleu"]), len(per[g]["periferie"]), len(tabg[g])))
    print("\nCONSUMATORI scoși din închidere (compară declarații, nu le hrănesc): %s"
          % (", ".join(sorted(consumatori())) or "niciunul"))
    print("\nTABELE COMUNE (citite de %d+ generatoare — nu spun care declarație):"
          % PRAG_SPECIFIC)
    print("  " + ", ".join("%s×%d" % (t, n) for t, n in
                           sorted(spec.items(), key=lambda kv: -kv[1]) if n >= PRAG_SPECIFIC))
    afara = in_afara()
    print("\nÎN AFARA CELOR NOUĂ — module de declarație fără generator probat în etapa 2: %d"
          % len(afara))
    print("  " + ", ".join(sorted(afara)))
    if fara:
        # Nu se rotunjește la „nu", și nici nu se lasă ca „dezacord": cele două feluri se
        # deosebesc pe CONȚINUT. Rutele generice de declarație sunt **actul de generare**, comun
        # tuturor celor nouă — nu alimentează una anume. Restul alimentează o ieșire din afara
        # celor nouă (bilanțul, `s1003`/`s1005`), și atât se poate spune despre ele.
        generice = [x for x in fara if x["cale"].startswith("/declaratii/")]
        altele = [x for x in fara if x["cale"] not in {y["cale"] for y in generice}]
        print("\nACTUL DE GENERARE — comun tuturor celor nouă, nu al uneia (%d):" % len(generice))
        for x in sorted(generice, key=_cheie):
            print("  %-6s %-58s %s" % (x["metoda"], x["cale"], x["fn"]))
        if altele:
            print("\nALIMENTEAZĂ O IEȘIRE DIN AFARA CELOR NOUĂ (%d) — bilanțul S1003/S1005, care "
                  "nu e între cele nouă:" % len(altele))
            for x in sorted(altele, key=_cheie):
                print("  %-6s %-58s %s" % (x["metoda"], x["cale"], x["fn"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
