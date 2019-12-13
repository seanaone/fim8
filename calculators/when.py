import math
def interestCalculator(principal, rate, timeInYears):
	rate = rate/100
	interest = math.pow((1 + rate) , timeInYears)	
	total = principal*interest
	return total

def whenCanIRetire(startingPrincipal, expectedAnnualReturn, monthlyContributions, percentageIncreaseInMonthlyContributionsPerYear, annualExpenses):
	numberOfYears = 0
	nestEgg = startingPrincipal
	#based off the 4 percent rule, you can safely live off of 25 times your annual expenses
	requiredNestEgg = annualExpenses*25
	while nestEgg < requiredNestEgg:
		nestEgg = nestEgg + (monthlyContributions*12)
		nestEgg = interestCalculator(nestEgg, expectedAnnualReturn, 1)
		numberOfYears  = numberOfYears + 1
		monthlyContributions = monthlyContributions*(1+(percentageIncreaseInMonthlyContributionsPerYear/100))
		print("monthlyContrib:  ", monthlyContributions)
	print(numberOfYears)
	return numberOfYears

def timeToPayOff(principal, rate, monthlyContributions):
	count = 0
	while principal > 0:
		#monthly compound interval, yearly interest rate
		principal = interestCalculator(principal, rate, (1/12))
		principal = principal - monthlyContributions
		count = count + 1
		print(count, " Months")

print(whenCanIRetire(5000, 8, 500, 2, 40000))