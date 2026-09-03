# -*- coding: utf-8 -*-
"""frontend_test/proba_verificare_functionalitati.py — HAMUL campaniei de verificare.

**Comanda** (Costin, 03.09.2026): *„Probeaza fiecare functionalitate, intai cu invalide, apoi cu
valide, si noteaza in tabel raspunsul aplicatiei — mesajul VERBATIM, nu rezumat. La invalide se
urmareste un singur lucru: aplicatia vorbeste. Tacerea e defect, chiar daca valoarea n-a intrat."*

**CE FACE.** Trimite cereri reale catre aplicatia care ruleaza (`127.0.0.1:8010`), cu token emis
server-side pentru un utilizator real al portofoliului, si tipareste raspunsul **neatins**: codul
HTTP si corpul, exact cum vin. Nu interpreteaza, nu rezuma, nu repara.

**DE CE UN FISIER COMIS, si nu o proba de unica folosinta.** Campania tine mai multe ture si trece
prin `/clear`. O proba pastrata „pentru mai tarziu" e o copie fara proprietar — asta are proprietar
si o treaba: sa poata fi RE-RULATA dupa fiecare reparatie, ca sa se scrie rezultatul de dupa.
Numele incepe cu `proba_`, deci pytest nu o culege.

**SUBIECTUL.** Cabinetul 1968 (`Cabinet Contabil Prisma SRL`), utilizator `patron@prisma-cont.test`
(rol `admin_firma`), firma **4838 `Comert Micro TVA SRL`** (`tenant_003`). Tot portofoliul e fictiv;
nu se ocroteste nimic.

    ./venv/bin/python frontend_test/proba_verificare_functionalitati.py T01
"""
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/home/costin/iconta_nou")

#: Portul se poate schimba din mediu: reprobarea de dupa o reparatie ruleaza pe o instanta
#: proaspata (`--port 8011`), fiindca procesul de productie tine codul VECHI pana la repornire.
BAZA = os.environ.get("PROBA_BAZA", "http://127.0.0.1:8010")
EMAIL = "patron@prisma-cont.test"
EMAIL_ANGAJAT = "asistent@prisma-cont.test"
EMAIL_CLIENT = "client@prisma-cont.test"
FIRMA = 4838
FIRMA_ALTUI_CABINET = 34061
INEXISTENT = 999999


def token(email):
    from core import db, auth_api
    import psycopg2.extras as E
    try:
        db.init_pool()
    except Exception:
        pass
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=E.RealDictCursor) as cur:
            cur.execute("SELECT u.*, af.nume AS nume_firma FROM public.users u "
                        "LEFT JOIN public.accounting_firms af ON af.id=u.accounting_firm_id "
                        "WHERE u.email=%s", (email,))
            u = cur.fetchone()
        conn.rollback()
    return auth_api.emite_token(dict(u)) if u else None


def cere(metoda, cale, payload=None, tok=None, brut=None, tip_continut=None):
    """(cod, corp_verbatim). Nimic nu se prelucreaza: corpul se intoarce ca text, exact."""
    h = {}
    date = None
    if brut is not None:
        date = brut
        h["Content-Type"] = tip_continut
    elif payload is not None:
        date = json.dumps(payload).encode()
        h["Content-Type"] = "application/json"
    if tok:
        h["Authorization"] = "Bearer " + tok
    req = urllib.request.Request(BAZA + cale, date, h, method=metoda)
    try:
        r = urllib.request.urlopen(req, timeout=120)
        return r.getcode(), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as ex:
        return None, "EXCEPTIE LOCALA: %r" % (ex,)


def multipart(nume_camp, nume_fisier, continut, tip="text/plain"):
    lim = "----probaVF7311"
    b = []
    b.append("--" + lim)
    b.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (nume_camp, nume_fisier))
    b.append("Content-Type: " + tip)
    b.append("")
    b.append(continut)
    b.append("--" + lim + "--")
    b.append("")
    return ("\r\n".join(b)).encode(), "multipart/form-data; boundary=" + lim


# ── PROBELE ──────────────────────────────────────────────────────────────────
# (nr_unitate, eticheta, metoda, cale, payload, ce s-a introdus)
def probe_T01():
    return [
        (4, "GET /coada — filtru de stare inexistent", "GET", "/coada?stare=INEXISTENT", None,
         "stare=INEXISTENT (nicio stare din nomenclator)"),
        (5, "POST /coada — firma inexistenta", "POST", "/coada",
         {"tenant_id": INEXISTENT, "tip": "d300", "an": 2026, "luna": 1},
         "tenant_id=999999"),
        (5, "POST /coada — luna 13", "POST", "/coada",
         {"tenant_id": FIRMA, "tip": "d300", "an": 2026, "luna": 13}, "luna=13"),
        (5, "POST /coada — tip de declaratie inexistent", "POST", "/coada",
         {"tenant_id": FIRMA, "tip": "d999", "an": 2026, "luna": 1}, "tip=d999"),
        (5, "POST /coada — corp gol", "POST", "/coada", {}, "corp JSON gol"),
        (6, "POST /coada/{}/aproba — element inexistent", "POST",
         "/coada/%d/aproba" % INEXISTENT, {}, "coada_id=999999"),
        (8, "POST /coada/{}/depune — element inexistent", "POST",
         "/coada/%d/depune" % INEXISTENT, {}, "coada_id=999999"),
        (9, "POST /coada/{}/respinge — motiv gol", "POST",
         "/coada/%d/respinge" % INEXISTENT, {"motiv": ""}, "motiv=\"\" (sir gol)"),
        (9, "POST /coada/{}/respinge — fara motiv", "POST",
         "/coada/%d/respinge" % INEXISTENT, {}, "camp motiv absent"),
        (12, "GET /declaratii/tipuri — firma inexistenta", "GET",
         "/declaratii/tipuri?tenant_id=%d" % INEXISTENT, None, "tenant_id=999999"),
        (13, "POST /declaratii/{tip} — tip inexistent", "POST", "/declaratii/d999",
         {"tenant_id": FIRMA, "an": 2026, "luna": 1}, "tip=d999"),
        (13, "POST /declaratii/{tip} — luna 13", "POST", "/declaratii/d300",
         {"tenant_id": FIRMA, "an": 2026, "luna": 13}, "luna=13"),
        (13, "POST /declaratii/{tip} — an 1900", "POST", "/declaratii/d300",
         {"tenant_id": FIRMA, "an": 1900, "luna": 1}, "an=1900"),
        (13, "POST /declaratii/{tip} — an ca text", "POST", "/declaratii/d300",
         {"tenant_id": FIRMA, "an": "douamiidouazecisisase", "luna": 1}, "an=\"douamiidouazecisisase\""),
        (13, "POST /declaratii/{tip} — firma inexistenta", "POST", "/declaratii/d300",
         {"tenant_id": INEXISTENT, "an": 2026, "luna": 1}, "tenant_id=999999"),
        (14, "POST /declaratii/{tip}/valideaza — luna 13", "POST", "/declaratii/d300/valideaza",
         {"tenant_id": FIRMA, "an": 2026, "luna": 13}, "luna=13"),
        (14, "POST /declaratii/{tip}/valideaza — tip inexistent", "POST",
         "/declaratii/d999/valideaza", {"tenant_id": FIRMA, "an": 2026, "luna": 1}, "tip=d999"),
        (15, "GET /firme/{}/verificari — fara an si luna", "GET",
         "/firme/%d/verificari" % FIRMA, None, "parametrii an si luna absenti"),
        (15, "GET /firme/{}/verificari — luna 13", "GET",
         "/firme/%d/verificari?an=2026&luna=13" % FIRMA, None, "luna=13"),
        (17, "POST /istoric-declaratii-import — randuri goale", "POST",
         "/tenants/%d/istoric-declaratii-import" % FIRMA, {"randuri": []}, "randuri=[]"),
        (17, "POST /istoric-declaratii-import — rand fara campuri", "POST",
         "/tenants/%d/istoric-declaratii-import" % FIRMA, {"randuri": [{}]}, "randuri=[{}]"),
    ]


def probe_import_gol():
    """Aceeasi clasa ca #17: un import cu lista goala. Cerut de Costin dupa lotul 1 —
    *„verifica apoi daca mai exista alte cai de import sau de inlocuire care golesc la intrare
    vida"*. Cautate mecanic: `DELETE FROM <tabel>` fara `WHERE`, in modulele de import."""
    return [
        (0, "POST /tenants/{}/asociati-import — lista goala", "POST",
         "/tenants/%d/asociati-import" % FIRMA, {"randuri": []}, "randuri=[]"),
        (0, "POST /tenants/{}/mijloace-fixe-import — lista goala", "POST",
         "/tenants/%d/mijloace-fixe-import" % FIRMA, {"randuri": []}, "randuri=[]"),
        (0, "POST /tenants/{}/parteneri — lista goala", "POST",
         "/tenants/%d/parteneri" % FIRMA, {"randuri": []}, "randuri=[]"),
    ]


FARA_TOKEN = {"GET /control-fiscal — fara token", "GET /supervizor — fara token"}
CU_CLIENT = {"GET /termene — cu rol CLIENT"}


def ruleaza(lot):
    tok = token(EMAIL)
    tok_client = token(EMAIL_CLIENT)
    probe = {"T01": probe_T01, "IMPORT-GOL": probe_import_gol}[lot]()
    out = []
    for nr, eticheta, metoda, cale, payload, introdus in probe:
        t = tok
        if eticheta in FARA_TOKEN:
            t = None
        elif eticheta in CU_CLIENT:
            t = tok_client
        cod, corp = cere(metoda, cale, payload, t)
        out.append({"nr": nr, "eticheta": eticheta, "metoda": metoda, "cale": cale,
                    "introdus": introdus, "cod": cod, "corp": corp})
        print("=" * 100)
        print("#%s  %s" % (nr, eticheta))
        print("    introdus: %s" % introdus)
        print("    HTTP %s" % cod)
        print("    corp: %s" % corp[:1500])
    if lot != "T01":
        return out
    # upload-ul, separat: cere multipart
    body, tip = multipart("fisier", "nu_e_un_tabel.txt", "linia unu, care nu e nici CSV nici XLSX")
    cod, corp = cere("POST", "/tenants/%d/istoric-declaratii-import/incarca" % FIRMA,
                     None, tok, brut=body, tip_continut=tip)
    out.append({"nr": 18, "eticheta": "POST .../incarca — fisier text in loc de tabel",
                "metoda": "POST", "cale": "/tenants/{}/istoric-declaratii-import/incarca",
                "introdus": "fisier .txt cu o linie de proza", "cod": cod, "corp": corp})
    print("=" * 100)
    print("#18  POST .../incarca — fisier text in loc de tabel")
    print("    HTTP %s" % cod)
    print("    corp: %s" % corp[:1500])
    return out


if __name__ == "__main__":
    lot = sys.argv[1] if len(sys.argv) > 1 else "T01"
    rez = ruleaza(lot)
    print("=" * 100)
    print("PROBE: %d" % len(rez))
