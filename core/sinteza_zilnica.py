"""
core/sinteza_zilnica.py — sinteza zilnica a activitatii din cabinet,
trimisa seara patronului (admin_firma) pe email-ul de login.

Rulat de cron (19:00 Bucharest, luni-vineri). Nu trimite daca ziua e goala.
Refoloseste observare.trimite_email_html (Brevo deja configurat pe iconta.eu).

Test manual pe un singur destinatar:
  python3 -m core.sinteza_zilnica --test cineva@example.com
"""
import os
import sys
import datetime
import psycopg2
import psycopg2.extras as _E
from core.pdf_util import data_ro as _data_ro

from core import observare


def _conn():
    return psycopg2.connect(os.environ["DATABASE_URL"])


def _patroni(conn):
    """Patronii activi: id, email, nume, cabinet."""
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, email, prenume, nume, accounting_firm_id AS cabinet_id "
            "  FROM public.users "
            " WHERE rol = 'admin_firma' AND activ = true "
            "   AND email IS NOT NULL AND email <> ''")
        return cur.fetchall()


def _nume_cabinet(conn, cabinet_id):
    with conn.cursor() as cur:
        cur.execute("SELECT nume FROM public.accounting_firms WHERE id = %s",
                    (cabinet_id,))
        r = cur.fetchone()
    return (r[0] if r else "") or "cabinet"


def sinteza_cabinet(conn, cabinet_id, zi):
    """Numara ce s-a petrecut azi (zi = date) + ce a ramas in asteptare.
    Intoarce un dict cu cifre. Daca tot ce conteaza e 0 -> 'gol': True."""
    d = {}
    with conn.cursor() as cur:
        # declaratii pe evenimentele zilei
        cur.execute(
            "SELECT "
            "  COUNT(*) FILTER (WHERE creat_la::date  = %(z)s) AS pregatite, "
            "  COUNT(*) FILTER (WHERE aprobat_la::date = %(z)s) AS validate, "
            "  COUNT(*) FILTER (WHERE respins_la::date = %(z)s) AS respinse, "
            "  COUNT(*) FILTER (WHERE depus_la::date   = %(z)s) AS depuse "
            "  FROM public.declaratii_coada WHERE cabinet_id = %(c)s",
            {"z": zi, "c": cabinet_id})
        r = cur.fetchone()
        d["pregatite"], d["validate"], d["respinse"], d["depuse"] = (
            int(r[0]), int(r[1]), int(r[2]), int(r[3]))

        # in asteptare ACUM: declaratii la senior (de validat)
        cur.execute(
            "SELECT COUNT(*) FROM public.declaratii_coada "
            " WHERE cabinet_id = %s AND stare = 'la_senior'", (cabinet_id,))
        d["de_validat"] = int(cur.fetchone()[0])

        # sesizari clienti: noi azi + fara raspuns acum
        cur.execute(
            "SELECT "
            "  COUNT(*) FILTER (WHERE creat_la::date = %(z)s) AS noi, "
            "  COUNT(*) FILTER (WHERE stare = 'noua') AS fara_raspuns "
            "  FROM public.raportari "
            " WHERE cabinet_id = %(c)s AND pentru_admin = false",
            {"z": zi, "c": cabinet_id})
        r = cur.fetchone()
        d["sesizari_noi"], d["sesizari_fara_raspuns"] = int(r[0]), int(r[1])

        # pachete lunare trimise azi (leg tenant -> cabinet)
        cur.execute(
            "SELECT COUNT(*) FROM public.pachet_povestea p "
            "  JOIN public.tenants t ON t.id = p.tenant_id "
            " WHERE t.accounting_firm_id = %(c)s "
            "   AND p.status = 'trimis' AND p.updated_at::date = %(z)s",
            {"z": zi, "c": cabinet_id})
        d["pachete_trimise"] = int(cur.fetchone()[0])

    activitate = (d["pregatite"] + d["validate"] + d["respinse"] + d["depuse"]
                  + d["sesizari_noi"] + d["pachete_trimise"])  # [p68_doar_pozitive]
    d["gol"] = (activitate == 0)
    return d


def _html(nume_cabinet, zi, d):  # [p68_doar_pozitive] afiseaza doar randuri cu valoare > 0
    data_ro = _data_ro(zi)

    def rand(eticheta, val, accent=None):
        if not val:
            return ""  # ascunde zerourile
        culoare = accent or "#1a1d21"
        return (
            '<tr>'
            '<td style="padding:8px 0;color:#444;font-size:14px;">' + eticheta + '</td>'
            '<td style="padding:8px 0;text-align:right;font-size:16px;font-weight:600;color:'
            + culoare + ';">' + str(val) + '</td>'
            '</tr>')

    def sectiune(titlu, randuri_html):
        if not randuri_html:
            return ""
        return (
            '<h3 style="font-size:14px;text-transform:uppercase;letter-spacing:.04em;'
            'color:#888;margin:0 0 6px;">' + titlu + '</h3>'
            '<table style="width:100%;border-collapse:collapse;border-top:1px solid #eee;'
            'margin-bottom:24px;">' + randuri_html + '</table>')

    randuri_azi = (
        rand("Declaratii pregatite", d["pregatite"]) +
        rand("Declaratii validate", d["validate"], "#1d7a4d") +
        rand("Declaratii respinse", d["respinse"], "#ff3b30") +
        rand("Declaratii depuse", d["depuse"], "#1d7a4d") +
        rand("Sesizari noi de la clienti", d["sesizari_noi"]) +
        rand("Pachete lunare trimise", d.get("pachete_trimise", 0), "#1d7a4d"))

    randuri_asteptare = (
        rand("De validat (in asteptare)", d["de_validat"], "#c9961f") +
        rand("Sesizari fara raspuns", d["sesizari_fara_raspuns"], "#ff3b30"))

    corp = sectiune("Ce s-a petrecut azi", randuri_azi) + sectiune("Ramas de rezolvat", randuri_asteptare)
    if not corp:
        corp = '<p style="color:#777;font-size:14px;">Zi linistita, nimic de raportat.</p>'

    return (
        '<div style="font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;'
        'max-width:560px;margin:0 auto;color:#1a1d21;">'
        '<h2 style="font-size:19px;margin:0 0 4px;">Sinteza zilei &mdash; ' + nume_cabinet + '</h2>'
        '<p style="color:#777;font-size:13px;margin:0 0 20px;">' + data_ro + '</p>'
        + corp +
        '<div style="text-align:center;margin-top:28px;">'
        '<a href="https://iconta.eu" '
        'style="display:inline-block;background:#1d7a4d;color:#fff;'
        'text-decoration:none;padding:12px 28px;border-radius:8px;'
        'font-size:15px;font-weight:600;">Deschide iConta</a>'
        '</div>'
        '<p style="color:#aaa;font-size:12px;margin-top:20px;text-align:center;">'
        'Raport automat iConta.</p>'
        '</div>')


def ruleaza(test_email=None):
    """Trimite sinteza catre toti patronii. Daca test_email e dat,
    trimite DOAR catre acel email (sinteza primului cabinet gasit), pentru proba."""
    zi = datetime.date.today()
    trimise, sarite = 0, 0
    conn = _conn()
    try:
        patroni = _patroni(conn)
        if test_email:
            patroni = patroni[:1]  # un singur cabinet, pentru proba
        for p in patroni:
            cab = p["cabinet_id"]
            if not cab:
                continue
            d = sinteza_cabinet(conn, cab, zi)
            if d["gol"] and not test_email:
                sarite += 1
                continue
            nume = _nume_cabinet(conn, cab)
            html = _html(nume, zi, d)
            subiect = "Sinteza zilei %s - %s" % (_data_ro(zi, "zi_luna"), nume)
            catre = test_email or p["email"]
            ok = observare.trimite_email_html(catre, subiect, html)
            if ok:
                trimise += 1
                print("trimis ->", catre, "|", nume)
            else:
                print("ESUAT ->", catre, "|", nume)
    finally:
        conn.close()
    print("Gata. Trimise: %d, sarite (zi goala): %d" % (trimise, sarite))


if __name__ == "__main__":
    test = None
    if "--test" in sys.argv:
        i = sys.argv.index("--test")
        if i + 1 < len(sys.argv):
            test = sys.argv[i + 1]
    from core import cron
    cron.ruleaza("sinteza_zilnica", lambda: ruleaza(test_email=test))
