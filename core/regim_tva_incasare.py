"""
core/regim_tva_incasare.py — regimul firmei în sistemul TVA la încasare (deficiența 428, lotul 10, comanda Costin 10.1).

[lotul 10, deficiența 428] „Firma nu poate fi declarată ca aplicând sistemul: vectorul fiscal are doar «Înregistrată în scopuri de
TVA: Da/Nu» […]. Construiește regimul pe firmă, cu data de la care se aplică și verificarea în registrul ANAF.”

CITIRE (stabilă — o folosesc motorul contabil și declarațiile):
    perioade(cur) -> [{id, de_la: date, pana_la: date|None, sursa, verificat_anaf_la, stare_anaf}], în ordinea lui de_la
    aplica_la(cur, data) -> bool        True dacă `data` (date sau 'YYYY-MM-DD') cade într-o perioadă: de_la <= data <= pana_la
                                        (pana_la NULL = se aplică în continuare). Firmă FĂRĂ nicio perioadă înregistrată: indicatorul
                                        vechi `firma_profil.tva_la_incasare` (nedatat), vezi `aplica_la`.
`cur` e un cursor pe schema firmei (search_path pus de `db.get_conn(schema)`); nimic de aici nu deschide conexiuni și nu comite.

SCRIERE: `salveaza` (perioada curentă: intrare / corectură / ieșire), `sterge` (o perioadă scrisă din greșeală), `inregistreaza_anaf`
(rezultatul verificării în registrul ANAF). Fiecare schimbare se jurnalizează prin `repo_firma_profil.jurnalizeaza_regim_tva`
(PIVOT DECIZII 04.10.2026: regimul de TVA la „Poate pregăti”, cu jurnalizarea fiecărei schimbări), iar indicatorul
`firma_profil.tva_la_incasare` („se aplică azi”) se sincronizează din perioade în aceeași tranzacție (`sincronizeaza`).

TEMEIUL (citat verbatim din anaf_surse/cod_fiscal_227_2015_consolidat.txt, forma în vigoare de la 01.03.2026):
- CF art.282 alin.(3): „exigibilitatea taxei intervine la data încasării contravalorii integrale sau parțiale a livrării de bunuri ori a
  prestării de servicii, în cazul persoanelor impozabile care optează în acest sens, denumite în continuare persoane care aplică
  sistemul TVA la încasare.”
- CF art.282 alin.(3^1) lit.a): eligibile sunt „persoanele impozabile înregistrate în scopuri de TVA conform art. 316 […] Persoana
  impozabilă care […] optează pentru aplicarea sistemului TVA la încasare, aplică sistemul TVA la încasare începând cu prima zi a
  perioadei fiscale următoare celei în care persoana impozabilă și-a exercitat opțiunea”;
  lit.b): „Persoana impozabilă care optează pentru aplicarea sistemului TVA la încasare începând cu data înregistrării în scopuri de TVA
  aplică sistemul TVA la încasare începând cu această dată. Persoana impozabilă care optează […] ulterior, în cursul anului
  înregistrării în scopuri de TVA, aplică sistemul TVA la încasare începând cu prima zi a perioadei fiscale următoare celei în care
  și-a exercitat opțiunea”.
- CF art.282 alin.(5): „Persoana impozabilă care optează pentru aplicarea sistemului TVA la încasare este obligată să aplice sistemul
  respectiv cel puțin până la sfârșitul anului calendaristic în care a optat pentru aplicarea sistemului, cu excepția situației în care
  în cursul aceluiași an cifra de afaceri depășește plafonul prevăzut la alin. (3) , caz în care sistemul se aplică până la sfârșitul
  perioadei fiscale următoare celei în care plafonul a fost depășit. […] Radierea persoanei respective din Registrul persoanelor care
  aplică sistemul TVA la încasare se realizează de organele fiscale competente începând cu prima zi a perioadei fiscale următoare
  celei în care a fost depusă notificarea.”

DE AICI, REGULILE (refuz = legea nu admite altfel; avertisment = legea admite și alt caz, pe care aplicația nu-l poate vedea):
- numai la firmă înregistrată în scopuri de TVA (alin.(3^1) lit.a/b) — refuz;
- „de la” = prima zi a unei perioade fiscale (lit.a, lit.b teza a 3-a) SAU data înregistrării în scopuri de TVA (lit.b teza a 2-a) —
  refuz pe altă zi decât 1 a lunii (orice perioadă fiscală începe pe 1); avertisment la decont trimestrial pe o lună din mijlocul
  trimestrului (periodicitatea de atunci poate fi alta decât cea de azi);
- „de la” nu e înaintea înregistrării în scopuri de TVA — refuz;
- „până la” (ultima zi în care se aplică) = sfârșitul unei perioade fiscale: și ieșirea prin depășirea plafonului („până la sfârșitul
  perioadei fiscale următoare”), și radierea („începând cu prima zi a perioadei fiscale următoare”) se termină la capăt de perioadă —
  refuz pe altă zi decât ultima a lunii; avertisment la decont trimestrial în afara capătului de trimestru;
- ieșirea înainte de sfârșitul anului în care a optat — AVERTISMENT, nu refuz: alin.(5) admite excepția depășirii plafonului;
- perioadele nu se suprapun — refuz (o zi e sau nu e în sistem).
"""
from __future__ import annotations

import datetime as _dt

MODUL = "regim_tva_incasare"

_COLOANE = ("id", "de_la", "pana_la", "sursa", "verificat_anaf_la", "stare_anaf")

#: câmpul de jurnal al perioadelor (text: „de la 01.03.2026 până la 31.12.2026; …”) — trece prin `jurnalizeaza_regim_tva`
CAMP_JURNAL = "tva_incasare_perioade"
COD_NEINREGISTRAT = "TVAI_FARA_INREGISTRARE_TVA"


# ── citire (stabilă) ────────────────────────────────────────────────────────────────────────────────────────────────
def _data(x):
    """date | 'YYYY-MM-DD' | datetime -> date (refuz numit pentru altceva)."""
    if isinstance(x, _dt.datetime):
        return x.date()
    if isinstance(x, _dt.date):
        return x
    try:
        return _dt.date.fromisoformat(str(x).strip()[:10])
    except (TypeError, ValueError):
        raise ValueError("dată invalidă pentru regimul TVA la încasare: %r" % (x,))


def _rand(r):
    return list(r.values()) if isinstance(r, dict) else list(r)


def perioade(cur):
    """Perioadele în care firma aplică sistemul TVA la încasare, în ordine cronologică (pana_la None = în curs)."""
    cur.execute("SELECT id, de_la, pana_la, sursa, verificat_anaf_la, stare_anaf FROM tva_incasare_perioade ORDER BY de_la, id")
    return [dict(zip(_COLOANE, _rand(r))) for r in cur.fetchall()]


def aplica_la(cur, data):
    """True dacă firma aplică sistemul TVA la încasare la `data` (CF art.282 alin.(3)): o perioadă cu de_la <= data <= pana_la.

    INTERPRETARE CU TEMEI (tranziția, lotul 10): o firmă fără NICIO perioadă înregistrată are numai indicatorul vechi, nedatat,
    `firma_profil.tva_la_incasare` (scris din ANAF RTVAI.statusTvaIncasare la adăugarea firmei) — pe el se răspunde, ca înainte de
    perioade, pentru orice dată. Alternativa respinsă: „fără perioadă = nu aplică” ar fi scos tacit din sistem firmele marcate din ANAF
    până să li se scrie data. Prima perioadă înregistrată (manual sau din ANAF) înlocuiește indicatorul; ecranul cere data cât timp
    lipsește (`stare()['fara_data']`). De reconfirmat când toate firmele marcate au perioada scrisă."""
    d = _data(data)
    cur.execute("SELECT (SELECT count(*) FROM tva_incasare_perioade), "
                "EXISTS (SELECT 1 FROM tva_incasare_perioade WHERE de_la <= %s AND (pana_la IS NULL OR pana_la >= %s)), "
                "(SELECT COALESCE(tva_la_incasare, false) FROM firma_profil WHERE id = 1)", (d, d))
    n, in_perioada, indicator = _rand(cur.fetchone())
    return bool(in_perioada) if n else bool(indicator)


# ── reguli pure (temeiul în antet) ──────────────────────────────────────────────────────────────────────────────────
def _ultima_zi(d):
    return (_dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1) - _dt.timedelta(days=1))


def _ro(d):
    from core.pdf_util import data_ro   # DS cap.4: formatul datei afișate, sursa unică
    return data_ro(d) if d else "—"


def text_perioade(lista):
    """Forma de jurnal / afișare: „de la 01.03.2026 până la 31.12.2026; de la 01.01.2027” (gol -> None)."""
    if not lista:
        return None
    return "; ".join("de la %s%s" % (_ro(p["de_la"]), (" până la %s" % _ro(p["pana_la"])) if p.get("pana_la") else "")
                     for p in lista)


def valideaza(de_la, pana_la, platitor_tva, tva_data_inceput=None, tip_decont=None, altele=()):
    """PURĂ. (erori [(camp, mesaj)], avertismente [mesaj]) pentru o perioadă [de_la, pana_la]. `altele` = celelalte perioade.
    Temeiul fiecărei reguli: antetul modulului (CF art.282 alin.(3^1), (5))."""
    er, av = [], []
    if platitor_tva is not True:
        er.append(("tva_incasare", "Sistemul TVA la încasare se aplică numai de firmele înregistrate în scopuri de TVA (Cod fiscal "
                                   "art. 282 alin. (3^1)). Alege întâi „Înregistrată în scopuri de TVA: Da”."))
        return er, av
    if de_la is None:
        er.append(("tva_incasare_de_la", "Scrie data de la care firma aplică sistemul TVA la încasare."))
        return er, av
    tva_in = _data(tva_data_inceput) if tva_data_inceput else None
    trim = str(tip_decont or "").strip().lower() in ("trimestrial", "t")
    if tva_in and de_la < tva_in:
        er.append(("tva_incasare_de_la", "Sistemul TVA la încasare nu se aplică înainte de înregistrarea în scopuri de TVA (%s): "
                                         "data „de la” e %s." % (_ro(tva_in), _ro(de_la))))
    elif de_la.day != 1 and de_la != tva_in:
        er.append(("tva_incasare_de_la", "Sistemul TVA la încasare se aplică de la prima zi a unei perioade fiscale sau de la data "
                                         "înregistrării în scopuri de TVA (Cod fiscal art. 282 alin. (3^1)), nu de la %s." % _ro(de_la)))
    elif trim and de_la.month % 3 != 1 and de_la != tva_in:
        av.append("Firma depune decontul trimestrial: perioada fiscală e trimestrul, iar sistemul se aplică de la prima zi a perioadei "
                  "fiscale (Cod fiscal art. 282 alin. (3^1)). %s nu e început de trimestru — verifică dacă periodicitatea era alta "
                  "atunci." % _ro(de_la))
    if pana_la is not None:
        if pana_la < de_la:
            er.append(("tva_incasare_pana_la", "Data „până la” (%s) e înaintea datei „de la” (%s)." % (_ro(pana_la), _ro(de_la))))
        elif pana_la != _ultima_zi(pana_la):
            er.append(("tva_incasare_pana_la", "Ieșirea din sistemul TVA la încasare are loc la sfârșitul unei perioade fiscale (Cod "
                                               "fiscal art. 282 alin. (5)): „până la” e ultima zi în care se aplică — ultima zi a "
                                               "lunii, nu %s." % _ro(pana_la)))
        else:
            if trim and pana_la.month % 3 != 0:
                av.append("Firma depune decontul trimestrial: ieșirea are loc la sfârșitul perioadei fiscale (trimestrul). %s nu e "
                          "sfârșit de trimestru — verifică dacă periodicitatea era alta atunci." % _ro(pana_la))
            if pana_la < _dt.date(de_la.year, 12, 31):
                av.append("Cine optează aplică sistemul cel puțin până la sfârșitul anului în care a optat (31.12.%d), cu excepția "
                          "depășirii plafonului în cursul anului (Cod fiscal art. 282 alin. (5)). Verifică motivul ieșirii la %s."
                          % (de_la.year, _ro(pana_la)))
    for p in altele or ():
        sf = p.get("pana_la")
        if de_la <= (sf or _dt.date.max) and p["de_la"] <= (pana_la or _dt.date.max):
            er.append(("tva_incasare_de_la", "Perioada se suprapune cu cea înregistrată deja (%s)." % text_perioade([p])))
            break
    return er, av


# ── stare pentru ecran ──────────────────────────────────────────────────────────────────────────────────────────────
def _iso(d):
    return d.isoformat() if hasattr(d, "isoformat") else d


def stare(cur, azi=None):
    """Ce arată vectorul fiscal: perioadele (ISO), perioada curentă (ultima), dacă se aplică azi, plus `fara_data` (indicatorul
    vechi pus, nicio perioadă) și avertismentul firmei care nu mai e înregistrată în scopuri de TVA cu sistemul încă deschis."""
    azi = azi or _dt.date.today()
    lista = perioade(cur)
    cur.execute("SELECT platitor_tva, COALESCE(tva_la_incasare, false) FROM firma_profil WHERE id = 1")
    r = cur.fetchone()
    platitor, indicator = (_rand(r) if r else (None, False))
    ultima = lista[-1] if lista else None
    av = []
    if lista and platitor is False and any(p["pana_la"] is None or p["pana_la"] >= azi for p in lista):
        av.append("Firma nu mai e înregistrată în scopuri de TVA, dar sistemul TVA la încasare e încă deschis (%s): scrie data "
                  "„până la”." % text_perioade([ultima]))
    return {"aplica_azi": aplica_la(cur, azi),
            "fara_data": (not lista) and bool(indicator),
            "curenta": ({**{k: _iso(v) for k, v in ultima.items()}} if ultima else None),
            "perioade": [{k: _iso(v) for k, v in p.items()} for p in lista],
            "avertismente": av}


# ── scriere ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def sincronizeaza(cur, user_id, azi=None):
    """`firma_profil.tva_la_incasare` = se aplică azi, din perioade (numai dacă există perioade; altfel indicatorul rămâne cum e).
    Schimbarea se jurnalizează (PIVOT 04.10.2026). Întoarce valoarea."""
    from core import repo_firma_profil as _rfp
    if not perioade(cur):
        return None
    azi = azi or _dt.date.today()
    vechi = _rfp.regim_tva_pentru_schimbare(cur)
    if vechi is None:
        return None
    acum = aplica_la(cur, azi)
    cur.execute("UPDATE firma_profil SET tva_la_incasare = %s WHERE id = 1", (acum,))
    _rfp.jurnalizeaza_regim_tva(cur, vechi, {"tva_la_incasare": acum}, user_id)
    return acum


def _luna_inchisa_de_la(cur, d):
    """Prima lună închisă (perioade_blocate) de la luna lui `d` încolo, sau None. [R46, aplicat regimului TVA la încasare] Perioadele
    decid exigibilitatea TVA (CF art.282 alin.(3)) — deci ce s-a declarat pe lunile închise; o schimbare care atinge o lună închisă ar
    rescrie trecutul. Spre deosebire de vector (orice lună închisă oprește), aici contează numai lunile pe care schimbarea le atinge:
    o intrare în sistem de la o lună deschisă nu rescrie nimic."""
    cur.execute("SELECT an, luna FROM perioade_blocate WHERE (an, luna) >= (%s, %s) ORDER BY an, luna LIMIT 1", (d.year, d.month))
    r = cur.fetchone()
    return _rand(r) if r else None


def _refuz_luna_inchisa(cur, d):
    from core.mesaje import MESAJ_PESTE_PERIOADA_INCHISA
    r = _luna_inchisa_de_la(cur, d) if d else None
    if not r:
        return None
    return {"ok": False, "camp": "tva_incasare_de_la",
            "mesaj": MESAJ_PESTE_PERIOADA_INCHISA % {"ce": "Regimul TVA la încasare", "an": r[0], "luna": int(r[1])}}


def _prima_zi_schimbata(vechi, nou):
    """Prima zi a cărei stare (în sistem / în afara lui) se schimbă între perioada `vechi` și `nou` ((de_la, pana_la) sau None)."""
    zi = []
    v1, v2 = vechi or (None, None)
    n1, n2 = nou or (None, None)
    if v1 != n1:
        zi += [x for x in (v1, n1) if x]
    if (vechi and nou) and v2 != n2:   # ieșirea mutată: se schimbă ziua de după cea mai devreme dintre cele două „până la”
        zi += [x + _dt.timedelta(days=1) for x in (v2, n2) if x]
    return min(zi) if zi else None


def _context(cur):
    cur.execute("SELECT platitor_tva, platitor_tva_anaf_inceput, tip_decont FROM firma_profil WHERE id = 1")
    r = cur.fetchone()
    return _rand(r) if r else (None, None, None)


def salveaza(cur, aplica, de_la=None, pana_la=None, user_id=None, azi=None):
    """[428] Perioada CURENTĂ (ultima) a sistemului TVA la încasare: intrare, corectură, ieșire.

    - `aplica` False: fără perioade -> nimic de scris; cu perioade -> refuz (ieșirea are o dată: „până la”; o perioadă scrisă greșit
      se șterge, `sterge`).
    - `aplica` True: dacă ultima perioadă e deschisă sau `de_la` cade până la sfârșitul ei -> o corectează; altfel -> perioadă nouă.
    Întoarce {ok, avertismente, stare} sau {ok: False, camp, mesaj}. Jurnalizat; indicatorul sincronizat. Nu comite."""
    from core import repo_firma_profil as _rfp
    if user_id is None:
        return {"ok": False, "camp": None, "mesaj": "Regimul TVA la încasare se schimbă cu utilizatorul care îl schimbă — lipsește."}
    lista = perioade(cur)
    if not aplica:
        if not lista:
            # indicatorul vechi (din ANAF, la adăugarea firmei), fără perioadă: „Nu” îl stinge — schimbare de regim, jurnalizată
            vechi = _rfp.regim_tva_pentru_schimbare(cur)
            if vechi and vechi.get("tva_la_incasare"):
                cur.execute("UPDATE firma_profil SET tva_la_incasare = false WHERE id = 1")
                _rfp.jurnalizeaza_regim_tva(cur, vechi, {"tva_la_incasare": False}, user_id)
            return {"ok": True, "avertismente": [], "stare": stare(cur, azi)}
        return {"ok": False, "camp": "tva_incasare",
                "mesaj": "Firma are înregistrat sistemul TVA la încasare (%s). Ieșirea din sistem are o dată: alege „Da” și scrie "
                         "„până la” (ultima zi în care s-a aplicat). O perioadă scrisă din greșeală se șterge din lista perioadelor."
                         % text_perioade(lista)}
    try:
        d1 = _data(de_la) if de_la not in (None, "") else None
    except ValueError:
        return {"ok": False, "camp": "tva_incasare_de_la", "mesaj": "Data „de la”: o dată (zi, lună, an)."}
    try:
        d2 = _data(pana_la) if pana_la not in (None, "") else None
    except ValueError:
        return {"ok": False, "camp": "tva_incasare_pana_la", "mesaj": "Data „până la”: o dată (zi, lună, an)."}
    ultima = lista[-1] if lista else None
    corecteaza = bool(ultima and d1 and (ultima["pana_la"] is None or d1 <= ultima["pana_la"]))
    altele = lista[:-1] if corecteaza else lista
    platitor, tva_in, decont = _context(cur)
    er, av = valideaza(d1, d2, platitor, tva_in, decont, altele)
    if er:
        return {"ok": False, "camp": er[0][0], "mesaj": er[0][1]}
    if corecteaza and (ultima["de_la"], ultima["pana_la"]) == (d1, d2):
        return {"ok": True, "avertismente": av, "stare": stare(cur, azi)}
    _rf = _refuz_luna_inchisa(cur, _prima_zi_schimbata((ultima["de_la"], ultima["pana_la"]) if corecteaza else None, (d1, d2)))
    if _rf:
        return _rf
    vechi = _rfp.regim_tva_pentru_schimbare(cur)
    if corecteaza:
        cur.execute("UPDATE tva_incasare_perioade SET de_la = %s, pana_la = %s, sursa = 'manual' WHERE id = %s", (d1, d2, ultima["id"]))
    else:
        cur.execute("INSERT INTO tva_incasare_perioade (de_la, pana_la, sursa) VALUES (%s, %s, 'manual')", (d1, d2))
    _rfp.jurnalizeaza_regim_tva(cur, dict(vechi or {}, **{CAMP_JURNAL: text_perioade(lista)}),
                                {CAMP_JURNAL: text_perioade(perioade(cur))}, user_id)
    sincronizeaza(cur, user_id, azi)
    return {"ok": True, "avertismente": av, "stare": stare(cur, azi)}


def sterge(cur, perioada_id, user_id, azi=None):
    """[428] Șterge o perioadă scrisă din greșeală (jurnalizat). Fără perioade rămase, indicatorul se pune pe „nu se aplică” — omul a
    spus că perioada nu era reală. Întoarce {ok, stare} sau {ok: False, mesaj}."""
    from core import repo_firma_profil as _rfp
    if user_id is None:
        return {"ok": False, "mesaj": "Regimul TVA la încasare se schimbă cu utilizatorul care îl schimbă — lipsește."}
    lista = perioade(cur)
    p = next((x for x in lista if x["id"] == perioada_id), None)
    if p is None:
        return {"ok": False, "mesaj": "Perioada nu există (poate a fost ștearsă deja)."}
    _rf = _refuz_luna_inchisa(cur, p["de_la"])
    if _rf:
        return {"ok": False, "mesaj": _rf["mesaj"]}
    vechi = _rfp.regim_tva_pentru_schimbare(cur)
    cur.execute("DELETE FROM tva_incasare_perioade WHERE id = %s", (perioada_id,))
    rest = perioade(cur)
    _rfp.jurnalizeaza_regim_tva(cur, dict(vechi or {}, **{CAMP_JURNAL: text_perioade(lista)}), {CAMP_JURNAL: text_perioade(rest)}, user_id)
    if rest:
        sincronizeaza(cur, user_id, azi)
    else:
        cur.execute("UPDATE firma_profil SET tva_la_incasare = false WHERE id = 1")
        _rfp.jurnalizeaza_regim_tva(cur, vechi, {"tva_la_incasare": False}, user_id)
    return {"ok": True, "stare": stare(cur, azi)}


# ── verificarea în registrul ANAF (RTVAI) ───────────────────────────────────────────────────────────────────────────
#: sursa verificării, cum o numește afirmația (`sursele` / `unde`)
REGISTRU_ANAF = "ANAF: Registrul persoanelor care aplică sistemul TVA la încasare"
def compara_anaf(rtvai, curenta):
    """PURĂ. Afirmația verificării: ce spune ANAF (statusul la data interogării + datele RTVAI), ce propune (datele ANAF, ca
    „de la” / „până la”) și dacă diferă de perioada scrisă. `rtvai` = `anaf_api` (`tva_incasare_rtvai`); `curenta` = perioada curentă
    (dict cu date) sau None. Întoarce o AFIRMAȚIE TIPATĂ (decizia Costin 21.08.2026: afirmațiile despre datele firmei sunt obiecte):
    `contradictie` când registrul ANAF diferă de perioada scrisă în iConta (`sursele` le numește pe amândouă), altfel `fapt` (cu
    `unde` = registrul ANAF, la data verificării); plus {status, de_la, pana_la, propunere, diferente: [text], mesaj}. Ecranul
    alege culoarea după `fel` („fapt” = confirmare)."""
    from core import afirmatii as _af
    status = bool((rtvai or {}).get("status"))
    a1, a2 = (rtvai or {}).get("data_inceput"), (rtvai or {}).get("data_sfarsit")
    dif = []
    if curenta:
        c1, c2 = curenta.get("de_la"), curenta.get("pana_la")
        c1 = _data(c1) if c1 else None
        c2 = _data(c2) if c2 else None
        if a1 and c1 != _data(a1):
            dif.append("„de la”: în iConta %s, la ANAF %s" % (_ro(c1), _ro(_data(a1))))
        if a2 and c2 != _data(a2):
            dif.append("„până la”: în iConta %s, la ANAF %s" % (_ro(c2), _ro(_data(a2))))
        if not a2 and c2 and status:
            dif.append("„până la”: în iConta %s, la ANAF fără dată de ieșire" % _ro(c2))
    elif status or a1:
        dif.append("în iConta nu e înregistrată nicio perioadă")
    # o dată din registru care nu e AAAA-LL-ZZ (forma celorlalte date ale serviciului) nu se ghicește: se arată, nu se propune
    brut = (rtvai or {}).get("brut") or {}
    nedate = [k for k, cheie in (("dataInceputTvaInc", "data_inceput"), ("dataSfarsitTvaInc", "data_sfarsit"))
              if str(brut.get(k) or "").strip() and not (rtvai or {}).get(cheie)]
    parti = ["ANAF (Registrul persoanelor care aplică sistemul TVA la încasare): %s" % (
        "firma aplică sistemul la data verificării" if status else "firma NU aplică sistemul la data verificării")]
    if a1:
        parti.append("de la %s%s" % (_ro(_data(a1)), (" până la %s" % _ro(_data(a2))) if a2 else ""))
    for k in nedate:
        parti.append("data din registru („%s”) nu e în forma așteptată (AAAA-LL-ZZ) — n-o propun" % brut.get(k))
    if dif:
        parti.append("diferă de ce e scris în iConta: " + "; ".join(dif))
    elif curenta or status:
        parti.append("coincide cu ce e scris în iConta")
    mesaj = ". ".join(parti) + "."
    if dif:
        af = _af.afirmatie("contradictie", "sistemul TVA la încasare", mesaj,
                           sursele=["iConta: perioada scrisă în Date firmă", REGISTRU_ANAF])
    else:
        af = _af.afirmatie("fapt", "sistemul TVA la încasare", mesaj, unde="%s, la data verificării" % REGISTRU_ANAF,
                           temei_completitudine="răspunsul serviciului ANAF pentru CUI-ul firmei, la data verificării")
    return dict(af, status=status, de_la=a1, pana_la=a2, propunere={"de_la": a1, "pana_la": a2} if a1 else None, diferente=dif,
                mesaj=mesaj)


def inregistreaza_anaf(cur, rezultat, azi=None):
    """Consemnează verificarea pe perioada curentă (`verificat_anaf_la`, `stare_anaf`) — un fapt despre verificare, nu o schimbare a
    regimului (perioadele nu se ating: ANAF propune, omul alege și salvează)."""
    lista = perioade(cur)
    if lista:
        cur.execute("UPDATE tva_incasare_perioade SET verificat_anaf_la = now(), stare_anaf = %s WHERE id = %s",
                    (rezultat["mesaj"], lista[-1]["id"]))
    return stare(cur, azi)
