# AȘTEPTAREA, scrisă ÎNAINTE de măsurătoarea „după" — valul 1

*`METODA_VERIFICARE.md` §1: cele trei acte sunt observația, **așteptarea scrisă înainte**, și
comparația de altă instanță. Fișierul ăsta e actul al doilea, și e comis **înainte** ca bancul să
ruleze a doua oară. Dacă o predicție iese greșit, se scrie că a ieșit greșit — nu se rescrie
așteptarea ca să se potrivească.*

**Ce s-a schimbat între cele două măsurători:** 16 din cele 17 rute ale valului 1 au trecut din
`async def` în `def`, deci Starlette le mută pe un fir din cele 40 ale limitatorului. Ruta subiect
a bancului — `POST /tenants/{id}/banca/parse-extras` — e una dintre ele. Nimic altceva: nici o
interogare n-a fost rescrisă, nici un index n-a fost adăugat, `ICONTA_POOL_MAX` a rămas 10.

**Cifrele de la care se pleacă** (`masuratori/p5/P5_MASURATORI.json`, pe `8ce4cd84`):
canar în gol p95 **3,4 ms** · la N=5000 ruta p50 **143,0 ms** și canar p95 **117,9 ms**, vârf
**158,7 ms** · martor sincron canar p95 **3,8 ms** · debit k=1/2/5/10 = **23,05 · 22,59 · 24,19 ·
22,15** cereri/s · conexiuni simultane maxime **1 · 2 · 4 · 8** din 10.

---

## Cele cinci predicții

**P1 — canarul se aplatizează.** La N=5000, `canar_p95` scade de la 117,9 ms la ordinul martorului
sincron, adică **sub 10 ms**. *Motivul: munca n-a dispărut, s-a mutat de pe buclă; canarul măsoară
bucla.* Dacă rămâne peste 30 ms, intervenția n-a atins cauza și trebuie recitită.

**P2 — ruta însăși NU se accelerează.** `durata_ruta_p50` la N=5000 rămâne în jur de **143 ms
± 25%**. *Nu am făcut nimic mai rapid; am mutat unde se execută.* O scădere mare ar fi suspectă —
ar însemna că măsor altă ramură.

**P3 — debitul începe să CREASCĂ cu k.** Azi e plat (22-24 req/s la orice k), fiindcă bucla
serializează. Cu 10 fire, la **k=10** aștept **peste 40 cereri/s** — nu 10× (pool-ul, GIL-ul și
baza pun propriile plafoane), dar clar peste linia plată. *Asta e proba că serializarea era a
buclei, nu a bazei.*

**P4 — `MAX_SIMULTANEOUS_RESOURCE_USE` URCĂ, și asta e vestea proastă din vestea bună.** Azi la
k=10 se ating 8 conexiuni din 10. Aștept ca acum să se atingă **10 din 10**, adică plafonul. *E
chiar argumentul pentru care valul 3 nu e opțional: blocarea buclei ASCUNDEA presiunea pe pool.
Dacă predicția asta iese, valul 1 n-a creat problema — a făcut-o vizibilă.*

**P5 — zero erori, zero timeouts, zero deadlocks**, ca înainte. Dacă apar `PoolTimeout`-uri la
k=10, atunci P4 s-a adeverit mai tare decât mă așteptam: pool-ul nu doar se atinge, ci se **umple**,
iar valul 3 devine urgent, nu doar necesar.

---

## Ce NU se poate ști din măsurătoarea asta

* **Cele 40 de fire nu se pot număra din afara procesului.** Dacă ele devin noul plafon, măsurătoarea
  n-o va arăta direct — se va vedea doar ca debit care nu mai crește. Rămâne declarat nemăsurat.
* **`horeca_import_amef` nu e în banc.** Rămâne `async def`, deci încă ține bucla; efectul ei nu
  intră în nicio cifră de mai jos.
* **Cele 29 de căi ale valului 3 n-au fost atinse și nu se măsoară** — ar cere apeluri reale la
  ANAF/SPV.
