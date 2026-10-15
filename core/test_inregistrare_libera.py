# -*- coding: utf-8 -*-
"""Înregistrarea liberă cu confirmarea emailului (comanda Costin 15.10.2026, „Lotul 4” pct.2, 3, 4, 6; verbatim în DECIZII).

Pe baza de TEST, pe drumul aplicației (`uc_auth`), cu emailuri sintetice (`@proba-inregistrare.test`) și cutia poștală de test
(`ICONTA_EMAIL_CUTIE`, în directorul testului): ce s-a scris se șterge la sfârșit, iar comutatorul revine la valoarea de dinainte.
MUTAȚII (DECIZII „Lotul 4”): contul creat la formular (nu la confirmare) -> pică primul test; `MIN_SECUNDE = 0` -> pică testul
anti-roboți; limita pe email scoasă -> pică testul limitelor; „deschisa” fără `email_functional` -> pică testul comutatorului."""
import datetime
import glob
import json
import os
import re
import secrets
import types

import pytest

from core import db, erori, nucleu, uc_auth, setari_platforma as setp, inregistrare_libera as il, stare_partajata as sp
from core.common import cfg_secret

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


def _email(eticheta):
    return "%s_%s%s" % (eticheta, secrets.token_hex(4), DOMENIU)


def _formular(acum_minus=10):
    import time
    return il.jeton_formular(acum=int(time.time()) - acum_minus)


def _date(email, **k):
    d = dict(email=email, parola=secrets.token_urlsafe(12) + "-Pp1", nume_cabinet="Cabinet Proba Inregistrare", nume="Proba",
             prenume="Ana", cui="", accept_termeni=True, invitatie=None, formular=_formular(), site_web="")
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
    """Fără jeton / jeton de alt scop (sesiune) -> refuz; jeton trimis prea repede -> refuz; capcana completată -> răspunsul de
    reușită, fără cerere și fără email."""
    email = _email("robot")
    for formular in (None, nucleu.creeaza_token({"uid": 1}, cfg_secret("JWT_SECRET"))):
        with pytest.raises(erori.CerereGresita) as e:
            uc_auth.register(_date(email, formular=formular), ip=_IP % 2)
        assert str(e.value) == il.MESAJ_FORMULAR
    with pytest.raises(erori.CerereGresita) as e:
        uc_auth.register(_date(email, formular=_formular(acum_minus=0)), ip=_IP % 2)
    assert str(e.value) == il.MESAJ_PREA_REPEDE
    r = uc_auth.register(_date(email, site_web="https://spam.example"), ip=_IP % 3)
    assert r["confirmare_trimisa"] is True
    assert _sql("SELECT count(*) FROM public.inregistrari_in_asteptare WHERE email = %s", (email,), unul=True) == (0,)
    assert _scrisori(mediu, email) == []


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
    assert (st["deschisa"], il.verifica_formular(st["formular"], acum=int(datetime.datetime.now().timestamp()) + 5)) == (True, None)
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
