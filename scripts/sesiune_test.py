# -*- coding: utf-8 -*-
"""scripts/sesiune_test.py — sesiunea unui cont de TEST pentru parcursul verificatorului (comanda 16.3, pct.1). Aceeași funcție ca `sesiune` din frontend_test/e2e/conftest.py, dar fără pytest și fără
importurile relative ale plasei (conftest.py nu se importă în afara depozitului): rădăcina depozitului intră pe sys.path din variabila ICONTA_RAD (dată de lansator), iar mediul bazei de test se citește
din ~/.iconta/test.env și ~/.iconta/api_keys.env. Întoarce scriptul de sessionStorage care pune tokenul contului (`sesiune_pentru_user`, drumul aplicației).
  sesiune_test.py <email>     tipărește scriptul"""
import json
import os
import sys

TELEFON_TEST = "+40700000000"   # ca în conftest.py: contul de test a trecut de prima intrare
IMPLICIT = "dovada.71507@sesiuneab.test"


def _incarca_mediul():
    """Mediul serverului de lucru, ca în scripts/e2e_poarta.py::_env_test: baza de test (test.env) și cheile (api_keys.env: JWT_SECRET), ca tokenul să fie al aceluiași server."""
    for cale in ("~/.iconta/test.env", "~/.iconta/api_keys.env"):
        for linie in open(os.path.expanduser(cale), encoding="utf-8"):
            linie = linie.strip()
            if linie.startswith("export "):
                linie = linie[7:]
            if "=" in linie and not linie.startswith("#"):
                k, v = linie.split("=", 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")


def sesiune(email=IMPLICIT, prima_intrare=False):
    rad = os.environ.get("ICONTA_RAD") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if rad not in sys.path:
        sys.path.insert(0, rad)
    _incarca_mediul()
    from core import auth_api, db
    try:
        db.init_pool()
    except Exception:  # noqa: BLE001 — deja inițializat
        pass
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM public.users WHERE email=%s", (email,))
            u = cur.fetchone()
            if u and not prima_intrare:
                cur.execute("UPDATE public.users SET telefon = COALESCE(telefon, %s), notificari_salvate_la = COALESCE(notificari_salvate_la, now()) WHERE id = %s", (TELEFON_TEST, u[0]))
                conn.commit()
        s = auth_api.sesiune_pentru_user(conn, u[0]) if u else None
        conn.rollback()
    assert s and s.get("ok"), "contul de test %s nu e disponibil" % email
    return ("sessionStorage.setItem('iconta_token'," + json.dumps(s["token"]) + ");"
            "sessionStorage.setItem('iconta_user'," + json.dumps(json.dumps(s["user"])) + ");")


if __name__ == "__main__":
    print(sesiune(sys.argv[1] if len(sys.argv) > 1 else IMPLICIT))
