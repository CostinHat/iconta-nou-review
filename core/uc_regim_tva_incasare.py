# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/tenants/{tenant_id}/tva-incasare` (deficiența 428, lotul 10, comanda Costin 10.1).

[lotul 10, deficiența 428] „Construiește regimul pe firmă, cu data de la care se aplică și verificarea în registrul ANAF.” Regulile
și temeiul (CF art.282 alin.(3), (3^1), (5)) sunt în `core/regim_tva_incasare.py`; aici: tranzacția (un refuz nu lasă nimic scris),
dreptul (ruta: „Poate pregăti”, ca regimul de TVA — PIVOT DECIZII 04.10.2026) și apelul ANAF, făcut ÎNAINTE de a deschide conexiunea
pe schema firmei (nu se ține o conexiune din pool peste un serviciu străin de 20 s).
"""
from core import db
from core import erori as _erori
from core import uc_comun as _uc_comun
from core import regim_tva_incasare as _rti
from core import repo_tenants


def _refuz(r):
    m = r.get("mesaj") or "regim TVA la încasare invalid"
    # [lotul 11, deficiența 440] toate erorile adunate (`regim_tva_incasare._refuz_adunat`), nu numai prima
    ec = r.get("erori_campuri") or ([{"camp": r["camp"], "mesaj": m}] if r.get("camp") else None)
    return _erori.DateInvalide({"mesaj": m, "erori_campuri": ec} if ec else m)


def _rtvai_firma(tenant_id):
    """(rtvai | None, motiv | None, indisponibil: bool): RTVAI-ul firmei din ANAF (statusul + datele sistemului TVA la încasare). Nu ridică: un serviciu
    străin căzut dă motivul (`anaf_api.mesaj_indisponibil`), nu o eroare internă. Chemat ÎNAINTE de conexiunea pe schema firmei."""
    from core import anaf_api
    with db.get_conn() as cpub, cpub.cursor() as cur:
        row = repo_tenants.nume_si_cui_spatiat(cur, tenant_id)
    cui = "".join(ch for ch in str((row[1] if row else "") or "") if ch.isdigit())
    if not cui:
        return None, "Firma n-are CUI: fără el nu se poate căuta în registrul ANAF.", False
    try:
        rez = anaf_api.valideaza_cui([cui])
    except Exception as e:  # noqa: BLE001 — orice cădere a serviciului străin: motivul în cuvinte, nu textul bibliotecii
        return None, anaf_api.mesaj_indisponibil(e), True
    if not (rez and rez[0].get("gasit")):
        return None, "ANAF nu găsește CUI-ul %s în registrul contribuabililor." % cui, False
    return (rez[0].get("tva_incasare_rtvai") or {}), None, False


def tva_incasare_salveaza(tenant_id, corp, ctx):
    """[428] Corpul rutei POST `/tenants/{tenant_id}/tva-incasare`: {aplica: da/nu, de_la, pana_la, data_optiune} — perioada curentă. După salvare,
    verificarea în registrul ANAF (ca la vector, F180: semnal, nu blocaj) se consemnează pe perioadă și se întoarce (`anaf`)."""
    corp = corp or {}
    try:
        aplica = _uc_comun.bifa(corp, "aplica")
    except (KeyError, ValueError) as e:
        m = "Aplică sistemul TVA la încasare: alege Da sau Nu."
        raise _erori.DateInvalide({"mesaj": m, "erori_campuri": [{"camp": "tva_incasare", "mesaj": m}]}) from e
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    rtvai, _motiv, _x = _rtvai_firma(tenant_id) if aplica else (None, None, False)
    with db.get_conn(schema) as conn, conn.cursor() as cur:
        # [lotul 13, 541] data notificării (opțiunea nu se aplică în perioada în curs) și data din registrul ANAF, citit mai sus
        r = _rti.salveaza(cur, aplica, corp.get("de_la"), corp.get("pana_la"), user_id=ctx["uid"], data_optiune=corp.get("data_optiune"),
                          de_la_anaf=(rtvai or {}).get("data_inceput"))
        if not r.get("ok"):
            raise _refuz(r)   # în blocul conexiunii: excepția anulează tranzacția
        if rtvai is not None:
            r["anaf"] = _rti.compara_anaf(rtvai, (_rti.perioade(cur) or [None])[-1])
            r["stare"] = _rti.inregistreaza_anaf(cur, r["anaf"])
        elif _motiv:
            # verificarea însăși s-a oprit (serviciul ANAF / CUI-ul lipsă): afirmație tipată `verificare_rupta`, cu motivul (decizia 21.08)
            from core import afirmatii as _af
            m = "Verificarea în registrul ANAF nu s-a putut face: %s" % _motiv
            r["anaf"] = _af.afirmatie("verificare_rupta", "sistemul TVA la încasare", m, eroare=_motiv, mesaj=m)
        return r


def tva_incasare_sterge(tenant_id, perioada_id, ctx):
    """[428] Corpul rutei DELETE `/tenants/{tenant_id}/tva-incasare/{perioada_id}`: o perioadă scrisă din greșeală."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn, conn.cursor() as cur:
        r = _rti.sterge(cur, perioada_id, ctx["uid"])
        if not r.get("ok"):
            raise _erori.DateInvalide(r.get("mesaj"))
        return r


def tva_incasare_verifica_anaf(tenant_id, ctx):
    """[428] Corpul rutei GET `/tenants/{tenant_id}/tva-incasare/verifica-anaf`: statusul și datele din Registrul persoanelor care
    aplică sistemul TVA la încasare (RTVAI). Propune datele ANAF și spune dacă diferă de ce e scris. CITIRE: nu scrie nimic — omul
    alege și salvează (verificarea se consemnează atunci, `tva_incasare_salveaza`)."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    rtvai, motiv, indisponibil = _rtvai_firma(tenant_id)
    if rtvai is None:
        raise (_erori.ServiciuIndisponibil if indisponibil else _erori.DateInvalide)(motiv)
    with db.get_conn(schema) as conn, conn.cursor() as cur:
        return _rti.compara_anaf(rtvai, (_rti.perioade(cur) or [None])[-1])
