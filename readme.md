# Rekeningnamen vergelijken

## Project

Doel van dit project is om te achterhalen of mensen geld overmaken naar hun externe rekeningen. Hiervoor moeten de namen van klantrekeningen vergeleken worden met met namen van externe rekeningen. Dit is lastig omdat de namen niet altijd hetzelfde worden genoteerd; "L.F. Koning", "Koning, L.F." en "Dhr LF Koning" kunnen allemaal naar dezelfde persoon wijzen ondands de verschillende schrijfwijze. Dit script probeert vergelijkt twee namen en geeft een waarschijnlijkheidsscore (0 - 100) of de namen overeenkomen


## Het proces

Het vergelijkingsproces in het script kent de volgende stappen:

### 1. Opschonen data:

De eerste stap is om de namen op de klantrekening en tegenrekening op te schonen. De namen worden geconverteerd naar kleine letters en trema's op letters worden verwijderd. Verder worden niet-informatieve woorden verwijderd (bijvoorbeeld "Dhr" of "Mevr"). Tot slot wordt gecontroleerd over de initialen qua schrijfwijze overeenkomen ("LF" versus "L.F."). 

### 2. Opknippen in 'termen'

Na de opschoning, wordt de overgebleven tekst opgeknipt in termen. Dit kan bijvoorbeeld een enkele letter zijn (initiaal "L") of een blok van letters (bijvoorbeeld "LF" of "Koning").

### 3. Termen matchen

Nadat de namen opgeknipt zijn in termen worden deze 1 voor 1 met elkaar vergeleken. Uit deze vergelijkingen komen zogenaamde 'Levenshtein afstanden'; dit is het aantal letters dat veranderd zou moeten worden om de termen gelijk te maken. Wat voorbeelden:

|*Term 1*|*Term 2*|*Afstand*|
|---|---|---|
|abc|abc|0|
|abc|ab|1|
|abc|abd|1|
|abc|cab|1|
|abc|ade|2|

De afstand voor iedere paarsgewijze vergelijking wordt opgeslagen in een matrix.

### 4. Best matchende paren selecteren

Op basis van de afstandenmatrix worden de beste matches (met de kleinste afstanden) geselecteerd. Neem de volgende afstandsmatrix:

||*L*|*Koning*|
|---|---|---|
|**LF**|1|6|
|**Koning**|6|0|

Het algoritme zoekt het minumum in de matrix (0 in het voorbeeld) en verwijderd deze rij en kolom uit de matrix. Deze matrix wordt dan gereduceerd tot:

||*L*|
|---|---|
|**LF**|1|

Vervolgens wordt weer de beste match geselecteerd ("L" met "LF") en de matrix verkleind. Dit gaat net zo lang door tot er geen paren meer over zijn.

### 5. Somscore berekenen

De somscore voor alle termen wordt berekend door de afstanden bij elkaar op te tellen. Uit bovenstaand voorbeeld:

|*Paar*|*Afstand*|
|---|---|
|"Koning" + "Koning"|0|
|"L" + "LF"|1|
|**Totaal**|**1**|

Als er termen overgebleven zijn die niet gematched konden worden, dan wordt het aantal karakters van deze overgebleven termen opgeteld bij de somscore.

Tot slot wordt de somscore genormaliseerd voor de lengte van de naam en uitgedrukt als percentage.


## Meer informatie:

Levenshtein afstand:
https://en.wikipedia.org/wiki/Levenshtein_distance