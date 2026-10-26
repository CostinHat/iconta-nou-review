# -*- coding: utf-8 -*-
"""core/uc_factura_primita.py — USE-CASE: VALIDAREA facturii primite, oricum a intrat — din XML-ul e-Factura (SPV / „Importă XML UBL”)
sau introdusă de mână de pe o factură pe hârtie / PDF (lotul 12, deficiența 477).

Comanda Costin 12.1 pct.8 (verbatim în DECIZII „Comanda 12.1”): „Fără funcții noi în afara celor cerute aici (461 lista de parteneri și 477
introducerea manuală a facturilor primite sunt cerute).” 477 (grav): „Facturi primite — Lipsește introducerea manuală a facturilor
primite”: furnizorul (CUI verificat la ANAF), seria / numărul, data, scadența, liniile cu cotele de TVA (din registrul de parametri fiscali),
moneda și cursul BNR, contul de cheltuială / stoc — și documentul trece prin ACEEAȘI contare și ACEEAȘI validare ca factura din XML.

UN SINGUR DRUM (`valideaza`): factura citită (dict-ul lui `efactura_import.parseaza_xml`, sau cel construit din formular de
`factura_din_formular`, cu aceleași chei) intră în evidență prin `uc_tenants._factura_importata` (facturi + linii + TVA pe cote + cursul),
apoi primește clasificarea aleasă la validare (tipul furnizorului pentru D394, TVA la încasare, țara, destinația TVA și contul fiecărei
linii), nota contabilă (`contare_facturi.contabilizeaza`, cu alegerea NIR-ului „fără factură”) și, pe un cont de stoc, intrarea în gestiune
(`stocuri_cv_api.intrare_din_factura`) — în aceeași tranzacție. Diferența factură din XML / factură de mână stă NUMAI în citire.

TEMEI. Statutul furnizorului la data facturii: HG 1/2016 titlul VII pct.67 alin.(6) (`anaf_api.statut_furnizori`). Cursul facturii în
valută: CF art.290 alin.(2) „cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a României [...]
valabil la data la care intervine exigibilitatea taxei pentru operațiunea în cauză”; HG 1/2016 pct.35 alin.(1) „prin ultimul curs de
schimb comunicat de Banca Națională a României se înțelege cursul de schimb comunicat de respectiva bancă în ziua anterioară și care este
valabil pentru operațiunile care se vor desfășura în ziua următoare.” (`contare_facturi.curs_factura_importate` -> `facturi_api.curs_automat`).
Decizia Costin „cursul vechi la validare (a)”: când cursul zilei lipsește și se folosește unul mai vechi, contabilul primește anunțul, ca la
emitere (`curs_bnr.cursul_zilei_lipsa`, act „validare”). Cotele de TVA: registrul de parametri fiscali (`common.cote_tva_in_vigoare`), la
data facturii. TVA-ul facturii de mână: regula unică a documentului (`tva_calcul.totaluri`, BR-CO-17: baza pe cotă × cotă, rotunjit o
dată pe cotă).
"""
import datetime as _dt
from decimal import Decimal, InvalidOperation

from core import auth_api, db
from core import chei_unice as _chei
from core import erori as _erori
from core import facturi as _fc
from core import uc_comun as _uc_comun
from core.pdf_util import data_ro as _data_ro   # data pentru om, sursa unică (DS cap.4)

#: id-urile câmpurilor formularului „Introdu factura primită” (refuzurile lângă câmp, DS cap.6, `erori.ErorileFormularului`)
CAMP = {"tert_nume": "pm-furnizor", "tert_cui": "pm-cui", "tert_tara": "pm-tara", "serie": "pm-serie", "numar": "pm-numar",
        "data_emitere": "pm-data", "data_scadenta": "pm-scadenta", "moneda": "pm-moneda", "cont": "pr-cont"}
#: câmpul unei linii: `pm-l<i>-<cheie>` (i de la 1, ca pe ecran)
CAMP_LINIE = {"descriere": "descriere", "cantitate": "cantitate", "um": "um", "pret_unitar": "pret", "cota_tva": "cota"}

#: [477] refuzul tipului furnizorului la factura de mână: același cod și același câmp ca la factura din XML (`uc_tenants.REFUZ_TERT_PLATITOR`),
#: cu motivul ei (nu „din XML”) și cu câmpul numit, ca ecranul să arate alegerea lângă el
_MESAJ_PLATITOR = ("Spune dacă furnizorul e înregistrat în scopuri de TVA: ANAF nu a răspuns pentru data facturii (sau furnizorul nu e din "
                   "România), iar D394 îl declară după tipul lui.")
REFUZ_TERT_PLATITOR_MANUALA = {"cod": "TERT_PLATITOR_DE_COMPLETAT", "camp": "pr-platitor", "mesaj": _MESAJ_PLATITOR,
                               "erori_campuri": [{"camp": "pr-platitor", "mesaj": _MESAJ_PLATITOR}]}

def camp_linie(i, cheie):
    return "pm-l%d-%s" % (i, CAMP_LINIE[cheie])


def _numar(x):
    try:
        v = Decimal(str(x).replace(",", ".").strip())
    except (InvalidOperation, ValueError, TypeError):
        return None
    return v if v.is_finite() else None


def _data(x):
    try:
        return _dt.date.fromisoformat(str(x or "").strip()[:10])
    except ValueError:
        return None


def factura_din_formular(corp):
    """PUR. Factura primită introdusă de mână -> dict-ul facturii, în forma lui `efactura_import.parseaza_xml` (aceleași chei, ca drumul să
    fie același), sau refuzul cu TOATE câmpurile greșite deodată (`erori.ErorileFormularului`, DS cap.6). Nu scrie nimic, nu cheamă ANAF.

    Ce se cere: furnizorul (numele, codul — cu cifra de control verificată la un furnizor din România —, țara), numărul (seria opțională),
    data facturii, scadența (opțională, nu înaintea datei), moneda, liniile (denumirea, cantitatea, unitatea de măsură — C104 —, prețul
    unitar fără TVA, cota de TVA în
    vigoare la data facturii) și contul facturii (cheltuială, sau 371 / 301–303 la marfă și materiale)."""
    from core import identitate as _id, tva_calcul as _tc
    from core.common import cote_tva_in_vigoare
    corp = corp or {}
    er = _erori.ErorileFormularului("Factura primită nu s-a salvat")
    txt = lambda k: str(corp.get(k) or "").strip()   # noqa: E731
    nume, cui, tara = txt("tert_nume"), txt("tert_cui").replace(" ", "").upper(), txt("tert_tara").upper()
    if not nume:
        er.camp(CAMP["tert_nume"], "Scrie numele furnizorului, cum e pe factură.")
    if not (len(tara) == 2 and tara.isalpha()):
        er.camp(CAMP["tert_tara"], "Scrie țara furnizorului: codul ISO din două litere (RO, DE, …).")
    if not cui:
        er.camp(CAMP["tert_cui"], "Scrie codul fiscal al furnizorului (CUI-ul, sau codul de TVA la un furnizor din altă țară).")
    elif tara == "RO":
        ok, motiv = _id.valideaza_cui(cui)
        if not ok:
            er.camp(CAMP["tert_cui"], "CUI-ul %s nu e valid (%s) — verifică-l pe factură." % (cui, motiv))
    numar, serie = txt("numar"), txt("serie")
    if not numar:
        er.camp(CAMP["numar"], "Scrie numărul facturii.")
    zi = _data(corp.get("data_emitere"))
    if zi is None:
        er.camp(CAMP["data_emitere"], "Alege data facturii.")
    scad = None
    if txt("data_scadenta"):
        scad = _data(corp.get("data_scadenta"))
        if scad is None:
            er.camp(CAMP["data_scadenta"], "Scadența nu e o dată din calendar.")
        elif zi is not None and scad < zi:
            er.camp(CAMP["data_scadenta"], "Scadența (%s) e înaintea datei facturii." % _data_ro(scad))
    moneda = txt("moneda").upper()
    if not (len(moneda) == 3 and moneda.isalpha()):
        er.camp(CAMP["moneda"], "Alege moneda facturii.")
    if not txt("cont"):
        er.camp(CAMP["cont"], "Scrie contul facturii: cheltuiala (ex. 628), sau 371 / 301–303 la marfă și materiale.")
    permise = None
    if zi is not None:
        permise, _t = cote_tva_in_vigoare(zi)
    linii = []
    brute = corp.get("linii") or []
    if not brute:
        er.fara_camp("Adaugă cel puțin o linie: ce scrie pe factură (denumirea, cantitatea, prețul fără TVA, cota).")
    for i, l in enumerate(brute, 1):
        l = l or {}
        den = str(l.get("descriere") or "").strip()
        cant, pret, cota = _numar(l.get("cantitate")), _numar(l.get("pret_unitar")), _numar(l.get("cota_tva"))
        if not den:
            er.camp(camp_linie(i, "descriere"), "Linia %d: scrie denumirea, cum e pe factură." % i)
        if cant is None or cant == 0:
            er.camp(camp_linie(i, "cantitate"), "Linia %d: scrie cantitatea (diferită de 0)." % i)
        um = _fc.um_linie(l) or ""   # [lotul 13, regula UM — o singură regulă cu emiterea și borderoul: gol nu devine „buc”]
        if not um:
            er.camp(camp_linie(i, "um"), _fc.MESAJ_UM_LIPSA)
        elif len(um) > 10:
            er.camp(camp_linie(i, "um"), "Linia %d: unitatea de măsură are cel mult 10 caractere." % i)
        if pret is None or pret < 0:
            er.camp(camp_linie(i, "pret_unitar"), "Linia %d: scrie prețul unitar fără TVA." % i)
        if cota is None:
            er.camp(camp_linie(i, "cota_tva"), "Linia %d: alege cota de TVA de pe factură." % i)
        elif permise is not None and cota not in {Decimal(str(c)) for c in permise}:
            er.camp(camp_linie(i, "cota_tva"), "Linia %d: cota %s%% nu era în vigoare la %s (cotele de atunci: %s)." % (
                i, cota.normalize(), _data_ro(zi), ", ".join("%s%%" % Decimal(str(c)).normalize() for c in sorted(permise))))
        linii.append({"descriere": den[:255], "cantitate": cant, "um": um or None, "pret_unitar": pret, "cota_tva": cota,
                      "categorie_tva": None, "valoare_neta": None})
    er.refuza()
    t = _tc.totaluri(linii)
    return {"numar": numar, "serie": serie or None, "data_emitere": zi.isoformat(), "data_scadenta": scad.isoformat() if scad else None,
            "furnizor_cod_tva": None, "directie": "primita", "tert_nume": nume, "tert_cui": cui, "tert_tara": tara,
            "total": t["total"], "tva": t["tva"], "moneda": moneda,
            "tva_cote": [], "tva_lei_xml": None, "taxare_inversa": False, "linii": linii, "xml": None, "manuala": True}


def statut_furnizor(f):
    """Statutul furnizorului la data facturii (ANAF: înregistrat în scopuri de TVA, TVA la încasare — `anaf_api.statut_furnizori`), cu
    conexiunea închisă (un apel ANAF nu ține o conexiune din pool). Furnizorul din altă țară nu e în registrele ANAF: rămâne necunoscut
    (None), iar contabilul îl spune."""
    if not (f.get("data_emitere") and f.get("tert_cui")) or (f.get("tert_tara") or "RO") != "RO":
        return {"platitor_tva": None, "tva_la_incasare": None}
    from core import anaf_api as _anaf
    c, d = f["tert_cui"], str(f["data_emitere"])
    return _anaf.statut_furnizori([(c, d, f.get("furnizor_cod_tva"))])[(c, d)]


def cont_facturii(conn, schema, corp, primita_id=None):
    """Contul facturii primite (cheltuiala, sau 371 / 301–303 la marfă și materiale), curățat și DIN PLANUL FIRMEI
    (`cont_valid.cere_cont`; decizia Costin 26.08.2026: „o intrare din afara unui nomenclator de registru se REFUZA”). Lipsă -> refuzul
    [FFF1] (contul obligatoriu, decizia Costin 29.08.2026); un cont care nu e în plan -> refuzul lângă câmp, cu contul și locul unde se
    creează. Nu scrie nimic: ruta din XML îl cheamă înaintea citirii XML-ului, `valideaza` înaintea oricărei scrieri."""
    from core import afirmatii as _af
    from core import cont_valid as _cv
    try:
        return _cv.cere_cont(conn, schema, corp.get("cont"), "Contul facturii")
    except _cv.ContNecunoscut as e:
        if e.detalii["fel"] == "lipsa":
            # [FFF1] CONTUL DE CHELTUIALĂ E OBLIGATORIU (decizia Costin 29.08.2026): nici cont implicit, nici validare fără notă
            raise _erori.DateInvalide(dict(_af.afirmatie(
                "neconformitate", "CONT_CHELTUIALA_OBLIGATORIU",
                "Alege contul de cheltuială înainte de a valida: validarea recunoaște "
                "cheltuiala și îi scrie nota contabilă în același act, iar nota nu poate "
                "ghici contul.",
                unde="factura primită #%s" % primita_id if primita_id else "factura primită introdusă de mână",
                regula="validarea unei facturi primite cere contul de cheltuială"),
                cod="CONT_CHELTUIALA_OBLIGATORIU"))
        er = _erori.ErorileFormularului("Factura primită nu s-a validat")
        er.camp(CAMP["cont"], _cv.randeaza(e.detalii))
        er.refuza()


def valideaza(conn, schema, f, corp, statut, primita_id=None):
    """Actul de VALIDARE al facturii primite citite (`f`, forma lui `parseaza_xml`), în tranzacția lui `conn` (aici se comite):
    intrarea în evidență, clasificarea aleasă, nota contabilă și, pe un cont de stoc, intrarea în gestiune. `primita_id` = rândul din
    `efactura_primite` (factura din XML); None = factura introdusă de mână (`f["manuala"]`). Aceeași factură de furnizor deja în evidență
    (furnizor + număr, `factura_primita_dublura`, lotul 12 C73.1) se refuză pe ambele drumuri; cursul BNR se pune pe factură aici (la XML îl pune `_factura_importata`). Întoarce {stare, factura_id, contare, stoc,
    curs_zilei_lipsa}."""
    from core import afirmatii as _af
    from core import contare_facturi as _cf
    from core import d394 as _d394
    from core import repo_efactura, repo_facturi
    from core import uc_tenants as _uct
    cont = cont_facturii(conn, schema, corp, primita_id)   # [FFF1] obligatoriu, și din planul firmei
    from core import centre_cost_api as _cc
    with conn.cursor() as cur:
        # [lotul 13, 536] centrul de cost al fiecărei linii (gol = fără centru): un centru activ al firmei, refuzat lângă linia lui, nimic scris
        _centre = list(corp.get("centre") or [])
        _rele = _cc.campuri_centru_gresit(cur, schema, _centre, (lambda i: "pm-l%d-centru" % (i + 1)) if f.get("manuala")
                                          else (lambda i: "pr-centru-l%d" % i))
        if _rele:
            er = _erori.ErorileFormularului("Factura primită nu s-a validat")
            for camp, mesaj in _rele:
                er.camp(camp, mesaj)
            er.refuza()
        # [lotul 6 pct.7c, 273] ce nu vine din factură se cere aici, înainte de orice scriere: tipul furnizorului (D394) și, la taxarea
        # inversă (linii „AE”), categoria produsului (codul D394, art.331)
        _tp = statut["platitor_tva"] if statut["platitor_tva"] is not None else corp.get("tert_platitor_tva")   # [418a] faptul, nu tastarea
        _c331 = (corp.get("categorie_331") or "").strip() or None
        if _tp is None:
            raise _erori.DateInvalide(REFUZ_TERT_PLATITOR_MANUALA if f.get("manuala") else _uct.REFUZ_TERT_PLATITOR)
        if f.get("taxare_inversa") and not (_c331 in _d394.CODPR or _c331 in _d394.CODPR_CEREALE):
            raise _erori.DateInvalide(_uct.REFUZ_CATEGORIE_331)
        try:   # leagă numai același document e-Factura (același XML); altă factură cu același furnizor + număr: refuz, nimic scris
            fid, _nou = _uct._factura_importata(cur, schema, f)
        except _chei.CheieDublata as e:
            # [lotul 12, C73.1] aceeași factură de furnizor deja în evidență (oricare ar fi data și calea pe care a intrat): refuzul numit,
            # lângă numărul facturii la factura de mână; excepția anulează tranzacția
            if f.get("manuala"):
                e.camp = CAMP["numar"]
            raise _erori.Conflict(e.detaliu())
        if f.get("manuala"):
            # [477] cursul BNR al facturii de mână în valută, pe aceeași regulă ca factura din XML (CF art.290 alin.(2), HG 1/2016 pct.35
            # alin.(1)); fără curs (BNR indisponibil, curs prea vechi) factura nu intră — refuzul spune de ce, nimic scris
            _rc = _cf.curs_factura_importate(cur, schema, {"id": fid, "moneda": f.get("moneda"), "curs_bnr": None, "xml": None,
                                                           "manuala": True, "data_emitere": f.get("data_emitere"),
                                                           "total": f.get("total"), "tva": f.get("tva")})
            if isinstance(_rc, dict) and _rc.get("ok") is False:
                er = _erori.ErorileFormularului("Factura primită nu s-a salvat")
                er.camp(CAMP["moneda"], "%s Reîncearcă peste câteva minute." % (_rc.get("mesaj") or "Cursul BNR nu e disponibil acum."))
                er.refuza()
        fid_final = repo_efactura.marcheaza_primita_validata(cur, schema, fid, cont or None, primita_id)[0] if primita_id else fid
        if fid_final:
            repo_facturi.actualizeaza_clasificarea(cur, schema, ["tert_platitor_tva=%s", "taxare_inversa=%s", "categorie_331=%s"],
                                                   [bool(_tp), bool(f.get("taxare_inversa")), _c331, fid_final])
        # [B1 D300] furnizor cu TVA la incasare (deducere amanata la plata, art.297 alin.2) / tara partenerului (achizitie IC vs import)
        _ftva = statut["tva_la_incasare"] if statut["tva_la_incasare"] is not None else corp.get("furnizor_tva_incasare")   # [418a] RTVAI
        _ttara = (corp.get("tert_tara") or "").strip().upper()
        if fid_final and (_ftva is not None or _ttara):
            _sets, _vals = [], []
            if _ftva is not None:
                _sets.append("furnizor_tva_incasare=%s"); _vals.append(bool(_ftva))
            if _ttara:
                _sets.append("tert_tara=%s"); _vals.append(_ttara)
            _vals.append(fid_final)
            repo_facturi.actualizeaza_clasificarea(cur, schema, _sets, _vals)
        # [A12b] destinatia TVA per LINIE (taxabil / scutit / mixt); doar liniile MIXTE intra in pro-rata (art.300 alin.5)
        _dest = corp.get("destinatii")
        if fid_final and _dest:
            repo_facturi.actualizeaza_destinatii_linii(cur, schema, fid_final, _dest)
        # [deficiența 418b] contul fiecărei linii (gol = contul facturii): marfa pe 371, cartea de birou pe cheltuială
        if fid_final and corp.get("conturi"):
            repo_facturi.actualizeaza_conturi_linii(cur, schema, fid_final, corp.get("conturi"))
        # [lotul 13, 536] centrul de cost al fiecărei linii, înaintea notei: contarea îl duce pe rândul de cheltuială
        if fid_final and any(_cc.centru_valoare(v) for v in _centre):
            repo_facturi.actualizeaza_centre_linii(cur, schema, fid_final, [_cc.centru_valoare(v) for v in _centre])
    # [FFF1] NOTA SE SCRIE AICI, în același act cu validarea — după ce clasificarea e pusă pe factură. [FFF2] Clasa ambiguă (furnizor la
    # încasare + firmă în regim normal) e refuzată automat, cu motivul: factura se validează oricum, nota o scrie omul.
    contare = {"stare": "neaplicabil", "afirmatie": _af.afirmatie(
        "absenta_observatie", "CONTARE_NEAPLICABILA",
        "validarea n-a legat nicio factură, deci n-are ce conta",
        surse_consultate=["efactura_primite.factura_id"])}
    if fid_final:
        from core import nir_legare as _nl
        try:
            with _cf.cursor_dict(conn) as cur2:
                contare = _cf.contabilizeaza(cur2, schema, fid_final, automat=True,
                                             cont_cheltuiala=cont or None,
                                             nir_legat=_nl.alegerea(corp.get("nir_id"), _uc_comun.bifa(corp, "alta_livrare", False)))
        except _cf.RefuzContare as e:
            if e.cod in _nl.CODURI:
                # [decizia 08.10 pct.2] alegerea NIR-ului se cere ÎNAINTE de validare: tot actul se anulează
                conn.rollback()
                raise _erori.DateInvalide(_nl.detaliu_refuz(e))
            contare = {"stare": "refuzata", "cod": e.cod, "detalii": e.detalii,
                       "afirmatie": _af.afirmatie(
                           "neconformitate", e.cod, e.mesaj,
                           unde="factura #%s" % fid_final,
                           regula="nota automată se scrie doar când toate intrările ei sunt "
                                  "cunoscute")}
    # [reconciliere factura->stoc, 21.09.2026] RECEPȚIA CANTITATIVĂ: pe un cont de STOC (al liniei sau al facturii), intrarea în fișa de
    # magazie din liniile facturii (cantitate-DOAR, idempotentă pe factura_id; OMFP 1802/2014: recepția mărfii e un act unic)
    stoc = None
    _conturi_ef = [(str(c or "").strip() or cont or "") for c in (corp.get("conturi") or [])] or [cont or ""]
    if fid_final and any(any(c.startswith(p) for p in _cf.CONTURI_FOND_EXACT) for c in _conturi_ef):
        from core import stocuri_cv_api as _cv
        stoc = _cv.intrare_din_factura(conn, schema, fid_final, cont or "", f.get("data_emitere"))
    curs_lipsa = _anunt_curs(conn, schema, fid_final)
    conn.commit()
    return {"stare": "validata", "factura_id": fid_final, "contare": contare, "stoc": stoc, "curs_zilei_lipsa": curs_lipsa}


def _anunt_curs(conn, schema, fid):
    """[decizia Costin „cursul vechi la validare (a)”] factura în valută validată cu un curs mai vechi decât ultimul comunicat înaintea
    datei ei (cursul zilei lipsește din aplicație): anunțul, ca la emitere (`curs_bnr.cursul_zilei_lipsa`, act „validare”); altfel None."""
    if not fid:
        return None
    from core import curs_bnr as _cb, repo_facturi
    with conn.cursor() as cur:
        r = repo_facturi.cursul_fixat(cur, schema, fid)
    if not r or not r["data_curs"] or (r["moneda"] or "RON").upper() == "RON":
        return None
    return _cb.cursul_zilei_lipsa(r["data_emitere"], r["data_curs"], act="validare")


def factura_primita_manuala(tenant_id, corp, ctx):
    """[lotul 12, deficiența 477] Corpul rutei `POST /tenants/{tenant_id}/facturi-primite/manual`: factura primită de pe hârtie / PDF,
    introdusă de contabil, validată pe ACELAȘI drum ca factura din XML (`valideaza`). Citirile lungi (cursul BNR, ANAF) se fac înaintea
    tranzacției, cu pool-ul liber; luna facturii trebuie să fie deschisă."""
    f = factura_din_formular(corp)
    _uc_comun._schema_sau_404(ctx, tenant_id)
    _uc_comun._preincalzeste_cursul(f["moneda"], f["data_emitere"])   # [P5 val 3] descărcarea BNR, înainte de tranzacție
    statut = statut_furnizor(f)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, f["data_emitere"])
        return valideaza(conn, schema, f, dict(corp or {}, tert_tara=f["tert_tara"]), statut)
