from django.shortcuts import render
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.template.defaultfilters import date
from django.conf import settings
from django.db.models import Sum
from dashboard.models import Account, User, Transaction
from budget.models import Budget, CategoryLimitandSpent, Goal
from crispy_forms.utils import render_crispy_form
from django.template.context_processors import csrf
import requests
#needed to serialize decimals to json 
import simplejson as json
import decimal
from django.core import serializers
import datetime
from .forms import newBudgetForm, addCategoryForm, editCategoryForm, goalForm, editGoalForm


'''
NAME
        budget

SYNOPSIS

        budget(request)

			Parameters:
				request --> takes in an http request object
					request.user  -->  the user currently logged in, used to pull just the users information
			Decorators:
				@login_required -->  only requests that have a user are accepted, else brought to login page

DESCRIPTION

		This function renders the budget page of the application.
		it assembles the data required for the current spending/income pie chart,
		and the data needed to display the budget cards.
		It passes the chart data, budget data, and associated forms to the budget home template

RETURNS
		return render(request, 'budget/home.html', context)
		returns the html budget home page rendered with all of the users budget catagories,
		as well as the current spending chart.
		this data is stored in a dictionary called context, which can be manipualted and accesses using
		the jinja templating engine directly in the html file.
AUTHOR

        Sean O'Neill
'''
@login_required
def budget(request):
	today = datetime.datetime.now()
	thisMonth = today.strftime('%Y-%m')
	#for test data demo purposes it is best if the app believes it is September
	thisMonth = '2019-09'
	print(thisMonth)

	#getPieChartOuterRingData() returns a list of tuples, thd first element in the tuple being the category,
	#the second being its amount
	outerRingData =  getPieChartOuterRingData(request, 'categoryTop', thisMonth)
	#zip() takes this list of tuples and divides them into two separate tuples, a category tuple and an amount tuple
	outerRingCategories, outerRingAmounts = zip(*outerRingData)
	transactions = Transaction.objects.filter(Account__user = request.user, categoryTop__in=outerRingCategories, datePosted__contains=thisMonth).order_by('categoryTop')
	print(transactions)
	transactions = serializers.serialize('json', transactions)

	#in order for these to be used in chart.js they need to be made readable by javascript
	outerRingCategories = json.dumps(outerRingCategories)
	
	outerRingAmounts = json.dumps(outerRingAmounts)
	#same process for data given by getPieChartInnerRingData()
	innerRingData = getPieChartInnerRingData(request, 'categoryTop', thisMonth)
	
	innerRingCategories, innerRingAmounts = zip(*innerRingData)

	innerRingCategories = json.dumps(innerRingCategories)
	#income is given by plaid as a negative number amount in transactions
	#tuples are immutable, convert to list and take absolute value of each amount
	innerRingAmounts = list(innerRingAmounts)
	lengthOfInnerRingAmountsList = len(innerRingAmounts)
	for index in range(lengthOfInnerRingAmountsList):
		innerRingAmounts[index] = abs(innerRingAmounts[index])
	totalIncome  = sum(innerRingAmounts)
	innerRingAmounts = json.dumps(innerRingAmounts)
	userHasBudget = Budget.objects.filter(user = request.user).exists()
	context = {
		'outerRingCategories': outerRingCategories,
		'outerRingAmounts': outerRingAmounts,
		'innerRingCategories': innerRingCategories,
		'innerRingAmounts': innerRingAmounts,
		'transactions': transactions,
		'userHasBudget' : userHasBudget,
		'new_budget_form': newBudgetForm,
		'add_category': addCategoryForm,
		'edit_category_form': editCategoryForm,
		'goal_form': goalForm(request.user),
		'edit_goal_form': editGoalForm,
		'totalIncome': totalIncome,

	}
	#if the user has a budget load the catagories in to be displayed
	if userHasBudget:
		budgetCategories = CategoryLimitandSpent.objects.filter(budget = request.user.budget)
		goals = Goal.objects.filter(budget = request.user.budget)
		for category in budgetCategories:
			#transactions must belong to the user, be of the same category, and have taken place this month
			#sums all the amounts
			category.spent = Transaction.objects.filter(Account__user = request.user, categoryTop=category.category, datePosted__contains=thisMonth).aggregate(Sum('amount'))['amount__sum']
			category.transactions = Transaction.objects.filter(Account__user=request.user, amount__gte=0, datePosted__contains=thisMonth, categoryTop=category.category)
		context['budgetCategories'] = budgetCategories
		context['goals'] = 	goals
	return render(request, 'budget/home.html', context)


'''
NAME
        saveBudget

SYNOPSIS

        saveBudget(request)

			Parameters:
				request --> takes in an http request object
					request.user  -->  the user currently logged in, used to pull just the users information
					request.POST --> data filled in by user from form
			Decorators:
				None

DESCRIPTION

			called from New Budget form submission button
			takes POST data from filled out form, checks if valid
			if it is, create and save userBudget object to database
			creates and save createBudgetCategory objects for a preset set of categories

RETURNS
			
		next = request.POST.get('next', '/budget')
		return HttpResponseRedirect(next)
		redirects to parent page's url to prevent errors
		rendered page will reflect changes submitted
AUTHOR

        Sean O'Neill
'''
#this uses the new budget form to create a Budget Object
#creates standard budget categories
def saveBudget(request):
	form = newBudgetForm(request.POST or None)
	if request.method == 'POST':
		if form.is_valid():

			if Budget.objects.filter(user = request.user).exists():
				tobeReplaced = Budget.objects.filter(user = request.user).first()
				tobeReplaced.delete()
			usersBudget = Budget()
			usersBudget.initialize(request.user, form.cleaned_data['income'], 0)
			usersBudget.save()
		#CREATE CATEGORIES FOR ALL CATEGORY FIELDS IN THE FORM
		createBudgetCategory(usersBudget, "income", form.cleaned_data['income'])
		createBudgetCategory(usersBudget, "food and drink", form.cleaned_data['foodAndDrink'])
		createBudgetCategory(usersBudget, "shops", form.cleaned_data['shops'])
		createBudgetCategory(usersBudget, "travel", form.cleaned_data['travel'])
		createBudgetCategory(usersBudget, "recreation", form.cleaned_data['recreation'])

	#this routes back to the budget home page without the functions path in the url
	#preventing errors when multiple functions are called in the same page session
	next = request.POST.get('next', '/budget')
	return HttpResponseRedirect(next)


'''
NAME
        createBudgetCategory

SYNOPSIS

        createBudgetCategory(usersBudget, label, limit)

			Parameters:
				usersBudget --> Budget Object the BudgetCategory will be associated with
				label  -->  name of the budget category, will also be used to filter transactions on
				limit --> amount the user is willing to spend on the category
			Decorators:
				None

DESCRIPTION

		creates, intializes and saves a budgetCategory object to the database

RETURNS
			
		return void
AUTHOR

        Sean O'Neill
'''
#this uses the addCategoryForm to create a new budgetCategory Object
def createBudgetCategory(usersBudget, label, limit):
	budgetCategory = CategoryLimitandSpent()
	budgetCategory.initialize(usersBudget, label, limit, 0)
	budgetCategory.save()


'''
NAME
        addToBudget

SYNOPSIS

        addToBudget(request)

			Parameters:
				request --> takes in an http request object
					request.user  -->  the user currently logged in, used to pull just the users information
					request.POST --> data filled in by user from form
			Decorators:
				None

DESCRIPTION

		finds the users Budget object and calls the createBudgetCategory() to 

RETURNS
			
		next = request.POST.get('next', '/budget')
		return HttpResponseRedirect(next)
		redirects to parent page's url to prevent errors
		rendered page will reflect changes submitted

AUTHOR

        Sean O'Neill
'''
#this uses the addCategoryForm to create a new budgetCategory Object
def addToBudget(request):
	form = addCategoryForm(request.POST or None)
	if request.method == 'POST':
		if form.is_valid():
			usersBudget = Budget.objects.filter(user=request.user).get()
			createBudgetCategory(usersBudget, form.cleaned_data['categoryLabel'], form.cleaned_data['categoryAmount'])
	next = request.POST.get('next', '/budget')
	return HttpResponseRedirect(next)

'''
NAME
        editBudgetCategory

SYNOPSIS

		editBudgetCategory(request, categoryName)

		Parameters:
			request --> takes in an http request object
				request.user  -->  the user currently logged in, used to find only the users CategoryLimitandSpent Objects
				request.POST --> data filled in by user from form
			categoryName --> used to filter through CategoryLimitandSpent Objects
		Decorators:
			None

DESCRIPTION

		 grabs the selected CategoryLimitandSpent Object,
		 alters the limit attribute with the users specified change from the form and
		 saves it to the database.

RETURNS
			
		next = request.POST.get('next', '/budget')
		return HttpResponseRedirect(next)
		redirects to parent page's url to prevent errors
		rendered page will reflect changes submitted
		
AUTHOR

        Sean O'Neill
'''
def editBudgetCategory(request, categoryName):

	form = editCategoryForm(request.POST or None)
	if request.method == 'POST':
		if form.is_valid():
			tobeEdited = CategoryLimitandSpent.objects.filter(budget = request.user.budget, category=categoryName).first()
			print(tobeEdited)
			tobeEdited.limit = form.cleaned_data['categoryAmount']
			tobeEdited.save()
	next = request.POST.get('next', '/budget')
	return HttpResponseRedirect(next)


'''
NAME
        deleteBudgetCategory

SYNOPSIS

		deleteBudgetCategory(request, categoryName)

		Parameters:
			request --> takes in an http request object
				request.user  -->  the user currently logged in, used to find only the users CategoryLimitandSpent Objects
				request.POST --> used to return to parent home page
			categoryName --> used to filter through CategoryLimitandSpent Objects
		Decorators:
			None

DESCRIPTION

		 grabs the selected CategoryLimitandSpent Object and deletes it from the database.

RETURNS
			
		next = request.POST.get('next', '/budget')
		return HttpResponseRedirect(next)
		redirects to parent page's url to prevent errors
		rendered page will reflect changes submitted
		
AUTHOR

        Sean O'Neill
'''
def deleteBudgetCategory(request, categoryName):
	tobeDeleted= CategoryLimitandSpent.objects.filter(budget = request.user.budget, category=categoryName).first()
	tobeDeleted.delete()
	next = request.POST.get('next', '/budget')
	return HttpResponseRedirect(next)



'''
NAME
        deleteGoal

SYNOPSIS

		deleteGoal(request, goalName)

		Parameters:
			request --> takes in an http request object
				request.user  -->  the user currently logged in, used to find only the users CategoryLimitandSpent Objects
				request.POST --> used to return to parent home page
			goalName --> used to filter through Goal Objects
		Decorators:
			None

DESCRIPTION

		 grabs the selected Goal Object and deletes it from the database.

RETURNS
			
		next = request.POST.get('next', '/budget')
		return HttpResponseRedirect(next)
		redirects to parent page's url to prevent errors
		rendered page will reflect changes submitted
		
AUTHOR

        Sean O'Neill
'''
def deleteGoal(request, goalName):
	tobeDeleted= Goal.objects.filter(budget = request.user.budget, nameOfGoal=goalName).first()
	tobeDeleted.delete()
	next = request.POST.get('next', '/budget')
	return HttpResponseRedirect(next)


'''
NAME
        getPieChartOuterRingData

SYNOPSIS

		getPieChartOuterRingData(request, categoryLevel, thisMonth)

		Parameters:
			request --> takes in an http request object
				request.user  -->  the user currently logged in, used to find only the users CategoryLimitandSpent Objects
			categoryLevel --> used to 
			thisMonth -->month and year in "YYYY-MM" format
		Decorators:
			None

DESCRIPTION

		 Querys the database for all of the the transactions associated with any of the users accounts,
		 whose amount is greater than 0 (Plaid makes cost transactions positive and depository transactions negative)
		 and occured within the month and year passed in
		 creates a set of category and aggregated summed amounts of the those category pairs

RETURNS
			
		expenses --> QuerySet of tuples, the first element of the tuple being a categoryTop name,
		the second element being the sum of every transaction that shares that name
		if there are none, a Query set of a tuple is [('No Monthly Expenses', 0)] is returned
AUTHOR

        Sean O'Neill
'''
def getPieChartOuterRingData(request, categoryLevel, thisMonth):
	expenses = Transaction.objects.filter(Account__user=request.user, amount__gte=0, datePosted__contains=thisMonth).values_list(categoryLevel).order_by(categoryLevel).annotate(total_price=Sum('amount'))
	if not expenses:
		expenses = [('No Monthly Expenses', 0)]
	return expenses

'''
NAME
        getPieChartInnerRingData
		
SYNOPSIS

		getPieChartInnerRingData(request, categoryLevel, thisMonth)

		Parameters:
			request --> takes in an http request object
				request.user  -->  the user currently logged in, used to find only the users CategoryLimitandSpent Objects
			categoryLevel --> used to 
			thisMonth -->month and year in "YYYY-MM" format
		Decorators:
			None

DESCRIPTION

		 Querys the database for all of the the transactions associated with any of the users accounts,
		 whose amount is less than 0 (Plaid makes cost transactions positive and depository transactions negative)
		 and occured within the month and year passed in
		 creates a set of category and aggregated summed amounts of the those category pairs

RETURNS
			
		income --> QuerySet of tuples, the first element of the tuple being a categoryTop name,
		the second element being the sum of every transaction that shares that name
		if there are none, a Query set of a tuple is [('No Monthly Income', 0)] is returned
AUTHOR

        Sean O'Neill
'''
def getPieChartInnerRingData(request, categoryLevel, thisMonth):
	income = Transaction.objects.filter(Account__user=request.user, amount__lte=0, datePosted__contains=thisMonth).values_list(categoryLevel).order_by(categoryLevel).annotate(total_price=Sum('amount'))
	if not income:
		income = [('No Monthly Income', 0)]
	return income







#skeleton
#will return a dict of positive and negative cashflows for the month
def getCurrentCashFlow(positive, negative):

	# positive = Transaction.objects.filter(User = currentUser).filter.amount__gte(0).aggregate(Sum('amount'))
	# #sums all of the transactions that belong to the user less than $0 by their amounts
	# negative = Transaction.objects.filter(User = currentUser).filter.amount__lte(0).aggregate(Sum('amount'))
	# #adds them together to get total cash flow
	total = positive + negative
	dictOfFlows = {'positive': positive, 'negative': negative, 'totalCashFlow': total}
	return dictOfFlows



#this uses the addGoal to create a new Goal Object
def addGoal(request):
	form = goalForm(request.user, request.POST or None)
	if request.method == 'POST':
		if form.is_valid():
			budgetGoal= Goal()
			usersBudget = Budget.objects.filter(user=request.user)[:1].get()
			print(form.cleaned_data['savingOrPayingOff'])
			print(form.cleaned_data['savingOrPayingOff'])
			print(form.cleaned_data['savingOrPayingOff'])
			print(form.cleaned_data['savingOrPayingOff'])
			print(form.cleaned_data['savingOrPayingOff'])
			budgetGoal.initialize(usersBudget, form.cleaned_data['savingOrPayingOff'], form.cleaned_data['goalLabel'], form.cleaned_data['goalAmount'], Account.objects.filter(accountID=form.cleaned_data['goalAccount']).first())
			budgetGoal.save()
	next = request.POST.get('next', '/budget')
	return HttpResponseRedirect(next)


'''
NAME
        editGoal

SYNOPSIS

		editGoal(request, goalName)

		Parameters:
			request --> takes in an http request object
				request.user  -->  the user currently logged in, used to find only the users Goal Objects
				request.POST --> data filled in by user from form
			goalName --> used to filter through Goal Objects
		Decorators:
			None

DESCRIPTION

		 grabs the selected Goal Object,
		 alters the limit attribute with the users specified change from the form and
		 saves it to the database.

RETURNS
			
		next = request.POST.get('next', '/budget')
		return HttpResponseRedirect(next)
		redirects to parent page's url to prevent errors
		rendered page will reflect changes submitted
		
AUTHOR

        Sean O'Neill
'''
def editGoal(request, goalName):

	form = editGoalForm(request.POST or None)
	if request.method == 'POST':
		if form.is_valid():
			tobeEdited = Goal.objects.filter(budget = request.user.budget, nameOfGoal=goalName).first()
			tobeEdited.goalAmount = form.cleaned_data['goalAmount']
			tobeEdited.save()
	next = request.POST.get('next', '/budget')
	return HttpResponseRedirect(next)




def getListOfTransactionsInCategory(request,category):
	listOfRelevantTransactions =  Transaction.objects.filter(Account__user = request.user, categoryTop=category)
	return list(listOfRelevantTransactions)
