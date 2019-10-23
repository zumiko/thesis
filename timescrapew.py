#https://blog.scrapinghub.com/2016/06/22/scrapy-tips-from-the-pros-june-2016
#https://www.datacamp.com/community/tutorials/json-data-python 

import json
import scrapy
import pandas as pd

# Import the CrawlerProcess: for running the spider
from scrapy.crawler import CrawlerProcess

#https://gateway.gofundme.com/web-gateway/v1/feed/military-veteran-rent-pass-due-eviction-notice/donations?limit=1000  1
#https://gateway.gofundme.com/web-gateway/v1/feed/helptheleague/donations?limit=1000 2
#https://gateway.gofundme.com/web-gateway/v1/feed/open-door-baptist-church-central-air-unit/donations?limit=1000 3
#https://gateway.gofundme.com/web-gateway/v1/feed/brianisbell/donations?limit=1000 4
#https://gateway.gofundme.com/web-gateway/v1/feed/reunite-family-with-dog-after-deportation/donations?limit=1000 5

class TymeSpyder(scrapy.Spider):
    name = 'timescrape'
    camp_base_url = 'https://gateway.gofundme.com/web-gateway/v1/feed/reunite-family-with-dog-after-deportation/donations?limit=1000 '
    #start_urls = [quotes_base_url % 1]
    download_delay = 4.0 #used to be 2 
    custom_settings = {
    'USER_AGENT' : 'gfm_spider',
    }


    def start_requests(self):
        allowed_domains = ['gofundme.com']
        camp_base_url = 'https://gateway.gofundme.com/web-gateway/v1/feed/reunite-family-with-dog-after-deportation/donations?limit=1000 '
        yield scrapy.Request(url = camp_base_url,
                               callback = self.parse)

    def parse(self, response):
        print("parsing")
        data = json.loads(response.body)

        df = pd.DataFrame(data)
        references = (df['references'])
        donations = references[0]
        dfdonations = pd.DataFrame(donations)

        #print(references)
        print(references[0])
        meta = (df['meta'])
        export_csv = dfdonations.to_csv (r'C:\Users\Claire\Desktop\d362065.csv', index = None, header=True)
        #print(df)
        #for item in data.get('references', []):

            #print(str(item))
            #https://stackoverflow.com/questions/42524415/need-help-in-python-for-json-data-scraping
            #print(item[2])
            #DonationObject = {
                    #'donation_id' : item[0:10]
                    #'donation_id': item.get(1),
                    #'amount': item.get('amount'),
                    #'is_offline': item.get('is_offline'),
                    #'is_anonymous': item.get('is_anonymous'),
                    #'name': item.get('name'),
                    #'created_at': item.get('created_at'),
                    #'content': item.get('content'),
                    #'comment': item.get('comment'),
                    #'profile_url': item.get('profile_url'),
                    #'status': item.get('status'),
                    #'is_hidden': item.get('is_hidden')
                    
                    #username = data["user_details"]['username']
                    #user_email = data["user_details"]['user_email']

            #}
            #print(DonationObject)
        #if data['has_next']:
            #next_page = data['page'] + 1
            #yield scrapy.Request(self.quotes_base_url % next_page)

#running spyder
process = CrawlerProcess()
process.crawl(TymeSpyder)
process.start()


#for person in data['people']: 
    #print(person['name'])