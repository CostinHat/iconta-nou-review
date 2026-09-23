---
title: "Înființare firmă cu cenzor obligatoriu: când e necesar"
description: Pentru un SRL, cenzorul devine obligatoriu abia când numărul asociaților trece de 15 — sub acest prag, numirea rămâne opțională.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Înființare firmă cu cenzor obligatoriu: când e necesar

La înființarea unei societăți, numirea unui cenzor nu e, de regulă, obligatorie pentru un SRL — devine obligatorie doar peste un prag legal explicit de asociați. Pentru societățile pe acțiuni, regula e diferită: cenzorii sunt, ca principiu, obligatorii.

## Temeiul legal

::: ghid-temei
„Dacă numărul asociaților trece de 15, numirea cenzorilor este obligatorie."

*(Legea nr. 31/1990 privind societățile, art. 199 alin. (3))*
:::

## Ce spune legea, pentru fiecare formă

- **SRL cu 15 asociați sau mai puțin**: numirea cenzorilor e opțională — adunarea asociaților poate numi unul sau mai mulți cenzori ori un auditor financiar, dar nu e obligată (art. 199 alin. (2)).
- **SRL cu peste 15 asociați**: numirea cenzorilor devine obligatorie (art. 199 alin. (3), citat mai sus). Regulile prevăzute pentru cenzorii societăților pe acțiuni se aplică și cenzorilor din SRL (art. 199 alin. (4)).
- **Societate pe acțiuni (SA)**: va avea, în principiu, 3 cenzori și un supleant, dacă actul constitutiv nu prevede un număr mai mare — numărul cenzorilor trebuie să fie mereu impar (art. 159 alin. (1)).
- **Societăți supuse auditului financiar obligatoriu** (potrivit criteriilor de mărime din legislația contabilă): situațiile financiare sunt auditate de auditori financiari, ceea ce poate înlocui sau completa rolul cenzorilor, conform art. 160 alin. (1).

## Ce se greșește în practică

- **Se presupune că orice SRL trebuie să aibă cenzor** de la înființare — regula se activează doar peste pragul de 15 asociați; sub acest prag, controlul gestiunii revine, în lipsa cenzorilor, fiecărui asociat neadministrator (art. 199 alin. (5)).
- **Se confundă obligația de cenzor cu obligația de audit financiar** — sunt praguri și mecanisme diferite: cenzorul e legat de numărul de asociați (pentru SRL) sau de forma juridică (SA), auditul financiar e legat de criteriile de mărime ale societății.
- **Nu se verifică paritatea numărului de cenzori** la o SA — legea cere explicit un număr impar.

## Ce face iConta.eu

Tratamentul fiscal al remunerației cenzorului — odată numit, indiferent dacă numirea a fost obligatorie sau opțională — e acoperit de modulul F021 (`core/contracte_speciale.py`): CAS 25% + CASS 10% + impozit 10% pe rest, fără CAM (temei fiscal: Codul fiscal art. 76 alin. (2) lit. i)), cu nota contabilă prin contul 621. Verificarea obligativității numirii unui cenzor la înființare — numărul de asociați, forma juridică, eventuala încadrare în criteriile de audit obligatoriu — ține de Legea 31/1990 și de actul constitutiv, nu de un calcul pe care aplicația îl automatizează.

[iConta.eu](/)
