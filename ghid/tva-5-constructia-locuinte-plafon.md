---
title: "TVA 5% pentru construcția de locuințe: plafon"
description: "De ce cota de TVA 5% pentru locuințe nu mai există din august 2025 și ce regim se aplică în prezent, cu ce plafoane, conform Codului fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# TVA 5% pentru construcția de locuințe: plafon

Cota redusă de TVA de 5% pentru achiziția de locuințe, cunoscută mulți ani ca facilitate fiscală în domeniul rezidențial, **nu mai există** ca atare din 1 august 2025. Legea nr. 141/2025 a eliminat vechea structură de cote reduse (5% și 9%) și a lăsat o singură cotă redusă, de 11%, aplicabilă unei liste limitative de bunuri și servicii — printre care, cu condiții specifice, și locuințele considerate „parte a politicii sociale".

## Temeiul legal

::: ghid-temei
„Cota standard se aplică asupra bazei de impozitare pentru operațiunile impozabile care nu sunt scutite de taxă sau care nu sunt supuse cotei reduse, iar nivelul acesteia este 21%. [...] Cota redusă de 11% se aplică asupra bazei de impozitare pentru următoarele prestări de servicii și/sau livrări de bunuri: [...] l) livrarea locuințelor ca parte a politicii sociale, inclusiv a terenului pe care sunt construite."
— Legea nr. 227/2015 privind Codul fiscal, art. 291 alin. (1) și alin. (2) lit. l), astfel cum au fost modificate de Legea nr. 141/2025 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Vechile alineate (3) și următoarele ale art. 291 — cele care stabileau cota de 5% pentru locuințele de până la 600.000 lei, cu suprafață utilă de maximum 120 mp — au fost **abrogate** odată cu modificarea din 2025. Legea a prevăzut însă un regim tranzitoriu, aplicabil doar pentru o perioadă limitată, cu o cotă de 9% (nu 5%) și cu aceleași praguri valorice și de suprafață:

::: ghid-temei
„Persoana fizică, în mod individual sau în comun cu altă persoană fizică/alte persoane fizice, poate achiziționa în perioada 1 august 2025-31 iulie 2026 inclusiv o singură locuință cu cota redusă de TVA de 9%, dacă se îndeplinesc în mod cumulativ următoarele condiții: a) locuința are o suprafață utilă de maximum 120 mp, exclusiv anexele gospodărești, și o valoare, inclusiv a terenului pe care este construită, care nu depășește suma de 600.000 lei, exclusiv taxa pe valoarea adăugată."
— Legea nr. 141/2025, Articolul III alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Regimul tranzitoriu de 9% nu era disponibil pentru orice cumpărător nou din acea perioadă, ci doar pentru cei care „a[u] încheiat până la data de 1 august 2025 un act juridic între vii care are ca obiect plata în avans pentru achiziționarea unei astfel de locuințe" (Articolul III alin. 1 lit. d) — practic, doar pentru tranzacțiile deja angajate printr-un avans înainte de intrarea în vigoare a legii. Fereastra s-a închis complet la **31 iulie 2026** — deci, la data acestui ghid, regimul tranzitoriu de 9% s-a încheiat deja. Din 1 august 2026, pentru achizițiile de locuințe de către persoane fizice nu mai există nicio cotă redusă generală bazată pe plafonul de 600.000 lei; se aplică fie cota standard de 21%, fie, dacă locuința se încadrează strict în categoria „locuință ca parte a politicii sociale" (definită restrictiv de lege — cămine de bătrâni, case de copii, centre de recuperare pentru minori cu handicap ș.a.), cota redusă de 11%.

Pentru firmele care construiesc și vând locuințe, concluzia practică e simplă: **cota de 5% nu se mai aplică sub nicio formă**, iar cota tranzitorie de 9% a expirat; regimul curent e 21% standard sau 11% pentru locuințele care se încadrează expres la definiția politicii sociale de la art. 291 alin. (2) lit. l).

## Ce se greșește în practică

- Se aplică din obișnuință cota de 5% la vânzarea unei locuințe noi, deși aceasta a fost abrogată încă din august 2025.
- Se confundă regimul tranzitoriu de 9% (valabil doar 1 august 2025 – 31 iulie 2026, cu plafon de 600.000 lei și 120 mp) cu regula permanentă de 11% pentru „locuințe ca parte a politicii sociale" — cele două categorii au condiții complet diferite.
- Se presupune greșit că orice locuință sub 600.000 lei beneficiază de cotă redusă — plafonul valoric era specific regimului tranzitoriu, deja expirat, nu unei reguli permanente.
- Nu se verifică dacă locuința se încadrează strict în definiția restrictivă de la art. 291 alin. (2) lit. l) (cămine de bătrâni, centre pentru minori cu handicap etc.) înainte de a aplica cota de 11% unei locuințe obișnuite.

## Ce face iConta.eu

Din verificarea codului sursă (`core/common.py`, registrul `COTE`), iConta.eu ține istoricul complet al cotelor de TVA (inclusiv fostele 9% și 5%, cu temeiurile lor legale), dar pentru orice dată de la 1 august 2025 încolo, atât fosta cotă de 9%, cât și fosta cotă de 5% sunt înregistrate ca fiind înlocuite de cota unică de 11% (Legea 141/2025, art. 291 alin. (2)) — codul distinge intern între cele două (9% a fost „comasată" în 11%, 5% a fost „abrogată" ca atare de la aceeași dată), dar rezultatul practic e identic: aplicația nu va mai propune 5% sau 9% pentru o factură emisă după 1 august 2025. Utilizatorul trebuie totuși să confirme manual dacă o locuință anume se încadrează la cota de 11% (politică socială) sau la 21% standard, întrucât încadrarea depinde de caracteristici pe care aplicația nu le verifică automat (tipul beneficiarului, suprafața, destinația clădirii).

[iConta.eu](/)
