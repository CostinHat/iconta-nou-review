---
title: "D205 și contribuția la sănătate a asociaților"
description: "De ce D205 (declarația firmei privind reținerea la sursă) nu calculează CASS pentru asociați — și unde se declară de fapt contribuția de sănătate pe veniturile din dividende."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# D205 și contribuția la sănătate a asociaților

D205 e declarația prin care firma raportează impozitul reținut la sursă pe veniturile plătite unor persoane fizice (printre care și dividendele către asociați). Contribuția de asigurări sociale de sănătate (CASS) pe aceleași dividende e însă o obligație **separată**, care nu se calculează și nu se declară prin D205, ci de către asociat, prin propria declarație anuală.

## Temeiul legal

::: ghid-temei
„Persoanele fizice care în anul fiscal pentru care se depune declarația prevăzută la art. 122 au realizat venituri din cele prevăzute la art. 155 alin. (1) lit. c)-h), din una sau mai multe surse și/sau categorii de venituri, datorează contribuția de asigurări sociale de sănătate la o bază de calcul stabilită potrivit alin. (3), dacă în anul de realizare a veniturilor valoarea cumulată a acestora este cel puțin egală cu 6 salarii minime brute pe țară."
— Legea 227/2015 (Codul fiscal), art. 170 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă din text:

- Obligația de CASS pe venituri din dividende (categoria de la art. 155 alin. (1) lit. c)-h)) aparține **persoanei fizice** (asociatului), nu firmei care distribuie dividendul.
- CASS se datorează doar dacă **valoarea cumulată** a acestor venituri (dividende plus alte venituri din aceeași categorie: cedarea folosinței bunurilor, investiții etc.) atinge sau depășește **6 salarii minime brute pe țară** în anul respectiv — sub acest prag, contribuția nu e obligatorie.
- Declarația prin care se stabilește și se plătește CASS pentru acest tip de venit e declarația prevăzută la art. 122 din Codul fiscal — Declarația Unică privind impozitul pe venit și contribuțiile sociale (D212) — depusă de asociat, personal, nu de firmă.

D205, în schimb, rămâne exclusiv declarația firmei privind impozitul pe venit **reținut la sursă** din dividendele plătite — un calcul și o obligație diferite de CASS.

## Ce se greșește în practică

- Se așteaptă ca D205 să conțină sau să calculeze CASS pentru asociați — D205 raportează doar impozitul reținut la sursă, nu contribuțiile sociale ale beneficiarului.
- Se omite verificarea plafonului de 6 salarii minime brute pe an, cumulat pe toate veniturile din categoria art. 155 alin. (1) lit. c)-h) ale asociatului, nu doar pe dividendul primit de la o singură firmă.
- Se presupune că firma are vreo obligație de a calcula sau reține CASS pe dividend — obligația e integral a persoanei fizice, prin declarația ei anuală.

## Ce face iConta.eu

Declarația D205 din iConta.eu calculează și raportează impozitul reținut la sursă pe veniturile plătite persoanelor fizice (inclusiv dividendele către asociați) — verificat în cod, modulul D205 nu conține niciun calcul sau referință la CASS. Contribuția de sănătate pe veniturile din categoria art. 155 alin. (1) lit. c)-h), inclusiv pragul de 6 salarii minime din art. 170, e implementată separat, în motorul Declarației Unice (D212) al aplicației, care calculează CASS pe venitul net al persoanei fizice pentru declarația ei personală — un flux distinct de D205, depus de asociat, nu de firmă.

[iConta.eu](/)
