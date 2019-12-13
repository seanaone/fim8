from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Sum
from dashboard.models import Account, User, Transaction, UserProfile, AssetLiabilityObject, AssetWithAccountObject
from fim8.settings import Plaid
import plaid
from plaid import Client
import os
import requests
import json
import zillow 
import datetime
from json import loads
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from .forms import addPropertyForm, addPropertyWithAccountForm, addAssetForm, addAssetWithAccountForm
#, RobinHoodLoginForm
#import robin_stocks as r



#this allows for communication between fim8 and the Plaid API for bank account and transaction information
#environment can be changed from 'sandbox' to 'development' to switch between real and fake bank account information
#being generated
client = Client(client_id=Plaid.PLAID_CLIENT_ID, secret=Plaid.PLAID_SECRET, 
    public_key=Plaid.PLAID_PUBLIC_KEY, environment=Plaid.PLAID_ENV)



'''
NAME
        home - main page of the application

SYNOPSIS

        home(request)

			Parameters:
				request -->takes in an http request object
					request.user  -->  the user currently logged in, used to pull just the users information
			Decorators:
				@login_required -->  only requests that have a user are accepted, else brought to login page

DESCRIPTION

		This function renders the dashboard of the application, which also serves as the main page.
		it grabs the users accounts, transactions, and assets from the database and adds them to a dictionary
		for the template.

RETURNS

        return render(request, 'dashboard/home.html', context)
		returns the html home page rendered with all of the users account, transactions, and asset data.
		this data is stored in a dictionary called context, which can be manipualted and accesses using
		the jinja templating engine directly in the html file.

AUTHOR

        Sean O'Neill
'''
#must login to view dashboard
@login_required
def home(request):

	# webhook_response = client.Item.webhook.update(
    # accounts.first().accessToken, 'https://plaid.com/updated/webhook')

	# print('')
	# print(webhook_response)



	###################ROBINHOOD####################

	####

	###################ASSETS####################
	#boolean used to determine whether to render users assets card or a prompt to add assets
	userHasAssets = AssetWithAccountObject.objects.filter(user = request.user).exists() | AssetLiabilityObject.objects.filter(user = request.user).exists()
	assetsAndLiabilities = getAssetsFromDB(request)

	###################ACCOUNTS####################
	#if no accounts, should load a prompt to add accounts
	accounts = getAccountsFromDB(request)
	if not accounts:
		return render(request, 'dashboard/noaccounts.html')


	###################TRANSACTIONS####################
	transactions = list(getTransactionsFromDB(request))


	#Dictionary passed in to template
	context =  {
		###################DATA####################
		'assets': assetsAndLiabilities, #all the users assets
		'userHasAssets': userHasAssets, #used to branch between displaying assets and prompt to add
		'accounts': accounts,  #the users accounts, 1st column
		'transactions': transactions, #the users transactions, 2nd column

		###################FORMS####################
		#forms for creating assets without accounts
		'add_asset_form': addAssetForm, 
		'add_property_form': addPropertyForm, 
		#forms for creating assets with accounts, must have user passed in for account choicefields
		'add_asset_with_account_form':  addAssetWithAccountForm(request.user),
		'add_property_with_account_form': addPropertyWithAccountForm(request.user)

		}
				# 'robin_hood_login_form': RobinHoodLoginForm,
	return render(request, 'dashboard/home.html', context)


'''
NAME
        getAccessToken

SYNOPSIS

        getAccessToken(request)

			Parameters:
				request -->takes in an http request object
					request.user  -->  the user currently logged in, used to pull just the users information
			Decorators:
				@login_required -->  only requests that have a user are accepted, else brought to login page

DESCRIPTION

		This function exchanges a public token, received from a successful account login through plaid, for an access token
		This access token is then used to retrieve account and transaction data from the API

RETURNS

		return JsonResponse(exchange_response)
			a JSON representation of the api response, triggers page reload with users data

AUTHOR

        Sean O'Neill
'''
@login_required
def getAccessToken(request):
	if request.method == 'POST':
		public_token = 	request.POST.get('public_token', None) 

		try:
			exchange_response = client.Item.public_token.exchange(public_token)
		except plaid.errors.PlaidError as e:
			return e

		access_token = exchange_response['access_token']

		getDashboardData(request, access_token)
		
		return JsonResponse(exchange_response)


'''
NAME
        getAssetsFromDB

SYNOPSIS

        getAccessToken(request)

			Parameters:
				request --> takes in an http request object
				request.user  -->  the user currently logged in, used to pull just the users information
			Decorators:
				@login_required -->  only requests that have a user are accepted, else brought to login page

DESCRIPTION

 			This function gets all the user's stored Assets

RETURNS

		return assetsCombined
			list of assets with and without associated accounts

AUTHOR

        Sean O'Neill
'''
@login_required
def getAssetsFromDB(request):
	assetsWithAccounts = list(AssetWithAccountObject.objects.filter(user = request.user))
	assetsWithoutAccounts = list(AssetLiabilityObject.objects.filter(user = request.user))
	assetsCombined = assetsWithAccounts +assetsWithoutAccounts
	return assetsCombined


# this function gets all the user's stored Accounts
# Parameter: in an http request object
# Returns: Query Set of Account objects that belong to the user
#
def getAccountsFromDB(request):
	return Account.objects.filter(user=request.user)


# this function gets all the user's stored Transactions
# Parameter: in an http request object
# Returns: Query Set of Transaction objects that belong to the user
#
def getTransactionsFromDB(request):
	return Transaction.objects.filter(Account__user = request.user).order_by('-datePosted')


'''
NAME
        getAccounts

SYNOPSIS

        getAccounts(request, access_token)

			Parameters:
				request --> takes in an http request object
					request.user  -->  the user currently logged in, used to pull just the users information

				access_token --> sent to the Plaid API in order to receive banking information
			Decorators:
				@login_required -->  only requests that have a user are accepted, else brought to login page

DESCRIPTION

 			This function gets the accounts response from the Plaid API
			Iterates over the Response and creates Account objects from each entry in the response
			if the account already exists, print to console
			if getAccounts fails, returns JSON response of error data

RETURNS

		return JsonResponse({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } }
		
		will only return a JSON response if there is an Error, else will not return anything

AUTHOR

        Sean O'Neill
'''
@login_required 
def getAccounts(request, access_token):

	try:
		accounts_response = client.Accounts.get(access_token)
		#for every Account Plaid sends, create a new Account object, initialize it, and save to the database
		for data in accounts_response['accounts']:

			if not Account.objects.filter(user=request.user, name = data.get('name', None), mask = data.get('mask', None)).exists():
				newAccount = Account()
				newAccount.initialize(access_token, data.get('account_id', None), access_token[1], data.get('balances', None), data.get('limit', None), data.get('mask', None),  data.get('name', None), data.get('official_name', None), data.get('subtype', None), data.get('type', None), request.user)
				newAccount.save()
			else:
				print('ACCOUNT ALREADY EXISTS')
	except plaid.errors.PlaidError as e:
		return JsonResponse({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })


'''
NAME
        getTransactions

SYNOPSIS

        getTransactions(request)

			Parameters:
				request --> takes in an http request object
					request.user  -->  the user currently logged in, used to pull just the users information

				access_token --> sent to the Plaid API in order to receive banking information
			Decorators:
				@login_required -->  only requests that have a user are accepted, else brought to login page

DESCRIPTION
			Gets all of the users transactions from the Plaid Api response fromm January 1st, 2000, until today
			for every entry in the response, create a new Transaction object
			These transaction objects are associated with Account objects via their account_id


RETURNS

		return JsonResponse({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } }
		
		will only return a JSON response if there is an Error, else will not return anything

AUTHOR

        Sean O'Neill
'''
def getTransactions(request, access_token):

	today = datetime.datetime.now()
	todayFormatted = today.strftime('%Y-%m-%d')
	
	try:
		response = client.Transactions.get(access_token, start_date='2000-01-01', end_date=todayFormatted)

		transactions = response['transactions']
		print(transactions)
		#for every transaction Plaid sends, create a new Transaction object, initialize it, and save to the database
		for data in transactions:
			newTransaction = Transaction()
			newTransaction.initialize(data.get('name', None), data.get('amount', None), data.get('date', None), data.get('account_id', None), data.get('category', None))
			newTransaction.save()
			# print(data.get('name', None))

	except plaid.errors.PlaidError as e:
		return JsonResponse({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })

'''
NAME
        getDashboardData

SYNOPSIS

        getDashboardData(request, access_token)

			Parameters:
				request --> takes in an http request object
					request.user  -->  the user currently logged in, used to pull just the users information

				access_token --> sent to the Plaid API in order to receive banking information


DESCRIPTION
			calls the functions to get adn store account and transaction data from the Plaid API


RETURNS
		void

AUTHOR

        Sean O'Neill
'''
def getDashboardData(request, access_token):
	#accounts needs to come first so that transactions can find their associated accounts
	getAccounts(request, access_token)
	getTransactions(request, access_token)


'''
NAME
        focusOnAccount

SYNOPSIS

        focusOnAccount(request, focusAccountID)

			Parameters:
				request --> takes in an http request object
					request.user  -->  the user currently logged in, used to pull just the users information

				focusAccountID --> the id of the account that is being pulled up
			Decorators:
				@login_required -->  only requests that have a user are accepted, else brought to login page

DESCRIPTION
			returns a rendered html page with the account retrieved by ID,
			 as well as the transactions associated with the account and the total of those transactions


RETURNS
		void

AUTHOR

        Sean O'Neill
'''
@login_required
def focusOnAccount(request, focusAccountID):
	account = Account.objects.get(accountID=focusAccountID)
	transactions  = Transaction.objects.filter(Account=account)
	totalOfTransactions = Transaction.objects.filter(Account=account).aggregate(Sum('amount'))
	context = {
		'account': account, 
		'transactions': transactions,
		'totalOfTransactions': totalOfTransactions['amount__sum']
	}
	return render(request, 'dashboard/accountfocus.html', context)


'''
NAME
        zillowRealEstateAppraisal

SYNOPSIS

       	zillowRealEstateAppraisal(address, postalCode)

			Parameters:
				address --> property's address, Street, Town, State format
				postalCode --> 7 digit postal code of property

			Decorators:
				None

DESCRIPTION
			uses the Zillow Valuation API to get a property's estimated value
			parses the Zillow Object returned by the API to grab the the valuation and recognized Address


RETURNS
			zillowAppraisal - list containing the estimated amount, and the address recognized by zillow

AUTHOR

        Sean O'Neill
'''
def zillowRealEstateAppraisal(address, postalCode):
	zillowApi = zillow.ValuationApi()
	zillowKey = 'X1-ZWz17t4tuf26mj_ac8os'
	zillowObject = zillowApi.GetDeepSearchResults(zillowKey, address, postalCode)
	detail_data = zillowApi.GetZEstimate(zillowKey, zillowObject.zpid)
	address = detail_data.get_dict()['full_address']['street'] + ", " + detail_data.get_dict()['full_address']['city'] + ", " + detail_data.get_dict()['full_address']['state'] + ", " + detail_data.get_dict()['full_address']['zipcode']
	zillowAppraisal = list()
	zillowAppraisal.append(detail_data.get_dict()['zestimate']['amount'])
	zillowAppraisal.append(address)
	return zillowAppraisal

'''
NAME
        addProperty

SYNOPSIS

       	addProperty(request)

			Parameters:
				request --> takes in an http request object
					request.user  -->  the user currently logged in, used to pull just the users information
					request.POST --> data filled in by user from form

			Decorators:
				@login_required -->  only requests that have a user are accepted, else brought to login page

DESCRIPTION
			called from add Property form submission button
			takes POST data from filled out form, checks if valid
			if it is, use Zillow to get Property Valuation
			create and save AssetLiabilityObject to database


RETURNS
			next = request.POST.get('next', '/')
			HttpResponseRedirect(next)
			redirects to parent page's url to prevent errors when adding multiple properties in the same session

AUTHOR

        Sean O'Neill
'''
#this uses the addPropertyForm to create a new Asset Object
@login_required
def addProperty(request):
	form = addPropertyForm(request.POST or None)
	if request.method == 'POST':
		if form.is_valid():
			try:
				propertyAppraisal = zillowRealEstateAppraisal(form.cleaned_data['address'], form.cleaned_data['zipCode'])
				assetProperty = AssetLiabilityObject()
				assetProperty.initialize(request.user, propertyAppraisal[1], propertyAppraisal[0], form.cleaned_data['assetAmountOwed'])
				assetProperty.save()
			except:
				print('Error: Could not add Property')
				pass
	next = request.POST.get('next', '/')
	return HttpResponseRedirect(next)


'''
NAME
        addPropertyWithAccount

SYNOPSIS

       	addPropertyWithAccount(request)

			Parameters:
				request --> takes in an http request object
					request.user  -->  the user currently logged in, used to pull just the users information
					request.POST --> data filled in by user from form

			Decorators:
				@login_required -->  only requests that have a user are accepted, else brought to login page

DESCRIPTION
			called from Add Property With Account form submission button
			takes POST data from filled out form, checks if valid
			if it is, use Zillow to get Property Valuation
			AssetWithAccountObject.owed is an Account object whose type is either loan or credit
			amount owed displayed is reference to that Accounts balanceAvailable attribute
			create and save AssetWithAccountObject to database


RETURNS
			next = request.POST.get('next', '/')
			HttpResponseRedirect(next)
			redirects to parent page's url to prevent errors when adding multiple properties in the same session

AUTHOR

        Sean O'Neill
'''
@login_required
#this uses the addPropertyForm to create a new Asset Object
def addPropertyWithAccount(request):
	form = addPropertyWithAccountForm(request.user, request.POST or None)
	if request.method == 'POST':
		if form.is_valid():
			try:
	
				propertyAppraisal = zillowRealEstateAppraisal(form.cleaned_data['address'], form.cleaned_data['zipCode'])
				assetProperty = AssetWithAccountObject() 
				assetProperty.initialize(request.user, propertyAppraisal[1], propertyAppraisal[0], Account.objects.filter(accountID=form.cleaned_data['assetAccount']).first())
				assetProperty.save()

			except Exception as e: 
				print(e)

	next = request.POST.get('next', '/')
	return HttpResponseRedirect(next)


'''
NAME
        addAsset

SYNOPSIS

        addAsset(request)

			Parameters:
				request --> takes in an http request object
					request.user  -->  the user currently logged in, used to pull just the users information
					request.POST --> data filled in by user from form

			Decorators:
				@login_required -->  only requests that have a user are accepted, else brought to login page

DESCRIPTION
			called from add Asset form submission button
			takes POST data from filled out form, checks if valid
			create and save AssetLiabilityObject to database


RETURNS
			next = request.POST.get('next', '/')
			HttpResponseRedirect(next)
			redirects to parent page's url to prevent errors when adding multiple properties in the same session

AUTHOR

        Sean O'Neill
'''
#this uses the addPropertyForm to create a new Asset Object
@login_required
def addAsset(request):
	form = addAssetForm(request.POST or None)
	if request.method == 'POST':
		if form.is_valid():
			try:
				asset = AssetLiabilityObject()
				asset.initialize(request.user, form.cleaned_data['assetLabel'], form.cleaned_data['assetValue'], form.cleaned_data['assetAmountOwed'])

				asset.save()
			except Exception as e: print(e)

	next = request.POST.get('next', '/')
	return HttpResponseRedirect(next)

'''
NAME
        addAssetWithAccount

SYNOPSIS

        addAssetWithAccount(request)

			Parameters:
				request --> takes in an http request object
					request.user  -->  the user currently logged in, used to pull just the users information
					request.POST --> data filled in by user from form

			Decorators:
				@login_required -->  only requests that have a user are accepted, else brought to login page

DESCRIPTION
			called from Add Asset With Account form submission button
			takes POST data from filled out form, checks if valid
			AssetWithAccountObject.owed is an Account object whose type is either loan or credit, selected in form
			amount owed displayed is reference to that Accounts balanceAvailable attribute
			create and save AssetWithAccountObject to database


RETURNS
			next = request.POST.get('next', '/')
			HttpResponseRedirect(next)
			redirects to parent page's url to prevent errors when adding multiple properties in the same session

AUTHOR

        Sean O'Neill
'''
#this uses the addPropertyForm to create a new Asset Object
@login_required
def addAssetWithAccount(request):
	form = addAssetWithAccountForm(request.user, request.POST or None)
	if request.method == 'POST':
		if form.is_valid():
			try:
				asset = AssetWithAccountObject()
				asset.initialize(request.user, form.cleaned_data['assetLabel'], form.cleaned_data['assetValue'], Account.objects.filter(accountID=form.cleaned_data['assetAccount']).first())
				asset.save()
			except Exception as e: 
				print(e)

	next = request.POST.get('next', '/')
	return HttpResponseRedirect(next)



'''
NAME
        deleteAsset

SYNOPSIS

        deleteAsset(request, assetName)

			Parameters:
				request --> takes in an http request object
					request.user  -->  the user currently logged in, used to pull just the users information
					assetName --> used to find Asset user wishes to delete
			Decorators:
				@login_required -->  only requests that have a user are accepted, else brought to login page

DESCRIPTION
			called from trash can button in Asset Card
			searches database to find an instance of either AssetLiabilityObject or AssetWithAccountObject
			that matches the name of the account, and the user
			deletes it from the the database

RETURNS
			next = request.POST.get('next', '/')
			HttpResponseRedirect(next)
			redirects to parent page's url to prevent errors when adding multiple properties in the same session

AUTHOR

        Sean O'Neill
'''
def deleteAsset(request, assetName):
	tobeDeleted = AssetLiabilityObject.objects.filter(user = request.user, name=assetName).first()
	if tobeDeleted == None:
		tobeDeleted = AssetWithAccountObject.objects.filter(user = request.user, name=assetName).first()
	tobeDeleted.delete()
	next = request.POST.get('next', '/')
	return HttpResponseRedirect(next)

# @login_required
# def robinhoodLogin(request):
# 	form = RobinHoodLoginForm(request.POST or None)
# 	if request.method == 'POST':
# 		if form.is_valid():
# 			try:
# 				robinhoodLogin = r.login(form.cleaned_data['username'], form.cleaned_data['password'])
# 				my_stocks = r.build_holdings()
# 				print(my_stocks)
# 			except Exception as e: print(e)

# 	next = request.POST.get('next', '/')
# 	return HttpResponseRedirect(next)


######################DELETEORIMPLEMENT###########################
def netWorth(request):
	return Account.objects.filter(user=request.user).aggregate(Sum('balanceAvailable')) + AssetLiabilityObject.filter(user=request.user).aggregate(Sum('equity')) + AssetWithAccountObject.filter(user=request.user).aggregate(Sum('equity'))

# Gets the top 5 largest expenses
# Parameter: takes in a Queryset of transactions
# Returns Queryset of Transactions
#
def getLargestExpenses(transactions):
	return transactions.order_by('amount').reverse()[:5]

def updateAccounts(request):
	accounts  = getAccountsFromDB(request)
	for account in accounts:
		create_response = client.Item.public_token.create(account.accessToken)
		public_token = create_response['public_token']
