# -*- coding: utf-8 -*-
"""Controlul de tranzacție, scos din stratul HTTP — dar FĂRĂ să mute proprietatea tranzacției.

[P7 · V2, 13.09.2026] Zece instrucțiuni trăiau în corpul rutelor: șase din familia `SAVEPOINT` și
patru `SET LOCAL search_path`. Nu sunt nici citiri, nici scrieri de business; sunt mecanica
tranzacției. `PLAN_HARDENING.md:846` cere ca ruta să nu conțină SQL — inclusiv pe acesta.

CE **NU** FACE MODULUL ĂSTA, și e partea care contează: **nu deține tranzacția**. Nu deschide
conexiuni, nu comite, nu face rollback complet. Fiecare funcție e o singură instrucțiune executată pe
cursorul primit, la locul și în ordinea în care era executată și înainte. Proprietarul tranzacției
rămâne cel care era — ruta care a deschis `db.get_conn()` (P4, neatins).

DE CE O FUNCȚIE PER SAVEPOINT, în loc de una generică `savepoint(cur, nume)`: forma generică ar
însemna un nume de savepoint interpolat într-un SQL, adică o suprafață de injecție care azi nu
există. SQL-ul rămâne literal, exact cum era.
"""


def savepoint_supervizor(cur):
    cur.execute("SAVEPOINT supervizor")


def elibereaza_supervizor(cur):
    cur.execute("RELEASE SAVEPOINT supervizor")


def intoarce_la_supervizor(cur):
    cur.execute("ROLLBACK TO SAVEPOINT supervizor")


def savepoint_z_insert(cur):
    cur.execute("SAVEPOINT z_insert")


def elibereaza_z_insert(cur):
    cur.execute("RELEASE SAVEPOINT z_insert")


def intoarce_la_z_insert(cur):
    cur.execute("ROLLBACK TO SAVEPOINT z_insert")


def savepoint_firma(cur):
    cur.execute("SAVEPOINT sp_firma")


def elibereaza_firma(cur):
    cur.execute("RELEASE SAVEPOINT sp_firma")


def intoarce_la_firma(cur):
    cur.execute("ROLLBACK TO SAVEPOINT sp_firma")


# [C201, lotul 13] Semaforul Control fiscal evaluat pe conexiunea apelantului (închiderea lunii), nu pe una a doua ținută deodată:
# o eroare a lui se întoarce la savepoint și nu anulează tranzacția apelantului (`uc_comun.declaratii_nedepuse_cu_termen_in_luna`).
def savepoint_semafor(cur):
    cur.execute("SAVEPOINT semafor")


def elibereaza_semafor(cur):
    cur.execute("RELEASE SAVEPOINT semafor")


def intoarce_la_semafor(cur):
    cur.execute("ROLLBACK TO SAVEPOINT semafor")


def fixeaza_schema(cur, schema):
    cur.execute(f"SET LOCAL search_path TO {schema}")
