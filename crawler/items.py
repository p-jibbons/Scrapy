# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy



class eventPageItem(scrapy.Item):
    # define the fields for your item here like:
    # summary of event details
    event_source = scrapy.Field()
    event_source_id = scrapy.Field()
    event_source_url = scrapy.Field()
    title = scrapy.Field()
    is_cancelled = scrapy.Field()
    published = scrapy.Field()
    summary = scrapy.Field()
    image_url = scrapy.Field()
    default_message = scrapy.Field()
    sales_status = scrapy.Field()
    message = scrapy.Field()
    message_code = scrapy.Field()
    message_type = scrapy.Field()
    is_sold_out = scrapy.Field()
    is_free = scrapy.Field()
    min_ticket_price = scrapy.Field()
    max_ticket_price = scrapy.Field()
    tickets_url = scrapy.Field()
    tickets_by = scrapy.Field()
    start_date = scrapy.Field()
    start_time = scrapy.Field()
    end_date = scrapy.Field()
    end_time = scrapy.Field()
    country = scrapy.Field()
    region = scrapy.Field()
    city = scrapy.Field()
    postal_code = scrapy.Field()
    localized_address_display = scrapy.Field()
    localized_area_display = scrapy.Field()
    address_1 = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    venue_name = scrapy.Field()
    venue_profile_url = scrapy.Field()
    source_venue_id = scrapy.Field()
    venue_age_restrictions = scrapy.Field()
    categories = scrapy.Field()