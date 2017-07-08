from django.shortcuts import render
from .forms import SubscriberForm
from .mailer import Mailer


def landing(request):
    name = 'Artur'
    form = SubscriberForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data

        # сообщаем в консоль о новом юзере
        print("Новый пользователь: {}, почта: {}".format(data['name'], data['email']))

        # создаем объект для пересылки письма и высылаем письмо
        new_mail = Mailer(data['name'], data['email'])
        new_mail.run()

        #сохраняем форму
        new_form = form.save()

    return render(request, 'landing/landing.html', locals())
