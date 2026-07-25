"""GDPR art.17 — cererea de stergere DEPUSA de cabinet (NU executa nimic).

Cabinetul CERE din aplicatie; superadminul executa manual (core.gdpr_sterge,
care face DROP SCHEMA — ireversibil). Aici doar:
  1) valideaza typed-back (retastarea denumirii cabinetului),
  2) jurnalizeaza cererea in public.gdpr_cereri_stergere (dovada ca a fost
     primita si cand),
  3) anunta echipa pe canalul comun (core.observare -> Brevo -> contact@iconta.eu).

Reutilizeaza observare._trimite_brevo (F164/F202) — NU construi canal paralel.
"""
from core import observare


def _nume_cabinet(conn, cabinet_id):
    with conn.cursor() as cur:
        cur.execute("SELECT nume FROM public.accounting_firms WHERE id=%s", (cabinet_id,))
        r = cur.fetchone()
    return r[0] if r else None


def depune_cerere(conn, cabinet_id, user_id, confirmare_nume, motiv=None):
    """Inregistreaza o cerere de stergere. Ridica ValueError daca typed-back-ul
    nu se potriveste. Intoarce {ok, cerere_id, termen_zile_lucratoare}."""
    nume = _nume_cabinet(conn, cabinet_id)
    if not nume:
        raise ValueError("cabinet inexistent")
    if (confirmare_nume or "").strip() != (nume or "").strip():
        raise ValueError("Denumirea retastata nu se potriveste cu numele cabinetului.")
    motiv = (motiv or "").strip() or None
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO public.gdpr_cereri_stergere "
            "(cabinet_id, cerut_de_user_id, nume_cabinet, motiv) "
            "VALUES (%s,%s,%s,%s) RETURNING id, cerut_la",
            (cabinet_id, user_id, nume, motiv))
        cid, cerut_la = cur.fetchone()
    # anunta echipa; esecul emailului NU anuleaza cererea (deja jurnalizata)
    try:
        observare._trimite_brevo(
            "Cerere de stergere cont (GDPR art.17)",
            "Cabinet #%s \"%s\" a depus o cerere de stergere.\n"
            "Cerere #%s, user #%s, la %s.\n"
            "Motiv: %s\n\n"
            "Executie MANUALA (superadmin, dupa verificare):\n"
            "  POST /gdpr/sterge-cabinet/%s/executa"
            % (cabinet_id, nume, cid, user_id, cerut_la, motiv or "(nespecificat)", cabinet_id))
    except Exception:
        pass
    return {"ok": True, "cerere_id": cid, "termen_zile_lucratoare": 5}
