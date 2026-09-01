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

**CRITERIUL DUPĂ CARE SE ATRIBUIE, dat de Costin la închiderea lui R115 (01.09.2026, verbatim):**

  > *„Tăria se dă după dacă diferența admite o explicație legitimă, nu după cine sunt cele două
  > părți. Certă = orice nepotrivire e eroare. Axa orizontală nu devine certă prin faptul că ambele
  > părți sunt declarate."*

**Criteriul e mai important decât valoarea, și de-aia e scris aici.** Întrebarea pe care i-o pusesem
— *„axa orizontală intră la certe, sau certele sunt doar declarație-contra-evidență?"* — era pusă pe
axa greșită: cine sunt părțile nu decide nimic. *Iar răspunsul la întrebarea corectă era deja scris
în `control_incrucisat`, în chiar temeiul comparației ăsteia: „decalaj de exigibilitate (art. 284),
regularizări sau rotunjire — legitim, nu eroare". Am propus CERTA peste o propoziție care spunea,
la o sută de linii distanță, că diferența e legitimă.*

**ÎMPĂRȚIREA PE TĂRII E A LUI COSTIN, PE TIPURI. SUPERVIZORUL NU O DEDUCE** — criteriul se aplică de
om, la înregistrarea tipului, și **rămâne scris** în `motiv_tarie`. De-aia `TIPURI` e un tabel de
**date**, nu o regulă, iar un tip fără tărie atribuită **nu produce niciun efect** — nu cade pe o
valoare implicită, fiindcă *orice implicit minte*. `tarie()` ridică pe un tip necunoscut; un tip
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


#: **TABELUL LUI COSTIN.** `tarie` se completează de el, pe tip, aplicând criteriul din antet.
#: Câmpurile `propus`/`motiv_propunere` sunt ale mele, **n-au niciun efect**, și există numai pe
#: tipurile ÎNCĂ NEATRIBUITE — ca răspunsul lui să ia o tură, nu două. La atribuire ele ies, iar
#: locul lor îl ia **`motiv_tarie`**: criteriul, aplicat în scris, pe tipul ăsta.
#:
#: **`motiv_tarie` e OBLIGATORIU pentru orice tip cu tărie** (gardat). Fără el, un tip nou ar putea
#: primi o tărie prin analogie cu vecinul lui din tabel — adică exact cum am propus eu CERTA:
#: uitându-mă la cine sunt părțile, nu la dacă diferența admite o explicație legitimă.
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
        "tarie": EURISTICA,
        "confirmat": True,
        "motiv_tarie":
            "EURISTICA — **Costin, 01.09.2026**, aplicând criteriul: *diferența admite o explicație "
            "legitimă*, iar explicațiile sunt numite în chiar temeiul comparației "
            "(`control_incrucisat._compara_d390_vs_d300`): decalaj de exigibilitate (art. 284 Cod "
            "fiscal), regularizări, rotunjire. Deci NU orice nepotrivire e eroare, deci nu e certă. "
            "*Faptul că ambele părți sunt declarate n-a contat — a fost întrebarea mea greșită.*",
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
def _culege_firma(conn, schema, an, luna):
    """`(constatari, orizontal_rulat, cauza)` — culegerea BRUTĂ pentru o firmă.

    Culege după **eticheta de tip**, nu după modul: orice funcție, de oriunde, poate emite o
    constatare orizontală dacă o ștampilează cu un tip înregistrat. Asta face perechile o mulțime de
    **date**, nu o listă de apeluri scrisă aici.

    **`orizontal_rulat` NU se deduce, se citește.** `verifica_d390` are o ieșire timpurie (D390 nu se
    poate calcula): atunci axa orizontală nu se atinge niciodată, iar firma întoarce zero constatări
    — **exact ca o firmă pe care axa a rulat și n-a găsit nimic**. Cele două sunt afirmații diferite,
    iar dacă se citesc la fel, tăcerea devine un răspuns. Câmpul lipsă **ridică**: un implicit aici
    ar fi ales tăcut una dintre cele două.
    """
    from core import control_incrucisat as _ci
    rez = _ci.verifica_d390(conn, schema, an, luna) or {}
    brute = rez.get("constatari") or []
    rulat = rez.get("orizontal_rulat")
    if rulat is None:
        raise ValueError(
            "`verifica_d390` n-a declarat `orizontal_rulat` — nu pot ști dacă axa orizontală a rulat "
            "sau doar n-a găsit nimic, iar un implicit ar transforma «n-am verificat» în «e curat»")

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

    cauza = None
    if not rulat:
        cauza = " ".join(str(c.get("mesaj") or c.get("motiv") or "").strip()
                         for c in brute).strip() or "axa orizontală nu s-a atins (cauză nedeclarată)"
    return out, bool(rulat), cauza


def constatari_firma(conn, schema, an, luna):
    """Constatările ORIZONTALE ale unei firme, cu tăria atașată."""
    return _culege_firma(conn, schema, an, luna)[0]


def ruleaza_firma(conn, schema, an, luna):
    """{an, luna, constatari, de_confirmat, tipuri_neatribuite} — pentru o firmă."""
    cs = constatari_firma(conn, schema, an, luna)
    return {"an": an, "luna": luna, "constatari": cs,
            "de_confirmat": [c for c in cs if c["cere_confirmare"]],
            "tipuri_neatribuite": tipuri_neatribuite()}


# ── DOMENIUL: PORTOFOLIUL ──────────────────────────────────────────────────────────────────────
# **DE CE aici, și de ce ACUM (01.09.2026).** Din cele trei fațete pe care `PLAN_LUCRU` le dă
# supervizorului — *„declanșator propriu, domeniu propriu și ieșire proprie"* —, **domeniul e
# singura deja decisă**: *„rulează pe portofoliu, nu pe un act"*. Celelalte două sunt scrise acolo
# ca fiind ale lui Costin și nedecise, iar `core/test_module_nelegate.py` ține modulul NELEGAT
# tocmai din motivul ăsta. Domeniul se poate construi fără să le atingă: funcția e **chemabilă**,
# nu programată și nu rutată. *Ce declanșează o rulare și ce vede contabilul din ea rămân întrebări
# deschise — asta e doar peste ce se uită când rulează.*
#
# **CE FACE IMPOSIBIL, și e singurul motiv pentru care are forma asta.** Un parcurgător de
# portofoliu scris firesc întoarce un contor: *„19 firme, 0 constatări"*. Cifra e **validă și
# falsă** — criteriul de prioritate dat de Costin. Falsă fiindcă strânge la un loc trei lucruri
# care nu seamănă: firme pe care nu s-a găsit nimic, firme care n-au ce compara, și firme pe care
# verificarea **n-a rulat deloc**. *Tiparul nu e presupus:* `core/alerte_control_fiscal.ruleaza()`
# incrementează `tot["firme"]` **după** succes, deci o firmă care ridică nu apare în niciun contor
# al dicționarului întors — se tipărește un `ESEC` la stdout și atât.
#
# Aici: trei rezultate EXCLUSIVE per firmă, iar rezumatul e **derivat** din ele, nu acumulat pe
# drum. O firmă nu poate să dispară dintr-un contor pe care nimeni nu l-a incrementat, fiindcă
# nimeni nu incrementează nimic.

#: Rezultatul unei firme. Cele trei sunt exclusive, și **suma lor e domeniul**.
CONSTATARI = "CONSTATARI"       #: axa a rulat și a produs constatări
FARA_SUBIECT = "FARA_SUBIECT"   #: axa a rulat și n-a avut ce compara (nu «e curat» — n-are subiect)
NEVERIFICAT = "NEVERIFICAT"     #: axa NU a rulat. Firma e NUMITĂ, cu cauza. Niciodată tăcut.
REZULTATE = (CONSTATARI, FARA_SUBIECT, NEVERIFICAT)

#: Criteriul domeniului, scris o dată și RAPORTAT în răspuns. Fără el, „19" s-ar citi ca „toate
#: firmele care există". Nu filtrează pe cabinet — spre deosebire de cronul de alerte, supervizorul
#: nu notifică pe nimeni, deci motivul aceluia de a sări firmele fără cabinet nu se aplică aici.
DOMENIU = ("firmele ACTIVE cu schemă proprie (public.tenants: activ = true, "
           "schema_name ~ '^tenant_[0-9]+$'). NU se filtrează pe cabinet.")


def firme_portofoliu(conn):
    """Domeniul, CITIT din bază. `[{tenant_id, schema, nume}]`, în ordinea id-ului."""
    with conn.cursor() as cur:
        cur.execute("SELECT id, schema_name, nume FROM public.tenants "
                    "WHERE activ = true AND schema_name ~ '^tenant_[0-9]+$' ORDER BY id")
        return [{"tenant_id": r[0], "schema": r[1], "nume": r[2]} for r in cur.fetchall()]


#: Cele două feluri de neverificare. Se ține ca DATE, nu se citește din textul erorii: unul se
#: repară completând profilul firmei, celălalt e un defect al aplicației.
AXA_NU_A_RULAT = "axa_nu_a_rulat"   #: precondiția a căzut (D390 nu se poate calcula) — axa nu s-a atins
EXCEPTIE = "exceptie"               #: ceva a ridicat pe drum — verificarea s-a rupt


def _neverificat(firma, eroare, felul):
    """Afirmația TIPATĂ care spune că firma **n-a fost verificată**, și de ce.

    Felul e `verificare_rupta` din nomenclatorul ÎNCHIS al lui `core/afirmatii.py` — al șaselea,
    adăugat 21.08.2026 pentru exact clasa asta: *„verificarea ÎNSĂȘI s-a oprit. NU e necunoaștere —
    aia ar ascunde-o ca verdict permanent gri"*. `eroare` e obligatorie acolo, și e chiar ce lipsea
    în cronul de alerte, unde firma care ridică se tipărește la stdout și dispare din cifre.
    """
    from core import afirmatii as _af
    return _af.afirmatie(
        "verificare_rupta", "supervizor",
        "Supervizorul NU a verificat firma «%s»: %s" % (firma.get("nume") or firma.get("schema"),
                                                        eroare),
        eroare=str(eroare), felul_neverificarii=felul, schema=firma.get("schema"))


def _domeniu_efectiv(firme, domeniu):
    """PURĂ. Cine primește dreptul de a numi domeniul rulării.

    **DE CE RIDICĂ, în loc să cadă pe `DOMENIU`.** Constanta descrie **tot portofoliul** și spune, în
    text, *„NU se filtrează pe cabinet"*. Dacă `firme` vine din afară — cum vine de pe ruta la
    cerere, unde e mulțimea firmelor CABINETULUI apelantului — iar răspunsul ar căra mai departe
    constanta aia, atunci ar **afirma despre o populație pe care n-a parcurs-o**. *Un domeniu
    nedeclarat se citește ca „toate firmele care există"; un domeniu declarat GREȘIT e mai rău — se
    citește ca o afirmație verificată.*
    """
    if firme is None:
        return domeniu or DOMENIU
    if not (domeniu or "").strip():
        raise ValueError(
            "`firme` injectate fără `domeniu` scris: răspunsul ar purta criteriul întregului "
            "portofoliu («%s») despre o mulțime aleasă de altcineva. Numește ce ai dat." % DOMENIU)
    return domeniu


def ruleaza_portofoliu(an, luna, firme=None, deschide=None, domeniu=None):
    """Supervizorul peste un domeniu de firme, pe o perioadă.

    `firme` / `deschide` se injectează (`deschide(schema)` = context manager de conexiune); implicit,
    domeniul se citește din bază și conexiunile vin din `core.db`. Injecția nu e stil: o probă care
    ține o firmă sintetică într-o tranzacție întoarsă **nu o poate vedea** de pe a doua conexiune,
    deci fără ea căile de eșec n-ar avea cum fi probate — iar ruta la cerere are nevoie de ea ca să
    ruleze pe firmele cabinetului apelantului. **Un domeniu injectat trebuie NUMIT** (`_domeniu_efectiv`).

    **Recalculează la fiecare chemare; nu persistă nimic** *(Costin, 01.09.2026: „constatări deschise
    = ce produce rularea curentă, recalculat la cerere, ca la `/control-fiscal`. Fără tabel nou, fără
    ciclu de viață")*. Un ciclu de viață — *apărut la · încă deschisă* — devine necesar abia când
    există consumatorul lui: stratul asistentului și urmărirea performanței.

    Întoarce `{an, luna, domeniu, firme:[...], rezumat, tipuri_neatribuite}`. **Nu blochează nimic**
    și nu scrie nimic — ca tot restul modulului.
    """
    from core import db as _db
    # ÎNAINTE de orice muncă: dacă domeniul nu se poate numi, nu se rulează deloc.
    domeniu = _domeniu_efectiv(firme, domeniu)
    deschide = deschide or _db.get_conn
    if firme is None:
        with _db.get_conn() as cp:
            firme = firme_portofoliu(cp)

    randuri = []
    for f in firme:
        r = {"tenant_id": f.get("tenant_id"), "schema": f.get("schema"), "nume": f.get("nume"),
             "constatari": [], "de_confirmat": 0, "neverificat": None}
        try:
            with deschide(f["schema"]) as c:
                cs, rulat, cauza = _culege_firma(c, f["schema"], an, luna)
        except Exception as e:
            # NEVERIFICAT, cu numele firmei si cu felul erorii. O firma care ridica NU dispare:
            # asta e chiar clasa masurata in cronul de alerte.
            r["rezultat"] = NEVERIFICAT
            r["neverificat"] = _neverificat(f, "%s: %s" % (type(e).__name__, e), EXCEPTIE)
        else:
            r["constatari"] = cs
            r["de_confirmat"] = sum(1 for c in cs if c["cere_confirmare"])
            if not rulat:
                r["rezultat"] = NEVERIFICAT
                r["neverificat"] = _neverificat(f, cauza, AXA_NU_A_RULAT)
            else:
                r["rezultat"] = CONSTATARI if cs else FARA_SUBIECT
        randuri.append(r)

    # REZUMATUL E DERIVAT din randuri, nu acumulat pe drum: un contor incrementat intr-o ramura
    # poate rata o firma in tacere, o numaratoare peste lista nu poate.
    rezumat = {k: sum(1 for r in randuri if r["rezultat"] == k) for k in REZULTATE}
    rezumat["firme_in_domeniu"] = len(randuri)
    rezumat["de_confirmat"] = sum(r["de_confirmat"] for r in randuri)
    rezumat["constatari_total"] = sum(len(r["constatari"]) for r in randuri)
    return {"an": an, "luna": luna, "domeniu": domeniu, "firme": randuri, "rezumat": rezumat,
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
