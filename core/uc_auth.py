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


def register(date):
    """[P7 · use-case] Corpul rutei `/auth/register`; docstringul ei a ramas in stratul HTTP."""
    if not date.accept_termeni:  # [termeni_v1] fara bifa -> contul NU se creeaza (gard pe backend, nu doar JS)
        raise _erori.CerereGresita("Trebuie să accepți Termenii și condițiile pentru a crea contul.")
    if not _nucleu.parola_ok(date.parola):  # [parola_min_v1] aceeasi cerinta ca activare/reset/schimbare
        raise _erori.CerereGresita(_nucleu.PAROLA_MESAJ)
    if not _uc_comun._email_valid(date.email):  # [email_valid_v1] email obligatoriu + format valid
        raise _erori.CerereGresita(EMAIL_INVALID)
    # [P4, 09.09.2026] Versiunea termenilor se citește ÎNAINTE de tranzacție. Un fișier care
    # lipsește trebuie să oprească înregistrarea înainte de orice scriere — nu să lase în urmă un
    # cont fără dovada acordului.
    try:
        _versiune_termeni = _uc_comun._termeni_versiune(open(_uc_comun._TERMENI_PATH, encoding="utf-8").read())
    except OSError as _e:
        raise _erori.ServiciuIndisponibil("Termenii și condițiile nu se pot citi acum, deci acordul tău "
                                 "nu s-ar putea consemna. Contul NU a fost creat. Încearcă din "
                                 "nou peste câteva minute.")
    # [P4] CONTUL ȘI DOVADA ACORDULUI, ÎN ACEEAȘI TRANZACȚIE.
    #
    # Ce era până azi: contul se crea într-o tranzacție, iar `acord_termeni` — dovada
    # consimțământului, cu versiunea textului — într-a doua, ambalată într-un `try` care doar
    # TIPĂREA la eșec. Ruta refuză din prima linie o înregistrare fără bifă; dar dovada bifei
    # putea lipsi în tăcere, iar contul rămânea. *Fără bifă contul nu se creează — deci nici
    # fără dovada ei.*
    with db.get_conn() as conn:
        r = auth_api.inregistreaza_cabinet(
            conn, date.email, date.parola, date.nume_cabinet,
            nume=date.nume, prenume=date.prenume)
        if r["ok"]:  # [termeni_v1] dovada de consimtamant: cine, cand, ce versiune
            with conn.cursor() as cur:
                repo_utilizatori.scrie_acordul_termenilor(cur, r.get("user_id"), r.get("firm_id"), date.email.strip().lower(), _versiune_termeni)
    if not r["ok"]:
        raise _erori.CerereGresita(r["mesaj"])
    try:  # register_email_v1: email de bun venit
        html = ("<p>Buna,</p><p>Contul cabinetului <b>%s</b> a fost creat pe iConta.eu.</p>"
                "<p>Te poti loga oricand cu emailul <b>%s</b> la <a href='https://iconta.eu'>iconta.eu</a>.</p>"
                "<p>Firma proprie a cabinetului este deja adaugata in portofoliu.</p>") % (date.nume_cabinet, date.email)
        _obs.trimite_email_html(date.email, "Bine ai venit pe iConta.eu", html)
    except Exception as _e:
        # [R73] fara alerta: bun venit nu e cale de ACCES, doar politete
        _obs.esec_secundar("email bun venit cabinet", _e)
    try:  # [alerta_cont_nou_v1] notificare interna la fiecare cont nou de cabinet (fara date personale)
        from datetime import datetime as _dt
        from zoneinfo import ZoneInfo as _Z
        _acum = _dt.now(_Z("Europe/Bucharest")).strftime("%Y-%m-%d %H:%M:%S")
        _mesaj_cn = ("S-a inregistrat un cont nou de cabinet pe iConta.eu la %s (ora Romaniei). "
                     "Alerta nu contine date personale." % _acum)
        if _obs.trebuie_trimisa("cont_nou_cabinet"):  # [alerta_dedup_v1] throttle anti-flood (implicit 15 min)
            _ok_cn = _obs._trimite_brevo("Cont nou de cabinet", _mesaj_cn)
            print("[alerta_cont_nou] trimisa=%s | %s" % (_ok_cn, _mesaj_cn), flush=True)
        else:
            print("[alerta_cont_nou] throttled (dedup) | %s" % _mesaj_cn, flush=True)
    except Exception as _e:
        print("[alerta_cont_nou] netrimisa: %s" % _e, flush=True)
    # [register_firma_v2 27.07.2026] Provisionarea primei firme poate esua (ANAF jos, schema
    # incompleta, DB). Inainte, esecul era INGHITIT si raspunsul spunea SUCCES - userul ramanea
    # cu cont valid si FARA firma, fara sa stie. Contul NU se anuleaza (e valid si util), dar
    # raspunsul poarta adevarul, iar ecranul il arata.
    _firma_ok = None                       # None = nu s-a incercat (fara CUI la inregistrare)
    _firma_motiv = ""
    if date.cui and _uc_comun._TENANT_TEMPLATE:  # register_primul_tenant_v1: entitatea proprie = prima firma
        _firma_ok = False
        # [P5 val 3, 11.09.2026] ANAF ÎNAINTE de conexiune: apelul are termen 20 s, iar forma
        # dinainte îl făcea cu tranzacția de creare a cabinetului deschisă. Eșecul se înghite și
        # se consemnează, exact ca înainte — firma rămâne creată, profilul completabil manual.
        try:
            _d_anaf = tenant_provisioning.date_din_anaf(date.cui)
        except Exception as _e:
            _obs.esec_secundar("precompletare ANAF la register", _e)
            _d_anaf = None
        try:
            with db.get_conn() as conn:
                _cui = date.cui.replace("RO", "").strip()
                _t = tenant_provisioning.provision_tenant(
                    conn, date.nume_cabinet, _cui,
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
            _cui_afis = (date.cui or "").strip()
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

