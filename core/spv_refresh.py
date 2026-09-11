# -*- coding: utf-8 -*-
"""
core/spv_refresh.py — driver cron pentru refresh-ul token-urilor SPV (F177).

Golul #1 al conectorului: access token-ul ANAF expira la 90 zile. Fara reimprospatare
automata, cabinetul se deconecteaza tacit si trebuie sa reautorizeze cu stickul.

CE FACE: ruleaza zilnic (systemd timer spv-refresh.timer), gaseste TOATE token-urile
active al caror access_expira intra sub marja (SPV_REFRESH_MARJA_ZILE, implicit 15 zile
- cu marja fata de expirarea reala, sa nu prinzi exact 90 zile) si le reimprospateaza.

REUTILIZARE: apeleaza spv_conector.reimprospateaza_token (functia exista, face ROTATIA -
salveaza AMBELE valori noi, access + refresh). Driver-ul NU redefineste logica de token.

FAIL-SAFE (cerinta): fiecare token intr-o tranzactie separata (db.get_conn). Esecul unui
token NU opreste restul si NU strica reimprospatarile reusite (deja commit-uite). La esec,
tranzactia face rollback -> tokenul RAMANE activ si se reincearca a doua zi (avem 15 zile
marja, o eroare ANAF tranzitorie nu forteaza reconectarea). Esecurile se aaduna si se
trimit pe email (Brevo, prin core.observare) - un token care nu se mai reimprospateaza
tacit = cabinet deconectat fara sa stie.
"""
import os
import sys
from datetime import datetime, timezone, timedelta

from core import db
from core import spv_conector as s

MARJA_ZILE = int(os.environ.get("SPV_REFRESH_MARJA_ZILE", "15"))


def token_uri_de_reimprospatat(conn, acum=None):
    """Randurile active cu access_expira sub marja. Pura fata de retea."""
    acum = acum if acum is not None else datetime.now(timezone.utc)
    prag = acum + timedelta(days=MARJA_ZILE)
    with conn.cursor() as cur:
        # GARDUL 3: selecteaza pe activ, NU pe accounting_firm_id IS NOT NULL - altfel ar sari
        # tacit peste tokenele gratuite (tenant_id). Ambele principaluri intra in refresh.
        cur.execute("""
            SELECT id, accounting_firm_id, tenant_id, serial_certificat, refresh_token, access_expira
              FROM public.spv_token
             WHERE activ = true AND access_expira < %s
             ORDER BY access_expira
        """, (prag,))
        return cur.fetchall()


def ruleaza(acum=None):
    """Punctul de intrare al cronului. Intoarce {reusite, esecuri}."""
    db.init_pool()
    with db.get_conn() as conn:
        randuri = token_uri_de_reimprospatat(conn, acum)
    ts = datetime.now(timezone.utc).isoformat()
    print("%s spv_refresh: %d token-uri sub marja de %d zile" % (ts, len(randuri), MARJA_ZILE))

    reusite = 0
    esecuri = []
    for (tid, firm_id, ten_id, serial, refresh_enc, access_expira) in randuri:
        eticheta = ("firma %s" % firm_id) if firm_id is not None else ("gratuit tenant %s" % ten_id)
        try:
            # [P5 val 3, 11.09.2026] Tranzactie per token, ca inainte — dar ea apartine ACUM
            # rotatiei, nu jobului: `reimprospateaza_token` face apelul `/token` (termen 30 s)
            # FARA conexiune, apoi deschide una scurta in care scrie si COMITE. Un esec pe un token
            # nu strica ce s-a comis pentru celelalte, exact ca inainte.
            token_row = {
                "id": tid,
                "accounting_firm_id": firm_id,
                "tenant_id": ten_id,
                "serial_certificat": serial,
                "refresh_token": s.decripteaza(refresh_enc),  # reimprospateaza_token cere clar
            }
            nou = s.reimprospateaza_token(token_row)
            reusite += 1
            print("  OK token %s (%s): access_expira %s -> %s"
                  % (tid, eticheta, access_expira.isoformat(), nou["access_expira"].isoformat()))
        except Exception as e:
            esecuri.append((tid, eticheta, type(e).__name__, str(e)[:200]))
            print("  ESEC token %s (%s): %s: %s"
                  % (tid, eticheta, type(e).__name__, e), file=sys.stderr)

    if esecuri:
        _alerteaza_esecuri(esecuri)
    print("%s spv_refresh terminat: %d reusite, %d esecuri"
          % (datetime.now(timezone.utc).isoformat(), reusite, len(esecuri)))
    return {"reusite": reusite, "esecuri": len(esecuri)}


def _alerteaza_esecuri(esecuri):
    """Email pe canalul comun (Brevo, core.observare). Nu construi canal paralel."""
    linii = "\n".join("token %s (%s): %s — %s" % e for e in esecuri)
    subiect = "Refresh token SPV esuat (%d)" % len(esecuri)
    mesaj = ("Reimprospatarea automata a esuat pentru %d token-uri SPV. Cabinetele afectate "
             "risca sa se deconecteze de la SPV si sa fie nevoite sa reconecteze din UI "
             "(Setari -> Conectare SPV). Detaliu:\n\n%s" % (len(esecuri), linii))
    try:
        from core import observare
        observare._trimite_brevo(subiect, mesaj)
        print("alerta email trimisa (%d esecuri)" % len(esecuri))
    except Exception as e:
        print("alerta email NETRIMISA: %s" % e, file=sys.stderr)


if __name__ == "__main__":
    from core import cron  # [R74] alerta la esec + bataie la reusita
    cron.ruleaza("spv_refresh", ruleaza)
