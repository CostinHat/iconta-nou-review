---
title: "Ce faci dacă raportul Z nu corespunde cu numerarul din casierie?"
description: Validarea din formularul de introducere a raportului Z verifică doar aritmetica internă a bonului (totalul pe cote trebuie să corespundă cu numerar + card) — nu verifică și numerarul fizic din sertar. Diferența dintre bon și sertar rămâne o verificare manuală a contabilului.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce faci dacă raportul Z nu corespunde cu numerarul din casierie?

Bonul Z tipărit de casa de marcat arată câți bani „ar trebui" să fie în sertar la închiderea zilei. Când numărătoarea fizică nu se potrivește cu acea sumă, întrebarea e ce face aplicația cu diferența — și răspunsul scurt e: nimic automat. Reconcilierea rămâne o verificare manuală.

## Temeiul legal

::: ghid-temei
„Registrul de casă servește ca: [...] document de stabilire, la sfârșitul fiecărei zile, a soldului de casă; [...] Registrul de casă se întocmește zilnic, pe baza documentelor justificative de încasări și plăți." — OMFP nr. 2634/2015 privind documentele financiar-contabile, Anexa 2 (Norme specifice), Registrul de casă, Cod 14-4-7A
:::

Obligația de a stabili zilnic soldul real de casă e a contabilului/casierului — norma nu descrie un mecanism automat de reconciliere, iar aplicația nu introduce unul acolo unde legea nu-l cere.

## Ce verifică efectiv aplicația — și ce nu verifică

Formularul de introducere manuală a Raportului Z validează o singură regulă aritmetică: suma dintre Total 11% și Total 21% trebuie să corespundă (cu toleranță de 0,01 lei) cu suma dintre numerar și card introduse în aceleași câmpuri. E o verificare de **consistență internă a bonului introdus**, nu o comparație cu numerarul numărat efectiv în casierie — aplicația nu are acces la o „numărătoare fizică" și nu o cere.

Aici contează și calea prin care a intrat raportul:

- **Import fișier AMEF real** → nota contabilă rezultată e generată ca **ciornă**, deci trece printr-un pas de verificare înainte de a deveni definitivă — moment în care o eventuală neconcordanță poate fi observată și corectată.
- **Introducere manuală** (Total 11%/21%, Numerar, Card) → nota contabilă e scrisă direct ca **validată**, fără al doilea control. Dacă suma introdusă manual nu corespunde cu ce arată bonul tipărit sau cu numerarul real din sertar, nimic din aplicație nu semnalează asta — verificarea rămâne integral responsabilitatea persoanei care introduce datele.

## Ce se greșește în practică

- Se presupune că trecerea validării aritmetice a formularului (numerar + card = total pe cote) înseamnă că suma e „confirmată" — validarea confirmă doar că cifrele introduse sunt coerente între ele, nu că se potrivesc cu banii reali din casierie.
- Se introduce manual o sumă „rotunjită" sau estimată, ca să treacă rapid validarea, în loc să se investigheze diferența față de bonul tipărit — nota rezultată devine validată direct, fără al doilea control, deci eroarea rămâne în evidență.
- Se ignoră diferența constatată la numărătoarea fizică, presupunând că se corectează „automat" la următorul Raport Z — aplicația nu reportează sau nu semnalează diferențe de casă între rapoarte.

## Ce face iConta.eu

iConta.eu validează doar coerența aritmetică a datelor introduse pentru Raportul Z (totalurile pe cote trebuie să corespundă cu numerar + card), fără o funcție dedicată de reconciliere cu numărătoarea fizică a casieriei sau de înregistrare a unui plus/minus de casă. Calea de import al fișierului real AMEF oferă un avantaj practic: nota rezultată e ciornă, deci poate fi verificată înainte de validare — pe când introducerea manuală scrie nota direct ca validată. Când apare o neconcordanță între bon și numerarul fizic, verificarea și corectarea rămân, în acest moment, o operațiune manuală a contabilului, în afara automatizărilor aplicației.

[iConta.eu](/)
