---
title: "Micro și scorul de credit al firmei: se schimbă ceva"
description: "De ce statutul de microîntreprindere nu are, prin el însuși, niciun efect legal asupra scorului de credit bancar al firmei."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Micro și scorul de credit al firmei: se schimbă ceva

Întrebarea ascunde de fapt două noțiuni diferite pe care merită să le despărțim clar: „creditul fiscal" (o sumă pe care legea o recunoaște ca reducere de impozit, cum e cazul creditului de sponsorizare) și „scorul de credit" (un indicator de risc calculat de bănci sau de societăți de rating pentru a decide dacă și cu ce dobândă îți acordă un împrumut). Statutul de microîntreprindere ține de prima categorie — e o formă de impozitare reglementată de Codul fiscal — dar nu are, prin el însuși, valoare juridică pentru a doua.

## Temeiul legal

::: ghid-temei
„În sensul prezentului titlu, o microîntreprindere este o persoană juridică română care îndeplinește cumulativ următoarele condiții, la data de 31 decembrie a anului fiscal precedent: [...] c) a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile; [...] d) capitalul social al acesteia este deținut de persoane, altele decât statul și unitățile administrativ-teritoriale; [...] e) nu se află în dizolvare, urmată de lichidare, înregistrată în registrul comerțului sau la instanțele judecătorești, potrivit legii. [...] g) are cel puțin un salariat, cu excepția situației prevăzute la art. 48 alin. (3); h) are asociați/acționari care dețin, în mod direct sau indirect, peste 25% din valoarea/numărul titlurilor de participare sau al drepturilor de vot și este singura persoană juridică stabilită de către asociați/acționari să aplice prevederile prezentului titlu; i) a depus în termen situațiile financiare anuale, dacă are această obligație potrivit legii."
— Codul fiscal (Legea 227/2015), art. 47 alin. (1), Titlul III (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Condițiile de mai sus sunt exclusiv fiscale, nu au legătură cu bonitatea sau riscul de nerambursare pe care îl evaluează o bancă:

- Pragul de **100.000 euro venituri anuale** (litera c, în forma actuală, în vigoare din 25.02.2026, OUG 8/2026) stabilește doar dacă firma plătește impozit pe veniturile microîntreprinderilor sau impozit pe profit — nu are legătură cu solvabilitatea.
- Condițiile de la literele d), e), g), h) și i) (structura acționariatului, lipsa dizolvării, cel puțin un salariat, depunerea situațiilor financiare la timp) sunt criterii de *încadrare fiscală*, nu criterii de risc de credit.
- Legea nu prevede niciun mecanism prin care trecerea de la impozit pe profit la impozit pe veniturile microîntreprinderilor (sau invers) ar „recalcula" automat un scor de credit — acesta este stabilit exclusiv de fiecare bancă, pe baza propriei metodologii interne de risc (de regulă aliniată la normele prudențiale BNR), nu de Codul fiscal.

## Ce se greșește în practică

- Se confundă „credit fiscal" (o reducere de impozit prevăzută de lege, cum e creditul de sponsorizare de la art. 25 din Codul fiscal) cu „scor de credit" (un indicator bancar de risc) — sunt noțiuni complet diferite, reglementate de acte diferite.
- Se presupune că trecerea la impozitare micro „arată mai bine" în fața băncii pentru că impozitul plătit e mai mic — de fapt, băncile se uită la cifra de afaceri, marja, fluxul de numerar și gradul de îndatorare din situațiile financiare, nu la regimul de impozitare ales.
- Se ignoră faptul că neîndeplinirea condițiilor de la art. 47 (de exemplu, nedepunerea la timp a situațiilor financiare, litera i) poate scoate firma din regimul micro *din oficiu*, ceea ce schimbă impozitul datorat și, indirect, profitul net raportat — un element pe care o bancă îl poate lua în calcul, dar nu ca literă de lege, ci ca parte din analiza sa financiară.

## Ce face iConta.eu

Acest subiect nu corespunde funcționalității F086 (sponsorizări și credit fiscal) cercetate pentru acest ghid și nici, în general, unei funcționalități fiscale declarative — ține de analiza de risc bancar, care e din afara sferei de conformitate fiscală pe care o acoperă iConta.eu. Cu certitudine, aplicația **nu calculează și nu afișează un „scor de credit"** al firmei — un asemenea indicator ține de metodologia internă a fiecărei bănci, nu de o obligație fiscală pe care un program de contabilitate ar avea motiv s-o automatizeze. Ce poate corect confirma acest ghid, pe baza cercetării F086 verificate direct în cod, este mecanismul separat, real, de credit fiscal legat de statutul de microîntreprindere: facilitatea de sponsorizare cu credit fiscal pentru microîntreprinderi (fostul art. 56 alin. (1^1) din Codul fiscal) a fost **eliminată prin OUG 115/2023**, ultimul an fiscal de aplicare fiind 2023 — deci, din 2024, o microîntreprindere care sponsorizează nu mai are credit fiscal, sponsorizarea rămânând o simplă cheltuială. Dincolo de acest punct verificat, nu avem în cercetarea de față o confirmare directă a vreunei alte funcții din iConta.eu legate de „scorul de credit", motiv pentru care acest ghid nu face afirmații neconfirmate despre asta.

[iConta.eu](/)
