---
title: "Cum se contabilizează taxa de transport nerestituită la retur?"
description: "Tratamentul contabil al garanției SGR de 0,50 lei/ambalaj — încasată la vânzare și restituită doar la returul efectiv al ambalajului — potrivit HG 1074/2021."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se contabilizează taxa de transport nerestituită la retur?

Ce e cunoscut popular drept „taxă" pe ambalaj, la produsele care intră sub sistemul garanție-returnare (SGR), nu e de fapt o taxă, ci o **garanție**: o sumă fixă încasată la vânzare, care se restituie doar atunci când consumatorul aduce efectiv ambalajul înapoi. Cât timp ambalajul nu e returnat, garanția nu se restituie — iar contabil, ea rămâne o datorie a comerciantului față de sistem, nu un venit.

## Temeiul legal

::: ghid-temei
„SGR sistem garantie-returnare — motor PUR (HG 1074/2021, garantie 0,50 lei/ambalaj, administrator RetuRO). Tratament MFP/CECCAR: garantia NU intra in sfera TVA; tariful de gestionare primit de la RetuRO este purtator de TVA (autofactura emisa de RetuRO in numele comerciantului)."
— HG 1074/2021 (garanția SGR), citat din documentația modulului core/sgr.py, verificat la sursă
:::

Monografia contabilă, pentru un comerciant care vinde produse cu ambalaj SGR:

- **La achiziția mărfii**: garanția plătită furnizorului se înregistrează **461.SGR = 401**, fără TVA — garanția nu intră în baza de TVA a tranzacției.
- **La vânzare**: garanția încasată de la client, evidențiată distinct pe bon, se înregistrează **5311/5121 = 462.SGR**.
- **Dacă ambalajul NU e returnat** de client (situația din titlul acestui ghid): garanția încasată rămâne în contul 462.SGR ca sumă de virat către amonte (462.SGR = 401/5121), pentru că nu există returnare care să declanșeze restituirea.
- **Dacă ambalajul E returnat**: restituirea către consumator se înregistrează **461.SGR = 5311/5121**, sumă care devine o creanță a comerciantului asupra administratorului RetuRO.
- **Autofactura lunară RetuRO**: încasarea garanțiilor efectiv returnate se înregistrează **5121 = 461.SGR** (fără TVA), iar tariful de gestionare primit de la RetuRO **4111 = 708 + 4427** (cu TVA).

## Ce se greșește în practică

- Se tratează garanția SGR ca parte din prețul de vânzare, inclusă în baza de TVA — garanția e explicit în afara sferei TVA; doar tariful de gestionare de la RetuRO e purtător de TVA.
- Se recunoaște garanția nerestituită direct ca venit al comerciantului, la momentul vânzării — de fapt rămâne o datorie (462.SGR) până la virarea ei către amonte/RetuRO, nu un venit propriu al firmei.
- Se amestecă, în aceeași notă contabilă, garanția încasată de la client cu garanția plătită furnizorului la achiziție — sunt fluxuri distincte, cu conturi analitice separate (461.SGR pentru creanțe, 462.SGR pentru datorii).

## Ce face iConta.eu

La data acestui ghid, iConta.eu are un motor real, dedicat, pentru contabilizarea garanției SGR (`core/sgr.py`): generează notele contabile pentru achiziția mărfii cu garanție plătită furnizorului, încasarea garanției la vânzare, restituirea către consumatorul care returnează ambalajul și autofactura lunară de la RetuRO — cu tratamentul corect de TVA (garanția în afara sferei TVA, tariful de gestionare purtător de TVA), conform monografiei MFP/CECCAR citate în cod.

[iConta.eu](/)
