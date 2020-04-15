import scrapy
import json
import pandas as pd
from getzips import *
from scrapy.crawler import CrawlerProcess


#first sheet has all zipcodes in search and associated campaign urls 
#second sheet has associated info for each campaign for a given zipcode 
#third sheet has donation history for each campaign

class gfm_Spider(scrapy.Spider):
  name = "gfm_spider"
  zipdict = {}
  description = []
  campzipurl = {}
  campzip = {}


  custom_settings = {
    'USER_AGENT' : 'gfm_spider',
    'DOWNLOAD_DELAY' : 1.25, 
    'DEPTH_PRIORITY' : 1,  #switch to breadth first crawl
    'SCHEDULER_DISK_QUEUE' : 'scrapy.squeues.PickleFifoDiskQueue',
    'SCHEDULER_MEMORY_QUEUE' : 'scrapy.squeues.FifoMemoryQueue'
    }
    #https://autopython.blogspot.com/p/scrapy-tutorial.html

  def __init__(self):
    self.item = None
    self.numcamps = 0 # iter up each time scrapes camp
    self.numchecked = 0 # iter up each time get has_next == False
    self.donationhist = pd.DataFrame()
    self.offsetdict = {}

  def start_requests(self):  #searches each zipcode
    allowed_domains = ['gofundme.com']

    #https://matthew-brett.github.io/teaching/string_formatting.html
    all_zip_codes = zipl1
    starturls = []
    for zipcode in all_zip_codes:
      i = 0   
      while i < 10: #doesn't allow for more than 9*10 in one zip code but seems safe will check
          urlfull = f"https://www.gofundme.com/mvc.php?route=homepage_norma/load_more&page={i}&term={zipcode}&country=US&postalCode={zipcode}&locationText="
          self.campzipurl[urlfull] = zipcode
          starturls.append(urlfull)
          i += 1
    for url in starturls:
      yield scrapy.Request(url = url,
                          callback = self.parse_front)
  
  def parse_front(self, response): #gets links to each campaign page
    urlold = response.request.url 
    myzip = self.campzipurl[urlold]
    tile = response.css('div.react-campaign-tile') 
    tile_links = tile.xpath('.//a/@href') 
    links_to_follow = tile_links.extract()

    for link in links_to_follow:
        urlcampsolid = link.replace('https://www.gofundme.com/f/', '')
        self.campzip[urlcampsolid] = myzip
    campzipcodes = pd.Series(self.campzip).to_frame()
    trial = 2
    export_csv = campzipcodes.to_csv(r'campsbyzip{}.csv'.format(trial), index = True)

    for url in links_to_follow:
      yield response.follow(url = url,
                            callback = self.parse_by_zip)

  def parse_donation_hist(self,response): #scrapes donation history
    #https://gateway.gofundme.com/web-gateway/v1/feed/helptheleague/donations?limit=20&offset=3&sort=recent
    data = json.loads(response.body)
    df = pd.DataFrame(data)
    references = (df['references'])
    donations = references[0]
    dfdonations = pd.DataFrame(donations)
    #print(self.donationhist)

    urlsolid = response.request.url  #this grabs the current url you are on
    urlsolid_ext = urlsolid.replace('https://gateway.gofundme.com/web-gateway/v1/feed/', '') 
    head, sep, tail = urlsolid_ext.partition('/donations?')
    urlsolid_ext_ext = head  #this grabs just the url name of the campaign for the next part

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
      export_csv = self.donationhist.to_csv(r'donationhistory.csv', index = None, header=True)

    #if self.numchecked == self.numcamps: 
      #print("sending csv")
      #export_csv = self.donationhist.to_csv(r'donationhistory.csv', index = None, header=True)

    if response.meta['has_next'] == True:
        self.offsetdict[urlsolid_ext_ext] += 100 #offset should be the same as whatever the limit is 
        offset = self.offsetdict[urlsolid_ext_ext]
        offlim = 'https://gateway.gofundme.com/web-gateway/v1/feed/{}/donations?limit=100&offset={}&sort=recent'.format(urlsolid_ext_ext, offset) #used to be self.offset
        yield response.follow(url = offlim,
                          callback = self.parse_donation_hist,
                          meta = response.meta)

  def parse_by_zip(self, response): #grabs traits of each campaign from campaign page and gets links to donation history data


    urlsolid = response.request.url  #this grabs the current url you are on
    urlsolid_ext = urlsolid.replace('https://www.gofundme.com/f/', '')  #this grabs just the url name of the campaign for the next 
    self.offsetdict[urlsolid_ext] = 0
    self.numcamps += 1

    camptitle = response.xpath('//h1[contains(@class,"campaign-title")]/text()')
    camptitle_ext = camptitle.extract_first().strip()
    #print(camptitle)

    category = response.xpath('//a[contains(@class, "m-campaign-byline-type")]/@href').extract()
    category_ext = str(category).replace('/discover/', '')

    created = response.xpath('//span[contains(@class, "m-campaign-byline-created")]/text()')
    created_ext = [l.strip() for l in created.extract()]

    terminated = response.xpath('//div[contains(@class, "o-campaign-sidebar-notification")]/text()')
    terminated_ext = [l.strip() for l in terminated.extract()]

    byline = response.xpath('//div[contains(@class, "m-campaign-byline-description")]/text()')
    byline_ext = [l.strip() for l in byline.extract()]

    description = response.xpath('//div[contains(@class, "o-campaign-story")]/text()')
    description_ext = [l.strip() for l in description.extract()]

    description2 = response.xpath('//div[contains(@class, "o-campaign-story")]//p/text()')
    description2_ext = [l.strip() for l in description2.extract()]

    description3 = response.xpath('//div[contains(@class, "o-campaign-story")]//div/text()')
    description3_ext = [l.strip() for l in description3.extract()]

    nonprofit = response.xpath('//div[contains(@class, "text-small")]//div/text()')
    nonprofit_ext = [l.strip() for l in nonprofit.extract()]

    amtraised = response.xpath('//h2[contains(@class, "m-progress-meter-heading")]/text()')
    amtraised_ext = [l.strip() for l in amtraised.extract()]

    goalamt = response.xpath('//span[contains(@class, "text-stat-title")]/text()')
    goalamt_ext = [l.strip() for l in goalamt.extract()]

    #myzip = self.campzip[urlsolid_ext.casefold()]

    info = [urlsolid_ext, camptitle_ext, category_ext, created_ext, terminated_ext, byline_ext, description_ext, description2_ext, description3_ext, nonprofit_ext, amtraised_ext, goalamt_ext] #byline_ext, created_ext, extra_ext, amtraised_ext, goalamt_ext, donorsamt_ext, sharesamt_ext]
    self.zipdict[urlsolid_ext] = info
    zipcollect = pd.DataFrame(self.zipdict, index =['urlname', 'title', 'category', 'created','terminated', 'organizer', 'description1', 'description2', 'description3', 'nonprofit?','amtraised', 'goalamt'])
    zipcollect = zipcollect.T #taking transpose to switch rows and columns

    export_csv = zipcollect.to_csv(r'campattributes.csv', index = True, header=True)

    urlhist = 'https://gateway.gofundme.com/web-gateway/v1/feed/{}/donations?limit=100&offset=0&sort=recent'.format(urlsolid_ext)
    yield response.follow(url = urlhist,
                            callback = self.parse_donation_hist)


process = CrawlerProcess()
process.crawl(gfm_Spider)
process.start()
