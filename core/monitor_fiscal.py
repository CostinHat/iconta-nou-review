# -*- coding: utf-8 -*-
"""Monitor fiscal: cron saptamanal. Citeste noutatile ANAF/MF, AI filtreaza
relevanta pentru iConta (TVA, salarii, plafoane, declaratii), salveaza + email."""
import re
import requests

SURSA_LISTA = "https://static.anaf.ro/static/10/Anaf/Legislatie_R/noutati_legislative.htm"
BAZA = "https://static.anaf.ro/static/10/Anaf/Legislatie_R/"

PROMPT = """Esti asistent fiscal pentru un soft de contabilitate romanesc.
Din textul de mai jos, extrage DOAR modificarile legislative fiscale noi care afecteaza:
cote TVA, salariu minim, CAS/CASS/impozit, plafoane (micro, TVA, MF), declaratii (structura/termen), dividende.
Raspunde DOAR JSON: [{"titlu": "...", "rezumat": "1-2 fraze, cu data intrarii in vigoare daca apare", "relevanta": "mare|medie"}]
Daca nu e nimic relevant, raspunde [].
TEXT:
"""


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


def salveaza(conn, sursa, alerte, url):
    noi = []
    with conn.cursor() as cur:
        for a in alerte:
            cur.execute("""INSERT INTO public.alerte_fiscale (sursa, titlu, rezumat, url, relevanta)
                           VALUES (%s,%s,%s,%s,%s)
                           ON CONFLICT (sursa, titlu) DO NOTHING RETURNING id""",
                        (sursa, a.get("titlu", "")[:500], a.get("rezumat"), url,
                         a.get("relevanta", "medie")))
            if cur.fetchone():
                noi.append(a)
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
        cur.execute("SELECT 1 FROM public.alerte_fiscale WHERE sursa='anaf_buletin' AND titlu=%s", (titlu[:500],))
        return cur.fetchone() is not None


def ruleaza(conn, max_buletine=3):
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
        if _procesat(conn, titlu):
            continue
        url = href if href.startswith("http") else BAZA + href.lstrip("/")
        try:
            rb = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
            text = text_din_pdf(rb.content) if rb.status_code == 200 else ""
            alerte = analizeaza(text) if text else []
        except Exception:
            alerte = []
        # marcam buletinul ca procesat chiar si fara alerte (idempotenta)
        salveaza(conn, "anaf_buletin", [{"titlu": titlu, "rezumat": f"{len(alerte)} modificari relevante", "relevanta": "info"}], url)
        toate_noi += salveaza(conn, "anaf_alerta", alerte, url)
        procesate += 1
    return toate_noi


def _main():
    from core import db, observare
    db.init_pool()
    with db.get_conn() as conn:
        noi = ruleaza(conn)
    print(f"{len(noi)} alerte noi")
    if noi:
        corp = "\n\n".join(f"[{a.get('relevanta')}] {a.get('titlu')}\n{a.get('rezumat')}" for a in noi)
        observare._trimite_brevo("iConta — alerte fiscale noi", corp)


if __name__ == "__main__":
    _main()
