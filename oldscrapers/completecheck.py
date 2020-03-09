import scrapy
import json
import pandas as pd
from scrapy.crawler import CrawlerProcess


#TODO: 
#Cycle through more pages for each zipcode
#Fix to get full donation hist
#I think you gotta make a full global dataframe at this pt. 


class gfm_Spider(scrapy.Spider):
  name = "gfm_spider"
  #download_delay = 2
  zipdict = {}
  description = []
  campzipurl = {}
  campzip = {}
  donationhist = pd.DataFrame() 
  offset = 0 

  custom_settings = {
    'USER_AGENT' : 'gfm_spider',
    'DOWNLOAD_DELAY' : 0.25, 
    'DEPTH_PRIORITY' : 1,
    'SCHEDULER_DISK_QUEUE' : 'scrapy.squeues.PickleFifoDiskQueue',
    'SCHEDULER_MEMORY_QUEUE' : 'scrapy.squeues.FifoMemoryQueue'
    }
    #https://autopython.blogspot.com/p/scrapy-tutorial.html


  def start_requests(self):  #searches each zipcode
    allowed_domains = ['gofundme.com']
    starturls = ['https://gateway.gofundme.com/web-gateway/v1/feed/28b3kc/donations?limit=100&offset=0&sort=recent']
    for url in starturls:
      yield scrapy.Request(url = url,
                          callback = self.parse_donation_hist)
  

  def parse_donation_hist(self,response): #scrapes all donation history
    #https://gateway.gofundme.com/web-gateway/v1/feed/helptheleague/donations?limit=20&offset=3&sort=recent
    data = json.loads(response.body)
    df = pd.DataFrame(data)
    references = (df['references'])
    donations = references[0]
    dfdonations = pd.DataFrame(donations)
    self.donationhist = self.donationhist.append(dfdonations, ignore_index = True)
    #print(self.donationhist)

    urlsolid = response.request.url  #this grabs the current url you are on
    urlsolid_ext = urlsolid.replace('https://gateway.gofundme.com/web-gateway/v1/feed/', '') 
    head, sep, tail = urlsolid_ext.partition('/donations?')
    urlsolid_ext_ext = head  #this grabs just the url name of the campaign for the next part
    #print("this is refzero" + str(references[0]))
    meta = (df['meta'])
    print("THIS IS THE META DATA")
    has_next = meta['has_next'] #this checks if there is more and returns True or False
    print(str(has_next))
    print(self.offset)
    if has_next == False: 
        print("send csv")
        nrows = self.donationhist.shape[0]  #get the number of rows 
        namels = [urlsolid_ext_ext] * nrows
        self.donationhist['urlsolid'] = namels
        export_csv = self.donationhist.to_csv(r'checkingalldonations{}.csv'.format(urlsolid_ext_ext), index = None, header=True)
        yield self.donationhist
        print("sent csv")

    if has_next == True: 
        self.offset += 100 #offset should be the same as whatever the limit is 
        offlim = 'https://gateway.gofundme.com/web-gateway/v1/feed/{}/donations?limit=100&offset={}&sort=recent'.format(urlsolid_ext_ext, self.offset)
        yield response.follow(url = offlim,
                          callback = self.parse_donation_hist)


        

    
      

    






process = CrawlerProcess()
process.crawl(gfm_Spider)
process.start()


#first datasheet will have all zipcodes in search and associated campaign urls 
#second datasheet has associated info for each campaign for a given zipcode 
#last datasheet has donation history for each campaign 
