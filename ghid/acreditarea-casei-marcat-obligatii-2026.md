---
title: "Acreditarea casei de marcat: obligații 2026"
description: "Ce înseamnă, din punct de vedere legal, acreditarea unei unități de comercializare sau service pentru aparate de marcat electronice fiscale — și de ce nu este o obligație a operatorului economic utilizator."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Acreditarea casei de marcat: obligații 2026

„Acreditarea" din legislația privind aparatele de marcat electronice fiscale (AMEF) nu este o obligație a comerciantului care utilizează casa de marcat, ci o autorizare specială pe care o obțin distribuitorii și unitățile prin care aceștia comercializează sau asigură service pentru aparate. Operatorul economic utilizator cumpără aparatul de la o unitate acreditată — el nu „acreditează" propria casă de marcat.

## Temeiul legal

::: ghid-temei
„(3) Aparatele de marcat electronice fiscale sunt livrate prin distribuitori autorizați. În sensul prezentei ordonanțe de urgență, prin distribuitor autorizat se înțelege operatorul economic pe numele căruia a fost eliberată autorizația prevăzută la art. 5 alin. (2).
(4) În baza autorizației de distribuție, distribuitorul are dreptul de a comercializa, direct sau prin intermediul operatorilor economici prevăzuți în autorizație, denumiți în continuare unități acreditate pentru comercializare, aparatele de marcat electronice fiscale [...].
(5) Distribuitorul autorizat are obligația să asigure service-ul, direct sau prin intermediul operatorilor economici prevăzuți în autorizație, denumiți în continuare unități acreditate pentru service, atât pentru aparatele comercializate în mod direct, cât și pentru cele comercializate prin intermediul unităților acreditate pentru comercializare."
— OUG nr. 28/1999 (republicată), art. 1 alin. (3)-(5) (sursă: anaf_surse/oug_28_1999.html)
:::

Structura pieței AMEF, așa cum rezultă din lege:

- **Distribuitorul autorizat** este operatorul care obține direct autorizația de la autoritatea competentă (art. 5 alin. (2)) și este singurul îndreptățit să introducă pe piață aparatele de marcat electronice fiscale.
- **Unitățile acreditate pentru comercializare** sunt operatorii economici desemnați de distribuitor, prin care acesta vinde aparatele — comerciantul final cumpără, de regulă, de la o astfel de unitate, nu direct de la producător.
- **Unitățile acreditate pentru service** sunt operatorii autorizați să întrețină și să repare aparatele deja instalate la utilizatori.
- Operatorul economic utilizator (comerciantul, prestatorul de servicii) **nu are un act de „acreditare" propriu** — obligațiile sale sunt cele de la art. 1 (utilizarea aparatului, emiterea bonului fiscal) și de la art. 3^1 (conectarea la distanță și evidența în Registrul național ANAF), nu o procedură de acreditare a echipamentului.

## Ce se greșește în practică

- Se caută o procedură de „acreditare" a casei de marcat proprii la ANAF, deși acreditarea, în sensul legii, privește distribuitorii și unitățile de comercializare/service, nu utilizatorul final.
- Se confundă „acreditarea" cu „fiscalizarea" (procesul tehnic prin care aparatul este inițializat și înregistrat pentru un anumit operator economic) — sunt noțiuni diferite, prima ținând de rețeaua de distribuție, a doua de aparatul concret aflat la comerciant.
- Se alege un furnizor de service care nu figurează ca unitate acreditată pentru service a distribuitorului aparatului respectiv, ceea ce poate crea probleme de conformitate la intervenții tehnice.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu are legătură cu procesul de acreditare a distribuitorilor sau unităților de comercializare/service pentru AMEF — acesta este un raport contractual/administrativ între operatorul economic, distribuitor și ANAF, exterior aplicației. iConta.eu poate importa, pentru evidența contabilă, Raportul Z generat de un aparat deja instalat și fiscalizat (`core/amef_import.py`), indiferent de distribuitorul sau unitatea acreditată prin care a fost achiziționat.

[iConta.eu](/)
