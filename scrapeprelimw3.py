
import scrapy
import json

#https://www.gofundme.com/mvc.php?route=categorypages/load_more&page=4&term=&cid=11 i think this is the json i need

# Import the CrawlerProcess: for running the spider
from scrapy.crawler import CrawlerProcess

# Create the Spider class
class gfm_Spider(scrapy.Spider):
  name = "gfm_spider"

  custom_settings = {
    'USER_AGENT' : 'gfm_spider',
    }
  #https://stackoverflow.com/questions/46746701/crawling-with-scrapy-http-status-code-is-not-handled-or-not-allowed

  # start_requests method
  def start_requests(self):
    allowed_domains = ['gofundme.com']
    url1 = "https://www.gofundme.com/mvc.php?route=categorypages/load_more&page=2&term=&cid=11"
    print("initiating requests")
    yield scrapy.Request(url = url1,
                         callback = self.parse_front)
  # First parsing method
  def parse_front(self, response):
    tile = response.css('div.react-campaign-tile') #this is getting each tile 
    tile_links = tile.xpath('./a/@href') #this gets links to individual campaigns 
    links_to_follow = tile_links.extract()
    print(links_to_follow)


# Run the Spider
process = CrawlerProcess()
process.crawl(gfm_Spider)
process.start()

# Print a preview of courses