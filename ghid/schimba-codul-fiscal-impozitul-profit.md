---
title: "Ce se schimbă în Codul fiscal la impozitul pe profit în 2026"
description: "Pentru anul fiscal 2026, cota impozitului minim pe cifra de afaceri (IMCA) scade la 0,5%, printr-o modificare recentă a Codului fiscal aplicabilă doar acestui an fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce se schimbă în Codul fiscal la impozitul pe profit în 2026

Printre modificările aduse Codului fiscal pentru 2026, una directă și cuantificabilă privește impozitul minim pe cifra de afaceri (IMCA), mecanismul care garantează un nivel minim de impozitare pentru contribuabilii mari, indiferent de rezultatul fiscal calculat clasic: cota din formulă scade, dar doar pentru acest an fiscal.

## Temeiul legal

::: ghid-temei
„(16) Pentru anul fiscal 2026/anul fiscal modificat care începe în anul 2026, cota de impozit din cadrul formulei prevăzute la alin. (3) este 0,5%. (17) Prevederile prezentului articol se aplică până la data de 31 decembrie 2026 inclusiv/ultima zi a anului fiscal modificat care se încheie în anul 2027 inclusiv."
— Legea nr. 227/2015 (Codul fiscal), art. 18^1 alin. (16)-(17), introduse prin OUG nr. 89/2025 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Cota folosită în formula impozitului minim pe cifra de afaceri (IMCA), aplicabilă contribuabililor care intră sub incidența acestui mecanism, este **0,5% pentru anul fiscal 2026** (respectiv pentru anul fiscal modificat care începe în 2026) — o valoare specifică acestui an, introdusă expres prin OUG nr. 89/2025.
- Modificarea e **temporară**, prevederile alin. (16)-(17) aplicându-se doar până la 31 decembrie 2026 inclusiv (sau ultima zi a anului fiscal modificat care se încheie în 2027) — nu o schimbare permanentă a formulei IMCA.
- Restul mecanismului IMCA (indicatorii I și A din formulă, condiția de păstrare a activelor scăzute din imobilizări timp de jumătate din durata de utilizare, dar nu mai mult de 5 ani) rămâne structural neschimbat, doar cota din alin. (16) fiind specifică lui 2026.
- Alte modificări intrate în vigoare pentru 2026 (de exemplu la art. 47 din Titlul III, privind pragul de venituri pentru microîntreprinderi, coborât la 100.000 euro prin OUG nr. 8/2026) afectează firmele care ar putea trece din impozit pe profit în regim micro, sau invers, deci merită verificate coroborat.

## Ce se greșește în practică

- Se aplică vechea cotă a formulei IMCA (dinaintea introducerii alin. (16)), pentru că modificarea a fost publicată aproape de finalul anului 2025 și poate fi ratată la actualizarea proceselor interne.
- Se presupune că modificarea de cotă e permanentă, deși legea o limitează expres la anul fiscal 2026/anul fiscal modificat corespunzător.
- Se ignoră legătura dintre schimbarea pragului de venituri pentru microîntreprinderi (art. 47) și eventuala trecere a unor firme de la impozit pe profit (cu formula IMCA) la impozit pe veniturile microîntreprinderilor, sau invers.

## Ce face iConta.eu

La data acestui ghid, modulul de impozit pe profit din iConta.eu (`core/d101.py`) implementează explicit cota redusă de IMCA pentru anul fiscal 2026: funcția `impozit_minim_cifra_afaceri` folosește o listă de cote versionate pe an (`_VARIANTE_COTA_IMCA`), cu 1% până în 2025 și 0,5% începând cu 1 ianuarie 2026, temei citat direct în cod (OUG nr. 89/2025). Aplicația calculează și pragul de eligibilitate pentru IMCA (cifră de afaceri peste 50.000.000 euro, conform art. 18^1 alin. (1)) prin funcția `datoreaza_imca`, deci firmele care intră sub incidența acestui mecanism primesc automat cota corectă pentru 2026 la generarea D101.

[iConta.eu](/)
