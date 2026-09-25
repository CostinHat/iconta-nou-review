---
title: Cum descarci facturile din RO e-Factura
description: Exemplarul original al unei facturi transmise prin RO e-Factura e fișierul XML semnat electronic de Ministerul Finanțelor, iar data comunicării către destinatar este chiar data la care factura devine disponibilă pentru descărcare din sistem.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum descarci facturile din RO e-Factura

Sistemul național RO e-Factura, reglementat prin OUG nr. 120/2021, nu e doar un canal de transmitere — e și locul unde factura "trăiește" oficial: fișierul XML semnat electronic de Ministerul Finanțelor este exemplarul original, nu PDF-ul generat ulterior pentru citire.

### Ce înseamnă tehnic "descărcarea"

Potrivit OUG nr. 120/2021, art. 4: sistemul RO e-Factura primește factura electronică de la emitent, îi aplică semnătura electronică a Ministerului Finanțelor (ceea ce atestă primirea în sistem) și o pune la dispoziția destinatarului. **Data comunicării facturii către destinatar se consideră chiar data la care factura devine disponibilă pentru descărcare din sistem** — nu data la care destinatarul chiar deschide/descarcă fișierul. Odată comunicată, factura electronică nu mai poate fi "returnată" în sistem — eventualele corecții se transmit ca factură nouă, corectată, conform Codul fiscal, art. 330.

### De unde se descarcă efectiv

- **Spațiul Privat Virtual (SPV)** — interfața ANAF prin care orice contribuabil înregistrat poate vedea și descărca facturile primite/emise prin sistem, autentificat cu certificat digital calificat sau alt mijloc de identificare acceptat.
- **Aplicațiile de conversie/prelucrare** puse la dispoziție de Ministerul Finanțelor prin Centrul Național pentru Informații Financiare, pentru cei care nu au propriul software de prelucrare a facturii XML.
- **API-ul pus la dispoziție de ANAF** — pentru descărcare automatizată, programatică, folosit de aplicațiile de contabilitate care se conectează direct la sistem.

### Exemplarul original vs. forma lizibilă

Fișierul XML semnat rămâne, legal, exemplarul original. Dacă destinatarul nu poate prelucra direct XML-ul, se poate folosi un document obținut prin conversie, care permite citirea și listarea — dar aplicația de conversie trebuie să asigure integritatea conținutului facturii electronice, adică forma "citibilă" (PDF, de regulă) trebuie să reflecte exact datele din XML, nu o reconstrucție aproximativă.

### Practic

- Nu vă bazați exclusiv pe PDF-ul primit prin e-mail de la furnizor — el poate diferi de forma oficială; forma legală e XML-ul din sistem, descărcat direct din SPV sau prin API.
- Dacă aveți obiecții la o factură primită (sumă greșită, date incorecte), înștiințați emitentul, inclusiv prin mesaj în sistemul RO e-Factura — factura comunicată nu poate fi retrasă, doar corectată printr-o factură nouă.
- Pentru contabilizare automată, integrarea prin API e mai fiabilă decât descărcarea manuală repetată din SPV — dar procedura tehnică de acces (autentificare, format) se aprobă prin ordin al ministrului finanțelor și poate fi actualizată.
