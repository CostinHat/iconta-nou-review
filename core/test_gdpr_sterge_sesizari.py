# -*- coding: utf-8 -*-
"""[C38, 15.10.2026] Ștergerea GDPR a unui cabinet (`core/gdpr_sterge.executa`) care a trimis o sesizare cu un fișier atașat: înainte,
`raportari.autor_id -> users` („NO ACTION”) oprea ștergerea userilor, iar fișierele din depozitul privat (`core/fisiere_private.py`,
directorul cabinetului) rămâneau pe disc. Acum dispar sesizarea, mesajele, rândul fișierului și directorul. Pe baza de TEST, pe un cabinet
sintetic fără firme, cu depozitul într-un director temporar.
MUTAȚII: ștergerea sesizărilor scoasă -> ForeignKeyViolation; ștergerea directorului scoasă -> pică."""
import os

from core import db, fisiere_private, gdpr_sterge

PNG = b"\x89PNG\r\n\x1a\n" + b"\0" * 64


def test_cabinetul_cu_sesizari_si_fisiere_se_sterge_complet(monkeypatch, tmp_path):
    monkeypatch.setenv("ICONTA_FISIERE_DIR", str(tmp_path / "fisiere"))
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:      # resturile unei rulări întrerupte (o mutație, un test oprit la jumătate)
            cur.execute("DELETE FROM public.raportari WHERE autor_id IN (SELECT id FROM public.users WHERE email = 'ztest_c38@invalid')")
            cur.execute("DELETE FROM public.users WHERE email = 'ztest_c38@invalid'")
            cur.execute("DELETE FROM public.accounting_firms WHERE nume = 'ZTEST C38 GDPR'")
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST C38 GDPR') RETURNING id")
            cab = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,rol,accounting_firm_id,activ) "
                        "VALUES ('ztest_c38@invalid','x','N','admin_firma',%s,true) RETURNING id", (cab,))
            uid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.raportari (autor_id, cabinet_id, subiect) VALUES (%s,%s,'proba C38') RETURNING id", (uid, cab))
            rid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.raportari_mesaje (raportare_id, autor_id, rol_autor, text) "
                        "VALUES (%s,%s,'utilizator','captura') RETURNING id", (rid, uid))
            mid = cur.fetchone()[0]
        fisiere_private.salveaza(conn, cab, uid, mid, "captura.png", PNG, ("png",))
        conn.commit()
    d = tmp_path / "fisiere" / str(cab)
    assert len(os.listdir(d)) == 1
    with db.get_conn() as conn:
        rez = gdpr_sterge.executa(conn, cab, "ZTEST C38 GDPR", None)
    assert rez["fisiere_sterse"] == 1 and not d.exists(), rez
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT (SELECT count(*) FROM public.raportari WHERE id=%s), (SELECT count(*) FROM public.raportari_mesaje "
                    "WHERE id=%s), (SELECT count(*) FROM public.fisiere_private WHERE cabinet_id=%s), (SELECT count(*) FROM "
                    "public.users WHERE id=%s), (SELECT count(*) FROM public.accounting_firms WHERE id=%s)", (rid, mid, cab, uid, cab))
        assert cur.fetchone() == (0, 0, 0, 0, 0)
        cur.execute("DELETE FROM public.gdpr_stergeri WHERE cabinet_id=%s", (cab,))
        conn.commit()
