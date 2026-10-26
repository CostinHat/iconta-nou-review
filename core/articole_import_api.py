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
#: [lotul 11] numele câmpului în refuzul coloanelor ambigue (`import_tabel.coloana`), în limba contabilului — nu cheia internă
#: (garda: core/test_lot11_import_etichete_camp.py)
ETICHETE_CAMP = {
    "denumire": "denumirea articolului",
    "um": "unitatea de măsură",
    "cantitate": "cantitatea",
    "pret": "prețul unitar",
    "cont_stoc": "contul de stoc",
    "cont_cheltuiala": "contul de cheltuială",
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
    col = lambda camp, exclus=(): _it.coloana(antet, CAMPURI[camp], exclus=exclus, camp=ETICHETE_CAMP[camp])
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


def _cheie_denumire(den):
    return " ".join(str(den or "").strip().lower().split())


def verifica_randuri(randuri, solduri=None):
    """PURĂ: respingerile [{rand, motiv, mesaj}] — rândurile care NU intră. Aceeași funcție la previzualizare ȘI la scriere (până azi
    `importa` credea indicatorul `valid` venit din cererea ecranului).
    [lotul 13, deficiența 668] `solduri` = balanța de deschidere ({cont: (debit, credit)}, None = fără balanță): rândurile unui cont de stoc
    ale cărui articole nu dau soldul lui din balanță nu intră (`stoc_nu_da_soldul`) — aceeași regulă ca la soldurile pe parteneri (346)."""
    er = []
    # [lotul 13, deficiența 590, comanda Costin 13.1: „La articol dublat, primul rând intră cu 10 buc (stocul real 13); trebuie respinse
    # ambele până la cumulare, ca la parteneri.”] TOATE aparițiile denumirii dublate se resping, nu numai a doua
    pe_den = {}
    for i, a in enumerate(randuri or [], start=2):
        k = _cheie_denumire(a.get("denumire"))
        if k:
            pe_den.setdefault(k, []).append(_it.nr_rand(a, i))
    for i, a in enumerate(randuri or [], start=2):
        i = _it.nr_rand(a, i)
        den = str(a.get("denumire") or "").strip()
        et = "„%s”" % den if den else "articolul"
        if not den:
            er.append(respinge("articol", i, "denumire_lipsa", "rândul n-are denumirea articolului"))
        else:
            # [385, retestul 19.10.2026: „acelasi articol pe doua randuri («Marfa valida» 10 buc si 3 buc) intra de doua ori, fara
            # observatie. Celelalte importuri resping dublurile.”] aceeași denumire (fără deosebire de litere mari / spații) = același articol
            alte = [n for n in pe_den.get(_cheie_denumire(den), []) if n != i]
            if alte:
                er.append(respinge("articol", i, "articol_dublat",
                                   "%s apare și pe %s — un articol se trece o singură dată, cu stocul lui total: adună cantitățile "
                                   "în fișier (niciunul din rânduri nu intră până atunci)"
                                   % (et, " și pe ".join("rândul %d" % n for n in alte))))   # rândurile se enumeră, nu se numără
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
    if solduri:
        er += respinse_balanta(randuri, solduri, {e["rand"] for e in er})
    return er


def respinse_balanta(randuri, solduri, deja_respinse=()):
    """[lotul 13, deficiența 668, comanda Costin 13.1: „Fișele (3 articole, 4.100 lei) față de 371 din balanță (4.200): diferența -100,00 lei
    e afișată, dar «Importă articolele» importă fără oprire sau confirmare și răspunde verde «3 articole importate». Fișele de magazie și 371
    pornesc nepotrivite. Aceeași regulă ca la parteneri: contul care nu se potrivește nu intră.”] Rândurile (încă nerespinse) ale unui cont
    de stoc a cărui valoare nu dă soldul lui din balanța de deschidere — fiecare respins, scurt; cifrele contului stau o singură dată, în
    confruntarea cu balanța (`reconciliere_balanta`)."""
    from core.pdf_util import bani as _b
    bune = [dict(a, stare="respins") if _it.nr_rand(a, i) in deja_respinse else a for i, a in enumerate(randuri or [], start=2)]
    nepotr = {c["cont"]: c for c in reconciliere_balanta(bune, solduri) if c["diferenta"] is not None and abs(c["diferenta"]) > 0.005}
    er = []
    for i, a in enumerate(randuri or [], start=2):
        n = _it.nr_rand(a, i)
        c = str(a.get("cont_stoc") or "").strip().split(".")[0]
        if n in deja_respinse or c not in nepotr:
            continue
        x = nepotr[c]
        er.append(respinge("articol", n, "stoc_nu_da_soldul",
                           "nu intră: articolele de pe contul %s dau %s, iar balanța de deschidere are %s (diferență %s)"
                           % (c, _b(x["registru"], "lei"), _b(x["balanta"], "lei"), _b(abs(x["diferenta"]), "lei")), cont=c))
    return er


def semnale_randuri(randuri):
    """PURĂ: rândurile care INTRĂ cu ceva completat din oficiu, spus (comanda Costin 8.2 pct.4).
    [lotul 13, deficiența 668 / clasa 666: „observația «607 dedus din 371» repetată pe fiecare rând”] o singură dată pe pereche (cont de stoc
    -> cont de cheltuială dedus), pe primul ei rând, cu numărul rândurilor pe care se aplică."""
    pe_pereche = {}
    for i, a in enumerate(randuri or [], start=2):
        if a.get("cont_cheltuiala_dedus"):
            pe_pereche.setdefault((a.get("cont_stoc"), a.get("cont_cheltuiala")), []).append(_it.nr_rand(a, i))
    out = []
    for (stoc, ch), nr in pe_pereche.items():
        out.append(semnaleaza("articol", nr[0], "cont_cheltuiala_dedus",
                              "contul de cheltuială %s e dedus din contul de stoc %s (lipsea din fișier)%s"
                              % (ch, stoc, "" if len(nr) == 1 else " — pe %s: %s" % (_cate_r(len(nr)), ", ".join(str(n) for n in nr)))))
    return out


def _cate_r(n):
    from core.common import cate
    return cate(n, "rând", "rânduri")


def eticheteaza(randuri, solduri=None):
    """[comanda Costin 8.2 pct.4] Starea fiecărui rând (ok / semnalat / respins), cu motivele. [lotul 13, 668] `solduri` = balanța de
    deschidere (rândurile contului de stoc nepotrivit sunt respinse, ca la salvare)."""
    er, sem = verifica_randuri(randuri, solduri), semnale_randuri(randuri)
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
    # [lotul 13, 668] aceeași confruntare cu balanța ca la previzualizare: rândurile contului de stoc nepotrivit nu intră
    from core import solduri_api as _sa
    with conn.cursor() as _cur:
        _cur.execute("SELECT to_regclass(%s)", ("%s.solduri_initiale" % schema,))
        solduri = None
        if _cur.fetchone()[0] is not None:
            solduri = _sa.solduri_deschidere(_cur) or None   # conexiunea e pe schema firmei (`db.get_conn(schema)`)
    er = verifica_randuri(articole, solduri)
    resp_idx = {e["rand"] for e in er}
    create, sarite = 0, list(er)
    with conn.cursor() as cur:
        for i, a in enumerate(articole, start=2):
            if _it.nr_rand(a, i) in resp_idx:
                continue
            from core import produse_api as _pa   # [lotul 11, 450] aceeași cheie de denumire ca nomenclatorul („grau” = „Grâu”)
            if _pa.articol_dupa_denumire(cur, schema, a["denumire"]):
                sarite.append(respinge("articol", _it.nr_rand(a, i), "deja_exista",
                                       "„%s” există deja în nomenclator - nu s-a dublat" % a["denumire"],
                                       denumire=a["denumire"]))
                continue
            from core import stocuri_cv_api as _cv   # [lotul 12, 475] singurul loc care scrie un articol nou
            aid = _cv.articol_pentru_intrare(cur, schema, a["denumire"], a["um"], a["cont_stoc"], a["cont_cheltuiala"])
            if (a["cantitate"] or 0) > 0:
                cur.execute(f"""INSERT INTO {schema}.miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document)
                                VALUES (%s,%s,'intrare',%s,%s,%s,'sold initial (import)')""",
                            (aid, d, a["cantitate"], a["pret"], float(_valoare(a))))
            create += 1
    return {"create": create, "sarite": sarite, "respinse": er}
