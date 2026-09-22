# Elektroniczna Szachownica

Szachownica z automatycznym wykrywaniem pozycji figur, oparta o Arduino i matrycę czujników magnetycznych. System wykrywa obecność figury na każdym z 64 pól w czasie rzeczywistym i śledzi ruchy w partii bez ingerencji gracza.

<p align="center">
  <img src="docs/images/board-overview.jpg" width="45%" />
  <img src="docs/images/board-underside.jpg" width="45%" />
</p>

## Jak to działa

Każda figura ma w podstawce osadzony mały magnes neodymowy. Pod planszą, pod każdym z 64 pól, znajduje się kontaktron (reed switch) — czujnik reagujący na pole magnetyczne. Gdy figura stoi na polu, magnes zamyka obwód kontaktronu; Arduino odczytuje ten stan i na tej podstawie śledzi, które pola są zajęte.

Typ figury (pionek, wieża, itd.) nie jest odczytywany bezpośrednio z czujnika — system śledzi go programowo na podstawie znanej pozycji startowej i zasad ruchu figur w szachach, aktualizując wewnętrzny model gry na podstawie tego, które pola się zwolniły, a które zajęły.

## Przegląd sprzętowy

**Logika (5V):**
- Arduino Uno/Nano — odczytuje 64 czujniki przez kaskadę multiplekserów i wypisuje stan planszy
- 4× CD74HC4067 (16-kanałowy multiplekser analogowy) — każdy obsługuje 16 pól, przełączane wspólnymi liniami adresowymi S0-S3 i osobną linią EN dla każdego modułu
- 64× kontaktron magnetyczny (reed switch, typ NO, 2×14mm) — po jednym pod każdym polem, podłączone przez wewnętrzny pull-up Arduino

**Czujniki w figurach:**
- Magnesy neodymowe osadzone w podstawkach figur

Konstrukcja podzielona jest na dwie fizycznie osobne płytki (odpowiadające dwóm połówkom składanej szachownicy), połączone elastycznym kablem wielożyłowym w miejscu zawiasu.

## Schemat

Pełny schemat, narysowany w KiCad:

![Schemat elektroniczny szachownicy](docs/images/chessboard_schematic.png)

Mapowanie pinów:

| Sygnał | Pin Arduino |
|---|---|
| S0 | D7 |
| S1 | D8 |
| S2 | D9 |
| S3 | D10 |
| EN1 / EN2 / EN3 / EN4 | D2 / D3 / D4 / D5 |
| SIG1 / SIG2 / SIG3 / SIG4 | A0 / A1 / A2 / A3 |

## Struktura projektu
firmware/
board_scan.ino - skanuje wszystkie 64 pola, wypisuje stan planszy na Serial
src/
(planowane) chess_logic - śledzenie typu figur i historii ruchów na podstawie occupancy
docs/
images/ - zdjęcia i schemat


## Wyzwania i wnioski

- **Dobór czujnika:** pierwsze podejście wykorzystywało analogowe czujniki Halla (SS49E), które ostatecznie okazały się niedopasowane do skali odległości figura–czujnik w tym zastosowaniu — czujniki tego typu sprawdzają się przy bardzo małych, kontrolowanych dystansach (np. w padach do gier), nie przy kilkumilimetrowej odległości przez grubość planszy. Przejście na kontaktrony magnetyczne (reed switch) rozwiązało problem czułości, kosztem rezygnacji z pomiaru siły pola — co i tak nie było potrzebne, skoro typ figury można śledzić programowo na podstawie logiki gry.
- **Diagnostyka multipleksera:** odróżnienie usterki konkretnego kanału od usterki całego układu wymagało systematycznego podejścia — test ze znanym, kontrolowanym sygnałem (zamiast samego czujnika) na pojedynczym wejściu szybko rozstrzygał, czy problem leży w komponencie, czy w reszcie ścieżki sygnałowej.
- **Lutowanie cyną bezołowiową:** wyższa temperatura topnienia i szybsze utlenianie grota (Sn99,3Cu0,7) wymagały innej techniki niż przy klasycznej cynie ołowiowej — dłuższe podgrzewanie, częstsze czyszczenie i cynowanie grota.
- **Ostrożność przy pomiarach pod napięciem:** pomiar multimetrem na gęsto upakowanych nóżkach układu scalonego pod napięciem niesie realne ryzyko przypadkowego zwarcia sąsiednich pinów — bezpieczniejsze okazało się diagnozowanie przez sam mikrokontroler (odczyt przez Serial) zamiast sondowania na żywo.
- **Ekranowanie pola magnetycznego:** silne magnesy w sąsiadujących figurach wzajemnie się przyciągały; testowane ferromagnetyczne taśmy ekranujące nie dały wystarczającej redukcji — docelowe rozwiązanie to dobór słabszych magnesów dopasowanych do czułości kontaktronu.

## Lista komponentów

- Arduino Uno/Nano
- 4× CD74HC4067
- 64× kontaktron magnetyczny NO 2×14mm
- Magnesy neodymowe
- Płytki uniwersalne (prototypowe)
- Elastyczny kabel wielożyłowy (połączenie między połówkami planszy)
- Drut kynar, cyna bezołowiowa Sn99,3Cu0,7

## Zdjęcia

**Test pojedynczego modułu multipleksera**
![Test multipleksera](docs/images/mux-test.jpg)

**Lutowanie matrycy czujników**
![Lutowanie](docs/images/soldering-progress.jpg)

**Widok od spodu z okablowaniem**
![Spód planszy](docs/images/board-underside.jpg)

## Status

W budowie. Pierwsza połówka planszy (32 pola) zlutowana i przetestowana kanał po kanale — multiplekser i odczyt kontaktronów działają poprawnie. Druga połówka oraz warstwa logiki gry (śledzenie ruchów, rozpoznawanie typu figury na podstawie zasad szachowych) w toku.

## Licencja

MIT
