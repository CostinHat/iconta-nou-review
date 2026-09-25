---
title: "NIR pentru bunuri primite în consignație 2026"
description: "Când e obligatorie Nota de recepție și constatare de diferențe pentru bunurile primite de la un terț și de ce consignația nu se tratează ca o achiziție proprie."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# NIR pentru bunuri primite în consignație 2026

Consignatarul nu cumpără bunurile pe care le primește de la consignant — le deține temporar, în numele acestuia, până la vânzare. Întrebarea revine des: se face NIR la primirea mărfii în consignație, ca la o achiziție obișnuită, sau nu?

## Temeiul legal

::: ghid-temei
„(Cod 14-3-1A) Nota de recepție și constatare de diferențe (NIR) servește ca: - document pentru recepția bunurilor aprovizionate; [...] Nota de recepție și constatare de diferențe se folosește ca document de recepție obligatoriu numai în cazul: - bunurilor materiale cuprinse într-o factură sau aviz de însoțire a mărfii, care fac parte din gestiuni diferite; - bunurilor materiale primite spre prelucrare, în custodie sau în păstrare; - bunurilor materiale procurate de la persoane fizice; - bunurilor materiale care sosesc neînsoțite de documente de livrare; - bunurilor materiale care prezintă diferențe la recepție; - mărfurilor intrate în gestiunile la care evidența se ține la preț de vânzare."
— OMFP 2634/2015, Anexa 2 (Norme specifice) (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Observație importantă: textul normativ de mai sus enumeră explicit cazurile în care NIR-ul e obligatoriu — printre ele, bunurile primite „spre prelucrare, în custodie sau în păstrare". Cuvântul „consignație" nu apare ca atare în listă. Nu există, în sursele verificate, un temei care să numească explicit consignația printre situațiile NIR obligatoriu; redirecționăm onest spre cel mai apropiat caz reglementat — custodia/păstrarea — pentru că, din punct de vedere contabil, bunurile primite în consignație au aceeași natură: aparțin unui terț (consignantul), nu sunt proprietatea consignatarului până la vânzare.

Ce rezultă din asimilarea consignației cu custodia/păstrarea:
- Bunurile **nu intră în stocul propriu** al consignatarului (nu se debitează contul 371 „Mărfuri" la primire), pentru că nu sunt proprietatea lui.
- Evidența se ține **extrapatrimonial**, în contul 8033 „Valori materiale primite în păstrare sau custodie" (OMFP 1802/2014), pe baza actului de predare-primire încheiat cu consignantul.
- Recepția fizică se poate consemna printr-un NIR sau printr-un proces-verbal de predare-primire, dar acest document nu generează o înregistrare de stoc propriu — doar evidența extrapatrimonială, până la momentul vânzării, când consignatarul stinge contul 8033 și înregistrează operațiunea de vânzare/facturare pentru consignant.

## Ce se greșește în practică

- Se întocmește NIR ca la o achiziție și marfa e încărcată direct în stocul propriu (371), ca și cum consignatarul ar fi cumpărat bunurile — ceea ce denaturează atât stocul, cât și rezultatul fiscal.
- Se omite complet evidența extrapatrimonială (8033), astfel încât bunurile aflate fizic în gestiune nu apar nicăieri în contabilitate până la vânzare.
- Se confundă momentul recepției fizice cu momentul transferului de proprietate — transferul, și implicit obligația de facturare din partea consignantului, are loc abia la vânzarea către clientul final, nu la primirea mărfii de către consignatar.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are un flux general de NIR pentru achiziții de stocuri (ecranul de recepții, prin care se introduc articolele, cantitățile și prețurile de achiziție), dar **nu are un flux dedicat pentru consignație** — nu există în aplicație o evidență extrapatrimonială (cont 8033) separată de stocul propriu. Pentru bunuri primite în consignație, contabilul trebuie să evite introducerea lor prin ecranul de recepții obișnuit (care le-ar trece în stocul propriu) și să le urmărească separat, prin alte mijloace, până la extinderea aplicației cu acest flux specific.

[iConta.eu](/)
