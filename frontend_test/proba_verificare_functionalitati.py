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
    ./venv/bin/python frontend_test/proba_verificare_functionalitati.py T02
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


def cere(metoda, cale, payload=None, tok=None, brut=None, tip_continut=None,
         antete=None):
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
    if antete:
        h.update(antete)
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


def probe_T02(cheie=None):
    """LOTUL 2 — T02, factura emisa. Cele 11 unitati ale traseului aflate in perimetrul etapei 1:
    #20, #21 (calea de API, cu cheie), #22, #23, #25, #27, #28, #30, #31, #34, #35.

    **Ce se lasa in urma, declarat** (capcana 9 din predare): singurele probe care POT scrie sunt
    cele de pe `#30` (numerotarea) si `#35` (supapa). Numerotarea se citeste inainte si se pune la
    loc dupa, de `ruleaza()`; supapa se probeaza numai pe o factura INEXISTENTA, deci `UPDATE`-ul
    nu prinde niciun rand. Restul sunt refuzuri asteptate; daca vreunul TRECE, faptul ala e chiar
    rezultatul probei si se scrie ca atare."""
    F = FIRMA
    linie_ok = {"descriere": "consultanta", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21}
    p = [
        # ── #22 lista facturilor ────────────────────────────────────────────
        (22, "GET /facturi — luna 13", "GET", "/tenants/%d/facturi?an=2026&luna=13" % F, None,
         "an=2026&luna=13"),
        (22, "GET /facturi — directie inexistenta", "GET",
         "/tenants/%d/facturi?directie=lateral" % F, None, "directie=lateral"),
        (22, "GET /facturi — limit negativ", "GET", "/tenants/%d/facturi?limit=-5" % F, None,
         "limit=-5"),
        (22, "GET /facturi — an ca text", "GET", "/tenants/%d/facturi?an=anul-trecut" % F, None,
         "an=anul-trecut"),
        # ── #23 crearea unei facturi ────────────────────────────────────────
        (23, "POST /facturi — corp gol", "POST", "/tenants/%d/facturi" % F, {}, "corp JSON gol"),
        (23, "POST /facturi — fara nicio linie", "POST", "/tenants/%d/facturi" % F,
         {"numar": "PROBA-1", "data_emitere": "2026-09-03", "directie": "emisa", "linii": []},
         "linii=[]"),
        (23, "POST /facturi — directie inexistenta", "POST", "/tenants/%d/facturi" % F,
         {"numar": "PROBA-2", "data_emitere": "2026-09-03", "directie": "lateral",
          "linii": [linie_ok], "tert_nume": "Proba SRL", "tert_cui": "RO1234567897"},
         "directie=lateral"),
        (23, "POST /facturi — data inexistenta in calendar", "POST", "/tenants/%d/facturi" % F,
         {"numar": "PROBA-3", "data_emitere": "2026-02-31", "directie": "emisa",
          "linii": [linie_ok], "tert_nume": "Proba SRL", "tert_cui": "RO1234567897"},
         "data_emitere=2026-02-31 (31 februarie)"),
        (23, "POST /facturi — cota de TVA inexistenta", "POST", "/tenants/%d/facturi" % F,
         {"numar": "PROBA-4", "data_emitere": "2026-09-03", "directie": "emisa",
          "linii": [dict(linie_ok, cota_tva=99)], "tert_nume": "Proba SRL",
          "tert_cui": "RO1234567897"}, "cota_tva=99"),
        (23, "POST /facturi — numar deja folosit", "POST", "/tenants/%d/facturi" % F,
         {"numar": "CMT149", "data_emitere": "2026-09-03", "directie": "emisa",
          "linii": [linie_ok], "tert_nume": "Proba SRL", "tert_cui": "RO1234567897"},
         "numar=CMT149 (exista deja pe factura 3)"),
        # ── #25 sablonul de factura recurenta ───────────────────────────────
        (25, "POST /facturi-recurente — corp gol", "POST",
         "/tenants/%d/facturi-recurente" % F, {}, "corp JSON gol"),
        (25, "POST /facturi-recurente — ziua 45", "POST", "/tenants/%d/facturi-recurente" % F,
         {"linii": [linie_ok], "tert_nume": "Proba SRL", "zi_emitere": 45}, "zi_emitere=45"),
        (25, "POST /facturi-recurente — ziua ca text", "POST",
         "/tenants/%d/facturi-recurente" % F,
         {"linii": [linie_ok], "tert_nume": "Proba SRL", "zi_emitere": "prima"},
         "zi_emitere=\"prima\""),
        # ── #27 comutarea sablonului ────────────────────────────────────────
        (27, "PUT /facturi-recurente/{sid} — fara activ", "PUT",
         "/tenants/%d/facturi-recurente/1" % F, {}, "parametrul activ absent"),
        (27, "PUT /facturi-recurente/{sid} — activ ca text", "PUT",
         "/tenants/%d/facturi-recurente/1?activ=poate" % F, {}, "activ=poate"),
        (27, "PUT /facturi-recurente/{sid} — sablon inexistent", "PUT",
         "/tenants/%d/facturi-recurente/%d?activ=true" % (F, INEXISTENT), {}, "sid=999999"),
        # ── #28 emiterea ────────────────────────────────────────────────────
        (28, "POST /facturi/emite — corp gol", "POST", "/tenants/%d/facturi/emite" % F, {},
         "corp JSON gol"),
        (28, "POST /facturi/emite — fara beneficiar", "POST", "/tenants/%d/facturi/emite" % F,
         {"linii": [linie_ok], "tert_nume": ""}, "tert_nume=\"\""),
        (28, "POST /facturi/emite — fara nicio linie", "POST", "/tenants/%d/facturi/emite" % F,
         {"linii": [], "tert_nume": "Proba SRL"}, "linii=[]"),
        (28, "POST /facturi/emite — cantitate negativa", "POST",
         "/tenants/%d/facturi/emite" % F,
         {"linii": [dict(linie_ok, cantitate=-5)], "tert_nume": "Proba SRL"}, "cantitate=-5"),
        # `tert_cui` e completat DELIBERAT: fara el proba se oprea la codul de partener si
        # nu ajungea niciodata la moneda — masurasem alta intrebare decat cea scrisa.
        (28, "POST /facturi/emite — moneda inexistenta", "POST",
         "/tenants/%d/facturi/emite" % F,
         {"linii": [linie_ok], "tert_nume": "Proba SRL", "tert_cui": "RO1234567897",
          "moneda": "XYZ"}, "moneda=XYZ (cu cod de partener completat)"),
        # ── #30 seria si numarul ────────────────────────────────────────────
        (30, "PUT /facturi/numerotare — corp gol", "PUT",
         "/tenants/%d/facturi/numerotare" % F, {}, "corp JSON gol (nimic de setat)"),
        (30, "PUT /facturi/numerotare — numar de start negativ", "PUT",
         "/tenants/%d/facturi/numerotare" % F, {"numar_start": -5}, "numar_start=-5"),
        (30, "PUT /facturi/numerotare — numar de start deja folosit", "PUT",
         "/tenants/%d/facturi/numerotare" % F, {"numar_start": 100},
         "numar_start=100 (seria a ajuns la 149; ar produce numere duplicate)"),
        (30, "PUT /facturi/numerotare — serie goala", "PUT",
         "/tenants/%d/facturi/numerotare" % F, {"serie": "   "}, "serie=\"   \""),
        # ── #31 detaliile unei facturi ──────────────────────────────────────
        (31, "GET /facturi/{id} — factura inexistenta", "GET",
         "/tenants/%d/facturi/%d" % (F, INEXISTENT), None, "factura_id=999999"),
        # ── #34 trimiterea pe email ─────────────────────────────────────────
        (34, "POST /facturi/{id}/email — adresa fara @", "POST",
         "/tenants/%d/facturi/3/email" % F, {"email": "nu-e-o-adresa"}, "email=nu-e-o-adresa"),
        (34, "POST /facturi/{id}/email — factura inexistenta", "POST",
         "/tenants/%d/facturi/%d/email" % (F, INEXISTENT), {"email": "test@exemplu.test"},
         "factura_id=999999, adresa valida"),
        # ── #35 supapa de notificare ────────────────────────────────────────
        (35, "PUT /facturi/{id}/notificare — factura inexistenta", "PUT",
         "/tenants/%d/facturi/%d/notificare" % (F, INEXISTENT), {"stop": True},
         "factura_id=999999"),
        (35, "PUT /facturi/{id}/notificare — data amanarii ca text", "PUT",
         "/tenants/%d/facturi/%d/notificare" % (F, INEXISTENT),
         {"stop": False, "amanata_pana": "maine"}, "amanata_pana=\"maine\""),
    ]
    # ── #20 si #21: calea de API, cu cheie. Fara cheie nu se poate ajunge la ruta.
    p += [
        (20, "GET /api/v1/.../facturi — fara cheie", "GET",
         "/api/v1/firme/%d/facturi" % F, None, "antetul X-Api-Key absent"),
        (20, "GET /api/v1/.../facturi — cheie inventata", "GET",
         "/api/v1/firme/%d/facturi" % F, None, "X-Api-Key=cheie-inventata"),
        (20, "GET /api/v1/.../facturi — luna 13", "GET",
         "/api/v1/firme/%d/facturi?an=2026&luna=13" % F, None, "an=2026&luna=13"),
        (20, "GET /api/v1/.../facturi — firma altui cabinet", "GET",
         "/api/v1/firme/%d/facturi" % FIRMA_ALTUI_CABINET, None,
         "tenant_id=34061 (alt cabinet)"),
        (21, "POST /api/v1/.../facturi — corp gol", "POST",
         "/api/v1/firme/%d/facturi" % F, {}, "corp JSON gol"),
        (21, "POST /api/v1/.../facturi — fara nicio linie", "POST",
         "/api/v1/firme/%d/facturi" % F, {"tert_nume": "Proba SRL", "linii": []}, "linii=[]"),
        (21, "POST /api/v1/.../facturi — cota de TVA inexistenta", "POST",
         "/api/v1/firme/%d/facturi" % F,
         {"tert_nume": "Proba SRL", "tert_cui": "RO1234567897",
          "linii": [dict(linie_ok, cota_tva=99)]}, "cota_tva=99"),
    ]
    return p


#: Probele care merg pe calea de API publica: cheie in loc de token. Numele lor spune singur ce
#: cheie primesc — `fara cheie` niciuna, `cheie inventata` una care nu exista, restul cea reala.
CU_CHEIE_API = "/api/v1/"


FARA_TOKEN = {"GET /control-fiscal — fara token", "GET /supervizor — fara token"}
CU_CLIENT = {"GET /termene — cu rol CLIENT"}


def _tipar(nr, eticheta, introdus, cod, corp):
    print("=" * 100)
    print("#%s  %s" % (nr, eticheta))
    print("    introdus: %s" % introdus)
    print("    HTTP %s" % cod)
    print("    corp: %s" % corp[:1500])


def _ruleaza_T02(tok):
    """LOTUL 2. Doua lucruri in plus fata de bucla obisnuita, amandoua pentru ca proba sa nu lase
    portofoliul schimbat (capcana 9): numerotarea firmei se citeste inainte si se pune la loc in
    `finally`, iar cheia de API se creeaza si se sterge tot aici. Cheia se face prin LANTUL
    APLICATIEI (`POST /cabinet/api-chei`), nu cu un INSERT — regula 3."""
    _c, numerotare_initiala = cere("GET", "/tenants/%d/facturi/numerotare" % FIRMA, None, tok)
    print("NUMEROTAREA DINAINTE (se pune la loc in finally): HTTP %s %s" % (_c, numerotare_initiala))
    cod, corp = cere("POST", "/cabinet/api-chei", {"nume": "proba lot 2"}, tok)
    if cod != 200:
        raise SystemExit("nu s-a putut emite cheia de API: HTTP %s %s" % (cod, corp))
    cheie = json.loads(corp)
    print("CHEIE DE API emisa pentru proba: id=%s prefix=%s" % (cheie["id"], cheie["prefix"]))
    out = []
    try:
        for nr, eticheta, metoda, cale, payload, introdus in probe_T02():
            antete, t = None, tok
            if CU_CHEIE_API in cale:
                t = None
                if "fara cheie" in eticheta:
                    antete = None
                elif "cheie inventata" in eticheta:
                    antete = {"X-Api-Key": "ick_cheie-care-nu-exista"}
                else:
                    antete = {"X-Api-Key": cheie["cheie"]}
            cod, corp = cere(metoda, cale, payload, t, antete=antete)
            out.append({"nr": nr, "eticheta": eticheta, "metoda": metoda, "cale": cale,
                        "introdus": introdus, "cod": cod, "corp": corp})
            _tipar(nr, eticheta, introdus, cod, corp)
    finally:
        print("=" * 100)
        try:
            # Cheile sunt cele pe care le INTOARCE ruta (`serie`, `urmator_numar`), nu numele
            # coloanelor din `firma_profil`. Prima forma le confunda, trimitea doua `None`,
            # primea „nimic de setat" — si lasa firma cu seria stearsa de o proba.
            n0 = json.loads(numerotare_initiala)
            cod, corp = cere("PUT", "/tenants/%d/facturi/numerotare" % FIRMA,
                             {"serie": n0.get("serie"),
                              "numar_start": n0.get("urmator_numar")}, tok)
            print("NUMEROTAREA PUSA LA LOC: HTTP %s %s" % (cod, corp))
            _c, acum = cere("GET", "/tenants/%d/facturi/numerotare" % FIRMA, None, tok)
            print("NUMEROTAREA DE ACUM:     HTTP %s %s" % (_c, acum))
            # Nu „am trimis PUT-ul", ci „starea e cea de dinainte". Un `finally` care raporteaza
            # ca a incercat, nu ca a reusit, e cum s-a pierdut seria la prima trecere.
            if json.loads(acum) != n0:
                print("ATENTIE: numerotarea NU e cea de dinainte. Era %s, e %s." % (n0, acum))
        except Exception as ex:
            print("NUMEROTAREA N-A PUTUT FI PUSA LA LOC: %r — se reface cu mana" % (ex,))
        cod, corp = cere("DELETE", "/cabinet/api-chei/%d" % cheie["id"], None, tok)
        print("CHEIA REVOCATA: HTTP %s %s" % (cod, corp))
        _sterge_cheia(cheie["id"])
    return out


def _sterge_cheia(kid):
    """Revocarea lasa randul in `public.api_chei` (`activ=false`). Portofoliul avea ZERO chei
    inainte de proba si ramane cu zero: randul se sterge, si se spune ca s-a sters."""
    from core import db
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM public.api_chei WHERE id=%s", (kid,))
            n = cur.rowcount
        conn.commit()
    print("RANDUL CHEII STERS din public.api_chei: %d" % n)


def ruleaza(lot):
    tok = token(EMAIL)
    tok_client = token(EMAIL_CLIENT)
    if lot == "T02":
        return _ruleaza_T02(tok)
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
        _tipar(nr, eticheta, introdus, cod, corp)
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
