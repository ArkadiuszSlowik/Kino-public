<h1> W skrócie </h1>
Web app: **https://kino.herokuapp.com/** | flask + sqlalchemy + wtforms

<h2> Technologia </h2>
- aplikacja miała być prosta i szybka do napisania, dlatego powstała w oparciu o framework flask
- operowanie na bazie danych jest intuicyjne dzięki flask-sqlalchemy, biblioteka umożliwiła także połączenie z postgresem
- za wygląd aplikacji odpowiada biblioteka flask-bootstrap oraz datatables.js
- za formularze i bezpieczne wprowadzanie danych odpowiadają biblioteki flask-wtf, wtforms i wtforms-validators oraz sqlalchemy-exc

Użycie powyższych technologii argumentuję chęcią praktycznego użycia frameworka flask,
tym samym pozostałe komponenty w dużej mierze narzucały się same.

<h2> Logowanie - kasjer </h2>
Przykładowe dane logowania:
**login**: 123456
**haslo**: 123456

<h2> Opis zadania </h2>

Jest to aplikacja zaliczeniowa stworzona przeze mnie na przedmiot Bazy Danych prowadzony na wydziale MIMUW:
https://usosweb.mimuw.edu.pl/kontroler.php?_action=katalog2/przedmioty/pokazPrzedmiot&kod=1000-134BAD

W kinie jest kilka sal kinowych, w których wyświetla się filmy (tytuł, rok produkcji, reżyser, typ, czas wyświetlania, jakiś opis). Filmy wyświetla się podczas seansów.

Seans to dzień tygodnia, sala, godzina rozpoczęcia oraz wyświetlany film.

Każda sala ma numer oraz liczbę miejsc, nie uwzględniamy numeracji miejsc ani podziału na rzędy.

Patroni (czytaj ,,klienci'') mogą sprawdzać, jakie filmy są/będą wyświetlane w kinie przez najbliższy tydzień, obejrzeć jakie seanse odbywaja się danego dnia tygodnia, oraz o jakich porach można zobaczyć dany film w ciągu tygodnia/dnia.

Mogą też zamawiać bilety na wybrane seanse (o ile są wolne miejsca), podając liczbę miejsc. Takie zamówienia są dalej obsługiwane przez kasjerów, którzy muszą je zaakceptować.

Wyróżnia się dwie kategorie użytkowników:
-obsługa (obejmuje kasjerów)
-klient.

Do obowiązków pracowników obsługi należy

-rejestrowanie nowych pracowników obsługi i sal (w praktyce raczej robi się to rzadko i off-line);
-rejestrowanie nowych filmów;
-dodawanie i usuwanie seansów;
-akceptacja zmówień klientów.





<h2> Opis zawartości </h2>
/ - strona główna, tutaj decydujemy się czy wcielamy się w rolę kasjera czy klienta

klient - panel klienta, tu decydujemy o kolejnych akcjach
    przegladaj_filmy - tutaj możemy zobaczyć informacje o filmach, w szczegolnosci przeniesc sie do panelu z opisem filmu
    przegladaj_seanse - tutaj mozemy przegladac seanse, w szczegolnosci przeniesc sie do panelu rezerwacji
    odwolaj_rezerwacje - tutaj mozemy odwolac rezerwację, o ile nie została już uprzednio zatwierdzona przez kasjera
    film/<dane_filmu> - tutaj możemy znaleźć opis filmu
    zarezerwuj/<dane_seansu> - tutaj możemy zarezerwować miejsca na wybrany seans

logowanie_kasjer - tutaj logujemy się do panelu kasjera, jeśli nie jesteśmy zalogowani to nie mamy dostępu do panelu kasjera
i dalszych akcji
kasjer - panel kasjera, tu decydujemy o kolejnych akcjach
    pracownicy - tutaj możemy podejrzeć listę pracowników oraz dodać nowego pracownika,
        sprawdzamy by nowy pracownik nie miał danych logowania lub żeby jego dane logowania były unikalne
    sale - tutaj możemy podejrzeć sale oraz dodawać nowe
    filmy - tutaj możemy podejrzeć filmy, a także dodać nowe filmy
    seanse - tutaj możemy dodać seanse, widząc informację o seansach, filmach i salach. Nie dopuszczamy,
    aby godziny saensów nachodziły na siebie
    seanse_usun - tutaj mamy mozliwosc usuniecia seansu, usuwając seans usuwamy wszystkie odpowiadające mu rezerwacje
    rezerwacje - tu mamy możliwość zmiany statusu rezerwacji i podanym id

Uwaga: Tabele możemy sortować naciskając na nazwy kolumn.
Uwaga: Naciskając na wiersz tabeli zostajemy przeniesieni do odpowiedniej sekcji (np. naciskając na film,
przenosimy się na stronę filmu, naciskając na seans, przenosimy się do panelu rezerwacji na ten seans),
wyjątkiem jest naciskanie na wiersze tabeli seanse ze strony kasjera,
bo zakładamy że jego celem obecnie nie jest chęć rezerwacji miejsc.

<h2> Bibliografia </h2>
-Flask:
    Flask Web Development: Developing Web Applications with Python
-Tabele:
    https://www.youtube.com/watch?v=wpfhcpWLT8A
    https://www.youtube.com/watch?v=IsuhCAptNbg
    https://www.codespeedy.com/how-to-pass-javascript-variables-to-python-in-flask/

