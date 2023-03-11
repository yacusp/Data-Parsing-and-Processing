# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst


def clean_data(value):
    value = value.strip().replace('\xa0', '')
    return value


def to_float_price(value):
    try:
        value = float(value)
    except ValueError:
        pass
    return value


def to_format(value):
    if value.isdigit():
        return int(value)
    else:
        try:
            return float(value)
        except ValueError:
            if ', ' in value:
                return [value.split(', ')]
            else:
                return value


class LeroymerlinparserItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field(output_processor=TakeFirst())
    _id = scrapy.Field(output_processor=TakeFirst())
    name = scrapy.Field(input_processor=MapCompose(clean_data),
                        output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(clean_data, to_float_price),
                         output_processor=TakeFirst())
    photos = scrapy.Field()
    chars_key = scrapy.Field()
    chars_value = scrapy.Field(input_processor=MapCompose(clean_data, to_format))
    characteristics = scrapy.Field()