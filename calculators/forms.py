from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from dashboard.forms import getExpenseAccounts

class InterestForm(forms.Form):

    principal = forms.FloatField(
        label = "principal?",
        required = True,
    )

    rate = forms.FloatField(
        label = "interest rate (Ex: 8.4% = 8.4)",
        required = True,
    )

    years = forms.IntegerField(
        label = "Over how many years?",
        required = True,
    )


    def __init__(self, *args, **kwargs):
        super(InterestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-InterestForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'POST'
        self.helper.form_action = '/'
        self.helper.add_input(Submit('submit', 'Submit'))

class WhenCanIRetireForm(forms.Form):

    startingPrincipal = forms.FloatField(
        label = "How much do you currently have saved for retirement?",
        required = True,
    )

    expectedAnnualReturn = forms.FloatField(
        label = "what is your expected annual return rate? (Ex: 8.4% = 8.4)",
        required = True,
    )

    monthlyContributions = forms.FloatField(
        label = "How much will you contribute per month to your nest egg?",
        required = True,
    )

    percentageIncreaseInMonthlyContributionsPerYear = forms.FloatField(
        label = "How much will you increase your contribution per year (percentage)",
        required = False,
        initial = 0,
    ) 

    annualExpenses = forms.FloatField(
        label = "How much do you expect to need annualy in retirement?",
        required = True,
    )

    def __init__(self, *args, **kwargs):
        super(WhenCanIRetireForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-WhenCanIRetireForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'POST'
        self.helper.form_action = '/when_can_i_retire_answer'
        self.helper.add_input(Submit('submit', 'Submit'))


class HowLongTillIPayOffAccountForm(forms.Form):

    principalAccount = forms.ChoiceField(
        label = "Which account are you trying to pay off??",
        required = True,
    )

    rate = forms.FloatField(
        label = "what is the APR on the loan",
        required = True,
    )

    monthlyContributions = forms.FloatField(
        label = "How much will you pay toward this loan per month?",
        required = True,
    )
 

    def __init__(self, user, *args, **kwargs):
        super(HowLongTillIPayOffAccountForm, self).__init__(*args, **kwargs)
        self.user = user
        #the accounts are retrieved dynamically on form creation
        self.fields['principalAccount'] = forms.ChoiceField(choices=getExpenseAccounts(self.user) )
        self.helper = FormHelper()
        self.helper.form_id = 'id-HowLongTillIPayOffAccountForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'POST'
        self.helper.form_action = '/'
        self.helper.add_input(Submit('submit', 'Submit'))

