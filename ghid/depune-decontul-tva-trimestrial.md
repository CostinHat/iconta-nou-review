---
title: "Cine poate depune decontul de TVA trimestrial"
description: "Condițiile legale pentru a folosi trimestrul, în loc de luna, ca perioadă fiscală de TVA în 2026."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cine poate depune decontul de TVA trimestrial

Regula implicită pentru orice persoană înregistrată în scopuri de TVA e decontul lunar. Trimestrul e excepția, condiționată de o cifră de afaceri mică și de absența achizițiilor intracomunitare de bunuri — iar condiția se verifică în fiecare an, nu se câștigă o singură dată.

## Temeiul legal

::: ghid-temei
„(1) Perioada fiscală este luna calendaristică. (2) Prin excepție de la prevederile alin. (1), perioada fiscală este trimestrul calendaristic pentru persoana impozabilă care în cursul anului calendaristic precedent a realizat o cifră de afaceri din operațiuni taxabile și/sau scutite cu drept de deducere și/sau neimpozabile în România conform art. 275 și 278, dar care dau drept de deducere conform art. 297 alin. (4) lit. b), care nu a depășit plafonul de 100.000 euro al cărui echivalent în lei se calculează conform normelor metodologice, cu excepția situației în care persoana impozabilă a efectuat în cursul anului calendaristic precedent una sau mai multe achiziții intracomunitare de bunuri."
— Codul fiscal (Legea 227/2015), art. 322 alin. (1)-(2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Condiția de bază e dublă, nu doar cifra de afaceri: în anul precedent, cifra de afaceri să nu fi depășit 100.000 euro **și** firma să nu fi făcut nicio achiziție intracomunitară de bunuri — o singură achiziție IC în anul precedent scoate firma din trimestrial, indiferent cât de mică e cifra de afaceri.
- O firmă nou-înregistrată în cursul anului declară, la înregistrare, cifra de afaceri estimată pentru perioada rămasă din an; dacă estimarea (recalculată la an întreg) nu depășește plafonul, poate depune trimestrial chiar din anul înregistrării (art. 322 alin. 3-4).
- Firma care are obligația trimestrialului trebuie să confirme anual acest lucru: până la 25 ianuarie, depune o declarație de mențiuni cu cifra de afaceri din anul precedent și confirmarea că nu a făcut achiziții intracomunitare (art. 322 alin. 6).
- Chiar și o firmă trimestrială trece automat la lunar, în cursul anului, din luna în care face o achiziție intracomunitară de bunuri taxabilă în România — regula exactă depinde de luna trimestrului în care apare exigibilitatea TVA a achiziției (art. 322 alin. 7), cu obligația de a depune o declarație de mențiuni în 5 zile lucrătoare de la sfârșitul lunii respective (alin. 8).
- Dacă cifra de afaceri efectivă a anului depășește plafonul, perioada devine lunară din anul următor (alin. 5); trecerea nu e retroactivă pe anul în care s-a depășit plafonul.

## Ce se greșește în practică

- Se presupune că trimestrul se păstrează definitiv odată obținut, fără verificare anuală a cifrei de afaceri și a achizițiilor intracomunitare din anul precedent.
- Se ignoră declarația de mențiuni de la 25 ianuarie, deși legea o cere explicit firmelor care rămân pe trimestrial.
- Se tratează orice achiziție intracomunitară ca fiind „prea mică" pentru a conta — legea nu are un prag de minimis pentru această condiție, o singură achiziție IC schimbă regimul.
- Se uită trecerea forțată la lunar în cursul anului, declanșată de o achiziție intracomunitară, și se continuă depunerea trimestrială fără declarația de mențiuni obligatorie.

## Ce face iConta.eu

iConta **nu calculează și nu verifică automat** eligibilitatea pentru trimestrial: periodicitatea (`tip_decont`) e un atribut pe care contabilul îl setează manual pe profilul firmei, nu o valoare dedusă din cifra de afaceri a anului precedent sau din prezența achizițiilor intracomunitare. Decontul D300, precum și D394 și SAF-T (D406), urmează întotdeauna acea setare — dacă profilul spune „trimestrial", aplicația generează deconturi pe trimestru, indiferent dacă firma mai îndeplinește sau nu condițiile legale de mai sus. Verificarea condiției (plafonul de 100.000 euro, achizițiile IC din anul precedent) rămâne o decizie profesională a contabilului, făcută în afara aplicației.

[iConta.eu](/)
