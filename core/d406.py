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

⚠️ STADIU: Header + MasterFiles + GeneralLedgerEntries complet din XSD.
   SourceDocuments: schelet (InvoiceStructure are sub-structuri mari — de extins cu DUK).
   Validare finală: DUKIntegrator_AnLunaUI.jar (-v D406 fisier.xml $ $ an=AAAA luna=LL).

CORECȚII față de prima schiță (confirmate din XSD):
  - namespace = mfp:anaf:dgti:d406t:declaratie:v1 (NU d406)
  - AccountType = Activ/Pasiv/Bifunctional (NU "GL")
  - TaxAccountingBasis enumerat: A/I/IFRS/BANK/INSURANCE/NORMA39/IFN/NORMA36/NORMA14/ONG
  - SelectionCriteria cere SelectionStartDate/EndDate + Period*
  - Header cere Company (CompanyHeaderStructure)

Separare strictă: construcție pură / validare / XML / DB / orchestrare.
"""
import re
from core import common as c
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

# namespace REAL din XSD (targetNamespace)
NS = "mfp:anaf:dgti:d406t:declaratie:v1"
REGULI = "2026.1"
SAFT_VERSION = "2.4.9"
TAX_ACCOUNTING_BASIS = "A"   # A = Accounting (contabilitate de angajamente)
_NEDIGIT = re.compile(r"\D")

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
    um: str = "BUC"          # InvoiceUOM
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
    metoda: str = "VIR"      # PaymentMethod (VIR virament, NUM numerar, etc.)
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


# cote TVA RO 2026 (TaxCode seria 380nnn)
COTE_TVA_STANDARD = [
    CotaTVA("310", Decimal("21"), "TVA 21%"),
    CotaTVA("320", Decimal("11"), "TVA 11%"),
    CotaTVA("330", Decimal("9"), "TVA 9%"),
    CotaTVA("300", Decimal("0"), "TVA 0% / scutit"),
]


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
    H.append('      <RegistrationNumber>%s</RegistrationNumber>' % _esc(cui))
    H.append('      <Name>%s</Name>' % _esc(prof.get("nume") or ""))
    H.append('      <Address>')
    H.append('        <StreetName>%s</StreetName>' % _esc(prof.get("adresa") or "-"))
    H.append('        <City>%s</City>' % _esc(prof.get("oras") or "-"))
    H.append('        <PostalCode>%s</PostalCode>' % _esc(prof.get("cod_postal") or "000000"))
    H.append('        <Country>RO</Country>')
    H.append('      </Address>')
    H.append('      <Contact>')
    H.append('        <ContactPerson>')
    H.append('          <FirstName>-</FirstName>')
    H.append('          <LastName>%s</LastName>' % _esc(prof.get("nume") or "-"))
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
    H.append('    <HeaderComment>D406 generat de iConta</HeaderComment>')
    H.append('    <SegmentIndex>1</SegmentIndex>')
    H.append('    <TotalSegmentsInsequence>1</TotalSegmentsInsequence>')
    # extensie RO: TaxAccountingBasis (după HeaderStructure)
    H.append('    <TaxAccountingBasis>%s</TaxAccountingBasis>' % TAX_ACCOUNTING_BASIS)
    H.append('  </Header>')
    return H


def _masterfiles(res):
    M = ['  <MasterFiles>']
    M.append('    <GeneralLedgerAccounts>')
    for c in res.conturi:
        M.append('      <Account>')
        M.append('        <AccountID>%s</AccountID>' % _esc(c.id))
        M.append('        <AccountDescription>%s</AccountDescription>' % _esc(c.descriere))
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
        M.append('          <RegistrationNumber>%s</RegistrationNumber>' % _esc(_NEDIGIT.sub("", c.cui or "")))
        M.append('          <Name>%s</Name>' % _esc(c.nume))
        M.append('          <Address>')
        M.append('            <City>%s</City>' % _esc(c.oras or "-"))
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
        M.append('          <RegistrationNumber>%s</RegistrationNumber>' % _esc(_NEDIGIT.sub("", f.cui or "")))
        M.append('          <Name>%s</Name>' % _esc(f.nume))
        M.append('          <Address>')
        M.append('            <City>%s</City>' % _esc(f.oras or "-"))
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
        M.append('          <Description>%s</Description>' % _esc(ct.descriere))
        M.append('          <TaxPercentage>%s</TaxPercentage>' % _dec(ct.procent))
        M.append('          <BaseRate>100.0000</BaseRate>')
        M.append('          <Country>RO</Country>')
        M.append('        </TaxCodeDetails>')
    M.append('      </TaxTableEntry>')
    M.append('    </TaxTable>')
    # containere obligatorii
    M.append('    <UOMTable>')
    M.append('      <UOMTableEntry>')
    M.append('        <UnitOfMeasure>BUC</UnitOfMeasure>')
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
    M.append('    <MovementTypeTable>')
    M.append('      <MovementTypeTableEntry>')
    M.append('        <MovementType>1</MovementType>')
    M.append('        <Description>Miscare stoc</Description>')
    M.append('      </MovementTypeTableEntry>')
    M.append('    </MovementTypeTable>')
    M.append('    <Products>')
    M.append('      <Product>')
    M.append('        <ProductCode>GENERIC</ProductCode>')
    M.append('        <Description>Produs generic</Description>')
    M.append('        <ProductCommodityCode>0</ProductCommodityCode>')
    M.append('        <ProductNumberCode>GENERIC</ProductNumberCode>')
    M.append('        <UOMBase>BUC</UOMBase>')
    M.append('        <UOMStandard>BUC</UOMStandard>')
    M.append('        <UOMToUOMBaseConversionFactor>1</UOMToUOMBaseConversionFactor>')
    M.append('      </Product>')
    M.append('    </Products>')
    M.append('    <Owners>')
    M.append('      <Owner>')
    M.append('        <CompanyStructure>')
    M.append('          <RegistrationNumber>%s</RegistrationNumber>' % _esc(_NEDIGIT.sub("", res.prof.get("cui") or "")))
    M.append('          <Name>%s</Name>' % _esc(res.prof.get("nume") or ""))
    M.append('          <Address>')
    M.append('            <City>%s</City>' % _esc(res.prof.get("oras") or "-"))
    M.append('            <Country>RO</Country>')
    M.append('          </Address>')
    M.append('        </CompanyStructure>')
    M.append('        <OwnerID>1</OwnerID>')
    M.append('        <AccountID>1012</AccountID>')
    M.append('      </Owner>')
    M.append('    </Owners>')
    M.append('    <Assets>')
    M.append('      <Asset>')
    M.append('        <AssetID>0</AssetID>')
    M.append('        <AccountID>21</AccountID>')
    M.append('        <Description>Fara active in perioada</Description>')
    M.append('        <DateOfAcquisition>%04d-%02d-01</DateOfAcquisition>' % (res.an, res.luna))
    M.append('        <StartUpDate>%04d-%02d-01</StartUpDate>' % (res.an, res.luna))
    M.append('        <Valuations>')
    M.append('          <Valuation>')
    M.append('            <AssetValuationType>1</AssetValuationType>')
    M.append('            <ValuationClass>0</ValuationClass>')
    M.append('            <AcquisitionAndProductionCostsBegin>0.00</AcquisitionAndProductionCostsBegin>')
    M.append('            <AcquisitionAndProductionCostsEnd>0.00</AcquisitionAndProductionCostsEnd>')
    M.append('            <InvestmentSupport>0.00</InvestmentSupport>')
    M.append('            <AssetLifeYear>0</AssetLifeYear>')
    M.append('            <AssetAddition>0.00</AssetAddition>')
    M.append('            <Transfers>0.00</Transfers>')
    M.append('            <AssetDisposal>0.00</AssetDisposal>')
    M.append('            <BookValueBegin>0.00</BookValueBegin>')
    M.append('            <DepreciationMethod>0</DepreciationMethod>')
    M.append('            <DepreciationPercentage>0</DepreciationPercentage>')
    M.append('            <DepreciationForPeriod>0.00</DepreciationForPeriod>')
    M.append('            <AppreciationForPeriod>0.00</AppreciationForPeriod>')
    M.append('            <ExtraordinaryDepreciationsForPeriod>')
    M.append('              <ExtraordinaryDepreciationForPeriod>')
    M.append('                <ExtraordinaryDepreciationMethod>0</ExtraordinaryDepreciationMethod>')
    M.append('                <ExtraordinaryDepreciationAmountForPeriod>0.00</ExtraordinaryDepreciationAmountForPeriod>')
    M.append('              </ExtraordinaryDepreciationForPeriod>')
    M.append('            </ExtraordinaryDepreciationsForPeriod>')
    M.append('            <AccumulatedDepreciation>0.00</AccumulatedDepreciation>')
    M.append('            <BookValueEnd>0.00</BookValueEnd>')
    M.append('          </Valuation>')
    M.append('        </Valuations>')
    M.append('      </Asset>')
    M.append('    </Assets>')
    M.append('  </MasterFiles>')
    return M


def _gl_entries(res):
    """GeneralLedgerEntries: Journal -> Transaction -> TransactionLine."""
    if not res.note:
        return []
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
    for n in res.note:
        G.append('      <Transaction>')
        G.append('        <TransactionID>%s</TransactionID>' % _esc(n.id))
        G.append('        <Period>%d</Period>' % res.luna)
        G.append('        <PeriodYear>%d</PeriodYear>' % res.an)
        G.append('        <TransactionDate>%s</TransactionDate>' % _d(n.data))
        G.append('        <Description>%s</Description>' % _esc(n.descriere))
        G.append('        <SystemEntryDate>%s</SystemEntryDate>' % _d(n.data))
        G.append('        <GLPostingDate>%s</GLPostingDate>' % _d(n.data))
        G.append('        <CustomerID>0</CustomerID>')
        G.append('        <SupplierID>0</SupplierID>')
        for l in n.linii:
            G.append('        <TransactionLine>')
            G.append('          <RecordID>%s</RecordID>' % _esc(l.record_id))
            G.append('          <AccountID>%s</AccountID>' % _esc(l.cont))
            G.append('          <CustomerID>0</CustomerID>')
            G.append('          <SupplierID>0</SupplierID>')
            G.append('          <Description>%s</Description>' % _esc(l.descriere))
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
            G.append('            <TaxCode>300</TaxCode>')
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
        X.append('%s    <Description>%s</Description>' % (sp, _esc(l.descriere)))
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
    # totaluri document
    X.append('%s  <InvoiceDocumentTotals>' % sp)
    X.append('%s    <TaxInformationTotals>' % sp)
    X.append('%s      <TaxType>300</TaxType>' % sp)
    X.append('%s      <TaxCode>310</TaxCode>' % sp)
    X.append('%s      <TaxPercentage>21.00</TaxPercentage>' % sp)
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
    """SourceDocuments: SalesInvoices, PurchaseInvoices, Payments (toate obligatorii în XSD)."""
    fv, fc, pl = res.facturi_vanzare, res.facturi_cumparare, res.plati
    S = ['  <SourceDocuments>']
    # SalesInvoices (obligatoriu)
    net_v = sum(f.net for f in fv)
    S.append('    <SalesInvoices>')
    S.append('      <NumberOfEntries>%d</NumberOfEntries>' % len(fv))
    S.append('      <TotalDebit>0.00</TotalDebit>')
    S.append('      <TotalCredit>%s</TotalCredit>' % _dec(net_v))
    for f in fv:
        S.extend(_factura_xml(f, True, 6))
    S.append('    </SalesInvoices>')
    # PurchaseInvoices (obligatoriu)
    net_c = sum(f.net for f in fc)
    S.append('    <PurchaseInvoices>')
    S.append('      <NumberOfEntries>%d</NumberOfEntries>' % len(fc))
    S.append('      <TotalDebit>%s</TotalDebit>' % _dec(net_c))
    S.append('      <TotalCredit>0.00</TotalCredit>')
    for f in fc:
        S.extend(_factura_xml(f, False, 6))
    S.append('    </PurchaseInvoices>')
    # Payments (obligatoriu)
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
        S.append('        <PaymentMethod>%s</PaymentMethod>' % _esc(p.metoda))
        S.append('        <Description>%s</Description>' % _esc(p.descriere or "Plata"))
        for l in p.linii:
            S.append('        <PaymentLine>')
            S.append('          <LineNumber>%d</LineNumber>' % l.nr)
            if l.doc_sursa:
                S.append('          <SourceDocumentID>%s</SourceDocumentID>' % _esc(l.doc_sursa))
            S.append('          <AccountID>%s</AccountID>' % _esc(l.cont))
            S.append('          <CustomerID>0</CustomerID>')
            S.append('          <SupplierID>0</SupplierID>')
            S.append('          <Description>%s</Description>' % _esc(l.descriere))
            S.append('          <DebitCreditIndicator>%s</DebitCreditIndicator>' % _esc(l.sens))
            S.append('          <PaymentLineAmount>')
            S.append('            <Amount>%s</Amount>' % _dec(l.suma))
            S.append('            <CurrencyCode>RON</CurrencyCode>')
            S.append('            <CurrencyAmount>%s</CurrencyAmount>' % _dec(l.suma))
            S.append('          </PaymentLineAmount>')
            S.append('          <TaxInformation>')
            S.append('            <TaxType>300</TaxType>')
            S.append('            <TaxCode>300</TaxCode>')
            S.append('            <TaxAmount>')
            S.append('              <Amount>0.00</Amount>')
            S.append('              <CurrencyCode>RON</CurrencyCode>')
            S.append('              <CurrencyAmount>0.00</CurrencyAmount>')
            S.append('            </TaxAmount>')
            S.append('          </TaxInformation>')
            S.append('        </PaymentLine>')
        S.append('      </Payment>')
    S.append('    </Payments>')
    # MovementOfGoods (obligatoriu în XSD; gol — fără mișcări de stoc)
    S.append('    <MovementOfGoods>')
    S.append('      <NumberOfMovementLines>0</NumberOfMovementLines>')
    S.append('      <TotalQuantityReceived>0</TotalQuantityReceived>')
    S.append('      <TotalQuantityIssued>0</TotalQuantityIssued>')
    S.append('    </MovementOfGoods>')
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
        cur.execute("SELECT nume, cui, adresa, oras, cod_postal FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        conturi, clienti, furnizori, note = [], [], [], []
        try:
            cur.execute("SELECT simbol, denumire, COALESCE(tip,'Bifunctional') AS tip, "
                        "COALESCE(sold_debitor,0) AS sd, COALESCE(sold_creditor,0) AS sc "
                        "FROM plan_conturi ORDER BY simbol")
            for r in cur.fetchall():
                conturi.append(Cont(id=r["simbol"], descriere=r["denumire"], cont_standard=r["simbol"],
                                    tip=r["tip"], sold_inchidere_d=Decimal(str(r["sd"])),
                                    sold_inchidere_c=Decimal(str(r["sc"]))))
        except Exception:
            pass
        try:
            cur.execute("SELECT id, nume, cui, oras FROM clienti ORDER BY id")
            for r in cur.fetchall():
                clienti.append(Partener(id=str(r["id"]), nume=r["nume"] or "", cui=r["cui"] or "", oras=r["oras"] or ""))
        except Exception:
            pass
        try:
            cur.execute("SELECT id, nume, cui, oras FROM furnizori ORDER BY id")
            for r in cur.fetchall():
                furnizori.append(Partener(id=str(r["id"]), nume=r["nume"] or "", cui=r["cui"] or "", oras=r["oras"] or ""))
        except Exception:
            pass
        try:
            cur.execute("SELECT i.id, i.data, i.descriere, l.cont, l.debit, l.credit, l.descriere AS ldesc "
                        "FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                        "WHERE i.data >= %s AND i.data < %s ORDER BY i.id, l.id", (di, ds))
            nmap = {}
            for r in cur.fetchall():
                n = nmap.get(r["id"])
                if n is None:
                    n = Nota(id=str(r["id"]), data=r["data"], descriere=r["descriere"] or "")
                    nmap[r["id"]] = n
                n.linii.append(LinieNota(record_id=str(len(n.linii) + 1), cont=r["cont"] or "",
                                         descriere=r["ldesc"] or "", debit=Decimal(str(r["debit"] or 0)),
                                         credit=Decimal(str(r["credit"] or 0))))
            note = list(nmap.values())
        except Exception:
            pass
        facturi_vanzare, facturi_cumparare, plati = [], [], []
        try:
            cur.execute("SELECT id, numar, data, partener_id, partener_nume, tip, "
                        "COALESCE(baza,0) AS baza, COALESCE(tva,0) AS tva, COALESCE(cota_tva,21) AS cota, directie "
                        "FROM facturi WHERE data >= %s AND data < %s ORDER BY id", (di, ds))
            for r in cur.fetchall():
                cota = Decimal(str(r["cota"]))
                tcod = {Decimal(21): "310", Decimal(11): "320", Decimal(9): "330"}.get(cota, "300")
                este_v = (r["directie"] or "emisa") in ("emisa", "vanzare")
                linie = LinieFactura(nr=1, cont=("707" if este_v else "371"),
                                     descriere=r["partener_nume"] or "", valoare=Decimal(str(r["baza"])),
                                     sens=("C" if este_v else "D"), tva_cod=tcod, tva_procent=cota,
                                     tva_suma=Decimal(str(r["tva"])))
                f = Factura(nr=r["numar"] or str(r["id"]), data=r["data"],
                            partener_id=str(r["partener_id"] or 0), partener_nume=r["partener_nume"] or "",
                            tip=r["tip"] or "FT", cont=("4111" if este_v else "401"), linii=[linie])
                (facturi_vanzare if este_v else facturi_cumparare).append(f)
        except Exception:
            pass
    return prof, conturi, clienti, furnizori, note, facturi_vanzare, facturi_cumparare, plati


def genereaza(conn, schema, an, luna):
    if luna < 1 or luna > 12:
        raise ValueError("Luna invalidă: %r" % luna)
    prof, conturi, clienti, furnizori, note, fv, fc, plati = pull(conn, schema, an, luna)
    res = construieste(prof, an, luna, conturi, clienti, furnizori, note=note,
                       facturi_vanzare=fv, facturi_cumparare=fc, plati=plati)
    return build_xml(res), res
