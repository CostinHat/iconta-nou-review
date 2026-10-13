---
title: "Cum se gestionează stocul de alimente perisabile la final de lună"
description: "Explică pașii legali pentru înregistrarea perisabilităților la alimente și cum generează iConta.eu nota contabilă lunară, cu limitele ei."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Cum se gestionează stocul de alimente perisabile la final de lună

La final de lună, pierderile constatate la alimentele perisabile (marfă cumpărată și revândută ca atare) se înregistrează contabil în limita coeficientului legal, cu documentele obligatorii care susțin constatarea.

Procedura standard: la constatarea faptică (inventariere, recepție sau predare de gestiune), administratorul aprobă pierderea, se întocmește proces-verbal, iar limita maximă deductibilă se calculează aplicând coeficientul grupei de mărfuri (din anexele HG 831/2004) la valoarea de înregistrare a intrărilor lunii, nu la stocul final. În limită, valoarea e deductibilă fără ajustare de TVA; peste limită, partea excedentară devine cheltuială nedeductibilă și, în plus, TVA-ul deja dedus la achiziție se ajustează pe partea de depășire — cu excepția cazului în care degradarea calitativă e dovedită și bunul e demonstrat distrus, situație în care ajustarea de TVA nu se face.

## Ce se greșește în practică

Greșeli frecvente: aplicarea coeficientului la stocul final în loc de valoarea intrărilor lunii; lipsa procesului-verbal sau a aprobării administratorului, care fac deductibilitatea contestabilă chiar dacă procentul e corect; și confundarea înregistrării contabile (valorică) cu scăderea efectivă din gestiunea cantitativă a stocului.

## Ce face iConta.eu

Din Operațiuni speciale → "Perisabilități și scăzăminte" (rută `nota-perisabilitati`), contabilul introduce valoarea intrărilor, procentul limită (stabilit din anexa HG 831/2004 aplicabilă grupei de produse — aplicația nu are acest tabel încorporat), pierderea constatată, cota de TVA (obligatorie, fără valoare implicită) și, opțional, dovada distrugerii. Motorul calculează automat limita, partea deductibilă/nedeductibilă și ajustarea de TVA aferentă, generând o notă contabilă în ciornă, cu descrierea sufixată automat "HG 831/2004".

Important de reținut: nota generată e o mișcare exclusiv valorică, în jurnalul contabil (`inregistrari`/„notele contabile”) — „Perisabilități și scăzăminte” nu scade cantitatea din gestiune (tabelele `articole`/„mișcările de stoc” nu sunt atinse). Contabilitatea și gestiunea sunt evidențe paralele în iConta.eu; dacă se dorește și o scădere cantitativă corelată a stocului, aceasta se face separat și manual, prin modulul de stocuri.

[iConta.eu](/)
