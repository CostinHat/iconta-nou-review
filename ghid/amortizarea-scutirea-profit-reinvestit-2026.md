---
title: "Amortizarea și scutirea pentru profit reinvestit 2026"
description: "Condițiile scutirii de impozit pe profit pentru profitul reinvestit în echipamente tehnologice și obligația de păstrare a activelor, conform Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Amortizarea și scutirea pentru profit reinvestit 2026

Scutirea de impozit pe profit pentru profitul reinvestit este una dintre puținele facilități fiscale românești valabile de mai mulți ani fără întrerupere — dar vine cu o obligație de păstrare a activelor, iar nerespectarea ei duce la recalcularea impozitului.

## Temeiul legal

::: ghid-temei
„Articolul 22 Scutirea de impozit a profitului reinvestit
(1) Profitul investit în echipamente tehnologice, active utilizate în activitatea de producție și procesare, activele reprezentând retehnologizare, calculatoare electronice și echipamente periferice, mașini și aparate de casă, de control și de facturare, în programe informatice, precum și pentru dreptul de utilizare a programelor informatice, produse și/sau achiziționate, inclusiv în baza contractelor de leasing financiar, și puse în funcțiune, folosite în scopul desfășurării activității economice, este scutit de impozit. [...]
(8) Contribuabilii care beneficiază de prevederile alin. (1) au obligația de a păstra în patrimoniu activele respective cel puțin o perioadă egală cu jumătate din durata de utilizare economică, stabilită potrivit reglementărilor contabile aplicabile, dar nu mai mult de 5 ani. În cazul nerespectării acestei condiții, pentru sumele respective se recalculează impozitul pe profit și se percep creanțe fiscale accesorii potrivit Codului de procedură fiscală, de la data aplicării facilității, potrivit legii."
— Legea 227/2015 (Codul fiscal), art. 22 alin. (1) și alin. (8) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul scutirii, așa cum rezultă din textul legal:

- **Ce se scutește**: profitul contabil brut cumulat de la începutul anului, investit în categoriile de active enumerate (echipamente tehnologice, active de producție/procesare, retehnologizare, calculatoare, case de marcat, programe informatice), puse efectiv în funcțiune.
- **Limita scutirii**: impozitul pe profit scutit nu poate depăși impozitul pe profit calculat cumulat de la începutul anului până în trimestrul/anul punerii în funcțiune a activelor.
- **Obligația de păstrare**: activele pentru care s-a beneficiat de scutire trebuie păstrate în patrimoniu **cel puțin jumătate din durata de utilizare economică, dar nu mai mult de 5 ani**.
- **Sancțiunea**: dacă activul este scos din patrimoniu înainte de acest termen, impozitul pe profit se **recalculează**, cu accesorii fiscale, de la data aplicării facilității — cu excepția situațiilor expres exceptate (reorganizări, lichidare/faliment, distrugere/pierdere/furt dovedite, sau scoatere din patrimoniu ca urmare a unor obligații legale).
- Suma pentru care s-a beneficiat de scutire, mai puțin partea de rezervă legală, se repartizează cu prioritate la rezerve, la sfârșitul exercițiului sau în anul următor.

## Ce se greșește în practică

- Se aplică scutirea și pentru active care nu se încadrează în categoriile enumerate expres la alin. (1) — de exemplu, mobilier de birou sau autovehicule care nu sunt echipamente tehnologice.
- Se vinde sau se casează un activ pentru care s-a beneficiat de scutire înainte de termenul de păstrare (jumătate din durata de utilizare, plafonat la 5 ani), fără să se recalculeze impozitul pe profit aferent.
- Se calculează scutirea peste limita impozitului pe profit datorat cumulat de la începutul anului până la punerea în funcțiune, depășind plafonul legal.

## Ce face iConta.eu

Am verificat în `core/d101.py` și `core/repo_mijloace_fixe.py`: nu am găsit o funcție dedicată care să calculeze automat scutirea de profit reinvestit conform art. 22 sau care să urmărească obligația de păstrare a activelor pe durata legală (jumătate din durata de utilizare, maximum 5 ani) și să alerteze la o eventuală înstrăinare prematură. Calculul scutirii și verificarea condiției de păstrare rămân, la acest moment, în sarcina contabilului.

[iConta.eu](/)
