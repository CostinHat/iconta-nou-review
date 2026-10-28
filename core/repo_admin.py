# -*- coding: utf-8 -*-
"""REPOSITORY — panoul de administrare: sănătate, activitate, anunțuri, evenimente publice.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:842`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""
from core import audit_automat as _audit_automat   # [715, 14.2] cererile de pornire ale ecranelor nu sunt „acțiuni” (regula, la citire)


#: [C101, lotul 12] contoarele de REZULTAT ale Panoului Admin (facturi emise, declarații depuse, recomandări) numără numai cererile
#: reușite: rândul de audit al unei cereri (`main._inregistreaza_activitate`) se scrie pentru orice răspuns, cu statusul în
#: `detalii.status`, deci o emitere refuzată (422) apărea „factură emisă”. Numai 2xx; un rând fără status nu e o reușită dovedită.
#: Activitatea (ultima acțiune, acțiunile, autentificările) rămâne numărată pe toate rândurile: o cerere refuzată tot e o acțiune.
#: Condiția e un fragment de SQL cu aliasul rândului de audit (`_REUSITA % "a2"`), nu o funcție: funcțiile unui repository primesc
#: cursorul apelantului (`core/test_p7_v1_citiri.py::test_fiecare_functie_de_repository_primeste_cursorul`).
_REUSITA = "(%s.detalii->>'status') ~ '^2[0-9][0-9]$'"


#: [lotul 13, găsită la e2e-ul integrat] Interogarea făcea `LEFT JOIN audit_log` pe toate rândurile, grupat pe cabinet, PLUS trei
#: subinterogări cu `LIKE` (o parcurgere a jurnalului de audit pe fiecare cabinet, pentru fiecare contor): 22 s pe baza de test (3,1 milioane
#: de rânduri de audit, 8 cabinete), peste termenul de 30 s al probei sub sarcină — Panou Admin → Activitate cabinete și centralizatorul
#: superadminului se încărcau greu sau deloc. Acum jurnalul se parcurge O SINGURĂ DATĂ (`pe_cabinet`), cu toate contoarele ca agregate
#: filtrate; aceleași cifre (`core/test_lot12_notif_c101_contoare_admin.py`, `core/test_lot13_admin_suspendare.py`).
def activitate_pe_cabinete(cur):
    cur.execute("""
                WITH pe_cabinet AS (
                    SELECT u.accounting_firm_id AS cabinet_id,
                           COUNT(*) FILTER (WHERE a.actiune LIKE 'POST /recomanda%%' AND """ + _REUSITA % "a" + """) AS nr_recomandari,
                           COUNT(*) FILTER (WHERE a.actiune LIKE '%%/facturi/emite%%' AND """ + _REUSITA % "a" + """) AS nr_facturi,
                           COUNT(*) FILTER (WHERE a.actiune LIKE '%%/depune%%' AND """ + _REUSITA % "a" + """) AS nr_declaratii,  -- ICRD_CABINETE_CATEGORII_V1
                           MAX(a.created_at) AS ultima_activitate,
                           MAX(a.created_at) FILTER (WHERE a.actiune = 'login') AS ultim_login,
                           COUNT(*) AS nr_actiuni,
                           COUNT(*) FILTER (WHERE a.actiune = 'login') AS nr_logari
                      FROM public.audit_log a JOIN public.users u ON u.id = a.user_id
                     WHERE u.accounting_firm_id IS NOT NULL
                       AND """ + _audit_automat.sql_actiune_omului("a") + """   -- [715, 14.2] cererile de pornire ale ecranelor nu sunt acțiuni
                     GROUP BY u.accounting_firm_id)
                SELECT f.id, f.nume, f.activ, f.creat_la,
                       -- [15.10.2026, lotul 4 pct.4] pe ce cale a venit cabinetul (invitația lui sau înregistrarea liberă confirmată)
                       CASE WHEN EXISTS (SELECT 1 FROM public.invitatii_cabinet ic WHERE ic.firm_id = f.id) THEN 'invitație'
                            WHEN EXISTS (SELECT 1 FROM public.inregistrari_in_asteptare ia WHERE ia.firm_id = f.id)
                                 THEN 'înregistrare liberă' END AS cale,
                       (SELECT COUNT(*) FROM public.tenants t WHERE t.accounting_firm_id = f.id) AS nr_firme,
                       -- [lotul 13, 644 b] conturile de utilizator ale cabinetului (administrator + asistenți), nu salariații firmelor
                       (SELECT COUNT(*) FROM public.users u2 WHERE u2.accounting_firm_id = f.id
                          AND u2.activ = true AND u2.rol IN ('admin_firma','angajat')) AS nr_utilizatori,
                       -- [lotul 13, 645] motivul suspendării deschise (NULL = activ, sau suspendat înainte de jurnal)
                       (SELECT s.motiv FROM public.suspendari_cabinet s WHERE s.cabinet_id = f.id AND s.reactivat_la IS NULL) AS motiv_suspendare,
                       (SELECT s.suspendat_la FROM public.suspendari_cabinet s WHERE s.cabinet_id = f.id AND s.reactivat_la IS NULL) AS suspendat_la,
                       COALESCE(p.nr_recomandari, 0) AS nr_recomandari, COALESCE(p.nr_facturi, 0) AS nr_facturi,
                       COALESCE(p.nr_declaratii, 0) AS nr_declaratii, p.ultima_activitate, p.ultim_login,
                       COALESCE(p.nr_actiuni, 0) AS nr_actiuni, COALESCE(p.nr_logari, 0) AS nr_logari
                FROM public.accounting_firms f
                LEFT JOIN pe_cabinet p ON p.cabinet_id = f.id
                ORDER BY f.nume
            """, _audit_automat.PARAM_OMULUI)
    return cur.fetchall()


def ultimele_actiuni(cur):
    cur.execute("""
                    SELECT id, actiune, tenant_id, user_id, created_at, detalii
                    FROM public.audit_log
                    WHERE created_at > now() - interval '24 hours'
                      AND (detalii->>'status')::int >= 500
                    ORDER BY created_at DESC
                """)
    return cur.fetchall()


def actiunile_cabinetului(cur, firm_id, limita):
    cur.execute("""
                SELECT a.id, a.actiune, a.tenant_id, a.created_at, u.nume, u.prenume
                FROM public.audit_log a
                JOIN public.users u ON u.id = a.user_id
                WHERE u.accounting_firm_id = %s
                  AND """ + _audit_automat.sql_actiune_omului("a") + """   -- [715, 14.2]
                ORDER BY a.created_at DESC
                LIMIT %s
            """,
                (firm_id, *_audit_automat.PARAM_OMULUI, limita))
    return cur.fetchall()


def marimea_bazei(cur):
    cur.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
    return cur.fetchone()


def conexiuni_active(cur):
    cur.execute("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()")
    return cur.fetchone()


def alerte_fiscale(cur):
    # [lotul 13, 646 b] cu data publicării actului și data intrării în vigoare (propunerile monitorului fiscal)
    cur.execute("""SELECT id, sursa, titlu, rezumat, url, relevanta, creat_la, data_publicarii, data_vigoare
                       FROM public.alerte_fiscale WHERE NOT vazut AND sursa NOT IN ('anaf_buletin', 'portal_act') ORDER BY id DESC LIMIT 30""")
    return cur.fetchall()


def anunturi_pentru_cabinet(cur, firm_id):
    # [lotul 13, 646 c-d] fără cele retrase de Admin iConta; cu data trimiterii / afișării (fereastra anunțului o arată)
    cur.execute("""SELECT id, mesaj, creat_la, data_afisare FROM public.anunturi_cabinet
                       WHERE cabinet_id=%s AND confirmat_la IS NULL AND retras_la IS NULL
                         AND (data_afisare IS NULL OR data_afisare <= CURRENT_DATE) ORDER BY id""",
                (firm_id,))
    return cur.fetchall()


def anunturi_trimise(cur, limita=100):
    """[lotul 13, 646 c] Trimiterile de anunțuri, cele mai noi întâi: mesajul, când, de cine, câte cabinete, câte l-au citit, retragerea."""
    cur.execute("""SELECT COALESCE(a.lot, a.id) AS lot, MIN(a.mesaj) AS mesaj, MIN(a.creat_la) AS creat_la, MIN(a.data_afisare) AS data_afisare,
                          MAX(a.retras_la) AS retras_la, MIN(a.trimis_de) AS trimis_de_id,
                          NULLIF(TRIM(COALESCE(MIN(u.prenume), '') || ' ' || COALESCE(MIN(u.nume), '')), '') AS trimis_de,
                          COUNT(*) AS destinatari, COUNT(a.confirmat_la) AS citite
                     FROM public.anunturi_cabinet a
                     LEFT JOIN public.users u ON u.id = a.trimis_de
                    GROUP BY COALESCE(a.lot, a.id)
                    ORDER BY MIN(a.creat_la) DESC, COALESCE(a.lot, a.id) DESC
                    LIMIT %s""", (limita,))
    return cur.fetchall()


def destinatarii_trimiterii(cur, lot):
    """[646 c] Cabinetele unei trimiteri: numele, dacă a citit (`confirmat_la`)."""
    cur.execute("""SELECT f.nume, a.confirmat_la FROM public.anunturi_cabinet a
                     LEFT JOIN public.accounting_firms f ON f.id = a.cabinet_id
                    WHERE COALESCE(a.lot, a.id) = %s ORDER BY f.nume""", (lot,))
    return cur.fetchall()


def retrage_trimiterea(cur, lot):
    """[646 c] Retragerea: anunțul nu se mai arată cabinetelor care nu l-au citit. Întoarce câte rânduri s-au retras."""
    cur.execute("UPDATE public.anunturi_cabinet SET retras_la = now() WHERE COALESCE(lot, id) = %s AND retras_la IS NULL", (lot,))
    return cur.rowcount


def leaga_trimiterea(cur, ids):
    """[646 c] Rândurile scrise de aceeași trimitere primesc `lot` = cel mai mic id dintre ele."""
    if ids:
        cur.execute("UPDATE public.anunturi_cabinet SET lot = %s WHERE id = ANY(%s)", (min(ids), list(ids)))


def istoric_sanatate(cur, ore):
    cur.execute("""
                SELECT ram_procent, disc_procent, load1, load15, conexiuni_db, erori_noi, creat_la   -- [lotul 13, 643] load15: baza alertei
                FROM public.metrici_sanatate
                WHERE creat_la > now() - (%s || ' hours')::interval
                ORDER BY creat_la ASC
            """,
                (ore,))
    return cur.fetchall()


def evenimente_pe_tip(cur, zile):
    cur.execute("SELECT tip, COUNT(*) AS n FROM public.eveniment_public "
                    "WHERE creat_la >= now() - (%s || ' days')::interval GROUP BY tip ORDER BY n DESC",
                (zile,))
    return cur.fetchall()


def evenimente_pe_zi(cur, zile):
    cur.execute("SELECT to_char(date_trunc('day', creat_la), 'YYYY-MM-DD') AS zi, COUNT(*) AS n "
                    "FROM public.eveniment_public WHERE creat_la >= now() - (%s || ' days')::interval "
                    "GROUP BY 1 ORDER BY 1 DESC",
                (zile,))
    return cur.fetchall()


def evenimente_pe_pagina(cur, zile):
    cur.execute("SELECT COALESCE(NULLIF(pagina,''),'landing') AS pagina, COUNT(*) AS n "
                    "FROM public.eveniment_public WHERE creat_la >= now() - (%s || ' days')::interval "
                    "GROUP BY 1 ORDER BY n DESC LIMIT 100",
                (zile,))
    return cur.fetchall()


def cate_evenimente(cur, zile):
    cur.execute("SELECT COUNT(*) AS n FROM public.eveniment_public "
                    "WHERE creat_la >= now() - (%s || ' days')::interval",
                (zile,))
    return cur.fetchone()


# ── P7 · V2: scrierile, mutate din rute ──────────────────────────────

def adauga_anunt(cur, cabinet_id, mesaj, data_afisare, trimis_de=None):
    """Un rând de anunț pentru un cabinet. Întoarce id-ul (trimiterea se leagă apoi cu `leaga_trimiterea`)."""
    cur.execute("INSERT INTO public.anunturi_cabinet (cabinet_id, mesaj, data_afisare, trimis_de) VALUES (%s,%s,%s,%s) RETURNING id",
                (cabinet_id, mesaj, data_afisare, trimis_de))
    return cur.fetchone()[0]


def marcheaza_alerta_vazuta(cur, id_):
    cur.execute("UPDATE public.alerte_fiscale SET vazut=true WHERE id=%s RETURNING id",
                (id_,))
    return cur.fetchone()


def confirma_anunt(cur, id_, cabinet_id):
    cur.execute("""UPDATE public.anunturi_cabinet SET confirmat_la=now()
                       WHERE id=%s AND cabinet_id=%s AND confirmat_la IS NULL RETURNING id""",
                (id_, cabinet_id))
    return cur.fetchone()


def scrie_audit_cu_detalii(cur, user_id, actiune, entitate, entitate_id):
    cur.execute("INSERT INTO public.audit_log (user_id, actiune, entitate, entitate_id, detalii) "
                    "VALUES (%s,'gdpr_export',%s,%s,%s)",
                (user_id, actiune, entitate, entitate_id))


def scrie_audit_login(cur, user_id):
    cur.execute("INSERT INTO public.audit_log (user_id, actiune) VALUES (%s,'login')",
                (user_id,))


def scrie_audit_reset_cerut(cur, user_id):
    cur.execute("INSERT INTO public.audit_log (user_id, actiune) VALUES (%s,'reset_parola_cerut')",
                (user_id,))


def scrie_audit_reset_schimbat(cur, user_id):
    cur.execute("INSERT INTO public.audit_log (user_id, actiune) VALUES (%s,'reset_parola_schimbat')",
                (user_id,))


def scrie_eveniment_public(cur, tip, pagina):
    cur.execute("INSERT INTO public.eveniment_public (tip, pagina) VALUES (%s, %s)",
                (tip, pagina))


def schema_exista(cur, schema):
    """[lotul 10, eroarea 500 din `/eu/ciorne`] Schema firmei există încă în bază (`pg_namespace`)?"""
    cur.execute("SELECT 1 FROM pg_namespace WHERE nspname = %s", (schema,))
    return cur.fetchone() is not None


# ── [lotul 13, deficiența 645] jurnalul suspendărilor unui cabinet (`public.suspendari_cabinet`, core/migrare_suspendari_cabinet.py) ──

def suspendarea_deschisa(cur, cabinet_id):
    """(motiv, suspendat_la) al suspendării deschise a cabinetului, sau None. `motiv` NULL = suspendat înainte de jurnal."""
    cur.execute("SELECT motiv, suspendat_la FROM public.suspendari_cabinet WHERE cabinet_id = %s AND reactivat_la IS NULL",
                (cabinet_id,))
    return cur.fetchone()


def deschide_suspendarea(cur, cabinet_id, motiv, nota_interna, user_id):
    """Rândul jurnalului pentru o suspendare nouă. Întoarce (id, suspendat_la), sau None dacă cabinetul are deja o suspendare deschisă
    (indexul unic parțial `suspendari_cabinet_deschisa`: două suspendări simultane — a doua nu scrie nimic, apelantul o refuză)."""
    cur.execute("INSERT INTO public.suspendari_cabinet (cabinet_id, motiv, nota_interna, suspendat_de) VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (cabinet_id) WHERE reactivat_la IS NULL DO NOTHING RETURNING id, suspendat_la",
                (cabinet_id, motiv, nota_interna, user_id))
    r = cur.fetchone()
    return tuple(r) if r else None


def inchide_suspendarea(cur, cabinet_id, user_id):
    """Reactivarea: suspendarea deschisă a cabinetului primește cine și când. Întoarce id-ul rândului închis (None dacă n-avea)."""
    cur.execute("UPDATE public.suspendari_cabinet SET reactivat_de = %s, reactivat_la = now() "
                " WHERE cabinet_id = %s AND reactivat_la IS NULL RETURNING id", (user_id, cabinet_id))
    r = cur.fetchone()
    return r[0] if r else None


def scrie_emailurile_suspendarii(cur, suspendare_id, n):
    cur.execute("UPDATE public.suspendari_cabinet SET emailuri_trimise = %s WHERE id = %s", (n, suspendare_id))


def jurnalul_suspendarilor(cur, cabinet_id):
    """Suspendările cabinetului, cele mai noi întâi, cu numele celor care au suspendat / reactivat."""
    cur.execute("""SELECT s.id, s.motiv, s.nota_interna, s.suspendat_la, s.reactivat_la, s.emailuri_trimise,
                          NULLIF(TRIM(COALESCE(us.prenume, '') || ' ' || COALESCE(us.nume, '')), '') AS suspendat_de,
                          NULLIF(TRIM(COALESCE(ur.prenume, '') || ' ' || COALESCE(ur.nume, '')), '') AS reactivat_de
                     FROM public.suspendari_cabinet s
                     LEFT JOIN public.users us ON us.id = s.suspendat_de
                     LEFT JOIN public.users ur ON ur.id = s.reactivat_de
                    WHERE s.cabinet_id = %s ORDER BY s.id DESC""", (cabinet_id,))
    return cur.fetchall()


def adminii_cabinetului(cur, cabinet_id):
    """[(email, prenume, nume)] — administratorii activi ai cabinetului (destinatarii emailului de suspendare)."""
    cur.execute("SELECT email, prenume, nume FROM public.users WHERE accounting_firm_id = %s AND rol = 'admin_firma' AND activ "
                "AND email IS NOT NULL ORDER BY id", (cabinet_id,))
    return cur.fetchall()


def numele_cabinetului(cur, cabinet_id):
    cur.execute("SELECT nume FROM public.accounting_firms WHERE id = %s", (cabinet_id,))
    r = cur.fetchone()
    return r[0] if r else None
