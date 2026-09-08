# DEPENDENȚELE MODELULUI DE CITIRE — ce invalidează ce, măsurat

*Scris 08.09.2026, la remedierea lui P2. Matricea de mai jos e **generată** din
`core/firma_rezumat.ASPECTE` și păzită caracter cu caracter de `core/test_dependente_masurate.py`;
textul din jur e scris de om.*

---

## De ce există documentul ăsta

P2 a mutat calculul portofoliului din cererea interactivă într-un model de citire. Un model de
citire e o promisiune: *„valoarea asta e adevărată până se schimbă ceva din ce a intrat în ea"*.
Promisiunea se ține doar dacă **știi exact ce a intrat în ea**.

Prima formă a lui P2 nu știa. Lista de tabele-sursă fusese **scrisă din memorie**, iar aspectele
grele — `termene` și `control_fiscal`, adică tocmai cele scumpe — nu declarau **niciun** tabel.
Măsurat: `control_fiscal` citește **27** de tabele din schema firmei; triggerele acopereau **8**.
Douăzeci de tabele puteau fi scrise fără ca nimic să invalideze ceva.

Asta nu e supra-invalidare, care doar costă muncă. E **sub-invalidare**: o valoare veche rămâne
etichetată `curent`, la nesfârșit, fără niciun semnal. Adică exact interdicția pe care modulul o
poartă în antet — *o valoare veche NU se arată ca fiind curentă*.

---

## Cum a fost măsurată, și de ce nu citită

`scripts/scan_dependente.py`. **Două instrumente independente, confruntate**, fiindcă fiecare are o
formă proprie de orbire:

* **PLAN** — pentru fiecare instrucțiune executată, `EXPLAIN (FORMAT JSON, VERBOSE)` pe o conexiune
  separată, iar din arborele de plan se culeg `Schema` + `Relation Name`. E o citire din **parserul
  lui PostgreSQL**, nu o potrivire de șir pe textul SQL (METODA §23: structură, nu text).
  *Orb la:* ce citește o funcție `plpgsql` pe dinăuntru.
* **STAT** — delta pe `pg_stat_all_tables` (`seq_scan + idx_scan`) în jurul calculului. E
  contabilitatea lui PostgreSQL despre ce relații au fost efectiv scanate, deci **vede și
  interiorul funcțiilor**. *Orb la:* atribuirea per instrucțiune.

**Calibrat în trei direcții**, nu în una: (a) o citire reală trebuie văzută de amândouă; (b) un bloc
fără citire nu are voie să inventeze o tabelă; (c) **o citire ascunsă în corpul unei funcții
`plpgsql` trebuie RATATĂ de PLAN și PRINSĂ de STAT**. Fără (c), cele două instrumente ar fi putut fi
de fapt unul singur, iar „acordul" dintre ele n-ar fi dovedit nimic.

Calibrarea a picat de trei ori înainte să treacă, și de fiecare dată defectul era al
instrumentului, nu al codului măsurat:

1. `EXPLAIN` fără `VERBOSE` nu poartă cheia `Schema` — `tenant_004.facturi` și `public.facturi` ar fi
   devenit aceeași dependență.
2. Contoarele `pg_stat` nu se varsă la capătul tranzacției tale, ci când **backendul** devine
   inactiv, nu mai devreme de o secundă. O așteptare fixă raporta ZERO pentru blocul care citise și
   apoi atribuia citirea aceea blocului **următor** — adică inventa dependențe.
3. `pg_stat_force_next_flush()` golește doar backendul care îl cheamă, iar munca se făcuse pe
   conexiuni din pool. Se scot pe rând și li se dă o comandă; abia atunci varsă.

### Punctul orb e FIRMA, nu ecranul

Prima rulare a fost pe o singură firmă și n-a atins `miscari_stoc`. Nu fiindcă modelul n-ar depinde
de ea, ci fiindcă datele **acelei** firme nu intrau pe ramura de stocuri. Matricea publicată e
**reuniunea peste toate cele 20 de firme active**; `miscari_stoc` apare la două dintre ele.

---

## Matricea

<!-- MATRICE:GENERAT — se scrie cu `python3 -m scripts.scan_dependente --doc` -->

| aspect | surse în schema firmei | surse în `public` | dependență de timp | regula de invalidare |
|---|---|---|---|---|
| `solduri` | `solduri_initiale` | — | nu depinde de ceas | `versiune_sursa` = suma contoarelor celor 1 tabele; invalidat când suma se schimbă |
| `plan_conturi` | `plan_conturi` | — | nu depinde de ceas | `versiune_sursa` = suma contoarelor celor 1 tabele; invalidat când suma se schimbă |
| `vector` | `firma_profil` | — | nu depinde de ceas | `versiune_sursa` = suma contoarelor celor 1 tabele; invalidat când suma se schimbă |
| `termene` | `clienti`, `d390_manual`, `facturi`, `firma_profil`, `salariati` | `declaratii_depuse` | **ziua** (`YYYY-MM-DD`) | `versiune_sursa` = suma contoarelor celor 6 tabele; invalidat când suma se schimbă **sau** când se schimbă epoca |
| `control_fiscal` | `articole`, `asociati`, `beneficii_lunare`, `bonuri`, `casa_operatiuni`, `chitante`, `clienti`, `concedii_medicale`, `d300_manual`, `d301_operatiuni`, `d390_manual`, `d390_reclasificare`, `extras_linii`, `factura_linii`, `facturi`, `firma_profil`, `furnizori`, `inregistrari`, `inregistrari_linii`, `mijloace_fixe`, `miscari_stoc`, `perioada_confirmata`, `plan_conturi`, `pontaj`, `salariati`, `salariu_istoric`, `solduri_initiale` | `declaratii_depuse` | **ziua** (`YYYY-MM-DD`) | `versiune_sursa` = suma contoarelor celor 28 tabele; invalidat când suma se schimbă **sau** când se schimbă epoca |

**Inversa** — ce invalidează o scriere într-un tabel:

| tabel-sursă | invalidează |
|---|---|
| `articole` | `control_fiscal` |
| `asociati` | `control_fiscal` |
| `beneficii_lunare` | `control_fiscal` |
| `bonuri` | `control_fiscal` |
| `casa_operatiuni` | `control_fiscal` |
| `chitante` | `control_fiscal` |
| `clienti` | `control_fiscal`, `termene` |
| `concedii_medicale` | `control_fiscal` |
| `d300_manual` | `control_fiscal` |
| `d301_operatiuni` | `control_fiscal` |
| `d390_manual` | `control_fiscal`, `termene` |
| `d390_reclasificare` | `control_fiscal` |
| `extras_linii` | `control_fiscal` |
| `factura_linii` | `control_fiscal` |
| `facturi` | `control_fiscal`, `termene` |
| `firma_profil` | `control_fiscal`, `termene`, `vector` |
| `furnizori` | `control_fiscal` |
| `inregistrari` | `control_fiscal` |
| `inregistrari_linii` | `control_fiscal` |
| `mijloace_fixe` | `control_fiscal` |
| `miscari_stoc` | `control_fiscal` |
| `perioada_confirmata` | `control_fiscal` |
| `plan_conturi` | `control_fiscal`, `plan_conturi` |
| `pontaj` | `control_fiscal` |
| `salariati` | `control_fiscal`, `termene` |
| `salariu_istoric` | `control_fiscal` |
| `solduri_initiale` | `control_fiscal`, `solduri` |
| `public.declaratii_depuse` | `control_fiscal`, `termene` |

**Citite, dar DELIBERAT neurmărite:** `public.tenants`, `public.users`, `public.accounting_firms` — poartă denumirea și cabinetul, nu faptele din care iese verdictul. O redenumire de firmă n-are voie să invalideze 1000 de rezumate.

**Trigger, dar nu sursă a niciunui aspect:** `efactura_trimiteri` — sursă a supervizorului (P1), care are contorul lui agregat. Un singur trigger servește amândoi consumatorii.

### ACOPERIRE RAMURI

*Ramurile sunt derivate prin MĂSURARE: ce declară registrul, minus ce atinge o firmă goală din `tenant_template.sql`. Fixturile stau în `core/test_dependente_ramuri.py`, iar garda cere ca fiecare ramură să-și deschidă chiar sursele declarate aici — o fixtură care n-o exercită pică, în loc să treacă tăcut.*

| aspect(e) | ramură | condiția care o activează | surse pe care le deschide |
|---|---|---|---|
| `termene`, `control_fiscal` | `baza_vector_complet` | firma goala, vector fiscal complet (srl · micro · platitor TVA lunar · IC) | — (nicio sursă nouă) |
| `control_fiscal` | `salarii` | salariat activ **cu tichete de masa** SI luna confirmata pe domeniul `pontaj` | `pontaj`, `salariu_istoric` |
| `control_fiscal` | `stoc` | articol cu miscare de stoc | `miscari_stoc` |
| `termene`, `control_fiscal` | `facturi_emise` | o factura emisa in luna | — (nicio sursă nouă) |
| `termene`, `control_fiscal` | `vector_pfa_profit_neplatitor` | PFA · partida simpla · regim de profit · neplatitor TVA · fara IC | — (nicio sursă nouă) |
| `termene`, `control_fiscal` | `vector_trimestrial_art317_tva_incasare` | SRL · profit · TVA trimestrial · IC · art. 317 · TVA la incasare | — (nicio sursă nouă) |

<!-- MATRICE:SFARSIT -->

---

## Ce s-a construit pe matricea asta

**Contor per (firmă, TABEL)**, în `public.firma_sursa_versiune`, ridicat de trigger la scriere.
Versiunea unui aspect e **suma contoarelor tabelelor lui**, agregată în SQL. Prima formă avea un
contor per firmă, deci o factură nouă invalida `tip_firma`; acum o scriere în `facturi` invalidează
`control_fiscal` și `termene`, și nimic altceva.

Citirea rămâne **o singură interogare** pentru tot portofoliul și toate aspectele: agregarea e un
`GROUP BY` într-un CTE, nu o interogare per firmă sau per aspect. Măsurat prin cererea HTTP
întreagă, la N între 5 și 1000, în patru scenarii: **5 interogări, constant**.

**Timpul e o dependență de sine stătătoare.** `termene` și `control_fiscal` primesc `azi` și răspund
„la termen / întârziat" **relativ la el**. Rândul poartă `epoca` pentru care a fost calculat, iar
prospețimea cere **și** potrivirea epocii. *O valoare care a încetat să fie adevărată fiindcă s-a
schimbat ziua e la fel de veche ca una căreia i s-a schimbat sursa.*

**`tip_firma` a fost RETRAS din model** și e acum o proiecție (`public.firma_tip`), întreținută
sincron de trigger pe `firma_profil`. Ca aspect, avea o fereastră în care lipsea sau era învechit,
iar `tenantii_userului` cădea în ea pe bucla per firmă — adică O(N)-ul pe care P2 tocmai îl scosese
se întorcea de fiecare dată când modelul era rece. O proiecție sincronă n-are fereastră, deci nu are
nevoie de cale de rezervă. *O cale de rezervă pe calea de cerere e tot o cale de cerere.*

---

## Ce NU acoperă matricea, declarat

* **Sursele din afara bazei.** Snapshotul ANAF al regimului TVA intră în `control_fiscal` prin
  `regim_tva_anaf`; el vine din tabele urmărite, dar prospețimea LUI față de ANAF e altă întrebare,
  a monitorului fiscal, nu a modelului de citire.
* **Ce citește o funcție `plpgsql` pe dinăuntru** ar fi invizibil pentru PLAN. Pe eșantionul cu
  confruntare, PLAN și STAT n-au avut niciun dezacord (`doar_stat` gol), deci codul aplicației nu
  ascunde citiri în funcții. Dacă asta se schimbă, confruntarea o va arăta.
* **Firmele care n-au apucat să producă o stare.** Matricea e reuniunea peste firmele existente
  astăzi. O ramură pe care nicio firmă din portofoliu n-o atinge încă nu e în ea — și de-aia
  măsurătoarea se rulează din nou, nu se crede pe cuvânt.

## Cum se reface

```
python3 -m scripts.scan_dependente          # calibrează, măsoară, scrie masuratori/p2/dependente_masurate.json
python3 -m scripts.scan_dependente --doc    # rescrie blocul generat de mai sus
```
