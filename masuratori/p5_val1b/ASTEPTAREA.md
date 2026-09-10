# AȘTEPTAREA, scrisă ÎNAINTE de măsurătoarea „după" — valul 1b

*Actul al doilea, comis înainte ca bancul să ruleze. La valul 1 am prezis greșit două din cinci, iar
una dintre explicații a fost o poveste până am măsurat-o. De data asta cifrele de plecare sunt cele
măsurate, nu cele de la care am pornit inițial.*

**Ce s-a schimbat față de măsurătoarea precedentă:** cele 12 rute care întorc liste mari își
construiesc singure răspunsul — `JSONResponse(jsonable_encoder(x))` — deci codificarea se execută pe
firul handler-ului, nu în învelișul `async` de după. Nimic altceva: nicio interogare rescrisă, niciun
index în plus pe calea măsurată, `ICONTA_POOL_MAX` tot 10.

*(În aceeași tură a intrat și indexul unic al raportului Z, dar el e pe altă rută — `horeca` — care
nu e în banc, și pe o tabelă pe care ruta măsurată n-o atinge.)*

**Cifrele de plecare** (`masuratori/p5_val1/P5_MASURATORI.json`): canar în gol p95 **3,0 ms** · la
N=5000 ruta p50 **149,7 ms**, canar p95 **93,7 ms**, vârf 107,2 ms · debit k=1/2/5/10 = **22,1 ·
29,2 · 19,3 · 19,4** cereri/s · conexiuni simultane la k=10 **10 din 10**.

**Componenta pe care o mut, măsurată separat:** `jsonable_encoder` 67,6 ms + `json.dumps` 7,2 ms =
**74,9 ms** din munca de pe buclă, la N=5000.

---

## Cele cinci predicții

**P1 — canarul scade MULT, dar NU se aplatizează.** 93,7 − 74,9 ≈ 19 ms. Aștept `canar_p95` la
N=5000 **sub 35 ms**, cel mai probabil **15–25 ms**. *Nu prezic „sub 10": pe buclă rămâne parsarea
multipart a celor 196 KB de intrare, care e tot muncă proporțională cu N și pe care intervenția asta
n-o atinge.* Dacă iese sub 10, înseamnă că parsarea intrării e mai ieftină decât cred; dacă rămâne
peste 50, înseamnă că mai e ceva pe buclă pe care nu l-am găsit.

**P2 — ruta însăși rămâne cam la fel.** `durata_ruta_p50` la N=5000 în jur de **150 ms ± 25%**.
Munca nu dispare, își schimbă doar firul. *Ar putea crește puțin: codificarea concurează acum cu
alte fire pentru GIL.*

**P3 — debitul la k=10 CREȘTE peste 19,4 req/s.** Aștept **peste 25**. Nu prezic o creștere mare:
codificarea e muncă de procesor în Python, deci zece fire care codifică deodată se calcă pe GIL.
*Predicția asta e cea pe care am greșit-o la valul 1 — atunci am prezis „peste 40" și a ieșit mai
prost decât înainte. Acum plafonul îl pune GIL-ul, nu bucla, și de-aia prezic mai puțin.*

**P4 — conexiunile la k=10 rămân 10 din 10.** Plafonul pool-ului e deja atins; asta nu-l mișcă.

**P5 — zero erori, zero timeouts, zero deadlocks.** Dacă apar `PoolTimeout`-uri, înseamnă că
cererile chiar s-au suprapus mai mult decât înainte, iar valul 3 devine urgent.

---

## Ce NU se poate ști din măsurătoarea asta

* **Parsarea multipart a intrării rămâne pe buclă** și nu e atinsă de valul 1b. Dacă P1 iese pe la
  20 ms, ea e explicația restului — dar asta rămâne o deducție până se măsoară separat.
* **Ocuparea celor 40 de fire** tot nu se poate număra din afara procesului.
* **Cele 29 de căi ale valului 3 rămân neatinse**, prin regula arhitectului.
* **Octeții răspunsului** nu se compară aici, ci în suită: o probă cere ca `_raspuns(x)` să producă
  exact ce ar fi produs FastAPI singur. *Un banc care măsoară mai repede un răspuns schimbat n-ar
  măsura nimic.*
