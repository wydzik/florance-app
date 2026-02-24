import os
from django.db import models
from django.contrib.auth.models import User

WOJEWODZTWA = [
    ("dolnośląskie", "Dolnośląskie"),
    ("kujawsko-pomorskie", "Kujawsko-Pomorskie"),
    ("lubelskie", "Lubelskie"),
    ("lubuskie", "Lubuskie"),
    ("łódzkie", "Łódzkie"),
    ("małopolskie", "Małopolskie"),
    ("mazowieckie", "Mazowieckie"),
    ("opolskie", "Opolskie"),
    ("podkarpackie", "Podkarpackie"),
    ("podlaskie", "Podlaskie"),
    ("pomorskie", "Pomorskie"),
    ("śląskie", "Śląskie"),
    ("świętokrzyskie", "Świętokrzyskie"),
    ("warmińsko-mazurskie", "Warmińsko-Mazurskie"),
    ("wielkopolskie", "Wielkopolskie"),
    ("zachodniopomorskie", "Zachodniopomorskie"),
]

lokalizacja_wojewodztwo = models.CharField(
    max_length=50,
    choices=WOJEWODZTWA,
    default="mazowieckie"  # 👈 wartość domyślna
)


# Definicja enum dla rodzaju prawa jazdy i rodzaju stawki
class PrawoJazdy(models.TextChoices):
    B = 'B', 'Kategoria B'
    C = 'C', 'Kategoria C'


class RodzajStawki(models.TextChoices):
    DZIENNA = 'dzienna', 'Dzienna'
    GODZINOWA = 'godzinowa', 'Godzinowa'


class Florysta(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    imie = models.CharField(max_length=50)
    nazwisko = models.CharField(max_length=50)

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True
    )

    lokalizacja_miasto = models.CharField(max_length=50)
    lokalizacja_wojewodztwo = models.CharField(
        max_length=50,
        choices=WOJEWODZTWA,
        null=True,
        blank=True
    )
    lokalizacja_kraj = models.CharField(max_length=50, default="Polska")

    czy_pracownia = models.BooleanField(default=False)
    czy_freelancuje = models.BooleanField(default=False)
    czy_prawo_jazdy_b = models.BooleanField(default=False)
    czy_prawo_jazdy_c = models.BooleanField(default=False)
    czy_uklada_kwiaty = models.BooleanField(default=True)
    czy_moze_dzwigac = models.BooleanField(default=False)
    czy_pracuje_na_wysokosci = models.BooleanField(default=False)
    czy_ma_auto = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.imie} {self.nazwisko} ({self.lokalizacja_miasto})"


# Definicja modelu Pracownia
class Pracownia(models.Model):
    owner = models.ForeignKey(Florysta, on_delete=models.CASCADE, related_name="pracownie")
    nazwa = models.CharField(max_length=100)
    lokalizacja_miasto = models.CharField(max_length=50)
    lokalizacja_wojewodztwo = models.CharField(max_length=50)
    lokalizacja_kraj = models.CharField(max_length=50, default="Polska")

    def __str__(self):
        return f"{self.nazwa} (właściciel: {self.owner.imie} {self.owner.nazwisko})"


# Definicja modelu Umiejętności
class Umiejetnosci(models.Model):
    florysta = models.ForeignKey(Florysta, on_delete=models.CASCADE)
    umiejetnosc = models.CharField(max_length=50)
    wartosc = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.umiejetnosc} - {self.wartosc}'


# Definicja modelu Realizacja
class Realizacja(models.Model):
    pracownia = models.ForeignKey(Pracownia, on_delete=models.CASCADE)
    nazwa_eventu = models.CharField(max_length=100)
    miejsce = models.CharField(max_length=255)
    data_rozpoczecia = models.DateTimeField()
    data_zakonczenia = models.DateTimeField()
    opis = models.TextField()

    # 🔒 PRYWATNE NOTATKI OWNERA
    notatki_prywatne = models.TextField(blank=True)

    def __str__(self):
        return self.nazwa_eventu


class StatusPrzypisania(models.TextChoices):
    OCZEKUJE = "oczekuje", "Oczekuje na potwierdzenie"
    ZAAKCEPTOWANE = "zaakceptowane", "Zaakceptowane"
    ODRZUCONE = "odrzucone", "Odrzucone"


class Pracownicy(models.Model):
    realizacja = models.ForeignKey(Realizacja, on_delete=models.CASCADE)

    # wymagania
    czy_wlasny_transport = models.BooleanField(default=False)
    czy_wymagane_dzwiganie = models.BooleanField(default=False)
    czy_wymagane_ukladanie_kwiatow = models.BooleanField(default=False)
    czy_wymagane_prawo_jazdy = models.CharField(
        max_length=1,
        choices=PrawoJazdy.choices,
        blank=True,
        null=True
    )

    data_pracy = models.DateField()
    stawka = models.DecimalField(max_digits=10, decimal_places=2)
    stawka_dzienna_czy_godzinowa = models.CharField(
        max_length=10,
        choices=RodzajStawki.choices
    )
    minimalny_czas_pracy = models.PositiveIntegerField()
    szczegoly = models.TextField()

    status_przypisania = models.CharField(
            max_length=20,
            choices=StatusPrzypisania.choices,
            default=StatusPrzypisania.OCZEKUJE
    )

    # 🔹 przypisany użytkownik systemu
    przypisany_florysta = models.ForeignKey(
        Florysta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="przypisane_stanowiska"
    )

    # 🔹 osoba spoza systemu
    przypisane_imie = models.CharField(max_length=50, blank=True, null=True)
    przypisane_nazwisko = models.CharField(max_length=50, blank=True, null=True)
    przypisany_telefon = models.CharField(max_length=20, blank=True, null=True)

    assigned_name = models.CharField(
        max_length=100,
        blank=True
    )
    assigned_phone = models.CharField(
        max_length=20,
        blank=True
    )

    @property
    def is_filled(self):
        return (
                self.status_przypisania == StatusPrzypisania.ZAAKCEPTOWANE
        )

    def __str__(self):
        return f"Stanowisko – {self.realizacja.nazwa_eventu}"

    @property
    def assigned_person_name(self):
        if self.przypisany_florysta:
            return f"{self.przypisany_florysta.imie} {self.przypisany_florysta.nazwisko}"
        elif self.przypisane_imie and self.przypisane_nazwisko:
            return f"{self.przypisane_imie} {self.przypisane_nazwisko}"
        return None

    @property
    def is_external(self):
        return self.przypisany_florysta is None and self.przypisane_imie


class StatusKandydata(models.TextChoices):
    OCZEKUJE = "oczekuje", "Oczekuje"
    WYBRANY = "wybrany", "Wybrany"
    ODRZUCONY = "odrzucony", "Odrzucony"


class Kandydat(models.Model):
    stanowisko = models.ForeignKey(
        "Pracownicy",
        on_delete=models.CASCADE,
        related_name="kandydaci"
    )
    florysta = models.ForeignKey(
        Florysta,
        on_delete=models.CASCADE,
        related_name="kandydatury"
    )
    wiadomosc = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=StatusKandydata.choices,
        default=StatusKandydata.OCZEKUJE
    )

    def __str__(self):
        return f"{self.florysta} → {self.stanowisko}"


# models.py

class RealizacjaPlik(models.Model):

    WIDOCZNOSC_CHOICES = [
        ("owner", "Tylko owner"),
        ("workers", "Widoczny dla przypisanych pracowników"),
    ]

    realizacja = models.ForeignKey(
        Realizacja,
        related_name="pliki",
        on_delete=models.CASCADE
    )

    plik = models.FileField(upload_to="realizacje/")
    nazwa = models.CharField(max_length=255, blank=True)
    dodano = models.DateTimeField(auto_now_add=True)

    widocznosc = models.CharField(
        max_length=20,
        choices=WIDOCZNOSC_CHOICES,
        default="workers"
    )

    def extension(self):
        return os.path.splitext(self.plik.name)[1].lower()

    def is_image(self):
        return self.extension() in [".jpg", ".jpeg", ".png", ".gif", ".webp"]

    def is_pdf(self):
        return self.extension() == ".pdf"


class KomentarzStanowiska(models.Model):

    TYP_CHOICES = [
        ("owner", "Prywatny dla ownera"),
        ("worker", "Tylko dla konkretnego pracownika"),
        ("all", "Dla wszystkich pracowników realizacji"),
    ]

    stanowisko = models.ForeignKey(
        Pracownicy,
        on_delete=models.CASCADE,
        related_name="komentarze"
    )

    autor = models.ForeignKey(
        Florysta,
        on_delete=models.CASCADE
    )

    tresc = models.TextField()

    typ = models.CharField(
        max_length=10,
        choices=TYP_CHOICES,
        default="owner"
    )

    # używane tylko gdy typ="worker"
    widoczny_dla = models.ForeignKey(
        Florysta,
        null=True,
        blank=True,
        related_name="komentarze_prywatne",
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Komentarz ({self.created_at:%d.%m.%Y})"


class Powiadomienie(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="powiadomienia"
    )
    tresc = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.tresc
