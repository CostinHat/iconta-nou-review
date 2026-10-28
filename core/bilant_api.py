# -*- coding: utf-8 -*-
"""S1005 - strat DB: solduri finale + rulaje din note VALIDATE, apoi core.bilant."""
import datetime as _dt
from decimal import Decimal
from psycopg2.extras import RealDictCursor
from core import bilant as _b
from core.common import cere_coloane_cursor  # [garda coloane 27.07.2026]
from core.erori import RefuzGenerare
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


def motiv_rulaje(tip, rl):
    """[deficiența 242] Rulajele anului pe care F20 nu le poate depune (sintetic cu analitice pe rânduri diferite, cont fără rând) — ca
    motiv de oprire alături de cele de la 31.12, nu abia la „Validează”. None = rulajele permit F20."""
    f20 = _b.f20_complet_din_rulaje if tip == "s1003" else _b.f20_din_rulaje
    try:
        f20(rl)
    except ValueError as e:
        t = str(e)
        return {"fel": "rulaje", "titlu": "Rulajele anului", "text": t.split(": ", 1)[1] if t.startswith("Bilanțul S100") else t,
                "simplu": t}
    return None


def _motive_31_12(cur, schema, s, an):
    """`bilant.motive_31_12` cu starea propunerii notei de închidere la 31.12.`an` (243: anul încheiat; 244: notele propuse, la zi)."""
    from core import inchidere_an as _ia
    p = _ia.ciorne(cur, schema, an)
    return _b.motive_31_12(s, an, propuse=p, incheiat=_ia.an_incheiat(an), s_dupa=_ia.solduri_dupa(cur, schema, s, p) if p else None)


def coloana_curenta_f10(cur, schema, an, tip=None):
    """F10 „An curent” = bilanțul la 31.12.an. Necunoscut (an dinaintea soldurilor de preluare) -> refuz: bilanțul nu se poate întocmi.
    [242] Cu `tip`, refuzul strânge TOATE motivele anului: soldurile la 31.12 (6 / 7, fără loc) și rulajele lui (F20)."""
    import datetime
    ref = data_soldurilor(cur, schema)
    s_c = sold_la(cur, schema, datetime.date(an, 12, 31), ref)
    if s_c is None:
        raise ValueError("Bilanțul pe %d nu se poate întocmi în iConta.eu: evidența firmei începe după soldurile de preluare de la %s, "
                         "deci soldurile de la %s nu sunt în aplicație." % (an, data_ro(ref), data_ro(datetime.date(an, 12, 31))))
    motive = _motive_31_12(cur, schema, s_c, an)   # [C15, 242] 6 / 7 închise în 121, soldurile cu loc în bilanț, rulajele — toate
    # [lotul 14, deficiența 683] anul care începe înainte de preluare, fără rulajele lui importate: refuz cu trimitere la Import date ›
    # Solduri inițiale (după import, rulajele intră în F20 prin `rulaje_67`)
    from core import rulaje_preluate as _rp
    _lipsa = _rp.lipsa_in_fereastra(cur, schema, _dt.date(an, 1, 1), _dt.date(an + 1, 1, 1))
    if _lipsa:
        motive.append({"fel": "rulaje_preluare", "titlu": "Rulajele anului până la preluare", "text": _rp.text_lipsa(_lipsa, "Bilanțul pe %d" % an, False),
                       "simplu": _rp.text_lipsa(_lipsa, "Bilanțul pe %d" % an)})
    if tip:
        m = motiv_rulaje(tip, _rulaje_67(cur, schema, an))
        motive += [m] if m else []
    _b.refuz(motive, an)
    return _b.f10_din_balanta(s_c)


# [deficiența 221, decizia Costin 11.10.2026, verbatim în DECIZII] „coloana «An precedent» din bilanț se completează din bilanțul anului
# anterior, dacă firma îl are în aplicație. Dacă nu îl are, se completează manual, cu avertisment vizibil. Bilanțul nu poate fi generat
# cu coloana goală.” Coloana = F10 și F20, coloana 1 (`xml_s1005`). TEMEI: OMFP 1802/2014, Reglementări, pct.130 — valoarea elementului
# corespondent pentru exercițiul financiar precedent.
FEL_MANUAL = "bilant_an_precedent"      # artefactul coloanei completate manual (core/artefacte.FELURI), cheia "<tip>:<an>"
#: secțiunile cu două coloane (an precedent / an curent) ale fiecărui formular; [C14] S1005 are și F30 cap.XIX
NOMENCLATOR_SECTIUNI = {"s1005": ("F10", "F20", "F30"), "s1003": ("F10", "F20")}


def sectiuni(tip):
    return NOMENCLATOR_SECTIUNI[tip]


def data_infiintare(cur, schema):
    """[deficiențele 229, 235] Data înființării firmei (Date firmă, `firma_profil.data_infiintare`) sau None — o singură citire, pentru
    coloana „An precedent” și pentru categoria de mărime (primul exercițiu)."""
    cur.execute(f"SELECT data_infiintare FROM {schema}.firma_profil WHERE id = 1")
    r = cur.fetchone()
    return (r["data_infiintare"] if isinstance(r, dict) else r[0]) if r else None


def randuri_formular(tip):
    """Rândurile fiecărei secțiuni a formularului `tip` (s1005 / s1003) — cele pe care le scrie generatorul, deci și cele de completat."""
    f20 = _b.f20_complet_din_rulaje if tip == "s1003" else _b.f20_din_rulaje
    out = {"F10": sorted(_b.f10_din_balanta({})), "F20": sorted(f20({}))}
    if "F30" in sectiuni(tip):                       # [C14] cap.XIX, rândurile scrise de generator
        out["F30"] = sorted(_b.f30_din_rulaje({}))
    return out


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
                for r, (e, p) in _b.NOMENCLATOR_TOTALURI[tip].get(s, {}).items() if r in rr[s]} for s in sectiuni(tip)}


def componente_formular(tip):
    """{secțiune: [rândurile pe care le completează contabilul]} = rândurile formularului fără totaluri."""
    tot = totaluri_formular(tip)
    return {s: [r for r in rr if r not in tot[s]] for s, rr in randuri_formular(tip).items()}


def ordine_formular(tip):
    """[deficiența 234] {secțiune: rândurile în ordinea formularului} și {secțiune: {rând: codul tipărit („06a (301)”)}}."""
    from core.bilant_denumiri import NOMENCLATOR_COD, NOMENCLATOR_ORDINE
    rr = randuri_formular(tip)
    ordine = {s: [r for r in NOMENCLATOR_ORDINE[tip][s] if r in rr[s]] + [r for r in rr[s] if r not in NOMENCLATOR_ORDINE[tip][s]]
              for s in sectiuni(tip)}
    return ordine, {s: {r: NOMENCLATOR_COD[tip][s].get(r, "%02d" % r) for r in rr[s]} for s in sectiuni(tip)}


def _ultimul(cur, schema, fel, cheie, numai_valid=False):
    cur.execute(f"""SELECT continut, exemplar, produs_la, produs_de FROM {schema}.artefacte_produse
                    WHERE fel = %s AND cheie = %s {"AND verdict = 'valid'" if numai_valid else ""}
                    ORDER BY exemplar DESC LIMIT 1""", (fel, str(cheie)))
    r = cur.fetchone()
    return dict(r) if r else None


def rulaje_an_cunoscute(cur, schema, ref, an):
    """Aplicația are rulajele ÎNTREGULUI an `an`? Da dacă evidența îl acoperă întreg (fără solduri de preluare, sau soldurile sunt de
    dinainte de 1 ianuarie), ori — [lotul 10, deficiența 425] — dacă preluarea e în `an` și balanța de deschidere a adus rulajele lui
    01.01 .. data preluării (`rulaje_preluate.are_rulaje`): „ele intră ca sold inițial și sume precedente”."""
    import datetime
    from core import rulaje_preluate as _rp
    return ref is None or ref < datetime.date(an, 1, 1) or (ref.year == an and _rp.are_rulaje(cur, schema, an))


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
    out = {s: None for s in sectiuni(tip)}
    out["sursa"] = {s: None for s in sectiuni(tip)}
    infiintare = data_infiintare(cur, schema)
    if infiintare and infiintare.year > an:
        raise ValueError(mesaj_inainte_de_infiintare(an, infiintare))
    if infiintare and infiintare.year == an:
        out.update({s: {} for s in sectiuni(tip)})
        out["sursa"] = {s: PRIMUL_EXERCITIU for s in sectiuni(tip)}
        out["infiintare"] = infiintare
        return out
    ref = data_soldurilor(cur, schema)
    s_p = sold_la(cur, schema, datetime.date(an - 1, 12, 31), ref)
    b = _ultimul(cur, schema, tip, an - 1, numai_valid=True)
    if b and (b["produs_la"] < S1003_F20_SCHEMA_NOUA_DIN or (tip == "s1005" and fara_cap_xix(b["continut"]))):
        # [C10, 12.10.2026] un S1003 produs înainte de rescrierea F20 pe rândurile formularului are F20 pe numerotarea veche (38 de rânduri
        # proprii): coloana lui „An curent” ar ajunge pe rânduri greșite. Nu se folosește; coloana se cere ca la bilanțul respins de 221.
        # [C12, C13 — clasa] la fel orice bilanț (S1005 / S1003) produs înainte ca F10 și F20 S1005 să urmeze listele formularului 2025.
        # [C14] și un S1005 fără F30 cap.XIX (produs înainte de C14): coloana lui F30 n-ar exista — se cere ca mai sus.
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
        col = {s: {} for s in sectiuni(tip)}
        rr = randuri_formular(tip)
        for x in _b.randuri_din_xml(b["continut"]):
            if x["formular"] in col and x["rand"] in rr[x["formular"]]:     # F30: numai cap.XIX (rd.01–03 nu sunt pe doi ani)
                col[x["formular"]][x["rand"]] = x["an_curent"]
        out.update(col)
        out["sursa"] = {s: "bilant" for s in sectiuni(tip)}
        out["bilant"] = {"exemplar": b["exemplar"], "la": b["produs_la"], "de": b["produs_de"]}
        return out
    if s_p is not None:
        motive = _motive_31_12(cur, schema, s_p, an - 1)   # [C15, 242] și coloana „An precedent” din evidență, la 31.12.an-1
        rl_p = _rulaje_67(cur, schema, an - 1) if rulaje_an_cunoscute(cur, schema, ref, an - 1) else None
        m = motiv_rulaje(tip, rl_p) if rl_p is not None else None
        _b.refuz(motive + ([m] if m else []), an - 1, bilant_pe=an)
        out["F10"], out["sursa"]["F10"] = _b.f10_din_balanta(s_p), "evidenta"
    if rulaje_an_cunoscute(cur, schema, ref, an - 1):
        f20 = _b.f20_complet_din_rulaje if tip == "s1003" else _b.f20_din_rulaje
        rl_p = _rulaje_67(cur, schema, an - 1)
        out["F20"], out["sursa"]["F20"] = f20(rl_p), "evidenta"
        if "F30" in out:                               # [C14] cap.XIX din aceleași rulaje
            out["F30"], out["sursa"]["F30"] = _b.f30_din_rulaje(rl_p), "evidenta"
    lipsa = [s for s in sectiuni(tip) if out[s] is None]
    if lipsa:
        m = _ultimul(cur, schema, FEL_MANUAL, "%s:%d" % (tip, an))
        valori = json.loads(m["continut"]) if m else {}
        tot = totaluri_formular(tip)
        for s in lipsa:
            if s in valori:          # [deficiența 233] totalurile se calculează din componente (și la o coloană salvată înainte)
                out[s], out["sursa"][s] = _b.cu_totaluri(tip, s, {int(k): int(v) for k, v in valori[s].items() if int(k) not in tot[s]}), "manual"
        if any(out["sursa"][s] == "manual" for s in sectiuni(tip)):
            out["manual"] = {"exemplar": m["exemplar"], "la": m["produs_la"], "de": m["produs_de"]}
    return out


def coloanele_verificate(cur, schema, tip, an):
    """(coloana „An precedent”, F10 „An curent”) — sau refuzul cu TOATE motivele de oprire ale ambilor ani (deficiența 242): un an
    dinaintea înființării (229) sau al preluării (228) se refuză întâi, singur; motivele de date (6 / 7, solduri fără loc, rulaje) se
    strâng."""
    oprite, cp, f10c = [], None, None
    try:
        cp = coloana_precedenta(cur, schema, tip, an)     # întâi: un an dinaintea înființării se refuză cu motivul lui (229)
    except _b.BilantOprit as e:
        oprite.append(e)
    try:
        f10c = coloana_curenta_f10(cur, schema, an, tip)
    except _b.BilantOprit as e:
        oprite.append(e)
    _b.refuz_impreuna(oprite)
    return cp, f10c


def coloanele(cur, schema, tip, an, av):
    """(f10p, f10c, f20p, f30p) pentru generare (f30p = F30 cap.XIX „An precedent”, numai S1005; None la S1003). „An curent” F10 necunoscut -> refuz (`coloana_curenta_f10`). „An precedent” fără sursă pe o
    secțiune -> refuz: bilanțul nu se generează cu coloana goală (decizia Costin 11.10.2026). Completat manual -> avertismentul vizibil."""
    cp, f10c = coloanele_verificate(cur, schema, tip, an)
    lipsa = [s for s in sectiuni(tip) if cp[s] is None]
    if lipsa:
        raise ValueError(mesaj_coloana_goala(an, lipsa, cp.get("bilant_respins")))
    manual = [s for s in sectiuni(tip) if cp["sursa"][s] == "manual"]
    if manual:
        av.append(avertisment_manual(an, manual, cp["manual"], cp.get("bilant_respins")))
    if "F30" in cp:
        nec = _b.neconcordante_f20_f30(cp["F20"], cp["F30"])
        if nec:
            raise ValueError(mesaj_neconcordanta(an, nec))
    return cp["F10"], f10c, cp["F20"], cp.get("F30")


PRIMUL_EXERCITIU = "primul_exercitiu"
#: [C10; C12, C13] momentul schimbării rândurilor bilanțului (de la el, F20 S1003, F10 și F20 S1005 pe formularul ANAF 2025); un bilanț
#: păstrat de dinainte nu e „An precedent”. 12.10.2026 13:00 UTC: după publicarea C10 (6dea8a28, procesul pornit la 10:33 UTC) și înaintea
#: lotului C12 / C13 — un prag în viitor (13.10, cum era) respingea și bilanțurile generate de codul nou până atunci (prins de plasa 221).
#: Fereastra 13:00 UTC → publicarea lotului se verifică pe producție (read-only) la publicare.
S1003_F20_SCHEMA_NOUA_DIN = _dt.datetime(2026, 10, 12, 13, 0, tzinfo=_dt.timezone.utc)


def fara_cap_xix(xml):
    """[C14] Un S1005 cu activitate (vreun rând F20 nenul) fără niciun rând F30 cap.XIX a fost produs înainte de C14: cap.XIX lipsește
    din el. (Fără activitate, cap.XIX e tot zero — nu lipsește nimic.)"""
    rr = _b.randuri_din_xml(xml)
    return any(x["formular"] == "F20" and x["an_curent"] for x in rr) and not any(x["formular"] == "F30" and x["rand"] >= 167 for x in rr)


def mesaj_neconcordanta(an, nec):
    """[C14] Coloana „An precedent” completată manual: F20 și F30 cap.XIX trebuie să dea aceleași cifre pe rândurile pe care validatorul
    ANAF le compară (`bilant.NOMENCLATOR_CONCORDANTA_F20_F30`)."""
    from core.pdf_util import bani
    det = "; ".join("F20 rândul %02d = %s lei, F30 %s = %s lei" % (r, bani(v20), " + ".join("rândul %d" % k for _s, k in _b.termeni_total(e)),
                                                                     bani(v30)) for r, v20, e, v30 in nec)
    return ("Coloana „An precedent” (%d) nu se potrivește între F20 și F30 cap.XIX, pe rândurile pe care validatorul ANAF le compară: %s. "
            "Corectează cifrele după bilanțul depus pe %d." % (an - 1, det, an - 1))


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
               " și ".join(dict.fromkeys({"F10": "soldurile de la %s" % data_ro("%d-12-31" % (an - 1)), "F20": "tot anul %d" % (an - 1),
                                          "F30": "tot anul %d" % (an - 1)}[s] for s in lipsa)),
               nota_bilant_respins(an, respins), an - 1))


def nota_bilant_respins(an, respins):
    """Bilanțul anului precedent din aplicație care NU se folosește (generat cu soldurile de preluare de după 31.12 a lui — defectul 221;
    sau un S1003 pe numerotarea veche a F20 — C10)."""
    if not respins:
        return ""
    if respins.get("numerotare_veche") and respins.get("tip") == "s1005":
        return (" Bilanțul S1005 pe %d păstrat în aplicație (%s) nu se folosește: rândurile lui sunt dinaintea rescrierii pe listele de "
                "conturi ale formularului ANAF 2025 și a situației veniturilor și cheltuielilor (F30 cap.XIX)."
                % (an - 1, data_ro(respins.get("la"), "cu_ora")))
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
    """Rulajele conturilor din clasele 6 / 7 pe anul `an` — `rulaje_67` pe [01.01.an, 01.01.an+1)."""
    return rulaje_67(cur, schema, _dt.date(an, 1, 1), _dt.date(an + 1, 1, 1))


def rulaje_67(cur, schema, de_la, pana_la):
    """Rulajele conturilor din clasele 6 / 7 pe [de_la, pana_la), din notele validate: {cont: (rulaj debitor, rulaj creditor)}. [C15] FĂRĂ
    închiderea în 121 (o linie cu 121 de partea cealaltă): închiderea mută soldul, nu e venit sau cheltuială — numărată, ar face 0 rulajul
    net al lui 711 / 712 (variația stocurilor) după ce contabilul închide anul, cum îi cere bilanțul (`bilant.inchiderea_6_7`).

    [lotul 10, deficiența 425, comanda Costin 10.1] „Cifra de afaceri a anului (707 = 180.000 lei) și cheltuielile dispar, deci D101,
    bilanțul anual [...] ies greșite pentru o firmă preluată în cursul anului.” Plus rulajele PRELUATE din balanța de deschidere pe
    fereastră (`rulaje_preluate.rulaje`, tot fără închiderea în 121 — OMFP 1802/2014, funcțiunea contului 121). O singură sursă a
    veniturilor și cheltuielilor anului: F20 / F30, categoria de mărime, D101 și D100 pe profit (`d101.baza_contabila`)."""
    from core import rulaje_preluate as _rp
    cur.execute(f"""
        SELECT l.cont_debit, l.cont_credit, l.suma
        FROM {schema}.inregistrari_linii l
        JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
        WHERE i.status = 'validata' AND i.data >= %s AND i.data < %s""",
        (de_la, pana_la))
    rl = {}
    for r in cur.fetchall():
        if str(r["cont_debit"]).startswith("121") or str(r["cont_credit"]).startswith("121"):
            continue
        s = Decimal(str(r["suma"]))
        for cont, idx in ((r["cont_debit"], 0), (r["cont_credit"], 1)):
            if str(cont)[:1] in ("6", "7"):
                v = rl.get(cont, [Decimal("0"), Decimal("0")])
                v[idx] += s
                rl[cont] = v
    for cont, (d, c) in _rp.rulaje(cur, schema, de_la, pana_la, fara_inchidere_121=True).items():
        if str(cont)[:1] in ("6", "7") and (d or c):
            v = rl.get(cont, [Decimal("0"), Decimal("0")])
            v[0] += d
            v[1] += c
            rl[cont] = v
    return {c: (v[0], v[1]) for c, v in rl.items()}


def avertismente_rulaje(cur, schema, an):
    """[lotul 10, deficiența 425] „Când are doar solduri finale [...] aplicația spune clar că rulajele anului lipsesc și ce afectează.”
    Textul afirmației `rulaje_preluate.avertisment` pe F20, ca listă (goală când rulajele anului sunt în aplicație)."""
    from core import rulaje_preluate as _rp
    a = _rp.avertisment(cur, schema, an, "bilant")
    return [a["motiv"]] if a else []


def avertismente_evidenta_an(conn, schema, an):
    """[lotul 10, deficiența 436, comanda Costin 10.2 pct.6 — generalizarea pe clasă: „08 și 09/2026 sunt încheiate, dar fără amortizare
    generată, iar D100 pe T3 nu semnalează”] Bilanțul se face din balanța notelor VALIDATE ale anului, deci spune, ca D100 / D101, ce e în
    afara evidenței validate: amortizarea lunilor încheiate negenerată sau nevalidată și notele nevalidate ale anului — aceeași funcție
    (`d101.avertismente_evidenta`), iar notele nevalidate opresc depunerea (`coada_api.DECLARATII_DIN_EVIDENTA`)."""
    from core import d101 as _d101
    return _d101.avertismente_evidenta(conn, schema, _dt.date(an, 1, 1), _dt.date(an + 1, 1, 1), "Bilanțul pe %d" % an,
                                       efect="rezultatul exercițiului și valoarea netă a imobilizărilor ies mai mari")


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
    # [lotul 10, deficiența C69 — „valoare inventată pe documentul ANAF în loc de blocaj”] județul sediului, marele contribuabil, forma
    # de proprietate și administratorul: verificarea e a antetului (`bilant.erori_antet`, sursa unică, citată acolo din structura ANAF),
    # aceeași pe care `xml_s1005` o face înainte să scrie ceva
    erori.extend(_b.erori_antet(prof))
    return erori


def cod_judet_sediu(judet):
    """Codul din Nomenclatorul Județe (01 Alba … 40 Municipiul București, 51 Călărași, 52 Giurgiu — anaf_surse/d394_struct_anaf.txt,
    „Nomenclator 1- Judete”), ca număr, din județul scris în Date firmă: nume („Cluj”, „București”), prescurtare („CJ”, „B”, cum îl
    aduce ANAF în `dcod_JudetAuto`) sau cod. `None` când lipsește sau nu e în nomenclator — NU un cod implicit. [lotul 10, C69]
    Refolosește `d394.jud_siruta` (aceeași conversie, sursa unică) și o restrânge la codurile nomenclatorului (fără 41: „fara cod 41”)."""
    from core.d394 import jud_siruta, JUDETE_SIRUTA
    cod = jud_siruta(judet)
    return int(cod) if cod in set(JUDETE_SIRUTA.values()) else None


def profil_bilant(p):
    """Datele antetului bilanțului, din rândul `firma_profil` — un singur loc pentru S1005 și S1003. [lotul 10, C69] + marele
    contribuabil, forma de proprietate și prenumele declarantului (antetul le cere: `bilant.erori_antet`); fără administrator implicit."""
    import re
    return {
        "cui_numeric": re.sub(r"\D", "", p.get("cui") or ""),
        "nume": p.get("nume"), "caen": re.sub(r"\D", "", p.get("caen") or ""),
        "reg_com": p.get("reg_com") or "", "adresa": p.get("adresa") or "",
        "cod_judet": cod_judet_sediu(p.get("judet")),   # [lotul 10, C69] fără „bucuresti” / 40 implicit
        "mare_contribuabil": p.get("mare_contribuabil"),   # NULL = nedeclarat -> refuz
        "forma_proprietate": p.get("forma_proprietate"),
        "declarant_nume": p.get("declarant_nume"),
        "declarant_prenume": p.get("declarant_prenume"),
        "interes_public": p.get("interes_public"),   # [lotul 11, decizia 10.3] NULL = nedeclarat -> refuz
    }


def intocmitor_cabinet(cur, schema):
    """[lotul 11, decizia Costin 10.3 pct.4: „calitatea întocmitorului în profilul cabinetului”] Întocmitorul bilanțului, din profilul
    cabinetului care ține firma (`public.accounting_firms`, coloanele din core/migrare_intocmitor_bilant.py): {calit_intocmit,
    intocmit_nume, cif_intocmit, nri_intocmit}; valori None când cabinetul nu le-a completat (`bilant.erori_intocmitor` le cere)."""
    cur.execute("SELECT af.calit_intocmit, af.nume_intocmit, af.cif_intocmit, af.nri_intocmit FROM public.tenants t "
                "JOIN public.accounting_firms af ON af.id = t.accounting_firm_id WHERE t.schema_name = %s", (schema,))
    r = cur.fetchone()
    r = (r if isinstance(r, (tuple, list)) else tuple(r.values())) if r else (None, None, None, None)
    return {"calit_intocmit": r[0], "intocmit_nume": r[1], "cif_intocmit": r[2], "nri_intocmit": r[3]}


#: [lotul 10, C69] câmpul din Date firmă pe care refuzul îl aduce în vedere, în ordinea verificărilor (primul lipsă)
_CAMP_ECRAN = (("reg_com", lambda pr: not str(pr.get("reg_com") or "").strip()),
               ("judet", lambda pr: not pr.get("cod_judet")),
               ("mare_contribuabil", lambda pr: pr.get("mare_contribuabil") is None),
               ("forma_proprietate", lambda pr: str(pr.get("forma_proprietate") or "").strip() not in _b.FORME_PROPRIETATE),
               ("declarant_nume", lambda pr: not _b.nume_administrator(pr)),
               ("interes_public", lambda pr: pr.get("interes_public") is None))   # [lotul 11, decizia 10.3]

#: [lotul 11, decizia 10.3] câmpurile întocmitorului, în profilul cabinetului (ecranul `date_cabinet`, id-urile din
#: `static/js/ecrane/intocmitor_bilant.js`), în ordinea verificărilor din `bilant.erori_intocmitor`
_CAMP_CABINET = (("calit_intocmit", lambda pr: pr.get("calit_intocmit") not in _b.CALITATI_INTOCMIT),
                 ("nume_intocmit", lambda pr: not str(pr.get("intocmit_nume") or "").strip()),
                 ("cif_intocmit", lambda pr: pr.get("calit_intocmit") in _b.CODURI_CALITATE_CU_CIF
                  and not str(pr.get("cif_intocmit") or "").strip()))


def camp_lipsa(prof):
    """Câmpul din Date firmă pe care refuzul îl aduce în vedere (`RefuzGenerare.camp_ecran`): primul lipsă, în ordinea verificărilor."""
    _camp = next((c for c, lipsa in _CAMP_ECRAN if lipsa(prof)), None)
    return ("df-" + _camp) if _camp else None


def tinta_refuz(prof):
    """(ecran, câmp) spre care trimite refuzul bilanțului: întâi Date firmă (primul câmp lipsă), apoi profilul cabinetului (întocmitorul,
    decizia 10.3). Un refuz are un singur buton; textul refuzului le numește pe toate."""
    c = camp_lipsa(prof)
    if c:
        return "date_firma", c
    _camp = next((c for c, lipsa in _CAMP_CABINET if lipsa(prof)), None)
    return ("date_cabinet", "cab-" + _camp) if _camp else ("date_firma", None)


def cere_an_incheiat(an, tip):
    """[lotul 10, deficiența 383, comanda Costin 10.2 pct.1: „O declarație pe o perioadă neîncheiată se refuză la generare, cu motivul scris,
    la toate declarațiile.”] Ecranul Bilanț generează pe drumul lui (`uc_tenants.s1005_xml` / `s1005_valideaza` / `s1003_*`), nu prin
    dispecer — refuzul stă deci și în generator, cu aceeași regulă (`coada_api.perioada_neincheiata`)."""
    from core import coada_api as _coada
    motiv = _coada.perioada_neincheiata(an, None, tip=tip)
    if motiv:
        raise RefuzGenerare(motiv)


def genereaza(conn, schema, an):
    cere_an_incheiat(an, "s1005")
    av = []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.firma_profil WHERE id = 1")
        cere_coloane_cursor(cur, _COLOANE_PROFIL, "firma_profil")   # [garda 27.07.2026]
        p = dict(cur.fetchone() or {})
        _int = intocmitor_cabinet(cur, schema)   # [lotul 11, decizia 10.3] întocmitorul, din profilul cabinetului
        f10p, f10c, f20p, f30p = coloanele(cur, schema, "s1005", an, av)
        rl = _rulaje_67(cur, schema, an)
        av.extend(avertismente_rulaje(cur, schema, an))
    av.extend(avertismente_evidenta_an(conn, schema, an))   # [lotul 10, 436] ce e în afara evidenței validate a anului
    prof = dict(profil_bilant(p), **_int)
    if not prof["reg_com"]:
        av.append("Nr. Reg. Com. lipsă în Profil firma (câmp obligatoriu S1005).")
    f20c = _b.f20_din_rulaje(rl)
    if f10c.get(15) != f10c.get(49):
        av.append(f"Verificare: rândul 15 (F) = {f10c.get(15)} diferă de rândul 49 (J) = {f10c.get(49)} — datoriile peste un an, "
                  "provizioanele sau veniturile în avans pot explica diferența.")
    _er = erori_generare(prof)
    if _er:   # [lotul 10, C69] refuzul trimite la Date firmă (butonul și câmpul de completat), ca la D406
        _ecran, _camp = tinta_refuz(prof)   # [lotul 11, decizia 10.3] Date firmă sau profilul cabinetului (întocmitorul)
        raise RefuzGenerare("Bilanț nu se poate genera: " + " ".join(_er), ecran=_ecran, camp_ecran=_camp)
    return _b.xml_s1005(prof, an, f10p, f10c, f20p, f20c, f30p, _b.f30_din_rulaje(rl)), av


def genereaza_s1003(conn, schema, an):
    """S1003 (mici): F10 identic, F20 complet."""
    cere_an_incheiat(an, "s1003")
    av = []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.firma_profil WHERE id = 1")
        cere_coloane_cursor(cur, _COLOANE_PROFIL, "firma_profil")   # [garda 27.07.2026]
        p = dict(cur.fetchone() or {})
        _int = intocmitor_cabinet(cur, schema)   # [lotul 11, decizia 10.3] întocmitorul, din profilul cabinetului
        f10p, f10c, f20p, _f30p = coloanele(cur, schema, "s1003", an, av)
        rl = _rulaje_67(cur, schema, an)
        av.extend(avertismente_rulaje(cur, schema, an))
    av.extend(avertismente_evidenta_an(conn, schema, an))   # [lotul 10, 436] ce e în afara evidenței validate a anului
    prof = dict(profil_bilant(p), **_int)
    f20c = _b.f20_complet_din_rulaje(rl)
    _er = erori_generare(prof)
    if _er:   # [lotul 10, C69] refuzul trimite la Date firmă (butonul și câmpul de completat), ca la D406
        _ecran, _camp = tinta_refuz(prof)   # [lotul 11, decizia 10.3] Date firmă sau profilul cabinetului (întocmitorul)
        raise RefuzGenerare("Bilanț nu se poate genera: " + " ".join(_er), ecran=_ecran, camp_ecran=_camp)
    return _b.xml_s1003(prof, an, f10p, f10c, f20p, f20c), av
