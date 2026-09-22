---
title: Pot ajusta baza de TVA pentru o creanță neîncasată de peste 270 de zile?
description: Nu — 270 de zile e pragul pentru deducerea ajustării de creanță la impozitul pe profit (CF art. 26), nu un prag de TVA. Ajustarea bazei de TVA are termene proprii, complet diferite, de la CF art. 287.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Pot ajusta baza de TVA pentru o creanță neîncasată de peste 270 de zile?

Nu există niciun prag de 270 de zile în regulile de ajustare a bazei de impozitare a TVA. Cei "270 de zile" apar în Codul fiscal exclusiv la art. 26 alin. (1) lit. c), care reglementează un subiect diferit — deducerea ajustării pentru deprecierea creanțelor la **impozitul pe profit**. Confuzia între cele două e frecventă pentru că ambele privesc aceeași situație practică (un client care nu plătește), dar regimurile sunt separate, cu temeiuri și termene diferite.

## Temeiul legal

::: ghid-temei
"ajustările pentru deprecierea creanțelor, înregistrate potrivit reglementărilor contabile aplicabile,
reprezentând sume datorate de clienții interni și externi pentru produse, semifabricate, materiale,
mărfuri vândute, lucrări executate și servicii prestate, în limita unui procent de 30% din valoarea
acestor ajustări, altele decât cele prevăzute la lit. d)-f), h) și i), dacă creanțele îndeplinesc
cumulativ următoarele condiții:
1. sunt neîncasate într-o perioadă ce depășește 270 de zile de la data scadenței;
2. nu sunt garantate de altă persoană;
3. sunt datorate de o persoană care nu este persoană afiliată contribuabilului;"

"în cazul în care contravaloarea bunurilor livrate sau a serviciilor prestate nu se poate încasa ca
urmare a intrării în faliment a beneficiarului sau ca urmare a punerii în aplicare a unui plan de
reorganizare admis și confirmat printr-o sentință judecătorească, prin care creanța creditorului este
modificată sau eliminată. Ajustarea este permisă începând cu data pronunțării hotărârii judecătorești
de confirmare a planului de reorganizare, iar, în cazul falimentului beneficiarului, începând cu data
sentinței sau, după caz, a încheierii, prin care s-a decis intrarea în faliment [...] Ajustarea se
efectuează în termen de 5 ani de la data de 1 ianuarie a anului următor [...]"

"în cazul în care contravaloarea totală sau parțială a bunurilor livrate sau a serviciilor prestate nu
a fost încasată de la beneficiarii persoane fizice în termen de 12 luni de la termenul de plată
stabilit de părți, ori în lipsa acestuia, de la data emiterii facturii, cu excepția situației în care
furnizorul/prestatorul și beneficiarul sunt părți afiliate [...] Ajustarea este permisă numai în cazul
în care se face dovada că s-au luat măsuri comerciale pentru recuperarea creanțelor de până la 1.000
lei, inclusiv, respectiv că au fost întreprinse proceduri judiciare pentru recuperarea creanțelor mai
mari de 1.000 lei."
:::

## Cele două regimuri, ca să nu le mai confunzi

| | Impozit pe profit (CF art. 26) | TVA (CF art. 287) |
|---|---|---|
| Ce se ajustează | ajustarea contabilă a creanței (cheltuială deductibilă) | baza de impozitare a TVA deja colectate |
| Prag pentru creanțe comerciale generale | **270 de zile** de la scadență (30% deducere), sau faliment declarat (100%) | **nu există prag în zile** pentru firme; doar evenimente juridice (faliment/reorganizare confirmată) |
| Prag specific persoane fizice | nu se aplică distinct | **12 luni** de la termenul de plată (sau de la factură), cu dovada demersurilor de recuperare |
| Termen de exercitare | anual/trimestrial, odată cu declararea profitului impozabil | 5 ani de la 1 ianuarie a anului următor evenimentului |

Niciunul din cele două regimuri nu folosește pragul de 270 de zile pentru TVA — acela e specific și exclusiv impozitului pe profit.

## Ce se greșește în practică

- Se aplică pragul de 270 de zile de la art. 26 (impozit pe profit) și la ajustarea de TVA, ca și cum ar fi aceeași regulă.
- Se ajustează TVA pentru o creanță comercială veche, fără să existe un eveniment juridic (faliment declarat sau plan de reorganizare confirmat prin hotărâre judecătorească) — pentru firme, simpla vechime a creanței nu justifică ajustarea TVA.
- Se aplică pragul de 12 luni (specific persoanelor fizice) la o creanță față de o firmă, sau invers.
- Se omite dovada demersurilor de recuperare (comerciale sub 1.000 lei, judiciare peste 1.000 lei), obligatorie la ajustarea pentru persoane fizice.
- Se depășește termenul de 5 ani de la 1 ianuarie a anului următor faptului generator, pierzând dreptul de ajustare a TVA.

## Ce face iConta.eu

`core/provizioane.py` calculează procentul de deducere a ajustării de creanță **la impozitul pe profit**, folosind pragul de 270 de zile din CF art. 26 alin. (1) lit. c) — exact regimul cu care se confundă frecvent ajustarea de TVA. Aplicația nu calculează ajustarea bazei de impozitare a TVA (CF art. 287): aceasta se analizează separat, pe baza evenimentului juridic (faliment/reorganizare) sau, pentru persoane fizice, pe baza termenului de 12 luni și a dovezilor de recuperare, conform tabelului de mai sus.

[iConta.eu](/)
