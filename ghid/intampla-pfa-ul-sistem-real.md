---
title: "Ce se întâmplă dacă PFA-ul în sistem real are pierdere?"
description: "PFA-ul cu pierdere fiscală în sistem real nu datorează impozit pe venit, dar poate reporta pierderea pe 5 ani, în limita a 70% din veniturile nete viitoare din aceeași sursă; motorul D212 al iConta.eu calculează doar anul curent, fără reportare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce se întâmplă dacă PFA-ul în sistem real are pierdere?

Dacă cheltuielile deductibile depășesc venitul brut, venitul net e zero pentru anul respectiv, nu negativ — dar pierderea nu se pierde: poate fi reportată și compensată din veniturile nete ale acelei surse în următorii 5 ani fiscali, în limita a 70%.

## Temeiul legal

::: ghid-temei
„Venitul net anual din activități independente se determină în sistem real, pe baza datelor din contabilitate, ca diferență între venitul brut și cheltuielile deductibile efectuate în scopul realizării de venituri, cu excepția situațiilor în care sunt aplicabile prevederile art. 68^1, 68^3 și 69."
— Cod fiscal (Legea 227/2015), art. 68 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Pierderea fiscală anuală înregistrată pe fiecare sursă din activități independente, din drepturi de proprietate intelectuală și din activități agricole, silvicultură și piscicultură, determinată în sistem real, se reportează și se compensează de către contribuabil în limita a 70% din veniturile nete anuale, obținute din aceeași sursă de venit în următorii 5 ani fiscali consecutivi."
— Cod fiscal, art. 118 alin. (4) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Regulile de reportare a pierderilor sunt următoarele: a) reportul se efectuează cronologic, în funcție de vechimea pierderii, în următorii 5 ani consecutivi; [...]"
— Cod fiscal, art. 118 alin. (5) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din aceste texte rezultă mecanismul complet:

- **Pentru anul cu pierdere**: venitul net e considerat zero (nu negativ) — nu se datorează impozit pe venitul din activitatea respectivă în acel an, dar pierderea rămâne consemnată separat.
- **Reportarea**: pierderea se compensează din veniturile nete anuale din **aceeași sursă**, în următorii **5 ani fiscali consecutivi**, în limita a **70%** din venitul net al fiecărui an de compensare.
- Reportul se face **cronologic**, în funcție de vechimea pierderii — pierderile mai vechi se compensează înaintea celor mai recente.

## Ce se greșește în practică

- Se presupune că o pierdere înseamnă doar „nu plătesc impozit anul ăsta" și se uită — de fapt pierderea are valoare fiscală viitoare, prin reportare pe 5 ani.
- Se compensează integral pierderea din venitul net al anului următor — legea limitează compensarea la 70% din venitul net anual din aceeași sursă, nu la 100%.
- Se confundă „aceeași sursă de venit" cu „orice venit din activități independente" — reportarea se face strict pe sursa care a generat pierderea, nu cumulat cu alte activități independente ale aceleiași persoane.

## Ce face iConta.eu

Motorul de calcul D212 (`core/d212_engine.py`) implementează exact regula de bază: venitul net rezultă din venitul brut minus cheltuielile deductibile din registrul de încasări și plăți validat, iar dacă rezultatul e negativ, e limitat (clampat) la zero pentru calculul CAS, CASS și impozitului anului respectiv — nu apare niciodată un venit net negativ în fișa de calcul.

**Motorul nu ține însă evidența pierderii reportabile de la un an la altul** — nu există în cod niciun mecanism care să rețină pierderea unui an și să o scadă automat, în limita de 70%, din venitul net al anilor următori. Fișa D212 din iConta.eu calculează fiecare an fiscal independent, pe baza registrului de încasări și plăți al acelui an. Dacă ai avut pierdere într-un an anterior și vrei să o reportezi, calculul reducerii aplicabile (70% din venitul net al anului curent, cronologic pe vechimea pierderilor) rămâne, la acest moment, o urmărire manuală a contabilului.

[iConta.eu](/)
