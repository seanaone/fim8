from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from dashboard.models import UserProfile, Account, Transaction, AssetLiabilityObject, AssetWithAccountObject
from budget.models import Budget, CategoryLimitandSpent, Goal
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(AssetLiabilityObject)
admin.site.register(AssetWithAccountObject)
admin.site.register(Budget)
admin.site.register(CategoryLimitandSpent)
admin.site.register(Goal)
# Define an inline admin descriptor for UserProfile model
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'UserProfile'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
