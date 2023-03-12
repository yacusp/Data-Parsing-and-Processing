import scrapy


class InstaparserItem(scrapy.Item):
    user_parser_name = scrapy.Field()
    user_id = scrapy.Field()
    username = scrapy.Field()
    photo = scrapy.Field()
    user_type = scrapy.Field()
    _id = scrapy.Field()