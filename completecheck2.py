import scrapy
import json
import pandas as pd
from scrapy.crawler import CrawlerProcess

#this one runs for a single campaign to check that it is getting all the time history

#TODO: 
#Cycle through more pages for each zipcode
#Fix to get full donation hist



class gfm_Spider(scrapy.Spider):
  name = "gfm_spider"
  description = []

  custom_settings = {
    'USER_AGENT' : 'gfm_spider',
    'DOWNLOAD_DELAY' : 1.25, 
    'DEPTH_PRIORITY' : 1,
    'SCHEDULER_DISK_QUEUE' : 'scrapy.squeues.PickleFifoDiskQueue',
    'SCHEDULER_MEMORY_QUEUE' : 'scrapy.squeues.FifoMemoryQueue', 
    'CONCURRENT_REQUESTS': '1'
    }
    #https://autopython.blogspot.com/p/scrapy-tutorial.html

  def __init__(self):
    self.item = None
    self.numcamps = 2 
    self.numchecked = 0 
    self.offset = 0
    self.donationhist = pd.DataFrame()
    self.offsetdict = dict({'rescateanimalmompiche': 0, 'rebuild4lindahubba': 0}) 


  def start_requests(self): 
    allowed_domains = ['gofundme.com']
    otherurls = [
    'https://gateway.gofundme.com/web-gateway/v1/feed/rescateanimalmompiche/donations?limit=100&offset=0&sort=recent',
    'https://gateway.gofundme.com/web-gateway/v1/feed/rebuild4lindahubba/donations?limit=100&offset=0&sort=recent'
    ]

    for url in otherurls:
      priority = otherurls.index(url)
      yield scrapy.Request(url = url,
                          callback = self.parse_donation_hist)
  

  def parse_donation_hist(self,response): #scrapes all donation history
    print(response.meta)
    
    data = json.loads(response.body)
    df = pd.DataFrame(data)
    references = (df['references'])
    donations = references[0]
    dfdonations = pd.DataFrame(donations)

    urlsolid = response.request.url  #this grabs the current url you are on
    urlsolid_ext = urlsolid.replace('https://gateway.gofundme.com/web-gateway/v1/feed/', '') 
    head, sep, tail = urlsolid_ext.partition('/donations?')
    urlsolid_ext_ext = head  #this grabs just the urlsolid of the campaign for the next part
    print(urlsolid_ext_ext)

    nrows = dfdonations.shape[0]
    namels = [urlsolid_ext_ext] * nrows
    dfdonations['urlsolid'] = namels
    self.donationhist = self.donationhist.append(dfdonations, ignore_index = True)

    meta = (df['meta'])
    has_next = meta['has_next'] #this checks if there is more and returns True or False 
    response.meta['has_next'] = has_next


    if response.meta['has_next'] == False: 
      self.numchecked += 1
      print("this one is done, and total= " + str(self.numchecked))

    if self.numchecked == self.numcamps: 
      print("sending csv")
      export_csv = self.donationhist.to_csv(r'donationhist.csv', index = None, header=True)


    if response.meta['has_next']  == True: 
         #offset should be the same as whatever the limit is 
        print(self.offsetdict)
        self.offsetdict[urlsolid_ext_ext] += 100
        offset = self.offsetdict[urlsolid_ext_ext]
        offlim = 'https://gateway.gofundme.com/web-gateway/v1/feed/{}/donations?limit=100&offset={}&sort=recent'.format(urlsolid_ext_ext, offset)
        yield response.follow(url = offlim,
                          callback = self.parse_donation_hist, meta= response.meta)






process = CrawlerProcess()
process.crawl(gfm_Spider)
process.start()
