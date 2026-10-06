---
title: "Încasări cu cardul: mai trebuie tipărit și înmânat bonul fiscal clientului?"
description: "Nu. La încasările cu cardul de credit sau de debit, bonul fiscal nu mai trebuie tipărit și înmânat, cu excepția cazului în care clientul îl cere. Casa de marcat rămâne însă obligatorie."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# Încasări cu cardul: mai trebuie tipărit și înmânat bonul fiscal clientului?

Nu. De la 26 decembrie 2024, OUG 28/1999 prevede că, pentru încasările cu **cardul de credit sau de debit**, comerciantul nu mai are obligația să tipărească și să înmâneze bonul fiscal clientului. Dacă însă clientul cere bonul, comerciantul îl poate tipări și înmâna. Extrasul de cont al clientului ține loc de bon ca mijloc de probă a cumpărăturii.

Excepția privește doar tipărirea și înmânarea. **Obligația de a folosi casa de marcat rămâne**, iar vânzarea se înregistrează în aparat, inclusiv când plata se face cu cardul.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile alin. (2) , pentru încasările realizate prin utilizarea cardurilor de credit/debit, utilizatorii nu au obligația să imprime/să înmâneze bonuri fiscale cu aparate de marcat electronice fiscale clienților. La solicitarea clienților, utilizatorii pot imprima și înmâna acestora bonul fiscal. Lipsa bonului fiscal tipărit nu afectează drepturile consumatorilor prevăzute de [...] extrasul de cont bancar ținând locul bonului fiscal drept mijloc de probă al achiziției."
— OUG 28/1999, art. 1 alin. (2^1) (sursă: [OUG nr. 28/1999 privind obligația operatorilor economici de a utiliza aparate de marcat electronice fiscale](https://legislatie.just.ro/Public/DetaliiDocument/17431))
:::

::: ghid-temei
„Operatorii economici care încasează, integral sau parțial, cu numerar sau prin utilizarea cardurilor de credit/debit sau a substitutelor de numerar contravaloarea bunurilor livrate cu amănuntul, precum și a prestărilor de servicii efectuate direct către populație sunt obligați să utilizeze aparate de marcat electronice fiscale."
— OUG 28/1999, art. 1 alin. (1) (sursă: [OUG nr. 28/1999 privind obligația operatorilor economici de a utiliza aparate de marcat electronice fiscale](https://legislatie.just.ro/Public/DetaliiDocument/17431))
:::

Ce rezultă din text:

- **Excepția e strict pentru card de credit sau de debit.** Art. 1 alin. (1) numește separat cardurile și „substitutele de numerar". Excepția de la alin. (2^1) le menționează doar pe primele. Pentru plățile cu tichete, vouchere sau alte substitute de numerar, regula generală de tipărire și înmânare a bonului se aplică în continuare. Aceasta este lectura literală a textului.
- **Clientul nu mai e obligat să ceară bonul la plata cu cardul.** Art. 1 alin. (10) obligă clientul să solicite bonul când nu îl primește, dar exceptează expres situația de la alin. (2^1).
- **Dacă clientul cere bonul, comerciantul „poate” să-l tipărească.** Textul folosește un verb permisiv, nu o obligație. Raportul cu dreptul clientului de a lua bunul fără plată, de la alin. (10^1), e discutabil la plata cu cardul. Prudent, bonul cerut se tipărește.
- **Plata mixtă** (o parte cash, o parte card): excepția vizează „încasările realizate prin utilizarea cardurilor". Pentru partea în numerar, alin. (2^1) nu oferă acoperire. Textul nu tratează expres bonul cu plată combinată, așa că soluția sigură este tipărirea bonului.
- **Încasarea cu cardul trece în continuare prin aparat.** Raportul fiscal de închidere zilnică al aparatelor noi conține sumele rezultate pentru fiecare mijloc de plată utilizat (art. 4 alin. (7)).

Pentru încasările cu cardul prin automate comerciale care funcționează exclusiv cu plată cu cardul, legea merge mai departe: aparatul de marcat nu este obligatoriu (art. 3 alin. (2^3)).

::: ghid-exemplu
Un client al magazinului SC Exemplu SRL cumpără produse de 146 lei:

- **Plătește integral cu cardul:** vânzarea se înregistrează în casa de marcat, dar bonul nu trebuie tipărit. Dacă clientul îl cere, i se tipărește.
- **Plătește 100 lei cu cardul și 46 lei numerar:** textul nu tratează expres plata mixtă; prudent, bonul se tipărește și se înmânează, pentru că încasarea nu e realizată integral cu cardul.
- **Plătește cu tichete de masă:** bonul se tipărește și se înmânează, pentru că tichetele nu sunt card de credit sau de debit.

La sfârșitul zilei, raportul Z arată separat încasările cu cardul, cele în numerar și cele cu tichete. Pe această defalcare se face reconcilierea cu extrasul bancar și cu registrul de casă.
:::

## Ce se greșește în practică

- Se înțelege că la plata cu cardul nu mai trebuie înregistrată vânzarea în casa de marcat. Excepția privește doar tipărirea și înmânarea bonului.
- Excepția se aplică și la tichete sau vouchere, deși textul vorbește numai de carduri de credit sau de debit.
- Bonul nu se mai tipărește nici la plata mixtă, deși excepția nu acoperă expres partea în numerar.
- Clientului care cere bonul i se refuză tipărirea pe motiv că „nu mai e obligatoriu".

## Ce face iConta.eu

iConta.eu preia raportul Z din fișierul exportat de casa de marcat (XML sau .p7b) și citește încasările pe tipuri de plată, așa cum le înregistrează aparatul: card, numerar, tichete, vouchere și altele. Nota contabilă propusă, în stare de ciornă, duce numerarul în 5311, iar cardul și celelalte forme de plată în 5125, separat de TVA colectată. Aplicația nu decide dacă bonul trebuia tipărit sau nu. Asta ține de casier și de configurarea aparatului.

[iConta.eu](/)
