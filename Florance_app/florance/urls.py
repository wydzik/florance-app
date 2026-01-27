from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register_florist/", views.register, name="register"),
    path("create_pracownia/", views.create_pracownia, name="create_pracownia"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("create_realizacja/", views.create_realizacja, name="create_realizacja"),
    path("dashboard/realizacje/", views.realizacje_dashboard, name="realizacje_dashboard"),
    path("realizacja/<int:pk>/edit/", views.edit_realizacja, name="edit_realizacja"),
    path("realizacja/<int:pk>/delete/", views.delete_realizacja, name="delete_realizacja"),
    path('pracownia/<int:pk>/edit/', views.edit_pracownia, name='edit_pracownia'),
    path('pracownia/create/', views.create_pracownia, name='create_pracownia'),
    path("realizacja/<int:pk>/", views.realizacja_detail, name="realizacja_detail"),
    path("realizacja/<int:realizacja_id>/stanowisko/dodaj/", views.create_pracownicy, name="create_pracownicy"),
    path("realizacja/<int:realizacja_id>/", views.realizacja_detail, name="realizacja_detail"),
    path("realizacja/<int:realizacja_id>/stanowisko/<int:pk>/edytuj/", views.edit_pracownicy, name="edit_pracownicy"),
    path("realizacja/<int:realizacja_id>/stanowisko/<int:pk>/usun/", views.delete_pracownicy, name="delete_pracownicy"),
    path("znajdz-zlecenie/", views.znajdz_zlecenie, name="znajdz_zlecenie"),
    path("stanowisko/<int:stanowisko_id>/apply/", views.apply_stanowisko, name="apply_stanowisko"),
    path("realizacja/<int:pk>/kandydaci/", views.lista_kandydatow, name="lista_kandydatow"),
    path("moje-aplikacje/", views.moje_aplikacje, name="moje_aplikacje"),
    path("realizacja/<int:realizacja_id>/stanowisko/<int:pk>/assign/", views.assign_pracownik, name="assign_pracownik"),
    path("florysta/<int:florysta_id>/", views.florysta_detail, name="florysta_detail"),
    path("zaproszenia/", views.twoje_zaproszenia, name="twoje_zaproszenia"),
    path("zaproszenia/<int:stanowisko_id>/odpowiedz/", views.odpowiedz_na_zaproszenie, name="odpowiedz_na_zaproszenie"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("aplikacja/<int:pk>/wycofaj/", views.withdraw_application, name="withdraw_application"),
    path("zaproszenie/<int:pk>/akceptuj/", views.accept_invite, name="accept_invite"),
    path("zaproszenie/<int:pk>/odrzuc/", views.reject_invite, name="reject_invite"),
    path("profil/edytuj/", views.edit_profile, name="edit_profile"),
    path("realizacja/<int:pk>/edit-opis/", views.edit_realizacja_opis, name="edit_realizacja_opis"),
    path("realizacja/<int:pk>/plik/add/", views.add_realizacja_plik, name="add_realizacja_plik"),
    path("realizacja/plik/<int:pk>/delete/", views.delete_realizacja_plik, name="delete_realizacja_plik"),
    path("realizacja/<int:pk>/edit/", views.edit_realizacja, name="edit_realizacja"),
    path("realizacja/plik/<int:pk>/delete/", views.delete_realizacja_plik, name="delete_realizacja_plik"),
    path("realizacja/<int:realizacja_id>/notatki/", views.edit_realizacja_notatki, name="edit_realizacja_notatki"),
    path("stanowisko/<int:stanowisko_id>/komentarz/add/", views.add_komentarz_stanowiska, name="add_komentarz_stanowiska"),
    path("powiadomienie/<int:pk>/read/", views.mark_notification_read, name="mark_notification_read"),
    path("password-reset/", auth_views.PasswordResetView.as_view(email_template_name="registration/password_reset_email.html", subject_template_name="registration/password_reset_subject.txt", success_url=reverse_lazy("password_reset_done")), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="auth/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="auth/password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="auth/password_reset_complete.html"), name="password_reset_complete"),

]


