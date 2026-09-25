---
title: "Poate ANAF compara D406 cu D300 și D394?"
description: "ANAF are, prin lege, dreptul de analiză de risc pe baza fișierului standard de control fiscal (D406/SAF-T) și a declarațiilor depuse; iConta.eu nu rulează însă azi o comparație automată D406↔D300↔D394."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Poate ANAF compara D406 cu D300 și D394?

Legal, da: fișierul standard de control fiscal (D406/SAF-T) e definit explicit ca probă și ca sursă de date pentru administrarea fiscală, alături de declarațiile deja depuse — inclusiv D300 și D394.

## Temeiul legal

::: ghid-temei
„3. analiza de risc - activitatea efectuată de organul fiscal în scopul identificării riscurilor de neconformare în ceea ce privește îndeplinirea de către contribuabil/plătitor a obligațiilor prevăzute de legislația fiscală, de a le evalua, de a le gestiona, precum și de a le utiliza în scopul efectuării activităților de administrare fiscală."
— Legea 207/2015 (Codul de procedură fiscală), art. 1 pct. 3 (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„(1) Contribuabilul/Plătitorul are obligația de a depune la organul fiscal central o declarație cuprinzând informații din evidența contabilă și fiscală, denumită în continuare fişierul standard de control fiscal."
— Legea 207/2015, art. 59^1 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„(1) Constituie probă orice element de fapt care servește la constatarea unei stări de fapt fiscale, [...] fişierul standard de control fiscal stocat într-un mediu care asigură unicitatea, integralitatea şi integritatea acestuia, [...]"
— Legea 207/2015, art. 55 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Din aceste texte rezultă cadrul legal, nu un mecanism tehnic concret publicat: ANAF are dreptul de analiză de risc pe baza oricăror informații de care dispune — inclusiv fișierul standard de control fiscal (D406), care conține, printre altele, jurnalul de vânzări/cumpărări și tranzacțiile contabile ale perioadei — și îl poate folosi ca probă alături de declarațiile deja depuse, precum D300 sau D394. Legea nu detaliază public un algoritm de confruntare automată D406↔D300↔D394; ea stabilește doar cadrul (analiza de risc, dreptul de a folosi fișierul ca probă), procedurile interne de verificare rămânând nepublicate.

## Ce se greșește în practică

- Se presupune că lipsa unui „algoritm public" înseamnă că ANAF nu poate face nicio corelare între D406 și celelalte declarații — cadrul legal (art. 1 pct. 3, art. 55) permite explicit folosirea oricărei informații disponibile, inclusiv SAF-T, în analiza de risc.
- Se confundă obligația de depunere D406 (art. 59^1) cu o garanție că datele din D406 vor coincide automat, cifră cu cifră, cu D300/D394 — cele trei surse au scopuri și granularități diferite (D406 e evidența completă, D300 e decontul de TVA, D394 e doar subsetul de operațiuni raportabile B2B), așa că diferențe legitime pot apărea fără să însemne eroare.
- Se așteaptă ca un software de contabilitate să garanteze coerența perfectă între cele trei declarații doar pentru că le generează pe toate — coerența depinde de completitudinea și corectitudinea datelor introduse, nu doar de generator.

## Ce face iConta.eu

iConta.eu generează atât D406 (SAF-T), cât și D300 și D394, fiecare validat local prin validatorul oficial ANAF (DUK) înainte de a fi considerat gata de depus. Aplicația are un motor propriu de verificare încrucișată declarație-vs-contabilitate (`core/control_incrucisat.py`), care compară, de exemplu, TVA colectată/dedusă din D300 cu rulajele conturilor 4427/4426, sau bazele intracomunitare din D390 cu evidența validată a acelorași facturi — fiecare verificare își declară explicit sursele și limita.

La data acestui ghid însă, **iConta.eu nu are o comparație automată dedicată între D406 (SAF-T) și D300/D394** — nu există în cod niciun modul care confrunte cele trei declarații între ele pe acest palier. Dacă vrei să verifici coerența lor, poți compara manual cifrele generate (venituri/TVA colectată din jurnalul de vânzări al D406 față de rândurile D300, respectiv operațiunile raportabile din D394), știind că diferențe legitime pot apărea din cauza scopurilor diferite ale celor trei declarații.

[iConta.eu](/)
