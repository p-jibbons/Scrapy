# -*- coding: utf-8 -*-


from datetime import datetime
BOT_NAME = 'crawler'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'



# import  datetime
# today = datetime.date.today()
# FEED_FORMAT = 'csv'
# FEED_URI = 's3://relayplay-prebackend/ev_scrapedata/' + today.strftime("%Y/%m/%d") + '/eventbrite_spider.csv'
# IMAGES_STORE = 's3://relayplay-prebackend/images'
#
IMAGES_URLS_FIELD = 'image_original_url'
IMAGES_RESULT_FIELD = 'image_s3_url'
# IMAGES_STORE_S3_ACL = 'public-read'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
CLOSESPIDER_PAGECOUNT = 2



# Configure a delay for requests for the same website (default: 0)

DOWNLOAD_DELAY = 1
DOWNLOAD_TIMEOUT = 360


# Disable cookies (enabled by default)
COOKIES_ENABLED = True

#

#


# Configure item pipelines
ITEM_PIPELINES = {
	# 'scrapy.pipelines.images.ImagesPipeline': 100,
	'crawler.database_write_pipeline.DatabasePipeline': 300,
}


# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = .3
AUTOTHROTTLE_MAX_DELAY = 1.5
AUTOTHROTTLE_DEBUG = False



# Retry many times since proxies often fail
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 503, 504, 400, 401, 403, 404, 405, 407, 408, 416, 456, 502, 429]

# # LOG_FILE = "scrapy.log"
LOG_LEVEL = 'DEBUG'
# LOG_STDOUT = True
# LOG_ENABLED=True




# USER_AGENT_LIST = [
# 	"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
# 	"Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
# ]

