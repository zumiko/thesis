
import scrapy
import json

#https://www.gofundme.com/mvc.php?route=categorypages/load_more&page=4&term=&cid=11 i think this is the json i need

# Import the CrawlerProcess: for running the spider
from scrapy.crawler import CrawlerProcess



# Create the Spider class
class gfm_Spider(scrapy.Spider):
  name = "gfm_spider"
  i = 1
  j = 0
  rep = str(i)
  allinks = []
  custom_settings = {
    'USER_AGENT' : 'gfm_spider',
    }
  #https://stackoverflow.com/questions/46746701/crawling-with-scrapy-http-status-code-is-not-handled-or-not-allowed

  #def __init__(self, allinks): 

    #self.allinks = allinks
  # start_requests method

  def duplicate_rule(self, links): #checking to see that each link has a duplicate
    print("checking duplicates")
    countlinks = len(links)
    uniquelinks = len(set(links)) 
    print("total links = " + str(countlinks))
    print("unique links = " + str(uniquelinks))

  def start_requests(self):
    allowed_domains = ['gofundme.com']
    #url1 = "https://www.gofundme.com/mvc.php?route=categorypages/load_more&page=1&term=&cid=11"
    
    while self.i <= 30: 
      url1 = "https://www.gofundme.com/mvc.php?route=categorypages/load_more&page=%s&term=&cid=11" %(self.i) # you can prob just make load more pages high and not have to worry about iterating
      #url1 = list(url1)   
      #url1[68] = str(self.i)  #iterating through pages
      #url1 = "".join(url1)    
      print("initiating request" + str(self.i))
      print(url1)
      yield scrapy.Request(url = url1,
                           callback = self.parse_front)

      self.i += 1 
  # First parsing method
  def parse_front(self, response):
    print("this is parse number " + str(self.i))
    tile = response.css('div.react-campaign-tile') #this is getting each tile 
    tile_links = tile.xpath('./a/@href') #this gets links to individual campaigns 
    links_to_follow = tile_links.extract()
    self.allinks.extend(links_to_follow) # used to say append
    if self.i >= 28:
      print(self.allinks)
    self.duplicate_rule(self.allinks)








#running spyder
process = CrawlerProcess()
process.crawl(gfm_Spider)
process.start()
