---
title: "Cum se rezolvă o diferență de TVA semnalată de sistem"
description: "Ce este decontul precompletat RO e-TVA și cum funcționează compararea automată dintre datele ANAF și decontul depus de firmă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se rezolvă o diferență de TVA semnalată de sistem

Când ANAF „semnalează" o diferență de TVA, de regulă vorbim despre rezultatul Modulului de valorificare RO e-TVA — sistemul care compară automat decontul depus de firmă cu decontul precompletat, generat din datele deja aflate în posesia Ministerului Finanțelor (e-Factura, e-Transport, case de marcat etc.).

## Temeiul legal

::: ghid-temei
„(1) Valorificarea datelor și informațiilor din decontul precompletat RO e-TVA se realizează de către Agenția Națională de Administrare Fiscală, prin identificarea diferențelor dintre datele și informațiile din decontul precompletat RO e-TVA și cele din decontul de taxă pe valoarea adăugată, astfel cum este prevăzut în Legea nr. 227/2015 privind Codul fiscal [...] (Codul fiscal), prin intermediul Modulului de valorificare a datelor și informațiilor RO e-TVA."
— OUG 70/2024, art. 4 alin. (1) (sursă: anaf_surse/oug_70_2024_ro_etva_decont_precompletat.txt)
:::

Câteva repere pentru a înțelege de unde vine diferența și ce trebuie făcut:

- **Sursele decontului precompletat**: RO e-Factura, RO e-Transport, RO e-Sigiliu, RO e-SAF-T, Registrul aparatelor de marcat electronice fiscale (RO e-Case de marcat), sistemul informatic vamal și alte sisteme proprii ale Ministerului Finanțelor — decontul precompletat se construiește automat din aceste surse, nu din datele interne ale firmei.
- **Decontul precompletat nu e titlu de creanță** — el nu creează, prin el însuși, o obligație de plată; el e un instrument de comparație și conformare voluntară.
- **Diferența „semnalată"** apare atunci când decontul depus de firmă (D300) nu corespunde cu ce rezultă din sursele automate ale ANAF — de exemplu, o factură emisă prin RO e-Factura care nu apare colectată în decontul depus, sau invers.
- **Verificarea revine firmei**: după primirea decontului precompletat (transmis până la data de 5 inclusiv a lunii următoare termenului legal de depunere a decontului), persoana impozabilă are obligația să verifice datele precompletate în raport cu operațiunile impozabile realizate și starea de fapt fiscală reală — nu invers, nu se presupune automat că sistemul ANAF are dreptate.
- Dacă diferența e reală (o eroare în decontul depus), corectarea se face prin decont rectificativ, conform regulilor generale de corectare a declarațiilor fiscale (art. 105 din Codul de procedură fiscală).
- Dacă diferența provine dintr-o eroare a surselor ANAF (de exemplu, o factură anulată/corectată care nu s-a reflectat corect în RO e-Factura), justificarea se face documentat, păstrând dovezile operațiunii reale.

## Ce se greșește în practică

- Se ajustează automat decontul depus la cifrele din decontul precompletat, fără verificarea prealabilă dacă diferența vine dintr-o eroare proprie sau dintr-o problemă a surselor ANAF (de exemplu, o factură dublată în e-Factura sau necorelată la timp).
- Se ignoră decontul precompletat, considerându-l fără valoare „pentru că nu e titlu de creanță" — deși nu creează el însuși o datorie, diferențele semnalate rămân un semnal de risc urmărit de ANAF pentru selecția la control.
- Se așteaptă un termen nedefinit pentru rezolvarea diferenței, deși corectarea (dacă e cazul) trebuie făcută prin decont rectificativ, cât mai aproape de momentul constatării erorii.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu se conectează la Modulul de valorificare RO e-TVA** și nu compară automat decontul propriu generat cu decontul precompletat al ANAF — aceasta rămâne o verificare pe care contabilul o face direct în Spațiul Privat Virtual. Aplicația oferă reconcilierea internă între facturi, jurnale și decontul de TVA generat (D300), astfel încât datele proprii ale firmei să fie coerente înainte de comparația cu decontul precompletat ANAF.

[iConta.eu](/)
