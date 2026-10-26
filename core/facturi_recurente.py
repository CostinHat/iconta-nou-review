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
al altui stat cu țara „România” (și șabloanele vechi, fără țară) și, la plătitor, clientul din altă țară pe o linie fără cotă aleasă.
TEMEI: CF art.325 alin.(1) lit.a și c (D390: livrările intracomunitare de bunuri și prestările art.278 alin.(2) către persoane impozabile
stabilite în alt stat membru); CF art.278 alin.(2) (locul prestării, la beneficiarul persoană impozabilă).

[lotul 12, comanda Costin 12.3 pct.9, verbatim: „Da: cota și categoria pe linia șablonului recurent, ca la factură.”] Ecranul șablonului
alege cota fiecărei linii (cotele în vigoare, propunerea din nomenclator preselectată) și, la cota 0 a plătitorului, categoria de TVA — aceleași
liste ca „Emite factură” (`facturi_api.pregatire_emitere`); la taxarea inversă, și categoria produsului (`categorie_331`, a documentului).
Proba de la salvare și cronul le dau emiterii (`emite_factura` le verifică: `categorii_tva.verifica_linii`). De aici, refuzul C160 al
clientului din alt stat la plătitor („ecranul șablonului nu alege cota și categoria liniei”) se ridică acolo unde linia are cota aleasă:
rămâne numai pe linia FĂRĂ cotă (`MESAJ_STRAIN_FARA_COTA`), a cărei cotă s-ar lua lunar din nomenclator, ca la o vânzare în România.

[lotul 12, comanda Costin 12.3 pct.1, verbatim: „C109: refuzul cronului ajunge la contabil prin notificare (clopoțel și email); pe șablon
se vede și starea ultimei emiteri.”] Un refuz al emiterii automate se scrie pe șablon (`ultimul_refuz`, `ultimul_refuz_la`; golite la
emiterea reușită — `core/migrare_sablon_recurent_stare.py`) și intră, în ACEEAȘI tranzacție, în clopoțelul celor care pregătesc pe firmă
(tipul `factura_recurenta_refuzata`, bifat din oficiu, deci pleacă și pe email — mecanismul comun, `core/notificari.py`). Cronul reîncearcă
zilnic un șablon refuzat (`de_emis`), deci același refuz se anunță o dată pe lună, nu în fiecare zi (`refuz_de_anuntat`). Tot aici: cursul
BNR refuzat la emitere (`emite_factura` întoarce `{"ok": False}`, fără factură) trecea șablonul drept emis în luna aceea.
"""
import json
import datetime
from psycopg2.extras import RealDictCursor
from core import facturi_api

# ── [lotul 13, deficiența 680] ACELEAȘI ÎNTREBĂRI CA „EMITE FACTURĂ”, NIMIC IMPLICIT ────────────────────────────────────────────────────
# Comanda 13.1, verbatim: „680: [...] lipsesc seria, scadența, perioada de valabilitate și, mai ales, dacă factura se emite singură sau ca
# ciornă și dacă pleacă singură în SPV. Șablonul folosește aceleași controale ca Emite factură”. Pe șablon se cer, fiecare explicit:
#   * scadența: termenul de plată în zile de la emitere (data scadenței facturii lunii = data emiterii + zilele; 0 = la emitere);
#   * perioada de valabilitate: de la (obligatoriu) și până la — o dată, sau „până îl opresc”, ales (`valabil_pana`);
#   * modul emiterii: „automata” (cronul emite factura în ziua ei) sau „ciorna” (cronul o pregătește și o anunță în clopoțel; contabilul o
#     emite din listă, cu „Emite factura lunii” — pe același drum ca cronul, `emite_unul`);
#   * trimiterea în SPV (numai la emiterea automată): factura emisă pleacă singură în RO e-Factura, sau o trimite contabilul.
# Seria e cea a firmei (numerotarea facturilor, ca la „Emite factură”); ecranul o arată.
MODURI = ("automata", "ciorna")
MESAJ_MOD = "Alege cum se emite factura lunară: singură (automat, în ziua ei) sau ca ciornă pregătită, pe care o emiți tu."
MESAJ_SPV = "Alege dacă factura emisă automat pleacă singură în SPV (RO e-Factura) sau o trimiți tu din Istoric facturi."
MESAJ_SCADENTA = "Scrie termenul de plată, în zile de la emitere (0 = scadența în ziua emiterii)."
MESAJ_INCEPUT = "Scrie data de la care e valabil șablonul (prima lună în care se emite factura)."
MESAJ_PANA = "Alege până când e valabil șablonul: până la o dată, sau până îl oprești."
MESAJ_SFARSIT = "Scrie data până la care e valabil șablonul (sau alege „până îl opresc”)."
MESAJ_NU_E_DE_EMIS = ("Factura lunii din acest șablon nu e de emis azi (a fost emisă luna asta, ziua ei n-a venit, sau șablonul e inactiv / "
                      "în afara perioadei de valabilitate).")
#: [680] tipul notificării pentru ciorna pregătită (același tip ca avertismentul emiterii: e „de știut” despre factura recurentă)
TIP_CIORNA = "factura_recurenta_avertisment"


def _data_ceruta(v):
    try:
        return datetime.date.fromisoformat(str(v)[:10]) if v not in (None, "") else None
    except ValueError:
        return False


def cere_emiterea(corp, er):
    """[680] Întrebările șablonului (scadența, perioada, modul, SPV), toate deodată în `er`, fiecare lângă câmpul ei. Întoarce valorile
    curate {scadenta_zile, data_inceput, data_sfarsit, mod_emitere, trimite_spv} (None unde lipsesc)."""
    out = {"scadenta_zile": None, "data_inceput": None, "data_sfarsit": None, "mod_emitere": None, "trimite_spv": None}
    z = corp.get("scadenta_zile")
    try:
        out["scadenta_zile"] = int(z) if z not in (None, "") else None
    except (TypeError, ValueError):
        er.camp("fr-scadenta", "Termenul de plată: %r nu e un număr de zile." % (z,))
    else:
        if out["scadenta_zile"] is None:
            er.camp("fr-scadenta", MESAJ_SCADENTA)
        elif not 0 <= out["scadenta_zile"] <= 365:
            er.camp("fr-scadenta", "Termenul de plată e între 0 și 365 de zile.")
    di = _data_ceruta(corp.get("data_inceput"))
    if not di:
        er.camp("fr-inceput", MESAJ_INCEPUT if di is None else "Data de început nu e o dată din calendar.")
    out["data_inceput"] = di or None
    pana = corp.get("valabil_pana")
    if pana not in ("data", "oprire"):
        er.camp("fr-pana", MESAJ_PANA)
    elif pana == "data":
        ds = _data_ceruta(corp.get("data_sfarsit"))
        if not ds:
            er.camp("fr-sfarsit", MESAJ_SFARSIT if ds is None else "Data de sfârșit nu e o dată din calendar.")
        elif di and ds < di:
            er.camp("fr-sfarsit", "Data de sfârșit e înaintea datei de început.")
        out["data_sfarsit"] = ds or None
    mod = corp.get("mod_emitere")
    if mod not in MODURI:
        er.camp("fr-mod", MESAJ_MOD)
    out["mod_emitere"] = mod if mod in MODURI else None
    if mod == "automata":
        t = corp.get("trimite_spv")
        if t not in (True, False):
            er.camp("fr-spv", MESAJ_SPV)
        out["trimite_spv"] = t if t in (True, False) else None
    elif mod == "ciorna":
        out["trimite_spv"] = False   # ciorna o emite contabilul; trimiterea în SPV o face tot el, după emitere
    return out


def in_valabilitate(s, azi):
    """PURĂ. [680] Șablonul e valabil azi (`data_inceput` <= azi <= `data_sfarsit`; fără ele — șablonul de dinainte de 680 — oricând)."""
    di, ds = s.get("data_inceput"), s.get("data_sfarsit")
    di = datetime.date.fromisoformat(str(di)[:10]) if di else None
    ds = datetime.date.fromisoformat(str(ds)[:10]) if ds else None
    return (di is None or di <= azi) and (ds is None or azi <= ds)


def scadenta(s, azi):
    """PURĂ. [680] Data scadenței facturii emise azi din șablon (None fără termen: șablonul de dinainte de 680)."""
    z = s.get("scadenta_zile")
    return (azi + datetime.timedelta(days=int(z))).isoformat() if z is not None else None

MESAJ_BENEFICIAR = "Scrie beneficiarul facturii (denumirea clientului)."
MESAJ_ARTICOL_STOC = ("Linia %d are un articol de stoc: factura lunară se emite automat și nu poate întreba dacă marfa pleacă odată cu ea "
                      "(un răspuns ales de aplicație ar descărca gestiunea fără știrea ta, sau ar lăsa stocul greșit). Emite marfa din "
                      "„Emite factură”; în șablon rămân serviciile și ce nu se descarcă din stoc.")
MESAJ_CLIENT_STRAIN = ("Codul %s e al unui client din alt stat, dar țara clientului din șablon e România: alege țara clientului. Altfel "
                       "factura lunară ar ieși ca o vânzare în România.")
#: [C160, 12.3 pct.9] plătitorul, clientul din altă țară, linia FĂRĂ cotă aleasă: cota ei s-ar lua lunar din nomenclator (cea a unei
#: vânzări în România); pe linia cu cota aleasă (și categoria, la 0%) refuzul nu se mai cere
MESAJ_STRAIN_FARA_COTA = ("Linia %d: clientul e din alt stat (%s), deci alege cota de TVA a liniei (iar la 0%%, categoria: livrare "
                          "intracomunitară, prestare de servicii cu locul în afara României, export). Fără ea, cota s-ar lua în fiecare "
                          "lună din nomenclator, ca la o vânzare în România.")
MESAJ_TARA = "Țara clientului: %r nu e un cod de țară. Alege țara din listă."
PREFIX_PROBA = "Factura lunară ar fi refuzată la emitere: "
_REFUZ_EMITERE = "Factura nu s-a emis: "   # începutul refuzurilor emiterii; sub PREFIX_PROBA nu se mai spune a doua oară
#: [C109] refuzul care nu vine din verificările emiterii (o cădere a aplicației): contabilul nu primește textul tehnic, operatorul îl
#: primește prin alertă (`observare.esec_secundar`), iar jurnalul jobului îl păstrează întreg
MESAJ_NEPREVAZUT = "a apărut o eroare neprevăzută la emitere; echipa iConta.eu a fost anunțată și o verifică."
#: [C109] tipul notificării (`notificari.TIPURI`)
TIP_REFUZ = "factura_recurenta_refuzata"
#: [lotul 12, C197] factura emisă de cron cu avertismentele emiterii (`emite_factura` -> `avertismente`: C84 livrarea intracomunitară
#: neîntrebată, C157 prestarea art.317 neînregistrată): ajung la contabil prin clopoțel + email, ca refuzul C109 — nu se pierd în cron
TIP_AVERTISMENT = "factura_recurenta_avertisment"


def tara_sablonului(s):
    """[C160] Țara clientului din șablon (`tert_tara`, cod din două litere, majuscule); lipsă -> „RO”, ca la `facturi.tert_tara`."""
    return str(s.get("tert_tara") or "").strip().upper() or "RO"


def verificari_drum(s, platitor=None):
    """PURĂ. Verificările drumului obișnuit de emitere care NU stau în `facturi_api.emite_factura` (le face ruta `facturi/emite`,
    `uc_tenants.facturi_emite`, și calea neinteractivă `uc_api`), pentru un șablon `{tert_nume, tert_cui, tert_tara, linii}`: [(câmp,
    mesaj)]. Le cer și salvarea șablonului, și cronul — un șablon salvat înainte de 462 nu scapă de ele la emitere.
    `platitor` = statutul firmei (`uc_comun._platitor_tva_firma`); None = verificarea plătitorului nu se cere (numai beneficiarul)."""
    out = []
    if not str(s.get("tert_nume") or "").strip():
        out.append(("fr-nume", MESAJ_BENEFICIAR))
    cui = str(s.get("tert_cui") or "").replace(" ", "").upper()
    tara = tara_sablonului(s)
    if cui[:2].isalpha() and cui[:2] != "RO" and tara == "RO":
        # [C160] codul altui stat cu țara „România” (și orice șablon de dinainte de C160, fără țară): factura ar ieși vânzare în România
        out.append(("fr-cui", MESAJ_CLIENT_STRAIN % cui))
    elif tara != "RO" and platitor is True:
        # [12.3 pct.9] linia cu cota aleasă (și, la 0%, categoria, cerută de `categorii_tva.verifica_linii`) spune operațiunea; cea fără
        # cotă și-ar lua-o lunar din nomenclator — cota unei vânzări în România
        for i, l in enumerate(s.get("linii") or []):
            if isinstance(l, dict) and l.get("cota_tva") is None:
                out.append(("fr-l%d-cota" % i, MESAJ_STRAIN_FARA_COTA % (i + 1, tara)))
    for i, l in enumerate(s.get("linii") or []):
        if isinstance(l, dict) and l.get("articol_id"):
            out.append(("fr-l%d-descriere" % i, MESAJ_ARTICOL_STOC % (i + 1)))
    return out


def _camp_sablon(camp):
    """Câmpul formularului de emitere (`em-l{i}-…`, `em-c331`) -> câmpul formularului șablonului (`fr-l{i}-…`, `fr-c331`); restul rămân
    cum sunt (fără câmp pe ecranul șablonului, ecranul le arată în caseta formularului)."""
    camp = str(camp)
    if camp.startswith("em-l"):
        return "fr-l" + camp[len("em-l"):]
    return "fr-c331" if camp == "em-c331" else camp


def motiv_refuzului(e):
    """[C109] Textul pentru contabil al unui refuz al emiterii (`ValueError` din `emite_factura`): liniile refuzate („Linia 1: categoria de
    TVA — …”), altfel mesajul, fără începutul „Factura nu s-a emis: ” (îl spune cine îl arată)."""
    if isinstance(e, facturi_api.LiniiIncomplete):
        return " ".join("%s — %s" % (x["eticheta"], x.get("mesaj") or "completează câmpul.") for x in e.campuri)
    m = str(e)
    return m[len(_REFUZ_EMITERE):] if m.startswith(_REFUZ_EMITERE) else m


def _motiv_curs(r):
    """Refuzul cursului BNR întors de `emite_factura` (`{"ok": False, "mesaj", "cod"}`)."""
    return str(r.get("mesaj") or r.get("cod") or "cursul BNR nu s-a putut stabili")


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
                                      platitor_tva=_uc._platitor_tva_firma(conn), raspunsuri_ai=raspunsuri_ai,
                                      categorie_331=corp.get("categorie_331"))   # [12.3 pct.9] categoria produsului, ca la factură
        if isinstance(r, dict) and r.get("ok") is False:   # cursul BNR (prea vechi / necotat / indisponibil): tranzacția e anulată
            vie = False
            rele.append((None, PREFIX_PROBA + _motiv_curs(r)))
    except facturi_api.LiniiIncomplete as e:
        for x in e.campuri:
            rele.append((_camp_sablon(x["camp"]), "%s — %s" % (x["eticheta"], x.get("mesaj") or "completează câmpul.")))
    except ValueError as e:
        rele.append((None, PREFIX_PROBA + motiv_refuzului(e)))
    finally:
        if vie:
            with conn.cursor() as cur:
                cur.execute("ROLLBACK TO SAVEPOINT proba_sablon")
                cur.execute("RELEASE SAVEPOINT proba_sablon")
    return rele


def lista(conn, schema):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""SELECT id, client_id, tert_nume, tert_cui, tert_tara, linii, zi_emitere,
                               moneda, activ, ultima_emitere, ultimul_refuz, ultimul_refuz_la, categorie_331,
                               scadenta_zile, data_inceput, data_sfarsit, mod_emitere, trimite_spv, ultima_pregatire
                        FROM {schema}.facturi_recurente ORDER BY id""")
        rows = [dict(r) for r in cur.fetchall()]
    azi = datetime.date.today()
    for r in rows:
        if isinstance(r["linii"], str):
            r["linii"] = json.loads(r["linii"])
        # [680] ciorna lunii: pregătită (scadentă azi, în valabilitate, neemisă luna asta) -> butonul „Emite factura lunii”
        r["de_emis_acum"] = bool(r.get("mod_emitere") == "ciorna" and de_emis([r], azi, mod="ciorna"))
        for k in ("ultima_emitere", "ultimul_refuz_la", "data_inceput", "data_sfarsit", "ultima_pregatire"):
            if r[k]:
                r[k] = str(r[k])
    return rows


def _categorie_331(corp):
    """[12.3 pct.9] Categoria produsului cu taxare inversă (codul D394), numai cât o linie are categoria „taxare_inversa” (ca la „Emite
    factură”, unde câmpul apare numai atunci)."""
    are = any(isinstance(l, dict) and l.get("categorie_tva") == "taxare_inversa" for l in corp.get("linii") or [])
    return (str(corp.get("categorie_331") or "").strip() or None) if are else None


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
        zi = int(_zi) if _zi not in (None, "") else None
        if zi is None:   # [lotul 13, 680] nimic implicit: ziua emiterii se cere (era 1 din oficiu)
            er.camp("fr-zi", "Scrie ziua din lună în care se emite factura (1–28).")
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
    em = cere_emiterea(corp, er)   # [lotul 13, 680] scadența, perioada, modul, SPV — toate deodată, fiecare lângă câmpul ei
    c331 = _categorie_331(corp)
    if not er:
        for camp, mesaj in _proba_emiterii(conn, schema, dict(corp, categorie_331=c331), raspunsuri_ai, azi):
            if camp:
                er.camp(camp, mesaj)
            else:
                er.fara_camp(mesaj)
    if er:
        d = er.detaliu()
        return {"eroare": d["mesaj"], "erori_campuri": d["erori_campuri"]}
    with conn.cursor() as cur:
        cur.execute(f"""INSERT INTO {schema}.facturi_recurente
            (client_id, tert_nume, tert_cui, tert_tara, linii, zi_emitere, moneda, categorie_331,
             scadenta_zile, data_inceput, data_sfarsit, mod_emitere, trimite_spv)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
            (corp.get("client_id"), corp.get("tert_nume"), corp.get("tert_cui"), tara,
             json.dumps(linii), zi, corp.get("moneda", "RON"), c331,
             em["scadenta_zile"], em["data_inceput"], em["data_sfarsit"], em["mod_emitere"], em["trimite_spv"]))
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


def de_emis(sabloane, azi=None, mod="automata"):
    """PURA: filtreaza sabloanele scadente azi. sabloane: [{id, activ, zi_emitere, ultima_emitere}].
    [lotul 13, 680] numai cele cu modul `mod` (cronul emite „automata”; „ciorna” o pregătește) și în perioada de valabilitate; șablonul de
    dinainte de 680 (fără mod, până la migrare) se emite automat, ca până acum."""
    azi = azi or datetime.date.today()
    rezultat = []
    for s in sabloane:
        if not s.get("activ"):
            continue
        if (s.get("mod_emitere") or "automata") != mod or not in_valabilitate(s, azi):
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


def refuz_de_anuntat(s, motiv, azi):
    """PURĂ. [C109] Refuzul de azi se anunță? Da, dacă e altul decât cel consemnat pe șablon, sau dacă cel consemnat e dintr-o lună de
    dinainte (factura altei luni). Același refuz, în aceeași lună, nu se mai anunță: cronul reîncearcă zilnic șablonul refuzat."""
    la = s.get("ultimul_refuz_la")
    if not la or (s.get("ultimul_refuz") or "") != motiv:
        return True
    d = datetime.date.fromisoformat(str(la)[:10])
    return (d.year, d.month) != (azi.year, azi.month)


def text_refuz(nume_firma, s, motiv, azi):
    """[C109] Textul din clopoțel (în aplicație: cu firma, clientul și motivul; pe email / WhatsApp pleacă numai eticheta tipului)."""
    from core.pdf_util import data_ro
    return ("%s: factura recurentă pentru %s nu s-a emis (%s). Motivul: %s Aplicația o încearcă din nou zilnic, până la sfârșitul lunii; "
            "motivul e și pe șablon, în Facturi → Facturi recurente." % (
                nume_firma, str(s.get("tert_nume") or "").strip() or "clientul șablonului", data_ro(azi.isoformat()),
                motiv.rstrip() if motiv.rstrip().endswith(".") else motiv.rstrip() + "."))


def text_avertisment(nume_firma, s, numar, avertismente, azi):
    """[C197] Textul din clopoțel pentru factura recurentă emisă cu avertismente: firma, clientul, numărul, data și fiecare avertisment."""
    from core.common import cate
    from core.pdf_util import data_ro
    return "%s: factura recurentă pentru %s s-a emis (%s, %s), cu %s: %s" % (
        nume_firma, str(s.get("tert_nume") or "").strip() or "clientul șablonului", numar or "fără număr", data_ro(azi.isoformat()),
        cate(len(avertismente), "avertisment", "avertismente"), " ".join(
            a.rstrip() if a.rstrip().endswith(".") else a.rstrip() + "." for a in avertismente))


def _consemneaza_refuzul(conn, schema, s, motiv, azi):
    """[C109] Refuzul de azi: pe șablon (`ultimul_refuz`, `ultimul_refuz_la`) și, dacă e nou (`refuz_de_anuntat`), în clopoțelul celor care
    pregătesc pe firmă — în aceeași tranzacție, comisă aici. O cădere aici nu oprește cronul (celelalte șabloane, celelalte firme): se
    semnalează operatorului."""
    from core import notificari_termene as _nt, observare as _obs
    try:
        anunt = refuz_de_anuntat(s, motiv, azi)
        with conn.cursor() as cur:
            cur.execute(f"UPDATE {schema}.facturi_recurente SET ultimul_refuz=%s, ultimul_refuz_la=%s WHERE id=%s",
                        (motiv, azi, s["id"]))
        if anunt:
            _nt.notifica_pe_conexiune(conn, schema, TIP_REFUZ, lambda nume: text_refuz(nume, s, motiv, azi))
        conn.commit()
    except Exception as e:  # noqa: BLE001 — starea și anunțul refuzului nu opresc cronul; eșecul nu e tăcut
        conn.rollback()
        _obs.esec_secundar("consemnarea refuzului facturii recurente %s/%s" % (schema, s.get("id")), e)


def emite_scadente(schema, azi=None, doar=None):
    """Emite facturile scadente pentru un tenant. Intoarce lista emisa.

    [R193, comanda Costin 10.10.2026 pct.2] Pe faze, ca `woocommerce.sincronizeaza`: (1) o citire scurta — abonamentele scadente,
    statutul de platitor TVA, ce linii cer raspunsul modelului; (2) cursul BNR si intrebarea catre model, fara conexiune; (3) emiterea,
    pe o conexiune noua, care RECITESTE abonamentele (unul emis intre timp de alta rulare nu se mai emite). Pana azi functia primea
    conexiunea de la apelant si intreba modelul cu ea in mana; iar statutul de platitor cadea tacit pe `True` daca citirea lui esua
    (`except: rollback`) — o firma neplatitoare ar fi facturat cu TVA. Acum citirea e cea a rutelor (`_platitor_tva_firma`), fara
    plasa: daca nu se poate citi, nu se emite.
    [C109] Orice refuz — verificările drumului, cursul BNR, refuzul emiterii — se consemnează pe șablon și se anunță
    (`_consemneaza_refuzul`); emiterea reușită golește refuzul consemnat."""
    from core import cote_tva, db, observare as _obs, uc_comun as _uc
    from core import uc_curs_bnr as _uc_cb
    azi = azi or datetime.date.today()
    _mod = None if doar is None else "ciorna"   # [680] „Emite factura lunii” emite ciorna aleasă, pe drumul cronului
    def _alese(sab):
        if doar is None:
            return de_emis(sab, azi)
        return [x for x in de_emis(sab, azi, mod=_mod) + de_emis(sab, azi) if x["id"] == doar][:1]
    with db.get_conn(schema) as conn:
        _scadente = _alese(lista(conn, schema))
        platitor = _uc._platitor_tva_firma(conn)
        de_intrebat = [d for _s in _scadente for d in facturi_api.intrebari_model(conn, _s["linii"], platitor)]
    if not _scadente:
        if doar is None:
            _anunta_ciornele(schema, azi)   # [680] și când nimic nu se emite automat azi
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
        for s in _alese(lista(conn, schema)):   # REVALIDARE: scadente si acum
            rele = verificari_drum(s, platitor)   # [462] și pe șabloanele salvate înainte de 462: aceleași verificări ca drumul obișnuit
            if rele:
                motiv = " ".join(m for _c, m in rele)
                emise.append({"sablon": s["id"], "eroare": motiv})
                _consemneaza_refuzul(conn, schema, s, motiv, azi)
                continue
            try:
                with conn.cursor() as cur:   # un rollback de mai jos anuleaza si SET-ul facut in tranzactia lui
                    cur.execute(f"SET search_path TO {schema}")
                r = facturi_api.emite_factura(conn, s["linii"], client_id=s.get("client_id"),
                        tert_nume=s.get("tert_nume"), tert_cui=s.get("tert_cui"), tert_tara=tara_sablonului(s),   # [C160]
                        data_emitere=azi.isoformat(), moneda=s.get("moneda") or "RON",
                        data_scadenta=scadenta(s, azi),   # [lotul 13, 680] termenul de plată al șablonului
                        platitor_tva=platitor, raspunsuri_ai=raspunsuri_ai,
                        tert_platitor_tva=platitori_tert.get(s["id"]),
                        categorie_331=s.get("categorie_331"))   # [12.3 pct.9] categoria produsului, ca la factură
                if isinstance(r, dict) and r.get("ok") is False:
                    # [C109] cursul BNR refuzat: `emite_factura` a anulat tranzacția, nicio factură. Înainte se trecea `ultima_emitere`
                    # și șablonul nu se mai încerca în luna aceea — factura lunii lipsea fără niciun semn
                    motiv = _motiv_curs(r)
                    emise.append({"sablon": s["id"], "eroare": motiv})
                    _consemneaza_refuzul(conn, schema, s, motiv, azi)
                    continue
                with conn.cursor() as cur:
                    cur.execute(f"UPDATE {schema}.facturi_recurente SET ultima_emitere=%s, ultimul_refuz=NULL, ultimul_refuz_la=NULL "
                                f"WHERE id=%s", (azi, s["id"]))
                _avert = list(r.get("avertismente") or [])
                if _avert:   # [C197] în ACEEAȘI tranzacție cu factura: emisă și anunțată, sau niciuna
                    from core import notificari_termene as _nt
                    _nt.notifica_pe_conexiune(conn, schema, TIP_AVERTISMENT,
                                              lambda nume, _s=s, _n=r.get("numar"), _a=_avert: text_avertisment(nume, _s, _n, _a, azi))
                conn.commit()
                emise.append({"sablon": s["id"], "factura": r.get("numar"), **({"avertismente": _avert} if _avert else {})})
                if s.get("trimite_spv"):   # [lotul 13, 680] factura emisă automat pleacă singură în SPV (alegerea de pe șablon)
                    emise[-1]["spv"] = _trimite_spv(conn, schema, s, r, azi)
            except Exception as e:  # noqa: BLE001 — refuzul unui șablon nu le oprește pe celelalte; se consemnează și se anunță
                conn.rollback()
                emise.append({"sablon": s["id"], "eroare": str(e)})   # jurnalul jobului: textul întreg
                if not isinstance(e, ValueError):   # o cădere a aplicației, nu un refuz al emiterii: operatorul e anunțat
                    _obs.esec_secundar("emiterea facturii recurente %s/%s" % (schema, s["id"]), e)
                _consemneaza_refuzul(conn, schema, s, motiv_refuzului(e) if isinstance(e, ValueError) else MESAJ_NEPREVAZUT, azi)
    if doar is None:
        _anunta_ciornele(schema, azi)
    if any("eroare" not in e for e in emise):
        _note_interne(schema, de_la, emise)
    return emise


def _anunta_ciornele(schema, azi):
    """[680] Ciornele lunii: pregătite (nu emise) — anunțate o dată pe lună, în clopoțel; contabilul le emite din listă."""
    from core import db
    with db.get_conn(schema) as conn:
        for s in de_emis(lista(conn, schema), azi, mod="ciorna"):
            if s.get("ultima_pregatire") and str(s["ultima_pregatire"])[:7] == azi.isoformat()[:7]:
                continue
            _anunta_ciorna(conn, schema, s, azi)


def text_ciorna(nume_firma, s, azi):
    """[680] Textul din clopoțel pentru ciorna pregătită a lunii."""
    from core.pdf_util import data_ro
    return ("%s: factura recurentă pentru %s e pregătită ca ciornă (%s). N-a fost emisă: o verifici și o emiți din Facturi → Facturi "
            "recurente, cu „Emite factura lunii”." % (nume_firma, str(s.get("tert_nume") or "").strip() or "clientul șablonului",
                                                     data_ro(azi.isoformat())))


def _anunta_ciorna(conn, schema, s, azi):
    """[680] Ciorna lunii, anunțată (clopoțel + email, ca refuzul C109) și consemnată pe șablon (`ultima_pregatire`), în aceeași tranzacție.
    O cădere aici nu oprește cronul; se semnalează operatorului."""
    from core import notificari_termene as _nt, observare as _obs
    try:
        with conn.cursor() as cur:
            cur.execute(f"UPDATE {schema}.facturi_recurente SET ultima_pregatire=%s WHERE id=%s", (azi, s["id"]))
        _nt.notifica_pe_conexiune(conn, schema, TIP_CIORNA, lambda nume: text_ciorna(nume, s, azi))
        conn.commit()
    except Exception as e:  # noqa: BLE001 — anunțul ciornei nu oprește cronul; eșecul nu e tăcut
        conn.rollback()
        _obs.esec_secundar("anunțul ciornei facturii recurente %s/%s" % (schema, s.get("id")), e)


#: [680] stările trimiterii în SPV care înseamnă „a plecat” (`efactura_trimitere.trimite`)
STARI_SPV_PLECATA = ("incarcat", "in_prelucrare", "ok", "deja_trimisa")


def _trimite_spv(conn, schema, s, r, azi):
    """[680] Trimiterea automată în SPV a facturii emise din șablon (`efactura_trimitere.trimite`, același drum ca butonul „Trimite în
    SPV”, cu principalul firmei — cabinetul). Orice altceva decât „a plecat” (fără token, fără drept, date incomplete, ANAF căzut) se
    anunță contabilului în clopoțel, cu motivul: factura rămâne emisă, iar trimiterea o face el din Istoric facturi."""
    import os
    from core import efactura_trimitere as _eft, notificari_termene as _nt, observare as _obs, spv_conector as _sc
    try:
        principal = _sc.principal_pentru_schema(conn, schema)
        rez = _eft.trimite(schema, r["factura_id"], principal, mediu=os.environ.get("EFACTURA_MEDIU", "prod"))
        stare, motiv = rez.get("stare"), rez.get("mesaj") or ("; ".join(rez.get("erori") or []) or rez.get("stare"))
    except Exception as e:  # noqa: BLE001 — trimiterea nereușită nu desface emiterea; se anunță
        _obs.esec_secundar("trimiterea în SPV a facturii recurente %s/%s" % (schema, s.get("id")), e)
        stare, motiv = "eroare", (str(e) if isinstance(e, ValueError) else "trimiterea n-a reușit (echipa iConta.eu a fost anunțată)")
    if stare not in STARI_SPV_PLECATA:
        try:
            _nt.notifica_pe_conexiune(conn, schema, TIP_AVERTISMENT, lambda nume: "%s: factura recurentă %s pentru %s s-a emis, dar n-a plecat "
                                      "în SPV: %s. Trimite-o din Istoric facturi." % (nume, r.get("numar") or "", str(s.get("tert_nume") or ""),
                                                                                     motiv))
            conn.commit()
        except Exception as e:  # noqa: BLE001
            conn.rollback()
            _obs.esec_secundar("anunțul trimiterii SPV a facturii recurente %s/%s" % (schema, s.get("id")), e)
    return stare


def emite_unul(schema, sablon_id, azi=None):
    """[680] „Emite factura lunii” pe ciorna pregătită: aceeași emitere ca a cronului (`emite_scadente`: verificările drumului, cursul,
    modelul, nota), numai pentru acest șablon, dacă e scadent azi. {factura, avertismente} sau {eroare}."""
    azi = azi or datetime.date.today()
    from core import db
    with db.get_conn(schema) as conn:
        s = next((x for x in lista(conn, schema) if x["id"] == int(sablon_id)), None)
    if s is None:
        return {"eroare": "Șablonul nu mai există."}
    if not de_emis([s], azi, mod=s.get("mod_emitere") or "automata"):
        return {"eroare": MESAJ_NU_E_DE_EMIS}
    rez = emite_scadente(schema, azi, doar=int(sablon_id))
    return next((x for x in rez if x.get("sablon") == int(sablon_id)), {"eroare": "Factura nu s-a emis."})


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


def emite_unul_uc(tenant_id, sablon_id, ctx):
    """[lotul 13, 680] Corpul rutei `POST /tenants/{tenant_id}/facturi-recurente/{sid}/emite` („Emite factura lunii” pe ciorna pregătită)."""
    from core import erori as _erori, uc_comun as _uc
    schema = _uc._schema_sau_404(ctx, tenant_id)
    r = emite_unul(schema, sablon_id)
    if r.get("eroare"):
        raise _erori.DateInvalide(r["eroare"])
    return r
