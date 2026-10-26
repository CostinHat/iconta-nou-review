# -*- coding: utf-8 -*-
"""Lotul 13, comanda Costin 13.1 (verbatim în DECIZII „Comanda 13.1”), pachetul PORTAL / P2 — notificări, sinteza zilnică, chei API, WhatsApp.

  * 565 — „Sinteza pe email nu apare în Setări cont → Notificări și n-a ajuns niciodată la administrator (5 zile verificate în inbox).”
    Cauza, citită în jurnalul jobului de cron: „registrul dezabonărilor nu s-a putut citi (RuntimeError: pool neinițializat …)” — jobul
    nu inițializa pool-ul aplicației, iar emailul informativ întreabă registrul prin el (fail-closed: nu pleca nimic);
  * 566 — „«O solicitare nouă de la un client» e debifată implicit la administrator”;
  * 567 — „Text stricat («Ai un element pregătit de tine a fost respins»); emailul nu spune ce element și la ce firmă.”;
  * 568 — „«1 de validat», deși coada are 5 note (Ana, 19.10) + 1 declarație; sinteza numără doar ce a intrat azi.” (emailul: o seară cu
    elemente în așteptare și fără activitate era „zi goală” și nu pleca);
  * 564 — momentele cheilor API (creată / folosită ultima dată) ajung pe ecran în forma aplicației: serverul le dă în ISO 8601;
  * 647 — „Trimite codul pe WhatsApp” refuzat de Meta (133010): mesajul pentru om e simplu, textul Meta rămâne în jurnal.

Datele: rânduri `public.*` efemere, într-o tranzacție ANULATĂ (cabinet sintetic, an 2099 unde e cazul); emailurile NU pleacă — cutia de
test (`ICONTA_EMAIL_CUTIE`, `observare._in_cutia_de_test`) le scrie ca fișiere.

Temei: N/A — notificările și sinteza sunt funcții ale aplicației, nu reguli fiscale. 647: documentația Meta „Error codes” (WhatsApp Cloud
API): „133010 — Phone number not registered on the WhatsApp Business Platform. Register the phone number before trying again.”
"""
import json
import os

import pytest

from core import db as _db
from core import notificari as N


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


ADMIN = {"rol": "admin_firma", "poate_pregati": True, "poate_valida": True}
ASIST = {"rol": "angajat", "poate_pregati": True, "poate_valida": False}


# ── 567 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_567_emailul_fiecarui_tip_incepe_cu_o_propozitie_intreaga():
    """Înainte: „Ai %s în iConta.eu.” lipit de etichetă -> „Ai un element pregătit de tine a fost respins”, „Ai un coleg și-a activat
    contul”. Acum eticheta e propoziția însăși, cu majusculă și punct. MUTAȚIE: „<p><b>%s</b></p>” -> „<p>Ai %s în iConta.eu.</p>” -> pică."""
    for tip, t in N.TIPURI.items():
        html = N.html_email(tip)
        assert "Ai " + t["eticheta"] not in html, (tip, html)
        prop = t["eticheta"][:1].upper() + t["eticheta"][1:] + "."
        assert "<b>%s</b>" % N._esc(prop) in html, (tip, html)


def test_567_emailul_respingerii_spune_elementul_si_firma_fara_motiv():
    """Textul real al respingerii unei note (`uc_comun._notif_pregatitor` + `_cu_firma`): emailul numește firma și nota, nu motivul și
    cifrele (rămân în aplicație — gărzile C109 / C197). MUTAȚIE: `rezumat` întoarce „” -> elementul lipsește -> pică."""
    text = "Alfa Test SRL: Notă · Plată chirie octombrie · OP 12 a fost respinsă. Motiv: contul 612 e greșit, suma 1.000 lei."
    html = N.html_email("respinsa", text)
    assert "<b>Un element pregătit de tine a fost respins.</b>" in html, html
    assert "Alfa Test SRL: Notă · Plată chirie octombrie · OP 12 a fost respinsă." in html, html
    assert "Motiv" not in html and "1.000" not in html and "612" not in html, html


@pytest.mark.parametrize("text, rez", [
    ("Alfa SRL: Notă pregătită, de validat: Notă · Plată chirie · OP 12.", "Alfa SRL: Notă pregătită, de validat: Notă · Plată chirie · OP 12."),
    ("Alfa SRL: Declarația D300 (09/2026) a fost respinsă. Motiv: x", "Alfa SRL: Declarația D300 (09/2026) a fost respinsă."),
    ("Firma FE3 SRL: factura recurentă pentru Kunde GmbH s-a emis (F1, 10.03.2099), cu 1 avertisment: Factura s-a emis automat cu scutirea.",
     "Firma FE3 SRL: factura recurentă pentru Kunde GmbH s-a emis (F1, 10.03.2099), cu 1 avertisment."),
    ("Firma FE3 SRL: factura recurentă pentru Client SRL nu s-a emis (10.03.2099). Motivul: firma nu e plătitoare de TVA.",
     "Firma FE3 SRL: factura recurentă pentru Client SRL nu s-a emis (10.03.2099)."),
    ("", ""),
])
def test_567_rezumatul_formele_reale(text, rez):
    assert N.rezumat(text) == rez


# ── 566 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_566_solicitarea_clientului_e_bifata_din_oficiu_la_administrator_si_la_asistent():
    """MUTAȚIE: `"implicit": True` scos de pe `solicitare_client` -> nebifată -> pică."""
    for actor in (ADMIN, ASIST):
        bife = {t["cheie"]: t["bifat"] for g in N.lista_pentru(actor, None) for t in g["tipuri"]}
        assert bife.get("solicitare_client") is True, (actor, bife)
    assert N.dorit("solicitare_client", None) and N.dorit("solicitare_client", {"de_validat": True})
    assert not N.dorit("solicitare_client", {"solicitare_client": False}), "alegerea omului rămâne"


@pytest.fixture()
def tx():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZT Lot 13 P2') RETURNING id")
            cab = cur.fetchone()[0]
        yield conn, cab
    finally:
        conn.rollback()
        p.putconn(conn)


def _user(conn, cab, email, rol, tipuri=None, salvat="now()"):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,activ,poate_pregati,poate_valida,"
                    "poate_depune,notificari_tipuri,notificari_salvate_la) VALUES (%s,'x','Probă','P2',%s,%s,true,true,true,true,%s::jsonb,"
                    + salvat + ") RETURNING id", (email, rol, cab, json.dumps(tipuri) if tipuri is not None else None))
        return cur.fetchone()[0]


def _bifa(conn, uid):
    with conn.cursor() as cur:
        cur.execute("SELECT notificari_tipuri->>'solicitare_client' FROM public.users WHERE id = %s", (uid,))
        return cur.fetchone()[0]


def test_566_migrarea_pune_bifa_la_loc_numai_pe_bifele_salvate_inaintea_ei(tx):
    """Datele existente: bifa „nu” salvată cu implicitul greșit (înainte de prima rulare) -> „da”; clientul (nu vede tipul) neatins; a doua
    rulare nu schimbă nimic. MUTAȚIE: condiția pe rol scoasă -> clientul atins -> pică."""
    from core import migrare_notificari_solicitare_client as M
    conn, cab = tx
    with conn.cursor() as cur:   # registrul migrărilor: fără rândul acestei migrări (prima rulare: pragul = acum)
        cur.execute(_db_ddl_registru())
        cur.execute("DELETE FROM public.migrari_rulate WHERE fisier = %s", (M.FISIER,))
    admin = _user(conn, cab, "zt_l13p2_admin@invalid", "admin_firma", {"solicitare_client": False, "de_validat": True},
                  "now() - interval '2 days'")
    asist = _user(conn, cab, "zt_l13p2_asist@invalid", "angajat", {"solicitare_client": False}, "now() - interval '2 days'")
    client = _user(conn, cab, "zt_l13p2_client@invalid", "client", {"solicitare_client": False}, "now() - interval '2 days'")
    neatins = _user(conn, cab, "zt_l13p2_fara@invalid", "admin_firma", None, "NULL")
    n = M.aplica(conn)
    assert n >= 2
    assert (_bifa(conn, admin), _bifa(conn, asist), _bifa(conn, client), _bifa(conn, neatins)) == ("true", "true", "false", None)
    with conn.cursor() as cur:
        cur.execute("SELECT notificari_tipuri->>'de_validat' FROM public.users WHERE id = %s", (admin,))
        assert cur.fetchone()[0] == "true", "celelalte bife rămân"
    assert M.ramase(conn) == 0


def _db_ddl_registru():
    from core.migrari_registru import DDL
    return DDL


# ── 565 / 568 — sinteza zilnică ─────────────────────────────────────────────────────────────────────────────────────────────────
def test_565_sinteza_apare_in_notificari_numai_la_administrator_bifata_numai_pe_email():
    """MUTAȚIE: tipul `sinteza_zilnica` scos din `TIPURI` -> nu apare în Notificări -> pică."""
    admin = {t["cheie"]: t for g in N.lista_pentru(ADMIN, None) for t in g["tipuri"]}
    assert admin["sinteza_zilnica"]["bifat"] is True and "numai pe email" in admin["sinteza_zilnica"]["rand"], admin.get("sinteza_zilnica")
    asist = {t["cheie"] for g in N.lista_pentru(ASIST, None) for t in g["tipuri"]}
    assert "sinteza_zilnica" not in asist
    assert N.TIPURI["sinteza_zilnica"].get("doar_email") is True


def test_568_sinteza_cu_coada_in_asteptare_nu_e_zi_goala(tx):
    """O declarație pregătită ieri și nevalidată: seara de azi n-are activitate, dar „de validat” = 1 -> sinteza pleacă (înainte: „zi
    goală”, nimic). MUTAȚIE: `de_validat` scos din condiția `gol` -> gol -> pică."""
    import datetime
    from core import coada_api as c
    from core import sinteza_zilnica as S
    conn, cab = tx
    uid = _user(conn, cab, "zt_l13p2_sin@invalid", "admin_firma")
    with conn.cursor() as cur:
        cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id, activ) VALUES ('efemer_l13p2', 'ZT P2 SRL', %s, true) "
                    "RETURNING id", (cab,))
        tid = cur.fetchone()[0]
    assert c.adauga_in_coada(conn, cab, tid, "d300", 2099, {"xml": "<x/>"}, creat_de=str(uid), creat_de_id=uid, luna=1)["ok"]
    with conn.cursor() as cur:
        cur.execute("SELECT now()::date")
        azi = cur.fetchone()[0]
    maine = azi + datetime.timedelta(days=1)          # „mâine seară”: nimic nou, coada a rămas
    d = S.sinteza_cabinet(conn, cab, maine)
    assert (d["pregatite"], d["validate"], d["respinse"], d["depuse"], d["de_validat"]) == (0, 0, 0, 0, 1), d
    assert d["gol"] is False, d
    assert "De validat (în așteptare)" in S._html("ZT Lot 13 P2", maine, d)


def test_565_jobul_de_cron_trimite_si_fara_pool_initializat(monkeypatch, tmp_path):
    """Cauza 565: jobul (proces separat, cron) n-avea pool-ul aplicației, iar emailul informativ citește registrul dezabonărilor prin
    el -> „pool neinițializat” -> nu pleca nimic. Aici: pool-ul procesului e scos, jobul rulează cu un patron sintetic, iar emailul
    ajunge în cutia de test (nu pleacă). Administratorul care a debifat sinteza nu o primește.
    MUTAȚIE: `db.init_pool()` scos din `ruleaza` -> RuntimeError „pool neinițializat” -> pică."""
    if not _db_ok():
        pytest.skip("DB indisponibil")
    from core import sinteza_zilnica as S
    cutie = tmp_path / "cutie"
    monkeypatch.setenv("ICONTA_EMAIL_CUTIE", str(cutie))
    monkeypatch.setattr(S, "_patroni", lambda conn: [
        {"id": 1, "email": "zt_l13p2_patron@invalid", "cabinet_id": 999999, "notificari_tipuri": None},
        {"id": 2, "email": "zt_l13p2_debifat@invalid", "cabinet_id": 999998, "notificari_tipuri": {"sinteza_zilnica": False}}])
    monkeypatch.setattr(S, "sinteza_cabinet", lambda conn, cab, zi: {"pregatite": 1, "validate": 0, "respinse": 0, "depuse": 0,
                                                                      "de_validat": 6, "sesizari_noi": 0, "sesizari_fara_raspuns": 0,
                                                                      "pachete_trimise": 0, "gol": False})
    monkeypatch.setattr(S, "_nume_cabinet", lambda conn, cab: "Cabinet Probă P2")
    vechi = _db._pool
    monkeypatch.setattr(_db, "_pool", None)          # procesul cronului: pool-ul aplicației nu există
    try:
        rez = S.ruleaza()
    finally:
        nou = _db._pool
        if nou is not None and nou is not vechi:
            nou.closeall()
    assert rez == {"trimise": 1, "sarite": 0, "debifate": 1}, rez
    (f,) = os.listdir(cutie)
    e = json.load(open(os.path.join(cutie, f), encoding="utf-8"))
    assert e["catre"] == "zt_l13p2_patron@invalid" and e["subiect"].startswith("Sinteza zilei ") and "Cabinet Probă P2" in e["subiect"]
    assert "De validat (în așteptare)" in e["html"] and "Dezabonează-te" in e["html"], "sinteza e informativă (268)"


# ── 564 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_564_lista_cheilor_da_momentele_in_iso(tx):
    """Ecranul scrie momentele cu `dataRo(…, "cu_ora")`; serverul le dă în ISO 8601 (cu „T”). Înainte: `str()` -> „2026-10-25
    14:30:00.123456+03:00”, tăiat pe ecran la 16 caractere, în format ISO. MUTAȚIE: `isoformat()` -> `str()` -> pică."""
    from core import api_public
    conn, cab = tx
    k = api_public.genereaza(conn, cab, "Probă 564")
    assert api_public.verifica(conn, k["cheie"]) == cab                  # o folosire reală: `ultima_folosire` scrisă
    (r,) = [x for x in api_public.lista(conn, cab) if x["id"] == k["id"]]
    assert "T" in r["creat_la"] and "T" in r["ultima_folosire"], r
    assert r["activ"] is True and "cheie" not in r, "lista nu arată niciodată cheia"


# ── 647 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_647_refuzul_meta_133010_ajunge_la_om_ca_mesaj_simplu(monkeypatch):
    """`POST /eu/telefon/cod` cu Meta refuzând 133010: omul primește „WhatsApp nu e disponibil acum … pe email”, fără cod HTTP / text
    Meta; textul Meta merge în jurnal (`esec_secundar`). MUTAȚIE: `MESAJ_WA_ESUAT` -> `str(e)` -> textul Meta ajunge la om -> pică."""
    from core import erori, uc_cont_notificari as U, whatsapp as W

    class _Repo:
        def __getattr__(self, n):
            return lambda *a, **k: {"telefonul": "+40700000001", "cod_cerut_de_curand": False}.get(n)
    jurnal = []
    monkeypatch.setattr(U, "_repo", _Repo())
    monkeypatch.setattr(U.db, "get_conn", lambda *a, **k: _Ctx())
    monkeypatch.setattr(W, "configurat", lambda: True)

    def _refuz(tel, cod):
        raise W._refuz(400, {"message": "(#133010) Account not registered", "code": 133010, "type": "OAuthException"})
    monkeypatch.setattr(W, "trimite_cod", _refuz)
    from core import observare
    monkeypatch.setattr(observare, "esec_secundar", lambda et, e, alerta=False: jurnal.append((et, str(e), alerta)))

    class _D:
        acord = True
    with pytest.raises(erori.Conflict) as ex:
        U.cere_cod(_D(), {"uid": 1})
    corp = ex.value.args[0]
    assert corp["cod"] == U.COD_WA_INDISPONIBIL and corp["mesaj"] == U.MESAJ_WA_ESUAT, corp
    assert "WhatsApp nu e disponibil acum" in corp["mesaj"] and "email" in corp["mesaj"]
    assert "133010" not in corp["mesaj"] and "Meta" not in corp["mesaj"] and "HTTP" not in corp["mesaj"], corp
    assert jurnal and "133010" in jurnal[0][1] and jurnal[0][2] is True, jurnal


class _Ctx:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def cursor(self, *a, **k):
        return _Ctx()
