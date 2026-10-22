# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d205.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d205.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_firma_profil(cur):
    cur.execute("SELECT nume, cui, adresa, oras, judet, "
                "declarant_nume, declarant_prenume, declarant_functie "
                "FROM firma_profil WHERE id = 1")
    return cur.fetchone()


def select_asociati(cur):
    cur.execute("SELECT nume, cnp, cota FROM asociati WHERE cota > 0")
    return cur.fetchall()


def select_asociati_istoric(cur):
    """[lot 19 pct.4e] Structurile anterioare ale asociaților (cesiuni), cu data până la care au fost valabile."""
    cur.execute("SELECT cnp, nume, cota, valabil_pana_la FROM asociati_istoric ORDER BY valabil_pana_la, cnp")
    return cur.fetchall()


#: [lotul 10, deficiența 431] coloanele mișcărilor de dividende pe NOTĂ — anualele pe 457, interimarele pe 456 (din 463); vezi
#: `dividende_curs._transe`
_MISCARI_DIVIDENDE = (
    "COALESCE(SUM(CASE WHEN l.cont_credit LIKE '457%%' THEN l.suma ELSE 0 END),0) AS distribuit, "
    "COALESCE(SUM(CASE WHEN l.cont_debit LIKE '457%%' AND l.cont_credit LIKE '446%%' THEN l.suma ELSE 0 END),0) AS impozit, "
    "COALESCE(SUM(CASE WHEN l.cont_debit LIKE '457%%' AND l.cont_credit NOT LIKE '463%%' AND l.cont_credit NOT LIKE '446%%' "
    "THEN l.suma ELSE 0 END),0) AS platit, "
    "COALESCE(SUM(CASE WHEN l.cont_debit LIKE '457%%' AND l.cont_credit LIKE '463%%' THEN l.suma ELSE 0 END),0) AS compensat, "
    "COALESCE(SUM(CASE WHEN l.cont_credit LIKE '456%%' AND l.cont_debit LIKE '463%%' THEN l.suma ELSE 0 END),0) AS distribuit_interimar, "
    "COALESCE(SUM(CASE WHEN l.cont_debit LIKE '456%%' AND l.cont_credit LIKE '446%%' THEN l.suma ELSE 0 END),0) AS impozit_interimar, "
    "COALESCE(SUM(CASE WHEN l.cont_debit LIKE '456%%' AND (l.cont_credit LIKE '512%%' OR l.cont_credit LIKE '531%%') "
    "THEN l.suma ELSE 0 END),0) AS platit_interimar ")
_LINII_DIVIDENDE = ("(l.cont_credit LIKE '457%%' OR l.cont_debit LIKE '457%%' "
                    "OR (l.cont_credit LIKE '456%%' AND l.cont_debit LIKE '463%%') OR l.cont_debit LIKE '456%%')")


def select_dividende_miscari(cur, _sf):
    """[A6] Mișcările de dividende pe NOTĂ, cu DATA, din tot registrul până la `_sf` (sfârșitul anului declarației,
    exclusiv): credit 457 = distribuire, 457 = 446 = impozitul înregistrat, celălalt debit 457 = plata netului, 457 = 463 =
    compensarea cu interimarele; [lotul 10, deficiența 431] interimarele pe 456 (463 = 456 distribuire, 456 = 446 impozitul,
    456 = 512x / 531x plata netului). Ordonate cronologic pentru atribuirea FIFO
    plată->distribuire (cota se ia după data distribuirii). Include distribuirile din ANII ANTERIORI, ca o plată de la începutul
    anului să se lege de distribuirea ei reală (Legea 141/2025 art.VII)."""
    cur.execute("SELECT i.data, " + _MISCARI_DIVIDENDE +
                "FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status='validata' AND " + _LINII_DIVIDENDE + " AND i.data < %s "
                "GROUP BY i.id, i.data ORDER BY i.data, i.id", (_sf.isoformat(),))
    return cur.fetchall()


def select_note_dividende_nevalidate(cur, _inc, _sf):
    """[lotul 10, deficiența 431] Notele de dividende NEVALIDATE din anul declarației (ciornă / la validare): D205 le ignoră
    (preia numai notele validate), iar refuzul le numește. [(id, data, status, suma distribuită)] în ordinea Registrului jurnal."""
    cur.execute("SELECT i.id, i.data, i.status, COALESCE(SUM(CASE WHEN l.cont_credit LIKE '457%%' OR "
                "(l.cont_credit LIKE '456%%' AND l.cont_debit LIKE '463%%') THEN l.suma ELSE 0 END),0) AS suma "
                "FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status <> 'validata' AND " + _LINII_DIVIDENDE + " AND i.data >= %s AND i.data < %s "
                "GROUP BY i.id, i.data, i.status HAVING SUM(CASE WHEN l.cont_credit LIKE '457%%' OR l.cont_debit LIKE '457%%' OR "
                "(l.cont_credit LIKE '456%%' AND l.cont_debit LIKE '463%%') THEN l.suma ELSE 0 END) > 0 "
                "ORDER BY i.data, i.id", (_inc.isoformat(), _sf.isoformat()))
    return cur.fetchall()


def select_457_preluat(cur, _sf):
    """[lotul 10, decizia Costin A — generalizarea pe clasă] Soldul creditor al lui 457 din balanța de deschidere, pe data ei de
    referință, înainte de `_sf`: dividendele distribuite înainte de evidența din iConta.eu și neplătite la preluare
    (`dividende_curs._transe`, cheia `preluat`). [(data_referinta, sold)] cu sold > 0, cronologic."""
    cur.execute("SELECT data_referinta AS data, SUM(sold_creditor - sold_debitor) AS preluat FROM solduri_initiale "
                "WHERE cont LIKE '457%%' AND data_referinta IS NOT NULL AND data_referinta < %s "
                "GROUP BY data_referinta HAVING SUM(sold_creditor - sold_debitor) > 0 ORDER BY data_referinta",
                (_sf.isoformat(),))
    return cur.fetchall()


def select_prima_depunere_iconta(cur, schema, an):
    """[lotul 11, decizia Costin 10.3 „D205 pe anii depuși după regula veche: fără rectificative”] Data primei D205 pe `an` depuse PRIN
    iConta.eu (`sursa = 'iconta'`; marcările „extern” / „contabil_anterior” și istoricul importat nu sunt conținut generat de aplicație)
    a firmei cu schema `schema`, sau None."""
    cur.execute("SELECT MIN(d.data_depunere) FROM public.declaratii_depuse d JOIN public.tenants t ON t.id = d.tenant_id "
                "WHERE t.schema_name = %s AND d.an = %s AND d.tip = 'd205' AND d.sursa = 'iconta'", (schema, an))
    r = cur.fetchone()
    return (r[0] if not isinstance(r, dict) else list(r.values())[0]) if r else None


def select_d205_completata(cur, schema, an, stari_active):
    """[lotul 11, decizia Costin 10.3 „Semaforul D205 numără 457 preluat ca incomplet până la completarea manuală”] True dacă D205 pe
    `an` a firmei e depusă (orice sursă: prin aplicație, marcată „extern” / „contabil_anterior”, importată) sau așteaptă în coadă
    (`stari_active` = `coada_api.STARI_ACTIVE`) cu beneficiarii completați manual (`_cerere.manual.beneficiari` — singurul drum de generare pe anul
    preluării cu 457 în balanța de deschidere, `d205.refuz_preluate`)."""
    cur.execute("SELECT EXISTS (SELECT 1 FROM public.declaratii_depuse d JOIN public.tenants t ON t.id = d.tenant_id "
                "WHERE t.schema_name = %s AND d.an = %s AND d.tip = 'd205') OR EXISTS (SELECT 1 FROM public.declaratii_coada c "
                "JOIN public.tenants t ON t.id = c.tenant_id WHERE t.schema_name = %s AND c.tip = 'd205' "
                "AND c.stare = ANY(%s) AND (c.payload->>'_an')::int = %s "
                "AND jsonb_typeof(c.payload->'_cerere'->'manual'->'beneficiari') = 'array' "
                "AND jsonb_array_length(c.payload->'_cerere'->'manual'->'beneficiari') > 0)", (schema, an, schema, list(stari_active), an))
    r = cur.fetchone()
    return bool(r[0] if not isinstance(r, dict) else list(r.values())[0])
