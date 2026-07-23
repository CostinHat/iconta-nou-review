# -*- coding: utf-8 -*-
"""
core/audit_preluare.py — F183: audit de PRELUARE firma.

Cand un cabinet preia o firma cu istoric de la alt contabil, importa un PACHET de documente
(balanta de deschidere, solduri pe parteneri, istoric declaratii depuse, iar la PFA registrul
de incasari-plati). Acest modul verifica COERENTA INTERNA a pachetului si raporteaza transparent
CE se poate / NU se poate verifica. Acoperire profesionala la preluarea raspunderii.

DE CE motor SEPARAT de control_incrucisat (nu un apel al lui):
  control_incrucisat compara doua surse INTERNE iConta - o declaratie GENERATA din iConta vs NOTE
  VALIDATE in iConta. La preluare NICIUNA nu exista inca: contabilitatea in iConta incepe DUPA
  preluare, iar facturile istorice nu-s in sistem. Ruland control_incrucisat pe luna preluata,
  rulaje_luna intoarce zero -> rosu fals "necontabilizat" pe tot. La preluare ambele surse sunt
  EXTERNE (documente de la contabilul anterior); intrebarea nu e "declarat vs contabilizat" ci
  "pachetul preluat e coerent cu el insusi?". Motoare separate care se cheama, nu se absorb
  (DECIZII 18.07 B).

REUTILIZEAZA anatomia control_incrucisat (nu logica): TREI stari - verde=COERENT / rosu=DIVERGENT /
gri=NEVERIFICAT (lipseste documentul). Fiecare constatare cu TEMEI si remediu in trei feluri
(executabil/sugerat/investigatie). "Gri e informatie, nu absenta": pe masura ce apar documentele,
gri-urile trec in verde/rosu -> raportul e REPETABIL (datat cu momentul rularii, de catre apelant).

REUTILIZEAZA cod existent (regula "nu construi paralel"):
  - solduri_api.verifica_echilibru  (echilibru balanta de deschidere, PURA)
  - solduri_parteneri_api.coerenta  (Sigma parteneri pe sintetic vs sold balanta)
  - pdf_util.bani                   (format monetar romanesc canonic 1.234,56 - DS cap.7)

SCOP v1 (DA gate 22.07.2026): balanta (echilibru) + solduri parteneri (Sigma=sold) + istoric
declaratii vs solduri fiscale + PFA/RIP (coerenta interna registru). Acopera ambele regimuri:
partida dubla (SRL) si partida simpla (PFA). NEVERIFICAT v1 (ramane vizibil gri prin lipsa checkului,
nu tacut): asociati/cote, mijloace fixe, salariati, vector fiscal vs documente.
"""
from decimal import Decimal
from core.pdf_util import bani

MODUL = "audit_preluare"
REGULI = "2026.1"
TOLERANTA = Decimal("0.01")


def _d(v):
    return Decimal(str(v or 0))


def _lei(x):
    """Suma in format romanesc canonic + ' lei' (1.234,56 lei). Sursa unica: pdf_util.bani (DS cap.7)."""
    return bani(x, "lei")


# Conturi de datorii/creante fiscale la deschidere -> declaratia care le explica. Un sold preluat
# pe aceste conturi FARA declaratia corespunzatoare in istoricul importat = SEMNAL (gri, nu rosu:
# soldurile fiscale au cauze legitime -> remediu investigatie, nu acuzatie mecanica).
# Ramificare pe regim a TEXTELOR limitei (STRATURI_META are doar (strat, regim), NU textele -> aici
# e maparea text<->strat care lipseste; regimul insusi vine din straturi_pentru, NU se dubleaza).
# _VERIFICAT_DESC: ce verifica auditul, pe stratul de care depinde (istoric-fiscal cere balanta=solduri).
_VERIFICAT_DESC = (
    ("solduri",           "echilibru balanță"),
    ("solduri_parteneri", "defalcare parteneri vs sintetic"),
    ("solduri",           "solduri fiscale vs istoric declarații"),
    ("rip",               "coerența registrului de încasări-plăți (sold implicit din Σ încasări − Σ plăți)"),
)
# _NEVERIFICAT_V1: straturi cu verificare NEIMPLEMENTATA in v1 (raman gri vizibil), cu textul lor.
_NEVERIFICAT_V1 = (
    ("asociați/cote",              "asociati"),
    ("mijloace fixe",              "mijloace_fixe"),
    ("salariați",                  "salariati"),
    ("vector fiscal vs documente", "vector_fiscal"),
)

# [tip_lowercase] decl = CHEIE de join (canonic lowercase, ca declaratii_depuse.tip); upper la display.
CONT_DECL_FISCAL = (
    ("4423", "d300", "TVA de plată"),
    ("4424", "d300", "TVA de recuperat"),
    ("444",  "d112", "impozit pe venituri din salarii"),
    ("4315", "d112", "CAS"),
    ("4316", "d112", "CASS"),
    ("436",  "d112", "contribuția asiguratorie pentru muncă"),
    ("4411", "d101", "impozit pe profit"),
    ("441",  "d101", "impozit pe profit"),
)


# ---- constructori de constatare (anatomia control_incrucisat: stare + temei + mesaj + remediu) ----

def _c(stare, eticheta, temei, mesaj, remediu=None):
    return {"stare": stare, "eticheta": eticheta, "temei": temei, "mesaj": mesaj, "remediu": remediu}


def _verde(et, temei, mesaj):
    return _c("verde", et, temei, mesaj, None)


def _gri(et, temei, mesaj, actiune, cauza="Lipsește un document necesar verificării."):
    return _c("gri", et, temei, mesaj,
              {"fel": "investigatie", "cauza": cauza, "actiune": actiune, "facturi": []})


def _rosu(et, temei, mesaj, cauza, actiune, fel="investigatie"):
    return _c("rosu", et, temei, mesaj,
              {"fel": fel, "cauza": cauza, "actiune": actiune, "facturi": []})


def _rows_solduri_initiale(conn, schema):
    """[{cont, debit, credit}] din solduri_initiale, sau None daca balanta nu a fost importata."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".solduri_initiale",))
        if cur.fetchone()[0] is None:
            return None
        cur.execute(f"SELECT cont, sold_debitor, sold_creditor FROM {schema}.solduri_initiale")
        return [{"cont": c, "debit": sd, "credit": sc} for c, sd, sc in cur.fetchall()]


# ---- verificarile (fiecare intoarce o LISTA de constatari; lista goala = nu se aplica regimului) ----

def verifica_balanta(conn, schema):
    """Balanta de deschidere se echilibreaza (debit=credit). Reutilizeaza solduri_api.verifica_echilibru."""
    from core.solduri_api import verifica_echilibru
    et = "Balanța de deschidere"
    temei = ("Balanța de deschidere trebuie să aibă totalul debitor egal cu cel creditor "
             "(solduri_initiale). O balanță dezechilibrată face toată contabilitatea preluată "
             "să pornească greșit.")
    rows = _rows_solduri_initiale(conn, schema)
    if rows is None:
        return [_gri(et, temei,
                     "Balanța de deschidere nu a fost importată — nu pot verifica echilibrul.",
                     "Importă balanța de deschidere (Migrare › Solduri inițiale), apoi reia auditul.")]
    if not rows:
        return [_gri(et, temei, "Balanța de deschidere e goală — nu pot verifica echilibrul.",
                     "Importă o balanță cu conturi, apoi reia auditul.")]
    ok, td, tc, dif = verifica_echilibru(rows)
    if ok:
        return [_verde(et, temei, f"Balanța de deschidere se echilibrează ({_lei(td)}).")]
    return [_rosu(et, temei,
                  f"Balanța: debit {_lei(td)}, credit {_lei(tc)} (diferență {_lei(dif)}).",
                  cauza="Totalul debitor diferă de cel creditor.",
                  actiune=("Verifică exportul balanței de la contabilul anterior: conturi omise, "
                           "sold pe cont greșit, rânduri de total incluse din greșeală. Reimportă "
                           "balanța corectă (Migrare › Solduri inițiale)."))]


def verifica_parteneri(conn, schema):
    """Sigma solduri parteneri pe sintetic (4111/401) = sold sintetic din balanta.
    Reutilizeaza solduri_parteneri_api.coerenta (search_path e pe schema prin SET LOCAL)."""
    from core.solduri_parteneri_api import coerenta
    et = "Solduri parteneri vs balanță"
    temei = ("Suma soldurilor pe parteneri (4111 clienți, 401 furnizori) trebuie să egaleze soldul "
             "sinteticului din balanța de deschidere. Defalcarea pe partener nu poate depăși sau rata "
             "totalul din balanță.")
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".solduri_parteneri",))
        if cur.fetchone()[0] is None:
            return [_gri(et, temei,
                         "Soldurile pe parteneri nu au fost importate — nu pot verifica defalcarea.",
                         "Importă soldurile pe parteneri (Migrare › Solduri parteneri), apoi reia auditul.")]
        cur.execute(f"SELECT cont, sold_debitor, sold_creditor FROM {schema}.solduri_parteneri")
        randuri = [{"cont": c, "debit": sd, "credit": sc} for c, sd, sc in cur.fetchall()]
    if not randuri:
        return [_gri(et, temei, "Nu există solduri pe parteneri de verificat.",
                     "Importă soldurile pe parteneri (Migrare › Solduri parteneri), apoi reia auditul.")]
    return constatare_parteneri(coerenta(conn, randuri))


def constatare_parteneri(rez_coerenta):
    """PURA (fara DB): din rezultatul solduri_parteneri_api.coerenta [{cont, suma_parteneri,
    sold_balanta, diferenta, coincide}], produce constatari. coincide=None -> gri (balanta nu are
    sinteticul); True -> verde; False -> rosu (defalcare != sold)."""
    et = "Solduri parteneri vs balanță"
    temei = ("Suma soldurilor pe parteneri (4111 clienți, 401 furnizori) trebuie să egaleze soldul "
             "sinteticului din balanța de deschidere. Defalcarea pe partener nu poate depăși sau rata "
             "totalul din balanță.")
    out = []
    for r in rez_coerenta:
        cont = r["cont"]
        if r["coincide"] is None:
            out.append(_gri(et, temei,
                            f"Contul {cont}: parteneri {_lei(r['suma_parteneri'])}, dar balanța nu are "
                            f"acest sold — nu pot compara.",
                            "Importă balanța de deschidere care conține contul, apoi reia."))
        elif r["coincide"]:
            out.append(_verde(et, temei,
                              f"Contul {cont}: defalcarea pe parteneri ({_lei(r['suma_parteneri'])}) "
                              f"coincide cu balanța."))
        else:
            out.append(_rosu(et, temei,
                             f"Contul {cont}: parteneri {_lei(r['suma_parteneri'])} vs balanță "
                             f"{_lei(r['sold_balanta'])} (diferență {_lei(r['diferenta'])}).",
                             cauza="Suma partenerilor nu egalează soldul sintetic din balanță.",
                             actiune=("Verifică: partener omis din defalcare, sold pe cont greșit, sau "
                                      "balanța și defalcarea preluate din momente diferite.")))
    return out


def verifica_istoric_fiscal(conn, schema, tenant_id, conn_public):
    """Solduri de deschidere pe conturi fiscale <-> istoricul declaratiilor importat. Doar SEMNAL (gri):
    un sold fiscal fara declaratia care-l explica in istoric merita verificat, nu e rosu automat."""
    et = "Istoric declarații vs solduri fiscale"
    temei = ("Un sold de deschidere pe un cont de datorie/creanță fiscală provine dintr-o declarație "
             "depusă anterior. La preluare, un sold fără declarația care-l explică în istoricul importat "
             "e un semnal de verificat — nu o certitudine (soldurile fiscale au cauze legitime).")
    rows = _rows_solduri_initiale(conn, schema)
    if rows is None:
        return [_gri(et, temei,
                     "Balanța de deschidere nu a fost importată — nu pot lega soldurile fiscale de istoric.",
                     "Importă balanța de deschidere (Migrare › Solduri inițiale), apoi reia.")]
    with conn_public.cursor() as cur:
        cur.execute("SELECT DISTINCT tip FROM public.declaratii_depuse_curente WHERE tenant_id=%s", (tenant_id,))  # [F163v2] pe vedere (DISTINCT tip e agnostic la versiuni, dar consistent)
        tipuri_depuse = {r[0] for r in cur.fetchall()}
    net = {}
    for r in rows:
        net[r["cont"]] = net.get(r["cont"], Decimal("0")) + _d(r["debit"]) - _d(r["credit"])
    return constatare_istoric_fiscal(net, tipuri_depuse)


def constatare_istoric_fiscal(net, tipuri_depuse):
    """PURA (fara DB): din soldurile nete pe cont {cont: Decimal} si tipurile de declaratii din istoric
    (set), produce SEMNALE gri. Un sold fiscal fara declaratia care-l explica in istoric -> gri (nu rosu:
    soldurile fiscale au cauze legitime). Fara istoric deloc -> gri (nu pot confirma). Cu istoric si fara
    nepotrivire -> verde."""
    et = "Istoric declarații vs solduri fiscale"
    temei = ("Un sold de deschidere pe un cont de datorie/creanță fiscală provine dintr-o declarație "
             "depusă anterior. La preluare, un sold fără declarația care-l explică în istoricul importat "
             "e un semnal de verificat — nu o certitudine (soldurile fiscale au cauze legitime).")
    out = []
    if not tipuri_depuse:
        out.append(_gri(et, temei,
                        "Istoricul declarațiilor nu a fost importat — nu pot confirma ce s-a depus înainte "
                        "de preluare.",
                        "Importă istoricul declarațiilor (Migrare › Istoric declarații), apoi reia."))
    for cont, decl, denum in CONT_DECL_FISCAL:
        sold = abs(_d(net.get(cont, 0)))
        if sold <= TOLERANTA or decl in tipuri_depuse:
            continue
        _D = decl.upper()   # upper DOAR la randare (decl e cheie lowercase)
        out.append(_gri(et, temei,
                        f"Sold de deschidere pe {cont} ({denum}, {_lei(sold)}) fără {_D} în istoricul importat.",
                        f"Verifică dacă {_D} a fost depusă înainte de preluare și importă-o în istoric, "
                        f"sau confirmă că soldul are altă natură.",
                        cauza=f"Soldul pe {cont} sugerează o obligație {_D} anterioară care nu apare în "
                              f"istoricul preluat."))
    if not out and tipuri_depuse:
        out.append(_verde(et, temei,
                          f"Soldurile fiscale de deschidere au acoperire în istoricul declarațiilor "
                          f"importat ({', '.join(sorted(t.upper() for t in tipuri_depuse))})."))
    return out


def verifica_rip(conn, schema):
    """PFA (partida simpla): coerenta interna a registrului de incasari-plati preluat. Tabel absent
    -> lista goala (nu e PFA cu strat RIP). Tabel prezent dar ZERO operatiuni validate -> GRI cu temei
    explicit (nu raport gol: fiecare verdict poarta motivatia, inclusiv griul)."""
    et = "Registru încasări-plăți (PFA)"
    temei = ("La partida simplă nu există balanță: registrul e cronologic, iar soldul e implicit din "
             "Σ încasări − Σ plăți. Coerența internă = sold implicit ne-negativ + operațiuni "
             "clasificate fiscal.")
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".rip_operatiuni",))
        if cur.fetchone()[0] is None:
            return []
        cur.execute(f"""SELECT
              COALESCE(SUM(suma) FILTER (WHERE tip='incasare'),0),
              COALESCE(SUM(suma) FILTER (WHERE tip='plata'),0),
              COUNT(*),
              COUNT(*) FILTER (WHERE categorie='neclasificat')
            FROM {schema}.rip_operatiuni WHERE status='validata'""")
        inc, plati, n, neclas = cur.fetchone()
    if not n:
        return [_gri(et, temei,
                     "Registrul de încasări-plăți nu are nicio operațiune validată — nu pot verifica coerența.",
                     "Importă registrul (Migrare › RIP) sau introdu operațiuni și validează-le, apoi reia auditul.",
                     cauza="Fără operațiuni RIP validate la partidă simplă nu există ce corela.")]
    return constatare_rip(inc, plati, n, neclas)


def constatare_rip(inc, plati, n_total, n_neclasificat):
    """PURA (fara DB): coerenta registrului RIP preluat. Sold implicit = Sigma incasari - Sigma plati;
    negativ -> rosu (semnal). Operatiuni neclasificate -> gri (reclasificare). n_total=0 se trateaza in
    apelant (lista goala = firma nu e PFA cu RIP)."""
    et = "Registru încasări-plăți (PFA)"
    temei = ("La partida simplă nu există balanță: registrul e cronologic, iar soldul e implicit din "
             "Σ încasări − Σ plăți. Coerența internă = sold implicit ne-negativ + operațiuni "
             "clasificate fiscal.")
    sold = _d(inc) - _d(plati)
    out = []
    if sold < -TOLERANTA:
        out.append(_rosu(et, temei,
                         f"Registru: încasări {_lei(inc)}, plăți {_lei(plati)}, sold implicit "
                         f"{_lei(sold)} ({n_total} operațiuni).",
                         cauza="Soldul implicit al registrului preluat e negativ (plăți > încasări cumulat).",
                         actiune=("Verifică registrul de la contabilul anterior: operațiuni de încasare "
                                  "omise, sume sau tip greșite, sold de report neinclus.")))
    else:
        out.append(_verde(et, temei,
                          f"Registrul preluat e coerent: încasări {_lei(inc)}, plăți {_lei(plati)}, "
                          f"sold implicit {_lei(sold)} ne-negativ ({n_total} operațiuni)."))
    if n_neclasificat:
        out.append(_gri(et, temei,
                        f"{n_neclasificat} din {n_total} operațiuni sunt „neclasificat” — categoria fiscală lipsește.",
                        "Reclasifică operațiunile în ecranul RIP (activitate / cheltuială deductibilă / limitată).",
                        cauza="Operațiuni preluate fără categorie fiscală (necesară la D212 / registru)."))
    return out


def _tip_firma(conn, schema):
    """tip_firma din firma_profil ('srl'/'pfa'/...) sau None daca firma_profil / coloana tip_firma LIPSESTE
    (schema veche) -> tratat ca 'srl' de straturi_pentru (default legitim). Existenta tabelului/coloanei se
    PROBEAZA (to_regclass + information_schema), nu prin except - ca sa NU inghitim o eroare reala de DB drept
    'absenta'. Orice eroare reala PROPAGA; audit() o trateaza ca regim NEDETERMINABIL (gri + straturi sarite),
    nu ca absenta tacuta care ingusteaza auditul. Vezi DECIZII 23.07."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".firma_profil",))
        if cur.fetchone()[0] is None:
            return None                                   # tabel absent -> SRL default (legitim)
        cur.execute("SELECT 1 FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='firma_profil' AND column_name='tip_firma'", (schema,))
        if cur.fetchone() is None:
            return None                                   # coloana absenta (schema veche) -> SRL default (legitim)
        cur.execute(f"SELECT tip_firma FROM {schema}.firma_profil LIMIT 1")
        row = cur.fetchone()
        return row[0] if row else None


def _audit_regim_nedeterminat(e):
    """Regim (SRL/PFA) NEDETERMINABIL dintr-o EROARE (nu absenta legitima): auditul NU ghiceste SRL tacit.
    Un audit care sare peste jumatate din verificari fara sa spuna e mai grav decat unul care crapa vizibil
    -> gri cu temei + lista straturilor nerulate (ambele regimuri). Vezi DECIZII 23.07."""
    from core.migrare_api import straturi_pentru
    toate = set(straturi_pentru("srl")) | set(straturi_pentru("pfa"))
    sarite = [d for s, d in _VERIFICAT_DESC if s in toate]
    return {"stare": "gri",
            "constatari": [_gri("regim nedeterminabil",
                "Auditul aplica straturi diferite dupa regim (SRL partida dubla / PFA partida simpla); fara "
                "regim nu stiu care se aplica, deci nu pot rula auditul complet.",
                "Nu am putut determina regimul firmei (SRL/PFA) — audit INCOMPLET, %d straturi nerulate." % len(sarite),
                "Verifica firma_profil.tip_firma (SRL/PFA), apoi reia auditul.",
                cauza="Nu pot citi tip_firma din firma_profil (%s)." % e)],
            "coerent": 0, "divergent": 0, "neverificat": 1,
            "limita": ("Audit NErulat: regimul (SRL/PFA) nu s-a putut determina. Straturi nerulate: %s. "
                       "Lipsa lor e vizibila prin gri, nu tacuta." % ", ".join(sarite)),
            "modul": MODUL, "reguli": REGULI}


def audit(conn, schema, tenant_id, conn_public):
    """Orchestrator F183: ruleaza verificarile APLICABILE REGIMULUI si grupeaza pe cele TREI categorii.
    Regimul (partida dubla SRL vs simpla PFA) vine din migrare_api.straturi_pentru(tip_firma) - SURSA
    UNICA a ce strat se aplica carui regim, NU se dubleaza aici. Legatura audit->strat: balanta<->solduri,
    parteneri<->solduri_parteneri, istoric-fiscal<->solduri (nevoie de balanta de deschidere), rip<->rip.
    La PFA (fara balanta prin definitie) verificarile de partida dubla NU apar - un gri "importa balanta"
    ar fi remediu IMPOSIBIL (partida simpla n-are balanta), incalcand contractul temei/limita/remediu.
    `conn` pe schema (SET LOCAL search_path); `conn_public` pe public. Data o pune apelantul (datat, acum).
    Un check care crapa nu doboara restul -> gri cu cauza (izolare, ca _incrucisat din main.py)."""
    from core.migrare_api import straturi_pentru
    try:
        tip = _tip_firma(conn, schema)
    except Exception as e:
        # regim NEDETERMINABIL (eroare reala, nu absenta) -> nu ghicim SRL tacit; gri + straturi sarite.
        return _audit_regim_nedeterminat(e)
    straturi = set(straturi_pentru(tip))
    plan = []
    if "solduri" in straturi:  # partida dubla (SRL): balanta + parteneri + istoric-vs-solduri-fiscale
        plan += [(verifica_balanta, (conn, schema)),
                 (verifica_parteneri, (conn, schema)),
                 (verifica_istoric_fiscal, (conn, schema, tenant_id, conn_public))]
    if "rip" in straturi:      # partida simpla (PFA): coerenta registrului
        plan.append((verifica_rip, (conn, schema)))
    constatari = []
    for fn, args in plan:
        try:
            constatari += fn(*args)
        except Exception as e:  # izolare: un check picat nu ascunde restul
            constatari.append(_gri(fn.__name__, "Verificarea nu a rulat.",
                                    f"NU pot rula verificarea ({e}).",
                                    "Reîncearcă; dacă persistă, verifică datele preluate ale firmei.",
                                    cauza="Eroare la verificare."))
    coerent = [c for c in constatari if c["stare"] == "verde"]
    divergent = [c for c in constatari if c["stare"] == "rosu"]
    neverificat = [c for c in constatari if c["stare"] == "gri"]
    stare = "rosu" if divergent else ("gri" if neverificat else ("verde" if coerent else "gri"))
    return {"stare": stare, "constatari": constatari,
            "coerent": len(coerent), "divergent": len(divergent), "neverificat": len(neverificat),
            "limita": limita_pe_regim(straturi), "modul": MODUL, "reguli": REGULI}


def limita_pe_regim(straturi):
    """PURA. Textul `limita` RAMIFICAT pe regim, din setul de straturi (straturi_pentru) - PFA nu vede
    termeni de partida dubla (balanta/parteneri/asociati/mij.fixe), SRL nu vede RIP. Reutilizeaza
    mecanismul de regim existent (straturi), nu construieste altul; textele vin din _VERIFICAT_DESC /
    _NEVERIFICAT_V1 (STRATURI_META n-are texte, doar (strat, regim))."""
    straturi = set(straturi)
    regim_lbl = "partidă dublă (SRL)" if "solduri" in straturi else "partidă simplă (PFA)"
    verificat = [d for s, d in _VERIFICAT_DESC if s in straturi]
    neverif = [t for t, s in _NEVERIFICAT_V1 if s in straturi]
    limita = "Verificat (%s): %s." % (regim_lbl, ", ".join(verificat) if verificat else "—")
    if neverif:
        limita += (" NEVERIFICAT (v1): %s — lipsa lor rămâne vizibilă prin gri, nu tăcută."
                   % ", ".join(neverif))
    limita += " Auditul verifică coerența INTERNĂ a pachetului preluat, NU corectitudinea evidenței contabilului anterior."
    return limita
