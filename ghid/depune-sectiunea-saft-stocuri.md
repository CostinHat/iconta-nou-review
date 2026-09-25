---
title: "Când se depune secțiunea SAF-T Stocuri?"
description: "Spre deosebire de restul declarației D406, secțiunea Stocuri nu se depune periodic, ci doar la solicitarea expresă a ANAF, cu termen minim de 30 de zile calendaristice."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când se depune secțiunea SAF-T Stocuri?

Secțiunea „Stocuri" din fișierul standard de control fiscal (SAF-T, D406) are un regim de depunere complet diferit de restul declarației. Dacă majoritatea informațiilor SAF-T se transmit lunar sau trimestrial, secțiunea Stocuri **nu se depune periodic** — se transmite doar când Agenția Națională de Administrare Fiscală o solicită expres, iar contribuabilul are un termen minim garantat de 30 de zile calendaristice ca să răspundă.

## Temeiul legal

::: ghid-temei
„1. Declaraţia informativă D406 se transmite în format electronic, data-limită de transmitere fiind: - ultima zi calendaristică a lunii următoare perioadei de raportare, respectiv luna/trimestrul calendaristic, după caz, pentru alte informaţii decât cele privind secţiunile «Stocuri» şi «Active»; - la termenul de depunere a situaţiilor financiare aferente exerciţiului financiar, în cazul secţiunii «Active»; - la termenul stabilit de organul fiscal central, care nu poate fi mai mic de 30 de zile calendaristice de la data solicitării, în cazul secţiunii «Stocuri».
9. Informaţiile privind «stocurile de produse» şi «producţie în curs» sunt transmise pe baza unei solicitări specifice din partea organelor fiscale centrale. În funcţie de perioada pentru care se solicită furnizarea informaţiilor privind stocurile prin fişierul standard de control fiscal (SAF-T), contribuabilii furnizează una sau mai multe declaraţii informative cuprinzând subsecţiunile din fişierul SAF-T relevante pentru «Stocuri», separate pentru fiecare dintre lunile/trimestrele calendaristice cuprinse în perioada pentru care a fost trimisă solicitarea din partea organelor fiscale centrale.
10. Declaraţiile informative D406 pentru «Stocuri» se depun în termenul stabilit de organul fiscal central, care nu poate fi mai mic de 30 de zile calendaristice de la data solicitării."
— OPANAF 1783/2021, Anexa 4 („Termenele de transmitere ... a fişierului standard de control fiscal SAF-T"), pct. 1 (a treia liniuță), pct. 9 și pct. 10 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Din text rezultă trei lucruri clare:

- Termenul lunar/trimestrial din regula generală **nu se aplică** secțiunii Stocuri — acesta e valabil doar pentru „alte informații" decât Stocuri și Active.
- Declanșatorul e o **solicitare specifică din partea ANAF**, nu o obligație periodică autonomă a contribuabilului.
- Termenul de răspuns e **minim 30 de zile calendaristice** de la solicitare — ANAF poate acorda mai mult, dar nu mai puțin de atât.

## Ce se greșește în practică

- Se așteaptă un termen lunar sau trimestrial pentru secțiunea Stocuri, similar restului SAF-T-ului, și se pregătește fișierul „din obligație", fără să existe o solicitare ANAF care să-l declanșeze.
- Se confundă termenul secțiunii Stocuri cu cel al secțiunii Active (care are alt regim — la termenul de depunere a situațiilor financiare anuale).
- Se ignoră faptul că solicitarea ANAF poate viza una sau mai multe perioade anterioare, caz în care se depun mai multe declarații informative distincte, câte una pentru fiecare lună/trimestru cuprins în solicitare — nu o singură declarație cumulată.

## Ce face iConta.eu

iConta.eu generează, la cerere directă din partea contabilului, fragmentul „Stocuri" (secțiunea PhysicalStock din SAF-T), pe baza mișcărilor de stoc înregistrate pentru firmele care țin gestiune cantitativ-valorică. Fragmentul se produce printr-un endpoint separat, pe un interval de date introdus manual (nu are ecran dedicat în interfață, la data acestui ghid) — nu e încorporat automat în declarația D406 lunară principală, exact conform naturii „la cerere" descrise mai sus.

Important de spus onest: iConta.eu **nu urmărește termenul legal de 30 de zile** — aplicația nu ține evidența datei la care a fost primită o solicitare ANAF și nu calculează sau alertează asupra scadenței de răspuns. Generarea fragmentului rămâne exclusiv o acțiune manuală, declanșată de contabil când decide el, nu un flux legat de o notificare ANAF primită.

[iConta.eu](/)
