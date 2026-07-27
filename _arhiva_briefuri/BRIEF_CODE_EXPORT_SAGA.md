# BRIEF_CODE_EXPORT_SAGA — export facturi emise catre SAGA

## Autonomie
Costin a aprobat executie completa fara opriri pe intrebari de implementare.
NU te opri pentru detalii tehnice — decizi singur si mergi pana termini.
EXCEPTIE (poarta ramane): daca descoperi ca ai nevoie de SCHEMA NOUA sau ca
trebuie sa MODIFICI cod LIVE (emitere, facturi_api) — STOP si intreaba. Exportul
NU ar trebui sa ceara niciuna: e transformare de format (citesti factura existenta
-> scrii XML), ruta noua read-only, fara atingere pe date. Daca te trezesti ca ai
nevoie de altceva, e semn ca ai iesit din scop.

## Scop: SAGA-only intai
Doar formatul SAGA acum (acopera majoritatea pietei). WinMentor/Ciel = later,
nu le implementa. Structureaza codul ca sa poata primi alte formate ulterior
(un generator per format), dar livreaza doar SAGA.

## Formatul-tinta (VERIFICAT LA SURSA 18.07.2026)
Sursa: manual.sagasoft.ro/sagac/topic-76-import-date + forum oficial SAGA.
SAGA importa facturi din XML propriu, prin "Diverse -> Import date -> Import date
din fisiere generate". E acelasi XML pe care SAGA il genereaza la tiparirea unei
facturi ca PDF cu optiune "format XML" — deci structura de mai jos e modelul exact.

Structura XML (tag-uri exacte, NU inventa altele):

<Facturi>
  <Factura>
    <Antet>
      <FurnizorNume> <FurnizorCIF> <FurnizorNrRegCom> <FurnizorCapital>
      <FurnizorAdresa> <FurnizorBanca> <FurnizorIBAN> <FurnizorInformatiiSuplimentare>
      <ClientNume> <ClientInformatiiSuplimentare> <ClientCIF> <ClientNrRegCom>
      <ClientAdresa> <ClientBanca> <ClientIBAN>
      <FacturaNumar> <FacturaData> <FacturaScadenta>
      <FacturaTaxareInversa> (Da/Nu) <FacturaTVAIncasare> (Da/Nu)
      <FacturaInformatiiSuplimentare> <FacturaMoneda> <FacturaCotaTVA> <FacturaGreutate>
    </Antet>
    <Detalii><Continut>
      <Linie>
        <LinieNrCrt> <Descriere> <CodArticolFurnizor> <CodArticolClient>
        <CodBare> <InformatiiSuplimentare> <UM> <Cantitate> <Pret> <Valoare> <TVA>
      </Linie>
      ... (o <Linie> per linie de factura)
    </Continut></Detalii>
    <Sumar><TotalValoare> <TotalTVA> <Total></Sumar>
    <Observatii><txtObservatii> <SoldClient></Observatii>
  </Factura>
</Facturi>

## Trei reguli SAGA critice (din documentatie, nu le incalca)

1. DIRECTIA se decide prin CIF, nu prin tag. SAGA importa in "Iesiri" cand CIF-ul
   firmei se gaseste la <FurnizorCIF>. Deci pentru facturi EMISE de firma-client:
   pui CIF-ul firmei-client la <FurnizorCIF> si clientul ei la <ClientCIF>.
   SAGA o claseaza automat ca iesire. NU marca tu directia.

2. NUMELE FISIERULUI are format fix obligatoriu:
   F_<cod-fiscal>_<numar-factura>_<data-factura>.xml
   Altfel SAGA nu-l vede la import.

3. Data in format zz.ll.aaaa (ex. 01.11.2020) — vezi exemplul din forum. Moneda
   "RON". Cota TVA cu 2 zecimale (ex. 9.00, 21.00). Verifica formatul exact al
   fiecarui camp pe exemplul real din forum inainte de a scrie generatorul.

## De unde iei datele (verifica la sursa)
Factura emisa exista deja in baza (core/facturi.py + facturi_api.py, F046).
grep structura reala a facturii emise + liniile ei. Nu presupune numele coloanelor
— citeste-le. Furnizor = firma-client (din firma_profil, F048). Client = partenerul
(clienti_api, F018). Liniile cu descriere/UM/cantitate/pret/valoare/TVA exista deja.

Camp care poate lipsi: <CodArticolFurnizor>/<CodArticolClient>. Nomenclatoarele SAGA
se leaga prin cod intern; daca factura n-are cod de articol, lasa gol — SAGA pune
linia pe "Nedefinit" (acceptabil, documentat). NU inventa coduri.

## Unde traieste
Ecranul Facturi (firma + cont gratuit). Buton "Export SAGA" pe o factura sau pe
un interval (luna). Ruta noua read-only in main.py — citeste facturi, produce XML,
returneaza fisier(e) cu numele in formatul F_*.xml. Fara schema, fara UPDATE.
Pentru interval: un XML per factura (SAGA importa asa), livrate ca .zip.

## Reguli permanente (CLAUDE.md)
- Rotunjire fiscala: Decimal + ROUND_HALF_UP, nu round().
- Diacritice: cod/markeri FARA, dar continutul XML respecta ce cere SAGA.
- Design System: citeste regula relevanta inainte de UI (buton pe card Facturi).
- Verificare functionala reala, nu py_compile: genereaza un XML pe o factura reala
  din tenant_002, verifica structura cap-coada.
- FUNCTIONALITATI.csv: pozitie noua pentru export SAGA, stare LIVE la final, in
  ACELASI commit (regula registrului).
- DECIZII.md: exportul SAGA era gol strategic (18.07); la final, actualizeaza ca
  livrat + noteaza limita (SAGA-only, WinMentor/Ciel later).

## Test la final
- XML generat pe o factura reala tenant_002, structura completa.
- Nume fisier in formatul F_<cif>_<nr>_<data>.xml.
- verificator_conformitate.py TOTAL 0.
- Restart: sudo systemctl restart iconta-nou.

## Ce raportezi la final
Commit-ul, un exemplu de XML generat (ca sa-l pot verifica ochiul contra structurii
SAGA), si limita declarata. Daca pe parcurs gasesti ca un camp SAGA cere date pe
care iConta nu le are, noteaza-l — nu inventa, lasa gol sau raporteaza.
