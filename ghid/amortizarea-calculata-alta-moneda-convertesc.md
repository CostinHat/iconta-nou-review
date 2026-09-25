---
title: "Amortizarea calculată în altă monedă: cum o convertesc"
description: "Ce curs de schimb se folosește la înregistrarea și amortizarea unui mijloc fix achiziționat sau facturat în valută, potrivit legii contabilității și reglementărilor OMFP 1802/2014."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Amortizarea calculată în altă monedă: cum o convertesc

Un mijloc fix achiziționat printr-o factură în euro sau dolari nu se amortizează în valută: contabilitatea românească se ține în lei, iar valoarea de intrare se stabilește o singură dată, la cursul de la data recunoașterii, după care rămâne fixă pe toată durata de amortizare — nu se recalculează lunar în funcție de cursul BNR curent.

## Temeiul legal

::: ghid-temei
„(1) Contabilitatea se ține în limba română și în moneda națională. (2) Contabilitatea operațiunilor efectuate în valută se ține atât în moneda națională, cât și în valută, potrivit reglementărilor elaborate în acest sens."
— Legea nr. 82/1991 (legea contabilității), art. 3 alin. (1)-(2) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

- Contabilitatea entității se ține **în lei**, indiferent de moneda în care e emisă factura furnizorului.
- Pentru operațiunile în valută, conversia se face la **cursul de schimb comunicat de BNR** din ultima zi bancară anterioară operațiunii — principiu aplicat de OMFP 1802/2014 și pentru intrarea imobilizărilor corporale.
- Odată stabilită, valoarea de intrare în lei a mijlocului fix **nu se recalculează** la cursuri ulterioare doar pentru că achiziția a fost în valută — amortizarea rulează pe valoarea fixată la intrare, ca orice alt mijloc fix cumpărat în lei.
- Diferențele de curs valutar apar doar la decontarea efectivă a facturii către furnizor (plată), nu la calculul amortizării.

## Ce se greșește în practică

- Se reconvertește valoarea rămasă de amortizat la cursul BNR din fiecare lună, ceea ce face ca amortizarea lunară să fluctueze fără temei — mijlocul fix nu e un post monetar în valută.
- Se confundă diferența de curs din decontarea facturii (cheltuială/venit financiar) cu o ajustare a valorii contabile a mijlocului fix.
- Se folosește cursul BVB sau cursul afișat de bancă la data plății, în loc de cursul BNR din ultima zi bancară anterioară datei operațiunii de recunoaștere a activului.

## Ce face iConta.eu

La data acestui ghid, modulul de mijloace fixe din iConta.eu **nu are o funcție dedicată de conversie valutară** la înregistrarea unui mijloc fix — nu am găsit în cod (`core/repo_mijloace_fixe.py`, `core/mijloace_fixe_import_api.py`) nicio referință la curs, monedă sau valută. Valoarea de intrare, contul de imobilizare și amortizarea se introduc și se calculează direct în lei; conversia facturii din valută în lei, la cursul BNR corect, rămâne în sarcina contabilului, înainte de introducerea valorii în evidența mijloacelor fixe.

[iConta.eu](/)
