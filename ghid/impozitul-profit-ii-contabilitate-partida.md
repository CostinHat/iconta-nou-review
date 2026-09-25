---
title: "Impozitul pe profit la o II cu contabilitate în partidă dublă"
description: "O întreprindere individuală nu plătește niciodată impozit pe profit, nici dacă optează pentru contabilitate în partidă dublă — rămâne impozitată cu 10% pe venitul net, potrivit Titlului IV din Codul fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Impozitul pe profit la o II cu contabilitate în partidă dublă

Întrebarea pornește de la o confuzie destul de răspândită: impozitul pe profit (Titlul II din Codul fiscal) se aplică doar persoanelor juridice, iar o întreprindere individuală (II) — formă de organizare a unei persoane fizice autorizate — nu e persoană juridică, oricât de detaliată i-ar fi contabilitatea.

## Temeiul legal

::: ghid-temei
„Sunt obligate la plata impozitului pe profit, conform prezentului titlu, următoarele persoane, denumite în continuare contribuabili: a) persoanele juridice române, cu excepțiile prevăzute la alin. (2); [...]"
— art. 13 alin. (1) lit. a) din Legea 227/2015 (Codul fiscal) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

::: ghid-temei
„Cota de impozit este de 10% și se aplică asupra venitului impozabil corespunzător fiecărei surse din fiecare categorie pentru determinarea impozitului pe veniturile din: a) activități independente; [...]"
— art. 64 alin. (1) din Legea 227/2015 (Codul fiscal) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

::: ghid-temei
„Persoanele prevăzute la art. 2 lit. a) au obligația să conducă evidența contabilă pe baza regulilor contabilității în partidă simplă sau, la opțiunea acestora, pe baza regulilor contabilității în partidă dublă, cu excepția celor pentru care în actul normativ de înființare, în legi speciale sau în alte acte normative există prevederi exprese privind ținerea contabilității în partidă simplă."
— OMFP 170/2015, art. 3 (sursă: anaf_surse/omfp_170_2015.txt)
:::

- Impozitul pe profit (art. 13, Titlul II) e datorat de **persoanele juridice române** — o întreprindere individuală, întreprindere familială sau persoană fizică autorizată nu are personalitate juridică (e o formă de organizare a unei persoane fizice, potrivit OUG 44/2008), deci nu intră sub incidența acestui titlu, indiferent de mărimea sau complexitatea activității.
- Veniturile unei II rămân impozitate potrivit **Titlului IV — Impozitul pe venit**, ca venituri din activități independente, la cota de **10%** aplicată asupra venitului net anual (art. 64 alin. 1) — nu la cota de 16% specifică impozitului pe profit.
- Faptul că o II optează pentru contabilitate în **partidă dublă**, în loc de partidă simplă, e permis de OMFP 170/2015, dar e o alegere pur contabilă (privind modul de evidență), care **nu schimbă regimul fiscal** aplicabil — venitul net se determină în continuare în sistem real, potrivit Titlului IV, cu cota de 10%.

## Ce se greșește în practică

- Se presupune, din formularea „impozit pe profit", că o II ar putea datora acest impozit dacă are o contabilitate suficient de elaborată (partidă dublă) — regimul fiscal ține de forma juridică (persoană fizică vs. persoană juridică), nu de metoda contabilă aleasă.
- Se aplică, din eroare, cota de 16% (specifică impozitului pe profit) la venitul net al unei II, în loc de cota corectă de 10% (impozit pe venit, Titlul IV).
- Se confundă „contabilitate în partidă dublă" cu „persoană juridică" — o II care ține partidă dublă rămâne, din punct de vedere fiscal și juridic, o persoană fizică autorizată, nu o societate.

## Ce face iConta.eu

Acest subiect nu are legătură cu funcționalitatea de contabilitate ONG din iConta.eu (`core/ong.py`), care tratează exclusiv regimul special de impozit pe profit al organizațiilor nonprofit (art. 15 Cod fiscal) — o întreprindere individuală e o formă juridică complet diferită de o organizație nonprofit, iar niciun cod din acest modul nu atinge subiectul II/PFA. **iConta.eu nu are nicio funcție care să calculeze „impozit pe profit" pentru o II** — pentru că, legal, o întreprindere individuală nu datorează niciodată acest impozit, indiferent de tipul de contabilitate ales; veniturile ei sunt gestionate în aplicație prin modulele dedicate impozitului pe venit din activități independente.

[iConta.eu](/)
