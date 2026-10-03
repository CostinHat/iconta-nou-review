---
title: "Administratorul care este și acționar poate vota descărcarea propriei gestiuni?"
description: "Nu. La SA, administratorul acționar nu poate vota, nici personal, nici prin mandatar, descărcarea propriei gestiuni. Poate vota situațiile financiare doar dacă altfel nu se formează majoritatea."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# Administratorul care este și acționar poate vota descărcarea propriei gestiuni?

Nu. La o societate pe acțiuni, acționarul care este membru al consiliului de administrație, al directoratului sau al consiliului de supraveghere nu poate vota, cu acțiunile pe care le deține, descărcarea propriei gestiuni. Nu poate vota nici personal, nici printr-un mandatar. Aceeași interdicție se aplică oricărei probleme în care persoana sau administrația lui ar fi în discuție.

Legea face o singură excepție. Situațiile financiare anuale pot fi votate și de administratorii acționari, dar numai dacă fără votul lor nu se poate forma majoritatea cerută. Distincția contează la adunarea anuală, unde aprobarea situațiilor financiare și descărcarea de gestiune sunt de obicei pe aceeași ordine de zi.

## Temeiul legal

::: ghid-temei
„Acționarii care au calitatea de membri ai consiliului de administrație, directoratului sau consiliului de supraveghere nu pot vota, în baza acțiunilor pe care le posedă, nici personal, nici prin mandatar, descărcarea gestiunii lor sau o problemă în care persoana sau administrația lor ar fi în discuție."
— Legea societăților nr. 31/1990, art. 126 alin. (1) (sursă: anaf_surse/legea_31_1990_societatile.txt)
„Persoanele respective pot vota însă situația financiară anuală, dacă nu se poate forma majoritatea prevăzută de lege sau de actul constitutiv."
— Legea societăților nr. 31/1990, art. 126 alin. (2) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

Ce înseamnă concret:

- **Descărcarea de gestiune: interdicție absolută.** Textul nu are excepții pentru descărcare. Administratorul acționar nu o votează, oricât de mare ar fi pachetul lui de acțiuni.
- **Nici prin mandatar.** Interdicția nu poate fi ocolită printr-o procură dată altei persoane pentru acțiunile administratorului.
- **Orice problemă care îl privește.** Dincolo de descărcare, administratorul nu votează „o problemă în care persoana sau administrația lor ar fi în discuție". Exemple tipice sunt o acțiune în răspundere împotriva lui sau verificarea unei operațiuni pe care a făcut-o.
- **Situațiile financiare: vot permis doar subsidiar.** Administratorul acționar poate vota situațiile financiare anuale numai când, fără votul lui, nu se poate forma majoritatea prevăzută de lege sau de actul constitutiv (art. 126 alin. (2)).
- **Adunarea se pronunță asupra gestiunii.** Adunarea generală ordinară este obligată să se pronunțe asupra gestiunii consiliului de administrație, respectiv a directoratului (art. 111 alin. (2) lit. d)). Descărcarea e un punct distinct de aprobarea situațiilor financiare. Pentru că art. 126 le supune unor reguli de vot diferite, cele două puncte se votează, în practică, separat.

**Ce se întâmplă la SRL.** Art. 126 e scris pentru societatea pe acțiuni. La SRL, adunarea asociaților dă descărcare de activitate administratorilor (art. 194 alin. (1) lit. b)). Pentru SRL nu există un text identic cu art. 126. Se aplică însă art. 79, prin art. 197 alin. (3): asociatul care are într-o operațiune interese contrare societății nu ia parte la deliberare sau la decizie. Dacă descărcarea propriei gestiuni intră sub această regulă e o chestiune de interpretare. Prudent este ca asociatul administrator să nu-și voteze propria descărcare și ca hotărârea să consemneze asta.

::: ghid-exemplu
SC Exemplu SA are trei acționari: Ion Popescu, administrator unic, cu 55% din acțiuni, Maria Ionescu cu 30% și Andrei Vasile cu 15%. Adunarea ordinară din aprilie 2026 are pe ordinea de zi: (1) aprobarea situațiilor financiare pe 2025; (2) descărcarea de gestiune a administratorului pentru 2025.

Punctul 2: Ion Popescu nu votează. Votează doar Maria Ionescu (30%) și Andrei Vasile (15%). Dacă Maria Ionescu votează pentru și Andrei Vasile contra, descărcarea se aprobă cu 30 din cele 45 de procente care au votat.

Punctul 1: dacă Maria Ionescu și Andrei Vasile, singuri, formează majoritatea cerută, Ion Popescu nu votează. Dacă nu se poate forma majoritatea fără el (de exemplu, unul dintre ei votează contra și celălalt se abține), Ion Popescu poate vota situațiile financiare, conform art. 126 alin. (2). Nu poate vota însă descărcarea.
:::

## Ce se greșește în practică

- Aprobarea situațiilor financiare și descărcarea de gestiune se votează împreună, într-un singur punct, cu voturile administratorului inclusiv.
- Administratorul acționar dă procură unui terț să voteze descărcarea cu acțiunile lui. Legea interzice expres votul „prin mandatar".
- Se consideră că descărcarea se aprobă automat odată cu situațiile financiare.
- Administratorul votează situațiile financiare deși ceilalți acționari formau singuri majoritatea, deci fără să fie îndeplinită condiția de la art. 126 alin. (2).
- La SRL, asociatul administrator își votează propria descărcare fără să se analizeze art. 79.

## Ce face iConta.eu

iConta.eu nu ține evidența voturilor din adunarea generală și nu redactează hotărârea de descărcare de gestiune. Acestea rămân în sarcina societății. Aplicația acoperă partea contabilă a închiderii anuale: generează situațiile financiare anuale (S1005 pentru microentități, S1003 pentru entități mici) din balanța firmei, ca XML validat. Numele administratorului trecut în bilanț se preia din profilul firmei. La generarea S1005, dacă numele lipsește, aplicația avertizează că bilanțul ar ieși cu mențiunea generică „ADMINISTRATOR" și cere completarea lui în datele firmei.

[iConta.eu](/)
