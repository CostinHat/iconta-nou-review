---
title: "Stocuri vândute cu amănuntul: descărcare zilnică"
description: "De ce descărcarea de gestiune la metoda global-valorică nu se face zilnic, ci lunar, și ce se înregistrează totuși în fiecare zi."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Stocuri vândute cu amănuntul: descărcare zilnică

Titlul cere o procedură de descărcare „zilnică" a stocului la comerțul cu amănuntul. Răspunsul onest, pe baza dosarului tehnic verificat: la metoda global-valorică, descărcarea de gestiune (separarea cost/adaos/TVA neexigibilă) **nu se face zilnic**, ci lunar, cumulat de la începutul exercițiului financiar. Explicăm mai jos de ce, și ce se întâmplă totuși în fiecare zi.

## Temeiul legal

::: ghid-temei
OMFP 1802/2014, Anexa 1 — Reglementări contabile, pct. 286 alin. (4): „Repartizarea diferențelor de preț asupra valorii bunurilor ieșite și asupra stocurilor se efectuează cu ajutorul unui coeficient care se calculează astfel: Coeficient de repartizare = [Soldul inițial al diferențelor de preț + Diferențe de preț aferente intrărilor în cursul perioadei, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] / [Soldul inițial al stocurilor la preț de înregistrare + Valoarea intrărilor în cursul perioadei la preț de înregistrare, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] x 100."

(Text consolidat OMFP 1802/2014, verificat pe mirrorul local la 17.09.2026.)
:::

Coeficientul de repartizare (adaosul comercial ca procent din stoc) este, prin definiție legală, un calcul **cumulat de la începutul exercițiului financiar până la finele perioadei de referință**. Un calcul „zilnic" al acestui coeficient ar produce, practic, o valoare diferită în fiecare zi, pentru aceeași marfă — ceea ce contrazice logica de „coeficient mediu" pe care se bazează metoda.

## Ce se greșește în practică

Greșeala tipică este să se creadă că, după fiecare zi de vânzare, trebuie generată o notă contabilă separată de descărcare (607/378/4428). Aceasta ar duplica sau ar denatura calculul coeficientului, care este gândit să funcționeze pe rulaje cumulate, nu pe tranzacții izolate.

## Ce face iConta.eu

Vânzările zilnice (bonuri, facturi de marfă) se înregistrează curent, pe măsură ce au loc, în contul 707. Separarea cost/adaos/TVA neexigibilă (378, 4428) se face însă o singură dată pe lună: funcția `descarca_luna` din `core/stocuri_api.py` calculează coeficientul cumulat de la 1 ianuarie și generează o singură notă de descărcare, la data ultimei zile calendaristice a lunii, ca ciornă supusă validării contabilului. Conform cercetării care stă la baza acestui ghid, în cod (`core/stocuri.py`, `core/stocuri_api.py`) **nu există niciun mecanism de descărcare zilnică** pentru gestiunea global-valorică — singura frecvență implementată este cea lunară.

[iConta.eu](/)
