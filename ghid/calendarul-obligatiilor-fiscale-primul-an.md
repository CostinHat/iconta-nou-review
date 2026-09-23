---
title: Calendarul obligațiilor fiscale în primul an de activitate
description: Ce declarații apar în calendarul iConta.eu pentru o firmă în primul ei an — de la D100 pe zero până la SAF-T cu perioadă de grație — și ce nu ține de aplicație, ci de formalitățile de înregistrare.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Calendarul obligațiilor fiscale în primul an de activitate

O firmă nouă nu are un calendar fiscal diferit calitativ față de una mai veche — regulile de termen sunt aceleași. Ce diferă e că, în primul an, câteva declarații nu se datorează încă (D112, până la primul angajat), altele apar totuși, chiar fără activitate (D100 pe zero), iar SAF-T are o regulă specială de grație.

## Temeiul legal

::: ghid-temei
„nu își îndeplinește, pe parcursul unui semestru calendaristic, nicio obligație declarativă prevăzută de lege"
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 92 alin. (1) lit. a)
:::

Textul citat mai sus e temeiul pentru care „nu am activitate încă" nu înseamnă „nu depun nimic": firma declarată contribuabil inactiv pentru neîndeplinirea niciunei obligații declarative pe un semestru calendaristic suferă efecte fiscale serioase (inclusiv pierderea dreptului de deducere TVA pe perioada inactivității). Vectorul fiscal — tipurile de obligații pe care le are firma — se stabilește prin ordin ANAF, la înregistrare (Legea 207/2015, art. 91 alin. (4)), și rămâne valabil indiferent dacă firma are sau nu activitate.

## Ce apare, de regulă, în primul an

Presupunând că vectorul fiscal e completat corect din prima lună:

- **D100 „pe zero"** — dacă firma e la impozit pe veniturile microîntreprinderilor, D100 se depune trimestrial (CF art. 56 alin. (1): „până la data de 25 inclusiv a lunii următoare trimestrului pentru care se calculează impozitul"), chiar și fără venituri în trimestrul respectiv. Motivul nu e o obligație legală separată de „depunere pe zero" — e o particularitate structurală a formularului D100, care cere cel puțin o secțiune de obligație completată; contribuabilul rămâne, oricum, obligat să depună declarația conform vectorului fiscal.
- **D112** — apare abia din luna în care firma angajează primul salariat, nu retroactiv pe lunile dinainte. O firmă fără personal nu are D112 de depus.
- **SAF-T (D406)** — obligatorie tuturor persoanelor juridice (cu excepția PFA/II/PFL), dar cu perioadă de grație la prima raportare (6 luni pentru transmitere lunară, 3 luni pentru transmitere trimestrială, descrescătoare la raportările următoare) — extrem de relevantă pentru o firmă nouă, care e mereu „la prima raportare".
- **D101** — abia dacă firma e pe regim de profit; termenul e 25 iunie anul următor, indiferent cât de activă a fost firma în anul respectiv.

## Ce NU arată calendarul iConta.eu

Formalitățile de **înregistrare fiscală la înființare** (declarația de înregistrare/mențiuni la ANAF, opțiunile de TVA/regim la CIF) nu sunt urmărite de calendarul din iConta.eu — sunt un proces care se derulează la ANAF/ONRC, separat de aplicație. Verificat direct: modulele vechi de mențiuni (D010/D020/D070) sunt blocate în iConta (fără validator XML oficial disponibil), iar declarația care le-a înlocuit (D700) are structura recuperată, dar validarea ei e blocată tehnic — niciunul din aceste formulare nu există funcțional în aplicație.

## Ce se greșește în practică

- Se presupune, greșit, că „firmă fără activitate" înseamnă „fără nimic de depus" — de fapt vectorul fiscal declară obligații indiferent de activitate, iar nedepunerea lor riscă declararea ca inactiv.
- Se tratează termenul SAF-T afișat de calendar ca fiind cel real, fără să se aplice perioada de grație de la prima raportare.
- Se așteaptă apariția D112 din prima lună de existență a firmei, deși el apare doar din luna angajării efective.

## Ce face iConta.eu

Ecranul „Termene" derivă scadențele din vectorul fiscal al firmei (regim, statut TVA, tip decont, operațiuni intracomunitare) și din faptele înregistrate (are sau nu salariați), pentru următoarele 60 de zile. Dacă vectorul fiscal nu e completat, firma apare separat, sub „neevaluate", cu mesajul exact „Vector fiscal necompletat — nu pot evalua obligațiile firmei." — nu dispare tăcut din listă.

Perioada de grație SAF-T nu e calculată automat; termenul afișat e cel nominal. Formalitățile de înregistrare la ANAF/ONRC rămân, integral, în afara aplicației.

[iConta.eu](/)
