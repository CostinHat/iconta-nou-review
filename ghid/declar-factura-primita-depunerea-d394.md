---
title: "Cum declar o factură primită după depunerea D394?"
description: "Ce se întâmplă când o factură de achiziție ajunge la firmă după ce D394 pentru perioada respectivă a fost deja depusă, conform instrucțiunilor oficiale de completare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum declar o factură primită după depunerea D394?

D394 raportează facturile de achiziție în funcție de perioada în care au fost **primite** de firmă, nu în funcție de data emiterii lor. Dacă o factură ajunge după ce declarația pentru luna/trimestrul respectiv a fost deja depusă, soluția nu e să o „strecori" în declarația perioadei curente, ci să depui o declarație rectificativă care înlocuiește integral declarația inițială.

## Temeiul legal

::: ghid-temei
„Declaraţia trebuie să conţină facturile care au fost primite în perioada de raportare, inclusiv cele care au înscrisă menţiunea «taxare inversă» sau «TVA la încasare», precum şi borderourile de achiziţii de bunuri şi filele din carnetele de comercializare a produselor din sectorul agricol în cazul achiziţiilor efectuate de la persoane fizice. [...] 3. În cazul în care, după depunerea declaraţiei, persoana impozabilă constată existenţa unor omisiuni/erori în datele declarate, aceasta trebuie să depună o nouă declaraţie corect completată, cu operaţiunile care necesită modificarea şi/sau operaţiunile care nu au fost declarate, declaraţie care înlocuieşte declaraţia informativă depusă iniţial."
— OPANAF 3.769/2015, Anexa nr. 2 - Instrucțiuni de completare a formularului 394 (sursă: anaf_surse/opanaf_3769_2015_d394_baza.txt)
:::

Rezultă două situații distincte:

- **Factura ajunge înainte de termenul de depunere** (25 a lunii următoare perioadei de raportare a decontului), dar firma a depus deja D394: se depune o **declarație care înlocuiește** integral declarația inițială, cu factura adăugată — nu o completare parțială.
- **Factura ajunge după ce s-a constatat, ulterior, o omisiune** (inclusiv după termenul de depunere): se aplică aceeași regulă — o nouă declarație informativă, corect completată, cu operațiunile care necesită modificare și/sau cele nedeclarate, care înlocuiește declarația depusă inițial pentru acea perioadă.

Important: declarația nouă **nu adaugă** doar factura lipsă — ea trebuie să conțină din nou toate operațiunile perioadei respective, corect completate, pentru că declarația nouă înlocuiește integral, nu completează, declarația depusă anterior.

## Ce se greșește în practică

- Se raportează factura primită târziu în declarația D394 a perioadei curente (când a fost primită efectiv factura), în loc de perioada în care ar fi trebuit inclusă conform regulii de „primire" — dacă factura aparține de o perioadă deja declarată, ea se adaugă prin rectificarea acelei perioade, nu prin includerea în perioada curentă.
- Se depune o declarație „doar cu diferența" (numai factura nouă), presupunând că ANAF o va cumula cu declarația inițială — declarația rectificativă trebuie să conțină toate operațiunile perioadei, pentru că înlocuiește, nu completează.
- Se amână depunerea rectificativei „până la următorul decont de TVA", tratând-o ca opțională — legea nu prevede un termen limită separat pentru rectificare, dar obligația de a corecta omisiunea există din momentul constatării ei.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează D394 din facturile de achiziție înregistrate pe perioada de raportare selectată (`core/d394.py` construiește declarația din datele curente ale bazei), dar **nu automatizează** detectarea unei facturi înregistrate ulterior pentru o perioadă deja declarată și nici generarea automată a unei declarații rectificative care să înlocuiască declarația inițială cu factura adăugată. Identificarea facturilor „întârziate" și depunerea rectificativei corespunzătoare rămân, la această dată, o verificare și o acțiune manuală a contabilului.

[iConta.eu](/)
