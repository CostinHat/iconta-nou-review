---
title: Cum retransmiți o factură respinsă de ANAF în RO e-Factura
description: O factură respinsă de sistemul RO e-Factura (structură invalidă) nu se poate corecta „pe loc" — se corectează eroarea și se retransmite ca document nou în același sistem, sau se emite o factură de corecție dacă a fost deja comunicată destinatarului.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum retransmiți o factură respinsă de ANAF în RO e-Factura

Există două situații complet diferite, pe care mulți contabili le confundă: factura respinsă de sistem pentru erori de structură și factura acceptată de sistem, dar contestată de destinatar. Se rezolvă diferit.

### Cazul 1: factura e respinsă de sistemul RO e-Factura (erori de structură)

Art. 4 din OUG 120/2021 descrie exact mecanismul:

> alin. (4): „În situația în care factura electronică transmisă respectă structura prevăzută la alin. (1), se aplică semnătura electronică a Ministerului Finanțelor și se comunică de îndată destinatarului."
>
> alin. (5): „În situația în care factura electronică transmisă **nu respectă structura** prevăzută la alin. (1), emitentul primește mesaj cu erorile identificate. **După corectarea erorilor identificate, factura electronică se transmite în cadrul aceluiași sistem național** privind factura electronică RO e-Factura."

Deci: dacă factura a fost respinsă (nu a primit semnătura electronică a Ministerului Finanțelor, nu a fost comunicată destinatarului), ea **nu există** ca document oficial în sistem. Procedura corectă:

1. Citește mesajul de eroare primit de la RO e-Factura (de regulă erori de validare CIUS-RO — cod de client greșit, cotă TVA inconsistentă, câmp obligatoriu lipsă etc.).
2. Corectează factura sursă (în softul de facturare, nu manual pe XML).
3. Retransmite documentul corectat **în același sistem** RO e-Factura — nu ca „factură de corecție", ci pur și simplu ca factură retransmisă, pentru că prima variantă nu a fost niciodată validată.

Nu se emite o factură de stornare pentru o factură respinsă — stornarea are sens doar pentru facturi care au fost efectiv comunicate.

### Cazul 2: factura a fost acceptată de sistem, dar destinatarul are obiecții

Aici regimul e diferit, pentru că factura există deja ca document oficial. Art. 4 din OUG 120/2021:

> alin. (8): „Factura electronică comunicată destinatarului **nu se poate returna** în sistemul național privind factura electronică RO e-Factura."
>
> alin. (9): „În situația unei facturi electronice asupra căreia destinatarul are obiecții, acesta înștiințează emitentul facturii electronice, inclusiv în sistemul național privind factura electronică RO e-Factura, prin înscrierea unui mesaj în acest sens."
>
> alin. (10): „**Corecția facturii electronice comunicată destinatarului** în sistemul RO e-Factura se efectuează conform **art. 330 din Legea nr. 227/2015** privind Codul fiscal... Factura electronică corectată se transmite în cadrul aceluiași sistem național privind factura electronică RO e-Factura."

Aici procedura e: emiți o **factură de corecție** (stornare parțială/totală + factură nouă, sau notă de corecție, după caz — conform art. 330 Cod fiscal), și o transmiți tot prin RO e-Factura, ca document distinct legat de factura inițială.

### Termenul de transmitere pentru orice retransmitere

Indiferent de motiv, termenul-limită pentru transmiterea facturilor B2B în RO e-Factura rămâne 5 zile lucrătoare de la data emiterii, dar nu mai târziu de 5 zile lucrătoare de la termenul-limită legal de emitere a facturii (art. 319 alin. 16 Cod fiscal) — regulă aflată la art. 10 alin. (7) din OUG 120/2021, așa cum a fost completat. O retransmitere după corectare nu prelungește acest termen — de aceea corectarea rapidă a erorilor de structură contează operațional, nu doar formal.

### În practică

- Verifică mesajul de eroare complet, nu doar primul rând — RO e-Factura poate semnala mai multe erori simultan.
- Nu redenumi/reemite manual un XML corectat fără să treacă din nou prin motorul de generare — riști să repeți aceeași eroare de structură.
- Pentru facturile deja acceptate și contestate de client, discută întâi cu destinatarul (mesaj în sistem, conform art. 4 alin. 9), apoi emite corecția conform art. 330 Cod fiscal.
