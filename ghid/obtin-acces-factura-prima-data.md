---
title: Cum obțin acces la e-Factura pentru prima dată?
description: Accesul la e-Factura are două straturi distincte — înregistrarea în Registrul RO e-Factura (pas legal, la ANAF) și conectarea tehnică a cabinetului cu certificatul calificat, prin OAuth, din iConta. Cele două nu se confundă.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum obțin acces la e-Factura pentru prima dată?

„Accesul la e-Factura" înseamnă, de fapt, doi pași diferiți, care nu se fac în același loc: unul e o formalitate legală la ANAF (înregistrarea în Registrul RO e-Factura), celălalt e o conectare tehnică, din iConta, cu certificatul digital calificat al cabinetului. Confundarea celor două duce la blocaje reale la prima utilizare.

## Temeiul legal

::: ghid-temei
"Emitentul... este obligat să fie înregistrat în Registrul operatorilor care au optat pentru utilizarea sistemului național... denumit în continuare Registrul RO e-Factura." — OUG 120/2021, art. 10 alin. (2)

"Registrul RO e-Factura este public și se afișează pe site-ul Agenției Naționale de Administrare Fiscală." — OUG 120/2021, art. 10 alin. (5)
:::

Registrul RO e-Factura este ținut și publicat de ANAF — înscrierea (sau, pentru relația B2B, aplicarea automată a obligativității, introdusă ulterior prin modificările legislative din 2024) se face la nivel de operator economic, prin declarație/opțiune la ANAF, nu prin nicio acțiune din aplicația de contabilitate. Acesta e primul strat, exterior aplicației.

Al doilea strat, tehnic, ține de accesul propriu-zis la Spațiul Privat Virtual (SPV), peste care rulează e-Factura: identificarea electronică se face cu certificat digital calificat, iar accesul (pentru firme) e permis reprezentantului legal, unui reprezentant desemnat sau unui împuternicit, conform procedurii SPV reglementate de ANAF. Fără acest certificat conectat, nicio aplicație terță (inclusiv iConta) nu poate trimite sau primi facturi în numele firmei.

## Ce se greșește în practică

Cea mai frecventă greșeală: încercarea de a „activa e-Factura" direct din iConta, fără ca certificatul calificat al cabinetului să fie deja recunoscut de ANAF cu drept SPV pe CIF-ul firmei respective — pasul administrativ la ANAF trebuie parcurs înainte, nu se poate sări. A doua greșeală: presupunerea că, odată conectat certificatul, accesul funcționează instantaneu — de regulă durează un interval de timp (de ordinul orelor) până când conexiunea devine efectiv funcțională la nivelul serviciilor ANAF.

## Ce face iConta.eu

Stratul tehnic e acoperit din secțiunea Setări → Conectare SPV: cabinetul autorizează o singură dată conexiunea OAuth cu ANAF, folosind certificatul digital calificat, printr-un flux standard de autorizare (redirecționare la ANAF, alegerea certificatului, revenire în aplicație cu token-ul criptat și stocat). Peste această conexiune rulează trimiterea și primirea facturilor prin e-Factura, pentru toate firmele (CIF-urile) pe care certificatul respectiv are deja drept SPV.

De reținut onest: iConta nu execută pasul legal de înregistrare în Registrul RO e-Factura și nu automatizează obținerea dreptului SPV pe un CIF nou — acelea rămân pași la ANAF, în afara aplicației. Conectarea din iConta presupune că certificatul cabinetului are deja acest drept recunoscut de ANAF; dacă nu îl are, obținerea lui e o procedură administrativă separată, la ANAF, nu ceva ce se rezolvă din ecranul de Setări.

[iConta.eu](/)
