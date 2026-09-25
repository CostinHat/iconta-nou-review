---
title: "Cum înrolez un SRL în SPV pentru e-Factura?"
description: "Obligația legală de înrolare în SPV pentru societățile cu răspundere limitată și condiția certificatului calificat, necesare pentru a folosi RO e-Factura."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum înrolez un SRL în SPV pentru e-Factura?

Pentru un SRL, înrolarea în Spațiul Privat Virtual nu este un pas facultativ făcut „ca să fie" — este o obligație de comunicare electronică impusă de Codul de procedură fiscală, iar fără ea societatea nu poate folosi RO e-Factura, indiferent dacă relația e B2B sau B2C.

## Temeiul legal

::: ghid-temei
„Prin excepţie de la alin. (1), contribuabilii/plătitorii persoane juridice, asocieri şi alte entităţi fără personalitate juridică [...] sunt obligaţi să transmită organului fiscal central documente de natura celor prevăzute la alin. (1) prin mijloace electronice de transmitere la distanţă în condiţiile prezentului articol, respectiv prin înrolarea în sistemul de comunicare electronică dezvoltat de Ministerul Finanţelor/A.N.A.F.
[art. 80 alin. (1) lit. a)] persoanele juridice, asocierile şi alte entităţi fără personalitate juridică, precum şi persoanele fizice care desfăşoară activităţi economice în mod independent ori exercită profesii libere se identifică numai cu certificate calificate."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 79 alin. (1^1) și art. 80 alin. (1) lit. a) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Pentru un SRL, aceste două articole stabilesc împreună cadrul obligatoriu:

- Societatea are **obligația**, nu opțiunea, de a comunica electronic cu ANAF prin înrolare în sistemul dezvoltat de Ministerul Finanțelor — asta include SPV.
- Identificarea se face **exclusiv cu certificat digital calificat** — un utilizator/parolă simplu nu este suficient pentru o persoană juridică, spre deosebire de unele categorii de persoane fizice fără activitate economică.
- Odată contul activ, SRL-ul trebuie separat să se înscrie și în Registrul RO e-Factura obligatoriu, atunci când intră sub incidența obligației de transmitere (B2B, B2C sau B2G, după caz) — un pas administrativ distinct, cu procedură proprie stabilită prin ordin al președintelui ANAF.

## Ce se greșește în practică

- Se cumpără certificatul digital pe numele administratorului, fără să se verifice că acesta este calificat pentru identificare la ANAF (nu orice semnătură electronică simplă îndeplinește condiția art. 80).
- Se presupune că un SRL nou înființat are un termen de grație nelimitat pentru înrolare — obligația de comunicare electronică se aplică din momentul în care societatea intră sub incidența legii, nu doar de la prima factură emisă.
- Se confundă înrolarea în SPV (obligație generală de comunicare cu ANAF) cu înscrierea în Registrul RO e-Factura (pas separat, specific facturării electronice).

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu creează contul SPV al societății** — înrolarea propriu-zisă se face de administrator sau împuternicit, direct pe portalul ANAF, cu certificatul calificat al firmei. După ce acest cont există, iConta.eu oferă conectorul OAuth2 (`core/spv_conector.py`) care leagă aplicația de contul SPV al SRL-ului, pentru trimiterea și primirea facturilor prin RO e-Factura din interfața de facturare. Pașii premergători — obținerea certificatului și înscrierea în SPV — rămân în afara aplicației.

[iConta.eu](/)
