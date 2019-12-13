from django.shortcuts import render
from django.http import HttpResponse
from dashboard.models import Account
import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from .forms import HowLongTillIPayOffAccountForm, WhenCanIRetireForm, InterestForm
import math
import datetime
import locale
#this is used to format the amounts into local currency
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')



'''
NAME
        whenCanIRetireFormScreen

SYNOPSIS

        whenCanIRetireFormScreen(request)

			Parameters:
				request --> takes in an http request object

			Decorators:
				None

DESCRIPTION

		renders the whenCanIRetireForm page

RETURNS
			
			return render(request, 'calculators/whencanIretireform.html', context)
			html page with retirement calculator form

AUTHOR

        Sean O'Neill
'''
def whenCanIRetireFormScreen(request):
	context =  {
		'when_can_i_retire_form': WhenCanIRetireForm
	}
	return render(request, 'calculators/whencanIretireform.html', context)


'''
NAME

        whenCanIRetireResultScreen

SYNOPSIS

        whenCanIRetireResultScreen(request)

			Parameters:
				request --> takes in an http request object
					request.POST --> data filled out by user
			Decorators:
				None

DESCRIPTION

		validates form passed in, if valid runs the data provided through the retirement calculator
		and stores the returned dictionary in the context dictionary under the key 'breakdown'
		also stores in context and calculates the required nest egg, expected annual return, starting principal,
		annual expenses and number of years until retirement

RETURNS
			
			return render(request, 'calculators/whencanIretireresult.html', context)
			html page with retirement calculator results
AUTHOR

        Sean O'Neill
'''
def whenCanIRetireResultScreen(request):
	form = WhenCanIRetireForm(request.POST or None)
	context = dict()
	if request.method == 'POST':
		if form.is_valid():
			context['breakdown'] =  whenCanIRetire(form.cleaned_data['startingPrincipal'], form.cleaned_data['expectedAnnualReturn'], form.cleaned_data['monthlyContributions'], form.cleaned_data['percentageIncreaseInMonthlyContributionsPerYear'], form.cleaned_data['annualExpenses'])
			if context['breakdown'] == False:
				return render(request, 'calculators/youcannotretire.html', context)
			context['requiredNestEgg'] = locale.currency(form.cleaned_data['annualExpenses']*25, grouping=True)
			context['expectedAnnualReturn'] = form.cleaned_data['expectedAnnualReturn']
			context['startingPrincipal'] = locale.currency(form.cleaned_data['startingPrincipal'], grouping=True) 
			context['annualExpenses'] = locale.currency(form.cleaned_data['annualExpenses'], grouping=True) 
			context['numberOfYears'] = len(context['breakdown'])


		return render(request, 'calculators/whencanIretireresult.html', context)


'''
NAME
        interestFormScreen

SYNOPSIS

        interestFormScreen(request)

			Parameters:
				request --> takes in an http request object

			Decorators:
				None

DESCRIPTION

		renders the whenCanIRetireForm page

RETURNS
			
			return render(request, 'calculators/interestform.html', context)
			html page with retirement calculator form

AUTHOR

        Sean O'Neill
'''
def interestFormScreen(request):
	context =  {
		'interest_form': InterestForm
	}
	return render(request, 'calculators/interestform.html', context)


'''
NAME

        interestResultScreen

SYNOPSIS

        interestResultScreen(request)

			Parameters:
				request --> takes in an http request object
					request.POST --> data filled out by user
			Decorators:
				None

DESCRIPTION

		validates form passed in, if valid runs the data provided through the retirement calculator
		and stores the returned value in the context dictionary under the key 'result'.
		also stores the principal, interest rate, and number of years in context to be displayed by th e html page
RETURNS
			
			return render(request, 'calculators/interestresult.html', context)
			html page with interest calculator results

AUTHOR

        Sean O'Neill
'''
def interestResultScreen(request):
	form = InterestForm(request.POST or None)
	context = dict()
	if request.method == 'POST':
		if form.is_valid():
			context['principal'] = locale.currency(form.cleaned_data['principal'], grouping=True)
			context['rate'] = form.cleaned_data['rate']
			context['years'] = form.cleaned_data['years']
			context['result'] = locale.currency(interestCalculator(form.cleaned_data['principal'], form.cleaned_data['rate'], form.cleaned_data['years']), grouping=True)
		return render(request, 'calculators/interestresult.html', context)


'''
NAME
        timeToPayOffFormScreen

SYNOPSIS

        timeToPayOffFormScreen(request)

			Parameters:
				request --> takes in an http request object

			Decorators:
				None

DESCRIPTION

		renders the timeToPayOffFormScreen page

RETURNS
			
			return render(request, 'calculators/timetopayoffform.html', context)
			html page with time to pay off form

AUTHOR

        Sean O'Neill
'''
def timeToPayOffFormScreen(request):
	context =  {
		'time_to_pay_off_form': HowLongTillIPayOffAccountForm(request.user)
	}
	return render(request, 'calculators/timetopayoffform.html', context)



'''
NAME

        timeToPayOffResultScreen

SYNOPSIS

        timeToPayOffResultScreen(request)

			Parameters:
				request --> takes in an http request object
					request.POST --> data filled out by user
					request.user --> used to find just the users accounts
			Decorators:
				None

DESCRIPTION

		validates form passed in, if valid runs the data provided through the payoff calculator function
		stores the returned dictionary in the context dictionary under the key 'breakdown'.
		also stores the principal, the principal account,  interest rate, how much is paid a month,
		and number of months it will take to pay off in context to be displayed by th e html page
RETURNS
			
			return render(request, 'calculators/interestresult.html', context)
			html page with time to payoff calculator results

AUTHOR

        Sean O'Neill
'''
def timeToPayOffResultScreen(request):
	form = HowLongTillIPayOffAccountForm(request.user, request.POST or None)
	context = dict()
	if request.method == 'POST':
		if form.is_valid():
			principalAccount = Account.objects.filter(user=request.user, accountID=form.cleaned_data['principalAccount']).first()   
			print('prinAcc:')
			print(principalAccount)
			principal = float(principalAccount.balanceCurrent)
			context['breakdown'] =  timeToPayOff(principal, form.cleaned_data['rate'], form.cleaned_data['monthlyContributions'])
			if context['breakdown'] == False:
				return render(request, 'calculators/neverpayoff.html', context)
			context['principalAccount'] = principalAccount.name
			context['principal'] = locale.currency(principal, grouping=True)
			context['rate'] = form.cleaned_data['rate']
			context['monthlyContributions'] = form.cleaned_data['monthlyContributions']
			context['numberOfMonths'] = len(context['breakdown'])
		return render(request, 'calculators/timetopayoffresult.html', context)



'''
NAME

        interestCalculator

SYNOPSIS

        interestCalculator(principal, rate, timeInYears)

			Parameters:
				principal --> initial amount in dollars
				rate --> yearly interest rate
				timeInyears --> number of years over which interest is calculated
			Decorators:
				None

DESCRIPTION

		calculates interest on a principal amount of money
RETURNS
			
			returns the total after the interest is added to the principal

AUTHOR

        Sean O'Neill
'''
def interestCalculator(principal, rate, time):
	rate = rate/100
	interest = math.pow((1 + rate) , time)	
	total = principal*interest
	return total


'''
NAME

        whenCanIRetire

SYNOPSIS

        whenCanIRetire(startingPrincipal, expectedAnnualReturn, monthlyContributions, percentageIncreaseInMonthlyContributionsPerYear, annualExpenses):

			Parameters:
				startingPrincipal --> initial amount already saved for retirement
				expectedAnnualReturn --> yearly return on the principal invested
				monthlyContributions --> how much the user is putting toward retirement a month
				percentageIncreaseInMonthlyContributionsPerYear --> how much the user will increase their monthly contributions over time (ie: getting a raise)
				annualExpenses --> the expected amount needed every year in retirement
			Decorators:
				None

DESCRIPTION

		calculates how much is necessary to retire based on the inputted annual expenses, and how long it will take ot reach that sum based onn
		the starting amount, annual return on investment and monthly contributions.
		The calculations are based off of the 4% rule or Trinity study https://en.wikipedia.org/wiki/Trinity_study,
		where a retiree can safely draw down 4% of the amount they have invested in a diversified portfolio of stocks, or stocks and bonds,
		even though the overall value of the portfolio is subject to short term volatility.
RETURNS
			
			return dictionaryOfYears or False
			dictionaryOfYears --> a dictionary where the key is a year and the value is a dictionary containing the current value of the nest egg, monthly contribution, and
			amount still needed for retirement.  the length of this dictionary is used to determine how long it will take to retire in years.

			if this function returns false, it means that either the  nest egg is not growing, or is not growing sufficiently in order to be able to retire
			within the next 120 years, as that seems far enough as to no longer be a practical lifetime and prevents infinite loops

AUTHOR

        Sean O'Neill
'''
def whenCanIRetire(startingPrincipal, expectedAnnualReturn, monthlyContributions, percentageIncreaseInMonthlyContributionsPerYear, annualExpenses):


	#these variables will be used to for the equation but also to provide the user with a table of each years
	#monthly contributions and nest egg totals
	numberOfYears = 0
	today = datetime.datetime.now()
	thisYear = int(today.strftime('%Y'))
	nestEgg = startingPrincipal
	dictionaryOfYears = dict()
	
	#based off the 4 percent rule, you can safely live off of 25 times your annual expenses
	requiredNestEgg = annualExpenses*25

	while nestEgg < requiredNestEgg:
		nestEgg = nestEgg + (monthlyContributions*12)
		nestEgg = interestCalculator(nestEgg, expectedAnnualReturn, 1)
		numberOfYears  = numberOfYears + 1
		monthlyContributions = monthlyContributions*(1+(percentageIncreaseInMonthlyContributionsPerYear/100))
		stillNeeded = requiredNestEgg-nestEgg
		#this gives an accurate value in the result table
		if stillNeeded < 0:
			stillNeeded = 0
		dictionaryOfYears[str(thisYear)] = {'Nest Egg' : locale.currency(nestEgg, grouping=True), 'Monthly Contribution':locale.currency(monthlyContributions, grouping=True) , 'Still Needed': locale.currency(stillNeeded, grouping=True)}
		thisYear = thisYear+1
		#if the payments aren't making a dent in the principal, will cause an infinite loop
		if nestEgg <= startingPrincipal or numberOfYears > 120:
			return False
		
	return dictionaryOfYears


'''
NAME

        timeToPayOff

SYNOPSIS

        timeToPayOff(amountOwed, rate, monthlyContributions)

			Parameters:
				amountOwed --> initial amount owed in the account
				rate --> how much interest is being charged on the loan
				monthlyContributions --> how much the user is putting toward retirement a month
			Decorators:
				None

DESCRIPTION

		calculates how many months it will take to pay off a users account with a given interest rate and monthly payment schedule

RETURNS
			
		return dictionaryOfMonths or False
			dictionaryOfMonths --> a dictionary where the key is a month and the value is a dictionary containing how much is owed that month and 
			how much has been paid up until that point.  the length of this dictionary is used to determine how long it will take to payoff in months

			if this function returns false, it means that the amount owed is not decreasing.

AUTHOR

        Sean O'Neill
'''
def timeToPayOff(amountOwed, rate, monthlyContributions):
	numberOfMonths = 0
	today = datetime.datetime.now()
	amountPaid = 0
	dictionaryOfMonths = dict()
	startingDebt = amountOwed
	while amountOwed > 0:
		
		#if principal is less than the monthly payment just pay off the principl
		if amountOwed > monthlyContributions:
			amountPaid = amountPaid + monthlyContributions
		else: 
			amountPaid = amountPaid + amountOwed
			amountOwed = 0
		thisMonth = (today + datetime.timedelta(days=30*numberOfMonths)).strftime('%Y-%m')
		dictionaryOfMonths[str(thisMonth)] = {'Amount Owed' : locale.currency(amountOwed, grouping=True), 'Amount Paid':locale.currency(amountPaid, grouping=True)}
		numberOfMonths = numberOfMonths + 1
		#monthly compound interval, yearly interest rate
		amountOwed = interestCalculator(amountOwed, rate, (1/12)) - monthlyContributions
		#if the payments aren't making a dent in the principal, will cause an infinite loop
		if startingDebt <= amountOwed:
			return False
	return dictionaryOfMonths

