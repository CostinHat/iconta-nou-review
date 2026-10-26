# -*- coding: utf-8 -*-
"""Monitor fiscal: cron saptamanal. Citeste noutatile ANAF/MF, AI filtreaza
relevanta pentru iConta (TVA, salarii, plafoane, declaratii), salveaza + email."""
import re

import requests

from core import clasificator_alerte as _ca
from core import repo_monitor_fiscal as _repo
from core.common import cate as _cate

SURSA_LISTA = "https://static.anaf.ro/static/10/Anaf/Legislatie_R/noutati_legislative.htm"
BAZA = "https://static.anaf.ro/static/10/Anaf/Legislatie_R/"

# [31.08.2026] Prompt-ul NU mai cere o judecata de ansamblu. Cere DOUA FAPTE, iar relevanta se
# calculeaza din ele in cod (`clasificator_alerte.relevanta_din`). Motivul e masurat, nu estetic:
# vechea forma cerea `relevanta: mare|medie` — o judecata FARA MOTIVE, care nu se poate contrazice.
# A gresit pe 2 din 2 acte, in directii OPUSE, si a putut sa taca fiindca nimic n-avea cu ce s-o
# compare. Doua fapte se pot confrunta cu masuratoarea; un verdict, nu.
#
# `mare|medie` nici nu continea raspunsul corect pentru un act care nu ne atinge deloc — nomenclatorul
# insusi cerea o minciuna. De-aia `zero` e acum o valoare.
PROMPT = """Esti asistent fiscal pentru un soft de contabilitate romanesc.
Din textul de mai jos, extrage DOAR modificarile legislative fiscale noi care afecteaza:
cote TVA, salariu minim, CAS/CASS/impozit, plafoane (micro, TVA, MF), declaratii (structura/termen), dividende.

Pentru fiecare, raspunde la DOUA INTREBARI DE FAPT, nu la «cat de important e»:

1. `directie` — incotro merge documentul pe care actul il reglementeaza:
   "catre_contribuabil" = ANAF emite catre contribuabil (decizii, referate, notificari, proceduri
                          interne ale organului fiscal). Softul NU produce asemenea documente.
   "catre_anaf"         = contribuabilul depune la ANAF (declaratii, formulare de declarare).
   "necunoscut"         = nu reiese din text. NU ghici.

2. `declaratii_atinse` — lista codurilor de declaratie carora actul le schimba modelul, continutul,
   nomenclatorul de obligatii sau termenul. Exemple de coduri: D100, D101, D112, D212, D300, D390,
   D394, D406, D710. Lista GOALA daca actul nu schimba niciuna. Un act care doar SE REFERA la o
   declaratie (o citeste ca intrare) NU o atinge — nu o pune in lista.

Raspunde DOAR JSON, cu EXACT campurile: %s
`data_vigoare` = "YYYY-MM-DD" sau null daca nu apare data intrarii in vigoare.
`data_publicarii` = "YYYY-MM-DD", data publicarii actului in Monitorul Oficial, sau null daca nu apare. NU ghici.
Daca nu e nimic relevant, raspunde [].
TEXT:
""" % ", ".join('"%s"' % c for c in _ca.CAMPURI_CERUTE)


def extrage_text(html):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return " ".join(t.split())[:12000]


def analizeaza(text):
    from core import ai_client
    import json
    if not ai_client.disponibil():
        return []
    r = ai_client.genereaza_text(PROMPT + text, max_tokens=1500, temperatura=0)
    try:
        curat = re.sub(r"```json|```", "", r or "").strip()
        d = json.loads(curat)
        return d if isinstance(d, list) else []
    except Exception:
        return []


def _data_iso(v):
    """PURĂ. O dată AAAA-LL-ZZ validă din răspunsul analizei, altfel None (nu se ghicește o dată)."""
    import datetime as _dt
    try:
        return _dt.date.fromisoformat(str(v)).isoformat() if v else None
    except ValueError:
        return None


def salveaza(conn, sursa, alerte, url):
    noi = []
    with conn.cursor() as cur:
        for a in alerte:
            dv = _data_iso(a.get("data_vigoare"))
            dp = _data_iso(a.get("data_publicarii"))   # [lotul 13, 646 b]
            # Relevanta se DERIVA din cele doua fapte, nu se ia din raspuns. Daca modelul o mai
            # trimite (prompt vechi in cache, alt apelant), e IGNORATA — altfel verdictul s-ar
            # strecura inapoi pe usa din dos, iar confruntarea n-ar mai avea ce compara.
            from core import clasificator_alerte as _ca
            directie = a.get("directie") or "necunoscut"
            if directie not in _ca.DIRECTII:
                directie = "necunoscut"
            decl = [str(x)[:16] for x in (a.get("declaratii_atinse") or [])]
            rel = _ca.relevanta_din(directie, decl)
            if _repo.insert_public(cur, sursa, url, rel, dv, directie, decl, a, dp):
                noi.append(dict(a, _relevanta=rel))   # relevanța DERIVATĂ (nu cea din răspuns), pentru notificare
    conn.commit()
    return noi


def buletine_din_lista(html):
    """Extrage (titlu, url) pentru buletinele PDF din pagina-index ANAF."""
    rez = []
    for m in re.finditer(r'href="([^"]*Noutati_legislative[^"]*\.pdf)"[^>]*>([^<]+)', html):
        rez.append(("Buletin " + m.group(2).strip(), m.group(1)))
    return rez[:20]


def text_din_pdf(continut):
    """Extrage text dintr-un PDF (bytes)."""
    try:
        from pypdf import PdfReader
        from io import BytesIO
        r = PdfReader(BytesIO(continut))
        return " ".join((p.extract_text() or "") for p in r.pages)[:12000]
    except Exception:
        return ""


def _procesat(conn, titlu):
    with conn.cursor() as cur:
        return _repo.select_public(cur, titlu) is not None


def ruleaza(max_buletine=3):
    """[P5 val 3, 11.09.2026] NU mai primeste o conexiune. Cele doua descarcari au termen de 30 s
    fiecare, iar forma dinainte le facea cu o conexiune din pool in mana — pentru tot lotul.

    Acum: HTTP fara conexiune -> tranzactie scurta pentru citirea `_procesat` -> HTTP fara
    conexiune -> tranzactie scurta pentru scriere. `_procesat` ramane unde era, ca verificare de
    DINAINTE, si `salveaza` marcheaza buletinul chiar si fara alerte — idempotenta, neschimbata.
    """
    from core import db
    toate_noi = []
    try:
        r = requests.get(SURSA_LISTA, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
    except Exception as e:
        print(f"lista: EROARE {e}")
        return []
    procesate = 0
    for titlu, href in buletine_din_lista(r.text):
        if procesate >= max_buletine:
            break
        with db.get_conn() as conn:                 # scurta, doar citirea
            deja = _procesat(conn, titlu)
        if deja:
            continue
        url = href if href.startswith("http") else BAZA + href.lstrip("/")
        try:                                        # fara nicio conexiune in mana
            rb = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
            text = text_din_pdf(rb.content) if rb.status_code == 200 else ""
            alerte = analizeaza(text) if text else []
        except Exception:
            alerte = []
        with db.get_conn() as conn:                 # scurta, doar scrierea
            # marcam buletinul ca procesat chiar si fara alerte (idempotenta)
            salveaza(conn, "anaf_buletin", [{"titlu": titlu, "rezumat": _cate(len(alerte), "modificare relevantă", "modificări relevante"), "relevanta": "info"}], url)
            toate_noi += salveaza(conn, "anaf_alerta", alerte, url)
            conn.commit()
        procesate += 1
    return toate_noi


# ── A DOUA SURSĂ: Portalul Legislativ (legislatie.just.ro) ─────────────────────────────────────────────────────────────────────────
# [17.10.2026, lotul 7 pct.2.6, comanda Costin verbatim în DECIZII „Lotul 6 închis”] „Alertele legislative: ultima a plecat pe 05.07. Află
# de ce s-au oprit, repară [...] (a doua sursă legislatie.just.ro, alertele importante pe canalul meu de notificare)”. Măsurat 17.10:
# pagina de buletine ANAF are ultima modificare pe 31.08 (ultimul buletin, nr. 30 din 28.08; nr. 31–35 -> 404), iar monitorul o citea ca
# SINGURĂ sursă — în timp ce ANAF a publicat în Monitorul Oficial 14 acte între 01.09 și 17.10 (portalul, emitentul ANAF), niciunul văzut.
# Portalul Ministerului Justiției listează actele după EMITENT și DATA PUBLICĂRII: `GET /Public/RezultateCautare?page=N&sectiuneact=<id
# emitent>&publicatinceputtext=AAAA/LL/ZZ&publicatsfarsittext=AAAA/LL/ZZ` (10 pe pagină), iar `/Public/DetaliiDocument/<id>` dă textul.
PORTAL = "https://legislatie.just.ro"
#: emitenții urmăriți (id-ul din lista portalului, citit 17.10.2026); ANAF și MF: orice act merge la analiză; Guvernul și Parlamentul emit
#: mult în afara fiscalului, deci numai actele al căror text pomenește un subiect fiscal (`_FISCAL`) merg la analiză
PORTAL_EMITENTI = {"239": "ANAF", "5": "Ministerul Finanțelor", "134": "Ministerul Finanțelor Publice", "3": "Guvernul", "2": "Parlamentul"}
PORTAL_TOATE = ("239", "5", "134")
_FISCAL = re.compile(r"Codul fiscal|Codului fiscal|procedur\w+ fiscal|impozit|tax[aăe] pe valoarea adăugată|TVA|contribuți\w+ sociale|"
                     r"contribuți\w+ de asigurări|salariul de bază minim|declarați\w+ fiscal|e-Factura|SAF-T", re.I)
PORTAL_ZILE = 45
PORTAL_MAX_ACTE = 25
_UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) iConta.eu monitor fiscal"}


def acte_din_pagina(html):
    """PURĂ. [(id document, eticheta)] din pagina de rezultate (`<nr>. ORDIN 1215 08/10/2026`)."""
    out = []
    for m in re.finditer(r'href="/Public/DetaliiDocument/(\d+)"[^>]*>\s*\d+\.\s*([^<]+)', html):
        out.append((m.group(1), " ".join(m.group(2).split())))
    return out


def acte_portal(emitent, de, pana, pagini=20):
    """Actele unui emitent publicate între `de` și `pana` (date), pe toate paginile."""
    vazute, out = set(), []
    for page in range(1, pagini + 1):
        r = requests.get(PORTAL + "/Public/RezultateCautare", headers=_UA, timeout=60, params={
            "page": page, "sectiuneact": emitent, "publicatinceputtext": de.strftime("%Y/%m/%d"),
            "publicatsfarsittext": pana.strftime("%Y/%m/%d")})
        r.raise_for_status()
        noi = [a for a in acte_din_pagina(r.text) if a[0] not in vazute]
        if not noi:
            break
        vazute.update(i for i, _ in noi)
        out += noi
    return out


def text_act(doc_id):
    """(titlul, textul) unui act din portal — titlul = prima frază care începe cu felul actului."""
    r = requests.get("%s/Public/DetaliiDocument/%s" % (PORTAL, doc_id), headers=_UA, timeout=60)
    r.raise_for_status()
    t = extrage_text(r.text)
    m = re.search(r"\b(ORDIN|HOTĂRÂRE|ORDONANȚĂ DE URGENȚĂ|ORDONANȚĂ|LEGE|PROCEDURĂ|INSTRUCȚIUNI|DECIZIE)\b nr\..{0,300}", t)
    titlu = m.group(0) if m else t[:300]
    return ((titlu.rsplit(" ", 1)[0] + " …") if len(titlu) >= 300 else titlu.strip(), t)


def _marcaj(doc_id):
    return "portal:%s" % doc_id


def ruleaza_portal(azi=None, max_acte=PORTAL_MAX_ACTE):
    """Actele noi din portal: fiecare intră o singură dată (marcajul `portal_act`), cu alertele extrase de analiză (`portal_alerta`).
    Ca la buletine: HTTP fără conexiune în mână, tranzacții scurte; un act eșuat la citire se reia la rularea următoare."""
    from core import db
    import datetime as _dt
    azi = azi or _dt.date.today()
    de = azi - _dt.timedelta(days=PORTAL_ZILE)
    noi, procesate = [], 0
    for emitent in PORTAL_EMITENTI:
        try:
            acte = acte_portal(emitent, de, azi)
        except Exception as e:  # noqa: BLE001 — un emitent căzut nu-i oprește pe ceilalți; se spune în jurnal
            print("portal %s: EROARE %s" % (PORTAL_EMITENTI[emitent], e))
            continue
        for doc_id, eticheta in acte:
            if procesate >= max_acte:
                return noi
            with db.get_conn() as conn:
                with conn.cursor() as cur:
                    deja = _repo.select_marcaj(cur, "portal_act", _marcaj(doc_id))
            if deja:
                continue
            try:
                titlu, text = text_act(doc_id)
            except Exception as e:  # noqa: BLE001 — se reia la rularea următoare (marcajul nu se scrie)
                print("portal %s: EROARE la actul %s: %s" % (PORTAL_EMITENTI[emitent], doc_id, e))
                continue
            de_analizat = emitent in PORTAL_TOATE or bool(_FISCAL.search(text))
            alerte = analizeaza(text) if de_analizat else []
            url = "%s/Public/DetaliiDocument/%s" % (PORTAL, doc_id)
            with db.get_conn() as conn:
                salveaza(conn, "portal_act", [{"titlu": _marcaj(doc_id), "rezumat": "%s — %s: %s" % (
                    PORTAL_EMITENTI[emitent], titlu[:300], _cate(len(alerte), "modificare relevantă", "modificări relevante")
                    if de_analizat else "fără subiect fiscal în text"), "relevanta": "info"}], url)
                noi += salveaza(conn, "portal_alerta", alerte, url)
            procesate += 1
    return noi


def notifica_importante(noi):
    """Alertele `mare` -> o notificare pentru fiecare superadmin, pe canalul lui (`core/notificari.py`); restul rămân în Panou Admin ->
    Anunțuri (propunerile monitorului). Întoarce câte notificări s-au scris."""
    from core import db
    from core import notificari as _notif
    importante = [a for a in noi if a.get("_relevanta") == "mare"]
    if not importante:
        return 0
    text = "Alertă legislativă importantă: %s" % "; ".join(str(a.get("titlu", ""))[:120] for a in importante[:3])
    with db.get_conn() as conn:
        r = _notif.pentru_superadmini(conn, "alerta_legislativa", text[:1000], "deschide:anunturi")
    return r.get("trimise", 0)


def _main():
    import sys as _sys
    from core import db
    db.init_pool()
    if "--doar-emitere" in _sys.argv:  # [F103 auto] cronul zilnic 7/3/0
        with db.get_conn() as conn:
            n = emite_alerte_programate(conn)
        print(f"{n} anunturi automate emise")
        return
    noi = ruleaza()                    # [P5 val 3] isi deschide singura tranzactiile scurte
    noi += ruleaza_portal()            # [17.10.2026, lotul 7 pct.2.6] a doua sursa: Portalul Legislativ
    with db.get_conn() as conn:
        emise = emite_alerte_programate(conn)  # [F103 auto] si dupa detectie
    # [17.10.2026, lotul 7 pct.2.6] „alertele importante vin la mine pe canalul de notificare” — nu mai pleaca un email-rezumat pe
    # adresa de alerta; cele importante devin notificari ale superadminilor (WhatsApp / email, dupa canalul fiecaruia), toate raman in
    # Panou Admin -> Anunturi (propunerile monitorului)
    notificate = notifica_importante(noi)
    print(f"{len(noi)} alerte noi ({sum(1 for a in noi if a.get('_relevanta') == 'mare')} importante, {notificate} notificari); "
          f"{emise} anunturi automate")

def emite_alerte_programate(conn):
    """[F103 auto] La 7/3/0 zile inainte de data intrarii in vigoare, anunt automat
    catre TOATE cabinetele active. Idempotent: jurnal public.alerte_emise (alerta_id, prag)."""
    emise = 0
    with conn.cursor() as cur:
        alerte = _repo.select_public_2(cur)
        for aid, titlu, rezumat, dv in alerte:
            for prag in (7, 3, 0):
                if not _repo.select(cur, dv, prag)[0]:
                    continue
                if not _repo.revendica_pragul(cur, aid, prag):
                    continue  # deja emis pragul asta (sau îl emite chiar acum altă rulare) — [lotul 10, C73 / U3] revendicat ÎNAINTE de anunțuri
                if prag == 0:
                    cap = "AZI intra in vigoare: "
                else:
                    cap = "In %s intra in vigoare: " % _cate(prag, "zi", "zile")
                mesaj = cap + (titlu or "") + ((" - " + rezumat) if rezumat else "")
                _repo.select_public_4(cur)
                ids = [_repo.insert_public_2(cur, cid, mesaj) for (cid,) in cur.fetchall()]
                _repo.leaga_trimiterea(cur, ids)   # [lotul 13, 646 c] o trimitere în lista anunțurilor din Panou Admin
                emise += len(ids)
    conn.commit()
    return emise

if __name__ == "__main__":
    from core import cron
    cron.ruleaza("monitor_fiscal", _main)
