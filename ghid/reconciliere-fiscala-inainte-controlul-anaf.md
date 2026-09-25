---
title: "Cum fac o reconciliere fiscală înainte de controlul ANAF?"
description: "Ce înseamnă reconcilierea dintre declarațiile fiscale depuse și evidența contabilă, și de ce e primul pas înainte de un control ANAF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum fac o reconciliere fiscală înainte de controlul ANAF?

Înainte de un control, organul fiscal compară ce ai declarat (D300, D112, D390 etc.) cu ce arată evidența ta contabilă. Dacă cele două nu coincid, diferența devine primul obiect al verificării — și, potrivit legii, poate atrage stabilirea creanței fiscale prin estimare. O reconciliere fiscală înseamnă exact acest exercițiu, făcut de tine, înainte ca ANAF să-l facă în locul tău.

## Temeiul legal

::: ghid-temei
„(1) Organul fiscal stabilește baza de impozitare și creanța fiscală aferentă, prin estimarea rezonabilă a bazei de impozitare, folosind orice probă și mijloc de probă prevăzute de lege, ori de câte ori acesta nu poate determina situația fiscală corectă.
(2) Stabilirea prin estimare a bazei de impozitare se efectuează în situații cum ar fi: [...] b) în situația în care organul fiscal nu poate determina situația fiscală corectă și constată că evidențele contabile sau fiscale ori declarațiile fiscale sau documentele și informațiile prezentate în cursul controlului fiscal sunt incorecte, incomplete, precum și în situația în care acestea nu există ori nu sunt puse la dispoziția organelor fiscale."
— Legea nr. 207/2015, art. 106 alin. (1)-(2) lit. b) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Practic, riscul nu e doar „am greșit o cifră", ci ce se întâmplă dacă evidența nu se poate reconcilia cu declarațiile: organul fiscal are dreptul legal să stabilească el însuși baza de impozitare, prin estimare, iar sarcina de a demonstra contrariul cade pe contribuabil.

- **TVA (D300)**: TVA colectată declarată trebuie să corespundă rulajului contului 4427, iar TVA deductibilă rulajului contului 4426, pe aceeași lună.
- **Salarii (D112)**: impozitul, CAS și CASS declarate trebuie să corespundă rulajelor din conturile 444, 4315 și 4316.
- **Operațiuni intracomunitare (D390)**: bazele declarate trebuie să corespundă facturilor intracomunitare înregistrate în perioada respectivă.
- Orice divergență nu înseamnă automat o eroare — poate fi doar o evidență rămasă în urmă (facturi emise, dar neînregistrate încă) — dar trebuie identificată și explicată înainte de control, nu în timpul lui.

## Ce se greșește în practică

- Se verifică doar totalul de plată din declarație, nu structura ei pe rânduri, față de rulajele conturilor corespunzătoare.
- Se presupune că „am depus declarația, deci sunt acoperit" — dar depunerea nu garantează concordanța cu contabilitatea; ANAF verifică exact acest raport.
- Reconcilierea se face abia când vine notificarea de control, când remedierea diferențelor din urmă e mult mai greoaie decât corectarea lunară curentă.

## Ce face iConta.eu

iConta.eu are un modul de verificare încrucișată care compară, lună de lună, ce a fost declarat (TVA colectată/deductibilă din D300, impozit/CAS/CASS din D112, bazele din D390) cu rulajele conturilor corespunzătoare din balanță (4427/4426, 444/4315/4316). Rezultatul e afișat cu trei stări: verde (verificat și coerent), roșu (verificat și divergent) și gri (nu s-a putut verifica din lipsă de date) — aplicația nu ascunde o divergență pe care nu o poate confirma. Nicio constatare nu e „ajustată" ca să iasă verde: o divergență reală rămâne vizibilă până e explicată sau corectată în evidență, nu cosmetizată.

[iConta.eu](/)
