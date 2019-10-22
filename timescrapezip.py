import scrapy
import pandas as pd
from scrapy.crawler import CrawlerProcess

# Create the Spider class
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
    url1 = "https://www.gofundme.com/mvc.php?route=homepage_norma/search&term=36206&country=US&locationText=&postalCode=36206"
    print("initiating requests")
    yield scrapy.Request(url = url1,
                         callback = self.parse_front)
  
  def parse_front(self, response):
    tile = response.css('div.react-campaign-tile') #this is getting each tile
    tile_links = tile.xpath('./a/@href') #this gets links to individual campaigns 
    links_to_follow = tile_links.extract()
    print(links_to_follow)
    for url in links_to_follow:
      yield response.follow(url = url,
                            callback = self.parse_pages)

  def parse_pages(self, response):
    camptitle = response.xpath('//h1[contains(@class,"campaign-title")]/text()')
    camptitle_ext = camptitle.extract_first().strip()
    #description = response.css('div.co-story truncate-text truncate-text--description js-truncate::text')
    description = response.xpath('//div[contains(@class, "o-campaign-story")]/text()')
    description_ext = [t.strip() for t in description.extract()]
    sidebar = response.xpath('//div[contains(@class, "o-campaign-sidebar-notification")]/text()')
    sidebar_ext = [t.strip() for t in sidebar.extract()]
    byline = response.xpath('//div[contains(@class, "m-campaign-byline-description")]/text()')
    byline_ext = [t.strip() for t in byline.extract()]
    created = response.xpath('//span[contains(@class, "m-campaign-byline-created")]/text()')
    created_ext = [t.strip() for t in created.extract()]
    extra = response.xpath('//div[contains(@class, "text-small")]//div/text()')
    extra_ext = [t.strip() for t in extra.extract()]

    info = [camptitle_ext, description_ext, sidebar_ext, byline_ext, created_ext, extra_ext]
    self.zipdict[camptitle_ext] = info
    df36206 = pd.DataFrame(self.zipdict)

    #df36206 = pd.DataFrame([camptitle_ext, description_ext, sidebar_ext, byline_ext, created_ext, extra_ext], index =['title', 'description', 'sidebar', 'byline', 'created', 'extra'], 
                                              #columns =[str(camptitle_ext)]) 
    print(df36206)

    export_csv = df36206.to_csv (r'C:\Users\Claire\Desktop\df36206.csv', index = True, header=True)


process = CrawlerProcess()
process.crawl(gfm_Spider)
process.start()



    #print(description_ext)


    #this part is collecting the individual donations for a certain campaign
    
    #names = response.xpath('.//div[@class = "m-comment-description"]/text()')
    #names = response.xpath('.//div[contains(@class, "person-info-content")]/div/span/text()')
    #names_ext = names.extract()
    #amounts = response.xpath('.//div[contains(@class, "person-info-content")]//span[contains(@class, "weight-900")]/text()')
    #amounts_ext = amounts.extract()
    #amounts_ext = [t.strip() for t in amounts.extract()]
    #print(names_ext)
    #print(amounts_ext)
    #times = response.xpath('.//div[@class = "supporter-time"]/text()')
    #time_ext = [t.strip() for t in times.extract()]
    #donations = [amounts_ext, names_ext] #add time_ext
    #print(donations)
    #print(description_ext)
    #dc_dict[camptitle_ext] = donations
    #print(dc_dict)

    #last link to follow for final parse method to get all donations including not yet displayed


#dc_dict = dict()

'''
# Run the Spider
process = CrawlerProcess()
process.crawl(gfm_Spider)
process.start()

# Print a preview of courses
#previewCourses(dc_dict)

# Import scrapy
import scrapy

# Import the CrawlerProcess: for running the spider
from scrapy.crawler import CrawlerProcess

# Create the Spider class
class gfm_Spider(scrapy.Spider):
  name = "gfm_spider"
  dc_dict = {}
  description = []

  custom_settings = {
    'USER_AGENT' : 'gfm_spider',
    }
  #https://stackoverflow.com/questions/46746701/crawling-with-scrapy-http-status-code-is-not-handled-or-not-allowed

  # start_requests method
  def start_requests(self):
    allowed_domains = ['gofundme.com/discover']
    url1 = "https://www.gofundme.com/discover"
    print("initiating requests")
    yield scrapy.Request(url = url1,
                         callback = self.parse_front)
  # First parsing method
  def parse_front(self, response):
    tile = response.css('div.react-campaign-tile') #this is getting each tile
    print("this is a " + str(tile))
    tile_links = tile.xpath('./a/@href') #this gets links to individual campaigns 
    links_to_follow = tile_links.extract()
    #print(links_to_follow)
    for url in links_to_follow:
      yield response.follow(url = url,
                            callback = self.parse_pages)
  # Second parsing method
  def parse_pages(self, response):
    camptitle = response.xpath('//h1[contains(@class,"campaign-title")]/text()')

    camptitle_ext = camptitle.extract_first().strip()
    print(camptitle_ext)
    #description = response.css('div.co-story truncate-text truncate-text--description js-truncate::text')
    description = response.xpath('//div[contains(@class, "o-campaign-story")]/text()')

    description_ext = [t.strip() for t in description.extract()]
    #print(description_ext)


    #this part is collecting the individual donations for a certain campaign
    
    #names = response.xpath('.//div[@class = "m-comment-description"]/text()')
    names = response.xpath('.//div[contains(@class, "person-info-content")]/div/span/text()')
    names_ext = names.extract()
    amounts = response.xpath('.//div[contains(@class, "person-info-content")]//span[contains(@class, "weight-900")]/text()')
    amounts_ext = amounts.extract()
    #amounts_ext = [t.strip() for t in amounts.extract()]
    print(names_ext)
    print(amounts_ext)
    #times = response.xpath('.//div[@class = "supporter-time"]/text()')
    #time_ext = [t.strip() for t in times.extract()]
    donations = [amounts_ext, names_ext] #add time_ext
    print(donations)
    #print(description_ext)
    dc_dict[camptitle_ext] = donations
    print(dc_dict)

    #last link to follow for final parse method to get all donations including not yet displayed

# Initialize the dictionary **outside** of the Spider class
dc_dict = dict()


# Run the Spider
process = CrawlerProcess()
process.crawl(gfm_Spider)
process.start()

# Print a preview of courses
#previewCourses(dc_dict)

# Create the Spider class
class gfm_Spider(scrapy.Spider):
  name = "gfm_spider"
  dc_dict = {}
  description = []

  custom_settings = {
    'USER_AGENT' : 'gfm_spider',
    }
  #https://stackoverflow.com/questions/46746701/crawling-with-scrapy-http-status-code-is-not-handled-or-not-allowed

  # start_requests method
  def start_requests(self):
    allowed_domains = ['gofundme.com/discover']
    url1 = "https://www.gofundme.com/discover"
    print("initiating requests")
    yield scrapy.Request(url = url1,
                         callback = self.parse_front)
  # First parsing method
  def parse_front(self, response):
    tile = response.css('div.react-campaign-tile') #this is getting each tile
    print("this is a " + str(tile))
    tile_links = tile.xpath('./a/@href') #this gets links to individual campaigns 
    links_to_follow = tile_links.extract()
    #print(links_to_follow)
    for url in links_to_follow:
      yield response.follow(url = url,
                            callback = self.parse_pages)
  # Second parsing method
  def parse_pages(self, response):
    camptitle = response.xpath('//h1[contains(@class,"campaign-title")]/text()')

    camptitle_ext = camptitle.extract_first().strip()
    print(camptitle_ext)
    #description = response.css('div.co-story truncate-text truncate-text--description js-truncate::text')
    description = response.xpath('//div[contains(@class, "o-campaign-story")]/text()')

    description_ext = [t.strip() for t in description.extract()]
    #print(description_ext)


    #this part is collecting the individual donations for a certain campaign
    
    #names = response.xpath('.//div[@class = "m-comment-description"]/text()')
    names = response.xpath('.//div[contains(@class, "person-info-content")]/div/span/text()')
    names_ext = names.extract()
    amounts = response.xpath('.//div[contains(@class, "person-info-content")]//span[contains(@class, "weight-900")]/text()')
    amounts_ext = amounts.extract()
    #amounts_ext = [t.strip() for t in amounts.extract()]
    print(names_ext)
    print(amounts_ext)
    #times = response.xpath('.//div[@class = "supporter-time"]/text()')
    #time_ext = [t.strip() for t in times.extract()]
    donations = [amounts_ext, names_ext] #add time_ext
    print(donations)
    #print(description_ext)
    dc_dict[camptitle_ext] = donations
    print(dc_dict)

    #last link to follow for final parse method to get all donations including not yet displayed

# Initialize the dictionary **outside** of the Spider class
dc_dict = dict()


# Run the Spider
process = CrawlerProcess()
process.crawl(gfm_Spider)
process.start()

# Print a preview of courses
#previewCourses(dc_dict)

'''