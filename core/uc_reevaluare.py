# -*- coding: utf-8 -*-
"""USE_CASE — reevaluarea lunară a elementelor monetare în valută, propusă de aplicație (lotul 10, deficiența 429).

Comanda Costin 20.10.2026 (10.1 pct.8, verbatim în DECIZII „Comanda 10.1”): „La închiderea lunii, aplicația propune singură creanțele
și datoriile în valută neîncasate (pe factură), disponibilitățile în valută, cursul din evidență, cursul BNR din ultima zi bancară și
diferența pe 665/765; contabilul verifică și generează nota.”

Temeiul și regulile propunerii: `core/reevaluare_valuta.py` (OMFP 1802/2014 pct.325). Aici: tranzacția, drepturile, perioada,
cursul BNR adus ÎNAINTEA tranzacției (`uc_curs_bnr.asigura_cursul`, ca `uc_comun._preincalzeste_cursul`) și nota (ciornă — R36:
nimic nu se scrie `validata` direct; a doua generare înlocuiește ciorna nevalidată a lunii, cu același document intern).
[lotul 11, 429] UN SINGUR FORMULAR: fostul formular manual din Operațiuni (`uc_tenants.reevaluare_valuta`, ruta
`POST /tenants/{id}/reevaluare-valuta`) a fost scos — Costin, pe producție, a ajuns la el și nu la propunere („formular manual, fără
propunere, fără curs BNR”). Ajustarea manuală (un cont pe care aplicația nu-l propune) e în același formular, marcată (`manuale`).
Refuzurile completărilor vin toate deodată, fiecare lângă câmpul ei (`erori_campuri`).
"""
import calendar as _cal
from datetime import date as _date, timedelta as _td

from core import db
from core import erori as _erori
from core import reevaluare_valuta as _rv
from core import repo_contabilitate
from core import uc_comun as _uc_comun


def _sfarsit(an, luna):
    return _date(int(an), int(luna), _cal.monthrange(int(an), int(luna))[1])


def _ultima_zi_lucratoare(zi):
    while zi.weekday() >= 5:
        zi -= _td(days=1)
    return zi


def _aduce_cursurile(schema, sfarsit, monede_in_plus=()):
    """Cursul BNR al ultimei zile bancare a lunii, adus în cache ÎNAINTEA tranzacției (descărcarea ține până la 3x10 s). Pragul e
    distanța până la ultima zi LUCRĂTOARE a lunii: un curs mai vechi decât ea în cache nu e „cel din ultima zi bancară” (OMFP 1802/2014
    pct.325 alin.(2) lit.b), deci se cere BNR-ului — cu regula sfârșitului de lună (`curs_bnr.REGULA_SFARSIT_LUNA`: și cursul comunicat
    chiar în ultima zi). O zi de sărbătoare legală cade în același caz și se recere — declarat. Tăcută la eșec, ca
    `_preincalzeste_cursul`: refuzul vine din propunere (cursul lipsă se arată pe element)."""
    from core import curs_bnr as _cb
    from core import uc_curs_bnr as _uc_cb
    with db.get_conn(schema) as conn, conn.cursor() as cur:
        monede = {r["moneda"] for r in _rv.reevaluari(cur, schema, sfarsit)}
        monede |= {f["moneda"] for f in _rv.facturi_in_valuta(cur, schema, sfarsit)}
    monede |= {str(m).strip().upper() for m in monede_in_plus if m}
    prag = (sfarsit - _ultima_zi_lucratoare(sfarsit)).days
    for m in sorted(x for x in monede if x and x != "RON"):
        try:
            _uc_cb.asigura_cursul(m, sfarsit, prag_zile=prag, regula=_cb.REGULA_SFARSIT_LUNA)
        except Exception:      # noqa: BLE001 — pre-încălzirea nu poate strica o cerere (ca `_preincalzeste_cursul`)
            pass


def _monede_din(completari, manuale=()):
    return [c.get("moneda") for c in list((completari or {}).values()) + list(manuale or []) if isinstance(c, dict)]


def _forma(completari, manuale):
    """Forma cererii: completările pe element {cheie: {sold_valuta?, moneda?, clauza?}} și rândurile ajustării manuale [{cont, moneda,
    sold_valuta, clauza?}]. JSON (la recalculare, în cerere) sau deja obiecte (la generare, în corp)."""
    import json
    c, m = completari or {}, manuale or []
    try:
        c = json.loads(c) if isinstance(c, str) else c
        m = json.loads(m) if isinstance(m, str) else m
    except ValueError:
        c = None
    if not (isinstance(c, dict) and all(isinstance(v, dict) for v in c.values())
            and isinstance(m, list) and all(isinstance(v, dict) for v in m)):
        raise _erori.DateInvalide("Completările trebuie trimise pe element (cheia elementului din propunere), iar ajustările manuale ca "
                                  "listă de rânduri.")   # FORMĂ: forma cererii
    return c, m


def _propunerea(cur, schema, an, luna, completari, manuale):
    """`reevaluare_valuta.propunere`, cu refuzurile completărilor traduse: toate deodată, fiecare pe câmpul ei de pe ecran."""
    try:
        return _rv.propunere(cur, schema, an, luna, completari=completari, manuale=manuale)
    except _rv.RefuzReevaluare as e:   # FORMĂ: completările de pe ecran (mesajele numite în `reevaluare_valuta`)
        raise _erori.DateInvalide({"mesaj": "Corectează câmpurile marcate: %s" % str(e), "erori_campuri": e.erori})


def reevaluare_valuta_propunere(tenant_id, an, luna, ctx, completari=None, manuale=None):
    """Propunerea lunii: elementele în valută cu soldul, cursul din evidență, cursul BNR (cu data lui) și diferența pe 665 / 765.
    `completari` / `manuale` (JSON): ce a scris contabilul pe ecran — propunerea se recalculează cu ele, fără să scrie nimic."""
    _uc_comun._cere_perioada(an, luna)
    comp, man = _forma(completari, manuale)
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    sfarsit = _sfarsit(an, luna)
    _aduce_cursurile(schema, sfarsit, _monede_din(comp, man))
    with db.get_conn(schema) as conn, conn.cursor() as cur:
        prop = _propunerea(cur, schema, an, luna, comp, man)
    from core import inchidere_luna as _il
    prop["luna_in_curs"] = _il.luna_in_curs(an, luna)
    return _public(prop)


def _ce_lipseste(e):
    """Ce cere un element înainte de generare, în limba contabilului (refuzul generării, lângă câmpul lui)."""
    nume = e.get("document") or e.get("partener") or ""
    if e.get("plati_de_legat"):
        # [lotul 11, F] suma și data în forma românească (`bani` / `data_ro`, DS cap.4), iar partenerul numit cu NUMELE lui — nu prin
        # facturile lui („partenerul Factură EX nr. 3 …”); fără nume, prin codul fiscal (cheia partenerului)
        from core.pdf_util import bani, data_ro
        cine = e.get("partener") or ("cu codul fiscal %s" % e["partener_cheie"].lstrip("~") if e.get("partener_cheie") else "fără nume")
        return ("leagă de factura pe care o stinge plata nelegată de %s (%s): partenerul %s are facturi în mai multe monede, deci nu se "
                "poate afla în ce monedă e plata" % (", ".join("%s din %s" % (bani(p["lei"], "lei"), data_ro(p["data"]))
                                                               for p in e["plati_de_legat"]), e["cont"], cine))
    return "completează %s pe contul %s%s" % (" și ".join({"sold_valuta": "soldul în valută", "moneda": "moneda",
                                                          "clauza": "dacă soldul e în lei cu clauză valutară (Da / Nu)"}[c]
                                                          for c in e["de_completat"]), e["cont"], (" (%s)" % nume) if nume else "")


def _camp_lipsa(e):
    """Câmpul de pe ecran pe care stă refuzul elementului: rândul manual, sau câmpul elementului."""
    c = (e["de_completat"] or ["sold_valuta"])[0]
    return ("rv-m%d-%s" % (e["rand_manual"], c)) if e.get("rand_manual") is not None else "rv-%s-%s" % (c, e["cheie"])


def _public(prop):
    """Linia notei (tuplu cu Decimal) nu pleacă pe fir; ecranul are contul și diferența."""
    for e in prop["elemente"]:
        e.pop("linie", None)
    return prop


def reevaluare_valuta_genereaza(tenant_id, corp, ctx):
    """Generează nota lunii din propunere (ciornă), cu completările contabilului: corp {an, luna, completari: {cheie: {sold_valuta?,
    moneda?, clauza?}}, manuale: [{cont, moneda, sold_valuta, clauza?}]}. Întoarce nota (eticheta ei), totalurile și câte elemente s-au
    reevaluat."""
    try:
        an, luna = int(corp["an"]), int(corp["luna"])
    except (KeyError, TypeError, ValueError) as e:
        raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e) if isinstance(e, KeyError) else "Luna sau anul nu sunt numere.")   # FORMĂ
    completari, manuale = _forma(corp.get("completari"), corp.get("manuale"))
    _uc_comun._cere_perioada(an, luna)
    _uc_comun._cere_luna_incheiata(an, luna, "Reevaluarea în valută a lunii")
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    sfarsit = _sfarsit(an, luna)
    _aduce_cursurile(schema, sfarsit, _monede_din(completari, manuale))
    from core import note_derivate as _nd
    from core.pdf_util import data_ro
    with db.get_conn() as conn:
        _uc_comun._cere_luna_deschisa(conn, schema, sfarsit)
        with conn.cursor() as cur:
            prop = _propunerea(cur, schema, an, luna, completari, manuale)
            lipsa = [e for e in prop["elemente"] if e["de_completat"] or e.get("plati_de_legat")]
            if lipsa:   # FORMĂ: un câmp lipsă (soldul în valută / moneda) sau o plată nelegată, pe care aplicația nu le ghicește (DS cap.17)
                raise _erori.DateInvalide({"mesaj": "Înainte de a genera nota, %s." % "; ".join(_ce_lipseste(e) for e in lipsa),
                                           "erori_campuri": [{"camp": _camp_lipsa(e), "mesaj": _ce_lipseste(e)} for e in lipsa]})
            fara_curs = [e for e in prop["elemente"] if e.get("curs_bnr") is None]
            if fara_curs:
                # normativ: OMFP 1802/2014 pct.325 alin.(1) cere cursul BNR din ultima zi bancară a lunii — fără el nota nu se scrie
                # cu alt curs. Refuzul e o afirmație tipată (decizia 21.08: lipsa cursului într-o sursă NUMITĂ), cu temeiul ca dată
                from core import afirmatii as _af
                m = fara_curs[0].get("motiv_curs") or "Cursul BNR al lunii nu e disponibil — reîncearcă."
                raise _erori.Conflict(dict(_af.afirmatie("absenta_observatie", "reevaluare valută", m,
                                                         surse_consultate="cursurile BNR, pentru ultima zi bancară a lunii"),
                                           mesaj=m, temei=_rv.TEMEI))
            de_scris = [e for e in prop["elemente"] if e.get("linie")]
            doc_vechi = None
            inlocuite = []
            for nid in prop["ciorna_lunii"]:   # T1: ciorna nevalidată (sau respinsă) a lunii se înlocuiește; cea validată nu se atinge
                if _nd.respinsa(cur, schema, nid) or _nd.ciorna_nevalidata(cur, schema, nid):
                    doc_vechi = doc_vechi or repo_contabilitate.documentul_notei(cur, schema, nid)
                    _nd.sterge_ciorna_inlocuita(cur, schema, nid)
                    inlocuite.append(nid)
            if not de_scris:
                conn.commit()
                from core import afirmatii as _af   # afirmație tipată (P8), ca la formularul manual
                return dict(_af.afirmatie("fapt", "reevaluare valută", "nicio diferență de curs de înregistrat", an=an, luna=luna,
                                          temei_completitudine="elementele în valută ale firmei la sfârșitul lunii, la cursul BNR "
                                          "din ultima zi bancară"),
                            **_rv.totaluri(prop["elemente"]), inregistrare_id=None, elemente=len(prop["elemente"]),
                            inlocuita=bool(inlocuite), mesaj="Nicio diferență de curs de înregistrat în luna aceasta.")
            data_curs = sorted({e["data_curs"] for e in de_scris if e.get("data_curs")})
            descr = ("Reevaluare valută la %s (%s, curs BNR din %s)" % (
                data_ro(sfarsit), _rv.TEMEI, ", ".join(data_ro(d) for d in data_curs)))[:200]
            if doc_vechi:
                repo_contabilitate.search_path_firma(cur, schema)
                iid = repo_contabilitate.nota_cu_sursa_si_status(cur, sfarsit, None, descr, "operatiuni", "ciorna", doc_vechi)[0]   # [430d]
            else:
                iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, sfarsit, descr)[0]   # [430d] sursa: nota nu vine din extrasul de cont
            for e in de_scris:   # [381] partenerul pe rândul de terți (4111 / 401), ca pe orice notă pe un cont de parteneri
                dd, cc, ss = e["linie"]
                p_cui = e["partener_cheie"] if e.get("partener_cheie") and not e["partener_cheie"].startswith("~") else None
                repo_contabilitate.adauga_linie_partener(cur, schema, iid, dd, cc, ss, p_cui,
                                                         e["partener"] if e.get("partener_cheie") else None)
            _rv.consemneaza(cur, schema, iid, sfarsit, prop["elemente"])
        conn.commit()
    return _uc_comun.cu_eticheta(schema, dict(_rv.totaluri(prop["elemente"]), inregistrare_id=iid, elemente=len(de_scris),
                                              inlocuita=bool(inlocuite)))
