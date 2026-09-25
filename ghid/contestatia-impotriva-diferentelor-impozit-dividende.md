---
title: "Contestația împotriva diferențelor de impozit pe dividende"
description: "Termenul, forma și procedura de contestare a unei decizii de impunere prin care ANAF stabilește diferențe de impozit pe dividende, conform Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Contestația împotriva diferențelor de impozit pe dividende

Când un control sau o verificare documentară ANAF stabilește diferențe de impozit pe dividende față de ce a fost deja declarat prin D205 (de exemplu pe o cotă aplicată greșit sau pe o distribuire considerată neplătită la termen), firma sau contribuabilul vizat are dreptul să conteste decizia de impunere. Procedura nu e specifică dividendelor — e cea generală, comună tuturor actelor administrativ-fiscale, din Codul de procedură fiscală.

## Temeiul legal

::: ghid-temei
„(1) Contestația se depune în termen de 45 de zile de la data comunicării actului administrativ fiscal, sub sancțiunea decăderii."
— Legea 207/2015 (Codul de procedură fiscală), art. 270 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Restul mecanismului, verificat la sursă în același text de lege:

- **Cine poate contesta** (art. 268 alin. (1)-(2)): „împotriva titlului de creanță, precum și împotriva altor acte administrative fiscale se poate formula contestație" — e îndreptățit „numai cel care consideră că a fost lezat în drepturile sale". Pentru dividende, contestă de regulă firma plătitoare (a emis D205 și a fost obligată la o diferență de impozit reținut), dar și un beneficiar poate contesta o decizie referitoare la baza de impozitare care îl privește (art. 268 alin. (5)).
- **Forma** (art. 269 alin. (1)): scrisă, cu datele contestatorului, obiectul, motivele de fapt și de drept, dovezile, semnătura. Se depune la organul fiscal emitent, fără taxă de timbru (art. 269 alin. (4)).
- **Termenul** (art. 270 alin. (1)): 45 de zile de la comunicarea actului, sub sancțiunea decăderii — depășirea termenului duce la respingerea contestației fără analiză pe fond.
- **Introducerea contestației nu suspendă executarea** actului atacat (art. 278 alin. (1)) — impozitul stabilit rămâne exigibil cât timp contestația e în curs, cu excepția unei suspendări obținute separat, în instanță, potrivit Legii contenciosului administrativ 554/2004.
- **Soluția** (art. 279): contestația poate fi admisă sau respinsă, total sau parțial; decizia poate anula actul, îl poate confirma sau îl poate desființa (trimițând organul fiscal să emită un act nou, strict pe considerentele deciziei).
- **Calea de atac** (art. 281 alin. (2)): decizia de soluționare a contestației poate fi atacată la instanța de contencios administrativ competentă.

## Ce se greșește în practică

- Se lasă să treacă termenul de 45 de zile în așteptarea unei discuții informale cu inspectorul — termenul curge de la comunicare, nu de la ultima discuție, și decăderea e sancțiunea automată.
- Se presupune că depunerea contestației oprește obligația de plată — nu o face; dobânzile și penalitățile continuă să curgă dacă suma nu e achitată, cu excepția unei suspendări obținute separat în instanță.
- Se contestă doar suma, fără să se individualizeze pe categorii de creanțe fiscale (impozit, accesorii) — art. 269 alin. (3) cere această precizare, iar organul fiscal poate cere completarea în 5 zile, altfel se consideră contestat întregul act.

## Ce face iConta.eu

Contestarea unui act administrativ-fiscal e o procedură care se poartă în întregime în afara aplicației, la organul fiscal emitent și, eventual, în instanță — iConta.eu nu are un modul de gestionare a contestațiilor fiscale.

Ce face F029 (D205 + distribuire dividende) este partea preventivă, nu cea de contestare: motorul de generare a D205 rulează o **a doua cale de verificare independentă** (`d205_reconciliere.py`), care recalculează separat, din contul 457, baza și impozitul pe fiecare beneficiar și compară rezultatul cu ce a produs generatorul — orice divergență blochează generarea declarației, tocmai ca să reducă riscul de a depune o D205 cu diferențe pe care ANAF le-ar putea contesta ulterior printr-o decizie de impunere. Dincolo de acest gard intern, dacă diferența de impozit a fost deja stabilită de ANAF printr-un act administrativ, pasul de contestare propriu-zis — redactarea, depunerea și urmărirea ei — rămâne integral responsabilitatea contribuabilului sau a contabilului, prin canalele oficiale (ANAF, SPV, instanță).

[iConta.eu](/)
