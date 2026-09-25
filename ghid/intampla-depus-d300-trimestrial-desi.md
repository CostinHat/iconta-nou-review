---
title: "Ce se întâmplă dacă am depus D300 trimestrial deși trebuia lunar?"
description: "Consecințele aplicării greșite a periodicității TVA — cine stabilește dacă decontul e lunar sau trimestrial și cum se corectează o depunere pe fereastra greșită."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce se întâmplă dacă am depus D300 trimestrial deși trebuia lunar?

Periodicitatea decontului de TVA (D300) nu e o alegere a contribuabilului — e stabilită de lege, în funcție de cifra de afaceri și de operațiunile intracomunitare din anul precedent. Dacă firma a depus trimestrial într-un an în care legea cerea perioadă lunară, decontul e depus cu întârziere pentru două din cele trei luni ale trimestrului, iar corectarea nu se face printr-o simplă „bifă", ci prin declarații separate pentru fiecare lună.

## Temeiul legal

::: ghid-temei
„Articolul 322 Perioada fiscală
(1) Perioada fiscală este luna calendaristică.
(2) Prin excepție de la prevederile alin. (1), perioada fiscală este trimestrul calendaristic pentru persoana impozabilă care în cursul anului calendaristic precedent a realizat o cifră de afaceri din operațiuni taxabile și/sau scutite cu drept de deducere și/sau neimpozabile în România [...] care nu a depășit plafonul de 100.000 euro [...], cu excepția situației în care persoana impozabilă a efectuat în cursul anului calendaristic precedent una sau mai multe achiziții intracomunitare de bunuri."
— Codul fiscal (Legea 227/2015), art. 322 alin. (1)-(2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„(1) Constituie contravenții următoarele fapte [...]: b) neîndeplinirea de către contribuabil/plătitor la termen a obligațiilor de declarare prevăzute de lege, a bunurilor și veniturilor impozabile sau, după caz, a impozitelor, taxelor, contribuțiilor și a altor sume [...]
(2) Contravențiile [...] se sancționează astfel: [...] d) cu amendă de la 1.000 lei la 5.000 lei pentru persoanele juridice încadrate în categoria contribuabililor mijlocii și mari și cu amendă de la 500 lei la 1.000 lei, pentru celelalte persoane juridice, precum și pentru persoanele fizice, în cazul săvârșirii faptei prevăzute la alin. (1) lit. a), b) și i)-m)."
— Legea 207/2015 privind Codul de procedură fiscală, art. 336 alin. (1) lit. b) și alin. (2) lit. d) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„Datele înscrise incorect într-un decont de taxă se pot corecta prin decontul unei perioade fiscale ulterioare și se vor înscrie la rândurile de regularizări."
— Codul fiscal, art. 323 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din textul de mai sus rezultă mecanismul complet:

- **Perioada fiscală implicită e luna** (art. 322 alin. 1); trimestrul e excepția, condiționată de plafonul de 100.000 euro cifră de afaceri anul precedent **și** de absența oricărei achiziții intracomunitare de bunuri în acel an. O singură achiziție IC în anul precedent scoate firma din trimestrial, indiferent de cifra de afaceri.
- Dacă firma a depus trimestrial deși pragurile de mai sus impuneau lunar, cele două luni „lipsă" din trimestru nu au fost, de fapt, declarate deloc la termenul lor legal (25 a lunii următoare fiecărei luni, nu 25 a lunii următoare trimestrului) — asta e fapta sancționată la art. 336 alin. (1) lit. b) CPF.
- **Amenda** pentru nedepunerea la termen: 1.000-5.000 lei pentru contribuabilii mijlocii/mari, 500-1.000 lei pentru ceilalți (art. 336 alin. 2 lit. d) CPF).
- **Corectarea** nu înseamnă „anularea" decontului trimestrial greșit, ci depunerea declarațiilor lunare care ar fi trebuit depuse, cu regularizarea sumelor deja raportate trimestrial prin rândurile de regularizări ale unui decont ulterior (art. 323 alin. 3 CF).

## Ce se greșește în practică

- Se verifică doar cifra de afaceri din anul precedent și se ignoră achizițiile intracomunitare — o singură achiziție IC anulează dreptul la trimestrial, chiar dacă cifra de afaceri e mult sub 100.000 euro.
- Se presupune că trecerea de la trimestrial la lunar se face „automat" de la data constatării erorii, când de fapt obligația legală exista retroactiv, de la începutul anului în care condițiile nu mai erau îndeplinite.
- Se încearcă „ștergerea" decontului trimestrial deja depus, în loc de a depune lunar declarațiile lipsă și de a regulariza prin rândurile dedicate ale unui decont ulterior.

## Ce face iConta.eu

Fereastra de TVA (lunar sau trimestrial) folosită la generarea D300 vine din profilul firmei (`tip_decont`), citit de modulul de dispecerizare a declarațiilor (`core/declaratii_api.py`, funcția `periodicitate_firma`) — deci, dacă profilul e setat corect, aplicația construiește deja decontul pe fereastra potrivită, lună de lună sau trimestru de trimestru. Aplicația **nu verifică retroactiv** dacă periodicitatea aplicată în trecut a fost cea corectă și **nu generează automat** declarațiile lunare lipsă atunci când se descoperă că firma ar fi trebuit să treacă la lunar mai devreme — depistarea situației și depunerea declarațiilor de regularizare rămân în sarcina contabilului.

[iConta.eu](/)
