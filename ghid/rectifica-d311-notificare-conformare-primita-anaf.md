---
title: "Cum se rectifică D311 după o notificare de conformare primită de la ANAF?"
description: "Depui un D311 nou, pe același format, cu bifa de rectificare ca urmare a notificării de conformare și cu toate rubricile completate cu datele corecte, nu doar cu diferențele."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# Cum se rectifică D311 după o notificare de conformare primită de la ANAF?

Rectificarea se face printr-un **D311 nou, pe același format**, în care bifezi căsuța „Declarație rectificativă ca urmare a unei notificări de conformare". În declarația rectificativă completezi **toate rubricile cu datele valabile** la data depunerii, inclusiv cele care erau corecte. Nu declari doar diferența.

Contează și termenul. Notificarea de conformare îți dă 30 de zile de la comunicare ca să corectezi declarațiile. În acest interval, organul de inspecție nu face demersuri pentru a te selecta la inspecție.

## Temeiul legal

::: ghid-temei
„Declarația depusă inițial se rectifică prin depunerea unei noi declarații, pe același format, bifând căsuța corespunzătoare de pe formular. În declarația rectificativă se completează toate rubricile formularului cu datele valabile la momentul declarării, indiferent dacă acestea au mai fost declarate."
— OPANAF nr. 188/2018, anexa nr. 2, cap. I „Felul declarației" (sursă: anaf_surse/ordin_188_2018.html)

„Se completează câte o declarație rectificativă pentru fiecare perioadă de raportare pentru care se operează rectificări."
— OPANAF nr. 188/2018, anexa nr. 2, cap. I „Felul declarației" (sursă: anaf_surse/ordin_188_2018.html)

„Căsuța «Declarație rectificativă ca urmare a unei notificări de conformare» se bifează în situația în care rectificarea datelor declarate anterior se efectuează ca urmare a unei notificări de conformare"
— OPANAF nr. 188/2018, anexa nr. 2, cap. I „Felul declarației" (sursă: anaf_surse/ordin_188_2018.html)
:::

::: ghid-temei
„(2) Prin notificare se comunică contribuabilului/plătitorului că în termen de 30 de zile de la data comunicării notificării are posibilitatea să depună sau să corecteze declarațiile fiscale. Până la expirarea acestui termen, organul de inspecție fiscală nu întreprinde nicio acțiune în vederea selectării pentru efectuarea inspecției fiscale."
— Codul de procedură fiscală (Legea 207/2015), art. 121^1 alin. (2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Pașii:

- **Citește riscurile din notificare.** Notificarea descrie riscurile fiscale identificate, ca să îți reanalizezi situația și, după caz, să depui sau să corectezi declarațiile (art. 121^1 alin. (1)).
- **Bifează căsuța potrivită.** Formularul are două căsuțe de rectificare: „Declarație rectificativă" și „Declarație rectificativă ca urmare a unei notificări de conformare". A doua a fost introdusă în anexă prin OPANAF nr. 779/2024, aplicabil din 22 aprilie 2024. Dacă rectifici la cererea din notificare, o bifezi pe aceasta.
- **Completezi totul din nou.** Datele de identificare, data anulării codului, motivul anulării și toate bazele și sumele de TVA se trec cu valorile corecte, chiar dacă nu s-au schimbat.
- **O rectificativă pentru fiecare lună.** Dacă notificarea privește trei perioade de raportare, depui trei declarații rectificative.
- **Plătești diferența.** Rectificativa arată suma corectă, iar diferența față de declarația inițială se plătește.

Ce nu rezolvă rectificarea:

- **Selecția pentru inspecție rămâne posibilă.** Corectarea declarațiilor nu împiedică selectarea pentru inspecție, dar aceasta poate avea loc numai după termenul de 30 de zile (art. 121^1 alin. (3)).
- **Riscurile neremediate au consecințe.** Contribuabilii cu risc fiscal ridicat care nu remediază riscurile notificate sunt supuși obligatoriu inspecției fiscale sau verificării documentare (art. 121^1 alin. (4)).
- **Rectificarea din timpul inspecției nu contează.** Declarația depusă sau corectată în timpul inspecției, pentru perioadele verificate, nu este luată în considerare (art. 105 alin. (8)).

::: ghid-exemplu
SC Exemplu SRL a avut codul de TVA anulat din oficiu. Pentru noiembrie 2025 a depus D311 cu baza de 40.000 lei și TVA de 8.400 lei. Pe 10 martie 2026 primește o notificare de conformare: în acea lună a mai facturat 15.000 lei, nedeclarați.

Rectificativa pentru noiembrie 2025, cu căsuța de notificare bifată, conține:

- baza: 40.000 + 15.000 = 55.000 lei;
- TVA de plată: 55.000 × 21% = 11.550 lei.

Diferența de plată este 11.550 − 8.400 = 3.150 lei. Termenul de 30 de zile se calculează de la data comunicării notificării.
:::

## Ce se greșește în practică

- În rectificativă se trece doar diferența de 15.000 lei, nu baza totală corectă.
- Se bifează căsuța „Declarație rectificativă" simplă, deși rectificarea vine din notificare.
- Se depune o singură rectificativă pentru mai multe luni.
- Corectarea se amână până după cele 30 de zile, când inspecția poate începe, iar o corecție depusă în timpul inspecției nu mai e luată în considerare.

## Ce face iConta.eu

În iConta.eu, formularul D311 are bifa „Declarație rectificativă". Contabilul reface situația din perioada respectivă cu valorile corecte, iar aplicația recalculează totalul și validează XML-ul pe validatorul oficial ANAF. Formularul din aplicație nu are căsuța distinctă pentru notificarea de conformare, iar structura folosită de aplicație nu are un câmp pentru ea. O rectificativă care trebuie să poarte această mențiune se întocmește în afara aplicației. Aplicația nu citește notificările din SPV, iar depunerea o face contabilul.

[iConta.eu](/)
