"""
core/articole_import_api.py - import articole + stoc initial CV (F151) per firma.
Citeste un export (.xlsx/.csv) cu denumire, UM, cantitate, pret unitar, cont stoc (optional).
Mapeaza flexibil coloanele (tiparul asociati_import_api). Creeaza articolele si o miscare
de INTRARE initiala (document 'sold initial') -> CMP-ul de pornire al fisei de magazie.
Idempotenta: articolele existente (aceeasi denumire) NU se dubleaza - se sare cu motiv.

"""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
from __future__ import annotations


# [14.10.2026, comanda Costin „Importul din SAGA”, verbatim în DECIZII] Citirea fișierului și potrivirea coloanelor trec prin
# `core.import_tabel` (sursa unică: format, codare Windows-1250 recunoscută sau refuzată, antet sub titluri, coloane pe cuvinte
# întregi, ambiguitate refuzată numit) — nu mai e o copie a lui `_gaseste_col` aici.
from core import import_tabel as _it

CAMPURI = {
    "denumire": ("denumire articol", "denumire*", "articol*", "produs*", "material*"),
    "um": ("=um", "u m", "unitate de masura", "unitate*"),
    "cantitate": ("cantitate*", "=stoc", "stoc initial", "cant"),
    "pret": ("pret unitar", "pret*", "cmp", "cost*"),
    "cont_stoc": ("cont stoc",),
    "cont_cheltuiala": ("cont cheltuiala",),
}


from core.numere import numar as _numar  # sursa unica (15.07.2026, vezi core/numere.py)
from core.common import _q, _dec   # [280] rotunjirea aritmetică a sumelor (ROUND_HALF_UP)
from core.migrare_api import respinge  # [P8/C] respingerea e o afirmatie, cu regula din nomenclator


def extrage(continut, nume_fisier=""):
    """Intoarce [{denumire, um, cantitate, pret, cont_stoc, cont_cheltuiala, valid, motiv}]."""
    randuri = _it.citeste(continut, nume_fisier)
    if not randuri or all(_it.rand_gol(r) for r in randuri):
        return []
    try:
        antet, start = _it.gaseste_antet(randuri, CAMPURI, obligatorii=("denumire",), nume_fisier=nume_fisier)
    except _it.FisierNecitit as e:
        if isinstance(e, _it.ColoaneAmbigue):
            raise
        raise ValueError("nu se găsește coloana cu denumirea articolului")
    col = lambda camp, exclus=(): _it.coloana(antet, CAMPURI[camp], exclus=exclus, camp=camp)
    i_den = col("denumire")
    i_um = col("um", (i_den,))
    i_cant = col("cantitate", (i_den,))
    i_pret = col("pret", (i_den,))
    i_cont = col("cont_stoc")
    i_ch = col("cont_cheltuiala")
    randuri = randuri[start - 1:]
    rez = []
    for r in randuri[1:]:
        den = _it.celula(r, i_den)
        if not den:
            continue
        cant = _numar(_it.valoare(r, i_cant)) if i_cant >= 0 else 0.0
        pret = _numar(_it.valoare(r, i_pret)) if i_pret >= 0 else 0.0
        um = _it.celula(r, i_um) or "buc"
        cont = _it.celula(r, i_cont) or "302"
        ch = _it.celula(r, i_ch) or "601"
        # [P8] randul de previzualizare poarta AFIRMATIA respingerii, nu doar textul ei: `regula`
        # nu se schimba cand se rescrie mesajul, iar `unde` numeste articolul. Codul se scrie LITERAL
        # la fiecare ramura - trecut printr-o variabila, scanul de confruntare nu-l mai poate verifica.
        _resp = _respingere(den, cant, pret)
        _r = {"denumire": den[:255], "um": um[:20], "cantitate": cant, "pret": pret,
              "cont_stoc": cont[:10], "cont_cheltuiala": ch[:10], "valid": _resp is None,
              "motiv": "ok"}
        if _resp is not None:
            _r.update(_resp)
        rez.append(_r)
    return rez


def _respingere(den, cant, pret):
    """Afirmația de respingere a unui articol, sau `None`. Aceeași funcție la previzualizare ȘI la scriere: până azi `importa`
    credea indicatorul `valid` venit din cererea ecranului (un client putea trimite `valid: true` pe o cantitate negativă)."""
    # [P8] randul de previzualizare poarta AFIRMATIA respingerii, nu doar textul ei: `regula`
    # nu se schimba cand se rescrie mesajul, iar `unde` numeste articolul. Codul se scrie LITERAL
    # la fiecare ramura - trecut printr-o variabila, scanul de confruntare nu-l mai poate verifica.
    _unde = "articolul „%s”" % (den or "?")
    if cant < 0 or pret < 0:
        return respinge("articol", _unde, "cantitate_pret_negativ", "cantitate/preț negativ")
    # [articol_pret] articol cu stoc dar pret 0/lipsa: parserul fabrica pret 0.0 (coloana absenta /
    # celula goala) -> miscarea de intrare ar avea valoare 0, CMP porneste de la 0, valoarea stocului
    # sub-raportata TACIT (DS cap.17, fara default fabricat). Un stoc real are cost > 0.
    if cant > 0 and pret <= 0:
        return respinge("articol", _unde, "pret_zero_cu_stoc",
                        "are stoc dar preț unitar 0/lipsă: valoarea stocului ar fi 0 - "
                        "completează costul unitar (CMP)")
    return None


def rezumat(articole):
    ok = [a for a in articole if a["valid"]]
    return {"total": len(articole), "valide": len(ok), "invalide": len(articole) - len(ok),
            "cu_stoc": sum(1 for a in ok if a["cantitate"] > 0),
            "valoare_totala": float(_q(sum((_dec(a["cantitate"]) * _dec(a["pret"]) for a in ok), _dec(0))))}   # [280] aritmetic


def importa(conn, schema, articole, data_sold=None):
    """Creeaza articolele noi + intrarea initiala pentru cele cu stoc. Existentele se sar."""
    # [lotul 6] O cerere fara niciun rand nu e un import cu zero rezultate: e o cerere fara
    # continut. „create: 0" arata identic cu un import inofensiv. Clasa e cea din lotul 1b.
    if not articole:
        raise ValueError("nu ai trimis niciun articol. Un import fără rânduri n-are ce adăuga în "
                         "nomenclatorul de articole; dacă voiai altceva, e altă operațiune.")
    # [C22, clasa — 14.10.2026] fără dată tacită: până azi lipsa devenea ziua importului. Apelantul trimite data soldurilor de
    # preluare (`uc_tenants._data_soldurilor`); dacă nu se știe, refuz numit — nu o dată inventată.
    if not data_sold:
        raise ValueError("Data stocului inițial nu se cunoaște: firma n-are balanță de deschidere și nici luna preluării. "
                         "Încarcă întâi balanța de deschidere (sau scrie luna preluării în Date firmă) — stocul inițial e "
                         "la data soldurilor de preluare.")
    d = data_sold
    create, sarite = 0, []
    with conn.cursor() as cur:
        for a in articole:
            _resp = _respingere(a["denumire"], float(a.get("cantitate") or 0), float(a.get("pret") or 0))
            if _resp is not None:
                sarite.append(dict(_resp, denumire=a["denumire"]))
                continue
            cur.execute(f"SELECT id FROM {schema}.articole WHERE lower(denumire)=lower(%s)", (a["denumire"],))
            if cur.fetchone():
                sarite.append(respinge("articol", "articolul „%s”" % a["denumire"], "deja_exista",
                                       "există deja în nomenclator - nu s-a dublat",
                                       denumire=a["denumire"]))
                continue
            cur.execute(f"""INSERT INTO {schema}.articole (denumire, um, cont_stoc, cont_cheltuiala)
                            VALUES (%s,%s,%s,%s) RETURNING id""",
                        (a["denumire"], a["um"], a["cont_stoc"], a["cont_cheltuiala"]))
            aid = cur.fetchone()[0]
            if a["cantitate"] > 0:
                val = float(_q(_dec(a["cantitate"]) * _dec(a["pret"])))   # [280] valoarea stocului: rotunjire aritmetică, nu la par
                cur.execute(f"""INSERT INTO {schema}.miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document)
                                VALUES (%s,%s,'intrare',%s,%s,%s,'sold initial (import)')""",
                            (aid, d, a["cantitate"], a["pret"], val))
            create += 1
    return {"create": create, "sarite": sarite}
