from urllib.request import urlopen
import json
from datetime import date
from datetime import timedelta
URL = 'https://api.telegram.org/bot'
TOKEN = 'token'

def get_updates()->'dict':
    url = URL + TOKEN + '/getUpdates'
    res = urlopen(url).read()
    return json.loads(res)


def get_schedule(par:'str')->'http.client.HTTPResponse object':
    '''params in argument(par) should be separated by "&"'''
    from http.client import HTTPConnection
    head = {'host':'inet.ibi.spb.ru',
            'Content-Type':'application/x-www-form-urlencoded',
            'Connection':'keep-alive',
            'Content-Length':'96',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'ru,en;q=0.9'}
    h1 = HTTPConnection('inet.ibi.spb.ru', 80)
    h1.request('POST', '/raspisan/rasp.php/', headers=head, body=par)
    r = h1.getresponse()
    h1.close()
    return r


def create_message(html):
    from bs4 import BeautifulSoup  as bs
    soup = bs(html, "html.parser")
    days = soup.find_all('tr')
    del days[0]#удаляем строчку: "дата","время занятий"
    #Делаем словарь: ключ-дата, значение-список с занятиями
    days = {d.find_all('td')[0].string : d.find_all('td')[1:] for d in days}
    for day in days: #заменяем список тегов на список занятий в каждом дне
        days[day] = [x.string for x in days[day]]
    times = []
    for item in soup.find_all('td'):# находим время
        if item.parent.name == 'table':#<td> с временем находятся не в <tr>
            times.append(item.string)
    message = ''
    for day, classes in days.items():#создаем сообщение для отправки
        message += '<b>' + day[:-1] + '</b>' + '\n'
        for i in range(len(classes)):
            if classes[i]!='\xa0':
                message += ('\u231a\ufe0f' + '<code>' + times[i][:-1] + '</code>' +
                            '\n' + classes[i][:-1] + '\n')
        message += '\n'
    return message    


def send_message(chat_id: 'str', text: 'str')-> 'True || False':
    from urllib.request import Request
    from urllib.parse import quote
    text = quote(text)
    url = (URL + TOKEN + '/sendMessage?chat_id=' + chat_id
           +'&text=' + text + '&parse_mode=HTML')
    req = Request(url=url, method = 'POST')
    res = urlopen(req)
    if res.status==200:
        return True
    else:
        return False


def setup_menu(chat_id: 'str')->'Boolean':
    url = URL+TOKEN+'/sendMessage?chat_id='+chat_id+'&text=ok&reply_markup='
    keyboard = {"keyboard":[["Сегодня", "Завтра"],["На эту неделю", "На следущую неделю"]]}
    keyboard = json.dumps(keyboard)
    url += keyboard
    res = urlopen(url).read().decode('utf-8')
    res = json.loads(res)
    if res['ok'] == True:
        return True
    else: return False
    
def handle_updates(updates:'dict', how_much:'int'): 
    for each in updates['result'][-how_much:]:
        #print(each)
        params = ['rtype=1', 'group=1880', 'exam=0', 'formo=0', 'allp=0', 'hour=0', 'tuttabl=0']
        if 'text' in each['message']:#ветвление на случай нетекстового сообщения
            
            if each['message']['text'] == 'Сегодня':
                message = 'Расписание на сегодня'
                today = date.today().isoformat().split('-')
                today.reverse()
                datef = 'datafrom=' + '.'.join(today)
                datend = 'dataend=' + '.'.join(today)
                params.extend([datef, datend])
                params = '&'.join(params)
                schedule = get_schedule(params).read().decode('utf-8')
                if schedule.find('<table')!=-1 & schedule.find('<tr')!=-1:
                    message = create_message(schedule)
                else:
                    message = 'Информации не обнаруженно!'
                chat_id = str(each['message']['chat']['id'])
                send_message(chat_id, message)
                print(each['message']['text'])
                
            elif each['message']['text'] == 'Завтра':
                today = date.today() 
                today = today + timedelta(days = 1)#today на самом деле уже завтра
                today = today.isoformat().split('-')
                today.reverse()
                datef = 'datafrom=' + '.'.join(today)
                datend = 'dataend=' + '.'.join(today)
                params.extend([datef, datend])
                params = '&'.join(params)
                schedule = get_schedule(params).read().decode('utf-8')
                if schedule.find('<table')!=-1 & schedule.find('<tr')!=-1:# а таблица ли это?
                    message = create_message(schedule)
                else:
                    message = 'Информации не обнаруженно!'
                chat_id = str(each['message']['chat']['id'])
                send_message(chat_id, message)
                print(each['message']['text'])
                
            elif each['message']['text'] == 'На эту неделю':
                today = date.today()
                weekday = today.weekday()
                datef = today - timedelta(days = weekday)
                datef = datef.isoformat().split('-')
                datef.reverse()
                datef = 'datafrom=' + '.'.join(datef)
                datend = today + timedelta(days = 6 - weekday)
                datend = datend.isoformat().split('-')
                datend.reverse()
                datend = 'dataend=' + '.'.join(datend)
                params.extend([datef, datend])
                params = '&'.join(params)
                schedule = get_schedule(params).read().decode('utf-8')
                if schedule.find('<table')!=-1 & schedule.find('<tr')!=-1:
                    message = create_message(schedule)
                else:
                    message = 'Информации не обнаруженно!'
                chat_id = str(each['message']['chat']['id'])
                send_message(chat_id, message)
                print(each['message']['text'])
            elif each['message']['text'] == 'На следущую неделю':
                today = date.today()
                datef = (today + timedelta(days=6-today.weekday()+1))
                datend = datef + timedelta(days = 6)
                datef = datef.isoformat().split('-')
                datend = datend.isoformat().split('-')
                datef.reverse()
                datend.reverse()
                datef = 'datafrom=' + '.'.join(datef)
                datend = 'dataend=' + '.'.join(datend)
                params.extend([datef, datend])
                params = '&'.join(params)
                schedule = get_schedule(params).read().decode('utf-8')
                if schedule.find('<table')!=-1 & schedule.find('<tr')!=-1:
                    message = create_message(schedule)
                else:
                    message = 'Информации не обнаруженно!'
                chat_id = str(each['message']['chat']['id'])
                send_message(chat_id, message)
                print(each['message']['text'])
            elif each['message']['text'] == '/start':
                setup_menu(str(each['message']['chat']['id']))
            else:
                message = 'Неизвестная команда'
                chat_id = str(each['message']['chat']['id'])
                send_message(chat_id, message)
                print(each['message']['text'])
        else:
            message = 'Бот принимает только текстовые команды'
            chat_id = str(each['message']['chat']['id'])
            send_message(chat_id, message)

        

    #print(message)
