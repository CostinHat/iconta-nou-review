# -*- coding: utf-8 -*-
"""REPOSITORY — profilul firmei din schema ei (`firma_profil`).

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:842`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""
from core.common import tip_decont_lung  # [PIVOT 04.10.2026] forma lungă a periodicității, în jurnalul regimului TVA


def profil_fiscal(cur):
    cur.execute("SELECT tip_firma, tip_decont, platitor_tva, operatiuni_ic, regim_fiscal FROM firma_profil WHERE id = 1")
    return cur.fetchone()


def email_firma(cur):
    cur.execute("SELECT email FROM firma_profil WHERE id = 1")
    return cur.fetchone()


def seria_chitantei(cur, schema):
    cur.execute(f"SELECT COALESCE(serie_chitanta, 'CH') FROM {schema}.firma_profil LIMIT 1")
    return cur.fetchone()


def amef_si_cont_venit(cur, schema):
    """[D394 Î2] (exceptată de la AMEF, contul de venit implicit) — chitanța de vânzare fără factură."""
    cur.execute(f"SELECT activitate_exceptata_amef, COALESCE(NULLIF(TRIM(cont_venit_implicit), ''), '707') "
                f"FROM {schema}.firma_profil LIMIT 1")
    return cur.fetchone()


def config_woocommerce(cur, schema):
    cur.execute(f"SELECT wc_url, (wc_ck IS NOT NULL AND wc_cs IS NOT NULL) AS are_chei FROM {schema}.firma_profil LIMIT 1")
    return cur.fetchone()


def cui_firma(cur, schema):
    cur.execute(f"SELECT cui FROM {schema}.firma_profil WHERE id = 1")
    return cur.fetchone()


def cui_firma_2(cur, schema):
    cur.execute(f"SELECT cui FROM {schema}.firma_profil WHERE id=1")
    return cur.fetchone()


def cui_firma_3(cur, schema):
    cur.execute(f"SELECT cui FROM {schema}.firma_profil LIMIT 1")
    return cur.fetchone()


def platitor_tva(cur, schema):
    cur.execute(f"SELECT COALESCE(platitor_tva, true) FROM {schema}.firma_profil LIMIT 1")
    return cur.fetchone()


def platitor_tva_2(cur, schema):
    cur.execute(f"SELECT COALESCE(platitor_tva, true) FROM {schema}.firma_profil LIMIT 1")
    return cur.fetchone()


# ── P7 · V2: scrierile, mutate din rute ──────────────────────────────

# [PIVOT DECIZII 04.10.2026] Costin: „Regimul de TVA la «Poate pregăti»: confirmat, cu jurnalizarea fiecărei schimbări
# (utilizator, dată, vechi → nou), ca la bifa C&D.” Câmpurile care schimbă ce declarații de TVA datorează firma și cum.
# Orice scriere a lor după crearea firmei trece prin `jurnalizeaza_regim_tva`, în ACEEAȘI tranzacție (gardat de
# `core/test_jurnal_regim_tva.py`); precompletarea din ANAF de la creare e valoarea inițială, nu o schimbare.
CAMPURI_REGIM_TVA = ("platitor_tva", "tip_decont", "inreg_art317")


def regim_tva_pentru_schimbare(cur):
    """Valorile curente ale câmpurilor de regim TVA, cu rândul BLOCAT (FOR UPDATE: două salvări simultane nu scriu același
    „vechi”); None dacă firma n-are încă profil."""
    cur.execute("SELECT platitor_tva, tip_decont, inreg_art317 FROM firma_profil WHERE id = 1 FOR UPDATE")
    r = cur.fetchone()
    return None if r is None else dict(zip(CAMPURI_REGIM_TVA, r))


def jurnalizeaza_regim_tva(cur, vechi, nou, user_id):
    """Un rând în `firma_profil_jurnal` pentru fiecare câmp din `nou` care chiar s-a schimbat față de `vechi` (None = firmă
    fără profil: vechiul e gol). Întoarce câte rânduri a scris. Fără utilizator nu se scrie nimic: schimbarea e refuzată."""
    if user_id is None:
        raise ValueError("schimbarea regimului de TVA se jurnalizează cu utilizatorul care o face — lipsește")
    scrise = 0
    for camp in CAMPURI_REGIM_TVA:
        if camp not in nou:
            continue
        v, n = (vechi or {}).get(camp), nou[camp]
        if camp == "tip_decont":
            # periodicitatea în forma lungă: seed-ul vechi „T” și „trimestrial” sunt aceeași alegere — altfel prima
            # salvare ar jurnaliza o schimbare pe care nimeni n-a făcut-o
            v, n = (tip_decont_lung(v) or v or None), (tip_decont_lung(n) or n or None)
        v, n = [None if x is None else (str(x).lower() if isinstance(x, bool) else str(x)) for x in (v, n)]
        if v != n:
            cur.execute("INSERT INTO firma_profil_jurnal (camp, valoare_veche, valoare_noua, user_id) "
                        "VALUES (%s, %s, %s, %s)", (camp, v, n, user_id))
            scrise += 1
    return scrise


def seteaza_platitor_tva(cur, platitor_tva, user_id):
    vechi = regim_tva_pentru_schimbare(cur)
    if vechi is None:
        return
    cur.execute("UPDATE firma_profil SET platitor_tva = %s WHERE id = 1",
                (platitor_tva,))
    jurnalizeaza_regim_tva(cur, vechi, {"platitor_tva": bool(platitor_tva)}, user_id)


def seteaza_config_woocommerce(cur, schema, wc_url, wc_ck, wc_cs):
    cur.execute(f"""UPDATE {schema}.firma_profil
                        SET wc_url=%s, wc_ck=%s, wc_cs=%s""",
                (wc_url, wc_ck, wc_cs))
