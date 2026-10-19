"""
core/articole_import_api.py - import articole + stoc initial CV (F151) per firma.
Citeste un export (.xlsx/.csv) cu denumire, UM, cantitate, pret unitar, cont stoc, cont cheltuiala (dedus din contul de stoc).
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
from core.migrare_api import respinge, semnaleaza  # [P8/C] respingerea e o afirmatie, cu regula din nomenclator


#: [373, comanda Costin 8.2] contul de cheltuială CORESPONDENT contului de stoc (OMFP 1802/2014, funcțiunea conturilor 30x/37x —
#: sursa unică e `inventariere.CORESPONDENT`, folosită și la plusurile de inventar)
from core.inventariere import CORESPONDENT as _CORESPONDENT


def _numar_sau_none(v):
    """Numărul din celulă; None dacă celula NU e goală dar nu e un număr („zece”) — până azi devenea 0 în tăcere (373)."""
    if v is None or str(v).strip() == "":
        return 0.0
    try:
        return _numar(v, strict=True)
    except ValueError:
        return None


def cont_cheltuiala_dedus(cont_stoc):
    """Contul de cheltuială corespondent contului de stoc (371 -> 607, 3021 -> 602), sau "" dacă nu există unul."""
    return _CORESPONDENT.get(str(cont_stoc or "").strip().split(".")[0][:3], "")


def e_cont_stoc(cont):
    """[373] Contul de stoc e din clasa 3 (stocuri și producție în curs), fără 39x (ajustări pentru depreciere) — OMFP 1802/2014 pct.594."""
    c = str(cont or "").strip().split(".")[0]
    return c.isdigit() and len(c) >= 3 and c[0] == "3" and not c.startswith("39")


def extrage(continut, nume_fisier=""):
    """Fiecare rând citit, cu valorile din fișier lângă cele interpretate: [{rand_fisier, denumire, um, cantitate, cantitate_brut, pret,
    pret_brut, cont_stoc, cont_cheltuiala, cont_cheltuiala_dedus}]. Verdictul e al lui `verifica_randuri`.

    [373, comanda Costin 8.2] Până azi rândul fără denumire dispărea, cantitatea „zece” devenea 0, UM lipsă devenea „buc”, iar contul
    de stoc lipsă devenea 302 — toate în tăcere. Acum nimic nu se completează din oficiu în afară de contul de cheltuială, dedus din
    contul de stoc (și spus pe rând)."""
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
    for nr, r in enumerate(randuri[1:], start=start + 1):
        if _it.rand_gol(r):
            continue
        cont = _it.celula(r, i_cont)
        ch = _it.celula(r, i_ch)
        rez.append({
            "rand_fisier": nr,
            "denumire": _it.celula(r, i_den)[:255],
            "um": _it.celula(r, i_um)[:20],
            "cantitate": _numar_sau_none(_it.valoare(r, i_cant)) if i_cant >= 0 else 0.0,
            "cantitate_brut": _it.celula(r, i_cant),
            "pret": _numar_sau_none(_it.valoare(r, i_pret)) if i_pret >= 0 else 0.0,
            "pret_brut": _it.celula(r, i_pret),
            "cont_stoc": cont[:10],
            "cont_cheltuiala": (ch or cont_cheltuiala_dedus(cont))[:10],
            "cont_cheltuiala_dedus": not ch and bool(cont_cheltuiala_dedus(cont)),
        })
    return rez


def verifica_randuri(randuri):
    """PURĂ: respingerile [{rand, motiv, mesaj}] — rândurile care NU intră. Aceeași funcție la previzualizare ȘI la scriere (până azi
    `importa` credea indicatorul `valid` venit din cererea ecranului)."""
    er = []
    vazut = {}
    for i, a in enumerate(randuri or [], start=2):
        i = _it.nr_rand(a, i)
        den = str(a.get("denumire") or "").strip()
        et = "„%s”" % den if den else "articolul"
        if not den:
            er.append(respinge("articol", i, "denumire_lipsa", "rândul n-are denumirea articolului"))
        else:
            # [385, retestul 19.10.2026: „acelasi articol pe doua randuri («Marfa valida» 10 buc si 3 buc) intra de doua ori, fara
            # observatie. Celelalte importuri resping dublurile.”] aceeași denumire (fără deosebire de litere mari / spații) = același articol
            cheie = " ".join(den.lower().split())
            if cheie in vazut:
                er.append(respinge("articol", i, "articol_dublat",
                                   "%s apare și pe rândul %s — un articol se trece o singură dată, cu stocul lui total" % (et, vazut[cheie])))
            else:
                vazut[cheie] = i
        if not str(a.get("um") or "").strip():
            er.append(respinge("articol", i, "um_lipsa", "%s: unitatea de măsură lipsește — nu se presupune „buc”" % et))
        cant, pret = a.get("cantitate"), a.get("pret")
        if cant is None:
            er.append(respinge("articol", i, "cantitate_invalida", "%s: cantitatea «%s» nu e un număr" % (et, a.get("cantitate_brut"))))
        if pret is None:
            er.append(respinge("articol", i, "pret_invalid", "%s: prețul «%s» nu e un număr" % (et, a.get("pret_brut"))))
        cant, pret = float(cant or 0), float(pret or 0)
        if cant < 0 or pret < 0:
            er.append(respinge("articol", i, "cantitate_pret_negativ", "%s: cantitate/preț negativ" % et))
        # [articol_pret] articol cu stoc dar pret 0/lipsa: miscarea de intrare ar avea valoare 0, CMP porneste de la 0, valoarea
        # stocului sub-raportata TACIT (DS cap.17, fara default fabricat). Un stoc real are cost > 0.
        elif cant > 0 and pret <= 0 and a.get("pret") is not None:
            er.append(respinge("articol", i, "pret_zero_cu_stoc",
                               "%s: are stoc dar preț unitar 0/lipsă: valoarea stocului ar fi 0 - completează costul unitar (CMP)" % et))
        cont = str(a.get("cont_stoc") or "").strip()
        if not cont:
            er.append(respinge("articol", i, "cont_stoc_lipsa",
                               "%s: contul de stoc lipsește (371 marfă, 301 materii prime, 302x materiale consumabile…) — stocul se "
                               "confruntă pe el cu balanța de deschidere" % et))
        elif not e_cont_stoc(cont):
            er.append(respinge("articol", i, "cont_stoc_invalid",
                               "%s: contul %s nu e un cont de stoc (clasa 3)" % (et, cont)))
        elif not str(a.get("cont_cheltuiala") or "").strip():
            er.append(respinge("articol", i, "cont_cheltuiala_lipsa",
                               "%s: contul de cheltuială lipsește și nu se poate deduce din contul de stoc %s" % (et, cont)))
    return er


def semnale_randuri(randuri):
    """PURĂ: rândurile care INTRĂ cu ceva completat din oficiu, spus pe rând (comanda Costin 8.2 pct.4)."""
    out = []
    for i, a in enumerate(randuri or [], start=2):
        if a.get("cont_cheltuiala_dedus"):
            out.append(semnaleaza("articol", _it.nr_rand(a, i), "cont_cheltuiala_dedus",
                                  "contul de cheltuială %s e dedus din contul de stoc %s (lipsea din fișier)"
                                  % (a.get("cont_cheltuiala"), a.get("cont_stoc"))))
    return out


def eticheteaza(randuri):
    """[comanda Costin 8.2 pct.4] Starea fiecărui rând (ok / semnalat / respins), cu motivele."""
    er, sem = verifica_randuri(randuri), semnale_randuri(randuri)
    for i, r in enumerate(randuri, start=2):
        n = _it.nr_rand(r, i)
        resp = [e["mesaj"] for e in er if e.get("rand") == n]
        obs = [e["mesaj"] for e in sem if e.get("rand") == n]
        r["stare"] = "respins" if resp else ("semnalat" if obs else "ok")
        r["motive"] = resp or obs
        # valoarea rândului, calculată aici (aritmetic, [280]) — ecranul n-o mai înmulțește singur
        r["valoare"] = float(_valoare(r)) if r.get("cantitate") is not None and r.get("pret") is not None else None
    return randuri


def _valoare(a):
    return _q(_dec(a.get("cantitate") or 0) * _dec(a.get("pret") or 0))   # [280] valoarea stocului: rotunjire aritmetică


def rezumat(articole):
    ok = [a for a in articole if a.get("stare") != "respins"]
    return {"total": len(articole), "valide": len(ok), "invalide": len(articole) - len(ok),
            "cu_stoc": sum(1 for a in ok if (a["cantitate"] or 0) > 0),
            "valoare_totala": float(sum((_valoare(a) for a in ok), _dec(0)))}


def reconciliere_balanta(randuri, solduri):
    """[374, comanda Costin 8.2 — „ca la 359”] Valoarea stocului inițial pe fiecare cont de stoc față de soldul lui din balanța de
    deschidere (`{cont: (debit, credit)}`; None = fără balanță, nu se presupune 0). Conturile de stoc cu sold în balanță și fără niciun
    articol se numesc și ele. -> [{cont, registru, balanta, diferenta}]."""
    from decimal import Decimal as _D
    pe_cont = {}
    for a in randuri or []:
        if a.get("stare") == "respins":
            continue
        c = str(a.get("cont_stoc") or "").strip().split(".")[0]
        if c:
            pe_cont[c] = pe_cont.get(c, _D(0)) + _valoare(a)
    if solduri:
        for cont, (d, c_) in solduri.items():
            s = str(cont).split(".")[0]
            if e_cont_stoc(s) and abs(_D(str(d or 0)) - _D(str(c_ or 0))) > _D("0.005") and not any(
                    s.startswith(k) or k.startswith(s) for k in pe_cont):
                pe_cont[s] = _D(0)
    out = []
    for cont, reg in sorted(pe_cont.items()):
        bal = None
        if solduri:
            bal = sum((_D(str(v[0] or 0)) - _D(str(v[1] or 0)) for k, v in solduri.items()
                       if str(k).split(".")[0].startswith(cont)), _D(0))
        out.append({"cont": cont, "registru": float(reg), "balanta": None if bal is None else float(bal),
                    "diferenta": None if bal is None else float(reg - bal)})
    return out


def importa(conn, schema, articole, data_sold=None):
    """Creeaza articolele noi + intrarea initiala pentru cele cu stoc. Existentele se sar; cele respinse (`verifica_randuri`) nu intră."""
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
    er = verifica_randuri(articole)
    resp_idx = {e["rand"] for e in er}
    create, sarite = 0, list(er)
    with conn.cursor() as cur:
        for i, a in enumerate(articole, start=2):
            if _it.nr_rand(a, i) in resp_idx:
                continue
            cur.execute(f"SELECT id FROM {schema}.articole WHERE lower(denumire)=lower(%s)", (a["denumire"],))
            if cur.fetchone():
                sarite.append(respinge("articol", _it.nr_rand(a, i), "deja_exista",
                                       "„%s” există deja în nomenclator - nu s-a dublat" % a["denumire"],
                                       denumire=a["denumire"]))
                continue
            cur.execute(f"""INSERT INTO {schema}.articole (denumire, um, cont_stoc, cont_cheltuiala)
                            VALUES (%s,%s,%s,%s) RETURNING id""",
                        (a["denumire"], a["um"], a["cont_stoc"], a["cont_cheltuiala"]))
            aid = cur.fetchone()[0]
            if (a["cantitate"] or 0) > 0:
                cur.execute(f"""INSERT INTO {schema}.miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document)
                                VALUES (%s,%s,'intrare',%s,%s,%s,'sold initial (import)')""",
                            (aid, d, a["cantitate"], a["pret"], float(_valoare(a))))
            create += 1
    return {"create": create, "sarite": sarite, "respinse": er}
