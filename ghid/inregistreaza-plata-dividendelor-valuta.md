---
title: "Cum se înregistrează plata dividendelor în valută?"
description: "Cursul valutar folosit pentru înregistrarea plății dividendelor în valută și impozitul pe dividende aplicabil, conform reglementărilor contabile și Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se înregistrează plata dividendelor în valută?

Nu există o regulă contabilă separată, dedicată strict dividendelor plătite în valută — se aplică regula generală de conversie a operațiunilor în valută, la cursul BNR din ziua efectuării plății, combinată cu regulile obișnuite de impozitare a dividendelor.

## Temeiul legal

::: ghid-temei
„(1) Operațiunile privind încasările și plățile în valută se înregistrează în contabilitate la cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunii respective. În vederea asigurării unui tratament contabil unitar, prin curs de schimb de la data efectuării operațiunii se înțelege cursul de schimb al pieței valutare, comunicat de Banca Națională a României, din ultima zi bancară anterioară operațiunii, disponibil ca informație la momentul efectuării operațiunii (încasare, plată, emitere de documente)."
— OMFP 1802/2014, pct. 304 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)

„(2) Impozitul pe dividende se stabilește prin aplicarea unei cote de impozit de 16% asupra dividendului brut plătit unei persoane juridice române. Impozitul pe dividende se declară și se plătește la bugetul de stat, până la data de 25 inclusiv a lunii următoare celei în care se plătește dividendul."
— Legea 227/2015, art. 43 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Pași concreți pentru înregistrarea unei plăți de dividende în valută:

- Datoria către asociat/acționar (contul 457) se stabilește inițial în lei, la valoarea dividendului aprobat prin hotărârea AGA — chiar dacă plata efectivă se face ulterior în valută.
- La data plății efective în valută, suma se convertește la **cursul BNR din ultima zi bancară anterioară plății** (pct. 304 alin. (1)) — nu la cursul din ziua aprobării dividendului și nu la cursul băncii comerciale prin care se face transferul.
- Diferența dintre cursul de la data înregistrării inițiale a datoriei și cursul de la data plății generează venituri sau cheltuieli din diferențe de curs valutar, recunoscute în luna în care are loc decontarea.
- Impozitul pe dividende (16% pentru dividende distribuite din 2026, conform art. 43 alin. (2)) se calculează asupra dividendului brut, indiferent de moneda de plată — conversia în lei pentru scopuri de declarare se face tot la cursul BNR de la data operațiunii relevante.

## Ce se greșește în practică

- Se folosește cursul băncii comerciale prin care se efectuează transferul valutar, în loc de cursul BNR din ultima zi bancară anterioară operațiunii.
- Se omite recunoașterea diferenței de curs valutar dintre data aprobării dividendului (înregistrarea datoriei) și data plății efective, atunci când cele două momente sunt în luni diferite.
- Se calculează impozitul pe dividende direct în valută, fără conversia corectă în lei la cursul de la data relevantă pentru declarare.

## Ce face iConta.eu

iConta.eu calculează impozitul pe dividende pe baza mișcărilor contului 457 (distribuiri și plăți), atribuind cota corectă de impozit fiecărei tranșe plătite în funcție de data distribuirii aferente — inclusiv pentru distribuții din 2025 care rămân la cota veche de 10% conform regulilor tranzitorii. La data acestui ghid, conversia valutară a plăților de dividende (cursul BNR de la data plății) se introduce manual de contabil, ca la orice altă operațiune în valută.

[iConta.eu](/)
