---
title: "Cum se leagă e-Factura cu RO e-Transport"
description: "RO e-Factura și RO e-Transport sunt două sisteme naționale distincte, cu obligații separate; datele lor sunt corelate de ANAF prin decontul precompletat RO e-TVA."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se leagă e-Factura cu RO e-Transport

RO e-Factura și RO e-Transport nu sunt același sistem și nu se condiționează direct unul pe celălalt — sunt două obligații separate, reglementate prin acte normative diferite, care urmăresc lucruri diferite: facturarea electronică, respectiv monitorizarea transporturilor rutiere de bunuri cu risc fiscal ridicat. Legătura reală dintre ele apare mai târziu în lanț, la nivelul ANAF, care le corelează pentru a verifica dacă o marfă transportată corespunde unei facturi emise.

## Temeiul legal

::: ghid-temei
„(1) Ministerul Finanţelor, prin Centrul Naţional pentru Informaţii Financiare, creează, dezvoltă şi administrează sistemul naţional privind factura electronică RO e-Factura."
— OUG 120/2021, art. 3 alin. (1) (sursă: anaf_surse/oug_120_2021.txt)

„Sistemul RO e-Transport reprezintă ansamblul de principii, reguli şi aplicaţii informatice având drept scop monitorizarea transporturilor de bunuri cu risc fiscal ridicat pe teritoriul naţional, care permite autorităţilor competente determinarea potenţialelor puncte de deturnare din sau în lanţul de aprovizionare, pe baza codului UIT."
— OUG 41/2022, art. 3 (sursă: anaf_surse/oug_41_2022.txt)

„a) Sistemul național privind factura electronică RO e-Factura, prevăzut la art. 3 alin. (2) din Ordonanța de urgență a Guvernului nr. 120/2021 [...]; b) Sistemul național RO e-Transport, prevăzut la art. 3 din Ordonanța de urgență a Guvernului nr. 41/2022 [...]"
— OUG 70/2024, art. 2 alin. (1) lit. a) și b) (sursă: anaf_surse/oug_70_2024_ro_etva_decont_precompletat.txt)
:::

Ce arată concret cele trei texte, puse cap la cap:

- **RO e-Factura** e sistemul de transmitere a facturilor electronice (OUG 120/2021), obligatoriu în relația B2B pentru persoanele impozabile stabilite în România.
- **RO e-Transport** e sistemul de monitorizare a transporturilor de bunuri cu risc fiscal ridicat (OUG 41/2022), cu propriile obligații de generare a codului UIT înainte de deplasarea mărfii — o obligație distinctă, legată de transport, nu de facturare.
- Cele două sisteme **nu se validează reciproc automat** la nivelul firmei care le folosește — nu există o regulă legală care să blocheze emiterea unei facturi fără cod UIT sau invers. Corelarea lor se face la nivel central, de către ANAF, prin **decontul precompletat RO e-TVA** (OUG 70/2024, art. 2), care agregă date din ambele sisteme (plus RO e-Sigiliu, RO e-SAF-T, case de marcat) pentru a identifica neconcordanțe.

## Ce se greșește în practică

- Se presupune că, odată transmisă factura prin RO e-Factura, obligația de RO e-Transport pentru marfa aferentă dispare automat — sunt obligații paralele, cu praguri și condiții proprii de declanșare.
- Se așteaptă ca aplicațiile comerciale să "sincronizeze" automat cele două fluxuri fără intervenție — legal, fiecare sistem are propriul canal de transmitere către ANAF, iar corelarea reală se întâmplă abia în instrumentele de analiză ale ANAF.
- Se ignoră faptul că neconcordanțele dintre e-Factura și e-Transport, vizibile ANAF prin modulul de valorificare RO e-TVA, pot declanșa verificări, chiar dacă fiecare declarație individuală a fost depusă corect formal.

## Ce face iConta.eu

iConta.eu generează separat documentele pentru cele două sisteme: facturile electronice pentru RO e-Factura (transmise prin conectorul SPV/ANAF) și XML-ul de notificare pentru RO e-Transport (structura oficială `eTransport declaratie v2`). La data acestui ghid, încărcarea notificării RO e-Transport în SPV se face manual, iar aplicația nu leagă automat o factură emisă de o notificare de transport corespunzătoare — corelarea rămâne o verificare a contabilului, la fel ca la ANAF.

[iConta.eu](/)
