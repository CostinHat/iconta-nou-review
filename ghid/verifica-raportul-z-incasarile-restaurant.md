---
title: Cum se verifică raportul Z cu încasările din restaurant?
description: Verificarea contează diferit după calea aleasă la înregistrare — importul de fișier AMEF produce o notă ciornă, verificabilă înainte să intre în rulaj; introducerea manuală intră direct ca notă validată.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se verifică raportul Z cu încasările din restaurant?

Controlul standard e simplu în principiu — totalul din Raportul Z trebuie să corespundă cu numerarul din casă și cu încasările de pe extrasul/terminalul de card. În aplicație însă, momentul la care se face verificarea diferă după calea de încărcare aleasă.

## Temeiul legal

::: ghid-temei
„Registrul de casă servește ca: [...] document de stabilire, la sfârșitul fiecărei zile, a soldului de casă [...] Registrul de casă se întocmește zilnic, pe baza documentelor justificative de încasări și plăți." — OMFP 2634/2015, Anexa 2 (Norme specifice), Registrul de casă (Cod 14-4-7A)
:::

## Ce verifici, pas cu pas

1. **Totalul pe Z tipărit** — suma pe cote (mâncare/alcool) + numerar + card trebuie să dea totalul afișat pe bonul Z fizic. Aplicația validează matematic doar egalitatea `numerar + card = total pe cote`, nu compară cu bonul tipărit — asta rămâne verificare manuală.
2. **Numerarul din Z vs. numerarul fizic din casă** — dacă firma ține și un registru de casă operativ separat (obligatoriu conform OMFP 2634/2015), soldul de acolo trebuie confruntat cu numerarul din Z, pentru că cele două evidențe nu se alimentează automat una din alta în aplicație.
3. **Cardul din Z vs. extrasul/terminalul POS** — vezi reconcilierea POS-Z, care are propriul ghid.

## Diferența importantă între cele două căi de înregistrare

Dacă Raportul Z a fost încărcat prin **import de fișier AMEF**, nota contabilă rezultată are statut de **ciornă** — rămâne vizibilă și modificabilă până la o verificare ulterioară, exact ca un al doilea om care confruntă cu Z-ul tipărit.

Dacă a fost introdus **manual** (totalurile pe cote, numerar, card, tastate direct în formular), nota contabilă se generează **direct ca validată** — fără pasul intermediar de ciornă. Practic, orice eroare de tastare la introducerea manuală ajunge deja în evidența validată înainte de o eventuală a doua verificare, spre deosebire de calea prin import.

## Ce se greșește în practică

Tratarea introducerii manuale ca fiind la fel de „sigură" ca importul, pentru că amândouă duc la aceeași notă contabilă finală — de fapt doar calea prin fișier trece printr-un pas de ciornă care poate fi verificat înainte de a intra definitiv în rulaj.

## Ce face iConta.eu

Aplicația marchează explicit statutul notei: „ciornă" pentru import AMEF, generat direct ca validat pentru introducerea manuală. Validarea automată se limitează la coerența aritmetică (numerar + card = total pe cote); confruntarea cu bonul Z tipărit și cu extrasul de cont rămâne o verificare pe care o face contabilul, nu una automatizată de aplicație.

[iConta.eu](/)
