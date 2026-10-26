# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/declaratii`.

[P7 · valul use-case, 13.09.2026] Corpurile astea stateau in `main.py`, adica in stratul HTTP, si
isi deschideau singure tranzactia. Textul canonic (`PLAN_HARDENING.md:840`) spune ca use-case-ul e
cel care **detine tranzactia si orchestreaza**; aici e mutarea, nu o rescriere.

CE S-A PASTRAT, literă cu literă: corpul, cu tot cu blocurile `with db.get_conn()`, in aceeasi
ordine, cu aceleasi efecte. CE S-A TRADUS: `HTTPException(cod, mesaj)` a devenit
`_erori.<Clasa>(mesaj)` — acelasi mesaj, iar codul se pune la loc in stratul HTTP, dintr-o singura
harta. Se poate face fiindca `HTTPException` **nu e prinsa nicaieri** in aplicatie.

CE A RAMAS IN `main.py`: semnatura rutei (FastAPI valideaza pe ea), docstringul ei, si o linie care
cheama functia de aici prin adaptorul `_http`.
"""

from core import db, auth_api, declaratii_api, control_fiscal_api, declaratii_componente, repo_declaratii, d207
from core import repo_firma_profil
from core.common import azi_ro
from core.mesaje import FARA_ACCES_TENANT
from core import erori as _erori
from core import uc_comun as _uc_comun


def declaratii_tipuri(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/declaratii/tipuri`; docstringul ei a ramas in stratul HTTP."""
    if tenant_id is None:
        raise _erori.CerereGresita("Alege firma întâi.")
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            row = repo_firma_profil.profil_fiscal(cur)
            antet = repo_declaratii.antet_firma(cur)   # [lotul 13, 636 / 594] precompletarea formularelor manuale din Date firmă
            monede = repo_declaratii.monede_bnr(cur)   # [lotul 13, 636] moneda D318 din lista BNR
        _vec = ({"tip_firma": row[0], "tip_decont": row[1], "platitor_tva": row[2],
                 "operatiuni_ic": row[3], "regim_fiscal": row[4],   # [R94] regimul intra in vector
                 "inreg_art317": antet["inreg_art317"]}            # [lotul 13, 595] D398 cere codul art.316 / art.317
                if row else {})
        # [21.08.2026] FAPTUL BATE VECTORUL: selectorul nu mai blocheaza D390/D301 pe bifa cand exista
        # operatiuni IC reale (sau cand evidenta e incompleta). Tiparul tenant_006. Sonda se cheama
        # INAINTE de inchiderea conexiunii - inainte era calculata dupa `with`, ceea ce n-ar fi mers.
        _neap = control_fiscal_api.neaplicabile_selector(
            _vec, ic_fapt=(lambda: control_fiscal_api.ic_fapt_din_db(conn, schema, azi_ro().year)))
        # [lotul 13, 650 / 595 / 635] regimul de TVA: D311 (plătitor), D398 (fără cod 316 / 317), D318 (neînregistrat) — aceeași poartă ca la
        # generare (`declaratii_api.genereaza`)
        _neap = {**declaratii_api.neaplicabile_regim(_vec), **_neap}
    # [deficiența 301] declarațiile pe care forma firmei nu le poate datora nici nu apar (persoanele fizice, la o persoană juridică)
    _forma = control_fiscal_api.neaplicabile_forma(row[0] if row else None)
    _tipuri = [t for t in declaratii_api.tipuri() if t not in control_fiscal_api._NEAP_PERSOANA_JURIDICA or t not in _forma]
    return {"tipuri": _tipuri,
            "periodicitate": {t: declaratii_api.periodicitate_firma(t, _vec if row else None) for t in _tipuri},
            "periodicitate_eticheta": {t: e for t, e in declaratii_api.ETICHETA_PERIODICITATE.items() if t in _tipuri},
            "neaplicabile": _neap,
            "datorate": _datorate_firmei(tenant_id, ctx),
            # [comanda Costin 9.1, A.3] obligațiile pe care le corectează formularul D710, cu denumirea oficială din nomenclator
            "obligatii_d710": _obligatii_d710(),
            # [lotul 13, 636 / 594] Date firmă pentru formularele manuale (D318, D398 …): ecranul le pune în câmpuri, vizibile și modificabile
            "firma": {k: v for k, v in antet.items() if k not in ("platitor_tva", "inreg_art317")},
            # [lotul 13, 653] statele de rezidență acceptate de validatorul D207 (lista cu căutare a formularului)
            "nomenclatoare": {"d207_stat_r": sorted(d207.STAT_R), "monede_bnr": ["RON"] + [m for m in monede if m != "RON"]}}


def aduce_localitati_parteneri(schema, tip):
    """[lotul 10, deficiența C69, decizia Costin 20.10.2026 „Completez din ANAF”, verbatim în DECIZII] „pentru partenerii cu CUI
    românesc, localitatea se aduce automat din ANAF la generare; se blochează numai ce rămâne necompletat.” Înaintea tranzacției de
    generare (ca `uc_reevaluare._aduce_cursurile`): o citire scurtă a partenerilor fără localitate scrisă (`d406.cuiuri_de_cerut_anaf`),
    apoi ANAF cu pool-ul liber (`anaf_api.aduce_localitati`, cache în proces). D406 (localitatea, S.AD.5 City) și D394 (județul
    partenerului neînregistrat, judP) citesc apoi numai cache-ul. ANAF jos nu oprește aici: generatorul numește partenerii rămași."""
    if tip not in ("d406", "d394"):
        return
    import psycopg2.extras as _E
    from core import anaf_api as _anaf, d406 as _d406, repo_d406 as _repo_d406
    with db.get_conn(schema) as conn, conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cuiuri = _d406.cuiuri_de_cerut_anaf(_repo_d406.parteneri_si_localitati(cur))
    try:
        _anaf.aduce_localitati(cuiuri)
    except Exception as e:   # noqa: BLE001 — ANAF indisponibil: refuzul generatorului numește partenerii fără localitate
        from core import observare as _obs
        _obs.esec_secundar("localitatea partenerilor din ANAF (%s)" % tip, e)


def _obligatii_d710():
    """[{cod, denumire}] — codurile pe care D710 le acceptă (`d710` le ia din `d100.COD_BUGETAR`), cu denumirea din
    `core.nomenclator_obligatii` (OPANAF 587/2016, anexa nr. 3). Ecranul nu mai ține o listă scrisă de mână."""
    from core import d100 as _d100, nomenclator_obligatii as _nom
    return [{"cod": c, "denumire": _nom.denumire("d710", c)} for c in sorted(_d100.COD_BUGETAR, key=int)]


def _datorate_firmei(tenant_id, ctx):
    """[deficiența 283] Ce datorează firma, din vectorul fiscal, cu termenul — din MOTORUL UNIC al termenelor (același calcul ca ecranul
    „Termene” și semaforul: `firma_rezumat._termene_una_firma` -> `termene_api.termene_firma` -> `control_fiscal_api.obligatii_datorate`;
    nedepusele cu termenul în următoarele 60 de zile). Firma neevaluabilă (vector necompletat) -> listă goală; ecranul arată toate
    declarațiile, ca înainte. [{tip, an, luna, perioada, termen}]."""
    from core import firma_rezumat as _fr
    try:
        ev, _ne = _fr._termene_una_firma({"id": tenant_id}, ctx, azi_ro())
    except Exception as _e:  # noqa: BLE001 — lista ajutătoare nu oprește selectorul; nu e tăcut
        from core import observare as _obs
        _obs.esec_secundar("datoratele firmei in selectorul de declaratii", _e)
        return []
    return sorted((ev or {}).get("termene") or [], key=lambda d: (d["termen"], d["tip"]))


def poarta_cererii(conn, schema, tip, body, xml, res):
    """Porțile care țin de CERERE, nu de calcul, chemate după dispecer (`declaratii_api.genereaza`) pe fiecare drum al generării cerute de om:
    pasul 2 al Declarațiilor (`declaratie_valideaza`), generarea (`declaratie_genereaza`) și intrarea în coadă (`uc_coada.coada_adauga`, care
    servește și „Generează din nou” și reluarea declarației care aștepta validarea notelor). Scripturile de citire (cifrele de referință,
    amprentele) cheamă dispecerul fără ea: nu produc ceva de depus.
    [lotul 12, C19, comanda Costin 12.3 pct.6, verbatim în DECIZII] „rectificativa D394 pentru o perioadă deja depusă se generează doar la
    cererea contabilului, cu diferențele față de cea depusă arătate înainte; niciodată automat.” [lotul 13, C19: și D112] ->
    `rectificativa.poarta_diferente` (declarațiile din `rectificativa.CU_DIFERENTE`): peste o
    depunere, declarația iese numai cu confirmarea contabilului pentru exact conținutul văzut ca diferențe; fără diferențe, nu iese deloc.
    Garda: `core/test_lot12_decl3_c19.py` (orice funcție a use-case-urilor care cheamă dispecerul cheamă și poarta)."""
    # [lotul 13, 656 + comanda 13.1 pct.5] verificarea proprie a cifrelor (impozit ≤ bază, cota legii), înaintea validatorului ANAF
    from core import verificare_bun_simt as _vbs
    _vbs.poarta(tip, body, res, conn)
    from core import rectificativa as _rect
    if tip in _rect.CU_DIFERENTE:   # [lotul 12 / 13, C19] D394, D112: rectificativa numai la cerere, după diferențe
        _rect.poarta_diferente(conn, schema, tip, body, xml, res)


def declaratie_valideaza(tip, date, ctx):
    """[P7 · use-case] Corpul rutei `/declaratii/{tip}/valideaza`; docstringul ei a ramas in stratul HTTP."""
    import base64 as _b64
    from core import duk as _duk
    body = date.model_dump(exclude_none=True)
    tenant_id = body.pop("tenant_id")
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise _erori.Inexistent(FARA_ACCES_TENANT)
    aduce_localitati_parteneri(schema, tip)   # [lotul 10, C69] ANAF înaintea tranzacției de generare
    try:
        with db.get_conn(schema) as conn:
            xml, res = declaratii_api.genereaza(conn, schema, tip, body)
            poarta_cererii(conn, schema, tip, body, xml, res)   # [lotul 12, C19] rectificativa D394 numai confirmată
            blocaj = blocaj_depunere(conn, schema, tip, body)
    except ValueError as e:   # [lotul 10, 431] refuzul cu trimitere (`RefuzGenerare`) ajunge la ecran ca obiect, celelalte ca text
        raise _erori.DateInvalide(e.detaliu() if isinstance(e, _erori.RefuzGenerare) else str(e))
    # an/luna OBLIGATORII pentru D406 (27.07.2026): SAF-T se valideaza cu
    # DUKIntegrator_AnLunaUI.jar, care le primeste ca parametri; fara ele
    # _valideaza_saft intoarce GRI intotdeauna - deci validarea D406 din aplicatie
    # nu s-a facut NICIODATA, desi calea merge (dovedit manual pe tenant_002/iunie
    # 2026: "Validare fara erori"). Celelalte declaratii le ignora (optionale).
    #
    # [R166, 05.09.2026] ...si tot nu se facea: perioada se citea din CORPUL cererii, dar
    # D406 se cere pe `trim` (cu `luna` generatorul da 422), iar conversia trim->luna-ancora
    # se petrece INAUNTRUL lui `declaratii_api` si nu ajunge inapoi in `body`. Rezultat: nu
    # exista niciun corp care sa treaca amandoua portile - forma care genereaza nu valideaza,
    # forma care ar valida nu genereaza. Se ia perioada de pe REZULTATUL generatorului, adica
    # cea folosita efectiv, cu corpul ca rezerva; o a doua conversie trim->luna aici ar fi
    # inceputul aceleiasi divergente tacute pe care a reparat-o R165.
    _an = getattr(res, "an", None) or body.get("an")
    _luna = getattr(res, "luna", None) or body.get("luna")
    rez = _duk.valideaza(xml, tip, an=_an, luna=_luna)  # java blocant
    return {"tip": tip, "stare": rez["stare"], "erori": rez["erori"],
            "severitate": rez.get("severitate"),  # [A2] E:(eroare) vs A:(atentionare) - frontendul il citeste
            "temei": rez["temei"], "limita": rez["limita"],
            **campuri_rezultat(tip, res), "blocaj_depunere": blocaj,
            "xml_b64": _b64.b64encode(xml.encode()).decode()}


def blocaj_depunere(conn, schema, tip, body):
    """[lotul 10, deficiența 436, comanda Costin 10.2 pct.6, verbatim în DECIZII] „când declarația știe că are cifra greșită din note
    nevalidate, depunerea se blochează până la validare, cu motivul lângă buton, la toate declarațiile.” Refuzul pe care pasul 2 îl arată
    lângă „Trimite în coadă” (butonul inactiv) — același ca la intrarea în coadă (`uc_coada.coada_adauga`) și la depunere
    (`coada_api.refuz_note_nevalidate`): `coada_api.blocaj_declaratie` pe perioada CERERII. {cod, mesaj, note} | None."""
    from core import coada_api as _coada
    with conn.cursor() as cur:
        return _coada.blocaj_declaratie(cur, schema, tip, body.get("an"), body.get("luna"), body.get("trim"))


def campuri_rezultat(tip, res):
    """Ce spune rezultatul motorului despre declarație — O SINGURĂ asamblare pentru validare și pentru generare.
    [retest 08.10 pct.16] „D406: caseta «Rezumat» nu se vede”: `sinteza` (V5) intrase numai în răspunsul generării, iar
    ecranul cheamă validarea. Două asamblări ale aceluiași răspuns se despart la primul câmp nou; una nu are cu cine."""
    return {
        "avertismente": getattr(res, "avertismente", None),
        "note_rezultat": getattr(res, "note_rezultat", None) or [],   # canal neutru (fapte despre rezultat); [] pt declaratiile fara canal
        "sinteza": getattr(res, "sinteza", None) or [],               # [08.10, V5] rezumatul, pe canalul lui (nu avertisment)
        "rectificativa": getattr(res, "rectificativa", None),   # [lotul 11, C77] „Rectificativă la declarația depusă …”
        # [poarta_gol_v1 27.07.2026] cate operatiuni are declaratia; None = nu se poate
        # numara (d101/d112). Ecranul pune o poarta la 0, ca declaratia goala legitima
        # sa nu mai arate identic cu cea golita de un query rupt.
        "operatiuni": declaratii_api.numar_operatiuni(tip, res),
        # [lista 5, 30.08.2026] DIN CE e facuta cifra, nu doar CATE. Pana azi ruta intorcea un
        # contor - „valid, 18 operatiuni" - iar contabilul nu putea vedea CARE 18: 0 din 92 de
        # iesiri isi aratau componentele (1c). Componentele existau pe obiectul de rezultat al
        # motorului; lipsea transportul. Ce nu se poate desface spune de ce, nu tace.
        "componente": declaratii_componente.componente(tip, res)}


def declaratie_genereaza(tip, date, ctx):
    """[P7 · use-case] Corpul rutei `/declaratii/{tip}`; docstringul ei a ramas in stratul HTTP."""
    body = date.model_dump(exclude_none=True)
    tenant_id = body.pop("tenant_id")
    # 1) pe public: aflu schema tenantului + verific accesul userului
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise _erori.Inexistent(FARA_ACCES_TENANT)
    # 2) pe schema tenantului (SET LOCAL search_path în get_conn, PgBouncer-safe):
    #    modulul rulează pe conexiunea deja poziționată, NU mai setează el search_path
    aduce_localitati_parteneri(schema, tip)   # [lotul 10, C69] ANAF înaintea tranzacției de generare
    try:
        with db.get_conn(schema) as conn:
            xml, res = declaratii_api.genereaza(conn, schema, tip, body)
            poarta_cererii(conn, schema, tip, body, xml, res)   # [lotul 12, C19] rectificativa D394 numai confirmată
            blocaj = blocaj_depunere(conn, schema, tip, body)
    except ValueError as e:   # [lotul 10, 431] refuzul cu trimitere (`RefuzGenerare`) ajunge la ecran ca obiect, celelalte ca text
        raise _erori.DateInvalide(e.detaliu() if isinstance(e, _erori.RefuzGenerare) else str(e))
    return {"tip": tip, "xml": xml, **campuri_rezultat(tip, res), "blocaj_depunere": blocaj}
