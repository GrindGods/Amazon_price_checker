import time
from time import strftime
import schedule
import smtplib
import requests
from bs4 import BeautifulSoup

cookies = {
    'session-id': '260-4401342-6647323',
    'i18n-prefs': 'EUR',
    'ubid-acbde': '262-4130625-6436332',
    'lc-acbde': 'de_DE',
    'session-token': 'hV+iHOCiilabIYLGCJR/wy+MrV74SN9hMuWyKIQswQjJxuXTzzUjlAZb56ymqjRNrVCUXaZbBZOLlzF0ENHq6z9O+deXyAxwmg8+j7+rIKv5MvAAfOcKYjToE/FcLv4dEOkZVoprSbx5eWemfk0UUIw04XxxlAYUu0MRHzP6LW5QHMbiR0EbXHRjRaAB8lZa',
    'csm-hit': 'tb:s-3RR29G2CB5SX7K01A2H5|1650405851483&t:1650405874602&adb:adblk_no',
    'session-id-time': '2082754801l',
}

headers = {
    'authority': 'www.amazon.de',
    'cache-control': 'max-age=0',
    'device-memory': '4',
    'dpr': '1',
    'viewport-width': '1920',
    'rtt': '50',
    'downlink': '7.7',
    'ect': '4g',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="92"',
    'sec-ch-ua-mobile': '?0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; CrOS armv7l 13597.84.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.98 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
    # Requests sorts cookies= alphabetically
    'cookie': 'session-id=260-4401342-6647323; i18n-prefs=EUR; ubid-acbde=262-4130625-6436332; lc-acbde=de_DE; session-token=hV+iHOCiilabIYLGCJR/wy+MrV74SN9hMuWyKIQswQjJxuXTzzUjlAZb56ymqjRNrVCUXaZbBZOLlzF0ENHq6z9O+deXyAxwmg8+j7+rIKv5MvAAfOcKYjToE/FcLv4dEOkZVoprSbx5eWemfk0UUIw04XxxlAYUu0MRHzP6LW5QHMbiR0EbXHRjRaAB8lZa; csm-hit=tb:s-3RR29G2CB5SX7K01A2H5|1650405851483&t:1650405874602&adb:adblk_no; session-id-time=2082754801l',
}

user = 'thomas-roedl@gmx.de'
pwd = 'Laplace!'


class Angebote:
    def __init__(self, url, item, limit, rcpt_to, name):
        self.price = ''
        self.price_float = 0.0
        self.item = item
        self.url = url
        self.limit = limit
        self.subject = 'Neues ' + self.item + '-Angebot'
        self.rcpt_to = rcpt_to
        self.name = name

    def send(self, price):
        print('============== mail gesendet mit Limit ', price, '==============')
        with smtplib.SMTP('mail.gmx.net', 587) as server:
            server.starttls()
            server.ehlo()
            server.login(user, pwd)
            mail_text = 'Hallo %s,\n\nhier ein neues Angebot:\n\n%s: %s Euro\n\n%s' % (self.name, self.item, price, self.url)
            data = 'FROM:%s\nTO:%s\nSubject:%s\n\n%s' % (user, self.rcpt_to, self.subject, mail_text)
            server.sendmail(user, self.rcpt_to, data)

    def req(self):
        time.sleep(180)
        with requests.Session() as s:
            page = s.get(self.url, headers=headers, cookies=cookies)
            soup = BeautifulSoup(page.text, 'html.parser')
            if soup.find(id='corePrice_feature_div'):
                result = soup.find(id='corePrice_feature_div')
                if result.find('span', {'class': 'a-offscreen'}):
                    self.price = result.find('span', {'class': 'a-offscreen'}).text
            elif soup.find(id='desktop_unifiedPrice'):
                result = soup.find(id='desktop_unifiedPrice')
                self.price = result.find('span', {'class': 'a-size-medium a-color-price priceBlockBuyingPriceString'}).text
            self.price_float = float(self.price[:-1].replace(',', '.'))
            print(self.name+':', self.item, '\n\tchecked at', strftime('%H:%M:%S'), 'Preis:', self.price, 'Limit:', self.limit, '€')
            if self.price_float < self.limit:
                self.limit = self.price_float
                self.send(self.price[:-1])


if __name__ == '__main__':
    print('Angebot-Script laeuft')

    thomas = Angebote('https://www.amazon.de/gp/product/B0973HRKWG', "Elden Ring", 45, 'deskoidenou@googlemail.com',
             'Thomas')
    susi = Angebote('https://www.amazon.de/gp/product/B07KSCV37M', 'Tefal Buegeleisen', 60, 'susanne.roedl@yahoo.de',
             'Susi')

    # debug:
    """
    thomas.req()
    susi.req()
    """

    def exec_six():
        thomas.req()
        susi.req()

    schedule.every(4).hours.do(exec_six)
    while True:
        schedule.run_pending()
