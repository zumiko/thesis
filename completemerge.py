import scrapy
import json
import pandas as pd
from scrapy.crawler import CrawlerProcess


#TODO: 
#Cycle through more pages for each zipcode
#Fix to get full donation hist


class gfm_Spider(scrapy.Spider):
  name = "gfm_spider"
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
    #all_zip_codes = [27263 ,36206, 55607, 92013, 20620, 90504, 95401, 63549, 60974, 7306] #original from R
    #all_zip_codes = [70182,  44235, 35564, 45388, 66776, 56425,  3086, 20250, 61488, 61241, 92147, 73620,
 #95640, 68748, 35586, 28236, 48667, 64745, 64850, 58651] #from python
    all_zip_codes = [27263] #, 36206, 55607, 92013, 20620, 90504, 95401, 63549, 60974,  7306, 20892, 18348, 66537, 37320, 75160, 48366,
    #70177, 99157, 37032, 75750, 94514, 21653, 62830, 13747, 27403, 37414,  1983, 37171, 85363, 33154, 47224, 58043,
 #48105, 19192, 79953, 64190, 77210, 12249, 70738, 39836, 79243, 62445, 76131, 53950, 50667, 76684,  3040, 46791,
 #71475, 67058]
    #https://matthew-brett.github.io/teaching/string_formatting.html
    starturls = []
    for zipcode in all_zip_codes:
      i = 0   
      while i < 20: #this doesnt allow for more than 90 campaigns in 1 zipcode seems safe to me but might wanna double check (yeah not a safe assumption
          #url = f"https://www.gofundme.com/mvc.php?route=homepage_norma/search&term={zipcode}&country=US&locationText=&postalCode={zipcode}"
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
    #print("this is the" + str(myzip))
    tile = response.css('div.react-campaign-tile') 
    print(tile)
    tile_links = tile.xpath('.//a/@href') 
    print(tile_links)
    #tile_links.append(tile.xpath())
    links_to_follow = tile_links.extract()
    for link in links_to_follow:
        urlcampsolid = link.replace('https://www.gofundme.com/', '')
        #print(urlcampsolid)
        self.campzip[urlcampsolid] = myzip
    campzipcodes = pd.Series(self.campzip).to_frame()
    #campzipcodes = pd.DataFrame.from_records(self.campzip)
    trial = 1
    export_csv = campzipcodes.to_csv(r'campsbyzip{}.csv'.format(trial), index = True)

    for url in links_to_follow:
      yield response.follow(url = url,
                            callback = self.parse_by_zip)

  def parse_donation_hist(self,response): #scrapes all donation history
    #https://gateway.gofundme.com/web-gateway/v1/feed/helptheleague/donations?limit=20&offset=3&sort=recent
    data = json.loads(response.body)
    df = pd.DataFrame(data)
    references = (df['references'])
    donations = references[0]
    print(donations)
    dfdonations = pd.DataFrame(donations)
    print(dfdonations)

    urlsolid = response.request.url  #this grabs the current url you are on
    urlsolid_ext = urlsolid.replace('https://gateway.gofundme.com/web-gateway/v1/feed/', '') 
    head, sep, tail = urlsolid_ext.partition('/donations?')
    urlsolid_ext_ext = head  #this grabs just the url name of the campaign for the next part

    nrows = dfdonations.shape[0]
    namels = [urlsolid_ext_ext] * nrows
    dfdonations['urlsolid'] = namels
    self.donationhist = self.donationhist.append(dfdonations, ignore_index = True)

    #print("this is refzero" + str(references[0]))
    meta = (df['meta'])
    print("THIS IS THE META DATA")
    has_next = meta['has_next'] #this checks if there is more and returns True or False
    print(str(has_next))

    if has_next == False: 
        print("send csv")
          #get the number of rows 
        export_csv = self.donationhist.to_csv(r'donationhist.csv', index = None, header=True) 
        self.offset = 0 
        yield self.donationhist
        print("sent csv")


    if has_next == True: 
        self.offset += 100 #offset should be the same as whatever the limit is 
        offlim = 'https://gateway.gofundme.com/web-gateway/v1/feed/{}/donations?limit=100&offset={}&sort=recent'.format(urlsolid_ext_ext, self.offset)
        yield response.follow(url = offlim,
                          callback = self.parse_donation_hist)

  def parse_by_zip(self, response): #grabs traits of each campaign from campaign page and gets links to donation history data


    urlsolid = response.request.url  #this grabs the current url you are on
    urlsolid_ext = urlsolid.replace('https://www.gofundme.com/f/', '')  #this grabs just the url name of the campaign for the next part

    camptitle = response.xpath('//h1[contains(@class,"campaign-title")]/text()')
    camptitle_ext = camptitle.extract_first().strip()
    print(camptitle)

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

    myzip = self.campzip[urlsolid_ext.casefold()]
    #print("this is the zipcode" + str(myzip))

    info = [urlsolid_ext, camptitle_ext, category_ext, created_ext, terminated_ext, byline_ext, description_ext, description2_ext, description3_ext, nonprofit_ext, amtraised_ext, goalamt_ext] #byline_ext, created_ext, extra_ext, amtraised_ext, goalamt_ext, donorsamt_ext, sharesamt_ext]
    self.zipdict[urlsolid_ext] = info
    zipcollect = pd.DataFrame(self.zipdict, index =['urlname', 'title', 'category', 'created','terminated', 'organizer', 'description1', 'description2', 'description3', 'nonprofit?','amtraised', 'goalamt'])
    #print(zipcollect)
    zipcollect = zipcollect.T #taking transpose to switch rows and columns


    export_csv = zipcollect.to_csv(r'campattributes.csv', index = True, header=True)


    urlhist = 'https://gateway.gofundme.com/web-gateway/v1/feed/{}/donations?limit=100&offset=0&sort=recent'.format(urlsolid_ext)

    yield response.follow(url = urlhist,
                            callback = self.parse_donation_hist)


process = CrawlerProcess()
process.crawl(gfm_Spider)
process.start()


#first datasheet will have all zipcodes in search and associated campaign urls 
#second datasheet has associated info for each campaign for a given zipcode 
#last datasheet has donation history for each campaign 