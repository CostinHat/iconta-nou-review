# -*- coding: utf-8 -*-
"""S1005 - strat DB: solduri finale + rulaje din note VALIDATE, apoi core.bilant."""
import datetime as _dt
from decimal import Decimal
from psycopg2.extras import RealDictCursor
from core import bilant as _b
from core.common import cere_coloane_cursor  # [garda coloane 27.07.2026]
from core.pdf_util import data_ro
_COLOANE_PROFIL = ("nume", "cui", "adresa", "caen")   # minimul citit de aici

def data_soldurilor(cur, schema):
    """[deficiența 221, 10.10.2026] Data LA CARE sunt soldurile de preluare (`solduri_initiale`), sau None dacă evidența firmei e
    întreagă în iConta.eu (nicio preluare). `data_referinta` când e scrisă; altfel ziua dinaintea lunii preluării (`luna_preluare` —
    decizia Costin 08.10.2026 §6 pct.4: evidența în iConta.eu începe cu luna preluării, deci soldurile sunt „la” ziua de dinainte).
    Aceeași regulă ca luna preluării din Date firmă și din Control fiscal, nu o a doua."""
    import datetime
    from core import luna_preluare as _lp
    cur.execute(f"""SELECT (SELECT luna_preluare FROM {schema}.firma_profil WHERE id = 1) AS salvata,
                           (SELECT creat_la FROM public.tenants WHERE schema_name = %s) AS creat_la,
                           (SELECT max(data_referinta) FROM {schema}.solduri_initiale) AS data_solduri,
                           (SELECT min(data) FROM {schema}.inregistrari) AS prima_nota,
                           (SELECT count(*) FROM {schema}.solduri_initiale) AS n_solduri""", (schema,))
    r = dict(cur.fetchone())
    if r["data_solduri"]:
        return r["data_solduri"]
    c = r["creat_la"]
    ef = _lp.efectiva(r["salvata"], c.date() if hasattr(c, "date") else c, None, r["prima_nota"])
    if not ef:
        return None
    return datetime.date(ef[0], ef[1], 1) - datetime.timedelta(days=1)


def sold_la(cur, schema, zi, ref="calculeaza"):
    """Soldurile conturilor LA `zi` (inclusiv): soldurile de preluare + mișcările validate de după data lor, până la `zi`.
    None dacă `zi` e înainte de data soldurilor de preluare: aplicația nu știe ce era atunci (nu se fabrică — OMFP 1802/2014 pct.130 cere
    valoarea REALĂ a exercițiului precedent, nu o copie). [deficiența 221: coloana „An precedent” era soldul de preluare oricare ar fi
    anul, deci pe anul preluării ieșea identică cu „An curent”.]"""
    if ref == "calculeaza":
        ref = data_soldurilor(cur, schema)
    if ref is not None and zi < ref:
        return None
    cur.execute(f"SELECT cont, sold_debitor, sold_creditor FROM {schema}.solduri_initiale")
    net = {}
    for r in cur.fetchall():
        net[r["cont"]] = net.get(r["cont"], Decimal("0")) + Decimal(str(r["sold_debitor"])) - Decimal(str(r["sold_creditor"]))
    cur.execute(f"""
        SELECT l.cont_debit, l.cont_credit, l.suma
        FROM {schema}.inregistrari_linii l
        JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
        WHERE i.status = 'validata' AND i.data <= %s AND (%s::date IS NULL OR i.data > %s::date)""", (zi, ref, ref))
    for r in cur.fetchall():
        s = Decimal(str(r["suma"]))
        net[r["cont_debit"]] = net.get(r["cont_debit"], Decimal("0")) + s
        net[r["cont_credit"]] = net.get(r["cont_credit"], Decimal("0")) - s
    return {c: ((v, Decimal("0")) if v >= 0 else (Decimal("0"), -v)) for c, v in net.items()}


def coloana_curenta_f10(cur, schema, an):
    """F10 „An curent” = bilanțul la 31.12.an. Necunoscut (an dinaintea soldurilor de preluare) -> refuz: bilanțul nu se poate întocmi."""
    import datetime
    ref = data_soldurilor(cur, schema)
    s_c = sold_la(cur, schema, datetime.date(an, 12, 31), ref)
    if s_c is None:
        raise ValueError("Bilanțul pe %d nu se poate întocmi în iConta.eu: evidența firmei începe după soldurile de preluare de la %s, "
                         "deci soldurile de la %s nu sunt în aplicație." % (an, data_ro(ref), data_ro(datetime.date(an, 12, 31))))
    return _b.f10_din_balanta(s_c)


# [deficiența 221, decizia Costin 11.10.2026, verbatim în DECIZII] „coloana «An precedent» din bilanț se completează din bilanțul anului
# anterior, dacă firma îl are în aplicație. Dacă nu îl are, se completează manual, cu avertisment vizibil. Bilanțul nu poate fi generat
# cu coloana goală.” Coloana = F10 și F20, coloana 1 (`xml_s1005`). TEMEI: OMFP 1802/2014, Reglementări, pct.130 — valoarea elementului
# corespondent pentru exercițiul financiar precedent.
FEL_MANUAL = "bilant_an_precedent"      # artefactul coloanei completate manual (core/artefacte.FELURI), cheia "<tip>:<an>"
SECTIUNI = ("F10", "F20")


def data_infiintare(cur, schema):
    """[deficiențele 229, 235] Data înființării firmei (Date firmă, `firma_profil.data_infiintare`) sau None — o singură citire, pentru
    coloana „An precedent” și pentru categoria de mărime (primul exercițiu)."""
    cur.execute(f"SELECT data_infiintare FROM {schema}.firma_profil WHERE id = 1")
    r = cur.fetchone()
    return (r["data_infiintare"] if isinstance(r, dict) else r[0]) if r else None


def randuri_formular(tip):
    """Rândurile fiecărei secțiuni a formularului `tip` (s1005 / s1003) — cele pe care le scrie generatorul, deci și cele de completat."""
    f20 = _b.f20_complet_din_rulaje if tip == "s1003" else _b.f20_din_rulaje
    return {"F10": sorted(_b.f10_din_balanta({})), "F20": sorted(f20({}))}


def denumiri_formular(tip):
    """[deficiența 227, comanda Costin 12.10.2026] {secțiune: {rând: denumirea de pe formular}} pentru rândurile din `randuri_formular`
    — din `core/bilant_denumiri.py` (structura ANAF a formularelor de bilanț 2025, generat). Un rând fără denumire e o eroare de date:
    `core/test_bilant_denumiri.py` cere ca fiecare rând de completat să aibă una."""
    from core.bilant_denumiri import NOMENCLATOR_DENUMIRI
    return {s: {r: NOMENCLATOR_DENUMIRI[tip][s][r] for r in rr} for s, rr in randuri_formular(tip).items()}


def totaluri_formular(tip):
    """[deficiența 233] {secțiune: {rând: {"termeni": [[semn, rând], …], "pozitiv": bool}}} — totalurile formularului (`bilant.
    NOMENCLATOR_TOTALURI`, = calculele formularului) pe rândurile scrise de generator; ecranul le calculează pe loc, serverul la fel."""
    rr = randuri_formular(tip)
    return {s: {r: {"termeni": [list(t) for t in _b.termeni_total(e)], "pozitiv": p}
                for r, (e, p) in _b.NOMENCLATOR_TOTALURI[tip].get(s, {}).items() if r in rr[s]} for s in SECTIUNI}


def componente_formular(tip):
    """{secțiune: [rândurile pe care le completează contabilul]} = rândurile formularului fără totaluri."""
    tot = totaluri_formular(tip)
    return {s: [r for r in rr if r not in tot[s]] for s, rr in randuri_formular(tip).items()}


def ordine_formular(tip):
    """[deficiența 234] {secțiune: rândurile în ordinea formularului} și {secțiune: {rând: codul tipărit („06a (301)”)}}."""
    from core.bilant_denumiri import NOMENCLATOR_COD, NOMENCLATOR_ORDINE
    rr = randuri_formular(tip)
    ordine = {s: [r for r in NOMENCLATOR_ORDINE[tip][s] if r in rr[s]] + [r for r in rr[s] if r not in NOMENCLATOR_ORDINE[tip][s]]
              for s in SECTIUNI}
    return ordine, {s: {r: NOMENCLATOR_COD[tip][s].get(r, "%02d" % r) for r in rr[s]} for s in SECTIUNI}


def _ultimul(cur, schema, fel, cheie, numai_valid=False):
    cur.execute(f"""SELECT continut, exemplar, produs_la, produs_de FROM {schema}.artefacte_produse
                    WHERE fel = %s AND cheie = %s {"AND verdict = 'valid'" if numai_valid else ""}
                    ORDER BY exemplar DESC LIMIT 1""", (fel, str(cheie)))
    r = cur.fetchone()
    return dict(r) if r else None


def coloana_precedenta(cur, schema, tip, an):
    """„An precedent” al bilanțului `tip` pe `an`, pe secțiuni: {"F10": {rând: lei} | None, "F20": … | None, "sursa": {secțiune: fel},
    "bilant"/"manual": cine și când}. Ordinea surselor (DECIZII 11.10.2026):
      (a) „bilant”   — bilanțul anului precedent validat în aplicație (artefactul `tip` pe an-1, ultimul exemplar „valid”): coloana lui
                       „An curent”, ambele secțiuni;
      (b) „evidenta” — evidența anului precedent din aplicație: F10 = soldurile la 31.12 (cunoscute de la soldurile de preluare încoace),
                       F20 = rulajele anului numai dacă evidența îl acoperă întreg (INTERPRETARE: e bilanțul pe care aplicația l-ar
                       genera pentru acel an);
      (c) „manual”   — completată de contabil (artefactul `FEL_MANUAL`), numai pentru secțiunile fără (a)/(b).
    O secțiune fără sursă rămâne None: `coloanele` refuză generarea.
    [deficiența 229, comanda Costin 12.10.2026] înaintea lor, PRIMUL EXERCIȚIU: firma înființată în anul bilanțului (`data_infiintare`)
    nu are exercițiu precedent — coloana „An precedent” rămâne legal goală, sursa „primul_exercitiu”, fără completare manuală. TEMEI:
    Legea 82/1991 art.27 alin.(8): „Exercițiul financiar al unităților nou-înființate începe la data înființării, potrivit legii.”;
    OMFP 1802/2014 pct.130 cere valoarea „pentru exercițiul financiar precedent” — în primul exercițiu nu există. Un bilanț pe un an
    dinaintea înființării nu există: refuz."""
    import datetime
    import json
    out = {"F10": None, "F20": None, "sursa": {"F10": None, "F20": None}}
    infiintare = data_infiintare(cur, schema)
    if infiintare and infiintare.year > an:
        raise ValueError(mesaj_inainte_de_infiintare(an, infiintare))
    if infiintare and infiintare.year == an:
        out.update({s: {} for s in SECTIUNI})
        out["sursa"] = {s: PRIMUL_EXERCITIU for s in SECTIUNI}
        out["infiintare"] = infiintare
        return out
    ref = data_soldurilor(cur, schema)
    s_p = sold_la(cur, schema, datetime.date(an - 1, 12, 31), ref)
    b = _ultimul(cur, schema, tip, an - 1, numai_valid=True)
    if b and b["produs_la"] < S1003_F20_SCHEMA_NOUA_DIN:
        # [C10, 12.10.2026] un S1003 produs înainte de rescrierea F20 pe rândurile formularului are F20 pe numerotarea veche (38 de rânduri
        # proprii): coloana lui „An curent” ar ajunge pe rânduri greșite. Nu se folosește; coloana se cere ca la bilanțul respins de 221.
        # [C12, C13 — clasa] la fel orice bilanț (S1005 / S1003) produs înainte ca F10 și F20 S1005 să urmeze listele formularului 2025.
        out["bilant_respins"] = {"exemplar": b["exemplar"], "la": b["produs_la"], "de": b["produs_de"], "numerotare_veche": True,
                                 "tip": tip}
        b = None
    if b and s_p is None:
        # [prins la proba pe producție, 11.10.2026] Un bilanț al anului precedent pe care aplicația NU l-ar putea întocmi azi (31.12 a
        # lui e înaintea soldurilor de preluare) a fost generat de defectul 221 — F1 avea S1005 2025 „valid” din 10.10, cu ambele
        # coloane = soldurile de preluare de la 31.08.2026. Cifrele lui nu sunt ale exercițiului precedent: nu se folosesc.
        out["bilant_respins"] = {"exemplar": b["exemplar"], "la": b["produs_la"], "de": b["produs_de"], "solduri_la": ref}
        b = None
    if b:
        col = {s: {} for s in SECTIUNI}
        for x in _b.randuri_din_xml(b["continut"]):
            if x["formular"] in col:
                col[x["formular"]][x["rand"]] = x["an_curent"]
        out.update(col)
        out["sursa"] = {s: "bilant" for s in SECTIUNI}
        out["bilant"] = {"exemplar": b["exemplar"], "la": b["produs_la"], "de": b["produs_de"]}
        return out
    if s_p is not None:
        out["F10"], out["sursa"]["F10"] = _b.f10_din_balanta(s_p), "evidenta"
    if ref is None or ref < datetime.date(an - 1, 1, 1):
        f20 = _b.f20_complet_din_rulaje if tip == "s1003" else _b.f20_din_rulaje
        out["F20"], out["sursa"]["F20"] = f20(_rulaje_67(cur, schema, an - 1)), "evidenta"
    lipsa = [s for s in SECTIUNI if out[s] is None]
    if lipsa:
        m = _ultimul(cur, schema, FEL_MANUAL, "%s:%d" % (tip, an))
        valori = json.loads(m["continut"]) if m else {}
        tot = totaluri_formular(tip)
        for s in lipsa:
            if s in valori:          # [deficiența 233] totalurile se calculează din componente (și la o coloană salvată înainte)
                out[s], out["sursa"][s] = _b.cu_totaluri(tip, s, {int(k): int(v) for k, v in valori[s].items() if int(k) not in tot[s]}), "manual"
        if any(out["sursa"][s] == "manual" for s in SECTIUNI):
            out["manual"] = {"exemplar": m["exemplar"], "la": m["produs_la"], "de": m["produs_de"]}
    return out


def coloanele(cur, schema, tip, an, av):
    """(f10p, f10c, f20p) pentru generare. „An curent” F10 necunoscut -> refuz (`coloana_curenta_f10`). „An precedent” fără sursă pe o
    secțiune -> refuz: bilanțul nu se generează cu coloana goală (decizia Costin 11.10.2026). Completat manual -> avertismentul vizibil."""
    cp = coloana_precedenta(cur, schema, tip, an)     # întâi: un an dinaintea înființării se refuză cu motivul lui (229)
    f10c = coloana_curenta_f10(cur, schema, an)
    lipsa = [s for s in SECTIUNI if cp[s] is None]
    if lipsa:
        raise ValueError(mesaj_coloana_goala(an, lipsa, cp.get("bilant_respins")))
    manual = [s for s in SECTIUNI if cp["sursa"][s] == "manual"]
    if manual:
        av.append(avertisment_manual(an, manual, cp["manual"], cp.get("bilant_respins")))
    return cp["F10"], f10c, cp["F20"]


PRIMUL_EXERCITIU = "primul_exercitiu"
#: [C10; C12, C13] momentul schimbării rândurilor bilanțului (de la el, F20 S1003, F10 și F20 S1005 pe formularul ANAF 2025); un bilanț
#: păstrat de dinainte nu e „An precedent”. 12.10.2026 13:00 UTC: după publicarea C10 (6dea8a28, procesul pornit la 10:33 UTC) și înaintea
#: lotului C12 / C13 — un prag în viitor (13.10, cum era) respingea și bilanțurile generate de codul nou până atunci (prins de plasa 221).
#: Fereastra 13:00 UTC → publicarea lotului se verifică pe producție (read-only) la publicare.
S1003_F20_SCHEMA_NOUA_DIN = _dt.datetime(2026, 10, 12, 13, 0, tzinfo=_dt.timezone.utc)


def mesaj_inainte_de_infiintare(an, infiintare):
    return ("Bilanțul pe %d nu există: firma s-a înființat pe %s, iar primul ei exercițiu financiar e %d (Legea 82/1991 art.27 alin.(8))."
            % (an, data_ro(infiintare), infiintare.year))


def nota_primul_exercitiu(an, infiintare):
    """Textul ecranului: de ce coloana „An precedent” e goală și nu se cere."""
    return ("Primul exercițiu financiar: firma s-a înființat pe %s, deci bilanțul pe %d nu are exercițiu precedent — coloana „An "
            "precedent” rămâne goală și nu se completează (Legea 82/1991 art.27 alin.(8))." % (data_ro(infiintare), an))


def mesaj_coloana_goala(an, lipsa, respins=None):
    return ("Bilanțul pe %d nu se poate genera cu coloana „An precedent” goală (%s): firma nu are în aplicație bilanțul pe %d validat, "
            "iar evidența din aplicație nu acoperă %s.%s Completeaz-o manual pe ecranul Bilanț, din bilanțul depus pe %d."
            % (an, ", ".join(lipsa), an - 1,
               " și ".join({"F10": "soldurile de la %s" % data_ro("%d-12-31" % (an - 1)), "F20": "tot anul %d" % (an - 1)}[s] for s in lipsa),
               nota_bilant_respins(an, respins), an - 1))


def nota_bilant_respins(an, respins):
    """Bilanțul anului precedent din aplicație care NU se folosește (generat cu soldurile de preluare de după 31.12 a lui — defectul 221;
    sau un S1003 pe numerotarea veche a F20 — C10)."""
    if not respins:
        return ""
    if respins.get("numerotare_veche") and respins.get("tip") == "s1005":
        return (" Bilanțul S1005 pe %d păstrat în aplicație (%s) nu se folosește: rândurile lui sunt dinaintea rescrierii pe listele de "
                "conturi ale formularului ANAF 2025." % (an - 1, data_ro(respins.get("la"), "cu_ora")))
    if respins.get("numerotare_veche"):
        return (" Bilanțul S1003 pe %d păstrat în aplicație (%s) nu se folosește: contul lui de profit și pierdere e pe numerotarea veche, "
                "dinaintea rescrierii pe rândurile formularului ANAF." % (an - 1, data_ro(respins.get("la"), "cu_ora")))
    return (" Bilanțul pe %d păstrat în aplicație (%s) nu se folosește: soldurile de preluare sunt de la %s, deci cifrele lui nu sunt ale "
            "exercițiului %d." % (an - 1, data_ro(respins.get("la"), "cu_ora"), data_ro(respins.get("solduri_la")), an - 1))


def avertisment_manual(an, sectiuni, meta, respins=None):
    return ("Coloana „An precedent” (%s) e completată manual%s, nu din bilanțul pe %d: firma nu îl are în aplicație.%s Verific-o față de "
            "bilanțul depus pe %d — cifrele ei intră în declarație așa cum au fost scrise."
            % (", ".join(sectiuni), (" de %s, la %s" % (meta.get("de") or "—", data_ro(meta.get("la"), "cu_ora"))) if meta else "",
               an - 1, nota_bilant_respins(an, respins), an - 1))


def _rulaje_67(cur, schema, an):
    cur.execute(f"""
        SELECT l.cont_debit, l.cont_credit, l.suma
        FROM {schema}.inregistrari_linii l
        JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
        WHERE i.status = 'validata' AND i.data BETWEEN %s AND %s""",
        (f"{an}-01-01", f"{an}-12-31"))
    rl = {}
    for r in cur.fetchall():
        s = Decimal(str(r["suma"]))
        for cont, idx in ((r["cont_debit"], 0), (r["cont_credit"], 1)):
            if str(cont)[:1] in ("6", "7"):
                v = rl.get(cont, [Decimal("0"), Decimal("0")])
                v[idx] += s
                rl[cont] = v
    return {c: (v[0], v[1]) for c, v in rl.items()}

_JUD = {"bucuresti": 40, "alba": 1, "arad": 2, "arges": 3, "bacau": 4, "bihor": 5,
        "bistrita-nasaud": 6, "botosani": 7, "brasov": 8, "braila": 9, "buzau": 10,
        "caras-severin": 11, "calarasi": 51, "cluj": 12, "constanta": 13, "covasna": 14,
        "dambovita": 15, "dolj": 16, "galati": 17, "giurgiu": 52, "gorj": 18, "harghita": 19,
        "hunedoara": 20, "ialomita": 21, "iasi": 22, "ilfov": 23, "maramures": 24,
        "mehedinti": 25, "mures": 26, "neamt": 27, "olt": 28, "prahova": 29, "satu mare": 30,
        "salaj": 31, "sibiu": 32, "suceava": 33, "teleorman": 34, "timis": 35, "tulcea": 36,
        "vaslui": 37, "valcea": 38, "vrancea": 39}

def erori_generare(prof):
    """Poarta bazei nule: profil incomplet -> STOP cu mesaj clar, nu XML respins de ANAF."""
    erori = []
    if not str(prof.get("cui_numeric") or "").strip():
        erori.append("Lipsă CUI firmă.")
    if not str(prof.get("nume") or "").strip():
        erori.append("Lipsă denumire firmă.")
    # regCom e OBLIGATORIU in S1005/S1003 (verificat la sursa: DUKIntegrator -v S1005 respinge XML-ul cu
    # "eroare atribut: regCom: atributul trebuie sa existe"). Fara aceasta poarta, genereaza emitea un
    # bilant FARA regCom - exact "XML respins de ANAF" pe care docstring-ul spune ca poarta il previne.
    if not str(prof.get("reg_com") or "").strip():
        erori.append("Nr. registrul comerțului lipsește — obligatoriu în bilanț; fără el declarația e "
                     "respinsă de validatorul ANAF. Se completează la Date firmă.")
    return erori


def genereaza(conn, schema, an):
    import re
    av = []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.firma_profil WHERE id = 1")
        cere_coloane_cursor(cur, _COLOANE_PROFIL, "firma_profil")   # [garda 27.07.2026]
        p = dict(cur.fetchone() or {})
        f10p, f10c, f20p = coloanele(cur, schema, "s1005", an, av)
        rl = _rulaje_67(cur, schema, an)
    j = (p.get("judet") or "bucuresti").strip().lower()
    prof = {
        "cui_numeric": re.sub(r"\D", "", p.get("cui") or ""),
        "nume": p.get("nume"), "caen": re.sub(r"\D", "", p.get("caen") or ""),
        "reg_com": p.get("reg_com") or "", "adresa": p.get("adresa") or "",
        "cod_judet": _JUD.get(j, 40),
        "declarant_nume": p.get("declarant_nume"),
        "intocmit_nume": p.get("declarant_nume"),
    }
    if not prof["reg_com"]:
        av.append("Nr. Reg. Com. lipsă în Profil firma (câmp obligatoriu S1005).")
    if not prof.get("declarant_nume"):
        # [declarant thread 3] Regula 4: fara fabricare tacita a administratorului
        av.append("Bilanț: declarantul (administrator) lipsește din profil — se trece implicit "
                  "\"ADMINISTRATOR\". Completează declarantul în Date firmă.")
    f20c = _b.f20_din_rulaje(rl)
    if f10c.get(15) != f10c.get(49):
        av.append(f"Verificare: rândul 15 (F) = {f10c.get(15)} diferă de rândul 49 (J) = {f10c.get(49)} — datoriile peste un an, "
                  "provizioanele sau veniturile în avans pot explica diferența.")
    _er = erori_generare(prof)
    if _er:
        raise ValueError("Bilanț nu se poate genera: " + " ".join(_er))
    return _b.xml_s1005(prof, an, f10p, f10c, f20p, f20c), av


def genereaza_s1003(conn, schema, an):
    """S1003 (mici): F10 identic, F20 complet."""
    import re
    av = []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.firma_profil WHERE id = 1")
        cere_coloane_cursor(cur, _COLOANE_PROFIL, "firma_profil")   # [garda 27.07.2026]
        p = dict(cur.fetchone() or {})
        f10p, f10c, f20p = coloanele(cur, schema, "s1003", an, av)
        rl = _rulaje_67(cur, schema, an)
    j = (p.get("judet") or "bucuresti").strip().lower()
    prof = {
        "cui_numeric": re.sub(r"\D", "", p.get("cui") or ""),
        "nume": p.get("nume"), "caen": re.sub(r"\D", "", p.get("caen") or ""),
        "reg_com": p.get("reg_com") or "", "adresa": p.get("adresa") or "",
        "cod_judet": _JUD.get(j, 40),
        "declarant_nume": p.get("declarant_nume"),
        "intocmit_nume": p.get("declarant_nume"),
    }
    f20c = _b.f20_complet_din_rulaje(rl)
    _er = erori_generare(prof)
    if _er:
        raise ValueError("Bilanț nu se poate genera: " + " ".join(_er))
    return _b.xml_s1003(prof, an, f10p, f10c, f20p, f20c), av
