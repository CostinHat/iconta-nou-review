"""
core/portal_api.py — portalul clientului (rol 'client'), READ-ONLY.
Clientul își vede propriile date, izolat: nu atinge zona cabinetului, nu poate
cere alt tenant. Tenantul se rezolvă din user_tenants (auth_api), nu din URL.

Suprafață separată de cabinet. Aici doar citiri:
  - datele firmei (firma_profil, pe schema tenantului)
  - declarațiile DEPUSE (jurnalul final, din public.declaratii_depuse)
  - facturile -> se refolosește facturi_api.lista_facturi (pe schema tenantului)
"""
from __future__ import annotations

REGULI = "2026.1"
MODUL = "portal_api"


# ============================================================
#  DATELE FIRMEI — pe schema tenantului
# ============================================================
def date_firma(conn, schema):
    """Profilul firmei clientului (firma_profil id=1), sau None."""
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT nume, cui, adresa, oras, judet, caen, banca, iban, "
            "tip_decont FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
    return dict(r) if r else None


# ============================================================
#  DECLARAȚII DEPUSE — jurnalul final (public)
# ============================================================
def declaratii_depuse(conn, tenant_id):
    """
    Declarațiile depuse pentru firma clientului (ce s-a trimis efectiv la ANAF).
    Doar jurnalul final — nu procesul intern al cabinetului (coadă, respingeri).
    """
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT tip, an, luna, data_depunere FROM public.declaratii_depuse_curente "
            "WHERE tenant_id = %s ORDER BY an DESC, luna DESC, tip", (tenant_id,))
        return [dict(r) for r in cur.fetchall()]
