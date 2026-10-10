"""
core/pachete_api.py — Pachetul lunar / "Povestea lunii".
Flux: aduna datele lunii -> AI scrie un draft de poveste pe intelesul antreprenorului
-> contabilul editeaza/aproba -> trimite pe email la antreprenor (Brevo).

Tabela (public): pachet_povestea(tenant_id, an, luna, text, status, updated_at).
DB pe schema tenantului pt date (note, firma_profil); povestea pe public.
"""
import re

import psycopg2.extras as _E
from decimal import Decimal

from core import motor, ai_client, observare
from core.ai_client import text_simplu


# Tabela public.pachet_povestea (tenant_id, an, luna, text, status, updated_at) traieste in prod;
# DDL-ul ei reproductibil sta in infra/bootstrap_public.sql (vezi DE_FACUT) - nu se creeaza lazy
# din cod (functia ensure_tabela era moarta, fara apelanti; stearsa 22.07).


# ---------- date lunare (pe schema tenantului) ----------
def _note_lunii(conn_schema, an, luna):
    """Notele contabile validate din luna (pt motor.rezultat)."""
    with conn_schema.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT l.cont_debit, l.cont_credit, l.suma "
            "  FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
            " WHERE EXTRACT(YEAR FROM i.data)=%s AND EXTRACT(MONTH FROM i.data)=%s "
            "   AND i.status='validata'",
            (an, luna))
        randuri = cur.fetchall()
    note = []
    for r in randuri:
        note.append({"debit": r["cont_debit"], "credit": r["cont_credit"],
                     "suma": Decimal(str(r["suma"]))})
    return note


def _profil(conn_schema):
    with conn_schema.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, email, patron_nume FROM firma_profil WHERE id = 1")
        return cur.fetchone() or {}


def _declaratii_depuse(conn_public, tenant_id, an, luna):
    with conn_public.cursor() as cur:
        cur.execute(
            "SELECT tip FROM public.declaratii_depuse_curente "
            " WHERE tenant_id=%s AND an=%s AND luna=%s", (tenant_id, an, luna))
        return [r[0].upper() for r in cur.fetchall()]


# ---------- rezumat lunar (pentru afisare + prompt AI) ----------
def rezumat_luna(conn_schema, conn_public, tenant_id, an, luna):
    note = _note_lunii(conn_schema, an, luna)
    rez = motor.rezultat(note) if note else {"venituri": 0, "cheltuieli": 0, "rezultat": 0, "tip": "neutru"}
    prof = _profil(conn_schema)
    depuse = _declaratii_depuse(conn_public, tenant_id, an, luna)
    return {
        "ok": True,
        "nume_firma": prof.get("nume"),
        "patron_nume": prof.get("patron_nume"),
        # [R65, 26.08.2026] O SINGURA adresa. `patron_email` avea precedenta aici si nicio cale
        # de scriere — coloana s-a si scos. Daca apare nevoia unei adrese separate de a firmei,
        # se construieste atunci, cu ecran si cu explicatie.
        "email": (prof.get("email") or "").strip(),
        "venituri": float(rez["venituri"]),
        "cheltuieli": float(rez["cheltuieli"]),
        "rezultat": float(rez["rezultat"]),
        # [comanda Costin 05.10.2026 pct.1, text fix din aceeași clasă] un rezultat ZERO nu e „profit”: motorul pune
        # `profit` pe `rez >= 0`, iar pachetul arăta „0,00 lei (profit)”.
        "tip": "neutru" if float(rez["rezultat"]) == 0 else rez["tip"],
        "declaratii_depuse": depuse,
        "are_date": bool(note),
    }


# [lot 06.10 pct.14, comanda Costin] „În email apar marcaje «**» netransformate. Emailul se trimite fără marcaje brute.”
# Povestea e TEXT SIMPLU; regula e `ai_client.text_simplu` (sursa unică pentru orice text AI afișat), aplicată la generare,
# la salvare și la orice afișare a unui text deja salvat (emailul, portalul) — o poveste aprobată înainte de reparație nu
# pleacă cu marcaje.


# ---------- narativ AI ----------
LUNI = ["", "ianuarie","februarie","martie","aprilie","mai","iunie",
        "iulie","august","septembrie","octombrie","noiembrie","decembrie"]


def _restante_desc(lipsa):
    """Restantele curente (control_fiscal_api.evalueaza_firma -> lipsa) ca text scurt,
    sau None daca nu exista restante. Fiecare item: {tip, an, luna, ...}."""
    parts = []
    for d in (lipsa or []):
        tip = (d.get("tip") or "").upper()
        l, a = d.get("luna"), d.get("an")
        per = (" " + LUNI[l]) if (l and 1 <= l <= 12) else ""
        if a:
            per += " " + str(a)
        parts.append((tip + per).strip())
    return ", ".join(parts) if parts else None


# [comanda Costin 05.10.2026 pct.1] „Textul generat folosește exact termenii și cifrele din pachet (venituri, cheltuieli,
# rezultat)”. Măsurat înainte: pachetul arăta „Venituri”, iar textul scria „încasări” și „a cheltuit mai mult decât a câștigat”.
# Venituri ≠ încasări (banii intrați) ≠ câștig; un antreprenor le citește diferit. Promptul cere termenii și sumele pachetului,
# iar `abateri_termeni` verifică textul DUPĂ generare (un model poate ignora o instrucțiune).
TERMENI_PACHET = ("venituri", "cheltuieli", "rezultat")
_SINONIME_INTERZISE = re.compile(r"(?i)\b(?:încas\w*|incas\w*|câștig\w*|castig\w*|bani\s+intra\w*|cifr[ăa]\s+de\s+afaceri|"
                                 r"(?:a|au|s-a|s-au)\s+intrat\b)")   # [deficiența 12] „tot ce a intrat ca venit” = încasare, nu venit
_RESTANTE = re.compile(r"(?i)\b(?:restan\w*|nedepus\w*|termen(?:ul|e|ele)?\s+dep[aă][sș]\w*|întârzier\w*|intarzier\w*)")
# [retestul Costin 09.10.2026, deficiența 32: „povestea lunii păstrează laude nesusținute de cifre”] Pachetul are cifrele UNEI luni:
# nicio comparație cu alte luni, niciun reper. O calificare („excelentă”, „creștere”, „felicitări”) nu se sprijină pe nimic din el.
_LAUDE = re.compile(r"(?i)\b(?:excelen\w*|extraordinar\w*|remarcabil\w*|impresionan\w*|fantastic\w*|minunat\w*|superb\w*|"
                    r"felicit\w*|bravo|succes\w*|reu[sș]i\w*|performan\w*|solid\w*|s[aă]n[aă]to[sș]\w*|prosper\w*|record\w*|"
                    r"frumo[sa]\w*|(?:foarte|deosebit\s+de)\s+bun\w*|cre[sș]te\w*|cre[sș]cut\w*|[iî]mbun[aă]t[aă]\w*|mai\s+bun\w*|"
                    r"[iî]ncuraj\w*|optimis\w*|lăudabil\w*|laudabil\w*|perfect\w*|admirabil\w*|str[aă]lucit\w*)")
# [retestul Costin 09.10.2026, deficiența 33: „povestea scrie fals «în septembrie nu a fost nicio declarație de depus»”; deficiența 209:
# „Povestea lunii: spune doar ce reiese din cifre și nimic despre declarații”] Declarațiile depuse stau în tabelul pachetului și al
# emailului; povestea nu vorbește despre declarații deloc — nici despre ce s-a depus, nici despre ce era de depus.
_DECLARATII = re.compile(r"(?i)declara[tț]i|\bD\s?\d{3}\b")
_PROPOZITIE = re.compile(r"(?<=[.!?…])\s+")
_SUMA_LEI = re.compile(r"(\d{1,3}(?:[.\s]\d{3})+(?:,\d{1,2})?|\d+(?:,\d{1,2})?)\s*(?:de\s+)?lei\b", re.I)


def _lei(x):
    from core.pdf_util import bani
    return bani(x, "lei")


def _suma_din_text(s):
    return round(float(s.replace(".", "").replace(" ", "").replace("\u00a0", "").replace(",", ".")), 2)


def abateri_termeni(text, rz):
    """Ce scrie textul altfel decât pachetul: [„termen: încasări”, „sumă: 1.200 lei (nu e în pachet)”, …]. Gol = textul
    folosește termenii și sumele pachetului."""
    out = sorted({"termen: " + m.group(0).lower() for m in _SINONIME_INTERZISE.finditer(text or "")})
    permise = {round(abs(float(rz.get(k) or 0)), 2) for k in TERMENI_PACHET}
    for m in _SUMA_LEI.finditer(text or ""):
        try:
            v = _suma_din_text(m.group(1))
        except ValueError:
            continue
        if v not in permise:
            out.append("sumă: %s (nu e în pachet)" % m.group(0).strip())
    if rz.get("tip") == "pierdere" and re.search(r"(?i)\bprofit", text or ""):
        out.append("termen: profit (pachetul arată pierdere)")
    if rz.get("tip") == "profit" and re.search(r"(?i)\bpierdere", text or ""):
        out.append("termen: pierdere (pachetul arată profit)")
    if _RESTANTE.search(text or ""):   # [lot 06.10 pct.16, decizia A] nu în povestea pentru client
        out.append("restanțe: povestea pentru client nu pomenește declarațiile restante (decizia A)")
    out += sorted({"laudă nesusținută de cifre: %s" % m.group(0).lower() for m in _LAUDE.finditer(text or "")})   # [deficiența 32]
    out += ["declarații: „%s” (povestea nu vorbește despre declarații)" % p for p in _propozitii_fara_sursa(text, rz, numai_declaratii=True)]
    return out


def _propozitii_fara_sursa(text, rz, numai_declaratii=False):
    """Propozițiile textului care spun ce povestea nu are voie să spună: o laudă nesusținută de cifre (deficiența 32) sau orice
    afirmație despre declarații (deficiențele 33 + 209)."""
    out = []
    for p in (x.strip() for ln in (text or "").split("\n") for x in _PROPOZITIE.split(ln)):
        if not p:
            continue
        despre_declaratii = bool(_DECLARATII.search(p))
        if despre_declaratii or (not numai_declaratii and _LAUDE.search(p)):
            out.append(p)
    return out


def scoate_afirmatii_fara_sursa(text, rz):
    """[deficiențele 32 + 33, retestul Costin 09.10.2026] Textul generat FĂRĂ propozițiile pe care pachetul nu le susține (laude,
    afirmații despre declarații nedepuse), și lista lor. Promptul le interzice și o reîncercare le numește, dar un model poate ignora
    o instrucțiune de două ori: ce ajunge în editor nu le mai conține — imposibil, nu improbabil. Rândurile textului se păstrează."""
    scoase = _propozitii_fara_sursa(text, rz)
    if not scoase:
        return text, []
    linii = []
    for ln in (text or "").split("\n"):
        pastrate = [x for x in _PROPOZITIE.split(ln) if x.strip() and x.strip() not in scoase]
        linii.append(" ".join(x.strip() for x in pastrate) if ln.strip() else ln)
    curat = re.sub(r"\n{3,}", "\n\n", "\n".join(linii)).strip()
    return curat, scoase


def _prompt_poveste(rz, an, luna, restante_desc=None, corectie=None):
    # [deficiențele 33 + 209] „Declarații depuse: nicio declarație” devenea „nu a fost nicio declarație de depus”, iar Costin: „spune doar
    # ce reiese din cifre și nimic despre declarații”. Promptul nu mai primește declarațiile deloc (ele stau în tabelul pachetului).
    # [lot 06.10 pct.16, decizia A a lui Costin] „Restanțele declarațiilor nu apar în povestea trimisă clientului.” Promptul
    # nu le mai primește (parametrul rămâne pentru semnătură, nefolosit), iar `abateri_termeni` prinde un text care le pomenește.
    del restante_desc
    calificativ = rz["tip"] or "neutru"   # exact cuvântul din pachet (profit / pierdere / neutru)
    corectie_linie = (("\nATENTIE: varianta anterioara a scris %s. Rescrie folosind DOAR termenii si sumele de mai sus.\n"
                       % "; ".join(corectie)) if corectie else "")
    return (
        "Esti contabilul firmei si scrii un scurt rezumat lunar pentru patronul firmei, "
        "in limba romana, pe intelesul unui om care NU e contabil. Ton profesional, sobru, clar. "
        "2-3 paragrafe scurte. Fara titlu, fara semnatura.\n\n"
        "Date despre %s, luna %s %d (exact cum apar in pachetul lunar pe care patronul il vede alaturi):\n"
        "- Venituri: %s\n- Cheltuieli: %s\n- Rezultat inainte de impozit: %s (%s)\n\n"
        "TERMENII SI CIFRELE (obligatoriu): foloseste EXACT cuvintele «venituri», «cheltuieli» si «rezultat», cu sumele "
        "de mai sus, scrise la fel. Veniturile NU sunt «incasari» (banii intrati in cont sunt alt lucru) si NU sunt "
        "«castig»; nu spune «a castigat», «a incasat», «bani intrati», «cifra de afaceri». Rezultatul il numesti "
        "«rezultat»; daca il califici, spui doar «%s», ca in pachet. Rezultatul e INAINTE de impozit: nu-l numi «profit net» "
        "si nu scade din el niciun impozit. Nu inventa alte sume in lei.\n"
        "Scrie povestea lunii: cum a mers firma, ce inseamna rezultatul in termeni simpli. "
        "Daca rezultatul e pierdere, explica fara alarmism. "
        "Nu vorbi despre declaratii restante, nedepuse sau termene depasite si nu afirma ca firma e «la zi»: "
        "situatia declaratiilor o discuta contabilul separat. Nu scrie nimic despre declaratii — nici ce s-a depus, nici ce era "
        "sau nu era de depus: povestea spune numai ce reiese din cifrele de mai sus. "
        "NU lauda si NU califica luna (fara «excelenta», «foarte buna», «felicitari», «crestere», «performanta», «succes»): "
        "pachetul are cifrele unei singure luni, fara comparatie cu alte luni — spui cifrele si ce inseamna, atat. "
        "Daca nu sunt date, spune simplu ca luna a fost fara activitate inregistrata.%s"
    ) % (rz["nume_firma"] or "firma", LUNI[luna] if 1 <= luna <= 12 else str(luna), an,
         _lei(rz["venituri"]), _lei(rz["cheltuieli"]), _lei(rz["rezultat"]), calificativ,
         calificativ, corectie_linie)


def genereaza_poveste(conn_schema, conn_public, tenant_id, an, luna, schema):
    """Cheama AI sa scrie un draft. Daca AI indisponibil -> intoarce ok=False, motiv.
    schema: numele schemei firmei (pentru control_fiscal_api.evalueaza_firma -> restante)."""
    rz = rezumat_luna(conn_schema, conn_public, tenant_id, an, luna)
    if not ai_client.disponibil():
        return {"ok": False, "cod": "AI_INDISPONIBIL", "rezumat": rz}
    from core import control_fiscal_api as _cf
    ev = _cf.evalueaza_firma(conn_schema, conn_public, tenant_id, schema)
    restante_desc = _restante_desc(ev.get("lipsa"))
    # o generare + o singură reîncercare, cu abaterile numite; dacă tot rămân, textul pleacă la editor CU ele (ecranul le
    # arată) — aprobarea nu se blochează: textul aprobat e al contabilului (CLAUDE.md §8, DECIZII 05.10.2026)
    abateri = None
    try:
        for _incercare in range(2):
            text = text_simplu(ai_client.genereaza_text(_prompt_poveste(rz, an, luna, restante_desc, corectie=abateri),
                                                         max_tokens=900))
            abateri = abateri_termeni(text, rz)
            if not abateri:
                break
    except Exception as e:
        return {"ok": False, "cod": "AI_EROARE", "mesaj": str(e), "rezumat": rz}
    text, scoase = scoate_afirmatii_fara_sursa(text, rz)   # [deficiențele 32 + 33] ce nu se sprijină pe pachet nu ajunge în editor
    abateri = abateri_termeni(text, rz)
    return {"ok": True, "text": text, "rezumat": rz, "restante": restante_desc, "abateri": abateri, "scoase": scoase}


# ---------- CRUD poveste ----------
def get_poveste(conn_public, tenant_id, an, luna):
    pass  # tabela creata manual (owner iconta_user)
    with conn_public.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT text, status, updated_at FROM public.pachet_povestea "
                    "WHERE tenant_id=%s AND an=%s AND luna=%s", (tenant_id, an, luna))
        row = cur.fetchone()
    if not row:
        return {"ok": True, "exista": False}
    return {"ok": True, "exista": True, "text": row["text"], "status": row["status"]}


def salveaza_poveste(conn_public, tenant_id, an, luna, text, status="ciorna"):
    text = text_simplu((text or "").strip())
    if not text:
        return {"ok": False, "cod": "TEXT_GOL"}
    pass  # tabela creata manual (owner iconta_user)
    with conn_public.cursor() as cur:
        # upsert-ok: salvare text pachet lunar pe (tenant,an,luna) - re-scriere intentionata
        cur.execute(
            "INSERT INTO public.pachet_povestea (tenant_id, an, luna, text, status, updated_at) "
            "VALUES (%s,%s,%s,%s,%s, now()) "
            "ON CONFLICT (tenant_id, an, luna) DO UPDATE SET "
            "text=EXCLUDED.text, status=EXCLUDED.status, updated_at=now()",
            (tenant_id, an, luna, text, status))
    return {"ok": True, "status": status}


# ---------- trimitere ----------
def _html(rz, an, luna, poveste, semnatura):
    """Emailul raportului lunar. [comanda Costin 05.10.2026 pct.7] arată CIFRELE pachetului (venituri, cheltuieli, rezultat,
    declarații depuse), cu aceiași termeni ca pachetul — previzualizarea e aceeași funcție, deci arată exact ce pleacă.
    Până azi: povestea și semnătura, fără nicio cifră; cu povestea goală, o casetă goală."""
    def esc(s): return ("" if s is None else str(s)).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    calificativ = rz.get("tip") or "neutru"   # exact cuvântul din pachet
    depuse = ", ".join(rz.get("declaratii_depuse") or []) or "niciuna"
    rand = ("<tr><td style='padding:4px 12px 4px 0;color:#555'>%s</td>"
            "<td style='padding:4px 0;text-align:right;font-weight:600'>%s</td></tr>")
    cifre = ("<table style='border-collapse:collapse;margin:0 0 16px'>%s%s%s%s</table>" % (
        rand % ("Venituri", esc(_lei(rz.get("venituri") or 0))),
        rand % ("Cheltuieli", esc(_lei(rz.get("cheltuieli") or 0))),
        rand % ("Rezultat înainte de impozit", esc("%s (%s)" % (_lei(rz.get("rezultat") or 0), calificativ))),
        rand % ("Declarații depuse", esc(depuse))))
    corp = esc(text_simplu(poveste)) if (poveste or "").strip() else "<i style='color:#5b6573'>Povestea lunii nu e scrisă încă.</i>"
    return (
        "<div style='font-family:sans-serif;font-size:15px;color:#111;max-width:640px'>"
        "<h2 style='margin:0 0 4px'>Raport lunar &mdash; %s</h2>"
        "<p style='color:#555;margin:0 0 16px'>Luna %02d/%d</p>"
        "%s"
        "<div style='background:#f6f8fa;padding:14px;border-radius:8px;white-space:pre-wrap'>%s</div>"
        "<p style='margin-top:14px;white-space:pre-wrap'>%s</p>"
        "<p style='color:#5b6573;font-size:13px;margin-top:20px'>Trimis prin iConta.</p></div>"
    ) % (esc(rz.get("nume_firma")), luna, an, cifre, corp, esc(semnatura))


def semnatura_cabinet(conn_public, uid, firm_id):
    """Compune semnatura raportului: nume contabil (public.users by uid) + nume cabinet
    (public.accounting_firms by firm_id). ctx-ul din token NU poarta numele, de aceea query aici.
    Fallback in cascada: doar cabinet daca lipseste contabilul; formula neutra daca lipsesc ambele.
    Nu intoarce niciodata string gol sau 'None'."""
    nume_contabil = nume_cabinet = ""
    with conn_public.cursor() as cur:
        if uid:
            cur.execute("SELECT prenume, nume FROM public.users WHERE id=%s", (uid,))
            r = cur.fetchone()
            if r:
                nume_contabil = " ".join(p.strip() for p in (r[0], r[1]) if p and p.strip())
        if firm_id:
            cur.execute("SELECT nume FROM public.accounting_firms WHERE id=%s", (firm_id,))
            r = cur.fetchone()
            if r and r[0]:
                nume_cabinet = r[0].strip()
    linii = [x for x in (nume_contabil, nume_cabinet) if x]
    if linii:
        return "Cu salutări,\n" + "\n".join(linii)
    return "Cu salutări,"


def preview_html(conn_schema, conn_public, tenant_id, an, luna, text, uid, firm):
    """HTML-ul emailului pentru un text dat (ciorna din editor, nu neaparat salvata),
    cu semnatura reala compusa din DB. Aceeasi functie _html ca trimite() -> preview
    identic cu emailul trimis. text vine din editor prin ruta, NU din pachet_povestea."""
    rz = rezumat_luna(conn_schema, conn_public, tenant_id, an, luna)
    semnatura = semnatura_cabinet(conn_public, uid, firm)
    return _html(rz, an, luna, text or "", semnatura)


def pregateste(conn_schema, conn_public, tenant_id, an, luna, semnatura=""):
    """CE ar pleca la antreprenor — numai CITIRE, niciun efect. Necesita email + status aprobat.

    [P5 val 3, 11.09.2026] Despartita de trimiterea propriu-zisa fiindca apelul la Brevo are
    termen de 15 s, iar ruta tinea DOUA conexiuni din pool peste el. Functia asta nu scrie nimic —
    deci separarea nu muta nicio decizie, doar elibereaza conexiunile inainte de efect.

    Intoarce `{ok: False, cod}` ca inainte, sau `{ok: True, email, subiect, html}`.
    """
    rz = rezumat_luna(conn_schema, conn_public, tenant_id, an, luna)
    email = rz["email"]
    if not email:
        return {"ok": False, "cod": "FARA_EMAIL"}
    pov = get_poveste(conn_public, tenant_id, an, luna)
    if not pov.get("exista") or pov.get("status") != "aprobat":
        return {"ok": False, "cod": "NEAPROBATA"}
    if not (pov.get("text") or "").strip():
        return {"ok": False, "cod": "POVESTE_GOALA"}
    return {"ok": True, "email": email,
            "subiect": "Raport lunar %02d/%d - %s" % (luna, an, rz["nume_firma"] or "firma"),
            "html": _html(rz, an, luna, pov["text"], semnatura)}


def trimite_pregatit(pregatit):
    """EFECTUL, in afara oricarei conexiuni. Codurile de raspuns raman exact cele de dinainte."""
    if not pregatit.get("ok"):
        return pregatit
    if not observare.trimite_email_html(pregatit["email"], pregatit["subiect"], pregatit["html"]):
        return {"ok": False, "cod": "EMAIL_ESUAT"}
    return {"ok": True, "email": pregatit["email"]}


# ICRD_POVESTI_LISTA_V1 - listeaza povestile aprobate ale unei firme (portal client)
def lista_povesti_aprobate(conn_public, tenant_id):
    with conn_public.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT an, luna, text, updated_at FROM public.pachet_povestea "
            "WHERE tenant_id=%s AND status='aprobat' ORDER BY an DESC, luna DESC",
            (tenant_id,))
        rows = cur.fetchall()
    for r in rows:   # [lot 06.10 pct.14] o poveste aprobată înainte de reparație nu ajunge la client cu marcaje
        r["text"] = text_simplu(r["text"])
    return rows
