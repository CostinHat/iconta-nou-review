# -*- coding: utf-8 -*-
"""USE_CASE — reevaluarea lunară a elementelor monetare în valută, propusă de aplicație (lotul 10, deficiența 429).

Comanda Costin 20.10.2026 (10.1 pct.8, verbatim în DECIZII „Comanda 10.1”): „La închiderea lunii, aplicația propune singură creanțele
și datoriile în valută neîncasate (pe factură), disponibilitățile în valută, cursul din evidență, cursul BNR din ultima zi bancară și
diferența pe 665/765; contabilul verifică și generează nota.”

Temeiul și regulile propunerii: `core/reevaluare_valuta.py` (OMFP 1802/2014 pct.325). Aici: tranzacția, drepturile, perioada,
cursul BNR adus ÎNAINTEA tranzacției (`uc_curs_bnr.asigura_cursul`, ca `uc_comun._preincalzeste_cursul`) și nota (ciornă — R36:
nimic nu se scrie `validata` direct; a doua generare înlocuiește ciorna nevalidată a lunii, cu același document intern).
Formularul manual din Operațiuni (`uc_tenants.reevaluare_valuta`) rămâne pentru cazurile speciale.
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
    pct.325 alin.(2) lit.b), deci se cere BNR-ului. O zi de sărbătoare legală cade în același caz și se recere — declarat. Tăcută la
    eșec, ca `_preincalzeste_cursul`: refuzul vine din propunere (cursul lipsă se arată pe element)."""
    from core import uc_curs_bnr as _uc_cb
    with db.get_conn(schema) as conn, conn.cursor() as cur:
        monede = {r["moneda"] for r in _rv.reevaluari(cur, schema, sfarsit)}
        monede |= {f["moneda"] for f in _rv.facturi_in_valuta(cur, schema, sfarsit)}
    monede |= {str(m).strip().upper() for m in monede_in_plus if m}
    prag = (sfarsit - _ultima_zi_lucratoare(sfarsit)).days
    for m in sorted(x for x in monede if x and x != "RON"):
        try:
            _uc_cb.asigura_cursul(m, sfarsit, prag_zile=prag)
        except Exception:      # noqa: BLE001 — pre-încălzirea nu poate strica o cerere (ca `_preincalzeste_cursul`)
            pass


def _monede_din(completari):
    return [c.get("moneda") for c in (completari or {}).values() if isinstance(c, dict)]


def _completari(text):
    """Completările de pe ecran, trimise la recalculare ca JSON în cerere: {cheie: {sold_valuta?, moneda?}}."""
    import json
    if not text:
        return {}
    try:
        c = json.loads(text)
    except ValueError:
        c = None
    if not isinstance(c, dict) or not all(isinstance(v, dict) for v in c.values()):
        raise _erori.DateInvalide("Completările trebuie trimise pe element (cheia elementului din propunere).")   # FORMĂ: forma cererii
    return c


def reevaluare_valuta_propunere(tenant_id, an, luna, ctx, completari=None):
    """Propunerea lunii: elementele în valută cu soldul, cursul din evidență, cursul BNR (cu data lui) și diferența pe 665 / 765.
    `completari` (JSON): ce a scris contabilul pe ecran — propunerea se recalculează cu ele, fără să scrie nimic."""
    _uc_comun._cere_perioada(an, luna)
    comp = _completari(completari)
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    sfarsit = _sfarsit(an, luna)
    _aduce_cursurile(schema, sfarsit, _monede_din(comp))
    with db.get_conn(schema) as conn, conn.cursor() as cur:
        try:
            prop = _rv.propunere(cur, schema, an, luna, completari=comp)
        except ValueError as e:
            raise _erori.DateInvalide(str(e))   # FORMĂ: completarea respinsă de `reevaluare_valuta._aplica` (mesajul ei, numit acolo)
    from core import inchidere_luna as _il
    prop["luna_in_curs"] = _il.luna_in_curs(an, luna)
    return _public(prop)


def _public(prop):
    """Linia notei (tuplu cu Decimal) nu pleacă pe fir; ecranul are contul și diferența."""
    for e in prop["elemente"]:
        e.pop("linie", None)
    return prop


def reevaluare_valuta_genereaza(tenant_id, corp, ctx):
    """Generează nota lunii din propunere (ciornă), cu completările contabilului: corp {an, luna, completari: {cheie: {sold_valuta?,
    moneda?}}}. Întoarce nota (eticheta ei), totalurile și câte elemente s-au reevaluat."""
    try:
        an, luna = int(corp["an"]), int(corp["luna"])
    except (KeyError, TypeError, ValueError) as e:
        raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e) if isinstance(e, KeyError) else "Luna sau anul nu sunt numere.")   # FORMĂ
    completari = corp.get("completari") or {}
    if not isinstance(completari, dict):
        raise _erori.DateInvalide("Completările trebuie trimise pe element (cheia elementului din propunere).")   # FORMĂ: forma cererii
    _uc_comun._cere_perioada(an, luna)
    _uc_comun._cere_luna_incheiata(an, luna, "Reevaluarea în valută a lunii")
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    sfarsit = _sfarsit(an, luna)
    _aduce_cursurile(schema, sfarsit, _monede_din(completari))
    from core import note_derivate as _nd
    from core.pdf_util import data_ro
    with db.get_conn() as conn:
        _uc_comun._cere_luna_deschisa(conn, schema, sfarsit)
        with conn.cursor() as cur:
            try:
                prop = _rv.propunere(cur, schema, an, luna, completari=completari)
            except ValueError as e:
                raise _erori.DateInvalide(str(e))   # FORMĂ: completarea respinsă de `reevaluare_valuta._aplica` (mesajul ei)
            lipsa = [e for e in prop["elemente"] if e["de_completat"]]
            if lipsa:   # FORMĂ: un câmp lipsă (soldul în valută / moneda), pe care aplicația nu-l ghicește (DS cap.17)
                raise _erori.DateInvalide("Înainte de a genera nota, completează %s: %s." % (
                    "soldul în valută" if all(e["de_completat"] == ["sold_valuta"] for e in lipsa) else "soldul în valută și moneda",
                    ", ".join("contul %s" % e["cont"] for e in lipsa)))
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
            for e in de_scris:
                dd, cc, ss = e["linie"]
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
            _rv.consemneaza(cur, schema, iid, sfarsit, prop["elemente"])
        conn.commit()
    return _uc_comun.cu_eticheta(schema, dict(_rv.totaluri(prop["elemente"]), inregistrare_id=iid, elemente=len(de_scris),
                                              inlocuita=bool(inlocuite)))
