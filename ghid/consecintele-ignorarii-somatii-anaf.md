---
title: "Consecințele ignorării unei somații ANAF"
description: "Ce se întâmplă dacă debitul dintr-o somație de executare silită nu este stins în termenul de 15 zile: continuarea măsurilor de executare silită, potrivit Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Consecințele ignorării unei somației ANAF

Somația este actul prin care începe, formal, executarea silită a unei creanțe fiscale. Ignorarea ei nu înseamnă „câștigarea de timp" — legea prevede un termen scurt după care măsurile de executare silită continuă automat.

## Temeiul legal

::: ghid-temei
„ART. 230 Somația
(1) Executarea silită începe prin comunicarea somației. Dacă în termen de 15 zile de la comunicarea somației nu se stinge debitul sau nu se notifică organul fiscal cu privire la intenția de a demara procedura de mediere, se continuă măsurile de executare silită. Somația este însoțită de un exemplar al titlului executoriu emis de organul de executare silită."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 230 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce înseamnă concret ignorarea somației:

- De la comunicarea somației există **15 zile** pentru a alege una dintre două căi: stingerea debitului sau notificarea organului fiscal cu privire la intenția de a intra într-o procedură de mediere.
- Dacă niciuna dintre aceste două acțiuni nu are loc în termen, organul fiscal **continuă măsurile de executare silită** — care pot include poprirea conturilor bancare sau sechestrul asupra bunurilor, fără o nouă înștiințare prealabilă obligatorie pentru fiecare pas.
- Procedura de mediere, dacă e solicitată la timp, oferă o cale de a clarifica întinderea obligației sau de a discuta modalități de stingere — dar trebuie inițiată explicit, prin notificare către organul fiscal, în același termen de 15 zile.

## Ce se greșește în practică

- Se ignoră somația considerând-o „o formalitate" sau presupunând că urmează neapărat o nouă înștiințare înainte de poprire — legea nu impune o a doua somație pentru continuarea executării.
- Se așteaptă mai mult de 15 zile pentru a solicita medierea, pierzând fereastra în care aceasta putea suspenda temporar procesul.
- Se contestă direct executarea silită fără a urma mai întâi calea mai rapidă și mai puțin costisitoare a medierii, disponibilă chiar în acest termen de 15 zile.

## Ce face iConta.eu

Verificat în cod: `core/control_fiscal_api.py` și `core/alerte_control_fiscal.py` verifică și notifică riscuri de neconcordanță între declarații și contabilitate (TVA, D112, D390), dar iConta.eu nu are, la acest moment, un modul care să urmărească somațiile primite de la ANAF sau termenele de 15 zile aferente lor — gestionarea unei somații de executare silită rămâne, integral, în afara aplicației.

[iConta.eu](/)
