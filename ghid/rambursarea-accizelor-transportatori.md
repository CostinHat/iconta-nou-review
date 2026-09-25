---
title: "Rambursarea accizelor pentru transportatori"
description: "Condițiile legale în care transportatorii rutieri de marfă sau persoane pot beneficia de restituirea diferenței dintre acciza standard și acciza redusă pentru motorină."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Rambursarea accizelor pentru transportatori

Firmele de transport rutier care folosesc motorină ca și carburant pot beneficia, în anumite condiții, de un nivel redus al accizei — nu printr-o scutire directă la pompă, ci prin restituirea diferenței dintre acciza standard și cea redusă, aplicată operatorilor licențiați în Uniunea Europeană.

## Temeiul legal

::: ghid-temei
„Pentru motorină se poate aplica un nivel redus al accizelor atunci când este utilizată drept carburant pentru motor în următoarele scopuri: a) transport rutier de mărfuri în cont propriu sau pentru alte persoane, cu autovehicule ori ansambluri de vehicule articulate destinate exclusiv transportului rutier de mărfuri și cu o greutate brută maximă autorizată de cel puțin 7,5 tone; b) transportul de persoane, regulat sau ocazional, cu excepția transportului public local de persoane, cu un autovehicul din categoria M2 ori M3 [...].
(10) Nivelul redus al accizelor prevăzut la alin. (9) se stabilește prin hotărâre a Guvernului și nu poate fi mai mic decât nivelul minim prevăzut în Directiva 2003/96/CE [...]. Reducerea nivelului accizelor se realizează prin restituirea sumelor reprezentând diferența dintre nivelul standard al accizelor și nivelul redus al accizelor către operatorii economici licențiați în Uniunea Europeană. Condițiile, procedura și termenele de restituire se stabilesc prin hotărâre a Guvernului."
— Legea 227/2015 (Codul fiscal), art. 342 alin. (9) lit. a), b) și alin. (10) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă din text pentru un transportator:

- **Mecanismul e restituire, nu scutire directă** — acciza se plătește integral la achiziția carburantului, iar diferența față de nivelul redus se recuperează ulterior, la cerere.
- **Condiția de vehicul pentru marfă**: autovehicule sau ansambluri articulate destinate exclusiv transportului rutier de mărfuri, cu masa brută maximă autorizată de **cel puțin 7,5 tone**.
- **Condiția pentru transportul de persoane**: vehicule din categoria M2 sau M3 (definite prin Directiva-cadru 2007/46/CE), cu excepția explicită a transportului public local de persoane, care nu se califică.
- **Nivelul redus concret și procedura de restituire** (cine solicită, cu ce document, în ce termen, la ce autoritate) se stabilesc prin hotărâre separată a Guvernului — Codul fiscal fixează doar principiul și limita minimă impusă de dreptul european.

## Ce se greșește în practică

- Se presupune că orice firmă de transport are dreptul la restituire, fără să se verifice masa brută maximă autorizată de cel puțin 7,5 tone a vehiculului folosit efectiv.
- Se confundă restituirea de acciză cu o deducere fiscală obișnuită — suma nu se scade din impozit, ci se recuperează separat, prin cererea și procedura stabilite prin hotărâre de Guvern.
- Se include în calculul restituibil transportul public local de persoane, exclus explicit de lege chiar și atunci când se face cu vehicule din categoriile M2/M3.
- Se aplică regimul redus pentru motorina folosită în agricultură confundând-o cu motorina pentru transport rutier — legea le tratează separat, cu regimuri și temeiuri distincte (art. 342 alin. (8), respectiv alin. (9)).

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu calculează și nu automatizează restituirea de accize** pentru transportatori. Modulele `core/d301.py`, `core/d301_operatiuni_api.py` și `core/d390.py` tratează produsele accizabile doar din perspectiva raportării TVA (achiziții intracomunitare de produse accizabile, coduri de operațiune pentru D301/D390) — nu există nicio funcție care să calculeze diferența dintre nivelul standard și cel redus al accizei sau să pregătească o cerere de restituire. Firma de transport trebuie să urmărească separat eligibilitatea vehiculelor și procedura de restituire stabilită prin hotărâre de Guvern.

[iConta.eu](/)
