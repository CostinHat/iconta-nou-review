# -*- coding: utf-8 -*-
"""USE_CASE — corpurile rutelor `/auth`.

[P7 · valul use-case, 13.09.2026] Corpurile au plecat din `main.py` VERBATIM, cu tranzactiile lor
cu tot: `with db.get_conn()` se deschide aici, in stratul care detine unitatea de lucru, nu in
stratul HTTP. `HTTPException(cod, mesaj)` a devenit `_erori.<Clasa>(mesaj)`; codul se pune la loc
in invelisul din `main.py`, dintr-o harta fixa. Mesajul si ordinea efectelor sunt neatinse.
"""
from core import db, auth_api, observare as _obs
from core import repo_admin
from core import erori as _erori
from core.common import cate as _cate
from core import uc_comun as _uc_comun
from core.mesaje import (EMAIL_INVALID)
from core import nucleu as _nucleu
from core import db, auth_api, tenant_provisioning, observare as _obs
from core import repo_utilizatori
from core import cui_forma as _forma_cui


def login(date):
    """[P7 · use-case] Corpul rutei `/auth/login`; docstringul ei a ramas in stratul HTTP."""
    _email = (date.email or "").strip().lower()
    if _uc_comun._login_blocat(_email):  # [login_lockout_v1] 5 esecuri / 15 min per cont
        raise _erori.PreaDes("Prea multe încercări eșuate pentru acest cont. Încearcă din nou peste câteva minute.")
    with db.get_conn() as conn:
        r = auth_api.login(conn, date.email, date.parola)
    if not r["ok"] and r.get("cod") == "CABINET_SUSPENDAT":
        # [lotul 13, 645] parola e corectă (auth_api o verifică înaintea suspendării), deci omul cabinetului află motivul ales, fără
        # linie de contact; nota internă a suspendării nu se arată
        from core import uc_admin as _uc_admin
        raise _erori.Neautentificat(_uc_admin.mesaj_suspendare(r.get("cabinet_id")))
    if not r["ok"]:
        _uc_comun._login_esec(_email)
        if _asteapta_confirmare(_email, date.parola):
            from core import inregistrare_libera as _il
            raise _erori.Neautentificat(_il.MESAJ_NECONFIRMAT)
        raise _erori.Neautentificat(r["mesaj"])
    _uc_comun._login_reset(_email)
    # [beta_gate_v1 SCOS 14.08] poarta "Site in lucru" eliminata - acces liber (decizie Costin).
    try:
        with db.get_conn() as conn2:
            with conn2.cursor() as cur:
                repo_admin.scrie_audit_login(cur, r["user"]["id"])
    except Exception as _e:
        _obs.esec_secundar("audit_log login", _e)  # inghitit, dar nu tacut (27.07.2026)
    return {"token": r["token"], "user": r["user"]}


def _asteapta_confirmare(email, parola):
    """[15.10.2026, lotul 4] Login eșuat: e o înregistrare liberă neconfirmată, cu aceeași parolă? (numai atunci se spune)."""
    from core import inregistrare_libera as _il
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                rez = _il.asteapta_confirmare(cur, email, parola)
            conn.rollback()
        return bool(rez)
    except Exception as _e:
        _obs.esec_secundar("login: cererea de inregistrare in asteptare", _e)
        return False


# [comanda Costin 05.10.2026 pct.1a] „un contabil nu pierde niciodată ce a completat — nici la expirarea sesiunii”. Măsurat:
# tokenul Anei a expirat la 24 h după logare (ICONTA_TOKEN_DURATA_SEC), în mijlocul unei facturi. Sesiunea VIE se reînnoiește
# cât se lucrează; una expirată, invalidată (parolă schimbată) sau suspendată NU (previzualizarea portalului o refuză deja
# filtrul global al scrierilor în modul preview).
MESAJ_REINNOIRE_INVALIDATA = "Sesiune încheiată (parola a fost schimbată). Autentifică-te din nou."


def reinnoieste(ctx):
    """Corpul rutei `/auth/reinnoieste`: un token nou, cu aceleași drepturi, pentru o sesiune încă validă."""
    from core import repo_main
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            r = repo_main.select_u(cur, ctx)
        if r and r[1] is not None and ctx.get("iat") is not None and ctx["iat"] < r[1]:
            raise _erori.Neautentificat(MESAJ_REINNOIRE_INVALIDATA)
        s = auth_api.sesiune_pentru_user(conn, ctx["uid"])
        conn.rollback()
    if not s.get("ok") and s.get("cod") == "CABINET_SUSPENDAT":   # [645] motivul suspendării, ca la logare
        from core import uc_admin as _uc_admin
        raise _erori.Neautentificat(_uc_admin.mesaj_suspendare(s.get("cabinet_id")))
    if not s.get("ok"):
        raise _erori.Neautentificat(s.get("mesaj") or "Sesiunea nu mai e valabilă. Autentifică-te din nou.")
    return {"token": s["token"], "user": s["user"]}


def _telefon(date):
    """Telefonul din formular, în forma internațională (None = gol sau nu e un număr)."""
    from core import whatsapp as _wa
    brut = str(getattr(date, "telefon", "") or "").strip()
    return _wa.normalizeaza(brut) if brut else None


def _scrie_telefonul(cur, user_id, telefon):
    if telefon and user_id:
        from core import repo_cont_notificari as _rcn
        _rcn.scrie_telefonul_contului_nou(cur, user_id, telefon)


def _valideaza_formularul(date):
    """Verificările comune ale formularului (bifa termenilor, parola, emailul) + versiunea termenilor, ÎNAINTEA oricărei scrieri."""
    # [lotul 11, deficiența 440, comanda Costin 11.1 pct.16: „toate erorile apar deodată, fiecare cu textul ei, în casetă și lângă câmp”]
    # bifa, parola, emailul, denumirea și telefonul se verifică toate; refuzul pleacă o dată (400, ca înainte), fiecare eroare cu câmpul
    # ei din formularul de înregistrare (`reg-…`, login.js)
    from core.erori import ErorileFormularului as _Erori
    er = _Erori("Contul nu s-a creat")
    cod = None
    if not date.accept_termeni:  # [termeni_v1] fara bifa -> contul NU se creeaza (gard pe backend, nu doar JS)
        er.camp("reg-termeni", "Trebuie să accepți Termenii și condițiile pentru a crea contul.")
    if not _nucleu.parola_ok(date.parola):  # [parola_min_v1] aceeasi cerinta ca activare/reset/schimbare
        er.camp("reg-parola", _nucleu.PAROLA_MESAJ)
    if not _uc_comun._email_valid(date.email):  # [email_valid_v1] email obligatoriu + format valid
        er.camp("reg-email", EMAIL_INVALID)
    if not str(date.nume_cabinet or "").strip():
        er.camp("reg-cabinet", "Completează denumirea cabinetului.")
    # [459, comanda Costin 11.3 pct.5] CUI-ul cabinetului (opțional): scris, se cere valabil — aceeași verificare ca la crearea firmei
    # (`tenant_provisioning.motiv_cui_firma_invalid`), înaintea contului; până azi contul se crea, iar firma proprie cădea după
    _cui_reg = str(getattr(date, "cui", "") or "").strip()
    if _cui_reg:
        _m_cui = tenant_provisioning.motiv_cui_firma_invalid(_cui_reg)
        if _m_cui:
            er.camp("reg-cui", _m_cui)
    # [17.10.2026, lotul 7 pct.2.2, verbatim în DECIZII] „câmp telefon opțional la înregistrarea cabinetului” — gol trece; scris, se cere
    # să fie un număr de telefon (se salvează NECONFIRMAT: confirmarea și canalul WhatsApp sunt în Setări cont -> Notificări)
    if str(getattr(date, "telefon", "") or "").strip() and not _telefon(date):
        from core import uc_cont_notificari as _ucn
        er.camp("reg-telefon", _ucn.MESAJ_TELEFON_INVALID)
        cod = _ucn.COD_TELEFON_INVALID if len(er.campuri) == 1 else None
    if er:
        d = er.detaliu()
        if len(d["erori_campuri"]) == 1 and not cod:
            raise _erori.CerereGresita(d["mesaj"])   # o singură eroare: textul ei, ca înainte (contractul celor patru refuzuri)
        raise _erori.CerereGresita(dict(d, cod=cod) if cod else d)
    # [P4, 09.09.2026] Versiunea termenilor se citește ÎNAINTE de tranzacție. Un fișier care
    # lipsește trebuie să oprească înregistrarea înainte de orice scriere — nu să lase în urmă un
    # cont fără dovada acordului.
    try:
        return _uc_comun._termeni_versiune(open(_uc_comun._TERMENI_PATH, encoding="utf-8").read())
    except OSError:
        raise _erori.ServiciuIndisponibil("Termenii și condițiile nu se pot citi acum, deci acordul tău "
                                 "nu s-ar putea consemna. Contul nu a fost creat. Încearcă din "
                                 "nou peste câteva minute.")


def register(date, ip=None):
    """[P7 · use-case] Corpul rutei `/auth/register`; docstringul ei a ramas in stratul HTTP.

    [15.10.2026, „Lotul 4”, verbatim în DECIZII] DOUĂ CĂI. Cu INVITAȚIE (lotul 2, „a doua cale, pentru cabinetele pe care le aduc
    eu”): contul se creează pe loc — linkul a ajuns la emailul invitat, deci emailul e dovedit. FĂRĂ invitație: numai dacă
    înregistrarea e liberă (comutatorul din Panou Admin, `setari_platforma`) și emailul poate pleca; atunci formularul devine o CERERE
    ÎN AȘTEPTARE (`inregistrare_libera`) și pleacă linkul de confirmare — contul, acordul și firma apar abia la clic."""
    _versiune_termeni = _valideaza_formularul(date)
    if str(getattr(date, "invitatie", "") or "").strip():
        return _register_cu_invitatie(date, _versiune_termeni)
    return _register_liber(date, _versiune_termeni, ip)


def _register_cu_invitatie(date, _versiune_termeni):
    # [P4] CONTUL ȘI DOVADA ACORDULUI, ÎN ACEEAȘI TRANZACȚIE.
    #
    # Ce era până azi: contul se crea într-o tranzacție, iar `acord_termeni` — dovada
    # consimțământului, cu versiunea textului — într-a doua, ambalată într-un `try` care doar
    # TIPĂREA la eșec. Ruta refuză din prima linie o înregistrare fără bifă; dar dovada bifei
    # putea lipsi în tăcere, iar contul rămânea. *Fără bifă contul nu se creează — deci nici
    # fără dovada ei.*
    # [14.10.2026, comanda Costin pct.3, verbatim în DECIZII „Lotul 2”] Invitația se verifică ÎNAINTE de orice scriere (fără ea,
    # nicio urmă), iar consumarea ei stă în ACEEAȘI tranzacție cu contul: un cont fără invitația lui consumată nu există, și nici o
    # invitație consumată fără cont.
    # [lotul 12, deficiența 642] firma proprie (din CUI) intră în ACEEAȘI tranzacție cu contul (`_firma_proprie`); datele ANAF ale
    # precompletării se iau ÎNAINTE, fără conexiune ținută (P5 val 3), și numai pentru o invitație valabilă
    from core import invitatii as _inv

    def _verifica_invitatia(cur):
        _s = _inv.stare(cur, date.invitatie)
        if not _s["valida"]:
            raise _erori.FaraDrept(_s["refuz"]["motiv"])
        if _s["email"] != date.email.strip().lower():
            raise _erori.FaraDrept("Invitația e pentru %s. Contul se creează numai cu emailul invitat." % _s["email"])
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            _verifica_invitatia(cur)
        conn.rollback()
    d_anaf = _anaf_firma_proprie(date.cui)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            _verifica_invitatia(cur)   # din nou, în tranzacția contului: invitația poate fi folosită între timp
        r = auth_api.inregistreaza_cabinet(
            conn, date.email, date.parola, date.nume_cabinet,
            nume=date.nume, prenume=date.prenume)
        if not r["ok"]:
            conn.rollback()
            raise _erori.CerereGresita(r["mesaj"])
        with conn.cursor() as cur:  # [termeni_v1] dovada de consimtamant: cine, cand, ce versiune
            repo_utilizatori.scrie_acordul_termenilor(cur, r.get("user_id"), r.get("firm_id"), date.email.strip().lower(), _versiune_termeni)
            _inv.consuma(cur, date.invitatie, date.email, r.get("firm_id"))
            _scrie_telefonul(cur, r.get("user_id"), _telefon(date))
        firma = _firma_proprie(conn, r, date.nume_cabinet, date.cui, d_anaf, camp="reg-cui",
                               din_nou="apoi apasă din nou „Creează cont”")
    return _dupa_cont_nou(r, date.nume_cabinet, date.email.strip().lower(), firma, "invitație")


def _register_liber(date, _versiune_termeni, ip):
    from core import inregistrare_libera as _il, setari_platforma as _set, stare_partajata as _sp
    email = date.email.strip().lower()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            stare = _set.inregistrare_libera(cur)
        conn.rollback()
    if not stare["deschisa"]:
        if stare["mod"] != _set.LIBERA:
            raise _erori.FaraDrept(stare["refuz"]["motiv"])
        raise _erori.ServiciuIndisponibil(stare["refuz"]["motiv"])
    # limitele pe oră se numără ÎNAINTEA verificării anti-roboți: și încercările respinse de ea consumă din ele
    with db.get_conn() as conn:
        pe_ip = _sp.ritm_incape(conn, "inregistrare_ip", ip or "?", maxreq=_il.LIMITA_IP, fereastra_sec=_il.FEREASTRA_SEC)
        pe_email = pe_ip and _sp.ritm_incape(conn, "inregistrare_email", email, maxreq=_il.LIMITA_EMAIL, fereastra_sec=_il.FEREASTRA_SEC)
        conn.commit()
    if not (pe_ip and pe_email):
        raise _erori.PreaDes(_il.MESAJ_PREA_DES)
    refuz = _il.verifica_turnstile(getattr(date, "turnstile", None), ip)   # [257] Cloudflare Turnstile
    if refuz:
        raise (_erori.ServiciuIndisponibil if refuz[0] == "indisponibil" else _erori.CerereGresita)(refuz[1])
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            if repo_utilizatori.contul_dupa_email(cur, email):
                raise _erori.Conflict("Există deja un cont cu emailul %s. Intră în cont (sau folosește „Am uitat parola”)." % email)
            tok = _il.creeaza(cur, {"email": email, "nume_cabinet": date.nume_cabinet.strip(), "nume": date.nume, "prenume": date.prenume,
                                    "cui": (date.cui or "").strip(), "telefon": _telefon(date)}, _nucleu.hash_parola(date.parola),
                            _versiune_termeni, ip)
        conn.commit()
    if not _trimite_confirmarea(email, date.nume_cabinet.strip(), tok):
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                _il.sterge(cur, tok)
            conn.commit()
        raise _erori.ServiciuIndisponibil("Emailul de confirmare nu a putut fi trimis la %s, deci contul nu a fost creat. Verifică "
                                          "adresa și încearcă din nou peste câteva minute." % email)
    with db.get_conn() as conn:   # [deficiența 282] momentul trimiterii, pe cerere (Panou Admin → Înregistrare)
        with conn.cursor() as cur:
            _il.marcheaza_trimis(cur, tok)
        conn.commit()
    return {"confirmare_trimisa": True, "email": email, "valabila_ore": _il.VALABILITATE_ORE}


def _trimite_confirmarea(email, nume_cabinet, tok):
    """Emailul cu linkul de confirmare (la înregistrare și la „Retrimite confirmarea”). True dacă a plecat."""
    import os
    from core import inregistrare_libera as _il
    link = os.environ.get("ICONTA_BAZA_URL", "http://localhost:8010") + "/#confirmare=" + tok
    html = ("<p>Bună,</p><p>Ai cerut crearea contului cabinetului <b>%s</b> pe iConta.eu.</p>"
            "<p><a href='%s' style='display:inline-block;background:#3d8fd6;color:#fff;padding:10px 22px;border-radius:6px;"
            "text-decoration:none'>Confirmă emailul și activează contul</a></p><p>Linkul e valabil %s și se folosește o "
            "singură dată. Până la confirmare contul nu există: nu te poți autentifica și nu se creează nicio firmă.</p>"
            "<p>Dacă nu tu ai cerut contul, ignoră acest email — fără clic nu se creează nimic.</p>") % (
                _esc(nume_cabinet), link, _esc(_cate(_il.VALABILITATE_ORE, "oră", "ore")))
    return _obs.trimite_email_html_sau_semnaleaza("email confirmare inregistrare", email, "Confirmă contul iConta.eu", html, postmark=True, alerta=True)


def inregistrari_neconfirmate(ctx):
    """[deficiența 282, comanda Costin 16.10.2026, verbatim în DECIZII] Corpul rutei `GET /admin/inregistrari-neconfirmate`: „data,
    denumirea cabinetului, emailul, dacă emailul de confirmare a plecat și când expiră linkul”."""
    from core import inregistrare_libera as _il
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            r = _il.neconfirmate(cur)
        conn.rollback()
    return {"cereri": r, "valabila_ore": _il.VALABILITATE_ORE}


def retrimite_confirmarea(cerere_id, ctx):
    """[deficiența 282] „Retrimite confirmarea”: link nou (cel vechi nu mai merge), valabil din nou VALABILITATE_ORE. Tokenul nou se
    scrie numai dacă emailul a plecat — altfel cererea rămâne cu linkul ei de dinainte. Emailul pleacă FĂRĂ conexiune ținută (clasa
    C5, `core/test_val3_contracte.py`): citirea cererii și scrierea tokenului sunt două tranzacții scurte, de o parte și de alta."""
    import secrets
    from core import inregistrare_libera as _il
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            c = _il.cerere_neconfirmata(cur, cerere_id)
        conn.rollback()
    if not c:
        raise _erori.Inexistent("Cererea nu mai așteaptă confirmarea: a fost confirmată sau ștearsă între timp.")
    email, nume_cabinet = c
    tok = secrets.token_urlsafe(32)
    if not _trimite_confirmarea(email, nume_cabinet, tok):
        raise _erori.ServiciuIndisponibil("Emailul de confirmare nu a putut fi retrimis la %s; linkul de dinainte a rămas "
                                          "valabil. Încearcă din nou peste câteva minute." % email)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            scris = _il.inlocuieste_tokenul(cur, cerere_id, tok)
        conn.commit()
    if not scris:
        raise _erori.Inexistent("Cererea a fost confirmată sau ștearsă cât pleca emailul: linkul nou nu mai e necesar.")
    return {"ok": True, "email": email, "valabila_ore": _il.VALABILITATE_ORE}


def _esc(t):
    import html as _h
    return _h.escape(str(t or ""), quote=True)


def confirma_inregistrarea(token, ip=None):
    """Corpul rutei `POST /public/confirma-inregistrare`: clicul pe linkul din email. ÎNTR-O SINGURĂ TRANZACȚIE: cererea (blocată),
    contul, dovada acordului termenilor (versiunea de la formular) și folosirea cererii — un cont fără cererea lui folosită nu există,
    și nici o cerere folosită fără cont. Apoi, ca la orice cont nou: bun venit, anunțul către superadmin, firma din CUI."""
    from core import inregistrare_libera as _il, stare_partajata as _sp
    with db.get_conn() as conn:
        incape = _sp.ritm_incape(conn, "confirmare_ip", ip or "?", maxreq=_il.LIMITA_CONFIRMARE_IP, fereastra_sec=_il.FEREASTRA_SEC)
        conn.commit()
    if not incape:
        raise _erori.PreaDes("Prea multe confirmări în ultima oră de la această adresă. Încearcă din nou peste o oră.")
    # [lotul 12, 642] datele ANAF ale firmei proprii, ÎNAINTEA tranzacției contului (fără conexiune ținută, P5 val 3): CUI-ul se citește
    # din cerere, fără s-o folosească; în tranzacție cererea se blochează și se verifică din nou
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            s0 = _il.ia_pentru_confirmare(cur, token)
        conn.rollback()
    d_anaf = _anaf_firma_proprie(s0["cerere"]["cui"]) if s0["valida"] else None
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            s = _il.ia_pentru_confirmare(cur, token)
            if not s["valida"]:
                conn.rollback()
                raise _erori.FaraDrept(s["refuz"]["motiv"])
            c = s["cerere"]
            if repo_utilizatori.contul_dupa_email(cur, c["email"]):
                conn.rollback()
                raise _erori.Conflict("Există deja un cont cu emailul %s. Intră în cont." % c["email"])
        r = auth_api.inregistreaza_cabinet(conn, c["email"], None, c["nume_cabinet"], nume=c["nume"], prenume=c["prenume"],
                                           parola_hash=c["parola_hash"])
        if not r["ok"]:
            conn.rollback()
            raise _erori.CerereGresita(r["mesaj"])
        with conn.cursor() as cur:
            repo_utilizatori.scrie_acordul_termenilor(cur, r["user_id"], r["firm_id"], c["email"], c["termeni_versiune"])
            _il.marcheaza_confirmata(cur, c["id"], r["firm_id"])
            _scrie_telefonul(cur, r["user_id"], c.get("telefon"))
        firma = _firma_proprie(conn, r, c["nume_cabinet"], c["cui"], d_anaf,
                               din_nou="apoi înregistrează-te din nou, cu CUI-ul corect sau fără CUI")
    raspuns = _dupa_cont_nou(r, c["nume_cabinet"], c["email"], firma, "înregistrare liberă")
    raspuns.update({"ok": True, "email": c["email"], "nume_cabinet": c["nume_cabinet"]})
    return raspuns


def _anunta_cabinet_nou(nume_cabinet, email, cale):
    """[15.10.2026, „Lotul 4” pct.4: „La fiecare cabinet nou confirmat primesc un email de anunț”] Către superadmin, la FIECARE cabinet
    (fără pragul de 15 minute al alertelor: un al doilea cabinet în același sfert de oră nu se mai pierde). Înlocuiește alerta
    `alerta_cont_nou_v1` (fără date: o alegere din cod, nu o decizie — anunțul cerut numește cabinetul)."""
    from datetime import datetime as _dt
    from zoneinfo import ZoneInfo as _Z
    from core import repo_main
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                dest = repo_main.select_public_2(cur)
            conn.rollback()
        dest = dest[0] if dest else None
    except Exception as _e:
        _obs.esec_secundar("anunt cabinet nou: emailul superadminului", _e)
        return False
    if not dest:
        _obs.esec_secundar("anunt cabinet nou", RuntimeError("niciun superadmin activ"))
        return False
    from core.pdf_util import data_ro
    acum = data_ro(_dt.now(_Z("Europe/Bucharest")), "cu_ora")   # formatorul canonic al datelor (DS cap.4)
    html = ("<p>Cabinet nou pe iConta.eu: <b>%s</b> (%s), creat la %s, prin %s.</p>"
            "<p>Îl vezi în Panou Admin &rarr; Activitate cabinete.</p>") % (_esc(nume_cabinet), _esc(email), _esc(acum), _esc(cale))
    return _obs.trimite_email_html_sau_semnaleaza("email anunt cabinet nou", dest, "[iConta.eu] Cabinet nou: %s" % nume_cabinet,
                                                  html, postmark=True)   # [lotul 13, 13.1 pct.1] tranzacțional: Postmark, rezerva Brevo


def _anaf_firma_proprie(cui):
    """Datele ANAF pentru precompletarea firmei proprii, luate ÎNAINTEA tranzacției contului (apelul are termen 20 s; P5 val 3: nu cu
    o conexiune ținută). None fără CUI sau cu ANAF căzut — atunci profilul firmei rămâne de completat manual, firma se creează."""
    if not str(cui or "").strip() or not _uc_comun._TENANT_TEMPLATE:
        return None
    try:
        return tenant_provisioning.date_din_anaf(cui)
    except Exception as _e:
        _obs.esec_secundar("precompletare ANAF la register", _e)
        return None


#: [642] începutul refuzului: contul nu se creează fără firma lui
_FARA_CONT = "Contul nu s-a creat: firma proprie a cabinetului (CUI %s) nu se poate adăuga. %s"


def _firma_proprie(conn, r, nume_cabinet, cui, d_anaf, camp=None, din_nou=""):
    """[lotul 12, deficiența 642 — comanda Costin 12.2 pct.19: „contul s-a creat, firma proprie a cabinetului nu (emailul «Eșec pe cale
    secundară: provisionare tenant la register»), iar emailul de bun venit spune că firma există”] Firma proprie a cabinetului, din CUI-ul
    scris la înregistrare, în TRANZACȚIA CONTULUI (`conn`, încă necomisă): contul și firma lui se creează împreună sau deloc.

    CAUZA: contul (cu acordul și invitația / cererea folosită) se comitea întâi, apoi `_dupa_cont_nou` trimitea bun venitul — cu fraza
    fixă „Firma proprie a cabinetului este deja adăugată în portofoliu.”, înainte de a încerca firma — și abia apoi crea firma într-o
    a doua tranzacție; o cădere (CUI-ul cu cifra de control greșită dintr-o cerere scrisă înainte de verificarea 459, un CUI al altui
    cabinet, o eroare tehnică) se înghițea în `esec_secundar` și contul rămânea fără firmă. În plus, o cădere a precompletării ANAF în
    aceeași tranzacție (fără punct de revenire) lăsa tranzacția stricată, iar `commit` o anula tăcut, cu „firma creată” în răspuns.

    Fără CUI: nicio firmă (None). Cu CUI: {cui, schema_name} sau ridică — refuzul numit (`CerereGresita`, cu câmpul `camp` când
    formularul îl are), ori `EsecIntern` (cu alertă) la o cădere tehnică; apelantul nu prinde, deci tranzacția contului cade cu tot.
    Precompletarea din ANAF stă sub un punct de revenire: lipsa ei nu e lipsa firmei (profilul se completează manual)."""
    if not str(cui or "").strip():
        return None
    _cui = _forma_cui.stocare(cui) or ""
    try:
        if not _uc_comun._TENANT_TEMPLATE:
            raise RuntimeError("șablonul firmei (tenant_template.sql) nu e încărcat")
        _t = tenant_provisioning.provision_tenant(conn, nume_cabinet, _cui, r["firm_id"], r["user_id"], _uc_comun._TENANT_TEMPLATE)
        # [register_cabinet_cui_v1] CUI-ul a trecut cifra de control în provision_tenant -> descrie entitatea proprie a cabinetului; se
        # păstrează ȘI pe accounting_firms.cui, altfel Setări cabinet îl citește NULL
        auth_api.actualizeaza_cabinet(conn, r["firm_id"], cui=_cui)
    except ValueError as _e:   # refuzul numit: CUI greșit (`CuiInvalid`), CUI al altui cabinet (`CheieDublata`), firmă dublată
        motiv = str(_e).strip()
        indemn = "Corectează CUI-ul (sau lasă-l gol și adaugă firma după intrarea în cont), %s." % din_nou if din_nou else ""
        mesaj = _FARA_CONT % (cui.strip(), (motiv + " " + indemn).strip())
        if not camp:
            raise _erori.CerereGresita(mesaj)
        raise _erori.CerereGresita({"mesaj": mesaj, "erori_campuri": [{"camp": camp, "mesaj": motiv}]})
    except Exception as _e:
        _obs.esec_secundar("provisionare tenant la register (contul NU s-a creat)", _e, alerta=True)
        raise _erori.EsecIntern(_FARA_CONT % (cui.strip(), "A apărut o eroare tehnică; nimic nu s-a scris. Încearcă din nou peste "
                                              "câteva minute."))
    # [register_profil_anaf_v2] precompletarea din ANAF (sursa unică), sub punct de revenire: căderea ei nu strică tranzacția contului
    tenant_provisioning.precompleteaza_sau_semnaleaza(conn, _t["schema_name"], d_anaf, "precompletare ANAF la register", seteaza_nume=True)
    return {"cui": _cui, "schema_name": _t["schema_name"]}


def text_bun_venit(nume_cabinet, email, firma):
    """[642] Emailul de bun venit spune ce s-a întâmplat: firma proprie numai când s-a creat (`_firma_proprie`), altfel unde se adaugă."""
    rand_firma = ("<p>Firma proprie a cabinetului (CUI %s) a fost adăugată în portofoliu.</p>" % _esc(firma["cui"]) if firma else
                  "<p>Firmele (și firma proprie a cabinetului) le adaugi după intrarea în cont, din ecranul Firme.</p>")
    return ("<p>Bună,</p><p>Contul cabinetului <b>%s</b> a fost creat pe iConta.eu.</p>"
            "<p>Te poți autentifica oricând cu emailul <b>%s</b> la <a href='https://iconta.eu'>iconta.eu</a>.</p>%s") % (
                _esc(nume_cabinet), _esc(email), rand_firma)


def _dupa_cont_nou(r, nume_cabinet, email, firma, cale):
    """Ce urmează oricărui cont nou de cabinet (invitație sau confirmare), DUPĂ commitul contului și al firmei lui (`_firma_proprie`):
    bun venit (cu ce s-a creat), anunțul către superadmin."""
    # register_email_v1: email de bun venit — [R73] fara alerta: bun venit nu e cale de ACCES, doar politete
    _obs.trimite_email_html_sau_semnaleaza("email bun venit cabinet", email, "Bine ai venit pe iConta.eu",
                                           text_bun_venit(nume_cabinet, email, firma), postmark=True)   # [lotul 13, 13.1 pct.1]
    _anunta_cabinet_nou(nume_cabinet, email, cale)
    return {"user_id": r["user_id"], "firm_id": r["firm_id"]}


# ── INVITAȚIILE (14.10.2026, comanda Costin pct.3: conturile noi de cabinet numai prin invitație) ─────────────────────────────
def invitatie_creeaza(date, ctx):
    """[superadmin] Invită un email: creează invitația și trimite linkul. Întoarce și linkul (superadminul îl poate da direct,
    dacă emailul nu ajunge) — e singura dată când tokenul apare în clar."""
    import os
    from core import invitatii as _inv
    email = str(date.email or "").strip().lower()
    if not _uc_comun._email_valid(email):
        raise _erori.DateInvalide(EMAIL_INVALID)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            if repo_utilizatori.contul_dupa_email(cur, email):
                raise _erori.Conflict("Există deja un cont cu emailul %s; nu e nevoie de invitație." % email)
            tok = _inv.creeaza(cur, email, ctx["uid"])
    link = os.environ.get("ICONTA_BAZA_URL", "http://localhost:8010") + "/#invitatie=" + tok
    html = ("<p>Bună,</p><p>Ești invitat să creezi contul cabinetului tău pe iConta.eu.</p>"
            "<p><a href='%s' style='display:inline-block;background:#3d8fd6;color:#fff;padding:10px 22px;border-radius:6px;"
            "text-decoration:none'>Creează contul</a></p><p>Contul se creează cu emailul <b>%s</b>. Invitația e valabilă %s "
            "și se folosește o singură dată.</p>") % (link, _esc(email), _esc(_cate(_inv.VALABILITATE_ZILE, "zi", "zile")))
    # superadminul vede pe ecran dacă a plecat (și primește linkul oricum) -> fără alertă
    trimis = _obs.trimite_email_html_sau_semnaleaza("email invitatie cabinet", email, "Invitație iConta.eu", html,
                                                    postmark=True)   # [lotul 13, 13.1 pct.1] tranzacțional: Postmark, rezerva Brevo
    return {"ok": True, "email": email, "link": link, "email_trimis": trimis, "valabila_zile": _inv.VALABILITATE_ZILE}


def invitatii_lista(ctx):
    """[superadmin] Invitațiile trimise (fără tokenuri)."""
    from core import invitatii as _inv
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            r = _inv.lista(cur)
        conn.rollback()
    return {"invitatii": r}


def invitatie_retrage(invitatie_id, ctx):
    """[superadmin, lotul 13, 646 e] Retrage o invitație nefolosită: linkul ei nu mai creează cont."""
    from core import invitatii as _inv
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            email = _inv.retrage(cur, invitatie_id)
    if not email:
        raise _erori.Conflict("Invitația nu se mai poate retrage: a fost folosită, retrasă deja sau nu există.")
    return {"ok": True, "email": email}


def invitatie_stare(token):
    """[public] Starea unei invitații: emailul invitat, dacă mai e valabilă (ecranul de înregistrare)."""
    from core import invitatii as _inv
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            s = _inv.stare(cur, token)
        conn.rollback()
    return s


# ── ÎNREGISTRAREA LIBERĂ: starea publică și comutatorul (15.10.2026, „Lotul 4” pct.2 și 6) ─────────────────────────────────────
def inregistrare_stare():
    """[public] `{deschisa, mod, refuz[, turnstile_sitekey, turnstile_script, valabila_ore]}` — formularul primește cheia publică a
    widgetului anti-roboți (Cloudflare Turnstile, deficiența 257) numai când e deschisă."""
    from core import inregistrare_libera as _il, setari_platforma as _set
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            st = _set.inregistrare_libera(cur)
        conn.rollback()
    if st["deschisa"]:
        st["turnstile_sitekey"], st["turnstile_script"] = _il.chei_turnstile()[0], _il.SCRIPT_WIDGET
        st["valabila_ore"] = _il.VALABILITATE_ORE
    return st


def setare_inregistrare_citeste(ctx):
    """[superadmin] Modul înregistrării + dacă emailul poate pleca (fără email, „liberă” rămâne închisă)."""
    from core import setari_platforma as _set
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            m = _set.mod_inregistrare(cur)
            st = _set.inregistrare_libera(cur)
        conn.rollback()
    m.update({"moduri": [{"mod": k, "eticheta": _set.ETICHETE[k]} for k in _set.MODURI], "deschisa": st["deschisa"],
              "refuz": st["refuz"], "email_functional": _set.email_functional()})
    return m


def setare_inregistrare_scrie(date, ctx):
    """[superadmin] Schimbă modul înregistrării (fără publicare); cine și când rămân scrise."""
    from core import setari_platforma as _set
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            try:
                _set.seteaza_mod_inregistrare(cur, str(date.mod or ""), ctx["uid"])
            except ValueError as e:
                raise _erori.DateInvalide(str(e))
    return setare_inregistrare_citeste(ctx)
