# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


from scrapy import Field



class eventPageItem(scrapy.Item):
    # define the fields for your item here like:

    # text about event
    # event_sha1 = models.CharField(max_length=255)
    event_title = Field()
    event_description = Field()

    # time date properties
    start_date = Field()
    end_date = Field()
    start_time = Field()
    end_time = Field()
    event_datetime_string = Field()

    # event source properties
    scrape_source_name = Field()
    scrape_source_url = Field()
    original_source_name = Field()
    original_source_url = Field()

    # event ticket propeties
    buy_tickets_url = Field()
    tickets_by = Field()
    ticket_vendor_image_url = Field()
    tickets_sold_out = Field()

    # event location properties
    venue_name = Field()
    venue_url = Field()
    venue_event_url = Field()

    venue_address_string = Field()
    venue_address1 = Field()
    venue_address2 = Field()
    venue_city = Field()
    venue_state = Field()
    venue_country = Field()
    venue_postal_code = Field()
    venue_neighbourhood = Field()
    venue_latitude = Field()
    venue_longitude = Field()
    venue_gmap_url = Field()

    # event cost properties
    cost_string = Field()
    cost_min_extract = Field()
    cost_max_extract = Field()
    cost_is_free = Field()

    # event_meta_properties
    age_restrictions_string = Field()
    age_minimum = Field()
    is_cancelled = Field()

    # event image properties
    image_original_url = Field()
    image_s3_url = Field()
    image_height = Field()
    image_width = Field()
    image_urls= Field()
    images = Field()

    # event contact properties
    contact_phone = Field()
    contact_email = Field()

    # storagee meta properties
    spider_name = Field()
    spider_scrape_datetime = Field()
    date_added = Field()
    date_updated = Field()
    date_last_seen = Field()
    suspected_duplicate_event = Field()
    inappropriate_events = Field()

