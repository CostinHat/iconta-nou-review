# -*- coding: utf-8 -*-
"""core/z_descarcare.py — raportul Z la firma cu stocul CANTITATIV-VALORIC (lotul „Deciziile 07.10”, D3).

Decizia Costin (07.10.2026, pct.3), verbatim: „Raportul Z la cantitativ-valoric: fără refuz. Descărcarea pe articol se cere
explicit (manual sau prin rețetă); Z-ul nu se validează fără ea.”

  · Z-ul se înregistrează (fără refuz), dar la cantitativ-valoric ca CIORNĂ: validarea trece pe unicul drum
    (`jurnal_api.valideaza` — jurnalul și coada), unde stă poarta de mai jos.
  · Descărcarea = ieșiri pe articol LEGATE de Z (`miscari_stoc.z_inregistrare_id`): manual (`stocuri_cv_api.iesire`) sau prin
    rețetă (`retete_api.descarca`), cu `z_id`. Z-ul n-are articole (casa de marcat nu le dă), deci ce s-a vândut din stoc
    spune omul — aplicația nu ghicește.
  · Z-ul în care nu s-a vândut marfă din stoc (numai servicii) se declară EXPLICIT „fără marfă” (`rapoarte_z_amef.fara_marfa`);
    nimic nu e presupus.
Temei: OMFP 1802/2014 pct.287 alin.(1)-(2) — „Metoda aleasă trebuie aplicată cu consecvență” (la cantitativ-valoric ieșirile se
evaluează pe articol, la CMP — `stocuri_cv`); la global-valoric Z-ul rămâne pe descărcarea lunară cu K (neschimbat).
"""
from decimal import Decimal, ROUND_HALF_UP

from psycopg2.extras import Json as _Json, RealDictCursor

from core import afirmatii as _af
from core.common import cate as _cate
from core.unde import Unde as _Unde

MESAJ_NEDESCARCAT = ("Raportul Z (nota %s) nu se validează fără descărcarea mărfii vândute: la stocul cantitativ-valoric ieșirea "
                     "se face pe articol. Pe ecranul Raport Z, la acest raport: „Ieșire pe articol” sau „Consum pe rețetă” — ori, "
                     "dacă n-a vândut marfă din stoc, „Fără marfă din stoc”.")
COD_NEDESCARCAT = "Z_NEDESCARCAT"


def _p(schema):
    return ('"%s".' % str(schema).strip('"')) if schema else ""


def e_z(cur, schema, nota_id):
    cur.execute("SELECT 1 FROM %srapoarte_z_amef WHERE inregistrare_id = %%s" % _p(schema), (int(nota_id),))
    return cur.fetchone() is not None


def stare(cur, schema, nota_id):
    """{"iesiri": n (ieșiri VII legate de Z), "fara_marfa": True/False/None}."""
    p = _p(schema)
    cur.execute(f"""SELECT (SELECT count(*) FROM {p}miscari_stoc m WHERE m.z_inregistrare_id = z.inregistrare_id
                              AND m.anuleaza_id IS NULL AND NOT EXISTS (SELECT 1 FROM {p}miscari_stoc r WHERE r.anuleaza_id = m.id)),
                           z.fara_marfa
                    FROM {p}rapoarte_z_amef z WHERE z.inregistrare_id = %s""", (int(nota_id),))
    r = cur.fetchone()
    if not r:
        return None
    r = tuple(r.values()) if isinstance(r, dict) else r
    return {"iesiri": int(r[0]), "fara_marfa": r[1]}


def refuz_validare(cur, schema, nota_id):
    """Mesajul refuzului (sau None): nota e un raport Z, firma e cantitativ-valorică, iar Z-ul n-are nici ieșiri legate, nici
    declarația „fără marfă”. Apelat din `jurnal_api.valideaza` — unicul drum de validare."""
    from core import metoda_stoc as _ms
    st = stare(cur, schema, nota_id)
    if st is None or st["iesiri"] > 0 or st["fara_marfa"] is True:
        return None
    if _ms.citeste(cur, schema) != _ms.CV:
        return None
    from core import eticheta_nota as _et   # [deficiența 258] nota cum o vede omul, nu id-ul ei
    return MESAJ_NEDESCARCAT % _et.nota(cur, schema, nota_id)


def cere_z(cur, schema, z_id):
    """Z-ul de care se leagă o ieșire: există, e raport Z, e încă ciornă (un Z validat nu mai primește descărcări). Întoarce
    id-ul sau ridică ValueError cu motivul."""
    try:
        zid = int(z_id)
    except (TypeError, ValueError):
        raise ValueError("Raportul Z ales nu e valid.")
    cur.execute("SELECT status FROM %sinregistrari WHERE id = %%s" % _p(schema), (zid,))
    r = cur.fetchone()
    st = (r["status"] if isinstance(r, dict) else r[0]) if r else None
    if st is None or not e_z(cur, schema, zid):
        raise ValueError("Raportul Z ales nu există.")
    if st != "ciorna":
        from core import eticheta_nota as _et
        raise ValueError("Raportul Z ales (nota %s) e deja validat: descărcarea se leagă numai de un Z nevalidat."
                         % _et.nota(cur, schema, zid))
    return zid


def document_z(cur, schema, z_id):
    """[lotul 10, deficiența 438] Documentul justificativ al vânzării de pe un raport Z: raportul Z însuși, cu textul notei lui
    („Raport Z nr 0042 din 20.10.2026 (casa 8000000001)” — `jurnal_api.eticheta_document`, scris la înregistrarea Z-ului, pe ambele
    rute). Comanda 10.2 pct.8a: „Bonul de consum e pentru consum intern; la vânzarea pe Z documentul e raportul Z (nr. 0042, casa
    8000000001).” Un Z fără text de document (scris înainte de 05.10.2026) se numește din cheia lui (casa + numărul, `Z-<casa>-<nr>`)
    și din dată — numai din ce există în date. Temei: Legea 82/1991 art.6 alin.(1): „Orice operațiune economico-financiară efectuată
    se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate”."""
    cur.execute("SELECT i.document_ref, i.numar, i.data, z.nui FROM %sinregistrari i JOIN %srapoarte_z_amef z ON z.inregistrare_id = i.id "
                "WHERE i.id = %%s" % (_p(schema), _p(schema)), (int(z_id),))
    r = cur.fetchone()
    if not r:
        return None
    doc, numar, data, nui = (r["document_ref"], r["numar"], r["data"], r["nui"]) if isinstance(r, dict) else tuple(r)
    if doc and str(doc).strip():
        return str(doc).strip()
    from core import jurnal_api as _j
    pref = "Z-%s-" % nui
    nr = numar[len(pref):] if numar and str(numar).startswith(pref) else None
    return _j.eticheta_document("Raport Z", nr, data, "casa %s" % nui)


def deblocat(zid):
    """[368] Z-ul descărcat pe articol / pe rețetă sau declarat „fără marfă” nu mai e refuzat la validare: la partidă simplă, unde nota
    lui se validează automat, middleware-ul o reîncearcă la sfârșitul cererii (`autor_cerere.reincearca_interna`)."""
    from core import autor_cerere as _ac
    _ac.reincearca_interna(zid)


def marcheaza_fara_marfa(conn, schema, nota_id, fara_marfa):
    """Declarația explicită: în Z nu s-a vândut marfă din stoc (True) / retrasă (None). Numai pe un Z nevalidat."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        zid = cere_z(cur, schema, nota_id)
        st = stare(cur, schema, zid)
        if fara_marfa and st["iesiri"]:
            raise ValueError("Raportul Z are deja %s de el — nu poate fi „fără marfă”." % _cate(st["iesiri"], "ieșire din stoc legată", "ieșiri din stoc legate"))
        cur.execute("UPDATE %srapoarte_z_amef SET fara_marfa = %%s WHERE inregistrare_id = %%s" % _p(schema),
                    (True if fara_marfa else None, zid))
    if fara_marfa:
        deblocat(zid)
    return {"ok": True, "nota_id": zid, "fara_marfa": True if fara_marfa else None}


#: [lotul 12, C139] sumele raportului Z citite din nota lui — o singură definiție, pentru lista lunii și pentru confirmarea ștergerii:
#: încasatul (5311 / 5125 = 707) și TVA-ul colectat (707 = 4427)
_SQL_INCASAT = ("(SELECT COALESCE(SUM(l.suma), 0) FROM {p}inregistrari_linii l WHERE l.inregistrare_id = i.id AND l.cont_credit = '707' "
                "AND l.cont_debit <> '707')")
_SQL_TVA = ("(SELECT COALESCE(SUM(l.suma), 0) FROM {p}inregistrari_linii l WHERE l.inregistrare_id = i.id AND l.cont_debit = '707' "
            "AND l.cont_credit = '4427')")


def lista_luna(conn, schema, an, luna):
    """Rapoartele Z ale lunii, cu starea descărcării (pentru ecranul Raport Z). [lotul 10, comanda 10.2 pct.8e] „După descărcare nu se
    vede valoarea descărcată” -> `valoare_descarcata`: suma ieșirilor VII legate de Z (la CMP, cât a ieșit din 371 pe 607).
    [lotul 12, C139] `stergere`: ce ar șterge „Șterge raportul Z” (confirmarea, cu cifrele) sau de ce nu se poate (`plan_stergere`)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        p = _p(schema)
        cur.execute(f"""SELECT i.id, i.data, i.numar, i.status, z.nui, z.nr_bonuri, z.fara_marfa,
                               {_SQL_INCASAT.format(p=p)} AS incasat, {_SQL_TVA.format(p=p)} AS tva
                        FROM {p}inregistrari i JOIN {p}rapoarte_z_amef z ON z.inregistrare_id = i.id
                        WHERE date_trunc('month', i.data) = %s ORDER BY i.data, i.id""", ("%d-%02d-01" % (int(an), int(luna)),))
        out = []
        for r in cur.fetchall():
            st = stare(cur, schema, r["id"])
            v = valoare_descarcata(cur, schema, r["id"])
            # [lotul 12, deficiența 474] „Z validat cu descărcare parțială din stoc, fără avertisment”: vânzarea fără TVA a Z-ului (707 net),
            # alături de costul descărcat, ca ecranul să le pună față în față înainte de validare (avertismentul `avertisment_descarcare`)
            net = Decimal(str(r["incasat"])) - Decimal(str(r["tva"]))
            pl = plan_stergere(cur, schema, r["id"], verifica_costul=False)
            rand = {"id": r["id"], "data": r["data"].isoformat(), "numar": r["numar"], "status": r["status"], "nui": r["nui"],
                    "nr_bonuri": r["nr_bonuri"], "incasat": str(r["incasat"]), "vanzari_fara_tva": str(net), "iesiri": st["iesiri"],
                    "fara_marfa": st["fara_marfa"], "valoare_descarcata": str(v),
                    "stergere": {"refuz": pl["refuz"], "cod": pl["cod"], "confirmare": pl["confirmare"]}}
            av = avertisment_descarcare(net, Decimal(str(v)), st["iesiri"])
            if av:   # afirmația despre descărcarea Z-ului e un obiect (`core/afirmatii.py`); ecranul îi citește textul din `avertisment`
                rand.update(_af.afirmatie(
                    "fapt", "descarcare_z", av, avertisment=av,
                    unde=_Unde("inregistrare", r["id"], document_z(cur, schema, r["id"])),
                    temei_completitudine="ieșirile din stoc legate de Z și nota lui; Z-ul n-are articole, deci completitudinea "
                                         "descărcării n-o poate ști aplicația — de-aia o confirmă contabilul"))
            out.append(rand)
    return out


# ── [lotul 12, C139] ȘTERGEREA RAPORTULUI Z NEVALIDAT ────────────────────────────────────────────────────────────────────────────────
# Deficiența C139 (găsită de Code la scenariul pilot, pasul 13): „Un raport Z importat (ciornă) nu se poate șterge de nicăieri: Registrul
# jurnal refuză nota derivată, iar pentru Raport Z nu există drum de ștergere — un fișier AMEF importat greșit rămâne în lună.” Clasa: orice
# raport Z nevalidat (importul AMEF și Z-ul scris de mână au aceeași cheie, `rapoarte_z_amef`), la orice metodă de stoc și la orice regim.
# Drumul: pe rândul Z-ului din ecranul Raport Z (`note_derivate.UNDE["raport_z"]`: „se corectează numai de acolo”), într-o tranzacție:
# Z-ul (nota ciornă, cu defalcarea pe cote și casa + bonurile, prin ON DELETE CASCADE), descărcările lui din stoc încă necontate (ieșirile
# legate și notele lor ciornă — marfa revine în stoc) și, la partidă simplă, încasarea lui ciornă din registrul de încasări și plăți.
# Un Z validat nu se șterge: a intrat în evidență, iar corectura e stornarea — OMFP 1802/2014 pct.69: „Înregistrarea stornării unei
# operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale
# (stornare în roșu), fie prin înregistrarea inversă a acesteia (stornare în negru)”. Aceeași regulă o ține baza (`regula_nota`,
# `regula_stoc`), iar luna blocată (`verifica_perioada_blocata*`). Ce se șterge se spune înainte, cu cifrele; urma rămâne în audit.
COD_Z_NU_SE_STERGE = "Z_NU_SE_STERGE"
COD_LUNA_BLOCATA = "LUNA_BLOCATA"
TEMEI_STERGERE = "OMFP 1802/2014 pct.69"
MESAJ_Z_VALIDAT = ("%s e validat (nota %s): a intrat în evidență, deci nu se mai șterge. O greșeală se corectează prin stornare "
                   "(OMFP 1802/2014 pct.69), în Registru jurnal: o notă cu aceleași conturi și sumele cu minus.")
MESAJ_Z_VALIDAT_SIMPLA = ("%s e în evidență (TVA-ul lui intră în decontul de TVA și în D394), deci nu se mai șterge. O greșeală se "
                          "corectează prin stornare (OMFP 1802/2014 pct.69).")
MESAJ_LUNA_BLOCATA = ("%s nu se mai șterge: luna %s e blocată. Cere-i administratorului cabinetului să o redeschidă, apoi îl poți "
                      "șterge.")
MESAJ_IESIRE_VALIDATA = ("%s nu se mai șterge: descărcarea lui din stoc (nota %s) e validată, deci marfa a ieșit în evidență. O greșeală "
                         "se corectează prin stornare (OMFP 1802/2014 pct.69).")
MESAJ_LA_VALIDARE = ("%s nu se șterge acum: nota %s e la validare în cabinet — cât timp așteaptă, nu se modifică și nu se șterge. Dacă "
                     "raportul e greșit, cabinetul o respinge cu motiv, iar după aceea îl poți șterge.")
MESAJ_COST_SCHIMBAT = ("%s nu se poate șterge: după descărcarea lui, articolul „%s” are o intrare și alte ieșiri (prima: %s din %s). "
                       "Ștergerea descărcării ar schimba costul acelor ieșiri în fișa de magazie (la costul mediu ponderat), fără să le "
                       "schimbe notele. Raportul Z rămâne; o greșeală se corectează prin stornare (OMFP 1802/2014 pct.69).")
MESAJ_RIP_VALIDATA = ("%s nu se mai șterge: încasarea lui din registrul de încasări și plăți e validată. O greșeală se corectează în "
                      "registru, prin stornare (OMFP 1802/2014 pct.69).")
MESAJ_DESCARCARE_AMESTECATA = ("%s nu se poate șterge de aici: o descărcare legată de el poartă și alte mișcări de stoc. Șterge-o întâi "
                               "din Stoc.")
#: [368] explicația încasării Z-ului în registrul de încasări și plăți (partidă simplă) — aceeași formă în care o scrie înregistrarea Z-ului
EXPLICATIE_RIP = "Încasări în numerar, raport Z nr. %s, casa %s"


def _rand(cur, coloane):
    r = cur.fetchone()
    if r is None:
        return None
    return dict(r) if isinstance(r, dict) else dict(zip(coloane, r))


def _nr_raport(numar, nui):
    pref = "Z-%s-" % nui
    return numar[len(pref):] if numar and str(numar).startswith(pref) else None


def _schimba_costul(cur, schema, sterse, articole):
    """(articol, ieșirea) — prima ieșire rămasă al cărei cost (la CMP, în fișa de magazie) s-ar schimba dacă mișcările `sterse` ar
    dispărea, sau None. Fișa refăcută fără ele (`stocuri_cv.fisa_magazie`, motorul unic) față de fișa de acum."""
    from core import repo_stocuri, stocuri_cv as _cv
    for aid in sorted(articole):
        m = repo_stocuri.miscari_ale_articolului(cur, schema, aid)
        # [696.1, 14.3] fișa de acum are ieșirile la valoarea din notă (cea scrisă pe mișcare); „ce-ar fi fără ele” se recalculează la CMP, ca să se vadă
        # dacă ștergerea ar schimba costul unei ieșiri rămase față de nota ei
        inainte = {x["id"]: Decimal(str(x["valoare"] or 0)) for x in m}
        ramase = [x for x in m if x["id"] not in sterse]
        try:
            dupa = _cv.fisa_magazie(ramase, recalculeaza=True)
        except ValueError:
            return aid, (ramase[0] if ramase else None)
        for x in dupa:
            if x["tip"] == "iesire" and x["id"] in inainte and Decimal(str(x["valoare"])) != inainte[x["id"]]:
                return aid, x
    return None


def plan_stergere(cur, schema, nota_id, verifica_costul=True):
    """Ce ar șterge „Șterge raportul Z” — fără să scrie nimic. None dacă nota nu e un raport Z. Altfel {"z": {...}, "note_iesiri": [ids],
    "miscari": [ids], "rip": id|None, "refuz": text|None, "cod": cod|None, "confirmare": text|None}. `verifica_costul=False` (lista lunii)
    sare peste refacerea fișelor de magazie; ștergerea o face mereu."""
    from core import coada_api as _coada, contare_facturi as _cf, eticheta_nota as _et
    from core.migrare_api import regim_contabil as _regim
    from core.pdf_util import bani, data_ro
    p = _p(schema)
    cur.execute(f"""SELECT i.id, i.data, i.numar, i.status, z.nui, {_SQL_INCASAT.format(p=p)} AS incasat, {_SQL_TVA.format(p=p)} AS tva
                    FROM {p}inregistrari i JOIN {p}rapoarte_z_amef z ON z.inregistrare_id = i.id WHERE i.id = %s""", (int(nota_id),))
    z = _rand(cur, ("id", "data", "numar", "status", "nui", "incasat", "tva"))
    if not z:
        return None
    doc = document_z(cur, schema, z["id"])
    # [lotul 13, 605] „Textul «raportul Z Raport Z nr»”: documentul („Raport Z nr 0042 din …”) se numește o dată — „Raportul Z nr 0042 din …”
    eticheta = ("Raportul Z" + doc[len("Raport Z"):]) if doc.startswith("Raport Z ") else "Raportul Z „%s”" % doc
    plan = {"z": {"id": z["id"], "data": str(z["data"])[:10], "document": doc, "incasat": str(z["incasat"]), "tva": str(z["tva"])},
            "note_iesiri": [], "miscari": [], "rip": None, "refuz": None, "cod": None, "confirmare": None, "dupa": None}

    def refuz(text, cod=COD_Z_NU_SE_STERGE):
        plan.update(refuz=text, cod=cod)
        return plan
    cur.execute(f"SELECT tip_firma FROM {p}firma_profil WHERE id = 1")
    tf = _rand(cur, ("tip_firma",))
    simpla = bool(tf) and _regim(tf["tip_firma"]) == "simpla"   # [368] la partidă simplă omul nu vede note contabile
    if z["status"] != "ciorna":
        return refuz(MESAJ_Z_VALIDAT_SIMPLA % eticheta if simpla else MESAJ_Z_VALIDAT % (eticheta, _et.nota(cur, schema, z["id"])))
    # descărcările lui: mișcările legate de Z și tot ce stă pe notele lor (stornarea la respingere poartă aceeași notă, fără Z)
    cur.execute(f"SELECT DISTINCT inregistrare_id FROM {p}miscari_stoc WHERE z_inregistrare_id = %s AND inregistrare_id IS NOT NULL",
                (z["id"],))
    note = sorted((x["inregistrare_id"] if isinstance(x, dict) else x[0]) for x in cur.fetchall())
    col = ("id", "articol_id", "inregistrare_id", "z_inregistrare_id", "anuleaza_id", "status", "data")
    cur.execute(f"""SELECT m.id, m.articol_id, m.inregistrare_id, m.z_inregistrare_id, m.anuleaza_id, i.status, i.data
                    FROM {p}miscari_stoc m LEFT JOIN {p}inregistrari i ON i.id = m.inregistrare_id
                    WHERE m.z_inregistrare_id = %s OR m.inregistrare_id = ANY(%s) ORDER BY m.id""", (z["id"], note))
    mis = [dict(x) if isinstance(x, dict) else dict(zip(col, x)) for x in cur.fetchall()]
    ale_z = {x["id"] for x in mis if x["z_inregistrare_id"] == z["id"]}
    if any(x["inregistrare_id"] is None or (x["id"] not in ale_z and x["anuleaza_id"] not in ale_z) for x in mis):
        # o notă de descărcare care poartă și altceva decât ieșirile acestui Z (sau o ieșire fără notă): n-o desfacem pe jumătate
        return refuz(MESAJ_DESCARCARE_AMESTECATA % eticheta)
    for d in sorted({str(z["data"])[:10]} | {str(x["data"])[:10] for x in mis if x["data"]}):
        if _cf.luna_blocata(cur, str(schema).strip('"'), d):
            return refuz(MESAJ_LUNA_BLOCATA % (eticheta, data_ro(d)[3:]), COD_LUNA_BLOCATA)
    for nid in [z["id"]] + note:
        if _coada.nota_la_validare(cur, schema, nid):
            return refuz(MESAJ_LA_VALIDARE % (eticheta, _et.nota(cur, schema, nid)), _coada.COD_NOTA_LA_VALIDARE)
    for x in mis:
        if x["status"] != "ciorna":
            return refuz(MESAJ_IESIRE_VALIDATA % (eticheta, _et.nota(cur, schema, x["inregistrare_id"])))
    # [368] la partidă simplă: încasarea lui în registrul de încasări și plăți, scrisă odată cu el (aceeași explicație)
    if simpla:
        nr = _nr_raport(z["numar"], z["nui"])
        cur.execute(f"""SELECT id, status FROM {p}rip_operatiuni WHERE tip = 'incasare' AND document_tip = 'raport Z'
                          AND document_numar = %s AND document_data = %s AND explicatie = %s ORDER BY id LIMIT 1""",
                    (nr, z["data"], EXPLICATIE_RIP % (nr, z["nui"])))
        rip = _rand(cur, ("id", "status"))
        if rip and rip["status"] != "ciorna":
            return refuz(MESAJ_RIP_VALIDATA % eticheta)
        plan["rip"] = rip["id"] if rip else None
    if verifica_costul and mis:
        sc = _schimba_costul(cur, schema, {x["id"] for x in mis}, {x["articol_id"] for x in mis})
        if sc:
            aid, ies = sc
            cur.execute(f"SELECT denumire FROM {p}articole WHERE id = %s", (aid,))
            den = (_rand(cur, ("denumire",)) or {}).get("denumire") or "articolul"
            return refuz(MESAJ_COST_SCHIMBAT % (eticheta, den, (ies or {}).get("document") or "ieșirea", data_ro((ies or {}).get("data"))))
    plan.update(note_iesiri=note, miscari=[x["id"] for x in mis])
    vii = [x for x in mis if x["id"] in ale_z and x["anuleaza_id"] is None and not any(y["anuleaza_id"] == x["id"] for y in mis)]
    et_note = ", ".join("nota %s" % e for _i, e in _et.note(cur, schema, note))
    cu = (["TVA-ul lui pe cote (din decontul de TVA și din D394)"]
          + (["încasarea lui din registrul de încasări și plăți (ciornă)"] if plan["rip"] else []) if simpla
          else ["nota lui ciornă (%s), cu TVA-ul lui pe cote" % _et.nota(cur, schema, z["id"])])
    if vii:
        cu.append("%s, în valoare de %s lei la cost (%s)"
                  % (_cate(len(vii), "ieșire din stoc legată de el, necontată", "ieșiri din stoc legate de el, necontate"),
                     bani(valoare_descarcata(cur, schema, z["id"])), et_note))
    elif note:
        cu.append("descărcările lui respinse la validare (%s)" % et_note)
    sume = "încasat %s lei, TVA %s lei" % (bani(z["incasat"]), bani(z["tva"]))
    plan["confirmare"] = ("Ștergi %s (%s)? Se șterg odată cu el: %s.%s Ștergerea nu se poate anula."
                          % (eticheta[0].lower() + eticheta[1:], sume, "; ".join(cu), " Marfa descărcată revine în stoc." if vii else ""))
    plan["dupa"] = ("%s s-a șters (%s), odată cu: %s.%s" % (eticheta, sume, "; ".join(cu),
                                                           " Marfa descărcată a revenit în stoc." if vii else ""))
    return plan


def sterge_z(conn, schema, nota_id, user_id=None, tenant_id=None):
    """Șterge raportul Z nevalidat după `plan_stergere`, în tranzacția apelantului, cu urma în `public.audit_log` (aceeași tranzacție).
    Întoarce planul — cu `refuz` dacă nu se poate, și atunci nu s-a scris nimic — sau None dacă nota nu e un raport Z."""
    p = _p(schema)
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # nota Z-ului blocată până la sfârșitul tranzacției: o validare sau o descărcare nouă legată de el (cheia străină) așteaptă
        cur.execute(f"SELECT id FROM {p}inregistrari WHERE id = %s FOR UPDATE", (int(nota_id),))
        if not cur.fetchone():
            return None
        plan = plan_stergere(cur, schema, nota_id)
        if plan is None or plan["refuz"]:
            return plan
        if plan["miscari"]:
            # stornarea la respingere (`anuleaza_id`) arată spre ieșirea stornată: legătura cade întâi, apoi ieșirile, apoi stornările
            # (în ordinea asta stocul nu trece niciodată sub zero — `regula_stoc_nenegativ`)
            cur.execute(f"UPDATE {p}miscari_stoc SET anuleaza_id = NULL WHERE id = ANY(%s) AND anuleaza_id IS NOT NULL", (plan["miscari"],))
            cur.execute(f"DELETE FROM {p}miscari_stoc WHERE id = ANY(%s) AND cantitate > 0", (plan["miscari"],))
            cur.execute(f"DELETE FROM {p}miscari_stoc WHERE id = ANY(%s)", (plan["miscari"],))
        if plan["note_iesiri"]:
            cur.execute(f"DELETE FROM {p}inregistrari WHERE id = ANY(%s) AND status = 'ciorna'", (plan["note_iesiri"],))
        if plan["rip"]:
            cur.execute(f"DELETE FROM {p}rip_operatiuni WHERE id = %s AND status = 'ciorna'", (plan["rip"],))
        cur.execute(f"DELETE FROM {p}inregistrari WHERE id = %s AND status = 'ciorna'", (int(nota_id),))
        if cur.rowcount != 1:   # nimic nu rămâne pe jumătate: tranzacția apelantului se întoarce
            raise RuntimeError("raportul Z %s nu s-a șters" % int(nota_id))
        fapt = _af.afirmatie(
            "fapt", "STERGERE_RAPORT_Z", plan["confirmare"][:500], unde="raportul Z #%s" % int(nota_id),
            temei_completitudine="urma se scrie în aceeași tranzacție cu ștergerea, deci nu poate exista ștergere fără ea",
            nota_id=int(nota_id), document=plan["z"]["document"], data=plan["z"]["data"], incasat=plan["z"]["incasat"],
            tva=plan["z"]["tva"], note_iesiri=plan["note_iesiri"], miscari_stoc=plan["miscari"], rip=plan["rip"])
        cur.execute("INSERT INTO public.audit_log (user_id, tenant_id, actiune, entitate, entitate_id, detalii) "
                    "VALUES (%s, (SELECT id FROM public.tenants WHERE id = %s), 'STERGERE raport Z', 'raport_z', %s, %s)",
                    (user_id, tenant_id, str(int(nota_id)), _Json(fapt)))
    return plan


def avertisment_descarcare(vanzari_fara_tva, cost_descarcat, iesiri):
    """PURĂ. [lotul 12, deficiența 474] Textul pe care contabilul îl confirmă înainte de a valida un Z descărcat pe articol. Z-ul n-are
    articole (casa de marcat nu le dă), deci aplicația NU poate ști dacă descărcarea e completă: spune cifrele (vânzarea fără TVA, costul
    mărfii descărcate, adaosul care ar rezulta) și cere confirmarea. Costul peste vânzare (marfă vândută sub cost, sau descărcată de două
    ori) se spune separat. None fără ieșiri legate (Z-ul nedescărcat nu se validează; „fără marfă” e declarația omului)."""
    from core.pdf_util import bani
    if not iesiri:
        return None
    v, c = Decimal(str(vanzari_fara_tva)), Decimal(str(cost_descarcat))
    baza = ("Ai descărcat din stoc %s la cost %s lei, pentru vânzări de %s lei fără TVA pe acest Z" %
            (_cate(iesiri, "ieșire", "ieșiri"), bani(c), bani(v)))
    if c > v:
        return baza + (": costul mărfii descărcate e MAI MARE decât vânzarea. Verifică cantitățile (o ieșire pusă de două ori?) înainte "
                       "de validare.")
    if c > 0:
        adaos = ((v - c) * 100 / c).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return baza + (" (adaos %s%%). Z-ul nu spune ce articole s-au vândut: dacă au mai ieșit și alte articole, descarcă-le înainte de "
                       "validare — după validare nu se mai leagă ieșiri de el." % adaos)
    return baza + ". Z-ul nu spune ce articole s-au vândut: verifică dacă ai descărcat tot."


def valoare_descarcata(cur, schema, nota_id):
    """Valoarea ieșirilor VII legate de Z (nici stornări, nici stornate) — ce s-a descărcat din stoc pentru vânzarea de pe el."""
    p = _p(schema)
    cur.execute(f"""SELECT COALESCE(SUM(m.valoare), 0) AS v FROM {p}miscari_stoc m WHERE m.z_inregistrare_id = %s
                      AND m.anuleaza_id IS NULL AND NOT EXISTS (SELECT 1 FROM {p}miscari_stoc r WHERE r.anuleaza_id = m.id)""",
                (int(nota_id),))
    r = cur.fetchone()
    return r["v"] if isinstance(r, dict) else r[0]
