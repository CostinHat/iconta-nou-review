# -*- coding: utf-8 -*-
"""core/p5_clasificare.py — VERDICTUL fiecărui candidat P5, scris o dată și păzit.

**CE E.** `scripts/scan_blocante.py` derivă din cod ce cale are I/O blocant. Inventarul **nu
judecă** — nu poate: „blocant" e o proprietate a formei, „îl doare pe altcineva" e o proprietate a
execuției. Judecata e aici, iar `core/test_blocante_clasificate.py` cere ca **fiecare** candidat
brut să aibă verdict, regulă și motiv.

**CLASELE**, în vocabularul cerut de runda de diagnostic:

| clasă | ce înseamnă |
|---|---|
| `ACTION_REQUIRED` | calea face rău altor cereri, sau leagă o resursă rară de un capăt pe care nu-l controlăm. Intră într-un val de remediere — **care NU se execută în faza de diagnostic** |
| `ACCEPTABLE_BY_DESIGN` | calea CHIAR are I/O blocant (inventarul are dreptate), dar el nu are cui să-i facă rău: nu e pe buclă, nu e într-o cerere, sau e mărginit prin construcție |
| `FALSE_POSITIVE` | inventarul s-a înșelat, și se spune **prin ce**: omonimie, ramuri aplatizate, primitivă care nu e de fapt blocantă |

**MAPARE CĂTRE PLANUL CANONIC.** `PLAN_HARDENING.md:330-334` cere trei pași per rută: benchmark
concurent · identificarea blocajului · intervenție minimă. Clasele de aici se așază pe pasul 2:
`ACTION_REQUIRED` = blocaj identificat, cu dovadă; celelalte două = ce s-a uitat și nu e blocaj.
Pasul 3 (intervenția) e **în afara** diagnosticului, prin regula rundei.

**TREI FELURI DE DOVADĂ, și nu se amestecă:**
  * **MĂSURAT** — există o cifră pe calea reală, în `masuratori/p5/`;
  * **STRUCTURAL_NEMĂRGINIT** — forma codului spune că nu există nicio limită superioară (un apel
    fără `timeout` poate ține firul la nesfârșit). Nu se poate măsura fără un capăt care atârnă;
  * **STRUCTURAL_MĂRGINIT_DAR_RAR** — există o limită, dar e mare față de resursa pe care o ține
    (60 s de apel extern pe una din cele 10 conexiuni ale pool-ului). Aritmetică de capacitate,
    nu măsurătoare.

*Un raport care le pune sub același cuvânt („am găsit 46 de probleme") ar ascunde exact partea care
decide ordinea reparațiilor.*
"""
import io
import os

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ACTIUNE = "ACTION_REQUIRED"
ACCEPTABIL = "ACCEPTABLE_BY_DESIGN"
FALS = "FALSE_POSITIVE"
INDIVIDUAL = "INDIVIDUAL"

MASURAT = "MASURAT"
NEMARGINIT = "STRUCTURAL_NEMARGINIT"
MARGINIT_RAR = "STRUCTURAL_MARGINIT_DAR_RAR"


# ============================================================================
#  CIFRELE CITATE ÎN MOTIVE — citite din artefact, niciodată scrise de mână
#
#  Prima formă le avea bătute în text („152,6 ms"). O re-rulare a bancului le-a
#  schimbat pe toate, iar textul ar fi rămas în urmă fără ca ceva să pice —
#  adică exact «o cifră care nu se poate recalcula nu e o măsurătoare, e o
#  amintire». Acum motivele citesc din `P5_MASURATORI.json`, iar garda cere ca
#  fișierul să existe și cifrele să fie acolo.
# ============================================================================

_M = {}


def masuratori(cale=None, reincarca=False):
    """`{cheie: valoare}` — cifrele care apar în motive, luate din banc.

    `{}` dacă artefactul lipsește: modulul rămâne importabil într-un checkout proaspăt, dar
    `core/test_blocante_clasificate.py` refuză starea aia, deci nu poate trece neobservată.
    """
    import json
    if _M and not reincarca:
        return _M
    cale = cale or os.path.join(_RAD, "masuratori", "p5", "P5_MASURATORI.json")
    if not os.path.exists(cale):
        return {}
    d = json.load(io.open(cale, encoding="utf-8"))
    curba = {r["N"]: r for r in d.get("curba_async", [])}
    conc = {r["k"]: r for r in d.get("concurenta", [])}
    varf = max(curba) if curba else None
    _M.clear()
    _M.update({
        "commit": d.get("commit"),
        "N_varf": varf,
        "canar_baza_p95": (d.get("calibrare_canar", {}).get("liber") or {}).get("p95_ms"),
        "canar_varf_p95": (curba.get(varf, {}).get("canar") or {}).get("p95_ms"),
        "canar_varf_max": (curba.get(varf, {}).get("canar") or {}).get("max_ms"),
        "ruta_varf_p50": curba.get(varf, {}).get("durata_ruta_p50_ms"),
        "canar_sync_p95": (d.get("martor_sync", {}).get("canar") or {}).get("p95_ms"),
        "k_max": max(conc) if conc else None,
        "conexiuni_max": (conc.get(max(conc), {}) if conc else {}).get(
            "MAX_SIMULTANEOUS_RESOURCE_USE"),
        "capacitate_pool": (conc.get(max(conc), {}) if conc else {}).get("RESOURCE_CAPACITY"),
    })
    return _M


def _c(cheie, sufix=" ms"):
    """O cifră din banc, sau un semn vizibil că lipsește — niciodată o valoare inventată."""
    v = masuratori().get(cheie)
    return "«fără măsurătoare»" if v is None else "%s%s" % (str(v).replace(".", ","), sufix)


def _f(x):
    return x.get("fapte", {}), set(x.get("detectori", {}))


def _loc(x, feluri=None, steag=None):
    """`file:line` al primei primitive care CHIAR susține verdictul.

    Nu prima primitivă din listă: dacă regula spune „se execută pe buclă", dovada trebuie să fie o
    primitivă cu `pe_bucla`, nu prima care s-a nimerit. *O trimitere `file:line` care arată spre
    altceva decât ce afirmă motivul e mai rea decât nicio trimitere — se citește ca verificată.*
    """
    def bun(p):
        return ((feluri is None or p["fel"] in feluri)
                and (steag is None or p.get(steag)))
    for p in x.get("primitive", []):
        if bun(p):
            return p["loc"]
    for p in x.get("primitive", []):          # relaxarea se vede: fără steag, dar cu felul cerut
        if feluri is None or p["fel"] in feluri:
            return p["loc"] + " (fără steagul cerut)"
    return x.get("fisier", "?")


# ============================================================================
#  RÂNDURI INDIVIDUALE — căile care au o poveste proprie
# ============================================================================

CLASIFICARE = {
    "POST /tenants/{tenant_id}/banca/parse-extras": {
        "clasa": ACCEPTABIL,
        "dovada": "REPARAT",
        "val": None,
        "cale_absenta": True,
        "de_ce": lambda: (
            "SUBIECTUL MĂSURĂTORII, ȘI PRIMA CALE REPARATĂ — de-aia are rând propriu, și de-aia "
            "rândul rămâne după ce calea a IEȘIT din inventar. Era `async def`, deci tot ce făcea "
            "— verificarea accesului în bază și parsarea extrasului — se întâmpla PE BUCLĂ. "
            "Măsurat ÎNAINTE, cu un canar care bătea o rută ieftină în paralel: la N=%s tranzacții "
            "ruta lua %s, iar canarul — care n-avea nicio legătură cu importul — aștepta p95 %s, "
            "vârf %s, față de %s în gol. **Valul 1 (10.09.2026)** a făcut handler-ul sincron, deci "
            "Starlette îl mută pe un fir. Azi calea nu mai aprinde NICIUN detector: nu e «mai "
            "puțin gravă», a ieșit cu totul din inventarul brut. *Rândul se păstrează fiindcă o "
            "reparație ștearsă din registru arată identic cu un defect care n-a existat niciodată.*"
            % (masuratori().get("N_varf"), _c("ruta_varf_p50"), _c("canar_varf_p95"),
               _c("canar_varf_max"), _c("canar_baza_p95"))),
    },
    "main.py::lifespan()": {
        "clasa": ACCEPTABIL,
        "dovada": "PORNIRE",
        "de_ce":
            "PORNIREA aplicației, nu o cerere. Blochează bucla ÎNAINTE ca serverul să accepte "
            "cereri — deci nu există nimeni căruia să-i facă rău. E și fail-closed prin decizie "
            "scrisă (P2): dacă pregătirea schemelor eșuează, procesul NU intră în starea gata. "
            "A-l muta pe threadpool ar strica exact garanția aia. Ce rămâne adevărat, și se "
            "scrie: durata pornirii crește cu numărul de firme, iar publicarea repornește "
            "procesul — deci costul ăsta se plătește la fiecare livrare, nu o dată.",
    },
    "POST /tenants/{tenant_id}/horeca/import-amef": {
        "clasa": ACTIUNE,
        "dovada": "SERIALIZARE_ACCIDENTALA",
        "val": 1,
        "de_ce":
            "SINGURA DIN CELE 17 CARE N-A FOST MUTATĂ, și nu din scăpare. Azi, după citirea "
            "fișierului, handler-ul rulează până la capăt FĂRĂ să mai cedeze bucla — deci două "
            "cereri simultane sunt SERIALIZATE. Pe serializarea asta se sprijină, fără s-o fi "
            "declarat nimeni, poarta R61 din `_cere_z_unic`: un raport Z duplicat se REFUZĂ. Iar "
            "`inregistrari` NU are index unic pe `(sursa, numar)` — verificat în "
            "`tenant_template.sql`, unde tabela are doar cheia primară pe `id`. Mutarea pe fir ar "
            "face ca două încărcări simultane ale aceluiași Z să treacă amândouă de verificare. "
            "*O regresie de contabilitate cumpărată cu o îmbunătățire de latență nu e o "
            "îmbunătățire* — iar planul cere explicit ca semantica să nu se schimbe "
            "(PLAN_HARDENING.md:337). Costul ținerii pe loc e mic: calea parsează un XML și scrie "
            "câteva rânduri, deci e cel mai ieftin dintre cei 17 blocanți. Se deblochează în două "
            "feluri, amândouă declarate: index unic pe `(sursa, numar)`, sau "
            "`pg_advisory_xact_lock` pe cheia raportului înainte de verificare.",
    },
    "middleware main.py::_audit_middleware()": {
        "clasa": ACCEPTABIL,
        "dovada": "TIPAR_BUN",
        "de_ce":
            "NU APARE ÎN INVENTAR, și merită spus de ce: middleware-ul de audit scrie în bază la "
            "fiecare cerere, dar o face prin `run_in_threadpool`. Deci casa ȘTIE deja tiparul cerut "
            "de pasul 3 al planului, și l-a aplicat exact acolo unde costă cel mai mult — pe calea "
            "prin care trece ORICE cerere. Rândul ăsta e reperul cu care se compară restul: cele 46 "
            "de căi cu acțiune nu cer o tehnică nouă, ci una pe care casa o are deja scrisă.",
        "cale_absenta": True,
    },
}


# ============================================================================
#  REGULI PE CLASE STRUCTURALE
#
#  ORDINEA CONTEAZĂ: prima care se potrivește dă verdictul. `OMONIM` stă
#  ÎNAINTEA regulilor de acțiune, nu după — spre deosebire de P4, unde stătea
#  la coadă. Motivul e simetric și merită scris: rezolvarea pe omonimie ADAUGĂ
#  evenimente, deci la P4, unde verdictul sigur era „non-critic", supra-
#  aproximarea era inofensivă; aici verdictul sigur e „acceptabil", iar
#  evenimentele în plus ar putea produce un `ACTION_REQUIRED` fals. *Aceeași
#  proprietate a instrumentului cere ordini opuse, fiindcă direcția prudentă e
#  opusă.*
# ============================================================================

REGULI = [
    {
        "cod": "OMONIM",
        "titlu": "dovada vine numai din nume cu mai multe definiții",
        "clasa": FALS,
        "dovada": "OARBIRE",
        "cand": lambda x: bool(_f(x)[0].get("numai_omonim")),
        "de_ce": lambda x: (
            "FALS POZITIV prin OMONIMIE, oarbirea declarată în antetul scanerului: TOATE "
            "primitivele căii vin din nume rezolvate pe treapta a treia — adică din reuniunea "
            "tuturor definițiilor cu acel nume, nu dintr-una anume. Regula stă ÎNAINTEA celor de "
            "acțiune, nu după: evenimentele în plus ar putea produce o acțiune falsă, iar aici "
            "direcția prudentă e opusă celei de la P4. Prima primitivă: %s" % _loc(x)),
    },
    {
        "cod": "FUNDAL",
        "titlu": "lucrător de fundal, fără buclă și fără om care așteaptă",
        "clasa": ACCEPTABIL,
        "dovada": "FARA_BUCLA",
        "cand": lambda x: x.get("fel") == "fundal",
        "de_ce": lambda x: (
            "LUCRĂTOR DE FUNDAL, nu cerere. Rulează într-un proces propriu, fără buclă de "
            "evenimente și fără nimeni care așteaptă un răspuns; I/O blocant e acolo forma "
            "NORMALĂ, nu un defect — a-l muta pe threadpool n-ar avea pe cine să elibereze. "
            "%d primitive (%s), prima la %s. Ce rămâne totuși adevărat, și se scrie: conexiunile "
            "lui ies din ACELAȘI pool de %s ca ale cererilor, deci un lucrător lung strâmtorează "
            "cererile. Dar aia e capacitate, nu blocaj de buclă, și se măsoară altfel."
            % (_f(x)[0].get("primitive_total", 0), ", ".join(_f(x)[0].get("feluri", [])),
               _loc(x), masuratori().get("capacitate_pool"))),
    },
    {
        "cod": "C1-CERERE",
        "titlu": "I/O blocant pe bucla de evenimente, pe o cale care servește cereri",
        "clasa": ACTIUNE,
        "dovada": MASURAT,
        "val": 1,
        "cand": lambda x: "C1" in _f(x)[1],
        "de_ce": lambda x: (
            "CHIAR DEFINIȚIA CANONICĂ (PLAN_HARDENING.md:328): handler `async def`, deci %d "
            "primitive blocante (%s) se execută PE BUCLĂ. Cât ține oricare din ele, TOATE "
            "celelalte cereri stau — oricâte fire ar fi libere, fiindcă nu firele lipsesc, ci "
            "bucla e ocupată. Măsurat pe o cale din aceeași familie: la N=%s, o cerere fără nicio "
            "legătură a așteptat până la %s, față de %s linia de bază. Prima primitivă chiar de "
            "pe buclă: %s"
            % (_f(x)[0].get("pe_bucla", 0), ", ".join(_f(x)[0].get("feluri", [])),
               masuratori().get("N_varf"), _c("canar_varf_max"), _c("canar_baza_p95"),
               _loc(x, steag="pe_bucla"))),
    },
    {
        "cod": "C6-FARA-TIMEOUT",
        "titlu": "apel de rețea fără termen, pe calea unei cereri",
        "clasa": ACTIUNE,
        "dovada": NEMARGINIT,
        "val": 2,
        "cand": lambda x: "C6" in _f(x)[1],
        "de_ce": lambda x: (
            "NEMĂRGINIT PRIN CONSTRUCȚIE: %d apeluri de rețea fără `timeout`. Un capăt care nu "
            "răspunde — și nici nu închide — ține firul din threadpool și, pe căile care și-au "
            "luat conexiune, una din cele 10, la NESFÂRȘIT. Nu se poate măsura fără un capăt care "
            "atârnă, iar eu n-am chemat servicii reale; de-aia dovada e structurală, și e mai tare "
            "decât o cifră: nu există limită superioară DE măsurat. Prima primitivă fără termen: %s"
            % (_f(x)[0].get("retea_fara_timeout", 0), _loc(x, ("RETEA",)))),
    },
    {
        "cod": "C5-EXTERN-CU-CONEXIUNE",
        "titlu": "apel extern cât timp e ținută o conexiune din pool",
        "clasa": ACTIUNE,
        "dovada": MARGINIT_RAR,
        "val": 3,
        "cand": lambda x: ("C5" in _f(x)[1]
                           and bool({"RETEA", "SUBPROC"} & set(_f(x)[0].get("feluri", [])))),
        "de_ce": lambda x: (
            "MĂRGINIT, DAR PE RESURSA RARĂ: %d primitive ne-DB se execută cu o conexiune din pool "
            "ținută (%s). Pool-ul are %s conexiuni, iar apelurile externe au termene de până la 60 "
            "s — deci tot atâtea cereri simultane pe o astfel de cale pot goli pool-ul pentru TOATĂ "
            "aplicația, inclusiv pentru rute care n-au nicio treabă cu serviciul extern. Dovada e "
            "aritmetică de capacitate, NU o măsurătoare: n-am chemat serviciile reale, fiindcă ar "
            "fi fost efect în afara noastră — și regula fazei interzice asta.%s%s Prima primitivă "
            "externă ținută peste conexiune: %s"
            % (_f(x)[0].get("in_domeniu_db", 0), ", ".join(_f(x)[0].get("feluri", [])),
               masuratori().get("capacitate_pool"),
               (" AICI E MAI RĂU DECÂT ATÂT: calea ține conexiunea și peste un `sleep`, adică "
                "peste o așteptare care se produce SIGUR, nu doar dacă serviciul extern e lent."
                if "SLEEP" in _f(x)[0].get("feluri", []) else ""),
               (" TERMENUL NU SE POATE DECIDE AICI: %d apeluri primesc `timeout` prin "
                "despachetare, deci mărginirea depinde de fiecare apelant în parte, iar funcția "
                "apelată n-are termen implicit. Azi toți apelanții îl trimit — verificat rând cu "
                "rând —, dar nimic nu oprește unul viitor să nu-l trimită."
                % _f(x)[0].get("retea_timeout_prin_kw", 0)
                if _f(x)[0].get("retea_timeout_prin_kw") else ""),
               _loc(x, ("RETEA", "SUBPROC"), steag="in_domeniu_db"))),
    },
    {
        "cod": "SINCRON-MARGINIT",
        "titlu": "rută sincronă, în threadpool, cu I/O mărginit",
        "clasa": ACCEPTABIL,
        "dovada": "THREADPOOL",
        "cand": lambda x: True,
        "de_ce": lambda x: (
            "RULEAZĂ ÎN THREADPOOL, nu pe buclă: handler sincron, deci Starlette îl mută pe un fir "
            "din cele 40 ale limitatorului. Blocajul lui nu atinge bucla, deci nu atinge celelalte "
            "cereri — și asta nu e o presupunere, e martorul măsurat pe o rută sincronă care CHIAR "
            "reușește: canar p95 %s, față de %s în gol, adică plat. %d primitive (%s), prima la "
            "%s; niciuna nu ține o conexiune peste un apel extern și niciuna nu e fără termen — "
            "dacă ar fi, ar fi fost prinsă de o regulă de mai sus. Ce rămâne e capacitatea celor "
            "40 de fire, care nu s-a atins în nicio măsurătoare: la k=%s, maximul de conexiuni "
            "simultane observat a fost %s din %s."
            % (_c("canar_sync_p95"), _c("canar_baza_p95"),
               _f(x)[0].get("primitive_total", 0), ", ".join(_f(x)[0].get("feluri", [])),
               _loc(x), masuratori().get("k_max"), masuratori().get("conexiuni_max"),
               masuratori().get("capacitate_pool"))),
    },
]


# ============================================================================
#  VALUL 1 — clichet în AMBELE direcții
#
#  O listă de „reparate" fără gardă e o promisiune. Lista de mai jos e citită de
#  `core/test_blocante_clasificate.py`, care cere ca NICIUNA să nu mai aprindă
#  C1 — și, separat, ca mulțimea celor rămase pe buclă să fie exact cea scrisă.
#  *Fără a doua parte, o rută nouă `async def` cu I/O blocant ar intra tăcut.*
# ============================================================================

#: cele 16 căi mutate de pe buclă pe 10.09.2026 (valul 1)
REPARATE_VAL1 = (
    "POST /migrare/fisier",
    "POST /migrare/incarca",
    "POST /portal/bon",
    "POST /raportari/mesaj/{mid}/imagine",
    "POST /tenants/{tenant_id}/articole-import/incarca",
    "POST /tenants/{tenant_id}/asociati-import/incarca",
    "POST /tenants/{tenant_id}/banca/parse-extras",
    "POST /tenants/{tenant_id}/banca/reconciliere/import",
    "POST /tenants/{tenant_id}/import-efactura",
    "POST /tenants/{tenant_id}/istoric-declaratii-import/incarca",
    "POST /tenants/{tenant_id}/mijloace-fixe-import/incarca",
    "POST /tenants/{tenant_id}/parteneri/incarca",
    "POST /tenants/{tenant_id}/retete-import/incarca",
    "POST /tenants/{tenant_id}/rip-import/incarca",
    "POST /tenants/{tenant_id}/salariati-import/incarca",
    "POST /tenants/{tenant_id}/solduri/incarca",
)

#: ce a RĂMAS să aprindă C1, cu motivul fiecăreia. Mulțimea e pinată: și o intrare
#: în plus, și una în minus, pică. O listă goală ar fi o minciună; una nescrisă, la fel.
RAMASE_PE_BUCLA = {
    "POST /tenants/{tenant_id}/horeca/import-amef":
        "ținută pe loc DELIBERAT: bucla îi serializează azi verificarea de unicitate a raportului "
        "Z, iar baza n-are index unic care s-o înlocuiască — v. rândul ei individual",
    "main.py::lifespan()":
        "pornirea aplicației, nu o cerere: blochează bucla ÎNAINTE ca serverul să accepte cereri, "
        "deci n-are cui să facă rău, și e fail-closed prin decizie scrisă la P2",
}


def verdict(x, clasificare=None, reguli=None):
    """`{clasa, regula, de_ce, dovada, val}` — sau `None` dacă nimic nu acoperă candidatul."""
    clasificare = CLASIFICARE if clasificare is None else clasificare
    reguli = REGULI if reguli is None else reguli
    rand = clasificare.get(x.get("intrare"))
    if rand:
        de_ce = rand["de_ce"]
        return {"clasa": rand["clasa"], "regula": INDIVIDUAL,
                "de_ce": de_ce() if callable(de_ce) else de_ce,
                "dovada": rand.get("dovada", "-"), "val": rand.get("val")}
    for r in reguli:
        try:
            if r["cand"](x):
                return {"clasa": r["clasa"], "regula": r["cod"], "de_ce": r["de_ce"](x),
                        "dovada": r.get("dovada", "-"), "val": r.get("val")}
        except Exception:
            continue
    return None


def clasifica(inv, clasificare=None, reguli=None):
    verdicte, neclasificate = [], []
    for x in inv:
        v = verdict(x, clasificare, reguli)
        if v is None:
            neclasificate.append(x.get("intrare"))
        else:
            verdicte.append((x.get("intrare"), v))
    return verdicte, neclasificate


def excluderi_toate(inv, clasificare=None, reguli=None):
    """`{intrare: de_ce}` pentru fiecare candidat care NU e `ACTION_REQUIRED`."""
    out = {}
    for x in inv:
        v = verdict(x, clasificare, reguli)
        if v is not None and v["clasa"] != ACTIUNE:
            out[x.get("intrare")] = v.get("de_ce")
    return out


def numaratori(inv, clasificare=None, reguli=None):
    """Blocul de cifre al diagnosticului, derivat — nu scris."""
    verdicte, neclasificate = clasifica(inv, clasificare, reguli)
    pe_clasa, pe_regula, pe_dovada, pe_val = {}, {}, {}, {}
    for _i, v in verdicte:
        pe_clasa[v["clasa"]] = pe_clasa.get(v["clasa"], 0) + 1
        pe_regula[v["regula"]] = pe_regula.get(v["regula"], 0) + 1
        pe_dovada[v["dovada"]] = pe_dovada.get(v["dovada"], 0) + 1
        if v["clasa"] == ACTIUNE:
            pe_val[v.get("val") or "?"] = pe_val.get(v.get("val") or "?", 0) + 1
    excl = excluderi_toate(inv, clasificare, reguli)
    nemotivate = sorted(k for k, m in excl.items()
                        if not isinstance(m, str) or len(m.strip()) < 80)
    suma = (pe_clasa.get(ACTIUNE, 0) + pe_clasa.get(ACCEPTABIL, 0) + pe_clasa.get(FALS, 0))
    return {
        "RAW_CANDIDATES": len(inv),
        "CLASSIFIED_CANDIDATES": len(verdicte),
        "UNCLASSIFIED_RAW_CANDIDATES": len(neclasificate),
        "neclasificate": neclasificate,
        "ACTION_REQUIRED": pe_clasa.get(ACTIUNE, 0),
        "ACCEPTABLE_BY_DESIGN": pe_clasa.get(ACCEPTABIL, 0),
        "FALSE_POSITIVES": pe_clasa.get(FALS, 0),
        "RAW_CLASS_SUM": suma,
        "RAW_CLASS_ACCOUNTING": ("PASS" if (suma == len(verdicte) == len(inv)
                                            and not neclasificate) else "FAIL"),
        "EXCLUSIONS_TOTAL": len(excl),
        "UNEXPLAINED_EXCLUSIONS": len(nemotivate),
        "nemotivate": nemotivate,
        "pe_regula": pe_regula,
        "pe_dovada": pe_dovada,
        "valuri": pe_val,
    }


def randuri_fara_cale():
    """Rândurile individuale care descriu o cale care NU e în inventar — declarate ca atare."""
    return [k for k, v in CLASIFICARE.items() if v.get("cale_absenta")]


def citeste_inventar(cale=None):
    """Inventarul brut, din artefactul generat. `None` dacă n-a fost produs încă."""
    import json
    cale = cale or os.path.join(_RAD, "masuratori", "p5", "P5_INVENTAR_BRUT.json")
    if not os.path.exists(cale):
        return None
    return json.load(io.open(cale, encoding="utf-8"))
