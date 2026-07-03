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


# ---------- tabela poveste (public) ----------
def ensure_tabela(conn):
    with conn.cursor() as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS public.pachet_povestea(
            tenant_id INTEGER NOT NULL,
            an INTEGER NOT NULL,
            luna INTEGER NOT NULL,
            text TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ciorna',
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY (tenant_id, an, luna))""")


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
        note.append({"cont_debit": r["cont_debit"], "cont_credit": r["cont_credit"],
                     "suma": Decimal(str(r["suma"]))})
    return note


def _profil(conn_schema):
    with conn_schema.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, email, patron_nume, patron_email FROM firma_profil WHERE id = 1")
        return cur.fetchone() or {}


def _declaratii_depuse(conn_public, tenant_id, an, luna):
    with conn_public.cursor() as cur:
        cur.execute(
            "SELECT tip FROM public.declaratii_depuse "
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
def _prompt_poveste(rz, an, luna):
    LUNI = ["", "ianuarie","februarie","martie","aprilie","mai","iunie",
            "iulie","august","septembrie","octombrie","noiembrie","decembrie"]
    depuse = ", ".join(rz["declaratii_depuse"]) if rz["declaratii_depuse"] else "nicio declaratie"
    return (
        "Esti contabilul firmei si scrii un scurt rezumat lunar pentru patronul firmei, "
        "in limba romana, pe intelesul unui om care NU e contabil. Ton cald, profesional, clar. "
        "NU folosi jargon contabil. 2-3 paragrafe scurte. Fara titlu, fara semnatura.\n\n"
        "Date despre %s, luna %s %d:\n"
        "- Venituri: %.2f lei\n- Cheltuieli: %.2f lei\n- Rezultat: %.2f lei (%s)\n"
        "- Declaratii depuse la ANAF: %s\n\n"
        "Scrie povestea lunii: cum a mers firma, ce inseamna rezultatul in termeni simpli, "
        "si linisteste-l ca declaratiile au fost depuse la timp. Daca rezultatul e pierdere, "
        "explica fara alarmism. Daca nu sunt date, spune simplu ca luna a fost fara activitate inregistrata."
    ) % (rz["nume_firma"] or "firma", LUNI[luna] if 1 <= luna <= 12 else str(luna), an,
         rz["venituri"], rz["cheltuieli"], rz["rezultat"], rz["tip"], depuse)


def genereaza_poveste(conn_schema, conn_public, tenant_id, an, luna):
    """Cheama AI sa scrie un draft. Daca AI indisponibil -> intoarce ok=False, motiv."""
    rz = rezumat_luna(conn_schema, conn_public, tenant_id, an, luna)
    if not ai_client.disponibil():
        return {"ok": False, "cod": "AI_INDISPONIBIL", "rezumat": rz}
    try:
        text = ai_client.genereaza_text(_prompt_poveste(rz, an, luna), max_tokens=900)
    except Exception as e:
        return {"ok": False, "cod": "AI_EROARE", "mesaj": str(e), "rezumat": rz}
    return {"ok": True, "text": text, "rezumat": rz}


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
