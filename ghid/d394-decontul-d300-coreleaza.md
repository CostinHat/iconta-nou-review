---
title: "D394 și decontul D300: cum se corelează"
description: D300 și D394 nu au aceeași sumă și nu ar trebui să aibă — D300 e TVA totală, D394 e doar subsetul raportabil. Aplicația nu compară automat cele două declarații, cu o singură excepție documentată, taxarea inversă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# D394 și decontul D300: cum se corelează

D300 și declarația informativă 394 provin din aceleași facturi, dar nu raportează aceeași sumă — și nu e o eroare când diferă. Mai jos e mecanismul real, verificat direct în cod, nu o presupunere despre cum "ar trebui" să se coreleze cele două.

## Temeiul legal

::: ghid-temei
„R17_1 = R1_1+ R2_1+ R3_1+ R4_1+ R5_1+ R6_1+ R7_1+ R8_1+ R9_1+ R10_1+ R11_1+ R12_1+ R14_1+ R15_1+ R16_1+ R13_1+ R64_1+ R65_1" — structura D300 v12 (OPANAF 174/2026), rd.17 col.1, Total taxă colectată
:::

Formula de mai sus e chiar motivul pentru care D300 și D394 nu pot fi puse în egalitate directă: rd.17 al D300 adună **toată** taxa colectată a perioadei, indiferent dacă operațiunea e sau nu raportabilă separat în D394. D394 raportează doar un subset — operațiunile B2B pe cote, către parteneri identificabili.

## De ce nu sunt aceeași sumă

Relația corectă între cele două declarații e o inegalitate, nu o egalitate: D300 colectat este întotdeauna mai mare sau egal cu D394 pe operațiunile raportabile pe cotă — niciodată invers, și rareori identic. O comparație pe egalitate ar semnala divergențe false, pentru operațiuni care legitim apar doar în D300.

## Ce nu face aplicația

Căutare directă în codul motorului D300 (`core/d300.py`) și al panoului manual F251 (`core/d300_manual_api.py`) nu găsește nicio referință la D394 — cele două module nu "știu" unul de celălalt.

Există un test intern, `test_d300_d394_paritate.py`, care confruntă `calcul_d300` cu `calcul_d394`, dar propriul lui docstring îl declară explicit **tautologic**: ambele generatoare citesc aceleași linii de factură și deduc cota identic — testul prinde doar drift între cele două generatoare, nu erori reale de agregare. Nu e un instrument expus contabilului.

Decizia de a nu construi o reconciliere încrucișată D394↔D300 e documentată explicit (DECIZII.md, 05.08.2026, secțiunea „GARD CONTINUT D394"), din exact aceste două motive: testul ar fi tautologic, iar relația dintre sume nu e de egalitate.

## Singura legătură reală: taxarea inversă

Pentru achizițiile cu taxare inversă (art. 331, măsuri de simplificare), rândurile rd.12 (colectat) și rd.25 (deductibil, oglindă net zero) se derivă **automat** din facturile primite cu flag `taxare_inversa`, atât timp cât factura are linii cu o cotă determinabilă. Panoul manual F251 rămâne necesar doar ca excepție — pentru o achiziție cu taxare inversă a cărei factură nu are linii/cotă determinabilă — iar gărzile anti-dublă-numărare interzic introducerea manuală a R12/R25 dacă în perioadă există deja o sumă derivată automat. D394 clasifică aceeași operațiune automat, ca tip C, indiferent dacă factura are sau nu linii — o divergență de mecanism între cele două declarații, documentată explicit ca intenționată (DECIZII.md, 31.07.2026: „d300 vs d394 pe reverse charge: divergența de clasificare e CERINȚĂ, nu bug"), nu ca defect.

## Ce se greșește în practică

- Se tratează orice diferență de sumă între D300 și D394 ca semnal automat de eroare, deși majoritatea diferențelor sunt legitime (D300 include operațiuni care nu apar deloc în D394).
- Se caută în aplicație un raport de „comparație D394↔D300" — nu există unul expus contabilului; gardul intern de test e doar pentru drift între generatoare.
- Se presupune că rd.12 (taxare inversă) trebuie mereu introdus manual prin F251 — de fapt se derivă automat din facturile primite cu linii; manualul e doar excepția pentru facturile fără linii determinabile.

## Ce face iConta.eu

Aplicația nu oferă o funcție de comparație automată D394↔D300 — nu există un asemenea mecanism în codul verificat. Gardul intern existent (`test_d300_d394_paritate.py`) e o măsură de testare internă, tautologică prin construcție, nu un instrument de verificare a conținutului pentru contabil. Pentru taxarea inversă primită (art. 331), D300 derivă automat rd.12/rd.25 din facturile cu flag taxare_inversa care au linii cu cotă determinabilă; panoul manual F251 rămâne necesar doar pentru facturile fără linii, cu gard explicit împotriva dublei numărări.

[iConta.eu](/)
