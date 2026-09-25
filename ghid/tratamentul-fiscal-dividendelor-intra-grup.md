---
title: "Tratamentul fiscal al dividendelor intra-grup la impozitul pe profit"
description: "Scutirea de impozit pe dividende între societăți românești legate, condițiile de deținere minimă și perioadă, conform art. 43 alin. (4) din Codul fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Tratamentul fiscal al dividendelor intra-grup la impozitul pe profit

Dividendele plătite între două societăți românești din același grup pot scăpa de impozitul de 16% reținut la sursă, dacă se îndeplinesc simultan condițiile de deținere minimă și de formă juridică prevăzute de lege — altfel, se aplică regimul general.

## Temeiul legal

::: ghid-temei
„Prevederile prezentului articol nu se aplică în cazul dividendelor plătite de o persoană juridică română unei alte persoane juridice române, dacă, la data plății dividendelor, fiecare dintre aceste persoane îndeplinește cumulativ următoarele condiții: a) persoana juridică beneficiară a dividendelor: (i) deține minimum 10% din titlurile de participare ale persoanei juridice române care plătește dividendele, pe o perioadă de un an împlinit până la data plății acestora inclusiv; (ii) este constituită ca o «societate pe acțiuni», «societate în comandită pe acțiuni», «societate cu răspundere limitată» [...]; (iii) plătește, fără posibilitatea unei opțiuni sau exceptări, impozit pe profit sau orice alt impozit care substituie impozitul pe profit; b) persoana juridică care plătește dividendele: (i) este constituită ca [...]; (ii) plătește, fără posibilitatea unei opțiuni sau exceptări, impozit pe profit sau orice alt impozit care substituie impozitul pe profit."
— Legea 227/2015, art. 43 alin. (4) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Impozitul pe dividende se stabilește prin aplicarea unei cote de impozit de 16% asupra dividendului brut plătit unei persoane juridice române. Impozitul pe dividende se declară și se plătește la bugetul de stat, până la data de 25 inclusiv a lunii următoare celei în care se plătește dividendul."
— Legea 227/2015, art. 43 alin. (2), astfel cum a fost modificat prin Legea nr. 141/2025, art. II pct. 1, aplicabil dividendelor distribuite de la 01.01.2026 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Condițiile cumulative pentru scutire (art. 43 alin. 4) — deținere de minimum 10% din titlurile de participare, pe o perioadă neîntreruptă de cel puțin un an împlinit la data plății, ambele societăți fiind persoane juridice române cu formă juridică eligibilă și plătitoare de impozit pe profit fără posibilitatea unei exceptări. Dacă oricare dintre aceste condiții lipsește — de exemplu, participația e sub 10%, sau perioada de deținere e mai scurtă de un an, sau firma beneficiară e microîntreprindere (care nu „plătește impozit pe profit" în sensul textului) — regimul general se aplică: reținere de 16% la sursă, declarată și plătită de firma plătitoare de dividende până pe 25 ale lunii următoare plății.

## Ce se greșește în practică

- Se aplică scutirea intra-grup fără a verifica împlinirea perioadei de un an de deținere la data plății, aplicând-o pe baza deținerii viitoare sau planificate.
- Se confundă condiția de la art. 43 alin. (4) lit. a) pct. (iii) — „plătește impozit pe profit, fără opțiune sau exceptare" — cu simpla calitate de persoană juridică română; o microîntreprindere beneficiară a dividendelor nu îndeplinește automat această condiție.
- Se calculează impozitul cu cota veche (10%), aplicabilă doar dividendelor interimare distribuite în 2025 și nerecalculate, deși cota generală pentru dividendele distribuite din 2026 e 16%.

## Ce face iConta.eu

iConta.eu calculează impozitul reținut pe dividende (declarația D205) cu cota corectă în funcție de data efectivă a distribuirii, nu de anul plății — motorul de calcul atribuie plățile pe distribuiri (FIFO, pe dată), astfel încât o distribuire interimară din 2025 rămâne la 10% chiar dacă se plătește ulterior în 2026, conform Legii 141/2025. Generarea automată de beneficiari D205 pornește din tabelul asociați (cotă de participare + CNP), gândit pentru asociați persoane fizice — nu identifică sau nu tratează distinct un beneficiar persoană juridică din alt grup. Aplicația nu verifică automat condițiile de scutire intra-grup de la art. 43 alin. (4) (procentul de deținere, perioada de un an, forma juridică a ambelor părți): pentru un beneficiar scutit, contabilul trebuie să suprascrie integral lista de beneficiari generată automat, prin parametrul manual al generării D205, introducând el însuși baza și impozitul (0, dacă e cazul) — aplicația nu calculează ea scutirea, doar acceptă valorile introduse manual.

[iConta.eu](/)
