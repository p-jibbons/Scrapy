from datetime import date
import requests
import lxml.html
from datetime import timedelta

date_short = date.today()
city_id = "85922227"
city_name = 'ca--san-diego'
url = f"https://www.eventbrite.com/d/{city_name}/all-events/?start_date={date_short}&end_date={date_short}"
response = requests.get(url)

tree = lxml.html.fromstring(response.text)
csrf = tree.xpath("//input[@name='csrfmiddlewaretoken']/@value")[0]


startdate = date.today()+ timedelta(days=10)
#print(startdate)