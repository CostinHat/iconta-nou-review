---
title: Termenul de depunere a D101: până când se depune și de ce diferă de la un an la altul
description: Până când se depune declarația anuală de impozit pe profit (D101) și de ce termenul diferă de la un an la altul — 25 iunie pentru 2021–2025 (OUG 153/2020) și 25 iunie permanent de la 2026 (OUG 8/2026), cu temeiul legal verbatim.
published: 2026-08-12
modified: 2026-08-12
---
# Până când se depune D101 și de ce diferă termenul de la un an la altul?

Termenul de depunere a declarației anuale privind impozitul pe profit (D101) pare simplu — „25 a lunii a treia a anului următor” — dar pentru anii fiscali din urmă s-a mutat de două ori, iar cifra pe care mulți o țin minte, 25 martie, nu este cea care se aplică. Întrebarea nu e doar „când”, ci „de ce nu e același termen în fiecare an”: baza din Codul fiscal spune o dată, o ordonanță de urgență a mutat-o pentru un întreg interval de ani, iar o a doua ordonanță a mutat-o din nou, de data asta permanent. Mai jos e termenul pe fiecare an, cu temeiul legal cuvânt cu cuvânt, plus ce cere astăzi validatorul oficial ANAF — ca să nu te sperii când DUKIntegrator îți respinge o dată pe care o credeai corectă.

## Temeiul legal

::: ghid-temei
**Baza — art. 42 alin. (1) din Codul fiscal (Legea 227/2015).** Regula de fond pentru declarația anuală de impozit pe profit este depunerea și plata „**până la data de 25 martie inclusiv a anului următor**”, respectiv, pentru contribuabilii cu an fiscal modificat (art. 16 alin. (5) CF), până la data de 25 a celei de-a treia luni inclusiv de la închiderea anului fiscal modificat. Aceasta este cifra „din memorie” — dar pentru anii de mai jos a fost înlocuită prin derogare.

**Anii fiscali 2021–2025 → 25 iunie — OUG nr. 153/2020 (Monitorul Oficial nr. 817 din 4 septembrie 2020).** Art. I alin. (13) lit. a) VERBATIM: „*Pe perioada aplicării prevederilor prezentului articol, termenele pentru depunerea declarațiilor și pentru plata impozitului sunt următoarele: a) pentru contribuabilii plătitori de impozit pe profit, **prin derogare de la prevederile art. 41 și 42 din Codul fiscal**, termenul pentru depunerea declarației anuale privind impozitul pe profit și plata impozitului pe profit aferent anului fiscal respectiv este **până la data de 25 iunie inclusiv a anului următor**, iar pentru contribuabilii care intră sub incidența prevederilor art. 16 alin. (5) din Codul fiscal până la data de 25 a celei de-a șasea luni inclusiv de la închiderea anului fiscal modificat (…)*”. Art. VI VERBATIM: „*Prevederile art. I intră în vigoare începând cu data de 1 ianuarie 2021 și se aplică pentru perioada 2021–2025*”. Derogarea este **generală** — privește toți plătitorii de impozit pe profit, nu doar grupurile fiscale.

**Anul fiscal 2026 și următorii → 25 iunie (permanent) — OUG nr. 8/2026 (Monitorul Oficial nr. 147 din 25 februarie 2026).** Schema OUG 153/2020 s-a încheiat cu anul 2025, iar pentru 2026 termenul ar fi revenit la baza de 25 martie din art. 42 alin. (1). Înainte ca acest lucru să se întâmple, **art. 6 pct. 12 din OUG nr. 8/2026 a modificat chiar art. 42 alin. (1) din Codul fiscal, așezând termenul la 25 iunie**, aplicabil începând cu declarația aferentă anului fiscal 2026. Practic, termenul de 25 iunie devine regula permanentă din 2026 încolo — de data aceasta din corpul Codului fiscal, nu printr-o derogare temporară.
:::

Nu există niciun conflict între lege și validatorul ANAF: termenul de 25 iunie pentru 2021–2025 vine dintr-o derogare pe care prima verificare o ratase; codul iConta.eu urmează validatorul și este, pe ambele ramuri, corect legal.

## Regula concretă

Termenul pe an fiscal, pentru contribuabilii cu an fiscal = anul calendaristic:

| An fiscal | Termen depunere D101 și plată | Temei |
|---|---|---|
| 2021 – 2025 | **25 iunie** a anului următor | OUG 153/2020, art. I alin. (13) lit. a) — derogare de la art. 41–42 CF |
| 2026 și următorii | **25 iunie** a anului următor | OUG 8/2026, art. 6 pct. 12 — modifică art. 42 alin. (1) CF |
| (bază, neaplicată în intervalul de mai sus) | 25 martie a anului următor | art. 42 alin. (1) CF (Legea 227/2015), forma originară |

Pentru contribuabilii cu **an fiscal modificat** (art. 16 alin. (5) CF), termenul se citește de la închiderea anului fiscal modificat: 25 a celei de-a șasea luni pentru 2021–2025 (OUG 153/2020) și, prin regula de fond mutată la iunie, tot a șasea lună pentru 2026 încolo.

Cu alte cuvinte: efectul pentru contribuabil este 25 iunie fără întrerupere din 2021. Ce s-a mutat de două ori este **mecanismul legal** — mai întâi o derogare temporară pentru 2021–2025, apoi o modificare permanentă a bazei din 2026 —, cu o fereastră teoretică de „25 martie” pentru 2026 pe care OUG 8/2026 a închis-o înainte să se aplice.

## Ce cere validatorul instalat astăzi

Validatorul oficial ANAF, **DUKIntegrator**, verifică termenul prin câmpul `Data_S` și îl leagă de luna de închidere a anului fiscal (LL):

::: ghid-semafor
verde: An fiscal 2021–2025 (Data_S 2022–2025) — validatorul cere LL+6, adică iunie (regula R17). Coincide cu OUG 153/2020. Aici nu ai surprize.
galben: An fiscal 2026 (Data_S 2026) — validatorul instalat cere încă LL+3, adică martie (regula R17.1). Este termenul-bază din art. 42 alin. (1), pe care jar-ul DUK nu l-a actualizat încă la 25 iunie conform OUG 8/2026.
gri: D101 pentru anul fiscal 2026 se depune de-abia în 2027 — până atunci, validatorul va prelua modificarea și va cere 25 iunie. Verifică versiunea DUKIntegrator la momentul depunerii.
:::

Concret: dacă astăzi generezi și validezi o D101 pentru un an din 2022–2025 cu termenul iunie, validatorul o acceptă. Dacă încerci pe 2026, validatorul instalat astăzi îți va cere martie (nu iunie) — nu pentru că 25 iunie ar fi greșit legal, ci pentru că jar-ul încă nu a preluat OUG 8/2026. Depunerea reală pentru 2026 fiind în 2027, la acel moment validatorul va fi actualizat la iunie.

## Un exemplu

::: ghid-exemplu
**Anul fiscal 2024.** O firmă plătitoare de impozit pe profit, cu an fiscal = an calendaristic, depune D101 pentru 2024 și plătește impozitul aferent **până la 25 iunie 2025** — nu 25 martie. Temeiul este OUG 153/2020, care derogă de la art. 42 CF pentru tot intervalul 2021–2025. Validatorul DUKIntegrator acceptă iunie (R17).

**Anul fiscal 2026.** Aceeași firmă va depune D101 pentru 2026 **până la 25 iunie 2027**, pe temeiul OUG 8/2026 care a mutat permanent termenul din art. 42 alin. (1) la 25 iunie. Dacă, în cursul lui 2026 sau la începutul lui 2027, deschizi validatorul instalat și el îți cere martie pentru Data_S 2026, este pentru că versiunea de jar nu a preluat încă modificarea — nu pentru că termenul legal ar fi martie. Depunerea o faci la termenul legal, cu versiunea de validator actualizată de la ANAF.
:::

## Ce se greșește în practică

::: ghid-procedura
- **Folosești „25 martie” din memorie.** Este termenul-bază al art. 42 alin. (1), dar pentru 2021–2025 a fost înlocuit cu 25 iunie prin OUG 153/2020, iar din 2026 tot 25 iunie prin OUG 8/2026. Pentru acești ani, 25 martie nu se aplică.
- **Crezi că derogarea privește doar grupurile fiscale.** Art. I alin. (13) lit. a) din OUG 153/2020 se referă la „contribuabilii plătitori de impozit pe profit” în general — derogarea este generală, nu limitată la anumite categorii.
- **Te sperii când validatorul îți respinge o dată.** Pentru 2026, validatorul instalat astăzi cere martie (termenul-bază, R17.1), nu iunie; modificarea OUG 8/2026 va fi preluată de jar până la depunerea din 2027. Nu este un conflict între lege și validator — este un decalaj de versiune, care se închide singur când actualizezi DUKIntegrator.
- **Uiți anul fiscal modificat.** Dacă firma are an fiscal ≠ an calendaristic (art. 16 alin. (5) CF), termenul nu se citește pe 25 iunie calendaristic, ci de la închiderea anului fiscal modificat (a șasea lună).
:::

## Ce face iConta.eu

Declarația D101 din iConta.eu calculează impozitul pe profit anual din balanță (cu pierderea reportată și comparația cu IMCA) și generează XML-ul validat pe validatorul oficial ANAF (DUKIntegrator). Scadența de depunere este urmărită **pe anul fiscal**: pentru 2021–2025 termenul de 25 iunie (OUG 153/2020), iar pentru 2026 încolo tot 25 iunie (OUG 8/2026), astfel încât data pe care o vezi în aplicație să fie cea acceptată de validatorul actualizat. Depunerea o faci tu din SPV, la termenul legal de mai sus.

[Deschide-ți cont pe iConta.eu](/) și lasă calculul și scadența D101 pe temeiul legal verificat la sursă, nu pe cifra din memorie.
