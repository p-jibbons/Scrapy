from __future__ import absolute_import
from scrapy.spiders import Spider

from scrapy import Request, FormRequest
from ..items import eventPageItem
from datetime import date, timedelta,datetime
from urllib.parse import urlparse
import dateutil.parser
import re





class eventbrite_events(Spider):
    name = "eventbrite_events"
    # allowed_domains = ['eventbrite.com','img.evbuc.com','evbuc.com']

    start_date_short =(date.today()).strftime("%Y-%m-%d")
    end_date_short = (date.today()+ timedelta(days = 10)).strftime("%Y-%m-%d")
    i=1
    url_start =f"https://www.eventbrite.com/d/ca--san-diego/all-events/?start_date={start_date_short}&end_date={end_date_short}&page=1"
    start_urls = [url_start]

    def parse(self, response):
        print("scraping")



        event_list = response.xpath('.//ul[@class="search-main-content__events-list"]/li')

        for event in event_list:
            event_card = event.xpath('.//div[@class="eds-event-card-content__content__principal"]')
            event_datetime_string = event_card.xpath('.//div[@class="eds-text-color--primary-brand eds-l-pad-bot-1 eds-text-weight--heavy eds-text-bs"]/text()').extract_first(default = '')
            event_title = event_card.xpath('.//div[@data-spec="event-card__formatted-name--content"]/text()').extract_first(default='')


            scrape_source_url = event_card.xpath('.//a[@class="eds-event-card-content__action-link"]/@href').extract_first()
            # print(scrape_source_url)
            absolute_url= urlparse(scrape_source_url).netloc + urlparse(scrape_source_url).path

            yield Request(scrape_source_url, callback=self.parse_page,
                                  meta={
                                        'event_datetime_string': event_datetime_string,
                                        'event_title':event_title,
                                        'absolute_url':absolute_url
                                        }
                          )
        self.i = self.i +1
        today = (date.today() - timedelta(days=365)).strftime('%Y/%b/%d').lower()
        start_date_short = (date.today()).strftime("%Y-%m-%d")
        end_date_short = (date.today() + timedelta(days=3)).strftime("%Y-%m-%d")
        absolute_next_url = f"https://www.eventbrite.com/d/ca--san-diego/all-events/?start_date={self.start_date_short}&end_date={self.end_date_short}&page={str(self.i)}"

        yield Request(absolute_next_url, callback=self.parse)


    def parse_page(self, response):
        event_title = response.meta.get('event_title')
        print(event_title)
        # print(response)
        sidebar = response.xpath('.//div[@class="event-details hide-small"]')

        # need to extract from previous page
        # venue_neighbourhood = response.meta.get('venue_neighbourhood')

        date_time_tuple = sidebar.xpath('.//div[@class="event-details__data"]/meta/@content').extract()
        if len(date_time_tuple)==2:
            start_date = dateutil.parser.isoparse(date_time_tuple[0]).strftime("%Y-%m-%d")
            end_date = dateutil.parser.isoparse(date_time_tuple[1]).strftime("%Y-%m-%d")
            start_time = dateutil.parser.isoparse(date_time_tuple[0]).time()
            end_time = dateutil.parser.isoparse(date_time_tuple[1]).time()
        else:
            start_date = None
            end_date = None
            start_time = None
            end_time = None


        absolute_url = response.meta.get('absolute_url')
        # events_date = response.meta.get('events_date')

        event_description = response.xpath('//div[contains(@class,"has-user-generated-content")]//text()').extract()

        event_description = [item for item in event_description if item not in [ 'Read more','\t','Read less']]
        event_description= ''.join(event_description)
        event_description = re.sub('\t', '', event_description).strip()


        cost_string = response.xpath('.//div[@class="js-display-price"]/text()').extract_first()
        if cost_string:
            cost_string = cost_string.strip()



            numbers = re.findall('\d+', cost_string)

            # dont know why this line doesnt work, the re expression already converted them to ints?
            # numbers = map(int, numbers)
            cost_min_extract = None
            cost_max_extract = None
            cost_is_free = None
            if len(numbers) > 0:
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

        #need to verify with more scraping
        # age_restrictions_string = response.xpath('//span[@class="text-body-medium text-body--faint"]/text()').extract()
        # if len(age_restrictions_string) > 0:
        #     age_restrictions_string = details.xpath(
        #         '//li/strong[text()="Age limit:"]/following-sibling::span/text()').extract_first()
        # else:
        #     age_restrictions_string = ''
        #


        event_datetime_string = response.meta.get('event_datetime_string')

        #
        venue_name = response.xpath('//a[@class="js-d-scroll-to listing-organizer-name text-default"]/text()').extract_first(default='By ').strip()[3:]


        # venue_address_string = response.xpath('//h3[text()="Location"]/following-sibling::div/p/text()')
        venue_address_string = response.xpath('//h3[text()="Location"]/following-sibling::div')
        if len(venue_address_string)>0:
            venue_address_string = venue_address_string.xpath('.//p/text()').extract()
            if "\n\t\t\t\t\t\t\t\t\t\t" in venue_address_string:
                cutoff = venue_address_string.index("\n\t\t\t\t\t\t\t\t\t\t")
                venue_address_string = venue_address_string[0:cutoff]
            venue_address_string = '\n'.join(venue_address_string)



        regex = re.compile(u'\d{5}')
        if venue_address_string and re.search(regex, venue_address_string):
            venue_postal_code = re.search(regex, venue_address_string).group(0)
        else:
            venue_postal_code = ''
        venue_gmap_url = response.xpath('.//a[@class="listing-map-link js-listing-map-link btn btn--dynamo"]/@href').extract_first(default='').replace(" ", "+")
        buy_tickets_url = absolute_url


        tickets_by = u'eventbrite'

        venue_latitude = response.xpath('.//meta[@property="event:location:latitude"]/@content').extract_first(default='')
        venue_longitude = response.xpath('.//meta[@property="event:location:longitude"]/@content').extract_first(default='')





        image_original_url= response.xpath('//div[@class= "listing-hero listing-hero--bkg clrfix fx--delay-6 fx--fade-in"]/picture/@content').extract_first()
        # print(image_original_url)



        items = eventPageItem()
        items['event_title'] = event_title
        items['event_description'] = event_description
        items['image_original_url'] = [image_original_url]
        # items['image_urls'] = [image_original_url]

        items['start_date'] = start_date
        items['end_date'] = end_date
        items['start_time'] = start_time
        items['end_time'] = end_time
        items['event_datetime_string'] = event_datetime_string
        items['scrape_source_name'] = u'eventbrite'
        items['scrape_source_url'] = absolute_url
        items['buy_tickets_url'] = buy_tickets_url
        items['tickets_by'] = tickets_by
        items['tickets_sold_out'] = False

        items['venue_name'] = venue_name
        # items['venue_url'] = venue_url
        items['venue_address_string'] = venue_address_string
        items['venue_city'] = u'San Diego'
        items['venue_state'] = u'CA'
        items['venue_country'] = u'US'
        items['venue_postal_code'] = venue_postal_code
        items['venue_latitude'] = venue_latitude
        items['venue_longitude'] = venue_longitude

        # items['venue_neighbourhood'] = venue_neighbourhood
        items['venue_gmap_url'] = venue_gmap_url
        items['cost_string'] = cost_string
        items['cost_min_extract'] = cost_min_extract
        items['cost_max_extract'] = cost_max_extract
        items['cost_is_free'] = cost_is_free
        items['age_restrictions_string'] = ''

        items['spider_name'] = self.name
        items['spider_scrape_datetime'] = datetime.now()
        items['date_added'] = date.today()

        yield(items)




