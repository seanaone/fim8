from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from budget.models import Goal, CategoryLimitandSpent
from dashboard.forms import getAllAccounts
class newBudgetForm(forms.Form):

    income = forms.DecimalField(
        label = "How much do you expect to make a month?",
        required = True,
    )

    shops = forms.DecimalField(
        label = "How much in retail shopping?",
        required = False,
    )

    foodAndDrink = forms.DecimalField(
        label = "How much in Overall Food and Drink?",
        required = False,
    )


    travel = forms.DecimalField(
        label = "How much in travel expenses?",
        required = False,
    )

    recreation = forms.DecimalField(
        label = "Set a limit on your entertainment spending",
        required = False,
    )

    def __init__(self, *args, **kwargs):
        super(newBudgetForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-newBudgetForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'POST'
        self.helper.form_action = 'save_budget/'
        self.helper.add_input(Submit('submit', 'Submit'))

class addCategoryForm(forms.Form):
 
    categoryLabel = forms.CharField(
        label = "Category",
        required = True,
    )

    categoryAmount = forms.DecimalField(
        label = "How much per month",
        required = True,
    )

    def __init__(self, *args, **kwargs):
        super(addCategoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-categoryForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'POST'
        self.helper.form_action = 'add_to_budget/'
        self.helper.add_input(Submit('submit', 'Submit'))

class editCategoryForm(forms.Form):

    categoryAmount = forms.DecimalField(
        label = "How much per month",
        required = True
    )

    def __init__(self, *args, **kwargs):
        super(editCategoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-categoryForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'POST'
        self.helper.form_action = 'edit_budget_category/'
        self.helper.add_input(Submit('submit', 'Submit'))



class editGoalForm(forms.Form):

    goalAmount = forms.DecimalField(
        label = "How much per month",
        required = True
    )

    def __init__(self, *args, **kwargs):
        super(editGoalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-editGoalForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'POST'
        self.helper.form_action = 'edit_goal/'
        self.helper.add_input(Submit('submit', 'Submit'))


class goalForm(forms.Form):
    
    savingOrPayingOff = forms.TypedChoiceField(
        label = "Are you saving or paying something off?",
        choices = ((1, "Saving"), (0, "Paying")),
        coerce = lambda x: bool(int(x)),
        widget = forms.RadioSelect,
        required = True,
    )

    goalAccount = forms.ChoiceField(
        label = "Which account?",
        required = True,
    )

    
    goalLabel = forms.CharField(
        label = "Name your Goal",
        required = True,
    )

    goalAmount = forms.DecimalField(
        label = "What is the goal amount?",
        required = True,
    )



    def __init__(self, user, *args, **kwargs):
        super(goalForm, self).__init__(*args, **kwargs)
        self.user = user
        #the accounts are retrieved dynamically on form creation
        self.fields['goalAccount'] = forms.ChoiceField(choices=getAllAccounts(self.user) )
        self.helper = FormHelper()
        self.helper.form_id = 'id-categoryForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'save_goal'
        self.helper.add_input(Submit('submit', 'Submit'))