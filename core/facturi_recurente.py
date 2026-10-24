# -*- coding: utf-8 -*-
"""Facturi recurente: emitere lunara automata din sabloane (cron zilnic).
Regula: sablon activ, zi_emitere <= azi.day, ultima_emitere nu e in luna curenta -> emite.

[deficiența 462, lotul 12, comanda 12.1] „Facturi recurente: Șablonul ocolește verificările facturii obișnuite.” Clasa (Costin): orice
drum care creează o factură trece prin aceleași verificări. Până acum șablonul se salva după trei verificări proprii (linii, beneficiar,
zi) și ajungea la emitere abia la cron, unde un refuz rămânea în jurnalul jobului — iar câteva verificări ale drumului obișnuit
(`uc_tenants.facturi_emite`) nu existau deloc pe el. Acum:
  * la SALVARE, șablonul trece prin emiterea însăși, de probă (`_proba_emiterii`: `facturi_api.emite_factura` într-un SAVEPOINT anulat,
    la data de azi) — exact verificările unei facturi obișnuite: liniile și cota fiecăreia la dată, codul fiscal al partenerului (CF
    art.319 alin.(20)), Date firmă (forma juridică, capitalul — Legea 31/1990 art.74 alin.(3)), seria (CF art.319 alin.(20) lit.a),
    emitentul neplătitor (CF art.310 alin.(10) lit.b), metoda de stoc și marfa fără articol, categoriile de TVA ale liniilor cu 0%,
    contul de venit; refuzul se vede lângă câmp sau în caseta formularului, nu la cron;
  * pe AMBELE drumuri (salvare și cron), verificările pe care drumul obișnuit le face în afara lui `emite_factura` (`verificari_drum`):
    denumirea beneficiarului obligatorie, clientul din alt stat (de la C160: numai unde șablonul nu poate spune operațiunea) și linia cu articol de
    stoc refuzată — emiterea automată nu poate întreba „Pleacă marfa acum?”,
    iar un răspuns implicit ar alege în locul omului (decizia R57, aceeași ca la emiterea prin API, `uc_api`);
  * la cron, plătitorul de TVA al beneficiarului român se citește din ANAF înainte de emitere, ca pe drumul obișnuit
    (`uc_comun._platitor_tva_tert`).

[lotul 12, C160] „Factura recurentă către un client din UE se emitea cu țara «RO»”: șablonul n-avea țara clientului, iar emiterea lui
(proba de la salvare și cronul) chema `emite_factura` cu implicitul `tert_tara="RO"` — la neplătitorul înregistrat art.317 fără axa
„servicii” (`categorii_tva.axa_neplatitor` cere țara), deci în D390 ca livrare de bunuri (L); la plătitor, categoriile intracomunitare ale
liniilor se refuzau față de „RO”. Acum șablonul poartă țara (`facturi_recurente.tert_tara`, `core/migrare_tara_sablon_recurent.py`), aleasă
pe ecran (dedusă din codul fiscal, ca la „Emite factură”), de la salvare până la emitere: proba, cronul și plătitorul beneficiarului o
primesc pe toate. Refuzul „clientului din alt stat” rămâne numai unde șablonul nu poate spune ce trebuie (`verificari_drum`): codul fiscal
al altui stat cu țara „România” (și șabloanele vechi, fără țară) și, la plătitor, clientul din altă țară fără nicio linie cu categoria
operațiunii (ecranul șablonului nu alege cota și categoria liniei, deci factura lunară ar ieși cu TVA-ul din România).
TEMEI: CF art.325 alin.(1) lit.a și c (D390: livrările intracomunitare de bunuri și prestările art.278 alin.(2) către persoane impozabile
stabilite în alt stat membru); CF art.278 alin.(2) (locul prestării, la beneficiarul persoană impozabilă).
"""
import json
import datetime
from psycopg2.extras import RealDictCursor
from core import facturi_api

MESAJ_BENEFICIAR = "Scrie beneficiarul facturii (denumirea clientului)."
MESAJ_ARTICOL_STOC = ("Linia %d are un articol de stoc: factura lunară se emite automat și nu poate întreba dacă marfa pleacă odată cu ea "
                      "(un răspuns ales de aplicație ar descărca gestiunea fără știrea ta, sau ar lăsa stocul greșit). Emite marfa din "
                      "„Emite factură”; în șablon rămân serviciile și ce nu se descarcă din stoc.")
MESAJ_CLIENT_STRAIN = ("Codul %s e al unui client din alt stat, dar țara clientului din șablon e România: alege țara clientului. Altfel "
                       "factura lunară ar ieși ca o vânzare în România.")
#: [C160] plătitorul, clientul din altă țară, nicio linie cu categoria operațiunii (livrare intracomunitară, prestare cu locul în afara
#: României, export): pe ecranul șablonului cota și categoria liniei nu se aleg
MESAJ_STRAIN_FARA_CATEGORIE = ("Clientul e din alt stat (%s): factura lunară ar ieși cu TVA-ul din România, fiindcă în șablon nu se alege "
                               "categoria de TVA a liniei (livrare intracomunitară, prestare de servicii cu locul în afara României, "
                               "export). Factura către un client din alt stat se emite din „Emite factură”.")
MESAJ_TARA = "Țara clientului: %r nu e un cod de țară. Alege țara din listă."
PREFIX_PROBA = "Factura lunară ar fi refuzată la emitere: "
_REFUZ_EMITERE = "Factura nu s-a emis: "   # începutul refuzurilor emiterii; sub PREFIX_PROBA nu se mai spune a doua oară


def tara_sablonului(s):
    """[C160] Țara clientului din șablon (`tert_tara`, cod din două litere, majuscule); lipsă -> „RO”, ca la `facturi.tert_tara`."""
    return str(s.get("tert_tara") or "").strip().upper() or "RO"


def verificari_drum(s, platitor=None):
    """PURĂ. Verificările drumului obișnuit de emitere care NU stau în `facturi_api.emite_factura` (le face ruta `facturi/emite`,
    `uc_tenants.facturi_emite`, și calea neinteractivă `uc_api`), pentru un șablon `{tert_nume, tert_cui, tert_tara, linii}`: [(câmp,
    mesaj)]. Le cer și salvarea șablonului, și cronul — un șablon salvat înainte de 462 nu scapă de ele la emitere.
    `platitor` = statutul firmei (`uc_comun._platitor_tva_firma`); None = verificarea plătitorului nu se cere (numai beneficiarul)."""
    from core import categorii_tva as _ct
    out = []
    if not str(s.get("tert_nume") or "").strip():
        out.append(("fr-nume", MESAJ_BENEFICIAR))
    cui = str(s.get("tert_cui") or "").replace(" ", "").upper()
    tara = tara_sablonului(s)
    if cui[:2].isalpha() and cui[:2] != "RO" and tara == "RO":
        # [C160] codul altui stat cu țara „România” (și orice șablon de dinainte de C160, fără țară): factura ar ieși vânzare în România
        out.append(("fr-cui", MESAJ_CLIENT_STRAIN % cui))
    elif tara != "RO" and platitor is True and not any(
            isinstance(l, dict) and l.get("categorie_tva") in _ct.CATEGORII for l in s.get("linii") or []):
        out.append(("fr-cui", MESAJ_STRAIN_FARA_CATEGORIE % tara))
    for i, l in enumerate(s.get("linii") or []):
        if isinstance(l, dict) and l.get("articol_id"):
            out.append(("fr-l%d-descriere" % i, MESAJ_ARTICOL_STOC % (i + 1)))
    return out


def _camp_sablon(camp):
    """Câmpul formularului de emitere (`em-l{i}-…`) -> câmpul formularului șablonului (`fr-l{i}-…`); restul rămân cum sunt (fără câmp
    pe ecranul șablonului, ecranul le arată în caseta formularului)."""
    return "fr-l" + camp[len("em-l"):] if str(camp).startswith("em-l") else camp


def _proba_emiterii(conn, schema, corp, raspunsuri_ai=None, azi=None):
    """Emiterea facturii din șablon, DE PROBĂ: `facturi_api.emite_factura` (aceleași verificări ca factura obișnuită) într-un SAVEPOINT
    anulat la capăt — nimic nu rămâne scris (nici factura, nici nota ei, nici numărul rezervat). Întoarce refuzurile: [(câmp|None, mesaj)].
    La un curs BNR refuzat, `emite_factura` anulează ea tranzacția (nimic nu fusese scris înaintea ei)."""
    from core import uc_comun as _uc
    azi = azi or datetime.date.today()
    rele = []
    with conn.cursor() as cur:
        cur.execute("SAVEPOINT proba_sablon")
        cur.execute("SET search_path TO %s, public" % schema)   # emite_factura scrie necalificat, ca la cron
    vie = True
    try:
        r = facturi_api.emite_factura(conn, corp.get("linii") or [], client_id=corp.get("client_id"),
                                      tert_nume=corp.get("tert_nume"), tert_cui=corp.get("tert_cui"),
                                      tert_tara=tara_sablonului(corp),   # [C160] țara clientului, ca la factura obișnuită
                                      data_emitere=azi.isoformat(), moneda=corp.get("moneda") or "RON",
                                      platitor_tva=_uc._platitor_tva_firma(conn), raspunsuri_ai=raspunsuri_ai)
        if isinstance(r, dict) and r.get("ok") is False:   # cursul BNR (prea vechi / necotat / indisponibil): tranzacția e anulată
            vie = False
            rele.append((None, PREFIX_PROBA + str(r.get("mesaj") or r.get("cod") or "cursul BNR nu s-a putut stabili")))
    except facturi_api.LiniiIncomplete as e:
        for x in e.campuri:
            rele.append((_camp_sablon(x["camp"]), "%s — %s" % (x["eticheta"], x.get("mesaj") or "completează câmpul.")))
    except ValueError as e:
        m = str(e)
        rele.append((None, PREFIX_PROBA + (m[len(_REFUZ_EMITERE):] if m.startswith(_REFUZ_EMITERE) else m)))
    finally:
        if vie:
            with conn.cursor() as cur:
                cur.execute("ROLLBACK TO SAVEPOINT proba_sablon")
                cur.execute("RELEASE SAVEPOINT proba_sablon")
    return rele


def lista(conn, schema):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""SELECT id, client_id, tert_nume, tert_cui, tert_tara, linii, zi_emitere,
                               moneda, activ, ultima_emitere
                        FROM {schema}.facturi_recurente ORDER BY id""")
        rows = [dict(r) for r in cur.fetchall()]
    for r in rows:
        if isinstance(r["linii"], str):
            r["linii"] = json.loads(r["linii"])
        if r["ultima_emitere"]:
            r["ultima_emitere"] = str(r["ultima_emitere"])
    return rows


def adauga(conn, schema, corp, raspunsuri_ai=None, azi=None):
    """[462] `raspunsuri_ai` = răspunsurile modelului pentru liniile șablonului, cerute de apelant ÎNAINTEA conexiunii
    (`uc_comun._intreaba_modelul`, R193), ca la emiterea obișnuită; fără ele, o linie a cărei cotă / cont de venit le cere e refuzată
    ca nedeterminată — tot ca acolo."""
    # [440, comanda Costin 11.1 pct.16] liniile, beneficiarul și ziua se judecă TOATE (`ErorileFormularului`), fiecare lângă câmpul ei
    # din ecran (`fr-linii`, `fr-nume`, `fr-zi`, `fr-l{i}-…`); înainte, beneficiarul și ziua se refuzau numai după linii, una câte una,
    # iar ziua greșită purta id-ul `fr-zi_emitere`, care nu există pe ecran
    from core.erori import ErorileFormularului as _Erori
    er = _Erori("Șablonul nu s-a salvat")
    linii = corp.get("linii") or []
    if not linii:
        er.camp("fr-linii", "Adaugă cel puțin o linie de facturat (denumire, cantitate, preț): fără ea, factura lunară n-ar avea ce "
                            "emite.")
    # [462] beneficiarul (denumirea) e obligatoriu ca pe factura obișnuită — înainte ajungea și numai `client_id`
    for camp, mesaj in verificari_drum({"tert_nume": corp.get("tert_nume"), "linii": []}):
        er.camp(camp, mesaj)
    # [probare invalid lot 2, 03.09.2026] `zi_emitere="prima"` cadea in `int()` si iesea `500`.
    # Un camp completat cu litere e o greseala de tastare, nu o cadere de sistem.
    _zi = corp.get("zi_emitere")
    try:
        zi = int(_zi) if _zi not in (None, "") else 1
    except (TypeError, ValueError):
        zi = None
        er.camp("fr-zi", "Ziua emiterii: %r nu e un număr. Scrie o zi între 1 și 28." % (_zi,))
    if zi is not None and not 1 <= zi <= 28:
        er.camp("fr-zi", "Ziua emiterii trebuie să fie între 1 și 28.")
    # [C160] țara clientului: codul din două litere al listei de pe ecran (ca `em-tara` la „Emite factură”); lipsă -> „RO”
    tara = tara_sablonului(corp)
    if not (len(tara) == 2 and tara.isascii() and tara.isalpha()):
        er.camp("fr-tara", MESAJ_TARA % (corp.get("tert_tara"),))
    # [cap.24 regula 2] validare per-linie AUTORITARA: un rand incomplet se raporteaza langa campul lui
    # (fr-l{i}-..), nu il filtreaza tacit frontendul. Aceleasi criterii (denumire nevida + cantitate>0),
    # din aceeasi functie ca emitere (fara oglinda care drifteaza, cap.24 regula 4).
    for x in facturi_api.linii_campuri_lipsa(linii, prefix="fr-l"):
        er.camp(x["camp"], "%s — %s" % (x["eticheta"], x.get("mesaj") or "completează câmpul."))
    # [462] liniile cu articol de stoc (calea automată nu poate întreba „Pleacă marfa acum?”) și codul fiscal al partenerului, apoi
    # emiterea de probă: aceleași verificări ca factura obișnuită, la salvare — nu la cron
    from core import repo_firma_profil as _rfp
    with conn.cursor() as cur:   # [C160] statutul firmei, citit pe schema ei (conexiunea rutei n-are search_path)
        _pl = _rfp.platitor_tva(cur, schema)
    for camp, mesaj in verificari_drum({"tert_nume": "-", "tert_cui": corp.get("tert_cui"), "tert_tara": tara, "linii": linii},
                                       bool(_pl[0]) if _pl else True):
        er.camp(camp, mesaj)
    if not er:
        try:
            facturi_api.cere_cod_partener(corp.get("tert_cui"), False, corp.get("tert_nume"))
        except ValueError as e:
            er.camp("fr-cui", str(e))
    if not er:
        for camp, mesaj in _proba_emiterii(conn, schema, corp, raspunsuri_ai, azi):
            if camp:
                er.camp(camp, mesaj)
            else:
                er.fara_camp(mesaj)
    if er:
        d = er.detaliu()
        return {"eroare": d["mesaj"], "erori_campuri": d["erori_campuri"]}
    with conn.cursor() as cur:
        cur.execute(f"""INSERT INTO {schema}.facturi_recurente
            (client_id, tert_nume, tert_cui, tert_tara, linii, zi_emitere, moneda)
            VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
            (corp.get("client_id"), corp.get("tert_nume"), corp.get("tert_cui"), tara,
             json.dumps(linii), zi, corp.get("moneda", "RON")))
        rid = cur.fetchone()[0]
    conn.commit()
    return {"id": rid}


def comuta(conn, schema, sablon_id, activ):
    with conn.cursor() as cur:
        cur.execute(f"UPDATE {schema}.facturi_recurente SET activ=%s WHERE id=%s RETURNING id",
                    (activ, sablon_id))
        if not cur.fetchone():
            return {"eroare": "Șablonul de factură recurentă cu id %s nu există "
                              "(a fost șters, sau id-ul e greșit)." % (sablon_id,)}
    conn.commit()
    return {"id": sablon_id, "activ": activ}


def sterge(conn, schema, sablon_id):
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM {schema}.facturi_recurente WHERE id=%s RETURNING id", (sablon_id,))
        if not cur.fetchone():
            return {"eroare": "Șablonul de factură recurentă cu id %s nu există "
                              "(a fost șters, sau id-ul e greșit)." % (sablon_id,)}
    conn.commit()
    return {"sters": sablon_id}


def de_emis(sabloane, azi=None):
    """PURA: filtreaza sabloanele scadente azi. sabloane: [{id, activ, zi_emitere, ultima_emitere}]."""
    azi = azi or datetime.date.today()
    rezultat = []
    for s in sabloane:
        if not s.get("activ"):
            continue
        if int(s["zi_emitere"]) > azi.day:
            continue
        ue = s.get("ultima_emitere")
        if ue:
            d = datetime.date.fromisoformat(str(ue)[:10])
            if d.year == azi.year and d.month == azi.month:
                continue
        rezultat.append(s)
    return rezultat


def emite_scadente(schema, azi=None):
    """Emite facturile scadente pentru un tenant. Intoarce lista emisa.

    [R193, comanda Costin 10.10.2026 pct.2] Pe faze, ca `woocommerce.sincronizeaza`: (1) o citire scurta — abonamentele scadente,
    statutul de platitor TVA, ce linii cer raspunsul modelului; (2) cursul BNR si intrebarea catre model, fara conexiune; (3) emiterea,
    pe o conexiune noua, care RECITESTE abonamentele (unul emis intre timp de alta rulare nu se mai emite). Pana azi functia primea
    conexiunea de la apelant si intreba modelul cu ea in mana; iar statutul de platitor cadea tacit pe `True` daca citirea lui esua
    (`except: rollback`) — o firma neplatitoare ar fi facturat cu TVA. Acum citirea e cea a rutelor (`_platitor_tva_firma`), fara
    plasa: daca nu se poate citi, nu se emite."""
    from core import cote_tva, db, uc_comun as _uc
    from core import uc_curs_bnr as _uc_cb
    azi = azi or datetime.date.today()
    with db.get_conn(schema) as conn:
        _scadente = de_emis(lista(conn, schema), azi)
        platitor = _uc._platitor_tva_firma(conn)
        de_intrebat = [d for _s in _scadente for d in facturi_api.intrebari_model(conn, _s["linii"], platitor)]
    if not _scadente:
        return []
    # [P5 val 3, 11.09.2026] Cursul BNR se aduce ACUM, pentru toate monedele lotului: `curs_pentru`
    # decide pe cache, iar descarcarea n-are ce cauta in mijlocul emiterii.
    for _m in {(_s.get("moneda") or "RON") for _s in _scadente}:
        try:
            _uc_cb.asigura_cursul(_m, azi)
        except Exception:      # noqa: BLE001 — pre-incalzirea nu poate strica emiterea
            pass
    raspunsuri_ai = cote_tva.intreaba(de_intrebat, platitor)
    # [462] plătitorul de TVA al beneficiarului român, din ANAF, înaintea tranzacției de emitere — ca pe drumul obișnuit
    # (`uc_tenants.facturi_emite`: `_platitor_tva_tert`); None = nu se poate ști, factura poartă codul cum e scris (CF art.318 alin.(1))
    platitori_tert = {_s["id"]: _uc._platitor_tva_tert(_s.get("tert_cui"), tara_sablonului(_s)) for _s in _scadente}   # [C160] țara lui
    emise = []
    # [368] începutul scrierii, pe același ceas și cu aceeași marjă ca middleware-ul (`main._autor_si_note_in_coada`)
    from core import uc_coada as _uc_coada_ni
    de_la = _uc_coada_ni.inceputul_scrierii()
    with db.get_conn(schema) as conn:
        platitor = _uc._platitor_tva_firma(conn)
        for s in de_emis(lista(conn, schema), azi):   # REVALIDARE: scadente si acum
            rele = verificari_drum(s, platitor)   # [462] și pe șabloanele salvate înainte de 462: aceleași verificări ca drumul obișnuit
            if rele:
                emise.append({"sablon": s["id"], "eroare": " ".join(m for _c, m in rele)})
                continue
            try:
                with conn.cursor() as cur:   # un rollback de mai jos anuleaza si SET-ul facut in tranzactia lui
                    cur.execute(f"SET search_path TO {schema}")
                r = facturi_api.emite_factura(conn, s["linii"], client_id=s.get("client_id"),
                        tert_nume=s.get("tert_nume"), tert_cui=s.get("tert_cui"), tert_tara=tara_sablonului(s),   # [C160]
                        data_emitere=azi.isoformat(), moneda=s.get("moneda") or "RON",
                        platitor_tva=platitor, raspunsuri_ai=raspunsuri_ai,
                        tert_platitor_tva=platitori_tert.get(s["id"]))
                with conn.cursor() as cur:
                    cur.execute(f"UPDATE {schema}.facturi_recurente SET ultima_emitere=%s WHERE id=%s",
                                (azi, s["id"]))
                conn.commit()
                emise.append({"sablon": s["id"], "factura": r.get("numar")})
            except Exception as e:
                conn.rollback()
                emise.append({"sablon": s["id"], "eroare": str(e)})
    if any("eroare" not in e for e in emise):
        _note_interne(schema, de_la, emise)
    return emise


def _note_interne(schema, de_la, emise):
    """[deficiența 368, decizia Costin 19.10.2026 „Se validează automat”] Cronul nu trece prin middleware-ul care validează notele unei
    firme în partidă simplă, deci notele facturilor emise se validează aici, ca note interne, după commitul emiterii (conexiunea ei e
    închisă). Notele cronului n-au autor (`creat_de_id` NULL). Un refuz nu oprește cronul: nota rămâne ciornă, iar refuzul intră în
    jurnalul jobului (lista întoarsă, tipărită de `_main`), ca eroarea unui șablon."""
    from core import observare as _obs, uc_coada as _uc_coada
    try:
        ni = _uc_coada.note_interne_schema(schema, None, de_la)
    except Exception as e:  # noqa: BLE001 — facturile sunt emise, notele rămân ciornă; eșecul nu e tăcut
        _obs.esec_secundar("validarea notelor interne (partidă simplă, facturi recurente %s)" % schema, e)
        return
    if ni["interne"] or ni["refuzate"]:
        emise.append({"note_interne": ni})


def _main():
    """Cron zilnic: parcurge toti tenantii activi."""
    from core import db
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM public.tenants WHERE activ")
            scheme = [r[0] for r in cur.fetchall()]
    total = []
    for sch in scheme:
        rez = emite_scadente(sch)
        if rez:
            total.append({sch: rez})
    print(datetime.datetime.now().isoformat(), "facturi recurente:", total or "nimic de emis")


if __name__ == "__main__":
    from core import cron
    cron.ruleaza("facturi_recurente", _main)
