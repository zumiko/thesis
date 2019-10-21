
import scrapy
import json
import random
from scrapy.crawler import CrawlerProcess


#list of categories: 
#medical: cid=11
#memorial: cid=9
#emergency: cid=2
#nonprofit: cid=13
#education: cid=17
#animals: cid=3
#business: cid=5
#community: cid=7
#competition: cid=19
#creative: cid=8
#event: cid=6 
#faith: cid=12
#family: cid=4
#newlywed: cid=14
#sports: cid=16
#travel: cid=10
#volunter: cid=18
#wishes: cid=20




class gfm_Spider(scrapy.Spider):
  name = "gfm_spider"
  i = 1
  allinks = []
  custom_settings = {
    'USER_AGENT' : 'gfm_spider',
    }
  #https://stackoverflow.com/questions/46746701/crawling-with-scrapy-http-status-code-is-not-handled-or-not-allowed

  def duplicate_rule(self, links): #checking to see that each link has a duplicate
    print("checking duplicates")
    countlinks = len(links)
    uniquelinks = len(set(links)) 
    print("total links = " + str(countlinks))
    print("unique links = " + str(uniquelinks))
    if uniquelinks == countlinks: 
      return True 
    else: 
      return False

  def choose_random(self, links): 
    random.seed(9)
    randomlinks = random.sample(links, 10) #selecting 10 at random 
    print("this is the list" + str(randomlinks))
    print(randomlinks)



  def start_requests(self):
    allowed_domains = ['gofundme.com']
    #url1 = "https://www.gofundme.com/mvc.php?route=categorypages/load_more&page=1&term=&cid=11"
    
    while self.i <= 100: 
      url1 = "https://www.gofundme.com/mvc.php?route=categorypages/load_more&page=%s&term=&cid=2" %(self.i) # you can prob just make load more pages high and not have to worry about iterating 
      print("initiating request" + str(self.i))
      #print(url1)
      yield scrapy.Request(url = url1,
                           callback = self.parse_front)

      if self.i == 100: 
        self.choose_random(self.allinks)

      self.i += 1 



  # First parsing method
  def parse_front(self, response):
    print("this is parse number " + str(self.i))
    tile = response.css('div.react-campaign-tile') #this is getting each tile 
    tile_links = tile.xpath('./a/@href') #this gets links to individual campaigns 
    links_to_follow = tile_links.extract()
    self.allinks.extend(links_to_follow) 
    self.duplicate_rule(self.allinks)
    #if self.i >= 99:
      #print(self.allinks)
      
      
    








#run it
process = CrawlerProcess()
process.crawl(gfm_Spider)
process.start()
