"""
core/solduri_parteneri_api.py — import solduri parteneri (defalcare 4111/401 per client/furnizor).

Citeste un fisier (.xlsx/.csv) cu coloanele: Cont, CUI, Denumire, Sold debitor, Sold creditor.
Un rand = un partener pe un cont. Se salveaza in schema tenantului (tabel solduri_parteneri).

Coerenta cu stratul 2 (solduri_initiale): suma soldurilor partenerilor pe contul sintetic
(4111, 401) se compara cu soldul sintetic din balanta (analiticele 4111.X grupate pe radacina).
Informativ, NU blocant — contabilul decide.

"""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
from __future__ import annotations


from core.numere import numar as _numar  # sursa unica (15.07.2026, vezi core/numere.py)
from core.migrare_api import respinge  # [P8/C] respingerea e o afirmatie, cu regula din nomenclator


def _radacina(cont):
    """Sinteticul de baza al unui cont: '4111.ALPHA' -> '4111', '401' -> '401'."""
    return str(cont).split(".")[0].strip()


def _curata_cui(v):
    """Normalizeaza CUI: RO14837428 -> 14837428, scoate spatii."""
    t = str(v or "").strip().upper().replace(" ", "")
    if t.startswith("RO"):
        t = t[2:]
    return t


# [14.10.2026, comanda Costin „Importul din SAGA”, verbatim în DECIZII] Fișierul trece prin `core.import_tabel` (format, codare,
# antet pe unul sau două rânduri, coloane pe cuvinte întregi). Antetele SAGA vin din manualul SAGA C: ecranul Terți are „Cod
# fiscal/ CNP” și „Cont analitic” (401.00001 / 4111.00001), iar „Situație clienți / furnizori” are „Neachitat final” — soldul
# fiecărui terț, fără coloana Cont (contul îl dă ecranul din care s-a exportat: clienți sau furnizori).
from core import import_tabel as _it

CAMPURI = {
    "cont": ("cont analitic", "simbol cont", "=cont", "=simbol"),
    "cui": ("cod fiscal cnp", "cod fiscal", "cui", "cif", "cnp", "cod unic de inregistrare"),
    "denumire": ("denumire partener", "denumire tert", "denumire", "partener", "tert", "client", "furnizor", "nume"),
    "debit": ("debit*",),
    "credit": ("credit*",),
    "sold": ("neachitat final", "sold final", "sold", "rest de plata", "rest de incasat"),
}

# Natura contului de parteneri: pe ce parte stă soldul lui obișnuit. Folosită numai când fișierul are O SINGURĂ coloană de sold
# („Neachitat final”) — atunci partea o dă contul, iar o valoare negativă trece pe partea cealaltă.
_DEBITOARE = ("4111", "4118", "409", "4091", "4092", "4093")
_CREDITOARE = ("401", "419")
CONTURI_ALESE = ("4111", "401")      # ce se poate alege pe ecran când fișierul n-are coloana Cont (situația clienților / furnizorilor)


def extrage(continut, nume_fisier="", cont_implicit=None):
    """
    Intoarce [{cont, cui, denumire, debit, credit}] din fisierul de parteneri.

    Coloanele: Cont (sau `cont_implicit`, ales pe ecran, când fișierul n-are coloana), CUI / CNP, Denumire, și fie perechea
    debit / credit (la o balanță completă: perechea soldului FINAL), fie o singură coloană de sold („Neachitat final”).
    Rândurile de total și cele cu sold 0 nu sunt parteneri — nu intră.
    """
    brut = _it.citeste(continut, nume_fisier)
    if not brut or all(_it.rand_gol(r) for r in brut):
        return []
    antet, start = _it.gaseste_antet(brut, CAMPURI, obligatorii=("denumire",), nume_fisier=nume_fisier)
    i_cont = _it.coloana(antet, CAMPURI["cont"], camp="cont")
    i_cui = _it.coloana(antet, CAMPURI["cui"], exclus=(i_cont,), camp="CUI / CNP")
    # denumirea se cauta DUPA cont si cui, sarind peste coloanele lor („CUI partener” nu e denumirea)
    i_den = _it.coloana(antet, CAMPURI["denumire"], exclus=(i_cont, i_cui), camp="denumire")
    are_dc = any(_it._e_debit(h) or _it._e_credit(h) for h in antet if h)
    i_deb = i_cre = i_sold = -1
    if are_dc:
        i_deb, i_cre = _it.pereche_sold_final(antet, nume_fisier)
    else:
        i_sold = _it.coloana(antet, CAMPURI["sold"], camp="sold")
        if i_sold < 0:
            raise _it.FisierNecitit("Fișierul %s n-are nici coloane debit / credit, nici o coloană de sold („Neachitat "
                                    "final”, „Sold final”) — nu se poate citi soldul partenerilor."
                                    % ("«%s»" % nume_fisier if nume_fisier else "trimis"))
    cont_ales = str(cont_implicit or "").strip()
    if i_cont < 0 and cont_ales not in CONTURI_ALESE:
        raise _it.FisierNecitit("Fișierul %s n-are coloana „Cont”. Alege din listă contul partenerilor din fișier (4111 — "
                                "situația clienților, 401 — situația furnizorilor) și încarcă-l din nou."
                                % ("«%s»" % nume_fisier if nume_fisier else "trimis"))

    out = []
    for nr, r in enumerate(brut[start:], start=start + 1):
        if _it.rand_gol(r):
            continue
        den = _it.celula(r, i_den)
        cui = _curata_cui(_it.celula(r, i_cui))
        cont = _it.celula(r, i_cont) if i_cont >= 0 else cont_ales
        if not cui and (not den or _it.norm(den).startswith("total")):
            continue                                       # rând de total / titlu, nu partener
        try:
            if i_sold >= 0:
                s = _numar(_it.valoare(r, i_sold), strict=True)
                debitor = _radacina(cont) in _DEBITOARE or (_radacina(cont) not in _CREDITOARE and s >= 0)
                deb, cre = ((s, 0.0) if s >= 0 else (0.0, -s)) if debitor else ((0.0, s) if s >= 0 else (-s, 0.0))
            else:
                deb = _numar(_it.valoare(r, i_deb), strict=True) if i_deb >= 0 else 0.0
                cre = _numar(_it.valoare(r, i_cre), strict=True) if i_cre >= 0 else 0.0
        except ValueError:
            raise _it.FisierNecitit("Rândul %d (%s): soldul nu e un număr. Corectează celula și încarcă fișierul din nou."
                                    % (nr, den or cui or "?"))
        if round(deb, 2) == 0 and round(cre, 2) == 0:
            continue                                       # partener fără sold: nu intră în soldurile inițiale
        out.append({"cont": cont, "cui": cui, "denumire": den, "debit": deb, "credit": cre, "rand_fisier": nr})
    # același partener pe același cont de două ori: baza are UNIQUE(cont, cui) (GARZI cat.1) — refuz numit, nu eroare de bază
    vazute, dubluri = {}, []
    for x in out:
        k = (x["cont"], x["cui"])
        if x["cui"] and k in vazute:
            dubluri.append("%s / %s (rândurile %s și %s)" % (x["cont"], x["cui"], vazute[k], x["rand_fisier"]))
        vazute.setdefault(k, x["rand_fisier"])
    if dubluri:
        raise _it.FisierNecitit("Același partener apare de două ori pe același cont: %s. Un partener are un singur sold pe un cont; "
                                "adună rândurile în fișier și încarcă-l din nou." % "; ".join(dubluri[:6]))
    return out


def asigura_tabel(conn):
    """Creeaza tabelul solduri_parteneri in schema curenta (search_path = tenantul)."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS solduri_parteneri (
                id SERIAL PRIMARY KEY,
                cont TEXT NOT NULL,
                cui TEXT NOT NULL DEFAULT '',
                denumire TEXT NOT NULL DEFAULT '',
                sold_debitor NUMERIC(15,2) NOT NULL DEFAULT 0,
                sold_creditor NUMERIC(15,2) NOT NULL DEFAULT 0,
                data_referinta DATE
            )
        """)


def coerenta(conn, randuri):
    """
    Compara soldurile partenerilor pe sintetic (radacina) cu soldurile din solduri_initiale.
    Intoarce [{cont, suma_parteneri, sold_balanta, diferenta, coincide}] per sintetic.
    Daca solduri_initiale nu exista inca, sold_balanta = None (nu putem verifica).
    """
    # suma partenerilor pe radacina sintetica, sold net (debit - credit)
    pe_sintetic = {}
    for r in randuri:
        rad = _radacina(r["cont"])
        net = float(r.get("debit", 0) or 0) - float(r.get("credit", 0) or 0)
        pe_sintetic[rad] = pe_sintetic.get(rad, 0.0) + net

    # soldurile din balanta, grupate pe radacina
    bal = {}
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('solduri_initiale')")
        exista = cur.fetchone()[0] is not None
        if exista:
            cur.execute("SELECT cont, sold_debitor, sold_creditor FROM solduri_initiale")
            for cont, sd, sc in cur.fetchall():
                rad = _radacina(cont)
                bal[rad] = bal.get(rad, 0.0) + (float(sd) - float(sc))

    out = []
    for rad in sorted(pe_sintetic.keys()):
        sp = round(pe_sintetic[rad], 2)
        if exista and rad in bal:
            sb = round(bal[rad], 2)
            dif = round(sp - sb, 2)
            out.append({"cont": rad, "suma_parteneri": sp, "sold_balanta": sb,
                        "diferenta": dif, "coincide": abs(dif) < 0.01})
        else:
            out.append({"cont": rad, "suma_parteneri": sp, "sold_balanta": None,
                        "diferenta": None, "coincide": None})
    return out


# Conturile pe care se tin solduri pe parteneri. Restul (5121 banca, 5311 casa,
# conturi de venituri/cheltuieli) NU au parteneri: un sold pe partener acolo e o
# eroare de export, nu o realitate contabila.
CONTURI_PARTENERI = ("4111", "401", "409", "419", "4118", "4091", "4092", "4093")

# cheia oficiala de control a CUI romanesc (aceeasi ca la CNP in salariati_import_api:
# algoritm publicat, nu inventat aici)
_CHEIE_CUI = [7, 5, 3, 2, 1, 7, 5, 3, 2]


def valideaza_cui(cui):
    """(valid, motiv) - cifra de control a CUI romanesc, LOCAL (fara retea).
    anaf_api.valideaza_cui() interogheaza ANAF si e potrivit la o firma, nu la fiecare
    rand dintr-un import de sute de parteneri."""
    c = "".join(ch for ch in str(cui or "") if ch.isdigit())
    if not c:
        return False, "lipsa"
    if len(c) == 13:
        # [14.10.2026] un partener persoană fizică e identificat prin CNP (ecranul Terți SAGA: „Cod fiscal/ CNP”); CNP-ul se
        # verifică cu cheia lui oficială, nu cu a CUI-ului
        from core.salariati_import_api import valideaza_cnp
        ok, motiv = valideaza_cnp(c)
        return ok, ("ok" if ok else "CNP: " + motiv)
    if not (2 <= len(c) <= 10):
        return False, "lungime (2-10 cifre)"
    corp, ctrl = c[:-1], int(c[-1])
    corp = corp.rjust(9, "0")
    s = sum(int(corp[i]) * _CHEIE_CUI[i] for i in range(9))
    rest = (s * 10) % 11
    if rest == 10:
        rest = 0
    return (rest == ctrl), ("ok" if rest == ctrl else "cifra de control")


def verifica_randuri(randuri):
    """PURA: (erori, randuri_bune). Ce nu poate intra in evidenta si de ce.

    Pana la 15.07.2026 nu exista NICIO validare intre extrage() si importa():
    - CUI cu cifra de control gresita -> intra
    - partener fara CUI pe cont de parteneri -> intra
    - partener pe 5121 (banca) -> intra
    verifica() calcula diferentele fata de balanta si le trimitea in raspuns, ecranul
    le afisa cu ⚠, iar importa() scria oricum. Migrarea marca stratul "gata" VERDE.
    Semnalarea fara oprire e mai rea decat tacerea: da impresia ca s-a verificat.
    """
    erori, bune = [], []
    for i, r in enumerate(randuri or [], start=2):   # +2: randul din fisier, cu antet
        i = _it.nr_rand(r, i)
        cont = str(r.get("cont") or "").strip()
        cui = str(r.get("cui") or "").strip()
        den = str(r.get("denumire") or "").strip()
        rad = _radacina(cont)
        if rad not in CONTURI_PARTENERI:
            erori.append(respinge(
                "sold partener", i, "cont_nepartener",
                "contul %s nu ține solduri pe parteneri (doar %s)"
                % (cont or "?", ", ".join(CONTURI_PARTENERI[:4])), cont=cont))
            continue
        ok, motiv = valideaza_cui(cui)
        if not ok:
            erori.append(respinge(
                "sold partener", i, "cui_invalid",
                ("partenerul %s nu are CUI" % (den or "?")) if motiv == "lipsa"
                else ("CNP %s invalid (%s)" % (cui, motiv[5:]) if motiv.startswith("CNP: ") else "CUI %s invalid (%s)" % (cui, motiv)),
                cont=cont, cui=cui, denumire=den))
            continue
        bune.append(r)
    return erori, bune


def importa(conn, randuri, data_referinta=None):
    """Inlocuieste partenerii (DELETE + INSERT) cu randurile BUNE. Intoarce {randuri, total_debit, total_credit, respinse}.
    Randurile respinse (vezi verifica_randuri) nu intra si se intorc numite (decizia Costin 14.10.2026 pct.2); ValueError numai
    cand niciun rand nu poate intra."""
    # [probare invalid, 03.09.2026 — aceeasi clasa ca importul de istoric] UN IMPORT GOL
    # STERGEA TOT, IN TACERE. Lista vida trecea de verificare (n-are ce respinge), ajungea la
    # `DELETE FROM solduri_parteneri` de mai jos, si raspundea ca un import reusit cu zero randuri. Un fisier gol,
    # unul cu numai antet (`extrage` intoarce [] pe el), sau un apel de API cu lista goala — toate
    # ajungeau acolo. *Un import care nu aduce nimic n-are voie sa stearga ce era acolo.*
    if not randuri:
        raise ValueError("nu ai trimis niciun rând. Importul ar fi șters soldurile inițiale ale "
                         "partenerilor și n-ar fi pus nimic în loc. Dacă chiar vrei să le "
                         "golești, e altă operațiune.")
    erori, bune = verifica_randuri(randuri)
    # [decizia Costin 14.10.2026 pct.2, verbatim în DECIZII] „rândurile bune se salvează, cele refuzate se arată numite, cu motivul
    # în cuvinte” — numai un import fără niciun rând bun se refuză întreg (și atunci soldurile existente rămân neatinse).
    if not bune:
        det = "; ".join("rand %s: %s" % (e["rand"], e["mesaj"]) for e in erori[:6])
        if len(erori) > 6:
            det += " (și încă %d)" % (len(erori) - 6)
        raise ValueError(
            "%d rânduri nu pot intra în evidență: %s. Soldurile pe parteneri au nevoie "
            "de CUI valid (intră în D394 și SAF-T) și de un cont care ține parteneri; niciun sold n-a fost scris."
            % (len(erori), det))
    asigura_tabel(conn)
    td = tc = 0.0
    with conn.cursor() as cur:
        cur.execute("DELETE FROM solduri_parteneri")
        for r in bune:
            cur.execute(
                "INSERT INTO solduri_parteneri (cont, cui, denumire, sold_debitor, sold_creditor, data_referinta) "
                "VALUES (%s,%s,%s,%s,%s,%s)",
                (r["cont"], r.get("cui", ""), r.get("denumire", ""),
                 r.get("debit", 0), r.get("credit", 0), data_referinta))
            td += float(r.get("debit", 0) or 0)
            tc += float(r.get("credit", 0) or 0)
    return {"randuri": len(bune), "total_debit": round(td, 2), "total_credit": round(tc, 2), "respinse": erori}


def rezumat(conn):
    """{are_parteneri, randuri, total_debit, total_credit} pentru firma curenta."""
    asigura_tabel(conn)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*), COALESCE(sum(sold_debitor),0), COALESCE(sum(sold_creditor),0) FROM solduri_parteneri")
        n, td, tc = cur.fetchone()
    return {"are_parteneri": n > 0, "randuri": n, "total_debit": float(td), "total_credit": float(tc)}
