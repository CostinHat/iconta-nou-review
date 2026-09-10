# CONFRUNTAREA — măsurătoarea „după" valul 1b, față de `ASTEPTAREA.md`

*Actul al treilea. Așteptarea a fost comisă înainte ca bancul să ruleze. **Trei predicții din cinci
au ieșit corecte, una la limită, una greșită** — iar căutarea cauzei ei a scos un defect al
bancului care schimbă cum se citesc TOATE cifrele de debit din P5.*

| | val 1 | val 1b | predicția | verdict |
|---|---|---|---|---|
| canar p95 @N=5000 | 93,7 ms | **33,2 ms** | „sub 35, probabil 15–25" | **CORECT la prag, greșit la interval** |
| canar vârf @N=5000 | 107,2 ms | **66,2 ms** | — | — |
| canar p95 @N=2500 | 60,2 ms | **30,2 ms** | — | — |
| ruta p50 @N=5000 | 149,7 ms | 163,6 ms | „150 ± 25%, poate crește puțin" | **CORECT** |
| debit @k=10 | 19,4 req/s | **23,7 req/s** | „peste 25" | **GREȘIT** |
| conexiuni @k=10 | 10/10 | 8/10 | „rămân 10/10" | **GREȘIT** |
| erori / timeouts / deadlocks | 0 | **0** | „zero" | **CORECT** |

---

## P1 — reparația a funcționat, dar intervalul meu a fost optimist

Canarul la N=5000 a scăzut de la **93,7** la **33,2 ms**, iar de la începutul lui P5 (117,9 ms) e o
scădere de **72%**. Am prezis „sub 35" — corect la un fir de păr — dar „cel mai probabil 15–25" a
fost prea optimist. Aritmetica mea scădea 74,9 ms de codificare din 93,7; realitatea a scăzut 60,5.
Diferența e muncă pe buclă pe care n-am numărat-o: parsarea multipart a intrării, și partea din
codificare care oricum nu se putea muta.

**Linia de bază a canarului e neschimbată (3,0 ms), martorul sincron la fel (3,7 ms).** Deci
scăderea nu vine dintr-o mașină mai odihnită.

## P3 a ieșit greșit — și căutându-i cauza am găsit că bancul se măsura pe SINE

Am prezis debit peste 25 la k=10; a ieșit 23,7. Dar cifra de la care porneam, **19,4, nu era o
măsurătoare a aplicației**.

**Cum s-a văzut.** Nu am dedus, ca la valul 1. Am măsurat, în ordinea asta:
1. **Cât consumă serverul.** `procesor / perete = 0,47` la orice k. Deci procesul-server stă degeaba
   jumătate din timp — **nu e saturat**, prin urmare nu GIL-ul lui e plafonul;
2. **E pool-ul?** Aceeași rafală, singura variabilă schimbată: `ICONTA_POOL_MAX` 10 → 40, numai pe
   serverul de probă. **381 ms → 379 ms.** Nu pool-ul. *(Pool-ul a fost mărit ca SONDĂ, pe un proces
   de probă, ca să aflu dacă el e cauza — nu ca să arate cifra mai bine. Producția n-a fost atinsă,
   iar cifrele raportate sunt cele de la pool-ul real.)*
3. **Atunci cine?** Am măsurat consumul **sondei**: la k=2, `procesor / perete = 0,98`. **Bancul
   trimitea cele k cereri din k FIRE ale unui singur proces Python** — fiecare construind un corp
   multipart și despachetând un JSON. Toate pe același GIL. *La k=2 sonda era saturată complet.*

**Ce înseamnă:** cifrele de debit de la k=2/5/10 din tot P5 — inclusiv „debitul e plat, concurența
nu cumpără nimic", pe care am pus-o în raport ca descoperire — **descriau bancul, nu aplicația**.

**Ce s-a reparat.** Cererile pleacă acum din **k procese**, nu din k fire. Bazinul se **încălzește
înainte de ceas** (fără asta, la k=1 ceasul arăta 65,5 ms pentru o cerere de 37 — restul era
pornirea proceselor; aceeași lecție ca la canar, care își plătea instalarea TCP). Și, mai important:
**bancul își măsoară și își raportează propria saturare**. Fiecare rând poartă `saturare_client` și
`DEBIT_DEMN_DE_INCREDERE`; la rularea asta, 0,30–0,38 și `True`.

## Ce spun cifrele de debit ACUM, cu un banc de încredere

```
k=1   27,5 req/s     k=2   28,5 req/s     k=5   23,9 req/s     k=10  23,7 req/s
```

**Tot plat.** Deci concluzia veche era adevărată — dar a fost adevărată **din întâmplare**, sprijinită
pe o măsurătoare care nu o dovedea. *O concluzie corectă obținută dintr-o cifră greșită rămâne o
concluzie nesusținută, și de-aia se rescrie, nu se păstrează fiindcă „oricum era așa".*

**Ce s-a exclus, măsurat:** nu e clientul (saturare 0,32), nu e pool-ul (10 vs 40, identic), nu e
saturarea de procesor a serverului (0,47).

**Ce rămâne DESCHIS, și nu inventez o explicație:** la k=10 aplicația face 180 ms de procesor în 422
ms de perete, cu 8 conexiuni din 10 folosite simultan, zero erori și zero așteptări la pool — și
totuși fiecare cerere durează de zece ori mai mult decât singură. Ceva nu se suprapune, și n-am
măsurat încă ce. **Am greșit de două ori în campania asta ghicind cauza înainte s-o măsor; a treia
oară nu mai ghicesc.** Următoarea măsurătoare care ar închide întrebarea: cronometrarea pe segmente
în interiorul cererii — dar aia cere instrumentare în codul de producție, deci se cere întâi.

## P4 — conexiunile au scăzut, nu au rămas

8 din 10 la k=10, față de 10 din 10 la valul 1. Predicția a fost greșită, dar în direcția bună: cu
mai puțin timp petrecut pe buclă, cererile stau mai puțin cu conexiunea în mână. **Nu e o
îmbunătățire pe care s-o pot revendica** — e o consecință, și e sub pragul de zgomot al unei singure
rulări.

## Ce e închis și ce nu

**Închis:** ce cere planul la `:328` — *„rutele în care un I/O blocant ține bucla de evenimente
ocupată"*. Pentru cele 12 rute, bucla nu mai e ținută nici de handler, nici de serializarea
răspunsului. Canarul o arată: **117,9 → 33,2 ms**, cu linia de bază neschimbată.

**Neînchis:** de ce nu crește debitul. E o întrebare de **capacitate**, nu de buclă — și e chiar
teritoriul valului 3, dar valul 3 nu se pornește pe o cauză nemăsurată.
