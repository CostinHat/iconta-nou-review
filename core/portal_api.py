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
            f"tip_decont, regim_fiscal FROM {schema}.firma_profil WHERE id = 1")   # [lotul 13, 554] regimul: numele impozitului de plată
        r = cur.fetchone()
    d = dict(r) if r else None
    if d:
        from core.common import tip_decont_lung  # [decont_lung] portalul clientului afisa "L"/"T" brut
        d["tip_decont"] = tip_decont_lung(d.get("tip_decont"))
    return d


# ============================================================
#  DECLARAȚII DEPUSE — jurnalul final (public)
# ============================================================
def denumire_declaratie(tip):
    """[lotul 13, 555] Denumirea oficială a formularului (`DENUMIRE_OFICIALA` din modulul lui, ex. `core/d406.py`: „Fișierul Standard de
    Control Fiscal (SAF-T) pentru România”), sau None când modulul n-o are — clientul citește ce e, nu doar „d406”."""
    import importlib
    import re
    t = (tip or "").strip().lower()
    if not re.fullmatch(r"d\d{3}[a-z]?", t):
        return None
    try:
        return getattr(importlib.import_module("core." + t), "DENUMIRE_OFICIALA", None)
    except ImportError:
        return None


def _zi_ro(data):
    """Ziua depunerii (ISO), în ora României — `data_depunere` e un moment (timestamptz)."""
    import datetime
    import zoneinfo
    if isinstance(data, datetime.datetime):
        return (data.astimezone(zoneinfo.ZoneInfo("Europe/Bucharest")) if data.tzinfo else data).date().isoformat()
    return data.isoformat() if data else None


def declaratii_depuse(conn, tenant_id, conn_schema=None):
    """
    Declarațiile depuse pentru firma clientului (ce s-a trimis efectiv la ANAF).
    Doar jurnalul final — nu procesul intern al cabinetului (coadă, respingeri).

    [lotul 13, deficiența 555, comanda Costin 13.1] „Rândul arată doar «d406 · depusă» (fără perioadă, dată, recipisă; gol după «·»)”:
    ecranul citea `perioada` și `depus_la`, pe care rândul nu le avea. Acum fiecare rând le poartă gata scrise: `cod` („D406”), `denumire`,
    `perioada` în forma ecranelor („09/2026”, „T3/2026”, „2025” — `control_fiscal_api.perioada_declaratiei`, după periodicitatea firmei, cu
    `conn_schema`), `data` depunerii (ISO) și `recipisa` ultimei depuneri (`public.declaratii_depuse`, rândul cu cel mai mare
    `nr_depunere`, ca vederea `declaratii_depuse_curente`). O singură sursă pentru cardul „Declarații depuse”.
    """
    from core import control_fiscal_api as _cf
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT ON (an, luna, tip) tip, an, luna, data_depunere, recipisa FROM public.declaratii_depuse "
                    "WHERE tenant_id = %s ORDER BY an, luna, tip, nr_depunere DESC", (tenant_id,))
        randuri = [tuple(r.values()) if isinstance(r, dict) else tuple(r) for r in cur.fetchall()]
    out = []
    for tip, an, luna, data, recipisa in randuri:
        per = (_cf.perioada_declaratiei(conn_schema, tip, an, luna) if conn_schema is not None
               else _cf.perioada_canonica(an, luna, "luna"))
        out.append({"tip": tip, "cod": (tip or "").upper(), "denumire": denumire_declaratie(tip), "an": an, "luna": luna,
                    "perioada": per, "data": _zi_ro(data),
                    "recipisa": (recipisa or "").strip() or None})
    out.sort(key=lambda d: (d["an"], d["luna"], d["tip"]), reverse=True)
    return out
