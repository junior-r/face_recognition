import os
import cv2
from matplotlib import pyplot
import imutils
from mtcnn.mtcnn import MTCNN
import time
import sqlite3


count = 0
name_employees = []

connect = sqlite3.connect('Companies.sqlite3')
cursor = connect.cursor()

query = f'''
    CREATE TABLE IF NOT EXISTS Companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        password TEXT
    )
'''
cursor.execute(query)

query = f'''
    CREATE TABLE IF NOT EXISTS Employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        tel TEXT,
        company_id INTEGER,
        FOREIGN KEY (company_id) REFERENCES Companies (id)
    )
'''
cursor.execute(query)


def login():
    '''
        Function to log in to a company.
        If the company name and company password are correct, it returns a menu that gives you the data pulled from the database.
        Else create a company with the data provided.
    '''
    company_name = str(input("Nombre de la empresa: "))
    company_password = str(input("Contraseña: "))

    query = f'SELECT * FROM Companies WHERE name = "{company_name}"'
    cursor.execute(query)
    get_data = cursor.fetchall()
    if get_data:
        if get_data[0][2] == company_password:
            menu(get_data)
        else:
            print('Contraseña incorrecta. Intente de nuevo.')
            login()
    else:
        create_company(company_name, company_password)


def menu(get_data):
    '''
        Menu function that presents different options.

        params: get_data "The Company data extracted from the database."
    '''
    print(
        '1 - Listar empleados, 2 - Crear empleado, 3 - Editar empleado, 4 - Borrar empleado, 5 - Registrar fotos a un empleado , 6 - Salir')
    opt = input('¿Qué desea hacer?: ')

    match opt:
        case 1 | '1':
            list_employees(company_data=get_data)
        case 2 | '2':
            number_employees = int(input('Número de empleados: '))
            create_employee(company_data=get_data, number_employees=number_employees)
        case 3 | '3':
            edit_employee(company_data=get_data)
        case 4 | '4':
            delete_employee(company_data=get_data)
        case 5 | '5':
            create_carpets(company_data=get_data)
        case 6 | '6':
            return ''
        case _:
            print('Opción inválida intente de nuevo!')
            menu(get_data)


def create_company(company_name, company_password):
    '''
        Function to create a company in case it don´t exists in the database.

        params: company_name "A name for the company provided by the User."
        params: company_password "A password for the company provided by the User."
    '''
    password = str(input('Confirme su contraseña: '))
    if company_password == password:
        try:
            query = f'INSERT INTO Companies VALUES (NULL, "{company_name}", "{company_password}")'
            cursor.execute(query)
            print('Compañia creada exitosamente!')
        except sqlite3.OperationalError:
            print('Ya existe')
    else:
        print('Las contraseñas no coinciden. Intente de nuevo.')
        create_company(company_name, company_password)


def create_employee(company_data, number_employees):
    '''
        Function to create an employee.

        params: company_data "The company data, to assign to their respective employees."
        params: number_of_employees "number of times will execute this function."

        return: Back to the menu options.
    '''
    global count

    while count < number_employees:
        count += 1
        name_employee = input(f'Nombre y apellido del empleado #{count}: ')
        phone_employee = str(input(f'Número de telefono del empleado #{count}: '))
        print()

        query = f'SELECT * FROM Employees WHERE name = "{name_employee}"'
        cursor.execute(query)
        if cursor.fetchall():
            if name_employees:
                for emp in name_employees:
                    if name_employee in emp:
                        print('Empleado ya existe!', end='\n')
                        count -= 1
            else:
                print('Empleado ya existe!', end='\n')
                count -= 1
        else:
            name_employees.append((name_employee, phone_employee, company_data[0][0]))

            query = f'INSERT INTO Employees VALUES (NULL, "{name_employee}", "{phone_employee}", "{company_data[0][0]}")'
            try:
                cursor.execute(query)
                print('Empleado registrado', end='\n')
            except sqlite3.OperationalError as e:
                print(f'ERROR: {e}')

    return menu(get_data=company_data)


def list_employees(company_data):
    '''
        Function to display all employees by the current company.

        params: company_data "The company data, to list their respective employees."

        return: Back to the menu options.
    '''
    print('Lista de empleados', end='\n')
    get_data = mechanism_list_employees(company_data)

    return menu(get_data=company_data)


def mechanism_list_employees(company_data):
    '''
        This function provides a list of all employees in the current company.

        params: company_data "The company data, to find their respective employees."

        return: list with all employees found.
    '''
    query = f'SELECT * FROM Employees WHERE company_id = "{company_data[0][0]}"'
    cursor.execute(query)
    get_data = cursor.fetchall()
    if get_data:
        print('ID | Nombre | Teléfono', end='\n')
        for data in get_data:
            print(f'{data[0]} | {data[1]} | {data[2]}')
            print('-' * 50)
        return get_data
    else:
        print('No tiene empleados registrados')
        return None


def edit_employee(company_data):
    get_data = mechanism_list_employees(company_data)
    print()
    if get_data is not None:
        print('Editar empleado', end='\n')
        id = int(input('Seleccione un empleado por su ID: '))
        query = f'SELECT * FROM Employees WHERE id = "{id}"'
        cursor.execute(query)
        employee = cursor.fetchall()
        if employee:
            print('name | tel', end='\n')

            field = input('Seleccione un campo a editar: ').lower()
            new_value = str(input('Escriba el nuevo valor: '))
            if new_value:
                query = f'UPDATE Employees SET "{field}" = "{new_value}" WHERE id = "{employee[0][0]}"'
                cursor.execute(query)
                print('Actualizado éxitosamente')
                list_employees(company_data)
            else:
                print('Valor inválido.')
                edit_employee(company_data)
        else:
            print('No se encontró el empleado. Intente de nuevo.')
            edit_employee(company_data)


def delete_employee(company_data):
    print()
    print('Borrar empleado\n')
    get_data = mechanism_list_employees(company_data)
    if get_data is not None:
        id = int(input('Seleccione un empleado por medio de su ID: '))
        if id:
            confirm = str(input('Escriba su contraseña por seguridad: '))

            if company_data[0][2] == confirm:
                query = f'DELETE FROM Employees WHERE id = {id} AND company_id = {company_data[0][0]}'
                cursor.execute(query)
                print('Usuario eliminado exitosamente.')
                list_employees(company_data)
            else:
                print('Contraseña incorrecta. Intente de nuevo.')
                delete_employee(company_data)
        else:
            print('No se encontró ese empleado. Intente de nuevo.')
            delete_employee(company_data)


def create_carpets(company_data):
    '''
        This function creates all the necessary directories for employees.

        params: company_data "The company data, to find their respective employees."
    '''
    carpet = f'C:/Users/USER/OneDrive/Escritorio/Proyectos/Deteccion facial/{company_data[0][1]}/People'
    if not os.path.exists(carpet):
        os.makedirs(carpet)
    query = f'SELECT * FROM Employees WHERE company_id = {company_data[0][0]}'
    cursor.execute(query)
    employees = cursor.fetchall()
    if employees:
        for employee in employees:
            if not os.path.exists(carpet + '/' + f'{employee[1]}'):
                os.makedirs(carpet + '/' + f'{employee[1]}')
            if not os.path.exists(carpet + '/' + f'{employee[1]}' + '/' + 'Photos'):
                os.makedirs(carpet + '/' + f'{employee[1]}' + '/' + 'Photos')
            if not os.path.exists(carpet + '/' + f'{employee[1]}' + '/' + 'Photos' + '/' + 'Profile'):
                os.makedirs(carpet + '/' + f'{employee[1]}' + '/' + 'Photos' + '/' + 'Profile')
            if not os.path.exists(carpet + '/' + f'{employee[1]}' + '/' + 'Photos' + '/' + 'p'):
                os.makedirs(carpet + '/' + f'{employee[1]}' + '/' + 'Photos' + '/' + 'p')
            if not os.path.exists(carpet + '/' + f'{employee[1]}' + '/' + 'Photos' + '/' + 'n'):
                os.makedirs(carpet + '/' + f'{employee[1]}' + '/' + 'Photos' + '/' + 'n')
        print('Carpetas creadas con éxito!')

    choose_carpet(company_data, carpet)


def choose_carpet(company_data, carpet):
    '''
        This function presents options for registering different types of images.

        params: company_data "The company data, to find their respective employees."
        params: carpet "This will be the path to save all the images."
    '''
    global emp
    counter = 0
    employees = os.listdir(carpet)
    # --------- Select Employee
    for employee in employees: print(employee)
    choose_employee = int(input('Elige un empleado por su número: '))

    try:
        emp = employees[choose_employee - 1]

        # Select Photo Carpet
        photo_options = os.listdir(carpet + '/' + emp + '/Photos')
        for opt in photo_options:
            counter += 1
            print(f'{counter} - {opt}', end=', ')
        choose_carpet_photo = int(input(f'¿Qúe tipo de foto desea registrar para {emp}?: '))
        photo_carpet = photo_options[choose_carpet_photo - 1]

        print(f'Usted eligió {emp} -> {photo_carpet}')
        carpet += f'/{emp}/Photos/{photo_carpet}'
        if photo_carpet == 'Profile':
            save_image_profile(carpet, emp)
        else:
            save_images(carpet, emp)
    except Exception as e:
        print(f'ERROR: {e}')
        choose_carpet(company_data, carpet)


def save_images(carpet, emp):
    '''
        This function save positive or negative images, depending on the "carpet" param.

        param: carpet "This will be the path to save 300 positive or negative images."
        param: emp -> employee "Determines the employee to which all images will be assigned."
    '''
    print('----------------------------------------------------------------------')
    print('Preparese para tomar 300 fotos que servirán para entrenar al programa.')
    print(f'Se almacenarán en {carpet}')
    print('Las imágenes se empezarán a tomar 10 segundos después de este mensaje')
    time.sleep(10)

    cap = cv2.VideoCapture(0)
    x1, y1 = 190, 80
    x2, y2 = 450, 398
    counter = 0

    while True:
        ret, frame = cap.read()
        if not ret: break
        img_aux = frame.copy()
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

        face = img_aux[y1:y2, x1:x2]
        face = imutils.resize(face, width=38)

        k = cv2.waitKey(1)
        if k == 27 or counter >= 300:
            break

        # Save Images
        counter += 1
        img_route = f'/face_{counter}.jpg'
        cv2.imwrite(carpet + img_route, face)
        print(f'Imágen alamacenada en: {carpet + img_route}')

        cv2.imshow('frame', frame)
        cv2.imshow('face', face)

    cap.release()
    cv2.destroyAllWindows()


def save_image_profile(carpet, emp):
    '''
        This function save profile images, depending on the "carpet" param.

        param: carpet "This will be the path to save 300 profile images."
        param: emp -> employee "Determines the employee to which all images will be assigned."
    '''
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
    counter = 0

    while True:
        ret, frame = cap.read()
        if not ret: break

        frame = imutils.resize(frame, width=640)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        auxFrame = frame.copy()
        faces = faceClassif.detectMultiScale(gray, 1.3, 5)
        img_route = f'/{emp}_{counter}.jpg'

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            rostro = auxFrame[y:y + h, x:x + w]
            rostro = cv2.resize(rostro, (150, 150), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(carpet + img_route, rostro)
            counter += 1
        cv2.imshow('frame', frame)
        print(f'Imágen alamacenada en: {carpet + img_route}')

        img_aux = frame.copy()
        # cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

        # face = img_aux[y1:y2, x1:x2]
        # face = imutils.resize(face, width=150, height=150)

        k = cv2.waitKey(1)
        if k == 27 or counter >= 300:
            break

        # cv2.imshow('frame', frame)
        # cv2.imshow('face', face)

    cap.release()
    cv2.destroyAllWindows()


login()


connect.commit()
connect.close()
