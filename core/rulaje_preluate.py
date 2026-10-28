# -*- coding: utf-8 -*-
"""core/rulaje_preluate.py — RULAJELE ANULUI PRELUATE din balanța de deschidere, pentru toți cititorii (balanța, D101, D100 pe profit,
bilanțul F20 / categoria de mărime, KPI / cash-flow, descărcarea global-valorică, controlul D101 ↔ 691) — o singură citire, o singură
regulă.

[lotul 10, deficiența 425, comanda Costin 10.1, verbatim în DECIZII „Comanda 10.1”] „O balanță completă la 30.09.2026 (format SAGA: solduri
inițiale an, rulaje precedente, rulaje lună, total sume, solduri finale [...]) e citită doar din «Solduri finale». Soldurile de la
1 ianuarie și rulajele ianuarie–septembrie se pierd [...] deci D101, bilanțul anual, plafonul de micro și controalele cumulate de TVA ies
greșite pentru o firmă preluată în cursul anului. Când fișierul are soldurile inițiale ale anului și rulajele, ele intră ca sold inițial și
sume precedente, cu toate conturile care au rulaj. Când are doar solduri finale, comportamentul de acum rămâne, dar aplicația spune clar
că rulajele anului lipsesc și ce afectează.”

DATELE (`solduri_initiale`, `core/migrare_balanta_rulaje_an.py`): `si_an_debit` / `si_an_credit` = soldul la 1 ianuarie al anului datei de
referință; `rulaj_an_debit` / `rulaj_an_credit` = rulajele 01.01 .. `data_referinta`, FĂRĂ soldul inițial; NULL pe toate patru = fișierul
avea numai solduri finale. `sold_debitor` / `sold_creditor` = soldurile finale la `data_referinta`. Un rând „are rulaje” dacă oricare
dintre cele patru coloane e scrisă (celelalte, goale, se citesc 0).

REGULA FERESTREI. Rulajele preluate acoperă intervalul [01.01.A, data_referinta] (A = anul datei de referință). Intră într-un calcul pe
fereastra [de_la, pana_la) numai dacă fereastra îl cuprinde ÎNTREG: de_la <= 01.01.A și data_referinta < pana_la. O fereastră care
începe după 1 ianuarie (o lună, un trimestru al D100 micro) sau se termină înainte de data preluării nu le poate folosi: rulajele
preluate sunt un singur cumul, nu se pot împărți pe luni.

ÎNCHIDEREA ÎN 121. TEMEI: OMFP 1802/2014, funcțiunea contului 121 — „În creditul contului 121 «Profit sau pierdere» se înregistrează:
– la sfârșitul perioadei, soldul creditor al conturilor din clasa 7 (701 la 786) [...] În debitul contului 121 «Profit sau pierdere» se
înregistrează: – la sfârșitul perioadei, soldul debitor al conturilor de cheltuieli (601 la 698)”, iar pct.420 alin.(1): „În
contabilitate, profitul sau pierderea se stabilește cumulat de la începutul exercițiului financiar.” La o firmă care închide lunar (soldul
final 0 pe 707, 607, 641 — exact balanța din comandă), rulajul preluat al unui cont de venit are pe DEBIT închiderea, iar al unui cont de
cheltuieli pe CREDIT. Pe notele din iConta.eu închiderea se scoate după contrapartida 121 ([C15], `bilant_api._rulaje_67`,
`repo_d100.select_inregistrari_linii`); balanța preluată nu are contrapartide, deci `fara_inchidere` păstrează numai latura funcțiunii
contului (OMFP 1802/2014 pct.594, `core/plan_functiune.py`: A = debit, P = credit; bifuncționalul rămâne cu ambele).
*INTERPRETARE CU TEMEI:* latura opusă a unui cont de venituri / cheltuieli din balanța preluată se socotește închidere în 121. Alternativa
respinsă: rulajul net (credit − debit) — la închiderea lunară dă 0 pe 707, exact pierderea cifrei de afaceri din comandă. Limita: o
stornare „în negru” pe latura opusă (nu „în roșu”) s-ar număra ca închidere. De reconfirmat dacă importul ajunge să aducă închiderea
separat. [lotul 12, C119 / C143] Pe NOTE (unde închiderea se scoate după contrapartida 121), D100, D101 și bilanțul (F20 / F30) citesc
rulajul NET al contului (credit − debit la venituri, debit − credit la cheltuieli): debitul 707 = 4427 al notei Raportului Z scade
venitul; aici, după `fara_inchidere`, latura opusă e deja 0, deci rulajul net al rândurilor preluate e chiar latura funcțiunii.
"""
import datetime as _dt
from decimal import Decimal

#: [lotul 10, deficiența 425] ce cifre afectează lipsa rulajelor, pe fiecare cititor (textul avertismentului — o singură sursă)
EFECTE = {
    "balanta": ("«Sold inițial» arată soldul de la data preluării, nu de la 1 ianuarie, iar «Sume precedente» nu cuprind lunile dinainte "
                "de preluare (veniturile și cheltuielile anului, deci rezultatul cumulat, ies mai mici)"),
    "d101": ("cifra de afaceri, veniturile și cheltuielile anului, deci profitul și impozitul, cuprind numai notele din iConta.eu de după "
             "preluare"),
    "d100": ("rezultatul fiscal cumulat de la 1 ianuarie cuprinde numai notele din iConta.eu de după preluare, deci impozitul pe profit "
             "iese greșit"),
    "bilant": ("contul de profit și pierdere (F20) — cifra de afaceri netă, veniturile și cheltuielile anului — cuprinde numai notele din "
               "iConta.eu de după preluare"),
}


def _d(x):
    return Decimal(str(x or 0))


def _tuplu(r):
    return tuple(r.values()) if isinstance(r, dict) else tuple(r)


def select_randuri(cur, schema):
    """REPOSITORY: rândurile balanței de deschidere cu data lor și cu coloanele anului — [(cont, data_referinta, sd, sc, si_an_d, si_an_c,
    rul_an_d, rul_an_c)]. `schema` gol = tabelul din `search_path` (cititorii care lucrează pe conexiunea firmei fără să-i știe schema)."""
    t = ("%s.solduri_initiale" % schema) if schema else "solduri_initiale"
    cur.execute(f"""SELECT cont, data_referinta, sold_debitor, sold_creditor, si_an_debit, si_an_credit, rulaj_an_debit, rulaj_an_credit
                    FROM {t}""")
    return [_tuplu(r) for r in cur.fetchall()]


def preluate(cur, schema, an):
    """Balanța de deschidere CU RULAJE a anului `an` (rândurile cu `data_referinta` în `an` și cel puțin o coloană a anului scrisă):
    {"ref": data_referinta, "conturi": {cont: {"si_d", "si_c", "rul_d", "rul_c", "sf_d", "sf_c"}}}, sau None (fără rulaje pe `an`)."""
    ref, conturi = None, {}
    for cont, data, sd, sc, sid, sic, rd, rc in select_randuri(cur, schema):
        if data is None or data.year != int(an) or all(v is None for v in (sid, sic, rd, rc)):
            continue
        ref = max(ref, data) if ref else data
        v = conturi.setdefault(cont, dict.fromkeys(("si_d", "si_c", "rul_d", "rul_c", "sf_d", "sf_c"), Decimal("0")))
        for k, x in (("si_d", sid), ("si_c", sic), ("rul_d", rd), ("rul_c", rc), ("sf_d", sd), ("sf_c", sc)):
            v[k] += _d(x)
    return {"ref": ref, "conturi": conturi} if conturi else None


def are_rulaje(cur, schema, an):
    """Balanța de deschidere a anului `an` a adus rulajele anului?"""
    return preluate(cur, schema, an) is not None


def fara_inchidere(cont, d, c):
    """(debit, credit) al rulajului PRELUAT al unui cont, fără închiderea în 121 (vezi antetul): la clasele 6 / 7 rămâne latura funcțiunii
    contului (A -> debit, P -> credit, OMFP 1802/2014 pct.594), bifuncționalul rămâne întreg; celelalte clase nu se ating."""
    if str(cont)[:1] not in ("6", "7"):
        return d, c
    from core.plan_functiune import functiune
    f = functiune(cont)
    if f == "A":
        return d, type(c)(0)
    if f == "P":
        return type(d)(0), c
    return d, c


def rulaje(cur, schema, de_la, pana_la, fara_inchidere_121=False):
    """Rulajele PRELUATE care intră în fereastra [de_la, pana_la) — {cont: (debit, credit)} în Decimal. Regula ferestrei din antet: numai
    anii al căror interval preluat [01.01, data_referinta] e cuprins întreg în fereastră. `fara_inchidere_121`: la clasele 6 / 7, fără
    închiderea în 121 (`fara_inchidere`) — pentru veniturile / cheltuielile anului (D101, F20); balanța le arată întregi."""
    out = {}
    for an in range(de_la.year, pana_la.year + 1):
        p = preluate(cur, schema, an)
        if not p or de_la > _dt.date(an, 1, 1) or p["ref"] >= pana_la:
            continue
        for cont, v in p["conturi"].items():
            d, c = v["rul_d"], v["rul_c"]
            if fara_inchidere_121:
                d, c = fara_inchidere(cont, d, c)
            x = out.get(cont, (Decimal("0"), Decimal("0")))
            out[cont] = (x[0] + d, x[1] + c)
    return out


def sold_preluat(cur, schema, prefix, inainte_de):
    """Partea PRELUATĂ a soldului conturilor `prefix` la sfârșitul zilei dinaintea lui `inainte_de` — (debit, credit) în Decimal; restul
    soldului îl dau notele (cititorul le adună). Când `inainte_de` e 1 ianuarie al anului preluării și balanța are soldurile inițiale ale
    anului -> soldul de la 1 ianuarie (`si_an`); altfel soldul final de la data preluării. *INTERPRETARE:* un sold cerut înainte de data
    preluării, fără soldul de la 1 ianuarie, se ia tot din soldul final (singurul cunoscut) — capitalul și rezervele se mișcă rar în an."""
    d = c = Decimal("0")
    for cont, data, sd, sc, sid, sic, rd, rc in select_randuri(cur, schema):
        if not str(cont).startswith(prefix):
            continue
        cu_an = data is not None and inainte_de == _dt.date(data.year, 1, 1) and not (sid is None and sic is None)
        d += _d(sid if cu_an else sd)
        c += _d(sic if cu_an else sc)
    return d, c


def avertisment(cur, schema, an, cititor):
    """[lotul 10, deficiența 425] „Când are doar solduri finale, comportamentul de acum rămâne, dar aplicația spune clar că rulajele anului
    lipsesc și ce afectează.” AFIRMAȚIE tipată (`core/afirmatii.py`, fel `necunoastere`: nu știm rulajele [01.01.an, data preluării]) sau
    None. Se dă când evidența firmei începe în anul `an` (data soldurilor de preluare — `bilant_api.data_soldurilor`, aceeași regulă ca
    luna preluării — e în `an`, după data înființării) și balanța de deschidere nu a adus rulajele lui. `cititor` ∈ `EFECTE`."""
    from psycopg2.extras import RealDictCursor
    from core import afirmatii as _af, bilant_api as _ba
    from core.pdf_util import data_ro
    with cur.connection.cursor(cursor_factory=RealDictCursor) as c2:
        ref = _ba.data_soldurilor(c2, schema)
        infiintare = _ba.data_infiintare(c2, schema)
    if ref is None or ref.year != int(an) or are_rulaje(cur, schema, an):
        return None
    # o firmă înființată în an nu are rulaje dinainte de înființare (Legea 82/1991 art.27 alin.(8): „Exercițiul financiar al unităților
    # nou-înființate începe la data înființării”) — lipsesc numai cele dintre înființare și preluare
    inceput = max(_dt.date(int(an), 1, 1), infiintare or _dt.date(int(an), 1, 1))
    if ref < inceput:
        return None
    cu_balanta = any(data is not None and data.year == int(an) for _c, data, *_r in select_randuri(cur, schema))
    motiv = ("Rulajele de la %s până la %s lipsesc: evidența firmei în iConta.eu începe după %s, iar %s. Pe %d, %s. %s balanța de la %s cu "
             "soldurile inițiale ale anului și rulajele (Import date › Solduri inițiale), ca ele să intre ca sold inițial și sume "
             "precedente."
             % (data_ro(inceput), data_ro(ref), data_ro(ref),
                "balanța de deschidere are numai soldurile finale, fără soldurile inițiale ale anului și rulajele lui" if cu_balanta
                else "aplicația nu are o balanță de deschidere cu rulajele anului",
                int(an), EFECTE[cititor], "Importă din nou" if cu_balanta else "Importă", data_ro(ref)))
    return _af.afirmatie("necunoastere", "rulaje_preluare", motiv,
                         domeniu_de="%04d-%02d" % (inceput.year, inceput.month), domeniu_pana="%04d-%02d" % (ref.year, ref.month))


# ── REFUZUL DECLARAȚIILOR / SITUAȚIILOR CARE ÎNCEP ÎNAINTE DE PRELUARE (lotul 14, deficiențele 683 + 695) ─────────────────────────────────
# Comanda Costin 14.1, verbatim: „683 — Bilanț. Fereastra nu semnalează lipsa rulajelor 01.01–31.08.2026 (balanța o semnalează): după 31.12
# bilanțul pe 2026 ar ieși doar cu sept.–dec., fără avertisment. Trebuie refuz cu trimitere la Import date › Solduri inițiale; după import,
# bilanțul folosește rulajele importate.” · „695 — D100 micro / preluare. F1, D100 T3/2026 (iul–sep): baza = 707 1.000 (doar septembrie),
# impozit 10 lei la 1%, validat și gata de «Pune în De depus», fără niciun avertisment că veniturile din iulie–august lipsesc (evidența
# începe după 31.08). Orice declarație sau situație a cărei perioadă începe înainte de preluare trebuie refuzată (sau completată cu
# rulajele importate), cu trimitere la Import date › Solduri inițiale.”
# Un avertisment (`avertisment`, lotul 10) se poate trece cu vederea; un document oficial cu cifre din jumătate de perioadă, nu. REGULA:
# o fereastră [de_la, pana_la) care cuprinde zile dinaintea datei preluării (în care aplicația nu are nicio notă) se refuză, afară de
# cazul în care balanța de deschidere a adus rulajele anului ȘI fereastra cuprinde întreg intervalul preluat [01.01, data preluării]
# (regula ferestrei de mai sus: rulajele preluate sunt un singur cumul, nu se împart pe luni). Deci: bilanțul și D101 (anul întreg) și
# D100 pe profit (cumulat de la 01.01) folosesc rulajele importate; D100 micro pe un trimestru care începe după 1 ianuarie nu le poate
# folosi și rămâne refuzat — venitul lunilor dinaintea preluării nu se poate separa de al celorlalte luni din cumul.
def lipsa_in_fereastra(cur, schema, de_la, pana_la):
    """None când evidența (notele din iConta.eu plus rulajele preluate care intră în fereastră) acoperă fereastra [de_la, pana_la);
    altfel {"ref": data preluării, "de_la": prima zi lipsă, "pana_la": ultima zi lipsă, "cu_import": balanța de deschidere a adus rulajele
    anului preluării}. Zilele dinaintea înființării firmei nu lipsesc (nu există). `cur` = RealDictCursor."""
    from core import bilant_api as _ba
    ref = _ba.data_soldurilor(cur, schema)
    if ref is None:
        return None
    infiintare = _ba.data_infiintare(cur, schema)
    prima = max(de_la, infiintare) if infiintare else de_la
    ultima = min(ref, pana_la - _dt.timedelta(days=1))
    if prima > ultima:
        return None
    cu_import = are_rulaje(cur, schema, ref.year)
    if cu_import and de_la <= _dt.date(ref.year, 1, 1) and ref < pana_la:
        return None          # fereastra cuprinde întreg intervalul preluat [01.01, ref]: rulajele importate intră în calcul
    return {"ref": ref, "de_la": prima, "pana_la": ultima, "cu_import": cu_import}


def text_lipsa(lipsa, ce, prefix=True):
    """Textul refuzului pentru `ce` (ex. „D100 pe T3/2026”), din rezultatul lui `lipsa_in_fereastra`. Trimite la Import date › Solduri
    inițiale; când balanța importată are rulajele anului dar ele nu se pot împărți pe luni, spune asta. `prefix=False`: fără „<ce> nu se
    poate genera:” în față (un motiv dintr-o listă de motive)."""
    from core.pdf_util import data_ro
    ref, a, b = lipsa["ref"], lipsa["de_la"], lipsa["pana_la"]
    cap = ("%s nu se poate genera: " % ce) if prefix else ""
    if lipsa["cu_import"]:
        cum = ("Balanța importată are rulajele cumulate de la 01.01.%d la %s, dar un cumul nu se poate împărți pe luni: veniturile de la %s "
               "la %s nu se pot separa de ale lunilor dinaintea lor, deci %s nu se poate calcula din ea."
               % (ref.year, data_ro(ref), data_ro(a), data_ro(b), ce))
        return ("%sperioada începe înainte de preluarea firmei în iConta.eu (evidența începe după %s). %s Depune-o din evidența de dinainte "
                "de preluare; din iConta.eu se depun perioadele care încep după %s." % (cap, data_ro(ref), cum, data_ro(ref)))
    return ("%sperioada începe înainte de preluarea firmei în iConta.eu (evidența începe după %s), iar rulajele de la %s până la %s lipsesc. "
            "Importă balanța de la %s cu soldurile inițiale ale anului și rulajele (Import date › Solduri inițiale), ca ele să intre ca sold "
            "inițial și sume precedente, apoi generează din nou." % (cap, data_ro(ref), data_ro(a), data_ro(b), data_ro(ref)))


def refuza_fereastra(cur, schema, de_la, pana_la, ce):
    """Ridică `RefuzGenerare` cu `text_lipsa` când fereastra începe înainte de preluare fără acoperire (vezi mai sus). `cur` = RealDictCursor."""
    from core.erori import RefuzGenerare
    lipsa = lipsa_in_fereastra(cur, schema, de_la, pana_la)
    if lipsa:
        # ecranul „Import date › Solduri inițiale” își are butonul lângă refuz (`ecran_destinatie.ECRANE.import_solduri`) când importul ajută
        raise RefuzGenerare(text_lipsa(lipsa, ce), ecran=None if lipsa["cu_import"] else "import_solduri")
