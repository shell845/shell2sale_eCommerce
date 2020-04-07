from django.conf import settings
from django.contrib.auth import authenticate, login, get_user_model
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.shortcuts import render, redirect

from .forms import ContactForm

# sendgrid library
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = getattr(settings, "SENDGRID_API_KEY", None)

DEFAULT_FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL", "shell2sale@shell2sale.com")
DEFAULT_TO_EMAIL = getattr(settings, "DEFAULT_TO_EMAIL", "shell2sale@shell2sale.com")


def home_page(request):
    context = {
        "title":"Hi There",
        "content":"Hey! Welcome to Shell2Sale",
    }
    if request.user.is_authenticated:
        context["premium_content"] = "Premium!!!"
    return render(request, "home_page.html", context)

def about_page(request):
    context = {
        "title":"About This Shop",
        "content":"This shop is for shell to sale her secondhands."
    }
    return render(request, "home_page.html", context)

def contact_page(request):
    contact_form = ContactForm(request.POST or None)
    context = {
        "title":"Contact Us",
        "content":"Feel free to talk...",
        "form": contact_form
    }

    if contact_form.is_valid():
        # print('*** contact form ', contact_form.cleaned_data)
        if request.is_ajax():
            # send email
            html_ = get_template("contact/contact-msg.html").render(context)
            subject = 'Shell2sale Contact Message'
            from_email = DEFAULT_FROM_EMAIL
            recipient = DEFAULT_TO_EMAIL
            # recipient_list = [self.email, from_email]

            # send email from sendgrid
            message = Mail(
                    from_email=from_email,
                    to_emails=recipient,
                    subject=subject,
                    html_content=html_)

            try:
                sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
                response = sg.send(message)
                # print(response.status_code)
                # print(response.body)
                # print(response.headers)
            except Exception as e:
                print(e) #.message)

            return JsonResponse({"message": "Thx"}) # json pass message in dict format

    if contact_form.errors:
        errors = contact_form.errors.as_json() # message in dict json format
        if request.is_ajax():
            return HttpResponse(errors, status=400, content_type='application/json') # msg already in json format

        # context['form'] = ContactForm()
    # view submit form content
    # if request.method == "POST":
    #   print(request.POST)
    #   #print(request.POST.get('fullname'))
    return render(request, "contact/view.html", context)
