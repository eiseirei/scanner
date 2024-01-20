# scanner
Программа для сканирования сети и отсылки запросов. Формат:

1. Сканирование сети
   
   curl -X GET -H "Content-type: application/json" http://localhost:3000/scan --data "{'target':'192.168.1.0', 'count': '3'}"  --http0.9
   
   где 192.168.1.0 -- это сеть, а 3 -- количество хостов

3. Отправка запросов
   
   curl -X POST -H "Content-type: application/json" http://localhost:3000/sendhttp --data "{'Header': 'Content-type', 'Header-value': 'text', 'Target':'http://www.google.com', 'Method': 'GET'}"  --http0.9
   
   где http://www.google.com -- ресурс, к которому отправляется запрос, Content-type -- заголовок, text -- значение заголовка, GET -- метод
