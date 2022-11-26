# http://localhost:5000/
from flask import Flask, render_template, session, redirect, url_for, flash
from sqlalchemy import desc
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, TextAreaField, SelectField, DateTimeField
from wtforms.validators import InputRequired, NumberRange, Length, Optional
# https://wtforms.readthedocs.io/en/2.3.x/validators/ InputRequired zamiast Required
from flask_sqlalchemy import SQLAlchemy
from flask_script import Shell, Manager  # flask-script==2.0.5
import json
from datetime import date
from sqlalchemy.exc import IntegrityError
import datetime
# Do generowania tokenu potrzebujemy:
import random
import string


class LoginForm(FlaskForm):
    login = StringField('Podaj login', validators=[InputRequired(), Length(min=6, max=20)])
    password = PasswordField('Podaj hasło', validators=[InputRequired(), Length(min=6, max=20)])
    submit = SubmitField('Zaloguj')


class ReservationForm(FlaskForm):
    seats = IntegerField('Jeśli chcesz zarezerwować miejsca na ten seans, podaj liczbę miejsc',
                         validators=[InputRequired(), NumberRange(min=1)])
    submit = SubmitField('Zarezerwuj')


class CancelReservationForm(FlaskForm):
    token = StringField('Podaj token rezygancji z rezerwacji', validators=[InputRequired(), Length(min=22, max=22)])
    submit = SubmitField('Odwołaj rezerwację')


class AddEmployee(FlaskForm):
    name = StringField('Podaj imię', validators=[InputRequired(), Length(max=20)])
    surname = StringField('Podaj nazwisko', validators=[InputRequired(), Length(max=30)])
    login = StringField('Podaj login', validators=[Optional(), Length(min=6, max=20)], default=None)
    password = StringField('Podaj hasło', validators=[Optional(), Length(min=6, max=20)], default=None)
    role = StringField('Podaj rolę', validators=[InputRequired(), Length(max=30)])
    submit = SubmitField('Dodaj pracownika')


class AddFilm(FlaskForm):
    title = StringField('Podaj tytuł', validators=[InputRequired(), Length(max=80)])
    year = IntegerField('Podaj rok produkcji', validators=[Optional(), NumberRange(min=1895, max=date.today().year)])
    director = StringField('Podaj reżysera', validators=[InputRequired(), Length(max=50)])
    type = StringField('Podaj typ', validators=[InputRequired(), Length(max=40)])
    time = IntegerField('Podaj czas wyswietlania', validators=[InputRequired(), NumberRange(min=1, max=1440)])
    description = TextAreaField('Podaj opis', validators=[InputRequired()])
    submit = SubmitField('Dodaj film')


class ReservationStatus(FlaskForm):
    id = IntegerField('Podaj id rezerwacji', validators=[InputRequired(), NumberRange(min=1)])
    status = SelectField('Wybierz status', choices=[('zatwierdzono', 'zatwierdzono'), ('odrzucono', 'odrzucono')],
                         validators=[InputRequired()])
    submit = SubmitField('Zmień')


class AddHall(FlaskForm):
    seats = IntegerField('Podaj liczbę miejsc', validators=[InputRequired(), NumberRange(min=1)])
    submit = SubmitField('Dodaj salę')


def make_shell_context():
    return dict(app=app, db=db, Filmy=Filmy)

app = Flask(__name__)  # initialization, application instance
app.config['SECRET_KEY'] = 'CJISDKW@#@$3FF5$35346FSAST43G#$G'  # flask-WTF configuration

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://xstixgkxgcrlfs:73cdf1b132b1eab4ab4b0bef611be8d045a4886c761308d4aa7cfdf5820d7ecd@ec2-44-199-22-207.compute-1.amazonaws.com:5432/d43fcsknmf3330'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)


class Filmy(db.Model):
    __tablename__ = 'filmy'
    id = db.Column(db.Integer, primary_key=True)
    tytul = db.Column(db.String(80), nullable=False)
    rok_produkcji = db.Column(db.SmallInteger,  db.CheckConstraint('rok_produkcji >= 1895 and \
                                                                    rok_produkcji <= EXTRACT(YEAR FROM CURRENT_DATE)'))
    rezyser = db.Column(db.String(50), nullable=False)
    typ = db.Column(db.String(40), nullable=False)
    czas_wyswietlania = db.Column(db.SmallInteger,
                                  db.CheckConstraint('czas_wyswietlania > 0 and czas_wyswietlania < 1440'),
                                  nullable=False)
    opis = db.Column(db.Text, nullable=False, unique=True)
    seans = db.relationship('Seanse', backref='film')

    def __repr__(self):
        return '<film %r>' % self.id

    def to_dict(self):
        return {
            'id_film': self.id,
            'tytul': self.tytul,
            'rok_produkcji': self.rok_produkcji,
            'rezyser': self.rezyser,
            'typ': self.typ,
            'czas_wyswietlania': self.czas_wyswietlania,
            'opis': self.opis,
        }


class Sale(db.Model):
    __tablename__ = 'sale'
    numer = db.Column(db.Integer, primary_key=True)
    liczba_miejsc = db.Column(db.Integer, db.CheckConstraint('liczba_miejsc>0'), nullable=False)
    seans = db.relationship('Seanse', backref='sala_numer')

    def __repr__(self):
        return '<sala %r>' % self.numer

    def to_dict(self):
        return {
            'numer_sali': self.numer,
            'liczba_miejsc': self.liczba_miejsc
        }


class Seanse(db.Model):
    __tablename__ = 'seanse'
    __table_args__ = (db.UniqueConstraint('sala', 'dzien', 'godzina'),)
    # https://stackoverflow.com/questions/10059345/sqlalchemy-unique-across-multiple-columns
    id = db.Column(db.Integer, primary_key=True)
    dzien = db.Column(db.String(12), db.CheckConstraint("dzien in ('poniedzialek','wtorek','sroda', \
                                                        'czwartek','piatek','sobota','niedziela')"), nullable=False)
    godzina = db.Column(db.Time, nullable=False)
    sala = db.Column(db.Integer, db.ForeignKey('sale.numer'))
    id_film = db.Column(db.Integer, db.ForeignKey('filmy.id'))
    wolne_miejsca = db.Column(db.Integer, db.CheckConstraint('wolne_miejsca >= 0'), nullable=False)
    rezerwacje = db.relationship('Rezerwacje', backref='seans')

    def __repr__(self):
        return '<seans %r>' % self.id

    def to_dict(self):
        return {
            'id_seans': self.id,
            'dzien': self.dzien,
            'godzina': self.godzina,
            'sala': self.sala,
            'wolne_miejsca': self.wolne_miejsca,
        }


class Rezerwacje(db.Model):
    __tablename__ = 'rezerwacje'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(22))
    id_seans = db.Column(db.Integer, db.ForeignKey('seanse.id', ondelete='CASCADE'))
    ile_biletow = db.Column(db.Integer, db.CheckConstraint('ile_biletow > 0'), nullable=False)
    data = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(12), db.CheckConstraint("status in ('odrzucono','zatwierdzono','oczekuje')"),
                       default='oczekuje')

    def __repr__(self):
        return '<rezerwacja o tokenie %r>' % self.token

    def to_dict(self):
        return {
            'id_rezerwacji': self.id,
            'token': self.token,
            'id_seans': self.id_seans,
            'ile_biletow': self.ile_biletow,
            'data': self.data,
            'status': self.status,
        }


class Pracownicy(db.Model):
    __tablename__ = 'pracownicy'
    id = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String(20), nullable=False)
    nazwisko = db.Column(db.String(30), nullable=False)
    login = db.Column(db.String(20), nullable=True, unique=True, default=None)
    haslo = db.Column(db.String(20), nullable=True, unique=True, default=None)
    rola = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return '<pracownik %r>' % self.id

    def to_dict(self):
        return {
            'id_pracownik': self.id,
            'imie': self.imie,
            'nazwisko': self.nazwisko,
            'login': self.login,
            'haslo': self.haslo,
            'rola': self.rola,
        }


def merge(dict1, dict2):
    # merging two disctionaries
    res = {**dict1, **dict2}
    return res


def inner_join(datatable1, datatable2):
    # inner_join for two datatables, output as list of rows of key dictionary
    results = db.session.query(datatable1, datatable2).join(datatable2).all()
    data_elements = []
    for el1, el2 in results:
        first = el1.to_dict()  # get information of row of first table
        second = el2.to_dict()  # get information of row of second table
        data_elements.append(merge(first, second))
    return {'data': data_elements}


def get_halls():
    halls = []
    query = Sale.query.all()
    for i in range(len(query)):
        halls.append(query[i].numer)
    return halls


def get_films():
    films = []
    query = Filmy.query.all()
    for i in range(len(query)):
        films.append(query[i].id)
    return films


class AddScreening(FlaskForm):
    day = SelectField('Wybierz dzień',
                      choices=[('poniedzialek', 'poniedziałek'), ('wtorek', 'wtorek'), ('sroda', 'środa'),
                               ('czwartek', 'czwartek'), ('piatek', 'piątek'), ('sobota', 'sobota'),
                               ('niedziela', 'niedziela')], validators=[InputRequired()])
    time = DateTimeField('Podaj czas rozpoczęcia', format='%H:%M', validators=[InputRequired()])
    hall = SelectField('Wybierz salę', choices=get_halls(), validators=[InputRequired()])
    id_film = SelectField('Wybierz id filmu', choices=get_films(), validators=[InputRequired()])
    submit = SubmitField('Dodaj seans')


class DeleteScreening(FlaskForm):
    id = IntegerField('Podaj indeks seansu, który chcesz usunąć', validators=[InputRequired(), NumberRange(min=1)])
    submit = SubmitField('Usuń seans')


def check_screening_time(seans):
    # funkcja sprawdza, czy przypadkiem wprowadzany seans nie nachodziłby na inne seanse
    # Zgarniamy czasy rozpoczecia i zakonczenia wprowadzanego seansu, data jest tu przypadkowa, chodzi o godzinę.
    godzina_rozpoczecia = datetime.datetime(2000, 10, 10, seans.godzina.hour, seans.godzina.minute, 0)
    # godzina rozpoczecia w formacie daty, przyda sie przy dodawaniu timedelta
    godz_rozp = seans.godzina.time().strftime('%H:%M:%S')  # godzina rozpoczecia w formacie czasu
    film = Filmy.query.filter_by(id=seans.id_film).first()  # zgarniamy film naszego seansu
    godzina_zakonczenia = godzina_rozpoczecia + datetime.timedelta(seconds=(60*film.czas_wyswietlania))
    # godzina zakonczenia w formacie daty
    poprzedni_seans = Seanse.query.filter_by(dzien=seans.dzien, sala=seans.sala).filter(
        Seanse.godzina <= godz_rozp).order_by(desc(Seanse.godzina)).first()  # zgarniamy poprzedni seans
    if poprzedni_seans is not None:  # jesli istnieje poprzedni seans tego dnia w tej sali
        poprzedni_film = Filmy.query.filter_by(id=poprzedni_seans.id_film).first()  # zgarniamy film poprzedniego seansu
        poprz_godz_rozp = datetime.datetime(2000, 10, 10, poprzedni_seans.godzina.hour, poprzedni_seans.godzina.minute,
                                            0)  # godzina rozpoczecia poprzedniego seansu w formacie daty
        poprz_godzina_zakonczenia = poprz_godz_rozp + datetime.timedelta(
            seconds=(60 * poprzedni_film.czas_wyswietlania))  # godzina zakonczenia poprzedniego seansu w formacie daty
        if poprz_godzina_zakonczenia >= godzina_rozpoczecia:
            # sprawdzamy czy poprzedni i biezacy seans na siebie nachodza
            flash('Godziny nachodza na siebie (poprzedni seans)!')
            return False
    nastepny_seans = Seanse.query.filter_by(dzien=seans.dzien, sala=seans.sala).filter(
        Seanse.godzina > godz_rozp).order_by(Seanse.godzina).first()  # zgarniamy nastepny seans tego dnia w tej sali

    if nastepny_seans is not None:  # jesli istnieje taki seans
        nast_godz_rozp = datetime.datetime(2000, 10, 10, nastepny_seans.godzina.hour, nastepny_seans.godzina.minute,
                                           0)  # zgarniamy jego godzine rozpoczecia w formacie daty
        if nast_godz_rozp < godzina_zakonczenia:  # sprawdzamy czy nastepny i biezacy seans na siebie nachodza
            flash('Godziny nachodza na siebie (następny seans)!')
            return False
    return True


manager = Manager(app)
manager.add_command("shell", Shell(make_context=make_shell_context))


bootstrap = Bootstrap(app)


@manager.command
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/logowanie_kasjer', methods=['GET', 'POST'])
def logowanie_kasjer():
    login_form = LoginForm()
    if session.get('logged_in') is None:
        if login_form.validate_on_submit():
            try_login = Pracownicy.query.filter_by(login=login_form.login.data,
                                                   haslo=login_form.password.data).first()
            # https://stackoverflow.com/questions/48819480/programming-error-with-wtforms-stringfield-writing-to-postgres

            if try_login is None:
                flash('Błędny login lub hasło')
            else:
                session['logged_in'] = True
                session['imie'] = try_login.imie
                session['nazwisko'] = try_login.nazwisko
                return render_template('kasjer.html', imie=session.get('imie'), nazwisko=session.get('nazwisko'),
                                       logged_in=session.get('logged_in'))

    else:
        return render_template('kasjer.html', imie=session.get('imie'), nazwisko=session.get('nazwisko'),
                               logged_in=session.get('logged_in'))
    return render_template('logowanie_kasjer.html', form=login_form)


@app.route('/kasjer')
def kasjer():
    if session.get('logged_in') is None:  # jeśli nie zalogowano to nie wpuszcza do panelu
        return redirect(url_for('logowanie_kasjer'))

    return render_template('kasjer.html', imie=session.get('imie'), nazwisko=session.get('nazwisko'),
                           logged_in=session.get('logged_in'))


@app.route('/pracownicy', methods=['GET', 'POST'])
def pracownicy():
    if session.get('logged_in') is None:  # jeśli nie zalogowano to nie wpuszcza do panelu
        flash('Brak uprawnień. Proszę się zalogować.')
        return redirect(url_for('logowanie_kasjer'))
    else:
        addemployee_form = AddEmployee()
        if addemployee_form.validate_on_submit():
            try:
                if addemployee_form.login.data == "":
                    addemployee_form.login.data = None
                if addemployee_form.password.data == "":
                    addemployee_form.password.data = None
                pracownik = Pracownicy(imie=addemployee_form.name.data, nazwisko=addemployee_form.surname.data,
                                       login=addemployee_form.login.data, haslo=addemployee_form.password.data,
                                       rola=addemployee_form.role.data)
                db.session.add(pracownik)
                db.session.commit()
                flash('Dodano pracownika '+pracownik.imie+' '+pracownik.nazwisko)
                redirect(url_for('pracownicy'))
            except IntegrityError:
                db.session.rollback()
                flash('Login lub hasło zajęte! Pracownik nie został dodany. Podaj inne dane logowania pracownika.')

    return render_template('pracownicy.html', logged_in=session.get('logged_in'), addemployee_form=addemployee_form)


@app.route('/filmy', methods=['GET', 'POST'])
def filmy():
    if session.get('logged_in') is None:  # jeśli nie zalogowano to nie wpuszcza do panelu
        flash('Brak uprawnień. Proszę się zalogować.')
        return redirect(url_for('logowanie_kasjer'))
    else:
        addfilm_form = AddFilm()
        if addfilm_form.validate_on_submit():
            try:
                film = Filmy(tytul=addfilm_form.title.data, rezyser=addfilm_form.director.data,
                             typ=addfilm_form.type.data, czas_wyswietlania=addfilm_form.time.data,
                             rok_produkcji=addfilm_form.year.data, opis=addfilm_form.description.data)
                db.session.add(film)
                db.session.commit()
                flash('Dodano film '+film.tytul)
                redirect(url_for('filmy'))
            except IntegrityError:
                db.session.rollback()
                flash('Istnieje już film o takim opisie')
    return render_template('filmy.html', logged_in=session.get('logged_in'), form=addfilm_form)


@app.route('/sale', methods=['GET', 'POST'])
def sale():
    if session.get('logged_in') is None:  # jeśli nie zalogowano to nie wpuszcza do panelu
        flash('Brak uprawnień. Proszę się zalogować.')
        return redirect(url_for('logowanie_kasjer'))
    else:
        addhall_form = AddHall()
        if addhall_form.validate_on_submit():
            sala = Sale(liczba_miejsc=addhall_form.seats.data)
            db.session.add(sala)
            db.session.commit()
            flash('Dodano salę ' + str(sala.numer))
            redirect(url_for('sale'))
            return redirect(url_for('sale'))
    return render_template('sale.html', logged_in=session.get('logged_in'), form=addhall_form)


@app.route('/seanse', methods=['GET', 'POST'])
def seanse():
    if session.get('logged_in') is None:  # jeśli nie zalogowano to nie wpuszcza do panelu
        flash('Brak uprawnień. Proszę się zalogować.')
        return redirect(url_for('logowanie_kasjer'))
    else:
        addscreening_form = AddScreening()
        if addscreening_form.validate_on_submit():
            try:
                sala = Sale.query.filter_by(numer=addscreening_form.hall.data).first()
                wolne_miejsca = sala.liczba_miejsc
                seans = Seanse(dzien=addscreening_form.day.data, godzina=addscreening_form.time.data,
                               sala=addscreening_form.hall.data, id_film=addscreening_form.id_film.data,
                               wolne_miejsca=wolne_miejsca)
                if check_screening_time(seans):  # sprawdzamy czy wprowadzony seans nie nachodzi na inne
                    db.session.add(seans)
                    db.session.commit()
                    flash('Dodano seans '+str(seans.id))
                    redirect(url_for('seanse'))
                else:
                    flash('Seans nie został dodany, bo jego czas trwania nachodzi na czas trwania innego seansu')
            except IntegrityError:
                db.session.rollback()
                flash('Seans nie został dodany')

    return render_template('seanse.html', logged_in=session.get('logged_in'), addscreening_form=addscreening_form)


@app.route('/seanse_usun', methods=['GET', 'POST'])
def seanse_usun():
    if session.get('logged_in') is None:  # jeśli nie zalogowano to nie wpuszcza do panelu
        flash('Brak uprawnień. Proszę się zalogować.')
        return redirect(url_for('logowanie_kasjer'))
    else:
        deletescreening_form = DeleteScreening()
        if deletescreening_form.validate_on_submit():
            try:
                query = Seanse.query.filter_by(id=deletescreening_form.id.data)
                if query.first() is None:
                    flash('Nie ma w bazie seansu o takim id')
                else:
                    query.delete()
                    db.session.commit()
                    flash('Seans został usunięty')
                    redirect(url_for('seanse_usun'))
            except IntegrityError:
                db.session.rollback()
                flash('Seans nie został usunięty')
                redirect(url_for('seanse_usun'))
        return render_template('seanse_usun.html', logged_in=session.get('logged_in'),
                               deletescreening_form=deletescreening_form)


@app.route('/rezerwacje', methods=['GET', 'POST'])
def rezerwacje():
    if session.get('logged_in') is None:  # jeśli nie zalogowano to nie wpuszcza do panelu
        flash('Brak uprawnień. Proszę się zalogować.')
        return redirect(url_for('logowanie_kasjer'))
    else:
        reservationstatus_form = ReservationStatus()
        if reservationstatus_form.validate_on_submit():
            try:
                rezerwacja = Rezerwacje.query.filter_by(id=reservationstatus_form.id.data).first()
                if rezerwacja is None:
                    flash('Błędne id')
                else:
                    if rezerwacja.status != 'zatwierdzono' and reservationstatus_form.status.data == 'zatwierdzono':
                        seans = Seanse.query.filter_by(id=rezerwacja.id_seans).first()
                        try:
                            seans.wolne_miejsca -= rezerwacja.ile_biletow
                        except IntegrityError:
                            db.session.rollback()
                            flash('Status rezerwacji nie został zmieniony, z powodu braku miejsc')
                    elif rezerwacja.status == 'zatwierdzono' and reservationstatus_form.status.data != 'zatwierdzono':
                        seans = Seanse.query.filter_by(id=rezerwacja.id_seans).first()
                        try:
                            seans.wolne_miejsca += rezerwacja.ile_biletow
                        except IntegrityError:
                            db.session.rollback()
                            flash('Status rezerwacji nie został zmieniony')
                    rezerwacja.status = reservationstatus_form.status.data
                    db.session.commit()
                    flash('Zmieniono status rezerwacji o id '+str(rezerwacja.id)+' na '+rezerwacja.status)
            except IntegrityError:
                db.session.rollback()
                flash('Status rezerwacji nie został zmieniony (brak miejsc)')
    return render_template('rezerwacje.html', logged_in=session.get('logged_in'), form=reservationstatus_form)


@app.route('/klient')
def klient():
    return render_template('klient.html')


@app.route('/przegladaj_filmy')
def przegladaj_filmy():
    return render_template('przegladaj_filmy.html')


@app.route('/przegladaj_seanse')
def przegladaj_seanse():
    # Wyświetla listę seansów, znajduje się tu też przycisk z przejściem do rezerwacji seansu
    # (wg polecenia), klient ma mozliwosc zawezenia wynikow do konkretnego filmu
    return render_template('przegladaj_seanse.html')


@app.route('/zarezerwuj/<string:row>', methods=['GET', 'POST'])
def zarezerwuj(row):
    row = json.loads(row)  # odbieramy dane o klikniętym wierszu tabeli na stronie przegladaj_seanse
    reservation_form = ReservationForm()  # tworzymy formularz rezerwacji
    if reservation_form.validate_on_submit():
        query = Seanse.query.filter_by(id=row['id_seans']).first()
        if query.wolne_miejsca < reservation_form.seats.data:
            # Sprawdzamy czy jest dostatecznie duża ilość miejsc dla tej rezerwacji
            flash('Niestety ale nie ma wystarczająco dużej liczby miejsc dla tej rezerwacji.'
                  'Rezerwacja nie powiodła się.')
        else:
            token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=22))  # Tworzymy token
            while Rezerwacje.query.filter_by(token=token).first() is not None:
                # w razie gdyby taki token juz byl w bazie
                token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=22))
            # Próbujemy dodać wiersz do tabeli rezerwacje
            try:
                rezerwacja = Rezerwacje(token=token, id_seans=row['id_seans'], ile_biletow=reservation_form.seats.data,
                                        data=datetime.datetime.now(), status='oczekuje')
                db.session.add(rezerwacja)
                db.session.commit()
                flash('Wysłano prosbę o rezerwację miejsc. Rezerwacja oczekuje na zatwierdzenie przez kasjera.'
                      'Twój token rezygnacji to: ' + token)
            except IntegrityError:
                db.session.rollback()
                flash('Nie można już zarezerwować miejsc na ten seans.')

    return render_template('zarezerwuj.html', form=reservation_form, duration=row['czas_wyswietlania'],
                           day=row['dzien'], start_time=row['godzina'], id_seans=row['id_seans'],
                           director=row['rezyser'], year=row['rok_produkcji'], hall=row['sala'],
                           type=row['typ'], title=row['tytul'], free_seats=row['wolne_miejsca'])


@app.route('/odwolaj_rezerwacje', methods=['GET', 'POST'])
def odwolaj_rezerwacje():
    cancelreservation_form = CancelReservationForm()
    if cancelreservation_form.validate_on_submit():
        query = Rezerwacje.query.filter_by(token=cancelreservation_form.token.data).first()
        if query is not None:
            if query.status != 'zatwierdzono':
                db.session.delete(query)
                db.session.commit()
                flash('Odwołano rezerwację')
            else:
                flash('Rezerwacja nie moze zostac odwolana, bo zostala juz zatwierdzona przez kasjera')
        else:
            flash('Błędny token')
    return render_template('odwolaj_rezerwacje.html', form=cancelreservation_form)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/logout')
def logout():
    session['imie'] = None
    session['nazwisko'] = None
    session['logged_in'] = None
    flash('Wylogowano.')
    return redirect(url_for('logowanie_kasjer'))


@app.route('/api/data_filmy')
def data_filmy():
    return {'data': [film.to_dict() for film in Filmy.query]}


@app.route('/api/data_seanse')
def data_seanse():
    mydict = inner_join(Seanse, Filmy)
    jeasonable_dict = json.dumps(mydict, indent=4, sort_keys=True, default=str)
    return jeasonable_dict


@app.route('/api/data_pracownicy')
def data_pracownicy():
    return {'data': [pracownik.to_dict() for pracownik in Pracownicy.query]}


@app.route('/api/data_rezerwacje')
def data_rezerwacje():
    return {'data': [rezerwacja.to_dict() for rezerwacja in Rezerwacje.query]}


@app.route('/api/data_sale')
def data_sale():
    return {'data': [sala.to_dict() for sala in Sale.query]}


@app.route('/film/<string:row>', methods=['GET', 'POST'])
def film(row):
    row = json.loads(row)
    return render_template('film.html', title=row['tytul'], director=row['rezyser'],
                           type=row['typ'], duration=row['czas_wyswietlania'],
                           year=row['rok_produkcji'], description=row['opis'])


if __name__ == '__main__':
    manager.run()
