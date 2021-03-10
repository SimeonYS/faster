import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import FasterItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class FasterSpider(scrapy.Spider):
	name = 'faster'
	start_urls = ['https://www.faster.dk/nyheder/']

	def parse(self, response):
		post_links = response.xpath('//nav[@class="list-group mt-3"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_links)

	def parse_links(self, response):
		links = response.xpath('//nav[@class="list-group mt-3"]/a/@href').getall()[1:]
		date = response.xpath('//nav[@class="list-group mt-3"]/a/text()').get()
		yield from response.follow_all(links, self.parse_post,cb_kwargs=dict(date=date))

	def parse_post(self, response,date):
		title = response.xpath('//h1/text()').get().strip()
		content = response.xpath('//p[@class="manchet"]//text()').getall() + response.xpath('//div[@class="rte"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=FasterItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
