from django.urls import path
from . import views

urlpatterns = [
    path('get_transactions', views.getTransactions ,name = 'getTransactions'),
    path('get_accounts', views.getAccounts ,name = 'getAccounts'),
    path('get_transactions_from_db', views.getTransactionsFromDB ,name = 'getTransactionsFromDB'),
    path('get_accounts_from_db', views.getAccountsFromDB ,name = 'getAccountsFromDB'),
    path('get_assets_from_db', views.getAssetsFromDB ,name = 'getAssetsFromDB'),
    path('get_access_token', views.getAccessToken ,name = 'getAccessToken'),
    path('accountfocus/(<focusAccountID>\s+)', views.focusOnAccount ,name = 'focusOnAccount'),
    path('add_property_with_account', views.addPropertyWithAccount, name = 'addPropertyWithAccount'),
    path('add_property', views.addProperty, name = 'addProperty'),
    path('add_asset_with_account', views.addAssetWithAccount, name = 'addAssetWithAccount'),
    path('add_asset', views.addAsset, name = 'addAsset'),
    path('delete_asset/(<assetName>\s+)', views.deleteAsset, name='deleteAsset'),
    # path('robinhood_login', views.robinhoodLogin, name='robinhoodLogin'),
    path('', views.home, name='dashboard-home'),
]
