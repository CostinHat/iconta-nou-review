"""
Modul D406 — Fișierul Standard de Control Fiscal (SAF-T) pentru România.
ANAF Schema v2.4.9 (Ro_SAFT_Schema_v249_2025.xsd), OPANAF 1783/2021.

CONSTRUIT din schema XSD OFICIALĂ descărcată de la ANAF (nu din memorie).
Namespace, valori enumerate, ierarhia și câmpurile sunt citite din XSD.

Structura AuditFile (OECD SAF-T 2.0 adaptat RO):
  Header                  — versiune, țară, companie, perioadă, monedă, TaxAccountingBasis
  MasterFiles             — GeneralLedgerAccounts, Customers, Suppliers, TaxTable, Products, Assets
  GeneralLedgerEntries    — Journal → Transaction → TransactionLine (note contabile)
  SourceDocuments         — SalesInvoices, PurchaseInvoices, Payments, MovementOfGoods

⚠️ STADIU (actualizat 03.08.2026): Header + MasterFiles + GeneralLedgerEntries complet din XSD.
   SourceDocuments: SalesInvoices/PurchaseInvoices se emit cu LINII REALE pe produs din factura_linii
   (cantitate/UM/pret/descriere/cota), reconciliate OBLIGATORIU cu antetul; DUK-validate structural
   (reparat 27.07). TaxCode livrari PERIOD-AWARE pe data facturii (03.08: coduri pre/post 01.08.2025,
   Legea 141/2025). Payments = gol (zero date de plati in model - datorie blocata pe DATE, se reia la
   prima plata reala; codul de emitere e scris). MovementOfGoods gol (self-closed); AssetTransactions
   absent (XSD minOccurs=0, optional). De rafinat (observatii DECIZII 03.08, necesita input/date):
   TaxCode achizitii pe deductibilitate reala (acum grosier 300501); adresa partener din nomenclator
   (acum placeholder). Validare finala: DUKIntegrator_AnLunaUI.jar (-v D406 fisier.xml $ $ an=AAAA luna=LL).

CORECȚII față de prima schiță (confirmate din XSD):
  - namespace = mfp:anaf:dgti:d406:declaratie:v1
    CORECTIE 15.07.2026: aici scria "d406t (NU d406)" - gresit. Validatorul
    oficial (DUKIntegrator_AnLunaUI -v D406) spune literal: "namespace
    ('mfp:anaf:dgti:d406t:declaratie:v1') lipsa sau incorect la sectiunea
    AuditFile. Valoarea corecta este xmlns='mfp:anaf:dgti:d406:declaratie:v1'".
    Greseala a supravietuit pentru ca "validarea" D406 era teatru: se chema cu
    jar-ul si cheia altei declaratii, iesea tacit si orice XML parea valid.
  - AccountType = Activ/Pasiv/Bifunctional (NU "GL")
  - TaxAccountingBasis enumerat: A/I/IFRS/BANK/INSURANCE/NORMA39/IFN/NORMA36/NORMA14/ONG
  - SelectionCriteria cere SelectionStartDate/EndDate + Period*
  - Header cere Company (CompanyHeaderStructure)

Separare strictă: construcție pură / validare / XML / DB / orchestrare.
"""
import re
from core import common as c
from core.common import text_anaf as _t, LIMITE_TEXT_ANAF as _LIM  # limite text SAF-T din XSD (03.08.2026)
from core.identitate import valideaza_cui as _vcui, valideaza_cif as _vcif  # T1/E3 (CATALOG_INVALIDITATE.md): checksum CUI/CNP + tip 03 CNP pre-DUK, sursa canonica read-only (LEAF, fara db)
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

# namespace REAL din XSD (targetNamespace)
NS = "mfp:anaf:dgti:d406:declaratie:v1"   # verificat la validatorul oficial 15.07.2026
REGULI = "2026.1"
SAFT_VERSION = "2.4.9"
# TaxAccountingBasis = NORMA CONTABILA aplicata de firma, nu "contabilitate de
# angajamente" cum zicea comentariul de aici. Determina si PLANUL DE CONTURI pe care
# ANAF il accepta: validatorul respinge orice cont care nu e in planul normei declarate
# (dovedit 15.07.2026: conturile 731-738 - venituri ONG, OMFP 3103/2017 - erau in
# planul implicit al TUTUROR firmelor, desi nu exista in plan_conturi_bal_soc_com).
# Nomenclatorul oficial: d406_nomenclatoare_anaf.properties (extras din D406TValidator).
TAB_IMPLICIT = "A"   # societati comerciale, OMFP 1802/2014 - cazul majoritatii
# norma (firma_profil.baza_contabila) -> cheia din nomenclatorul ANAF
PLAN_NOMENCLATOR = {
    "A": "plan_conturi_bal_soc_com",
    "IFRS": "plan_conturi_ifrs",
    "BANK": "plan_conturi_banci",
    "INSURANCE": "plan_conturi_soc_asigurari",
    "ONG": "plan_conturi_ONG",
    "NORMA39": "plan_conturi_n39",
    "NORMA36": "plan_conturi_n36",
    "NORMA14": "plan_conturi_norma14",
    "IFN": "plan_conturi_ifn",
}


# UnitOfMeasure: nomenclatorul e UN/ECE Recommendation 20, NU unitatile romanesti.
# Dovedit 15.07.2026 pe validatorul oficial: "BUC" -> "valoarea 'BUC' nu se afla in
# lista"; H87/KGM/LTR/MTR/... exista toate. iConta tinea "BUC" hardcodat in SAF-T.
UOM_UNECE = {
    "buc": "H87", "bucata": "H87", "bucati": "H87", "buc.": "H87", "pcs": "H87",
    "kg": "KGM", "kgm": "KGM", "kilogram": "KGM",
    "g": "GRM", "gr": "GRM", "gram": "GRM",
    "t": "TNE", "to": "TNE", "tona": "TNE",
    "l": "LTR", "litru": "LTR", "litri": "LTR",
    "ml": "MLT",
    "m": "MTR", "metru": "MTR", "ml.": "MTR",
    "cm": "CMT", "km": "KMT",
    "mp": "MTK", "m2": "MTK", "mc": "MTQ", "m3": "MTQ",
    "ora": "HUR", "ore": "HUR", "h": "HUR",
    "zi": "DAY", "zile": "DAY", "luna": "MON", "luni": "MON", "an": "ANN", "ani": "ANN",
    "set": "SET", "per": "PR", "pereche": "PR",
    "kwh": "KWH", "mwh": "MWH",
}
UOM_IMPLICIT = "H87"

# HeaderComment: obligatoriu, maximum 2 caractere (dovedit pe validatorul oficial).
HEADER_COMMENT = "L"   # depunere lunara

# MovementType / StockMovementType: nomenclatorul OFICIAL ANAF de miscari de produse in stocuri
# (anaf_surse/d406_schema_anaf.xlsx, foaia "Nomenclator stocuri" - 19 coduri). Completeaza campul
# MovementType (MasterFiles/2.8 MovementTypeTable) si "Movement subtype" (SourceDocuments/
# StockMovement), AMBELE obligatorii DOAR in raportarea de STOCURI (ceruta separat, nu lunar; lunar
# sectiunile se emit GOALE - <MovementTypeTable/>, <MovementOfGoods/>). Nota 5 a foii: o valoare din
# AFARA listei -> eroare FATALA, D406 respins (trimiteam candva "1", care nu exista). Coduri dormante
# pana se cableaza raportarea de stocuri, dar nomenclatorul COMPLET e pazit
# (test_movementtype_nomenclator_oficial) ca sa fie corect din prima cand se activeaza.
MISCARI_STOC = {
    "10": "Achizitie", "20": "Productie", "30": "Vanzare",
    "40": "Retur produse vandute", "50": "Retur produse achizitionate",
    "60": "Reduceri comerciale primite", "70": "Consum", "80": "Transfer intern",
    "90": "Cheltuieli ulterioare incluse în valoarea de intrare",
    "100": "Diferente de preț pozitive", "101": "Diferente de preț negative",
    "110": "Plus de inventar", "120": "Minus de inventar",
    "130": "Ajustari pentru deprecierea stocurilor",
    "140": "Reluari de ajustari pentru deprecierea stocurilor",
    "150": "Bunuri acordate cu titlu gratuit", "160": "Bunuri degradate",
    "170": "Bunuri expirate", "180": "Alte tranzacții",
}
MOVEMENT_IMPLICIT = "10"

# BaseRate (MF.TT.11) = pro-rata de DEDUCERE per cod de taxa, encodata ca FRACTIE in [0.0000, 1.0000]
# unde 1.0000 = 100.00% (tip SAFBaseRate = decimal totalDigits 5, fractionDigits 4). ATENTIE, foaia
# "2. MasterFiles" e intern CONTRADICTORIE: proza spune "Standard is 100 (whole amount) / 60 if 60%"
# (text OECD-legacy pe procente), DAR restrictia OBLIGATORIE din aceeasi celula e "[0,0000 - 1,0000]
# (unde 1,0000 = 100,00%)". Restrictia CASTIGA: o valoare 100 sau 60 ar viola [0-1] -> D406 respins.
# Intreaga suma deductibila = 1 (=1.0000), NU 100. Livrarile (singurele coduri emise azi) n-au pro-rata
# de deducere -> 1. Un cod achizitie ded. 50% ar cere 0.5 (datorie: cote_tva emite doar livrari azi).
# NU schimba in 100 (comentariul vechi cita GRESIT doc-ul ca "standard 1" - concluzia corecta, dar din
# restrictie, nu din proza). Pazit de test_baserate_encoding_pro_rata_fractie.
BASE_RATE = 1

# PaymentMethod (SD Payment) = cod de DOUA CIFRE din nomenclatorul oficial ANAF
# (d406_schema_anaf.xlsx, foaia "Nom_Mecanisme_plati", coloana "Code used for Payment
# Method"). Valorile permise sunt DOAR: 01 Numerar, 02 Compensare, 03 Fara numerar,
# 98 Definit de comun acord, 99 Instrument nedefinit. Literalii "VIR"/"NUM" NU exista in
# lista - respinsi de validatorul oficial ("valoarea VIR nu se afla in lista", probat pe
# DUK 09.08.2026 pe Payments injectate). Mapam tokenii interni la codul ANAF; necunoscut -> 03.
METODE_PLATA_ANAF = {"01", "02", "03", "98", "99"}
_METODA_PLATA_MAP = {
    "num": "01", "numerar": "01", "cash": "01", "casa": "01", "chitanta": "01",
    "comp": "02", "compensare": "02", "offset": "02", "netting": "02",
    "vir": "03", "virament": "03", "transfer": "03", "op": "03", "banca": "03",
    "card": "03", "cec": "03", "ob": "03", "mobilpay": "03", "pos": "03",
}
PAYMENT_METHOD_IMPLICIT = "03"   # fara numerar (virament/card) - cazul majoritatii platilor


def payment_method_anaf(m):
    """Metoda noastra de plata -> cod ANAF de 2 cifre (Nom_Mecanisme_plati). Un cod deja
    valid (01/02/03/98/99) trece neschimbat; necunoscut -> 03 (fara numerar), niciodata
    literalul brut (respins de validator: valoarea ... nu se afla in lista)."""
    if not m:
        return PAYMENT_METHOD_IMPLICIT
    k = str(m).strip()
    if k in METODE_PLATA_ANAF:
        return k
    return _METODA_PLATA_MAP.get(k.lower(), PAYMENT_METHOD_IMPLICIT)


def _payment_method_anaf_stiut(m):
    """Ca payment_method_anaf, dar intoarce (cod, cunoscut): cunoscut=False cand valoarea a fost
    inlocuita TACIT cu implicitul 03 pentru ca nu e in nomenclator (T3). Gol -> (03, True): nu s-a
    dat nimic, nu e o coercitie a unei valori gresite."""
    if not m:
        return PAYMENT_METHOD_IMPLICIT, True
    k = str(m).strip()
    if k in METODE_PLATA_ANAF:
        return k, True
    kl = k.lower()
    if kl in _METODA_PLATA_MAP:
        return _METODA_PLATA_MAP[kl], True
    return PAYMENT_METHOD_IMPLICIT, False


def uom_unece(um):
    """Unitatea noastra -> cod UN/ECE Rec.20. Necunoscut -> H87 (bucata), cu semnalare
    la apelant: mai bine o unitate implicita declarata decat un XML respins."""
    if not um:
        return UOM_IMPLICIT, False
    k = str(um).strip().lower()
    if k.upper() in set(UOM_UNECE.values()):
        return k.upper(), True          # deja e cod UN/ECE
    c = UOM_UNECE.get(k)
    return (c, True) if c else (UOM_IMPLICIT, False)


# Prefixe VAT/VIES ale statelor UE (fara RO), asa cum apar pe codul partenerului de pe factura.
# ATENTIE Grecia: prefixul VAT/VIES e "EL", NU ISO "GR" - schema ANAF (5. Structures) exemplifica
# LITERAL "01EL123456789". Setul tine deci "EL", nu "GR".
_UE_NON_RO = {"AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","EL",
              "HU","IE","IT","LV","LT","LU","MT","NL","PL","PT","SK","SI","ES","SE"}
# Un cod ISO 3166 venit din surse (Grecia "GR") -> prefixul VAT cerut de ANAF ("EL").
_ISO_TO_VAT = {"GR": "EL"}


def _partener_registration_number(cui_brut, eticheta=None):
    """RegistrationNumber pt. PARTENERI (Customer/Supplier, S.C.1 CompanyStructure) -
    diferit de registration_number() de mai jos, care e pt. firma proprie (S.CMH.1).
    Format oficial (d406_schema_anaf.xlsx, "5. Structures", citat integral):
      00+CUI (operator RO, FARA prefix RO - "Atentie! Nu se trece atributul fiscal
              RO pentru platitorii de TVA")
      01+tara+CUI (operator UE, alta decat RO, verificat VIES)
      02+tara+CUI (operator din afara UE)
    Mutata la nivel de modul (16.07.2026) din pull(), unde era definita DUPA locul
    unde acum trebuie folosita (la construirea notelor, care au nevoie de partener
    real per tranzactie, nu "primul din lista" - bug dovedit prin migrare reala).
    """
    c = (cui_brut or "").strip().upper()
    tara = c[:2] if len(c) >= 2 and c[:2].isalpha() else ""
    tara = _ISO_TO_VAT.get(tara, tara)          # Grecia ISO "GR" -> prefix VAT "EL" (cerut de ANAF)
    rest = _NEDIGIT.sub("", c[2:] if tara else c)
    if not rest:
        return None
    if tara == "RO" or not tara:
        # RO / fara prefix: cod fiscal romanesc = CUI (persoana juridica) SAU CNP (persoana
        # fizica). Cifra de control se verifica OFFLINE, PRE-DUK (T1, CATALOG_INVALIDITATE.md):
        # un cod cu checksum/lungime gresita era emis TACIT "00"+cod -> DUK
        # "RegistrationNumber/SupplierID format invalid" (userul afla abia la depunere). Un CNP
        # VALID -> tipul 03 (E3/E4: d406_schema_anaf.xlsx "5. Structures", regula sintactica
        # S.I.26 pct.1.4 "03 urmat de CNP ... 13 caractere numerice, prima cifra diferita de 0"),
        # NU 00+CNP (respins de DUK indiferent de validitate - tipul gresit, calea 03 inexistenta).
        _valid, _tip, _motiv = _vcif(rest)
        if not _valid:
            _cine = (" (%s)" % eticheta) if eticheta else ""
            raise ValueError(
                "D406: cod fiscal partener invalid%s: %r - %s. Corectează codul fiscal al "
                "partenerului înainte de generare (DUK regula S.I.26/S.C.1)."
                % (_cine, cui_brut, _motiv))
        return ("03" + rest) if _tip == "cnp" else ("00" + rest)
    if tara in _UE_NON_RO:
        return "01" + tara + rest
    return "02" + tara + rest


def _partener_id_saft(cui_brut, nume, eticheta=None):
    """CustomerID/SupplierID pt. un partener de pe FACTURA/master, cf. codificarii
    oficiale ANAF (d406_schema_anaf.xlsx, '5. Structures', tip 00-11 + regula
    sintactica S.I.23/S.I.26/SD.P.22/SD.P.23). Un furnizor/client de pe o factura are
    mereu identitate cunoscuta -> ID-ul NU poate fi '0' (validatorul oficial: '2.
    Altfel daca ... egal cu 0 se semnaleaza eroare sintactica - SupplierID nu poate fi
    0'; codul 08 'neidentificat' e interzis EXPLICIT pe SupplierID). Reguli:
      - cu cod fiscal   -> 00/01/02 (via _partener_registration_number)
      - persoana fizica -> tipul 04 = 'cod client asociat in mod unic de catre
        FARA cod fiscal    operatorul economic ... pentru pers. fizice care nu isi
                           declara CNP-ul' (regula sintactica 1.5: doar alfanumeric,
                           fara caractere speciale; max 33 = 35 SAFmiddle1textType - 2).
                           Codul intern e derivat determinist din numele partenerului.
    NU inventeaza un CUI: 04 e placeholder-ul PREVAZUT de norma pentru PF fara cod
    fiscal declarat. Daca sistemul ar captura CNP-ul, tipul corect ar fi 03+CNP -
    facturile nu poarta inca CNP, deci 04 e singura optiune valida. Fara cod fiscal SI
    fara nume -> None: apelantul raporteaza (nu cade pe '0', nu inventeaza)."""
    rid = _partener_registration_number(cui_brut, eticheta=eticheta)
    if rid:
        return rid
    cod = _NEALNUM.sub("", (nume or "").upper())[:33]
    return ("04" + cod) if cod else None


def registration_number(prof):
    """RegistrationNumber conform schemei oficiale ANAF (d406_schema_anaf.xlsx,
    foaia "5. Structures", S.CMH.1 CompanyHeaderStructure), citat integral:

      "Pentru nerezidentii cu inregistrare fiscala in Romania: Cod de inregistrare
       fiscala (CIF). Pentru rezidenti: daca este inregistrata in scopuri de TVA,
       setati numarul de inregistrare VAT cu prefixul RO; in caz contrar, setati
       Codul unic de inregistrare (CUI)"

    Deci prefixul RO NU e optional: e obligatoriu pentru platitorii de TVA si
    interzis pentru neplatitori. Codul scria _NEDIGIT.sub("", cui), adica stergea
    exact prefixul cerut -> "formatul este invalid" pentru orice platitor de TVA.
    """
    cif = _NEDIGIT.sub("", prof.get("cui") or "")
    if not cif:
        return ""
    platitor = prof.get("platitor_tva")
    if platitor is None:
        platitor = True     # implicit: platitor (cazul majoritatii firmelor D406)
    return ("RO" + cif) if platitor else cif


def plan_oficial(norma):
    """Conturile pe care ANAF le accepta pentru norma data. Sursa: nomenclatorul
    din validatorul oficial (d406_nomenclatoare_anaf.properties). Intoarce set gol
    daca nomenclatorul lipseste - atunci NU filtram (nu inventam un plan al nostru)."""
    import os as _os
    cheie = PLAN_NOMENCLATOR.get((norma or TAB_IMPLICIT).upper())
    if not cheie:
        return set()
    cale = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "anaf_surse",
                         "d406_nomenclatoare_anaf.properties")
    if not _os.path.exists(cale):
        return set()
    with open(cale, encoding="utf-8", errors="replace") as fh:
        for l in fh:
            if l.startswith(cheie + "="):
                return {x.strip() for x in l.split("=", 1)[1].strip().split(",") if x.strip()}
    return set()
_NEDIGIT = re.compile(r"\D")
_NEALNUM = re.compile(r"[^A-Z0-9]")  # tip 04: doar alfanumeric, fara caractere speciale

# valori enumerate confirmate din XSD
TAB_VALORI = {"A", "I", "IFRS", "BANK", "INSURANCE", "NORMA39", "IFN", "NORMA36", "NORMA14", "ONG"}
ACCOUNT_TYPE = {"Activ", "Pasiv", "Bifunctional"}


def _esc(v):
    s = "" if v is None else str(v)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))


def _dec(x):
    return str(Decimal(str(x or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _d(x):
    if isinstance(x, date):
        return x.isoformat()
    return str(x or "")


def _ultima_zi(an, luna):
    if luna == 12:
        return date(an, 12, 31)
    return date(an, luna + 1, 1) - timedelta(days=1)


# ---------- structuri de date ----------

@dataclass
class Cont:
    id: str
    descriere: str
    cont_standard: str
    tip: str = "Bifunctional"          # Activ/Pasiv/Bifunctional
    sold_deschidere_d: Decimal = Decimal(0)
    sold_deschidere_c: Decimal = Decimal(0)
    sold_inchidere_d: Decimal = Decimal(0)
    sold_inchidere_c: Decimal = Decimal(0)


@dataclass
class Partener:
    id: str
    nume: str
    cui: str
    tara: str = "RO"
    oras: str = ""
    adresa: str = ""
    sold_d: Decimal = Decimal(0)
    sold_c: Decimal = Decimal(0)


@dataclass
class CotaTVA:
    cod: str
    procent: Decimal
    descriere: str = ""


@dataclass
class LinieNota:
    record_id: str
    cont: str
    descriere: str
    debit: Decimal = Decimal(0)
    credit: Decimal = Decimal(0)
    cont_partener_id: str = ""


@dataclass
class Nota:
    id: str               # TransactionID
    data: date
    descriere: str
    jurnal: str = "GENERAL"
    linii: list = field(default_factory=list)


@dataclass
class LinieFactura:
    nr: int
    cont: str                # AccountID
    descriere: str
    cantitate: Decimal = Decimal(1)
    um: str = UOM_IMPLICIT   # InvoiceUOM - cod UN/ECE Rec.20 (H87 = bucata)
    pret_unitar: Decimal = Decimal(0)
    valoare: Decimal = Decimal(0)        # InvoiceLineAmount (baza, fără TVA)
    sens: str = "C"          # DebitCreditIndicator (C credit pt vânzare, D debit pt cumpărare)
    tva_cod: str = "310"     # TaxCode
    tva_procent: Decimal = Decimal(21)
    tva_suma: Decimal = Decimal(0)       # TaxAmount


@dataclass
class Factura:
    nr: str                  # InvoiceNo
    data: date               # InvoiceDate
    partener_id: str         # CustomerID / SupplierID
    partener_nume: str
    tip: str = "FT"          # InvoiceType (FT factură, FS factură simplificată, etc.)
    cont: str = "4111"       # AccountID
    self_billing: str = "0"  # SelfBillingIndicator
    linii: list = field(default_factory=list)

    @property
    def net(self):
        return sum(l.valoare for l in self.linii)

    @property
    def tva(self):
        return sum(l.tva_suma for l in self.linii)

    @property
    def brut(self):
        return self.net + self.tva


@dataclass
class LiniePlata:
    nr: int
    cont: str
    descriere: str
    suma: Decimal = Decimal(0)
    sens: str = "D"          # DebitCreditIndicator
    doc_sursa: str = ""      # SourceDocumentID (factura achitată)


@dataclass
class Plata:
    ref: str                 # PaymentRefNo
    data: date               # TransactionDate
    metoda: str = "03"       # PaymentMethod cod ANAF (01 numerar/02 compensare/03 fara numerar)
    partener_id: str = ""
    descriere: str = ""
    linii: list = field(default_factory=list)

    @property
    def total(self):
        return sum(l.suma for l in self.linii)


@dataclass
class Rezultat:
    an: int
    luna: int
    prof: dict
    conturi: list = field(default_factory=list)
    clienti: list = field(default_factory=list)
    furnizori: list = field(default_factory=list)
    cote_tva: list = field(default_factory=list)
    note: list = field(default_factory=list)        # GeneralLedgerEntries
    facturi_vanzare: list = field(default_factory=list)   # SalesInvoices
    facturi_cumparare: list = field(default_factory=list) # PurchaseInvoices
    plati: list = field(default_factory=list)             # Payments
    avertismente: list = field(default_factory=list)


# TaxCode SAF-T: cod de 6 CIFRE, nu 3. Seria (primele 3) = categoria operatiunii,
# ultimele 3 = pozitia in nomenclator. Codurile de aici sunt cele din schema OFICIALA
# ANAF (d406_schema_anaf.xlsx, foaia "Livrari", versiunea 05.02.2026):
#   310nnn = livrari ; 301nnn-309nnn = achizitii deductibile 100% ;
#   320nnn = achizitii ded. 50% pro-rata ; 380nnn = note contabile fara document sursa.
# Codul depinde de COTA SI DE PERIOADA: pentru 21% si 11% ANAF a adaugat coduri NOI,
# active cu 01.08.2025 (Legea 141/2025); cele vechi raman pentru perioadele anterioare.
# Vechea lista de aici ("310"/"320"/"330"/"300") era inventata - prefixe, nu coduri.
# Fiecare cod corespunde unui RAND din D300 (col. "Corespondent rand D300").
COTE_TVA_STANDARD = [
    CotaTVA("310344", Decimal("21"), "Livrări taxabile cota 21% (rd. 9 D300)"),
    CotaTVA("310351", Decimal("11"), "Livrări taxabile cota 11% (rd. 10 D300)"),
    CotaTVA("310311", Decimal("5"), "Livrări taxabile cota 5% (rd. 11 D300)"),
    CotaTVA("310312", Decimal("0"), "Livrări cu taxare inversa (rd. 13 D300)"),
]
# cota -> TaxCode livrari, dupa 01.08.2025 (Legea 141/2025)
TAXCODE_LIVRARI = {21: "310344", 11: "310351", 9: "310357", 5: "310311", 0: "310312"}
# cotele de dinainte de 01.08.2025 (perioade raportate retroactiv)
TAXCODE_LIVRARI_PRE_2025_08 = {19: "310309", 9: "310310", 5: "310311", 0: "310312"}
# granita codurilor TaxCode livrari (Legea 141/2025). Sub ea = codurile epocii, peste = cele noi.
_TAXCODE_141_DIN = date(2025, 8, 1)

# TaxCode pentru liniile de NOTA CONTABILA / PLATA fara TVA (banca, casa, creante,
# venituri neimpozabile - TaxAmount 0.00). Nomenclatorul oficial (d406_schema_anaf.xlsx,
# foaia 'TVA_NoteContabile', antet: 'NOMENCLATOR CODURI DE TAXA PENTRU RAPORTAREA
# NOTELOR CONTABILE CARE NU AU CORESPONDENT IN DOCUMENTE SURSA') acopera DOAR familia
# 380xxx; '300' (emis anterior) NU exista in el - era un prefix inventat, nu un cod.
# Singurul cod cu cota 0 / scutit din familie este 380304 (cota 0, 'Livrari/prestari
# pentru care nu exista obligatia emiterii facturii si nu sunt supuse TVA, art. 319
# alin. 10 Cod Fiscal') - valoarea corecta de nomenclator pentru liniile de nota fara TVA.
TAXCODE_NOTA_FARA_TVA = "380304"


def _taxcode_livrari(cota, data_factura):
    """TaxCode SAF-T pentru livrari, PERIOD-AWARE pe data facturii. ANAF a schimbat codurile cu
    01.08.2025 (Legea 141/2025): factura dinainte foloseste codurile epocii (19/9/5), una de dupa
    cele noi (21/11/9/5). Fara asta, o raportare retroactiva emite coduri gresite (ex. 19% negasit
    in tabela noua -> default 310312 taxare inversa). Data lipsa -> tabela curenta (post)."""
    tabela = (TAXCODE_LIVRARI_PRE_2025_08 if (data_factura and data_factura < _TAXCODE_141_DIN)
              else TAXCODE_LIVRARI)
    return tabela.get(int(cota), "310312")


def _cota_livrari_in_tabela(cota, data_factura):
    """True daca cota exista in tabela TaxCode livrari a epocii facturii. False =
    _taxcode_livrari a inlocuit-o TACIT cu 310312 (taxare inversa) - se semnaleaza (T3)."""
    tabela = (TAXCODE_LIVRARI_PRE_2025_08 if (data_factura and data_factura < _TAXCODE_141_DIN)
              else TAXCODE_LIVRARI)
    return int(cota) in tabela


def construieste(prof, an, luna, conturi, clienti, furnizori, note=None,
                 facturi_vanzare=None, facturi_cumparare=None, plati=None, cote_tva=None):
    res = Rezultat(an=an, luna=luna, prof=prof, conturi=conturi, clienti=clienti,
                   furnizori=furnizori, note=note or [],
                   facturi_vanzare=facturi_vanzare or [],
                   facturi_cumparare=facturi_cumparare or [],
                   plati=plati or [],
                   cote_tva=cote_tva or COTE_TVA_STANDARD)
    res.avertismente.append("D406 v%s: %d conturi, %d clienți, %d furnizori, %d note, %d fact.vânz, %d fact.cump, %d plăți."
                            % (SAFT_VERSION, len(conturi), len(clienti), len(furnizori), len(res.note),
                               len(res.facturi_vanzare), len(res.facturi_cumparare), len(res.plati)))
    res.avertismente.append("Validare finală: DUKIntegrator pe server (-v D406 fisier.xml $ $ an=%d luna=%d)." % (an, luna))
    # T3 (CATALOG_INVALIDITATE.md): o metoda de plata necunoscuta e inlocuita TACIT cu 03 (fara
    # numerar) de payment_method_anaf. Nu tacit: semnalam per plata valoarea exacta inlocuita.
    for _p in (plati or []):
        _pm, _pm_stiut = _payment_method_anaf_stiut(getattr(_p, "metoda", None))
        if not _pm_stiut:
            res.avertismente.append(
                "ATENTIE (D406): metoda de plată necunoscută %r pe plată %s - înlocuită cu 03 "
                "(fără numerar). Mapează metoda în nomenclatorul de mecanisme de plată "
                "(Nom_Mecanisme_plati: 01/02/03/98/99)." % (_p.metoda, getattr(_p, "ref", "?")))
    return res


def valideaza(res):
    erori = []
    prof = res.prof
    if not _NEDIGIT.sub("", prof.get("cui") or ""):
        erori.append("LIPSĂ CUI companie (RegistrationNumber).")
    if not prof.get("nume"):
        erori.append("LIPSĂ denumire companie.")
    if res.luna < 1 or res.luna > 12:
        erori.append("Lună invalidă.")
    if not res.conturi:
        erori.append("LIPSĂ plan de conturi (GeneralLedgerAccounts).")
    ids = [c.id for c in res.conturi]
    if len(ids) != len(set(ids)):
        erori.append("AccountID duplicat în planul de conturi.")
    for c in res.conturi:
        if c.tip not in ACCOUNT_TYPE:
            erori.append("AccountType invalid pentru cont %s (trebuie Activ/Pasiv/Bifunctional)." % c.id)
    # echilibru note: debit = credit pe fiecare notă
    for n in res.note:
        td = sum(l.debit for l in n.linii)
        tc = sum(l.credit for l in n.linii)
        if abs(td - tc) > Decimal("0.01"):
            erori.append("Nota %s nu e echilibrată (debit %s ≠ credit %s)." % (n.id, _dec(td), _dec(tc)))
    # coerență facturi: brut = net + tva
    for f in (res.facturi_vanzare + res.facturi_cumparare):
        if not f.linii:
            erori.append("Factura %s fără linii." % f.nr)
        for l in f.linii:
            tva_calc = (l.valoare * l.tva_procent / Decimal(100)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if abs(l.tva_suma - tva_calc) > Decimal("0.02"):
                erori.append("Factura %s linia %d: TVA %s ≠ %s (%s%% din %s)."
                             % (f.nr, l.nr, _dec(l.tva_suma), _dec(tva_calc), _dec(l.tva_procent), _dec(l.valoare)))
    return erori


def _header(res):
    prof = res.prof
    cui = _NEDIGIT.sub("", prof.get("cui") or "")
    di = date(res.an, res.luna, 1)
    ds = _ultima_zi(res.an, res.luna)
    H = []
    H.append('  <Header>')
    # HeaderStructure (ordine fixă)
    H.append('    <AuditFileVersion>%s</AuditFileVersion>' % SAFT_VERSION)
    H.append('    <AuditFileCountry>RO</AuditFileCountry>')
    H.append('    <AuditFileDateCreated>%s</AuditFileDateCreated>' % _d(date.today()))
    H.append('    <SoftwareCompanyName>iConta</SoftwareCompanyName>')
    H.append('    <SoftwareID>iConta SaaS</SoftwareID>')
    H.append('    <SoftwareVersion>1.0</SoftwareVersion>')
    H.append('    <Company>')
    # [reg number firma proprie 16.08] S.CMH.1: platitor TVA -> RO+CIF; neplatitor -> CIF.
    # registration_number() implementa regula dar era COD MORT (0 apeluri) - headerul emitea CUI
    # brut (fara RO) -> "format invalid" la DUK pt platitorii de TVA (exact ce docstring-ul functiei descrie).
    H.append('      <RegistrationNumber>%s</RegistrationNumber>' % _esc(registration_number(prof)))
    H.append('      <Name>%s</Name>' % _esc(_t(prof.get("nume") or "", _LIM["d406"]["CompanyName"])))
    H.append('      <Address>')
    H.append('        <StreetName>%s</StreetName>' % _esc(_t(prof.get("adresa") or "-", _LIM["d406"]["StreetName"])))
    H.append('        <City>%s</City>' % _esc(_t(prof.get("oras") or "-", _LIM["d406"]["City"])))
    H.append('        <PostalCode>%s</PostalCode>' % _esc(_t(prof.get("cod_postal") or "000000", _LIM["d406"]["PostalCode"])))
    H.append('        <Country>RO</Country>')
    H.append('      </Address>')
    H.append('      <Contact>')
    H.append('        <ContactPerson>')
    H.append('          <FirstName>-</FirstName>')
    H.append('          <LastName>%s</LastName>' % _esc(_t(prof.get("nume") or "-", _LIM["d406"]["ContactLastName"])))
    H.append('        </ContactPerson>')
    H.append('        <Telephone>-</Telephone>')
    H.append('      </Contact>')
    H.append('      <BankAccount>')
    H.append('        <IBANNumber>RO00BANK0000000000000000</IBANNumber>')
    H.append('      </BankAccount>')
    H.append('    </Company>')
    H.append('    <DefaultCurrencyCode>RON</DefaultCurrencyCode>')
    H.append('    <SelectionCriteria>')
    H.append('      <PeriodStart>%d</PeriodStart>' % res.luna)
    H.append('      <PeriodStartYear>%d</PeriodStartYear>' % res.an)
    H.append('      <PeriodEnd>%d</PeriodEnd>' % res.luna)
    H.append('      <PeriodEndYear>%d</PeriodEndYear>' % res.an)
    H.append('    </SelectionCriteria>')
    # HeaderComment: OBLIGATORIU (min 1 aparitie) dar MAX 2 CARACTERE - dovedit pe
    # validator, in ambele sensuri. Nu e un comentariu liber, ci un cod scurt; in SAF-T
    # RO marcheaza tipul depunerii. Textul "D406 generat de iConta" facea XML-ul invalid.
    H.append('    <HeaderComment>%s</HeaderComment>' % HEADER_COMMENT)
    H.append('    <SegmentIndex>1</SegmentIndex>')
    H.append('    <TotalSegmentsInsequence>1</TotalSegmentsInsequence>')
    # extensie RO: TaxAccountingBasis (după HeaderStructure)
    H.append('    <TaxAccountingBasis>%s</TaxAccountingBasis>'
             % ((res.prof.get("baza_contabila") or TAB_IMPLICIT).upper()))
    H.append('  </Header>')
    return H


def _masterfiles(res):
    M = ['  <MasterFiles>']
    M.append('    <GeneralLedgerAccounts>')
    for c in res.conturi:
        # AccountID trebuie NUMERIC INTREG (validator: "numar intreg eronat" pe
        # simboluri cu punct precum '401.05', '4111.01' - analiticele din
        # migrare). SAF-T identifica contul dupa sintetic (AccountID); detalierea
        # pe partener se face prin Customers/Suppliers (deja generate separat,
        # linia ~466/484), nu prin conturi analitice in GeneralLedgerAccounts.
        # cont_standard e deja radacina sintetica (ex. '401' pentru '401.05').
        account_id = c.cont_standard if ("." in c.id and c.cont_standard) else c.id
        M.append('      <Account>')
        M.append('        <AccountID>%s</AccountID>' % _esc(account_id))
        M.append('        <AccountDescription>%s</AccountDescription>' % _esc(_t(c.descriere, _LIM["d406"]["AccountDescription"])))
        M.append('        <StandardAccountID>%s</StandardAccountID>' % _esc(c.cont_standard or c.id))
        M.append('        <AccountType>%s</AccountType>' % _esc(c.tip))
        # choice: debit XOR credit (nu ambele)
        if c.sold_deschidere_c and not c.sold_deschidere_d:
            M.append('        <OpeningCreditBalance>%s</OpeningCreditBalance>' % _dec(c.sold_deschidere_c))
        else:
            M.append('        <OpeningDebitBalance>%s</OpeningDebitBalance>' % _dec(c.sold_deschidere_d))
        if c.sold_inchidere_c and not c.sold_inchidere_d:
            M.append('        <ClosingCreditBalance>%s</ClosingCreditBalance>' % _dec(c.sold_inchidere_c))
        else:
            M.append('        <ClosingDebitBalance>%s</ClosingDebitBalance>' % _dec(c.sold_inchidere_d))
        M.append('      </Account>')
    M.append('    </GeneralLedgerAccounts>')
    # Customers (Customer: CompanyStructure wrapper + CustomerID/AccountID/solduri)
    M.append('    <Customers>')
    for c in res.clienti:
        M.append('      <Customer>')
        M.append('        <CompanyStructure>')
        # Bug vechi la RegistrationNumber: _esc('') + _esc(cui) + _esc('') era
        # string Python concatenat IN AFARA formatului %s (deci "%s" primea
        # doar primul _esc('') = "", restul se lipea alaturi in Python, invizibil
        # in atributul XML real) - de-aia era "vid nepermis". Foloseste CUI-ul
        # PARTENERULUI (c.cui), nu al firmei proprii (res.prof) - client gresit
        # legat de CUI-ul firmei. Prefixul RO e obligatoriu pt. platitorii de TVA
        # (aceeasi regula ca registration_number(), aplicata aici pt. partener).
        # c.id e deja formatul oficial S.C.1 (00/01/02 + cod), calculat o singura
        # data la sursa (_registration_number() in pull()) - RegistrationNumber si
        # CustomerID trebuie sa fie IDENTICE intre ele si cu ce refera TransactionLine.
        M.append('          <RegistrationNumber>%s</RegistrationNumber>' % _esc(c.id))
        M.append('          <Name>%s</Name>' % _esc(_t(c.nume, _LIM["d406"]["PartnerName"])))
        M.append('          <Address>')
        M.append('            <City>%s</City>' % _esc(_t(c.oras or "-", _LIM["d406"]["City"])))
        M.append('            <Country>%s</Country>' % _esc(c.tara or "RO"))
        M.append('          </Address>')
        M.append('        </CompanyStructure>')
        M.append('        <CustomerID>%s</CustomerID>' % _esc(c.id))
        M.append('        <AccountID>4111</AccountID>')
        M.append('        <OpeningDebitBalance>%s</OpeningDebitBalance>' % _dec(c.sold_d))
        M.append('        <ClosingDebitBalance>%s</ClosingDebitBalance>' % _dec(c.sold_d))
        M.append('      </Customer>')
    M.append('    </Customers>')
    # Suppliers
    M.append('    <Suppliers>')
    for f in res.furnizori:
        M.append('      <Supplier>')
        M.append('        <CompanyStructure>')
        # Acelasi format ca la Customer: prefix RO obligatoriu pt. CUI romanesc.
        # Acelasi principiu ca la Customer: f.id e deja formatul S.C.1 corect.
        M.append('          <RegistrationNumber>%s</RegistrationNumber>' % _esc(f.id))
        M.append('          <Name>%s</Name>' % _esc(_t(f.nume, _LIM["d406"]["PartnerName"])))
        M.append('          <Address>')
        M.append('            <City>%s</City>' % _esc(_t(f.oras or "-", _LIM["d406"]["City"])))
        M.append('            <Country>%s</Country>' % _esc(f.tara or "RO"))
        M.append('          </Address>')
        M.append('        </CompanyStructure>')
        M.append('        <SupplierID>%s</SupplierID>' % _esc(f.id))
        M.append('        <AccountID>401</AccountID>')
        M.append('        <OpeningCreditBalance>%s</OpeningCreditBalance>' % _dec(f.sold_c))
        M.append('        <ClosingCreditBalance>%s</ClosingCreditBalance>' % _dec(f.sold_c))
        M.append('      </Supplier>')
    M.append('    </Suppliers>')
    # TaxTable (TaxCodeDetails: TaxCode/Description/TaxPercentage/Country)
    M.append('    <TaxTable>')
    M.append('      <TaxTableEntry>')
    M.append('        <TaxType>300</TaxType>')
    M.append('        <Description>TVA</Description>')
    for ct in res.cote_tva:
        M.append('        <TaxCodeDetails>')
        M.append('          <TaxCode>%s</TaxCode>' % _esc(ct.cod))
        M.append('          <Description>%s</Description>' % _esc(_t(ct.descriere, _LIM["d406"]["Description"])))
        M.append('          <TaxPercentage>%s</TaxPercentage>' % _dec(ct.procent))
        M.append('          <BaseRate>%s</BaseRate>' % BASE_RATE)
        M.append('          <Country>RO</Country>')
        M.append('        </TaxCodeDetails>')
    # 380304 e referit pe liniile GL/Payment fara TVA -> il declaram si in TaxTable
    # (cod valid din nomenclatorul TVA_NoteContabile), ca sa fie regasit la lookup.
    M.append('        <TaxCodeDetails>')
    M.append('          <TaxCode>%s</TaxCode>' % TAXCODE_NOTA_FARA_TVA)
    M.append('          <Description>Nota contabila fara TVA (art. 319 alin. 10 CF)</Description>')
    M.append('          <TaxPercentage>0</TaxPercentage>')
    M.append('          <BaseRate>%s</BaseRate>' % BASE_RATE)
    M.append('          <Country>RO</Country>')
    M.append('        </TaxCodeDetails>')
    M.append('      </TaxTableEntry>')
    M.append('    </TaxTable>')
    # containere obligatorii
    M.append('    <UOMTable>')
    M.append('      <UOMTableEntry>')
    M.append('        <UnitOfMeasure>%s</UnitOfMeasure>' % UOM_IMPLICIT)
    M.append('        <Description>Bucata</Description>')
    M.append('      </UOMTableEntry>')
    M.append('    </UOMTable>')
    M.append('    <AnalysisTypeTable>')
    M.append('      <AnalysisTypeTableEntry>')
    M.append('        <AnalysisType>1</AnalysisType>')
    M.append('        <AnalysisTypeDescription>General</AnalysisTypeDescription>')
    M.append('        <AnalysisID>1</AnalysisID>')
    M.append('        <AnalysisIDDescription>General</AnalysisIDDescription>')
    M.append('      </AnalysisTypeTableEntry>')
    M.append('    </AnalysisTypeTable>')
    # MovementTypeTable: sectiunea e OBLIGATORIE structural, dar GOALA in raportarea
    # lunara. Schema ANAF (d406_schema_anaf.xlsx, "2. MasterFiles"): pct. 2.8 tabela =
    # "Mandatory - by request", iar MF.MT.1 (MovementTypeTableEntry) = 0..*.
    # Validatorul confirma in ambele sensuri (15.07.2026): fara tabela -> "ar fi trebuit
    # sa apara de minimum 1 ori"; cu o intrare -> "MovementType a depasit numarul maxim
    # de aparitii (0)". Deci tabela da, continut nu - continutul apare doar la
    # raportarea de STOCURI, ceruta separat. Codurile: MISCARI_STOC (nomenclatorul oficial, 19 coduri).
    M.append('    <MovementTypeTable/>')
    M.append('    <Products>')
    M.append('      <Product>')
    M.append('        <ProductCode>GENERIC</ProductCode>')
    M.append('        <Description>Produs generic</Description>')
    M.append('        <ProductCommodityCode>0</ProductCommodityCode>')
    M.append('        <ProductNumberCode>GENERIC</ProductNumberCode>')
    M.append('        <UOMBase>%s</UOMBase>' % UOM_IMPLICIT)
    M.append('        <UOMStandard>%s</UOMStandard>' % UOM_IMPLICIT)
    M.append('        <UOMToUOMBaseConversionFactor>1</UOMToUOMBaseConversionFactor>')
    M.append('      </Product>')
    M.append('    </Products>')
    # Owners: sectiune GOALA in raportarea lunara, ca MovementTypeTable.
    # Schema ANAF (d406_schema_anaf.xlsx): pct. 2.11 Owners = "Mandatory - by request";
    # MF.O.2 Owner/CompanyStructure = "TBD" (to be determined - nu se completeaza);
    # S.C.1 CompanyStructure/RegistrationNumber = "TBD". In XSD toate sunt minOccurs=0.
    # Validatorul confirma: "elementul 'RegistrationNumber' a depasit numarul maxim de
    # aparitii (0)" - adica in Owners nu are voie sa existe deloc; eroarea de format era
    # doar efectul validarii unui camp care nu trebuia sa fie acolo.
    # ATENTIE la doua structuri DIFERITE cu reguli diferite (greseala mea 15.07.2026):
    #   S.CMH.1 CompanyHeaderStructure (Header/Company) -> RegistrationNumber cu prefix
    #     RO pentru platitorii de TVA (vezi registration_number()); ACOLO se valideaza.
    #   S.C.1  CompanyStructure (Owners)                -> TBD, nu se completeaza.
    # Cand se vor raporta asociatii: OwnerID cu formatul "00" + CUI (MF.O.3).
    M.append('    <Owners/>')
    # Assets: GOALA in raportarea LUNARA. Schema ANAF (d406_schema_anaf.xlsx,
    # "2. MasterFiles", pct. 2.12): "Mandatory - once per year" - mijloacele fixe se
    # raporteaza o data pe an, in declaratia anuala (tip raportare A), nu lunar.
    # Validatorul: "elementul 'AssetID' a depasit numarul maxim de aparitii (0)".
    # Al treilea caz de acelasi fel, dupa MovementTypeTable (2.8) si Owners (2.11):
    # sectiunea exista, continutul apare doar la raportarea in care e ceruta.
    # PhysicalStock (2.10, "by request", 0..1) - nu o generam deloc.
    M.append('    <Assets/>')
    M.append('  </MasterFiles>')
    return M


def _cod_propriu(prof):
    """Codul contribuabilului RAPORTOR in formatul CustomerID/SupplierID (00 + CUI,
    fara prefixul RO - regula sintactica GL.28/GL.29 pct. 2.1: "The substring RO is
    not accepted"). Folosit pe liniile care NU sunt de client/furnizor: regula oficiala
    (nota GL.28/GL.29 [17]) cere ca acolo AMBELE campuri sa poarte codul propriu al
    firmei, nu "0" - "0" pe ambele e interzis (rd. sintactic 1: daca unul e "0",
    celalalt trebuie sa fie diferit de "0")."""
    cui = _NEDIGIT.sub("", prof.get("cui") or "")
    return ("00" + cui) if cui else "0"


def _cust_supp_linie(cont, partener_id, cod_propriu):
    """(CustomerID, SupplierID) pentru o TransactionLine, dupa regula oficiala ANAF
    (d406_schema_anaf.xlsx, "3. GeneralLedgerEntries", GL.28/GL.29). AMBELE sunt
    obligatorii in XSD (minOccurs=1) pe FIECARE linie:
      - cont client (4111): CustomerID=partener (sau cod propriu daca lipseste), SupplierID="0"
      - cont furnizor (401): SupplierID=partener (sau cod propriu daca lipseste), CustomerID="0"
      - orice alt cont: AMBELE = codul propriu al raportorului (linia nu tine evidenta
        pe partener - venituri, TVA, banca, etc.)."""
    radacina = cont.split(".")[0] if "." in cont else cont
    if radacina == "4111":
        return (partener_id or cod_propriu, "0")
    if radacina == "401":
        return ("0", partener_id or cod_propriu)
    return (cod_propriu, cod_propriu)


def _gl_entries(res):
    """GeneralLedgerEntries: Journal -> Transaction -> TransactionLine.

    Sectiunea e OBLIGATORIE chiar si pe o luna fara miscari (schema ANAF, "3.
    GeneralLedgerEntries" = Mandatory).

    LUNA FARA MISCARI: firma activa cu o luna fara nicio nota contabila depune "pe
    zero" - sectiunea GOALA, self-closed <GeneralLedgerEntries/>, fara a fabrica nicio
    tranzactie. Confirmat din surse ANAF si dovedit pe validatorul oficial (16.07.2026,
    experimente directe): <GeneralLedgerEntries/> = VALID. Orice forma partiala e
    respinsa - DUK cere lantul complet daca sectiunea are continut (fara Transaction:
    "Transaction ... minimum 1 ori"; Journal self-closed: "JournalID ... minimum 1 ori";
    fara Journal: "Journal ... minimum 1 ori"). Deci: ori lant complet cu date reale,
    ori sectiune complet goala - niciodata partiala.
    """
    if not res.note:
        return ['  <GeneralLedgerEntries/>']
    nr = len(res.note)
    td = sum(sum(l.debit for l in n.linii) for n in res.note)
    tc = sum(sum(l.credit for l in n.linii) for n in res.note)
    G = ['  <GeneralLedgerEntries>']
    G.append('    <NumberOfEntries>%d</NumberOfEntries>' % nr)
    G.append('    <TotalDebit>%s</TotalDebit>' % _dec(td))
    G.append('    <TotalCredit>%s</TotalCredit>' % _dec(tc))
    G.append('    <Journal>')
    G.append('      <JournalID>GENERAL</JournalID>')
    G.append('      <Description>Jurnal general</Description>')
    G.append('      <Type>GL</Type>')
    cod_propriu = _cod_propriu(res.prof)
    for n in res.note:
        G.append('      <Transaction>')
        G.append('        <TransactionID>%s</TransactionID>' % _esc(n.id))
        G.append('        <Period>%d</Period>' % res.luna)
        G.append('        <PeriodYear>%d</PeriodYear>' % res.an)
        G.append('        <TransactionDate>%s</TransactionDate>' % _d(n.data))
        G.append('        <Description>%s</Description>' % _esc(_t(n.descriere, _LIM["d406"]["Description"])))
        G.append('        <SystemEntryDate>%s</SystemEntryDate>' % _d(n.data))
        G.append('        <GLPostingDate>%s</GLPostingDate>' % _d(n.data))
        # CustomerID/SupplierID la nivel Transaction: OBLIGATORII in XSD (minOccurs=1,
        # dupa GLPostingDate, INAINTE de TransactionLine). Lipsa lor era prima
        # discrepanta structurala reala din document - validatorul o raporta insa pe
        # TransactionLine(1) (sectiunea urmatoare parsata), nu aici. Sensul tranzactiei
        # (client vs furnizor) se ia din prima linie de partener; altfel cod propriu
        # pe ambele (regula GL.19/GL.20, aceeasi ca la linii).
        t_cust, t_supp = cod_propriu, cod_propriu
        for l in n.linii:
            radacina = l.cont.split(".")[0] if "." in l.cont else l.cont
            if radacina == "4111" and l.cont_partener_id:
                t_cust, t_supp = l.cont_partener_id, "0"
                break
            if radacina == "401" and l.cont_partener_id:
                t_cust, t_supp = "0", l.cont_partener_id
                break
        G.append('        <CustomerID>%s</CustomerID>' % _esc(t_cust))
        G.append('        <SupplierID>%s</SupplierID>' % _esc(t_supp))
        for l in n.linii:
            G.append('        <TransactionLine>')
            G.append('          <RecordID>%s</RecordID>' % _esc(l.record_id))
            G.append('          <AccountID>%s</AccountID>' % _esc(l.cont))
            # CustomerID SI SupplierID: AMBELE OBLIGATORII in XSD pe FIECARE linie
            # (minOccurs=1, dupa AccountID, inainte de Description). Vechiul cod emitea
            # doar unul, conditionat -> pe liniile 707/4427/banca nu aparea niciunul ->
            # "elementul 'CustomerID' ar fi trebuit sa apara de minimum 1 ori".
            # Valorile: partenerul REAL pe linia de client/furnizor (l.cont_partener_id
            # = JOIN inregistrari.factura_id -> facturi.tert_cui), "0" pe partea opusa,
            # iar pe liniile fara evidenta pe partener AMBELE = codul propriu (regula
            # oficiala GL.28/GL.29 nota [17]). NICIODATA ambele "0" (regula sintactica).
            l_cust, l_supp = _cust_supp_linie(l.cont, l.cont_partener_id, cod_propriu)
            G.append('          <CustomerID>%s</CustomerID>' % _esc(l_cust))
            G.append('          <SupplierID>%s</SupplierID>' % _esc(l_supp))
            # Description: obligatoriu, nevid. Daca linia n-are descriere proprie,
            # folosim descrierea notei (era "" fix, respins ca "atribut vid nepermis").
            desc_linie = l.descriere or n.descriere or ("Nota %s" % n.id)
            G.append('          <Description>%s</Description>' % _esc(desc_linie))
            if l.debit and not l.credit:
                G.append('          <DebitAmount>')
                G.append('            <Amount>%s</Amount>' % _dec(l.debit))
                G.append('            <CurrencyCode>RON</CurrencyCode>')
                G.append('            <CurrencyAmount>%s</CurrencyAmount>' % _dec(l.debit))
                G.append('          </DebitAmount>')
            else:
                G.append('          <CreditAmount>')
                G.append('            <Amount>%s</Amount>' % _dec(l.credit))
                G.append('            <CurrencyCode>RON</CurrencyCode>')
                G.append('            <CurrencyAmount>%s</CurrencyAmount>' % _dec(l.credit))
                G.append('          </CreditAmount>')
            G.append('          <TaxInformation>')
            G.append('            <TaxType>300</TaxType>')
            G.append('            <TaxCode>%s</TaxCode>' % TAXCODE_NOTA_FARA_TVA)
            G.append('            <TaxAmount>')
            G.append('              <Amount>0.00</Amount>')
            G.append('              <CurrencyCode>RON</CurrencyCode>')
            G.append('              <CurrencyAmount>0.00</CurrencyAmount>')
            G.append('            </TaxAmount>')
            G.append('          </TaxInformation>')
            G.append('        </TransactionLine>')
        G.append('      </Transaction>')
    G.append('    </Journal>')
    G.append('  </GeneralLedgerEntries>')
    return G


def _factura_xml(f, este_vanzare, indent):
    """Generează un element <Invoice> conform InvoiceStructure din XSD."""
    sp = " " * indent
    X = []
    X.append('%s<Invoice>' % sp)
    X.append('%s  <InvoiceNo>%s</InvoiceNo>' % (sp, _esc(f.nr)))
    if este_vanzare:
        X.append('%s  <CustomerInfo>' % sp)
        X.append('%s    <CustomerID>%s</CustomerID>' % (sp, _esc(f.partener_id)))
        X.append('%s    <BillingAddress>' % sp)
        X.append('%s      <City>-</City>' % sp)
        X.append('%s      <Country>RO</Country>' % sp)
        X.append('%s    </BillingAddress>' % sp)
        X.append('%s  </CustomerInfo>' % sp)
    else:
        X.append('%s  <SupplierInfo>' % sp)
        X.append('%s    <SupplierID>%s</SupplierID>' % (sp, _esc(f.partener_id)))
        X.append('%s    <BillingAddress>' % sp)
        X.append('%s      <City>-</City>' % sp)
        X.append('%s      <Country>RO</Country>' % sp)
        X.append('%s    </BillingAddress>' % sp)
        X.append('%s  </SupplierInfo>' % sp)
    X.append('%s  <AccountID>%s</AccountID>' % (sp, _esc(f.cont)))
    X.append('%s  <InvoiceDate>%s</InvoiceDate>' % (sp, _d(f.data)))
    X.append('%s  <InvoiceType>%s</InvoiceType>' % (sp, _esc(f.tip)))
    X.append('%s  <SelfBillingIndicator>%s</SelfBillingIndicator>' % (sp, _esc(f.self_billing)))
    for l in f.linii:
        X.append('%s  <InvoiceLine>' % sp)
        X.append('%s    <LineNumber>%d</LineNumber>' % (sp, l.nr))
        X.append('%s    <AccountID>%s</AccountID>' % (sp, _esc(l.cont)))
        X.append('%s    <Quantity>%s</Quantity>' % (sp, _dec(l.cantitate)))
        X.append('%s    <InvoiceUOM>%s</InvoiceUOM>' % (sp, _esc(l.um)))
        X.append('%s    <UnitPrice>%s</UnitPrice>' % (sp, _dec(l.pret_unitar)))
        X.append('%s    <TaxPointDate>%s</TaxPointDate>' % (sp, _d(f.data)))
        X.append('%s    <Description>%s</Description>' % (sp, _esc(_t(l.descriere, _LIM["d406"]["Description"]))))
        X.append('%s    <InvoiceLineAmount>' % sp)
        X.append('%s      <Amount>%s</Amount>' % (sp, _dec(l.valoare)))
        X.append('%s      <CurrencyCode>RON</CurrencyCode>' % sp)
        X.append('%s      <CurrencyAmount>%s</CurrencyAmount>' % (sp, _dec(l.valoare)))
        X.append('%s    </InvoiceLineAmount>' % sp)
        X.append('%s    <DebitCreditIndicator>%s</DebitCreditIndicator>' % (sp, _esc(l.sens)))
        X.append('%s    <TaxInformation>' % sp)
        X.append('%s      <TaxType>300</TaxType>' % sp)
        X.append('%s      <TaxCode>%s</TaxCode>' % (sp, _esc(l.tva_cod)))
        X.append('%s      <TaxPercentage>%s</TaxPercentage>' % (sp, _dec(l.tva_procent)))
        X.append('%s      <TaxBase>%s</TaxBase>' % (sp, _dec(l.valoare)))
        X.append('%s      <TaxAmount>' % sp)
        X.append('%s        <Amount>%s</Amount>' % (sp, _dec(l.tva_suma)))
        X.append('%s        <CurrencyCode>RON</CurrencyCode>' % sp)
        X.append('%s        <CurrencyAmount>%s</CurrencyAmount>' % (sp, _dec(l.tva_suma)))
        X.append('%s      </TaxAmount>' % sp)
        X.append('%s    </TaxInformation>' % sp)
        X.append('%s  </InvoiceLine>' % sp)
    # totaluri document: TaxCode/TaxPercentage din PRIMA linie a facturii, nu
    # hardcodat 310/21% (gresit pentru achizitii si pentru facturile cu cota 0 -
    # intracomunitare, taxare inversa).
    prima = f.linii[0] if f.linii else None
    tcod_tot = prima.tva_cod if prima else "310312"
    tperc_tot = prima.tva_procent if prima else Decimal(0)
    X.append('%s  <InvoiceDocumentTotals>' % sp)
    X.append('%s    <TaxInformationTotals>' % sp)
    X.append('%s      <TaxType>300</TaxType>' % sp)
    X.append('%s      <TaxCode>%s</TaxCode>' % (sp, _esc(tcod_tot)))
    X.append('%s      <TaxPercentage>%s</TaxPercentage>' % (sp, _dec(tperc_tot)))
    X.append('%s      <TaxBase>%s</TaxBase>' % (sp, _dec(f.net)))
    X.append('%s      <TaxAmount>' % sp)
    X.append('%s        <Amount>%s</Amount>' % (sp, _dec(f.tva)))
    X.append('%s        <CurrencyCode>RON</CurrencyCode>' % sp)
    X.append('%s        <CurrencyAmount>%s</CurrencyAmount>' % (sp, _dec(f.tva)))
    X.append('%s      </TaxAmount>' % sp)
    X.append('%s    </TaxInformationTotals>' % sp)
    X.append('%s    <NetTotal>%s</NetTotal>' % (sp, _dec(f.net)))
    X.append('%s    <GrossTotal>%s</GrossTotal>' % (sp, _dec(f.brut)))
    X.append('%s  </InvoiceDocumentTotals>' % sp)
    X.append('%s</Invoice>' % sp)
    return X


def _source_documents(res):
    """SourceDocuments: SalesInvoices, PurchaseInvoices, Payments, MovementOfGoods.

    REGULA SECTIUNILOR GOALE (dovedita pe validatorul oficial 16.07.2026, experimente
    directe pe XML): sub-sectiunile cu liste (SalesInvoices/PurchaseInvoices/Payments)
    NU se emit cand sunt goale - se OMIT complet. Emise vide (cu NumberOfEntries=0, fara
    Invoice/Payment) validatorul le respinge: "elementul 'Payment' ar fi trebuit sa
    apara de minimum 1 ori" / "elementul '' ... minimum 1 ori". Desi XSD da Invoice si
    Payment cu minOccurs=0, DUK cere continut cand sectiunea e prezenta si accepta
    absenta ei. MovementOfGoods e OBLIGATORIU (nu se poate omite: "MovementOfGoods ...
    minimum 1 ori") DAR trebuie GOL - self-closed, fara NumberOfMovementLines/totaluri
    ("NumberOfMovementLines a depasit numarul maxim de aparitii (0)"), exact ca
    MovementTypeTable/Owners/Assets: stocurile se raporteaza doar la cerere, nu lunar.
    """
    fv, fc, pl = res.facturi_vanzare, res.facturi_cumparare, res.plati
    S = ['  <SourceDocuments>']
    # SalesInvoices - doar daca exista facturi de vanzare
    if fv:
        net_v = sum(f.net for f in fv)
        S.append('    <SalesInvoices>')
        S.append('      <NumberOfEntries>%d</NumberOfEntries>' % len(fv))
        S.append('      <TotalDebit>0.00</TotalDebit>')
        S.append('      <TotalCredit>%s</TotalCredit>' % _dec(net_v))
        for f in fv:
            S.extend(_factura_xml(f, True, 6))
        S.append('    </SalesInvoices>')
    # PurchaseInvoices - doar daca exista facturi de cumparare
    if fc:
        net_c = sum(f.net for f in fc)
        S.append('    <PurchaseInvoices>')
        S.append('      <NumberOfEntries>%d</NumberOfEntries>' % len(fc))
        S.append('      <TotalDebit>%s</TotalDebit>' % _dec(net_c))
        S.append('      <TotalCredit>0.00</TotalCredit>')
        for f in fc:
            S.extend(_factura_xml(f, False, 6))
        S.append('    </PurchaseInvoices>')
    # Payments - doar daca exista plati
    if pl:
        cod_propriu = _cod_propriu(res.prof)
        td = sum(sum(l.suma for l in p.linii if l.sens == "D") for p in pl)
        tc = sum(sum(l.suma for l in p.linii if l.sens == "C") for p in pl)
        S.append('    <Payments>')
        S.append('      <NumberOfEntries>%d</NumberOfEntries>' % len(pl))
        S.append('      <TotalDebit>%s</TotalDebit>' % _dec(td))
        S.append('      <TotalCredit>%s</TotalCredit>' % _dec(tc))
        for p in pl:
            S.append('      <Payment>')
            S.append('        <PaymentRefNo>%s</PaymentRefNo>' % _esc(p.ref))
            S.append('        <TransactionID>%s</TransactionID>' % _esc(p.ref))
            S.append('        <TransactionDate>%s</TransactionDate>' % _d(p.data))
            S.append('        <PaymentMethod>%s</PaymentMethod>' % _esc(payment_method_anaf(p.metoda)))
            S.append('        <Description>%s</Description>' % _esc(_t(p.descriere or "Plata", _LIM["d406"]["Description"])))
            for l in p.linii:
                # CustomerID/SupplierID pe PaymentLine: aceeasi regula ca la GL
                # (AMBELE obligatorii, niciodata ambele "0") - cod propriu pe partea
                # neaplicabila, partenerul real pe partea de client/furnizor.
                pl_cust, pl_supp = _cust_supp_linie(l.cont, "", cod_propriu)
                S.append('        <PaymentLine>')
                S.append('          <LineNumber>%d</LineNumber>' % l.nr)
                if l.doc_sursa:
                    S.append('          <SourceDocumentID>%s</SourceDocumentID>' % _esc(l.doc_sursa))
                S.append('          <AccountID>%s</AccountID>' % _esc(l.cont))
                S.append('          <CustomerID>%s</CustomerID>' % _esc(pl_cust))
                S.append('          <SupplierID>%s</SupplierID>' % _esc(pl_supp))
                S.append('          <Description>%s</Description>' % _esc(_t(l.descriere, _LIM["d406"]["Description"])))
                S.append('          <DebitCreditIndicator>%s</DebitCreditIndicator>' % _esc(l.sens))
                S.append('          <PaymentLineAmount>')
                S.append('            <Amount>%s</Amount>' % _dec(l.suma))
                S.append('            <CurrencyCode>RON</CurrencyCode>')
                S.append('            <CurrencyAmount>%s</CurrencyAmount>' % _dec(l.suma))
                S.append('          </PaymentLineAmount>')
                S.append('          <TaxInformation>')
                S.append('            <TaxType>300</TaxType>')
                S.append('            <TaxCode>%s</TaxCode>' % TAXCODE_NOTA_FARA_TVA)
                S.append('            <TaxAmount>')
                S.append('              <Amount>0.00</Amount>')
                S.append('              <CurrencyCode>RON</CurrencyCode>')
                S.append('              <CurrencyAmount>0.00</CurrencyAmount>')
                S.append('            </TaxAmount>')
                S.append('          </TaxInformation>')
                S.append('        </PaymentLine>')
            S.append('      </Payment>')
        S.append('    </Payments>')
    # MovementOfGoods: OBLIGATORIU dar GOL (self-closed) in raportarea lunara.
    S.append('    <MovementOfGoods/>')
    S.append('  </SourceDocuments>')
    return S


def build_xml(res):
    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    H.append('<AuditFile xmlns="%s">' % NS)
    H.extend(_header(res))
    H.extend(_masterfiles(res))
    H.extend(_gl_entries(res))
    H.extend(_source_documents(res))
    H.append('</AuditFile>')
    return "\n".join(H)


def pull(conn, schema, an, luna):
    import psycopg2.extras as _E
    di = "%04d-%02d-01" % (an, luna)
    ds = ("%04d-01-01" % (an + 1,)) if luna == 12 else ("%04d-%02d-01" % (an, luna + 1))
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, adresa, oras, cod_postal, platitor_tva FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        conturi, clienti, furnizori, note = [], [], [], []
        strain = []   # conturi din plan care nu apartin normei declarate
        try:
            cur.execute("SELECT simbol, denumire, COALESCE(tip,'Bifunctional') AS tip, "
                        "COALESCE(sold_debitor,0) AS sd, COALESCE(sold_creditor,0) AS sc "
                        "FROM plan_conturi ORDER BY simbol")
            # Declaram DOAR conturile din planul normei firmei: ANAF respinge restul
            # ("ID-ul contului [731] trebuie sa se gaseasca in planul de conturi").
            # Filtram dupa nomenclatorul OFICIAL, nu dupa o lista scrisa de noi.
            oficial = plan_oficial(prof.get("baza_contabila"))
            for r in cur.fetchall():
                if oficial and r["simbol"] not in oficial:
                    strain.append(r["simbol"])
                    continue
                # cont_standard = radacina sintetica ('401.05' -> '401'), nu simbolul
                # intreg - dovedit gresit azi: era setat = simbol (identic cu id),
                # deci pentru analitice ramanea tot cu punct -> AccountID respins
                # ("numar intreg eronat"). SAF-T identifica contul dupa sintetic.
                simb = r["simbol"]
                sintetic = simb.split(".")[0] if "." in simb else simb
                conturi.append(Cont(id=simb, descriere=r["denumire"], cont_standard=sintetic,
                                    tip=r["tip"], sold_inchidere_d=Decimal(str(r["sd"])),
                                    sold_inchidere_c=Decimal(str(r["sc"]))))
        except Exception as e:
            # MASCA SCOASA (27.07.2026, al doilea val). In PostgreSQL un query esuat
            # OTRAVESTE tranzactia: masca ascundea cauza, iar eroarea aparea abia in
            # blocul urmator, cu mesaj gresit ('citirea notelor a esuat' cand de fapt
            # picase planul de conturi). Dovedit pe tenant_002 prin redenumirea tabelei.
            raise RuntimeError("D406: citirea planului de conturi a eșuat - %s" % e) from e
        try:
            # SAF-T: identitatea partenerului (RegistrationNumber/CustomerID/SupplierID) = format
            # oficial via _partener_id_saft (00/01/02+cod, 03+CNP, 04+nume) - ACEEASI logica ca
            # fallback-ul (derivare din facturi) si ca liniile de tranzactie. NU id-ul brut de
            # nomenclator: bug PROD (11.08) -> DUK "RegistrationNumber/CustomerID format invalid"
            # pe orice tenant cu nomenclator POPULAT; mascat de nomenclator gol (-> calea fallback).
            # Gard anti-regresie: core/test_d406_partener_id_neconform.py.
            cur.execute("SELECT id, nume, cui, oras FROM clienti ORDER BY id")
            vazut_cl = set()
            for r in cur.fetchall():
                pid = _partener_id_saft(r["cui"], r["nume"], eticheta=r["nume"])
                if pid and pid not in vazut_cl:
                    vazut_cl.add(pid)
                    clienti.append(Partener(id=pid, nume=r["nume"] or "", cui=r["cui"] or "", oras=r["oras"] or ""))
        except ValueError:
            raise  # eroare de CONTINUT (CUI/CNP partener invalid) - nu se mascheaza in RuntimeError
        except Exception as e:
            # MASCA SCOASA (27.07.2026, al doilea val). In PostgreSQL un query esuat
            # OTRAVESTE tranzactia: masca ascundea cauza, iar eroarea aparea abia in
            # blocul urmator, cu mesaj gresit ('citirea notelor a esuat' cand de fapt
            # picase nomenclatorul de clienti). Dovedit pe tenant_002 prin redenumirea tabelei.
            raise RuntimeError("D406: citirea nomenclatorului de clienți a eșuat - %s" % e) from e
        try:
            # SAF-T: identitatea partenerului (RegistrationNumber/CustomerID/SupplierID) = format
            # oficial via _partener_id_saft (00/01/02+cod, 03+CNP, 04+nume) - ACEEASI logica ca
            # fallback-ul (derivare din facturi) si ca liniile de tranzactie. NU id-ul brut de
            # nomenclator: bug PROD (11.08) -> DUK "RegistrationNumber/CustomerID format invalid"
            # pe orice tenant cu nomenclator POPULAT; mascat de nomenclator gol (-> calea fallback).
            # Gard anti-regresie: core/test_d406_partener_id_neconform.py.
            cur.execute("SELECT id, nume, cui, oras FROM furnizori ORDER BY id")
            vazut_fu = set()
            for r in cur.fetchall():
                pid = _partener_id_saft(r["cui"], r["nume"], eticheta=r["nume"])
                if pid and pid not in vazut_fu:
                    vazut_fu.add(pid)
                    furnizori.append(Partener(id=pid, nume=r["nume"] or "", cui=r["cui"] or "", oras=r["oras"] or ""))
        except ValueError:
            raise  # eroare de CONTINUT (CUI/CNP partener invalid) - nu se mascheaza in RuntimeError
        except Exception as e:
            # MASCA SCOASA (27.07.2026, al doilea val). In PostgreSQL un query esuat
            # OTRAVESTE tranzactia: masca ascundea cauza, iar eroarea aparea abia in
            # blocul urmator, cu mesaj gresit ('citirea notelor a esuat' cand de fapt
            # picase nomenclatorul de furnizori). Dovedit pe tenant_002 prin redenumirea tabelei.
            raise RuntimeError("D406: citirea nomenclatorului de furnizori a eșuat - %s" % e) from e
        # FALLBACK: daca nomenclatoarele clienti/furnizori sunt goale (dovedit
        # 16.07.2026: facturile create direct NU populeaza automat clienti/
        # furnizori - limitare cunoscuta, nereparata inca la sursa), derivam
        # macar un partener minimal din facturi, ca SAF-T sa aiba CustomerID/
        # SupplierID valabil (obligatoriu pe liniile 4111/401). De inlocuit cu
        # nomenclatorul real cand facturile vor popula clienti/furnizori automat.
        try:
            # FALLBACK: nomenclatoarele clienti/furnizori sunt goale (dovedit
            # 16.07.2026: facturile create direct NU le populeaza automat -
            # limitare cunoscuta, de reparat la sursa in facturi_api.py). Derivam
            # TOTI partenerii distincti din facturi, cu formatul oficial S.C.1
            # (00/01/02 + cod), ca fiecare linie 4111/401 sa aiba un CustomerID/
            # SupplierID valabil - nu doar primul partener (LIMIT 1 lasa restul
            # tranzactiilor fara CustomerID, cum s-a dovedit cu factura UE).
            # ROOT FIX (tip-04): derivarea partenerilor din facturi trebuie sa
            # foloseasca ACEEASI identitate ca referinta de pe factura
            # (_partener_id_saft, folosit la construirea Invoice mai jos): cu cod
            # fiscal -> 00/01/02, iar PF FARA cod fiscal declarat -> tipul 04 + cod
            # din nume. Vechiul cod folosea _partener_registration_number (doar
            # 00/01/02) SI filtra tert_cui != '' -> partenerul PF (tip 04) referit
            # de factura (SupplierID/CustomerID=04...) NU aparea in <Customers>/
            # <Suppliers> (neconformitate: referit pe factura, absent din master).
            # Dedup pe identitatea SAF-T (pid), NU pe tert_cui: toti PF au tert_cui=''
            # -> DISTINCT ON (tert_cui) i-ar fi colapsat pe toti intr-un singur rand.
            if not clienti:
                cur.execute(
                    "SELECT tert_cui, tert_nume FROM facturi "
                    "WHERE directie='emisa' ORDER BY id")
                vazut = set()
                for r in cur.fetchall():
                    pid = _partener_id_saft(r["tert_cui"], r["tert_nume"], eticheta=r["tert_nume"])
                    if pid and pid not in vazut:
                        vazut.add(pid)
                        clienti.append(Partener(id=pid, nume=r["tert_nume"] or "",
                                                cui=r["tert_cui"] or "", oras=""))
            if not furnizori:
                cur.execute(
                    "SELECT tert_cui, tert_nume FROM facturi "
                    "WHERE directie='primita' ORDER BY id")
                vazut = set()
                for r in cur.fetchall():
                    pid = _partener_id_saft(r["tert_cui"], r["tert_nume"], eticheta=r["tert_nume"])
                    if pid and pid not in vazut:
                        vazut.add(pid)
                        furnizori.append(Partener(id=pid, nume=r["tert_nume"] or "",
                                                  cui=r["tert_cui"] or "", oras=""))
        except ValueError:
            # Eroare de CONTINUT (checksum CUI/CNP partener, T1): trece nemodificata,
            # nu se mascheaza in RuntimeError (cauza reala ar fi ascunsa).
            raise
        except Exception as e:
            # MASCA SCOASA (27.07.2026, al doilea val). In PostgreSQL un query esuat
            # OTRAVESTE tranzactia: masca ascundea cauza, iar eroarea aparea abia in
            # blocul urmator, cu mesaj gresit ('citirea notelor a esuat' cand de fapt
            # picase derivarea partenerilor din facturi). Dovedit pe tenant_002 prin redenumirea tabelei.
            raise RuntimeError("D406: derivarea partenerilor din facturi a eșuat - %s" % e) from e
        try:
            # COLOANE REALE (dovedit 16.07.2026 prin \d tenant_002.inregistrari_linii):
            # cont_debit, cont_credit, suma - NU cont/debit/credit cum interoga codul
            # vechi. Interogarea gresita CRAPA mereu, dar era prinsa de un except: pass
            # tacut - <GeneralLedgerEntries> ramanea mereu GOL, pentru ORICE firma,
            # indiferent cate note validate existau. Bug universal, nu specific unei
            # firme - descoperit abia acum, prin auditul pe date reale ale lui DANTE.
            # O linie din inregistrari_linii (cont_debit + cont_credit + suma) e o
            # singura miscare contabila; in SAF-T devine DOUA TransactionLine (una pe
            # contul debitor cu debit=suma, alta pe contul creditor cu credit=suma) -
            # asta e conventia LinieNota deja existenta (un cont, debit SAU credit).
            # Doar notele VALIDATE (regula EVIDENTEI: ciorna nu e evidenta).
            # JOIN cu facturi prin i.factura_id: fiecare nota poate purta partenerul
            # REAL al facturii care a generat-o - nu se mai ghiceste "primul client
            # din lista" (bug dovedit 16.07.2026: 5 tranzactii cu 5 parteneri diferiti
            # primeau toate CustomerID-ul aceluiasi client, fiscal incorect - Auchan
            # Italia aparea pe factura ALTEX). Notele fara factura_id (dividende,
            # inregistrari manuale) raman fara partener - nu se aplica.
            cur.execute("SELECT i.id, i.data, i.descriere, l.cont_debit, l.cont_credit, l.suma, "
                        "f.tert_cui, f.tert_nume "
                        "FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                        "LEFT JOIN facturi f ON f.id = i.factura_id "
                        "WHERE i.status = 'validata' AND i.data >= %s AND i.data < %s "
                        "ORDER BY i.id, l.id", (di, ds))
            nmap = {}
            for r in cur.fetchall():
                n = nmap.get(r["id"])
                if n is None:
                    n = Nota(id=str(r["id"]), data=r["data"], descriere=r["descriere"] or "")
                    nmap[r["id"]] = n
                suma = Decimal(str(r["suma"] or 0))
                pid = _partener_registration_number(r["tert_cui"], eticheta=r["tert_nume"]) if r["tert_cui"] else ""
                n.linii.append(LinieNota(record_id=str(len(n.linii) + 1), cont=r["cont_debit"] or "",
                                         descriere="", debit=suma, credit=Decimal("0"),
                                         cont_partener_id=pid))
                n.linii.append(LinieNota(record_id=str(len(n.linii) + 1), cont=r["cont_credit"] or "",
                                         descriere="", debit=Decimal("0"), credit=suma,
                                         cont_partener_id=pid))
            note = list(nmap.values())
        except ValueError:
            # Eroare de CONTINUT (checksum CUI/CNP partener, T1): trece nemodificata,
            # nu se mascheaza in RuntimeError (cauza reala ar fi ascunsa).
            raise
        except Exception as e:
            # MASCA SCOASA (27.07.2026) - vezi nota de la blocul facturi.
            raise RuntimeError("D406: citirea notelor a eșuat - %s" % e) from e
        facturi_vanzare, facturi_cumparare, plati = [], [], []
        um_necunoscute = []  # [B17] UM necunoscute -> H87; (factura, UM) NUMITE in avertisment, nu tacit (T3)
        cote_necunoscute = []  # T3: cota fara cod TaxCode livrari -> 310312 (taxare inversa); (factura, cota) NUMITE
        try:
            # COLOANE REALE facturi (dovedit 16.07.2026 prin \d tenant_002.facturi):
            # data_emitere (NU 'data'), tert_cui/tert_nume (NU partener_id/nume),
            # total = BRUT cu TVA (NU 'baza'), tva, taxare_inversa, storno_din_id.
            # Nu exista coloana 'cota_tva' - cota se DEDUCE (tva / net * 100). Query-ul
            # vechi cerea coloane inexistente -> arunca -> except: pass -> 0 facturi in
            # SalesInvoices/PurchaseInvoices, DESI existau 5 facturi reale in iunie
            # (aceeasi clasa de bug ca la note: schema presupusa != schema reala).
            # LINII REALE (27.07.2026). Codul anterior emitea o SINGURA linie sintetica
            # per factura: cantitate=1, pret_unitar=net, um=H87 implicit, descriere=
            # numele partenerului, cota DEDUSA din antet (tva/net*100). Dovedit fals pe
            # date reale (tenant_002, factura 7 "Deseuri fier vechi"): in DB 1000 kg x
            # 5,00 lei/kg; in SAF-T iesea 1 buc x 5000 lei. Cantitate, UM si descriere
            # FALSE catre ANAF. In plus cota dedusa din antet e gresita pe factura cu
            # cote mixte (21% + 11% -> o cota medie care nu corespunde niciunei linii).
            # factura_linii are descriere/um/cantitate/pret_unitar/cota_tva. uom_unece()
            # exista din 16.07 (d406.py:101) si traducea deja 'buc'/'kg' in H87/KGM -
            # era scrisa si NEAPELATA aici.
            cur.execute("SELECT factura_id, id, descriere, um, "
                        "COALESCE(cantitate,0) AS cantitate, "
                        "COALESCE(pret_unitar,0) AS pret_unitar, "
                        "COALESCE(cota_tva,0) AS cota_tva "
                        "FROM factura_linii WHERE factura_id IN "
                        "(SELECT id FROM facturi WHERE data_emitere >= %s AND data_emitere < %s) "
                        "ORDER BY factura_id, id", (di, ds))
            linii_pe_factura = {}
            for lr in cur.fetchall():
                linii_pe_factura.setdefault(lr["factura_id"], []).append(lr)
            cur.execute("SELECT id, numar, data_emitere, tert_cui, tert_nume, "
                        "COALESCE(total,0) AS total, COALESCE(tva,0) AS tva, "
                        "COALESCE(taxare_inversa,false) AS ti, storno_din_id, directie "
                        "FROM facturi WHERE data_emitere >= %s AND data_emitere < %s ORDER BY id", (di, ds))
            for r in cur.fetchall():
                total = Decimal(str(r["total"]))
                tva = Decimal(str(r["tva"]))
                net = total - tva
                este_v = (r["directie"] or "emisa") in ("emisa", "vanzare")
                # InvoiceType = COD SAFcodeType (Nom_Tipuri_facturi): 380 factura
                # comerciala, 381 nota de credit (storno). Valoarea DB 'tip' NU e cod valid.
                itype = "381" if r["storno_din_id"] else "380"
                # SupplierID/CustomerID pe factura NU poate fi "0" (regula oficiala
                # SD.P.22/SD.P.23): furnizorul/clientul de pe o factura are mereu
                # identitate. Fara cod fiscal (PF) -> tipul 04 + cod intern (vezi
                # _partener_id_saft). "0" era respins de DUK SAF-T ("SupplierID nu
                # poate fi 0") pe achizitiile de la persoane fizice.
                pid = _partener_id_saft(r["tert_cui"], r["tert_nume"], eticheta=r["tert_nume"])
                if not pid:
                    raise ValueError(
                        "D406: factura %s nu are nici cod fiscal nici nume de partener - "
                        "nu se poate emite un SupplierID/CustomerID valid (interzis '0'). "
                        "Completează partenerul pe factura." % (r["numar"] or r["id"]))
                cont_l = "707" if este_v else "371"
                sens = "C" if este_v else "D"
                linii = []
                for idx, lr in enumerate(linii_pe_factura.get(r["id"], []), 1):
                    cant = Decimal(str(lr["cantitate"]))
                    pret = Decimal(str(lr["pret_unitar"]))
                    cota_l = Decimal(str(lr["cota_tva"])).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
                    val = (cant * pret).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    tva_l = (val * cota_l / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    # TaxCode PE LINIE, dupa cota liniei si sensul operatiunii.
                    if este_v:
                        tcod_l = _taxcode_livrari(cota_l, r["data_emitere"])
                        if not _cota_livrari_in_tabela(cota_l, r["data_emitere"]):
                            cote_necunoscute.append((r["numar"] or str(r["id"]), str(cota_l)))
                    else:
                        tcod_l = "300101" if (r["ti"] or cota_l == 0) else "300501"
                    um_cod, _um_stiut = uom_unece(lr["um"])
                    if not _um_stiut and lr.get("um"):
                        um_necunoscute.append((r["numar"] or str(r["id"]), str(lr["um"]).strip()))
                    linii.append(LinieFactura(nr=idx, cont=cont_l,
                                              descriere=lr["descriere"] or "Produs/serviciu",
                                              cantitate=cant, um=um_cod, pret_unitar=pret,
                                              valoare=val, sens=sens, tva_cod=tcod_l,
                                              tva_procent=cota_l, tva_suma=tva_l))
                if linii:
                    # RECONCILIERE OBLIGATORIE: liniile trebuie sa dea antetul. Divergenta
                    # tacuta intre doua surse ale aceleiasi facturi = eroare, nu detaliu.
                    nl = sum(l.valoare for l in linii)
                    tl = sum(l.tva_suma for l in linii)
                    if abs(nl - net) > Decimal("0.01") or abs(tl - tva) > Decimal("0.01"):
                        raise ValueError(
                            "D406: factura %s nu se reconciliază - antet net=%s tva=%s, "
                            "linii net=%s tva=%s. Corectează factura înainte de generare."
                            % (r["numar"] or r["id"], net, tva, nl, tl))
                else:
                    # Factura fara linii in DB. NU se inventeaza cantitate: 1 x net, UM
                    # implicita, descriere care SPUNE ca detaliul lipseste (semnal in XML,
                    # nu mimare de detaliu real).
                    cota = (tva / net * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP) if net else Decimal(0)
                    if este_v:
                        tcod_l = _taxcode_livrari(cota, r["data_emitere"])
                        if not _cota_livrari_in_tabela(cota, r["data_emitere"]):
                            cote_necunoscute.append((r["numar"] or str(r["id"]), str(cota)))
                    else:
                        tcod_l = "300101" if (r["ti"] or cota == 0) else "300501"
                    linii = [LinieFactura(nr=1, cont=cont_l,
                                          descriere="Factura fără detaliu de linii",
                                          cantitate=Decimal(1), um=UOM_IMPLICIT, pret_unitar=net,
                                          valoare=net, sens=sens, tva_cod=tcod_l,
                                          tva_procent=cota, tva_suma=tva)]
                f = Factura(nr=r["numar"] or str(r["id"]), data=r["data_emitere"],
                            partener_id=pid, partener_nume=r["tert_nume"] or "",
                            tip=itype, cont=("4111" if este_v else "401"), linii=linii)
                (facturi_vanzare if este_v else facturi_cumparare).append(f)
        except ValueError:
            # Eroare de CONTINUT (reconciliere linii-antet), nu de citire: trece
            # nemodificata. Altfel garda de mai sus ar fi raportata drept "citirea a
            # esuat" - cauza reala ascunsa sub un mesaj tehnic gresit, adica exact
            # invelisul pe care il scoatem aici.
            raise
        except Exception as e:
            # MASCA SCOASA (27.07.2026): `except: pass` facea ca orice query rupt sa
            # produca SalesInvoices/PurchaseInvoices goale intr-un XML valid structural.
            # Clasa de bug din 16.07. Orice garda pusa deasupra ar fi fost inghitita aici.
            raise RuntimeError("D406: citirea facturilor a eșuat - %s" % e) from e
    return prof, conturi, clienti, furnizori, note, facturi_vanzare, facturi_cumparare, plati, strain, um_necunoscute, cote_necunoscute


def erori_generare(prof):
    """Poarta bazei nule: profil incomplet -> STOP cu mesaj clar, nu XML respins de ANAF."""
    erori = []
    _cui = str(prof.get("cui") or "").strip()
    if not _cui:
        erori.append("LIPSĂ CUI firma.")
    else:
        # T1 (CATALOG_INVALIDITATE.md): cifra de control a CUI-ului firmei, verificata OFFLINE
        # pre-DUK. Un CUI cu checksum gresit era emis tacit in RegistrationNumber -> DUK
        # "formatul este invalid" abia la depunere. Firma proprie e mereu persoana juridica.
        _ok, _motiv = _vcui(_cui)
        if not _ok:
            erori.append("CUI firma invalid (%s) - %s. Corectează CUI-ul în profilul firmei "
                         "(DUK regula S.CMH.1)." % (_cui, _motiv))
    if not str(prof.get("nume") or "").strip():
        erori.append("LIPSĂ denumire firma.")
    return erori


def genereaza(conn, schema, an, luna):
    if luna < 1 or luna > 12:
        raise ValueError("Luna invalidă: %r" % luna)
    prof, conturi, clienti, furnizori, note, fv, fc, plati, strain, um_necunoscute, cote_necunoscute = pull(conn, schema, an, luna)
    _er = erori_generare(prof)
    if _er:
        raise ValueError("D406 nu se poate genera: " + " ".join(_er))
    res = construieste(prof, an, luna, conturi, clienti, furnizori, note=note,
                       facturi_vanzare=fv, facturi_cumparare=fc, plati=plati)
    # T2 (CATALOG_INVALIDITATE.md): valideaza(res) are o verificare AccountType (Activ/Pasiv/
    # Bifunctional) pe care genereaza() nu o chema (cod mort). O cablam TINTIT aici (nu tot
    # valideaza(res), care ar bloca fixture-le legitime fara plan de conturi): un AccountType in
    # afara nomenclatorului era emis tacit -> DUK il respinge; acum prins pre-DUK cu mesaj clar.
    for _c in res.conturi:
        if _c.tip not in ACCOUNT_TYPE:
            raise ValueError("D406: AccountType invalid pentru contul %s: %r (trebuie Activ/Pasiv/"
                             "Bifunctional). Corectează tipul contului în planul de conturi." % (_c.id, _c.tip))
    if strain:
        # Conturile din planul firmei care NU sunt in nomenclatorul normei declarate se EXCLUD (ANAF le
        # respinge: "ID-ul contului trebuie sa se gaseasca in planul de conturi"). NU tacit - le NUMIM in
        # avertisment, ca sa nu dispara un cont cu sold fara ca contabilul sa stie (aceeasi regula ca la N
        # in d394 - decizie Costin 04.08: exclus, dar vizibil). Verifica norma firmei / planul de conturi.
        lista = ", ".join(strain[:30]) + (" ... (+%d)" % (len(strain) - 30) if len(strain) > 30 else "")
        res.avertismente.insert(0, "ATENTIE: %d cont(uri) EXCLUS(e) din D406 - nu apartin normei contabile "
                                   "declarate (%s), ANAF le-ar respinge: %s. Verifică planul de conturi / baza "
                                   "contabila a firmei." % (len(strain), prof.get("baza_contabila") or "A", lista))
    if um_necunoscute:
        _detu = "; ".join("factura %s: UM %r" % (nrf, um) for nrf, um in um_necunoscute)
        res.avertismente.insert(0, "ATENTIE (D406): unitate(i) de masura necunoscută(e) înlocuită(e) "
                                   "cu H87 (bucata) - NU tacit: o unitate greșită e eronata/respinsă la "
                                   "ANAF. %s. Mapează unitatile în nomenclatorul UN/ECE Rec.20." % _detu)
    if cote_necunoscute:
        _detc = "; ".join("factura %s: cota %s%%" % (nrf, ct) for nrf, ct in cote_necunoscute)
        res.avertismente.insert(0, "ATENTIE (D406): cota(e) de TVA fără cod TaxCode de livrare în "
                                   "nomenclator, înlocuită(e) TACIT cu 310312 (taxare inversa) - date "
                                   "GRESITE la ANAF. %s. Verifică cota facturii / actualizeaza "
                                   "nomenclatorul de coduri de taxa." % _detc)
    # POARTA A DOUA CALE (gard de continut, 05.08.2026, pas 4/6): balanta de rulaje per cont
    # INDEPENDENTA din inregistrari_linii, legata de SAF-T emis + invariant Sdebit=Scredit.
    # Divergenta = HARD-BLOCK. Vezi core/d406_reconciliere.py.
    from core.d406_reconciliere import verifica_reconciliere
    verifica_reconciliere(conn, schema, an, luna, res)
    return build_xml(res), res
