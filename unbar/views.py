from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from unbar import connect

def home(request):
	if request.POST:
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return redirect("dashboard")
		else:
			return render(request, 'fragments/error.html', {})
	if request.user.is_authenticated():
		return redirect("dashboard")
	return render(request, 'fragments/login.html', {})


def dashboard(request):
	if not request.user.is_authenticated:
		return redirect('home')
	return render(request, 'fragments/home.html', {})


def logout_view(request):
	logout(request)
	return redirect("home")


def unbar(request):
	if not request.user.is_authenticated:
		return redirect('home')
	if request.POST:
		servicenum = request.POST.get('servicenum')
		status = connect.get_status(servicenum)
		brm = True if status[2] == 'Active' else False
		crm = True if status[6] == 'Unbarred' or status[6] is None else False
		mvne = True if status[5] == 'Active' else False
		cl = status[3]
		dues = status[4]
		so = status[9]
		reason = status[11]
		if so =='Pending':
			status.append('CHECK PENDING SO')
		elif dues >= cl and brm == False and crm == False and mvne == False:
			status.append('SYNC')
		elif dues >= cl and brm == True and crm == False and mvne == False:
			status.append('Testnap BRM BAR CL')
		elif dues >= cl and brm == False and crm == True and mvne == False:
			status.append("BAR CL")
		elif dues >= cl and brm == False and crm == False and mvne == True:
			status.append('Check MVNE')
		elif dues < cl and brm == False and crm == False and mvne == False:
			status.append('UNBAR')
		elif dues < cl and brm == True and crm == False and mvne == False:
			status.append('Testnap BRM Unbar')
		elif dues < cl and brm == True and crm == True  and mvne == False:
			status.append('BAR SL')
		elif dues < cl and brm == True and crm == True and mvne == True:
			status.append('SYNC')

		return render(request, 'fragments/unbar_result.html', {'status':status})
	return render(request, 'fragments/unbar.html', {})


def report(request):
	if not request.user.is_authenticated:
		return redirect('home')
	return render(request, 'fragments/report.html', {})