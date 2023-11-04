from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.db import connection  # Import the connection object to execute raw SQL queries
from django.http import HttpResponse
from django.utils import timezone 

def admin_login(request):
    if request.method == 'POST':
        admin_id = request.POST.get('admin_id')
        password = request.POST.get('password')

     
        sql_query = """
            SELECT * FROM User_Data
            WHERE emailId = %s AND password_hash = %s AND registering_as = 'Admin'
        """

        with connection.cursor() as cursor:
            cursor.execute(sql_query, [admin_id, password])
            user = cursor.fetchone()

        if user:
           return redirect('admin_portal') 
        else:
            return render(request, 'error.html')

       

    return render(request, 'admin_login.html')


# Create your views here.
def home(request):
    return render(request, 'home.html')

def register(request):
    return render(request, 'register.html')

def admin_portal(request):
    with connection.cursor() as cursor:
        sql_query = "SELECT * FROM User_Data WHERE registering_as = 'specialist';"
        cursor.execute(sql_query)
        data = dictfetchall(cursor)
    context = {
        'specialists': data
    }
    
    return render(request, 'admin_portal.html', context)

def all_patient_list(request):
    with connection.cursor() as cursor:
        sql_query = "SELECT * FROM Reports;"
        cursor.execute(sql_query)
        data = dictfetchall(cursor)
    context = {
        'reports': data
    }
    print(context)
    return render(request, 'all_patient_list.html', context)

def dictfetchall(cursor):
    # Helper function to fetch all rows as dictionaries
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
def register_specialist(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        emailId = request.POST['emailId']
        phone_number = request.POST['phone_number']
        password = request.POST['password_hash']
        password_hash = make_password(password)
        insert_query = "INSERT INTO User_Data (full_name, emailId, phone_number, registering_as, password_hash) VALUES (%s, %s, %s, %s, %s)"
        data = (full_name, emailId, phone_number, 'specialist', password_hash)
        with connection.cursor() as cursor:
            cursor.execute(insert_query, data)
        cursor.close()
        return render(request, 'register_lab_assistant.html')
    else:
        return render(request, 'register_specialist.html')
def register_lab_assistant(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        emailId = request.POST['emailId']
        phone_number = request.POST['phone_number']
        password = request.POST['password_hash']
        password_hash = make_password(password)
        insert_query = "INSERT INTO User_Data (full_name, emailId, phone_number, registering_as, password_hash) VALUES (%s, %s, %s, %s, %s)"
        data = (full_name, emailId, phone_number, 'lab assistant', password_hash)
        with connection.cursor() as cursor:
            cursor.execute(insert_query, data)
        cursor.close()
        return render(request, 'register_lab_assistant.html')
    else:
        return render(request, 'register_lab_assistant.html')

def lab_assistant_list(request):
    with connection.cursor() as cursor:
        sql_query = "SELECT * FROM User_Data WHERE registering_as = 'lab assistant';"
        cursor.execute(sql_query)
        data = dictfetchall(cursor)
    context = {
        'assistants': data
    }
    
    return render(request, 'lab_assistant_list.html', context)

from django.contrib.auth.hashers import check_password

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        usertype = request.POST['usertype']

        # Retrieve the hashed password from the database
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT password_hash,id FROM User_Data WHERE emailId = %s AND registering_as = %s",
                [email, usertype]
            )
            hashed_password = cursor.fetchone()

        if hashed_password and check_password(password, hashed_password[0]):
            if usertype =='specialist':
                context = {
                    'id':hashed_password[1],
                }
                return redirect('specialist_home',id=context['id'])  # Passwords match, user is logged in
            else:
                context = {
                    'id':hashed_password[1],
                }
                return redirect('lab_assistant_home',id=context['id'])
        else:
            return render(request, 'error.html')  # Passwords do not match, show an error

    return render(request, 'login.html')

def specialist_home(request, id):
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        comment = request.POST.get('comment')

        # Define the SQL query to update the specialist comments
        sql_query = """
            UPDATE Reports
            SET specialist_comments = %s
            WHERE report_id = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(sql_query, [comment, report_id])
    # Fetch the reports assigned to the specialist with the given ID
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM Reports WHERE assigned_to_specialist = %s AND specialist_comments = 'Not Prescribed Yet'",
            [id]
        )
        reports = dictfetchall(cursor)

    context = {
        'reports': reports,
        'id':id,
    }

    return render(request, 'specialist_home.html', context)


def lab_assistant_home(request, id):
    if request.method == 'POST':
        patient_id = request.POST['patient_id']
        patient_name = request.POST['patient_name']
        patient_age = request.POST['patient_age']
        patient_gender = request.POST['patient_gender']
        assigned_to_specialist = request.POST['assigned_to_specialist']
        report_data = request.FILES['report_data'].read()
        lab_assistant_id = id  # Get lab_assistant_id from function argument
        added_on_date_time = timezone.now()  # Get the current date and time

        sql_query = """
            INSERT INTO Reports (patient_id, lab_assistant_id, patient_name, patient_age, patient_gender, assigned_to_specialist, report_data, added_on_date_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        with connection.cursor() as cursor:
            cursor.execute(sql_query, [patient_id, lab_assistant_id, patient_name, patient_age, patient_gender, assigned_to_specialist, report_data, added_on_date_time])

        return render(request, 'upload_success.html')
    else:
        with connection.cursor() as cursor:
            sql_query = "SELECT * FROM User_Data WHERE registering_as = 'specialist';"
            cursor.execute(sql_query)
            data = dictfetchall(cursor)
            context = {
                'specialists': data,
                'id':id,
            }

        return render(request, 'lab_assistant_home.html', context)

def upload_success(request):
    return render(request,'upload_success.html')
def show_report(request, report_id):
    # Fetch the report data from the database
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT report_data
            FROM Reports
            WHERE report_id = %s
            """,
            [report_id]
        )
        report_data = cursor.fetchone()

    if report_data:
        # Prepare the HTTP response with the report data
        response = HttpResponse(report_data[0], content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="report-{report_id}.pdf"'
        return response
    else:
        return HttpResponse("Report not found", status=404)
def view_specialist_previous_reports(request, id):
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        comment = request.POST.get('comment')

        # Define the SQL query to update the specialist comments
        sql_query = """
            UPDATE Reports
            SET specialist_comments = %s
            WHERE report_id = %s
        """
        with connection.cursor() as cursor:
           
                cursor.execute(sql_query, [comment, report_id])
                connection.commit()  # Commit the transaction
           

    # Fetch the reports assigned to the specialist with the given ID
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM Reports WHERE assigned_to_specialist = %s AND specialist_comments != 'Not Prescribed Yet'",
            [id]
        )
        reports = dictfetchall(cursor)

    context = {
        'reports': reports,
        'id':id,
    }
    return render(request, 'view_specialist_previous_reports.html', context)

def view_assistant_previous_reports(request, id):
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        
        # Define the SQL query to update the specialist comments
        sql_query = """
            DELETE FROM Reports
            WHERE report_id = %s;
        """
        with connection.cursor() as cursor:
           
                cursor.execute(sql_query, [report_id])
                connection.commit()  # Commit the transaction
           

    # Fetch the reports assigned to the specialist with the given ID
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM Reports WHERE lab_assistant_id = %s",
            [id]
        )
        reports = dictfetchall(cursor)

    context = {
        'reports': reports,
        'id':id,
    }
    return render(request, 'view_assistant_previous_reports.html', context)