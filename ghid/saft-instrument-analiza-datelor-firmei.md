---
title: "SAF-T ca instrument de analiză a datelor firmei"
description: "Ce este fișierul standard de control fiscal (SAF-T/D406), cine e obligat să-l depună și de ce datele lui pot fi folosite și intern, nu doar pentru raportare către ANAF."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# SAF-T ca instrument de analiză a datelor firmei

Fișierul standard de control fiscal (SAF-T), depus prin Declarația informativă D406, e cunoscut mai ales ca o obligație de raportare către ANAF. Mai puțin cunoscut e că structura lui — jurnale, stocuri, active, tranzacții pe conturi — e, de fapt, o oglindă completă a contabilității firmei, utilă și pentru analiză internă.

## Temeiul legal

::: ghid-temei
„3. Următoarele categorii de contribuabili au obligația de depunere a fișierului standard de control fiscal (SAF-T), prin intermediul Declarației informative D406: - regiile autonome; - institutele naționale de cercetare-dezvoltare; - societățile pe acțiuni (S.A.); - societățile în comandită pe acțiuni (SCA); - societățile în comandită simplă (SCS); - societățile în nume colectiv (SNC); - societățile cu răspundere limitată (S.R.L.) [...]"
— OPANAF nr. 1.783/2021, Anexa 5 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Câteva repere despre ce conține și cine depune SAF-T:

- Obligația de depunere se aplică **treptat**, în funcție de categoria de contribuabil: marii contribuabili din 1 ianuarie 2022, contribuabilii mijlocii din 1 ianuarie 2023, iar contribuabilii mici din 1 ianuarie 2025 — cei nou-înregistrați intră în obligație de la data efectivă a înregistrării, ulterior datei de referință a categoriei lor.
- SAF-T nu e doar un „export XML" pentru ANAF: structura lui (definită prin standardul internațional SAF-T, adaptat la particularitățile românești) organizează în același fișier jurnalul contabil, registrul de stocuri (mișcări cantitative și valorice), mijloacele fixe și tranzacțiile de vânzare/cumpărare — practic un instantaneu complet al perioadei raportate.
- Tocmai pentru că e complet și structurat, fișierul SAF-T poate fi refolosit ca sursă pentru **rapoarte interne** de gestiune (rulaje pe conturi, mișcări de stoc, evoluția achizițiilor/vânzărilor pe perioade) — fără să fie nevoie de o extragere separată din contabilitate pentru fiecare analiză.
- Declarația se validează cu un instrument oficial ANAF (Validatorul SAF-T), disponibil public, care verifică structura XML înainte de depunere — același instrument poate fi rulat și doar pentru verificare, fără depunere.

## Ce se greșește în practică

- Se tratează SAF-T exclusiv ca o corvoadă de raportare, generată o dată pe lună/trimestru și uitată, fără să se exploateze faptul că datele din el pot arăta discrepanțe (de exemplu între stocul contabil și cel fizic) mai devreme decât un inventar clasic.
- Se ignoră datele de referință pe categorii de contribuabili și se presupune că obligația a intrat în vigoare pentru toată lumea deodată — o firmă mică poate avea o dată de intrare în obligație diferită de una mijlocie sau mare.
- Nu se validează fișierul înainte de depunere cu instrumentul oficial, ceea ce duce la respingeri repetate și la pierderea termenului de raportare.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează Declarația informativă D406 direct din datele contabile ale firmei (jurnal, stocuri, mijloace fixe), fără o extragere manuală separată — structura fișierului e construită din aceleași înregistrări pe care contabilul le vede în aplicație la zi, ceea ce face posibilă și o citire a lui ca instrument de verificare internă, nu doar ca obligație de depunere.

[iConta.eu](/)
