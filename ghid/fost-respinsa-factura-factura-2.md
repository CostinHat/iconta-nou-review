---
title: De ce mi-a fost respinsă factura în e-Factura
description: RO e-Factura respinge orice fișier care nu respectă structura RO_CIUS — sistemul trimite emitentului mesajul cu erorile identificate, iar factura corectată se retransmite, fără să se poată returna cea deja comunicată.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# De ce mi-a fost respinsă factura în e-Factura

O factură „respinsă" în sistemul RO e-Factura nu e un refuz al conținutului economic al facturii, ci al structurii tehnice a fișierului transmis — sistemul verifică dacă respectă formatul standard, nu dacă suma sau partenerul sunt corecte.

### Ce verifică sistemul la transmitere

Art. 4 alin. (1) din OUG 120/2021 stabilește că structura facturii electronice trebuie să respecte trei niveluri: specificațiile tehnice ale standardului european SR EN 16931-1, specificațiile RO_CIUS (regulile operaționale specifice aplicabile la nivel național) și conținutul semantic descris în același standard. Elementele obligatorii de bază — identificatori de proces și factură, data facturii, identificarea emitentului și a destinatarului, defalcarea TVA, totalul facturii — sunt enumerate la art. 4 alin. (2).

### Ce se întâmplă la o factură care nu respectă structura

Art. 4 alin. (5) din OUG 120/2021 descrie exact mecanismul: în situația în care factura electronică transmisă nu respectă structura prevăzută la alin. (1), emitentul primește mesaj cu erorile identificate. După corectarea erorilor identificate, factura electronică se transmite în cadrul aceluiași sistem național. Practic, respingerea = un mesaj de validare eșuată, cu detalii despre ce anume nu corespunde (câmp lipsă, format greșit, cod CAEN neconcordant, cotă de TVA inconsistentă cu suma calculată etc.), nu o decizie discreționară a ANAF asupra conținutului comercial.

Când, dimpotrivă, factura respectă structura, art. 4 alin. (4) prevede că se aplică semnătura electronică a Ministerului Finanțelor și se comunică de îndată destinatarului — momentul acestei semnături atestă primirea efectivă în sistem.

### Factura odată comunicată nu se poate returna

Art. 4 alin. (8) din OUG 120/2021 e important pentru fluxul de corectare: factura electronică comunicată destinatarului nu se poate returna în sistemul național. Dacă emitentul descoperă o eroare de conținut după ce factura a fost deja comunicată destinatarului (nu respinsă de sistem, ci acceptată și livrată), soluția nu e „ștergerea" ei, ci emiterea unei facturi de corecție.

### Corecția se face conform art. 330 din Codul fiscal

Art. 4 alin. (10) din OUG 120/2021 trimite explicit la regulile de corecție a facturilor din Codul fiscal: corecția facturii electronice comunicate destinatarului în sistemul RO e-Factura se efectuează conform art. 330 din Legea nr. 227/2015 privind Codul fiscal, iar factura electronică corectată se transmite în cadrul aceluiași sistem național.

### Ce se greșește în practică

- Se interpretează mesajul de eroare ca respingere a conținutului comercial al facturii, deși e strict o eroare de validare a structurii XML/RO_CIUS — soluția e corectarea formatului, nu renegocierea cu partenerul.
- Se încearcă „ștergerea" sau anularea unei facturi deja comunicate destinatarului, deși sistemul nu permite returnarea — corect e emiterea unei facturi de corecție, conform art. 330 din Codul fiscal.
- Se retransmite factura corectată sub alt identificator, fără legătură cu cea inițială respinsă, ceea ce complică reconcilierea ulterioară a documentelor.
