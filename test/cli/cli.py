import requests

auth_token = None

def storage():
    global auth_token
    headers = {}
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'
        response = requests.get('http://localhost:5000/storage', headers=headers)
        print(response.json())
        
        while(True):
            chose = input('Для скачивания файла необходимо ввести "d",для возврата введите "menu": ')
            if chose == "d":
                id = input('Введите id файла для скачивания: ')
                if int(id) >= len(response.json()):
                    print("Неправильный id")
                    continue
                name = response.json()[str(id)]
                response = requests.get('http://localhost:5000/storage/' + name, headers=headers)
                with open(name, 'wb') as f:
                    f.write(response.content)
                response = requests.get('http://localhost:5000/storage', headers=headers)
            elif chose == "menu":
                break
            else:
                print("Неизвестная команда")
    else:
        print("Необходимо авторизоваться")


def send_file():
    global auth_token
    file_path = input("Введите путь до файла: ")
    file_path = file_path.replace("\\", "/")
    if file_path[0] == '"' and file_path[-1] == '"':
        file_path = file_path[1:-1]
    headers = {}
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'
        with open(file_path, 'rb') as f:
            response = requests.post('http://localhost:5000/', files={'file': f}, headers=headers)
        print(response.text)
    else:
        print("Необходимо авторизоваться")

    
def login():
    global auth_token
    login = input("Введите логин: ")
    password = input("Введите пароль: ")
    data = {
        'login': login,
        'password': password
    }
    response = requests.post('http://localhost:5000/login', json=data)
    
    if response.status_code == 200:
        auth_token = response.json().get('token')
        print('Успешная авторизация')
    else:
        print("Авторизация не удалась")


def register():
    password = 0
    password2 = 1
    while password != password2:
        login = input("Введите логин для создания учетной записи: ")
        password = input("Введите пароль для создания учетной записи: ")
        password2 = input("Повторите пароль для создания учетной записи: ")
        if password != password2:
                print('Пароли не совпадают')
        elif password == '' or login == '':
            print('Логин или пароль не может быть пустым')
        else:
            data = {
                'login': login,
                'password': password,
                'password2': password2
            }
            response = requests.post('http://localhost:5000/register', json=data)
            print(response.text)


print('CLI для взаимодействия с сервером')
while(True):
    choose = input('Введите "r" для регистрации,"a" для авторизации на сервере, "u" для загрузки файла на сервер, "l" для получения списка файлов в хранилище и возможности их скачивания, "exit" для выхода: ')
    if choose == 'r':
        register()
    elif choose == "a":
        login()
    elif choose == "u":
        send_file()
    elif choose == "l":
        storage()
    elif choose == "exit":
        break
    else:
        print("Неизвестная команда")