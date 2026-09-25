---
title: "Când o cheltuială trebuie capitalizată în loc să fie dedusă imediat?"
description: "Criteriul contabil care decide dacă o cheltuială ulterioară legată de o imobilizare corporală majorează valoarea activului sau se înregistrează direct pe cheltuieli."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când o cheltuială trebuie capitalizată în loc să fie dedusă imediat?

O reparație, o îmbunătățire sau o piesă înlocuită la un mijloc fix pun mereu aceeași întrebare: se înregistrează direct pe cheltuieli ale perioadei sau majorează valoarea contabilă a activului, urmând să se amortizeze pe mai mulți ani? Reglementările contabile dau un criteriu clar, dar las decizia finală pe seama politicii contabile a fiecărei entități.

## Temeiul legal

```
::: ghid-temei
„Cheltuieli ulterioare 227. - (1) Cheltuielile ulterioare efectuate în legătură cu o imobilizare corporală sunt cheltuieli ale perioadei în care sunt efectuate sau majorează valoarea imobilizării respective, în funcție de beneficiile economice aferente acestor cheltuieli (de exemplu, influența asupra duratei de viață rămase a imobilizărilor), potrivit criteriilor generale de recunoaștere. (2) Entitatea stabilește prin politicile contabile criteriile în funcție de care cheltuielile ulterioare efectuate în legătură cu imobilizările corporale majorează valoarea acestora sau se evidențiază în contul de profit și pierdere."
— OMFP nr. 1.802/2014 pentru aprobarea reglementărilor contabile privind situațiile financiare anuale individuale și consolidate, pct. 227 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::
```

Ce rezultă din text, punct cu punct:

- **Criteriul central este beneficiul economic viitor:** dacă o cheltuială prelungește durata de viață rămasă a activului, îi crește capacitatea sau performanța, sau reduce costurile viitoare de exploatare, ea se capitalizează (majorează valoarea imobilizării). Dacă doar menține activul în starea inițială de funcționare, e cheltuială a perioadei.
- **Entitatea își stabilește propriile criterii**, prin politica contabilă aprobată de administratori — legea nu dă un prag valoric fix la nivel național pentru această distincție, spre deosebire de alte reguli fiscale.
- Pentru **componente care se înlocuiesc periodic** (de exemplu, un motor sau un acoperiș), costul componentei noi se recunoaște în valoarea contabilă a activului, dacă îndeplinește criteriile generale de recunoaștere — practic o „capitalizare parțială", pe componentă, nu pe tot activul.
- Pentru **inspecții și revizii generale regulate**, costul poate fi recunoscut fie ca o cheltuială, fie ca o componentă a activului (amortizată până la următoarea revizie), tot pe baza politicii contabile stabilite.

## Ce se greșește în practică

- Se capitalizează automat orice cheltuială peste un anumit prag valoric, confundând regula contabilă (bazată pe beneficiul economic viitor) cu pragul fiscal de recunoaștere a mijloacelor fixe (folosit pentru altă distincție: mijloc fix vs. obiect de inventar).
- Se trece direct pe cheltuieli o reparație care de fapt prelungește semnificativ durata de viață a activului, doar pentru că valoarea pare „mică" în raport cu valoarea activului — criteriul legal e beneficiul economic, nu proporția valorică.
- Se schimbă de la un exercițiu la altul criteriul de capitalizare fără să existe o politică contabilă scrisă și aprobată, ceea ce contravine principiului permanenței metodelor.

## Ce face iConta.eu

Modulele legate de mijloace fixe din `core/` (`repo_mijloace_fixe.py`, `mijloace_fixe_import_api.py`, `inventariere.py`) gestionează evidența și amortizarea activelor deja înregistrate ca imobilizări; decizia dacă o cheltuială ulterioară se capitalizează sau se înregistrează direct pe cheltuieli **rămâne o alegere a contabilului**, pe baza politicii contabile a firmei — nu a fost găsită în cod o regulă automată care să claseze cheltuielile ulterioare în funcție de beneficiul economic viitor, iar o astfel de regulă ar fi, de altfel, greu de automatizat complet, fiind prin natura ei o estimare profesională.

[iConta.eu](/)
