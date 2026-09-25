---
title: "Contestația la decizia de impunere pe lipsuri de stoc"
description: "Regulile generale de formă, termen și obiect ale contestației împotriva unei decizii de impunere, potrivit titlului VIII din Codul de procedură fiscală — aplicabile și deciziilor pe lipsuri de stoc."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Contestația la decizia de impunere pe lipsuri de stoc

Nu există, în sursele verificate, o procedură specială de contestație pentru deciziile de impunere emise ca urmare a constatării unor lipsuri de stoc — acestea urmează regimul general al contestațiilor administrativ-fiscale, prevăzut de titlul VIII din Codul de procedură fiscală.

## Temeiul legal

::: ghid-temei
„ART. 268 Posibilitatea de contestare
(1) împotriva titlului de creanță, precum și împotriva altor acte administrative fiscale se poate formula contestație potrivit prezentului titlu. Contestația este o cale administrativă de atac și nu înlătură dreptul la acțiune al celui care se consideră lezat în drepturile sale printr-un act administrativ fiscal.
[...]
(3) Baza de impozitare și creanța fiscală stabilite prin decizie de impunere se contestă numai împreună."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 268 alin. (1) și (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă din acest temei pentru o decizie de impunere emisă pe lipsuri de stoc constatate la inventar sau control:

- Contestația se formulează **în scris**, cu datele de identificare, obiectul contestației, motivele de fapt și de drept și dovezile pe care se întemeiază (art. 269 alin. (1)) — pentru lipsurile de stoc, dovezile relevante includ, tipic, fișele de magazie, listele de inventariere și documentele de recepție/ieșire.
- **Baza de impozitare** (valoarea lipsurilor constatate) și **creanța fiscală** rezultată (impozitul/TVA aferent) se contestă **împreună**, nu separat — o contestație care atacă doar cuantumul impozitului, fără baza de calcul, riscă să fie incompletă.
- Contestația se depune la **organul fiscal emitent** al actului administrativ atacat, nu direct la instanță — calea administrativă e prealabilă acțiunii în justiție.

## Ce se greșește în practică

- Se contestă doar suma finală a impozitului stabilit, fără a ataca explicit modul de calcul al lipsurilor de stoc (baza de impozitare) — art. 268 alin. (3) cere contestarea lor împreună.
- Se depune contestația fără dovezi concrete (fișe de magazie, liste de inventariere, documente de gestiune) care să susțină o poziție diferită de cea a organului de control — motivele „de drept" fără motive „de fapt" documentate sunt insuficiente.
- Se confundă termenul de contestație cu termenul de plată al obligației — depunerea unei contestații nu suspendă automat obligația de plată, decât în condițiile prevăzute expres de lege.

## Ce face iConta.eu

Verificat în cod: `core/stocuri.py` și `core/repo_stocuri.py` țin evidența mișcărilor de stoc pe articol, iar `core/control_incrucisat.py` semnalează neconcordanțele dintre declarații și contabilitate cu stare verde/roșu/gri; iConta.eu nu are, la acest moment, un modul dedicat generării sau depunerii unei contestații împotriva unei decizii de impunere — redactarea și depunerea contestației, cu documentele justificative aferente lipsurilor de stoc, rămân în sarcina contabilului/firmei.

[iConta.eu](/)
