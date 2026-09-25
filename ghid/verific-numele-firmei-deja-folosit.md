---
title: "Cum verific dacă numele firmei mele nu e deja folosit"
description: "De ce denumirea societății este o condiție de valabilitate a actului constitutiv, și de ce verificarea disponibilității ei ține de o procedură separată, la registrul comerțului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific dacă numele firmei mele nu e deja folosit

Denumirea unei firme nu e un detaliu estetic al actului constitutiv — legea o tratează ca element obligatoriu, a cărui lipsă poate duce chiar la nulitatea societății. Verificarea disponibilității unei denumiri, în schimb, e o procedură administrativă separată, ținută de registrul comerțului, iar sursele fiscale folosite pentru acest ghid confirmă doar prima parte, nu și pașii tehnici ai celei de-a doua.

## Temeiul legal

```
::: ghid-temei
„Nulitatea unei societăți înmatriculate în registrul comerțului poate fi declarată de tribunal numai atunci când: [...] f) actul constitutiv nu prevede denumirea societății, obiectul său de activitate, aporturile asociaților sau capitalul social subscris."
— Legea nr. 31/1990 a societăților, art. 56 lit. f) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::
```

Ce se poate confirma, cu onestitate, din text:

- **Denumirea societății e o mențiune obligatorie a actului constitutiv**, alături de obiectul de activitate, aporturile asociaților și capitalul social subscris — lipsa ei atrage, potrivit legii, chiar nulitatea societății, sancțiunea cea mai gravă posibilă.
- **Verificarea și rezervarea efectivă a unei denumiri disponibile** este, însă, o procedură distinctă, reglementată azi de Legea nr. 265/2022 privind registrul comerțului (art. 48–51 pentru firmă, art. 50 pentru disponibilitate, caracter distinctiv și valabilitatea de o lună a dovezii). Legea nr. 26/1990, la care trimiteau reglementările mai vechi, a fost abrogată expres prin Legea nr. 265/2022 (art. 140 alin. (1) lit. a)); actul în vigoare se regăsește în corpusul de surse (anaf_surse/legea_265_2022.html).
- Textul disponibil confirmă contextul mai larg: **Legea nr. 265/2022 a reformat regimul registrului comerțului și a abrogat Legea nr. 26/1990**, iar Legea nr. 31/1990 a fost modificată succesiv — semn că regulile aplicabile astăzi la înmatriculare, inclusiv cele privind denumirea, s-au schimbat semnificativ față de forma inițială.

**Recomandare practică, dincolo de ce se poate confirma din surse:** verificarea disponibilității unei denumiri se face direct pe portalul Oficiului Național al Registrului Comerțului (recom.ro/onrc.ro), unde rezervarea denumirii e un pas formal, cu taxă proprie, anterior depunerii actului constitutiv.

## Ce se greșește în practică

- Se presupune că o denumire „similară", dar nu identică, cu una deja existentă e automat acceptată — criteriile de similitudine folosite de registrul comerțului sunt mai stricte decât o simplă comparație caracter cu caracter.
- Se redactează actul constitutiv cu o denumire nici măcar verificată preliminar, riscând respingerea cererii de înmatriculare și pierderea timpului investit în restul documentației.
- Se confundă rezervarea denumirii (pas administrativ la ONRC, anterior înființării) cu înregistrarea unei mărci (procedură complet separată, la OSIM) — o denumire de firmă disponibilă la ONRC nu garantează că nu încalcă o marcă înregistrată de altcineva.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu verifică disponibilitatea denumirilor de firmă** — nu a fost găsită nicio funcționalitate cu acest scop în `core/`, iar o astfel de verificare ar necesita, oricum, acces direct la baza de date a registrului comerțului. Aplicația preia denumirea firmei ca dată de identificare odată ce societatea e deja înmatriculată, pentru a fi folosită corect pe facturi și declarații.

[iConta.eu](/)
