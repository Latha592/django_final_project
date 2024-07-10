from django.urls import path
from ecomapp import views
from django. conf import settings
from django.conf.urls.static import static


urlpatterns=[
    path('product',views.product),
    path('register',views.register),
    path('login',views.login),
    path('logout',views.logout),
    path('cartfilter',views.carfilter),
    path('sort/<sv>',views.sortbyprice),
    path('pricefilter',views.pricefilter),
    path('search',views.search),
    path('productdetails',views.productdetails),
    path('addtocart',views.addtocart),
    path('viewcart',views.viewcart),
    path('updateeqty/<x>/<cid>',views.updateqty),
    path('remove/<cid>',views.remove),
    path('placeorder',views.placeorder),
    path('fetchorder',views.fetchorder),
    path('makepayment',views.makepayment),
    path('paymentsuccess',views.paymentsuccess),
    path('landing',views.landing),
    path('orderhistory',views.orderhistory),

]
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)