from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import authenticate, login, logout
from ecomapp.models import Contactenquiry, Cart, Order, Orderhistory
from django.contrib.auth.models import User
from django.db.models import Q
import random
import razorpay
from django.core.mail import send_mail


# Create your views here.
def product(request):
    p = product.objects.filter(is_active=True)
    #print(p)
    context ={}
    context['data'] = p
    return render(request,'index.html', context)

def user_login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    else:
        n = request.POST['uname']
        p = request.POST['upass']
        #print(n)
        #print(p)
        u = authenticate(username=n, password=p)
        #print(u)
        if u is not None:
            login(request, u)
            return redirect('/product')
        else:
            context = {}
            context['errmsg'] = 'Invalid Username and Password '
            return render(request, 'login.html', context)

def user_logout(request):
    logout(request)
    return redirect('/login')


def search(request):
    query = request.GET['query']
    #print(query)
    pname = 'Product'.Objects.filter(name__icontains=query)
    pcat = 'Product'.Objects.filter(cat__icontains=query)
    pdetail = 'Product'.Objects.filter(pdetail__icontains=query)

    allprod = pname.union(pcat , pdetail)
    context = {}

    if allprod.count() == 0:
        context['errmsg'] = 'Dog not FOUND'

        context['date'] = allprod
        return render(request, 'index.html', context)


def landing(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        se = Contactenquiry(name=name, email=email, message=message)
        se.save()
    return render(request, 'index.html')


def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        context = {}
        n = request.POST['uname']
        p = request.POST['upass']
        cp = request.POST['cp']

        if n == '' or p == '' or cp == '':
            context['errmsg'] = 'Field can not be NULL'
            return render(request, 'register.html', context)
        elif len(p) < 8:
            context['errmsg'] = 'Password must be at least 8 characters'
            return render(request, 'register.html', context)
        elif p != cp:
            context['errmsg'] = 'passwords and confirm password must be same'
            return render(request, 'register.html', context)

        else:
            try:
                u = User.objects.create(Username=n, email=n)
                u.set_password(p)
                u.save()
                context['success'] = 'User Created Successfully '
                return render(request, 'register.html', context)
            except Exception:
                context['errmsg'] = 'User already exists,please login..',
                return render(request, 'register.html', context)


def Orderhistory(request):
    return render(request, 'orderhistory.html')


def productdetails(request, pid):
    p = product.objects.filter(id=pid)
    context = {}
    context['data'] = p
    return render(request, 'product_detail.html', context)


def addtocart(request, pid):
    if request.user.is_autheticated:
        context = {}
        u = User.objects.filter(id=request.user.id)
        p = product.objects.filter(id=pid)
        # check product id exists or not
        q1 = Q(uid=u[0])
        q2 = Q(pid=p[0])
        c = Cart.objects.filter(q1 & q2)
        n = len(c)
        context['data'] = p
        if n == 1:
            context['errmsg'] = "Pet Already Exist"
            return render(request, 'product_detail.html', context)
        else:
            c = Cart.objects.create(uid=u[0])
            c.save()
            context['msg'] = "Pet added sucessfully in the cart"
            return render(request, 'product_details', context)
            # return HttpResponse('product added to cart')

    else:
        return redirect('/login')


def viewcart(request):
    c = Cart.objects.filter(uid=request.user.id)
    # print(c)
    context = {}
    context['data'] = c
    sum = 0
    for x in c:
        sum = sum + x.pid.price * x.qty

    context['total'] = sum
    context['n'] = len(c)

    return render(request, 'cart.html', context)


def pricefilter(request):
    min = request.GET['min']
    max = request.GET['max']
    # print(min)
    # print(max)

    q1 = Q(price__gte=min)
    q2 = Q(price__lte=max)

    p = product.objects.filter(q1 & q2)
    context = {}
    context['data'] = p
    return render(request, 'index.html', context)


def catfilter(request, cv):
    q1 = Q(is_active=True)
    q2 = Q(cat=cv)
    p = product.objects.filter(q1 & q2)
    context = {}
    context['data'] = p
    return render(request, 'index.html', context)


def sortbyprice(request, sv):
    if sv == '1':
        p = product.objects.order_by("price")
    else:
        p = product.object.order_by("price")
        context = {}
        context['data'] = p
        return render(request, 'index.html', context)


def updateqty(request, x, cid):
    c = Cart.objects.filter(id=cid)
    q = c[0].qty
    # print(type(x))
    if x == "1":
        q = q + 1
    elif q > 1:
        q = q - 1

    c.update(qty=q)
    return redirect('/viewcart')


def remove(request, cid):
    c = Cart.objects.filter(id=cid)
    c.delete()
    return redirect('/viewcart')


def placeorder(request):
    c = Cart.objects.filter(uid=request.user.id)
    orderid = random.randrange(1000, 9999)
    for x in c:
        amount = x.qty * x.pid.price
        o = Order.objects.create(orderid=orderid, pid=x.pid, uid=x.uid, amount=amount)
        o.save()

        x.delete()
        return redirect('/fetchorder')


def fetchorder(request):
    o = Order.objects.filter(uid=request.user.id)
    context = {'data': o}
    sum = 0
    for x in o:
        sum = sum + x.amt
    context['total'] = sum
    context['n'] = len(o)

    orders_to_delete = list(o)

    for order in orders_to_delete:
        Orderhistory.objects.create(order=order, payment_status='successful')

    return render(request, 'placeorder.html', context)


def paymentsuccess(request):
    sub = 'SAM DOG Shop Order Status'
    msg = 'Thanks For Buying....!!!'
    frm = 'sanjana2022@gmail.com'
    u = User.objects.filter(id=request.user.id)
    to = u[0].email
    send_mail(
        sub,
        msg,
        frm,
        [to],

        fail_silently=False
    )
    return redirect(request, 'paymentsuccess.html')


def makepayment(request):
    client = razorpay.Client(auth=("", ""))

    o = Order.objects.filter(uid=request.user.id)
    sum = 0
    for x in o:
        sum = sum + x.amt
        oid = x.orderid

    data = {"amount": sum * 100, "currency": "INR", "receipt": "oid"}
    payment = client.order.create(data=data)
    # print(payment)
    context = {}
    context['payment'] = payment
    return render(request, 'pay.html', context)






















