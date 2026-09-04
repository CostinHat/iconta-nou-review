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
    ./venv/bin/python frontend_test/proba_verificare_functionalitati.py T05
    ./venv/bin/python frontend_test/proba_verificare_functionalitati.py T03T04
    ./venv/bin/python frontend_test/proba_verificare_functionalitati.py ACHIZITII
    ./venv/bin/python frontend_test/proba_verificare_functionalitati.py T07T09T10
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


#: LOTUL 8 — corpul gol, pe toate caile care primesc unul. Aceeasi proba de deschidere ca la lotul
#: 7, unde din 28 de cai sase au cazut cu `500`.
_CORP_GOL_L8 = [
    (240, "POST", "/tenants/%d/d390-clasificare/manual"),
    (242, "PUT", "/tenants/%d/d390-clasificare/reclasificare"),
    (245, "POST", "/tenants/%d/registre-art321/cumparari"),
    (246, "POST", "/tenants/%d/vanzare-ic"),
    (253, "POST", "/tenants/%d/export-extracomunitar"),
    (256, "POST", "/tenants/%d/vanzare-agricultor"),
    (257, "POST", "/tenants/%d/vanzare-aur-investitii"),
    (258, "POST", "/tenants/%d/vanzare-marja"),
    (259, "POST", "/tenants/%d/vanzare-marja-turism"),
    (260, "POST", "/tenants/%d/decontare-valuta"),
    (261, "POST", "/tenants/%d/reevaluare-valuta"),
    (263, "POST", "/tenants/%d/d300-manual"),
    (266, "POST", "/tenants/%d/d301-operatiuni"),
    (269, "POST", "/tenants/%d/registru-evidenta-fiscala"),
    (271, "POST", "/tenants/%d/rip/import-banca"),
    (272, "POST", "/tenants/%d/rip/import-casa"),
    (273, "POST", "/tenants/%d/rip/operatiuni"),
    (277, "POST", "/tenants/%d/facturi/export-saga"),
    (278, "POST", "/tenants/%d/facturi/export-winmentor"),
    (284, "POST", "/tenants/%d/centre-cost"),
    (292, "POST", "/tenants/%d/rapoarte-salvate"),
]

#: Subiecte inexistente.
_INEXISTENT_L8 = [
    (241, "DELETE", "/tenants/%d/d390-clasificare/manual/999999", None),
    (267, "DELETE", "/tenants/%d/d301-operatiuni/999999", None),
    (287, "PUT", "/tenants/%d/centre-cost/999999", {"denumire": "X"}),
    (288, "PUT", "/tenants/%d/centre-cost/999999/buget", {"buget": 1000}),
]


def probe_LOT8():
    """LOTUL 8 — T28…T34, 43 de unitati in sapte trasee."""
    F = FIRMA
    p = []
    for nr, met, cale in _CORP_GOL_L8:
        p.append((nr, "%s %s — corp gol" % (met, cale.split("/")[-1]), met, cale % F, {},
                  "corp JSON gol"))
    for nr, met, cale, corp in _INEXISTENT_L8:
        p.append((nr, "%s %s — subiect inexistent" % (met, cale.split("/")[-2]), met, cale % F,
                  corp, "id=999999"))
    p += [
        # ── T28 operatiunile intracomunitare ─────────────────────────────────
        (239, "GET /d390-clasificare — luna 13", "GET",
         "/tenants/%d/d390-clasificare?an=2026&luna=13" % F, None, "luna=13"),
        (243, "GET /intrastat-praguri — an 1900", "GET",
         "/tenants/%d/intrastat-praguri?an=1900" % F, None, "an=1900"),
        (244, "GET /registre-art321/{fel} — fel inexistent", "GET",
         "/tenants/%d/registre-art321/ceva-ce-nu-exista" % F, None, "fel=ceva-ce-nu-exista"),
        (248, "GET /verifica-vies — cod TVA care nu e cod TVA", "GET",
         "/tenants/%d/verifica-vies?cod=NU-E-UN-COD" % F, None, "cod=NU-E-UN-COD"),
        (246, "POST /vanzare-ic — cota inexistenta", "POST", "/tenants/%d/vanzare-ic" % F,
         {"data": "2026-09-04", "valoare": 1000, "cota": 99, "tip": "bunuri",
          "cod_tva_client": "DE123456789", "numar": "V-1"}, "cota=99"),
        # ── T29 regimurile speciale ──────────────────────────────────────────
        (255, "GET /jurnal-marja — luna 13", "GET",
         "/tenants/%d/jurnal-marja?an=2026&luna=13" % F, None, "luna=13"),
        (258, "POST /vanzare-marja — pret de vanzare sub cel de cumparare", "POST",
         "/tenants/%d/vanzare-marja" % F,
         {"data": "2026-09-04", "pret_vanzare": 100, "pret_cumparare": 500, "cota": 21},
         "pret_vanzare < pret_cumparare"),
        # ── T30 valuta ───────────────────────────────────────────────────────
        (260, "POST /decontare-valuta — moneda inexistenta", "POST",
         "/tenants/%d/decontare-valuta" % F,
         {"data": "2026-09-04", "moneda": "XYZ", "valoare_valuta": 100, "curs_evidenta": 5,
          "tip": "creanta", "cont_tert": "4111"}, "moneda=XYZ"),
        # ── T31 completarile manuale ─────────────────────────────────────────
        (262, "GET /d300-manual — luna 13", "GET",
         "/tenants/%d/d300-manual?an=2026&luna=13" % F, None, "luna=13"),
        (263, "POST /d300-manual — rand de declaratie inexistent", "POST",
         "/tenants/%d/d300-manual" % F,
         {"an": 2026, "luna": 8, "rand": "R999", "valoare": 100}, "rand=R999"),
        (265, "GET /d301-operatiuni — luna 13", "GET",
         "/tenants/%d/d301-operatiuni?an=2026&luna=13" % F, None, "luna=13"),
        (268, "GET /registru-evidenta-fiscala — an 1900", "GET",
         "/tenants/%d/registru-evidenta-fiscala?an=1900" % F, None, "an=1900"),
        # ── T32 partida simpla ───────────────────────────────────────────────
        (270, "GET /rip/d212/{an} — an 1900", "GET", "/tenants/%d/rip/d212/1900" % F, None,
         "an=1900"),
        (276, "GET /rip/registru — luna 13", "GET",
         "/tenants/%d/rip/registru?an=2026&luna=13" % F, None, "luna=13"),
        (273, "POST /rip/operatiuni — suma negativa", "POST", "/tenants/%d/rip/operatiuni" % F,
         {"data": "2026-09-04", "fel": "incasare", "suma": -100}, "suma=-100"),
        # ── T33 exportul contabil ────────────────────────────────────────────
        (277, "POST /facturi/export-saga — luna 13", "POST",
         "/tenants/%d/facturi/export-saga" % F, {"an": 2026, "luna": 13}, "luna=13"),
        (278, "POST /facturi/export-winmentor — luna 13", "POST",
         "/tenants/%d/facturi/export-winmentor" % F, {"an": 2026, "luna": 13}, "luna=13"),
        # ── T34 rapoartele ───────────────────────────────────────────────────
        (281, "GET /api/v1/.../kpi — luna 13", "GET",
         "/api/v1/firme/%d/kpi?an=2026&luna=13" % F, None, "luna=13"),
        (282, "GET /cabinet/consolidare — luna 13", "GET",
         "/cabinet/consolidare?an=2026&luna=13", None, "luna=13"),
        # `#283` n-are `an` in semnatura; se probeaza filtrul pe care il ARE.
        (283, "GET /centre-cost — filtru `doar_active` care nu e da/nu", "GET",
         "/tenants/%d/centre-cost?doar_active=poate" % F, None, "doar_active=poate"),
        (285, "GET /centre-cost/raport — sfarsit inaintea inceputului", "GET",
         "/tenants/%d/centre-cost/raport?de=2026-09-30&pana=2026-09-01" % F, None, "pana < de"),
        # `#286` are `an`, nu `luna`.
        (286, "GET /centre-cost/varianta — an 1900", "GET",
         "/tenants/%d/centre-cost/varianta?an=1900" % F, None, "an=1900"),
        # `#289` primeste un INTERVAL (`de`/`pana`), nu an/luna.
        (289, "GET /rapoarte-comerciale — sfarsit inaintea inceputului", "GET",
         "/tenants/%d/rapoarte-comerciale?de=2026-09-30&pana=2026-09-01" % F, None,
         "pana < de"),
        (290, "GET /rapoarte-comerciale/fisa — partener inexistent", "GET",
         "/tenants/%d/rapoarte-comerciale/fisa?partener=NU-EXISTA&an=2026" % F, None,
         "partener=NU-EXISTA"),
        (291, "GET /rapoarte-salvate — fara parametri", "GET",
         "/tenants/%d/rapoarte-salvate" % F, None, "niciun parametru"),
    ]
    return p


#: LOTUL 7 — corpul gol, pe toate caile care primesc unul. E proba cea mai ieftina si cea care
#: scoate contractul la iveala: ce raspunde o ruta cand nu i se da nimic spune ce considera ea
#: obligatoriu. (nr, metoda, cale, are_tenant)
_CORP_GOL_L7 = [
    (165, "POST", "/tenants/%d/contracte/genereaza", True),
    (167, "POST", "/tenants/%d/contracte/sabloane", True),
    (169, "POST", "/tenants/%d/prapastie-salariu", True),
    (170, "POST", "/tenants/%d/reges-config", True),
    (172, "POST", "/tenants/%d/reges-trimite-salariat", True),
    (174, "POST", "/tenants/%d/salariati", True),
    (180, "POST", "/tenants/%d/pontaj/confirma", True),
    (184, "POST", "/tenants/%d/plata-salarii-fisier", True),
    (189, "POST", "/tenants/%d/chitante", True),
    (193, "PUT", "/tenants/%d/scadentar/opt-in", True),
    (200, "POST", "/tenants/%d/stocuri/descarcare", True),
    (201, "POST", "/tenants/%d/stocuri/iesire", True),
    (202, "POST", "/tenants/%d/stocuri/intrare", True),
    (204, "POST", "/tenants/%d/stocuri/reclasificare", True),
    (205, "POST", "/tenants/%d/stocuri/transfer", True),
    (207, "POST", "/tenants/%d/produse", True),
    (208, "POST", "/tenants/%d/produse/potriveste", True),
    (212, "POST", "/tenants/%d/retete", True),
    (213, "POST", "/tenants/%d/retete/descarca", True),
    (215, "POST", "/tenants/%d/amortizare", True),
    (217, "POST", "/tenants/%d/reevaluare-imobilizare", True),
    (227, "POST", "/tenants/%d/horeca/import-amef", True),
    (228, "POST", "/tenants/%d/horeca/raport-z", True),
    (230, "PUT", "/tenants/%d/woocommerce/config", True),
    (233, "POST", "/tenants/%d/registratura", True),
    (234, "POST", "/tenants/%d/etransport-xml", True),
    (235, "POST", "/tenants/%d/etransport/trimite", True),
    (218, "POST", "/portal/bon", False),
]

#: Subiecte inexistente: acelasi `999999` pe fiecare cale care are un id in ea.
_INEXISTENT_L7 = [
    (177, "PUT", "/tenants/%d/salariati/999999", {"nume": "X"}),
    (178, "POST", "/tenants/%d/salariati/999999/adeverinta", {}),
    (179, "PUT", "/tenants/%d/salariati/999999/beneficiu-lunar", {"suma": 100}),
    (181, "GET", "/tenants/%d/salariati/999999/pontaj?an=2026&luna=8", None),
    (182, "PUT", "/tenants/%d/salariati/999999/pontaj", {"an": 2026, "luna": 8, "zile": []}),
    (196, "POST", "/tenants/%d/stocuri/articole/999999/barcode", {"barcode": "123"}),
    (198, "POST", "/tenants/%d/stocuri/articole/999999/nivel-minim", {"nivel_minim": 5}),
    (210, "PUT", "/tenants/%d/produse/999999", {"denumire": "X"}),
    (223, "POST", "/tenants/%d/bonuri/999999/aproba", {}),
    (226, "POST", "/tenants/%d/bonuri/999999/stinge", {}),
]

#: Perioade imposibile, pe rutele de citire ale lotului.
#: CORECTAT dupa prima trecere: `#188` (chitante), `#194` (analitica) si `#173` (salariati) NU au
#: parametrii `an`/`luna` in semnatura — FastAPI lasa parametrii necunoscuti sa treaca, iar proba
#: masurase o intrebare pe care ruta n-o pusese niciodata. A patra proba oarba a campaniei. Raman
#: cele care CHIAR primesc o perioada.
_PERIOADA_L7 = [
    (185, "/tenants/%d/plata-salarii-preview", True),
    (232, "/tenants/%d/registratura", False),
]


def probe_LOT7():
    """LOTUL 7 — T15…T27, 49 de unitati in treisprezece trasee.

    **Corpul gol e proba de deschidere, nu una slaba:** ce raspunde o ruta cand nu primeste nimic
    arata ce considera ea obligatoriu — iar acolo unde raspunde `200`, intrebarea e daca a facut
    ceva fara sa i se ceara."""
    F = FIRMA
    p = []
    for nr, met, cale, cu_tenant in _CORP_GOL_L7:
        p.append((nr, "%s %s — corp gol" % (met, cale.split("/")[-1]), met,
                  (cale % F) if cu_tenant else cale, {}, "corp JSON gol"))
    for nr, met, cale, corp in _INEXISTENT_L7:
        p.append((nr, "%s %s — subiect inexistent" % (met, cale.split("/")[-1].split("?")[0]),
                  met, cale % F, corp, "id=999999"))
    for nr, cale, are_luna in _PERIOADA_L7:
        if are_luna:
            p.append((nr, "GET %s — luna 13" % cale.split("/")[-1], "GET",
                      (cale % F) + "?an=2026&luna=13", None, "luna=13"))
        else:
            p.append((nr, "GET %s — an 1900" % cale.split("/")[-1], "GET",
                      (cale % F) + "?an=1900", None, "an=1900"))
    p += [
        # ── T15 salariatul ───────────────────────────────────────────────────
        (164, "GET /cor — cautare cu sir gol", "GET", "/cor?q=", None, "q= (sir gol)"),
        (164, "GET /cor — cod COR inexistent", "GET", "/cor?q=999999", None, "q=999999"),
        # `#173` n-are `an` in semnatura; se probeaza filtrul pe care il ARE.
        (173, "GET /salariati — filtru `activ` care nu e da/nu", "GET",
         "/tenants/%d/salariati?activ=poate" % F, None, "activ=poate"),
        (174, "POST /salariati — CNP care nu trece cifra de control", "POST",
         "/tenants/%d/salariati" % F,
         {"nume": "Proba", "cnp": "1234567890123", "data_angajare": "2026-09-01",
          "salariu_brut": 5000}, "cnp=1234567890123 (cifra de control gresita)"),
        (174, "POST /salariati — salariu negativ", "POST", "/tenants/%d/salariati" % F,
         {"nume": "Proba", "cnp": "1850715410012", "data_angajare": "2026-09-01",
          "salariu_brut": -5000}, "salariu_brut=-5000"),
        # ── T16 pontajul ─────────────────────────────────────────────────────
        (183, "GET /util/zile-lucratoare — sfarsit inaintea inceputului", "GET",
         "/util/zile-lucratoare?start=2026-09-30&end=2026-09-01", None, "end < start"),
        (183, "GET /util/zile-lucratoare — date inexistente in calendar", "GET",
         "/util/zile-lucratoare?start=2026-02-31&end=2026-03-02", None, "start=2026-02-31"),
        (180, "POST /pontaj/confirma — luna 13", "POST", "/tenants/%d/pontaj/confirma" % F,
         {"an": 2026, "luna": 13}, "luna=13"),
        # ── T18 chitanta ─────────────────────────────────────────────────────
        (189, "POST /chitante — suma negativa", "POST", "/tenants/%d/chitante" % F,
         {"data": "2026-09-04", "suma": -100, "client": "Proba SRL"}, "suma=-100"),
        # ── T20 stocul ───────────────────────────────────────────────────────
        (202, "POST /stocuri/intrare — cantitate negativa", "POST",
         "/tenants/%d/stocuri/intrare" % F,
         {"data": "2026-09-04", "articol_id": 1, "cantitate": -5, "pret_unitar": 10},
         "cantitate=-5"),
        (201, "POST /stocuri/iesire — cantitate negativa", "POST",
         "/tenants/%d/stocuri/iesire" % F,
         {"data": "2026-09-04", "articol_id": 1, "cantitate": -5}, "cantitate=-5"),
        (205, "POST /stocuri/transfer — aceeasi locatie la plecare si la sosire", "POST",
         "/tenants/%d/stocuri/transfer" % F,
         {"data": "2026-09-04", "articol_id": 1, "cantitate": 1, "din": "DEP", "in": "DEP"},
         "din == in"),
        (203, "GET /stocuri/locatii — articol inexistent", "GET",
         "/tenants/%d/stocuri/locatii?articol_id=999999" % F, None, "articol_id=999999"),
        # ── T22 amortizarea ──────────────────────────────────────────────────
        # `#215` cere `an`/`luna` ca PARAMETRI, nu in corp: prima forma le trimitea in corp si
        # primea „an lipsește; luna lipsește" — proba masura alta intrebare.
        (215, "POST /amortizare — luna 13", "POST",
         "/tenants/%d/amortizare?an=2026&luna=13" % F, {}, "luna=13"),
        (217, "POST /reevaluare-imobilizare — valoare negativa", "POST",
         "/tenants/%d/reevaluare-imobilizare" % F,
         {"data": "2026-09-04", "mijloc_fix_id": 1, "valoare_noua": -1000},
         "valoare_noua=-1000"),
        # ── T23 bonul de la client ───────────────────────────────────────────
        # Cele trei rute de PORTAL cer rol CLIENT; cu tokenul de cabinet raspundeau „Alegeți
        # firma", adica se opreau la poarta de contexte, nu la bonul inexistent. Se probeaza cu
        # tokenul potrivit (v. `CU_CLIENT`).
        (219, "DELETE /portal/bon/{id} — bon inexistent · CLIENT", "DELETE",
         "/portal/bon/999999", None, "bon_id=999999"),
        (220, "POST /portal/bon/{id}/confirma — bon inexistent · CLIENT", "POST",
         "/portal/bon/999999/confirma", {}, "bon_id=999999"),
        (221, "GET /portal/bon/{id}/imagine/{n} — bon inexistent · CLIENT", "GET",
         "/portal/bon/999999/imagine/1", None, "bon_id=999999"),
        # ── T27 e-Transport ──────────────────────────────────────────────────
        (234, "POST /etransport-xml — cod de operatiune inexistent", "POST",
         "/tenants/%d/etransport-xml" % F,
         {"cod_operatiune": "ceva-ce-nu-exista", "data": "2026-09-04"},
         "cod_operatiune=ceva-ce-nu-exista"),
    ]
    return p


#: Rutele care primesc o PERIOADA: (nr, cale-sablon, are_luna).
_PERIOADA = [
    (105, "/tenants/%d/casa/registru", True),
    (106, "/tenants/%d/d406-active", False),
    (111, "/tenants/%d/facturi/perioada", True),
    (117, "/tenants/%d/perioade-blocate/istoric", True),
    (118, "/tenants/%d/categorie-marime", False),
    (120, "/tenants/%d/s1003-xml", False),
    (122, "/tenants/%d/s1005-xml", False),
]

#: Importurile care primesc `randuri` prin JSON. Clasa „import care goleste la intrare vida" a fost
#: inchisa in lotul 1b pe trei dintre ele; aici se probeaza CELELALTE, plus randul fara campuri.
_IMPORT_JSON = [
    (146, "/tenants/%d/articole-import"),
    (155, "/tenants/%d/retete-import"),
    (158, "/tenants/%d/salariati-import"),
    (161, "/tenants/%d/solduri"),
]

#: Incarcarile de fisier (multipart). Proba: un `.txt` cu o linie de proza — nici CSV, nici XLSX.
_INCARCARI = [
    (94, "/tenants/%d/banca/parse-extras"),
    (97, "/tenants/%d/banca/reconciliere/import"),
    (147, "/tenants/%d/articole-import/incarca"),
    (149, "/tenants/%d/asociati-import/incarca"),
    (151, "/tenants/%d/mijloace-fixe-import/incarca"),
    (154, "/tenants/%d/parteneri/incarca"),
    (156, "/tenants/%d/retete-import/incarca"),
    (157, "/tenants/%d/rip-import/incarca"),
    (159, "/tenants/%d/salariati-import/incarca"),
    (162, "/tenants/%d/solduri/incarca"),
]

#: Incarcarile de la nivel de CABINET (fara tenant in cale).
_INCARCARI_CABINET = [(133, "/migrare/fisier"), (135, "/migrare/incarca")]


def probe_LOT6():
    """LOTUL 6 — opt trasee, 45 de unitati. V. antetul modulului."""
    F = FIRMA
    p = []
    for nr, cale, are_luna in _PERIOADA:
        c = cale % F
        if are_luna:
            p.append((nr, "GET %s — luna 13" % cale.split("/")[-1], "GET",
                      c + "?an=2026&luna=13", None, "luna=13"))
        p.append((nr, "GET %s — an 1900" % cale.split("/")[-1], "GET",
                  c + ("?an=1900&luna=1" if are_luna else "?an=1900"), None, "an=1900"))
    for nr, cale in _IMPORT_JSON:
        p.append((nr, "POST %s — randuri goale" % cale.split("/")[-1], "POST", cale % F,
                  {"randuri": []}, "randuri=[]"))
        p.append((nr, "POST %s — rand fara campuri" % cale.split("/")[-1], "POST", cale % F,
                  {"randuri": [{}]}, "randuri=[{}]"))
    p += [
        # ── T-SPV ────────────────────────────────────────────────────────────
        (2, "GET /spv/autorizare — fara parametri", "GET", "/spv/autorizare", None,
         "niciun parametru"),
        (3, "GET /spv/stare — pe un cont fara SPV", "GET", "/spv/stare", None, "cont fara SPV"),
        (1, "GET /anaf/oauth/callback — cod de autorizare inventat", "GET",
         "/anaf/oauth/callback?code=cod-inventat&state=stare-inventata", None,
         "code=cod-inventat"),
        # ── T07 ──────────────────────────────────────────────────────────────
        (95, "GET /banca/reconciliere — status inexistent", "GET",
         "/tenants/%d/banca/reconciliere?status=INEXISTENT" % F, None, "status=INEXISTENT"),
        (98, "POST /banca/reconciliere/{id}/conteaza — linie inexistenta", "POST",
         "/tenants/%d/banca/reconciliere/%d/conteaza" % (F, INEXISTENT), {}, "linie_id=999999"),
        # ── T09 ──────────────────────────────────────────────────────────────
        (103, "POST /casa/operatiuni — corp gol", "POST", "/tenants/%d/casa/operatiuni" % F, {},
         "corp JSON gol"),
        (103, "POST /casa/operatiuni — categorie inexistenta", "POST",
         "/tenants/%d/casa/operatiuni" % F,
         {"data": "2026-09-04", "categorie": "ceva-ce-nu-exista", "suma": 100},
         "categorie=ceva-ce-nu-exista"),
        (103, "POST /casa/operatiuni — suma negativa", "POST",
         "/tenants/%d/casa/operatiuni" % F,
         {"data": "2026-09-04", "categorie": "incasare_client", "suma": -100}, "suma=-100"),
        (103, "POST /casa/operatiuni — data inexistenta in calendar", "POST",
         "/tenants/%d/casa/operatiuni" % F,
         {"data": "2026-02-31", "categorie": "incasare_client", "suma": 100},
         "data=2026-02-31"),
        # ── T10 ──────────────────────────────────────────────────────────────
        (107, "GET /d406-stocuri — date inexistente in calendar", "GET",
         "/tenants/%d/d406-stocuri?data_start=2026-02-31&data_end=2026-03-02&cui=RO1234567897" % F,
         None, "data_start=2026-02-31"),
        (107, "GET /d406-stocuri — sfarsit inaintea inceputului", "GET",
         "/tenants/%d/d406-stocuri?data_start=2026-09-30&data_end=2026-09-01&cui=RO1234567897" % F,
         None, "data_end < data_start"),
        (109, "POST /stocuri/inventar — corp gol", "POST", "/tenants/%d/stocuri/inventar" % F, {},
         "corp JSON gol"),
        (109, "POST /stocuri/inventar — articol inexistent", "POST",
         "/tenants/%d/stocuri/inventar" % F,
         {"data": "2026-09-04", "linii": [{"articol_id": INEXISTENT, "faptic": 5}]},
         "articol_id=999999"),
        (109, "POST /stocuri/inventar — cantitate faptica negativa", "POST",
         "/tenants/%d/stocuri/inventar" % F,
         {"data": "2026-09-04", "linii": [{"articol_id": 1, "faptic": -5}]}, "faptic=-5"),
        # ── T11 inchiderea lunii ─────────────────────────────────────────────
        (112, "POST /facturi/perioada/confirma — corp gol", "POST",
         "/tenants/%d/facturi/perioada/confirma" % F, {}, "corp JSON gol"),
        (112, "POST /facturi/perioada/confirma — luna 13", "POST",
         "/tenants/%d/facturi/perioada/confirma" % F, {"an": 2026, "luna": 13}, "luna=13"),
        (113, "POST /facturi/perioada/redeschide — luna 13", "POST",
         "/tenants/%d/facturi/perioada/redeschide" % F, {"an": 2026, "luna": 13}, "luna=13"),
        (116, "POST /perioade-blocate — corp gol", "POST",
         "/tenants/%d/perioade-blocate" % F, {}, "corp JSON gol"),
        (116, "POST /perioade-blocate — luna 13", "POST", "/tenants/%d/perioade-blocate" % F,
         {"an": 2026, "luna": 13, "motiv": "proba"}, "luna=13"),
        (116, "POST /perioade-blocate — motiv gol", "POST", "/tenants/%d/perioade-blocate" % F,
         {"an": 2026, "luna": 8, "motiv": ""}, "motiv=\"\""),
        (114, "DELETE /perioade-blocate — perioada neblocata", "DELETE",
         "/tenants/%d/perioade-blocate?an=1995&luna=1" % F, None, "an=1995 (perioada neblocata)"),
        # ── T12 inchiderea anului ────────────────────────────────────────────
        (119, "POST /s1003-valideaza — an 1900", "POST",
         "/tenants/%d/s1003-valideaza?an=1900" % F, {}, "an=1900"),
        (121, "POST /s1005-valideaza — an 1900", "POST",
         "/tenants/%d/s1005-valideaza?an=1900" % F, {}, "an=1900"),
        # ── T13 trecerea de regim ────────────────────────────────────────────
        (126, "POST /firma-profil/date — corp gol", "POST",
         "/tenants/%d/firma-profil/date" % F, {}, "corp JSON gol"),
        (126, "POST /firma-profil/date — CUI care nu trece cifra de control", "POST",
         "/tenants/%d/firma-profil/date" % F, {"cui": "RO1234567890"},
         "cui=RO1234567890 (cifra de control gresita)"),
        (127, "POST /firma-profil/model — culoare care nu e culoare", "POST",
         "/tenants/%d/firma-profil/model" % F, {"culoare": "ceva-ce-nu-e-culoare"},
         "culoare=ceva-ce-nu-e-culoare"),
        (128, "POST /firma-profil/regim-tva — regim inexistent", "POST",
         "/tenants/%d/firma-profil/regim-tva" % F, {"regim": "ceva-ce-nu-exista"},
         "regim=ceva-ce-nu-exista"),
        (130, "POST /vector — corp gol", "POST", "/tenants/%d/vector" % F, {}, "corp JSON gol"),
        (130, "POST /vector — periodicitate inexistenta", "POST", "/tenants/%d/vector" % F,
         {"tip_decont": "ceva-ce-nu-exista"}, "tip_decont=ceva-ce-nu-exista"),
        # ── T14 preluarea unei firme ─────────────────────────────────────────
        (134, "POST /migrare/importa — corp gol", "POST", "/migrare/importa", {}, "corp JSON gol"),
        (143, "POST /migrare/status — corp gol", "POST", "/migrare/status", {}, "corp JSON gol"),
        (144, "GET /migrare/straturi — tip de firma inexistent", "GET",
         "/migrare/straturi?tip_firma=ceva-ce-nu-exista", None, "tip_firma=ceva-ce-nu-exista"),
        (145, "POST /migrare/valideaza — corp gol", "POST", "/migrare/valideaza", {},
         "corp JSON gol"),
    ]
    # incarcarile de fisier: acelasi `.txt` care nu e tabel, pe toate douasprezece
    for nr, cale in _INCARCARI:
        p.append((nr, "POST %s — fisier text in loc de tabel" % cale.split("/")[-2:][0], "POST",
                  cale % F, "FISIER", "fisier .txt cu o linie de proza"))
    for nr, cale in _INCARCARI_CABINET:
        p.append((nr, "POST %s — fisier text in loc de tabel" % cale, "POST", cale, "FISIER",
                  "fisier .txt cu o linie de proza"))
    return p


def probe_T07T09T10():
    """LOTUL 6 — extrasul bancar (T07), casa (T09), inventarierea (T10). Noua unitati in
    perimetrul etapei 1: `#94`, `#95`, `#97`, `#98` · `#103`, `#105` · `#106`, `#107`, `#109`.

    **Corp de baza VALID, minus o singura abatere** — regula scrisa la lotul 5, dupa patru grupuri
    de probe oarbe."""
    F = FIRMA
    casa_ok = {"data": "2026-09-04", "categorie": "incasare_client", "suma": 100,
               "document": "CH-1"}
    return [
        # ── T07 extrasul bancar ──────────────────────────────────────────────
        (95, "GET /banca/reconciliere — status inexistent", "GET",
         "/tenants/%d/banca/reconciliere?status=INEXISTENT" % F, None, "status=INEXISTENT"),
        (98, "POST /banca/reconciliere/{id}/conteaza — linie inexistenta", "POST",
         "/tenants/%d/banca/reconciliere/%d/conteaza" % (F, INEXISTENT), {},
         "linie_id=999999"),
        (98, "POST /banca/reconciliere/{id}/conteaza — cont inexistent", "POST",
         "/tenants/%d/banca/reconciliere/%d/conteaza" % (F, INEXISTENT), {"cont": "9999"},
         "cont=9999"),
        # ── T09 casa ─────────────────────────────────────────────────────────
        (103, "POST /casa/operatiuni — corp gol", "POST", "/tenants/%d/casa/operatiuni" % F, {},
         "corp JSON gol"),
        (103, "POST /casa/operatiuni — categorie inexistenta", "POST",
         "/tenants/%d/casa/operatiuni" % F, dict(casa_ok, categorie="ceva-ce-nu-exista"),
         "categorie=ceva-ce-nu-exista"),
        (103, "POST /casa/operatiuni — suma negativa", "POST",
         "/tenants/%d/casa/operatiuni" % F, dict(casa_ok, suma=-100), "suma=-100"),
        (103, "POST /casa/operatiuni — data inexistenta in calendar", "POST",
         "/tenants/%d/casa/operatiuni" % F, dict(casa_ok, data="2026-02-31"),
         "data=2026-02-31 (31 februarie)"),
        (105, "GET /casa/registru — luna 13", "GET",
         "/tenants/%d/casa/registru?an=2026&luna=13" % F, None, "luna=13"),
        (105, "GET /casa/registru — an 1900", "GET",
         "/tenants/%d/casa/registru?an=1900&luna=1" % F, None, "an=1900"),
        # ── T10 inventarierea ────────────────────────────────────────────────
        (106, "GET /d406-active — an 1900", "GET",
         "/tenants/%d/d406-active?an=1900" % F, None, "an=1900"),
        (107, "GET /d406-stocuri — date inexistente in calendar", "GET",
         "/tenants/%d/d406-stocuri?data_start=2026-02-31&data_end=2026-03-02&cui=RO1234567897" % F,
         None, "data_start=2026-02-31"),
        (107, "GET /d406-stocuri — sfarsit inaintea inceputului", "GET",
         "/tenants/%d/d406-stocuri?data_start=2026-09-30&data_end=2026-09-01&cui=RO1234567897" % F,
         None, "data_end < data_start"),
        (107, "GET /d406-stocuri — CUI care nu trece cifra de control", "GET",
         "/tenants/%d/d406-stocuri?data_start=2026-09-01&data_end=2026-09-30&cui=RO1234567890" % F,
         None, "cui=RO1234567890 (cifra de control gresita)"),
        (109, "POST /stocuri/inventar — corp gol", "POST",
         "/tenants/%d/stocuri/inventar" % F, {}, "corp JSON gol"),
        (109, "POST /stocuri/inventar — articol inexistent", "POST",
         "/tenants/%d/stocuri/inventar" % F,
         {"data": "2026-09-04", "linii": [{"articol_id": INEXISTENT, "faptic": 5}]},
         "articol_id=999999"),
        (109, "POST /stocuri/inventar — cantitate faptica negativa", "POST",
         "/tenants/%d/stocuri/inventar" % F,
         {"data": "2026-09-04", "linii": [{"articol_id": 1, "faptic": -5}]}, "faptic=-5"),
    ]


def probe_ACHIZITII():
    """LOTUL 5 — facturile PRIMITE si achizitiile. **Nu e un traseu, e o suprafata**: cerand-o,
    Costin a scris *„oricare i-ar fi numarul"*, iar cautarea in inventar a aratat de ce — nu exista
    un traseu cu numele asta. Ce exista e suprafata prin care intra TVA-ul DEDUCTIBIL, imprastiata
    in patru trasee:

      * **T06** — factura primita prin e-Factura: `#88` respinge, `#89` valideaza, `#92` import
      * **T08** — receptia: `#101` lista NIR, `#102` NIR nou
      * **T28** — achizitia intracomunitara: `#238`
      * **T29** — regimurile speciale pe achizitii: `#249` agricultor, `#250` necorporala,
        `#251` de la neinregistrat, `#252` taxare inversa, `#254` import extracomunitar

    Unsprezece unitati. Se adauga o **a doua trecere** pe `#23` (`POST /facturi`), pe directia
    PRIMITA — probata in lotul 2 numai pe emisa —, fiindca ea e chiar poarta prin care o factura de
    achizitie ajunge in evidenta. Nu se numara ca unitate noua; se scrie ca a doua trecere.

    **Ce se lasa in urma:** toate probele sunt intrari incomplete sau imposibile. Daca vreuna trece,
    se sterge si se spune."""
    F = FIRMA
    linie_ok = {"descriere": "marfa", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21}
    # NIR-ul are ALTE nume de camp decat factura: `denumire` si `pret_achizitie`. Prima forma a
    # probelor trimitea numele de la factura, deci se oprea la „completeaza articolele" si nu
    # ajungea niciodata la data, la cantitate sau la cota.
    art_ok = {"denumire": "marfa", "cantitate": 1, "pret_achizitie": 100, "cota_tva": 21}
    # Corpuri de baza VALIDE; fiecare proba schimba UN singur camp.
    ic_ok = {"data": "2026-09-04", "valoare": 1000, "cont_destinatie": "371", "tip": "bunuri",
             "cota": 21, "cod_tva_furnizor": "DE123456789", "numar": "F-IC-1"}
    ti_ok = {"data": "2026-09-04", "categorie": "cereale", "valoare": 1000,
             "cont_destinatie": "371", "cota": 21, "furnizor_cui": "RO1234567897"}
    ext_ok = {"data": "2026-09-04", "valoare_vamala": 1000, "cota": 21,
              "cont_destinatie": "371"}
    p = [
        # ── #88 · #89 factura primita prin e-Factura ─────────────────────────
        (88, "POST /facturi-primite/{id}/respinge — element inexistent", "POST",
         "/tenants/%d/facturi-primite/%d/respinge" % (F, INEXISTENT), {"motiv": "proba"},
         "primita_id=999999"),
        (88, "POST /facturi-primite/{id}/respinge — motiv gol", "POST",
         "/tenants/%d/facturi-primite/%d/respinge" % (F, INEXISTENT), {"motiv": ""},
         "motiv=\"\" (sir gol)"),
        (89, "POST /facturi-primite/{id}/valideaza — element inexistent", "POST",
         "/tenants/%d/facturi-primite/%d/valideaza" % (F, INEXISTENT), {},
         "primita_id=999999"),
        # ── #101 · #102 receptia ─────────────────────────────────────────────
        (101, "GET /stocuri/nir — luna 13", "GET",
         "/tenants/%d/stocuri/nir?an=2026&luna=13" % F, None, "luna=13"),
        (101, "GET /stocuri/nir — an 1900", "GET",
         "/tenants/%d/stocuri/nir?an=1900&luna=1" % F, None, "an=1900"),
        (102, "POST /stocuri/nir — corp gol", "POST", "/tenants/%d/stocuri/nir" % F, {},
         "corp JSON gol"),
        (102, "POST /stocuri/nir — data inexistenta in calendar", "POST",
         "/tenants/%d/stocuri/nir" % F,
         {"data": "2026-02-31", "furnizor": "Proba SRL", "cota": 21, "linii": [art_ok]},
         "data=2026-02-31 (31 februarie)"),
        (102, "POST /stocuri/nir — cantitate negativa", "POST", "/tenants/%d/stocuri/nir" % F,
         {"data": "2026-09-04", "furnizor": "Proba SRL",
          "linii": [dict(art_ok, cantitate=-5)]}, "cantitate=-5"),
        (102, "POST /stocuri/nir — cota de TVA inexistenta", "POST",
         "/tenants/%d/stocuri/nir" % F,
         {"data": "2026-09-04", "furnizor": "Proba SRL", "cota": 99,
          "linii": [dict(art_ok, cota_tva=99)]}, "cota_tva=99 (si cota=99 pe nota)"),
        # ── #238 achizitia intracomunitara ───────────────────────────────────
        (238, "POST /achizitie-ic — corp gol", "POST", "/tenants/%d/achizitie-ic" % F, {},
         "corp JSON gol"),
        (238, "POST /achizitie-ic — data ca text", "POST", "/tenants/%d/achizitie-ic" % F,
         dict(ic_ok, data="ieri"), "data=\"ieri\""),
        (238, "POST /achizitie-ic — valoare negativa", "POST", "/tenants/%d/achizitie-ic" % F,
         dict(ic_ok, valoare=-1000), "valoare=-1000"),
        (238, "POST /achizitie-ic — tip inexistent", "POST", "/tenants/%d/achizitie-ic" % F,
         dict(ic_ok, tip="altceva"), "tip=altceva"),
        (238, "POST /achizitie-ic — cota de TVA inexistenta", "POST",
         "/tenants/%d/achizitie-ic" % F,
         dict(ic_ok, cota=99), "cota=99"),
        (238, "POST /achizitie-ic — cont inexistent in plan", "POST",
         "/tenants/%d/achizitie-ic" % F,
         dict(ic_ok, cont_destinatie="9999"), "cont_destinatie=9999"),
        # ── #249 achizitia de la agricultor ──────────────────────────────────
        (249, "POST /achizitie-agricultor — corp gol", "POST",
         "/tenants/%d/achizitie-agricultor" % F, {}, "corp JSON gol"),
        (249, "POST /achizitie-agricultor — valoare negativa", "POST",
         "/tenants/%d/achizitie-agricultor" % F,
         {"data": "2026-09-04", "valoare": -500, "cont_cheltuiala": "601",
          "agricultor_in_registru": True}, "valoare=-500"),
        # ── #250 achizitia necorporala ───────────────────────────────────────
        (250, "POST /achizitie-necorporala — corp gol", "POST",
         "/tenants/%d/achizitie-necorporala" % F, {}, "corp JSON gol"),
        (250, "POST /achizitie-necorporala — tip inexistent", "POST",
         "/tenants/%d/achizitie-necorporala" % F,
         {"data": "2026-09-04", "denumire": "Proba", "valoare": 1000, "tip": "altceva"},
         "tip=altceva"),
        # ── #251 achizitia de la neinregistrat ───────────────────────────────
        (251, "POST /achizitie-neinregistrat — corp gol", "POST",
         "/tenants/%d/achizitie-neinregistrat" % F, {}, "corp JSON gol"),
        (251, "POST /achizitie-neinregistrat — furnizor gol", "POST",
         "/tenants/%d/achizitie-neinregistrat" % F,
         {"data": "2026-09-04", "furnizor_nume": "", "valoare": 500, "cont_cheltuiala": "601"},
         "furnizor_nume=\"\""),
        # ── #252 taxarea inversa ─────────────────────────────────────────────
        (252, "POST /achizitie-taxare-inversa — corp gol", "POST",
         "/tenants/%d/achizitie-taxare-inversa" % F, {}, "corp JSON gol"),
        (252, "POST /achizitie-taxare-inversa — categorie inexistenta", "POST",
         "/tenants/%d/achizitie-taxare-inversa" % F,
         dict(ti_ok, categorie="ceva-ce-nu-exista"), "categorie=ceva-ce-nu-exista"),
        (252, "POST /achizitie-taxare-inversa — cota inexistenta", "POST",
         "/tenants/%d/achizitie-taxare-inversa" % F,
         dict(ti_ok, cota=99), "cota=99"),
        # ── #254 importul extracomunitar ─────────────────────────────────────
        (254, "POST /import-extracomunitar — corp gol", "POST",
         "/tenants/%d/import-extracomunitar" % F, {}, "corp JSON gol"),
        (254, "POST /import-extracomunitar — valoare vamala negativa", "POST",
         "/tenants/%d/import-extracomunitar" % F,
         dict(ext_ok, valoare_vamala=-1000), "valoare_vamala=-1000"),
        (254, "POST /import-extracomunitar — procent de taxa vamala absurd", "POST",
         "/tenants/%d/import-extracomunitar" % F,
         dict(ext_ok, procent_taxa_vamala=500), "procent_taxa_vamala=500"),
        # ── #23, A DOUA TRECERE: aceeasi ruta, directia PRIMITA ──────────────
        (23, "POST /facturi (PRIMITA) — cota de TVA inexistenta", "POST",
         "/tenants/%d/facturi" % F,
         {"numar": "F-PROBA-1", "data_emitere": "2026-09-04", "directie": "primita",
          "linii": [dict(linie_ok, cota_tva=99)], "tert_nume": "Furnizor SRL",
          "tert_cui": "RO1234567897", "tert_tara": "RO"},
         "cota_tva=99, directie=primita, tert_tara=RO"),
        (23, "POST /facturi (PRIMITA) — data inexistenta in calendar", "POST",
         "/tenants/%d/facturi" % F,
         {"numar": "F-PROBA-2", "data_emitere": "2026-02-31", "directie": "primita",
          "linii": [linie_ok], "tert_nume": "Furnizor SRL", "tert_cui": "RO1234567897"},
         "data_emitere=2026-02-31, directie=primita"),
    ]
    return p


#: Un salariat care EXISTA in firma de proba (`tenant_003` are doi: 1 si 3). Probele care vor sa
#: ajunga dincolo de „salariatul nu exista" trebuie sa-l foloseasca pe asta — altfel se opresc mai
#: devreme decat scrie in eticheta lor, cum s-a intamplat de doua ori in loturile 2 si 3.
SALARIAT = 1


def probe_T03T04():
    """LOTUL 4 — T03 (statul de plata, 8 unitati) + T04 (concediul medical, 5 unitati). Doisprezece
    din treisprezece sunt in perimetrul etapei 1; `#52` (stergerea unui concediu) e ruta fara
    campuri de completat.

    **Ce se lasa in urma, declarat:** patru dintre unitati SCRIU — `#41` scrie nota ciorna a
    statului, `#44` o corectie, `#46` emite exemplarul, `#51` salveaza un concediu. Toate primesc
    intrari incomplete sau imposibile, deci n-ar trebui sa ajunga la `INSERT`; daca vreuna trece,
    faptul ala e rezultatul probei si se sterge dupa."""
    F, S = FIRMA, SALARIAT
    return [
        # ── #40 fluturasul ───────────────────────────────────────────────────
        (40, "GET /fluturas — luna 13", "GET",
         "/tenants/%d/fluturas/%d?an=2026&luna=13" % (F, S), None, "luna=13"),
        (40, "GET /fluturas — salariat inexistent", "GET",
         "/tenants/%d/fluturas/%d?an=2026&luna=8" % (F, INEXISTENT), None, "salariat_id=999999"),
        # ── #41 nota ciorna a statului ───────────────────────────────────────
        (41, "POST /salarii-contare — luna 13", "POST",
         "/tenants/%d/salarii-contare?an=2026&luna=13" % F, {}, "luna=13"),
        (41, "POST /salarii-contare — an 1900", "POST",
         "/tenants/%d/salarii-contare?an=1900&luna=1" % F, {}, "an=1900"),
        # ── #42 propunerea de nota ───────────────────────────────────────────
        (42, "POST /salarii-contare/propunere — luna 0", "POST",
         "/tenants/%d/salarii-contare/propunere?an=2026&luna=0" % F, {}, "luna=0"),
        # ── #43 statul de plata ──────────────────────────────────────────────
        (43, "GET /stat-plata — luna 13", "GET",
         "/tenants/%d/stat-plata?an=2026&luna=13" % F, None, "luna=13"),
        (43, "GET /stat-plata — an ca text", "GET",
         "/tenants/%d/stat-plata?an=anul-trecut&luna=1" % F, None, "an=anul-trecut"),
        # ── #44 corectia pe stat ─────────────────────────────────────────────
        (44, "POST /stat-plata/corectie — corp gol", "POST",
         "/tenants/%d/stat-plata/corectie" % F, {}, "corp JSON gol"),
        (44, "POST /stat-plata/corectie — salariat inexistent", "POST",
         "/tenants/%d/stat-plata/corectie" % F,
         {"salariat_id": INEXISTENT, "an": 2026, "luna": 8}, "salariat_id=999999"),
        (44, "POST /stat-plata/corectie — luna 13", "POST",
         "/tenants/%d/stat-plata/corectie" % F, {"salariat_id": S, "an": 2026, "luna": 13},
         "luna=13"),
        # ── #45 exemplarele emise ────────────────────────────────────────────
        (45, "GET /stat-plata/emis — luna 13", "GET",
         "/tenants/%d/stat-plata/emis?an=2026&luna=13" % F, None, "luna=13"),
        # ── #46 emiterea statului ────────────────────────────────────────────
        (46, "POST /stat-plata/emite — corp gol", "POST",
         "/tenants/%d/stat-plata/emite" % F, {}, "corp JSON gol"),
        (46, "POST /stat-plata/emite — luna 13", "POST",
         "/tenants/%d/stat-plata/emite" % F, {"an": 2026, "luna": 13}, "luna=13"),
        # ── #47 motivul unui exemplar ────────────────────────────────────────
        (47, "POST /stat-plata/motiv — corp gol", "POST",
         "/tenants/%d/stat-plata/motiv" % F, {}, "corp JSON gol"),
        (47, "POST /stat-plata/motiv — motiv gol", "POST",
         "/tenants/%d/stat-plata/motiv" % F, {"exemplar_id": INEXISTENT, "motiv": ""},
         "motiv=\"\" (sir gol)"),
        (47, "POST /stat-plata/motiv — exemplar inexistent", "POST",
         "/tenants/%d/stat-plata/motiv" % F, {"exemplar_id": INEXISTENT, "motiv": "proba"},
         "exemplar_id=999999"),
        # ── #48 calculul indemnizatiei de concediu medical ───────────────────
        (48, "POST /calcul-cm — corp gol", "POST", "/tenants/%d/calcul-cm" % F, {},
         "corp JSON gol"),
        (48, "POST /calcul-cm — cod de indemnizatie inexistent", "POST",
         "/tenants/%d/calcul-cm" % F,
         {"salariat_id": S, "an": 2026, "luna": 8, "zile_lucratoare_cm": 5, "cod": "99"},
         "cod=99"),
        (48, "POST /calcul-cm — zile negative", "POST", "/tenants/%d/calcul-cm" % F,
         {"salariat_id": S, "an": 2026, "luna": 8, "zile_lucratoare_cm": -5, "cod": "01"},
         "zile_lucratoare_cm=-5"),
        (48, "POST /calcul-cm — luna 13", "POST", "/tenants/%d/calcul-cm" % F,
         {"salariat_id": S, "an": 2026, "luna": 13, "zile_lucratoare_cm": 5, "cod": "01"},
         "luna=13"),
        (48, "POST /calcul-cm — salariat inexistent", "POST", "/tenants/%d/calcul-cm" % F,
         {"salariat_id": INEXISTENT, "an": 2026, "luna": 8, "zile_lucratoare_cm": 5, "cod": "01"},
         "salariat_id=999999"),
        # ── #49 codurile de indemnizatie ─────────────────────────────────────
        (49, "GET /concedii/coduri — data ca text", "GET",
         "/tenants/%d/concedii/coduri?la_data=ieri" % F, None, "la_data=ieri"),
        (49, "GET /concedii/coduri — data inexistenta in calendar", "GET",
         "/tenants/%d/concedii/coduri?la_data=2026-02-31" % F, None, "la_data=2026-02-31"),
        # ── #50 lista concediilor ────────────────────────────────────────────
        (50, "GET /concedii — salariat inexistent", "GET",
         "/tenants/%d/salariati/%d/concedii?an=2026" % (F, INEXISTENT), None,
         "salariat_id=999999"),
        (50, "GET /concedii — an 1900", "GET",
         "/tenants/%d/salariati/%d/concedii?an=1900" % (F, S), None, "an=1900"),
        # ── #51 salvarea unui concediu ───────────────────────────────────────
        (51, "POST /concedii — corp gol", "POST",
         "/tenants/%d/salariati/%d/concedii" % (F, S), {}, "corp JSON gol"),
        (51, "POST /concedii — cod inexistent", "POST",
         "/tenants/%d/salariati/%d/concedii" % (F, S),
         {"cod": "99", "data_inceput": "2026-08-03", "data_sfarsit": "2026-08-07", "zile": 5},
         "cod=99"),
        (51, "POST /concedii — sfarsit inaintea inceputului", "POST",
         "/tenants/%d/salariati/%d/concedii" % (F, S),
         {"cod": "01", "data_inceput": "2026-08-07", "data_sfarsit": "2026-08-03", "zile": 5},
         "data_sfarsit < data_inceput"),
        (51, "POST /concedii — data inexistenta in calendar", "POST",
         "/tenants/%d/salariati/%d/concedii" % (F, S),
         {"cod": "01", "data_inceput": "2026-02-31", "data_sfarsit": "2026-03-02", "zile": 3},
         "data_inceput=2026-02-31"),
        (51, "POST /concedii — salariat inexistent", "POST",
         "/tenants/%d/salariati/%d/concedii" % (F, INEXISTENT),
         {"cod": "01", "data_inceput": "2026-08-03", "data_sfarsit": "2026-08-07", "zile": 5},
         "salariat_id=999999"),
    ]


#: Cele nouasprezece note SPECIALE, cu numarul lor din LISTA_FUNCTIONALITATI.md. Toate au aceeasi
#: forma — `POST /tenants/{id}/nota-<fel>`, corp liber cu `data` + un discriminator (`operatie` sau
#: `fel`) — si trec toate prin `_cere_luna_deschisa(conn, schema, corp.get("data"))`. De-aia proba
#: de baza e aceeasi pentru toate: daca ceva se rupe in punctul comun, se rupe in nouasprezece
#: locuri deodata, si asta se vede numai probandu-le pe toate.
NOTE_SPECIALE = [
    (63, "asociati"), (64, "avans"), (65, "bacsis"), (66, "chirie"),
    (67, "contract-special"), (68, "credit"), (69, "decont-deplasare"),
    (70, "inventariere"), (71, "leasing"), (72, "lichidare"), (73, "obiect-inventar"),
    (74, "ong"), (75, "perisabilitati"), (76, "productie"), (77, "provizion"),
    (78, "sgr"), (79, "sponsorizare"), (80, "subventie"), (81, "tva-incasare"),
]


def probe_T05():
    """LOTUL 3 — T05, nota contabila. Cele 32 de unitati ale traseului aflate in perimetrul
    etapei 1 (din 34: `#59` si `#62` sunt rute fara campuri de completat).

    **Ce se lasa in urma, declarat:** probele sunt REFUZURI asteptate. Singurele care ar putea
    scrie sunt `#58` (nota noua) si cele nouasprezece `nota-*`; toate primesc intrari incomplete
    sau imposibile, deci n-ar trebui sa ajunga la `INSERT`. Daca vreuna TRECE, faptul ala e chiar
    rezultatul probei — se scrie, si se sterge ce a ramas."""
    F = FIRMA
    p = [
        # ── citirile cu an/luna ──────────────────────────────────────────────
        (54, "GET /balanta — luna 13", "GET",
         "/tenants/%d/balanta?an=2026&luna=13" % F, None, "luna=13"),
        (54, "GET /balanta — an ca text", "GET",
         "/tenants/%d/balanta?an=anul-trecut&luna=1" % F, None, "an=anul-trecut"),
        (55, "GET /documente/balanta — luna 0", "GET",
         "/tenants/%d/documente/balanta?an=2026&luna=0" % F, None, "luna=0"),
        (57, "GET /jurnal — luna 13", "GET",
         "/tenants/%d/jurnal?an=2026&luna=13" % F, None, "luna=13"),
        (57, "GET /jurnal — an 1900", "GET",
         "/tenants/%d/jurnal?an=1900&luna=1" % F, None, "an=1900"),
        (56, "GET /fisa-cont — cont inexistent in plan", "GET",
         "/tenants/%d/fisa-cont?an=2026&cont=9999" % F, None, "cont=9999"),
        (56, "GET /fisa-cont — an lipsa", "GET", "/tenants/%d/fisa-cont?cont=411" % F, None,
         "parametrul an absent"),
        # ── registrul-inventar ───────────────────────────────────────────────
        (84, "GET /registru-inventar — exercitiu 1900", "GET",
         "/tenants/%d/registru-inventar?exercitiu=1900" % F, None, "exercitiu=1900"),
        (86, "GET /registru-inventar/propunere — luna 13", "GET",
         "/tenants/%d/registru-inventar/propunere?an=2026&luna=13" % F, None, "luna=13"),
        (85, "POST /registru-inventar — corp gol", "POST",
         "/tenants/%d/registru-inventar" % F, {}, "corp JSON gol"),
        # ── planul de conturi ────────────────────────────────────────────────
        (82, "GET /plan-conturi — cautare cu sir gol", "GET",
         "/tenants/%d/plan-conturi?q=" % F, None, "q= (sir gol)"),
        (83, "POST /plan-conturi — corp gol", "POST", "/tenants/%d/plan-conturi" % F, {},
         "corp JSON gol"),
        (83, "POST /plan-conturi — simbol care nu e numar de cont", "POST",
         "/tenants/%d/plan-conturi" % F, {"simbol": "ABC", "denumire": "Proba"}, "simbol=ABC"),
        # ── nota din registrul-jurnal ────────────────────────────────────────
        (58, "POST /jurnal — corp gol", "POST", "/tenants/%d/jurnal" % F, {}, "corp JSON gol"),
        # NU „nota dezechilibrata": schema tine debit, credit si suma pe aceeasi linie, deci o
        # nota nu POATE fi dezechilibrata. Intrebarea care are sens e alta — o nota fara linii.
        (58, "POST /jurnal — nota fara nicio linie", "POST", "/tenants/%d/jurnal" % F,
         {"data": "2026-09-04", "descriere": "proba", "linii": []}, "linii=[]"),
        (58, "POST /jurnal — cont inexistent in plan", "POST", "/tenants/%d/jurnal" % F,
         {"data": "2026-09-04", "descriere": "proba",
          "linii": [{"debit": "9999", "credit": "4111", "suma": 100}]}, "debit=9999"),
        (58, "POST /jurnal — data inexistenta in calendar", "POST", "/tenants/%d/jurnal" % F,
         {"data": "2026-02-31", "descriere": "proba",
          "linii": [{"debit": "5121", "credit": "4111", "suma": 100}]},
         "data=2026-02-31 (31 februarie)"),
        (58, "POST /jurnal — suma negativa", "POST", "/tenants/%d/jurnal" % F,
         {"data": "2026-09-04", "descriere": "proba",
          "linii": [{"debit": "5121", "credit": "4111", "suma": -100}]}, "suma=-100"),
        (60, "PUT /jurnal/{id} — nota inexistenta", "PUT",
         "/tenants/%d/jurnal/%d" % (F, INEXISTENT), {"data": "2026-09-04", "descriere": "x",
                                                     "linii": []}, "nota_id=999999"),
        (61, "POST /jurnal/{id}/dezleaga — nota inexistenta", "POST",
         "/tenants/%d/jurnal/%d/dezleaga" % (F, INEXISTENT), {}, "nota_id=999999"),
    ]
    # ── cele nouasprezece note speciale: acelasi punct comun, probat pe toate ─
    for nr, fel in NOTE_SPECIALE:
        p.append((nr, "POST /nota-%s — corp gol" % fel, "POST",
                  "/tenants/%d/nota-%s" % (F, fel), {}, "corp JSON gol"))
    # ── si patru dintre ele, probate pe adancime ─────────────────────────────
    # Valoarea discriminatorului trebuie sa fie VALIDA pentru nota probata, altfel proba de
    # „suma negativa" nu ajunge la suma: se opreste la discriminator si masoara alta intrebare.
    # (Prima forma trimitea `dividend` la toate patru — oarba pe trei din ele.)
    for nr, fel, disc, valid in ((63, "asociati", "operatie", "dividend"),
                                 (64, "avans", "operatie", "avans_incasat"),
                                 (65, "bacsis", "fel", "incasare"),
                                 (68, "credit", "operatie", "primire")):
        p.append((nr, "POST /nota-%s — data ca text" % fel, "POST",
                  "/tenants/%d/nota-%s" % (F, fel),
                  {"data": "ieri", disc: valid, "suma": 100, "cota": 21},
                  "data=\"ieri\""))
        p.append((nr, "POST /nota-%s — %s inexistent" % (fel, disc), "POST",
                  "/tenants/%d/nota-%s" % (F, fel),
                  {"data": "2026-09-04", disc: "ceva-ce-nu-exista", "suma": 100},
                  "%s=ceva-ce-nu-exista" % disc))
        p.append((nr, "POST /nota-%s — suma negativa" % fel, "POST",
                  "/tenants/%d/nota-%s" % (F, fel),
                  {"data": "2026-09-04", disc: valid, "suma": -500, "cota": 21},
                  "suma=-500 (cu %s valid)" % disc),)
    # ── calea de API: balanta ────────────────────────────────────────────────
    p += [
        (53, "GET /api/v1/.../balanta — luna 13", "GET",
         "/api/v1/firme/%d/balanta?an=2026&luna=13" % F, None, "luna=13"),
        (53, "GET /api/v1/.../balanta — fara an si luna", "GET",
         "/api/v1/firme/%d/balanta" % F, None, "parametrii an si luna absenti"),
    ]
    return p


#: Probele care merg pe calea de API publica: cheie in loc de token. Numele lor spune singur ce
#: cheie primesc — `fara cheie` niciuna, `cheie inventata` una care nu exista, restul cea reala.
CU_CHEIE_API = "/api/v1/"


FARA_TOKEN = {"GET /control-fiscal — fara token", "GET /supervizor — fara token"}
CU_CLIENT = {"GET /termene — cu rol CLIENT",
             "DELETE /portal/bon/{id} — bon inexistent · CLIENT",
             "POST /portal/bon/{id}/confirma — bon inexistent · CLIENT",
             "GET /portal/bon/{id}/imagine/{n} — bon inexistent · CLIENT"}


def _tipar(nr, eticheta, introdus, cod, corp):
    print("=" * 100)
    print("#%s  %s" % (nr, eticheta))
    print("    introdus: %s" % introdus)
    print("    HTTP %s" % cod)
    print("    corp: %s" % corp[:1500])


def _ruleaza_cu_cheie(lot, tok, tok_client=None):
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
        for nr, eticheta, metoda, cale, payload, introdus in {"T02": probe_T02, "T05": probe_T05, "T03T04": probe_T03T04,
                          "ACHIZITII": probe_ACHIZITII,
                          "T07T09T10": probe_T07T09T10,
                          "LOT6": probe_LOT6,
                          "LOT7": probe_LOT7,
                          "LOT8": probe_LOT8}[lot]():
            antete, t = None, tok
            if eticheta in CU_CLIENT:
                t = tok_client
            elif CU_CHEIE_API in cale:
                t = None
                if "fara cheie" in eticheta:
                    antete = None
                elif "cheie inventata" in eticheta:
                    antete = {"X-Api-Key": "ick_cheie-care-nu-exista"}
                else:
                    antete = {"X-Api-Key": cheie["cheie"]}
            if payload == "FISIER":
                # [lotul 6] Douasprezece rute de incarcare primesc acelasi fisier: un `.txt` cu o
                # linie de proza. Clasa e comuna, deci si proba.
                _b, _tip = multipart("fisier", "nu_e_un_tabel.txt",
                                     "linia unu, care nu e nici CSV nici XLSX")
                cod, corp = cere(metoda, cale, None, t, brut=_b, tip_continut=_tip)
            else:
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
    if lot in ("T02", "T05", "T03T04", "ACHIZITII", "T07T09T10", "LOT6", "LOT7", "LOT8"):
        return _ruleaza_cu_cheie(lot, tok, tok_client)
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
