---
title: "Amortizarea activelor primite prin donație sau sponsorizare"
description: "Ce valoare fiscală se amortizează pentru un mijloc fix primit cu titlu gratuit, conform definiției din Codul fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Amortizarea activelor primite prin donație sau sponsorizare

Un mijloc fix primit cu titlu gratuit — prin donație, sponsorizare sau ca aport — nu are un cost de achiziție propriu-zis, dar tot trebuie amortizat fiscal. Codul fiscal rezolvă acest caz explicit, prin definiția valorii fiscale.

## Temeiul legal

::: ghid-temei
„valoarea fiscală reprezintă: [...] c) costul de achiziție, de producție sau valoarea de piață a mijloacelor fixe dobândite cu titlu gratuit ori constituite ca aport, la data intrării în patrimoniul contribuabilului, utilizată pentru calculul amortizării fiscale, după caz - pentru mijloace fixe amortizabile și terenuri. În valoarea fiscală se includ și reevaluările contabile efectuate potrivit legii."
— Legea 227/2015 (Codul fiscal), art. 7 pct. 44 lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.html)
:::

Ce rezultă concret din text:

- **Baza de amortizare pentru un activ primit gratuit e valoarea de piață** la data intrării în patrimoniu — nu zero, așa cum s-ar putea presupune din faptul că firma nu a plătit nimic pentru el.
- **Aceeași regulă se aplică activelor constituite ca aport** (la capitalul social), tratate identic cu cele dobândite cu titlu gratuit, pentru scopul amortizării fiscale.
- **Condiția generală de mijloc fix amortizabil** (art. 28 alin. 2) trebuie îndeplinită și pentru activele gratuite: deținere și utilizare în activitatea firmei, plus pragul valoric legal la data intrării în patrimoniu.
- **Reevaluările ulterioare** se includ în valoarea fiscală, iar o reevaluare care scade valoarea sub costul/valoarea de piață inițială impune recalcularea valorii fiscale rămase neamortizate până la nivelul valorii inițiale (art. 7 pct. 44 lit. c, ultima teză).

## Ce se greșește în practică

- Se înregistrează activul primit gratuit la valoare zero sau la o valoare simbolică, omițând obligația de a-l evalua la valoarea de piață de la data intrării (art. 7 pct. 44 lit. c).
- Se confundă tratamentul contabil al venitului din primirea gratuită (recunoscut, de regulă, ca venit amânat/subvenție) cu baza de amortizare fiscală — cele două înregistrări coexistă, nu se anulează reciproc.
- Se omite documentarea valorii de piață la data intrării (evaluare, raport de evaluare sau altă dovadă rezonabilă), lăsând amortizarea ulterioară fără o bază justificabilă la control.

## Ce face iConta.eu

iConta.eu are teste dedicate metodei de amortizare pe ecran (`core/test_amortizare_ecran_metoda.py`) și confruntă amortizarea cu structura oficială a SAF-T (`core/test_r191_amortizare_confruntata.py`), ceea ce arată un motor de amortizare funcțional pentru mijloacele fixe introduse normal. Nu am identificat însă în cod o rută sau un câmp specific pentru introducerea unui mijloc fix „primit gratuit" cu valoare de piață la intrare, distinctă de introducerea unui activ achiziționat — dacă acest caz apare, valoarea de intrare trebuie stabilită și introdusă manual de contabil, conform art. 7 pct. 44 lit. c).

[iConta.eu](/)
