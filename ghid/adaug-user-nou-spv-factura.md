---
title: "Cum adaug un user nou în SPV pentru e-Factura"
description: "Adăugarea unui împuternicit în relația cu organul fiscal este reglementată de Codul de procedură fiscală, dar procedura tehnică de administrare a utilizatorilor SPV se stabilește prin ordin ANAF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum adaug un user nou în SPV pentru e-Factura

Dacă vrei ca o altă persoană (contabil extern, angajat) să acceseze SPV-ul firmei, legea are un concept clar pentru asta: împuternicirea. Procedura tehnică exactă din portalul ANAF pentru adăugarea unui utilizator suplimentar este însă stabilită separat, prin ordin al președintelui ANAF, nu prin Codul de procedură fiscală propriu-zis.

## Temeiul legal

::: ghid-temei
„(1) În relaţiile cu organul fiscal contribuabilul/plătitorul poate fi reprezentat printr-un împuternicit. Conţinutul şi limitele reprezentării sunt cele cuprinse în împuternicire sau stabilite de lege, după caz. Desemnarea unui împuternicit nu îl împiedică pe contribuabil/plătitor să îşi îndeplinească personal obligaţiile prevăzute de legislaţia fiscală, chiar dacă nu a procedat la revocarea împuternicirii potrivit alin. (2).
(2) Împuternicitul este obligat să depună la organul fiscal actul de împuternicire, în original sau în copie legalizată. Revocarea împuternicirii operează faţă de organul fiscal de la data depunerii actului de revocare, în original sau în copie legalizată."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 18 alin. (1)-(2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă de aici pentru accesul suplimentar la SPV:

- Legea permite reprezentarea contribuabilului de către un împuternicit, cu limitele stabilite explicit în actul de împuternicire — nu este o simplă „partajare de parolă", ci o relație juridică formalizată.
- Împuternicitul trebuie să depună la organul fiscal actul de împuternicire (original sau copie legalizată) — un pas administrativ separat de simpla activare tehnică a unui cont în portal.
- Desemnarea unui împuternicit nu îl exonerează pe titular de obligațiile sale fiscale — titularul rămâne răspunzător chiar dacă a delegat accesul.
- Procedura tehnică exactă (cum se adaugă, în interfața SPV, un al doilea utilizator cu certificatul propriu, ce drepturi capătă) este stabilită prin proceduri ANAF specifice, care nu au fost identificate ca text verbatim în sursele verificate pentru acest ghid — pentru pașii de ecran, se urmează instrucțiunile oficiale ANAF.

## Ce se greșește în practică

- Se dă certificatul digital al titularului unei alte persoane, ca soluție rapidă, în loc să se facă o împuternicire corectă — riscant juridic, pentru că identitatea folosită la ANAF rămâne, aparent, cea a titularului.
- Se presupune că adăugarea unui utilizator în SPV scutește titularul de răspunderea pentru actele depuse prin acel cont — legea spune explicit contrariul, la art. 18 alin. (1).
- Se uită depunerea actului de împuternicire la organul fiscal — fără acest pas, reprezentarea nu este opozabilă ANAF.

## Ce face iConta.eu

iConta.eu nu gestionează utilizatorii contului SPV al ANAF — acest lucru se face direct în portalul ANAF, cu certificatele digitale ale persoanelor autorizate. Ce oferă aplicația este propriul sistem de conturi și drepturi de acces la datele firmei din iConta.eu, separat de contul SPV: mai mulți utilizatori pot avea acces la aplicație, dar autorizarea tehnică pentru trimiterea facturilor prin RO e-Factura (conectorul OAuth2 din `core/spv_conector.py`) se face o singură dată, pe baza certificatului calificat al reprezentantului sau împuternicitului firmei.

[iConta.eu](/)
