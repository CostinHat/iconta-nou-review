# -*- coding: utf-8 -*-
"""REPOSITORY — e-Factura primită și trimiterile către SPV.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:842`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""
from core import chei_unice as _chei   # [lotul 10, C73 / U2] a doua trimitere vie a facturii -> numită, nu 500


def primite_in_asteptare(cur, schema):
    cur.execute(f"""SELECT id, cif_emitent, cif_beneficiar, status, xml_brut, factura_id
                              FROM {schema}.efactura_primite WHERE status IN ('descarcata','ciorna')
                              ORDER BY importat_la DESC LIMIT 100""")
    return cur.fetchall()


def contul_invatat_al_emitentului(cur, schema, cif_emitent):
    # [lotul 11, decizia 10.3 pct.4] CIF-ul în forma păstrată (`cui_forma`), pe ambele părți: rândurile vechi au „RO”, cele noi nu
    from core import cui_forma as _cf
    cur.execute(f"""SELECT cont_cheltuiala FROM {schema}.efactura_primite
                                WHERE {_cf.SQL.format(c="cif_emitent")}=%s AND cont_cheltuiala IS NOT NULL
                                ORDER BY validat_la DESC NULLS LAST LIMIT 1""",
                (_cf.stocare(cif_emitent) or "",))
    return cur.fetchone()


def xml_brut(cur, schema, primita_id):
    cur.execute(f"SELECT xml_brut FROM {schema}.efactura_primite WHERE id=%s",
                (primita_id,))
    return cur.fetchone()


def primita_pentru_validare(cur, schema, primita_id):
    cur.execute(f"""SELECT status, xml_brut, cif_beneficiar, factura_id
                              FROM {schema}.efactura_primite WHERE id=%s FOR UPDATE""",
                (primita_id,))
    return cur.fetchone()


def starea_primitei_blocata(cur, schema, primita_id):
    cur.execute(f"SELECT status FROM {schema}.efactura_primite WHERE id=%s FOR UPDATE",
                (primita_id,))
    return cur.fetchone()


def ultima_trimitere_per_factura(cur, schema):
    cur.execute(f"""SELECT DISTINCT ON (factura_id) factura_id, stare, index_incarcare, error_message
                              FROM {schema}.efactura_trimiteri ORDER BY factura_id, id DESC""")
    return cur.fetchall()


# ── P7 · V2: scrierile, mutate din rute ──────────────────────────────

def marcheaza_primita_validata(cur, schema, factura_id, cont_cheltuiala, id_):
    cur.execute(f"""UPDATE {schema}.efactura_primite
                            SET status='validata', factura_id=COALESCE(%s, factura_id),
                                cont_cheltuiala=%s, validat_la=now() WHERE id=%s
                            RETURNING factura_id""",
                (factura_id, cont_cheltuiala, id_))
    return cur.fetchone()


def marcheaza_primita_respinsa(cur, schema, motiv_respins, id_):
    cur.execute(f"""UPDATE {schema}.efactura_primite SET status='respinsa', motiv_respins=%s
                            WHERE id=%s""",
                (motiv_respins, id_))


# ── P7 · valul D2: SQL-ul care statea in motorul fiscal `core/efactura_send.py` ──
#
# Cele sapte de mai jos erau, pana la 13.09.2026, in corpul lui `incarca_factura` si al lui
# `trimite`, intr-un modul declarat `FISCAL_ENGINE`. Textul canonic cere ca un motor fiscal sa nu
# atinga baza; instructiunile s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri,
# aceeasi ordine. Proiectiile sunt cele cerute de UBL 2.1 / CIUS-RO, de-aia stau aici si nu in
# `repo_facturi`: nu sunt „factura", sunt „factura asa cum o cere e-Factura".

def factura_pentru_ubl(cur, schema, factura_id):
    from core import repo_facturi as _rf   # [417] factura stornată (BG-3)
    cur.execute(f"""SELECT id, numar, serie, data_emitere, data_scadenta, moneda,
                               tert_nume, tert_cui, tert_adresa, tert_oras, tert_judet,
                               taxare_inversa, tip, storno_din_id, total, tva,
                               directie, bon_fiscal_nr, bon_fiscal_data, tert_tara, data_faptului_generator,
                               {_rf.SQL_STORNO_DIN.format(s=schema + ".", a="f")}
                          FROM {schema}.facturi f WHERE id = %s""", (int(factura_id),))
    return cur.fetchone()


def linii_pentru_ubl(cur, schema, factura_id):
    # [lotul 11, C86] + valoare_neta (BT-131 exact: stornarea unei facturi venite din XML o poartă negată; NULL = cantitate × preț)
    cur.execute(f"""SELECT descriere, um, cantitate, pret_unitar, cota_tva, categorie_tva, valoare_neta
                          FROM {schema}.factura_linii WHERE factura_id = %s ORDER BY id""",
                (int(factura_id),))
    return cur.fetchall()


def emitent_pentru_ubl(cur, schema):
    cur.execute(f"""SELECT nume, cui, reg_com, adresa, oras, judet, cod_postal, iban,
                               platitor_tva
                          FROM {schema}.firma_profil WHERE id = 1""")
    return cur.fetchone()


def cui_emitent(cur, schema):
    cur.execute(f"SELECT cui FROM {schema}.firma_profil WHERE id=1")
    return cur.fetchone()


def trimitere_vie(cur, schema, factura_id, mediu):
    cur.execute(f"""SELECT id, stare FROM {schema}.efactura_trimiteri
                WHERE factura_id=%s AND mediu=%s AND stare IN ('incarcat','in_prelucrare','ok')
                LIMIT 1""", (factura_id, mediu))
    return cur.fetchone()


def insereaza_trimitere_pregatita(cur, schema, factura_id, mediu, xml, sha):
    cur.execute(f"""INSERT INTO {schema}.efactura_trimiteri
                (factura_id, mediu, stare, xml_trimis, xml_sha256, trimis_la)
                VALUES (%s,%s,'pregatit',%s,%s, now()) RETURNING id""",
                (factura_id, mediu, xml, sha))
    return cur.fetchone()


def trimitere_in_curs(cur, schema, factura_id, mediu, minute):
    """[lotul 10, C73 / U2] Poarta trimiterii, SERIALIZATĂ pe factură: lacătul pe rândul facturii (`FOR UPDATE`, ține până la
    comiterea rândului «pregătit») face ca două trimiteri simultane să treacă prin poartă una după alta. Întoarce trimiterea
    «pregătit» a facturii pornită în ultimele `minute` (încărcarea ei la ANAF încă rulează), sau None.

    De ce: rândul «pregătit» nu e în indexul `uq_efactura_trimiteri_viu` (numai incarcat/in_prelucrare/ok), deci două cereri
    simultane îl scriau amândouă, încărcau AMÂNDOUĂ factura la ANAF (dublă factură în SPV), iar a doua cădea abia la scrierea
    rezultatului, cu 500 și cu indexul ANAF pierdut."""
    cur.execute(f"SELECT id FROM {schema}.facturi WHERE id = %s FOR UPDATE", (factura_id,))
    cur.execute(f"""SELECT id, trimis_la FROM {schema}.efactura_trimiteri
                WHERE factura_id = %s AND mediu = %s AND stare = 'pregatit' AND trimis_la > now() - %s * interval '1 minute'
                ORDER BY id DESC LIMIT 1""", (factura_id, mediu, minute))
    return cur.fetchone()


def refuz_alta_vie(cur, schema, trimitere_id):
    """Refuzul: factura avea deja altă trimitere vie (citită după întoarcerea la savepoint)."""
    cur.execute(f"""SELECT a.id FROM {schema}.efactura_trimiteri a JOIN {schema}.efactura_trimiteri t ON t.factura_id = a.factura_id
                WHERE t.id = %s AND a.id <> t.id AND a.mediu = 'prod' AND a.stare IN ('incarcat','in_prelucrare','ok')""",
                (trimitere_id,))
    r = cur.fetchone()
    return _chei.CheieDublata("ANAF a primit și această încărcare, dar factura avea deja o trimitere vie (trimiterea %s): factura "
                              "e de două ori în SPV. Verifică în SPV și anulează dublura." % (r[0] if r else "?"),
                              existent={"trimitere_id": r[0]} if r else None)


def rezultatul_trimiterii(cur, schema, stare, index_incarcare, execution_status, errmsg, trimitere_id):
    """Rezultatul încărcării, pe rândul «pregătit». [lotul 10, C73 / U2] Dacă rândul ar deveni al doilea viu al facturii
    (`uq_efactura_trimiteri_viu`; poarta `trimitere_in_curs` o face posibilă numai peste o încărcare mai lungă decât fereastra ei),
    rezultatul nu se pierde într-un 500: rândul trece în «investigatie», cu indexul ANAF și cu dublura numită."""
    try:
        with _chei.refuza_dublura(cur, ("uq_efactura_trimiteri_viu",), lambda cur, e: refuz_alta_vie(cur, schema, trimitere_id)):
            cur.execute(f"""UPDATE {schema}.efactura_trimiteri
                        SET stare=%s, index_incarcare=%s, execution_status=%s, error_message=%s,
                            actualizat_la=now(),
                            finalizat_la=CASE WHEN %s IN ('nok','eroare_upload') THEN now() ELSE finalizat_la END
                        WHERE id=%s""",
                        (stare, index_incarcare, execution_status, errmsg, stare, trimitere_id))
    except _chei.CheieDublata as e:
        cur.execute(f"""UPDATE {schema}.efactura_trimiteri
                    SET stare='investigatie', index_incarcare=%s, execution_status=%s, error_message=%s, actualizat_la=now()
                    WHERE id=%s""", (index_incarcare, execution_status, str(e), trimitere_id))
        return str(e)
    return None


# ── [lotul 11, C79] TVA-ul de pe factură, pe cote (BG-23) ─────────────────────────────────────────────────

# Prefixul de schemă al tabelelor de mai jos: `schema.` calificat, sau gol (schema None) când apelantul a fixat deja `search_path` (D300,
# contarea pe `db.get_conn(schema)`). Scris în fiecare interogare: o funcție de repository fără cursor ar ieși din tiparul P7
# (`core/test_p7_v1_citiri.py::test_fiecare_functie_de_repository_primeste_cursorul`).


def salveaza_tva_cote(cur, schema, factura_id, cote):
    """Rândurile de defalcare a TVA-ului facturii (`efactura_import.tva_cote_din_xml`), numai dacă factura nu le are deja — o factură
    importată a doua oară (dedup pe număr / terț / dată) își păstrează rândurile de la primul import; două importuri concurente ale aceleiași
    facturi se întâlnesc pe cheia (factura_id, nr) — al doilea nu mai scrie (`ON CONFLICT DO NOTHING`), nu cade. Întoarce True dacă a scris."""
    if not cote:
        return False
    cur.execute(f"SELECT 1 FROM {(schema + '.') if schema else ''}factura_tva_cote WHERE factura_id = %s LIMIT 1", (factura_id,))
    if cur.fetchone():
        return False
    for nr, c in enumerate(cote, start=1):
        cur.execute(f"""INSERT INTO {(schema + '.') if schema else ''}factura_tva_cote (factura_id, nr, categorie, cota, baza, tva, sursa)
                        VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (factura_id, nr) DO NOTHING""",
                    (factura_id, nr, c.get("categorie"), c["cota"], c.get("baza"), c["tva"], c["sursa"]))
    return True


def tva_cote(cur, schema, factura_ids):
    """{factura_id: [(cota, tva, sursa, categorie, baza)]} — TVA-ul de pe factură, în moneda documentului, în ordinea defalcării."""
    if not factura_ids:
        return {}
    cur.execute(f"""SELECT factura_id, cota, tva, sursa, categorie, baza FROM {(schema + '.') if schema else ''}factura_tva_cote
                    WHERE factura_id = ANY(%s) ORDER BY factura_id, nr""", (list(factura_ids),))
    out = {}
    for r in cur.fetchall():
        r = tuple(r.values()) if isinstance(r, dict) else tuple(r)
        out.setdefault(r[0], []).append(r[1:])
    return out


# ── [lotul 11, C83] cursul facturii importate din XML în valută ──────────────────────────────────────────────
def seteaza_cursul_importului(cur, schema, factura_id, curs, data_curs, sursa, tva_lei, total_lei):
    """Cursul și sumele în lei ale facturii din XML (`contare_facturi.curs_factura_importate`), numai dacă factura nu are încă un curs —
    cursul fixat nu se mai recalculează (HG 1/2016 pct.35 alin.(2): „va rămâne neschimbat la data definitivării operațiunii”)."""
    cur.execute(f"""UPDATE {(schema + '.') if schema else ''}facturi SET curs_bnr = %s, data_curs = %s, curs_sursa = %s, tva_lei = %s, total_lei = %s
                    WHERE id = %s AND curs_bnr IS NULL""", (curs, data_curs, sursa, tva_lei, total_lei, factura_id))


def moneda_si_data(cur, schema, factura_id):
    """(moneda, data_emitere) ale facturii, sau None — ca ruta să aducă cursul BNR înaintea tranzacției contării."""
    cur.execute(f"SELECT moneda, data_emitere FROM {(schema + '.') if schema else ''}facturi WHERE id = %s", (factura_id,))
    r = cur.fetchone()
    return (tuple(r.values()) if isinstance(r, dict) else tuple(r)) if r else None
