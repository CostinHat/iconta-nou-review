# CONFRUNTAREA — măsurătoarea „după" valul 1, față de `ASTEPTAREA.md`

*Actul al treilea. Așteptarea a fost scrisă și comisă înainte ca bancul să ruleze. **Două din cinci
predicții au ieșit greșit**, iar una dintre ele mi-a răsturnat explicația. Se scrie ce a ieșit, nu
se rescrie așteptarea.*

| | înainte (`8ce4cd84`) | după (valul 1) | predicția | verdict |
|---|---|---|---|---|
| canar p95 la N=5000 | 117,9 ms | **93,7 ms** | „sub 10 ms" | **GREȘIT** |
| canar max la N=5000 | 158,7 ms | 107,2 ms | — | — |
| ruta p50 la N=5000 | 143,0 ms | **149,7 ms** | „143 ± 25%" | **CORECT** |
| debit la k=10 | 22,15 req/s | **19,4 req/s** | „peste 40 req/s" | **GREȘIT, și invers** |
| conexiuni simultane la k=10 | 8 din 10 | **10 din 10** | „10 din 10" | **CORECT** |
| erori / timeouts / deadlocks | 0 | **0** | „zero" | **CORECT** |
| martor sincron, canar p95 | 3,8 ms | 4,3 ms | — | neschimbat |

---

## P1 a ieșit greșit. Prima explicație a fost și ea greșită.

**Ce am crezut întâi:** că vinovat e GIL-ul — parsarea e muncă de procesor în Python, iar un fir nu
o face paralelă. **Am măsurat, în loc să deduc**, și explicația a căzut: pe N=5000, în proces, fără
server și fără bază,

```
parse_extras       p50 =  12,3 ms
bucla regulilor    p50 =  26,2 ms
TOTAL procesor pur p50 =  38,5 ms      din cei 149,7 ms ai rutei
```

38,5 ms nu pot produce o coadă de 93,7 ms la canar. *O explicație plauzibilă care nu se măsoară e o
poveste.*

## Cauza adevărată: ce am mutat de pe buclă e handler-ul, nu răspunsul

Ruta întoarce **5000 de tranzacții** — aproape **1 MB** de JSON. FastAPI **nu** serializează
răspunsul în handler: îl trece prin `jsonable_encoder` și `json.dumps` în învelișul `async` de
după, adică **pe buclă**, indiferent dacă handler-ul e `def` sau `async def`. Măsurat pe același
răspuns:

```
corpul cererii:        195,9 KB
răspunsul serializat:  998,3 KB
  jsonable_encoder  p50 = 67,6 ms     <-- PE BUCLĂ, orice-aș face cu handler-ul
  json.dumps        p50 =  7,2 ms     <-- tot pe buclă
  TOTAL ieșire      p50 = 74,9 ms
```

**74,9 ms de muncă rămasă pe buclă explică 93,7 ms de coadă la canar** — restul e parsarea
multipart a celor 196 KB de intrare, tot pe buclă.

**Comparația de altă instanță, care închide argumentul.** Martorul sincron —
`GET /tenants/{id}/facturi` — e tot un handler `def`, tot în threadpool, tot cu acces la bază: canar
p95 **4,3 ms, plat**. Singura diferență e mărimea răspunsului. *Același mecanism, două rezultate
opuse, o singură variabilă.*

**Ce înseamnă asta pentru inventarul P5:** detectorii au căutat I/O blocant **în codul nostru**.
Serializarea răspunsului nu e în codul nostru, e în framework — deci n-a fost văzută de niciun
detector, și nu figurează în niciunul din cei 94 de candidați. **E o oarbire prin construcție a
inventarului, descoperită abia măsurând reparația.**

## P3 a ieșit greșit, și în direcția proastă

Debitul la k=10 a scăzut de la 22,15 la 19,4 cereri/s (total 451,5 → 514,6 ms). Aștept**am** o
creștere, fiindcă zece fire pot lucra deodată. N-au putut: cât timp bucla încă serializează
serializarea răspunsurilor, cele zece cereri se aliniază tot acolo — iar acum plătesc și zece
conexiuni ținute simultan, în loc de opt. *Planul o spune direct: „o intervenție care îmbunătățește
p50 și înrăutățește p95 nu e o îmbunătățire" (`PLAN_HARDENING.md:336`). Aici s-a îmbunătățit coada
canarului cu 20% și s-a înrăutățit debitul cu 12%.*

## P4 a ieșit corect, și e vestea care contează pentru valul 3

Conexiunile simultane au urcat de la **8 din 10** la **10 din 10** — plafonul atins. Exact ce am
scris înainte de măsurătoare: *blocarea buclei ASCUNDEA presiunea pe pool.* Valul 1 n-a creat
problema, a făcut-o vizibilă. **Zero `PoolTimeout` în jurnalul serverului**, deci s-a atins
plafonul fără să se rupă nimic — încă.

---

## Ce e închis și ce nu

**Închis:** cele 16 rute nu mai țin bucla cu propria lor muncă. Pentru cele **4** care ajung la
rețea, `sleep` sau disc — `POST /migrare/fisier`, `POST /migrare/incarca`, `POST /portal/bon`,
`POST /raportari/mesaj/{mid}/imagine` — câștigul e întreg, fiindcă acele primitive eliberează
GIL-ul cât așteaptă. **`POST /migrare/fisier`, calea cerută cu prioritate, era cazul cel mai grav:
`time.sleep(1.1)` la fiecare 100 de CUI-uri, pe buclă. Un fișier cu 500 de CUI-uri îngheța
aplicația 4,4 secunde. Acum ține un fir, nu bucla.** Efectul ăsta nu se vede în tabelul de sus:
bancul măsoară altă rută, iar aceasta n-a fost chemată fiindcă ar fi însemnat apeluri reale la ANAF.

**NEînchis:** pentru cele **12** rute care întorc liste mari, coada canarului rămâne dominată de
serializarea răspunsului, care e în afara handler-ului. Valul 1 era necesar, dar nu e suficient
pentru ele.

**Neatins:** `POST /tenants/{id}/horeca/import-amef` — v. rândul ei din `core/p5_clasificare.py`.
