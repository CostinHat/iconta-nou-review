"""
core/notificari_scadenta.py — F131 comp.5: notificare email scadenta/restanta.

Cron zilnic (~08:00). Emailul pleaca spre CLIENTUL firmei, in numele firmei:
  From = contact@iconta.eu (SPF/DKIM iconta.eu), expeditor_nume = '<Firma> prin iConta',
  Reply-To = firma_profil.email (raspunsul clientului ajunge la firma).

Reguli (agreate cu Costin 17.07.2026):
  - OPT-IN per firma, implicit OPRIT (firma_profil.notificari_scadenta_activ).
  - Supape per factura: notificare_stop (nu notifica) / notificare_amanata_pana (pana la X).
  - Praguri {-3, +1, +7} zile fata de scadenta (negativ = inainte). Fara +14 (a doua
    somatie automata o decide omul).
  - STADIU CURENT, nu match exact pe azi: se trimite pragul cel mai urgent ATINS si
    netrimis. O zi ratata de cron intarzie, NU pierde; opt-in pe factura veche trimite
    doar stadiul curent (fara backfill/spam).
  - Idempotenta: jurnal notificari_scadenta (factura_id, prag) - un rand per (factura,
    prag), ca public.alerte_emise la F103. `stare` inregistreaza si esecurile
    (fara_reply_to / fara_email_client) - se raporteaza, nu se reincearca pragul.
"""
from core import common, db

PRAGURI = [-3, 1, 7]
# [R138] Copia regexului s-a scos: faptul e in `core/common`. Numele ramane exportat, fiindca
# modulul il foloseste in bucla de trimitere si e citat in gardile lui.
email_valid = common.email_valid


def prag_curent(scadenta, azi, deja_trimise, praguri=PRAGURI):
    """Pragul de trimis ACUM (stadiul curent) sau None. PUR.
    d = azi - scadenta (zile; pozitiv = restanta). deja_trimise = set de praguri deja
    in jurnal pt factura. Aplicabile = {p : d >= p}; curent = max(aplicabile);
    trimit doar daca nu e deja trimis (fara backfill al stadiilor depasite)."""
    if scadenta is None:
        return None
    d = (azi - scadenta).days
    aplicabile = [p for p in praguri if d >= p]
    if not aplicabile:
        return None
    curent = max(aplicabile)
    return None if curent in deja_trimise else curent


def _eticheta(prag):
    if prag < 0:
        return "scade in %d zile" % (-prag)
    if prag == 1:
        return "a devenit restanta"
    return "restanta de %d zile" % prag


def _email_corp(firma_nume, f, prag):
    """HTML minimal, in numele firmei. f = dict factura."""
    from decimal import Decimal
    suma = Decimal(str(f.get("suma") or 0))
    return (
        "<p>Bună ziua,</p>"
        "<p>Vă reamintim că factura <b>%s</b> emisă de <b>%s</b>, "
        "în valoare de <b>%s %s</b>, cu scadența <b>%s</b>, %s.</p>"
        "<p>Vă rugăm să efectuați plata sau să ne contactați "
        "dacă aveți întrebări.</p>"
        "<hr><p style='font-size:12px;color:#667'>Acest mesaj vă este trimis "
        "în numele <b>%s</b> prin platforma iConta.eu. Răspundeți la acest "
        "email pentru a contacta direct firma.</p>"
        % (f.get("numar") or "—", firma_nume, suma, f.get("moneda") or "lei",
           f.get("data_scadenta"), _eticheta(prag), firma_nume)
    )


def _rezerva_pragul(schema, factura_id, prag):
    """Rezervă pragul într-o tranzacție PROPRIE, comisă. `True` dacă rezervarea e a noastră.

    [P4, 09.09.2026] Limita tranzacției e a ACTULUI — o notificare —, nu a buclei care le
    parcurge pe toate. Rândul ăsta e singurul lucru care oprește a doua trimitere, deci trebuie
    să fie durabil **înainte** ca e-mailul să plece. `ON CONFLICT DO NOTHING ... RETURNING` face
    rezervarea și verificarea dintr-o singură mișcare: dacă nu întoarce nimic, altcineva a luat-o.
    """
    with db.get_conn(schema) as c:
        with c.cursor() as cur:
            cur.execute("INSERT INTO notificari_scadenta (factura_id, prag, stare) "
                        "VALUES (%s, %s, 'in_curs') ON CONFLICT (factura_id, prag) "
                        "DO NOTHING RETURNING factura_id", (factura_id, prag))
            return cur.fetchone() is not None


def _consemneaza(schema, factura_id, prag, stare):
    """Prag consumat FARA e-mail (fara reply-to, fara e-mail de client), in tranzactia lui.

    [P4] Sta aici, si nu pe conexiunea apelantului, ca sa ramana adevarat un singur lucru despre
    modulul asta: **nimic din el nu scrie in tranzactia altcuiva**. Cat timp o singura ramura mai
    scria acolo, cititorul trebuia sa stie CARE — iar asta e chiar felul de cunoastere pe care
    P4 il scoate din cap si il pune in cod."""
    with db.get_conn(schema) as c:
        with c.cursor() as cur:
            cur.execute("INSERT INTO notificari_scadenta (factura_id, prag, stare) "
                        "VALUES (%s, %s, %s) ON CONFLICT (factura_id, prag) DO NOTHING",
                        (factura_id, prag, stare))


def _scrie_rezultatul(schema, factura_id, prag, stare):
    """Rezultatul trimiterii, în tranzacția LUI. Un prag rămas `in_curs` = e-mail plecat, rezultat
    nescris: se vede, și e mai bun decât un e-mail trimis de două ori."""
    with db.get_conn(schema) as c:
        with c.cursor() as cur:
            cur.execute("UPDATE notificari_scadenta SET stare = %s "
                        " WHERE factura_id = %s AND prag = %s", (stare, factura_id, prag))


def emite_pentru_firma(conn, schema, azi=None):
    """Trimite notificarile scadente pentru o firma (daca opt-in). Intoarce
    {trimise, fara_reply_to, fara_email_client, inactiv}. Conexiunea pozitionata pe schema."""
    from core import observare
    from datetime import date as _d
    azi = azi or _d.today()
    rez = {"trimise": 0, "fara_reply_to": 0, "fara_email_client": 0, "inactiv": False}
    with conn.cursor() as cur:
        cur.execute("SELECT nume, email, COALESCE(notificari_scadenta_activ, false) "
                    "FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
        if not r or not r[2]:
            rez["inactiv"] = True
            return rez
        firma_nume, firma_email = r[0] or "Firma", r[1]
        reply_ok = email_valid(firma_email)
        cur.execute(
            "SELECT f.id, f.numar, f.data_scadenta, COALESCE(f.total,0) AS suma, f.moneda, "
            "       c.email AS client_email "
            "  FROM facturi f LEFT JOIN clienti c ON c.id = f.client_id "
            " WHERE f.directie='emisa' AND f.platita_la IS NULL "
            "   AND COALESCE(f.tip,'factura')='factura' AND f.storno_din_id IS NULL "
            "   AND COALESCE(f.notificare_stop, false) = false "
            "   AND (f.notificare_amanata_pana IS NULL OR f.notificare_amanata_pana < %s) "
            "   AND f.data_scadenta IS NOT NULL", (azi,))
        facturi = [dict(id=x[0], numar=x[1], data_scadenta=x[2], suma=x[3],
                        moneda=x[4], client_email=x[5]) for x in cur.fetchall()]
        for f in facturi:
            cur.execute("SELECT prag FROM notificari_scadenta WHERE factura_id=%s", (f["id"],))
            deja = {x[0] for x in cur.fetchall()}
            prag = prag_curent(f["data_scadenta"], azi, deja)
            if prag is None:
                continue
            if not reply_ok:
                stare = "fara_reply_to"
            elif not email_valid(f["client_email"]):
                stare = "fara_email_client"
            else:
                # [P4, 09.09.2026] REZERVAREA PRAGULUI SE COMITE ÎNAINTE DE E-MAIL.
                #
                # Ce era până azi: e-mailul pleca la CLIENTUL firmei, iar rândul care împiedică
                # retrimiterea se scria după el — amândouă în tranzacția deschisă pentru toată
                # firma, pentru toate facturile ei. O eroare la orice factură de după, sau la
                # commit, întorcea tranzacția: e-mailurile plecate rămâneau plecate, rândurile
                # care le consemnau nu. A doua zi, cronul le trimitea din nou. *Un `rollback` nu
                # desface un e-mail — iar aici desfăcea exact evidența care l-ar fi oprit.*
                #
                # Acum: se rezervă pragul într-o tranzacție PROPRIE, comisă; abia apoi pleacă
                # e-mailul; apoi se scrie rezultatul, tot separat. Alegerea e deliberată — **cel
                # mult o dată**, nu cel puțin o dată: o notificare pierdută se vede în evidență ca
                # prag rămas `in_curs`; una trimisă de două ori ajunge la clientul firmei și nu se
                # mai poate lua înapoi.
                if not _rezerva_pragul(schema, f["id"], prag):
                    continue          # rezervat de altcineva între citire și acum
                ok = observare.trimite_email_html(
                    f["client_email"],
                    "Factura %s - %s" % (f["numar"] or "", _eticheta(prag)),
                    _email_corp(firma_nume, f, prag),
                    reply_to=firma_email, expeditor_nume="%s prin iConta.eu" % firma_nume)
                stare = "trimis" if ok else "fara_reply_to"  # esec Brevo -> nu bloca pragul
                _scrie_rezultatul(schema, f["id"], prag, stare)
                rez["trimise" if stare == "trimis" else stare] += 1
                continue
            _consemneaza(schema, f["id"], prag, stare)
            rez["trimise" if stare == "trimis" else stare] += 1
    return rez


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    tot = {"trimise": 0, "fara_reply_to": 0, "fara_email_client": 0}
    for s in scheme:
        try:
            with db.get_conn(s) as conn:
                r = emite_pentru_firma(conn, s)
            if not r.get("inactiv"):
                for k in tot:
                    tot[k] += r.get(k, 0)
                print("  %s: trimise=%d fara_reply_to=%d fara_email_client=%d"
                      % (s, r["trimise"], r["fara_reply_to"], r["fara_email_client"]))
        except Exception as e:
            print("  ESEC %s: %s" % (s, e))
    print("Notificari scadenta: trimise=%d, fara_reply_to=%d, fara_email_client=%d"
          % (tot["trimise"], tot["fara_reply_to"], tot["fara_email_client"]))

    # [alerte_control_fiscal] Push in-app al findingurilor ROSII de control fiscal, agatat de acest
    # cron zilnic (nu timer nou - reutilizeaza slotul de 08:00). Logica IZOLATA in modulul propriu;
    # aici doar declansare, protejata: un esec al alertelor NU trebuie sa strice notificarile de scadenta.
    try:
        from core import alerte_control_fiscal
        alerte_control_fiscal.ruleaza()
    except Exception as e:
        print("  ESEC alerte control fiscal: %s" % e)

    # [supervizor] DECLANSATORUL PROPRIU al confruntarii incrucisate (Costin, 01.09.2026:
    # „extinde cronul de 08:00 care exista. Plus rulare la cerere. Nu construi al doilea mecanism").
    #
    # ASTA E TOT CE-I TREBUIA CA SA AIBA DECLANSATOR. Pana azi confruntarea se intampla agatata de
    # actul depunerii, deci mostenea momentul, domeniul si populatia actului; acum ruleaza pe
    # PORTOFOLIU, zilnic, fara sa astepte ca cineva sa depuna ceva.
    #
    # CE NU FACE, si e cerut explicit: nu impinge nimic in clopotel. **Clopotelul e deja cablat, prin
    # constructie** - o constatare orizontala ROSIE face `verifica_d390` sa intoarca `stare="rosu"`,
    # iar `alerte_control_fiscal.verificatori_rosii` il duce mai departe AGREGAT PE FIRMA. Deci
    # „clopotelul ramane rosu agregat, nu o notificare pe constatare" se respecta NEATINGAND nimic
    # acolo. Un push de aici ar fi fost chiar al doilea mecanism.
    #
    # Ce aduce in plus rularea asta, si nu se vede de nicaieri altundeva: **acoperirea proprie** -
    # cate firme au fost efectiv verificate si cate NU, cu numele si cauza. O firma pe care axa nu
    # ruleaza deloc arata, in orice alt loc, identic cu una curata.
    try:
        from core import supervizor as _sv
        from core.common import azi_ro as _azi_ro
        # [fus] perioada evaluata = zi RO, ca in `alerte_control_fiscal.ruleaza` — robust la OS TZ.
        _azi = _azi_ro()
        an, luna = _azi.year, _azi.month
        _r = _sv.ruleaza_portofoliu(an, luna)
        _z = _r["rezumat"]
        print("Supervizor (%04d-%02d): constatari=%d pe %d firme · fara subiect=%d · NEVERIFICATE=%d "
              "din %d · de confirmat=%d"
              % (an, luna, _z["constatari_total"], _z[_sv.CONSTATARI], _z[_sv.FARA_SUBIECT],
                 _z[_sv.NEVERIFICAT], _z["firme_in_domeniu"], _z["de_confirmat"]))
        for _f in _r["firme"]:
            if _f["rezultat"] == _sv.NEVERIFICAT:
                print("  NEVERIFICATA %s (%s): %s"
                      % (_f["schema"], _f["nume"], _f["neverificat"]["eroare"]))
    except Exception as e:
        print("  ESEC supervizor: %s" % e)


if __name__ == "__main__":
    from core import cron
    cron.ruleaza("notificari_scadenta", _main)
