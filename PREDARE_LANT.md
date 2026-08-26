Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — 193 din 193 scrise, una singură exercitată (26.08.2026, noapte)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-08-26** (noapte), *rescriere COMPLETĂ, nu petic*
- **pe commit**: `cf945fc`
- **de ce acum**: **nu fiindcă a sunat pragul.** Contorul arăta **4** commituri de la ultima
  rescriere (`b678b45`), sub pragul de 10, iar avertismentul nu mai sunase. S-a rescris fiindcă
  **conținutul** s-a schimbat: trei restanțe noi, două reparații aplicate, un gard nou și o
  afirmație de-a mea infirmată. *O predare se rescrie când nu mai descrie lumea, nu când sună un
  contor.*
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire.**
- **gardat**: `scripts/githooks/pre-commit` avertizează peste 10 commituri;
  `core/test_predare_proaspata.py` nu lasă avertismentul să dispară tăcut. Avertizează, nu
  blochează.

---

## STAREA LA PREDARE

Poartă verde la `cf945fc`: **3298 teste** ✓ · 10 skip · 14 xfail · ruff OK · verificator
**TOTAL 0** · site 200 · four-way `HEAD = origin/main = backup/lant-2026-08-26 = cf945fc`, proces
viu pornit **după** commit. *(Se reverifică rulând poarta, nu se crede pe cuvânt.)*

Neurmărite: cele șapte `LOT_*_VERIFICARI.md`, `corectii_lot_1.md`, artefacte vizuale în
`frontend_test/`. Zero modificări necomise.

**Cifrele nu se scriu aici** — `scripts/raport_b.py`. Fotografia de la `cf945fc`: interdicții
MĂSURATE 21 · PARȚIAL 16 · NEMĂSURABILE 1 · NEÎNCEPUTE 38; restanțe deschise **45** (E1: **22**).

---

## PRIMUL LUCRU DE ȘTIUT: OPT FIRME NU MAI POT EMITE ADEVERINȚE

`firma_profil.patron_nume` era citită de `adeverinta`, `contracte_api` și `pachete_api` — și
**scrisă de nimic**. Documentele o tipăreau goală. Din 26.08: câmpul există în *Date firmă › Nume
administrator*, iar cele două documente **refuză motivat** fără el.

**Măsurat: câmpul e gol pe toate cele 19 firme, iar 8 au salariați.** Prima adeverință cerută pe
oricare din ele se oprește. E o oprire corectă — documentul ieșea cu un gol la un om — dar cine
continuă trebuie s-o știe **înainte** ca cineva să dea de ea.

---

## PASUL CURENT: SCRIS ÎNTREG, EXERCITAT O DATĂ

**`TRASEE_VERIFICARI.md`: 193 din 193, zero locuri goale.** Loturile 6 și 7 mutate în fișierul
canonic; loturile rămân netracked ca istoric.

**Din cele 193, una singură a fost exercitată pe date** — proba portalului (R62), făcută de Costin
pe o firmă de test. A produs: **un defect de prag 1** pe cod scris și gardat în aceeași zi, opt
observații, **patru restanțe noi**, și **patru rapoarte care s-au dovedit premise**. Mai mult decât
o zi întreagă de gărzi.

*Verde nu înseamnă exercitat.* E propoziția cea mai scumpă a zilei.

---

## TREI FORME NUMITE AZI, CU INSTANȚELE LOR

### 1. Ceva scris și ceva care ajunge la el intră ÎMPREUNĂ

| forma | instanțe |
|---|---|
| **coloană** cu drum de citire, fără drum de scriere | `principal_client_id` (scoasă) · `patron_email` (scoasă) · `patron_nume` (reparată) |
| **rută** scrisă și gardată, fără apelant | `POST /public/confirma-email` — prag 1, o zi ascuns |
| **coloană nouă** care nu se adaugă singură | `nir_linii.articol_id` (R64) — de aceea nu s-a adăugat azi |

Regula, în forma finală: **coloana și calea ei de scriere · ruta și calea ei de apelare · nu se
adaugă una fără cealaltă.**

### 2. Calea nu e un fapt textual — șapte instanțe într-o zi

Docstringul citit ca SQL (tabela inventată `oarb`) · coloane „scrise de nimic" (**17**, invalidată
înainte de a intra în registru) · teste cuplate la firme reale (**18 → 6 → 4 → 3**, prin citire) ·
rute fără apelant (**13 → 6 → zeci → 32 → 5**, prin citire).

**De ce:** UI-ul compune căi la rulare (`` `${tip()}-valideaza` ``) și dispecerizează prin tabele
(`ruta: "nota-sgr"`); codul asamblează liste de coloane din constante. Un scan pe text pe clasele
astea **se calibrează pe un caz cunoscut rezolvat înainte de a publica orice cifră** — regula a
salvat cifra 17 de la a intra în registru.

### 3. Un raport cade pe o premisă mai des decât pe un defect

**Patru** azi. Trei ale lui Costin (o măsurătoare de-a mea citită ca stare curentă după 40 de
minute · un cont căutat la o adresă tocmai schimbată · un ecran deschis pe firma **duplicat**), una
a mea (`s1003`/`s1005` „fără ecran" — ecranul există). **O cifră fără momentul ei nu e o
măsurătoare, e o amintire.**

---

## CE S-A ÎNCHIS ȘI CE S-A DESCHIS AZI

**Închise:** R60 · R61 · R62 (prag 1) · R65 · R46 (**prima reaprindere mecanică reală**).

**Deschise și nerezolvate:** R63 (decis, aplicat) · R64 (decis: documentele produc mișcarea; cere
`articol_id` întâi) · R66 (aplicat) · **R67** (suita rulează pe baza de **producție**; decis:
utilizator de test restrâns — **cere `postgres`, nu pot eu**) · R68 · R69 (declarații depuse pe un
regim schimbat: **6 firme, 55 de declarații**) · R70 (gard construit; 5 rute fără apelant) · R71
(opt observații din probă) · **R72** (o firmă adăugată din greșeală **nu se poate scoate** — nu
există rută de ștergere) · R73 (aplicat).

---

## CE BLOCHEAZĂ, ÎN ORDINE

1. **R72 e singura cerută și neîncepută.** Costin a dat definiția: *evidență = document ieșit din
   aplicație sau rând în evidența contabilă* (notă, factură emisă, declarație, stat de plată,
   artefact). Nu: schema, planul implicit, vectorul, conturile de client. Ștergerea curăță tot ce
   depinde de firmă; un cont legat și de altă firmă **se dezleagă**, nu se șterge. Prima parte a
   construcției e lista tabelelor din `public` care poartă `tenant_id` — nemăsurată.
2. **R67 cere `postgres`.** `iconta_user` n-are CREATEROLE. Comanda e în raportul turei. Și o
   corecție la variantă: în PostgreSQL nu se pot da drepturi *doar pe `test_*`* — `CREATE SCHEMA`
   se acordă pe bază. Forma implementabilă e complementul: **nimic pe `tenant_*`**.
3. **Două firme `PROBA PORTAL SRL`** rămân în bază (CUI `14399840` și `2816464`), plus contul
   `+client2`. Se șterg când R72 dă o cale curată. Duplicatul **a costat deja**: a produs un raport
   de defect fals în aceeași zi.
4. **R73 n-are clichet.** O revenire la `except: pass` ar trece.

---

## REGULI EXERCITATE AZI

- **Consemnează întâi, decide după** — toate restanțele noi scrise înainte de decizie.
- **O măsurătoare se calibrează înainte de publicare** — 17 a murit înainte de registru.
- **Clichetul 50 respinge și gărzile proprii** — două fișiere rescrise pe structură; forma
  acceptată e operatorul de mulțime (`>= {…}`), nu `in`.
- **Un refuz numește lucrul și locul** — `UNDE_ADMINISTRATOR`, `UNDE_PERIOADE`, valori cu nume, ca
  gardul să asertea că mesajul e **compus** din ele.
- **Mesajele de commit se trimit ca FIȘIER** — un heredoc neghilimelat a golit un cuvânt din
  `892b337`.
- **Registrele nu se umplu ca să pară pline** — `GARZI.md` și `TESTE.md` au rămas neatinse de
  patru ori azi, cu motivul scris de fiecare dată.

---

## CIFRE INVALIDATE — se păstrează, nu se șterg

*O cifră ai cărei termeni nu se mai pot reconstitui se **INVALIDEAZĂ**, nu se corectează.*

| cifra | unde apărea | de ce e INVALIDATĂ |
|---|---|---|
| **131** (valori fiscale în afara registrului) | predarea din 22.08 | termeni recalculați pe domeniu lărgit de trei ori. Clichetul viu: `core/test_constante_nesursate.py` |
| **„25 de trasee"** | comenzile din 24 si 25.08 | nu exista instrument. Cifra care se poate reface e **35** |
| **„129 de rute schimbă date fără rol"** | predarea din 26.08 dimineață | raza nu se mai poate reconstitui |
| **„R55: șapte rute"** | comanda din 26.08 | proxy pe numele grupului. Real: **40**, din care 3 scriu `validata` direct |
| **17** (coloane citite și scrise de nimic) | instrument din 26.08 seara | **INVALIDATĂ înainte de publicare** — calibrarea pe R51 a infirmat-o |
| **18** (teste cuplate la firme reale) | raportul din 26.08 | grep naiv; real, prin citire: **3** |
| **13 / 6** (rute de citire fără apelant) | raportul din 26.08 seara | ancoră greșită; real, prin citire: **5** în total |

---

## CE NU E ADEVĂRAT DESPRE STAREA ASTA, ȘI SE SPUNE

- **Verde nu înseamnă exercitat.** 3298 de teste trec, și un prag 1 a stat ascuns o zi pe cod
  gardat.
- **193 de verificări sunt scrise, una e exercitată.** Rata nu se extrapolează dintr-un caz — dar
  nici nu se ignoră.
- **Baseline-ul din `test_ruta_fara_apelant.py` nu e curat.** E o fotografie care conține și rute
  reale, și artefacte ale detectorului. Gardul spune că **nu crește**, nu că lista e adevărată.
- **Trei observații din R71 sunt de așezare** — clasa e declarată nemăsurabilă în CLAUDE.md.
