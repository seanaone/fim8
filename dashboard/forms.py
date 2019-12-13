from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from dashboard.models import Account
from django import forms
import parser

#this is used to get an associated account with an asset
#for instance if a user adds their home, they can attach their mortgage account to it
def getAllAccounts(user):
	accounts = list()
	#gets only the user's loan or credit accounts
	acc = list(Account.objects.filter(user=user))
	#creates a list of choicefield options
	for account in acc:
		#choicefield options are comprised of a key and a value
		#in this case, the account name the user would recognize, and the actual account object
		item = (account.accountID, account.name)
		accounts.append(item)
	return accounts


#this is used to get an associated account with an asset
#for instance if a user adds their home, they can attach their mortgage account to it
def getExpenseAccounts(user):
	accounts = list()
	#gets only the user's loan or credit accounts
	acc = list(Account.objects.filter(user=user, accountType="loan") | Account.objects.filter(user=user, accountType="credit"))
	#creates a list of choicefield options
	for account in acc:
		#choicefield options are comprised of a key and a value
		#in this case, the account name the user would recognize, and the actual account object
		item = (account.accountID, account.name)
		accounts.append(item)
	return accounts


#this form is used to add a realestate property and get a zillow estimate for it
class addPropertyForm(forms.Form):

	address = forms.CharField(
		label = "Street, Town, State",
		required = True,
	)

	zipCode = forms.CharField(
		label = "Zipcode",
		required = True,
	)

	assetAmountOwed = forms.IntegerField(
		label = "How much is owed on it? (blank if 0)",
		required = False,
	)

	def __init__(self, *args, **kwargs):
		super(addPropertyForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = 'id-addPropertyForm'
		self.helper.form_class = 'blueForms'
		self.helper.form_method = 'POST'
		self.helper.form_action = ''
		self.helper.add_input(Submit('submit', 'Submit'))


#this form is used to add a realestate property with an associated account
# and get a zillow estimate for it
class addPropertyWithAccountForm(forms.Form):

	address = forms.CharField(
		label = "Street, Town, State",
		required = True,
	)

	zipCode = forms.CharField(
		label = "Zipcode",
		required = True,
	)

	# account = models.ForeignKey(Account, on_delete=models.CASCADE)
	assetAccount = forms.ChoiceField(
		label = "Select Associated Account",
		required = True,
	)

	def __init__(self, user, *args, **kwargs):
		super(addPropertyWithAccountForm, self).__init__(*args, **kwargs)
		self.user = user
		#the accounts are retrieved dynamically on form creation
		self.fields['assetAccount'] = forms.ChoiceField(choices=getExpenseAccounts(self.user) )
		self.helper = FormHelper()
		self.helper.form_id = 'id-addPropertyWithAccountForm'
		self.helper.form_class = 'blueForms'
		self.helper.form_method = 'POST'
		self.helper.form_action = ''
		self.helper.add_input(Submit('submit', 'Submit'))


#adds an asset to be stored
class addAssetForm(forms.Form):

	# name = models.CharField(max_length = 100)
	assetLabel = forms.CharField(
		label = "What is it?",
		required = True,

	)

	# value = models.IntegerField()
	assetValue = forms.IntegerField(
		label = "What's it worth?",
		required = True
	)

	# owed = models.IntegerField()
	assetAmountOwed = forms.IntegerField(
		label = "How much is owed on it? (blank if 0)",
		required = False
		
	)

	def __init__(self, *args, **kwargs):
		super(addAssetForm, self).__init__(*args, **kwargs)
		assetLabelInitial = kwargs.get('assetLabelInitial', None)
		assetValueInitial = kwargs.get('assetValueInitial', None)
		assetAmountOwedInitial = kwargs.get('assetAmountOwedInitial', None)
		self.fields['assetLabel'].initial = assetLabelInitial
		self.fields['assetValue'].initial = assetValueInitial
		self.fields['assetAmountOwed'].initial = assetAmountOwedInitial
		self.helper = FormHelper()
		self.helper.form_id = 'id-addAssetForm'
		self.helper.form_class = 'blueForms'
		self.helper.form_method = 'POST'
		self.helper.form_action = ''
		self.helper.add_input(Submit('submit', 'Submit'))


#adds asset with associated account
class addAssetWithAccountForm(forms.Form):
	# name = models.CharField(max_length = 100)
	assetLabel = forms.CharField(
		label = "What is it?",
		required = True,
		)

	# value = models.IntegerField()
	assetValue = forms.IntegerField(
		label = "What's it worth?",
		required = True,
	)

	# account = models.ForeignKey(Account, on_delete=models.CASCADE)
	assetAccount = forms.ChoiceField(
		label = "Select Associated Account",
		required = True,
	)
	
	def __init__(self, user, *args, **kwargs):
		super(addAssetWithAccountForm, self).__init__(*args, **kwargs)
		self.user = user
		self.fields['assetAccount'] = forms.ChoiceField(choices=getAllAccounts(self.user) )
		self.helper = FormHelper()
		self.helper.form_id = 'id-addAssetWithAccountForm'
		self.helper.form_class = 'blueForms'
		self.helper.form_method = 'POST'
		self.helper.form_action = ''
		self.helper.add_input(Submit('submit', 'Submit'))




# class RobinHoodLoginForm(forms.Form):

#     username =  forms.CharField(
#         label = "Username",
#         required = True,
#     )

#     password =  forms.CharField(
#         label = "Password",
#         required = True,
#     )

#     def __init__(self, *args, **kwargs):
#         super(RobinHoodLoginForm, self).__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_id = 'id-RobinHoodLoginForm'
#         self.helper.form_class = 'blueForms'
#         self.helper.form_method = 'POST'
#         self.helper.form_action = 'robinhood_login/'
#         self.helper.add_input(Submit('submit', 'Submit'))

