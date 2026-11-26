"""17.5-Q12 — cazurile controlate ale lotului (fără Chromium, fără 8019, fără rețea; baza de test numai la AC191 — episodul pe două conexiuni).

AC197  regula pragurilor după poarta roșie: candidatul A (114 s > 105 s) oprit, B corectiv (87 s) publicabil; depășirea urmată de reluare pe
       același SHA rămâne; pragul egal trece; SHA lipsă / scurt nu exclude rularea; jurnalul de probă (fișier), nu cel al lotului.
AC191  alerta de sănătate pe episoade: normal, anomalie, aceeași anomalie de mai multe ori, rezolvare, reapariție; repornire (starea în bază)
       și două verificări concurente pe aceeași cauză (un singur câștigător).
AC192  domeniile rezervate (.test, .example, .invalid, .localhost, numele însele, subdomenii, majuscule): niciun transport extern, nici rezerva.
AC194  WhatsApp numai PORNIT / OPRIT; copia pe e-mail a anunțului OPRIT scoasă; eroarea de transport trece pe e-mail (rezerva rămâne).
F028 / F070 / F169 / F179 / F034  funcțiile pure ale reparațiilor (luna cu două cifre, diacriticele temeiului, reconcilierea ciornelor,
       citirea SPV pe rezultat, ce lipsește operațiunii N).
"""
import datetime
import importlib.util
import json
import os
import sys
import threading
from decimal import Decimal

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(RAD, "scripts")


def _script(nume):
    sys.path.insert(0, SCRIPTS)
    try:
        spec = importlib.util.spec_from_file_location("q12_" + nume, os.path.join(SCRIPTS, nume + ".py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    finally:
        sys.path.remove(SCRIPTS)


# ── AC197 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
A_SHA, B_SHA = "a" * 40, "b" * 40


def _jurnal_proba(cale, randuri):
    """Jurnalul de probă în forma lui `.lot_jurnal.log` (TAB): lot, fază, început/sfârșit, ora, sha, rezultat, id, pid, detalii."""
    with open(cale, "w", encoding="utf-8") as f:
        for lot, faza, sha, inceput, sfarsit, rez, id_ in randuri:
            f.write("\t".join([lot, faza, "inceput", inceput, sha[:12], "-", id_, "1", ""]) + "\n")
            f.write("\t".join([lot, faza, "sfarsit", sfarsit, sha[:12], rez, id_, "1", ""]) + "\n")


def test_ac197_candidatul_inlocuit_nu_judeca_sha_final(tmp_path):
    PL = _script("publica_lot")
    cale = tmp_path / "jurnal.log"
    _jurnal_proba(cale, [
        ("Q", "poarta_verificator", A_SHA, "2026-11-26T10:00:00+02:00", "2026-11-26T10:01:54+02:00", "rosu_1", "1"),   # A: 114 s, roșu
        ("Q", "poarta_verificator", B_SHA, "2026-11-26T11:00:00+02:00", "2026-11-26T11:01:27+02:00", "verde", "2"),    # B: 87 s, verde
        ("Q", "hook", A_SHA, "2026-11-26T09:00:00+02:00", "2026-11-26T09:01:40+02:00", "ok", "3")])
    d = PL.durate_cu_sha("Q", str(cale))
    assert [x[5] for x in d] == [114, 87, 100]
    praguri = ["max poarta_verificator 105", "max hook 146"]
    assert PL.depasiri_praguri(PL.eligibile_sha_final(d, B_SHA), praguri)[0] == []                    # B publicabil
    assert PL.depasiri_praguri(PL.eligibile_sha_final(d, A_SHA), praguri)[0] == ["pragul „poarta_verificator” depășit: 114s > 105s"]
    assert PL.depasiri_praguri([x[:6] for x in d], praguri)[0] != []                                   # regula veche ar fi oprit B


def test_ac197_reluarea_pe_acelasi_sha_nu_sterge_depasirea_si_pragul_egal_trece(tmp_path):
    PL = _script("publica_lot")
    cale = tmp_path / "jurnal.log"
    _jurnal_proba(cale, [
        ("Q", "poarta_verificator", B_SHA, "2026-11-26T10:00:00+02:00", "2026-11-26T10:01:54+02:00", "rosu_1", "1"),
        ("Q", "poarta_verificator", B_SHA, "2026-11-26T11:00:00+02:00", "2026-11-26T11:01:20+02:00", "verde", "2"),
        ("Q", "poarta_pytest", B_SHA, "2026-11-26T11:02:00+02:00", "2026-11-26T11:14:10+02:00", "verde", "3")])
    d = PL.durate_cu_sha("Q", str(cale))
    stop = PL.depasiri_praguri(PL.eligibile_sha_final(d, B_SHA), ["max poarta_verificator 105", "max poarta_pytest 730"])[0]
    assert stop == ["pragul „poarta_verificator” depășit: 114s > 105s"]                                # 730 = 730: trece


def test_ac197_sha_lipsa_sau_scurt_nu_exclude():
    PL = _script("publica_lot")
    d = [("poarta_plasa", "1", "x", "y", "verde", 4000, ""), ("poarta_plasa", "2", "x", "y", "verde", 3900, "-"), ("poarta_plasa", "3", "x", "y", "verde", 3800, "ab12")]
    assert len(PL.eligibile_sha_final(d, B_SHA)) == 3


def test_ac197_dupa_rosu_verificare_imediata_si_oprirea_candidatului():
    PR = _script("poarta_rulare")
    rl = [{"faza": "poarta_verificator", "sha": A_SHA[:12], "secunde": 114, "rezultat": "rosu_1", "inceput": "2026-11-26T10:00:00+02:00"},
          {"faza": "poarta_pytest", "sha": A_SHA[:12], "secunde": 500, "rezultat": "verde", "inceput": "2026-11-26T10:02:00+02:00"},
          {"faza": "poarta_verificator", "sha": B_SHA[:12], "secunde": 87, "rezultat": "verde", "inceput": "2026-11-26T11:00:00+02:00"}]
    pr = {"poarta_verificator": 105, "poarta_pytest": 730}
    dep = PR.depasiri_dupa_rosu(rl, A_SHA, pr)
    assert dep == ["pragul „poarta_verificator” depășit: 114s > 105s"]
    assert PR.depasiri_dupa_rosu(rl, B_SHA, pr) == []
    assert PR.depasiri_dupa_rosu(rl, A_SHA, pr, de_la="2026-11-26T10:30:00+02:00") == []          # numai rularea acestei porți
    st = PR.opreste_candidat({"complete": [{"sha": A_SHA, "curat": False}], "reluari": [], "regresii": [], "oprit": None}, A_SHA, dep)
    assert st["candidati_opriti"] == {A_SHA: "pragul „poarta_verificator” depășit: 114s > 105s"} and st["oprit"] is None   # lotul nu e oprit
    assert len(st["complete"]) == 1                                                                   # A rămâne numărată (limita pe lot)


# ── AC191 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_ac191_traseul_episoadelor_cu_transport_controlat():
    from core import alerta_load as al
    deschise, livrari = set(), []

    def incepe(c):
        if c in deschise:
            return False
        deschise.add(c)
        return True

    def inchide(c):
        if c not in deschise:
            return False
        deschise.discard(c)
        return True
    traseu = [("normal", {"disc": None}), ("anomalie", {"disc": "Disc folosit: 80% (prag 75%)"}), ("aceeasi", {"disc": "Disc folosit: 81% (prag 75%)"}),
              ("aceeasi", {"disc": "Disc folosit: 82% (prag 75%)"}), ("nemasurat", {}), ("rezolvat", {"disc": None}), ("stabil", {"disc": None}),
              ("reaparitie", {"disc": "Disc folosit: 90% (prag 75%)"})]
    for pas, c in traseu:
        a, r = al.episoade(c, incepe, inchide)
        livrari.append((pas, len(a), len(r)))
    assert livrari == [("normal", 0, 0), ("anomalie", 1, 0), ("aceeasi", 0, 0), ("aceeasi", 0, 0), ("nemasurat", 0, 0), ("rezolvat", 0, 1),
                       ("stabil", 0, 0), ("reaparitie", 1, 0)]


def test_ac191_episodul_in_baza_repornire_si_concurenta():
    """Pe baza de test: aceeași cauză din două conexiuni deodată = un singur câștigător; după «repornire» (o conexiune nouă) anomalia care rămâne
    nu mai trimite; rezolvarea o trimite o dată. Cheia e a probei (șters la final)."""
    from core import db, repo_notificari_livrare as rnl
    try:
        db.init_pool()
    except Exception:  # noqa: BLE001 — pool deja inițializat
        pass
    cat = "ztest_q12_%d" % os.getpid()
    rezultate = []
    bariera = threading.Barrier(2)

    def verificare():
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                bariera.wait()
                rezultate.append(rnl.episod_incepe(cur, cat))
            conn.commit()
    try:
        fire = [threading.Thread(target=verificare) for _ in range(2)]
        [f.start() for f in fire]
        [f.join(30) for f in fire]
        assert sorted(rezultate) == [False, True]
        with db.get_conn() as conn:                     # „repornirea”: o conexiune nouă, starea din bază
            with conn.cursor() as cur:
                assert rnl.episod_incepe(cur, cat) is False
                assert rnl.episod_se_incheie(cur, cat) is True
                assert rnl.episod_se_incheie(cur, cat) is False
            conn.commit()
    finally:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM public.alerte_cooldown WHERE categorie = %s", (rnl.PREFIX_EPISOD + cat,))
            conn.commit()


# ── AC192 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("adresa,rezervata", [
    ("a@exemplu.test", True), ("A@B.TEST", True), ("x@test", True), ("x@example", True), ("x@invalid", True), ("x@localhost", True),
    ("y@sub.example.com", True), ("z@EXAMPLE.ORG.", True), ("w@foo.invalid", True), ("v@x.localhost", True), ("u@example.net", True),
    ("control@iconta.eu", False), ("r@gmail.com", False), ("s@testing.ro", False), ("t@example.co", False), ("fara-arond", True)])
def test_ac192_domeniile_rezervate(adresa, rezervata):
    from core import observare
    assert observare.adresa_rezervata(adresa) is rezervata


def test_ac192_niciun_transport_extern_nici_rezerva(monkeypatch, capsys):
    import urllib.request
    from core import observare
    apeluri = []

    class Raspuns:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b'{"ErrorCode": 0}'
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: apeluri.append(req.full_url) or Raspuns())
    monkeypatch.setenv("POSTMARK_SERVER_TOKEN", "pm_fals")
    monkeypatch.setenv("BREVO_API_KEY", "brevo_fals")
    monkeypatch.delenv("ICONTA_EMAIL_CUTIE", raising=False)
    for a in ("a@exemplu.test", "X@Sub.Example.COM", "z@localhost"):
        assert observare.trimite_email_html(a, "Probă", "<p>x</p>") is False
    assert apeluri == []
    jurnal = capsys.readouterr().out
    assert "domeniu rezervat de test" in jurnal and "a@exemplu" not in jurnal          # jurnalul fără partea personală a adresei
    assert observare.trimite_email_html("control@iconta.eu", "Probă", "<p>x</p>") is True
    assert apeluri == ["https://api.postmarkapp.com/email"]                           # controlul permis trece pe transport


def test_ac192_cutia_de_test_ramane_transportul_de_proba(monkeypatch, tmp_path):
    from core import observare
    monkeypatch.setenv("ICONTA_EMAIL_CUTIE", str(tmp_path))
    assert observare.trimite_email_html("a@exemplu.test", "Probă", "<p>x</p>") is True
    assert len(list(tmp_path.iterdir())) == 1


# ── AC194 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def alerta(monkeypatch, tmp_path):
    import urllib.request
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("ALERTA_WA_LOG", str(tmp_path / "alerte.log"))
    monkeypatch.setenv("WA_INCERCARI_LOG", str(tmp_path / "incercari.log"))
    monkeypatch.setenv("ALERTA_WA_CATRE", "+40700000123")
    monkeypatch.setenv("WHATSAPP_TOKEN", "TOKEN_FALS_Q12")
    monkeypatch.setenv("ICONTA_ALERTA_EMAIL", "alerta@iconta.eu")
    monkeypatch.delenv("ICONTA_WHATSAPP_SIMULAT", raising=False)
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: (_ for _ in ()).throw(AssertionError("rețea")))
    A = _script("alerta_whatsapp")
    A.cereri, A.emailuri, A.program = [], [], []

    def cere(cale, corp):
        A.cereri.append(cale)
        pas = A.program.pop(0) if A.program else None
        if pas:
            raise A.wa.Refuzat(pas)
        return {"messages": [{"id": "wamid.Q12_%d" % len(A.cereri)}]}
    monkeypatch.setattr(A.wa, "_cere", cere)
    monkeypatch.setattr(A.observare, "trimite_email_html", lambda catre, subiect, html, *a, **k: A.emailuri.append(subiect) or True)
    return A


def test_ac194_numai_pornit_si_oprit_pe_whatsapp_fara_copie_email(alerta):
    A = alerta
    A.alerta("17.5", "PORNIT", acum=datetime.datetime(2026, 11, 26, 12, 0))
    A.alerta("17.5", "nepublicat", "-", "poarta roșie", acum=datetime.datetime(2026, 11, 26, 13, 0))
    A.alerta("17.5", "publicat", "0123456789abcdef", acum=datetime.datetime(2026, 11, 26, 14, 0))
    assert len(A.cereri) == 3 and A.emailuri == []                    # trei anunțuri pe WhatsApp, nicio copie pe e-mail


def test_ac194_eroarea_de_transport_trece_pe_email(alerta):
    A = alerta
    A.program = ["Meta a refuzat cererea (HTTP 400): a", "Meta a refuzat cererea (HTTP 400): b"]
    A.alerta("17.5", "nepublicat", "-", "prag depășit", acum=datetime.datetime(2026, 11, 26, 13, 0))
    assert len(A.cereri) == 2 and A.emailuri == ["[iConta.eu] Lotul 17.5: OPRIT 13:00: prag depășit"]


# ── reparațiile, funcțiile pure ──────────────────────────────────────────────────────────────────────────────────────────────────────
def test_f028_luna_cu_doua_cifre_in_rezumat():
    from core.uc_declaratii import luna_doua_cifre
    assert luna_doua_cifre("D112: 1 salariat - CAM 313,00 lei (luna 9/2026).") == "D112: 1 salariat - CAM 313,00 lei (luna 09/2026)."
    assert luna_doua_cifre("(luna 10/2026)") == "(luna 10/2026)"


def test_f070_temeiul_cu_diacritice_original_pastrat():
    from core import produse_api as pa
    vechi = ("Painea alba este aliment pentru consum uman, incadrandu-se la art. 291 (2) b) Cod fiscal, fara zahar adaugat >= 10g/100g, "
             "deci cota redusa de 11% se aplica.")
    d = pa._temei_afisat({"justificare": vechi, "cota_tva": 11.0})
    assert d["justificare"] == ("Pâinea albă este aliment pentru consum uman, încadrându-se la art. 291 (2) b) Cod fiscal, fără zahăr adăugat "
                                ">= 10g/100g, deci cota redusă de 11% se aplică.")
    assert d["justificare_originala"] == vechi and d["cota_tva"] == 11.0
    assert pa._temei_afisat({"justificare": "Pâine albă feliată"}) == {"justificare": "Pâine albă feliată"}


def test_f169_reconcilierea_ciornelor_pana_la_rest():
    from core import control_incrucisat as ci
    note = [{"fel": "in_decont", "suma": "529.32"}, {"fel": "raport_z", "suma": "52.90"}, {"fel": "exclusa", "suma": "21.00"},
            {"fel": "fara_document", "suma": "14.70"}]
    t = ci._reconciliere_ciorne("4427", Decimal("529.06"), note)
    assert "(1, 529,32 lei), validate, o închid; rămân -0,26 lei din rotunjirea decontului la leu întreg" in t
    assert "(88,60 lei) nu intră în decont" in t and "suma tuturor ciornelor (617,92 lei) nu e egală cu diferența (529,06 lei)" in t
    t2 = ci._reconciliere_ciorne("4427", Decimal("600"), [{"fel": "in_decont", "suma": "500"}])
    assert "numai în parte; rest neexplicat de note: 100,00 lei." in t2
    assert ci._fel_ciorna({"sursa": "horeca_z"}, ()) == "raport_z"
    assert ci._fel_ciorna({"f_numar": "F1A17", "_document": "Factură F1A nr. 17 din 29.10.2026"}, {"Factură F1A nr. 17 din 29.10.2026"}) == "exclusa"
    assert ci._fel_ciorna({"f_numar": "F1A16", "_document": "x"}, set()) == "in_decont"
    assert ci._fel_ciorna({"sursa": "stocuri"}, set()) == "fara_document"


def test_f179_citirea_spv_pe_rezultat():
    from core.spv_receive import pe_rezultat
    inainte = {"ciorna": 3, "descarcata": 0, "deja": 5, "scurgere_evitata": 1, "skip_auth": 0, "descarca_esec": 0, "fara_xml": 0}
    dupa = {"ciorna": 4, "descarcata": 1, "deja": 7, "scurgere_evitata": 2, "skip_auth": 0, "descarca_esec": 1, "fara_xml": 0}
    assert pe_rezultat(inainte, dupa, 7) == {"gasite": 7, "importate": 2, "duplicate": 2, "refuzate": 1, "neimportate": 1}


def test_f034_ce_lipseste_operatiunii_n():
    from core import facturi_api as fa
    assert fa.lipsuri_operatiune_n("cereale", None) == ["subcodul NC al cerealelor (ex. 1001 grâu / 1005 porumb)", "județul vânzătorului"]
    assert fa.lipsuri_operatiune_n("1001", "CJ") == []
    assert fa.lipsuri_operatiune_n("deseuri", "IL") == []
    o = fa.optiuni_operatiune_n("cereale", "CJ")
    assert o["judete"] == [] and ["1001", "Grâu și meslin"] in o["coduri_nc"]


# ── AC195 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def rotatie_spv_pe_copie(conn):
    """Proba AC195 pe o copie izolată, în tranzacția conexiunii date (apelantul face rollback la final): tokenuri de probă criptate cu cheia veche,
    o rotație întreruptă (revenire: totul rămâne pe cheia veche), o rotație completă (fiecare valoare se recitește identic cu cheia nouă și numai cu
    ea), citirea în timpul rotației (cheia veche lângă cea nouă). Nicio valoare de token nu iese din funcție: numai numere și rezultate de integritate."""
    from cryptography.fernet import Fernet, InvalidToken
    from core import spv_conector as sc
    veche, noua = Fernet.generate_key().decode(), Fernet.generate_key().decode()
    clar = {("SER-Q12-%d" % i): ("acces-proba-%d" % i, "refresh-proba-%d" % i) for i in range(3)}
    os.environ["SPV_FERNET_KEY"] = veche
    with conn.cursor() as cur:
        for ser, (a, r) in clar.items():
            cur.execute("INSERT INTO public.spv_token (tenant_id, serial_certificat, access_token, refresh_token, access_expira, refresh_expira, activ) "
                        "VALUES ((SELECT id FROM public.tenants ORDER BY id LIMIT 1), %s, %s, %s, now(), now(), false)", (ser, sc.cripteaza(a), sc.cripteaza(r)))
        cur.execute("SAVEPOINT inainte_de_rotatie")

    def citeste():
        with conn.cursor() as cur:
            cur.execute("SELECT serial_certificat, access_token, refresh_token FROM public.spv_token WHERE serial_certificat LIKE 'SER-Q12-%%' ORDER BY id")
            return cur.fetchall()
    out = {"inregistrari": len(clar)}
    # întreruperea: a doua scriere cade -> rollback la savepoint; datele rămân pe cheia veche, toate citibile
    orig = sc.Fernet if hasattr(sc, "Fernet") else None
    pasi = {"n": 0}
    import cryptography.fernet as cf

    class Cade(cf.Fernet):
        def encrypt(self, data):
            pasi["n"] += 1
            if pasi["n"] == 3:
                raise RuntimeError("întrerupere simulată")
            return super().encrypt(data)
    real = cf.Fernet
    cf.Fernet = Cade
    try:
        try:
            sc.recripteaza_tokenuri(conn, veche, noua)
            out["intrerupere"] = "nu a căzut"
        except RuntimeError:
            with conn.cursor() as cur:
                cur.execute("ROLLBACK TO SAVEPOINT inainte_de_rotatie")
            out["intrerupere"] = "căzută, revenire la savepoint"
    finally:
        cf.Fernet = real
    v = Fernet(veche.encode())
    out["dupa_intrerupere_citibile_cu_veche"] = all((v.decrypt(a.encode()).decode(), v.decrypt(r.encode()).decode()) == clar[s] for s, a, r in citeste())
    rez = sc.recripteaza_tokenuri(conn, veche, noua)
    out["recriptate"] = rez
    n = Fernet(noua.encode())
    out["dupa_rotatie_identice_cu_noua"] = all((n.decrypt(a.encode()).decode(), n.decrypt(r.encode()).decode()) == clar[s] for s, a, r in citeste())
    try:
        v.decrypt(citeste()[0][1].encode())
        out["veche_nu_mai_citeste"] = False
    except InvalidToken:
        out["veche_nu_mai_citeste"] = True
    os.environ["SPV_FERNET_KEY"], os.environ["SPV_FERNET_KEY_VECHE"] = noua, veche
    try:
        out["citire_in_rotatie"] = sc.decripteaza(Fernet(veche.encode()).encrypt(b"x").decode()) == "x" and sc.decripteaza(sc.cripteaza("y")) == "y"
    finally:
        os.environ.pop("SPV_FERNET_KEY_VECHE", None)
    return out


def test_ac195_rotatia_cheii_spv_pe_copie_cu_recuperare():
    from core import db
    try:
        db.init_pool()
    except Exception:  # noqa: BLE001
        pass
    cheie = os.environ.get("SPV_FERNET_KEY")
    with db.get_conn() as conn:
        try:
            out = rotatie_spv_pe_copie(conn)
        finally:
            conn.rollback()
            if cheie is not None:
                os.environ["SPV_FERNET_KEY"] = cheie
    assert out == {"inregistrari": 3, "intrerupere": "căzută, revenire la savepoint", "dupa_intrerupere_citibile_cu_veche": True,
                   "recriptate": {"randuri": 3, "valori": 6}, "dupa_rotatie_identice_cu_noua": True, "veche_nu_mai_citeste": True,
                   "citire_in_rotatie": True}, out


def test_ac195_sesiunea_veche_expira_autentificarea_noua_reuseste():
    from core import auth_api
    user = {"id": 7, "rol": "cabinet", "accounting_firm_id": 1, "email": "proba@iconta.eu"}
    vechi = auth_api.emite_token(user, secret="secret-vechi-proba-q12-0123456789abcdef")
    assert auth_api.context_din_token(vechi, secret="secret-vechi-proba-q12-0123456789abcdef")["ok"] is True
    assert auth_api.context_din_token(vechi, secret="secret-nou-proba-q12-0123456789abcdef0")["ok"] is False      # după rotație
    nou = auth_api.emite_token(user, secret="secret-nou-proba-q12-0123456789abcdef0")
    assert auth_api.context_din_token(nou, secret="secret-nou-proba-q12-0123456789abcdef0")["ok"] is True
