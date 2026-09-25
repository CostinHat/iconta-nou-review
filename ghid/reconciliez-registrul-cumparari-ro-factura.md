---
title: "Cum reconciliez registrul de cumpărări cu RO e-Factura?"
description: "Nu există o obligație legală distinctă de 'reconciliere' a registrului de cumpărări cu RO e-Factura — dar sistemul național privind factura electronică, definit prin OUG 120/2021, este sursa oficială a facturilor primite pe care se bazează orice verificare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum reconciliez registrul de cumpărări cu RO e-Factura?

Legea nu prevede o procedură explicită numită „reconciliere” între registrul de cumpărări și RO e-Factura — ceea ce prevede este funcționarea sistemului național privind factura electronică drept canal oficial prin care operatorii economici emit și primesc facturi. Verificarea că fiecare achiziție înregistrată în contabilitate are corespondent în facturile primite prin sistem este o practică de control intern, nu o obligație declarativă separată, dar se sprijină direct pe definițiile din actul normativ care a înființat sistemul.

## Temeiul legal

::: ghid-temei
„c) emitent al facturii electronice - operatorul economic care emite factura electronică către destinatar şi o transmite în sistemul naţional privind factura electronică RO e-Factura [...]
(2) Sistemul naţional privind factura electronică RO e-Factura reprezintă ansamblul de principii, reguli şi aplicaţii informatice având drept scop primirea facturii electronice de la emitent cu respectarea structurii facturii electronice prevăzute la art. 4 alin. (1), stocarea prin mijloace electronice a facturilor şi transmiterea către destinatar."
— OUG nr. 120/2021, art. 2 lit. c) și art. 3 alin. (2) (sursă: anaf_surse/oug_120_2021.txt)
:::

Ce rezultă de aici pentru practica de reconciliere:

- RO e-Factura este **sistemul oficial** prin care facturile electronice ajung la destinatar — orice factură primită prin acest canal poate fi descărcată din Spațiul Privat Virtual și comparată cu ce a fost efectiv înregistrat în contabilitate.
- Nu există o normă care să impună explicit un „proces de reconciliere” cu un termen legal — scopul verificării este practic: să nu rămână facturi primite prin sistem neînregistrate în registrul de cumpărări (risc de TVA nededusă) și nici înregistrări în contabilitate care nu au corespondent oficial în sistem.
- Dreptul de deducere a TVA rămâne condiționat de deținerea documentelor justificative, potrivit regulilor generale din Codul fiscal (art. 297-301) — o factură primită prin RO e-Factura, dar neînregistrată, nu generează automat deducere; trebuie preluată și contabilizată.

## Ce se greșește în practică

- Se presupune că simpla primire a unei facturi în RO e-Factura echivalează cu înregistrarea ei automată în contabilitate și în registrul de cumpărări — preluarea și contarea rămân un pas distinct.
- Se face reconcilierea o singură dată, la final de lună, în loc să se verifice periodic dacă toate facturile primite prin sistem au corespondent în evidența contabilă, ceea ce crește riscul de a rata termenul de deducere pentru o factură „pierdută”.
- Se confundă existența unei facturi în sistem cu validarea ei fiscală completă (cotă corectă, bază de calcul, calitate de persoană impozabilă a emitentului) — sistemul transmite factura, nu validează conținutul ei fiscal.

## Ce face iConta.eu

iConta.eu preia facturile electronice primite prin RO e-Factura (format UBL 2.1/CIUS-RO) și le contabilizează automat, extrăgând numărul, data, scadența, furnizorul/clientul, totalul cu TVA și liniile facturii direct din fișierul XML. Această preluare automată este, în esență, mecanismul prin care aplicația leagă registrul de cumpărări de sursa oficială RO e-Factura — dar o verificare manuală, factură cu factură, de tip „reconciliere” explicită nu este o funcționalitate separată în aplicație.

[iConta.eu](/)
