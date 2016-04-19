"""
Validator and Normaliser Classes


VALIDATORS

Validors are objects that instantiate into callables, and those callables return
True is validation succeeds, and False if it does not

    NumericValidator()('123') # True

- Validator: validator base class (everything validates True)
- RegexValidator: base class for regular expression validator (everything validates True)
- NumericValidator: validator numeric expressions ([0-9]*)
- AlphaValidator: validator alphabetic expressions ([a-zA-Z]*)
- AlpnumValidator: validator alpha numeric expressions ([a-zA-Z]*)
- CpfValidator: validator for CPF numbers (Brazilian tax ID numbers)
- CnpjValidator: validator for CNPJ numbers (Brazilian corp tax ID numbers)


NORMALISERS

Normalisers are objects that 
- transform inputs into a database-ready format ( `inp()` and `__call__()` )
- database items into nicely formatted output ( `outp()` )

- Normaliser: normaliser base class; only strip; noop for output)
- NumericNormaliser: removes everything but digits, noop for output
- AlphaNormaliser: removes everything but alpha, noop for output
- AlnumNormaliser: removes everything but alnum, noop for output
- CpfNormaliser: for Brazilian CPF
- PhoneNormaliser, MobNormaliser: for Brazilian fixed line and mobile phones
- PassportNormaliser, IDCardNormaliser: for Brazilian identity documents
- PostCodeNormaliser: for Brazilian post codes
- DateNormaliser: for dates


CLEANING FUNCTION

Normalisers and validators can be combined into cleaning functions that can be used
in forms. They return the cleaned data or raise an exception

    clean_numeric = cleaning_func(NumericValidator(), NumericNormaliser(), "bang!")
    validate_numeric("100") # '100'
    validate_numeric(" 100 ") # '100'
    validate_numeric(" 100x ") # raises ValidationError("bang!")

ATTENTION: note the `()` when passing `NumericValidator` and `NumericNormaliser`-- in fact,
`cleaning_func` will accept any callable

REQUIREMENTS

Uses [brazilnum](https://github.com/poliquin/brazilnum)

    pip3 install brazilnum 


COPYRIGHT

Copyright (c) Stefan LOESCH, oditorium 2016. All rights reserved.
Licensed under the Mozilla Public License, v. 2.0 <https://mozilla.org/MPL/2.0/>
"""
import datetime

__version__ = "1.0"
__version_dt__ = "2015-03-15"


########################################################################################
## VALIDATOR

import re
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from brazilnum.cpf import validate_cpf
from brazilnum.cnpj import validate_cnpj


########################################
## VALIDATOR
class Validator():
    """
    base class for a generic input validator (here everything validates True)

    RETURNS
        True if valiation succeeds
        False if validation fails
        
    USAGE

        v = SomeClassDerivedFromValidator()
        if v(text_to_validate):
            print('validation OK')
        else
            print ('validation failed')


    CUSTOMISING VALIDATORS

        validators are customised by deriving classes from `Validator` that overwrite
        the __call__ function. See `RegexValidator` as an example for such a derived class

    UNIT TEST
    
    note that there are unit tests in the file `tests_validators.py`. It must be move into an app directory.
    """

    def __call__(s, input_to_validate):
        return True


########################################
## HELPERS
class _remove_other_chars():
    """class allowing to remove characters from a string
    
    USAGE
        remover = _remove_other_chars(str.isdigit)
        remover("AA-123-456") # "123456"
    
    """
    def __init__(s, is_valid_func=None):
        s.is_valid_func = is_valid_func
    
    def __call__(s, text):
        if text:
            text = str(text)
            text = ''.join([s for s in filter(s.is_valid_func, text)]) # remove all non-digit characters
        return text

_remove_non_digit_chars = _remove_other_chars(str.isdigit)
_remove_non_alnum_chars = _remove_other_chars(str.isalnum)
_remove_non_alpha_chars = _remove_other_chars(str.isalpha)


########################################
## CPF VALIDATOR
def _check_cpf(cpf):
    """
    verifies the checksum in a given CPF - DOES NOT WORK!

    RETURNS
        True if correct, False if not (None if other error, eg lenght)

    USAGE

        import cpfcsum
        cpfcsum.check('11144477735') # True
        cpfcsum.check('11144477736') # False
        cpfcsum.check('1114447773')  # None

    CREDIT 
        https://gist.github.com/henriquebastos/9040667

    """
    def dv(partial):
        s = sum(b * int(v) for b, v in zip(range(len(partial)+1, 1, -1), partial))
        return s % 11

    try:
        cpf = _remove_non_digit_chars(cpf)
        if len(cpf) != 11: return None
        dv1 = 11 - dv(cpf[:9])
        q2 = dv(cpf[:10])
        dv2 = 11 - q2 if q2 >= 2 else 0

        return dv1 == int(cpf[9]) and dv2 == int(cpf[10])

    except:
        return None


class CpfValidator(Validator):
    """
    validator for CPF numbers (Brazilian individual tax ID numbers)
    """


    def __call__(s, param):
        if not param: return False # validate_cpf falls over with ""
        #if s._check_cpf(param): return True
        if validate_cpf(param): return True
        else: return False


########################################
## CNPJ VALIDATOR
class CnpjValidator(Validator):
    """
    validator for CNPJ numbers (Brazilian company tax ID numbers)
    """

    def __call__(s, param):
        if not param: return False # validate_cnpj falls over with ""
        if validate_cnpj(param): return True
        else: return False

########################################
## REGEX VALIDATOR
class RegexValidator(Validator):
    """
    base class for regular expression validator (everything validates True)

    USAGE

        v = SomeClassDerivedFromRegexValidator()
        if v(text_to_validate): print('validation OK')
        else: print ('validation failed')


    CUSTOMISING VALIDATORS

        regex validators can be customised at the instance and at the class level
        instance level validation is as follows

            v = RegexValidator(r'[0-9]*')
            if v(text_to_validate): print('validation OK')
            else: print ('validation failed')

        or as follows

            v = RegexValidator()
            v.regex = r'[0-9]*'
            if v(text_to_validate): print('validation OK')
            else: print ('validation failed')

        class level validation goes as follows

            class NumericValidator(RegexValidator):
                regex = r'[0-9]*'

            v = NumericValidator()
            if v(text_to_validate): print('validation OK')
            else: print ('validation failed')
    """

    regex = r'.*'

    def __init__(s, regex=None):
        if regex: s.regex = regex

    def __call__(s, input_to_validate):
        match = re.fullmatch(s.regex, input_to_validate)
        return True if match else False

class NumericValidator(RegexValidator):
    """validates a text only consisting of digits ('[0-9]*')"""
    regex = r'[0-9]*'

class AlphaValidator(RegexValidator):
    """validates a text only consisting of letters ('[a-zA-Z]*')"""
    regex = r'[a-zA-Z]*'

class AlnumValidator(RegexValidator):
    """validates a text only consisting of letters and digits ('[a-zA-Z0-9]*')"""
    regex = r'[a-zA-Z0-9]*'

class PhoneValidator(RegexValidator):
    """validates a Brazilian phone number (10-11 digits)"""
    regex = r'[0-9]{10,11}'

class PassportValidator(RegexValidator):
    """a validates a Brazilian passport number ('AB123456')"""
    regex = r'[A-Z]{2}[0-9]{6}'

class IDCardValidator(RegexValidator):
    """a validates a Brazilian ID card number ('123456789')"""
    regex = r'[0-9]{9}'

class PostCodeValidator(RegexValidator):
    """
    validates Brazillian Post Code
    """
    regex = r'[0-9]{8}'

class DobValidator(Validator):
    """
    validates date of birth (must not be in the future)
    """
    def __call__(self, date, *args, **kwargs):
        if date < datetime.date.today(): return True
        else: False


########################################################################################
## NORMALISER

class NullNormaliser():
    """trivial normaliser base class (see Normaliser for details)"""

    def inp(s, data):
        """normalise input data (here: pass through)"""
        return data
        
    def outp(s, data):
        """normalise output data (here: pass through)"""
        return data

    def __call__(s, data):
        """
        alias for `inp`
        """
        return s.inp(data)


class Normaliser(NullNormaliser):
    """
    base class for normalising input and output

    USAGE

        Normaliser().inp(' Paul ') # 'Paul'  - default: strip()
        Normaliser()(' Paul ')     # 'Paul'  - __call__() is in()
        Normaliser().outp('Paul')  # 'Paul'  - default: noop

    CUSTOMISATION

    This base class allows for four different operations

    - remove certain character from the string
    - strip (remove spaces on both sides)
    - lstrip (remove leading spaces)
    - rstrip (remove trailing spaces)

    By default, only strip is active, but others can be passed as arguments.
    For example, this is how we'd only do `lstrip`

        n = Normaliser(lstrip=True) # strip is set to False automatically in this case

    This is how we'd remove dashes and dots (and `strip`)

        n = Normaliser('-.')

    DERIVED CLASSES

    It is also possible do fix those parameters in derived classes. For example, the
    following code would produce a class removing dashes and dots, but no `strip`

        class DashDotNormaliser(Normaliser):
            remove = '-.'
            strip = False

        n = DashDotNormaliser()
        print (n('020-1234-5678 ')) # '02012345678 '

    For more complex cases, derived classes can overwrite the `inp` and `_outp` methods
    (they should not redefined `outp` unless they want to call `inp` manually)
    See `PhoneNormaliser` as an example
    """

    remove = ''
    strip = True
    lstrip = False
    rstrip = False

    def __init__(s, remove=None, strip=None, lstrip=None, rstrip=None):
        if remove: s.remove = remove
        if strip: s.strip = strip
        if lstrip: s.lstrip = lstrip
        if rstrip: s.rstrip = rstrip
        if (lstrip or rstrip) and strip == None: s.strip=False


    ########################################
    ## input normalisation
    def _inp(s, text_to_normalise):
        """
        normalise input: strip and replace, depending on object properties

        note: derived classes should overwrite this method, not `inp`
        """
        remove = list(s.remove)
        for r in remove:
            text_to_normalise = text_to_normalise.replace(r,"")
        if s.strip:  text_to_normalise=text_to_normalise.strip()
        if s.lstrip: text_to_normalise=text_to_normalise.lstrip()
        if s.rstrip: text_to_normalise=text_to_normalise.rstrip()
        return text_to_normalise
    
    def inp(s, text_to_normalise):
        """
        normalise input

        note: derived classes should overwrite `_inp`, not this one
        """
        if not text_to_normalise: text_to_normalise = "" # replace None (and False)
        text_to_normalise = str(text_to_normalise)
        return s._inp(text_to_normalise)


    ########################################
    ## output normalisation
    def _outp(s, text_to_normalise):
        """
        normalise output: noop

        note: derived classes should overwrite this method, not `outp`
        """
        return text_to_normalise
        
    def outp(s, text_to_normalise):
        """
        normalise output

        note: derived classes should overwrite `_outp`, not this one
        """
        if not text_to_normalise: text_to_normalise=""
        text_to_normalise = str(text_to_normalise)
        text_to_normalise = s.inp(text_to_normalise)
        return s._outp(text_to_normalise)

     

#########################################################
## NUMERIC, ALPHA, ALNUM NORMALISER
class NumericNormaliser(Normaliser):
    """
    normalise a numeric field
    
    input: remove all non-numeric characters
    output: noop
    """
    def __init__(s):
        pass

    def _inp(s, text_to_normalise):
        """remove all non-numeric characters"""
        return _remove_non_digit_chars(text_to_normalise)

class AlphaNormaliser(NumericNormaliser):
    """
    normalise an alpha field

    input: remove all non-alpha characters
    output: noop
    """
    def _inp(s, text_to_normalise):
        """remove all non-alpha characters"""
        return _remove_non_alpha_chars(text_to_normalise)

class AlnumNormaliser(NumericNormaliser):
    """
    normalise an alpha-numeric field

    input: remove all non-alpha-numeric characters
    output: noop
    """
    def _inp(s, text_to_normalise):
        """remove all non-alpha-numeric characters"""
        return _remove_non_alnum_chars(text_to_normalise)


#########################################################
## PHONE NORMALISERS
class PhoneNormaliser(NumericNormaliser):
    """
    normalise fixed line phone number
    """
    def _outp(s, text_to_normalise):
        """format: (12) 3456 7890 or (12) 3456 78901"""
        t = text_to_normalise
        if not len(t) in [10,11]: return t
        return "({}) {} {}".format(t[0:2], t[2:6], t[6:])


class MobNormaliser(PhoneNormaliser):
    """
    normalise a mobile phone number
    """
    pass


#########################################################
## IDCARD, PASSPORT NORMALISERS
class PassportNormaliser(AlnumNormaliser):
    """
    normalise a Brazilian passport number
    """
    def _inp(s, text_to_normalise):
        text_to_normalise = super()._inp(text_to_normalise)
        return text_to_normalise.upper()

    def _outp(s, text):
        if len(text) != 8: return text
        return "{} {} {}".format(text[0:2], text[2:5], text[5:8])
        
class IDCardNormaliser(NumericNormaliser):
    """
    normalise a Brazilian ID card number
    """
    def _outp(s, text):
        if len(text) != 9: return text
        return "{}.{}-{}".format(text[0:4], text[4:8], text[8:9])

class PostCodeNormaliser(NumericNormaliser):
    """
    normalise post code
    """
    def _outp(s, text_to_normalise):
        """format: 11111-111"""
        t = text_to_normalise
        if len(t) != 8: return t
        return "{}-{}".format(t[0:5], t[5:8])


#########################################################
## CPF NORMALISER
class CpfNormaliser(NumericNormaliser):
    """
    normalise a CPF number 

    input: remove all non-numeric characters
    output: 999.999.999-99

    EXAMPLES
        CpfNormaliser()('111.222.333-00')      # '11122233300'
        CpfNormaliser().inp('111.222.333-00')  # '11122233300'
        CpfNormaliser().outp('11122233300')    # '111.222.333-00'
    """
    def _outp(s, text_to_normalise):
        """format: 999.999.999-99"""
        t = text_to_normalise
        if len(t) != 11: return t
        return "{}.{}.{}-{}".format(t[0:3], t[3:6], t[6:9], t[9:11])

#########################################################
## CNPJ NORMALISER
class CnpjNormaliser(NumericNormaliser):
    """
    normalise a CNPJ number 

    input: remove all non-numeric characters
    output: 00.000.000/0001-00
    """
    def _outp(s, text_to_normalise):
        """format: 00.000.000/0001-00"""
        t = text_to_normalise
        if len(t) != 14: return t
        return "{}.{}.{}/{}-{}".format(t[0:2], t[2:5], t[5:8], t[8:12], t[12:14])


#########################################################
## DATE NORMALISER
from django.utils import formats
from datetime import date

class DateNormaliser(NullNormaliser):
    """
    normalises date type

    reads array of localised ISO DATE_INPUT_FORMATS from formats.py defined by django
    if the input is of type date then it is formatted and returned given that input_format is present
    else the input is returned without modification
    """

    def outp(s, dt):
        date_formats = formats.get_format('DATE_INPUT_FORMATS')
        if date_formats and len(date_formats) > 0 and type(dt) == date:
            return dt.strftime(date_formats[1])
        else:
            return dt


########################################################################################
## CLEANING
class Cleaner(object):
    """
    makes a cleaning function that can be used in a form
    
    PARAMETERS
    - validator: the validation callable (default: Validator() )
    - normaliser: the normalisation callable (default: Normaliser() )
    - exception_msg: the exception message (default: "validation error")
    - exception: the exception thrown (default: ValidationError)
    
    USAGE
    
        clean_pp = Cleaner(PassportValidator(), PassportNormaliser(), "not a valid passport number")
        
        # example
        c = clean_pp("  aa123456  ") # 'AA123456'
        c = clean_pp("A12345") # raises ValidationError("not a valid passport number")
        
        # usage in a form
        class Form(forms.ModelForm)
            ...
            pp = forms.CharField(validators=[clean_pp])
            ...
            def clean(s):
                if 'pp' in self.cleaned_data:
                    self.cleaned_data['pp] = clean_pp(self.cleaned_data['pp'])
        
        # display data
        print(clean_pp.ft("aa123456")) # "AA123456"
        
    """
    def __init__(s, validator=None, normaliser=None, exception_msg=None, exception=None):
        
        if validator == None: validator = Validator()
        if normaliser == None: normaliser = Normaliser()
        if exception_msg == None: exception_msg = "validation error"
        if exception == None: exception = ValidationError
        s.validator = validator
        s.normaliser = normaliser
        s.exception_msg = exception_msg
        s.exception = exception
    
    #####################################################
    ## EXECUTE (form validation)
    def execute(s,text):
        """
        validator and cleaning function to be used in a form
        
        this function takes a text argument, preprocesses it with the normaliser input
        function and then applies the validator to it; if it validates true the normalised
        input is returned, otherwise an exception thrown
        
        it would generally be used twice in forms: once as a field validator, and then again
        in the cleaning function
        
            clean_pp = Cleaner(PassportValidator(), PassportNormaliser(), "not a valid passport number")
        
            class Form(forms.ModelForm)
                ...
                pp = forms.CharField(validators=[clean_pp])
                ...
                def clean(s):
                    if 'pp' in self.cleaned_data:
                        self.cleaned_data['pp] = clean_pp(self.cleaned_data['pp'])
        """
        text = s.normaliser(text)
        if s.validator(text): return text
        raise s.exception(s.exception_msg)
    
    def __call__(s, text):
        """
        alias for `validator`
        """
        return s.execute(text)
    
    #####################################################
    ## FT (output formatting)
    def ft(s, text):
        """
        formats text using the normaliser's `outp` method
        
        print(clean_pp.ft("aa123456")) # "AA123456"
        """ 
        return s.normaliser.outp(text)
