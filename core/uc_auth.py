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


def login(date):
    """[P7 · use-case] Corpul rutei `/auth/login`; docstringul ei a ramas in stratul HTTP."""
    _email = (date.email or "").strip().lower()
    if _uc_comun._login_blocat(_email):  # [login_lockout_v1] 5 esecuri / 15 min per cont
        raise _erori.PreaDes("Prea multe încercări eșuate pentru acest cont. Încearcă din nou peste câteva minute.")
    with db.get_conn() as conn:
        r = auth_api.login(conn, date.email, date.parola)
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
    if not s.get("ok"):
        raise _erori.Neautentificat(s.get("mesaj") or "sesiune invalidă")
    return {"token": s["token"], "user": s["user"]}


def _valideaza_formularul(date):
    """Verificările comune ale formularului (bifa termenilor, parola, emailul) + versiunea termenilor, ÎNAINTEA oricărei scrieri."""
    if not date.accept_termeni:  # [termeni_v1] fara bifa -> contul NU se creeaza (gard pe backend, nu doar JS)
        raise _erori.CerereGresita("Trebuie să accepți Termenii și condițiile pentru a crea contul.")
    if not _nucleu.parola_ok(date.parola):  # [parola_min_v1] aceeasi cerinta ca activare/reset/schimbare
        raise _erori.CerereGresita(_nucleu.PAROLA_MESAJ)
    if not _uc_comun._email_valid(date.email):  # [email_valid_v1] email obligatoriu + format valid
        raise _erori.CerereGresita(EMAIL_INVALID)
    if not str(date.nume_cabinet or "").strip():
        raise _erori.CerereGresita("Completează denumirea cabinetului.")
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
    from core import invitatii as _inv
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            _s = _inv.stare(cur, date.invitatie)
        if not _s["valida"]:
            raise _erori.FaraDrept(_s["refuz"]["motiv"])
        if _s["email"] != date.email.strip().lower():
            raise _erori.FaraDrept("Invitația e pentru %s. Contul se creează numai cu emailul invitat." % _s["email"])
        r = auth_api.inregistreaza_cabinet(
            conn, date.email, date.parola, date.nume_cabinet,
            nume=date.nume, prenume=date.prenume)
        if r["ok"]:  # [termeni_v1] dovada de consimtamant: cine, cand, ce versiune
            with conn.cursor() as cur:
                repo_utilizatori.scrie_acordul_termenilor(cur, r.get("user_id"), r.get("firm_id"), date.email.strip().lower(), _versiune_termeni)
                _inv.consuma(cur, date.invitatie, date.email, r.get("firm_id"))
    if not r["ok"]:
        raise _erori.CerereGresita(r["mesaj"])
    return _dupa_cont_nou(r, date.nume_cabinet, date.email.strip().lower(), date.cui, "invitație")


def _register_liber(date, _versiune_termeni, ip):
    import os
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
                                    "cui": (date.cui or "").strip()}, _nucleu.hash_parola(date.parola), _versiune_termeni, ip)
        conn.commit()
    link = os.environ.get("ICONTA_BAZA_URL", "http://localhost:8010") + "/#confirmare=" + tok
    html = ("<p>Bună,</p><p>Ai cerut crearea contului cabinetului <b>%s</b> pe iConta.eu.</p>"
            "<p><a href='%s' style='display:inline-block;background:#3d8fd6;color:#fff;padding:10px 22px;border-radius:6px;"
            "text-decoration:none'>Confirmă emailul și activează contul</a></p><p>Linkul e valabil %s și se folosește o "
            "singură dată. Până la confirmare contul nu există: nu te poți autentifica și nu se creează nicio firmă.</p>"
            "<p>Dacă nu tu ai cerut contul, ignoră acest email — fără clic nu se creează nimic.</p>") % (
                _esc(date.nume_cabinet.strip()), link, _esc(_cate(_il.VALABILITATE_ORE, "oră", "ore")))
    if not _obs.trimite_email_html_sau_semnaleaza("email confirmare inregistrare", email, "Confirmă contul iConta.eu", html,
                                                  alerta=True, cerut_de_destinatar=True):   # [268] și la o adresă dezabonată
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                _il.sterge(cur, tok)
            conn.commit()
        raise _erori.ServiciuIndisponibil("Emailul de confirmare nu a putut fi trimis la %s, deci contul nu a fost creat. Verifică "
                                          "adresa și încearcă din nou peste câteva minute." % email)
    return {"confirmare_trimisa": True, "email": email, "valabila_ore": _il.VALABILITATE_ORE}


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
    raspuns = _dupa_cont_nou(r, c["nume_cabinet"], c["email"], c["cui"], "înregistrare liberă")
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
                                                  html)


def _dupa_cont_nou(r, nume_cabinet, email, cui, cale):
    """Ce urmează oricărui cont nou de cabinet (invitație sau confirmare): bun venit, anunțul către superadmin, firma din CUI."""
    # register_email_v1: email de bun venit — [R73] fara alerta: bun venit nu e cale de ACCES, doar politete
    html = ("<p>Bună,</p><p>Contul cabinetului <b>%s</b> a fost creat pe iConta.eu.</p>"
            "<p>Te poți autentifica oricând cu emailul <b>%s</b> la <a href='https://iconta.eu'>iconta.eu</a>.</p>"
            "<p>Firma proprie a cabinetului este deja adăugată în portofoliu.</p>") % (_esc(nume_cabinet), _esc(email))
    _obs.trimite_email_html_sau_semnaleaza("email bun venit cabinet", email, "Bine ai venit pe iConta.eu", html)
    _anunta_cabinet_nou(nume_cabinet, email, cale)
    # [register_firma_v2 27.07.2026] Provisionarea primei firme poate esua (ANAF jos, schema
    # incompleta, DB). Inainte, esecul era INGHITIT si raspunsul spunea SUCCES - userul ramanea
    # cu cont valid si FARA firma, fara sa stie. Contul NU se anuleaza (e valid si util), dar
    # raspunsul poarta adevarul, iar ecranul il arata.
    _firma_ok = None                       # None = nu s-a incercat (fara CUI la inregistrare)
    _firma_motiv = ""
    if cui and _uc_comun._TENANT_TEMPLATE:  # register_primul_tenant_v1: entitatea proprie = prima firma
        _firma_ok = False
        # [P5 val 3, 11.09.2026] ANAF ÎNAINTE de conexiune: apelul are termen 20 s, iar forma
        # dinainte îl făcea cu tranzacția de creare a cabinetului deschisă. Eșecul se înghite și
        # se consemnează, exact ca înainte — firma rămâne creată, profilul completabil manual.
        try:
            _d_anaf = tenant_provisioning.date_din_anaf(cui)
        except Exception as _e:
            _obs.esec_secundar("precompletare ANAF la register", _e)
            _d_anaf = None
        try:
            with db.get_conn() as conn:
                _cui = cui.replace("RO", "").strip()
                _t = tenant_provisioning.provision_tenant(
                    conn, nume_cabinet, _cui,
                    r["firm_id"], r["user_id"], _uc_comun._TENANT_TEMPLATE)
                # [register_cabinet_cui_v1] CUI-ul a trecut cifra de control in provision_tenant
                # -> descrie entitatea proprie a cabinetului. Se persista SI pe accounting_firms.cui
                # (nu doar pe firma-tenant): altfel get_cabinet il citeste NULL si ecranul Setari
                # cabinet ramane gol desi userul l-a tastat si verificat la ANAF la inregistrare.
                auth_api.actualizeaza_cabinet(conn, r["firm_id"], cui=_cui)
                # [register_profil_anaf_v1] Datele de la ANAF se SALVEAZA in profil, nu
                # doar se afiseaza pe ecran la inregistrare. Fara ele firma noua se naste
                # cu caen gol si platitor_tva necunoscut -> D394 blocat (caen e obligatoriu),
                # iar TVA-ul ramane pe valoarea din template in loc de realitate.
                # Acelasi tipar ca [gratuit_tva_anaf_v1] la contul gratuit (DS: aceeasi
                # situatie = aceeasi rezolvare), extins la toate campurile pe care ANAF
                # le da: denumire, cod_caen, adresa, platitor_tva.
                try:
                    # [register_profil_anaf_v2] SURSA UNICA de precompletare ANAF
                    # (tenant_provisioning.precompleteaza_din_anaf), aceeasi ca la add-firm/import.
                    # seteaza_nume=True: firma proprie preia si denumirea de la ANAF.
                    # [P5 val 3] datele ANAF s-au luat INAINTE de bloc (`_d_anaf`); aici doar scrie.
                    if _t and _t.get("schema_name"):
                        tenant_provisioning.precompleteaza_din_anaf(conn, _t["schema_name"], _d_anaf, seteaza_nume=True)
                except Exception as _e:
                    # ANAF jos -> profilul ramane de completat manual. Firma EXISTA, doar
                    # datele preluate lipsesc - deci NU e esec de provisionare.
                    _obs.esec_secundar("precompletare ANAF la register", _e)
                conn.commit()
                _firma_ok = True
        except Exception as _e:
            # Contul RAMANE valid: userul se poate loga si adauga firma manual din ecranul
            # Firme. Dar raspunsul NU mai minte cu succes - vezi register_firma_v2 mai sus.
            # [register_motiv_real_v1] Raspunsul poarta MOTIVUL real, nu un generic. Modelul e mesajul
            # de la numerotarea facturilor ("nu putem presupune numarul 1") - spune DE CE. Contul + cabinetul
            # SUNT create si userul e logat automat -> mesajul il indruma spre ecranul Firme, nu "te poti loga".
            _obs.esec_secundar("provisionare tenant la register", _e, alerta=True)
            _txt = str(_e).lower()
            _cui_afis = (cui or "").strip()
            if "cifra de control" in _txt or "cui invalid" in _txt:
                _motiv = ("CUI-ul introdus (%s) nu este valid \u2014 cifra de control nu corespunde. "
                          "Verific\u0103 cifrele (f\u0103r\u0103 spa\u021bii sau litere)." % _cui_afis)
            elif "exist" in _txt and "deja" in _txt:
                _motiv = "exist\u0103 deja o firm\u0103 cu acest CUI \u00een portofoliul cabinetului."
            else:
                _motiv = "a ap\u0103rut o eroare tehnic\u0103 la ad\u0103ugarea firmei."
            _firma_motiv = ("Contul \u0219i cabinetul au fost create. Firma proprie NU a putut fi ad\u0103ugat\u0103 "
                            "automat: %s O po\u021bi ad\u0103uga oric\u00e2nd din ecranul Firme." % _motiv)
    raspuns = {"user_id": r["user_id"], "firm_id": r["firm_id"]}
    if _firma_ok is not None:
        raspuns["firma_creata"] = _firma_ok
        if _firma_motiv:
            raspuns["avertisment"] = _firma_motiv
    return raspuns


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
    trimis = _obs.trimite_email_html_sau_semnaleaza("email invitatie cabinet", email, "Invitație iConta.eu", html)
    r = {"ok": True, "email": email, "link": link, "email_trimis": trimis, "valabila_zile": _inv.VALABILITATE_ZILE}
    if not trimis:
        r["motiv_netrimis"] = _obs.refuz_dezabonare(email)   # [268] adresa dezabonată: superadminul vede de ce, nu doar că n-a plecat
    return r


def invitatii_lista(ctx):
    """[superadmin] Invitațiile trimise (fără tokenuri)."""
    from core import invitatii as _inv
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            r = _inv.lista(cur)
        conn.rollback()
    return {"invitatii": r}


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
