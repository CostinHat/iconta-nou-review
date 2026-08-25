# ȘABLONUL DE RAPORT

**De ce există ca fișier.** Regulile de raportare erau descrise — în memorie și în `CLAUDE.md` — și
o descriere se poate rata din memorie. Un șablon cu secțiuni goale nu. Fiecare raport se scrie
**pornind de la fișierul ăsta**, nu din amintirea structurii.

Cerut de Costin pe **23.08.2026**, după un raport care avea trei abateri, toate de formă, niciuna de
conținut: numerotarea nu urma comanda (șase puncte primite, grupate sub titluri proprii), **§11
lipsea complet**, iar la un punct evaluarea unui răspuns anterior a fost scrisă fără să fie numit
autorul lui — de unde a rezultat că raportul părea să atribuie comenzii ceva ce nu conținea.

---

## Șablonul

```
RAPORT — <ce s-a lucrat> | <data> | <HEAD intrare> → <HEAD ieșire>

## ÎNȚELEGEREA

Ce am înțeles că s-a cerut, în propriile cuvinte, înainte de muncă.

## A. RĂSPUNS LA COMANDĂ

1. <punctul 1 din comandă, citat>
   <răspunsul>
2. <punctul 2 din comandă, citat>
   <răspunsul>
...

## §7 — ÎN PLUS / MAI PUȚIN

Ce am făcut peste ce s-a cerut. Ce am făcut mai puțin.

## §7b — PRESUPUNERI

Ce am presupus și nu era în comandă.

## §11 — CE AM ACTUALIZAT

Fiecare registru, cu ce s-a scris în el. Un registru neatins se scrie
„nimic de actualizat, fiindcă…", nu se omite.

## B. UNDE SUNTEM

Derivat cu `scripts/raport_b.py`. Nu se scrie de mână.

## POARTA

Teste, verificator, four-way, site.

## CERINTE:

1. <ce e> — <ce blochează dacă rămâne nedată> — <detalii care ajută decizia> — <a câta tură>
2. ...

(sau, dacă tura nu cere nimic: „nimic")
```

---

## Regulile fiecărei secțiuni

### ÎNȚELEGEREA
Se scrie **înainte de muncă**, nu după. E locul în care o citire greșită a comenzii devine vizibilă
cât mai e ieftin de corectat. Dacă înțelegerea de la început diferă de ce a ieșit, diferența se
scrie — nu se rescrie înțelegerea ca să se potrivească.

### A. RĂSPUNS LA COMANDĂ
**Numerotarea e a COMENZII, nu a mea.** Fiecare punct primit primește un punct aici, în aceeași
ordine, cu **textul comenzii citat**. Nu se grupează, nu se comasează, nu se reordonează după ce mi
s-a părut mai important.

- Un punct nefăcut se scrie **„nefăcut, fiindcă…"** — nu se omite și nu se topește în alt punct.
- O întrebare primită e un punct ca oricare altul: se citează întrebarea, apoi se răspunde.
- Când răspunsul corectează ceva scris mai devreme, **se numește autorul lucrului corectat**. „O
  cifră s-a dovedit greșită" fără să spună a cui era e o propoziție care ascunde exact partea care
  contează.

### §7 — ÎN PLUS / MAI PUȚIN
Ambele direcții, explicit. **Mai puțin** nu e o omisiune permisă: e o declarație. Munca făcută peste
comandă se declară aici chiar dacă decurgea firesc din ea.

### §7b — PRESUPUNERI
Ce am presupus și nu era în comandă. O presupunere nescrisă e o decizie luată în numele altcuiva.

### §11 — CE AM ACTUALIZAT
Fiecare registru, cu ce s-a scris în el. **Un registru neatins se scrie „nimic de actualizat,
fiindcă…", nu se omite** — altfel nu se poate deosebi „n-avea ce" de „am uitat".

`CONFORMITATE.md` intră aici **întotdeauna**.

Registrele de verificat, de fiecare dată: `CONFORMITATE.md` · `DECIZII.md` · `ISTORIC.md` ·
`GARZI.md` · `TESTE.md` · `PLAN_LUCRU.md` · `PLAN_INVESTIGATII.md` · `PLAN_ARHITECTURA.md` ·
`METODA_VERIFICARE.md` · `DESIGN_SYSTEM.md` · `INSTRUMENTE_ROADMAP.md` · `MODEL_AUDIT_TENANT.md` ·
`ISTORIC_TENANTI.md` · `anaf_surse/INDEX.json` · `anaf_surse/PROVENIENTA.json`.

### B. UNDE SUNTEM
**Derivat cu `scripts/raport_b.py`. Nu se scrie de mână.** Se rulează *după* ce commitul a intrat,
altfel raportează starea de dinainte.

Atenție la partea derivată vs. partea scrisă: cifrele se derivă, dar **proza antetului nu** — a
rămas stătută cel puțin o dată (23.08: antetul spunea că 52 e PARȚIALĂ în commitul în care nu mai
era). Proza antetului se recitește la fiecare raport.

### CERINTE
**Toate cerințele către Costin stau AICI, la sfârșitul raportului, numerotate.** Nu se
împrăștie prin raport, nu se lasă pe la mijloc, nu se scriu ca observații. **Dacă nu e în lista
asta, nu e o cerință — e o observație.**

Fiecare poziție are patru lucruri:

| ce | de ce |
|---|---|
| **ce e** — decizia sau lucrul de făcut | fără el, cererea nu se poate îndeplini |
| **ce blochează dacă rămâne nedată** | fără el, nu se poate prioritiza |
| **detalii care ajută decizia** | variantele, cifra, instanța — ca răspunsul să nu ceară o a doua tură |
| **a câta tură se cere** | o cerință repetată de trei ori e o cerință scrisă prost, nu una ignorată |

**Dacă tura nu cere nimic, secțiunea scrie „nimic".** Nu se omite — altfel nu se poate deosebi
„n-am avut ce cere" de „am uitat".

**Motivul, cu instanțele.** *(Costin, 25.08.2026)* Cerințele împrăștiate prin raport se ratează:
**R40** a fost cerută **patru ture** și n-a fost văzută · *„TRASEE.md e netracked"* era scris în
`§11` și n-a fost citit · **trei din patru decizii** dintr-o tură au rămas fără răspuns. O listă
numerotată la sfârșit **se poate confrunta**: dacă răspunsul n-are punctul 3, se vede.

### POARTA
Teste (numărul, verde/roșu) · verificator (TOTAL) · **four-way** (HEAD = `origin/main` = ramura de
backup = procesul viu, cu ora de pornire ulterioară commitului) · site (cod HTTP).

---

## Autoverificarea, ca ULTIMĂ operațiune înainte de a trimite

Nu la început, nu pe parcurs: la final, ca act separat.

1. **Recitește comanda** — textul ei, nu amintirea ei.
2. **Numără punctele** primite.
3. **Confirmă** că fiecare are răspuns **cu același număr**, în aceeași ordine.
4. **Confirmă** că `§11` există și **enumeră registrele**, inclusiv pe cele neatinse.
5. **Confirmă** că `B` e **derivat**, nu scris.
6. **Confirmă** că `CERINTE` există, e la SFÂRȘIT, e numerotată, și că nicio cerință nu e
   scrisă în altă parte a raportului. Dacă nu se cere nimic, scrie „nimic".
7. **Confirmă** că nicio afirmație despre ce s-a cerut nu adaugă și nu scoate ceva față de textul
   comenzii — regula B în oglindă: nu doar că *ce afirmă comanda se verifică*, ci și că *nu i se
   atribuie ce nu conține*.
