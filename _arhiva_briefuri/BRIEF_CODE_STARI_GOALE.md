# BRIEF_CODE_STARI_GOALE — clasa canonica pentru stare goala

## Decizie luata (Costin, DA 17.07.2026)

DESIGN_SYSTEM.md cap. 6 primeste un concept nou, v2.13,
intre "mesaj de stare" si "ghidaj de camp":

> **Stare goala (v2.13).** Lista cu zero randuri NU e mesaj de stare — nu se
> afiseaza prin `arataMesaj()`. Nu s-a intamplat nicio actiune; e continut de
> ecran, nu feedback tranzitoriu. Clasa canonica unica: `.stare-goala`.
> `mig-gol` / `cap-gol` / `sa-gol` se elimina.
> Trei parti obligatorii:
>   1. **golul** — ce lipseste
>   2. **cauza** — de ce e gol; daca e preconditie neindeplinita, cu temei
>   3. **iesirea** — butonul care repara, SAU regula sistemului pe care omul
>      n-o stia (cand golul e normal: n-a inceput inca)
> Fundatura interzisa: "Niciun X." fara cauza si fara iesire.

## De ce a aparut abaterea (nu e neglijenta)

Cap. 6 spune DEJA "INTERZIS mesaj de stare prin innerHTML cu clase ad-hoc
(mig-gol, pf-intro, span inline)". Regula exista si e incalcata ~20 de ori, LIVE.

A supravietuit fiindca `arataMesaj` acopera doar ok/eroare/avert/info — feedback
dupa o actiune. Starea goala nu e feedback dupa actiune; nu s-a intamplat nimic,
lista pur si simplu are zero randuri. Cap. 6 n-avea canonic pentru asta.
Programatorul a avut dreptate sa nu forteze `arataMesaj`, si greseala sa inventeze
clasa. v2.13 astupa gaura, nu adauga birocratie.

## Modelele bune (sursa formularii — NU le strica)

- static/js/ecrane/produse_ecran.js:52 — "Niciun produs inca. Adauga primul
  produs — cota se completeaza automat." -> preda un COMPORTAMENT al sistemului.
- static/js/ecrane/firme.js:1824 — "Niciun document de verificat. Clientii
  pozeaza, aici certifici." -> preda IMPARTIREA MUNCII.

Ambele au textul corect si clasa gresita. Se pastreaza textul, se schimba clasa.

## Precedent deja aplicat

F145 (LIVE 17.07) implementeaza regula: referinta partener disparuta ->
gol + cauza + iesire. Un ecran o respecta, ~20 o incalca.

## FAZA 1 — inventar + propunere. STOP inainte de cod.

1. Inventar COMPLET. Grep-ul initial a fost `head -20`, deci partial. Cauta si
   alte formulari: "Nicio", "Nimic", "0 rezultate", "inca", liste cu fallback ca
   parametru (firme.js:1114-1116 — functia `lista()` cu text de gol ca argument),
   text inline (firme.js:709 "niciun raspuns nou").

   Cunoscute pana acum: tipare.js:65, admin_gratuite.js:21, admin_activitate.js:26
   si :119, firme.js:336/655/1195/1824/2146, capacitate.js:43, produse_ecran.js:52,
   cabinet.js:111, asistenti.js:70/77.

2. Tabel per aparitie: fisier:linie | clasa azi | text azi | gol normal SAU
   preconditie neindeplinita | cauza (cu temei, daca e preconditie) | iesire
   propusa (buton + ruta, sau regula predata).

3. **Textele sunt voce de produs — le PROPUI, nu le scrii inca.** Costin aproba
   tabelul. Nu inventa temeiuri; daca o cauza nu se poate verifica la sursa,
   marcheaz-o "de stabilit cu Costin", nu ghici.

4. Doua intrebari de raportat, nu de rezolvat unilateral:
   - `.sa-gol` (cabinet.js:111) e o linie in interiorul unui panou, aliniata
     stanga — nu lista goala pe ecran plin. O clasa unica ajunge, sau trebuie
     modificator `.stare-goala--inline`? Modificatorul e DS -> cere DA.
   - Ecranele de observatie superadmin (admin_activitate: "Niciun cabinet inca.")
     n-au buton de reparat. Iesirea acolo = ce regula? Propune.

5. DS regula 0b: verifica regulile CSS globale intai. `.cap-gol` si `.sa-gol`
   folosesc `#999` hardcodat in loc de `var(--gri)` — a doua abatere DS, pe token
   de culoare. Se repara odata cu prima.

## FAZA 2 — executie (dupa DA pe tabel)

1. static/stil.css: `.stare-goala` (+ modificator daca s-a aprobat).
   Sterge `.mig-gol` (~605), `.cap-gol` (~1591), `.sa-gol` (~1634).
   DS regula 0a: reparatie reala, fara clase moarte lasate in urma.
2. Inlocuieste toate aparitiile. Diacritice: text afisat CU, cod/markeri FARA.
3. verificator_conformitate.py — garda NOUA (F106: ~14 reguli azi), doua verificari:
   a. clasa interzisa: `mig-gol|cap-gol|sa-gol` in orice .js
   b. fundatura: `.stare-goala` fara <button>/ruta in continut
   Garda se adauga DUPA ce textele sunt reparate — verificatorul e la TOTAL 0 si
   trebuie sa ramana la TOTAL 0. Ordinea inversa sparge invariantul.
4. DESIGN_SYSTEM.md cap. 6: adauga v2.13 inainte de "## 7. Documente PDF".
   Fisier normativ -> grep dupa scriere ca sa confirmi patch-ul.

## Poarta

Fara schema, fara migrare, fara backend. Doar static/ + stil.css +
verificator_conformitate.py + DESIGN_SYSTEM.md.
NU atinge main.py, nici fisierele create pentru F144/F145 (Lot 5 abia inchis).

## Test

verificator_conformitate.py -> TOTAL 0 dupa reparatie.
Apoi verificare vizuala reala pe minim 3 ecrane cu lista goala, nu doar
`node --check` (DS regula 0c: sintaxa nu e runtime).
Restart: sudo systemctl restart iconta-nou
