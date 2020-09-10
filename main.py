import requests
from multiprocessing import Pool
from driver.selenium_setup import Driver
import time
from datetime import date, timedelta
import csv

CompanyList = [
    'PD',
    'ZUO',
    'PINS',
    'ZM',
    'PVTL',
    'DOCU',
    'CLDR',
    'RUN',
]


class YahooParser:
    csv_link = None

    def __init__(self, company):
        self.company = company

    def _get_csv_link(self):
        if self.csv_link is None:
            with Driver() as driver:
                url = f'https://finance.yahoo.com/quote/{self.company}/history?p={self.company}'
                try:
                    driver.get(url)
                    if driver.current_url != f'https://finance.yahoo.com/quote/{self.company}/history?p={self.company}':
                        return
                    driver.implicitly_wait(3)
                    driver\
                        .find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/'
                                               'section/div[1]/div[1]/div[1]/div/div/div')\
                        .click()

                    driver.find_element_by_id('dropdown-menu')\
                        .find_element_by_xpath('//button[@data-value="MAX"]')\
                        .click()

                    self.csv_link = driver\
                        .find_element_by_xpath(f'//a[@download="{self.company}.csv"]')\
                        .get_attribute('href')
                except Exception as e:
                    print(e)
                    return
        return self.csv_link

    def save_price_csv(self):
        url = self._get_csv_link()
        if url is None:
            print(f'Company "{self.company}" not found')
            return
        response = requests.get(url)
        content = response.content.decode('utf-8').split('\n')
        header = content[0].split(',')
        content = [dict(zip(header, line.split(','))) for line in content[1:]]
        header.append('3day_before_change')
        with open(f'./yahoo_finance/{self.company}.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            for line in content:
                before_date = date.fromisoformat(line['Date']) - timedelta(days=3)
                current_price = float(line['Close'])
                for new_line in content:
                    if date.fromisoformat(new_line['Date']) == before_date:
                        line['3day_before_change'] = str(current_price/float(new_line['Close']))
                        break
                    else:
                        line['3day_before_change'] = '-'
                writer.writerow(line)

    def _news(self):
        with Driver() as driver:
            driver.get(f'https://finance.yahoo.com/quote/{self.company}/')
            if driver.current_url != f'https://finance.yahoo.com/quote/{self.company}/':
                return 'Company not found'
            for elem in driver.find_elements_by_xpath('//div[@id="quoteNewsStream-0-Stream"]/ul/*'):
                yield ((elem.find_element_by_xpath('.//div/div/div/h3/a').get_attribute('href'),
                        elem.find_element_by_xpath('.//div/div/div/h3').text))

    def save_news_csv(self):
        header = ('Url', 'Title')
        with open(f'./yahoo_finance/{self.company}-news.csv', 'w') as csvfile:
            writer = csv.writer(csvfile, )
            writer.writerow(header)
            for line in self._news():
                writer.writerow(line)


if __name__ == '__main__':
    start_time = time.time()
    procs = []
    p = Pool(8)
    for company in CompanyList:
        parser = YahooParser(company)
        procs.append(p.apply_async(parser.save_price_csv))
        procs.append(p.apply_async(parser.save_news_csv))
    try:
        [r.get() for r in procs]
    except Exception as e:
        print('Interrupted')
        print(e)
        p.terminate()
        p.join()

    print('Time= ', time.time()-start_time)

