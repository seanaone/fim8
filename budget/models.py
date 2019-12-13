from django.db import models
from dashboard.models import Account, User, Transaction

class Budget(models.Model): 
	user = models.OneToOneField(User, on_delete=models.PROTECT)
	expectedMonthlyIncome = models.DecimalField(max_digits=15, decimal_places=2)
	totalMonthlyExpenses = models.DecimalField(max_digits=15, decimal_places=2)
	dateStarted = models.DateField(("Date"), auto_now_add=True)

	def initialize(self, user, expectedMonthlyIncome, totalMonthlyExpenses):
		self.user = user
		self.expectedMonthlyIncome = expectedMonthlyIncome
		self.totalMonthlyExpenses = totalMonthlyExpenses

	def __str__(self):  
		return "%s's Budget" % self.user


class CategoryLimitandSpent(models.Model): 
	budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
	category = models.CharField(max_length=50)
	limit  = models.DecimalField(max_digits=15, decimal_places=2)
	spent = models.DecimalField(max_digits=15, decimal_places=2)

	def initialize(self, budget, category, limit, spent):
		self.budget = budget
		self.category = category
		self.limit = limit
		self.spent = spent

	def __str__(self):  
		return self.category + ' ' + str(self.limit)

class Goal(models.Model): 
	budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
	# ((1, "Saving"), (0, "Paying"))
	savingOrPayingoff = models.CharField(max_length=10)
	nameOfGoal = models.CharField(max_length=50)
	goalAmount = models.DecimalField(max_digits=15, decimal_places=2)
	account = models.ForeignKey(Account, on_delete=models.CASCADE, null = True)


	def initialize(self, budget, savingOrPayingoff, nameOfGoal, goalAmount, account):
		self.budget = budget
		self.savingOrPayingoff = savingOrPayingoff
		self.nameOfGoal = nameOfGoal
		self.goalAmount = goalAmount
		self.account = account

	def __str__(self):  
		return self.nameOfGoal
