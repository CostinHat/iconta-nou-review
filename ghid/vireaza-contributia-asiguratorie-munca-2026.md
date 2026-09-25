---
title: "Când se virează contribuția asiguratorie de muncă 2026"
description: "Termenul legal de plată a contribuției asiguratorii pentru muncă (CAM), datorată de angajatori pentru veniturile din salarii."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când se virează contribuția asiguratorie de muncă 2026

Contribuția asiguratorie pentru muncă (CAM) este datorată de angajatori pentru veniturile din salarii și asimilate salariilor, într-un cont distinct al bugetului de stat. Termenul de plată urmează logica generală a contribuțiilor sociale plătite de angajator, dar merită confirmat direct din text, pentru că se leagă de perioada de referință a veniturilor plătite, nu de o dată fixă de calendar.

## Temeiul legal

```
::: ghid-temei
„...au obligația de a calcula contribuția asiguratorie pentru muncă și de a o plăti la bugetul de stat, într-un cont distinct, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile sau până la data de 25 inclusiv a lunii următoare trimestrului pentru care se plătesc veniturile, după caz."
— Legea nr. 227/2015 privind Codul fiscal, art. 220^6 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::
```

Reguli practice care rezultă din text:

- **Termenul standard este 25 a lunii următoare** celei pentru care se plătesc veniturile din salarii — aceeași dată ca la CAS, CASS și impozitul pe venitul din salarii reținute de angajator, declarate prin D112.
- Pentru angajatorii care aplică **declarare trimestrială** (plătitori de venituri salariale care se încadrează în categoriile pentru care legea permite acest regim), termenul se mută la 25 a lunii următoare trimestrului, nu următoare lunii.
- CAM se plătește **într-un cont distinct**, nu cumulat cu celelalte contribuții — o eroare de virare pe contul greșit nu stinge obligația, chiar dacă suma ajunge la bugetul de stat.
- Obligația de **declarare** a CAM se face, potrivit legii, până la același termen de plată prevăzut la art. 220^6, prin declarația unică D112.

## Ce se greșește în practică

- Se virează CAM pe același cont ca CAS/CASS angajator, din obișnuință sau dintr-o setare greșită de OP, iar suma nu se stinge automat pe obligația corectă.
- Se aplică termenul lunar (25 a lunii următoare) și în cazul angajatorilor cu declarare trimestrială, care au de fapt un termen diferit, legat de trimestru.
- Se omite plata CAM pentru veniturile asimilate salariilor (de exemplu, indemnizații ale administratorilor cu contract de mandat), considerându-se — greșit — că se aplică doar la salariile propriu-zise.

## Ce face iConta.eu

La data acestui ghid, salarizarea din `core/` (modulele legate de D112 și de stat de plată) calculează contribuțiile datorate de angajator, inclusiv CAM, pe baza veniturilor înregistrate; declarația D112 generată de aplicație a fost verificată, conform disciplinei proiectului, pe validatorul oficial ANAF. Distincția între regimul lunar și cel trimestrial de declarare rămâne o setare pe care contabilul o confirmă pentru fiecare firmă, în funcție de încadrarea ei legală.

[iConta.eu](/)
