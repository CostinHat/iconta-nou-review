"""[715, comanda 14.2] Alerta de acces anormal numără acțiunile omului, nu cererile de pornire ale ecranelor și nu conturile de test;
numește utilizatorul și cabinetul. Pe Postgres, în tranzacție anulată (firme și utilizatori sintetici)."""
import json
from core import alerta_acces as AA, audit_automat as AU, db
from core.test_lot11_t import conn_t  # noqa: F401 — fixtura schemei sintetice


def _automata(cur, actiune):
    """Aceeași regulă ca în interogările Fișei și alertei: `sql_actiune_omului` îl lasă pe loc doar ce NU e cerere automată."""
    cur.execute("SELECT NOT (x.actiune <> ALL(%s) AND x.actiune NOT LIKE %s) FROM (SELECT %s AS actiune) x", (*AU.PARAM_OMULUI, actiune))
    return cur.fetchone()[0]


def test_cererile_de_pornire_sunt_automate_iar_scrierile_si_datele_nu(conn_t):
    with conn_t.cursor() as cur:
        for c in ("GET /eu/drepturi", "GET /asistenti/echipa/semafor", "GET /tenants", "GET /coada", "GET /termene", "GET /firme-scoase",
                  "GET /spv/autorizare", "GET /tenants/105779/spv/stare"):
            assert _automata(cur, c), c
        for c in ("PUT /tenants/1/ciorne-formular/factura", "POST /coada", "GET /tenants/1/facturi", "GET /tenants/1/balanta"):
            assert not _automata(cur, c), c


def _cabinet_cu_utilizator(cur, nume_cabinet, eticheta, cereri):
    cur.execute("INSERT INTO public.accounting_firms (nume) VALUES (%s) RETURNING id", (nume_cabinet,))
    fid = cur.fetchone()[0]
    cur.execute("INSERT INTO public.users (email, password_hash, nume, prenume, accounting_firm_id) VALUES (%s,'x','Ionescu','Ana',%s) RETURNING id",
                ("ztest715_%s@exemplu.test" % eticheta, fid))
    uid = cur.fetchone()[0]
    for actiune, _automat in cereri:
        cur.execute("INSERT INTO public.audit_log (user_id, actiune, detalii) VALUES (%s,%s,%s)",
                    (uid, actiune, json.dumps({"status": 200})))
    return uid


def test_alerta_ignora_automatele_si_cabinetele_de_test_si_numeste_omul():
    cereri = [("GET /eu/drepturi", True)] * 400 + [("PUT /tenants/1/x", False)] * 5
    conn = db.pool().getconn()
    try:
        with conn.cursor() as cur:
            u1 = _cabinet_cu_utilizator(cur, "Cabinet Real Ztest715 SRL", "a", cereri)
            u2 = _cabinet_cu_utilizator(cur, "Cabinet Test Ztest715 SRL", "b", [("PUT /tenants/1/x", False)] * 400)
            u3 = _cabinet_cu_utilizator(cur, "Cabinet Real Doi Ztest715 SRL", "c", [("PUT /tenants/1/x", False)] * 400)
        gasiti = {u["user_id"]: u for u in AA.detecteaza(conn, 10, 8, 300)}
        assert u1 not in gasiti, "cele 400 de cereri automate nu sunt acțiuni"
        assert u2 not in gasiti, "cabinetul de test nu alertează"
        u = gasiti[u3]
        assert u["actiuni"] == 400 and u["cabinet"] == "Cabinet Real Doi Ztest715 SRL" and u["nume"] == "Ana Ionescu"
        assert u["email"] == "ztest715_c@exemplu.test"
    finally:
        conn.rollback()
        db.pool().putconn(conn)


def test_subiectul_alertei_numeste_omul_cabinetul_si_scrie_firma_la_singular(monkeypatch):
    trimise = []
    monkeypatch.setattr(AA, "detecteaza", lambda *a, **k: [{"user_id": 1, "tenanti": 1, "actiuni": 350, "nume": "Ana Ionescu",
                                                            "email": "a@x.ro", "cabinet": "Cabinet X SRL"}])
    monkeypatch.setattr(AA, "_poate_trimite", lambda *a, **k: True)
    AA.ruleaza(trimite=lambda s, m: trimise.append((s, m)))
    s, m = trimise[0]
    assert s == "Acces anormal: Ana Ionescu (a@x.ro), cabinetul Cabinet X SRL (1 firmă, 350 acțiuni în 10 min)", s
    assert m == ("Semnal automat (art.33): utilizatorul Ana Ionescu (a@x.ro), cabinetul Cabinet X SRL (id 1), a atins 1 firmă distincte și 350 "
                 "acțiuni în ultimele 10 min (praguri 8 firme / 300 acțiuni). Nu s-a blocat nimic. Verifică manual."), m
