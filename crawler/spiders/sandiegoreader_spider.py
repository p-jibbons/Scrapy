# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from datetime import datetime, timedelta,date
from ..items import eventPageItem
import re
from urllib.parse import urlparse

def try_parsing_date(text):
    for fmt in ('%I:%M%p', '%I%p'):
        try:
            return datetime.strptime(text,fmt).time()
        except ValueError:
            pass
    raise ValueError('no valid date format found')

class SandiegoreaderSpiderSpider(scrapy.Spider):
    name = 'sandiegoreader_spider'
    allowed_domains = ['sandiegoreader.com']
    today =(date.today() - timedelta(days=365)).strftime('%Y/%b/%d').lower()
    start_urls = ['https://www.sandiegoreader.com/events/'+today + '/']

    def parse(self, response):

        request_url = (response.request.url).strip('https://www.sandiegoreader.com/events/')
        events_date = datetime.strptime(request_url, '%Y/%b/%d')
        allDays = response.xpath('//div[@class = "all-class-listed restaurants-listed"]')
        day_list= allDays.xpath('//div[@class = "events-date"]')
        event_list = response.xpath('//div[@class = "event-item event-item-single"]')
        for event in event_list:
            event_title = event.xpath('div[@class="event-single-top"]/div[@class= "event-content event-content-single"]/a[@class="event-title"]/text()').extract_first()
            venue_neighbourhood = event.xpath('div[@class="event-single-top"]/div[@class= "event-content event-content-single"]/a[@class="event-place w-inline-block"]/div[@class="event-location"]/text()').extract_first()
            scrape_source_url = event.xpath('div[@class="event-single-top"]/div[@class= "event-content event-content-single"]/a[@class="event-title"]/@href').extract_first()
            absolute_url = 'https://www.sandiegoreader.com' + scrape_source_url

            time_string = event.xpath('div[@class="event-single-top"]/div[@class="event-time event-time-single"]/div/text()').get()
            split_list = time_string.split(u"–")
            len_time_list = len(split_list)

            if len_time_list == 1:
                start_time = try_parsing_date(split_list[0])
                # end_time = try_parsing_date(split_list[0])
                end_time = None

            elif len_time_list == 2:
                start_time = try_parsing_date(split_list[0])
                end_time = try_parsing_date(split_list[1])


            yield Request(absolute_url, callback=self.parse_page
                          ,
                                  meta={
                                        'event_title': event_title,
                                        'events_date':events_date,
                                        'venue_neighbourhood': venue_neighbourhood,
                                        'start_time': start_time,
                                        'end_time': end_time,
                                        'absolute_url': absolute_url
                                        }
                          )
        relative_next_url = response.xpath('//a[text()="Next"]/@href').extract_first()
        absolute_next_url = "https://www.sandiegoreader.com" + relative_next_url
        yield Request(absolute_next_url, callback=self.parse)

    def parse_page(self, response):

        venue_neighbourhood = response.meta.get('venue_neighbourhood')
        start_time = response.meta.get('start_time')
        end_time = response.meta.get('end_time')
        absolute_url = response.meta.get('absolute_url')
        events_date = response.meta.get('events_date')

        body = response.xpath('//div[@class="content_info"]')
        event_title = body.xpath('h2/text()').extract_first()
        details=body.xpath('//ul[@class="details"]')

        event_description = body.xpath('div[not(@class)]/p/text()')
        if len(event_description) > 0:
            event_description = body.xpath('div[not(@class)]/p/text()').getall()
            event_description = ' '.join(event_description)
        else:
            event_description = ''

        cost_string = details.xpath('li/strong[text()="Cost:"]/../text()')
        if len(cost_string) > 0:
            cost_string = details.xpath('li/strong[text()="Cost:"]/../text()').extract()
            cost_string = cost_string[1].strip().splitlines()[0]
        else:
            cost_string = ''

        numbers = re.findall('\d+', cost_string)
        # TODO numbers = map(int, numbers)
        if len(numbers) >0:
            cost_min_extract = min(numbers)
            cost_max_extract = max(numbers)
            cost_is_free = False
        else:
            cost_min_extract = None
            cost_max_extract = None
            cost_is_free = None

        if "Free" in cost_string:
            cost_min_extract = 0
            cost_is_free = True

        age_restrictions_string = details.xpath('//li/strong[text()="Age limit:"]/following-sibling::span/text()')
        if len(age_restrictions_string) > 0:
            age_restrictions_string = details.xpath('//li/strong[text()="Age limit:"]/following-sibling::span/text()').extract_first()
        else:
            age_restrictions_string = ''

        event_datetime_string = details.xpath('//li/strong[text()="When:"]/following-sibling::span/text()')
        if len(event_datetime_string) > 0:
            event_datetime_string = details.xpath('//li/strong[text()="When:"]/following-sibling::span/text()').get()
            event_datetime_string = event_datetime_string.strip()
        else:
            event_datetime_string = ''

        venue_name = details.xpath('//li/strong[text()="Where:"]/following-sibling::div/span/strong/a/text()').get(default='')
        venue_url = "https://www.sandiegoreader.com" + details.xpath('//li/strong[text()="Where:"]/following-sibling::div/span/strong/a/@href').get(default='')
        if venue_url == 'https://www.sandiegoreader.com':
            venue_url = ''

        venue_address_string = details.xpath('//li/strong[text()="Where:"]/following-sibling::div/p/text()').get(default = '' ).strip('\n')

        regex = re.compile(u'\d{5}')
        if re.search(regex, venue_address_string) :
            venue_postal_code = re.search(regex, venue_address_string).group(0)
        else:
            venue_postal_code = ''

        venue_gmap_url = details.xpath('li/strong[text()="Where:"]/following-sibling::div/p/a/@href').get(default='').replace(" ", "+")
        buy_tickets_url = details.xpath('//a[@class="buy_tickets"]/@href').get(default = "")

        if buy_tickets_url:
            tickets_by = urlparse(buy_tickets_url).hostname
        else:
            tickets_by=None

        image_original_url= response.xpath('//div[@class= "thumbnail-container"]/img/@src').extract_first()

        items = eventPageItem()
        items['event_title'] = event_title
        items['event_description'] =  event_description
        items['image_original_url'] = [image_original_url]
        items['start_date'] =  events_date
        items['end_date'] = events_date
        items['start_time'] =  start_time
        items['end_time'] = end_time
        items['event_datetime_string'] = event_datetime_string
        items['scrape_source_name'] = u'sandiegoreader'
        items['scrape_source_url'] = absolute_url
        items['buy_tickets_url'] = buy_tickets_url
        items['tickets_by'] = tickets_by
        items['tickets_sold_out'] = False


        items['venue_name'] = venue_name
        items['venue_url'] = venue_url
        items['venue_address_string'] = venue_address_string
        items['venue_city'] = u'San Diego'
        items['venue_state'] = u'CA'
        items['venue_country'] = u'US'
        items['venue_postal_code'] = venue_postal_code

        items['venue_neighbourhood'] = venue_neighbourhood
        items['venue_gmap_url'] = venue_gmap_url
        items['cost_string'] = cost_string
        items['cost_min_extract'] = cost_min_extract
        items['cost_max_extract'] = cost_max_extract
        items['cost_is_free'] = cost_is_free
        items['age_restrictions_string'] = age_restrictions_string

        items['spider_name'] = self.name
        items['spider_scrape_datetime'] = datetime.now()
        items['date_added'] = date.today()

        yield items



