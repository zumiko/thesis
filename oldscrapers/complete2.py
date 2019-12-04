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
  #https://stackoverflow.com/questions/46746701/crawling-with-scrapy-http-status-code-is-not-handled-or-not-allowed

  
  def start_requests(self):
    allowed_domains = ['gofundme.com']
    all_zip_codes = [27263, 36206, 55607, 92013] #20620, 90504, 95401, 63549, 60974, 7306]
    #https://matthew-brett.github.io/teaching/string_formatting.html
    starturls = []
    for zipcode in all_zip_codes:
      url = f"https://www.gofundme.com/mvc.php?route=homepage_norma/search&term={zipcode}&country=US&locationText=&postalCode={zipcode}"
      starturls.append(url)
    for url in starturls:
      yield scrapy.Request(url = url,
                          callback = self.parse_front)
  
  def parse_front(self, response):
    tile = response.css('div.react-campaign-tile') #this is getting each tile
    tile_links = tile.xpath('./a/@href') #this gets links to individual campaigns 
    links_to_follow = tile_links.extract()
    #print(links_to_follow)
    for url in links_to_follow:
      yield response.follow(url = url,
                            callback = self.parse_by_zip)

  def parse_donation_hist(self,response): 
    #https://gateway.gofundme.com/web-gateway/v1/feed/helptheleague/donations?limit=1000
    data = json.loads(response.body)
    df = pd.DataFrame(data)
    references = (df['references'])
    donations = references[0]
    dfdonations = pd.DataFrame(donations)
    urlsolid = response.request.url  #this grabs the current url you are on
    urlsolid_ext = urlsolid.replace('https://gateway.gofundme.com/web-gateway/v1/feed/', '') 
    urlsolid_ext_ext = urlsolid_ext.replace('/donations?limit=1000', '')   #this grabs just the url name of the campaign for the next part

    #print(references)
    print(references[0])
    meta = (df['meta'])
    export_csv = dfdonations.to_csv (r'C:\Users\Claire\Desktop\d{}.csv'.format(urlsolid_ext_ext + "hist"), index = None, header=True)

  def parse_by_zip(self, response):
    camptitle = response.xpath('//h1[contains(@class,"campaign-title")]/text()')
    camptitle_ext = camptitle.extract_first().strip()
    #description = response.css('div.co-story truncate-text truncate-text--description js-truncate::text')

    urlsolid = response.request.url  #this grabs the current url you are on
    urlsolid_ext = urlsolid.replace('https://www.gofundme.com/f/', '')  #this grabs just the url name of the campaign for the next part

    description = response.xpath('//div[contains(@class, "o-campaign-story")]/text()')
    description_ext = [t.strip() for t in description.extract()]

    #urlsolid = response.xpath('//div[contains(@class, "fund-item")]/a/@href').extract_first()
    


    #sidebar = response.xpath('//div[contains(@class, "o-campaign-sidebar-notification")]/text()')
    #sidebar_ext = sidebar.extract_first().strip()
    #sidebar_ext = [t.strip() for t in sidebar.extract()]

    #byline = response.xpath('//div[contains(@class, "m-campaign-byline-description")]/text()')
    #byline_ext = [t.strip() for t in byline.extract()]

    #created = response.xpath('//span[contains(@class, "m-campaign-byline-created")]/text()')
    #created_ext = [t.strip() for t in created.extract()]

    #extra = response.xpath('//div[contains(@class, "text-small")]//div/text()')
    #extra_ext = [t.strip() for t in extra.extract()]

    #amtraised = response.xpath('//h2[contains(@class, "m-progress-meter-heading")]/text()')
    #amtraised_ext = [t.strip() for t in amtraised.extract()]

    goalamt = response.xpath('//span[contains(@class, "text-stat-title")]/text()')
    goalamt_ext = [t.strip() for t in goalamt.extract()]

    #donorsamt = response.xpath('//span[contains(@class, "text-stat-value") and contains(@class, "text-underline") and contains(@class, "u-pointer")]/text()')   #//div[contains(@class, 'class1') and contains(@class, 'class2')]
    #donorsamt_ext = [t.strip() for t in donorsamt.extract()]

    #sharesamt = donorsamt.xpath('//span[contains(@class, "text-stat-value")]/span/text()')
    #sharesamt_ext = [t.strip() for t in sharesamt.extract()]


    info = [camptitle_ext, description_ext, goalamt_ext] #byline_ext, created_ext, extra_ext, amtraised_ext, goalamt_ext, donorsamt_ext, sharesamt_ext]
    self.zipdict[urlsolid_ext] = info
    zipcollect = pd.DataFrame(self.zipdict)

    #gendataframe = pd.DataFrame([camptitle_ext, description_ext, sidebar_ext, byline_ext, created_ext, extra_ext], index =['title', 'description', 'sidebar', 'byline', 'created', 'extra'], 
                                              #columns =[str(camptitle_ext)]) 

    export_csv = zipcollect.to_csv (r'C:\Users\Claire\Desktop\d{}.csv'.format(urlsolid_ext), index = True, header=True)

    urlhist = 'https://gateway.gofundme.com/web-gateway/v1/feed/{}/donations?limit=1000'.format(urlsolid_ext)

    yield response.follow(url = urlhist,
                            callback = self.parse_donation_hist)










process = CrawlerProcess()
process.crawl(gfm_Spider)
process.start()