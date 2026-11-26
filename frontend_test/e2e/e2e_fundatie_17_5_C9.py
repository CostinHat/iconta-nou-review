"""AC201 (17.5-C9, r2): CIF-ul emitentului la importul SPV când lista ANAF nu îl dă; emitentul vine din partea furnizorului a XML-ului.

Proba REAL a arhitectului, pe copia 8019. Răspunsul SPV e CONTROLAT și declarat ca atare: metadatele mesajului (fără cif_emitent,
cif_beneficiar și detalii, ca la martorii ABFEC01233/ABFEC01234 din nota AC201) și arhiva descărcată (XML de probă cu
PartyTaxScheme/CompanyID 26766053 și PartyLegalEntity/CompanyID «-/-/-») sunt date de test, puse peste efactura_send.descarca în
procesul testului. Importul rulează codul aplicației, core.spv_receive.importa_mesaj, pe baza de test a copiei. Martorii sunt rândul
persistent din efactura_primite și fereastra contabilului (F1 › Facturi › Facturi primite › Validare factură), la 1366×768 și 603×590.
  e.1 ciorna facturii de probă ajunge o singură dată în F1, cu beneficiarul F1 și XML-ul probei, și se vede în listă;
  e.2 emitentul persistat are una din formele permise (26766053, RO26766053), iar câmpul «Furnizor» arată exact «<nume> · <acel cod>»;
  e.3 reluarea aceluiași mesaj păstrează același rând, neschimbat (id, stare, emitent, beneficiar, SHA-ul XML), și nu scrie în altă firmă.
Identitățile fixturii (mesajul, cererea, descărcarea, firma destinatară, SHA-ul XML-ului introdus) se verifică separat de predicate:
o măsură a altei facturi nu e o observație a probei.
"""

import hashlib
import io
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path


DIM = ((1366, 768), (603, 590))
IDS = ("e.1", "e.2", "e.3")
LOT = "17_5_C9"
FIRMA = "F1 Comert Stoc SRL"
CUI_F1 = "401002001"
EMITENT = "26766053"
EMITENT_FORME = ("26766053", "RO26766053")
INDEX = "9178305201"
SOLICITARE = "9178305101"
DATA_CREARE = "202611261630"
TIP = "FACTURA PRIMITA"
NUMAR = "PROBA-C9-AC201"
FURNIZOR = "FURNIZOR PROBA AC201 SRL"
CONT_PROBA = "dovada.71507@sesiuneab.test"
RASPUNS = "SPV controlat (date de test)"
CAMPURI_RAND = ("id", "stare", "emitent", "beneficiar", "xml")


def cifre(x):
    return "".join(c for c in str(x or "") if c.isdigit())


def xml_proba(cui_cumparator, nume_cumparator):
    """Factura UBL de probă (CIUS-RO), declarată ca dată de test; furnizorul are codul numai în PartyTaxScheme."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
  <cbc:CustomizationID>urn:cen.eu:en16931:2017#compliant#urn:efactura.mfinante.ro:CIUS-RO:1.0.1</cbc:CustomizationID>
  <cbc:ID>{NUMAR}</cbc:ID>
  <cbc:IssueDate>2026-11-24</cbc:IssueDate>
  <cbc:DueDate>2026-12-24</cbc:DueDate>
  <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
  <cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
  <cac:AccountingSupplierParty><cac:Party>
    <cac:PostalAddress><cbc:StreetName>Str. Proba 1</cbc:StreetName><cbc:CityName>SECTOR1</cbc:CityName><cbc:CountrySubentity>RO-B</cbc:CountrySubentity><cac:Country><cbc:IdentificationCode>RO</cbc:IdentificationCode></cac:Country></cac:PostalAddress>
    <cac:PartyTaxScheme><cbc:CompanyID>{EMITENT}</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:PartyTaxScheme>
    <cac:PartyLegalEntity><cbc:RegistrationName>{FURNIZOR}</cbc:RegistrationName><cbc:CompanyID>-/-/-</cbc:CompanyID></cac:PartyLegalEntity>
  </cac:Party></cac:AccountingSupplierParty>
  <cac:AccountingCustomerParty><cac:Party>
    <cac:PostalAddress><cbc:StreetName>Str. Comertului 1</cbc:StreetName><cbc:CityName>SECTOR1</cbc:CityName><cbc:CountrySubentity>RO-B</cbc:CountrySubentity><cac:Country><cbc:IdentificationCode>RO</cbc:IdentificationCode></cac:Country></cac:PostalAddress>
    <cac:PartyTaxScheme><cbc:CompanyID>RO{cui_cumparator}</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:PartyTaxScheme>
    <cac:PartyLegalEntity><cbc:RegistrationName>{nume_cumparator}</cbc:RegistrationName></cac:PartyLegalEntity>
  </cac:Party></cac:AccountingCustomerParty>
  <cac:TaxTotal>
    <cbc:TaxAmount currencyID="RON">21.00</cbc:TaxAmount>
    <cac:TaxSubtotal><cbc:TaxableAmount currencyID="RON">100.00</cbc:TaxableAmount><cbc:TaxAmount currencyID="RON">21.00</cbc:TaxAmount><cac:TaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>21</cbc:Percent><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:TaxCategory></cac:TaxSubtotal>
  </cac:TaxTotal>
  <cac:LegalMonetaryTotal>
    <cbc:LineExtensionAmount currencyID="RON">100.00</cbc:LineExtensionAmount>
    <cbc:TaxExclusiveAmount currencyID="RON">100.00</cbc:TaxExclusiveAmount>
    <cbc:TaxInclusiveAmount currencyID="RON">121.00</cbc:TaxInclusiveAmount>
    <cbc:PayableAmount currencyID="RON">121.00</cbc:PayableAmount>
  </cac:LegalMonetaryTotal>
  <cac:InvoiceLine>
    <cbc:ID>1</cbc:ID>
    <cbc:InvoicedQuantity unitCode="H87">1</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount currencyID="RON">100.00</cbc:LineExtensionAmount>
    <cac:Item><cbc:Name>Serviciu de proba AC201</cbc:Name><cac:ClassifiedTaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>21</cbc:Percent><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:ClassifiedTaxCategory></cac:Item>
    <cac:Price><cbc:PriceAmount currencyID="RON">100.00</cbc:PriceAmount></cac:Price>
  </cac:InvoiceLine>
</Invoice>
""".encode("utf-8")


def sha_xml_proba():
    """SHA-256 al XML-ului introdus de probă, așa cum îl calculează importul (textul UTF-8 al documentului)."""
    return hashlib.sha256(xml_proba(CUI_F1, FIRMA).decode("utf-8").encode("utf-8")).hexdigest()


def mesaj_proba():
    return {"id": INDEX, "id_solicitare": SOLICITARE, "data_creare": DATA_CREARE, "tip": TIP}


class RaspunsControlat:
    """Răspunsul descărcării SPV, dat de test (status 200, ZIP cu factura și semnătura), ca forma răspunsului ANAF."""

    status_code = 200

    def __init__(self, continut):
        self.content = continut


def arhiva(xml):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr(INDEX + ".xml", xml)
        z.writestr("semnatura_" + INDEX + ".xml", b"<Semnatura>proba</Semnatura>")
    return b.getvalue()


def randuri(sql, schema):
    return [list(r) for r in sql('SELECT id, status, cif_emitent, cif_beneficiar, xml_sha256 FROM "%s".efactura_primite '
                                 "WHERE id_mesaj_anaf = %%s ORDER BY id" % schema, (INDEX,))]


def in_alte_firme(sql, schema):
    scheme = [r[0] for r in sql("SELECT table_schema FROM information_schema.tables WHERE table_name = 'efactura_primite' "
                                "AND table_schema ~ '^tenant_[0-9]+$' AND table_schema <> %s ORDER BY 1", (schema,))]
    return sum(sql('SELECT count(*) FROM "%s".efactura_primite WHERE id_mesaj_anaf = %%s' % s, (INDEX,))[0][0] for s in scheme)


def importa(monkeypatch, schema, cui):
    """Un mesaj al listei ANAF (răspuns controlat) prin importul aplicației; întoarce indexurile descărcate."""
    from core import db, spv_conector
    from core import efactura_send as efs
    from core import spv_receive as sr

    descarcate = []

    def descarca(principal, id_descarcare, mediu="test"):
        descarcate.append(str(id_descarcare))
        if str(id_descarcare) != INDEX:
            raise AssertionError("descărcare străină probei: %s" % id_descarcare)
        return RaspunsControlat(arhiva(xml_proba(CUI_F1, FIRMA)))

    monkeypatch.setattr(efs, "descarca", descarca)
    with db.get_conn() as conn:
        principal = spv_conector.principal_pentru_schema(conn, schema)
    mesaj = dict(mesaj_proba(), cif=cui)
    sr.importa_mesaj(schema, principal, cui, mesaj, defaultdict(int))
    return descarcate


def identitate(db):
    """Măsura descrie factura probei: mesajul, cererea, descărcarea, firma destinatară și XML-ul introdus, confruntate cu fixtura."""
    if db.get("raspuns") != RASPUNS:
        raise ValueError("Martorul nu declară răspunsul SPV controlat")
    if db.get("mesaj") != mesaj_proba():
        raise ValueError("Identitatea mesajului diferă de fixtură (id, cerere, dată, tip)")
    d = db.get("descarcari")
    if not isinstance(d, list) or not 1 <= len(d) <= 2 or any(x != INDEX for x in d):
        raise ValueError("Descărcările nu sunt ale mesajului probei")
    if db.get("cui_firma") != CUI_F1:
        raise ValueError("Firma destinatară diferă de fixtură (F1 %s)" % CUI_F1)
    if db.get("sha_xml") != sha_xml_proba():
        raise ValueError("SHA-ul declarat nu e al XML-ului probei")


def rand(lista):
    """Rândul unic al facturii probei sau None; un rând malformat face măsura incompletă."""
    if any(not isinstance(r, list) or len(r) != len(CAMPURI_RAND) for r in lista):
        raise ValueError("Martorul bazei de date e incomplet")
    return dict(zip(CAMPURI_RAND, lista[0])) if len(lista) == 1 else None


def analiza(date, dim):
    """Măsura unei dimensiuni -> {id: [condițiile căzute]}. Lipsa ecranului, o citire parțială sau o identitate străină nu
    constituie roșul prezis (ValueError)."""
    if set(date) != {"db", "ui"}:
        raise ValueError("Măsura nu are ambele familii de martori")
    db, ui = date["db"], date["ui"]
    if ui.get("viewport") != list(dim):
        raise ValueError("Rezoluție străină măsurii")
    for cheie in ("dupa_import", "dupa_reluare"):
        if not isinstance(db.get(cheie), list):
            raise ValueError("Martorul bazei de date e incomplet: " + cheie)
    if type(db.get("alte_firme")) is not int:
        raise ValueError("Martorul firmelor e incomplet")
    identitate(db)
    lista, fer = ui.get("lista"), ui.get("fereastra")
    if not isinstance(lista, dict) or not isinstance(fer, dict):
        raise ValueError("Ecranul nu a fost măsurat")
    if type(lista.get("butoane")) is not int or type(lista.get("vizibil")) is not bool or type(lista.get("clicabil")) is not bool \
            or not isinstance(lista.get("text"), str):
        raise ValueError("Lista nu a fost măsurată")
    if not isinstance(fer.get("titlu"), str) or not isinstance(fer.get("furnizor"), str) or type(fer.get("vizibil")) is not bool:
        raise ValueError("Fereastra de validare nu a fost măsurată")
    unu, doi = rand(db["dupa_import"]), rand(db["dupa_reluare"])
    rez = {i: [] for i in IDS}
    if unu is None:
        rez["e.1"].append("rand_import_%d" % len(db["dupa_import"]))
        rez["e.2"].append("rand_import_absent")
    else:
        if unu["stare"] != "ciorna":
            rez["e.1"].append("stare_import")
        if unu["beneficiar"] not in (CUI_F1, "RO" + CUI_F1):
            rez["e.1"].append("beneficiar_import")
        if unu["xml"] != sha_xml_proba():
            rez["e.1"].append("xml_import")
        if unu["emitent"] not in EMITENT_FORME:
            rez["e.2"].append("emitent_stocat")
        if fer["furnizor"] != "%s · %s" % (FURNIZOR, unu["emitent"]) or unu["emitent"] not in EMITENT_FORME:
            rez["e.2"].append("emitent_afisat")
    for cond, ok in (("lista_butoane", lista["butoane"] == 1), ("lista_vizibil", lista["vizibil"]), ("lista_clicabil", lista["clicabil"]),
                     ("lista_text", NUMAR in lista["text"]), ("titlu", NUMAR in fer["titlu"]), ("fereastra_vizibila", fer["vizibil"])):
        if not ok:
            rez["e.1"].append(cond)
    if doi is None:
        rez["e.3"].append("randuri_reluare_%d" % len(db["dupa_reluare"]))
    elif unu is not None:
        rez["e.3"] += ["reluare_" + c for c in CAMPURI_RAND if unu[c] != doi[c]]
    if db["alte_firme"] != 0:
        rez["e.3"].append("alte_firme")
    return rez


def valideaza(date, dim):
    return {i: not motive for i, motive in analiza(date, dim).items()}


def test_fundatie_17_5_C9(browser, capsys, monkeypatch):
    from conftest import BAZA, CAPTURI, Ecran, sesiune, sql
    from core.ceas_proba import MOMENT_REF
    from e2e_ferestre_17_5_Q5 import TOP, F1, firma, origine_proba

    origine_proba(BAZA)
    director = Path(CAPTURI) / LOT
    director.mkdir(parents=True, exist_ok=True)
    tenant = sql("SELECT schema_name, cui FROM public.tenants WHERE nume = %s", (F1,))
    assert F1 == FIRMA and len(tenant) == 1, "firma de probă F1 lipsește, e dublă sau are alt nume"
    schema, cui = tenant[0][0], cifre(tenant[0][1])
    assert re.fullmatch(r"tenant_[0-9]+", schema) and cui == CUI_F1, "identitatea firmei F1 diferă de fixtură"
    sql('DELETE FROM "%s".efactura_primite WHERE id_mesaj_anaf = %%s' % schema, (INDEX,))
    try:
        descarcate = importa(monkeypatch, schema, cui)
        dupa_import = randuri(sql, schema)
        descarcate += importa(monkeypatch, schema, cui)
        dupa_reluare = randuri(sql, schema)
        alte = in_alte_firme(sql, schema)
        martor_db = {"dupa_import": dupa_import, "dupa_reluare": dupa_reluare, "alte_firme": alte, "cui_firma": cui,
                     "sha_xml": sha_xml_proba(), "descarcari": descarcate, "raspuns": RASPUNS, "mesaj": mesaj_proba()}
        masuri = {i: {} for i in IDS}
        per_dim = []
        for w, h in DIM:
            z = f"{w}x{h}"
            ctx = browser.new_context(viewport={"width": w, "height": h})
            try:
                ctx.clock.set_fixed_time(MOMENT_REF)
                ctx.add_init_script(sesiune(CONT_PROBA))
                pg = ctx.new_page()
                Ecran(pg, "c9").acasa()
                firma(pg, F1, "#fa-facturi")
                pg.locator(TOP + "#fac-primite").click()
                pg.locator(TOP + "#fp-actiuni").wait_for(state="attached")
                sel = TOP + ".fac-primita-btn[data-id='%s']" % (dupa_import[0][0] if dupa_import else "lipsa")
                buton = pg.locator(sel)
                buton.first.wait_for(state="visible", timeout=20000)
                buton.first.scroll_into_view_if_needed()
                pg.evaluate("() => new Promise(ok => requestAnimationFrame(() => requestAnimationFrame(ok)))")
                lista = buton.first.evaluate("""el => {
                    const r = el.getBoundingClientRect(), p = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2);
                    return {text: el.innerText.trim(), vizibil: el.checkVisibility({checkOpacity: true, checkVisibilityCSS: true})
                              && r.width > 0 && r.height > 0, clicabil: !!p && el.contains(p)};
                }""")
                lista["butoane"] = buton.count()
                pg.screenshot(path=str(director / f"lista_{z}.png"))
                buton.first.click()
                camp = pg.locator(TOP + 'input[aria-label="Furnizor"]')
                camp.wait_for(state="visible", timeout=20000)
                camp.scroll_into_view_if_needed()
                pg.evaluate("() => new Promise(ok => requestAnimationFrame(() => requestAnimationFrame(ok)))")
                fer = camp.evaluate("""el => {
                    const f = el.closest('.fereastra'), r = el.getBoundingClientRect();
                    return {titlu: (f && f.querySelector('h2') ? f.querySelector('h2').innerText.trim() : ''),
                            furnizor: el.value, vizibil: el.checkVisibility({checkOpacity: true, checkVisibilityCSS: true})
                              && r.width > 0 && r.height > 0, trunchiat: el.scrollWidth > el.clientWidth,
                            titlu_camp: el.getAttribute('title') || ''};
                }""")
                pg.screenshot(path=str(director / f"validare_{z}.png"))
            finally:
                ctx.close()
            date = {"db": martor_db, "ui": {"viewport": [w, h], "lista": lista, "fereastra": fer}}
            per_dim.append(valideaza(date, (w, h)))
            for i, poza in zip(IDS, ("lista", "validare", "lista")):
                masuri[i][z] = date
                continut = (director / f"{poza}_{z}.png").read_bytes()
                (director / f"{i}_{z}.png").write_bytes(continut)
                if w == 1366:
                    (director / f"{i}.png").write_bytes(continut)
        (director / "masuri.json").write_text(json.dumps(masuri, ensure_ascii=False))
        for nume in ("erori.json", "partiale.json"):
            (director / nume).write_text("{}")
        with capsys.disabled():
            for i in IDS:
                print("VERDICT", i, "trece" if all(x[i] for x in per_dim) else "pica", flush=True)
        assert all(all(x.values()) for x in per_dim), "C9_EMITENT_SPV"
    finally:
        sql('DELETE FROM "%s".efactura_primite WHERE id_mesaj_anaf = %%s' % schema, (INDEX,))
