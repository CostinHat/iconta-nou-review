---
title: "Cont bancar în valută pentru import-export"
description: Deschiderea unui cont bancar în valută e o decizie de business/bancă, nu o funcționalitate de contabilitate — ce ține de aplicație e conversia la cursul BNR și diferențele de curs valutar, aplicabile oricărei operațiuni în valută.
published: 2026-09-24
modified: 2026-10-13
poarta: v1
---

# Cont bancar în valută pentru import-export

Deschiderea unui cont bancar în valută pentru operațiuni de import-export este o decizie bancară și de business — alegerea băncii, a valutei, a comisioanelor — și nu o funcționalitate pe care o configurează o aplicație de contabilitate. Ce ține efectiv de partea de contabilitate sunt cele două consecințe fiscale ale oricărei operațiuni derulate printr-un asemenea cont: conversia sumelor la cursul BNR și eventualele diferențe de curs valutar rezultate.

## Temeiul legal

::: ghid-temei
„Dacă elementele folosite pentru stabilirea bazei de impozitare a unei operațiuni, alta decât importul de bunuri, se exprimă în valută, cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a României sau ultimul curs de schimb publicat de Banca Centrală Europeană ori cursul de schimb utilizat de banca prin care se efectuează decontările, valabil la data la care intervine exigibilitatea taxei pentru operațiunea în cauză [...]”
— Codul fiscal (Legea 227/2015), art. 290 alin. (2) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„O tranzacție în valută trebuie înregistrată inițial la cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunii.”
— OMFP 1802/2014 (Reglementările contabile), pct. 319 (sursă: [OMFP nr. 1802/2014 (Reglementările contabile privind situațiile financiare anuale individuale și consolidate)](https://legislatie.just.ro/Public/DetaliiDocument/164320))

„Diferențele de curs valutar care apar cu ocazia decontării creanțelor și datoriilor în valută la cursuri diferite față de cele la care au fost înregistrate inițial pe parcursul lunii sau față de cele la care sunt înregistrate în contabilitate trebuie recunoscute în luna în care apar, ca venituri sau cheltuieli din diferențe de curs valutar.”
— OMFP 1802/2014 (Reglementările contabile), pct. 322 alin. (1) (sursă: [OMFP nr. 1802/2014 (Reglementările contabile privind situațiile financiare anuale individuale și consolidate)](https://legislatie.just.ro/Public/DetaliiDocument/164320))
:::

Aceste două temeiuri sunt generale — se aplică oricărei operațiuni în valută dintr-o firmă, nu specific import-exportului extracomunitar. Un import sau export facturat în valută nu are, din perspectivă fiscală, o regulă separată de conversie sau de tratare a diferențelor de curs doar pentru că e o operațiune extracomunitară; mecanismul e identic cu cel al oricărei alte tranzacții în valută.

## Ce se greșește în practică

- Se caută în aplicația de contabilitate o funcție de "cont bancar în valută" care să gestioneze direct relația cu banca — deschiderea și administrarea contului rămân integral în sfera relației firmă-bancă, nu a softului de contabilitate.
- Se presupune că importul-exportul are o regulă specială de conversie valutară, diferită de restul operațiunilor firmei — cursul BNR aplicabil și tratarea diferențelor de curs sunt aceleași, indiferent de tipul operațiunii care generează suma în valută.
- Se ignoră diferențele de curs valutar apărute între data facturii și data încasării/plății, tratând suma în valută ca fiind "fixă" în lei pe toată durata operațiunii.

## Ce face iConta.eu

iConta.eu nu are — și nu are cum să aibă, fiind un soft de contabilitate, nu o bancă — o funcționalitate de "cont bancar în valută". Ce oferă aplicația sunt cele două funcționalități generale conexe, aplicabile oricărei operațiuni în valută, inclusiv celor de import-export: conversia la cursul BNR (funcționalitatea de curs valutar, temei art. 290 alin. 2 Cod fiscal) și calcularea automată a diferențelor de curs valutar la decontare (funcționalitatea dedicată, temei OMFP 1802/2014 pct. 316-322). Alegerea băncii și a contului rămâne o decizie de business a firmei, care se reflectă în aplicație doar prin sumele și cursurile operațiunilor efectiv înregistrate.

[iConta.eu](/)
