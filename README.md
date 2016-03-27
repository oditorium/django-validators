# django-validators
_input validation, cleaning, and formatting for Django_

## Installation

### Example Installation

This repo contains an entire Django project that should run out of the box, and that
contains the validation library as part of the `validators` app. It should run on 
any server that has `Django 1.9+` and `Python 3.5+` installed. To install on an Ubuntu 
server (or most other Linux servers for that matter) use the following commands:

	git clone https://github.com/oditorium/django-validators.git
	cd django-validators
	python3 manage.py test
	python3 manage.py runserver

This launches a server on <http://localhost:8000>. An alternative is to install it on 
[Heroku][Heroku]. After installing the Heroku [Toolbelt][Toolbelt] run the following commands:
[Heroku]: https://www.heroku.com/
[Toolbelt]: https://toolbelt.heroku.com/

	git clone https://github.com/oditorium/django-validators.git
	cd django-validators
	heroku create
	heroku config:set HEROKU=1
	git push heroku +master

### Installing the Library

In your own project you almost certainly want to use the library files on their own. Those
files are:

- `validators/validators.py` (library)
- `validators/tests_validators.py` (library tests)

You can either just dump them into any of your own apps (or non-app submodules for that matter),
or you can place the whole `validators` app in your Django project--the extra files providing
examples etc won't matter unless you connect them to the URL routing of your project.


## Usage

There are three types of objects in this library

- **normalisers** normalise user input into a standard format for the database (eg, stripping 
	dots and dashes), and also reformat it into a standard format on the way back 

- **validators** take an already normalised user input and assess whether or not it is valid

- **cleaners** combine validators and normalisers, and can directly be used in Django forms

It should be noted that whilst _cleaners_ are Django specific, _normalisers_ and _validators_ 
are not.

There are a number of _validators_ and _normalisers_ implemented already, and the number 
is expected to grow. Please refer to the code or Python's help functionality--all items 
have doc strings, and any description here is bound to become stale.

There are no _cleaners_ implemented in the `validators.py` because different installations 
will differ on the cleaning to be performed (eg, whether alpha characters in a phone number 
should be stripped, or fail validation). There are however many example cleaners defined 
in `tests_validator.py` and creating others is straight forward.

### Normalisers
#### Signature

The ultimate base class for normalisers is `NullNormaliser` which simple passes arguments through 
both ways:

	class NullNormaliser():
	
	    def inp(s, data):
	        return data
        
	    def outp(s, data):
	        return data

	    def __call__(s, data):
	        return s.inp(data)

The signature of a normaliser is that it has 

- an input validation method `inp`
- an output validation method `outp`
- is callable, which is an alias for `inp`

However, usually normalisers would not inherit directly from `NullNormaliser` but from
`Normaliser` whose overall layout is as follows:

	class Normaliser():
	
	    def _inp(s, data):
	        return -normalised-(data)
    
		def inp(s, data)
			-perform common normalisations on data-
			return _inp(data)
		 
		....

meaning that both `inp` and `outp` first perform some common normalisations (eg, they
deal with None, which might be received instead of a blank string) and then call the
`_inp` or `_outp` functions respectively. **Important: generally those common normalisation 
should be preserved, so normaliser classes should derive from `Normaliser` and overwrite 
`_inp` and `_outp`!**

Currently the library is a bit sloppy with respect to types. The idea is that inputs and 
outputs should be strings both ways, but--as can be seen in `NullValidator`--if the input
is not a string, the output might not be a string either. Note that we might tighten this
in the future--using those functions with anything but string inputs is not recommended
(the exception to this is `None` which all validators but the `NullValidator` should 
recognise as a blank string).

#### Examples

By way of example, `NumericNormaliser` on the _input_ removes all non-digit character from a 
string, for example

	print( NumericNormaliser(" 11.22-3a4 ") ) # "112234"

On the output it is a noop, except that it deals with `None`

	print( NumericNormaliser.outp("112234") )	# "112234"
	print( NumericNormaliser.outp(None) ) 		# ""

An example for a normaliser with non-trivial output is the `PassportNormaliser` which
formats Brazilian passport numbers

	print( PassportNormaliser.outp("AA123456") )     # "AA 123 456"

**Important: the output formatter expect the data having been gone through input normalisation
and cleaning first; if this is not the case the behaviour is undefined.** For example, 
`PassportNormaliser.outp` might or might not complain if the string is not of the right lenght,
or it the first two characters are not uppercase alpha.

### Validators
#### Signature

The validator base class `Validator` is extremely simple: it is a callable object that 
always returns `True`, ie accepts everything as valid:

	class Validator():
	    def __call__(s, input_to_validate):
	        return True

So the validator signature is simply being a callable with return values

- `True` if the item validates, and
- `False` if the item does not validate


#### Examples

Most validators are subclasses of `RegexValidator` which considers strings to be valid 
if and only if they satisfy a certain regular expression. For example, the `PassportValidator` 
for Brazilian passport numbers is

	class PassportValidator(RegexValidator):
	    regex = r'[A-Z]{2}[0-9]{6}'

meaning that it expects exactly two uppercase letters, and exactly six digits.

Some validators also deal with checksums. For example, Brazilian CPF numbers' last two
digits are check digits, and `CpfValidator` checks that those are correct as well.
(hat tip to poliquin's `brazilnum` [library][brazilnum] for doing the heavy lifting here)
[brazilnum]: https://github.com/poliquin/brazilnum



### Cleaner
#### Signature

The `Cleaner` class instantiates into a callable object that contains a normaliser and a validator.


	class Cleaner(object):
	    def __init__(s, validator=None, normaliser=None, exception_msg=None, exception=None):
	    	...

	    def execute(s,text):
	        text = s.normaliser(text)
	        if s.validator(text): return text
	        raise s.exception(s.exception_msg)
    
	    def __call__(s, text):
	        return s.execute(text)
    
	    def ft(s, text):
	        return s.normaliser.outp(text)

Calling the object (or calling `execute`) first normalises the text and then validates it. If 
validation  fails, an exception is raised (by default, `ValidationError`). Calling the `ft` 
method is equivalent to calling the normaliser's `outp` method.

#### Examples

There are no cleaners predefined in the library module, but there are many examples given in the
test module. To remain with the passport example, a passport cleaning function would be

	clean_passport = Cleaner(PassportValidator(), PassportNormaliser(), "Passport number invalid")

This object can be directly used as a Django validator function, ie it can be passed as an argument
to the relevant form definition:

	class ContactForm(forms.Form):
		passport = forms.CharField(validators=[clean_passport])
		...

Note that this fragment only _validates_ the input, but does not actually normalise it, meaning that
whatever the user has put into the form would actually end up in the database. In order to clean the 
data we must add the following code to our form:

	class ContactForm(forms.Form):
	
		def clean(self):
			self.cleaned_data = super().clean()
			if 'passport' in self.cleaned_data:
				self.cleaned_data['passport'] = clean_passport(self.cleaned_data['passport'])
		...

This leaves the normalised value in `cleaned_data`, ready to be saved into the database. Note that
we do care about normalisation. For example, consider passport numbers: we probably want them to
be unique, but a database will not understand that 'AA 123 456' and 'aa123456' actually corresponds
to the same passport number.

A nice-to-have is that valid data is already formatted properly when it is presented back to the user,
eg because there is a form error in other parts of the form. This involves writing to `self.data`--except
that `self.data` is immutable! A hack addressing this is to replace `self.data` with an entirely new
dict as in the code below. It seems to work for us, but of course it does break some contracts, notably
that `self.data` is immutable. Use at your own risk!

	class ContactForm(forms.Form):
	
		def clean(self):
		    self.cleaned_data = super().clean()
		    form_data = {f:self.data[f] for f in self.data}
		    if 'passport' in self.cleaned_data:
		        self.cleaned_data['passport'] = clean_passport(self.cleaned_data['passport'])
		        form_data['passport'] = clean_passport.ft(self.cleaned_data['passport'])
		    self.data = form_data
		...

Finally we also want the initial value in the field to be properly formatted (of course that makes
more sense with model forms, as other forms usually have blank default values). The following code takes
care of this

	class ContactForm(forms.Form):
	
		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			if 'passport' in self.initial:
				self.initial['passport'] = clean_passport.ft(self.initial['passport'])
		...

Please do keep in mind that not all keys are present in `self.initial`, so the check above is crucial.


## Contributions

Contributions welcome. Send us a pull request!


## Change Log


The idea is to use [semantic versioning](http://semver.org/), even though initially we might make some minor
API changes without bumping the major version number. Be warned!

- **v1.0** initial release