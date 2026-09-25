---
title: "Ce fac dacă D212 este respinsă de ANAF?"
description: "O respingere la depunerea electronică nu se reface din senin — data validării declarației corectate rămâne cea inițială dacă se depune până la sfârșitul lunii termenului legal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă D212 este respinsă de ANAF?

O respingere la depunere nu înseamnă că declarația s-a pierdut, dar nici că poți lăsa lucrurile așa. Contează foarte mult CÂND o corectezi — legea oferă o plasă de siguranță pentru cine reacționează repede.

## Temeiul legal

::: ghid-temei
„Data depunerii declarației fiscale prin mijloace electronice de transmitere la distanță este data înregistrării acesteia pe portal, astfel cum rezultă din mesajul electronic transmis de sistemul de tranzacționare a informațiilor, cu condiția validării conținutului declarației. În cazul în care declarația nu este validată, data depunerii declarației este data validării astfel cum rezultă din mesajul electronic."
— Legea 207/2015 (Codul de procedură fiscală), art. 103 alin. (4) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„Prin excepție de la prevederile alin. (4), în situația în care declarația fiscală a fost depusă până la termenul legal, iar din mesajul electronic transmis de sistemul de tranzacționare a informațiilor rezultă că aceasta nu a fost validată ca urmare a detectării unor erori în completarea declarației, data depunerii declarației este data din mesajul transmis inițial în cazul în care contribuabilul/plătitorul depune o declarație validă până în ultima zi a lunii în care se împlinește termenul legal de depunere."
— Legea 207/2015, art. 103 alin. (5) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce înseamnă practic:

- O declarație respinsă (nevalidată) din cauza unor erori de completare NU e considerată depusă — regula de bază de la alin. (4).
- Excepția de la alin. (5) salvează situația: dacă declarația inițială a fost trimisă până la termenul legal (ex. 25 mai) și o versiune validă se depune până la sfârșitul lunii respective, data depunerii rămâne cea din mesajul inițial — deci fără penalități de întârziere.
- Dincolo de sfârșitul lunii în care se împlinește termenul legal, corectarea și redepunerea se face în regim de declarație depusă cu întârziere.
- Dacă declarația a fost validată, dar conține o eroare de conținut (nu de formă), corecția se face printr-o declarație rectificativă (art. 105), nu prin repetarea depunerii inițiale.

## Ce se greșește în practică

- Se lasă declarația respinsă necorectată, presupunând că „ANAF va reveni" — respingerea nu generează nicio acțiune automată din partea organului fiscal, corectarea e responsabilitatea contribuabilului.
- Se depune o versiune corectată după sfârșitul lunii termenului legal, fără să se realizeze că plasa de siguranță a expirat și declarația e acum considerată depusă cu întârziere.
- Se confundă respingerea tehnică (eroare de validare la depunere) cu o eroare de conținut descoperită ulterior, pe o declarație deja validată — cele două se rezolvă diferit (redepunere vs. rectificativă).

## Ce face iConta.eu

Generatorul D212 al iConta.eu (`core/d212.py`) construiește XML-ul conform structurii validate de ANAF (D212Validator) — respectă câmpurile obligatorii pe rădăcină și pe fiecare capitol, ceea ce reduce riscul unei respingeri din cauza unor câmpuri lipsă sau invalide la nivel de structură. Aplicația nu are însă integrare directă cu portalul ANAF pentru depunere și validare online: nu primește și nu procesează automat mesajul de respingere al sistemului ANAF, iar urmărirea termenului de „ultima zi a lunii" pentru redepunerea validă rămâne o obligație a contabilului, în afara aplicației.

[iConta.eu](/)
