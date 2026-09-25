---
title: "Ce acte suspendă termenul de prescripție fiscală?"
description: "Situațiile în care se suspendă termenul de 5 ani în care organul fiscal poate stabili creanțe fiscale, conform art. 111 din Codul de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce acte suspendă termenul de prescripție fiscală?

Dreptul organului fiscal de a stabili creanțe fiscale (impozite, taxe, contribuții) nu e nelimitat în timp — se prescrie în 5 ani. Dar acest termen nu curge neîntrerupt: legea prevede explicit situațiile în care se suspendă, adică se oprește temporar, fără să se resetteze.

## Temeiul legal

::: ghid-temei
„ART. 111 Întreruperea și suspendarea termenului de prescripție a dreptului de a stabili creanțe fiscale
[...]
(2) Termenele de prescripție prevăzute la art. 110 se suspendă:
a) în cazurile și în condițiile stabilite de lege pentru suspendarea termenului de prescripție a dreptului la acțiune;
b) pe perioada cuprinsă între data începerii inspecției fiscale/verificării situației fiscale personale și data emiterii deciziei de impunere ca urmare a efectuării inspecției fiscale/verificării situației fiscale personale, în condițiile respectării duratei legale de efectuare a acestora;
c) pe timpul cât contribuabilul/plătitorul se sustrage de la efectuarea inspecției fiscale/verificării situației fiscale personale;
d) pe perioada cuprinsă între data declarării unui contribuabil/plătitor inactiv și data reactivării acestuia.
e) pe perioada cuprinsă între data comunicării către organele de urmărire penală a procesului-verbal de sesizare a organelor de urmărire penală sau a procesului-verbal întocmit ca urmare a solicitării organelor de urmărire penală [...] și data rămânerii definitive a soluției de rezolvare a cauzei penale.
f) pe perioada cuprinsă între data decesului persoanei fizice la care era în curs de desfășurare o acțiune de inspecție fiscală/verificare a situației fiscale personale și data luării la cunoștință de către organul de inspecție/verificare că există sau nu succesori, după caz."
— Legea 207/2015 (Codul de procedură fiscală), art. 111 alin. (2) lit. a)-f) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Termenul de bază, de la care pleacă toate aceste suspendări, e cel de la art. 110: **5 ani, cu începere de la 1 iulie a anului următor celui pentru care se datorează obligația fiscală** (10 ani, dacă obligația rezultă dintr-o infracțiune, de la data faptei).

Situațiile concrete de suspendare, cele mai relevante pentru o firmă:

- **Perioada inspecției fiscale** (lit. b) — de la data începerii inspecției până la emiterea deciziei de impunere, dar numai dacă inspecția respectă durata legală maximă. O inspecție care depășește nejustificat termenele legale nu mai beneficiază de această suspendare.
- **Sustragerea de la inspecție** (lit. c) — dacă firma evită efectiv controlul (nu se prezintă, nu pune la dispoziție documentele), termenul se oprește cât timp durează sustragerea.
- **Declararea contribuabilului inactiv** (lit. d) — de la data declarării inactivității fiscale și până la reactivare, termenul de prescripție nu curge.
- **Sesizarea penală** (lit. e) — dacă fapta constatată e trimisă organelor de urmărire penală, termenul se suspendă până la soluția definitivă a cauzei penale, indiferent cât durează procesul.

Important: suspendarea diferă de **întrerupere** (art. 111 alin. 1) — întreruperea „resetează" termenul, care începe să curgă din nou de la zero; suspendarea doar îl oprește temporar, iar la încetarea cauzei, termenul continuă de unde a rămas.

## Ce se greșește în practică

- Se confundă suspendarea cu întreruperea, calculând greșit termenul rămas — suspendarea nu anulează timpul deja scurs înainte de cauza de suspendare, doar îl „pune pe pauză".
- Se presupune că orice inspecție fiscală, indiferent de durată, suspendă automat termenul — legea condiționează suspendarea de respectarea duratei legale de efectuare a inspecției (lit. b); o inspecție tărăgănată peste limitele legale nu beneficiază automat de suspendare.
- Se ignoră perioada de inactivitate fiscală ca motiv de suspendare — o firmă declarată inactivă și apoi reactivată poate constata că termenul de prescripție „s-a lungit" cu exact perioada de inactivitate, nu s-a scurs normal.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu calculează și nu urmărește termenul de prescripție a dreptului organului fiscal de a stabili creanțe fiscale** — nu există în cod o funcție dedicată acestui calcul. Aplicația are un modul de control fiscal (`core/control_fiscal_api.py`) care urmărește obligațiile declarative curente ale firmei (termene de depunere, obligații datorate pe fiecare tip de declarație), dar acesta e un calendar de conformare, diferit conceptual de termenul de prescripție discutat aici; verificarea prescripției rămâne o evaluare juridică separată, în sarcina contabilului sau a unui consultant fiscal.

[iConta.eu](/)
