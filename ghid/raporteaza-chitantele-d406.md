---
title: "Cum se raportează chitanțele în D406?"
description: "Chitanțele de casă nu au un element dedicat în SAF-T, ci se raportează ca plăți în numerar, în secțiunea Payments a Declarației informative D406."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se raportează chitanțele în D406?

Declarația informativă D406 (fișierul standard de control fiscal, SAF-T) nu are o secțiune separată numită „chitanțe". Chitanța de casă, ca document care atestă o încasare sau o plată în numerar, se regăsește în structura SAF-T ca înregistrare de plată (Payment), cu metoda de plată marcată drept numerar. Practic, la nivel tehnic, chitanța „dispare" ca document și devine o linie cu un cod de metodă de plată.

## Temeiul legal

::: ghid-temei
„SD.P.10 | PaymentMethod | Cheque, Bank, Giro, Cash etc | Cec, Bancă, Giro, Numerar etc. [...] Mandatory | Mandatory | Validation according to the codes defiend in the nomenclature Nom_Mecanisme_plati"
— OPANAF 1.783/2021 (modificat prin OPANAF 407/2025), Anexa privind structura fișierului standard de control fiscal, foaia „4. SourceDocuments", element SD.P.10 (sursă: anaf_surse/d406_schema_anaf.xlsx)
:::

::: ghid-temei
„Pentru completarea PaymentMethod se vor selecta codurile asociate de mai jos: [...] codul 01 - pentru Numerar [...] codul 03 - pentru Fără numerar [...] Pentru completarea câmpului PaymentMechanism se vor selecta, cu prioritate, coduri din cele de mai jos: [...] codul 10 - pentru plata în numerar, inclusiv pentru plățile efectuate la casieriile trezoreriei"
— Nomenclatorul „Mecanisme de plată/încasare" (Nom_Mecanisme_plati), parte integrantă a structurii SAF-T aprobate prin OPANAF 1.783/2021 (sursă: anaf_surse/d406_schema_anaf.xlsx)
:::

Din aceste elemente rezultă practic regula de raportare:

- Fiecare încasare sau plată în numerar consemnată printr-o chitanță intră în secțiunea `SourceDocuments > Payments` a fișierului SAF-T, ca element `Payment`.
- Câmpul `PaymentMethod` (SD.P.10) este obligatoriu și se completează cu codul **„01" — Numerar** pentru orice operațiune încasată/plătită prin chitanță de casă, spre deosebire de codul „03" folosit pentru plățile fără numerar (virament, card).
- Opțional, se poate completa și `PaymentMechanism` cu codul **„10"**, care descrie explicit plata în numerar.
- Cine trebuie să depună D406 este stabilit separat, pe categorii de contribuabili și date de referință (mari, mijlocii, mici, pe ani), conform Anexei nr. 5 la OPANAF 1.783/2021, modificată prin OPANAF 407/2025.

## Ce se greșește în practică

- Se caută în schema SAF-T un element numit literal „Receipt" sau „Chitanță" — nu există; informația se regăsește la nivelul metodei de plată din secțiunea `Payments`.
- Se lasă necompletat câmpul `PaymentMethod`, deși e obligatoriu conform structurii SAF-T, ceea ce duce la respingerea fișierului de către validatorul ANAF.
- Se confundă `PaymentMethod` (obligatoriu, cod pe două cifre din nomenclator) cu `PaymentMechanism` (opțional, mai detaliat) — folosirea unui cod din nomenclatorul greșit la câmpul greșit invalidează fișierul.
- Se raportează toate plățile ca „03 – fără numerar" din comoditate, chiar și cele efectuate efectiv prin casierie, ceea ce denaturează informația din SAF-T.

## Ce face iConta.eu

iConta.eu chiar tratează explicit acest caz în motorul de generare D406: la construirea secțiunii `Payments`, aplicația recunoaște metodele de plată introduse ca „numerar", „cash", „casa" sau chiar direct „chitanța" și le mapează automat la codul oficial ANAF **„01"**; orice altă metodă neconformă e adusă implicit la codul „03" (fără numerar), niciodată lăsată necompletată. Validarea codului de metodă de plată (că e unul din cele cinci coduri valide: 01/02/03/98/99) este acoperită de teste dedicate în motorul de generare a declarației. Deci, dacă o încasare sau o plată e înregistrată în casierie ca fiind în numerar, ea ajunge corect marcată în D406 fără intervenție manuală suplimentară.

[iConta.eu](/)
