---
title: Cum se ajustează TVA la lichidarea firmei?
description: Ce acoperă efectiv iConta.eu din partea de TVA la lichidare (TVA colectată la vânzarea activelor) și unde se oprește dosarul de cercetare disponibil pentru acest subiect.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se ajustează TVA la lichidarea firmei?

„Ajustarea TVA" la încetarea activității unei societăți este un subiect distinct de TVA colectată la vânzarea unui activ — se referă, în general, la eventuala regularizare a TVA dedusă anterior pentru bunuri care rămân în patrimoniu la momentul radierii sau își schimbă destinația. Este important să separăm clar ce confirmă cercetarea de bază a acestui ghid de ce rămâne de verificat separat.

## Temeiul legal

::: ghid-temei
„Se aprobă Normele metodologice privind reflectarea în contabilitate a principalelor operațiuni de fuziune, divizare, dizolvare și lichidare a societăților [...], cuprinse în anexa nr. 1, care face parte integrantă din prezentul ordin."
— OMFP 897/2015, art. 1
:::

Acest ordin este temeiul contabil general pentru operațiunile de lichidare pe care se bazează și motorul de calcul din iConta.eu. Textul propriu-zis al normelor metodologice (Anexa 1) și al exemplelor de monografii contabile (Anexa 2) se publică separat, în Monitorul Oficial, Partea I, nr. 711 bis, și **nu a fost disponibil în dosarul de cercetare** folosit pentru acest ghid.

**Notă de transparență, conform regulii de aur a acestor ghiduri:** dosarul de cercetare pentru funcționalitatea F057 nu conține un text legal citabil verbatim, specific „ajustării" (regularizării) TVA deduse la lichidarea/radierea unei societăți (de tipul prevederilor din Codul fiscal privind ajustarea deducerii pentru bunuri de capital sau la încetarea calității de plătitor). Nu inventăm aici un asemenea citat. Ceea ce putem confirma, din codul sursă al aplicației, este tratamentul TVA la **vânzarea** activelor rămase în cursul lichidării — descris mai jos.

## Ce se greșește în practică

Se confundă adesea TVA colectată la vânzarea unui activ rămas (care rezultă automat din prețul de vânzare) cu eventuala obligație de ajustare a TVA dedusă inițial la achiziția acelui activ, dacă bunul respectiv nu mai este folosit pentru operațiuni taxabile sau iese din sfera de aplicare a TVA fără vânzare (de exemplu, la predare directă către asociați, în natură, la partaj). Cele două sunt calcule fiscale distincte, iar iConta.eu, conform dosarului de cercetare, are un motor confirmat doar pentru primul caz.

## Ce face iConta.eu

Pentru vânzarea unui activ imobilizat în cursul lichidării, operația „Vânzare activ la lichidare" din ecranul „Lichidare / radiere firmă" calculează și înregistrează automat TVA colectată aferentă prețului de vânzare (`461 = 7583 + 4427`), pe baza cotei de TVA introduse explicit — aplicația nu propune nicio cotă implicită, tocmai pentru ca nota contabilă să reflecte întotdeauna cota corectă în vigoare la data operațiunii.

Aplicația nu are, conform verificării de cod din dosarul de cercetare, o funcție dedicată de calcul al ajustării TVA deduse (regularizare) la lichidare — dacă situația dumneavoastră implică un asemenea calcul (de exemplu bunuri de capital ieșite din patrimoniu altfel decât prin vânzare taxabilă), tratați acest aspect separat, cu sprijinul unui consultant fiscal, pe baza textului integral al Codului fiscal aplicabil la data operațiunii.

[iConta.eu](/)
