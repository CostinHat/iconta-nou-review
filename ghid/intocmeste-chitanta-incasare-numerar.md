---
title: "Cum se întocmește chitanța pentru încasare numerar"
description: "Ce e obligatoriu pe o chitanță de încasare numerar, conform OMFP 2634/2015, și când ea ține loc de document justificativ pentru venituri."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se întocmește chitanța pentru încasare numerar

Chitanța rămâne documentul standard pentru o încasare în numerar care nu trece prin aparatul de marcat electronic fiscal — de la o firmă către alta, sau pentru operațiuni scutite de TVA fără drept de deducere.

## Temeiul legal

::: ghid-temei
„Chitanța și chitanța pentru operațiuni în valută sunt documente justificative de înregistrare în registrul de casă/registrul de casă în valută și în contabilitate a încasărilor și plăților efectuate în numerar (lei/valută), precum și a depunerilor de sume la casieria entității. În condițiile în care sumele înscrise în chitanță sunt aferente livrărilor de bunuri sau prestărilor de servicii scutite fără drept de deducere conform prevederilor din Codul fiscal, formularul de chitanță este documentul justificativ care stă la baza înregistrării veniturilor în contabilitate. [...] Se întocmește pentru fiecare sumă încasată, de către casierul entității și se semnează de acesta pentru primirea sumei."
— OMFP 2634/2015, Anexa 2, Cod 14-4-1 — Chitanța (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Ce reține norma:

- **Se întocmește pentru fiecare sumă încasată**, semnată de casier — nu e un document opțional sau recapitulativ, ci unul emis operațiune cu operațiune.
- Servește dublu: e documentul justificativ pentru **registrul de casă** și, în același timp, documentul justificativ **contabil** al încasării.
- Pentru **livrări/prestări scutite fără drept de deducere**, chitanța devine chiar documentul care stă la baza înregistrării veniturilor — nu doar al mișcării de numerar, ci al venitului însuși.
- Chitanța pentru operațiuni în valută e un formular distinct (Cod 14-4-1/a), nu aceeași chitanță completată cu altă monedă.

## Ce se greșește în practică

- Se folosește chitanța și pentru încasările prin AMEF, dublând inutil documentul — pentru vânzările cu casă de marcat, documentul justificativ e Raportul fiscal de închidere zilnică, nu chitanța.
- Se emite o singură chitanță recapitulativă pentru mai multe încasări din aceeași zi — norma cere emiterea pentru fiecare sumă încasată, nu cumulat.
- Se omite semnătura casierului pentru primirea sumei — fără ea, chitanța nu are valoarea de document justificativ cerută de normă.

## Ce face iConta.eu

La data acestui ghid, `core/chitante.py` conține funcția `pdf_chitanta(emitent, ch)`, care generează documentul de chitanță, inclusiv conversia sumei în litere (`suma_in_litere()`), element standard al formularului. Aplicația produce efectiv documentul pentru fiecare încasare introdusă, coerent cu cerința normei de emitere pe operațiune.

[iConta.eu](/)
