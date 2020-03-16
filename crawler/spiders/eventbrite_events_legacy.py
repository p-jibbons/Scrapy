from __future__ import absolute_import
from scrapy.spiders import Spider

from scrapy import Request, FormRequest

from datetime import date, timedelta,datetime
import json

import time


from collections import OrderedDict
import xlsxwriter


class eventbrite_events_legacy(Spider):
    name = "eventbrite_events_legacy"
    allowed_domains = []
    download_timeout = 30


    def start_requests(self):

        conf = {}
        with open("eventbrite.conf", "r") as f:
            conf = json.loads(f.read())
        print(conf)
        self.city = conf.get("city", [])
        startdate = conf.get("startdate", "")
        enddate = conf.get("enddate", "")

        if startdate == "":
            self.startdate = datetime.today()
        else:
            self.startdate = datetime.strptime(startdate, "%m/%d/%Y")

        if enddate == "":
            self.enddate = datetime.today()
        else:
            self.enddate = datetime.strptime(enddate, "%m/%d/%Y")

        cursor = self.startdate
        while cursor <= self.enddate:
            print(cursor)
            date_short = cursor.strftime("%Y-%m-%d")

            for city in self.city:
                city_id = city.get("id")
                city_name = city.get("name")

                url = f"https://www.eventbrite.com/d/{city_name}/all-events/?start_date={date_short}&end_date={date_short}"
                yield Request(url, callback=self.parse,
                              meta={"date_short": date_short, "city_name": city_name, "city_id": city_id})

            cursor = cursor + timedelta(days=1)

    def parse(self, response):

        date_short = response.meta.get("date_short")
        city_name = response.meta.get("city_name")
        city_id = response.meta.get("city_id")
        csrf = response.xpath("//input[@name='csrfmiddlewaretoken']/@value").extract_first()

        headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': response.url,
            'X-CSRFToken': csrf
        }

        data = {"event_search": {
            "dates": "current_future", "date_range": {"to": date_short, "from": date_short},
            "places": [city_id], "page": 1, "page_size": 20, "online_events_only": False},
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

            mapping = ["start_date", "end_date", "start_time", "end_time", "tickets_url", "tickets_by", "name", "url",
                       "summary"]

            images = []
            image = e.get("image", {}).get("url")
            if image:
                images.append(image)

            primary_venue = e.get("primary_venue", {})
            address = primary_venue.get("address", {})
            event = {
                "image_urls": images,
                "category": ', '.join([_.get("display_name") for _ in e.get("tags")]),
                "primary_venue": primary_venue.get("name"),
                "city": address.get("city"),
                "state": address.get("state"),
                "region": address.get("region"),
                "postal_code": address.get("postal_code"),
                "address_1": address.get("address_1"),
            }

            for m in mapping:
                event[m] = e.get(m)
            yield event

        page_number = jresp.get("events").get("pagination").get("page_number")
        page_count = jresp.get("events").get("pagination").get("page_count")

        if page_number == 1:

            for page_number in range(2, page_count + 1):
                data["event_search"]["page"] = page_number

                yield Request(self.url, method="POST", callback=self.parse_listing, headers=headers,
                              body=json.dumps(data), meta={"headers": headers, "data": data}, dont_filter=True)

