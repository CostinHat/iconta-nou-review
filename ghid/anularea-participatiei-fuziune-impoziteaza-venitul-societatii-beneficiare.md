---
title: "Anularea participației la fuziune: când nu se impozitează venitul societății beneficiare?"
description: "La o fuziune transfrontalieră în UE, venitul societății beneficiare din anularea participației la societatea cedentă nu se impozitează dacă participația depășește 10% din capital."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# Anularea participației la fuziune: când nu se impozitează venitul societății beneficiare?

Venitul pe care societatea beneficiară îl obține din anularea participației deținute la societatea cedentă nu se impozitează dacă participația este **mai mare de 10%** din capitalul cedentei. Regula din art. 33 alin. (7) al Codului fiscal (Legea 227/2015) se aplică fuziunilor și divizărilor la care participă societăți din cel puțin două state membre, dintre care una din România.

Situația apare des: firma românească deține deja acțiuni sau părți sociale la societatea pe care o absoarbe. La fuziune participația dispare, iar diferența dintre valoarea ei și partea din activul net preluat poate genera un venit. Pragul de 10% decide dacă acest venit intră sau nu în profitul impozabil.

## Temeiul legal

::: ghid-temei
„Atunci când o societate beneficiară deține o participație la capitalul societății cedente, veniturile societății beneficiare provenite din anularea participației sale nu se impozitează în cazul în care participația societății beneficiare la capitalul societății cedente este mai mare de 10%."
— Codul fiscal (Legea 227/2015), art. 33 alin. (7) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

::: ghid-temei
„operațiunilor de fuziune, divizare totală, divizare parțială, transferurilor de active și schimburilor de acțiuni în care sunt implicate societăți din două sau mai multe state membre, din care una este din România;"
— Codul fiscal (Legea 227/2015), art. 33 alin. (1) lit. a) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

::: ghid-temei
„Prevederile prezentului articol nu se aplică atunci când fuziunea, divizarea sub orice formă, transferul de active sau schimbul de acțiuni: a) are drept consecință frauda și evaziunea fiscală constatată în condițiile legii;"
— Codul fiscal (Legea 227/2015), art. 33 alin. (12) lit. a) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

Ce trebuie verificat concret:

- **Pragul este strict „mai mare de 10%".** O participație de exact 10% nu se încadrează. Venitul din anulare intră atunci în rezultatul fiscal, după regulile generale.
- **Participația se raportează la capitalul societății cedente**, adică al celei care își transferă activele și pasivele (art. 33 alin. (2) pct. 7). Nu contează cât reprezintă participația din activul beneficiarei.
- **Ambele societăți trebuie să fie „societăți dintr-un stat membru".** Art. 33 alin. (2) pct. 12 cere cumulativ: o formă de organizare din anexa nr. 3 la Titlul II, rezidență fiscală în UE și plata unui impozit pe profit din anexa nr. 4, fără opțiune sau exceptare. Pentru România, anexa nr. 3 enumeră doar societățile pe acțiuni, în comandită pe acțiuni și cu răspundere limitată.
- **Firma străină condusă efectiv din România** poate folosi art. 33 numai dacă are una dintre formele din anexa nr. 3 (art. 35).
- **Regimul cade la fraudă sau evaziune constatate** în condițiile legii (art. 33 alin. (12)). Atunci venitul din anulare nu mai beneficiază de neimpozitare.
- **La fuziunile între două firme românești** se aplică art. 32, nu art. 33. Art. 32 alin. (5) folosește însă același prag, „mai mare de 10%".

::: ghid-exemplu
SC Exemplu SRL (România) deține 40% din capitalul unei GmbH din Austria și o absoarbe printr-o fuziune transfrontalieră. Participația figurează în evidență la 200.000 lei. Partea de activ net al GmbH-ului care îi corespunde este de 260.000 lei, deci din anularea participației rezultă un venit de 60.000 lei.

Cum 40% > 10%, cei 60.000 lei nu se impozitează și nu intră în profitul impozabil.

Dacă SC Exemplu SRL ar fi deținut doar 8%, același venit ar fi intrat în profitul impozabil: 60.000 × 16% = 9.600 lei impozit pe profit.
:::

## Ce se greșește în practică

- Se aplică art. 33 la o fuziune între două societăți românești. Pentru acestea temeiul e art. 32, chiar dacă pragul e același.
- Participația de exact 10% este tratată ca îndeplinind condiția. Legea cere „mai mare de 10%".
- Procentul se calculează din capitalul societății beneficiare sau din valoarea fuziunii, nu din capitalul societății cedente.
- Nu se verifică forma de organizare a partenerului din celălalt stat membru în anexa nr. 3, deși condiția e cumulativă.
- Venitul din anulare rămâne în rezultatul contabil fără ajustarea fiscală corespunzătoare în declarația de impozit pe profit.

## Ce face iConta.eu

În iConta.eu, declarația D101 se calculează din balanța firmei, cu pierderea reportată și comparația cu impozitul minim pe cifra de afaceri, și se generează ca XML validat. Aplicația nu are un flux dedicat fuziunilor transfrontaliere și nu identifică singură venitul din anularea participației. Încadrarea în art. 33 alin. (7), verificarea pragului de 10% și tratarea venitului ca neimpozabil le face contabilul, pe baza proiectului de fuziune.

[iConta.eu](/)
