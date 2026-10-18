# -*- coding: utf-8 -*-
"""core/notificari.py — LIVRAREA notificărilor din aplicație (clopoțelul, `public.notificari`) pe canalul ales de fiecare utilizator:
WhatsApp (numărul confirmat + acordul) sau email (implicit).

Comanda Costin 17.10.2026, lotul 7 pct.2.1–2.3 (verbatim în DECIZII „Lotul 6 închis”):
- „Notificări WhatsApp [...]: mesaj scurt, fără conținut fiscal, cu link în aplicație. Emailul rămâne pentru confirmarea contului, resetarea
  parolei, linkul de logare și ca rezervă când WhatsApp nu livrează.” -> confirmarea, resetarea și linkul de logare NU trec pe aici (rămân
  emailuri tranzacționale în `uc_auth` / `uc_public`). Pe aici trec notificările clopoțelului: textul lor (cu firma, perioada, motivul)
  rămâne în aplicație; afară pleacă numai ETICHETA tipului (`TIPURI`: ce s-a întâmplat, fără cifre, fără conținut fiscal) și linkul.
- „în Setări cont, fiecare utilizator își pune numărul și alege WhatsApp sau email (implicit email). WhatsApp se activează numai după
  confirmarea numărului printr-un cod trimis pe WhatsApp și bifa de acord pentru mesaje.” -> `pe_whatsapp`, plus CHECK-ul din bază.
- „Notificare pentru mine (superadmin) la fiecare cerere de import și sesizare din Suport” și (2.6) „alertele importante vin la mine pe
  canalul de notificare” -> notificări de clopoțel pentru superadmini (`pentru_superadmini`), livrate la fel.

**De ce o „cutie de ieșire”, nu trimiterea pe loc.** `notificari_api.adauga` scrie rândul în tranzacția apelantului, cu `de_livrat = true`;
livrarea îl ia abia după ce tranzacția s-a comis (`livreaza_in_asteptare`, bucla din `main.lifespan`, la `INTERVAL_SEC`). O trimitere pe
loc ar fi plecat și pentru o tranzacție anulată după ea („nota a fost validată” pentru o validare întoarsă), și ar fi ținut conexiunea
peste apelul HTTP. Revendicarea e `FOR UPDATE SKIP LOCKED`, comisă ÎNAINTE de trimitere: cu două procese, un rând pleacă o singură dată
(cel mult o dată — ca la `notificari_scadenta`: o notificare pierdută se vede în jurnal, una dublă n-o mai iei înapoi).
Rândurile de dinainte de migrare au `de_livrat = false` (valoarea implicită a coloanei), deci nu pleacă retroactiv.
"""
import os

from core import db
from core import observare as _obs
from core import repo_notificari_livrare as _repo
from core import repo_utilizatori as _ru
from core import whatsapp as _wa
from core.common import esc as _esc

INTERVAL_SEC = 30
LOT = 20

#: [17.10.2026] locurile din aplicație spre care trimite o notificare: `GET /deschide/<cheie>` -> `/#deschide=<cheie>`, iar aplicația, după
#: autentificare, apasă elementul cu `data-deschide="<cheie>"` (`static/js/app.js`). O rută cu o cale, nu un `#` în butonul WhatsApp: partea
#: variabilă a URL-ului din șablon e un sufix de cale. Mulțime ÎNCHISĂ (o cheie necunoscută duce la pagina principală).
DESCHIDERI = ("notificari", "raportari", "anunturi", "raport")

#: [deficiența 320, comanda Costin 17.10.2026 7.2, verbatim în DECIZII] „În Setări cont → Notificări apar toate tipurile de notificări ale
#: aplicației, grupate (Termene și declarații, Facturi și SPV, Validări, Clienți, Cont și echipă), fiecare cu un rând care spune ce face
#: aplicația acolo; utilizatorul bifează ce îl interesează. Fiecare vede doar tipurile care îl privesc după drepturi; termenele și validările
#: vin bifate din oficiu; emailurile de cont (confirmare, resetare parolă, link de logare) nu sunt în listă și pleacă mereu; bifele decid
#: doar WhatsApp/email, clopoțelul din aplicație arată tot.”
GRUPURI = ("Termene și declarații", "Facturi și SPV", "Validări", "Clienți", "Cont și echipă")
#: grupele bifate din oficiu (cât omul n-a salvat altceva)
GRUPURI_IMPLICITE = ("Termene și declarații", "Validări")
#: cine vede tipul în Notificări (și cui i se trimite): `pregatire` / `validare` = bifa din Asistenți („Poate pregăti” / „Poate valida”;
#: administratorul cabinetului le are pe toate), `admin` = administratorul cabinetului, `cabinet` = orice om al cabinetului, `client` =
#: clientul din portal, `superadmin` = platforma
CINE = ("pregatire", "validare", "admin", "cabinet", "client", "superadmin")

#: tipurile clopoțelului -> eticheta trimisă în afara aplicației (fără cifre, fără conținut fiscal), locul din aplicație, grupa, rândul
#: din Notificări („ce face aplicația aici”) și cine îl vede. Mulțime ÎNCHISĂ: un tip nou scris în `notificari_api.adauga` fără intrare aici
#: e prins de `core/test_notificari_canal.py` (scanare AST a apelurilor).
TIPURI = {
    "termen_declaratie": {"eticheta": "o declarație cu termenul aproape, nedepusă", "deschide": "notificari", "grup": "Termene și declarații",
                          "rand": "Cu trei zile înainte de termenul unei declarații încă nedepuse, pe firmele tale.", "cine": "pregatire"},
    "declaratie_reluata": {"eticheta": "o declarație a revenit în coadă", "deschide": "notificari", "grup": "Termene și declarații",
                           "rand": "Când o declarație care aștepta validarea notelor s-a generat din nou și a intrat în coadă.",
                           "cine": "pregatire"},
    "depusa": {"eticheta": "o declarație pregătită de tine a fost depusă", "deschide": "notificari", "grup": "Termene și declarații",
               "rand": "Când un coleg a depus la ANAF o declarație pregătită de tine.", "cine": "pregatire"},
    "control_fiscal": {"eticheta": "o alertă nouă de control fiscal", "deschide": "notificari", "grup": "Termene și declarații",
                       "rand": "Când Control fiscal găsește o constatare roșie nouă: o restanță sau o diferență față de evidență.",
                       "cine": "validare"},
    "alerta_legislativa": {"eticheta": "o alertă legislativă importantă", "deschide": "anunturi", "grup": "Termene și declarații",
                           "rand": "Când apare în Monitorul Oficial sau pe Portalul Legislativ un act care schimbă o regulă din aplicație.",
                           "cine": "superadmin"},
    "factura_primita": {"eticheta": "facturi noi primite din SPV", "deschide": "notificari", "grup": "Facturi și SPV",
                        "rand": "Când citirea automată din SPV aduce facturi noi de la furnizorii firmelor tale.", "cine": "pregatire"},
    "de_validat": {"eticheta": "un element nou de validat", "deschide": "notificari", "grup": "Validări",
                   "rand": "Când un coleg trimite la validare o notă sau o declarație.", "cine": "validare"},
    "aprobata": {"eticheta": "un element pregătit de tine a fost validat", "deschide": "notificari", "grup": "Validări",
                 "rand": "Când o notă sau o declarație pregătită de tine a fost validată.", "cine": "pregatire"},
    "respinsa": {"eticheta": "un element pregătit de tine a fost respins", "deschide": "notificari", "grup": "Validări",
                 "rand": "Când o notă sau o declarație pregătită de tine a fost respinsă, cu motivul.", "cine": "pregatire"},
    "solicitare_client": {"eticheta": "o solicitare nouă de la un client", "deschide": "notificari", "grup": "Clienți",
                          "rand": "Când un client îți scrie din portal.", "cine": "cabinet"},
    "pachet_lunar": {"eticheta": "raportul lunar al firmei e gata", "deschide": "notificari", "grup": "Clienți",
                     "rand": "Când contabilul aprobă raportul lunar al firmei (Povestea lunii).", "cine": "client"},
    "mesaj_cabinet": {"eticheta": "un mesaj nou de la cabinet", "deschide": "notificari", "grup": "Clienți",
                      "rand": "Când cabinetul îți scrie în Solicitări — de exemplu, îți cere documente.", "cine": "client"},
    "asistent_activat": {"eticheta": "un coleg și-a activat contul", "deschide": "notificari", "grup": "Cont și echipă",
                         "rand": "Când un coleg invitat în Asistenți își activează contul.", "cine": "admin"},
    "sesizare": {"eticheta": "o sesizare nouă în Suport", "deschide": "raportari", "grup": "Cont și echipă",
                 "rand": "Când un cabinet trimite o sesizare din Suport.", "cine": "superadmin"},
    "cerere_import": {"eticheta": "o cerere nouă de import din altă aplicație", "deschide": "raportari", "grup": "Cont și echipă",
                      "rand": "Când un cabinet cere, din Suport, importul dintr-o aplicație pe care încă n-o citim.", "cine": "superadmin"},
}


def vede_tipul(tip, actor):
    """PURĂ. Tipul îl privește pe `actor` ({rol, poate_pregati, poate_valida})? Administratorul cabinetului are toate drepturile cabinetului."""
    cine, rol = TIPURI[tip]["cine"], (actor or {}).get("rol")
    if cine == "superadmin":
        return rol == "superadmin"
    if cine == "client":
        return rol == "client"
    if rol in ("client", "superadmin"):   # [340, 18.10.2026] superadminul (platforma) vede numai tipurile lui, nu pe ale cabinetelor
        return False
    if rol == "admin_firma":
        return True
    return {"pregatire": bool(actor.get("poate_pregati")), "validare": bool(actor.get("poate_valida")), "admin": False,
            "cabinet": True}[cine]


def implicit(tip):
    """Bifat din oficiu: grupele implicite și [340, 18.10.2026] tipurile superadminului — „Notificare pentru mine (superadmin) la fiecare
    cerere de import și sesizare din Suport” (comanda Costin 17.10.2026 pct.2.3, DECIZII „Lotul 6 închis de Costin”), deci pornite fără
    o bifă a lui."""
    return TIPURI[tip]["grup"] in GRUPURI_IMPLICITE or TIPURI[tip]["cine"] == "superadmin"


def dorit(tip, preferinte):
    """PURĂ. Tipul pleacă pe WhatsApp / email? Bifa salvată a omului; fără ea, implicitul grupei. Clopoțelul îl arată oricum."""
    if isinstance(preferinte, dict) and tip in preferinte:
        return bool(preferinte[tip])
    return implicit(tip)


def lista_pentru(actor, preferinte):
    """[{grup, tipuri: [{cheie, eticheta, rand, bifat}]}] — tipurile care îl privesc pe `actor`, în ordinea grupelor."""
    out = []
    for g in GRUPURI:
        t = [{"cheie": k, "eticheta": v["eticheta"], "rand": v["rand"], "bifat": dorit(k, preferinte)}
             for k, v in TIPURI.items() if v["grup"] == g and vede_tipul(k, actor)]
        if t:
            out.append({"grup": g, "tipuri": t})
    return out


def _baza():
    return os.environ.get("ICONTA_BAZA_URL", "https://iconta.eu").rstrip("/")


def link(tip):
    return "%s/deschide/%s" % (_baza(), TIPURI[tip]["deschide"])


def pe_whatsapp(d):
    """PURĂ. Notificarea pleacă pe WhatsApp numai dacă omul a ales canalul, are numărul confirmat și a dat acordul."""
    return bool(d and d["canal"] == "whatsapp" and d["telefon"] and d["confirmat"] and d["acord"])


def html_email(tip):
    return ("<div style='font-family:Arial,sans-serif;max-width:520px'>"
            "<p>Ai %s în iConta.eu.</p>"
            "<p><a href='%s' style='background:#3d8fd6;color:#fff;padding:9px 18px;border-radius:6px;text-decoration:none'>"
            "Deschide iConta.eu</a></p>"
            "<p style='color:#6b7280;font-size:12px'>Notificările tale vin pe email. Le poți primi pe WhatsApp din Setări cont → "
            "Notificări.</p></div>") % (_esc(TIPURI[tip]["eticheta"]), _esc(link(tip)))


def subiect_email(tip):
    return "iConta.eu — %s" % TIPURI[tip]["eticheta"]


def _jurnal(nid, user_id, tip, canal, stare, mesaj_id=None, rezerva=False, detaliu=None):
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            _repo.scrie_jurnalul(cur, nid, user_id, tip, canal, TIPURI[tip]["deschide"], mesaj_id, stare, rezerva,
                                 (detaliu or "")[:500] or None)
        conn.commit()


def _pe_email(nid, d, tip, rezerva=False, detaliu=None):
    ok = _obs.trimite_email_html_sau_semnaleaza("notificare %s" % tip, d["email"], subiect_email(tip), html_email(tip))
    _jurnal(nid, d["uid"], tip, "email", "trimis" if ok else "netrimis", rezerva=rezerva, detaliu=detaliu)
    return "email" if ok else "netrimis"


def livreaza(nid, d, tip):
    """O notificare, pe canalul omului. Întoarce canalul pe care a plecat: 'whatsapp' | 'email' | 'netrimis'."""
    if tip not in TIPURI:
        raise ValueError("tip de notificare fără etichetă de livrare: %r" % tip)
    if pe_whatsapp(d):
        try:
            mid = _wa.trimite_notificare(d["telefon"], TIPURI[tip]["eticheta"], TIPURI[tip]["deschide"])
        except (_wa.Neconfigurat, _wa.Refuzat, OSError) as e:
            # rezerva: WhatsApp n-a primit cererea -> emailul, acum, cu motivul în jurnal
            return _pe_email(nid, d, tip, rezerva=True, detaliu="WhatsApp: %s" % e)
        _jurnal(nid, d["uid"], tip, "whatsapp", "trimis", mesaj_id=mid)
        return "whatsapp"
    return _pe_email(nid, d, tip)


def _revendica(limita):
    """Rândurile de livrat, revendicate (`de_livrat = false`) și comise înaintea trimiterii; cu destinatarul lor."""
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            randuri = _repo.revendica(cur, limita)
            if not randuri:
                conn.rollback()
                return []
        conn.commit()
    return [(r[0], r[1], {"uid": r[2], "email": r[3], "canal": r[4], "telefon": r[5], "confirmat": r[6], "acord": r[7], "activ": r[8],
                          "preferinte": r[9]})
            for r in randuri]


#: [320] ce scrie jurnalul livrării pentru un tip debifat de om: nu pleacă pe canal, rămâne în clopoțel
DETALIU_NEBIFAT = "nebifat în Setări cont → Notificări: rămâne în clopoțel"


def livreaza_in_asteptare(limita=LOT):
    """Un pas al buclei: livrează ce a rămas în cutia de ieșire. Întoarce {canal: câte}."""
    rez = {}
    for nid, tip, d in _revendica(limita):
        if not d["activ"] or tip not in TIPURI:
            canal = "netrimis"
            _jurnal(nid, d["uid"], tip if tip in TIPURI else "de_validat", "email", "netrimis",
                    detaliu="cont inactiv" if not d["activ"] else "tip fără etichetă de livrare: %s" % tip)
        elif not dorit(tip, d.get("preferinte")):
            # [320] „bifele decid doar WhatsApp/email, clopoțelul din aplicație arată tot”: nebifat în Notificări -> rămâne în clopoțel
            canal = "nedorit"
            _jurnal(nid, d["uid"], tip, d["canal"] if d["canal"] in ("email", "whatsapp") else "email", "netrimis",
                    detaliu=DETALIU_NEBIFAT)
        else:
            try:
                canal = livreaza(nid, d, tip)
            except Exception as e:  # noqa: BLE001 — o notificare căzută nu le oprește pe celelalte; eșecul se semnalează
                _obs.esec_secundar("livrare notificare %s" % nid, e)
                canal = "netrimis"
        rez[canal] = rez.get(canal, 0) + 1
    return rez


def superadmini(conn):
    """Id-urile superadminilor activi (destinatarii notificărilor de platformă)."""
    with conn.cursor() as cur:
        return _repo.superadmini(cur)


def pentru_superadmini(conn, tip, text, legatura=None):
    """O notificare de clopoțel pentru fiecare superadmin, în tranzacția apelantului; livrarea pe canal vine după commit."""
    from core import notificari_api as _n
    return _n.adauga_multi(conn, superadmini(conn), tip, text, legatura)


def stare_livrare(mesaj_id, stare, detaliu=None):
    """Webhook-ul: starea unui mesaj WhatsApp. „esuat” pe o notificare fără rezervă -> emailul pleacă acum (o singură dată)."""
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            r = _repo.scrie_starea_mesajului(cur, mesaj_id, stare, detaliu)
            rezerva = None
            if r and stare == "esuat" and not r[3] and r[2] in TIPURI:
                _repo.marcheaza_rezerva(cur, mesaj_id)
                e = _ru.emailul_contului(cur, r[1])
                rezerva = (r[0], {"uid": r[1], "email": e[0]}, r[2]) if e else None
        conn.commit()
    if rezerva:
        _pe_email(rezerva[0], rezerva[1], rezerva[2], rezerva=True, detaliu="WhatsApp nu a livrat: %s" % (detaliu or "fără motiv"))
    return bool(r)
