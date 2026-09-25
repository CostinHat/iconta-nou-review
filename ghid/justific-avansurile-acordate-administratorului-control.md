---
title: "Cum justific avansurile acordate administratorului la control?"
description: "Regula de decontare a avansurilor spre decontare conform normelor financiar-contabile și plafonul zilnic din Legea 70/2015, aplicate sumelor acordate administratorului."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum justific avansurile acordate administratorului la control?

Un avans acordat administratorului nu rămâne „bani ai firmei ieșiți din casă" până la proba contrarie — el trebuie decontat cu documente justificative pentru fiecare leu cheltuit, iar tot ce nu se decontează se reclasifică drept creanță, nu dispare din evidență.

## Temeiul legal

::: ghid-temei
„2. Documentele justificative trebuie să cuprindă următoarele elemente principale: [...] conținutul operațiunii economico-financiare și, atunci când este necesar, temeiul legal al efectuării acesteia; [...] datele cantitative și valorice aferente operațiunii economico-financiare efectuate, după caz; [...]"
— OMFP 2634/2015, Anexa 1 (Norme generale), pct. 2 (sursă: anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt)

„plăți din avansuri spre decontare, în limita unui plafon zilnic de 5.000 lei, stabilit pentru fiecare persoană care a primit avansuri spre decontare.
[...]
La data acordării avansurilor spre decontare, sumele aferente intră în calculul plafonului zilnic prevăzut la alin. (1) lit. c) sau d), după caz."
— Legea 70/2015, art. 3 alin. (1) lit. e) și alin. (4) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Mecanismul de justificare, pas cu pas:

- **Acordarea avansului** e o operațiune de trezorerie (contul 542), nu o cheltuială — el nu afectează rezultatul fiscal la momentul acordării, ci doar la decontare, când sumele sunt susținute de documente.
- **Fiecare decontare** trebuie să aibă la bază documente justificative complete, conform pct. 2 din normele generale — conținutul operațiunii, temeiul, datele cantitative/valorice. Un avans decontat „în bloc", fără documente pentru fiecare cheltuială, nu respectă această cerință.
- **Plafonul zilnic de 5.000 lei** pentru plățile din avansuri spre decontare (art. 3 alin. (1) lit. e)) se calculează per persoană — deci per administrator, dacă sunt mai mulți. E un plafon distinct de cel pentru plățile obișnuite în numerar către persoane (lit. c)) sau către cash and carry (lit. d)): potrivit alin. (4), suma acordată ca avans intră, chiar de la data acordării, în calculul plafonului de la lit. c) sau d) — nu în plafonul de la lit. e), care privește separat sumele plătite ulterior din avansul respectiv, la decontare.
- **Suma nedecontată** la o dată de referință (de exemplu, la închiderea exercițiului financiar) nu rămâne „în aer" — ea trebuie reclasificată, de regulă la o creanță asupra administratorului (dacă e vorba de o sumă personală, nedecontată cu documente de firmă), pentru a reflecta corect realitatea economică a operațiunii.

## Ce se greșește în practică

- Se acordă avansuri repetate administratorului fără decontarea celor anterioare, ceea ce lasă solduri mari, nejustificate, ale contului de avansuri de trezorerie — vizibile imediat la un control.
- Se decontează avansul cu documente incomplete (bonuri fiscale fără detaliere, facturi fără legătură clară cu activitatea firmei), ceea ce nu satisface cerințele de la pct. 2 al normelor generale.
- Se depășește plafonul zilnic de 5.000 lei per persoană fără să se observe, pentru că suma se calculează cumulat pe zi, nu per operațiune individuală de acordare.

## Ce face iConta.eu

Modulul de casierie al iConta.eu (`core/casa.py`) tratează explicit acest flux: `avans_acordare` înregistrează nota de acordare (cont 542), `avans_deconteaza` generează notele de decontare pe baza liniilor introduse (cu TVA aferent, dacă e cazul) și calculează suma rămasă de restituit, iar `reclasificare_bilant` mută soldurile de avansuri nedecontate la contul corespunzător (4282 pentru avansuri personale, 461 pentru altele), cu temeiul citat explicit în cod (OMFP 1802/2014 pct. 302/306). Funcția `verifica_plafon` din același modul semnalează, ca avertisment, depășirea plafonului zilnic de 5.000 lei per persoană la avansurile din ziua respectivă. Documentele justificative propriu-zise pentru fiecare cheltuială decontată rămân, evident, în afara aplicației — introduse și păstrate de contabil.

[iConta.eu](/)
