---
title: "TVA la achiziția unui vehicul comercial din UE"
description: "Regula generală de achiziție intracomunitară de bunuri se aplică și vehiculelor comerciale, cu excepția specială pentru mijloacele de transport noi."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# TVA la achiziția unui vehicul comercial din UE

Achiziția unui vehicul comercial (utilitară, camion, remorcă) dintr-un alt stat membru UE urmează, ca principiu, regula achiziției intracomunitare de bunuri — dar cu o excepție importantă pentru vehiculele **noi**.

## Temeiul legal

::: ghid-temei
CF art. 268 alin. (1)-(3) lit. a): „Operațiuni impozabile; alin. (3) lit. a) — AIC de bunuri (altele decât mijloace de transport noi/accizabile) urmând unei LIC scutite.” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L16593-16626)

CF art. 308-309: „Obligat la plata taxei = beneficiarul, la AIC/servicii primite.” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L19405, L19418)
:::

Textul citat exclude explicit „mijloacele de transport noi” din regimul obișnuit al achiziției intracomunitare care urmează unei livrări intracomunitare scutite — pentru vehiculele noi există un regim special (impozitare la destinație, la cumpărător, indiferent de statutul lui de plătitor de TVA), diferit de regula standard descrisă mai jos pentru achizițiile obișnuite.

Pentru un vehicul comercial care **nu** se încadrează în categoria „mijloc de transport nou” (regulile de noutate țin de vechime/kilometraj, nu sunt detaliate în cercetarea care stă la baza acestui ghid), se aplică regula generală: dacă firma din România e înregistrată în scopuri de TVA (normal sau prin codul special art. 317) și furnizorul are cod de TVA valid în alt stat membru, achiziția e o AIC — TVA se calculează prin taxare inversă (beneficiarul e obligat la plata taxei, conform art. 308-309), cu formula contabilă 4426 = 4427.

## Ce se greșește în practică

- Se tratează orice vehicul cumpărat din UE la fel, fără a verifica dacă se încadrează la excepția „mijloc de transport nou” — regim cu reguli proprii, diferite de AIC obișnuită.
- Se omite verificarea codului de TVA al vânzătorului în VIES înainte de a aplica taxarea inversă.
- Se confundă tratamentul TVA la achiziție cu alte reguli fiscale specifice vehiculelor (de exemplu limitări de deducere aplicabile autoturismelor) — acestea sunt teme separate, neacoperite de acest ghid.

## Ce face iConta.eu

Pentru o achiziție intracomunitară obișnuită de bunuri (inclusiv vehicule care nu intră în categoria „mijloc de transport nou”), folosești formularul de achiziție intracomunitară (`achizitie_ic`), tip „bunuri”, din categoria „Extern”: data, valoarea în RON, codul de TVA al furnizorului, numărul facturii, furnizorul, contul de destinație (sugestie 371) și cota de TVA aplicabilă, declarată explicit.

Aplicația calculează TVA prin taxare inversă (4426 = 4427) și clasifică operațiunea pentru D390, cod A. Pentru cazul particular al unui mijloc de transport nou, verifică regulile specifice — nu confirmate în cercetarea care stă la baza acestui ghid ca fiind acoperite de un formular dedicat.

[iConta.eu](/)
