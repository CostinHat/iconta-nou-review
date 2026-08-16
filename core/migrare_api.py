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
