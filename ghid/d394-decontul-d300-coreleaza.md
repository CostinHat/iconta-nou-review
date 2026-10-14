---
title: "D394 și decontul D300: cum se corelează"
description: D300 și D394 nu au aceeași sumă și nu ar trebui să aibă — D300 e TVA totală, D394 e doar subsetul raportabil. Aplicația nu compară automat cele două declarații, cu o singură excepție documentată, taxarea inversă.
published: 2026-09-23
modified: 2026-10-13
poarta: v1
---

# D394 și decontul D300: cum se corelează

D300 și declarația informativă 394 provin din aceleași facturi, dar nu raportează aceeași sumă — și nu e o eroare când diferă. Mai jos e mecanismul real, verificat direct în cod, nu o presupunere despre cum "ar trebui" să se coreleze cele două.

## Temeiul legal

::: ghid-temei
„TOTAL TAXĂ COLECTATĂ (sumă de la rd. 1 până la rd. 18, cu excepţia celor de la rd. 3.1, 5.1, 7.1, 12.1, 12.2)”
— OPANAF 174/2026, anexa 1, formularul 300, rândul 19 (sursă: [OPANAF nr. 174/2026 pentru aprobarea formularului 300 (Decont de TVA)](https://legislatie.just.ro/Public/DetaliiDocument/307258))
:::

Formula de mai sus e chiar motivul pentru care D300 și D394 nu pot fi puse în egalitate directă: rândul 19 al D300 adună **toată** taxa colectată a perioadei, indiferent dacă operațiunea e sau nu raportabilă separat în D394. D394 raportează doar un subset — operațiunile B2B pe cote, către parteneri identificabili.

## De ce nu sunt aceeași sumă

Relația corectă între cele două declarații e o inegalitate, nu o egalitate: D300 colectat este întotdeauna mai mare sau egal cu D394 pe operațiunile raportabile pe cotă — niciodată invers, și rareori identic. O comparație pe egalitate ar semnala divergențe false, pentru operațiuni care legitim apar doar în D300.

## Ce nu face aplicația

Căutare directă în codul motorului D300 și al panoului manual „Rând manual D300” nu găsește nicio referință la D394 — cele două module nu "știu" unul de celălalt.

Există un test intern, aplicația, care confruntă „calculul D300 (Declarații)” cu „calculul D394 (Declarații)”, dar propriul lui docstring îl declară explicit **tautologic**: ambele generatoare citesc aceleași linii de factură și deduc cota identic — testul prinde doar drift între cele două generatoare, nu erori reale de agregare. Nu e un instrument expus contabilului.

Decizia de a nu construi o reconciliere încrucișată D394↔D300 e documentată explicit (DECIZII.md, 05.08.2026, secțiunea „GARD CONTINUT D394"), din exact aceste două motive: testul ar fi tautologic, iar relația dintre sume nu e de egalitate.

## Singura legătură reală: taxarea inversă

Pentru achizițiile cu taxare inversă (art. 331, măsuri de simplificare), rândurile 12 (colectat) și 26 (deductibil, oglindă net zero) se derivă **automat** din facturile primite cu flag „taxare inversă”, atât timp cât factura are linii cu o cotă determinabilă. Panoul manual „Rând manual D300” rămâne necesar doar ca excepție — pentru o achiziție cu taxare inversă a cărei factură nu are linii/cotă determinabilă — iar gărzile anti-dublă-numărare interzic introducerea manuală a rândurilor 12/26 dacă în perioadă există deja o sumă derivată automat. D394 clasifică aceeași operațiune automat, ca tip C, indiferent dacă factura are sau nu linii — o divergență de mecanism între cele două declarații, documentată explicit ca intenționată (DECIZII.md, 31.07.2026: „d300 vs d394 pe reverse charge: divergența de clasificare e CERINȚĂ, nu bug"), nu ca defect.

## Ce se greșește în practică

- Se tratează orice diferență de sumă între D300 și D394 ca semnal automat de eroare, deși majoritatea diferențelor sunt legitime (D300 include operațiuni care nu apar deloc în D394).
- Se caută în aplicație un raport de „comparație D394↔D300" — nu există unul expus contabilului; gardul intern de test e doar pentru drift între generatoare.
- Se presupune că rândul 12 (taxare inversă) trebuie mereu introdus manual prin „Rând manual D300” — de fapt se derivă automat din facturile primite cu linii; manualul e doar excepția pentru facturile fără linii determinabile.

## Ce face iConta.eu

Aplicația nu oferă o funcție de comparație automată D394↔D300 — nu există un asemenea mecanism în codul verificat. Gardul intern existent e o măsură de testare internă, tautologică prin construcție, nu un instrument de verificare a conținutului pentru contabil. Pentru taxarea inversă primită (art. 331), D300 derivă automat rândurile 12/26 din facturile cu flag taxare inversă care au linii cu cotă determinabilă; panoul manual „Rând manual D300” rămâne necesar doar pentru facturile fără linii, cu gard explicit împotriva dublei numărări.

[iConta.eu](/)
