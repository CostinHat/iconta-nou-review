"""
core/migrare_api.py — starea migrării unui cabinet, pe straturi.

Fiecare strat de migrare (firme, solduri, salariați, asociați, mijloace fixe)
are o stare per cabinet: 'gata' sau 'in_lucru'. La 'in_lucru' contabilul scrie
o notă (de ce nu e gata) — apare ca reminder pe cardul Firme.

Tabelul se auto-creează (CREATE TABLE IF NOT EXISTS) la pornire.
"""
from __future__ import annotations

# straturile de migrare, în ordinea logică (firme întâi — creează tenant-urile)
# 'regim' = pentru ce tip de firma se aplica stratul:
#   'ambele' -> SRL si PFA; 'dubla' -> doar SRL (partida dubla); 'simpla' -> doar PFA (RIP).
STRATURI_META = [
    ("firme",              "ambele"),
    ("vector_fiscal",      "ambele"),
    ("solduri",            "dubla"),
    ("solduri_parteneri",  "dubla"),
    ("salariati",          "ambele"),
    ("asociati",           "dubla"),
    ("mijloace_fixe",      "dubla"),
    ("istoric_declaratii", "ambele"),
    ("plan_conturi",       "dubla"),
    ("rip",                "simpla"),
]  # [p82_vector] [p95_plan_conturi] [p_pfa_rip 20.07]
STRATURI = [s for s, _ in STRATURI_META]


def tip_firma_nrm(tip_firma):
    """tip_firma normalizat (lower+trim), default 'srl' la lipsă/None — UNICUL loc cu default-ul de creare
    (srl = partidă dublă implicit). Nu validează în {srl,pfa} (CHECK-ul DB o face); doar normalizează.
    Consumatorii (auth_api, tenant_provisioning, regim_contabil) îl folosesc — NU redau `or "srl"` inline.
    Vezi DESIGN_SYSTEM cap. DEFAULT_FISCAL_TACIT + DECIZII 23.07."""
    return (tip_firma or "srl").strip().lower()


def regim_contabil(tip_firma):
    """'dubla' | 'simpla' din tip_firma — UN SINGUR loc unde scrie faptul (srl=partidă dublă, pfa=partidă
    simplă). straturi_pentru() + regim_efectiv() îl folosesc; regula NU se recopiază. Vezi DECIZII 23.07."""
    return "simpla" if tip_firma_nrm(tip_firma) == "pfa" else "dubla"


def straturi_pentru(tip_firma):
    """Straturile aplicabile unui tip de firma ('srl' | 'pfa')."""
    vrut = regim_contabil(tip_firma)   # 'dubla' | 'simpla' — fapt UNIC (regim_contabil), nu recopiat
    return [s for s, regim in STRATURI_META if regim in ("ambele", vrut)]


def regim_efectiv(profil: dict) -> str | None:
    """Regimul CIT EFECTIV al firmei: 'micro' | 'profit' | None. Partidă simplă (pfa) => None NECONDIȚIONAT
    (profesie liberală/PFA: impozit pe venit prin D212, nu regim CIT), oricât ar scrie regim_fiscal. Contract
    STRICT: profil TREBUIE să aibă 'tip_firma' + 'regim_fiscal' (KeyError altfel — fără .get, fără fallback;
    callerul dă profil complet). Vezi DECIZII 23.07."""
    if regim_contabil(profil["tip_firma"]) == "simpla":
        return None
    rf = profil["regim_fiscal"]
    return rf.strip().lower() if rf else None
STARI = ("gata", "in_lucru")


def asigura_tabel(conn):
    """Creează tabelul de status dacă nu există. Idempotent."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS public.migrare_status (
                id SERIAL PRIMARY KEY,
                accounting_firm_id INTEGER NOT NULL,
                strat TEXT NOT NULL,
                stare TEXT NOT NULL DEFAULT 'in_lucru',
                nota TEXT NOT NULL DEFAULT '',
                actualizat_la TIMESTAMPTZ NOT NULL DEFAULT now(),
                UNIQUE (accounting_firm_id, strat)
            )
        """)
    conn.commit()


def citeste_status(conn, firm_id):
    """
    Întoarce starea fiecărui strat pentru cabinet:
    {strat: {"stare": ..., "nota": ...}}. Straturile neîncepute lipsesc din dict.
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT strat, stare, nota FROM public.migrare_status "
            "WHERE accounting_firm_id = %s",
            (firm_id,),
        )
        randuri = cur.fetchall()
    out = {}
    for strat, stare, nota in randuri:
        out[strat] = {"stare": stare, "nota": nota or ""}
    return out


def seteaza_status(conn, firm_id, strat, stare, nota=""):
    """Upsert starea unui strat. La 'in_lucru' nota e obligatorie."""
    if strat not in STRATURI:
        raise ValueError(f"strat necunoscut: {strat}")
    if stare not in STARI:
        raise ValueError(f"stare necunoscută: {stare}")
    if stare == "in_lucru" and not (nota or "").strip():
        raise ValueError("nota e obligatorie când importul nu e gata")

    with conn.cursor() as cur:
        # upsert-ok: set stare strat import pe (firma,strat) - actualizare intentionata a statusului
        cur.execute(
            "INSERT INTO public.migrare_status "
            "  (accounting_firm_id, strat, stare, nota, actualizat_la) "
            "VALUES (%s, %s, %s, %s, now()) "
            "ON CONFLICT (accounting_firm_id, strat) DO UPDATE SET "
            "  stare = EXCLUDED.stare, nota = EXCLUDED.nota, actualizat_la = now()",
            (firm_id, strat, stare, (nota or "").strip()),
        )
    conn.commit()
    return {"strat": strat, "stare": stare, "nota": (nota or "").strip()}


def reminder(conn, firm_id, tip_firma="srl"):
    """
    Pentru cardul Firme: straturile care NU sunt 'gata' și au fost declarate
    'in_lucru' (cu notă). Întoarce listă [{strat, nota}].
    Filtrat pe tip_firma: PFA nu vede straturi de partida dubla, SRL nu vede rip.
    """
    status = citeste_status(conn, firm_id)
    out = []
    for strat in straturi_pentru(tip_firma):
        s = status.get(strat)
        if s and s["stare"] == "in_lucru":
            out.append({"strat": strat, "nota": s["nota"]})
    return out


def erori_verifica(rez):
    """Normalizeaza rezultatul verifica_randuri (lista SAU tuplu (erori, bune)) la lista de erori
    [{rand, motiv, mesaj}]. POARTA UNICA preview<->salvare (DS cap.24): previzualizarea intoarce
    ACEEASI verdict ca verifica_randuri - poarta pe care importa() o aplica la scriere - nu o a doua
    validare din extrage (flaguri cnp_valid/ok) care drifteaza (un camp verificat intr-un capat si nu
    in celalalt). Frontendul consuma `erori` si blocheaza Salvarea pe randurile respinse (cap.6)."""
    if isinstance(rez, tuple):
        return rez[0] or []
    return rez or []


# ─────────────────────────────────────────────────────────────────────────────
# [P8/C, 21.08.2026] RESPINGERILE DE RAND LA IMPORT SUNT AFIRMATII, cu regula NUMITA.
#
# Pana azi fiecare modul isi inventa codurile. Masurat: 46 de respingeri in 12 module, din care 27
# purtau deja un cod masinal si 9 doar proza. ZERO coliziuni intre module (verificat, nu presupus),
# deci nomenclatorul se poate INCHIDE fara sa cimenteze o ambiguitate.
#
# DE CE conteaza, cu instanta: `migrare.js` numara duplicatele cu
# `erori.filter(e => (e.mesaj || "").includes("există deja"))` - o clasificare prin potrivire de
# PROZA. Cine reformuleaza mesajul strica tacut numaratoarea, iar ecranul spune „0 firme erau deja in
# portofoliu" despre un import in care erau. Un cod inchis nu se schimba cand se rescrie textul.
#
# `fel` de aici NU e felul afirmatiei (ala e mereu `neconformitate`), ci FORMA respingerii - ce s-a
# intamplat cu valoarea. Randorul poate grupa dupa el fara sa citeasca textul.
REGULI = {
    # --- lipsa: campul nu are valoare, iar fara ea nu se poate merge mai departe
    "cod_lipsa":        {"fel": "lipsa", "inseamna": "mijloc fix fara cod de inventar"},
    "durata_lipsa":     {"fel": "lipsa", "inseamna": "durata de amortizare lipseste sau nu e pozitiva"},
    "norma_lipsa":      {"fel": "lipsa", "inseamna": "norma de lucru (intreaga/partiala) lipseste - ceruta de D112"},
    "salariu_lipsa":    {"fel": "lipsa", "inseamna": "salariul de baza lipseste sau nu e mai mare ca 0"},
    "valoare_lipsa":    {"fel": "lipsa", "inseamna": "valoarea de intrare lipseste sau nu e pozitiva"},
    "data_lipsa":       {"fel": "lipsa", "inseamna": "data operatiunii lipseste"},
    "explicatie_lipsa": {"fel": "lipsa", "inseamna": "explicatia operatiunii lipseste (coloana e NOT NULL)"},

    # --- invalid: valoarea E acolo, dar nu satisface regula
    "cnp_invalid":      {"fel": "invalid", "inseamna": "CNP care nu trece cifra de control"},
    "cui_invalid":      {"fel": "invalid", "inseamna": "CUI care nu trece cifra de control"},
    "iban_invalid":     {"fel": "invalid", "inseamna": "IBAN care nu trece mod-97 (ISO 13616)"},
    "judet_invalid":    {"fel": "invalid", "inseamna": "judet inexistent in nomenclatorul oficial"},
    "ore_invalide":     {"fel": "invalid", "inseamna": "ore/zi peste norma legala"},
    "an_invalid":       {"fel": "invalid", "inseamna": "anul e in afara intervalului acceptat"},
    "luna_invalida":    {"fel": "invalid", "inseamna": "luna nu e intre 1 si 12, sau nu e numar"},
    "data_invalida":    {"fel": "invalid", "inseamna": "data nu se poate interpreta"},
    "data_viitor":      {"fel": "invalid", "inseamna": "data e in viitor, unde nu poate fi"},
    "tip_necunoscut":   {"fel": "invalid", "inseamna": "tipul nu exista in nomenclatorul asteptat"},
    "suma_invalida":    {"fel": "invalid", "inseamna": "suma e 0 sau neinterpretabila"},
    "cont_nepartener":  {"fel": "invalid", "inseamna": "contul nu tine solduri pe parteneri"},

    # --- duplicat: valoarea intra in conflict cu una care exista deja
    "cod_duplicat":     {"fel": "duplicat", "inseamna": "acelasi cod de inventar apare de doua ori in fisier"},
    "deja_exista":      {"fel": "duplicat", "inseamna": "inregistrarea exista deja si nu se dubleaza"},

    # --- esec: nu datele sunt de vina, ci operatiunea s-a rupt. Sta in ACEEASI lista pe care o vede
    # contabilul, deci trebuie sa se poata DEOSEBI de o respingere de date - altfel „N firme nu au
    # putut fi adaugate" amesteca „CUI invalid" cu „baza de date a picat", si omul cauta in locul gresit.
    "creare_esuata":    {"fel": "esec", "inseamna": "crearea inregistrarii s-a oprit cu o eroare tehnica"},

    # --- incoerent: doua valori ale aceluiasi rand (sau set) nu pot fi amandoua adevarate
    "rezidual_peste_intrare": {"fel": "incoerent",
                               "inseamna": "valoarea ramasa depaseste valoarea de intrare"},
    "cote_nu_dau_suta":       {"fel": "incoerent",
                               "inseamna": "cotele asociatilor nu insumeaza 100%"},
    "data_inainte_de_perioada": {"fel": "incoerent",
                                 "inseamna": "depunerea e datata inaintea perioadei raportate"},
}


def respinge(tip, unde, regula, mesaj, **campuri):
    """O respingere de rand, ca AFIRMATIE. Constructorul UNIC - un cod care nu e in REGULI nu poate
    fi produs, deci o greseala de tastare nu mai trece tacut ca o categorie noua.

    CIOCNIRE DE VOCABULAR, rezolvata explicit (21.08.2026): pana azi cheia "motiv" purta CODUL in
    importuri si TEXTUL in afirmatii - acelasi nume, doua intelesuri, exact capcana pe care o vaneaza
    campania. De-acum "motiv" e TEXTUL peste tot; codul traieste in "regula". Consumatorii au fost
    NUMARATI inainte, nu presupusi: trei fisiere de test si fallback-ul din migrare.js. Modulul
    tipare_api grupeaza respingerile ANAF din baza - alt camp cu acelasi nume, care nu se atinge.

    Cheia "mesaj" ramane, cu ACEEASI valoare ca "motiv", fiindca frontendul o randeaza; testul
    asertaza ca nu pot diverge. Cheia "rand" e domeniul concret, pe langa "unde" care il scrie in
    limba omului."""
    from core import afirmatii as _af
    if regula not in REGULI:
        raise ValueError(
            "regula %r nu e in nomenclator; cele declarate: %s. Un cod nou se ADAUGA in REGULI, cu "
            "ce inseamna - altfel randorul primeste o categorie despre care nu stie nimic."
            % (regula, ", ".join(sorted(REGULI))))
    if unde is None or str(unde).strip() == "":
        raise ValueError("respingerea cere domeniul: fara el, contabilul nu stie ce sa corecteze")
    if not (mesaj or "").strip():
        raise ValueError("respingerea cere un text pentru om, nu doar codul %r" % regula)
    # DOMENIUL nu e mereu un rand. Prima forma cerea `rand`, si era peste-croita pe importurile din
    # fisier: `articole_import` si `retete_import` identifica prin DENUMIRE, iar coerenta cotelor e
    # despre SETUL de asociati. A doua constructor pentru „acelasi lucru, alt domeniu" ar fi fost
    # exact logica paralela pe care o evitam. Aici: numarul devine „randul N", restul se scrie ca atare.
    e_rand = isinstance(unde, int) or (isinstance(unde, str) and unde.strip().isdigit())
    a = _af.afirmatie("neconformitate", tip, mesaj,
                      unde=("rândul %s" % unde) if e_rand else str(unde), regula=regula)
    if e_rand:
        a["rand"] = int(unde)      # cheia pe care o citeste poarta unica preview<->salvare
    a["mesaj"] = mesaj
    a["forma"] = REGULI[regula]["fel"]   # lipsa | invalid | duplicat | incoerent - pt grupare la randare
    a.update(campuri)
    return a
