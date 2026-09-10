# UNDE STAU CELE ~460 ms — profilul cererii, măsurat din interiorul ei

*Instrumentare în codul de producție, cerută și aprobată separat pe 10.09.2026. Inertă fără
`ICONTA_CRONOMETRU=1`. Până acum, din afară se vedea numai totalul; dinăuntru, numai ce e după
intrarea în handler. Reperele de mai jos acoperă tot drumul, iar restul neacoperit se numără.*

## Profilul, la k=10, N=250 (mediană pe cerere, ms)

| segment | k=1 | k=2 | k=5 | **k=10** | ce e |
|---|---|---|---|---|---|
| `intrare` | 21,6 | 42,1 | 78,8 | **138,7** | de la trimitere până la primul middleware: citirea corpului de uvicorn, dispecerizarea ASGI |
| `mw_edge` + `mw_audit` | 0,1 | 0,1 | 0,2 | **1,3** | cele trei middleware-uri ale casei, la intrare |
| `intrare-handler` | 3,0 | 13,8 | 55,5 | **105,7** | între ultimul middleware și prima linie a handler-ului: parsarea multipart, rezolvarea dependențelor (`cere_cabinet`), trecerea pe fir |
| `conexiune` | 0,0 | 0,0 | 21,8 | **45,4** | obținerea unei conexiuni din pool |
| `acces` | 0,5 | 2,2 | 30,3 | **67,1** | interogarea `schema_tenant` |
| `parsare` + `reguli` | 2,6 | 3,6 | 3,1 | **2,7** | **munca proprie a rutei** |
| `inainte-serializare` | 0,0 | 0,0 | 0,0 | **0,0** | (serializarea e acum pe fir, v. valul 1b) |
| `iesire` | 2,5 | 13,0 | 44,1 | **94,8** | de la ultima linie a handler-ului până la primirea răspunsului: scrierea de audit + transmiterea |
| `nemasurat` | 4,7 | 4,8 | 5,3 | **5,8** | rest neacoperit de repere |
| **total** | **35,0** | **68,1** | **236,3** | **457,2** | |

**Contabilitatea se închide:** restul neacoperit rămâne 5,8 ms la orice k. *Un profil care nu se
închide n-ar fi un profil, ar fi o împărțire a totalului.* (Prima formă calcula restul din mediane și
ieșea **−14 ms** la k=2 — medianele unor segmente diferite nu aparțin aceleiași cereri. Se calculează
acum per cerere, apoi se ia mediana lui.)

## Ce spune profilul

**Munca proprie a rutei e 2,7 ms din 457.** Handler-ul — cel pe care l-am reparat de două ori în
campania asta — nu e nici pe departe unde stă timpul.

**74% e în afara handler-ului**: `intrare` 138,7 + `intrare-handler` 105,7 + `iesire` 94,8 = **339 din
457 ms**. Alea sunt transport, parsare de corp, rezolvare de dependențe și scriere de audit.

**Verificarea de acces costă 112,5 ms** (`conexiune` 45,4 + `acces` 67,1), față de **0,5 ms** la k=1.
O interogare simplă, de 130 de ori mai lentă sub concurență.

## Cele două experimente care exclud explicațiile evidente

**Nu e capacitatea unui singur proces uvicorn.** Aceeași rafală, singura variabilă `--workers`:

```
1 lucrător   k=10   348,4 ms   28,7 req/s
2 lucrători  k=10   500,1 ms   20,0 req/s      <-- mai RĂU
```

Doi lucrători au înrăutățit-o cu 44%. *Dacă bucla unui singur proces ar fi fost plafonul, al doilea
proces ar fi ajutat.*

**Mașina e aproape plină.** În timpul rafalei, procesorul OCUPAT pe toată mașina — toate procesele —
e **1,57 din 2 nuclee, adică 79%**. Din care procesul-server 0,47 și sonda 0,57; restul, prin
scădere, e PostgreSQL plus nucleul.

*Măsurătoarea directă a lui PostgreSQL a EȘUAT și n-o raportez ca cifră: însumarea pe procese a ieșit
**negativă** (−340 ms), fiindcă backend-urile se creează și dispar între cele două eșantioane, iar
unul care a ieșit nu mai e în `/proc`. Cifra prin scădere e o deducție, nu o măsurătoare — se scrie
ca atare.*

## RĂSPUNSUL LA ÎNTREBAREA PUSĂ: valul 3 NU e remediul

Valul 3 vizează **apeluri externe executate cât timp e ținută o conexiune din pool**. Ruta măsurată
**nu face niciun apel extern**. Niciunul din cele nouă segmente de mai sus nu e tiparul pe care valul
3 îl repară, iar cele două cifre mari — `intrare` și `intrare-handler` — se petrec înainte ca ruta să
atingă vreo conexiune.

**Deci strangularea e altundeva**, și e de trei feluri, în ordinea mărimii:

1. **Costul per cerere al cadrului și al transportului** (339 ms din 457). Nu e cod de-al nostru:
   citirea corpului, parsarea multipart, rezolvarea dependențelor, scrierea de audit. Scade dacă
   scade **mărimea corpului și a răspunsului**, sau dacă cererea nu mai trece prin toate straturile.
2. **Verificarea de acces**, 112 ms din 457 — o interogare pe cerere, care sub concurență se
   scumpește de 130 de ori. E singurul punct din listă care e **al nostru** și se poate atinge
   direct.
3. **Capacitatea mașinii**: 2 nuclee, 79% ocupate, cu sonda pe aceleași nuclee. **Orice cifră de
   debit măsurată aici e un plafon inferior**, iar comparațiile între rulări sunt valide numai
   fiindcă sonda e identică.

## Ce NU știu, și nu presupun

* **Cât din `intrare` e citirea corpului și cât e dispecerizarea** — reperul e pus la primul
  middleware, deci înainte de el totul e o singură cutie. S-ar despărți instrumentând la nivel ASGI,
  sub middleware.
* **De ce `acces` se scumpește de 130 de ori.** Poate fi așteptare pe pool (dar `conexiune` e
  măsurat separat), poate fi PostgreSQL sub presiune, poate fi firul care nu e programat. **Nu aleg
  între ele fără o măsurătoare** — în campania asta am ghicit cauza de trei ori și am greșit de
  fiecare dată.
* **Cum arată toate astea pe o mașină cu mai multe nuclee.** Toate cifrele de aici poartă limita de
  2 nuclee.
