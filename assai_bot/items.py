# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AssaiBotAnimeItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    producer = scrapy.Field()
    pictureLink = scrapy.Field()
    tags = scrapy.Field()
    description = scrapy.Field()
    seasons = scrapy.Field()


class AssaiBotSeasonsItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    producer = scrapy.Field()
    pictureLink = scrapy.Field()
    tags = scrapy.Field()
    description = scrapy.Field()
