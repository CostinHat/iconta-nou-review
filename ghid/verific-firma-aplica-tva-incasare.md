---
title: Cum verific dacă o firmă aplică TVA la încasare?
description: Verificarea se face în Registrul public al persoanelor care aplică TVA la încasare, ținut de ANAF — nu prin presupunere pe baza cifrei de afaceri sau a plafonului legal.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific dacă o firmă aplică TVA la încasare?

A aplica TVA la încasare nu e o stare dedusă din cifra de afaceri a unei firme, ci un fapt înregistrat oficial. Singurul loc unde afli cu certitudine dacă o firmă (a ta sau a unui partener) aplică sistemul este Registrul public al ANAF.

## Temeiul legal

::: ghid-temei
**Art. 324 alin. (16) din Codul fiscal (Legea 227/2015)**: „A.N.A.F. organizează Registrul persoanelor impozabile care aplică sistemul TVA la încasare conform art. 282 alin. (3)-(8) [...]. Registrul este public și se afișează pe site-ul A.N.A.F. [...]" Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, liniile 22087-22093.

**Art. 282 alin. (3) CF**, modificat prin art. 6 pct. 38 OUG 8/2026 (MO 147/25.02.2026): „[...] exigibilitatea taxei intervine la data încasării [...] Plafonul pentru aplicarea sistemului TVA la încasare este de: a) 5.000.000 lei, în perioada 1 martie-31 decembrie 2026; b) 5.500.000 lei, începând cu data de 1 ianuarie 2027." Anterior, plafonul a fost 4.500.000 lei, în vigoare din 1 ianuarie 2021 (Legea 296/2020) până la 28 februarie 2026. Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, liniile 17635-17649.
:::

Pasul corect e să cauți firma (după CUI) în Registrul persoanelor impozabile care aplică sistemul TVA la încasare, public pe site-ul ANAF — nu să deduci statusul din cifra de afaceri sau din faptul că firma pare eligibilă. Eligibilitatea (înregistrare TVA, sediu în România, cifră de afaceri sub plafon) e o condiție necesară, dar nu suficientă: firma trebuie să fi depus și notificarea de opțiune la ANAF, iar organul fiscal trebuie să o fi înscris efectiv în Registru.

Dacă vrei doar să estimezi eligibilitatea (de exemplu pentru propria firmă, înainte de a opta), plafonul de referință depinde de dată: 4.500.000 lei a fost valabil până la 28 februarie 2026, 5.000.000 lei din 1 martie până la 31 decembrie 2026, iar de la 1 ianuarie 2027 plafonul urcă la 5.500.000 lei. Cifra de afaceri a anului precedent trebuie comparată cu plafonul aplicabil anului în curs, nu cu unul istoric.

## Ce se greșește în practică

- Se presupune că o firmă aplică TVA la încasare doar pentru că cifra ei de afaceri e sub plafon — eligibilitatea nu înseamnă înscriere efectivă în Registru.
- Se folosește plafonul vechi de 4.500.000 lei și după 1 martie 2026, fără să se țină cont de majorarea adusă de OUG 8/2026.
- Se ia decizia pe baza mențiunii (sau lipsei ei) de pe factură, fără verificare directă în Registrul public ANAF.

## Ce face iConta.eu

Funcția `plafon_la(data)` din motorul F097 calculează automat plafonul corect valabil la orice dată (4,5M / 5M / 5,5M, în funcție de perioadă), pe baza istoricului legislativ din tabelul intern al aplicației. Verificarea propriu-zisă a înscrierii unei firme în Registrul public ANAF **nu este automatizată** — rămâne un pas manual al contabilului, pe portalul ANAF.

[iConta.eu](/)
