---
title: "Cum corectez o declarație OSS depusă greșit"
description: "Mecanismul prin care se corectează o eroare dintr-o declarație depusă în regimul special OSS/One Stop Shop, conform Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum corectez o declarație OSS depusă greșit

Firmele înregistrate în regimul special One Stop Shop (OSS) raportează, printr-o singură declarație depusă în România (ca stat membru de identificare), TVA-ul datorat în fiecare stat membru de consum pentru vânzările la distanță sau prestările de servicii către persoane neimpozabile din UE. O eroare într-o astfel de declarație nu se corectează prin redepunerea declarației inițiale, ci printr-un mecanism separat de corecție, aplicat într-o declarație ulterioară.

## Temeiul legal

::: ghid-temei
„Regimul special pentru vânzările intracomunitare de bunuri la distanță, pentru livrările de bunuri interne efectuate de interfețele electronice care facilitează aceste livrări și pentru serviciile prestate de persoane impozabile stabilite în Uniunea Europeană, dar nu în statul membru de consum"
— Codul fiscal (Legea 227/2015), secțiunea dedicată regimului special UE (OSS), art. 315 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

**Limitare de temei:** sursele disponibile conțin textul Codului fiscal (art. 314 pentru regimul non-UE, art. 315 pentru regimul UE, art. 315^2 pentru regimul de import/IOSS) și normele metodologice aferente, dar nu conțin ordinul ANAF de aprobare a modelului declarației D398 — acesta nu a fost identificat printre sursele verificate, structura formularului fiind stabilită, în practică, prin validatorul oficial ANAF, nu printr-un act normativ distinct publicat separat.

Ce rezultă, totuși, cu certitudine din structura regimului OSS (reflectată și în validatorul oficial al declarației):

- Corecția unei erori dintr-o perioadă anterioară **nu se face prin redepunerea declarației respective**, ci printr-o secțiune dedicată de corecție, în cadrul unei declarații ulterioare, care indică explicit **statul membru de consum vizat**, **perioada de raportare corectată** și **anul** la care se referă eroarea, alături de suma corecției (pozitivă sau negativă).
- Fiecare corecție trebuie să fie unică pe combinația (perioadă, an, stat membru) — nu se pot introduce două corecții separate pentru aceeași perioadă și același stat, într-o singură declarație.
- Suma corecției nu poate fi zero — o corecție presupune, prin definiție, o modificare efectivă a sumei raportate anterior pentru statul membru respectiv.
- O declarație care conține doar corecții, fără operațiuni curente, nu este considerată o declarație „fără activitate" (nil), pentru că totalul de plată rezultă din corecțiile aplicate.

## Ce se greșește în practică

- Se încearcă redepunerea declarației OSS pentru perioada greșită, ca și cum ar fi o declarație obișnuită la ANAF care poate fi rectificată direct — regimul OSS funcționează diferit, prin corecții aplicate în declarațiile ulterioare.
- Se introduc două corecții pentru aceeași perioadă și același stat membru în cadrul aceleiași declarații, ceea ce contravine regulii de unicitate a combinației (perioadă, an, stat).
- Se omite precizarea exactă a perioadei și a anului la care se referă eroarea inițială, informații fără de care corecția nu poate fi asociată corect cu declarația greșită.

## Ce face iConta.eu

iConta.eu generează declarația D398 (regimul special OSS) pe baza datelor introduse manual de utilizator — aplicația nu urmărește automat operațiunile OSS pe stat de consum și cotă străină, acestea fiind introduse direct de contabil. Pentru corecții, aplicația oferă o secțiune dedicată (stat membru, perioadă, an, sumă de corecție), cu verificări care resping o corecție cu suma zero sau o combinație (perioadă, an, stat) duplicată în aceeași declarație, în linie cu regulile validatorului oficial ANAF.

[iConta.eu](/)
