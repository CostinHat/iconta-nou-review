# -*- coding: utf-8 -*-
"""LOTUL 15 — desfacerea starii pe care probele au lasat-o, obiect cu obiect, NUMIT.

`curata_proba_ecrane.py` desface INSERT-urile care poarta semnatura; ce ramane e aici, si fiecare
rand spune de ce nu putea fi acolo:

 1. `tenant_003.firma_profil.wc_*` — MODIFICARE, deci unealta generica refuza (corect). Valoarea
    de dinainte nu se ia din memorie: se ia din CE ARATA ECRANUL inainte de proba — deschizatorul
    apasat de sonda a fost «Configurează magazinul», adica ramura `!cfg.configurat`, iar
    `configurat = url ȘI chei`. Starea observata era „neconfigurat"; se pune la loc exact aia.
 2. `public.declaratii_coada` 8149 — proba dialogului de motiv (#498) a RESPINS un element real.
    Se pune la loc starea de dinainte (`la_senior`, randata de lista „De depus" cu «Renunță»).
 3. povestea lunii scrisa cu santinela in proba modalului `pachete` (#486).
 4. fixturile lotului: mijlocul fix `MF-PROBA-L15` + nota lui, sesizarea `PROBA LOT 15` + mesajele.

Ce NU se sterge, si se spune: nimic altceva. Daca vreun numar ramane mutat, se scrie in raport.
"""
import sys

sys.path.insert(0, "/home/costin/iconta_nou")
from core import db  # noqa: E402

SEMNATURA = "«»@#$%"
COD_MF = "MF-PROBA-L15"
SUBIECT = "PROBA LOT 15"
COADA = 8149

db.init_pool()
with db.get_conn() as conn, conn.cursor() as cur:
    cur.execute("UPDATE tenant_003.firma_profil SET wc_url=NULL, wc_ck=NULL, wc_cs=NULL "
                "WHERE wc_url=%s OR wc_ck=%s OR wc_cs=%s", (SEMNATURA, SEMNATURA, SEMNATURA))
    print("1. firma_profil.wc_* -> NULL:", cur.rowcount)

    cur.execute("SELECT stare, motiv_respingere FROM public.declaratii_coada WHERE id=%s", (COADA,))
    print("2. coada %d, inainte: %s" % (COADA, cur.fetchone()))
    cur.execute("UPDATE public.declaratii_coada SET stare='la_senior', motiv_respingere=NULL, "
                "respins_la=NULL, respins_de=NULL, respins_de_id=NULL "
                "WHERE id=%s AND motiv_respingere=%s", (COADA, SEMNATURA))
    print("   pus la loc:", cur.rowcount)

    cur.execute("SELECT table_name FROM information_schema.tables "
                "WHERE table_schema='public' AND table_name LIKE '%%poveste%%'")
    tabele = [r[0] for r in cur.fetchall()]
    for t in tabele:
        cur.execute("DELETE FROM public.%s WHERE text=%%s" % t, (SEMNATURA,))
        print("3. %s -> sterse %d" % (t, cur.rowcount))

    cur.execute("DELETE FROM tenant_003.mijloace_fixe WHERE cod=%s", (COD_MF,))
    print("4. mijloace_fixe:", cur.rowcount)
    cur.execute("SELECT id FROM tenant_003.inregistrari WHERE descriere ILIKE %s",
                ("%Plus la inventar mijloace fixe%",))
    note = [r[0] for r in cur.fetchall()]
    if note:
        cur.execute("DELETE FROM tenant_003.inregistrari_linii WHERE inregistrare_id = ANY(%s)", (note,))
        print("   linii:", cur.rowcount)
        cur.execute("DELETE FROM tenant_003.inregistrari WHERE id = ANY(%s)", (note,))
        print("   note:", cur.rowcount, note)
    cur.execute("SELECT id FROM public.raportari WHERE subiect=%s", (SUBIECT,))
    rap = [r[0] for r in cur.fetchall()]
    if rap:
        cur.execute("DELETE FROM public.raportari_mesaje WHERE raportare_id = ANY(%s)", (rap,))
        print("   raportari_mesaje:", cur.rowcount)
        cur.execute("DELETE FROM public.raportari WHERE id = ANY(%s)", (rap,))
        print("   raportari:", cur.rowcount, rap)
    conn.commit()

# VERIFICAREA: nu se afirma ca s-a curatat — se RECITESTE starea.
with db.get_conn() as conn, conn.cursor() as cur:
    cur.execute("SELECT wc_url, wc_ck, wc_cs FROM tenant_003.firma_profil")
    print("\nverificare firma_profil:", cur.fetchall())
    cur.execute("SELECT id, stare, motiv_respingere FROM public.declaratii_coada WHERE id=%s", (COADA,))
    print("verificare coada:", cur.fetchall())
    cur.execute("SELECT count(*) FROM tenant_003.registratura")
    print("verificare registratura (randuri):", cur.fetchone()[0])
    cur.execute("SELECT count(*) FROM tenant_003.mijloace_fixe WHERE cod=%s", (COD_MF,))
    print("verificare mijloace_fixe MF-PROBA-L15:", cur.fetchone()[0])
    cur.execute("SELECT count(*) FROM public.raportari WHERE subiect=%s", (SUBIECT,))
    print("verificare raportari PROBA LOT 15:", cur.fetchone()[0])
    conn.rollback()
