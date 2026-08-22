# -*- coding: utf-8 -*-
"""core/baza_cm.py — baza indemnizatiei de concediu medical vine din statele EMISE. (22.08.2026)

DECIS DE COSTIN: **emis**, nu recalcul. Acelasi motiv ca la fluturas: ce s-a platit efectiv e un FAPT.
Media legala (OUG 158/2005 art.10 al.4) se face pe ce a PRIMIT omul in cele 6 luni anterioare, nu pe
ce ar rezulta din calculul de azi. Daca intre timp s-a schimbat o cota sau salariul minim, recalculul
da alte venituri decat cele de pe fluturasii deja dati - iar indemnizatia s-ar calcula pe o realitate
care n-a existat niciodata.

DE CE ARGUMENTUL VECHI NU MAI TINE. Pana pe 20.08, ruta citea baza din `state_plata`, iar tabelul era
populat ca EFECT SECUNDAR al unui GET /stat-plata: media depindea de ce luni deschisese cineva in
interfata, iar lunile nedeschise lipseau TACIT. Reparatia de atunci - „calculeaza, nu citi" - era
corecta pentru tabelul de atunci, un cache de navigare. Din 21.08 `state_plata` e REGISTRUL
DOCUMENTELOR EMISE, cu amprenta si exemplare. Sursa s-a schimbat sub argument, deci argumentul cade.

REGULA, in trei parti:
  1. luna EMISA intra cu cifrele EMISE;
  2. luna NEEMISA intra cu recalculul - dar se NUMARA separat si se spune, ca sa nu se amestece tacit
     doua feluri de cifre in aceeasi medie;
  3. daca nicio luna nu e emisa, comportamentul e cel dinainte - firmele care inca nu emit nu se rup.
"""


def luni_anterioare(an, luna, cate=6):
    """Cele `cate` luni dinaintea lunii certificatului, in ordine cronologica."""
    out = []
    for i in range(cate, 0, -1):
        m = luna - i
        out.append((an - 1, m + 12) if m <= 0 else (an, m))
    return out


def aduna(luni, emise, recalculate, zile_lucratoare):
    """PURA. Aduna veniturile si zilele lucrate, preferand cifrele EMISE.

    `emise` / `recalculate`: {(an, luna): {"brut": float, "cm_zile": int}}.
    `zile_lucratoare(an, luna)` -> int (zile lucratoare FARA sarbatori, OUG 158/2005 art.10).

    Intoarce {venituri, zile, nr_luni, luni_emise, luni_recalculate, luni_lipsa, temei}.
    `temei` spune PE CE s-a facut media - fara el, contabilul vede o cifra si nu stie din ce vine."""
    venituri, zile = 0.0, 0
    n_emise = n_recalc = n_lipsa = 0
    for a, l in luni:
        r, e_emisa = emise.get((a, l)), True
        if r is None:
            r, e_emisa = recalculate.get((a, l)), False
        if r is None:
            n_lipsa += 1
            continue
        zl = max(int(zile_lucratoare(a, l)) - int(r.get("cm_zile") or 0), 0)
        if zl <= 0:
            continue                     # luna integral in CM: n-are zile lucrate, nu intra in medie
        venituri += float(r.get("brut") or 0)
        zile += zl
        n_emise += int(e_emisa)
        n_recalc += int(not e_emisa)

    if n_emise and n_recalc:
        temei = ("media pe %d luni: %d din statele EMISE (cifrele de pe fluturașii dați), %d "
                 "recalculate (lunile neemise)" % (n_emise + n_recalc, n_emise, n_recalc))
    elif n_emise:
        temei = "media pe %d luni, toate din statele EMISE (cifrele de pe fluturașii dați)" % n_emise
    elif n_recalc:
        temei = ("media pe %d luni RECALCULATE - niciuna dintre luni nu are stat emis, deci cifrele "
                 "pot diferi de ce s-a plătit efectiv" % n_recalc)
    else:
        temei = "nicio lună lucrată în intervalul cerut"
    if n_lipsa:
        temei += "; %d luni fără nicio sursă (salariatul nu era angajat sau datele lipsesc)" % n_lipsa

    return {"venituri": venituri, "zile": zile, "nr_luni": n_emise + n_recalc,
            "luni_emise": n_emise, "luni_recalculate": n_recalc, "luni_lipsa": n_lipsa,
            "temei": temei}


def culege(conn, schema, salariat_id, luni):
    """Citeste, pentru fiecare luna, exemplarul EMIS si (daca lipseste) recalculul.

    NU scrie nimic: clasa a fost deja arsa o data pe exact tabelul asta - o sonda „de citire" a lasat
    24 de randuri in `state_plata` (`test_get_fara_scriere`)."""
    from core import stat_plata_api as _sp
    from core import stat_plata_emis as _spe
    emise, recalc = {}, {}
    for a, l in luni:
        try:
            ex = _spe.citeste(conn, schema, a, l, salariat_id=salariat_id)
        except Exception:
            ex = []      # MASCA MOTIVATA: tenant nemigrat -> nu exista exemplare, se cade pe recalcul
        if ex:
            emise[(a, l)] = max(ex, key=lambda x: x["exemplar"])["date"]
            continue
        try:
            stat = _sp.stat_plata(conn, schema, a, l)
        except Exception:
            continue     # MASCA MOTIVATA: luna necalculabila (date lipsa) - nu o inventez
        r = next((x for x in stat if int(x.get("id") or 0) == salariat_id), None)
        if r is not None:
            recalc[(a, l)] = r
    return emise, recalc
