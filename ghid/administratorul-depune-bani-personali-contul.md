---
title: "Poate administratorul depune bani personali în contul firmei?"
description: "Cum se tratează legal și contabil depunerea de bani personali de către administrator sau asociat în contul firmei, și plafonul legal pentru încasările în numerar de acest fel."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Poate administratorul depune bani personali în contul firmei?

Da. Cea mai frecventă formă e împrumutul acordat de asociat/administrator societății („creditare de firmă"), care nu presupune modificarea actului constitutiv, spre deosebire de un aport la capitalul social. Suma intră ca datorie a firmei față de persoana care a depus-o și se poate restitui ulterior, fără dobândă sau cu dobândă, potrivit înțelegerii dintre părți. Dacă depunerea se face în numerar, se aplică însă un plafon legal.

## Temeiul legal

::: ghid-temei
„(1) Operațiunile de încasări în numerar efectuate de persoanele prevăzute la art. 1 alin. (1), de la persoane fizice, reprezentând cesiuni de creanțe, primiri de împrumuturi sau alte finanțări, precum și contravaloarea unor livrări de bunuri sau a unor prestări de servicii se efectuează în limita unui plafon zilnic de 10.000 lei de la o persoană.
(2) Sunt interzise încasările fragmentate de la o persoană, pentru operațiunile de încasări în numerar prevăzute la alin. (1), cu o valoare mai mare de 10.000 lei, precum și fragmentarea tranzacțiilor reprezentând cesiuni de creanțe, primiri de împrumuturi sau alte finanțări [...]."
— Legea 70/2015 privind limitarea operațiunilor cu numerar, art. 4 alin. (1) și (2) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

- Suma pe care administratorul/asociatul o „depune" în firmă e, contabil, o primire de împrumut — se poate face oricând, fără să modifice capitalul social sau actul constitutiv, spre deosebire de un aport în numerar (care presupune majorare de capital, potrivit Legii 31/1990).
- Dacă banii intră în numerar la casierie, se aplică plafonul de **10.000 lei/zi de la aceeași persoană** — inclusiv pentru operațiunile de primire de împrumut, nu doar pentru vânzări/cumpărări obișnuite.
- Fragmentarea intenționată a sumei în mai multe tranșe, ca să nu se depășească plafonul zilnic, e interzisă explicit de lege.
- Depunerea prin virament bancar (din contul personal al administratorului direct în contul firmei) nu e supusă acestui plafon de numerar, dar rămâne o operațiune care trebuie documentată (contract de împrumut sau decizie asociat unic, după caz), pentru a nu fi tratată ulterior ca venit nejustificat al firmei.
- Orice operațiune economico-financiară de acest fel trebuie consemnată printr-un document justificativ care stă la baza înregistrării în contabilitate.

## Ce se greșește în practică

- Se depun bani personali în numerar la casierie, fără să se verifice plafonul zilnic de 10.000 lei de la aceeași persoană, sau se „sparge" suma în mai multe zile ca să pară sub plafon — ambele practici sunt sancționate contravențional.
- Nu se întocmește niciun document (contract de împrumut, decizie a asociatului unic sau proces-verbal AGA) pentru suma depusă, iar contabilitatea rămâne fără document justificativ pentru operațiune.
- Se confundă „depunerea de bani" cu un aport la capitalul social, deși din punct de vedere juridic sunt operațiuni diferite — aportul presupune modificarea actului constitutiv și înregistrare la Registrul Comerțului, împrumutul nu.
- Se ignoră faptul că, dacă suma e acordată cu dobândă, dobânda plătită de firmă are un regim fiscal propriu (impozitare la sursă pentru persoana fizică), separat de tratamentul principalului împrumutat.

## Ce face iConta.eu

iConta.eu **are un motor contabil dedicat pentru decontările cu asociații**, inclusiv pentru împrumutul de la asociat: modulul `decontari_asociati.py` generează notele contabile pentru primirea sumei (cont 5121 = 4551), restituirea ei (4551 = 5121) și, dacă e cazul, dobânda aferentă (666 = 4551, cu impozitul de 10% pe venitul din dobândă reținut la sursă: 4551 = 446). Aplicația nu verifică însă automat plafonul de 10.000 lei/zi din Legea 70/2015 pentru încasările în numerar — respectarea acestui plafon rămâne responsabilitatea celui care depune efectiv banii.

[iConta.eu](/)
