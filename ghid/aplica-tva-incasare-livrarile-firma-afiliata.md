---
title: "Se aplică TVA la încasare pentru livrările către o firmă afiliată?"
description: "Nu. Livrările și prestările către o persoană afiliată sunt excluse din TVA la încasare: taxa devine exigibilă după regulile generale, chiar dacă factura nu e încasată."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Se aplică TVA la încasare pentru livrările către o firmă afiliată?

Nu. Chiar dacă firma ta e înscrisă în sistemul TVA la încasare, livrările de bunuri și prestările de servicii către un beneficiar afiliat nu intră în sistem. Pentru ele, TVA devine exigibilă după regulile generale, adică la data faptului generator (livrarea sau prestarea) sau la emiterea facturii, dacă factura a fost emisă înainte. Nu contează când plătește clientul.

În practică, asta înseamnă bani. O factură neîncasată către firma-soră trebuie plătită la buget cu decontul perioadei în care a fost făcută livrarea. Nu poate aștepta în 4428 până la încasare.

## Temeiul legal

::: ghid-temei
„Persoanele impozabile care optează pentru aplicarea sistemului TVA la încasare aplică sistemul respectiv numai pentru operațiuni pentru care locul livrării, conform prevederilor art. 275 [...] nu aplică sistemul respectiv pentru următoarele operațiuni care intră sub incidența regulilor generale privind exigibilitatea TVA: [...] d) livrările de bunuri/prestările de servicii pentru care beneficiarul este o persoană afiliată furnizorului/prestatorului potrivit art. 7 pct. 26”
— Codul fiscal (Legea 227/2015), art. 282 alin. (6) lit. d) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

::: ghid-temei
„În sensul art. 282 alin. (6) lit. d) din Codul fiscal, se exclud de la aplicarea sistemului TVA la încasare livrările de bunuri/prestările de servicii dacă, la momentul emiterii facturii sau, după caz, la data termenului-limită prevăzut de lege pentru emiterea facturii în situația în care factura nu a fost emisă în termenul prevăzut de lege, beneficiarul este o persoană afiliată furnizorului/prestatorului potrivit art. 7 pct. 26 din Codul fiscal.”
— HG 1/2016 (Normele metodologice ale Codului fiscal), pct. 26 alin. (14) (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))
:::

::: ghid-temei
„o persoană juridică este afiliată cu altă persoană juridică dacă cel puțin aceasta deține, în mod direct sau indirect, inclusiv deținerile persoanelor afiliate, minimum 25% din valoarea/numărul titlurilor de participare sau al drepturilor de vot la cealaltă persoană juridică ori dacă controlează în mod efectiv acea persoană juridică;”
— Codul fiscal, art. 7 pct. 26 lit. c) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

Ce înseamnă concret:

- **Afilierea se verifică pe fiecare factură.** Momentul relevant este emiterea facturii. Dacă factura a întârziat, se ia termenul-limită legal de emitere. Dacă relația de afiliere începe sau încetează în cursul anului, tratamentul se schimbă de la factura respectivă.
- **Pragul este de 25%.** Poate fi deținere directă sau indirectă, iar la calcul se adună și deținerile persoanelor afiliate. Controlul efectiv, fără procent, ajunge și el. Două firme cu același asociat de peste 25% sunt afiliate între ele (lit. d).
- **Firma rămâne în sistem.** Excluderea privește doar operațiunile către afiliat. Pentru ceilalți clienți, exigibilitatea rămâne la încasare.
- **Ordinea este: întâi afilierea, apoi regimul.** Excluderea pentru afiliat se aplică pe lângă cele pentru taxare inversă, operațiuni scutite și regimuri speciale (lit. a)-c) ale aceluiași alineat).

::: ghid-exemplu
SC Exemplu SRL aplică TVA la încasare și deține 60% din SC Filiala SRL. Pe 10 septembrie 2026 îi livrează mărfuri de 10.000 lei + TVA 21% = 2.100 lei. Factura e emisă în aceeași zi, iar încasarea vine abia în noiembrie.

Filiala este afiliată, așa că TVA de 2.100 lei devine exigibilă în septembrie: 4111 = 707 10.000 lei și 4111 = 4427 2.100 lei. Suma intră în decontul pe septembrie. Încasarea din noiembrie stinge doar creanța și nu mai mută TVA.

Dacă aceeași livrare ar fi mers la un client neafiliat, TVA ar fi stat în 4428 până în noiembrie.
:::

## Ce se greșește în practică

- Toate facturile firmei se tratează „la încasare”, inclusiv cele către firma-soră sau către firma asociatului majoritar. Rezultatul e TVA declarată prea târziu, cu dobânzi și penalități de întârziere pentru perioada decalată.
- Se verifică doar deținerea directă și se scapă afilierea prin asociat comun sau prin lanț de dețineri.
- Nu se recalifică nimic după o cesiune de părți sociale în cursul anului. Afilierea se judecă la data fiecărei facturi, nu o dată pe an.
- Se bifează „TVA la încasare” pe factura către afiliat. Mențiunea este corectă doar pentru operațiunile care intră efectiv în sistem.

## Ce face iConta.eu

La contarea facturilor, iConta.eu înregistrează TVA pe 4428 sau pe 4427, după cum marchezi factura ca fiind sau nu în regim de TVA la încasare. Motorul dedicat TVA la încasare calculează TVA exigibilă din sumele încasate, prin suta mărită. Aplicația nu identifică singură afilierea dintre parteneri. Tu decizi care facturi către afiliați ies din sistem și le contezi cu 4427. În D394, operațiunile cu persoane afiliate se semnalează prin indicatorul dedicat din antetul declarației.

[iConta.eu](/)
