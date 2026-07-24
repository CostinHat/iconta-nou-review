"""
core/pachete_api.py — Pachetul lunar / "Povestea lunii".
Flux: aduna datele lunii -> AI scrie un draft de poveste pe intelesul antreprenorului
-> contabilul editeaza/aproba -> trimite pe email la antreprenor (Brevo).

Tabela (public): pachet_povestea(tenant_id, an, luna, text, status, updated_at).
DB pe schema tenantului pt date (note, firma_profil); povestea pe public.
"""
import psycopg2.extras as _E
from decimal import Decimal

from core import motor, ai_client, observare


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
        cur.execute("SELECT nume, email, patron_nume, patron_email FROM firma_profil WHERE id = 1")
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
        "email": (prof.get("patron_email") or prof.get("email") or "").strip(),
        "venituri": float(rez["venituri"]),
        "cheltuieli": float(rez["cheltuieli"]),
        "rezultat": float(rez["rezultat"]),
        "tip": rez["tip"],
        "declaratii_depuse": depuse,
        "are_date": bool(note),
    }


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


def _prompt_poveste(rz, an, luna, restante_desc=None):
    depuse = ", ".join(rz["declaratii_depuse"]) if rz["declaratii_depuse"] else "nicio declaratie"
    restante_linie = (("- Declaratii RESTANTE (nedepuse, termen depasit): %s\n" % restante_desc)
                      if restante_desc else "- Declaratii restante: niciuna\n")
    return (
        "Esti contabilul firmei si scrii un scurt rezumat lunar pentru patronul firmei, "
        "in limba romana, pe intelesul unui om care NU e contabil. Ton cald, profesional, clar. "
        "NU folosi jargon contabil. 2-3 paragrafe scurte. Fara titlu, fara semnatura.\n\n"
        "Date despre %s, luna %s %d:\n"
        "- Venituri: %.2f lei\n- Cheltuieli: %.2f lei\n- Rezultat: %.2f lei (%s)\n"
        "- Declaratii depuse la ANAF: %s\n"
        "%s\n"
        "Scrie povestea lunii: cum a mers firma, ce inseamna rezultatul in termeni simpli. "
        "Daca rezultatul e pierdere, explica fara alarmism. "
        "NU afirma ca firma e la zi sau ca nu are restante decat daca lista de datorate/lipsa e goala; "
        "daca exista restante, mentioneaza-le concret, fara alarmism. "
        "Daca nu sunt date, spune simplu ca luna a fost fara activitate inregistrata."
    ) % (rz["nume_firma"] or "firma", LUNI[luna] if 1 <= luna <= 12 else str(luna), an,
         rz["venituri"], rz["cheltuieli"], rz["rezultat"], rz["tip"], depuse, restante_linie)


def genereaza_poveste(conn_schema, conn_public, tenant_id, an, luna, schema):
    """Cheama AI sa scrie un draft. Daca AI indisponibil -> intoarce ok=False, motiv.
    schema: numele schemei firmei (pentru control_fiscal_api.evalueaza_firma -> restante)."""
    rz = rezumat_luna(conn_schema, conn_public, tenant_id, an, luna)
    if not ai_client.disponibil():
        return {"ok": False, "cod": "AI_INDISPONIBIL", "rezumat": rz}
    from core import control_fiscal_api as _cf
    ev = _cf.evalueaza_firma(conn_schema, conn_public, tenant_id, schema)
    restante_desc = _restante_desc(ev.get("lipsa"))
    try:
        text = ai_client.genereaza_text(_prompt_poveste(rz, an, luna, restante_desc), max_tokens=900)
    except Exception as e:
        return {"ok": False, "cod": "AI_EROARE", "mesaj": str(e), "rezumat": rz}
    return {"ok": True, "text": text, "rezumat": rz, "restante": restante_desc}


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
    text = (text or "").strip()
    if not text:
        return {"ok": False, "cod": "TEXT_GOL"}
    pass  # tabela creata manual (owner iconta_user)
    with conn_public.cursor() as cur:
        cur.execute(
            "INSERT INTO public.pachet_povestea (tenant_id, an, luna, text, status, updated_at) "
            "VALUES (%s,%s,%s,%s,%s, now()) "
            "ON CONFLICT (tenant_id, an, luna) DO UPDATE SET "
            "text=EXCLUDED.text, status=EXCLUDED.status, updated_at=now()",
            (tenant_id, an, luna, text, status))
    return {"ok": True, "status": status}


# ---------- trimitere ----------
def _html(nume_firma, an, luna, poveste, semnatura):
    def esc(s): return ("" if s is None else str(s)).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return (
        "<div style='font-family:sans-serif;font-size:15px;color:#111;max-width:640px'>"
        "<h2 style='margin:0 0 4px'>Raport lunar &mdash; %s</h2>"
        "<p style='color:#555;margin:0 0 16px'>Luna %02d/%d</p>"
        "<div style='background:#f6f8fa;padding:14px;border-radius:8px;white-space:pre-wrap'>%s</div>"
        "<p style='margin-top:14px;white-space:pre-wrap'>%s</p>"
        "<p style='color:#888;font-size:13px;margin-top:20px'>Trimis prin iConta.</p></div>"
    ) % (esc(nume_firma), luna, an, esc(poveste), esc(semnatura))


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


def trimite(conn_schema, conn_public, tenant_id, an, luna, semnatura=""):
    """Trimite povestea aprobata la antreprenor. Necesita email + status aprobat."""
    rz = rezumat_luna(conn_schema, conn_public, tenant_id, an, luna)
    email = rz["email"]
    if not email:
        return {"ok": False, "cod": "FARA_EMAIL"}
    pov = get_poveste(conn_public, tenant_id, an, luna)
    if not pov.get("exista") or pov.get("status") != "aprobat":
        return {"ok": False, "cod": "NEAPROBATA"}
    subiect = "Raport lunar %02d/%d - %s" % (luna, an, rz["nume_firma"] or "firma")
    html = _html(rz["nume_firma"], an, luna, pov["text"], semnatura)
    ok = observare.trimite_email_html(email, subiect, html)
    if not ok:
        return {"ok": False, "cod": "EMAIL_ESUAT"}
    return {"ok": True, "email": email}


# ICRD_POVESTI_LISTA_V1 - listeaza povestile aprobate ale unei firme (portal client)
def lista_povesti_aprobate(conn_public, tenant_id):
    with conn_public.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT an, luna, text, updated_at FROM public.pachet_povestea "
            "WHERE tenant_id=%s AND status='aprobat' ORDER BY an DESC, luna DESC",
            (tenant_id,))
        return cur.fetchall()
