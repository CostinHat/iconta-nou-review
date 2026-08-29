# -*- coding: utf-8 -*-
"""PROBA că un eșec de trimitere a emailului LASĂ URMĂ — R73, blocul TTT3 (29.08.2026).

CE PROBEAZĂ, și de ce nu e redundant cu gardul. `core/test_esec_trimitere_email.py` verifică
**structural**, pe AST, că fiecare `except` din jurul unui `trimite_email_html` cheamă
`esec_secundar` — deci că apelul e acolo. Aici se **provoacă eșecul** și se citește ce iese: ruta
răspunde normal, iar urma apare. *Un apel scris și o urmă care apare nu sunt același lucru.*

CUM: `observare.trimite_email_html` e înlocuit cu o funcție care ridică. `observare.alerteaza` e
înlocuit și el — altfel `esec_secundar(alerta=True)` ar trimite alerte REALE prin Brevo la fiecare
rulare a probei. Ieșirea standard se capturează și se caută eticheta.

CE NU SE EXERCITĂ, declarat: **emailul de bun venit la înregistrarea unui cabinet**. Ruta creează un
cabinet întreg, cu schemă de tenant — pe instalarea asta ar lăsa urme pe care nu le pot curăța fără
să ating `tenant_stergere` (care, la R79, își produce propriul orfan). Rămâne acoperit structural, de
gardă. *Se scrie, nu se ascunde în „3 din 3".*

NU LASĂ URME: utilizatorii creați de probă se șterg în `finally`, cu tot ce atârnă de ei.

    ./venv/bin/python scripts/proba_esec_email.py
"""
import contextlib
import io as _io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main  # noqa: E402
from core import db, observare as _obs  # noqa: E402

EMAIL = "proba-ttt3@iconta.test"            # cont de CABINET — resetarea de parolă
EMAIL_CLIENT = "proba-ttt3-client@iconta.test"   # cont de CLIENT — linkul de logare
EMAIL_ASIST = "proba-ttt3-asistent@iconta.test"


class _Cerere:
    """Minimul de care are nevoie limitatorul de rată: o adresă de client."""
    class client:
        host = "127.0.0.1"
    headers = {}


def _pregateste():
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM public.accounting_firms ORDER BY id LIMIT 1")
            cabinet = cur.fetchone()[0]
            # DOUĂ conturi, fiindcă cele două căi servesc doi oameni diferiți:
            # `cere_reset` întoarce (None, None) pentru rol `client` — *„clientii au magic-link,
            # nu parola"* —, deci un singur cont n-ar fi atins amândouă ramurile.
            cur.execute("INSERT INTO public.users (email, password_hash, nume, rol, "
                        "accounting_firm_id, activ) VALUES (%s,'x','PROBA TTT3','admin_firma',%s,"
                        "true) RETURNING id", (EMAIL, cabinet))
            uid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email, password_hash, nume, rol, "
                        "accounting_firm_id, activ) VALUES (%s,'x','PROBA TTT3 CLIENT','client',%s,"
                        "true)", (EMAIL_CLIENT, cabinet))
        conn.commit()
    return uid, cabinet


def _curata(uid):
    sters = 0
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            for tabel, coloana in (("public.user_tenants", "user_id"),
                                   ("public.audit_log", "user_id")):
                try:
                    cur.execute("DELETE FROM %s WHERE %s IN (SELECT id FROM public.users "
                                "WHERE email IN (%%s,%%s,%%s))" % (tabel, coloana),
                                (EMAIL, EMAIL_CLIENT, EMAIL_ASIST))
                except Exception:
                    conn.rollback()
            cur.execute("DELETE FROM public.reset_parola_token WHERE user_id IN "
                        "(SELECT id FROM public.users WHERE email IN (%s,%s,%s))",
                        (EMAIL, EMAIL_CLIENT, EMAIL_ASIST))
            cur.execute("DELETE FROM public.users WHERE email IN (%s,%s,%s)",
                        (EMAIL, EMAIL_CLIENT, EMAIL_ASIST))
            sters = cur.rowcount
        conn.commit()
    return sters


def _ruleaza_captand(fn):
    """Rulează, cu trimiterea stricată și cu alerta oprită. Întoarce (rezultat|excepție, ieșire)."""
    def _crapa(*a, **k):
        raise RuntimeError("SMTP indisponibil (probă TTT3)")

    alerte = []
    vechi_t, vechi_a = _obs.trimite_email_html, _obs.alerteaza
    _obs.trimite_email_html = _crapa
    _obs.alerteaza = lambda cheie, subiect, mesaj, acum=None: alerte.append(cheie) or True
    buf = _io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            try:
                r = fn()
            except Exception as e:
                r = "EXCEPȚIE %s: %s" % (type(e).__name__, str(e)[:80])
    finally:
        _obs.trimite_email_html, _obs.alerteaza = vechi_t, vechi_a
    return r, buf.getvalue(), alerte


def ruleaza():
    db.init_pool()
    uid, cabinet = _pregateste()
    rez = []
    try:
        # 1. resetarea parolei — cale de acces, cu alertă
        r, iesire, alerte = _ruleaza_captand(
            lambda: main.reset_parola_cere(main.ResetCereIn(email=EMAIL), _Cerere()))
        rez.append(("resetare parolă", "email resetare parola", r, iesire, alerte, True))

        # 2. linkul de logare — singura ușă a portalului, cu alertă
        r, iesire, alerte = _ruleaza_captand(
            lambda: main.magic_link_cere(main.MagicCereIn(email=EMAIL_CLIENT), _Cerere()))
        rez.append(("link de logare", "email link de logare", r, iesire, alerte, True))

        # 3. invitația de asistent — cale de acces, cu alertă
        # `_cer_admin_cabinet` citește `ctx["firm"]` — numele se ia din cod, nu din memorie.
        ctx = {"uid": uid, "rol": "admin_firma", "firm": cabinet}
        r, iesire, alerte = _ruleaza_captand(
            lambda: main.asistent_creeaza(
                main.AsistentNouIn(email=EMAIL_ASIST, nume="PROBA TTT3"), ctx))
        rez.append(("invitație asistent", "email invitatie asistent", r, iesire, alerte, True))
    finally:
        sterse = _curata(uid)

    print("PROBĂ TTT3 — se provoacă eșecul trimiterii, se citește urma\n")
    ok_total = True
    for eticheta, urma, r, iesire, alerte, cere_alerta in rez:
        gasit = ("[esec secundar: %s]" % urma) in iesire
        alertat = bool(alerte)
        ok = gasit and (alertat if cere_alerta else True) and not str(r).startswith("EXCEPȚIE")
        ok_total = ok_total and ok
        print("%s  %s" % ("[x]" if ok else "[ ]", eticheta))
        print("        ruta a răspuns: %s" % str(r)[:70])
        print("        urmă în log: %s%s" % ("DA" if gasit else "NU",
                                             ("  ·  alertă: %s" % alerte) if alerte else ""))
        if iesire.strip():
            print("        ieșire: %s" % iesire.strip().splitlines()[0][:110])
    print("\n[ ]  email bun venit cabinet — NEEXERCITAT: ruta creează un cabinet întreg, cu schemă")
    print("        de tenant. Acoperit structural de `core/test_esec_trimitere_email.py`; se spune,")
    print("        nu se ascunde într-un «3 din 3».")
    print("\n═══ VERDICT")
    print("  căi de intrare probate: %d din 3 · a patra trimitere (bun venit) rămâne neexercitată"
          % sum(1 for _e, _u, _r, i, a, _c in rez if ("[esec secundar" in i)))
    print("  utilizatori de probă șterși: %d" % sterse)
    return ok_total


if __name__ == "__main__":
    sys.exit(0 if ruleaza() else 1)
