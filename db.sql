CREATE TABLE Filmy (
    id SERIAL,
    tytul varchar(80) NOT NULL,
    rok_produkcji smallint CHECK (rok_produkcji >= 1895 and rok_produkcji <= EXTRACT(YEAR FROM CURRENT_DATE)),
  rezyser varchar(50) NOT NULL,
  typ varchar(40) NOT NULL,
  czas_wyswietlania smallint NOT NULL CHECK (czas_wyswietlania > 0 and czas_wyswietlania <= 1440),
  opis text UNIQUE NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE Sale(
numer SERIAL,
  liczba_miejsc int not NULL check ( liczba_miejsc > 0 ),
  PRIMARY KEY (numer)
);

CREATE TABLE Seanse (
id SERIAL,
  dzien varchar(12) NOT NULL CHECK (dzien in ('poniedzialek','wtorek','sroda','czwartek','piatek','sobota','niedziela')),
  godzina time NOT NULL,
  sala int NOT NULL,
  id_film INT NOT NULL,
  wolne_miejsca int NOT NULL CHECK ( wolne_miejsca >= 0 ),
  PRIMARY KEY (id),
  UNIQUE(sala, dzien, godzina),
  CONSTRAINT fk_film
    FOREIGN KEY(id_film)
    REFERENCES Filmy(id),
  CONSTRAINT fk_sala
    FOREIGN KEY(sala)
    REFERENCES Sale(numer)
);

CREATE TABLE Rezerwacje(
    id SERIAL,
token VARCHAR(22) UNIQUE NOT NULL,
  id_seans int NOT NULL,
  ile_biletow int check ( ile_biletow > 0 ) NOT NULL,
  data date NOT NULL,
  status varchar(15) check ( status in ('odrzucono','zatwierdzono','oczekuje') ) DEFAULT 'oczekuje',
  PRIMARY KEY (id),
  CONSTRAINT fk_seans
    FOREIGN KEY(id_seans)
    REFERENCES Seanse(id)
);

CREATE TABLE Pracownicy(
  id SERIAL,
  imie varchar(20) NOT NULL,
  nazwisko VARCHAR(30) NOT NULL,
  login varchar(20) UNIQUE NOT NULL check (length(login)>=6 and length(login) <=20),
  haslo varchar(20) UNIQUE NOT NULL check (length(haslo)>=6 and length(haslo) <=20),
  rola varchar(30) not NULL,
  PRIMARY KEY (id)
);
