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

SCOP v1 (DA gate 22.07.2026): balanta (echilibru) + solduri parteneri (Sigma=sold) + istoric
declaratii vs solduri fiscale + PFA/RIP (coerenta interna registru). Acopera ambele regimuri:
partida dubla (SRL) si partida simpla (PFA). NEVERIFICAT v1 (ramane vizibil gri prin lipsa checkului,
nu tacut): asociati/cote, mijloace fixe, salariati, vector fiscal vs documente.
"""
from decimal import Decimal

MODUL = "audit_preluare"
REGULI = "2026.1"
TOLERANTA = Decimal("0.01")


def _d(v):
    return Decimal(str(v or 0))


# Conturi de datorii/creante fiscale la deschidere -> declaratia care le explica. Un sold preluat
# pe aceste conturi FARA declaratia corespunzatoare in istoricul importat = SEMNAL (gri, nu rosu:
# soldurile fiscale au cauze legitime -> remediu investigatie, nu acuzatie mecanica).
CONT_DECL_FISCAL = (
    ("4423", "D300", "TVA de plata"),
    ("4424", "D300", "TVA de recuperat"),
    ("444",  "D112", "impozit pe venituri din salarii"),
    ("4315", "D112", "CAS"),
    ("4316", "D112", "CASS"),
    ("436",  "D112", "contributia asiguratorie pentru munca"),
    ("4411", "D101", "impozit pe profit"),
    ("441",  "D101", "impozit pe profit"),
)


# ---- constructori de constatare (anatomia control_incrucisat: stare + temei + mesaj + remediu) ----

def _c(stare, eticheta, temei, mesaj, remediu=None):
    return {"stare": stare, "eticheta": eticheta, "temei": temei, "mesaj": mesaj, "remediu": remediu}


def _verde(et, temei, mesaj):
    return _c("verde", et, temei, mesaj, None)


def _gri(et, temei, mesaj, actiune, cauza="Lipseste un document necesar verificarii."):
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
    et = "Balanta de deschidere"
    temei = ("Balanta de deschidere trebuie sa aiba totalul debitor egal cu cel creditor "
             "(solduri_initiale). O balanta dezechilibrata face toata contabilitatea preluata "
             "sa porneasca gresit.")
    rows = _rows_solduri_initiale(conn, schema)
    if rows is None:
        return [_gri(et, temei,
                     "Balanta de deschidere nu a fost importata - nu pot verifica echilibrul.",
                     "Importa balanta de deschidere (Migrare > Solduri initiale), apoi reia auditul.")]
    if not rows:
        return [_gri(et, temei, "Balanta de deschidere e goala - nu pot verifica echilibrul.",
                     "Importa o balanta cu conturi, apoi reia auditul.")]
    ok, td, tc, dif = verifica_echilibru(rows)
    if ok:
        return [_verde(et, temei, f"Balanta de deschidere se echilibreaza ({td:.2f} lei).")]
    return [_rosu(et, temei,
                  f"Balanta: debit {td:.2f} lei, credit {tc:.2f} lei (diferenta {dif:.2f} lei).",
                  cauza="Totalul debitor difera de cel creditor.",
                  actiune=("Verifica exportul balantei de la contabilul anterior: conturi omise, "
                           "sold pe cont gresit, randuri de total incluse din greseala. Reimporta "
                           "balanta corecta (Migrare > Solduri initiale)."))]


def verifica_parteneri(conn, schema):
    """Sigma solduri parteneri pe sintetic (4111/401) = sold sintetic din balanta.
    Reutilizeaza solduri_parteneri_api.coerenta (search_path e pe schema prin SET LOCAL)."""
    from core.solduri_parteneri_api import coerenta
    et = "Solduri parteneri vs balanta"
    temei = ("Suma soldurilor pe parteneri (4111 clienti, 401 furnizori) trebuie sa egaleze soldul "
             "sinteticului din balanta de deschidere. Defalcarea pe partener nu poate depasi sau rata "
             "totalul din balanta.")
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".solduri_parteneri",))
        if cur.fetchone()[0] is None:
            return [_gri(et, temei,
                         "Soldurile pe parteneri nu au fost importate - nu pot verifica defalcarea.",
                         "Importa soldurile pe parteneri (Migrare > Solduri parteneri), apoi reia auditul.")]
        cur.execute(f"SELECT cont, sold_debitor, sold_creditor FROM {schema}.solduri_parteneri")
        randuri = [{"cont": c, "debit": sd, "credit": sc} for c, sd, sc in cur.fetchall()]
    if not randuri:
        return [_gri(et, temei, "Nu exista solduri pe parteneri de verificat.",
                     "Importa soldurile pe parteneri (Migrare > Solduri parteneri), apoi reia auditul.")]
    return constatare_parteneri(coerenta(conn, randuri))


def constatare_parteneri(rez_coerenta):
    """PURA (fara DB): din rezultatul solduri_parteneri_api.coerenta [{cont, suma_parteneri,
    sold_balanta, diferenta, coincide}], produce constatari. coincide=None -> gri (balanta nu are
    sinteticul); True -> verde; False -> rosu (defalcare != sold)."""
    et = "Solduri parteneri vs balanta"
    temei = ("Suma soldurilor pe parteneri (4111 clienti, 401 furnizori) trebuie sa egaleze soldul "
             "sinteticului din balanta de deschidere. Defalcarea pe partener nu poate depasi sau rata "
             "totalul din balanta.")
    out = []
    for r in rez_coerenta:
        cont = r["cont"]
        if r["coincide"] is None:
            out.append(_gri(et, temei,
                            f"Contul {cont}: parteneri {r['suma_parteneri']:.2f} lei, dar balanta nu are "
                            f"acest sold - nu pot compara.",
                            "Importa balanta de deschidere care contine contul, apoi reia."))
        elif r["coincide"]:
            out.append(_verde(et, temei,
                              f"Contul {cont}: defalcarea pe parteneri ({r['suma_parteneri']:.2f} lei) "
                              f"coincide cu balanta."))
        else:
            out.append(_rosu(et, temei,
                             f"Contul {cont}: parteneri {r['suma_parteneri']:.2f} lei vs balanta "
                             f"{r['sold_balanta']:.2f} lei (diferenta {r['diferenta']:.2f} lei).",
                             cauza="Suma partenerilor nu egaleaza soldul sintetic din balanta.",
                             actiune=("Verifica: partener omis din defalcare, sold pe cont gresit, sau "
                                      "balanta si defalcarea preluate din momente diferite.")))
    return out


def verifica_istoric_fiscal(conn, schema, tenant_id, conn_public):
    """Solduri de deschidere pe conturi fiscale <-> istoricul declaratiilor importat. Doar SEMNAL (gri):
    un sold fiscal fara declaratia care-l explica in istoric merita verificat, nu e rosu automat."""
    et = "Istoric declaratii vs solduri fiscale"
    temei = ("Un sold de deschidere pe un cont de datorie/creanta fiscala provine dintr-o declaratie "
             "depusa anterior. La preluare, un sold fara declaratia care-l explica in istoricul importat "
             "e un semnal de verificat - nu o certitudine (soldurile fiscale au cauze legitime).")
    rows = _rows_solduri_initiale(conn, schema)
    if rows is None:
        return [_gri(et, temei,
                     "Balanta de deschidere nu a fost importata - nu pot lega soldurile fiscale de istoric.",
                     "Importa balanta de deschidere (Migrare > Solduri initiale), apoi reia.")]
    with conn_public.cursor() as cur:
        cur.execute("SELECT DISTINCT tip FROM public.declaratii_depuse WHERE tenant_id=%s", (tenant_id,))
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
    et = "Istoric declaratii vs solduri fiscale"
    temei = ("Un sold de deschidere pe un cont de datorie/creanta fiscala provine dintr-o declaratie "
             "depusa anterior. La preluare, un sold fara declaratia care-l explica in istoricul importat "
             "e un semnal de verificat - nu o certitudine (soldurile fiscale au cauze legitime).")
    out = []
    if not tipuri_depuse:
        out.append(_gri(et, temei,
                        "Istoricul declaratiilor nu a fost importat - nu pot confirma ce s-a depus inainte "
                        "de preluare.",
                        "Importa istoricul declaratiilor (Migrare > Istoric declaratii), apoi reia."))
    for cont, decl, denum in CONT_DECL_FISCAL:
        sold = abs(_d(net.get(cont, 0)))
        if sold <= TOLERANTA or decl in tipuri_depuse:
            continue
        out.append(_gri(et, temei,
                        f"Sold de deschidere pe {cont} ({denum}, {sold:.2f} lei) fara {decl} in istoricul importat.",
                        f"Verifica daca {decl} a fost depusa inainte de preluare si importa-o in istoric, "
                        f"sau confirma ca soldul are alta natura.",
                        cauza=f"Soldul pe {cont} sugereaza o obligatie {decl} anterioara care nu apare in "
                              f"istoricul preluat."))
    if not out and tipuri_depuse:
        out.append(_verde(et, temei,
                          f"Soldurile fiscale de deschidere au acoperire in istoricul declaratiilor "
                          f"importat ({', '.join(sorted(tipuri_depuse))})."))
    return out


def verifica_rip(conn, schema):
    """PFA (partida simpla): coerenta interna a registrului de incasari-plati preluat. Lista goala =
    firma nu are RIP (nu e PFA cu istoric preluat) -> verificarea nu apare, nu se falsifica."""
    et = "Registru incasari-plati (PFA)"
    temei = ("La partida simpla nu exista balanta: registrul e cronologic, iar soldul e implicit din "
             "Sigma incasari - Sigma plati. Coerenta interna = sold implicit ne-negativ + operatiuni "
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
        return []
    return constatare_rip(inc, plati, n, neclas)


def constatare_rip(inc, plati, n_total, n_neclasificat):
    """PURA (fara DB): coerenta registrului RIP preluat. Sold implicit = Sigma incasari - Sigma plati;
    negativ -> rosu (semnal). Operatiuni neclasificate -> gri (reclasificare). n_total=0 se trateaza in
    apelant (lista goala = firma nu e PFA cu RIP)."""
    et = "Registru incasari-plati (PFA)"
    temei = ("La partida simpla nu exista balanta: registrul e cronologic, iar soldul e implicit din "
             "Sigma incasari - Sigma plati. Coerenta interna = sold implicit ne-negativ + operatiuni "
             "clasificate fiscal.")
    sold = _d(inc) - _d(plati)
    out = []
    if sold < -TOLERANTA:
        out.append(_rosu(et, temei,
                         f"Registru: incasari {_d(inc):.2f} lei, plati {_d(plati):.2f} lei, sold implicit "
                         f"{sold:.2f} lei ({n_total} operatiuni).",
                         cauza="Soldul implicit al registrului preluat e negativ (plati > incasari cumulat).",
                         actiune=("Verifica registrul de la contabilul anterior: operatiuni de incasare "
                                  "omise, sume sau tip gresite, sold de report neinclus.")))
    else:
        out.append(_verde(et, temei,
                          f"Registrul preluat e coerent: incasari {_d(inc):.2f} lei, plati {_d(plati):.2f} "
                          f"lei, sold implicit {sold:.2f} lei ne-negativ ({n_total} operatiuni)."))
    if n_neclasificat:
        out.append(_gri(et, temei,
                        f"{n_neclasificat} din {n_total} operatiuni sunt \"neclasificat\" - categoria fiscala lipseste.",
                        "Reclasifica operatiunile in ecranul RIP (activitate / cheltuiala deductibila / limitata).",
                        cauza="Operatiuni preluate fara categorie fiscala (necesara la D212 / registru)."))
    return out


def audit(conn, schema, tenant_id, conn_public):
    """Orchestrator F183: ruleaza toate verificarile aplicabile si grupeaza pe cele TREI categorii
    cerute. `conn` pozitionat pe schema (get_conn(schema), SET LOCAL search_path); `conn_public` pe
    public (istoric declaratii_depuse). Data raportului o pune apelantul (repetabil, datat cu acum).
    Un check care crapa nu doboara restul -> gri cu cauza (izolare, ca _incrucisat din main.py)."""
    constatari = []
    for fn, args in ((verifica_balanta, (conn, schema)),
                     (verifica_parteneri, (conn, schema)),
                     (verifica_istoric_fiscal, (conn, schema, tenant_id, conn_public)),
                     (verifica_rip, (conn, schema))):
        try:
            constatari += fn(*args)
        except Exception as e:  # izolare: un check picat nu ascunde restul
            constatari.append(_gri(fn.__name__, "Verificarea nu a rulat.",
                                    f"NU pot rula verificarea ({e}).",
                                    "Reincearca; daca persista, verifica datele preluate ale firmei.",
                                    cauza="Eroare la verificare."))
    coerent = [c for c in constatari if c["stare"] == "verde"]
    divergent = [c for c in constatari if c["stare"] == "rosu"]
    neverificat = [c for c in constatari if c["stare"] == "gri"]
    stare = "rosu" if divergent else ("gri" if neverificat else ("verde" if coerent else "gri"))
    return {"stare": stare, "constatari": constatari,
            "coerent": len(coerent), "divergent": len(divergent), "neverificat": len(neverificat),
            "limita": ("Verificat: echilibru balanta, defalcare parteneri vs sintetic, solduri fiscale vs "
                       "istoric declaratii, coerenta registru PFA. NEVERIFICAT (v1): asociati/cote, mijloace "
                       "fixe, salariati, vector fiscal vs documente - lipsa lor ramane vizibila prin gri, nu "
                       "tacuta. Auditul verifica coerenta INTERNA a pachetului preluat, NU corectitudinea "
                       "evidentei contabilului anterior."),
            "modul": MODUL, "reguli": REGULI}
