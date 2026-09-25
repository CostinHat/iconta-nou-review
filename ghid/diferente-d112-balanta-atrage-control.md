---
title: "Ce diferențe între D112 și balanță pot atrage un control?"
description: "De ce discrepanțele dintre D112 și balanța contabilă contează în analiza de risc a ANAF, care stă la baza selecției pentru inspecție fiscală."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce diferențe între D112 și balanță pot atrage un control?

Legea nu are un articol care să enumere explicit „diferența dintre D112 și balanță" ca motiv de control. Ce există, în schimb, e mecanismul general prin care ANAF selectează contribuabilii pentru inspecție fiscală: analiza de risc. O discrepanță între ce a fost declarat prin D112 (salarii, contribuții, angajați) și ce arată balanța contabilă (conturile 421, 431, 444) e exact genul de semnal pe care acest mecanism e construit să-l identifice.

## Temeiul legal

::: ghid-temei
„3. analiza de risc - activitatea efectuată de organul fiscal în scopul identificării riscurilor de neconformare în ceea ce privește îndeplinirea de către contribuabil/plătitor a obligațiilor prevăzute de legislația fiscală, de a le evalua, de a le gestiona, precum și de a le utiliza în scopul efectuării activităților de administrare fiscală [...]
ART. 121 (1) [...] selectarea contribuabililor/plătitorilor pentru efectuarea acțiunii de inspecție fiscală se efectuează la nivelul aparatului central al ANAF, în funcție de nivelul riscului stabilit pe baza analizei de risc."
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 1 pct. 3 și art. 121 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Legea nu detaliază public criteriile exacte de risc (ele sunt, de regulă, interne A.N.A.F.), dar principiul e clar: orice neconcordanță între ce declari și ce ai în contabilitate alimentează scorul de risc care determină selecția pentru inspecție. Tipuri de diferențe D112–balanță relevante în practică:

- **Numărul de salariați/contracte active** declarat în D112 nu corespunde cu soldul contului 421 „Personal — salarii datorate" din balanță pentru luna respectivă.
- **Suma brută a salariilor** din D112 diferă de rulajul contului 641 „Cheltuieli cu salariile personalul" pentru aceeași perioadă.
- **Contribuțiile calculate și reținute** (CAS, CASS, impozit pe venit din salarii) din D112 nu se regăsesc, ca sold, în conturile 4315 „Contribuția de asigurări sociale", 4316 „Contribuția de asigurări sociale de sănătate" și 444 „Impozitul pe venituri de natura salariilor" corespunzătoare.
- Legea prevede explicit un mecanism de „a doua șansă" înainte de inspecție: notificarea de conformare — „organul de inspecție fiscală transmite [...] o notificare de conformare cu privire la riscurile fiscale identificate [...] cu privire la posibilitatea de a depune sau de a corecta declarațiile fiscale", cu un termen de 30 de zile (art. 121^1 din aceeași lege).

## Ce se greșește în practică

- Se depune D112 din memoria salariilor plătite efectiv, nu din datele contabile ale lunii de referință, generând sistematic mici diferențe cu balanța.
- Nu se rulează, lunar, o reconciliere internă între D112 depus și conturile de personal/contribuții — diferența se descoperă abia la un control.
- Se ignoră notificarea de conformare primită de la ANAF, deși legea dă expres un termen de 30 de zile pentru corectarea declarațiilor înainte de declanșarea propriu-zisă a inspecției.
- Se rectifică D112 fără să se actualizeze și înregistrările contabile corespunzătoare (sau invers), perpetuând diferența în loc s-o închidă.

## Ce face iConta.eu

iConta.eu are un modul dedicat de reconciliere pentru D112 (`d112_reconciliere.py`, cu funcțiile `reconciliaza` și `verifica_reconciliere`), care compară valorile calculate/declarate în D112 cu datele din motorul de salarizare al aplicației, exact pentru a prinde din timp acest tip de diferențe. Reconcilierea se face la nivelul motorului de calcul al salariilor, nu direct contra unei balanțe contabile externe — dacă firma ține contabilitatea în alt program decât cel de salarizare din iConta.eu, verificarea finală față de balanță rămâne un pas manual al contabilului.

[iConta.eu](/)
