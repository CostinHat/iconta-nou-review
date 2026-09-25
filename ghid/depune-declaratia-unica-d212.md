---
title: "Unde se depune Declarația Unică D212?"
description: "D212 se depune la organul fiscal competent, de regulă prin mijloace electronice de transmitere la distanță — data validării, nu a trimiterii, contează ca dată de depunere."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Unde se depune Declarația Unică D212?

D212 se depune la organul fiscal central competent pentru contribuabilul persoană fizică, iar în practică aproape toate depunerile se fac electronic, prin sistemul de transmitere la distanță al ANAF (Spațiul Privat Virtual). Data care contează ca dată de depunere nu e cea la care apeși „trimite", ci cea a validării declarației de către sistem.

## Temeiul legal

::: ghid-temei
„Declarația fiscală se depune la registratura organului fiscal competent sau se comunică prin poștă, cu confirmare de primire, ori prin mijloace electronice sau prin sisteme electronice de transmitere la distanță."
— Legea 207/2015 (Codul de procedură fiscală), art. 103 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„Data depunerii declarației fiscale prin mijloace electronice de transmitere la distanță este data înregistrării acesteia pe portal, astfel cum rezultă din mesajul electronic transmis de sistemul de tranzacționare a informațiilor, cu condiția validării conținutului declarației. În cazul în care declarația nu este validată, data depunerii declarației este data validării astfel cum rezultă din mesajul electronic."
— Legea 207/2015, art. 103 alin. (4) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce contează de reținut din text:

- Există trei canale legale de depunere: registratura organului fiscal, poșta cu confirmare de primire, sau mijloace electronice — dar legea lasă pe seama ANAF, prin ordin al președintelui, care declarații se depun obligatoriu electronic.
- Pentru depunerea electronică, data e cea a **validării** conținutului, nu a transmiterii — o declarație trimisă la timp dar respinsă de sistem din cauza unor erori nu e considerată depusă la acea dată.
- Art. 103 alin. (5) oferă totuși o plasă de siguranță: dacă declarația a fost transmisă până la termenul legal, dar respinsă din cauza unor erori, iar o declarație validă e depusă până în ultima zi a lunii în care se împlinește termenul, se păstrează data depunerii inițiale.
- O declarație depusă la un organ fiscal necompetent nu se pierde — se consideră depusă la data înregistrării acolo, iar organul necompetent are obligația s-o transmită celui competent în 5 zile lucrătoare.

## Ce se greșește în practică

- Se consideră declarația „depusă" din momentul trimiterii, fără să se verifice mesajul electronic de confirmare a validării — o eroare de completare nedescoperită la timp poate muta data reală de depunere.
- Se ignoră excepția de „ultimă zi a lunii" pentru corectarea unei declarații respinse din cauza erorilor — mulți refac declarația crezând că termenul legal a fost deja depășit.
- Se trimite declarația la un organ fiscal greșit fără să se mai verifice ulterior că a ajuns la organul competent.

## Ce face iConta.eu

D212 e o declarație manuală în iConta.eu (`core/d212.py`), care generează fișierul XML conform structurii validate de ANAF (D212Validator), pregătit pentru depunere. Aplicația nu are integrare directă cu portalul ANAF pentru transmiterea automată a D212 — depunerea efectivă, prin Spațiul Privat Virtual sau alt canal electronic, rămâne un pas separat, făcut de contabil sau contribuabil în afara aplicației.

[iConta.eu](/)
