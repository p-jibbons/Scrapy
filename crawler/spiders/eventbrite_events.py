from __future__ import absolute_import
from scrapy.spiders import Spider

from scrapy import Request, FormRequest
from ..items import eventPageItem
from datetime import date, timedelta,datetime
import json





class eventbrite_events(Spider):
    name = "eventbrite_events"
    allowed_domains = []
    download_timeout = 30


    def start_requests(self):
        self.startdate = date.today()
        self.startdate = date.today() + timedelta(days = 3)
        self.city = "ca--san-diego"



        start_date_short = self.startdate.strftime("%Y-%m-%d")
        end_date_short = self.startdate.strftime("%Y-%m-%d")



        self.url = f"https://www.eventbrite.com/d/{self.city}/all-events/?start_date={start_date_short}&end_date={end_date_short}"
        print(self.url)
        yield Request(self.url, callback=self.parse, meta={
                                'start_date_short': start_date_short,
                                'end_date_short': end_date_short})



    def parse(self, response):

        start_date_short = response.meta.get("start_date_short")
        end_date_short = response.meta.get("end_date_short")
        city_id = "85922227"
        csrf = response.xpath("//input[@name='csrfmiddlewaretoken']/@value").extract_first()

        headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': response.url,
            'X-CSRFToken': csrf
        }

        data = {"event_search": {
            "dates": "current_future", "date_range": {"to": start_date_short, "from": end_date_short},
            "places": [city_id], "page": 1, "page_size": 1, "online_events_only": False},
            "expand.destination_event": ["primary_venue", "image", "ticket_availability", "saves", "series",
                                         "my_collections", "event_sales_status"]}

        self.url = "https://www.eventbrite.com/api/v3/destination/search/"
        yield Request(self.url, method="POST", callback=self.parse_listing, headers=headers, body=json.dumps(data),
                      meta={"headers": headers, "data": data}, dont_filter=True)



    def parse_listing(self, response):

        headers = response.meta.get("headers")
        data = response.meta.get("data")

        jresp = json.loads(response.body)


        for e in jresp.get("events").get("results"):
            #print(e.get("name"))
            items = eventPageItem()

            #summary of event details
            items['event_source'] = 'eventbrite'
            items['event_source_id'] = e.get("series_id", {})
            items['event_source_url'] = e.get("url", {})
            items['title'] = e.get("name", {})
            items['is_cancelled'] = e.get("is_cancelled", {})
            items['published']=e.get("published", {})
            items['summary'] = e.get("summary", {})
            items['image_url'] = e.get("image", {}).get("url", {})

            #sale status
            items['default_message'] = e.get("event_sales_status",   {}).get("default_message",{})
            items['sales_status'] = e.get("event_sales_status",  {}).get("sales_status",{})
            items['message'] = e.get("event_sales_status",  {}).get("message",{})
            items['message_code'] = e.get("event_sales_status",  {}).get("message_code",{})
            items['message_type'] = e.get("event_sales_status",  {}).get("message_type",{})
            items['is_sold_out'] = e.get("ticket_availability",  {}).get("is_sold_out",{})
            items['is_free'] = e.get("ticket_availability",  {}).get("is_free",{})

            try:
                items['min_ticket_price'] = e.get("ticket_availability", {}).get("minimum_ticket_price", {}).get(
                    "major_value", {})
            except AttributeError:
                pass

            try:
                items['max_ticket_price'] = e.get("ticket_availability", {}).get("maximum_ticket_price", {}).get("major_value", {})
            except AttributeError:
                pass


            #items['max_ticket_price'] = e.get("ticket_availability",  {}).get("maximum_ticket_price", {}).get("major_value",{})
            items['tickets_url'] = e.get("tickets_url")
            items['tickets_by'] = e.get("tickets_by")


            #date and time
            items['start_date'] = e.get("start_date", {})
            items['start_time'] = e.get("start_time", {})
            items['end_date'] = e.get("end_date", {})
            items['end_time'] = e.get("end_time", {})

            #address data
            items['country'] = e.get("primary_venue", {}).get("address", {}).get("country", {})
            items['region'] = e.get("primary_venue", {}).get("address", {}).get("california", {})
            items['city'] = e.get("primary_venue", {}).get("address", {}).get("city", {})
            items['postal_code'] = e.get("primary_venue", {}).get("address", {}).get("postal_code", {})
            items['localized_address_display'] = e.get("primary_venue", {}).get("address", {}).get("localized_address_display", {})
            items['localized_area_display'] = e.get("primary_venue", {}).get("address", {}).get("localized_area_display", {})
            items['address_1'] = e.get("primary_venue", {}).get("address", {}).get("address_1", {})
            items['latitude']=e.get("primary_venue", {}).get("address", {}).get("latitude", {})
            items['longitude']=e.get("primary_venue", {}).get("address", {}).get("longitude", {})

            #venue details
            items['venue_name'] = e.get("primary_venue", {}).get("name", {})
            items['venue_profile_url'] = e.get("primary_venue", {}).get("venue_profile_url", {})
            items['source_venue_id'] = e.get("primary_venue", {}).get("id", {})
            items['venue_age_restrictions'] = e.get("primary_venue", {}).get("age_restriction", {})

            items['categories'] = ', '.join([_.get("display_name", {}) for _ in e.get("tags", {})])
            #print(items)
            print(e.get("start_date", {}) + ' ' + e.get("name", {}))

            yield (items)
        #loop through all pages
        page_number = jresp.get("events").get("pagination").get("page_number")
        page_count = jresp.get("events").get("pagination").get("page_count")

        if page_number == 1:

            for page_number in range(2, page_count + 1):
                data["event_search"]["page"] = page_number

                yield Request(self.url, method="POST", callback=self.parse_listing, headers=headers,
                              body=json.dumps(data), meta={"headers": headers, "data": data}, dont_filter=True)

