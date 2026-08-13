---
title: Termenul de depunere a D101: 25 iunie, nu 25 martie
description: Termenul de depunere a declarației anuale de impozit pe profit este 25 iunie: pentru 2021-2025 prin OUG 153/2020, iar din 2026 permanent prin OUG 8/2026. De ce cifra din memorie e greșită.
published: 2026-08-12
modified: 2026-08-13
---

# Până când se depune D101 și de ce nu e 25 martie?

Cifra pe care majoritatea o ține minte pentru declarația anuală de impozit pe profit este 25 martie. Nu e cea care se aplică. Din 2021 încoace termenul e **25 iunie**, dar prin două mecanisme legale diferite: mai întâi o derogare temporară, apoi o modificare permanentă a Codului fiscal. Rezultatul e același pentru contribuabil; drumul până la el explică de ce circulă încă termenul greșit.

## Temeiul legal

::: ghid-temei
**Baza — art. 42 alin. (1) din Codul fiscal (Legea 227/2015).** Regula de fond pentru declarația anuală de impozit pe profit era depunerea și plata *„până la data de 25 martie inclusiv a anului următor"*, respectiv, pentru contribuabilii cu an fiscal modificat (art. 16 alin. (5)), până la data de 25 a celei de-a treia luni de la închiderea anului fiscal modificat.

**Anii fiscali 2021–2025 → 25 iunie. OUG nr. 153/2020**, Monitorul Oficial nr. 817 din 4 septembrie 2020.

Art. I alin. (13) lit. a): *„Pe perioada aplicării prevederilor prezentului articol, termenele pentru depunerea declarațiilor și pentru plata impozitului sunt următoarele: a) pentru contribuabilii plătitori de impozit pe profit, prin derogare de la prevederile art. 41 și 42 din Codul fiscal, termenul pentru depunerea declarației anuale privind impozitul pe profit și plata impozitului pe profit aferent anului fiscal respectiv este până la data de 25 iunie inclusiv a anului următor, iar pentru contribuabilii care intră sub incidența prevederilor art. 16 alin. (5) din Codul fiscal până la data de 25 a celei de-a șasea luni inclusiv de la închiderea anului fiscal modificat […]"*

Art. VI: *„Prevederile art. I intră în vigoare începând cu data de 1 ianuarie 2021 și se aplică pentru perioada 2021–2025."*

Derogarea este **generală** — privește toți plătitorii de impozit pe profit, nu doar anumite categorii.

**Anul fiscal 2026 și următorii → 25 iunie, permanent. OUG nr. 8/2026**, Monitorul Oficial nr. 147 din 25 februarie 2026. Art. 6 pct. 12 modifică **însuși art. 42 alin. (1) din Codul fiscal**, așezând termenul la 25 iunie, aplicabil începând cu declarația aferentă anului fiscal 2026.
:::

## Regula concretă

| An fiscal | Termen de depunere și plată | Temei |
|---|---|---|
| 2021 – 2025 | **25 iunie** a anului următor | OUG 153/2020, derogare de la art. 41–42 |
| 2026 și următorii | **25 iunie** a anului următor | OUG 8/2026, modifică art. 42 alin. (1) |
| (bază, neaplicată în intervalul de mai sus) | 25 martie a anului următor | art. 42 alin. (1), forma originară |

Pentru contribuabilii cu **an fiscal modificat**, termenul nu se citește pe calendarul obișnuit: e a șasea lună de la închiderea anului fiscal propriu.

Efectul practic: **25 iunie, fără întrerupere, din 2021 încoace**. Ce s-a schimbat de două ori e mecanismul — o derogare temporară pentru 2021–2025, apoi mutarea permanentă a regulii de bază din 2026. A existat o fereastră teoretică de „25 martie" pentru 2026, pe care OUG 8/2026 a închis-o înainte să se aplice.

## Ce cere validatorul instalat astăzi

Validatorul oficial ANAF, DUKIntegrator, verifică termenul și îl leagă de luna de închidere a anului fiscal.

Pentru anii 2021–2025 cere iunie — coincide cu OUG 153/2020, deci nicio surpriză.

Pentru anul fiscal 2026, versiunea instalată astăzi cere încă **martie** — termenul-bază din forma originară a art. 42, pentru că modificarea adusă de OUG 8/2026 nu a fost încă preluată în validator. Nu e un conflict între lege și validator, ci un decalaj de versiune. D101 pentru 2026 se depune în 2027; până atunci validatorul va fi actualizat.

Concret: dacă generezi astăzi o D101 pentru 2026 și validatorul îți cere martie, nu înseamnă că termenul legal e martie. Înseamnă că fișierul de validare nu e la zi.

## Un exemplu

::: ghid-exemplu
**Anul fiscal 2024.** O firmă plătitoare de impozit pe profit, cu an fiscal egal cu anul calendaristic, depune D101 pentru 2024 și plătește impozitul **până la 25 iunie 2025** — nu 25 martie. Temeiul: OUG 153/2020, care derogă de la art. 42 pentru tot intervalul 2021–2025. Validatorul acceptă iunie.

**Anul fiscal 2026.** Aceeași firmă va depune D101 pentru 2026 **până la 25 iunie 2027**, pe temeiul OUG 8/2026. Dacă între timp deschizi validatorul instalat și el îți cere martie pentru 2026, e o chestiune de versiune, nu de drept. Depunerea o faci la termenul legal, cu validatorul actualizat de la ANAF.

**An fiscal modificat.** O firmă cu exercițiul închis la 30 septembrie depune D101 până la 25 a celei de-a șasea luni de la închidere — adică 25 martie al anului următor. Aceeași regulă, alt calendar.
:::

## Ce se greșește în practică

- **Se folosește „25 martie" din memorie.** E termenul-bază, dar a fost înlocuit cu 25 iunie pentru 2021–2025 prin derogare și, din 2026, prin modificarea chiar a art. 42.
- **Se crede că derogarea privea doar grupurile fiscale.** Textul se referă la „contribuabilii plătitori de impozit pe profit" în general.
- **Se ia respingerea validatorului drept lege.** Pentru 2026, validatorul instalat astăzi cere martie. E decalaj de versiune, nu termen legal.
- **Se uită anul fiscal modificat.** Dacă exercițiul nu coincide cu anul calendaristic, termenul se citește de la închiderea lui, nu pe calendar.

## Ce face iConta.eu

D101 se calculează din balanță — cu pierderea reportată și comparația cu impozitul minim — și se generează ca fișier XML validat pe validatorul oficial ANAF.

Scadența e urmărită **pe anul fiscal**: 25 iunie pentru 2021–2025 și tot 25 iunie din 2026 încolo, inclusiv pentru firmele cu an fiscal modificat, unde se calculează de la închiderea exercițiului propriu. Data pe care o vezi în aplicație e cea legală, nu cea din memoria unui șablon.

Depunerea o faci din SPV.

Vezi și: [regimul microîntreprinderii în 2026](/ghid/impozit-micro-2026), pentru firmele care trec la impozit pe profit în cursul anului.

[iConta.eu](/)
