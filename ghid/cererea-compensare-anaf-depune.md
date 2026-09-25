---
title: "Cererea de compensare la ANAF: cum se depune"
description: "Ce înseamnă legal compensarea creanțelor fiscale, cine o poate cere, când operează de drept și cât timp are ANAF să comunice decizia."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cererea de compensare la ANAF: cum se depune

O firmă care are, simultan, o sumă de restituit de la buget (TVA de rambursat, de exemplu) și o obligație fiscală neplătită la alt tip de impozit poate cere ca cele două sume să se stingă reciproc, în loc să plătească separat una și să aștepte separat cealaltă. Acesta e mecanismul compensării, reglementat expres de Codul de procedură fiscală.

## Temeiul legal

::: ghid-temei
„(1) Prin compensare se sting creanțele statului sau unităților administrativ-teritoriale ori subdiviziunilor acestora reprezentând impozite, taxe, contribuții și alte sume datorate bugetului general consolidat cu creanțele debitorului reprezentând sume de rambursat, de restituit sau de plată de la buget, până la concurența celei mai mici sume, când ambele părți dobândesc reciproc atât calitatea de creditor, cât și pe cea de debitor, cu condiția ca respectivele creanțe să fie administrate de aceeași autoritate publică, inclusiv unitățile subordonate acesteia. [...]
(4) Dacă legea nu prevede altfel, compensarea operează de drept la data la care creanțele există deodată, fiind deopotrivă certe, lichide și exigibile. [...]
(7) Compensarea se constată de către organul fiscal competent, la cererea debitorului sau din oficiu. Dispozițiile art. 165 privind ordinea stingerii datoriilor sunt aplicabile în mod corespunzător.
(8) Organul fiscal competent comunică debitorului decizia cu privire la efectuarea compensării, în termen de 7 zile de la data efectuării operațiunii."
— Legea 207/2015 (Codul de procedură fiscală), art. 167 alin. (1), (4), (7) și (8) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă concret din text:

- **Condiția de bază**: cele două creanțe (a firmei față de buget, și a bugetului față de firmă) trebuie administrate de aceeași autoritate publică — nu se compensează, de exemplu, o creanță administrată de ANAF cu o datorie către o unitate administrativ-teritorială, decât în condițiile speciale ale alin. (2)-(3).
- **Compensarea operează, în principiu, de drept** — la data la care ambele creanțe devin deodată certe, lichide și exigibile, nu abia la momentul cererii. Cererea depusă de contribuabil are rolul de a determina organul fiscal să **constate** compensarea deja operată de drept, sau, dacă e cazul, să o realizeze; compensarea se poate produce și **din oficiu**, fără cerere.
- **Momentul exigibilității diferă în funcție de tipul creanței de restituit** — legea (alin. (5)) leagă exigibilitatea de: scadența obligației, termenul de depunere a decontului de TVA cu opțiune de rambursare, data cererii de restituire pentru accize/TVA, data comunicării deciziei de impunere, sau data plății sumei achitate în plus, după caz.
- **Termenul de comunicare a deciziei**: odată constatată compensarea, ANAF are 7 zile de la efectuarea operațiunii să comunice contribuabilului decizia — un termen explicit, verificabil.

## Ce se greșește în practică

- Se presupune că fără o cerere depusă, compensarea nu se produce — legea prevede expres că poate opera de drept sau din oficiu, la data la care ambele creanțe devin certe, lichide și exigibile, indiferent de existența unei cereri.
- Se cere compensarea unor creanțe administrate de autorități diferite (ex. o datorie locală cu o restituire de TVA administrată de ANAF), ignorând condiția explicită din alin. (1) privind aceeași autoritate publică.
- Se ignoră momentul exigibilității specific fiecărui tip de sumă de restituit (alin. (5)) — o firmă poate crede că suma de rambursat e „disponibilă" pentru compensare imediat, deși legea leagă exigibilitatea de un moment precis (data cererii de restituire, data deciziei etc.), diferit de la caz la caz.
- Se pierde din vedere termenul de 7 zile în care ANAF trebuie să comunice decizia — util pentru a ști când să solicite lămuriri dacă decizia întârzie.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are o funcționalitate dedicată depunerii sau urmăririi cererii de compensare** conform art. 167. Aplicația calculează și urmărește obligațiile declarate (prin `core/control_fiscal_api.py`) și poate semnala sume de recuperat (ex. TVA de rambursat), dar nu generează cererea de compensare, nu verifică dacă cele două creanțe sunt administrate de aceeași autoritate și nu urmărește termenul de 7 zile pentru comunicarea deciziei ANAF. Depunerea cererii, prin mijloacele puse la dispoziție de ANAF (ex. Spațiul Privat Virtual), rămâne un demers separat al contribuabilului.

[iConta.eu](/)
