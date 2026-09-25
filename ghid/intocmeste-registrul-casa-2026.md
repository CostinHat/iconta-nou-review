---
title: "Cum se întocmește registrul de casă în 2026?"
description: "Regulile de completare zilnică a registrului de casă și plafoanele de încasări/plăți în numerar aplicabile în 2026."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se întocmește registrul de casă în 2026?

Registrul de casă rămâne, și în 2026, documentul obligatoriu prin care o firmă înregistrează zilnic toate încasările și plățile în numerar. Regulile de completare nu s-au schimbat esențial, dar plafoanele legale de operare cu numerar — care influențează direct ce poate intra sau ieși din casierie — rămân un punct sensibil de verificare.

## Temeiul legal

::: ghid-temei
„REGISTRUL DE CASĂ [...] servește ca: - document de înregistrare operativă a încasărilor și plăților în numerar (lei sau valută), efectuate prin casieria entității; - document de stabilire, la sfârșitul fiecărei zile, a soldului de casă; - document de înregistrare în contabilitate a operațiunilor de casă. Registrul de casă se întocmește zilnic, pe baza documentelor justificative de încasări și plăți."
— OMFP nr. 2.634/2015 privind documentele financiar-contabile, Anexa 2, Norme specifice de întocmire și utilizare a formularelor (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

- Registrul de casă se completează **zilnic**, nu periodic sau la sfârșit de lună — fiecare încasare și plată în numerar trebuie înregistrată pe baza documentului justificativ corespunzător (chitanță, dispoziție de plată/încasare către casierie, bon fiscal etc.).
- La finalul fiecărei zile, registrul trebuie să stabilească **soldul de casă** — diferența dintre report/sold ziua precedentă, încasările și plățile zilei.
- Documentul justificativ de bază pentru înregistrarea sumelor în registru este, de regulă, **chitanța**; pentru cazul unităților cu aparate de marcat electronice fiscale, veniturile din încasările zilnice se înregistrează pe baza **Raportului fiscal de închidere zilnică**, nu a chitanțelor individuale.
- Pentru operațiuni în valută, se ține un registru de casă separat, cu o structură care include și cursul valutar aplicat.
- Plafoanele de operare cu numerar rămân cele stabilite de Legea nr. 70/2015, art. 4 alin. (1): încasările în numerar de la persoane fizice, reprezentând contravaloarea unor livrări de bunuri sau prestări de servicii, se efectuează „în limita unui plafon zilnic de 10.000 lei de la o persoană", cu interdicția expresă a fragmentării încasărilor pentru a evita acest plafon, potrivit alin. (2) (sursă: anaf_surse/legea_70_2015_consolidat.txt).

## Ce se greșește în practică

- Se completează registrul de casă retroactiv, la sfârșit de lună, deși legea cere înregistrare zilnică pe baza documentelor justificative.
- Se omite calculul și menționarea soldului de casă la finalul fiecărei zile, ceea ce face imposibilă o verificare rapidă a numerarului efectiv existent.
- Se acceptă încasări în numerar peste plafonul zilnic legal, sau se fragmentează artificial o încasare mai mare într-o zi în mai multe tranșe, exact interdicția pe care legea o vizează explicit.
- Se confundă documentul justificativ corect: pentru firmele cu casă de marcat, veniturile zilnice se preiau din raportul fiscal de închidere, nu din chitanțe individuale emise în paralel.

## Ce face iConta.eu

iConta.eu are o funcție dedicată registrului de casă (`registru_casa` în `core/casa.py`), care generează automat registrul pe baza operațiunilor de încasare/plată introduse în aplicație, calculează soldul final zilnic (`sold_final`) și verifică depășirea plafoanelor legale de numerar, inclusiv regimul special pentru comerțul cash and carry (`verifica_plafon`). Contabilul nu mai trebuie să calculeze manual soldul de casă sau să verifice singur plafoanele — aplicația semnalează automat orice operațiune care ar depăși limita zilnică legală.

[iConta.eu](/)
