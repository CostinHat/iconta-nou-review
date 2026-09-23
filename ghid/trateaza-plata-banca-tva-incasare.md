---
title: Cum se tratează plata prin bancă în TVA la încasare?
description: Data exigibilității e cea din extrasul de cont, pentru transfer-credit — pentru instrumente de tip cec, cambie sau bilet la ordin regula diferă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se tratează plata prin bancă în TVA la încasare?

Plata prin bancă pare simplă — dar legea distinge explicit între transferul obișnuit (transfer-credit) și instrumentele de plată de tip transfer-debit (cec, cambie, bilet la ordin), cu date de exigibilitate diferite.

## Temeiul legal

::: ghid-temei
**Pct. 26 alin. (10) din Normele metodologice de aplicare a Codului fiscal (HG 1/2016)**: „În cazul încasărilor prin bancă de tipul transfer-credit, data încasării contravalorii totale/parțiale a livrării de bunuri/prestării de servicii de către persoana care aplică sistemul TVA la încasare este data înscrisă în extrasul de cont sau în alt document asimilat acestuia." Sursă: `anaf_surse/hg_1_2016_norme_cod_fiscal.txt`, linia 6582.

**Pct. 26 alin. (11)**: „În cazul în care încasarea se efectuează prin instrumente de plată de tip transfer-debit, respectiv cec, cambie și bilet la ordin, data încasării [...] este: a) data înscrisă în extrasul de cont [...], în situația în care furnizorul/prestatorul [...] nu girează instrumentul de plată, ci îl încasează/scontează [...]; b) data girului, în situația în care furnizorul/prestatorul [...] girează instrumentul de plată altei persoane." Sursă: `anaf_surse/hg_1_2016_norme_cod_fiscal.txt`, liniile 6584-6589.
:::

Pentru un transfer bancar obișnuit (ordin de plată primit de la client), data exigibilității TVA este strict data înscrisă în extrasul de cont — nu data la care a fost emis ordinul de plată de către client, nici data facturii.

Pentru cec, cambie sau bilet la ordin, regula se schimbă în funcție de ce faci cu instrumentul: dacă îl încasezi sau îl scontezi, exigibilitatea e tot la data din extrasul de cont (la scontare, se consideră încasată întreaga valoare a instrumentului); dacă în schimb îl girezi mai departe altei persoane, exigibilitatea intervine la data girului, nu la o eventuală încasare ulterioară — motiv pentru care norma cere păstrarea unei copii a instrumentului girat, cu mențiunea persoanei către care a fost girat.

## Ce se greșește în practică

- Se consideră exigibilă TVA la data emiterii ordinului de plată de către client, nu la data reală din extrasul de cont.
- Se tratează cecul/cambia/biletul la ordin girat mai departe la fel ca unul încasat direct, ignorând că girul mută data exigibilității.
- Se scontează un instrument de plată și se raportează ca exigibilă doar suma efectiv primită de la bancă (după scont), nu valoarea integrală a instrumentului, cum cere norma.

## Ce face iConta.eu

Ecranul manual „TVA la încasare" din iConta (rută `nota-tva-incasare`) cere contabilului să introducă direct data și suma încasată — aplicația nu diferențiază automat între transfer-credit, cec, cambie sau bilet la ordin. Stabilirea datei corecte de exigibilitate, conform regulilor de mai sus (extras de cont vs. dată gir), rămâne un calcul făcut de contabil înainte de a introduce operațiunea.

[iConta.eu](/)
