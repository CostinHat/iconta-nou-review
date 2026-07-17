# BRIEF CLAUDE CODE — CURATENIE FISIERE NORMATIVE (17.07.2026)

## Ce este
CARENTE (in DE_FACUT.md), sectiunile vechi din DE_FACUT.md, si ISTORIC.md s-au umplut
in timp cu intrari (REZOLVAT) care nu au fost niciodata mutate/sterse, plus intrari
vagi care nu se mai stie daca sunt inca valabile. Scopul: curatenie MECANICA, verificata,
nu ghicita. Rezultatul: fiecare fisier reflecta STAREA REALA de azi, nu un amestec de
istoric si backlog.

## REGULA DE AUR SE APLICA STRICT AICI
NIMIC nu se sterge, nu se muta, nu se marcheaza rezolvat fara DOVADA:
- grep care arata ca functia/ruta/coloana exista si e folosita, SAU
- test functional real care trece, SAU
- verificare directa in DB (psql) ca structura exista
Daca nu poti dovedi in 2 minute -> NU se atinge, se marcheaza "DE VERIFICAT" cu motivul
exact al nesigurantei. A pierde o intrare valida e mai rau decat a pastra una inutila.

## Ciclul, in ordine (STOP intre fiecare, raportezi inainte de a continua)

### PAS 1 — CARENTE (sectiunea din DE_FACUT.md, linia ~41)
Pentru fiecare din cele 10 intrari:
  - Deja (REZOLVAT ...) in text -> verifica cu grep/test ca INTR-ADEVAR e asa (nu presupune
    ca eticheta veche era corecta). Daca confirmat: MUTA in ISTORIC.md, la data mentionata
    in eticheta (nu la 17.07), sub sectiunea corespunzatoare de sesiune daca exista, sau
    intr-o linie noua "REZOLVARI CONFIRMATE 17.07 (verificate retroactiv)". STERGE din CARENTE.
  - Fara (REZOLVAT) -> verifica DACA s-a rezolvat between timp fara sa fi fost notat.
    Daca da: acelasi tratament ca mai sus, cu nota "gasit rezolvat, netaguit". Daca nu:
    ramane in CARENTE, dar reformulat scurt cu STAREA ACTUALA verificata azi.
Raporteaza: cate mutate, cate ramase, cate "DE VERIFICAT".

### PAS 2 — Sectiunile vechi din DE_FACUT.md
Ordinea: "1. Testare pentru pilot" -> "2. Blocate" -> "3. Sesiune desktop" ->
"4. Infra" -> "5. Iteratii viitoare" -> "6. Ecrane firma" (deja marcata REZOLVAT 13.07,
doar verifica si arhiveaza in ISTORIC.md) -> "ANEXA Inventar functionalitati".
Pentru "ANEXA — Inventar functionalitati" (liniile ~67-137): verifica daca e DUPLICAT
al FUNCTIONALITATI.csv (care e sursa canonica din 16.07). Daca da -> STERGE anexa
intreaga, las-o doar o linie "vezi FUNCTIONALITATI.csv, sursa canonica". Doua inventare
= drift garantat (acelasi principiu ca la DECIZII.md).

### PAS 3 — FUNCTIONALITATI.csv
NU se restructureaza (e deja canonic si activ folosit). Doar: grep pentru orice pozitie
cu Stare goala sau ambigua, raporteaza-le, NU le schimba fara sa intrebi.

### PAS 4 — ISTORIC.md
NU se editeaza continutul vechi (e jurnal cronologic, istoria nu se rescrie - aceeasi
regula ca la DECIZII.md). Se adauga DOAR ce a fost mutat la Pasul 1 si Pasul 2, cu
data originala pastrata, marcat explicit "arhivat 17.07, eveniment original [data]".

## Ce NU faci
- Nu atingi DECIZII.md (e deja curat, structura lui e alta).
- Nu atingi CLAUDE.md, DESIGN_SYSTEM.md, verificator_conformitate.py.
- Nu redenumesti, nu restructurezi capitole doar din motive stilistice.
- Daca gasesti o CONTRADICTIE intre doua fisiere (ex: CSV zice LIVE, CARENTE zice
  netestat) -> STOP, raporteaza, nu decide singur care are dreptate.

## Verificare finala (regula 0c)
- ISTORIC.md: nicio linie stearsa, doar adaugate (git diff arata doar insertii pe
  continutul vechi, eventual mutari clar marcate).
- DE_FACUT.md: doar ce e REALMENTE deschis azi ramane.
- wc -l inainte/dupa pe fiecare fisier, raportat.
- git commit separat per pas (4 commituri), nu unul singur mare - usor de revizuit/revert.
