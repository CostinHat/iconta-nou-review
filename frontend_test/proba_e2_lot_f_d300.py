# -*- coding: utf-8 -*-
"""ETAPA 2, LOTUL F — unitățile-nucleu ale D300 care hrănesc decontul prin OPERAȚIUNI SPECIALE.

Comanda (Costin, 15.09.2026): *„Fiecare unitate: valoarea intră, se înregistrează, ajunge în rândul
corect al declarației cu suma corectă, declarația generează și validează. Suprapunerea nu contează
ca probă."*

**AȘTEPTAREA E SCRISĂ AICI, ÎNAINTE DE PROBĂ.** Fiecare regulă e citită la sursă, iar locul e trecut
lângă rând — nu se derivă din ce a ieșit:

| # | unitatea | intrarea | rândul așteptat | de unde vine regula |
|---|---|---|---|---|
| 1 | `POST /tenants/{}/achizitie-ic` · bunuri | 1.000 @ 21% | `R5_1`+1000 `R5_2`+210 **și** `R18_1`+1000 `R18_2`+210 | `core/d300.py:405` — *„achizitii IC bunuri -> rd.5 colectat + rd.18 deductibil (taxare inversa, net zero)"* |
| 2 | `POST /tenants/{}/achizitie-ic` · servicii | 800 @ 21% | `R7_1`+800 `R7_2`+168 **și** `R20_1`+800 `R20_2`+168 | `core/d300.py:309` (rd.7 bază servicii IC) + `:454` |
| 3 | `POST /tenants/{}/achizitie-taxare-inversa` | 400 @ 21%, lit. a) deșeuri | `R12_1`+400 `R12_2`+84 **și** `R25_1`+400 `R25_2`+84 | `core/d300.py:384` — beneficiar art. 331, măsuri de simplificare |
| 4 | `POST /tenants/{}/achizitie-necorporala` | 1.000 @ 21%, software | `R22_1`+1000 `R22_2`+210 (Rd.24) | `_ACHIZ_RAND = {21: "R22"}`, `core/d300.py:47` |
| 5 | `POST /tenants/{}/achizitie-neinregistrat` | 150, PF fără CUI | **niciun** rând de TVA nu se mișcă | `main.py:5710` — *„PF nu factureaza TVA -> linie cota 0"* |
| 6 | `POST /tenants/{}/woocommerce/sincronizeaza` | — | **REFUZ motivat**, nu tăcere și nu „conectat" | R152 — magazinul nu se declară conectat fără să fi vorbit cineva cu el |

**CATEGORIA art. 331 e aleasă cu motiv:** `deseuri` (lit. a) e singura din nomenclator fără dată de
expirare **și** fără prag — `cereale` expiră în 2026, iar `telefoane` are prag pe factură. *Dacă aș
fi ales o categorie expirată, refuzul corect al aplicației ar fi intrat în raport ca defect.*

SCENARIUL, DECLARAT: «Comert Micro TVA SRL» (`tenant_003`), plătitor TVA **trimestrial**, luna
**09/2026** — aceeași firmă și aceeași perioadă ca lotul A, ca delta să se citească peste starea lui.
Sumele sunt rotunde, ca TVA-ul să nu depindă de rotunjire.

**RE-RULABILĂ, cu delta MĂSURATĂ de fiecare dată.** Intrările poartă `PROBA-E2-F-<lanț>-<rulare>`,
iar numărul rulării se derivă numărând facturile care poartă deja marca. Nu se sare peste intrări la
a doua rulare: aceea a fost lecția deciziei 69 — *o probă care nu-și poate măsura delta se reduce
tăcut la invarianți absoluți și raportează „0 nepotriviri" despre nimic.* Costul e scris: firma
acumulează un set de operațiuni per rulare.

CE NU DEMONSTREAZĂ, declarat: că rândul e cel cerut de LEGE pentru operațiunea aia (întrebare de
temei, nu de lanț) · că nu există o a treia cale prin care aceleași date ar intra altfel în decont.
"""
import base64
import json
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/home/costin/iconta_nou/frontend_test")
sys.path.insert(0, "/home/costin/iconta_nou")

import e2_util as U  # noqa: E402

FIRMA = "Comert Micro TVA SRL"
AN, LUNA, TRIM = 2026, 9, 3   # firma e TRIMESTRIALA: decontul se cere pe TRIMESTRU (art.322 alin.(2)),
#: iar luna ramane numai pentru datele operatiunilor. Refuzul rutei a fost cel care mi-a corectat asteptarea.
MARCA = "PROBA-E2-F"
OUT = "/home/costin/iconta_nou/frontend_test/proba_e2_lot_f_d300.json"

CUI_FURNIZOR_RO = "95275466"   # Distributie Profit IC SRL — CUI real al portofoliului, cifră de control validă
COD_TVA_UE = "DE811907980"     # cod TVA UE, formă corectă
CUI_FIRMA = "95141537"         # chiar «Comert Micro TVA SRL» — din el iese `directie = emisa`


def cere_cu_cheie(metoda, cale, corp, cheie):
    """Cerere pe calea PUBLICĂ, cu `X-Api-Key` — nu cu jetonul de sesiune.

    E o a doua poartă, nu o a doua formă a aceleiași: `main.cere_api_key` trece prin
    `api_public.verifica`, singurul loc prin care intră o cheie — chiar poarta pusă pe 14.09 pentru
    cabinetul suspendat. Proba lanțului o exercită pe drumul bun.
    """
    req = urllib.request.Request(
        U.BAZA + cale, method=metoda,
        data=json.dumps(corp).encode() if corp is not None else None,
        headers={"Content-Type": "application/json", "X-Api-Key": cheie})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            b = r.read().decode()
            return r.status, (json.loads(b) if b.strip().startswith(("{", "[")) else b)
    except urllib.error.HTTPError as e:
        b = e.read().decode()
        try:
            return e.code, json.loads(b)
        except Exception:  # noqa: BLE001
            return e.code, b[:600]


def cere_fisier(cale, nume_fisier, octeti, tok, camp="fisiere"):
    """Încărcare `multipart/form-data` — ruta de import cere un FIȘIER, nu un JSON.

    Se construiește aici, nu în `e2_util`, fiindcă e singurul lot care încarcă fișiere; dacă mai
    apare unul, se mută acolo, nu se scrie a doua oară.
    """
    lim = "----probaE2F%d" % len(octeti)
    corp = (("--%s\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"%s\"\r\n"
             "Content-Type: application/xml\r\n\r\n" % (lim, camp, nume_fisier)).encode()
            + octeti + ("\r\n--%s--\r\n" % lim).encode())
    req = urllib.request.Request(
        U.BAZA + cale, method="POST", data=corp,
        headers={"Content-Type": "multipart/form-data; boundary=%s" % lim,
                 "Authorization": "Bearer " + tok})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            b = r.read().decode()
            return r.status, (json.loads(b) if b.strip().startswith(("{", "[")) else b)
    except urllib.error.HTTPError as e:
        b = e.read().decode()
        try:
            return e.code, json.loads(b)
        except Exception:  # noqa: BLE001
            return e.code, b[:600]


#: UBL 2.1 minimal, construit după CE CITEȘTE parserul (`core/efactura_import.parseaza_xml`), nu
#: după o schemă copiată: `cbc:ID`, `cbc:IssueDate`, cele două părți cu `CompanyID`,
#: `LegalMonetaryTotal/TaxInclusiveAmount`, `TaxTotal/TaxAmount` și `InvoiceLine`. Furnizorul e
#: CHIAR firma probată — de acolo iese `directie = emisa`, singura cale prin care o factură EMISĂ
#: intră prin import (R91).
UBL = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
  <cbc:ID>%(numar)s</cbc:ID>
  <cbc:IssueDate>%(data)s</cbc:IssueDate>
  <cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
  <cac:AccountingSupplierParty><cac:Party>
    <cac:PartyLegalEntity><cbc:RegistrationName>%(furn_nume)s</cbc:RegistrationName>
      <cbc:CompanyID>%(furn_cui)s</cbc:CompanyID></cac:PartyLegalEntity>
  </cac:Party></cac:AccountingSupplierParty>
  <cac:AccountingCustomerParty><cac:Party>
    <cac:PartyLegalEntity><cbc:RegistrationName>%(cli_nume)s</cbc:RegistrationName>
      <cbc:CompanyID>%(cli_cui)s</cbc:CompanyID></cac:PartyLegalEntity>
  </cac:Party></cac:AccountingCustomerParty>
  <cac:TaxTotal><cbc:TaxAmount currencyID="RON">%(tva)s</cbc:TaxAmount></cac:TaxTotal>
  <cac:LegalMonetaryTotal>
    <cbc:TaxInclusiveAmount currencyID="RON">%(total)s</cbc:TaxInclusiveAmount>
  </cac:LegalMonetaryTotal>
  <cac:InvoiceLine>
    <cbc:InvoicedQuantity>1</cbc:InvoicedQuantity>
    <cac:Item><cbc:Name>%(descriere)s</cbc:Name>
      <cac:ClassifiedTaxCategory><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
    <cac:Price><cbc:PriceAmount currencyID="RON">%(baza)s</cbc:PriceAmount></cac:Price>
  </cac:InvoiceLine>
</Invoice>
"""


def d300(tok, tid):
    st, r = U.cere("POST", "/declaratii/d300", {"tenant_id": tid, "an": AN, "trim": TRIM}, tok)
    if st != 200 or not isinstance(r, dict):
        return None, {"stare": st, "raspuns": str(r)[:300]}
    xml = r.get("xml") or r.get("continut") or ""
    if not xml and r.get("xml_b64"):
        xml = base64.b64decode(r["xml_b64"]).decode("utf-8", "replace")
    # DECLARATIA `<?xml ... ?>` se TAIE inainte de citire: `randuri_xml` ia atributele PRIMULUI
    # element, iar fara taiere acela e chiar declaratia — se intorc `version` si `encoding`, adica
    # ZERO randuri. Proba a raportat asa opt delte de zero, pe o aplicatie care lucra corect.
    # Lotul A taia declaratia (`proba_e2_d300.py:121`); eu am uitat-o. *Un cititor care nu gaseste
    # nimic trebuie sa CADA, nu sa intoarca gol* — de-aia aserttiunea de dedesubt.
    randuri = U.randuri_xml(xml.split("?>", 1)[-1])
    if not any(k.startswith("R") for k in randuri):
        raise SystemExit("ANTI-VACUU: decontul s-a generat (%d octeti) dar nu i s-a citit niciun "
                         "rand `R*` — cititorul probei e orb, nu declaratia e goala. Chei vazute: %s"
                         % (len(xml), sorted(randuri)[:8]))
    return randuri, {"stare": st, "octeti_xml": len(xml), "randuri_citite": len(randuri)}


def numarul_rularii(tok, tid):
    """Câte facturi poartă deja marca — de aici iese numărul rulării. Fără el, a doua rulare ar
    trimite același număr de factură și n-ar mai măsura nimic."""
    st, r = U.cere("GET", "/tenants/%d/facturi?an=%d&luna=%d" % (tid, AN, LUNA), None, tok)
    lista = (r.get("facturi") if isinstance(r, dict) else r) or []
    if not isinstance(lista, list):
        return 1, {"stare": st, "necitit": str(r)[:200]}
    ale_mele = [f for f in lista if str(f.get("numar") or "").startswith(MARCA)]
    return len(ale_mele) + 1, {"stare": st, "facturi_cu_marca": len(ale_mele)}


def main():
    tok, tid, schema = U.context(FIRMA)
    rul, meta_rul = numarul_rularii(tok, tid)
    rez = {"firma": FIRMA, "tenant_id": tid, "schema": schema,
           "perioada": "%d-%02d" % (AN, LUNA), "rulare": rul, "cum_s_a_aflat": meta_rul,
           "lanturi": []}

    randuri0, meta0 = d300(tok, tid)
    rez["d300_la_pornire"] = meta0
    if randuri0 is None:
        rez["OPRIT"] = "D300 nu se generează la pornire — proba n-are de unde măsura delta"
        print(json.dumps(rez, indent=1, ensure_ascii=False))
        return 2

    def pas(nume, cale, corp, asteptat, se_asteapta_refuz=False):
        intrare = {"lant": nume, "ruta": "POST " + cale, "corp_trimis": corp}
        inainte, _ = d300(tok, tid)
        st, r = U.cere("POST", cale, corp, tok)
        intrare["raspuns"] = {"stare": st, "corp": r if not isinstance(r, str) else r[:300]}
        if se_asteapta_refuz:
            motiv = json.dumps(r, ensure_ascii=False) if isinstance(r, dict) else str(r)
            intrare["OK"] = (st >= 400 and len(motiv) > 20)
            intrare["ce_s_a_cerut"] = "refuz MOTIVAT (nu 200 tăcut, nu mesaj gol)"
            rez["lanturi"].append(intrare)
            return
        dupa, meta_d = d300(tok, tid)
        intrare["d300_dupa"] = meta_d
        d, nepotriviri = {}, {}
        for k, cerut in asteptat.items():
            a, b = U.numar((inainte or {}).get(k)), U.numar((dupa or {}).get(k))
            m = (b - a) if (a is not None and b is not None) else None
            d[k] = {"inainte": a, "dupa": b, "delta": m}
            if m != cerut:
                nepotriviri[k] = {"asteptat": cerut, "masurat": m}
        intrare["delta"] = d
        intrare["nepotriviri"] = nepotriviri
        intrare["OK"] = (st in (200, 201)) and not nepotriviri
        rez["lanturi"].append(intrare)

    zi = lambda z: "%d-%02d-%02d" % (AN, LUNA, z)  # noqa: E731
    nr = lambda n: "%s-%d-%d" % (MARCA, n, rul)    # noqa: E731

    pas("1 · achizitie-ic BUNURI 1000 @21%%", "/tenants/%d/achizitie-ic" % tid,
        {"data": zi(15), "valoare": 1000, "cont_destinatie": "371", "cota": 21,
         "tip": "bunuri", "cod_tva_furnizor": COD_TVA_UE, "numar": nr(1),
         "furnizor_nume": "FURNIZOR UE GMBH", "descriere": "%s achizitie IC bunuri" % MARCA},
        {"R5_1": 1000, "R5_2": 210, "R18_1": 1000, "R18_2": 210})

    pas("2 · achizitie-ic SERVICII 800 @21%%", "/tenants/%d/achizitie-ic" % tid,
        {"data": zi(16), "valoare": 800, "cont_destinatie": "628", "cota": 21,
         "tip": "servicii", "cod_tva_furnizor": COD_TVA_UE, "numar": nr(2),
         "furnizor_nume": "FURNIZOR UE GMBH", "descriere": "%s servicii IC" % MARCA},
        {"R7_1": 800, "R7_2": 168, "R20_1": 800, "R20_2": 168})

    pas("3 · achizitie-taxare-inversa 400 @21%% (deseuri, lit. a)",
        "/tenants/%d/achizitie-taxare-inversa" % tid,
        {"data": zi(17), "categorie": "deseuri", "valoare": 400, "cont_destinatie": "371",
         "cota": 21, "furnizor_cui": CUI_FURNIZOR_RO, "furnizor_platitor_tva": True,
         "numar": nr(3), "furnizor_nume": "FURNIZOR RO SRL",
         "descriere": "%s taxare inversa" % MARCA},
        {"R12_1": 400, "R12_2": 84, "R25_1": 400, "R25_2": 84})

    pas("4 · achizitie-necorporala 1000 @21%% (software, 36 luni)",
        "/tenants/%d/achizitie-necorporala" % tid,
        {"data": zi(18), "denumire": "%s licenta software" % MARCA, "valoare": 1000,
         "tip": "software", "cota": 21, "furnizor_cui": CUI_FURNIZOR_RO,
         "furnizor_nume": "FURNIZOR RO SRL", "numar": nr(4)},
        {"R22_1": 1000, "R22_2": 210})

    pas("5 · achizitie-neinregistrat 150 (PF, fara CUI)",
        "/tenants/%d/achizitie-neinregistrat" % tid,
        {"data": zi(19), "furnizor_nume": "%s Persoana Fizica" % MARCA, "valoare": 150,
         "cont_cheltuiala": "607", "categorie": "alte_bunuri", "numar": nr(5)},
        {"R22_1": 0, "R22_2": 0, "R23_1": 0, "R23_2": 0})

    pas("6 · woocommerce/sincronizeaza (magazin neconectat)",
        "/tenants/%d/woocommerce/sincronizeaza" % tid, {}, {}, se_asteapta_refuz=True)

    # ── 7. STORNO: al doilea document, nu corectarea primului (R42) ──────────
    #    Precondiția (emiterea) NU e proba: `facturi_emite` e deja probată în lotul A. Ce se
    #    probează aici e că STORNO-ul scade exact cât a adăugat emiterea — pe același rând.
    st_e, r_e = U.cere("POST", "/tenants/%d/facturi/emite" % tid,
                       {"tip": "factura", "data_emitere": zi(20), "tert_nume": "CLIENT PROBA F",
                        "tert_cui": CUI_FURNIZOR_RO,
                        "linii": [{"descriere": "%s-7 de stornat" % MARCA, "cantitate": 1,
                                   "pret_unitar": 1000, "cota_tva": 21}]}, tok)
    fid_storno = (r_e or {}).get("factura_id") if isinstance(r_e, dict) else None
    intr7 = {"lant": "7 · facturi/{}/storno peste o emisă 1000 @21%",
             "preconditie": {"emitere_stare": st_e, "factura_id": fid_storno}}
    if not fid_storno:
        intr7["NEPROBAT"] = ("precondiția nu s-a putut construi: emiterea a răspuns %s — fără o "
                             "factură emisă, stornarea n-are subiect" % st_e)
        intr7["OK"] = False
        rez["lanturi"].append(intr7)
    else:
        inainte7, _ = d300(tok, tid)
        st7, r7 = U.cere("POST", "/tenants/%d/facturi/%d/storno" % (tid, fid_storno), None, tok)
        dupa7, meta7 = d300(tok, tid)
        d7, nep7 = {}, {}
        for k, cerut in {"R9_1": -1000, "R9_2": -210}.items():
            a, b = U.numar((inainte7 or {}).get(k)), U.numar((dupa7 or {}).get(k))
            m = (b - a) if (a is not None and b is not None) else None
            d7[k] = {"inainte": a, "dupa": b, "delta": m}
            if m != cerut:
                nep7[k] = {"asteptat": cerut, "masurat": m}
        intr7.update({"ruta": "POST /tenants/{}/facturi/{}/storno", "raspuns": {"stare": st7,
                      "corp": r7 if not isinstance(r7, str) else r7[:300]},
                      "d300_dupa": meta7, "delta": d7, "nepotriviri": nep7,
                      "OK": st7 in (200, 201) and not nep7})
        rez["lanturi"].append(intr7)

    # ── 8. PROFORMA nu e în decont; transformarea o bagă (decizia 3ca96f2f) ──
    #    Două aserțiuni, nu una: întâi ABSENȚA (proforma emisă nu mișcă D300), apoi PREZENȚA.
    #    *O probă care verifică numai a doua jumătate ar trece și dacă proforma ar fi fost tot
    #    timpul în decont.*
    inainte8a, _ = d300(tok, tid)
    st_p, r_p = U.cere("POST", "/tenants/%d/facturi/emite" % tid,
                       {"tip": "proforma", "data_emitere": zi(21), "tert_nume": "CLIENT PROBA F",
                        "tert_cui": CUI_FURNIZOR_RO,
                        "linii": [{"descriere": "%s-8 proforma" % MARCA, "cantitate": 1,
                                   "pret_unitar": 600, "cota_tva": 21}]}, tok)
    fid_pf = (r_p or {}).get("factura_id") if isinstance(r_p, dict) else None
    dupa8a, _ = d300(tok, tid)
    intr8 = {"lant": "8 · proforma 600 @21% NU e în decont, transformarea o bagă",
             "preconditie": {"emitere_proforma": st_p, "factura_id": fid_pf}}
    d8a, nep8 = {}, {}
    for k in ("R9_1", "R9_2"):
        a, b = U.numar((inainte8a or {}).get(k)), U.numar((dupa8a or {}).get(k))
        m = (b - a) if (a is not None and b is not None) else None
        d8a[k] = {"inainte": a, "dupa": b, "delta": m}
        if m != 0:
            nep8["proforma_" + k] = {"asteptat": 0, "masurat": m,
                                     "de_ce": "o proformă nu e document fiscal — nu intră în D300"}
    intr8["a_proforma_absenta"] = d8a
    if not fid_pf:
        intr8["NEPROBAT_transformarea"] = "proforma nu s-a emis (stare %s)" % st_p
        intr8["OK"] = False
    else:
        inainte8b, _ = d300(tok, tid)
        st8, r8 = U.cere("POST", "/tenants/%d/facturi/%d/transforma" % (tid, fid_pf), None, tok)
        dupa8b, meta8 = d300(tok, tid)
        d8b = {}
        for k, cerut in {"R9_1": 600, "R9_2": 126}.items():
            a, b = U.numar((inainte8b or {}).get(k)), U.numar((dupa8b or {}).get(k))
            m = (b - a) if (a is not None and b is not None) else None
            d8b[k] = {"inainte": a, "dupa": b, "delta": m}
            if m != cerut:
                nep8["transformata_" + k] = {"asteptat": cerut, "masurat": m}
        intr8.update({"ruta": "POST /tenants/{}/facturi/{}/transforma",
                      "raspuns": {"stare": st8, "corp": r8 if not isinstance(r8, str) else r8[:300]},
                      "b_dupa_transformare": d8b, "d300_dupa": meta8,
                      "OK": st8 in (200, 201) and not nep8})
    intr8["nepotriviri"] = nep8
    rez["lanturi"].append(intr8)

    # ── 9. EMITEREA PRIN CHEIE DE API (calea publică, nu ecranul) ───────────
    intr9 = {"lant": "9 · api/v1/firme/{}/facturi, emisă 500 @21%% prin CHEIE DE API",
             "ruta": "POST /api/v1/firme/{}/facturi"}
    st_k, r_k = U.cere("POST", "/cabinet/api-chei", {"nume": "%s cheie lot F" % MARCA}, tok)
    cheie = (r_k or {}).get("cheie") if isinstance(r_k, dict) else None
    kid = (r_k or {}).get("id") if isinstance(r_k, dict) else None
    intr9["preconditie"] = {"emitere_cheie": st_k, "s_a_primit_cheia": bool(cheie), "id": kid}
    if not cheie:
        intr9["NEPROBAT"] = ("cheia de API nu s-a emis (stare %s) — fără ea calea publică n-are "
                             "cum fi apăsată; cheia se arată O SINGURĂ DATĂ, deci nu se poate lua "
                             "din bază" % st_k)
        intr9["OK"] = False
    else:
        inainte9, _ = d300(tok, tid)
        st9, r9 = cere_cu_cheie("POST", "/api/v1/firme/%d/facturi" % tid,
                                {"tip": "factura", "data_emitere": zi(22),
                                 "tert_nume": "CLIENT PROBA F API", "tert_cui": CUI_FURNIZOR_RO,
                                 "linii": [{"descriere": "%s-9 prin cheie" % MARCA,
                                            "cantitate": 1, "pret_unitar": 500, "cota_tva": 21}]},
                                cheie)
        dupa9, meta9 = d300(tok, tid)
        d9, nep9 = {}, {}
        for k, cerut in {"R9_1": 500, "R9_2": 105}.items():
            a, b = U.numar((inainte9 or {}).get(k)), U.numar((dupa9 or {}).get(k))
            m = (b - a) if (a is not None and b is not None) else None
            d9[k] = {"inainte": a, "dupa": b, "delta": m}
            if m != cerut:
                nep9[k] = {"asteptat": cerut, "masurat": m}
        intr9.update({"raspuns": {"stare": st9, "corp": r9 if not isinstance(r9, str) else r9[:300]},
                      "d300_dupa": meta9, "delta": d9, "nepotriviri": nep9,
                      "OK": st9 in (200, 201) and not nep9})
        # cheia se REVOCĂ după probă: o cheie vie lăsată în urmă e o ușă, nu un artefact
        if kid:
            st_r, _ = U.cere("DELETE", "/cabinet/api-chei/%s" % kid, None, tok)
            intr9["cheia_revocata"] = {"stare": st_r}
    rez["lanturi"].append(intr9)

    # ── 10. IMPORT e-FACTURA (UBL) — singura cale prin care o EMISĂ intră prin import
    intr10 = {"lant": "10 · import-efactura, UBL emisă 300 @21%%",
              "ruta": "POST /tenants/{}/import-efactura"}
    xml = (UBL % {"numar": nr(10), "data": zi(23), "furn_nume": FIRMA,
                  "furn_cui": CUI_FIRMA, "cli_nume": "CLIENT PROBA F UBL",
                  "cli_cui": CUI_FURNIZOR_RO, "tva": "63.00", "total": "363.00",
                  "descriere": "%s-10 linie importata" % MARCA, "baza": "300.00"}).encode()
    inainte10, _ = d300(tok, tid)
    st10, r10 = cere_fisier("/tenants/%d/import-efactura" % tid, "%s-10.xml" % MARCA, xml, tok)
    dupa10, meta10 = d300(tok, tid)
    d10, nep10 = {}, {}
    for k, cerut in {"R9_1": 300, "R9_2": 63}.items():
        a, b = U.numar((inainte10 or {}).get(k)), U.numar((dupa10 or {}).get(k))
        m = (b - a) if (a is not None and b is not None) else None
        d10[k] = {"inainte": a, "dupa": b, "delta": m}
        if m != cerut:
            nep10[k] = {"asteptat": cerut, "masurat": m}
    intr10.update({"raspuns": {"stare": st10, "corp": r10 if not isinstance(r10, str) else r10[:400]},
                   "d300_dupa": meta10, "delta": d10, "nepotriviri": nep10,
                   "OK": st10 in (200, 201) and not nep10})
    rez["lanturi"].append(intr10)

    # ── 11. VALIDAREA UNEI FACTURI PRIMITE (four-eyes) ──────────────────────
    #    A zecea unitate-nucleu a lotului. Lanțul pe date VALIDE nu se poate exercita azi, și
    #    motivul se măsoară, nu se presupune: ruta lucrează pe un rând din `efactura_primite`, iar
    #    SINGURUL producător al acelui rând e calea de recepție SPV (`spv_receive.importa_mesaj`,
    #    chemată de cron). Coada e goală pe toate firmele de probă. *Aș fi putut semăna rândul
    #    direct în tabel — dar o probă care își scrie singură precondiția pe la spatele aplicației
    #    dovedește citirea aplicației, nu lanțul ei.* Ce se poate exercita — și se exercită — e
    #    REFUZUL pe un id inexistent, ca ruta să nu treacă drept „netestată".
    intr11 = {"lant": "11 · facturi-primite/{}/valideaza (four-eyes)",
              "ruta": "POST /tenants/{}/facturi-primite/{}/valideaza"}
    st_l, r_l = U.cere("GET", "/tenants/%d/facturi-primite" % tid, None, tok)
    coada = (r_l.get("facturi") if isinstance(r_l, dict) else r_l) or []
    intr11["coada_de_validat"] = {"stare": st_l, "cate": len(coada) if isinstance(coada, list) else "?"}
    st_r, r_r = U.cere("POST", "/tenants/%d/facturi-primite/999999999/valideaza" % tid, {}, tok)
    intr11["refuz_pe_id_inexistent"] = {"stare": st_r,
                                        "corp": r_r if not isinstance(r_r, str) else r_r[:300]}
    if isinstance(coada, list) and coada:
        pid = coada[0].get("id")
        inainte11, _ = d300(tok, tid)
        st11, r11 = U.cere("POST", "/tenants/%d/facturi-primite/%s/valideaza" % (tid, pid), {}, tok)
        dupa11, meta11 = d300(tok, tid)
        intr11.update({"raspuns": {"stare": st11, "corp": str(r11)[:300]},
                       "R22_1": {"inainte": U.numar((inainte11 or {}).get("R22_1")),
                                 "dupa": U.numar((dupa11 or {}).get("R22_1"))},
                       "d300_dupa": meta11, "OK": st11 in (200, 201)})
    else:
        intr11["NEPROBAT_pe_date_valide"] = (
            "coada `efactura_primite` e GOALĂ pe firma probată, iar singurul producător al unui rând "
            "acolo e calea de recepție SPV (`spv_receive.importa_mesaj`, chemată de cron) — nu există "
            "rută prin care un om să pună un rând în coadă. Semănarea directă în tabel ar fi o probă "
            "despre citirea aplicației, nu despre lanțul ei. Ce s-a exercitat: REFUZUL pe id "
            "inexistent, care trebuie să fie motivat, nu 500.")
        motiv = str(intr11["refuz_pe_id_inexistent"]["corp"])
        intr11["OK"] = (st_r >= 400 and st_r != 500 and len(motiv) > 20)
        intr11["ce_s_a_cerut"] = "refuz MOTIVAT (nu 500, nu tăcere) pe un id inexistent"
    rez["lanturi"].append(intr11)

    # ── declarația, la capăt: generează ȘI validează ────────────────────────
    st, r = U.cere("POST", "/declaratii/d300/valideaza",
                   {"tenant_id": tid, "an": AN, "trim": TRIM}, tok, timeout=300)
    rez["duk"] = {"stare_http": st, "verdict": r if not isinstance(r, str) else r[:400]}

    text = json.dumps(rez, indent=1, ensure_ascii=False)
    open(OUT, "w", encoding="utf-8").write(text)
    print(text)
    nep = [x for x in rez["lanturi"] if not x.get("OK")]
    print("\nLANTURI: %d · CU NEPOTRIVIRI SAU REFUZ NEASTEPTAT: %d" % (len(rez["lanturi"]), len(nep)))
    for x in nep:
        print("   ! %s -> %s" % (x["lant"], x.get("nepotriviri") or x["raspuns"]))
    return 1 if nep else 0


if __name__ == "__main__":
    sys.exit(main())
