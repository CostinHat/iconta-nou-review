---
title: "Cum se validează fișierul XML al D112?"
description: "Cine aprobă modelul și structura formularului 112 și de ce transmiterea prin mijloace electronice presupune trecerea fișierului printr-un validator conform."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se validează fișierul XML al D112?

D112 nu e o declarație liberă la completare — modelul, conținutul și structura fișierului electronic sunt aprobate printr-un ordin comun al ANAF, Casei Naționale de Pensii Publice, CNAS și ANOFM, iar depunerea ei se face obligatoriu prin mijloace electronice de transmitere la distanță, ceea ce presupune conformitatea fișierului cu structura XML publicată oficial.

## Temeiul legal

::: ghid-temei
„Art. 1 - (1) Se aprobă modelul şi conţinutul formularului 112 «Declaraţie privind obligaţiile de plată a contribuţiilor sociale, impozitului pe venit şi evidenţa nominală a persoanelor asigurate»... (4) Declaraţia prevăzută la alin. (1) este o declaraţie de impunere în sensul art. 1 pct. 18 din Legea nr. 207/2015 privind Codul de procedură fiscală. Art. 3 - Persoanele fizice şi juridice care au calitatea de angajatori sau sunt asimilate acestora... au obligaţia depunerii declaraţiei prevăzute la art. 1 prin mijloace electronice de transmitere la distanţă."
— Ordinul comun ANAF/CNPP/CNAS/ANOFM nr. 605/95/928/2.314/2026, art. 1 și art. 3 (sursă: anaf_surse/opanaf_605_2026_d112.txt)
:::

Ce înseamnă, practic, „validarea" fișierului XML al D112:

- Structura tehnică a fișierului (elementele obligatorii, formatul câmpurilor, relațiile dintre secțiuni) e cea publicată de ANAF pentru versiunea în vigoare a formularului — orice fișier depus trebuie să respecte exact această structură, nu o variantă aproximativă.
- Verificarea de conformitate se face, în practică, printr-un **validator oficial** (soft-ul XSD/DUK pus la dispoziție de ANAF pentru fiecare versiune a declarației), care confirmă dacă fișierul respectă schema și regulile de validare semantică (de exemplu corelații între baza de calcul și contribuția aferentă, coduri CNP/CUI valide, indicative corecte pentru condiții deosebite de muncă).
- Fiind o **declarație de impunere** (în sensul Codului de procedură fiscală), o eroare de structură care blochează validarea echivalează, practic, cu imposibilitatea depunerii — nu doar cu un avertisment cosmetic.
- Depunerea prin mijloace electronice de transmitere la distanță e obligatorie pentru angajatori — fișierul „hârtie" nu mai e o variantă validă pentru majoritatea situațiilor.

## Ce se greșește în practică

- Se generează fișierul XML după o versiune veche a structurii, fără verificarea dacă în intervalul respectiv a apărut un ordin nou care modifică formularul sau nomenclatoarele aferente.
- Se ignoră mesajele de eroare ale validatorului atunci când par „fără legătură" cu secțiunea vizată — adesea eroarea reală se află într-o secțiune anterioară din fișier, care rupe parsarea restului documentului.
- Se presupune că un fișier „care se deschide corect" într-un editor XML e automat valid pentru ANAF — validitatea sintactică (XML bine format) nu înseamnă conformitate cu schema și regulile semantice specifice D112.

## Ce face iConta.eu

La data acestui ghid, generatorul D112 din iConta.eu produce fișierul XML direct conform structurii extrase din validatorul oficial (XSD-ul publicat de ANAF pentru versiunea curentă a formularului), cu verificări interne suplimentare (checksum CNP/CUI, câmpuri obligatorii per lege) înainte de a considera declarația gata de depunere. Contabilul rămâne responsabil să confirme că versiunea de formular folosită e cea în vigoare pentru perioada declarată.

[iConta.eu](/)
