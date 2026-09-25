---
title: "Cum se cumulează veniturile pentru stabilirea CAS și CASS?"
description: "CAS cumulează doar activități independente și drepturi de proprietate intelectuală; CASS cumulează, separat, aceleași venituri (liniar) și, pe altă categorie, veniturile pasive (pe trepte)."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se cumulează veniturile pentru stabilirea CAS și CASS?

Cumularea nu se face „la grămadă", pe toate veniturile unei persoane — legea separă strict două categorii, cu reguli de cumul și plafoane diferite pentru fiecare.

## Temeiul legal

::: ghid-temei
„Încadrarea în plafonul anual de cel puțin 12 salarii minime brute pe țară sau de cel puțin 24 de salarii minime brute pe țară, după caz, se efectuează prin cumularea veniturilor nete și/sau a normelor anuale de venit din activități independente determinate potrivit art. 68, 68^3 și 69, a venitului brut realizat în baza contractelor de activitate sportivă potrivit art. 68^1, precum și a veniturilor nete din drepturi de proprietate intelectuală determinate potrivit art. 72, 72^1 și 73, realizate în anul pentru care se datorează contribuția."
— Codul fiscal (Legea 227/2015), art. 148 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Încadrarea în plafonul anual de cel puțin 6, 12 sau 24 de salarii minime brute pe țară, după caz, se efectuează prin cumularea veniturilor prevăzute la art. 155 alin. (1) lit. c)-h)."
— Codul fiscal, art. 170 alin. (4) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cum funcționează, pe cele două contribuții:

- **CAS** (art. 148 alin. (3)) cumulează: venitul net/norma de venit din activități independente, venitul brut din contracte de activitate sportivă ȘI venitul net din drepturi de proprietate intelectuală. Chiriile, dividendele sau veniturile agricole NU intră în acest cumul.
- **CASS pentru activități independente** (art. 170 alin. (1)) cumulează o listă mai restrânsă: doar venitul net/norma de venit din activități independente și din activitate sportivă (art. 68, 68^1, 68^3, 69) — plafonarea e liniară pe venitul net, nu în trepte. Spre deosebire de CAS, drepturile de proprietate intelectuală NU intră aici.
- **CASS pentru venituri pasive** (art. 170 alin. (4)) cumulează, separat, o listă diferită: drepturile de proprietate intelectuală (care, la CASS, se regăsesc DOAR aici, nu și la alin. (1)), venituri din asocieri cu persoane juridice, chirii, investiții, activități agricole/silvicultură/piscicultură și alte surse — cu plafonare pe trepte de 6/12/24 salarii minime brute.
- Cele două cumuluri (activități independente vs. venituri pasive) sunt paralele, nu se amestecă — un contribuabil poate datora CAS/CASS pe activități independente ȘI, separat, CASS pe venituri pasive, fiecare cu propriul prag.

## Ce se greșește în practică

- Se cumulează toate veniturile unei persoane într-un singur total, indiferent de categorie, pentru a stabili un singur plafon — de fapt există cumuluri separate, cu categorii de venit diferite pentru fiecare.
- Se include venitul din chirii sau dividende în cumulul pentru CAS — CAS privește strict activități independente, activitate sportivă și proprietate intelectuală.
- Se aplică regula pe trepte a veniturilor pasive (art. 170 alin. (4)) și asupra veniturilor din activități independente — acestea din urmă se calculează liniar, conform art. 170 alin. (1).

## Ce face iConta.eu

Motorul `core/d212_engine.py` calculează corect CAS și CASS pentru un singur venit net dat ca parametru — funcțiile `calculeaza_cas` și `calculeaza_cass` aplică regulile de prag și plafonare exact cum le cere legea, pentru categoria „activități independente". Cumularea venitului dintr-o singură sursă evidențiată în Registrul-jurnal de încasări și plăți (`core/rip_api.py`, `fisa_d212`) e automată în interiorul acelei surse.

Aplicația nu cumulează automat venituri din surse diferite (de exemplu, o normă de venit plus drepturi de autor plus chirii ale aceleiași persoane) și nu separă automat cumulul CAS de cele două cumuluri CASS (activități independente vs. venituri pasive) — verificarea și cumularea manuală, pe categoriile corecte, rămân în sarcina contabilului.

[iConta.eu](/)
