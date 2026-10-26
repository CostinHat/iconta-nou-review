# -*- coding: utf-8 -*-
"""USE_CASE — Setări cont → Notificări: telefonul, confirmarea lui prin WhatsApp, acordul și canalul (lotul 7 pct.2.2).

Comanda Costin 17.10.2026 (verbatim în DECIZII „Lotul 6 închis”): „în Setări cont, fiecare utilizator își pune numărul și alege WhatsApp
sau email (implicit email). WhatsApp se activează numai după confirmarea numărului printr-un cod trimis pe WhatsApp și bifa de acord pentru
mesaje.”

Ordinea, impusă aici și în bază (CHECK `users_canal_notificari_check`): numărul -> bifa de acord (fără ea nu se trimite nimic pe WhatsApp,
nici codul) -> codul primit pe WhatsApp -> canalul WhatsApp. Schimbarea numărului șterge confirmarea și întoarce canalul pe email; retragerea
acordului la fel. Codul: 6 cifre, valabil `whatsapp.COD_MINUTE` minute, cel mult `INCERCARI` încercări, cel mult unul pe minut; se păstrează
numai hash-ul lui.
"""
import hashlib
import hmac
import secrets

from core import db
from core import erori as _erori
from core import repo_cont_notificari as _repo
from core import whatsapp as _wa

INCERCARI = 5
PAUZA_COD_SEC = 60
CANALE = ("email", "whatsapp")

COD_TELEFON_INVALID = "TELEFON_INVALID"
COD_TELEFON_LIPSA = "TELEFON_LIPSA"
COD_ACORD_LIPSA = "ACORD_WHATSAPP_LIPSA"
COD_NECONFIRMAT = "TELEFON_NECONFIRMAT"
COD_COD_GRESIT = "COD_TELEFON_GRESIT"
COD_COD_EXPIRAT = "COD_TELEFON_EXPIRAT"
COD_PREA_DES = "COD_TELEFON_PREA_DES"
COD_WA_INDISPONIBIL = "WHATSAPP_INDISPONIBIL"
COD_CANAL_INVALID = "CANAL_INVALID"

MESAJ_TELEFON_INVALID = ("Numărul nu e un număr de telefon: scrie-l cu prefixul țării (+40 7xx xxx xxx) sau ca număr românesc "
                         "(07xx xxx xxx).")
MESAJ_ACORD_LIPSA = "Bifează acordul pentru mesaje pe WhatsApp: fără el nu se trimite nimic pe WhatsApp, nici codul."
MESAJ_TELEFON_LIPSA = "Scrie întâi numărul de telefon și salvează-l."
MESAJ_PREA_DES = "Un cod a plecat acum mai puțin de un minut. Așteaptă-l pe WhatsApp sau cere altul peste un minut."
MESAJ_WA_INACTIV = ("Trimiterea pe WhatsApp nu e încă activă pe iConta.eu. Acordul tău a fost salvat; notificările rămân pe email până se "
                    "activează.")
#: [deficiența 598, lotul 12: „La eșecul WhatsApp, mesajul îi cere contabilului să-și verifice numărul și arată termeni tehnici; trebuie
#: spus că WhatsApp nu e disponibil și notificările vin pe email.”] Meta a refuzat sau n-a primit cererea: nu se știe că ar fi de vină
#: numărul (pe 22.10 era contul iConta.eu, neînregistrat la Meta), deci nu i se cere omului să-l verifice; i se spune ce face aplicația
MESAJ_WA_ESUAT = ("WhatsApp nu e disponibil acum, deci codul de confirmare nu a plecat. Notificările îți vin în continuare pe email; "
                  "poți cere codul din nou mai târziu.")
#: [deficiența 335 + 336, 18.10.2026] motivul, spus pe ecran înainte de orice clic (codul pe WhatsApp nu se mai oferă cât WhatsApp nu
#: trimite) și în mesajul de după salvare („vin pe email” fără motiv)
MOTIV_WA_INACTIV = "Trimiterea pe WhatsApp nu e încă activă pe iConta.eu, deci notificările vin pe email până se activează."
#: [deficiența 338, 18.10.2026] același număr la alt cont: avertisment, fără să se spună al cui e contul (alt cabinet, poate)
AVERTISMENT_TELEFON_DUBLU = ("Același număr e salvat și la alt cont din iConta.eu. Codul de confirmare și mesajele pe WhatsApp pleacă la "
                             "numărul ăsta pentru fiecare cont care îl are: verifică dacă e numărul tău.")
MESAJ_COD_EXPIRAT = "Codul a expirat sau a fost încercat de prea multe ori. Cere un cod nou."
MESAJ_COD_GRESIT = "Codul nu se potrivește. Scrie cele 6 cifre primite pe WhatsApp."
MESAJ_NECONFIRMAT = "Confirmă întâi numărul cu codul primit pe WhatsApp."
MESAJ_CANAL_INVALID = "Alege email sau WhatsApp."


def _refuz_camp(clasa, cod, camp, mesaj):
    return clasa({"mesaj": mesaj, "cod": cod, "erori_campuri": [{"camp": camp, "mesaj": mesaj}]})


def _hash(uid, cod):
    return hashlib.sha256(("%s:%s" % (uid, cod)).encode()).hexdigest()


#: [320] emailurile contului nu sunt în listă și pleacă mereu (textul de sub bife)
NOTA_EMAILURI_CONT = ("Emailurile contului — confirmarea, resetarea parolei, linkul de logare — nu sunt în listă: pleacă mereu, pe email. "
                      "Bifele decid numai ce pleacă pe WhatsApp sau pe email; clopoțelul din aplicație arată tot.")


def _actor(r):
    return {"rol": r[2], "poate_pregati": r[3], "poate_valida": r[4]}


def _stare(cur, uid):
    from core import notificari as _n
    r = _repo.stare(cur, uid)
    p = _repo.preferintele(cur, uid)
    st = {"telefon": r[0], "confirmat": r[1], "canal": r[2], "acord": r[3], "whatsapp_disponibil": _wa.configurat(),
          "numar_iconta": _wa.NUMAR_AFISAT}
    st["whatsapp_motiv"] = None if st["whatsapp_disponibil"] else MOTIV_WA_INACTIV   # [335]
    # [338] numărul salvat și la alt cont: avertismentul se vede la fiecare deschidere, nu numai la salvare
    st["avertisment_telefon"] = AVERTISMENT_TELEFON_DUBLU if _repo.alte_conturi_cu_telefonul(cur, uid, r[0]) else None
    # [deficiența 320] toate tipurile care îl privesc, grupate, cu bifele lui (sau implicitul grupei); prima intrare e completă când
    # telefonul e scris și bifele (cu canalul) au fost salvate o dată — sau contul exista la publicarea lotului 7 („Numai conturile
    # noi”, decizia Costin 17.10.2026, `prima_intrare_scutita_la` din `core/migrare_canal_notificari.py`)
    st["grupuri"] = _n.lista_pentru(_actor(p), p[0])
    st["salvate"] = bool(p[1])
    st["complet"] = bool(p[5]) or (bool(r[0]) and bool(p[1]))
    st["nota_emailuri_cont"] = NOTA_EMAILURI_CONT
    st["nota_sinteza"] = _nota_sinteza(cur, uid, st["grupuri"])
    return st


#: [lotul 13, deficiența 565] sinteza zilnică e email INFORMATIV (core/dezabonare.py): adresa dezabonată din linkul emailului n-o mai
#: primește, oricare ar fi bifa — se spune lângă bifă, ca bifa să nu promită un email care nu pleacă
NOTA_SINTEZA_DEZABONAT = ("Adresa contului tău s-a dezabonat de la emailurile informative (din linkul „Dezabonează-te” al unui email), "
                          "deci sinteza zilei nu pleacă, chiar dacă e bifată. Scrie-ne din Suport dacă vrei s-o primești din nou.")


def _nota_sinteza(cur, uid, grupuri):
    if not any(t["cheie"] == "sinteza_zilnica" for g in grupuri for t in g["tipuri"]):
        return None
    from core import dezabonare as _dez
    email = _repo.emailul(cur, uid)
    return NOTA_SINTEZA_DEZABONAT if email and _dez.e_dezabonata(cur, email) else None


def stare(ctx):
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            return _stare(cur, ctx["uid"])


def telefon_seteaza(date, ctx):
    """Numărul nou (gol = fără telefon). Altul decât cel salvat -> confirmarea se șterge, canalul revine pe email."""
    brut = (date.telefon or "").strip()
    tel = _wa.normalizeaza(brut) if brut else None
    if brut and not tel:
        raise _refuz_camp(_erori.CerereGresita, COD_TELEFON_INVALID, "not-telefon", MESAJ_TELEFON_INVALID)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            _repo.seteaza_telefonul(cur, ctx["uid"], tel)
            st = _stare(cur, ctx["uid"])
    return st


def cere_cod(date, ctx):
    """Bifa de acord + codul pe WhatsApp. Fără bifă nu se trimite nimic (nici codul)."""
    if not date.acord:
        raise _refuz_camp(_erori.CerereGresita, COD_ACORD_LIPSA, "not-acord", MESAJ_ACORD_LIPSA)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            tel = _repo.telefonul(cur, ctx["uid"])
            if not tel:
                raise _refuz_camp(_erori.CerereGresita, COD_TELEFON_LIPSA, "not-telefon", MESAJ_TELEFON_LIPSA)
            if _repo.cod_cerut_de_curand(cur, ctx["uid"], PAUZA_COD_SEC):
                raise _erori.Conflict({"mesaj": MESAJ_PREA_DES, "cod": COD_PREA_DES})
            _repo.scrie_acordul(cur, ctx["uid"])
    if not _wa.configurat():
        raise _erori.Conflict({"mesaj": MESAJ_WA_INACTIV, "cod": COD_WA_INDISPONIBIL})
    cod = "%06d" % secrets.randbelow(10 ** 6)
    with db.get_conn() as conn:          # codul se scrie ÎNAINTE de trimitere: un cod trimis și nescris n-ar mai putea fi confirmat
        with conn.cursor() as cur:
            _repo.scrie_codul(cur, ctx["uid"], tel, _hash(ctx["uid"], cod), _wa.COD_MINUTE)
    try:
        _wa.trimite_cod(tel, cod)
    except (_wa.Neconfigurat, _wa.Refuzat, OSError) as e:
        # [598] răspunsul Meta (HTTP, cod, „Account not registered”) e pentru echipa iConta.eu: în jurnal și în alertă, nu pe ecran
        from core import observare as _obs
        _obs.esec_secundar("whatsapp: codul de confirmare", e, alerta=True)
        raise _erori.Conflict({"mesaj": MESAJ_WA_ESUAT, "cod": COD_WA_INDISPONIBIL})
    return {"ok": True, "minute": _wa.COD_MINUTE}


def confirma_cod(date, ctx):
    cod = (date.cod or "").strip()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            r = _repo.codul_in_curs(cur, ctx["uid"])
            expirat = not r or not r[1] or not r[3] or r[2] >= INCERCARI
            if expirat:
                _repo.sterge_codul(cur, ctx["uid"])
            elif not hmac.compare_digest(r[0], _hash(ctx["uid"], cod)):
                _repo.numara_incercarea(cur, ctx["uid"])
            else:
                _repo.confirma_telefonul(cur, ctx["uid"])
                _repo.sterge_codul(cur, ctx["uid"])
                return _stare(cur, ctx["uid"])
    # refuzul se ridică DUPĂ commit: încercarea numărată (sau codul șters) rămâne scrisă
    if expirat:
        raise _refuz_camp(_erori.CerereGresita, COD_COD_EXPIRAT, "not-cod", MESAJ_COD_EXPIRAT)
    raise _refuz_camp(_erori.CerereGresita, COD_COD_GRESIT, "not-cod", MESAJ_COD_GRESIT)


COD_TELEFON_OBLIGATORIU = "TELEFON_OBLIGATORIU"
MESAJ_TELEFON_OBLIGATORIU = ("Scrie numărul tău de telefon și salvează-l: e obligatoriu, chiar dacă notificările vin pe email "
                             "(prin el te anunțăm pe WhatsApp, dacă alegi canalul).")


def canal_seteaza(date, ctx):
    """Canalul ('email' | 'whatsapp'), acordul și [320] bifele pe tipuri (`date.tipuri`: {tip: bool}, numai tipurile care îl privesc pe om).
    Acordul retras: canalul e email. WhatsApp cere numărul confirmat și acordul. Salvarea bifelor cere telefonul (prima intrare)."""
    import json
    from core import notificari as _n
    if date.canal not in CANALE:
        raise _refuz_camp(_erori.CerereGresita, COD_CANAL_INVALID, "not-canal", MESAJ_CANAL_INVALID)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            st = _stare(cur, ctx["uid"])
            tipuri = getattr(date, "tipuri", None)
            if tipuri is not None:
                if not st["telefon"]:
                    raise _refuz_camp(_erori.CerereGresita, COD_TELEFON_OBLIGATORIU, "not-telefon", MESAJ_TELEFON_OBLIGATORIU)
                vazute = {t["cheie"] for g in st["grupuri"] for t in g["tipuri"]}
                _repo.scrie_preferintele(cur, ctx["uid"], json.dumps({k: bool(v) for k, v in tipuri.items() if k in vazute and k in _n.TIPURI},
                                                                     sort_keys=True))
            if date.acord is False:
                _repo.retrage_acordul(cur, ctx["uid"])
            elif date.canal == "whatsapp":
                if not (st["telefon"] and st["confirmat"]):
                    raise _erori.Conflict({"mesaj": MESAJ_NECONFIRMAT, "cod": COD_NECONFIRMAT})
                if not (st["acord"] or date.acord):
                    raise _refuz_camp(_erori.CerereGresita, COD_ACORD_LIPSA, "not-acord", MESAJ_ACORD_LIPSA)
                _repo.alege_whatsapp(cur, ctx["uid"])
            else:
                _repo.alege_emailul(cur, ctx["uid"])
            return _stare(cur, ctx["uid"])
