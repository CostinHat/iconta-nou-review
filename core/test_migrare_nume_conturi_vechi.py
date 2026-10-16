# -*- coding: utf-8 -*-
"""[269, comanda 4 a lotului 5] Migrarea numelor conturilor vechi (core/migrare_nume_conturi_vechi.py), pe baza de TEST, în tranzacție
anulată: administratorul de cabinet creat cu formularul vechi („Test 253” -> nume „Test”, prenume „253”) primește numele întreg; un
cont creat după publicare, un asistent și un client cu prenume nu se ating; a doua rulare nu mai schimbă nimic.
MUTAȚII: ordinea `prenume nume` -> pică; condiția pe rol scoasă -> pică; pragul `creat_la` scos -> pică."""
from core import db
from core import migrare_nume_conturi_vechi as M


def _cont(cur, email, rol, firma, nume, prenume, creat_la):
    cur.execute("INSERT INTO public.users (email, password_hash, nume, prenume, rol, accounting_firm_id, activ, creat_la) "
                "VALUES (%s, 'x', %s, %s, %s, %s, true, %s) RETURNING id", (email, nume, prenume, rol, firma, creat_la))
    return cur.fetchone()[0]


def test_numele_impartit_se_lipeste_la_loc_numai_la_conturile_vechi_de_cabinet():
    db.init_pool()
    with db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('Cabinet proba 269') RETURNING id")
                f = cur.fetchone()[0]
                vechi = "2026-10-01 10:00:00+03"
                a = _cont(cur, "a269@proba-269.test", "admin_firma", f, "Test", "253", vechi)
                b = _cont(cur, "b269@proba-269.test", "admin_firma", f, None, "Ion", vechi)
                c = _cont(cur, "c269@proba-269.test", "admin_firma", f, "Ion Pop", None, vechi)
                d = _cont(cur, "d269@proba-269.test", "admin_firma", f, "Pop", "Ion", "2026-10-20 10:00:00+03")   # după publicare
                e = _cont(cur, "e269@proba-269.test", "angajat", f, "Ana", "Maria", vechi)    # asistentul
            ids = M.aplica(conn)
            assert {a, b} <= set(ids) and not ({c, d, e} & set(ids)), ids
            with conn.cursor() as cur:
                cur.execute("SELECT id, nume, prenume FROM public.users WHERE id = ANY(%s) ORDER BY id", ([a, b, c, d, e],))
                assert cur.fetchall() == [(a, "Test 253", None), (b, "Ion", None), (c, "Ion Pop", None), (d, "Pop", "Ion"),
                                          (e, "Ana", "Maria")]
            assert M.verifica(conn) == 0 and M.aplica(conn) == []
        finally:
            conn.rollback()
