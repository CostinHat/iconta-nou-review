# RAPORT P3 — DIAGNOSTIC | 09.09.2026 | pe commitul `6b59c19f`

**Diagnostic, fără implementare.** Nu s-a schimbat nicio linie din calea de cerere. Nu s-a mutat
nimic în cache, nu s-a atins fail-closed-ul, advisory lockul, `citeste()` set-based sau vreo gardă
P2. Ce urmează sunt măsurători și cauze demonstrate; propunerile din §6 sunt **scrise, nu făcute**.

---

## 1. CUM S-A DERIVAT LISTA RUTELOR — nu din memorie

`scripts/scan_cale_cerere.py`. O rută poate crește cu numărul de firme dacă ajunge, direct sau prin
apeluri, la funcția prin care o cerere află *care sunt firmele utilizatorului* —
`auth_api.tenantii_userului`. Se parsează `main.py` + `core/*.py` cu `ast`, se construiește graful
de apeluri pe nume simple, se ia închiderea tranzitivă a apelanților, apoi se încrucișează cu
decoratorii de rută.

**Calibrat în trei direcții** (apelant direct · apelant indirect la două niveluri · nu inventează o
rută străină) — altfel un graf care ar întoarce „toate rutele" ar părea că funcționează.

**37 de rute ating portofoliul. Doar 12 cresc cu N** — restul sunt de portal, unde poarta e
`cere_client`: un client vede **o** firmă, deci costul lui nu depinde de mărimea cabinetului.
Deosebirea se face pe poarta de autorizare, citită din `Depends(...)`, nu pe ghicite din cale.

**Ce nu vede instrumentul, declarat:** apeluri prin variabilă sau `getattr`; omonimii (două funcții
cu același nume simplu se contopesc → posibile fals-pozitive, care se văd la măsurare). Lista e un
**plafon inferior**.

---

## 2. INSTRUMENTUL — ce despică, și cum s-a dovedit că despică

`scripts/masoara_p3.py`, peste hamul HTTP din P2. Măsoară **cererea întreagă** prin `TestClient` și
o desface în:

| coloană | ce e |
|---|---|
| `db_sec` | timpul petrecut ÎN bază: durata fiecărui `execute` / `fetch*` **plus** deschiderea conexiunii, cronometrate în jurul apelului real |
| `cpu_sec` | `total_sec − db_sec` — Python: dependențele FastAPI, construirea răspunsului, serializarea JSON |
| `octeti` | mărimea răspunsului — proxy pentru serializare și rețea |

**De ce despicarea contează:** o rută poate avea **număr constant de interogări și tot să crească
liniar**, dacă lista de răspuns are N elemente. Fără despicare, „N+1 în bază" și „am de serializat N
obiecte" arată identic.

**Calibrare, ambele direcții** — și e chiar proba că separarea înseamnă ceva:

```
(a) rută care doar AȘTEAPTĂ baza (pg_sleep 0,2 s) -> db_sec 0,2021 · cpu_sec 0,0102 · db 95,2%
(b) rută care doar ARDE CPU (buclă 0,2 s)         -> db_sec 0,0000 · cpu_sec 0,2033 · db  0,0%
```

*Un instrument care ar pune tot timpul într-o singură coloană ar trece nedetectat pe orice rută
reală; numai o rută sigur de celălalt fel îl demască.*

---

## 3. DOMENIUL MĂSURĂTORII, cu limita lui scrisă

**Curba sintetică**, N = 5/50/100/250/500/1000: firme în `public.tenants`, fiecare cu schema ei, cu
nume propriu și **inexistentă pe disc** (`tenants.schema_name` e unic — schemele reale nu se pot
cicla). Pentru rutele care citesc doar modelul, e fidel: ele nu deschid nicio schemă. Pentru rutele
care deschid schema fiecărei firme, curba redă corect **FORMA creșterii** (câte interogări și
conexiuni per firmă), dar **subestimează munca** per firmă.

**De aceea costul real per firmă se măsoară separat**, pe portofoliul REAL — 14 firme, scheme
adevărate. Raportul le pune cap la cap: *forma × costul real*. Amândouă componentele sunt măsurate.

---

## 4. CURBELE BRUTE

Artefact: `masuratori/post_p2/curba_p3.json` · rulare: `masuratori/post_p2/curba_p3.iesire.txt`

### 4.1 Interogări / conexiuni

| rută | N=5 | N=50 | N=100 | N=250 | N=500 | N=1000 |
|---|---|---|---|---|---|---|
| `/control-fiscal` | 5q/3c | 5q/3c | 5q/3c | 5q/3c | 5q/3c | **5q/3c** |
| `/migrare/plan-conturi` | 5q/3c | 5q/3c | 5q/3c | 5q/3c | 5q/3c | **5q/3c** |
| `/migrare/solduri` | 5q/3c | 5q/3c | 5q/3c | 5q/3c | 5q/3c | **5q/3c** |
| `/migrare/vector` | 5q/3c | 5q/3c | 5q/3c | 5q/3c | 5q/3c | **5q/3c** |
| `/termene` | 5q/3c | 5q/3c | 5q/3c | 5q/3c | 5q/3c | **5q/3c** |
| `/tenants` | 4q/3c | 4q/3c | 4q/3c | 4q/3c | 4q/3c | **4q/3c** |
| `/migrare/istoric-declaratii` | 9q/8c | 54q/53c | 104q/103c | 254q/253c | 504q/503c | **1004q/1003c** |
| `/supervizor` | 15q/9c | 105q/54c | 205q/104c | 505q/254c | 1005q/504c | **2005q/1004c** |
| `/migrare/asociati` | 19q/13c | 154q/103c | 304q/203c | 754q/503c | 1504q/1003c | **3004q/2003c** |
| `/migrare/mijloace-fixe` | 19q/13c | 154q/103c | 304q/203c | 754q/503c | 1504q/1003c | **3004q/2003c** |
| `/migrare/salariati` | 19q/13c | 154q/103c | 304q/203c | 754q/503c | 1504q/1003c | **3004q/2003c** |
| `/migrare/parteneri` | 24q/13c | 204q/103c | 404q/203c | 1004q/503c | 2004q/1003c | **4004q/2003c** |

### 4.2 Latență totală, cu procentul petrecut în bază

| rută | N=5 | N=100 | N=1000 | db% la N=1000 |
|---|---|---|---|---|
| `/tenants` | 0,004 s | 0,006 s | **0,025 s** | 25,7% |
| `/migrare/plan-conturi` | 0,005 | 0,045 | **0,040 s** | 54,3% |
| `/migrare/solduri` | 0,005 | 0,009 | **0,042 s** | 52,0% |
| `/control-fiscal` | 0,005 | 0,010 | **0,050 s** | 50,9% |
| `/termene` | 0,005 | 0,009 | **0,053 s** | 51,2% |
| `/migrare/vector` | 0,005 | 0,009 | **0,097 s** | 22,1% |
| `/migrare/istoric-declaratii` | 0,006 | 0,037 | **0,324 s** | 66,2% |
| `/supervizor` | 0,007 | 0,053 | **0,496 s** | 71,4% |
| `/migrare/salariati` | 0,009 | 0,104 | **0,983 s** | 59,8% |
| `/migrare/mijloace-fixe` | 0,010 | 0,105 | **0,993 s** | 59,7% |
| `/migrare/asociati` | 0,010 | 0,104 | **0,995 s** | 59,8% |
| `/migrare/parteneri` | 0,016 | 0,135 | **1,317 s** | 62,1% |

*Latențele de mai sus sunt un PLAFON INFERIOR pentru rutele cu N+1 — schemele sintetice nu există,
deci munca reală per firmă lipsește din ele.*

### 4.3 Octeți de răspuns (N=1000) — costul care NU vine din interogări

| rută | octeți | per firmă |
|---|---|---|
| `/supervizor` | 592.255 | 592 B |
| `/termene` | 359.347 | 359 B |
| `/migrare/vector` | 261.311 | 261 B |
| `/control-fiscal` | 202.163 | 202 B |
| `/tenants` | 199.013 | 199 B |
| `/migrare/solduri` | 170.311 | 170 B |
| `/migrare/plan-conturi` | 154.311 | 154 B |
| cele 5 rute de status | ~90.000 | ~90 B |

### 4.4 Portofoliul REAL — 14 firme, scheme adevărate

| rută | interog | conex | total_s | db_s | cpu_s | octeți |
|---|---|---|---|---|---|---|
| `/tenants` | 4 | 3 | 0,0050 | 0,0012 | 0,0039 | 2.935 |
| `/control-fiscal` | 5 | 3 | 0,0060 | 0,0020 | 0,0041 | 9.479 |
| `/migrare/plan-conturi` | 5 | 3 | 0,0059 | 0,0019 | 0,0040 | 2.371 |
| `/migrare/solduri` | 5 | 3 | 0,0059 | 0,0018 | 0,0040 | 2.580 |
| `/migrare/vector` | 5 | 3 | 0,0059 | 0,0018 | 0,0041 | 3.982 |
| `/termene` | 5 | 3 | 0,0066 | 0,0019 | 0,0046 | 9.633 |
| `/migrare/istoric-declaratii` | 18 | 17 | 0,0098 | 0,0044 | 0,0054 | 1.446 |
| `/supervizor` | 33 | 18 | 0,0132 | 0,0066 | 0,0065 | 8.623 |
| `/migrare/mijloace-fixe` | 60 | 31 | 0,0232 | 0,0135 | 0,0096 | 1.460 |
| `/migrare/asociati` | 60 | 31 | 0,0238 | 0,0140 | 0,0098 | 1.460 |
| `/migrare/salariati` | 60 | 31 | 0,0236 | 0,0140 | 0,0097 | 1.472 |
| `/migrare/parteneri` | 60 | 31 | 0,0252 | 0,0143 | 0,0109 | 1.474 |

**Costul real per firmă**, derivat: cele patru rute de import fac **~4,3 interogări și ~2,2
conexiuni per firmă**, cu ~1 ms de bază per firmă. La 1000 de firme: ~4.300 de interogări, ~2.200 de
conexiuni, **~1 s doar timp de bază** — și asta e cifra *măsurată pe scheme reale*, nu extrapolată
din curba sintetică.

---

## 5. TOPUL COSTURILOR CARE CRESC CU N, cu cauza demonstrată

### Clasa 1 — N+1 pe conexiuni și interogări (6 rute)

Ordonate după costul măsurat la N=1000:

| # | rută | la N=1000 | per firmă | cauza, la linie |
|---|---|---|---|---|
| 1 | `/migrare/parteneri` | 4004q / 2003c / 1,32 s | 4q + 2c | `main.py:2310` `for f in firme:` → `schema_tenant` (conexiune proprie) + `get_conn(schema)` + `solduri_parteneri_api.rezumat(c)` |
| 2 | `/migrare/asociati` | 3004q / 2003c / 0,99 s | 3q + 2c | `main.py:2441` → `schema_tenant` + `get_conn(schema)` + `asociati_import_api.rezumat(c)` |
| 3 | `/migrare/mijloace-fixe` | 3004q / 2003c / 0,99 s | 3q + 2c | `main.py:2540` → idem, `mijloace_fixe_import_api.rezumat(c)` |
| 4 | `/migrare/salariati` | 3004q / 2003c / 0,98 s | 3q + 2c | `main.py:2380` → idem, `salariati_import_api.rezumat(c)` |
| 5 | `/supervizor` | 2005q / 1004c / 0,50 s | 2q + 1c | `main.py:2880` `for f in ale_mele:` → `with db.get_conn() as c: schema_tenant(...)`, **o conexiune per firmă doar ca să rezolve schema și accesul** |
| 6 | `/migrare/istoric-declaratii` | 1004q / 1003c / 0,32 s | 1q + 1c | `main.py:2592` → `istoric_declaratii_import_api.rezumat(c, tid)`, o conexiune per firmă (citește din `public`, **nu deschide schema**) |

**Cauza e aceeași pentru primele patru, și e chiar tiparul pe care P2 l-a scos din celelalte trei
rute surori:** o buclă per firmă care deschide **două** conexiuni — una ca să afle schema, alta ca
să citească din ea. Cele trei rute vecine (`/migrare/solduri`, `/migrare/plan-conturi`,
`/migrare/vector`) au fost convertite la modelul de citire în P2; **aceste patru au rămas**.

**`/supervizor` e un caz aparte, și merită numit exact:** P1 a rezolvat partea scumpă — rezultatele
se citesc **set-based**, într-o singură interogare (`supervizor_cache.citeste`, `main.py:2899`). Ce
a rămas e o buclă **înaintea** ei, care rezolvă schema și accesul firmă cu firmă. Deci nu e o
regresie a lui P1; e o bucată pe care P1 n-a atins-o fiindcă nu era în domeniul lui.

**Cifra care doare nu e numărul de interogări, ci de CONEXIUNI.** Pool-ul are `maxconn = 10`
(implicit, `ICONTA_POOL_MAX` nesetat). O cerere care cere 2.003 conexiuni le ia și le dă înapoi
secvențial — nu se blochează singură, dar **ține pool-ul ocupat 2.003 de ori**, iar utilizatorii
concurenți se serializează pe el.

### Clasa 2 — payload și serializare (toate cele 12, inclusiv cele „constante")

Rutele convertite în P2 au **număr constant de interogări** și tot cresc liniar în latență:
`/control-fiscal` 0,005 → 0,050 s, `/termene` 0,005 → 0,053 s. Cauza e demonstrată de despicare:
la N=1000, **~50% din timp e în bază** (aducerea a N rânduri) și **~50% în Python** (construirea
listei + serializarea JSON).

`/tenants` e cazul curat: **4 interogări la orice N**, dar **74% din timp e CPU** — nu are ce citi
în plus, are ce serializa în plus.

`/supervizor` are cel mai mare răspuns: **592 KB la 1000 de firme**, fiindcă întoarce constatările
întregi, nu un rezumat.

*Asta e o clasă de cost pe care niciun read-model n-o rezolvă: dacă răspunsul are N elemente,
cineva tot trebuie să-l construiască, să-l serializeze și să-l trimită.*

### Ce NU crește

Cele cinci rute convertite în P2 plus `/tenants`: **numărul de interogări și de conexiuni e constant
la orice N**, confirmat din nou aici, independent de gărzile P2.

---

## 6. PROPUNEREA MINIMĂ DE REMEDIERE — **scrisă, NU implementată**

Ordonată după raport cost/beneficiu măsurat. Fiecare punct e minim prin construcție: nu cere
mecanism nou, ci folosește unul care există și e deja gardat.

### 6.1 `/supervizor` — cea mai ieftină reparație din listă

**Ce:** rezolvarea schemei și a accesului, **într-o singură interogare** pentru tot portofoliul, în
loc de o conexiune per firmă. `tenantii_userului` întoarce deja `schema_name`; bucla o recere prin
`schema_tenant` doar ca să verifice accesul — verificare pe care apartenența la cabinet o dă deja.

**Câștig măsurat (proiecție din cifrele de mai sus):** 2005q/1004c → ~5q/3c. **Efect zero asupra
prospețimii** — nu atinge modelul de citire, doar rezolvarea de schemă.

**Risc:** trebuie păstrată exact semantica de acces (o firmă la care userul n-are acces se sare, nu
se afișează). Se probează cu un test de izolare, care există deja ca tipar.

### 6.2 Cele patru rute de status — aspecte noi în modelul de citire existent

**Ce:** `asociati`, `mijloace_fixe`, `parteneri`, `salariati` devin patru aspecte în
`firma_rezumat.ASPECTE`, calculate de lucrător, citite set-based — **exact drumul deja parcurs**
pentru `solduri`, `plan_conturi` și `vector`.

**Câștig:** 4×(3004q/2003c) → 4×(5q/3c).

**Costul mutat, declarat:** patru aspecte în plus înseamnă mai multă muncă pentru lucrător și mai
multe surse de invalidare. Payloadul lor e mic (~90 B/firmă), deci clasa 2 nu se agravează.

**Obligatoriu, prin regula deja scrisă în `GARZI.md`:** fiecare aspect nou vine în același commit cu
(1) sursele în registru, (2) fixtura care activează ramura, (3) testul că sursa e observată, (4)
testul de invalidare.

### 6.3 `/migrare/istoric-declaratii` — o singură interogare, fără model nou

**Ce:** `istoric_declaratii_import_api.rezumat(c, tid)` citește din `public`, pe `tenant_id`. Se
poate cere **pentru toate firmele deodată**, cu `WHERE tenant_id = ANY(...)` și un `GROUP BY`.

**Câștig:** 1004q/1003c → ~5q/3c, fără niciun aspect nou și fără nicio dependență de prospețime.
*E cea mai mică schimbare din listă și n-are legătură cu modelul de citire.*

### 6.4 Clasa 2 (payload) — cere o decizie, nu o optimizare

Nu propun nimic tehnic aici, fiindcă întrebarea e de produs: **are un contabil nevoie de toate cele
1000 de firme într-un singur răspuns?** Variantele obișnuite — paginare, câmpuri reduse, filtrare pe
server — schimbă contractul ecranelor. La 592 KB (`/supervizor`) și 359 KB (`/termene`) merită pusă
întrebarea; la 0,05 s pentru celelalte, nu urgent.

### Ce NU propun

Cache nou, event bus, denormalizare suplimentară, atingerea advisory lockului, a fail-closed-ului
sau a semanticilor `CURENT`/`INVALIDAT`/`EROARE`. Nimic din ce e demonstrat nu cere așa ceva.

---

## 7. RISCURI DE PROSPEȚIME ȘI CONCURENȚĂ

**Prospețime.** §6.2 e singurul punct care introduce prospețime unde azi nu există: cele patru rute
citesc **acum** date proaspete direct din schema firmei. Trecerea la modelul de citire înseamnă că
vor putea arăta `invalidat`/`lipseste` — corect, dar **e o schimbare de contract al ecranului**, nu
doar de performanță. Ecranul trebuie să știe să arate starea, cum o fac deja cele cinci convertite.

**§6.1 și §6.3 nu ating prospețimea deloc** — de aceea le pun primele.

**Concurență.** Riscul real e **pool-ul**, nu blocajele: `maxconn = 10`, iar rutele din clasa 1 cer
peste 2.000 de conexiuni per cerere. Doi utilizatori care deschid simultan ecranul de parteneri pe
un cabinet mare se serializează pe pool. Reparațiile din §6 îl scad la 3 conexiuni per cerere, deci
riscul dispare odată cu cauza.

**Lucrătorul.** Patru aspecte în plus cresc lotul: la 1000 de firme, backlogul complet trece de la 5
la 9 perechi per firmă. Metricile există deja (`p2_worker_remaining`,
`p2_oldest_pending_age_seconds`) — deci efectul ar fi **vizibil**, nu presupus.

---

## 8. R177 NU SE DESCHIDE ÎN P3

Comanda cere să nu fie deschisă decât dacă măsurătoarea demonstrează **aceeași cauză**. Nu o
demonstrează, și se poate spune precis de ce:

**R177** e despre un model de citire ale cărui **dependențe au fost scrise din memorie** — o valoare
veche arătată drept `curent`. Cele șase rute din clasa 1 **n-au niciun model de citire**: citesc
direct din schema firmei, la fiecare cerere. Sunt proaspete prin construcție; defectul lor e de
**cost**, nu de adevăr.

Legătura ar apărea abia dacă se implementează §6.2 — atunci cele patru aspecte noi *ar deveni*
purtători ai clasei R177, și **de-aia regula din `GARZI.md` le cere fixtura și testul de invalidare
în același commit**. Până atunci R177 rămâne separată, deschisă, netratată.

---

## 9. TESTE DE ACCEPTARE PROPUSE — pentru o eventuală remediere

Scrise acum, ca să nu fie inventate după implementare.

| # | test | criteriu |
|---|---|---|
| 1 | `test_p3_endpoint_query_count_toate_cele_12` | pe **toate** cele 12 rute derivate: 5 firme vs 50 → același număr de interogări **și** de conexiuni |
| 2 | `test_p3_conexiuni_sub_plafonul_poolului` | nicio rută nu cere mai multe conexiuni decât `maxconn` într-o singură cerere |
| 3 | `test_p3_paritate_status_import` | pentru fiecare din cele 4 rute de status: răspunsul de dinainte și de după, **întreg**, fără normalizare |
| 4 | `test_p3_supervizor_acces_neschimbat` | o firmă la care userul n-are acces **rămâne** absentă din răspuns după batching |
| 5 | `test_p3_aspect_nou_invalideaza` | pentru fiecare aspect nou: scriere în sursă → `invalidat`; scriere în sursă străină → **rămâne** `curent` |
| 6 | `test_p3_ramura_noua_e_acoperita` | regula din `GARZI.md`, aplicată: fiecare sursă nouă are fixtură și e observată |
| 7 | `test_p3_payload_declarat` | mărimea răspunsului per firmă rămâne sub un plafon scris, ca o creștere de payload să fie o decizie, nu o surpriză |

**Instrumentul există deja** — `scripts/masoara_p3.py` produce toate cifrele de care au nevoie
testele 1, 2 și 7; nu trebuie construit nimic nou ca să se poată verifica.

---

## 10. CE NU ACOPERĂ ACEST DIAGNOSTIC

- **Doar `GET`-uri de cabinet, fără parametru de cale.** Un `POST` de portofoliu ar schimba date, iar
  o măsurătoare care scrie nu se poate repeta identic.
- **O singură cerere pe rând, fără concurență.** Efectul pool-ului sub sarcină simultană e
  **argumentat** din numărul de conexiuni, **nu măsurat**. O măsurătoare de concurență e o temă
  separată.
- **Latențele sintetice ale rutelor cu N+1 sunt plafoane inferioare** (schemele nu există). Costul
  real per firmă vine din §4.4.
- **Cele 25 de rute de portal** n-au fost măsurate: poarta lor e `cere_client`, deci văd o firmă.
- **Nu s-a măsurat frontendul** — câte cereri face un ecran la deschidere. Instrumentul are deja
  `--ecrane` pentru asta; n-a intrat în domeniul cerut.
