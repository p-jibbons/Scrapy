# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2
# import mysql.connector
# from .sql_statements import insert_event_sql






class CrawlerPipeline(object):

    def open_spider(self, spider):
        hostname = 'ec2-52-6-143-153.compute-1.amazonaws.com'
        username = 'jowgcbbjlvqmop'
        password = '2597fd295caa3bc47b21d30deefb4498ce4bdc59f0d3210947ea4026a9e8b063' # your password
        database = 'd7dq8ub5ap4ncg'
        port = '5432'
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database, port=port)
        self.cur = self.connection.cursor()
        # self.cur.execute("DELETE FROM events_event;")
        # self.connection.commit()
        # print('datebase deleted')

    # def open_spider(self, spider):
    #
    #     self.connection = mysql.connector.connect(
    #         host="development.relayplay.com",
    #         user="r1baldwi_develop",
    #         passwd="0bZyPQ[304zZ",
    #         database='r1baldwi_development'
    #     )
    #
    #     self.cur = self.connection.cursor()
    #     self.cur.execute("DELETE FROM wp_rp_events_live;")
    #     self.connection.commit()
    #     print('datebase deleted')

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()
        print('spider closed')

    def process_item(self, item, spider):
        if item.get('image_original_url')[0]:
            item['image_original_url'] = item.get('image_original_url')[0]
        else:
            item['image_original_url'] = ''

        if item.get('image_s3_url')[0]:
            thisdict = item.get('image_s3_url')[0]
            item['image_s3_url'] = thisdict["path"]
            print(item['image_s3_url'])
        else:
            item['image_s3_url'] = ''


        try:
            spider_fields = ['event_title',
                                'event_description',
                                'image_original_url',
                                'image_s3_url',
                                'start_date',
                                'end_date',
                                'start_time',
                                'end_time',
                                'event_datetime_string',
                                'scrape_source_name',
                                'scrape_source_url',
                                'buy_tickets_url',
                                'tickets_by',
                                'tickets_sold_out',
                                'venue_name',
                                # 'venue_url',
                                'venue_address_string',
                                'venue_city',
                                'venue_state',
                                'venue_country',
                                'venue_postal_code',
                                'venue_longitude',
                                'venue_latitude',
                                # 'venue_neighbourhood',
                                'venue_gmap_url',
                                'cost_string',
                                'cost_min_extract',
                                'cost_max_extract',
                                'cost_is_free',
                                'age_restrictions_string',
                                'spider_name',
                                'spider_scrape_datetime',
                                'date_added'
                                ]

            # insert_event_sql = 'insert into events_event(' + ','.join(spider_fields) + ') VALUES (' + ','.join(['%s'] * len(spider_fields)) + ') ON CONFLICT ON CONSTRAINT unique_event DO NOTHING;'
            insert_event_sql = 'insert into events_event(' + ','.join(spider_fields) + ') VALUES (' + ','.join(['%s'] * len(spider_fields)) + ');'

            values = []
            for field in spider_fields:
                values.append(item[field])
            self.cur.execute(insert_event_sql,values)
            print('success')
        except Exception as inst:
            print('failed')
            self.cur.execute("ROLLBACK")

            print(type(inst))  # the exception instance
            print(inst.args)  # arguments stored in .args
            print(inst)
            print('Fail to write to db')

        self.connection.commit()
        return item