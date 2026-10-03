---
title: "Cum ceri ANAF raportul cu datele din sursele folosite la precompletarea e-TVA?"
description: "Cererea se face electronic: firma are dreptul să ceară rapoarte cu datele din sursele folosite la precompletarea decontului RO e-TVA. Actele nu descriu pas cu pas procedura sau formatul."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# Cum ceri ANAF raportul cu datele din sursele folosite la precompletarea e-TVA?

Electronic. Atât OUG 70/2024, cât și OPANAF 3775/2024, care aprobă formularul decontului precompletat, prevăd două lucruri. Decontul precompletat RO e-TVA conține informații privind sursele de date folosite. Persoanele impozabile pot solicita electronic rapoarte cu datele și informațiile din aceste surse. Mai mult decât atât, textele nu spun: nu descriu un formular de cerere, un termen de răspuns sau structura raportului. Detaliile practice trebuie urmărite în canalele electronice ale ANAF.

Raportul este instrumentul care face decontul precompletat verificabil. O cifră agregată de TVA colectată sau deductibilă spune puțin. Raportul pe surse arată din ce facturi e-Factura, din ce înregistrări de case de marcat sau din ce alte sisteme provine cifra. Doar așa poate fi comparată, rând cu rând, cu evidența firmei.

## Temeiul legal

::: ghid-temei
„Decontul precompletat RO e-TVA conține informații privind sursele de date utilizate pentru precompletare. Persoanele impozabile pot solicita electronic rapoarte privind datele și informațiile din sursele de date utilizate."
— OPANAF 3775/2024, art. 4 (sursă: anaf_surse/ordin_3775_2024.html)

„(4) În situația în care nu sunt identificate date și informații pentru precompletarea tuturor rubricilor din decontul precompletat RO e-TVA sau acestea rezultă din operațiuni pentru care nu există obligativitatea transmiterii de informații către Agenția Națională de Administrare Fiscală, aceste rubrici rămân necompletate. (5) Decontul precompletat RO e-TVA conține informații privind sursele de date utilizate pentru precompletare. Persoanele impozabile pot solicita electronic rapoarte privind datele și informațiile din sursele de date utilizate."
— OUG 70/2024, art. 2 alin. (4) și (5) (sursă: anaf_surse/oug_70_2024_ro_etva_decont_precompletat.txt)
:::

Ce rezultă practic:

- **Dreptul aparține persoanei impozabile.** Firma, sau contabilul împuternicit să lucreze pentru ea, poate cere raportul. Textul spune „pot solicita", deci este un drept, nu o obligație.
- **Calea este electronică.** Actele nu prevăd o cerere pe hârtie. Ruta concretă din serviciile electronice ale ANAF nu este descrisă în ordin și se verifică în materialele informative pe care ANAF are obligația să le publice (OUG 70/2024 art. 10 lit. g)).
- **Când are sens cererea.** Decontul precompletat se transmite până la data de 5 inclusiv a lunii următoare termenului legal de depunere a decontului de TVA (OUG 70/2024 art. 3 alin. (2)). Raportul pe surse se cere după primirea lui, când apar diferențe.
- **Ce surse pot apărea.** RO e-Factura, RO e-Transport, RO e-Sigiliu, RO e-SAF-T, registrul caselor de marcat electronice, sistemul informatic vamal și alte sisteme ale Ministerului Finanțelor (OUG 70/2024 art. 2 alin. (1)).
- **Rubricile goale nu sunt erori.** Dacă nu există date pentru o rubrică sau operațiunile nu trebuiau transmise la ANAF, rubrica rămâne necompletată (art. 2 alin. (4)). Raportul nu va avea nimic pentru ea.

Limite de reținut:

- Decontul precompletat nu constituie titlu de creanță (OUG 70/2024 art. 3 alin. (5); OPANAF 3775/2024 art. 2 alin. (2)).
- Firma depune în continuare propriul decont D300, până la 25 a lunii următoare perioadei fiscale, cu informații corecte, complete și de bună-credință (OPANAF 3775/2024 art. 5). Raportul pe surse ajută la verificare, nu ține loc de decont.

::: ghid-exemplu
Pentru august 2026, SC Exemplu SRL, plătitoare lunară de TVA, depune D300 cu TVA deductibilă de 18.900 lei. Decontul precompletat, primit până pe 5 octombrie 2026, arată TVA deductibilă de 21.000 lei.

Diferența este de 21.000 − 18.900 = 2.100 lei, adică TVA de 21% la o bază de 10.000 lei. Contabilul cere electronic raportul pe surse. Raportul arată, pe sursa RO e-Factura, o factură de achiziție de 10.000 lei plus TVA 2.100 lei, emisă de un furnizor pe 30 august. Firma a primit-o abia pe 3 septembrie și a înregistrat-o în septembrie.

Cu raportul în mână, diferența este explicată: o factură, o dată, un furnizor. Nu mai trebuie căutată în toată evidența lunii.
:::

## Ce se greșește în practică

- Diferențele sunt comparate doar pe totaluri, fără cererea raportului pe surse, și se pierde timp căutând manual în jurnale.
- Decontul precompletat este tratat ca „cifra corectă" după care se ajustează D300, deși legea spune expres că nu e titlu de creanță.
- Se presupune că rubricile goale din precompletat sunt greșeli ale ANAF. Legea prevede expres că rămân necompletate când nu există date.
- Raportul este căutat pe hârtie sau prin cerere la ghișeu, deși calea prevăzută este cea electronică.

## Ce face iConta.eu

iConta.eu nu descarcă decontul precompletat RO e-TVA și nici rapoartele pe surse, așa că nu le compară automat cu evidența. Aplicația generează D300 din facturile emise și primite și compară, din note validate, TVA colectată și deductibilă din decont cu rulajele lunare ale conturilor 4427 și 4426. Facturile primite prin e-Factura sunt preluate din SPV ca ciorne, pe care contabilul le validează. Odată ce are raportul de la ANAF, contabilul compară facturile din raport cu cele înregistrate în aplicație pentru aceeași lună.

[iConta.eu](/)
