---
title: "Ce date ale SRL-ului care vinde pe platforme online ajung la ANAF prin DAC7?"
description: "Pentru un SRL, platforma raportează denumirea, sediul social, CUI-ul, codul de TVA, numărul de la registrul comerțului, sediile permanente din UE, contul bancar și sumele pe trimestre."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# Ce date ale SRL-ului care vinde pe platforme online ajung la ANAF prin DAC7?

Pentru un SRL care vinde, închiriază sau prestează servicii printr-o platformă, operatorul colectează șase date de identificare: denumirea juridică, adresa sediului social, orice NIF cu statul emitent, numărul de TVA, numărul de înregistrare la registrul comerțului și existența sediilor permanente din UE prin care se desfășoară activitatea. Le raportează la ANAF împreună cu contul în care plătește banii, statele de rezidență și, pe fiecare trimestru, contraprestația, numărul de activități și comisioanele reținute.

Datele unei firme sunt oricum publice în mare parte. Interesul fiscal stă în altă parte: ANAF primește sumele trimestriale încasate prin platformă și le poate compara cu veniturile din contabilitate, cu decontul de TVA și cu SAF-T.

## Temeiul legal

::: ghid-temei
„2. Operatorul de platformă care are obligația de raportare colectează toate informațiile următoare pentru fiecare Vânzător care este o Entitate și care nu este Vânzător Exclus: a)denumirea juridică; b)Adresa Principală; c)orice NIF emis Vânzătorului respectiv, inclusiv fiecare stat membru emitent; d)numărul TVA al Vânzătorului respectiv, dacă există; e)numărul de înregistrare în Registrul Comerțului; f)existența oricărui sediu permanent prin care se realizează Activități Relevante în România sau în oricare alt stat membru, dacă informația este disponibilă, indicând fiecare stat membru în care este situat un astfel de sediu permanent."
— Codul de procedură fiscală (Legea 207/2015), Anexa nr. 5, secț. II lit. B pct. 2 (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„Pentru a determina dacă un Vânzător care este o Entitate se califică drept Vânzător Exclus în sensul descris la pct. 4 lit. a) și b) din subsecțiunea B din secțiunea I, un Operator de platformă care are obligația de raportare poate utiliza informațiile disponibile în mod public sau o confirmare din partea Vânzătorului care este o Entitate."
— Codul de procedură fiscală (Legea 207/2015), Anexa nr. 5, secț. II lit. A (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce înseamnă fiecare element pentru un SRL românesc:

- **Denumirea juridică** este denumirea din registrul comerțului, nu numele comercial al magazinului de pe platformă.
- **Adresa principală** a unei entități este adresa sediului social (Anexa nr. 5, secț. I lit. C pct. 5). Un punct de lucru nu ține loc de sediu.
- **NIF-ul** este codul unic de înregistrare, pe care Codul de procedură fiscală îl stabilește drept cod de identificare fiscală pentru entitățile înregistrate la registrul comerțului (art. 82 alin. (1) lit. b)). **Numărul de TVA** apare numai dacă firma e înregistrată în scopuri de TVA.
- **Numărul de la registrul comerțului** se colectează separat de CUI. Nu se colectează doar dacă statul de rezidență nu emite un asemenea număr (secț. II lit. B pct. 4).
- **Sediile permanente** din România sau din alte state membre prin care se desfășoară activitatea se declară dacă informația e disponibilă. Ele contează la stabilirea statelor de rezidență (secț. II lit. D pct. 3).
- **Datele financiare** sunt aceleași ca la persoanele fizice: contul financiar, titularul contului dacă e altul decât firma, statele de rezidență, contraprestația și numărul de activități pe trimestru, comisioanele pe trimestru (secț. III lit. B pct. 2).

Nu orice entitate e raportată. Sunt excluse entitățile guvernamentale, entitățile cotate pe o piață reglementată și cele afiliate lor (secț. I lit. B pct. 4 lit. a) și b)). Pentru aceste excluderi, platforma se poate baza pe informații publice sau pe confirmarea firmei. Un SRL obișnuit nu se încadrează aici, cu excepția filialelor unui grup cotat. Afilierea înseamnă control de peste 50% (secț. I lit. C pct. 1). Mai sunt excluse entitățile pentru care platforma a facilitat peste 2.000 de închirieri ale aceluiași bun imobil listat și orice vânzător cu sub 30 de vânzări de bunuri și cel mult echivalentul a 2.000 de euro în an (secț. I lit. B pct. 4 lit. c) și d)).

::: ghid-exemplu
SC Exemplu SRL, plătitoare de TVA, vinde accesorii auto pe un marketplace european. Pentru 2026, platforma raportează la ANAF:
- SC Exemplu SRL, sediul social din Brașov, CUI-ul, codul RO de TVA, numărul de la registrul comerțului, fără sedii permanente în alte state;
- IBAN-ul firmei;
- în trimestrul III: 310 vânzări, contraprestație de 41.800 lei, comisioane reținute de 6.200 lei.
Contabilul verifică dacă vânzările din trimestrul III din contabilitate acoperă cel puțin 41.800 + 6.200 = 48.000 lei și dacă încasările nete și comisioanele se regăsesc pe conturile corespunzătoare.
:::

## Ce se greșește în practică

- În contul de vânzător de pe platformă rămâne trecută adresa veche a sediului, după o mutare neactualizată.
- Încasările se fac într-un cont al administratorului sau al altei firme din grup. Raportarea arată atunci alt titular, iar veniturile nu se mai leagă de SRL.
- Se presupune că un SRL nu e raportat fiindcă „firmele mari nu sunt raportate”. Mărimea firmei nu contează: excluderile privesc entitățile guvernamentale, pe cele cotate și afiliatele lor, volumele foarte mari de închirieri pe același bun și vânzările mici de bunuri sub prag.
- Comisioanele reținute de platformă nu se înregistrează, deși apar distinct în raportare.

## Ce face iConta.eu

iConta.eu nu primește raportările DAC7. Pentru un SRL, aplicația importă extrasul bancar (XLS, CSV sau MT940), propune note contabile pe tipuri de operațiuni și potrivește încasările pe facturile deschise ale partenerului. Pentru un magazin propriu WooCommerce, comenzile devin facturi automat. Separarea comisionului platformei din suma încasată nu se face automat: contabilul îl înregistrează pe baza decontului sau facturii platformei.

[iConta.eu](/)
