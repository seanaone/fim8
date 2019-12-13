from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django_mysql.models import JSONField
from django.db.models import Sum
import base64
import os
import datetime
import plaid
import json
import time

setup_json = JSONField(null=True)

#this extends the django user model to include a profile picture
#and store the access tokens of each of the users plaid items
class UserProfile(models.Model): 
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	profilePicture = models.CharField(max_length = 100)
	def __str__(self):  
		return "%s's profile" % self.user
	

class Account(models.Model):
	accessToken = models.CharField(max_length=100)
	itemID = models.CharField(max_length=100)
	accountID = models.CharField(max_length=100)
	balanceAvailable = models.DecimalField(null=True, max_digits=15, decimal_places=2)
	balanceCurrent = models.DecimalField(max_digits=15, decimal_places=2)
	currenctCode = models.CharField(max_length=10, null=True)
	limit = models.DecimalField(null=True, max_digits=15, decimal_places=2)
	mask = models.CharField(max_length=40)
	name = models.CharField(max_length=40)
	officialName = models.CharField(max_length=80, null=True)
	accountSubType = models.CharField(max_length=20)
	accountType = models.CharField(max_length=20)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

#django docs strongly reccomend not rewriting __init__ functions and to instead use a separate function
#initializing data in __init__ function caused Attribute Error
	def initialize(self, accessToken, accountID, itemID, balanceDataPassedIn, limit, mask, name, officialName, accountSubType, accountType, user):
		self.accessToken = accessToken
		self.itemID = itemID
		self.accountID = accountID
		balanceData = balanceDataPassedIn
		self.balanceAvailable = balanceData['available']
		self.balanceCurrent = balanceData['current']
		self.currenctCode = balanceData['iso_currency_code']
		self.limit = limit
		self.mask = mask
		self.name = name
		self.officialName = officialName
		self.accountSubType = accountSubType
		self.accountType = accountType
		self.user = user

	def __str__(self):
		return f' {self.name} , {self.mask}'
	
	def duplicateCheck(self):
		return f' {self.name} , {self.mask}, {self.officialName}, {self.accountSubType}, {self.accountType}'



class Transaction(models.Model):
	name = models.CharField(max_length = 100)
	amount = models.DecimalField(max_digits=15, decimal_places=2)
	datePosted = models.CharField(max_length = 100)
	categoryTop = models.CharField(max_length = 100, null = True)
	categoryMiddle = models.CharField(max_length = 100, null = True)
	categoryBottom = models.CharField(max_length = 100, null = True)
	Account = models.ForeignKey(Account, on_delete=models.CASCADE, null = True)
	# User = models.ForeignKey(User, on_delete=models.CASCADE)
#django docs strongly reccomend not rewriting __init__ functions and to instead use a separate function
#initializing data in __init__ function caused Attribute Error
	def initialize(self, name, amount, date, account_id, category):
		self.name = name
		self.amount = amount
		self.datePosted = date
		self.Account = Account.objects.get(accountID = account_id)
		#transactions given by the api have varying levels of detail when it comes to their category
		#anywhere from 1-3 tiers of detail, if only one, that is a top level category
		categoriesList = category
		if len(categoriesList) == 3:
			self.categoryTop = categoriesList[0]
			self.categoryMiddle = categoriesList[1]
			self.categoryBottom = categoriesList[2]
		elif len(categoriesList) == 2:
			self.categoryTop = categoriesList[0]
			self.categoryMiddle = categoriesList[1]
		elif len(categoriesList) == 1:
			self.categoryTop = categoriesList[0]

	# this returns the name, amount and date
	def __str__(self):
		return f'{self.name}, {self.amount}, {self.datePosted}'


class AssetLiabilityObject(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length = 100)
	value = models.DecimalField(max_digits=15, decimal_places=2)
	owed = models.DecimalField(null=True, max_digits=15, decimal_places=2)
	equity = models.DecimalField(max_digits=15, decimal_places=2)
	
	def initialize(self, user, name, value, owed):
		self.user = user
		self.name = name
		self.value = value
		self.owed = owed
		self.equity = value - owed
	def __str__(self):
		return f' {self.name} , {self.value}, {self.owed}'


class AssetWithAccountObject(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length = 100)
	value = models.DecimalField(max_digits=15, decimal_places=2)
	owed = models.ForeignKey(Account, on_delete=models.CASCADE)
	equity = models.DecimalField(max_digits=15, decimal_places=2)


	def initialize(self, user, name, value, account):
		self.user = user
		self.name = name
		self.value = value
		self.owed = account
		self.equity = self.value - self.owed.balanceCurrent

	def __str__(self):
		return f' {self.name} , {self.value}, {self.owed.balanceCurrent}'

