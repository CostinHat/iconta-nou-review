---
title: "Cum se gestionează stocurile la mai multe puncte de lucru"
description: Legea permite ținerea evidenței pe locuri de depozitare fără să impună un cost mediu separat pentru fiecare punct de lucru. Ce înseamnă asta practic și ce oferă, concret, iConta.eu la acest nivel.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se gestionează stocurile la mai multe puncte de lucru

O firmă cu mai multe puncte de lucru trebuie să știe, în orice moment, câtă marfă are la fiecare dintre ele. Asta nu înseamnă însă, automat, că fiecare punct de lucru are propriul cost mediu de gestiune — sunt două lucruri diferite, pe care legea le tratează distinct.

## Temeiul legal

::: ghid-temei
„Contabilitatea stocurilor se ține cantitativ și valoric sau numai valoric prin folosirea inventarului permanent sau a inventarului intermitent."

— OMFP 1802/2014, Anexa 1 (Reglementări contabile), pct. 289

„O diferență în localizarea geografică nu este suficientă pentru a justifica alegerea de metode diferite [de determinare a costului]."

— OMFP 1802/2014, Anexa 1 (Reglementări contabile), pct. 287 alin. (4)
:::

Primul text stabilește distincția de bază: contabilitatea de stocuri poate fi ținută cantitativ și valoric (pe fiecare articol, urmărind mișcarea reală) sau numai valoric (metoda global-valorică, tipică comerțului cu amănuntul). Al doilea text taie scurt o presupunere frecventă: faptul că firma are puncte de lucru la adrese diferite nu justifică, prin el însuși, o metodă de cost diferită de la un punct la altul. Costul mediu ponderat (CMP), acolo unde se aplică, rămâne unul singur la nivel de firmă — locația e o etichetă administrativă pe cantitate, nu un criteriu care schimbă modul de calcul al costului.

## Ce se greșește în practică

- Se așteaptă ca fiecare punct de lucru să aibă propriul cost mediu, de parcă ar fi o gestiune complet independentă — regula de la pct. 287 alin. (4) exclude exact această interpretare.
- Se denumesc punctele de lucru inconsecvent în documente și în evidența internă („Depozit 1", „depozit1", „D1") — fiecare variantă riscă să devină o „locație" distinctă în rapoarte, deși e vorba de același loc fizic.
- Se confundă „evidență pe locație" cu „gestiune cantitativ-valorică separată per depozit" — sunt niveluri diferite de detaliu, cu implicații diferite de cost și de raportare.

## Ce face iConta.eu

iConta.eu oferă, la acest nivel, evidența cantitativă pe locație: stocul fiecărui articol poate fi urmărit separat pe fiecare punct de lucru (câte bucăți/unități sunt la fiecare locație), iar transferurile între puncte de lucru se înregistrează prin funcția de transfer (F138). Costul mediu ponderat rămâne însă **unic la nivel de firmă** — nu separat pe fiecare punct de lucru; un transfer între locații e, din acest motiv, neutru pe valorizare (nu schimbă costul mediu, doar mută cantitatea).

De reținut o limitare tehnică reală: numele locației e text liber în sistem, fără o listă centralizată de gestiuni/puncte de lucru și fără validare a denumirii. Un typo la scrierea locației (de exemplu „Depozit1" în loc de „Depozit 1") creează, silențios, o locație nouă, distinctă, în rapoartele de stoc — recomandăm să stabiliți intern o denumire unică, exactă, pentru fiecare punct de lucru și să o folosiți consecvent.

Un cost mediu separat, propriu fiecărui depozit (gestiune cantitativ-valorică multiplă), e un nivel mai avansat, momentan amânat în dezvoltarea aplicației.

[iConta.eu](/)
