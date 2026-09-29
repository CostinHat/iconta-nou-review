---
title: "De la ce dată începe perioada impozabilă a unei microîntreprinderi nou-înființate?"
description: "De la data înregistrării în registrul comerțului (sau în registrul autorității competente). Anul fiscal al primului an e doar perioada în care firma a existat."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# De la ce dată începe perioada impozabilă a unei microîntreprinderi nou-înființate?

Perioada impozabilă începe la data înregistrării firmei în registrul comerțului. Pentru entitățile care nu se înregistrează acolo, data este cea a înregistrării în registrul ținut de instanță sau de altă autoritate competentă. Nu contează data semnării actului constitutiv, a primei facturi sau a deschiderii contului bancar.

Pentru primul an, anul fiscal al microîntreprinderii nu e anul calendaristic întreg. El durează din ziua înregistrării până la 31 decembrie. Primul trimestru declarat în D100 este trimestrul în care cade data înregistrării, calculat de la acea dată.

## Temeiul legal

::: ghid-temei
„(1) În cazul înființării unei microîntreprinderi într-un an fiscal, perioada impozabilă începe: a) de la data înregistrării acesteia la registrul comerțului, dacă are această obligație; [...] b) de la data înregistrării în registrul ținut de instanțele judecătorești sau alte autorități competente, dacă are această obligație, potrivit legii.”
— HG 1/2016 (Normele metodologice ale Codului fiscal), pct. 3 alin. (1), titlul III (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

::: ghid-temei
„În cazul unei microîntreprinderi care se înființează sau își încetează existența, anul fiscal este perioada din anul calendaristic în care persoana juridică a existat.”
— Codul fiscal (Legea 227/2015), art. 50 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„O persoană juridică română care este nou-înființată poate opta să plătească impozit pe veniturile microîntreprinderilor începând cu primul an fiscal, dacă condițiile prevăzute la art. 47 alin. (1) lit. d) și h) sunt îndeplinite la data înregistrării în registrul comerțului, iar cea prevăzută la lit. g) în termen de 90 de zile inclusiv de la data înregistrării persoanei juridice respective.”
— Codul fiscal, art. 48 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă concret:

- **Data de start este data înregistrării.** În practică, e data din certificatul de înregistrare emis de registrul comerțului. Veniturile micro se calculează de la această dată.
- **Primul an e un an fiscal scurt.** Conform art. 50 alin. (2), anul fiscal este perioada din anul calendaristic în care firma a existat. Trimestrul înregistrării se declară doar pentru zilele de la înregistrare încoace.
- **Regimul micro se poate aplica din primul an, cu condiții.** Capitalul nu trebuie să fie deținut de stat sau de UAT (lit. d). Condiția privind asociații și unicitatea firmei micro trebuie îndeplinită la data înregistrării (lit. h). Pentru salariat există un termen de 90 de zile inclusiv de la înregistrare (lit. g).
- **Dacă salariatul nu apare în 90 de zile**, firma datorează impozit pe profit din trimestrul următor celui în care expiră cele 90 de zile (art. 48 alin. (3), teza a doua).
- **Termenele de plată și declarare rămân cele trimestriale:** D100 și plata până pe 25 ale lunii următoare trimestrului (art. 56 alin. (1)-(2)).

::: ghid-exemplu
SC Exemplu SRL se înregistrează la registrul comerțului pe 18 mai 2026 și optează pentru regimul micro.

- Perioada impozabilă începe pe 18 mai 2026. Primul trimestru declarat este trimestrul II, pentru intervalul 18 mai - 30 iunie 2026, cu D100 și plata până pe 25 iulie 2026.
- Termenul de 90 de zile pentru angajarea unui salariat se împlinește pe 16 august 2026, inclusiv. Dacă până atunci nu există salariat, termenul expiră în trimestrul III. Firma datorează atunci impozit pe profit din trimestrul IV 2026, începând cu 1 octombrie.
:::

## Ce se greșește în practică

- Perioada impozabilă se socotește de la data actului constitutiv sau de la data depunerii dosarului, nu de la data înregistrării.
- Se includ în baza micro venituri înregistrate înainte de data înregistrării firmei.
- Se calculează greșit termenul de 90 de zile pentru salariat, de la sfârșitul lunii sau de la prima factură. Termenul curge de la data înregistrării și se împlinește inclusiv în ultima zi.
- Se rămâne pe micro după expirarea celor 90 de zile fără salariat, deși legea mută firma la impozit pe profit din trimestrul următor.

## Ce face iConta.eu

iConta.eu generează declarația D100 pentru impozitul pe veniturile microîntreprinderilor, pe trimestru. Aplicația aplică cota pe perioadă și scadențele micro și produce XML validat pe validatorul oficial ANAF. Data înregistrării firmei, opțiunea pentru regimul micro și îndeplinirea condiției privind salariatul în primele 90 de zile le verifici tu. Tot tu le configurezi în vectorul fiscal al firmei.

[iConta.eu](/)
