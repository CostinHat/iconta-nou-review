"""GDPR art.5 minimizare — retentie pe public.audit_log.
Sterge inregistrarile mai vechi de AUDIT_LOG_RETENTIE_LUNI (implicit 12 luni).
Rulat zilnic din cron (04:00). N=12: acopera un AN FISCAL complet (intrebarile de audit vin la
util operational pentru suport + investigatie securitate ~2 trimestre; peste atat nu
mai e necesar (minimizare). Configurabil prin env.
Cron: 0 4 * * * cd ~/iconta_nou && . db.env && python3 -m core.audit_retentie"""
import os
from core import db

def luni():
    try:
        return max(1, int(os.environ.get("AUDIT_LOG_RETENTIE_LUNI", "12")))
    except (ValueError, TypeError):
        return 12

def ruleaza(_luni=None):
    n = _luni if _luni is not None else luni()
    try:
        db.pool()
    except Exception:
        db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM public.audit_log WHERE created_at < now() - make_interval(months => %s)", (n,))
            sterse = cur.rowcount
        conn.commit()
    return {"retentie_luni": n, "sterse": sterse}

if __name__ == "__main__":
    import json, datetime
    print("%s audit_retentie: %s" % (datetime.datetime.now().isoformat(timespec="seconds"), json.dumps(ruleaza())))
