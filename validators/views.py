from django import forms
from django.http import HttpResponse
from django.views.generic.edit import FormView

from . import validators



clean_passport = validators.Cleaner(validators.PassportValidator(), validators.PassportNormaliser(), "Passport number invalid")

class ContactForm(forms.Form):
    name = forms.CharField()
    passport = forms.CharField(validators=[clean_passport])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'passport' in self.initial:
            self.initial['passport'] = clean_passport.ft(self.initial['passport'])
    
    def clean(self):
        self.cleaned_data = super().clean()
        form_data = {f:self.data[f] for f in self.data}
        if 'passport' in self.cleaned_data:
            self.cleaned_data['passport'] = clean_passport(self.cleaned_data['passport'])
            print (self.cleaned_data['passport']) # check stdout / log for result
            form_data['passport'] = clean_passport.ft(self.cleaned_data['passport'])
        self.data = form_data


class ContactView(FormView):
    form_class = ContactForm
    template_name = 'validators/form.html'
    success_url = '/thankyou'




def thankyou(request):
    return HttpResponse('Thank You!')

