---
title: Cum se tratează cesiunea de creanță în sistemul TVA la încasare?
description: Cesiunea unei creanțe declanșează exigibilitatea integrală a TVA la data cesiunii, indiferent de prețul la care creanța a fost cedată.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se tratează cesiunea de creanță în sistemul TVA la încasare?

Când o firmă cedează unui terț dreptul de a încasa o factură neplătită, legea consideră că întreaga contravaloare a fost încasată la data cesiunii — chiar dacă prețul obținut din cesiune e mai mic decât valoarea facturii.

## Temeiul legal

::: ghid-temei
**Pct. 26 alin. (8) lit. a) din Normele metodologice de aplicare a Codului fiscal (HG 1/2016)**: „dacă furnizorul/prestatorul cesionează creanțele aferente unor facturi emise pentru livrări de bunuri/prestări de servicii, se consideră că la data cesiunii creanțelor, **indiferent de prețul cesiunii creanțelor**, este încasată întreaga contravaloare a facturilor neîncasate până la momentul cesiunii. În cazul în care cedentul este o persoană impozabilă care aplică sistemul TVA la încasare pentru respectivele operațiuni, exigibilitatea taxei intervine la data cesiunii creanțelor." Sursă: `anaf_surse/hg_1_2016_norme_cod_fiscal.txt`, liniile 6559-6564.

Exemplu din normă (același punct, verbatim, folosind cota istorică de 20% valabilă la data redactării textului): „Societatea A [...] emite o factură [...] în sumă de 120.000 lei (inclusiv TVA de 20%) [...]. TVA în sumă de 20.000 lei se înregistrează în creditul contului 4428 [...]. La data de 15 noiembrie 2016, societatea A cesionează către societatea N creanța aferentă acestei facturi [...]. Prețul cesiunii este de 80.000 lei [...]. [...] se consideră că aceasta este încasată și exigibilitatea TVA intervine la data de 15 noiembrie 2016, societatea A având obligația să colecteze TVA în sumă de 20.000 lei."
:::

Regula esențială: prețul obținut din vânzarea creanței (adesea sub valoarea nominală, pentru că cesionarul își asumă riscul de neplată) nu contează pentru TVA — la data cesiunii, întreaga sumă rămasă neîncasată din factură devine exigibilă, integral, indiferent cât încasează efectiv cedentul din vânzarea creanței.

Norma tratează separat și situația inversă: când cumpărătorul unei livrări cedează furnizorului o creanță de-a lui (de exemplu dreptul de rambursare TVA), drept plată pentru achiziție — aici data cesiunii e data la care se consideră că beneficiarul a plătit, respectiv furnizorul a încasat, la nivelul valorii creanței cesionate; pentru o eventuală diferență rămasă neacoperită, exigibilitatea/deducerea rămân amânate până la plata efectivă a diferenței.

## Ce se greșește în practică

- Se raportează ca exigibilă doar suma efectiv încasată din prețul cesiunii, nu întreaga valoare rămasă neîncasată din factură.
- Se confundă data semnării contractului de cesiune cu o altă dată (de exemplu data notificării debitorului cedat), deși norma leagă exigibilitatea de data cesiunii creanțelor.
- Nu se tratează distinct cazul beneficiarului care cedează el însuși o creanță drept plată — situație cu reguli proprii, diferite de cesiunea făcută de furnizor.

## Ce face iConta.eu

Cercetarea la sursă a codului F097 nu a găsit o ramură dedicată cesiunii de creanță — motorul aplică formula sutei mărite pe orice sumă și dată introduse manual de contabil în ecranul „TVA la încasare". Pentru o cesiune de creanță, contabilul trebuie să introducă manual data cesiunii ca dată de „încasare" și valoarea integrală rămasă neîncasată din factură, conform regulii de mai sus — calculul specific al acestei situații nu e automatizat de aplicație.

[iConta.eu](/)
