---
title: "Când se recunoaște venitul dintr-un abonament SaaS anual?"
description: "Regula contabilă de recunoaștere eșalonată a veniturilor din servicii prestate în timp, aplicată abonamentelor software facturate anual anticipat."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Când se recunoaște venitul dintr-un abonament SaaS anual?

Un abonament SaaS facturat anual anticipat pune o întrebare contabilă clasică: banii intră o dată, dar serviciul se prestează lună de lună, pe toată durata abonamentului. Reglementările contabile tranșează exact acest caz.

## Temeiul legal

::: ghid-temei
„446. - (1) Veniturile din prestări de servicii se înregistrează în contabilitate pe măsura efectuării acestora. Prestarea de servicii cuprinde inclusiv executarea de lucrări și orice alte operațiuni care nu pot fi considerate livrări de bunuri.
[...]
447. - În cazul în care prețul de vânzare include o valoare distinctă, specificată contractual, destinată prestării ulterioare de servicii (de exemplu, asistența tehnică și perfecționarea produsului după vânzarea unui program informatic), acea sumă este amânată (contul 472 «Venituri înregistrate în avans») și recunoscută ca venit pe parcursul perioadei în care se prestează serviciile, dar nu mai târziu de încheierea perioadei pentru care a fost contractată prestarea ulterioară de servicii."
— OMFP 1802/2014 (Reglementările contabile privind situațiile financiare anuale individuale și consolidate), pct. 446 alin. (1), pct. 447 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Aplicat la un abonament SaaS anual, facturat integral la începutul perioadei:

- **Venitul nu se recunoaște integral la facturare.** Suma încasată pentru un abonament de 12 luni corespunde unei obligații de a presta acces la serviciu pe toată acea perioadă — deci se înregistrează inițial în contul 472 „Venituri înregistrate în avans", nu direct în contul de venituri.
- **Recunoașterea se face pe măsura prestării serviciului** — de regulă liniar, lună de lună, pe durata abonamentului (pct. 446 alin. 1), cu excepția cazului în care există un tipar de consum diferit, dovedit obiectiv (de exemplu, consum concentrat la începutul perioadei).
- Dacă abonamentul e structurat ca **licență de tip „drept de acces"** la proprietatea intelectuală (accesul la platformă pe toată perioada licenței, cu actualizări continue) — cazul tipic al unui SaaS — normele metodologice (pct. 448^5-448^7) confirmă că venitul se recunoaște **în timp**, pe măsura executării obligației de a oferi acces, nu dintr-o dată, la momentul livrării unui „cod" sau al activării contului.
- Diferența față de o licență software „la un moment dat" (cazul unei licențe perpetue, vândute o singură dată, fără obligații ulterioare) e esențială: acolo venitul se recunoaște integral la transferul licenței, pentru că nu există o obligație de executare continuă.

## Ce se greșește în practică

- Se recunoaște integral venitul din abonamentul anual la data facturii, pentru că banii au fost încasați integral — încasarea nu e criteriul de recunoaștere; criteriul e prestarea efectivă a serviciului (contabilitate de angajamente, nu de casă).
- Se tratează abonamentul SaaS ca pe o vânzare de licență perpetuă (recunoaștere integrală la un moment dat), deși accesul continuu la platformă și actualizările fac din el o obligație de executare în timp, nu punctuală.
- Se uită reversarea lunară din contul 472 în contul de venituri — suma rămâne „blocată" în venituri în avans până la închiderea anului, deformând rezultatul lunar raportat.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are un modul dedicat pentru recunoașterea eșalonată a veniturilor din abonamente** (nu automatizează înregistrarea în contul 472 și reluarea lunară în contul de venituri) — nu există în cod o funcție care să gestioneze explicit „venituri înregistrate în avans". O firmă care facturează abonamente SaaS anuale înregistrează în prezent manual, prin notă contabilă, atât suma amânată la facturare, cât și reluarea ei lunară pe durata abonamentului, conform pct. 446-447 din OMFP 1802/2014.

[iConta.eu](/)
