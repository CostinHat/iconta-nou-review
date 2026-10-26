"""
core/sinteza_zilnica.py — sinteza zilnica a activitatii din cabinet,
trimisa seara patronului (admin_firma) pe email-ul de login.

Rulat de cron (19:00 Bucharest, luni-vineri). Nu trimite daca ziua e goala SI nimic nu asteapta.
Refoloseste observare.trimite_email_html (Brevo deja configurat pe iconta.eu).

[lotul 13, deficiența 565: „Sinteza pe email nu apare în Setări cont → Notificări și n-a ajuns niciodată la administrator (5 zile verificate
în inbox).”] CAUZA, citită în jurnalul jobului (`sinteza.log`, 16.10, 19.10, 22.10): „[email netrimis, registrul dezabonărilor nu s-a putut
citi (RuntimeError: pool neinițializat — cheamă init_pool() la startup) …]”. De la 268 (lotul 5), emailul INFORMATIV întreabă registrul
dezabonărilor prin `db.get_conn()` (pool-ul aplicației), iar jobul de cron lucra pe o conexiune brută și nu inițializa pool-ul -> fail-closed:
niciun email nu pleca, iar logul spunea doar „ESUAT”. Acum jobul inițializează pool-ul și lucrează numai prin el (fără conexiune brută).
Și: sinteza se trimite numai administratorilor care n-au debifat-o în Setări cont → Notificări (tipul `sinteza_zilnica`, bifat din oficiu),
iar o zi fără activitate dar cu elemente care așteaptă validarea / sesizări fără răspuns NU e „goală” (568: coada contează, nu numai ziua).

Test manual pe un singur destinatar:
  python3 -m core.sinteza_zilnica --test cineva@example.com
"""
import sys
import datetime
import psycopg2.extras as _E
from core.pdf_util import data_ro as _data_ro

from core import db
from core import observare
from core import repo_sinteza_zilnica as _repo
from core.common import esc as _esc_html   # [C39] text scris de om în HTML-ul emailurilor


def _patroni(conn):
    """Patronii activi: id, email, nume, cabinet, bifele din Notificări (`notificari_tipuri`, 565)."""
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        return _repo.patronii(cur)


def dorita(patron):
    """PURĂ. [565] Administratorul vrea sinteza? Bifa lui din Setări cont → Notificări; fără bifă salvată, implicitul (bifată)."""
    from core import notificari as _n
    return _n.dorit("sinteza_zilnica", patron.get("notificari_tipuri"))


def _nume_cabinet(conn, cabinet_id):
    with conn.cursor() as cur:
        return _repo.numele_cabinetului(cur, cabinet_id) or "cabinet"


def sinteza_cabinet(conn, cabinet_id, zi):
    """Numara ce s-a petrecut azi (zi = date) + ce a ramas in asteptare.
    Intoarce un dict cu cifre. Daca tot ce conteaza e 0 -> 'gol': True.
    [lotul 13] Instrucțiunile SQL stau în `core/repo_sinteza_zilnica.py` (depozitul primește cursorul): jobul își deschide acum singur
    conexiunea din pool (565), deci e USE_CASE, iar contractul straturilor cere SQL-ul în depozit."""
    with conn.cursor() as cur:
        d = _repo.cifrele_zilei(cur, cabinet_id, zi)
    activitate = (d["pregatite"] + d["validate"] + d["respinse"] + d["depuse"]
                  + d["sesizari_noi"] + d["pachete_trimise"])  # [p68_doar_pozitive]
    # [lotul 13, 568] ce așteaptă (coada întreagă, nu numai ce a intrat azi) face ziua „negoală”: 5 note de validat de pe 19.10 trebuie
    # amintite și într-o seară fără activitate
    d["gol"] = (activitate + d["de_validat"] + d["sesizari_fara_raspuns"] == 0)
    return d


def _html(nume_cabinet, zi, d):  # [p68_doar_pozitive] afiseaza doar randuri cu valoare > 0
    data_ro = _data_ro(zi)

    def rand(eticheta, val, accent=None):
        if not val:
            return ""  # ascunde zerourile
        culoare = accent or "#1a1d21"
        return (
            '<tr>'
            '<td style="padding:8px 0;color:#444;font-size:14px;">' + _esc_html(eticheta) + '</td>'
            '<td style="padding:8px 0;text-align:right;font-size:16px;font-weight:600;color:'
            + culoare + ';">' + _esc_html(val) + '</td>'
            '</tr>')

    def sectiune(titlu, randuri_html):
        if not randuri_html:
            return ""
        return (
            '<h3 style="font-size:14px;text-transform:uppercase;letter-spacing:.04em;'
            'color:#888;margin:0 0 6px;">' + _esc_html(titlu) + '</h3>'
            '<table style="width:100%;border-collapse:collapse;border-top:1px solid #eee;'
            'margin-bottom:24px;">' + randuri_html + '</table>')

    randuri_azi = (
        rand("Declarații pregătite", d["pregatite"]) +
        rand("Declarații validate", d["validate"], "#1d7a4d") +
        rand("Declarații respinse", d["respinse"], "#ff3b30") +
        rand("Declarații depuse", d["depuse"], "#1d7a4d") +
        rand("Sesizări noi de la clienți", d["sesizari_noi"]) +
        rand("Pachete lunare trimise", d.get("pachete_trimise", 0), "#1d7a4d"))

    randuri_asteptare = (
        rand("De validat (în așteptare)", d["de_validat"], "#c9961f") +
        rand("Sesizări fără răspuns", d["sesizari_fara_raspuns"], "#ff3b30"))

    corp_html = sectiune("Ce s-a petrecut azi", randuri_azi) + sectiune("Rămas de rezolvat", randuri_asteptare)
    if not corp_html:
        corp_html = '<p style="color:#777;font-size:14px;">Zi liniștită, nimic de raportat.</p>'

    return (
        '<div style="font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;'
        'max-width:560px;margin:0 auto;color:#1a1d21;">'
        '<h2 style="font-size:19px;margin:0 0 4px;">Sinteza zilei &mdash; ' + _esc_html(nume_cabinet) + '</h2>'
        '<p style="color:#777;font-size:13px;margin:0 0 20px;">' + _esc_html(data_ro) + '</p>'
        + corp_html +
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
    trimise, sarite, debifate = 0, 0, 0
    # [565] pool-ul aplicației: registrul dezabonărilor (`observare.refuz_dezabonare`) se citește prin el; fără el niciun email nu pleca
    db.init_pool()
    with db.get_conn() as conn:
        patroni = _patroni(conn)
        if test_email:
            patroni = patroni[:1]  # un singur cabinet, pentru proba
        de_trimis = []
        for p in patroni:
            cab = p["cabinet_id"]
            if not cab:
                continue
            if not test_email and not dorita(p):
                debifate += 1
                continue
            d = sinteza_cabinet(conn, cab, zi)
            if d["gol"] and not test_email:
                sarite += 1
                continue
            nume = _nume_cabinet(conn, cab)
            de_trimis.append((test_email or p["email"], nume, _html(nume, zi, d),
                              "Sinteza zilei %s — %s" % (_data_ro(zi, "zi_luna"), nume)))
        conn.rollback()   # numai citire; conexiunea se întoarce în pool înainte de trimiteri (registrul dezabonărilor ia alta)
    for catre, nume, html, subiect in de_trimis:
        ok = observare.trimite_email_html(catre, subiect, html, informativ=True)   # [268] informativ: cu dezabonare
        if ok:
            trimise += 1
            print("trimis ->", catre, "|", nume)
        else:
            print("ESUAT ->", catre, "|", nume, "(motivul e în rândul de deasupra)")
    print("Gata. Trimise: %d, sarite (zi goala): %d, debifate in Setari cont: %d" % (trimise, sarite, debifate))
    return {"trimise": trimise, "sarite": sarite, "debifate": debifate}


if __name__ == "__main__":
    test = None
    if "--test" in sys.argv:
        i = sys.argv.index("--test")
        if i + 1 < len(sys.argv):
            test = sys.argv[i + 1]
    from core import cron
    cron.ruleaza("sinteza_zilnica", lambda: ruleaza(test_email=test))
