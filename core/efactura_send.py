# -*- coding: utf-8 -*-
"""
core/efactura_send.py — e-Factura TRIMITERE: generator XML UBL 2.1 / CIUS-RO (F126/F160).

PASUL 1 (FAZA constructie e-Factura): generator PUR de XML + loader pe schema CURENTA +
config host FCTEL intr-o singura constanta. NU face retea aici (upload/stare = pasul 2).

Reutilizeaza STRUCTURA XML dovedita in build-ul vechi (_efx_build_xml), dar:
  - loader rescris pe schema curenta (facturi.tert_*, factura_linii, firma_profil) -
    build-ul vechi citea dintr-un tabel `clienti` care nu mai exista;
  - rotunjire fiscala explicita (Decimal + ROUND_HALF_UP, regula iConta), nu round().

HOST-uri e-Factura (VERIFICAT LIVE 18.07 - trei metode, trei host-uri; DECIZII.md):
  - UPLOAD/stare/descarcare prin OAuth (Bearer)  -> api.anaf.ro/{prod|test}/FCTEL/rest
    (TLS standard, accepta token; DOVADA: 200 cu token, 401 fara).
  - VALIDARE structura (fara token/drept)         -> webservicesp.anaf.ro/prod/FCTEL/rest/validare/{std}
  - Metoda cu CERTIFICAT (mTLS)                    -> webserviceapl.anaf.ro (cere cert client;
    DOVADA: TLS handshake FAILURE fara certificat - inutilizabil server-side pe OAuth).
Corectie fata de nota 18.07 care pusese webserviceapl pentru upload (aia e ruta mTLS).
Fiecare host = o SINGURA constanta; upload/stare/descarcare o refolosesc, nu o rescriu.

[P7 · valul D2, 13.09.2026] STRAT: FISCAL_ENGINE, si de-acum chiar e unul. Loaderul,
orchestrarea trimiterii si cele 8 instructiuni SQL au trecut in `core/efactura_trimitere.py`
(use-case) si `core/repo_efactura.py` / `core/repo_tenants.py` (repository). Textul canonic,
`PLAN_HARDENING.md:845`: *un motor fiscal nu importa `db`*. Aici a ramas ce produce si ce
valideaza documentul: XML-ul UBL, validatorul de structura ANAF si invelisurile de apel.

LIMITELE v1 de aici au fost inchise (19.10.2026, C62 — comentariul vechi spunea inca altceva):
  - Cumparatorul: localitatea / judetul (BT-52 / BT-54) din `facturi.tert_oras` / `tert_judet` (core/migrare_efactura_adresa.py);
    la clientul roman fara ele, trimiterea le ia din ANAF (`efactura_trimitere.completeaza_client_ro`, C61).
  - Categoriile pe 0% (AE / E / K / G) si neplatitorul (O): mai jos, din categoria liniei (274b). Stornarea: factura cu valorile
    cu minus si trimiterea la factura stornata (BG-3, 417), `stare=ok` pe validatorul FACT1.

[punctul 3, 03.10.2026] FACTURA EMISA PE BAZA BONULUI FISCAL -> InvoiceTypeCode 751 + mentiunea in BT-22. Sursa:
Ministerul Finantelor, „Ghid de utilizare a codurilor dedicate tipurilor de facturi … RO e-Factura” v2.9 (static.anaf.ro),
pct.2.5: „Factura informativă în scop contabile este emisă în conformitate cu art. 319 alin. (10) lit a-c) … utilizând
pentru sistemul național de facturare electronică RO e-Factura Codul 751”; folosita pentru „Evidența livrărilor bazate pe
bonuri fiscale …”; „Documentul va include clar mențiunea privind documentele ce au stat la baza livrării anterioare (ex.
«Factura încasată cu bon fiscal ….»”. Cu 380, vanzarea ar ajunge la ANAF a doua oara (o data prin casa de marcat).
Definitia „din bon”: core.facturi.e_din_bon_fiscal. Pana azi: 380 pe orice factura.
"""

#: [punctul 3] BT-3 pentru factura emisa pe baza bonului fiscal (Ghidul MF v2.9 pct.2.5) si pentru factura obisnuita
INVOICE_TYPE_INFORMATIVA_BON, INVOICE_TYPE_FACTURA = "751", "380"
import re
import unicodedata
from decimal import Decimal, ROUND_HALF_UP
from xml.sax.saxutils import escape as _xml_escape

from core.common import cfg, cate as _cate
from core import erori as _erori

# ============================================================
#  CONFIG HOST — env citit LA APEL (cfg), o singura sursa per host
# ============================================================
def fctel_base(mode="prod"):
    """Baza REST e-Factura (OAuth) pentru mode 'prod'/'test'. SINGURA sursa a host-ului.
    Host din EFACTURA_FCTEL_BASE (implicit api.anaf.ro/%s/FCTEL/rest), citit la apel."""
    mode = (mode or "prod").strip().lower()
    if mode not in ("prod", "test"):
        mode = "prod"
    return cfg("EFACTURA_FCTEL_BASE", "https://api.anaf.ro/%s/FCTEL/rest") % mode


def fctel_validare_url(standard="FACT1"):
    """URL validator de structura (schematron CIUS-RO), FARA token. SINGURA sursa.
    Din EFACTURA_VALIDARE_URL (implicit webservicesp.anaf.ro/.../validare/%s), citit la apel."""
    return cfg("EFACTURA_VALIDARE_URL",
               "https://webservicesp.anaf.ro/prod/FCTEL/rest/validare/%s") % standard


# CIUS-RO: structura romaneasca peste EN16931 (valoare din build vechi, de confirmat pe TEST)
CUSTOMIZATION_ID = "urn:cen.eu:en16931:2017#compliant#urn:efactura.mfinante.ro:CIUS-RO:1.0.1"

_D0 = Decimal("0.00")

# Judet -> cod ISO 3166-2:RO (cbc:CountrySubentity)
_JUD = {
    "alba": "RO-AB", "arad": "RO-AR", "arges": "RO-AG", "bacau": "RO-BC", "bihor": "RO-BH",
    "bistrita-nasaud": "RO-BN", "bistrita nasaud": "RO-BN", "botosani": "RO-BT", "braila": "RO-BR",
    "brasov": "RO-BV", "bucuresti": "RO-B", "buzau": "RO-BZ", "calarasi": "RO-CL",
    "caras-severin": "RO-CS", "caras severin": "RO-CS", "cluj": "RO-CJ", "constanta": "RO-CT",
    "covasna": "RO-CV", "dambovita": "RO-DB", "dolj": "RO-DJ", "galati": "RO-GL", "giurgiu": "RO-GR",
    "gorj": "RO-GJ", "harghita": "RO-HR", "hunedoara": "RO-HD", "ialomita": "RO-IL", "iasi": "RO-IS",
    "ilfov": "RO-IF", "maramures": "RO-MM", "mehedinti": "RO-MH", "mures": "RO-MS", "neamt": "RO-NT",
    "olt": "RO-OT", "prahova": "RO-PH", "salaj": "RO-SJ", "satu mare": "RO-SM", "sibiu": "RO-SB",
    "suceava": "RO-SV", "teleorman": "RO-TR", "timis": "RO-TM", "tulcea": "RO-TL", "valcea": "RO-VL",
    "vaslui": "RO-VS", "vrancea": "RO-VN",
}
_CODURI_JUD = {v[3:] for v in _JUD.values()}

# UM iConta -> cod UN/ECE Rec 20
_UM = {
    "buc": "H87", "bucata": "H87", "bucati": "H87", "ora": "HUR", "ore": "HUR", "h": "HUR",
    "kg": "KGM", "g": "GRM", "l": "LTR", "litru": "LTR", "ml": "MLT", "m": "MTR", "mp": "MTK",
    "m2": "MTK", "mc": "MTQ", "m3": "MTQ", "km": "KMT", "luna": "MON", "luni": "MON", "zi": "DAY",
    "zile": "DAY", "set": "SET", "pereche": "PR", "kwh": "KWH", "to": "TNE", "tona": "TNE",
    # [deficiența 331, 18.10.2026] serviciul: E48 („service unit”). Verificat 18.10.2026 la validatorul ANAF FACT1: E48 trece fără eroare,
    # „BUC” dă BR-CL-23 (calibrare)
    "serv": "E48", "serv.": "E48", "serviciu": "E48", "servicii": "E48",
}


def _norm(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.strip().lower()


def _jud(judet):
    n = _norm(judet)
    if not n:
        return ""
    v = _JUD.get(n)
    if v:
        return v
    u = n.upper().replace(" ", "")
    if u.startswith("RO-"):
        u = u[3:]
    return ("RO-" + u) if u in _CODURI_JUD else ""


_SECTOR_RE = re.compile(r"sector\s*([1-6])", re.IGNORECASE)


class EDateIncomplete(_erori.RefuzGenerare):
    """Date de factura insuficiente pentru un XML valid (ex. sector Bucuresti lipsa).
    Butonul de trimitere blocheaza cu mesajul asta, NU trimite structura falsa.
    [lotul 10, C69] `ecran` / `camp_ecran`: unde se completează (datele firmei -> „date_firma”). E un `core.erori.RefuzGenerare`
    (rămâne `ValueError`): același corp tipat al refuzului (`detaliu`, afirmație `neconformitate`), nu o copie a lui."""

    TIP = "factură e-Factura"

    def __init__(self, mesaj, ecran=None, camp_ecran=None):
        super().__init__(mesaj, ecran=ecran, camp_ecran=camp_ecran)


#: [lotul 10, deficiența C69 — „valoare inventată pe documentul ANAF în loc de blocaj”] Câmpurile părților pe care generatorul le
#: completa cu „-” și pe care CIUS-RO le cere. Sursa: validatorul ANAF FACT1 (schematron CIUS-RO), probat 20.10.2026 pe XML sintetic
#: din care s-a scos câte un element (scratchpad N2/p_fact1.out): „[BR-RO-080]-Adresa Vanzatorului - Linia 1 (BT-35) trebuie
#: furnizata”, „[BR-RO-080]-Adresa Cumparatorului - Linia 1 (BT-50) trebuie furnizata” (cod BR-RO-082), „[BR-RO-090]-Localitatea
#: Vanzatorului (BT-37) trebuie furnizata” (BR-RO-091), „[BR-RO-090]-Localitatea Cumparatorului (BT-52) trebuie furnizata” (BR-RO-092),
#: „[BR-06]-An Invoice shall contain the Seller name (BT-27)”, „[BR-07]-An Invoice shall contain the Buyer name (BT-44)”. Cu „-”
#: FACT1 răspunde „ok” la toate șase — deci numai blocajul de aici oprește o factură cu date inventate.
#: (parte, cheie, ce lipsește, regula, câmpul din Date firmă pentru vânzător)
CAMPURI_PARTI_CERUTE = (
    ("vanzator", "nume", "denumirea firmei", "BR-06 (BT-27)", "df-nume-portofoliu"),
    ("vanzator", "adresa", "adresa firmei (strada)", "BR-RO-080 (BT-35)", "df-adresa"),
    ("vanzator", "oras", "localitatea firmei", "BR-RO-090 (BT-37)", "df-oras"),
    ("cumparator", "nume", "denumirea clientului", "BR-07 (BT-44)", None),
    ("cumparator", "adresa", "adresa clientului (strada)", "BR-RO-082 (BT-50)", None),
    ("cumparator", "oras", "localitatea clientului", "BR-RO-092 (BT-52)", None),
)


def cere_partile(furnizor, client):
    """Refuzul (`EDateIncomplete`) când lipsește un câmp cerut al vânzătorului sau al cumpărătorului — numit, cu locul de completare.
    În București localitatea se poate scrie și numai în adresă („Sector 2”): `_localitate` o derivă de acolo (BR-RO-100)."""
    lipsa_v, lipsa_c = [], []
    for parte, cheie, ce, regula, camp in CAMPURI_PARTI_CERUTE:
        d = furnizor if parte == "vanzator" else client
        v = str(d.get(cheie) or "").strip()
        if cheie == "oras" and not v and _jud(d.get("judet")) == "RO-B" and _SECTOR_RE.search(str(d.get("adresa") or "")):
            v = "sector din adresă"
        if not v:
            (lipsa_v if parte == "vanzator" else lipsa_c).append((ce, regula, camp))
    if lipsa_v:
        raise EDateIncomplete(
            "Factura nu se poate trimite în e-Factura: lipsesc %s — ANAF le cere (regulile %s). Completează-le în Date firmă; factura nu "
            "pleacă cu „-” în locul lor." % (", ".join(c for c, _r, _k in lipsa_v), ", ".join(r for _c, r, _k in lipsa_v)),
            ecran="date_firma", camp_ecran=lipsa_v[0][2])
    if lipsa_c:
        raise EDateIncomplete(
            "Factura nu se poate trimite în e-Factura: pe factură lipsesc %s — ANAF le cere (regulile %s). Factura nu pleacă cu „-” în "
            "locul lor; completează datele clientului pe factură." % (", ".join(c for c, _r, _k in lipsa_c),
                                                                     ", ".join(r for _c, r, _k in lipsa_c)))


def _localitate(judet_code, oras, adresa="", eticheta="firma"):
    """CityName (BT-37 vanzator / BT-52 cumparator). eFactura regula BR-RO-100 (validator ANAF):
    in Bucuresti (RO-B) localitatea trebuie sa fie SECTOR1..6, NU 'Bucuresti'. In rest = orasul.
    STRICT (funcționalitatea F160): daca e Bucuresti dar NU se extrage clar sectorul din oras+adresa, NU
    inventa unul -> ridica EDateIncomplete. Sector gresit derivat = nok sau, mai rau, factura
    acceptata cu date gresite. Filozofia control_incrucisat: gri (nu pot determina) nu se
    falsifica in verde."""
    if judet_code == "RO-B":
        m = _SECTOR_RE.search("%s %s" % (oras or "", adresa or ""))
        if m:
            return "SECTOR" + m.group(1)
        raise EDateIncomplete(
            "Localitate incompletă (%s): firma e în București dar lipsește sectorul "
            "(SECTOR1..6) în adresa. Completează sectorul înainte de trimitere." % eticheta)
    if not str(oras or "").strip():   # [lotul 10, C69] BR-RO-090: era „-”; `cere_partile` a oprit deja lipsa
        raise EDateIncomplete("Localitate lipsă (%s): e-Factura o cere (regula ANAF BR-RO-090); nu se scrie „-”." % eticheta)
    return oras


def _um(um):
    return _UM.get(_norm(um)) or "C62"


def _D(x):
    return Decimal(str(x if x not in (None, "") else 0))


def _bani(x):
    """Rotunjire fiscala: 2 zecimale, ROUND_HALF_UP (regula iConta, nu round())."""
    return _D(x).quantize(_D("0.01"), rounding=ROUND_HALF_UP)


def _num(x):
    return str(_bani(x))


def _e(s):
    return _xml_escape(str(s)) if s is not None else ""


def _vatid(cui):
    """CUI -> RO+cifre (identificator VAT, pentru platitor TVA)."""
    digits = "".join(ch for ch in str(cui or "") if ch.isdigit())
    return ("RO" + digits) if digits else ""


# ============================================================
#  GENERATOR XML — PUR (fara DB/retea)
# ============================================================
def genereaza_xml(factura, linii, furnizor, client):
    """
    Construieste XML-ul UBL 2.1 / CIUS-RO dintr-o factura + linii + emitent + cumparator.
    Pur: nu atinge DB/retea. Rotunjire fiscala ROUND_HALF_UP. Vezi LIMITE v1 in docstring.
    """
    moneda = (factura.get("moneda") or "RON").strip() or "RON"
    # [05.10.2026] numărul facturii emise conține deja seria — compus „serie + număr” ieșea „FCTFCT12” (BT-1 ≠ PDF)
    from core import pdf_util as _pu
    numar_complet = _pu.numar_cu_serie(factura.get("serie"), factura.get("numar"))

    # --- calcule pe linii, grupate pe (categorie, cota) ---
    # [274b, 16.10.2026] categoria de TVA a liniei (BT-151) vine din `core/categorii_tva` (decizia Costin 16.10.2026; Ghidul MF e-Factura
    # v2.9 cap.3): S pe cota pozitivă; pe 0%: AE / E / K / G din categoria liniei, cu motivul scutirii (BT-120) și codul VATEX (BT-121)
    # pe defalcarea TVA; O pe toată factura unui neplătitor (fără cota, fără codurile de TVA ale părților — ghidul, regulile BG-23).
    # O linie cu 0% de dinainte de categorie (NULL) rămâne „Z”, ca până acum.
    from core import categorii_tva as _ct
    from core import tva_calcul as _tc
    neplatitor = not furnizor.get("platitor_tva")
    line_net = []
    grup = {}  # (cat, cota, motiv, vatex) -> baza
    for l in linii:
        cota = _D(l.get("cota_tva") if l.get("cota_tva") is not None else 0)
        # BR-DEC-23 (regula unică, `core/tva_calcul.py`); [lotul 11, C86] valoarea netă scrisă pe linie (`factura_linii.valoare_neta`: stornarea
        # unei facturi venite din XML poartă −BT-131 al originalului), ca BT-131 trimis să fie cel din contabilitate, nu cantitate × preț
        net = _tc.net_linie(l.get("cantitate"), l.get("pret_unitar"), l.get("valoare_neta"))
        if neplatitor:
            d = _ct.NEPLATITOR
        elif cota > 0:
            d = {"ubl": "S", "mentiune": None, "vatex": None}
        else:
            d = _ct.descriere(l.get("categorie_tva"), client.get("tara")) or {"ubl": "Z", "mentiune": None, "vatex": None}
        cheie = (d["ubl"], cota, d.get("mentiune"), d.get("vatex"))
        line_net.append((l, cota, net, cheie))
        grup[cheie] = grup.get(cheie, _D0) + net

    line_ext = _bani(sum((n for _, _, n, _ in line_net), _D0))
    tax_subtotals = []
    tax_total = _D0
    for cheie, baza in grup.items():
        cat, cota, motiv, vatex = cheie
        taxa = _tc.tva_din_baza(baza, cota)   # BR-CO-17: o rotunjire pe cotă (regula unică, decizia Costin 10.3)
        tax_total += taxa
        tax_subtotals.append((_bani(baza), taxa, cat, cota, motiv, vatex))
    tax_total = _bani(tax_total)
    tax_incl = _bani(line_ext + tax_total)

    sup_vat = _vatid(furnizor.get("cui")) if furnizor.get("platitor_tva") else ""
    tara_cli = (client.get("tara") or "RO").strip().upper() or "RO"
    # [274b] O („nu face obiectul TVA”): factura NU conține codul de TVA al cumpărătorului (ghidul MF v2.9, reguli BG-23); pentru un
    # client străin codul de TVA e chiar al lui (prefixul țării), nu „RO” + cifre
    from core.d390 import TARI_UE as _UE
    # [lotul 11, semnalat de subagentul P] BT-48 e „identificatorul de TVA al Cumpărătorului” — EN 16931 BR-CO-09: „the Buyer VAT identifier
    # (BT-48) shall have a prefix in accordance with ISO code ISO 3166-1 alpha-2”; un client român NEînregistrat în scopuri de TVA n-are
    # cod de TVA, deci „RO” + cifre ar fi un cod fals. CF art.319 alin.(20) lit.f) cere „codul de înregistrare în scopuri de TVA SAU codul
    # de identificare fiscală al beneficiarului”: la clientul român BT-48 numai când e plătitor de TVA (statutul înghețat pe factură la
    # emitere, `facturi.tert_platitor_tva`); altfel (neplătitor sau statut necunoscut) CUI-ul fără „RO” la BT-47 (RO_CIUS BR-RO-120).
    # Înainte: „RO” + cifre oricărui client român.
    if neplatitor or (tara_cli != "RO" and tara_cli not in _UE):
        cli_vat = ""
    elif tara_cli == "RO":
        cli_vat = _vatid(client.get("cui")) if client.get("platitor_tva") is True else ""
    else:
        cli_vat = "".join(ch for ch in str(client.get("cui") or "").upper() if ch.isalnum())
    sup_jud = _jud(furnizor.get("judet"))
    cere_partile(furnizor, client)   # [lotul 10, C69] numele, strada, localitatea părților: cerute, nu „-”
    # [lotul 10, C69, generalizarea clasei] numele articolului (BT-153, validatorul FACT1, probat 20.10.2026: „[BR-25]-Each Invoice line (BG-25) shall contain the Item name (BT-153).”)
    # era `descriere or "-"`; emiterea îl cere deja (`facturi_api`), deci un rând fără el e o factură veche / importată — se numește
    _fara_den = [str(i) for i, l in enumerate(linii, start=1) if not str(l.get("descriere") or "").strip()]
    if _fara_den:
        raise EDateIncomplete("Factura nu se poate trimite în e-Factura: %s fără denumirea articolului (rândul %s) — ANAF o cere "
                              "(regula BR-25, BT-153); factura nu pleacă cu „-” în locul ei." % (
                                  "un rând e" if len(_fara_den) == 1 else _cate(len(_fara_den), "rând", "rânduri") + " sunt",
                                  ", ".join(_fara_den)))

    P = []
    P.append('<?xml version="1.0" encoding="UTF-8"?>')
    P.append('<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
             'xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" '
             'xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">')
    P.append('<cbc:CustomizationID>%s</cbc:CustomizationID>' % CUSTOMIZATION_ID)
    P.append('<cbc:ID>%s</cbc:ID>' % _e(numar_complet))
    P.append('<cbc:IssueDate>%s</cbc:IssueDate>' % _e(factura.get("data_emitere")))
    if factura.get("data_scadenta"):
        P.append('<cbc:DueDate>%s</cbc:DueDate>' % _e(factura.get("data_scadenta")))
    from core import facturi as _fc
    din_bon = _fc.e_din_bon_fiscal(factura)
    P.append('<cbc:InvoiceTypeCode>%s</cbc:InvoiceTypeCode>'
             % (INVOICE_TYPE_INFORMATIVA_BON if din_bon else INVOICE_TYPE_FACTURA))
    if din_bon:   # BT-22 (Ghidul MF v2.9 pct.2.5: mentiunea documentului care a stat la baza livrarii)
        P.append('<cbc:Note>%s</cbc:Note>' % _e("Factura încasată cu bon fiscal — " + _fc.mentiune_bon(factura)))
    storno = _fc.mentiune_storno(factura)
    if storno:   # [deficiența 417] BT-22: mențiunea de pe PDF (CF art.330 alin.(1) lit.b)
        P.append('<cbc:Note>%s</cbc:Note>' % _e(storno))
    if factura.get("tva_la_incasare"):
        # [lotul 10, deficiența 428] BT-22: mențiunea obligatorie CF art.319 alin.(20) lit.p), „TVA la încasare”. Locul ei, din ghidul MF
        # (anaf_surse/mf_ghid_coduri_facturi_efactura_v2_9.txt): „Conform RO_CIUS: În Comentariu (BT-22) se trec orice mențiuni obligatoriu
        # a fi înscrise în facturi potrivit legislației în vigoare, necuprinse în altă parte [...] ca de exemplu: [...] «TVA la încasare»”
        from core import tva_incasare as _tvi
        P.append('<cbc:Note>%s</cbc:Note>' % _e(_tvi.MENTIUNE))
    P.append('<cbc:DocumentCurrencyCode>%s</cbc:DocumentCurrencyCode>' % _e(moneda))
    if storno:
        # [417] BG-3 „Referință la o factură anterioară”: BT-25 numărul (ca în BT-1 al ei) și BT-26 data facturii stornate. Locul în UBL:
        # după DocumentCurrencyCode, înaintea părților (ordinea schemei Invoice-2)
        o = factura["storno_din"]
        P.append('<cac:BillingReference><cac:InvoiceDocumentReference><cbc:ID>%s</cbc:ID><cbc:IssueDate>%s</cbc:IssueDate>'
                 '</cac:InvoiceDocumentReference></cac:BillingReference>'
                 % (_e(_pu.numar_cu_serie(o.get("serie"), o.get("numar"))), _e(str(o.get("data_emitere"))[:10])))

    # --- Furnizor (emitent) ---
    P.append('<cac:AccountingSupplierParty><cac:Party>')
    P.append('<cac:PostalAddress>')
    P.append('<cbc:StreetName>%s</cbc:StreetName>' % _e(furnizor.get("adresa")))
    P.append('<cbc:CityName>%s</cbc:CityName>' % _e(_localitate(sup_jud, furnizor.get("oras"), furnizor.get("adresa"), "vanzator")))
    if furnizor.get("cod_postal"):
        P.append('<cbc:PostalZone>%s</cbc:PostalZone>' % _e(furnizor.get("cod_postal")))
    if sup_jud:
        P.append('<cbc:CountrySubentity>%s</cbc:CountrySubentity>' % sup_jud)
    P.append('<cac:Country><cbc:IdentificationCode>RO</cbc:IdentificationCode></cac:Country>')
    P.append('</cac:PostalAddress>')
    if sup_vat:
        P.append('<cac:PartyTaxScheme><cbc:CompanyID>%s</cbc:CompanyID>'
                 '<cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:PartyTaxScheme>' % _e(sup_vat))
    P.append('<cac:PartyLegalEntity>')
    P.append('<cbc:RegistrationName>%s</cbc:RegistrationName>' % _e(furnizor.get("nume")))
    if not sup_vat and furnizor.get("cui"):
        # [274b] vânzătorul fără cod de TVA (neplătitor): ANAF îl identifică după CUI în BT-30 („Nu a fost identificat cui vanzator”
        # cu numărul de la Registrul Comerțului acolo — validatorul FACT1, 16.10.2026)
        P.append('<cbc:CompanyID>%s</cbc:CompanyID>' % _e("".join(ch for ch in str(furnizor.get("cui")) if ch.isdigit())))
    elif furnizor.get("reg_com"):
        P.append('<cbc:CompanyID>%s</cbc:CompanyID>' % _e(furnizor.get("reg_com")))
    P.append('</cac:PartyLegalEntity>')
    P.append('</cac:Party></cac:AccountingSupplierParty>')

    # --- Cumparator --- (BT-52 oras, BT-54 judet - obligatorii pt RO, vezi eFactura regula BR-RO-110 / eFactura regula BR-RO-100)
    cli_jud = _jud(client.get("judet"))
    P.append('<cac:AccountingCustomerParty><cac:Party>')
    P.append('<cac:PostalAddress>')
    P.append('<cbc:StreetName>%s</cbc:StreetName>' % _e(client.get("adresa")))
    P.append('<cbc:CityName>%s</cbc:CityName>' % _e(_localitate(cli_jud, client.get("oras"), client.get("adresa"), "cumparator")))
    if client.get("cod_postal"):
        P.append('<cbc:PostalZone>%s</cbc:PostalZone>' % _e(client.get("cod_postal")))
    if cli_jud and tara_cli == "RO":
        P.append('<cbc:CountrySubentity>%s</cbc:CountrySubentity>' % cli_jud)
    P.append('<cac:Country><cbc:IdentificationCode>%s</cbc:IdentificationCode></cac:Country>' % _e(tara_cli))
    P.append('</cac:PostalAddress>')
    if cli_vat:
        P.append('<cac:PartyTaxScheme><cbc:CompanyID>%s</cbc:CompanyID>'
                 '<cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:PartyTaxScheme>' % _e(cli_vat))
    P.append('<cac:PartyLegalEntity>')
    P.append('<cbc:RegistrationName>%s</cbc:RegistrationName>' % _e(client.get("nume")))
    if not cli_vat and client.get("cui"):
        # [274b] fără cod de TVA al cumpărătorului (O; client din afara UE): identificatorul legal BT-47 (RO_CIUS BR-RO-120)
        P.append('<cbc:CompanyID>%s</cbc:CompanyID>' % _e(_vatid(client.get("cui"))[2:] if tara_cli == "RO" else
                                                           "".join(ch for ch in str(client.get("cui")).upper() if ch.isalnum())))
    P.append('</cac:PartyLegalEntity>')
    P.append('</cac:Party></cac:AccountingCustomerParty>')

    # --- Delivery (BT-72, BT-80) --- [274b] livrarea intracomunitară (K) cere data livrării și țara de livrare (EN 16931 BR-IC-11,
    # BR-IC-12). Data = data faptului generator când e pe factură, altfel data emiterii: CF art.319 alin.(20) lit.e cere data livrării pe
    # factură numai „dacă această dată diferă de data emiterii facturii”.
    # RO_CIUS cere, odată ce adresa de livrare există, strada, localitatea și subdiviziunea țării (BR-RO-180 / 200 / 210): se iau din
    # adresa clientului; lipsa lor se spune, nu se ghicește.
    if any(c[0] == "K" for c in grup):
        if not (client.get("adresa") and client.get("oras") and client.get("judet")):
            raise EDateIncomplete(
                "Livrarea intracomunitară cere în XML adresa de livrare completă (regulile ANAF BR-RO-180, BR-RO-200, BR-RO-210): adresa, "
                "localitatea și regiunea clientului. Completează-le pe factură (Localitatea, Regiunea) înainte de trimitere.")
        P.append('<cac:Delivery><cbc:ActualDeliveryDate>%s</cbc:ActualDeliveryDate><cac:DeliveryLocation><cac:Address>'
                 '<cbc:StreetName>%s</cbc:StreetName><cbc:CityName>%s</cbc:CityName><cbc:CountrySubentity>%s</cbc:CountrySubentity>'
                 '<cac:Country><cbc:IdentificationCode>%s</cbc:IdentificationCode></cac:Country></cac:Address></cac:DeliveryLocation>'
                 '</cac:Delivery>' % (_e(factura.get("data_faptului_generator") or factura.get("data_emitere")), _e(client.get("adresa")),
                                      _e(client.get("oras")), _e(client.get("judet")), _e(tara_cli)))

    # --- PaymentMeans (IBAN) ---
    if furnizor.get("iban"):
        P.append('<cac:PaymentMeans><cbc:PaymentMeansCode>30</cbc:PaymentMeansCode>'
                 '<cac:PayeeFinancialAccount><cbc:ID>%s</cbc:ID></cac:PayeeFinancialAccount>'
                 '</cac:PaymentMeans>' % _e(furnizor.get("iban")))

    # --- TaxTotal ---
    P.append('<cac:TaxTotal>')
    P.append('<cbc:TaxAmount currencyID="%s">%s</cbc:TaxAmount>' % (moneda, _num(tax_total)))
    for baza, taxa, cat, cota, motiv, vatex in tax_subtotals:
        P.append('<cac:TaxSubtotal>')
        P.append('<cbc:TaxableAmount currencyID="%s">%s</cbc:TaxableAmount>' % (moneda, _num(baza)))
        P.append('<cbc:TaxAmount currencyID="%s">%s</cbc:TaxAmount>' % (moneda, _num(taxa)))
        P.append('<cac:TaxCategory><cbc:ID>%s</cbc:ID>%s%s%s'
                 '<cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:TaxCategory>'
                 % (cat, "" if cat == "O" else "<cbc:Percent>%s</cbc:Percent>" % _num(cota),
                    "<cbc:TaxExemptionReasonCode>%s</cbc:TaxExemptionReasonCode>" % _e(vatex) if vatex else "",
                    "<cbc:TaxExemptionReason>%s</cbc:TaxExemptionReason>" % _e(motiv) if motiv else ""))
        P.append('</cac:TaxSubtotal>')
    P.append('</cac:TaxTotal>')

    # --- LegalMonetaryTotal ---
    P.append('<cac:LegalMonetaryTotal>')
    P.append('<cbc:LineExtensionAmount currencyID="%s">%s</cbc:LineExtensionAmount>' % (moneda, _num(line_ext)))
    P.append('<cbc:TaxExclusiveAmount currencyID="%s">%s</cbc:TaxExclusiveAmount>' % (moneda, _num(line_ext)))
    P.append('<cbc:TaxInclusiveAmount currencyID="%s">%s</cbc:TaxInclusiveAmount>' % (moneda, _num(tax_incl)))
    P.append('<cbc:PayableAmount currencyID="%s">%s</cbc:PayableAmount>' % (moneda, _num(tax_incl)))
    P.append('</cac:LegalMonetaryTotal>')

    # --- Linii ---
    for idx, (l, cota, net, cheie) in enumerate(line_net, start=1):
        cat = cheie[0]
        P.append('<cac:InvoiceLine>')
        P.append('<cbc:ID>%d</cbc:ID>' % idx)
        P.append('<cbc:InvoicedQuantity unitCode="%s">%s</cbc:InvoicedQuantity>'
                 % (_um(l.get("um")), _e(l.get("cantitate"))))
        P.append('<cbc:LineExtensionAmount currencyID="%s">%s</cbc:LineExtensionAmount>' % (moneda, _num(net)))
        P.append('<cac:Item><cbc:Name>%s</cbc:Name>' % _e(l.get("descriere")))   # [C69] cerută mai sus, nu „-”
        P.append('<cac:ClassifiedTaxCategory><cbc:ID>%s</cbc:ID>%s'
                 '<cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:ClassifiedTaxCategory>'
                 % (cat, "" if cat == "O" else "<cbc:Percent>%s</cbc:Percent>" % _num(cota)))
        P.append('</cac:Item>')
        P.append('<cac:Price><cbc:PriceAmount currencyID="%s">%s</cbc:PriceAmount></cac:Price>'
                 % (moneda, _num(l.get("pret_unitar"))))
        P.append('</cac:InvoiceLine>')

    P.append('</Invoice>')
    return "\n".join(P)


def valideaza(xml, standard="FACT1"):
    """
    Valideaza STRUCTURA XML pe validatorul oficial ANAF (schematron CIUS-RO), FARA token si
    FARA drept pe CIF - validare pura, publica. E judecatorul de structura (ca DUK pentru
    declaratii): sursa de adevar, nu presupunerea din memorie. Intoarce (ok: bool, mesaje: list).
    Apel direct (nu apel_anaf): endpoint fara autentificare, nu e un apel SPV.
    """
    import requests
    r = requests.post(fctel_validare_url(standard), data=xml.encode("utf-8"),
                      headers={"Content-Type": "text/plain"}, timeout=45)
    try:
        j = r.json()
    except ValueError:
        return False, ["raspuns non-JSON de la validator: %s" % (r.text or "")[:400]]
    ok = (j.get("stare") == "ok")
    mesaje = [m.get("message", "") for m in (j.get("Messages") or [])]
    return ok, mesaje


# ============================================================
#  TRIMITERE SPV — prin apel_anaf (pasul 2). TOATE apelurile ANAF trec prin conector.
# ============================================================
from core import spv_conector


def _parse_upload(text):
    """Din raspunsul XML al /upload: (execution_status, index_incarcare, [errorMessage...])."""
    t = text or ""
    ex = re.search(r'ExecutionStatus="(\d+)"', t)
    idx = re.search(r'index_incarcare="(\d+)"', t)
    errs = re.findall(r'errorMessage="([^"]*)"', t)
    return (int(ex.group(1)) if ex else None,
            idx.group(1) if idx else None, errs)


def _parse_stare(text):
    """Din raspunsul /stareMesaj: (stare, id_descarcare)."""
    t = text or ""
    st = re.search(r'stare="([^"]*)"', t)
    idd = re.search(r'id_descarcare="(\d+)"', t)
    return (st.group(1) if st else None, idd.group(1) if idd else None)


def e_identificare_cumparator(mesaj):
    """[274b] Mesajul validatorului care spune numai că cumpărătorul nu e un contribuabil român („ERRIdentif — nu a fost identificat
    cui cumparator”) — la un cumpărător din afara României îl rezolvă `extern=DA` la încărcare."""
    m = (mesaj or "").lower()
    return "errident" in m and "cumparator" in m


def upload_ubl(principal, cif, xml, mediu="test", extern=False):
    """POST /upload?standard=UBL&cif=X prin apel_anaf (pe tokenul principalului). Intoarce Response.
    [274b] `extern=DA` când cumpărătorul e din afara României (MF, „Prezentare servicii web e-Factura”: parametrul „se completeaza doar
    in cazul in care cumparatorul este din exteriorul Romaniei (nu are CUI sau NIF)”)."""
    url = "%s/upload?standard=UBL&cif=%s%s" % (fctel_base(mediu), cif, "&extern=DA" if extern else "")
    return spv_conector.apel_anaf(principal, "POST", url, data=xml.encode("utf-8"),
                                  headers={"Content-Type": "application/xml"}, timeout=60)


def stare_mesaj(principal, index_incarcare, mediu="test"):
    """GET /stareMesaj?id_incarcare=N prin apel_anaf. Intoarce Response."""
    url = "%s/stareMesaj?id_incarcare=%s" % (fctel_base(mediu), index_incarcare)
    return spv_conector.apel_anaf(principal, "GET", url, timeout=30)


def descarca(principal, id_descarcare, mediu="test"):
    """GET /descarcare?id=N prin apel_anaf. Intoarce Response (ZIP in .content).
    Partajata intre F178 (poll recipise) si primirea F126 (facturi furnizori) - un singur client."""
    url = "%s/descarcare?id=%s" % (fctel_base(mediu), id_descarcare)
    return spv_conector.apel_anaf(principal, "GET", url, timeout=120)


def lista_mesaje(principal, cif, mediu="test", zile=3, filtru="P"):
    """
    GET listaMesajeFactura?zile=N&cif=X&filtru=F prin apel_anaf (pe tokenul principalului).
    Intoarce (mesaje, eroare): mesaje = lista de dict-uri cu campurile ANAF (id = id de descarcare,
    id_solicitare = indexul incarcarii, data_creare, tip, cif_emitent, cif_beneficiar, detalii);
    eroare = textul din campul 'eroare' (ex. fara mesaje / fara drept) sau None.

    Parametri VERIFICATI LA SURSA OFICIALA (mfinante.gov.ro, doc API e-Factura; vezi ARHITECTURA_SPV.md):
      - zile: 1..60 OBLIGATORIU (fereastra); cif: numeric OBLIGATORIU.
      - filtru (optional): E=erori, T=trimisa, P=PRIMITA (facturi de la furnizori), R=mesaj cumparator.
    Limita: listaMesajeFactura = 1500 apeluri/zi/CUI.

    GARD PENTRU APELANT (cron receive, la construcTie): filtru=P intoarce ce a marcat ANAF ca 'primita',
    dar dedup+import TREBUIE sa confirme cif_beneficiar == CIF-ul tenantului (nu doar tip=P). Pe un token
    de cabinet care acopera N CIF-uri, factura importata se leaga de tenantul al carui CIF e cif_beneficiar,
    nu de primul din bucla - altfel scurgere intre chiriasi.
    """
    zile = max(1, min(int(zile), 60))
    cifn = "".join(c for c in str(cif) if c.isdigit())
    url = "%s/listaMesajeFactura?zile=%d&cif=%s&filtru=%s" % (fctel_base(mediu), zile, cifn, filtru)
    r = spv_conector.apel_anaf(principal, "GET", url, timeout=60)
    try:
        j = r.json()
    except ValueError:
        return [], "raspuns non-JSON de la listaMesajeFactura: %s" % (r.text or "")[:300]
    if isinstance(j, dict) and j.get("eroare"):
        return [], j.get("eroare")
    if isinstance(j, dict):
        return (j.get("mesaje") or []), None
    return [], "forma neasteptata listaMesajeFactura: %s" % str(j)[:200]
