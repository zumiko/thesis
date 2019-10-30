import scrapy
import json
import pandas as pd
from scrapy.crawler import CrawlerProcess


class gfm_Spider(scrapy.Spider):
  name = "gfm_spider"
  zipdict = {}
  description = []

  custom_settings = {
    'USER_AGENT' : 'gfm_spider',
    }

  
  def start_requests(self):  #searches each zipcode
    allowed_domains = ['gofundme.com']
    all_zip_codes = [27263, 36206, 55607, 92013, 20620, 90504, 95401, 63549, 60974, 7306]
    #https://matthew-brett.github.io/teaching/string_formatting.html
    starturls = []
    for zipcode in all_zip_codes:
      url = f"https://www.gofundme.com/mvc.php?route=homepage_norma/search&term={zipcode}&country=US&locationText=&postalCode={zipcode}"
      starturls.append(url)
    for url in starturls:
      yield scrapy.Request(url = url,
                          callback = self.parse_front)
  
  def parse_front(self, response): #gets links to each campaign page
    tile = response.css('div.react-campaign-tile') 
    tile_links = tile.xpath('./a/@href') 
    links_to_follow = tile_links.extract()
    for url in links_to_follow:
      yield response.follow(url = url,
                            callback = self.parse_by_zip)

  def parse_donation_hist(self,response): #scrapes all donation history
    #https://gateway.gofundme.com/web-gateway/v1/feed/helptheleague/donations?limit=1000
    data = json.loads(response.body)
    df = pd.DataFrame(data)
    references = (df['references'])
    donations = references[0]
    dfdonations = pd.DataFrame(donations)
    urlsolid = response.request.url  #this grabs the current url you are on
    urlsolid_ext = urlsolid.replace('https://gateway.gofundme.com/web-gateway/v1/feed/', '') 
    urlsolid_ext_ext = urlsolid_ext.replace('/donations?limit=1000000', '')   #this grabs just the url name of the campaign for the next part

    print(references[0])
    meta = (df['meta'])
    export_csv = dfdonations.to_csv (r'C:\Users\Claire\Desktop\dzz{}.csv'.format(urlsolid_ext_ext + "hist"), index = None, header=True)

  def parse_by_zip(self, response): #grabs traits of each campaign from campaign page and gets links to donation history data


    urlsolid = response.request.url  #this grabs the current url you are on
    urlsolid_ext = urlsolid.replace('https://www.gofundme.com/f/', '')  #this grabs just the url name of the campaign for the next part

    camptitle = response.xpath('//h1[contains(@class,"campaign-title")]/text()')
    camptitle_ext = camptitle.extract_first().strip()

    category = response.xpath('//a[contains(@class, "m-campaign-byline-type")]/@href').extract()
    category_ext = str(category).replace('/discover/', '')

    created = response.xpath('//span[contains(@class, "m-campaign-byline-created")]/text()')
    created_ext = [l.strip() for l in created.extract()]

    byline = response.xpath('//div[contains(@class, "m-campaign-byline-description")]/text()')
    byline_ext = [l.strip() for l in byline.extract()]

    description = response.xpath('//div[contains(@class, "o-campaign-story")]/text()')
    description_ext = [l.strip() for l in description.extract()]

    amtraised = response.xpath('//h2[contains(@class, "m-progress-meter-heading")]/text()')
    amtraised_ext = [l.strip() for l in amtraised.extract()]

    goalamt = response.xpath('//span[contains(@class, "text-stat-title")]/text()')
    goalamt_ext = [l.strip() for l in goalamt.extract()]

    info = [urlsolid_ext, camptitle_ext, category_ext, created_ext, byline_ext, description_ext, amtraised_ext, goalamt_ext] #byline_ext, created_ext, extra_ext, amtraised_ext, goalamt_ext, donorsamt_ext, sharesamt_ext]
    self.zipdict[urlsolid_ext] = info
    zipcollect = pd.DataFrame(self.zipdict, index =['urlname', 'title', 'category', 'created', 'organizer', 'description', 'amtraised', 'goalamt'])


    export_csv = zipcollect.to_csv (r'C:\Users\Claire\Desktop\dzz{}.csv'.format(urlsolid_ext), index = True, header=True)

    urlhist = 'https://gateway.gofundme.com/web-gateway/v1/feed/{}/donations?limit=1000000'.format(urlsolid_ext)

    yield response.follow(url = urlhist,
                            callback = self.parse_donation_hist)



process = CrawlerProcess()
process.crawl(gfm_Spider)
process.start()


#first datasheet will have all zipcodes in search and associated campaign urls 
#second datasheet has associated info for each campaign for a given zipcode 
#last datasheet has donation history for each campaign 







