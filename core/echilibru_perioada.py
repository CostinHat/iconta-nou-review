# -*- coding: utf-8 -*-
"""
core/echilibru_perioada.py — C3 (integritate in TIMP): partida dubla la nivel de PERIOADA/tenant + orfani.

A DOUA CALE pentru ce DUK NU verifica: DUK accepta un GL (SAF-T / registru) STRUCTURAL valid dar cu Sigma debit !=
Sigma credit (descoperit la tura 10: TotalDebit 0 vs TotalCredit 15000 trecea DUK).

[R33 varianta b'', 26.08.2026] Modulul e LEGAT din main._verificari_contabile. Pana azi era scris aici -- si in alte
patru registre -- ca ar fi "a doua implementare" a lui verificatoare.verifica_balanta. Masurat pe aceleasi date
(25.08.2026): NU E. Modurile de esec sunt DISJUNCTE -- aici se prinde linia cu o parte lipsa si orfanul, acolo se
prind soldurile initiale dezechilibrate, si fiecare o rateaza pe cealalta. Cele doua se compun intr-un SINGUR
verdict (verdict_echilibru mai jos); contabilul vede o singura verificare, "Echilibru", cu ce a gasit fiecare.
Egalitatea Sigma debit = Sigma credit se verifica DOAR aici: ramura ei din verifica_balanta era tautologica pe
intrarea reala (0 din 2000 de seturi) si a fost scoasa. Aici:
- echilibru_perioada(linii): Sigma(suma pe cont_debit) == Sigma(suma pe cont_credit) - o linie cu o parte lipsa
  (debit SAU credit gol) rupe egalitatea = eroare de integritate (retroactiv / import stricat / editare in luna).
- orfani(linii, id_uri): linii care trimit la o inregistrare inexistenta.
PUR (primeste linii), deci testabil fara DB; un reader DB subtire (echilibru_perioada_db) il aplica pe perioada.
LIMITA declarata: nu e snapshot+hash (regenerare-diff a declaratiei depuse) - aia e alta felie C3 (state_plata
snapshot DECIS in GARZI INVENTAR A). Aici doar invariantul contabil Sigma debit=Sigma credit + orfani.
"""
from decimal import Decimal

# [R33 b''] Vocabularul constatarilor, INTR-UN SINGUR LOC (P1). Nu e cosmetica: pana la el,
# fiecare `fel` traia ca sir repetat in motor, in garda si in randor, iar clichetul 50 a prins
# doua aserttiuni ancorate pe text. Un `fel` nou se adauga AICI si nicaieri altundeva.
FEL_LEDGER = "ledger_dezechilibrat"      # partida dubla rupta pe liniile perioadei
FEL_ORFANI = "orfani"                    # linii care trimit la o inregistrare inexistenta
FEL_SOLDURI = "solduri_dezechilibrate"   # soldurile initiale nu se inchid
FEL_NEVERIFICAT = "neverificat"          # verificarea n-a rulat (P6: nu e „in regula")
FELURI = (FEL_LEDGER, FEL_ORFANI, FEL_SOLDURI, FEL_NEVERIFICAT)
# LIMITA DECLARATA: randorul (`static/js/ecrane/firme.js`, `detaliuEchilibru`) isi tine propria
# mapare fel -> propozitie, fiindca JS nu poate importa de aici. Un `fel` nou nu rupe ecranul (are
# ramura de rezerva `esc(x.fel)`), dar apare nefrumos pana i se scrie propozitia.


def _d(x):
    if isinstance(x, Decimal):
        return x
    return Decimal(str(x or 0))


def _are_cont(v):
    """Un cont e PREZENT doar daca ramane ceva dupa strip. [R33 b'', 26.08.2026]

    Pana azi testul era `if l.get("cont_debit")`, iar un sir format din SPATII e ADEVARAT in
    Python -- deci `"   "` numara drept cont prezent si dezechilibrul devenea invizibil.
    Nu e ipotetic: masurat pe 26.08, 12 locuri din cod scriu contul cu tiparul
    `str(corp.get("cont_x") or "<implicit>")`, FARA strip -- deci spatiile ajung in baza
    verbatim. `NOT NULL` nu le opreste, un `CHECK (cont <> '')` nu le-ar opri, si probat pe
    schema efemera: niciuna dintre cele doua verificari nu le vedea."""
    return bool((v or "").strip() if isinstance(v, str) else v)


def echilibru_perioada(linii):
    """PUR. linii = [{cont_debit, cont_credit, suma}, ...]. Intoarce (sigma_debit, sigma_credit, echilibrat: bool).
    O partida dubla corecta: fiecare linie are AMBELE conturi si aceeasi suma pe debit si credit -> egale. Daca o
    linie are o parte lipsa (cont gol, NULL sau numai spatii), suma ei intra doar pe o parte -> Sigma-le difera."""
    sd = sum((_d(l.get("suma")) for l in linii if _are_cont(l.get("cont_debit"))), Decimal(0))
    sc = sum((_d(l.get("suma")) for l in linii if _are_cont(l.get("cont_credit"))), Decimal(0))
    return sd, sc, sd == sc


def orfani(linii, id_uri_inregistrari):
    """PUR. Linii al caror inregistrare_id NU e in setul de inregistrari existente (referinta rupta)."""
    valide = set(id_uri_inregistrari or ())
    return [l for l in linii if l.get("inregistrare_id") not in valide]


def echilibru_perioada_db(conn, schema, an, luna, doar_validate=True):
    """Reader DB subtire: aplica echilibru_perioada + orfani pe liniile perioadei (note validate). Intoarce dict cu
    starea. NU ridica - semnaleaza (jobul consuma rezultatul; hard-block la nevoie de apelant)."""
    inceput = "%04d-%02d-01" % (an, luna)
    sfarsit = ("%04d-01-01" % (an + 1,)) if luna == 12 else ("%04d-%02d-01" % (an, luna + 1))
    filtru = "AND i.status = 'validata'" if doar_validate else ""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT l.inregistrare_id, l.cont_debit, l.cont_credit, l.suma "
            "FROM %s.inregistrari_linii l JOIN %s.inregistrari i ON i.id = l.inregistrare_id "
            "WHERE i.data >= %%s AND i.data < %%s %s" % (schema, schema, filtru),
            (inceput, sfarsit))
        linii = [{"inregistrare_id": r[0], "cont_debit": r[1], "cont_credit": r[2], "suma": r[3]} for r in cur.fetchall()]
        cur.execute("SELECT id FROM %s.inregistrari" % schema)
        id_uri = {r[0] for r in cur.fetchall()}
    sd, sc, echilibrat = echilibru_perioada(linii)
    orf = orfani(linii, id_uri)
    return {"an": an, "luna": luna, "sigma_debit": sd, "sigma_credit": sc,
            "echilibrat": echilibrat, "diferenta": sd - sc, "orfani": len(orf)}


def verdict_echilibru(rez_perioada, problema_solduri, perioada=None):
    """PURA. UN SINGUR verdict `echilibru`, compus LA CONSTRUCTIE din cele doua verificari.

    [R33 varianta b'', decizia lui Costin 26.08.2026] *"La ecran: cele doua se arata ca una
    singura, «echilibru», cu ce a gasit fiecare. Contabilul nu trebuie sa stie ca sunt doua
    module."*

    De ce se compune AICI si nu la randare: un verdict carpit dupa constructie are doua surse
    (aceeasi clasa cu VERDICT_COLAPSAT din verificator). Si de ce constatarile sunt OBIECTE, nu
    fraze: dintr-o propozitie cifrele nu se pot compune inapoi (DS cap.13).

      rez_perioada     = ce intoarce echilibru_perioada_db(...), sau None daca n-a putut rula
      problema_solduri = ce intoarce verificatoare.verifica_balanta(bal)

    Intoarce {ok, constatari:[...]}. `ok` e ADEVARAT numai daca AMANDOUA au trecut si amandoua
    au rulat -- o verificare care n-a rulat NU se rotunjeste la "in regula" (P6: verdele
    afirma; necunoscutul domina favorabilul)."""
    constatari = []
    a_rulat_perioada = isinstance(rez_perioada, dict) and "echilibrat" in rez_perioada

    if not a_rulat_perioada:
        constatari.append({"fel": FEL_NEVERIFICAT, "ce": "partida dubla pe perioada",
                           "motiv": (rez_perioada or {}).get("eroare") if isinstance(rez_perioada, dict)
                                    else "verificarea nu a rulat"})
    else:
        if not rez_perioada.get("echilibrat"):
            constatari.append({
                "fel": FEL_LEDGER,
                "sigma_debit": str(rez_perioada.get("sigma_debit")),
                "sigma_credit": str(rez_perioada.get("sigma_credit")),
                "diferenta": str(rez_perioada.get("diferenta")),
                "perioada": perioada})
        if rez_perioada.get("orfani"):
            constatari.append({"fel": FEL_ORFANI, "numar": rez_perioada["orfani"],
                               "perioada": perioada})

    if problema_solduri is None:
        constatari.append({"fel": FEL_NEVERIFICAT, "ce": "inchiderea soldurilor initiale",
                           "motiv": "verificarea nu a rulat"})
    elif not problema_solduri.get("ok"):
        constatari.append({
            "fel": FEL_SOLDURI,
            "cod": problema_solduri.get("cod"),
            "diferenta_solduri": str(problema_solduri.get("diferenta_solduri")),
            "mesaj": problema_solduri.get("mesaj"),
            "temei": problema_solduri.get("temei")})

    return {"ok": not constatari, "constatari": constatari}
