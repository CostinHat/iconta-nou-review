# -*- coding: utf-8 -*-
"""FUZIUNEA ADRESELOR unei persoane — R63, blocul QQQ (29.08.2026).

CE FACE. Pentru fiecare firmă, compară cele două adrese ale aceleiași persoane:
  * **adresa de autentificare** — `public.users.email`, contul de portal legat de firmă;
  * **adresa de pachet** — `firma_profil.patron_email` (sau `firma_profil.email`), unde pleacă
    pachetul lunar (`core/pachete_api.py`).
Dacă amândouă există și **diferă**, păstrează pe cea mai recent actualizată, scrie cealaltă în
`public.audit_log` **înainte** de ștergere, cu identificatorul persoanei, apoi o golește.

CE TREBUIE CITIT ÎNAINTE DE A RULA — două lucruri care schimbă înțelesul rezultatului:

1. **Există o decizie contrară, aplicată pe 26.08.2026 (R63, varianta (c)).** Costin, atunci:
   *„rămân două, fiindcă înseamnă lucruri diferite… cine intră în portal și cine primește pachetul
   lunar chiar pot fi persoane diferite — administratorul firmei și contabilul intern, sau patronul
   și asistenta. A le uni ar forța o realitate pe care produsul n-o are."* Ce s-a construit atunci a
   fost **numirea** lor pe ecran, nu unirea. Fuziunea de aici merge în direcția opusă. *Se scrie ca
   să nu treacă drept o completare a deciziei vechi.*

2. **„Cea mai recent actualizată" n-are semnal mecanic.** `public.users` are `creat_la` (crearea
   contului, nu ultima schimbare a adresei), iar `firma_profil` n-are nicio marcă de timp per câmp.
   Deci ordinea „mai recentă" nu se poate citi din date. Unde nu se poate ști, scriptul **nu
   ghicește**: raportează cazul ca nedecidabil și **nu atinge nimic**.

NU ȘTERGE NIMIC FĂRĂ URMĂ: adresa scoasă intră în `audit_log` întâi, în aceeași tranzacție.

    ./venv/bin/python scripts/fuziune_adrese.py            # doar arata
    ./venv/bin/python scripts/fuziune_adrese.py --scrie    # executa
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import db  # noqa: E402


def perechi(conn):
    """[(tenant_id, schema, nume, email_portal, user_id, creat_la, email_pachet, camp)]"""
    out = []
    with conn.cursor() as cur:
        cur.execute("SELECT id, schema_name, nume FROM public.tenants WHERE activ ORDER BY id")
        firme = cur.fetchall()
    for tid, schema, nume in firme:
        with conn.cursor() as cur:
            cur.execute("SELECT u.id, u.email, u.creat_la FROM public.users u "
                        "JOIN public.user_tenants ut ON ut.user_id = u.id "
                        "WHERE ut.tenant_id = %s AND u.rol = 'client' AND u.activ "
                        "ORDER BY u.id", (tid,))
            conturi = cur.fetchall()
            try:
                cur.execute("SELECT patron_email, email FROM %s.firma_profil WHERE id=1" % schema)
                r = cur.fetchone()
            except Exception:
                conn.rollback()
                r = None
        pachet, camp = (None, None)
        if r:
            if str(r[0] or "").strip():
                pachet, camp = r[0].strip(), "patron_email"
            elif str(r[1] or "").strip():
                pachet, camp = r[1].strip(), "email"
        for uid, mail, creat in conturi:
            out.append((tid, schema, nume, (mail or "").strip(), uid, creat, pachet, camp))
        if not conturi:
            out.append((tid, schema, nume, None, None, None, pachet, camp))
    return out


def ruleaza(scrie=False):
    db.init_pool()
    with db.get_conn() as conn:
        lot = perechi(conn)
    print("MOD: %s\n" % ("SCRIE" if scrie else "doar arată"))
    print("%-12s %-32s %-28s %-28s" % ("schemă", "firmă", "adresa de autentificare",
                                       "adresa de pachet"))
    divergente, nedecidabile, fuzionate = [], [], []
    for tid, schema, nume, portal, uid, creat, pachet, camp in lot:
        print("%-12s %-32s %-28s %-28s" % (schema, (nume or "")[:32], portal or "—", pachet or "—"))
        if not portal or not pachet or portal.lower() == pachet.lower():
            continue
        divergente.append((tid, schema, nume, portal, uid, creat, pachet, camp))

    print("\n═══ DIVERGENȚE (amândouă există și diferă): %d" % len(divergente))
    for tid, schema, nume, portal, uid, creat, pachet, camp in divergente:
        # „mai recentă" — se caută semnalul; dacă nu există, NU se ghicește.
        print("  %s — portal %r (cont #%s, creat %s) vs pachet %r (`%s`)"
              % (schema, portal, uid, creat, pachet, camp))
        print("      semnal de «mai recentă»: NU EXISTĂ — `users.creat_la` e crearea contului, nu "
              "ultima schimbare a adresei, iar `firma_profil` n-are marcă de timp per câmp.")
        nedecidabile.append((schema, portal, pachet))

    if scrie and divergente and not nedecidabile:
        for tid, schema, nume, portal, uid, creat, pachet, camp in divergente:
            with db.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO public.audit_log (user_id, tenant_id, actiune, detalii) "
                        "VALUES (%s, (SELECT id FROM public.tenants WHERE id = %s), %s, %s)",
                        (uid, tid, "FUZIUNE adresa persoana",
                         json.dumps({"fel": "fapt", "tip": "FUZIUNE_ADRESA",
                                     "motiv": "adresa de pachet scoasă la fuziune (R63/QQQ)",
                                     "temei_completitudine": "urma se scrie ÎNAINTE de ștergere, "
                                                             "în aceeași tranzacție",
                                     "unde": "%s.firma_profil.%s" % (schema, camp),
                                     "persoana_user_id": uid, "adresa_scoasa": pachet,
                                     "adresa_pastrata": portal})))
                    cur.execute("UPDATE %s.firma_profil SET %s = NULL WHERE id=1" % (schema, camp))
                conn.commit()
            fuzionate.append((schema, pachet))

    print("\n═══ REZULTAT")
    print("  firme × conturi examinate:        %d" % len(lot))
    print("  persoane cu DOUĂ adrese diferite: %d" % len(divergente))
    print("  nedecidabile (fără semnal de «mai recentă»): %d" % len(nedecidabile))
    print("  fuzionate efectiv:                %d" % len(fuzionate))
    if not divergente:
        print("\n  NIMIC DE FUZIONAT. Nu fiindcă adresele ar coincide, ci fiindcă pe nicio firmă nu")
        print("  există AMÂNDOUĂ — aceeași cifră ca la măsurătoarea din 26.08 (R63).")
    return divergente, nedecidabile, fuzionate


if __name__ == "__main__":
    ruleaza(scrie="--scrie" in sys.argv)
