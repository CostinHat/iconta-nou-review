# -*- coding: utf-8 -*-
"""USE_CASE — cardurile de început (deficiențele 319 + 320, comanda Costin 17.10.2026 7.2, verbatim în DECIZII „Comanda 7.2”).

320: „Fiecare actor are cardurile lui: administratorul cabinetului cei trei pași de la 319; asistentul Setări cont (telefon, canal,
notificări) și un card cu firmele alocate și ce are voie să facă; clientul din portal telefonul, canalul și ce vrea să primească (pachetul
lunar, cererile de documente). Cardul duce în ecranul real și se bifează singur doar când acțiunea a fost făcută acolo, nu la apăsarea
cardului. Cardurile nu se pot închide cât timp nu sunt făcute, dar nu blochează lucrul; când toate sunt făcute dispar de tot, iar ghidul de
început rămâne în butonul de ajutor (?).”

319: textul cardurilor administratorului, aprobat de Costin, pus întocmai; „numele ecranelor, butoanelor și verificările auditului de
preluare le aliniezi cu cele reale”. Ce s-a aliniat (față de textul din DECIZII), și de ce:
- pasul 1.6: auditul de preluare (`core/audit_preluare.py`) verifică pachetul ADUS (balanța, soldurile partenerilor, soldurile fiscale față
  de istoricul declarațiilor importat), nu „situația firmei la ANAF”, și nu citește datoriile de la ANAF; butonul e „Rulează auditul de
  preluare”, în Control fiscal, pe firmă;
- pasul 2.2: butonul se numește „Conectează SPV”;
- pasul 3.5: butonul formularului se numește „Trimite invitația” (drepturile și firmele se bifează acum din invitație — `uc_asistenti`).
Fiecare card spune când devine verde, iar semnalul e citit din bază (`repo_inceput`), nu dintr-un clic.
"""
from core import db
from core import repo_inceput as _repo

#: ce butoane deschid ce ecrane (ecranul îl deschide interfața, `static/js/ecrane/inceput.js`)
DESCHIDERI = ("migrare", "suport_import", "setari_spv", "setari_notificari", "asistenti", "lucrez_singur", "firme", "notificari_portal")

CARDURI_ADMIN = (
    {"cheie": "preluare", "titlu": "Pasul 1 · Adu firmele din aplicația veche",
     "ce_faci": "Ce faci aici: muți în iConta firmele pe care le ții acum în altă aplicație de contabilitate, ca să nu le introduci de mână.",
     "pasi": (
         "Deschide aplicația pe care o folosești acum (de exemplu SAGA) și alege prima firmă.",
         "Exportă din ea, pe rând, patru fișiere: balanța de verificare la sfârșitul ultimei luni închise, lista partenerilor cu soldurile "
         "lor, lista salariaților și lista mijloacelor fixe. Salvează-le într-un dosar cu numele firmei, ca să nu le amesteci.",
         "În iConta apasă butonul de mai jos, Deschide Migrare cabinet. Alege aplicația ta din butoanele de sus și urmează pașii din ecran: "
         "încarci fișierele unul câte unul, iar iConta îți arată ce a citit înainte să salveze.",
         "Verifică pe ecran că soldurile din balanță sunt cele din aplicația veche. Dacă ceva nu se potrivește, nu salva; scrie-ne din Suport.",
         "Repetă pentru fiecare firmă.",
         "Pentru fiecare firmă importată, rulează auditul de preluare: în Control fiscal, pe firmă, butonul Rulează auditul de preluare. "
         "Aplicația verifică dacă ce ai adus se leagă și îți arată, într-o listă, ce a găsit: o balanță neechilibrată, solduri ale "
         "partenerilor care nu se leagă de conturile lor, sume de plată sau de recuperat pe conturile de impozite fără declarația lor în "
         "istoricul importat. Citește lista înainte să începi lucrul pe firmă: ce apare acolo s-a întâmplat înainte de tine, și e bine "
         "să-l discuți cu clientul de la început."),
     "nota": ("Dacă aplicația ta nu are buton activ în Migrare cabinet, încă nu o putem citi automat. Atunci deschide Suport, fila Cerere "
              "import din altă aplicație, scrie numele aplicației și atașează o captură a meniului ei de export și exportul unei singure "
              "firme. Îți răspundem acolo dacă și când o putem prelua."),
     "verde": "Cardul devine verde când cel puțin o firmă are balanța importată și auditul de preluare făcut.",
     "butoane": ({"eticheta": "Deschide Migrare cabinet", "deschide": "migrare"},
                 {"eticheta": "Deschide Suport", "deschide": "suport_import"})},
    {"cheie": "anaf", "titlu": "Pasul 2 · Leagă contul de ANAF și alege cum afli noutățile",
     "ce_faci": ("Ce faci aici: pui iConta în legătură cu Spațiul Privat Virtual (SPV), ca facturile firmelor tale să plece și să vină "
                 "singure, și alegi pe unde te anunțăm când ai ceva de făcut."),
     "pasi": (
         "Apasă Deschide Setări cont, apoi Conectare SPV.",
         "Conectează certificatul digital cu care intri acum în SPV pentru firmele tale, cu butonul Conectează SPV. Conectarea se face o "
         "singură dată, pentru tot cabinetul.",
         "Dacă ai înrolat certificatul în SPV în ultimele 24 de ore, așteaptă o zi înainte de conectare; altfel ANAF răspunde cu eroare, "
         "chiar dacă totul e corect.",
         "După conectare, iConta îți arată lista firmelor și, la fiecare, dacă certificatul tău are drept în SPV pentru ea. La firmele fără "
         "drept scrie exact ce ai de făcut.",
         "Tot în Setări cont deschide Notificări. Alege pe unde vrei să fii anunțat (email, WhatsApp) și pentru ce: termene de declarații, "
         "facturi primite, note de validat, mesaje de la clienți. Apasă Salvează."),
     "nota": None,
     "verde": "Cardul devine verde când certificatul e conectat și notificările sunt salvate.",
     "butoane": ({"eticheta": "Deschide Setări cont · Conectare SPV", "deschide": "setari_spv"},
                 {"eticheta": "Deschide Notificări", "deschide": "setari_notificari"})},
    {"cheie": "echipa", "titlu": "Pasul 3 · Adaugă echipa",
     "ce_faci": ("Ce faci aici: dai acces colegilor care lucrează cu tine și hotărăști ce are voie să facă fiecare. Dacă lucrezi singur, "
                 "sari peste acest pas cu butonul Lucrez singur."),
     "pasi": (
         "Apasă Deschide Asistenți, apoi Adaugă asistent.",
         "Scrie numele și emailul colegului. El primește pe email linkul cu care își face parola.",
         "Bifează ce poate face. Poate pregăti: introduce facturi, note, state de plată și pregătește declarații, dar tot ce face ajunge la "
         "tine spre validare. Poate valida: aprobă munca altor colegi, niciodată pe a lui. Poate depune: trimite declarațiile la ANAF.",
         "Bifează firmele pe care le lucrează. Colegul vede numai firmele bifate.",
         "Apasă Trimite invitația. Poți schimba oricând drepturile și firmele din același ecran."),
     "nota": None,
     "verde": "Cardul devine verde când ai adăugat un asistent sau ai ales Lucrez singur.",
     "butoane": ({"eticheta": "Deschide Asistenți", "deschide": "asistenti"},
                 {"eticheta": "Lucrez singur", "deschide": "lucrez_singur"})},
)

CARD_NOTIFICARI = {
    "cheie": "notificari", "titlu": "Setări cont · telefonul, canalul și notificările",
    "ce_faci": "Ce faci aici: îți pui numărul de telefon și alegi pe unde te anunțăm (email sau WhatsApp) și pentru ce.",
    "pasi": ("Apasă Deschide Notificări.", "Scrie numărul de telefon și apasă Salvează numărul.",
             "Alege canalul și bifează ce vrei să primești; apasă Salvează."),
    "nota": None, "verde": "Cardul devine verde când numărul e scris și notificările sunt salvate.",
    "butoane": ({"eticheta": "Deschide Notificări", "deschide": "setari_notificari"},)}

DREPTURI_NUME = (("poate_pregati", "Poate pregăti: introduci facturi, note, state de plată și pregătești declarații; ce faci ajunge la "
                                   "validare."),
                 ("poate_valida", "Poate valida: aprobi munca altor colegi, niciodată pe a ta."),
                 ("poate_depune", "Poate depune: trimiți declarațiile la ANAF."))

CARD_CLIENT = {
    "cheie": "client", "titlu": "Cum afli noutățile de la cabinet",
    "ce_faci": ("Ce faci aici: îți pui numărul de telefon, alegi pe unde te anunțăm (email sau WhatsApp) și ce vrei să primești: raportul "
                "lunar al firmei, mesajele cabinetului (de exemplu cererile de documente)."),
    "pasi": ("Apasă Deschide Notificări.", "Scrie numărul de telefon și apasă Salvează numărul.",
             "Alege canalul și bifează ce vrei să primești; apasă Salvează."),
    "nota": None, "verde": "Cardul devine verde când numărul e scris și notificările sunt salvate.",
    "butoane": ({"eticheta": "Deschide Notificări", "deschide": "notificari_portal"},)}


def _card(c, facut, **extra):
    return dict(c, pasi=list(c["pasi"]), butoane=list(c["butoane"]), facut=bool(facut), **extra)


def carduri(ctx):
    """{carduri: [...], toate_facute} — cardurile actorului, fiecare cu `facut` citit din bază."""
    uid = int(ctx["uid"])
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            rol, cabinet, telefon, salvate, firme_vazute, pp, pv, pd = _repo.omul(cur, uid)
            notif = bool(telefon) and salvate
            if rol == "admin_firma" and cabinet:
                preluat = False
                for _tid, schema in _repo.firmele_cabinetului(cur, cabinet):
                    sold, audit = _repo.preluare_facuta(cur, schema)
                    if sold and audit:
                        preluat = True
                        break
                cu_asistent, singur = _repo.echipa(cur, cabinet)
                out = [_card(CARDURI_ADMIN[0], preluat), _card(CARDURI_ADMIN[1], _repo.spv_conectat(cur, cabinet) and notif),
                       _card(CARDURI_ADMIN[2], cu_asistent or singur)]
            elif rol == "angajat":
                firme = [n for _i, n in _repo.firmele_asistentului(cur, uid)]
                drepturi = [t for k, t in DREPTURI_NUME if {"poate_pregati": pp, "poate_valida": pv, "poate_depune": pd}[k]]
                card_firme = {"cheie": "firme", "titlu": "Firmele tale și ce ai voie să faci",
                              "ce_faci": "Ce faci aici: vezi firmele pe care le lucrezi și ce îți permite administratorul cabinetului.",
                              "pasi": [("Firmele tale: " + ", ".join(firme) + ".") if firme else
                                       "Încă nu ai nicio firmă alocată: ți-o alocă administratorul cabinetului, din ecranul Asistenți."]
                                      + (drepturi or ["Încă n-ai niciun drept bifat: ți-l dă administratorul cabinetului, din ecranul "
                                                      "Asistenți."])
                                      + ["Apasă Deschide Firme și deschide o firmă: lucrezi numai pe firmele de mai sus."],
                              "nota": None, "verde": "Cardul devine verde după ce deschizi una dintre firmele tale.",
                              "butoane": ({"eticheta": "Deschide Firme", "deschide": "firme"},)}
                out = [_card(CARD_NOTIFICARI, notif), _card(card_firme, firme_vazute)]
            elif rol == "client":
                out = [_card(CARD_CLIENT, notif)]
            else:
                out = []
        conn.rollback()
    return {"carduri": out, "toate_facute": all(c["facut"] for c in out)}


def lucrez_singur(ctx):
    """„Lucrez singur” (cardul „Adaugă echipa”): numai administratorul cabinetului; o alegere în ecranul cardului, păstrată pe cabinet."""
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            _repo.lucrez_singur(cur, int(ctx["firm"]))
        conn.commit()
    return carduri(ctx)


def firme_vazute(ctx):
    """Asistentul a deschis o firmă din lista firmelor lui (ecranul Firme): cardul „Firmele tale” e făcut."""
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            _repo.firme_vazute(cur, int(ctx["uid"]))
        conn.commit()
    return {"ok": True}
