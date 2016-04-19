"""
testing code for `validators.py`

Copyright (c) Stefan LOESCH, oditorium 2016. All rights reserved.
Licensed under the Mozilla Public License, v. 2.0 <https://mozilla.org/MPL/2.0/>
"""


from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse_lazy, reverse
#from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError

from _project.decorators import ignore_failing, ignore_long

from .validators import *

#########################################################################################
## TRIVIAL TEST
@ignore_failing
class TrivialTest(TestCase):
    """just making sure the testing framework works properly"""
    def test_fails(s):
        s.assertEqual(2,1+1)
        #s.assertTrue(False)

#########################################################################################
## VALIDATOR TEST
class ValidatorTest(TestCase):
    
    def test_validator(s):
        """test Validator (always True)"""
        s.assertTrue( Validator()(''))
        s.assertTrue( Validator()('1111'))
        s.assertTrue( Validator()('aaaa'))
        
    def test_num_validator(s):
        """test NumericValidator (digits only)"""
        s.assertTrue( NumericValidator()(''))
        s.assertTrue( NumericValidator()('1234567890'))
        s.assertFalse( NumericValidator()('abcdefg'))
        s.assertFalse( NumericValidator()('abcdefg1'))

    def test_alpha_validator(s):
        """test AlphaValidator (alpha only)"""
        s.assertTrue( AlphaValidator()(''))
        s.assertFalse( AlphaValidator()('1234567890'))
        s.assertTrue( AlphaValidator()('abcdefg'))
        s.assertTrue( AlphaValidator()('ABCDEFG'))
        s.assertTrue( AlphaValidator()('abcDEFG'))
        s.assertFalse( AlphaValidator()('abcdefg1'))

    def test_alnum_validator(s):
        """test AlnumValidator (alpha-numeric only)"""
        s.assertTrue( AlnumValidator()(''))
        s.assertTrue( AlnumValidator()('abc123'))
        s.assertFalse( AlnumValidator()('abc-123'))
        s.assertFalse( AlnumValidator()('abc.123'))

    def test_phone_validator(s):
        """test Brazil PhoneValidator (10 or 11 digits)"""
        s.assertFalse( PhoneValidator()(''))
        s.assertTrue( PhoneValidator()('1234567890'))
        s.assertTrue( PhoneValidator()('12345678901'))
        s.assertFalse( PhoneValidator()('123456789'))
        s.assertFalse( PhoneValidator()('123456789012'))
        s.assertFalse( PhoneValidator()('1234567890a'))

    def test_postcode_validator(s):
        """test Brazil PostCodeValidator (8 digits)"""
        s.assertFalse( PostCodeValidator()(''))
        s.assertTrue( PostCodeValidator()('12345678'))
        s.assertFalse( PostCodeValidator()('1234567'))
        s.assertFalse( PostCodeValidator()('123456789'))
        s.assertFalse( PhoneValidator()('1234567a'))

    def test_passport_validator(s):
        """test Brazil PassportValidator (AA999999)"""
        s.assertFalse( PassportValidator()(''))
        s.assertTrue( PassportValidator()('AA123456'))
        s.assertFalse( PassportValidator()('a123456'))
        s.assertFalse( PassportValidator()('a123456'))
        s.assertFalse( PassportValidator()('aa-123456'))

    def test_idcard_validator(s):
        """test Brazil IDCardValidator (9 digits)"""
    
        s.assertFalse( IDCardValidator()(''))
        s.assertTrue( IDCardValidator()('123456789'))
        s.assertTrue( IDCardValidator()('000000000'))
        s.assertFalse( IDCardValidator()('1234567890'))
        s.assertFalse( IDCardValidator()('12345678'))
        s.assertFalse( IDCardValidator()('12345678a'))

    def test_regex_validator(s):
        """test RegexValidator (generic regex)"""
        
        v = RegexValidator(r'[a-z][0-9][A-C]')
        s.assertFalse( v(''))
        s.assertTrue( v('a0A'))
        s.assertTrue( v('b5C'))
        s.assertFalse( v('b5C '))
        s.assertFalse( v(' b5C'))
    
    def test_cpf_validator(s):
        """test CpfValidator"""
        # http://geradorderg.com/gerador-de-cpf/
        s.assertFalse( CpfValidator()('') )
        s.assertFalse( CpfValidator()(None) )
        s.assertTrue( CpfValidator()('70600399109') )
        s.assertTrue( CpfValidator()('00000101117') )
        s.assertTrue( CpfValidator()('00000107158') )
        s.assertTrue( CpfValidator()('00000118001') )
        s.assertTrue( CpfValidator()('00000128155') )
        s.assertTrue( CpfValidator()('00000142735') )
        s.assertTrue( CpfValidator()('11456458876') )
        s.assertTrue( CpfValidator()('22434070191') )
        s.assertTrue( CpfValidator()('69720010568') )
        s.assertTrue( CpfValidator()('697.200.105-68') )

    def test_cnpj_validator(s):
        """test CnpjValidator"""
        # http://geradorderg.com/gerar-cnpj/
        s.assertFalse( CnpjValidator()('') )
        s.assertFalse( CnpjValidator()(None) )
        s.assertFalse( CnpjValidator()('70600399109') )
        s.assertTrue ( CnpjValidator()('62173620000180') )
        s.assertFalse( CnpjValidator()('62173620000181') )
        s.assertTrue ( CnpjValidator()('90400888000142') )
        s.assertFalse( CnpjValidator()('90400888000141') )
        s.assertFalse( CnpjValidator()('90400888000149') )
        s.assertTrue ( CnpjValidator()('62173620000180') )
        s.assertFalse( CnpjValidator()('62173620000182') )


#########################################################################################
## NORMALISER TEST
class NormaliserTest(TestCase):
    def test_normaliser(s):
        """test Normaliser (strip)"""
        s.assertEqual(Normaliser()(''), '')
        s.assertEqual(Normaliser()('abc'), 'abc')
        s.assertEqual(Normaliser()(' abc'), 'abc')
        s.assertEqual(Normaliser()('abc '), 'abc')
        s.assertEqual(Normaliser()(' abc '), 'abc')
        s.assertEqual(Normaliser(lstrip=True)(' abc '), 'abc ')
        s.assertEqual(Normaliser(rstrip=True)(' abc '), ' abc')
        s.assertEqual(Normaliser().inp(' abc '), 'abc')
        
        s.assertEqual(Normaliser(lstrip=True).inp(' abc '), 'abc ')
        s.assertEqual(Normaliser(rstrip=True).inp(' abc '), ' abc')

        s.assertEqual(Normaliser().outp('abc'), 'abc')
        s.assertEqual(Normaliser().outp('  abc  '), 'abc')
        s.assertEqual(Normaliser().outp(None), '')
        

    def test_numeric_normaliser(s):
        """ test NumericNormaliser (remove non-digits)"""
        s.assertEqual(NumericNormaliser()(''), '')
        s.assertEqual(NumericNormaliser()('abc'), '')
        s.assertEqual(NumericNormaliser()('100'), '100')
        s.assertEqual(NumericNormaliser()('100,000,000.00'), '10000000000')
        s.assertEqual(NumericNormaliser()('11111111111111111111'), '11111111111111111111')
        s.assertEqual(NumericNormaliser()('12345'), '12345')
        s.assertEqual(NumericNormaliser()('  12345'), '12345')
        s.assertEqual(NumericNormaliser()('12345  '), '12345')
        s.assertEqual(NumericNormaliser()('  12345  '), '12345')
        s.assertEqual(NumericNormaliser()('as1=2/3..4--5s££$%^'), '12345')
        s.assertEqual(NumericNormaliser().inp('as1=2/3..4--5s££$%^'), '12345')
        s.assertEqual(NumericNormaliser().outp('as1=2/3..4--5s££$%^'), '12345')
        s.assertEqual(NumericNormaliser().outp(None), '')


    def test_phone_normaliser(s):
        """ test Brazilian PhoneNormaliser (10-11 digits, '(12) 3456 7890')"""
        s.assertEqual(PhoneNormaliser()(''), '')
        s.assertEqual(PhoneNormaliser()('(01)-2345.6789'), '0123456789')
        s.assertEqual(PhoneNormaliser().inp('1-212-317-000'), '1212317000')

        s.assertEqual(PhoneNormaliser().outp('1234567890'), '(12) 3456 7890')
        s.assertEqual(PhoneNormaliser().outp('12345678901'), '(12) 3456 78901')
        s.assertEqual(PhoneNormaliser().outp(None), '')

    def test_mob_normaliser(s):
        """ test Brazilian MobNormaliser (10-11 digits, '(12) 3456 7890')"""
        s.assertEqual(MobNormaliser()(''), '')
        s.assertEqual(MobNormaliser()('(01)-2345.6789'), '0123456789')
        s.assertEqual(MobNormaliser().inp('1-212-317-000'), '1212317000')

        s.assertEqual(MobNormaliser().outp('1234567890'), '(12) 3456 7890')
        s.assertEqual(MobNormaliser().outp('12345678901'), '(12) 3456 78901')
        s.assertEqual(MobNormaliser().outp(None), '')

    def test_cpf_normaliser(s):
        """test CPF Normaliser ('111.222.333-44')"""
        s.assertEqual(CpfNormaliser()(''), '')
        s.assertEqual(CpfNormaliser()('697.200.105-68'), '69720010568')
        s.assertEqual(CpfNormaliser().inp('697.200.105-68'), '69720010568')
        s.assertEqual(CpfNormaliser()('   697.200.105-68   '), '69720010568')
        s.assertEqual(CpfNormaliser().inp('   697.200.105-68   '), '69720010568')
        s.assertEqual(CpfNormaliser()('a697q20x0=105?6€8'), '69720010568')

        s.assertEqual(CpfNormaliser().outp('69720010568'), '697.200.105-68')
        s.assertEqual(CpfNormaliser().outp('697.200.105-68'), '697.200.105-68')
        s.assertEqual(CpfNormaliser().outp(' 697.200.105-68  '), '697.200.105-68')
        s.assertEqual(CpfNormaliser().outp(None), '')

    def test_cnpj_normaliser(s):
        """test CNPJ Normaliser ('11.222.333/4444-55')"""
        s.assertEqual(CnpjNormaliser()(''), '')
        s.assertEqual(CnpjNormaliser()('62173620000180'), '62173620000180')
        s.assertEqual(CnpjNormaliser().inp('62173620000180'), '62173620000180')
        s.assertEqual(CnpjNormaliser()('62.173.620/0001-80'), '62173620000180')
        s.assertEqual(CnpjNormaliser()('  62 173 620 0001 80   '), '62173620000180')
        s.assertEqual(CnpjNormaliser()('11.222.333/4444-55'), '11222333444455')

        s.assertEqual(CnpjNormaliser().outp('62.173.620/0001-80'), '62.173.620/0001-80')
        s.assertEqual(CnpjNormaliser().outp('62173620000180'), '62.173.620/0001-80')

    def test_passport_normaliser(s):
        """ test Brazilian PassportNormaliser ('AA 123 456')"""
        s.assertEqual(PassportNormaliser()(''), '')
        s.assertEqual(PassportNormaliser().outp('AA123456'), 'AA 123 456')
        s.assertEqual(PassportNormaliser().outp('A123456'), 'A123456')
        s.assertEqual(PassportNormaliser().outp('AAA123456'), 'AAA123456')
        s.assertEqual(PassportNormaliser().outp(None), '')
        
    def test_idcard_normaliser(s):
        """ test Brazilian IDCardNormaliser ('1234.5678-9')"""
        s.assertEqual(IDCardNormaliser()(''), '')
        s.assertEqual(IDCardNormaliser().outp('123456789'), '1234.5678-9')
        s.assertEqual(IDCardNormaliser().outp('12345678'), '12345678')
        s.assertEqual(IDCardNormaliser().outp('1234567890'), '1234567890')
        s.assertEqual(IDCardNormaliser().outp(None), '')
        


#########################################################################################
## VALIDATION TEST
class ValidationTest(TestCase):
    
    def setUp(s):
        s.clean = Cleaner()
        s.clean_numeric = Cleaner(NumericValidator(), NumericNormaliser(), "xyz")
        s.clean_alpha = Cleaner(AlphaValidator(), AlphaNormaliser(), "xyz")
        s.clean_alnum = Cleaner(AlnumValidator(), AlnumNormaliser(), "xyz")
        s.clean_passport = Cleaner(PassportValidator(), PassportNormaliser(), "xyz")
        s.clean_idcard = Cleaner(IDCardValidator(), IDCardNormaliser(), "xyz")
        s.clean_cpf = Cleaner(CpfValidator(), CpfNormaliser(), "xyz")
        s.clean_cnpj = Cleaner(CnpjValidator(), CnpjNormaliser(), "xyz")
    
    def test_cleaning_correct(s):
        """test cleaning of correct expressions"""
        s.assertEqual(s.clean(""),  "")
        s.assertEqual(s.clean("  123  abc&*@$ --= "),  "123  abc&*@$ --=")
        
        s.assertEqual(s.clean_numeric(""),  "")
        s.assertEqual(s.clean_numeric("123"), "123")
        s.assertEqual(s.clean_numeric("  123  "), "123")
        s.assertEqual(s.clean_numeric("1a2b3c"), "123")
        
        s.assertEqual(s.clean_alpha(""),  "")
        s.assertEqual(s.clean_alpha("abc"), "abc")
        s.assertEqual(s.clean_alpha("  abc  "), "abc")
        s.assertEqual(s.clean_alpha("1a2b3c"), "abc")
        
        s.assertEqual(s.clean_alnum(""),  "")
        s.assertEqual(s.clean_alnum("1a2b3c"), "1a2b3c")
        s.assertEqual(s.clean_alnum("  1a2b3c  "), "1a2b3c")
        s.assertEqual(s.clean_alnum("1a=2b-3c"), "1a2b3c")

        s.assertEqual(s.clean_passport("AA123456"), "AA123456")
        s.assertEqual(s.clean_passport("  AA123456  "), "AA123456")
        s.assertEqual(s.clean_passport("AA-123.456"), "AA123456")
        s.assertEqual(s.clean_passport("aa123456"), "AA123456")

        s.assertEqual(s.clean_idcard("123456789"), "123456789")
        s.assertEqual(s.clean_idcard("  123456789  "), "123456789")
        s.assertEqual(s.clean_idcard("1234.5678-9"), "123456789")
        
        s.assertEqual(s.clean_cpf("00000128155"), "00000128155")
        s.assertEqual(s.clean_cpf("000.001.281-55"), "00000128155")
        s.assertEqual(s.clean_cpf("000 001 281 55"), "00000128155")

        s.assertEqual(s.clean_cnpj("62.173.620/0001-80"), "62173620000180")
        s.assertEqual(s.clean_cnpj("62173620000180"), "62173620000180")
        s.assertEqual(s.clean_cnpj("62 173 620 0001 80"), "62173620000180")

    def test_clean_raise(s):
        """test that Validation errors are raised by the cleaners"""
        with s.assertRaisesMessage(ValidationError, "xyz"): s.clean_passport("")
        with s.assertRaisesMessage(ValidationError, "xyz"): s.clean_passport("AA12345")
        with s.assertRaisesMessage(ValidationError, "xyz"): s.clean_passport("A123456")
        with s.assertRaisesMessage(ValidationError, "xyz"): s.clean_passport("123456ab")

        with s.assertRaisesMessage(ValidationError, "xyz"): s.clean_idcard("")
        with s.assertRaisesMessage(ValidationError, "xyz"): s.clean_idcard("12345678")
        with s.assertRaisesMessage(ValidationError, "xyz"): s.clean_idcard("1234567890")
        with s.assertRaisesMessage(ValidationError, "xyz"): s.clean_idcard("aa12345678")
        with s.assertRaisesMessage(ValidationError, "xyz"): s.clean_idcard("aa1234567")

        with s.assertRaisesMessage(ValidationError, "xyz"): s.clean_cpf("000001281555") # too long
        with s.assertRaisesMessage(ValidationError, "xyz"): s.clean_cpf("0000012815") # too short
        with s.assertRaisesMessage(ValidationError, "xyz"): s.clean_cpf("00000128156") # wrong checksum

        with s.assertRaisesMessage(ValidationError, "xyz"): s.clean_cnpj("621736200001800") # too long
        with s.assertRaisesMessage(ValidationError, "xyz"): s.clean_cnpj("6217362000018") # too short
        with s.assertRaisesMessage(ValidationError, "xyz"): s.clean_cnpj("62173620000181") # wrong checksum
        
    def test_clean_ft(s):
        """test that the `ft` (=formatting method) of the cleaner works"""
        s.assertEqual(s.clean_passport.ft("AA123456"), "AA 123 456")
        s.assertEqual(s.clean_passport.ft("aa-12-34-56"), "AA 123 456")
        s.assertEqual(s.clean_idcard.ft("123456789"), "1234.5678-9")
        s.assertEqual(s.clean_idcard.ft("12-34.56=78/9"), "1234.5678-9")
        s.assertEqual(s.clean_cpf.ft("70600399109"), "706.003.991-09")
        s.assertEqual(s.clean_cpf.ft("706.003/991-09"), "706.003.991-09")

        

