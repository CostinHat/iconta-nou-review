---
title: "Cum se reflectă pierderile de colet în contabilitate"
description: O pierdere de colet e, contabil, o lipsă de marfă constatată în gestiune — tratamentul diferă după cum lipsa e imputabilă unui vinovat (curier, transportator) sau nu, cu efecte diferite asupra TVA și a impozitului pe profit.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se reflectă pierderile de colet în contabilitate

Un colet pierdut în timpul transportului sau al livrării se reflectă în contabilitate ca o lipsă de marfă din gestiune — nu ca o categorie contabilă separată. Tratamentul corect depinde de un singur lucru: poți sau nu identifica un vinovat și recupera contravaloarea de la el.

## Temeiul legal

::: ghid-temei
„Nu se ajustează deducerea inițială a taxei în cazul: a) bunurilor distruse, pierdute sau furate, în condițiile în care aceste situații sunt demonstrate sau confirmate în mod corespunzător de persoana impozabilă. În cazul bunurilor furate, persoana impozabilă demonstrează furtul bunurilor pe baza actelor doveditoare emise de organele judiciare."
— Codul fiscal, art. 304 alin. (2) lit. a)
:::

::: ghid-temei
„cheltuielile privind bunurile de natura stocurilor [...] constatate lipsă din gestiune ori degradate, neimputabile, precum și taxa pe valoarea adăugată aferentă [...] sunt deductibile în următoarele situații/condiții: 1. bunurile [...] distruse ca urmare a unor calamități naturale sau a altor cauze de forță majoră [...]; 2. bunurile [...] pentru care au fost încheiate contracte de asigurare; 3. bunurile [...] degradate calitativ, dacă se face dovada distrugerii [...]"
— Codul fiscal, art. 25 alin. (4) lit. c)
:::

Dacă poți identifica vinovatul — de exemplu firma de curierat, printr-o reclamație recunoscută sau o despăgubire acordată — lipsa e **imputabilă**: se descarcă gestiunea, iar contravaloarea recuperată se înregistrează ca venit din imputare, cu TVA calculată pe valoarea imputată.

Dacă nu există vinovat identificat sau recuperare, lipsa e **neimputabilă**. Aici contează dovada: dacă pierderea e demonstrată sau confirmată corespunzător (de exemplu proces-verbal de constatare, confirmarea transportatorului), TVA dedusă inițial nu se ajustează (art. 304 alin. 2 lit. a). Dacă lipsa nu poate fi demonstrată, TVA se ajustează (se restituie, prin 635=4426). Cât despre impozitul pe profit, cheltuiala cu marfa pierdută neimputabil e, ca regulă, nedeductibilă — devine deductibilă doar dacă se încadrează într-una din situațiile enumerate limitativ la art. 25 alin. (4) lit. c) (calamitate, asigurare, dovadă de distrugere pentru degradare etc.). Un colet „pur și simplu pierdut", fără nicio dovadă și fără asigurare, nu e automat deductibil.

## Ce se greșește în practică

- Se tratează orice colet pierdut ca fiind automat deductibil fiscal, fără verificarea condițiilor limitative de la art. 25 alin. (4) lit. c).
- Se omite ajustarea TVA atunci când lipsa nu poate fi demonstrată sau confirmată corespunzător.
- Se confundă „pierdere de colet imputabilă transportatorului" cu „pierdere neimputabilă", deși regimul contabil și fiscal e diferit în fiecare caz.

## Ce face iConta.eu

Operația „Minus" din formularul „Inventariere anuală" înregistrează scăderea din gestiune a mărfii pierdute, cu cont de stoc dintre cele predefinite (371, 301, 302, 303, 345, 381), cotă de TVA obligatorie (fără valoare implicită) și un flag pentru imputabil/neimputabil. Pentru minusul imputabil, generează nota pe salariat sau terț, cu TVA pe valoarea de imputare; pentru cel neimputabil, aplică ajustarea de TVA doar dacă marchezi explicit lipsa ca nedemonstrată/nedistrusă — altfel, dacă bifezi „asigurat sau distrus dovedit", nu adaugă linia de ajustare TVA. Decizia despre deductibilitatea la impozitul pe profit rămâne, în toate cazurile, a ta — aplicația nu evaluează automat dacă situația se încadrează într-una din excepțiile din art. 25 alin. (4) lit. c).

[iConta.eu](/)
