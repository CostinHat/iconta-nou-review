# -*- coding: utf-8 -*-
"""SUPERVIZORUL — confruntarea încrucișată ca funcționalitate distinctă a aplicației.

**GAURA MĂSURATĂ (01.09.2026).** Aplicația confruntă mult, dar aproape numai **vertical**: fiecare
declarație față de **propria** sursă. Orizontal — declarație contra declarație — există **o singură**
pereche în tot codul: `control_incrucisat.compara_d390_vs_d300`. *Nouă declarații verificate fiecare
pe verticala ei nu produc nicio afirmație despre coerența dintre ele.* Supervizorul e locul unde stau
perechile orizontale, și singurul care le poate crește ca **date**, nu ca operație pe cod.

**CE E, ca arhitectură** (`PLAN_LUCRU`, „Supervizorul inversează dependența"): confruntarea capătă
declanșator propriu, domeniu propriu (portofoliul) și ieșire proprie. Produce **constatări**, nu
blocaje; depunerea **citește** ce a găsit el, în loc să-l cheme.

**CELE DOUĂ TĂRII** *(Costin, 01.09.2026, verbatim)*:

  - **euristice** — „semnalează, nu opresc niciodată";
  - **certe** — „nepotrivire aritmetică între ce se declară și ce e în evidență … nu blochează, dar
    cer confirmare explicită înainte de depunere, iar confirmarea rămâne scrisă".

**ÎMPĂRȚIREA PE TĂRII E A LUI COSTIN, PE TIPURI. SUPERVIZORUL NU O DEDUCE.** De-aia `TIPURI` e un
tabel de **date**, nu o regulă, iar un tip fără tărie atribuită **nu produce niciun efect** — nu cade
pe o valoare implicită, fiindcă *orice implicit minte*. `tarie()` ridică pe un tip necunoscut; un tip
cunoscut dar neatribuit dă `None`, iar `cere_confirmare()` întoarce `False` pentru el.

CE NU FACE, declarat:
  - **nu blochează nimic, niciodată.** Nici măcar constatările certe: ele cer o **confirmare scrisă**,
    iar poarta de depunere e cea care o citește. Supervizorul nu e a doua poartă.
  - **nu inventează identități fiscale.** O pereche orizontală intră aici doar cu o identitate care
    se poate scrie și verifica. Azi există **una**; restul se adaugă când au temei, nu ca să pară
    plin.
  - **nu compară recalculat cu recalculat** și nu-l declară „declarat". Perechea orizontală citește
    ce s-a **depus** (`declaratii_depuse_curente.randuri`). *Măsurat 01.09: din 55 de depuneri, doar
    1 are rânduri persistate — restul sunt dinainte de F163v2. Calea CURENTĂ le persistă, deci
    populația crește de acum înainte; până atunci, perechea răspunde onest „n-am ce compara".*
"""
import hashlib
import json
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)

#: Nomenclator ÎNCHIS. O a treia tărie ar fi o decizie de arhitectură, nu o valoare nouă.
EURISTICA = "EURISTICA"
CERTA = "CERTA"
TARII = (EURISTICA, CERTA)


class TipNecunoscut(KeyError):
    """Un tip de constatare care nu e în `TIPURI`. NU se cade pe o tărie implicită: o constatare
    fără tărie declarată n-are voie să circule, fiindcă cine o citește n-ar putea ști dacă cere
    confirmare sau doar semnalează."""


#: **TABELUL LUI COSTIN.** `tarie` se completează de el, pe tip. Câmpurile `propus`/`motiv_propunere`
#: sunt ale mele și **nu au niciun efect** — există ca răspunsul lui să ia o tură, nu două.
#:
#: Un tip cu `tarie=None` produce constatări (se văd), dar **nu cere confirmare** și nu atinge
#: depunerea. Așa, nimic nu se blochează așteptând un răspuns, și nimic nu se aplică fără el.
TIPURI = {
    "D390_VS_D300_IC": {
        "axa": "ORIZONTALA",
        "ce": "Bazele intracomunitare din D390 (recapitulativa VIES) față de rândurile "
              "intracomunitare ale D300 EFECTIV DEPUS.",
        "identitate": "baza D390 (L, A) == rândurile IC ale D300 depus, pe aceeași perioadă",
        "sursa_stanga": "recalcul D390 pe perioada D300 depus",
        "sursa_dreapta": "public.declaratii_depuse_curente.randuri (ce s-a depus)",
        "tarie": None,
        "confirmat": False,
        "propus": CERTA,
        "motiv_propunere":
            "E o nepotrivire ARITMETICĂ între două cifre declarate. Definiția dată de Costin spune "
            "«între ce se declară și ce e în evidență»; aici amândouă părțile sunt declarate, deci "
            "nu e acoperită literal. ÎNTREBAREA CARE RĂMÂNE A LUI: axa orizontală intră la CERTE, "
            "sau certele sunt doar declarație-contra-evidență?",
    },
}


def tarie(tip):
    """Tăria unui tip. `None` = neatribuită încă. Ridică pe tip necunoscut — niciodată implicit."""
    if tip not in TIPURI:
        raise TipNecunoscut(
            "tip de constatare neînregistrat: %r. Un tip nou intră în `TIPURI` ÎMPREUNĂ cu tăria "
            "lui, altfel constatarea circulă fără să se știe dacă cere confirmare." % (tip,))
    t = TIPURI[tip].get("tarie")
    if t is not None and t not in TARII:
        raise ValueError("tărie nevalidă pentru %r: %r (cele două sunt %s)" % (tip, t, ", ".join(TARII)))
    return t


def cere_confirmare(tip):
    """Constatarea de tipul ăsta cere confirmare scrisă înainte de depunere?

    **DOAR** dacă tăria e `CERTA` **și** e confirmată de Costin. Un tip propus dar neconfirmat nu
    are niciun efect — propunerea mea nu are voie să devină regulă prin trecerea timpului."""
    return TIPURI[tip].get("confirmat", False) and tarie(tip) == CERTA


def tipuri_neatribuite():
    """Tipurile care așteaptă tăria. Se raportează, nu se ascund."""
    return sorted(t for t in TIPURI if TIPURI[t].get("tarie") is None)


# ── AMPRENTA unei constatări ───────────────────────────────────────────────────────────────────
#: Câmpurile care fac IDENTITATEA unei constatări. **Nu** mesajul: o reformulare n-are voie să
#: invalideze o confirmare, iar o cifră schimbată TREBUIE s-o invalideze.
_CAMPURI_AMPRENTA = ("tip_constatare", "eticheta", "stare", "declarat_d390", "declarat_d300",
                     "diferenta")


def amprenta(constatare):
    """SHA-256 peste cifrele constatării, nu peste proza ei.

    **De ce contează:** confirmarea se dă pe o nepotrivire ANUME, nu pe un tip. Dacă cifrele se
    schimbă după confirmare, amprenta se schimbă, iar confirmarea veche **nu se mai potrivește** —
    deci nu acoperă tăcut o divergență nouă. *Asta e deosebirea dintre „am confirmat că știu de
    diferența de 1.200 lei" și „am confirmat tipul ăsta de constatare, o dată, pentru totdeauna".*
    """
    d = {k: constatare.get(k) for k in _CAMPURI_AMPRENTA if k in constatare}
    if "tip_constatare" not in d:
        raise TipNecunoscut("constatare fără `tip_constatare` — nu i se poate calcula amprenta")
    tarie(d["tip_constatare"])   # ridică dacă tipul nu e înregistrat
    s = json.dumps(d, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:32]


# ── CULEGEREA constatărilor orizontale ─────────────────────────────────────────────────────────
def constatari_firma(conn, schema, an, luna):
    """Constatările ORIZONTALE ale unei firme, cu tăria atașată.

    Culege după **eticheta de tip**, nu după modul: orice funcție, de oriunde, poate emite o
    constatare orizontală dacă o ștampilează cu un tip înregistrat. Asta face perechile o mulțime de
    **date**, nu o listă de apeluri scrisă aici.
    """
    from core import control_incrucisat as _ci
    brute = []
    rez = _ci.verifica_d390(conn, schema, an, luna)
    brute += (rez or {}).get("constatari") or []

    out = []
    for c in brute:
        tip = c.get("tip_constatare")
        if not tip:
            continue                      # constatare VERTICALĂ — nu e treaba supervizorului
        c = dict(c)
        c["tarie"] = tarie(tip)
        c["cere_confirmare"] = cere_confirmare(tip) and c.get("stare") == "rosu"
        c["amprenta"] = amprenta(c)
        out.append(c)
    return out


def ruleaza_firma(conn, schema, an, luna):
    """{an, luna, constatari, de_confirmat, tipuri_neatribuite} — pentru o firmă."""
    cs = constatari_firma(conn, schema, an, luna)
    return {"an": an, "luna": luna, "constatari": cs,
            "de_confirmat": [c for c in cs if c["cere_confirmare"]],
            "tipuri_neatribuite": tipuri_neatribuite()}


# ── CONFIRMAREA, care rămâne SCRISĂ ────────────────────────────────────────────────────────────
def scrie_confirmare(conn, tenant_id, an, luna, constatare, confirmat_de, confirmat_de_id, motiv):
    """Consemnează confirmarea unei constatări CERTE. Nu comite — comiterea e a apelantului.

    Se scrie **amprenta**, nu doar tipul: confirmarea acoperă cifrele văzute atunci."""
    if not motiv or not str(motiv).strip():
        raise ValueError("confirmarea cere un motiv scris — o confirmare fără motiv e o bifă, "
                         "iar o bifă nu se poate citi peste șase luni")
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO public.supervizor_confirmari "
            "(tenant_id, an, luna, tip_constatare, amprenta, confirmat_de, confirmat_de_id, motiv) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) "
            "ON CONFLICT (tenant_id, an, luna, tip_constatare, amprenta) DO NOTHING",
            (tenant_id, an, luna, constatare["tip_constatare"], constatare["amprenta"],
             confirmat_de, confirmat_de_id, str(motiv).strip()))


def confirmari(conn, tenant_id, an, luna):
    """{(tip, amprenta): {confirmat_de, confirmat_la, motiv}} — ce s-a confirmat deja."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT tip_constatare, amprenta, confirmat_de, confirmat_la, motiv "
            "FROM public.supervizor_confirmari WHERE tenant_id=%s AND an=%s AND luna=%s",
            (tenant_id, an, luna))
        return {(t, a): {"confirmat_de": cd, "confirmat_la": cl, "motiv": m}
                for t, a, cd, cl, m in cur.fetchall()}


def neconfirmate(conn, schema, tenant_id, an, luna):
    """Constatările CERTE care cer confirmare și **încă n-au una potrivită pe amprentă**.

    Asta citește poarta de depunere. Lista goală = nimic de confirmat, NU „totul e verde"."""
    date = confirmari(conn, tenant_id, an, luna)
    return [c for c in constatari_firma(conn, schema, an, luna)
            if c["cere_confirmare"] and (c["tip_constatare"], c["amprenta"]) not in date]
