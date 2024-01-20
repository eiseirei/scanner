#!/usr/local/bin/python

# Импортируем необходимые библиотеки
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import ast
import os
import json
import requests

# Объявляем функцию для сканирование сети
def ping_sweep(ip_of_host, num_of_host):
    # Проверяем, что использован верный формат для IP-адреса
    try:
        ip_parts = list(map(int, ip_of_host.split(".")))
    except ValueError:
        return(
            f"[#] Результат сканирование: {ip_of_host} [#]\n"
            "Неверный формат IP-адреса\n"
        )
    ip_parts[-1] += num_of_host
    scanned_ip = ".".join(list(map(str,ip_parts[0:len(ip_parts)])))
    # Проверяем не выходит ли адрес за диапазон
    if  all(
            [len(ip_parts) == 4,
             *[0 <= octect <= 255 for octect in ip_parts]]
        ):
        # Если IP-адрес корректный
        response = os.popen(f"ping -c 1 {scanned_ip}")
        res = response.readlines()
        return(
            f"[#] Результат сканирование: {scanned_ip} [#]\n" +
            f"{res[1]}".encode("cp1251").decode("cp866")
        )
    # Если IP-адрес некорректный
    return(
        f"[#] Результат сканирование: {scanned_ip} [#]\n"
        "Неверный IP-адрес\n"
    )

# Объявляем функцию для отправки HTTP запросов
def sent_http_request(target, method, headers=None, payload=None):
    #  Формируем словарь для HTTP-заголовков
    headers_dict = {}
    if headers:
        for header in headers:
            header_name = header.split(":")[0]
            header_value = header.split(":")[1:]
            headers_dict[header_name] = ":".join(header_value)
    # Если пользователь выбрал метод GET
    if method == "GET":
        # Проверяем возможность подключения к ресурсу
        try:
            response = requests.get(target, headers=headers_dict, timeout=10)
        # Если такой ресурс существует, но не отвечает
        except requests.exceptions.Timeout:
            return f"Время ожидания ответа {target} вышло\n"
        # Во всех остальных случаях предполагаем, что пользователь ввёл неверный адрес
        except:
            return f"Неверный адрес ресурса {target}\n"
    # Если пользователь выбрал метод POST
    elif method == "POST":
        # Проверяем возможность подключения к ресурсу
        try:
            response = requests.post(target, headers=headers_dict, data=payload, timeout=10)
        # Если такой ресурс существует, но не отвечает
        except requests.exceptions.Timeout:
            return f"Время ожидания ответа {target} вышло\n"
        # Во всех остальных случаях предполагаем, что пользователь ввёл неверный адрес
        except:
            return f"Неверный адрес ресурса {target}\n"
    # Если пользователь забыл указать метод, то сообщаем ему об этом
    else:
        return f"Не выбран метод GET или POST для ресурса {target}\n"
    # Закрываем подключение, если оно случилось
    response.close()
    # Выводим ответ
    return(
        f"[#] Код ответа: {response.status_code}\n"
        f"[#] Заголовок ответа: {json.dumps(dict(response.headers), indent=4, sort_keys=True)}\n"
        f"[#] Телоо ответа:\n {response.text}\n"
    )

# Объявляем свой класс для обработки HTTP-запросов
class WebServerHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        if '/sendhttp' == self.path:
            length = int(self.headers.get('content-length'))
            message = self.rfile.read(length)
            # Создаём байтовый объект, куда будем записывать весь вывод для HTTP-ответа
            response = BytesIO()
            # Пытаемся разобрать запрос
            try:
                data = ast.literal_eval(message.decode('utf-8'))
                result = sent_http_request(data['Target'], data['Method'],
                              str.split(data['Header']+':'+data['Header-value'])
                )
                response.write(bytes(result,'UTF-8'))
            except SyntaxError:
                response.write(bytes("Неверный запрос\n",
                                     'UTF-8'
                                     )
                )
            # Выводим HTTP-ответ
            self.wfile.write(response.getvalue())
        else:
            self.send_response(403)

    def do_GET(self):
        if '/scan' == self.path:
            length = int(self.headers.get('content-length'))
            message = self.rfile.read(length)
            #Создаём байтовый объект, куда будем записывать весь вывод для HTTP-ответа
            response = BytesIO()
            # Пытаемся разобрать запрос
            try:
                data = ast.literal_eval(message.decode('utf-8'))
                # Проверяем переданные данные
                try:
                    for host_num in range(int (data['count'])):
                        result = ping_sweep(data['target'], host_num)
                        response.write(bytes(result,'UTF-8'))
                # Если количество адресов не число
                except (ValueError,TypeError):
                    response.write(bytes(
                                    f"[#] Результат сканирование: {data['target']} [#]\n"
                                    "Неверное или не указано количество IP-адресов\n",
                                    'UTF-8'
                                    )
                    )
            except SyntaxError:
                response.write(bytes("Неверный запрос\n",
                                     'UTF-8'
                                     )
                )
            # Выводим HTTP-ответ
            self.wfile.write(response.getvalue())
        else:
            self.send_response(403)

# Объявляем главную фукнцию, которая будет запускать после запуска скрипта
def main():
    try:
        port = 3000
        server = HTTPServer(('', port), WebServerHandler)
        print (f"Web Server running on port: {port}")
        server.serve_forever()
    except KeyboardInterrupt:
        print (" ^C entered, stopping web server....")
        server.shutdown()

# Запуск главной функции
if __name__ == "__main__":
    main()
