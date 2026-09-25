---
title: "Ce document justifică împrumutul în numerar acordat firmei de asociat"
description: "Plafonul legal pentru împrumuturile acordate în numerar de o persoană fizică unei firme și documentul care trebuie să stea la baza operațiunii."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce document justifică împrumutul în numerar acordat firmei de asociat

Asociații care „injectează" bani în firmă rapid, în numerar, pentru o urgență de trezorerie, se lovesc de o limită legală strictă — și de nevoia unui document care să justifice, în fața unui eventual control, atât suma, cât și natura operațiunii.

## Temeiul legal

::: ghid-temei
„Operațiunile de încasări în numerar efectuate de persoanele prevăzute la art. 1 alin. (1), de la persoane fizice, reprezentând cesiuni de creanțe, primiri de împrumuturi sau alte finanțări, precum și contravaloarea unor livrări de bunuri sau a unor prestări de servicii se efectuează în limita unui plafon zilnic de 10.000 lei de la o persoană.
Sunt interzise încasările fragmentate de la o persoană, pentru operațiunile de încasări în numerar prevăzute la alin. (1), cu o valoare mai mare de 10.000 lei, precum și fragmentarea tranzacțiilor reprezentând cesiuni de creanțe, primiri de împrumuturi sau alte finanțări [...]"
— Legea nr. 70/2015, art. 4 alin. (1)-(2) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Din text rezultă atât plafonul, cât și logica documentului justificativ:

- **Plafonul e de 10.000 lei pe zi, de la aceeași persoană** — dacă asociatul vrea să împrumute firmei o sumă mai mare, excedentul peste 10.000 lei nu se poate încasa în numerar în aceeași zi; trebuie virat prin cont bancar.
- **Fragmentarea e interzisă explicit** — împărțirea unui împrumut de 20.000 lei în două tranșe de câte 10.000 lei, în aceeași zi sau în zile succesive, cu scopul de a eluda plafonul, e o încălcare a legii, nu o soluție.
- Documentul care justifică operațiunea în contabilitate e, potrivit principiului general al Legii contabilității (art. 6), cel care consemnează efectuarea ei — pentru o încasare în numerar de la asociat, acesta e de regulă un contract de împrumut (sau o notă/decizie a asociatului) plus documentul de casă (chitanța sau dispoziția de încasare către casierie) prin care suma intră efectiv în gestiunea firmei.

## Ce se greșește în practică

- Se împrumută firma cu sume mari, în numerar, într-o singură zi, depășind plafonul de 10.000 lei — operațiunea devine sancționabilă contravențional, indiferent de intenția bună a asociatului.
- Se fragmentează artificial împrumutul pe mai multe zile consecutive, considerând că astfel se respectă plafonul zilnic — legea interzice explicit exact acest tip de fragmentare.
- Se înregistrează suma încasată direct în contabilitate, fără contract de împrumut sau document de casă, ceea ce lasă operațiunea fără document justificativ, contrar principiului din Legea contabilității.

## Ce face iConta.eu

Verificat în cod: modulul `core/decontari_asociati.py` generează notele contabile pentru împrumutul de la asociat (contul 4551) — atât la primire (5121=4551), cât și la restituire, inclusiv cu dobânda și impozitul reținut, dacă e cazul. Funcția `nota_imprumut_asociat` din aplicație presupune însă mișcarea prin cont bancar (contul 5121), nu prin casierie — aplicația **nu verifică automat plafonul de 10.000 lei/zi pentru încasările în numerar** de la asociat și nu generează documentul de casă asociat unei astfel de operațiuni; pentru un împrumut acordat efectiv în numerar, respectarea plafonului și emiterea documentului justificativ rămân în sarcina contabilului.

[iConta.eu](/)
