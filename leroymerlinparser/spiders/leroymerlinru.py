import scrapy
from scrapy.http import HtmlResponse
from leroymerlinparser.items import LeroymerlinparserItem
from scrapy.loader import ItemLoader


class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, **kwargs):
        super().__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={kwargs.get("search")}']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@data-qa-pagination-item='right']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[@data-qa='product-name']")
        for link in links:
            yield response.follow(link, callback=self.parse_product)

    def parse_product(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroymerlinparserItem(), response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('_id', '//div[@class="product-detailed-page"]/@data-product-id')
        loader.add_xpath('name', '//div[@class="product-detailed-page"]/@data-product-name')
        loader.add_xpath('price', '//div[@class="product-detailed-page"]/@data-product-price')
        loader.add_xpath('photos', '//img[@alt="product image"]/@src')
        loader.add_xpath('chars_key', '//dt//text()')
        loader.add_xpath('chars_value', '//dd//text()')
        yield loader.load_item()