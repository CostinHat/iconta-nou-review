# -*- coding: utf-8 -*-
"""Înregistrarea liberă cu confirmarea emailului (comanda Costin 15.10.2026, „Lotul 4” pct.2, 3, 4, 6; verbatim în DECIZII).

Pe baza de TEST, pe drumul aplicației (`uc_auth`), cu emailuri sintetice (`@proba-inregistrare.test`) și cutia poștală de test
(`ICONTA_EMAIL_CUTIE`, în directorul testului): ce s-a scris se șterge la sfârșit, iar comutatorul revine la valoarea de dinainte.
Anti-roboții (257, DECIZII „Poarta o dată pe lot”): Cloudflare Turnstile, cu cheile de test ale Cloudflare și siteverify ÎNLOCUIT aici
(`_siteverify` -> răspunsuri fixe pe token: drumul real prin Cloudflare îl face plasa e2e) — testul e determinist, fără rețea.
MUTAȚII (DECIZII „Lotul 4”): contul creat la formular (nu la confirmare) -> pică primul test; verificarea Turnstile scoasă din
`_register_liber` -> pică testul anti-roboți; limita pe email scoasă -> pică testul limitelor; „deschisa” fără `email_functional` / fără
`chei_turnstile` -> pică testul comutatorului; cheile de test acceptate pe producție -> pică testul cheilor."""
import datetime
import glob
import json
import os
import re
import secrets
import types

import pytest

from core import db, erori, nucleu, uc_auth, setari_platforma as setp, inregistrare_libera as il, stare_partajata as sp

DOMENIU = "@proba-inregistrare.test"
_IP = "203.0.113.%d"


def _sql(q, p=(), unul=False):
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(q, p)
            r = cur.fetchall() if cur.description else None
        conn.commit()
    return (r[0] if r else None) if unul else r


@pytest.fixture()
def mediu(tmp_path, monkeypatch):
    """Cutia poștală de test, modul „liberă”; la final: rândurile probei șterse, comutatorul înapoi."""
    db.init_pool()
    monkeypatch.setenv("ICONTA_EMAIL_CUTIE", str(tmp_path))
    monkeypatch.delenv("BREVO_API_KEY", raising=False)
    monkeypatch.setenv("TURNSTILE_SITEKEY", SITEKEY_TEST)
    monkeypatch.setenv("TURNSTILE_SECRET", SECRET_TEST)
    monkeypatch.setattr(il, "_siteverify", _siteverify_fals)
    CERUTE.clear()
    inainte = _sql("SELECT valoare, modificat_de, modificat_la FROM public.setari_platforma WHERE cheie = 'inregistrare'", unul=True)
    _sql("UPDATE public.setari_platforma SET valoare = 'libera' WHERE cheie = 'inregistrare'")
    try:
        yield tmp_path
    finally:
        _sql("DELETE FROM public.acord_termeni WHERE email LIKE %s", ("%" + DOMENIU,))
        firme = [r[0] for r in _sql("SELECT accounting_firm_id FROM public.users WHERE email LIKE %s", ("%" + DOMENIU,))]
        _sql("DELETE FROM public.users WHERE email LIKE %s", ("%" + DOMENIU,))
        if firme:
            _sql("DELETE FROM public.accounting_firms WHERE id = ANY(%s)", (firme,))
        _sql("DELETE FROM public.inregistrari_in_asteptare WHERE email LIKE %s", ("%" + DOMENIU,))
        _sql("DELETE FROM public.cereri_ritm WHERE ip LIKE %s OR ip LIKE '203.0.113.%%'", ("%" + DOMENIU,))
        if inainte:
            _sql("UPDATE public.setari_platforma SET valoare = %s, modificat_de = %s, modificat_la = %s WHERE cheie = 'inregistrare'",
                 inainte)


SITEKEY_TEST, SECRET_TEST = il.CHEI_DE_TEST[0], il.CHEI_DE_TEST[5]   # cheile de test ale Cloudflare care trec mereu
CERUTE = []


def _siteverify_fals(secret, token, ip):
    """Ce ar răspunde Cloudflare: `tok-bun` trece; `tok-retea` = Cloudflare indisponibil; orice alt token e respins."""
    import urllib.error
    CERUTE.append((secret, token, ip))
    if token == "tok-retea":
        raise urllib.error.URLError("proba: rețeaua căzută")
    return {"success": True} if token == "tok-bun" else {"success": False, "error-codes": ["invalid-input-response"]}


def _email(eticheta):
    return "%s_%s%s" % (eticheta, secrets.token_hex(4), DOMENIU)


def _date(email, **k):
    d = dict(email=email, parola=secrets.token_urlsafe(12) + "-Pp1", nume_cabinet="Cabinet Proba Inregistrare", nume="Proba",
             prenume="Ana", cui="", accept_termeni=True, invitatie=None, turnstile="tok-bun")
    d.update(k)
    return types.SimpleNamespace(**d)


def _scrisori(cutie, catre):
    out = []
    for f in sorted(glob.glob(os.path.join(str(cutie), "*.json"))):
        m = json.load(open(f, encoding="utf-8"))
        if m["catre"] == catre:
            out.append(m)
    return out


def _link(cutie, email):
    (m,) = _scrisori(cutie, email)
    return re.search(r"#confirmare=([\w-]+)", m["html"]).group(1)


def test_pana_la_confirmare_nu_exista_cont_apoi_linkul_il_creeaza_o_singura_data(mediu):
    email = _email("flux")
    d = _date(email)
    r = uc_auth.register(d, ip=_IP % 1)
    assert r == {"confirmare_trimisa": True, "email": email, "valabila_ore": il.VALABILITATE_ORE}
    # până la clic: niciun cont, nicio firmă — numai cererea (cu hash-ul tokenului, nu tokenul)
    assert _sql("SELECT count(*) FROM public.users WHERE email = %s", (email,), unul=True) == (0,)
    tok = _link(mediu, email)
    assert _sql("SELECT count(*) FROM public.inregistrari_in_asteptare WHERE email = %s AND token_hash <> %s AND confirmata_la IS NULL",
                (email, tok), unul=True) == (1,)
    with pytest.raises(erori.Neautentificat) as e:            # parola bună, cont neconfirmat -> „confirmă emailul”
        uc_auth.login(types.SimpleNamespace(email=email, parola=d.parola))
    assert str(e.value) == il.MESAJ_NECONFIRMAT
    with pytest.raises(erori.Neautentificat) as e:            # parola greșită -> nu află nimic despre cerere
        uc_auth.login(types.SimpleNamespace(email=email, parola=secrets.token_hex(8)))
    assert str(e.value) != il.MESAJ_NECONFIRMAT
    c = uc_auth.confirma_inregistrarea(tok, ip=_IP % 1)
    assert (c["ok"], c["email"], c["nume_cabinet"]) == (True, email, "Cabinet Proba Inregistrare")
    assert _sql("SELECT activ, rol FROM public.users WHERE email = %s", (email,), unul=True) == (True, "admin_firma")
    assert _sql("SELECT count(*) FROM public.acord_termeni WHERE email = %s", (email,), unul=True) == (1,)
    with pytest.raises(erori.FaraDrept) as e:                 # o singură folosire
        uc_auth.confirma_inregistrarea(tok, ip=_IP % 1)
    assert str(e.value).startswith("Linkul a fost folosit deja")
    assert uc_auth.login(types.SimpleNamespace(email=email, parola=d.parola))["user"]["email"] == email
    sa = _sql("SELECT email FROM public.users WHERE rol='superadmin' AND activ=true ORDER BY id LIMIT 1", unul=True)[0]
    anunt = [m for m in _scrisori(mediu, sa) if m["subiect"] == "[iConta.eu] Cabinet nou: Cabinet Proba Inregistrare"]
    assert len(anunt) == 1 and anunt[0]["html"].count(email) == 1


def test_linkul_expira_si_cel_inventat_nu_exista(mediu):
    email = _email("exp")
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            vechi = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=il.VALABILITATE_ORE + 1)
            tok = il.creeaza(cur, {"email": email, "nume_cabinet": "X"}, nucleu.hash_parola(secrets.token_urlsafe(12)), "v1", None, acum=vechi)
            assert il.ia_pentru_confirmare(cur, tok)["refuz"]["cod"] == "EXPIRATA"
            assert il.ia_pentru_confirmare(cur, "inventat")["refuz"]["cod"] == "INEXISTENTA"
        conn.rollback()


def test_anti_robotii(mediu):
    """[257] Fără token / token respins de Cloudflare -> refuz cu motivul; Cloudflare indisponibil -> „nu răspunde”, nu „trece”; în
    toate trei: nicio cerere, niciun email. Cu tokenul bun, siteverify primește secretul, tokenul și IP-ul vizitatorului."""
    email = _email("robot")
    for token, eroare, mesaj in ((None, erori.CerereGresita, il.MESAJ_ANTIROBOT), ("tok-rau", erori.CerereGresita, il.MESAJ_ANTIROBOT),
                                 ("tok-retea", erori.ServiciuIndisponibil, il.MESAJ_ANTIROBOT_INDISPONIBIL)):
        with pytest.raises(eroare) as e:
            uc_auth.register(_date(email, turnstile=token), ip=_IP % 2)
        assert str(e.value) == mesaj, token
    assert _sql("SELECT count(*) FROM public.inregistrari_in_asteptare WHERE email = %s", (email,), unul=True) == (0,)
    assert _scrisori(mediu, email) == []
    CERUTE.clear()
    assert uc_auth.register(_date(_email("om")), ip=_IP % 3)["confirmare_trimisa"] is True
    assert CERUTE == [(SECRET_TEST, "tok-bun", _IP % 3)]


def test_cheile_de_test_numai_pe_instanta_de_proba(mediu, monkeypatch):
    """Cheile de test ale Cloudflare trec MEREU: pe producție (fără cutia poștală de test) se socotesc lipsă -> înregistrarea liberă e
    închisă, nu deschisă oricărui robot. O cheie adevărată trece."""
    assert il.chei_turnstile() == (SITEKEY_TEST, SECRET_TEST)
    monkeypatch.delenv("ICONTA_EMAIL_CUTIE")
    assert il.chei_turnstile() is None
    monkeypatch.setenv("TURNSTILE_SITEKEY", "0x4AAAAAAA" + secrets.token_hex(8))
    monkeypatch.setenv("TURNSTILE_SECRET", "0x4AAAAAAA" + secrets.token_hex(16))
    assert il.chei_turnstile() == (os.environ["TURNSTILE_SITEKEY"], os.environ["TURNSTILE_SECRET"])
    monkeypatch.setenv("TURNSTILE_SECRET", SECRET_TEST)                # o singură cheie de test ajunge ca să le refuze pe amândouă
    assert il.chei_turnstile() is None


def test_limita_pe_ora_pe_email_si_pe_ip(mediu):
    email = _email("lim")
    for i in range(il.LIMITA_EMAIL):
        uc_auth.register(_date(email), ip=_IP % (10 + i))
    with pytest.raises(erori.PreaDes) as e:                    # al patrulea pe același email, din alt IP
        uc_auth.register(_date(email), ip=_IP % 20)
    assert str(e.value) == il.MESAJ_PREA_DES
    for i in range(il.LIMITA_IP):
        uc_auth.register(_date(_email("ip%d" % i)), ip=_IP % 30)
    with pytest.raises(erori.PreaDes):                         # al șaselea din același IP, cu alt email
        uc_auth.register(_date(_email("ip9")), ip=_IP % 30)


def test_limita_de_o_ora_nu_e_stearsa_de_un_limitator_de_15_minute(mediu):
    """[ritm_incape pe cheie] rândurile de 40 de minute ale înregistrării rămân după ce un limitator de 15 minute scrie."""
    _sql("INSERT INTO public.cereri_ritm (cheie, ip, la) VALUES ('inregistrare_ip', %s, now() - interval '40 minutes')", (_IP % 40,))
    with db.get_conn() as conn:
        sp.ritm_incape(conn, "reset_parola", _IP % 41)
        conn.commit()
        assert sp.cereri_in_fereastra(conn, "inregistrare_ip", _IP % 40, fereastra_sec=il.FEREASTRA_SEC) == 1
    _sql("DELETE FROM public.cereri_ritm WHERE ip IN (%s, %s)", (_IP % 40, _IP % 41))


def test_comutatorul_si_emailul_inchid_inregistrarea(mediu, monkeypatch):
    email = _email("com")
    ctx = {"uid": None, "rol": "superadmin"}
    r = uc_auth.setare_inregistrare_scrie(types.SimpleNamespace(mod="invitatie"), ctx)
    assert (r["mod"], r["deschisa"]) == ("invitatie", False)
    with pytest.raises(erori.FaraDrept) as e:
        uc_auth.register(_date(email), ip=_IP % 50)
    assert str(e.value) == setp.MESAJ_NUMAI_INVITATIE
    st = uc_auth.inregistrare_stare()
    assert (st["deschisa"], st["mod"], st["refuz"]["cod"], st["refuz"]["motiv"]) == (False, "invitatie", "NUMAI_INVITATIE",
                                                                                   setp.MESAJ_NUMAI_INVITATIE)
    with pytest.raises(erori.DateInvalide):
        uc_auth.setare_inregistrare_scrie(types.SimpleNamespace(mod="oricum"), ctx)
    assert uc_auth.setare_inregistrare_scrie(types.SimpleNamespace(mod="libera"), ctx)["deschisa"] is True
    st = uc_auth.inregistrare_stare()
    assert (st["deschisa"], st["turnstile_sitekey"], st["turnstile_script"]) == (True, SITEKEY_TEST, il.SCRIPT_WIDGET)
    monkeypatch.delenv("TURNSTILE_SECRET")                     # [257] fără cheile anti-roboți, „liberă” rămâne închisă
    with pytest.raises(erori.ServiciuIndisponibil) as e:
        uc_auth.register(_date(email), ip=_IP % 52)
    assert str(e.value) == setp.MESAJ_FARA_ANTIROBOT
    st = uc_auth.inregistrare_stare()
    assert (st["deschisa"], st["refuz"]["cod"], st.get("turnstile_sitekey")) == (False, "FARA_ANTIROBOT", None)
    monkeypatch.setenv("TURNSTILE_SECRET", SECRET_TEST)
    monkeypatch.delenv("ICONTA_EMAIL_CUTIE")                   # fără email funcțional, „liberă” rămâne închisă (pct.1)
    with pytest.raises(erori.ServiciuIndisponibil) as e:
        uc_auth.register(_date(email), ip=_IP % 51)
    assert str(e.value) == setp.MESAJ_FARA_EMAIL
    assert _sql("SELECT count(*) FROM public.inregistrari_in_asteptare WHERE email = %s", (email,), unul=True) == (0,)


def test_emailul_care_nu_pleaca_nu_lasa_cererea(mediu, monkeypatch):
    from core import observare
    email = _email("fara")
    monkeypatch.setattr(observare, "trimite_email_html_sau_semnaleaza", lambda *a, **k: False)
    with pytest.raises(erori.ServiciuIndisponibil):
        uc_auth.register(_date(email), ip=_IP % 60)
    assert _sql("SELECT count(*) FROM public.inregistrari_in_asteptare WHERE email = %s", (email,), unul=True) == (0,)
