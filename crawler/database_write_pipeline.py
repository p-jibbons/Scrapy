# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2
# import mysql.connector
# from .sql_statements import insert_event_sql


class DatabasePipeline(object):
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
        print('datebase connection added')

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()
        print('spider closed')


    def process_item(self, item, spider):
        try:
            spider_fields = list(item.keys())
            insert_event_sql = 'insert into events_event(' + ','.join(spider_fields) + ') VALUES (' + ','.join(['%s'] * len(spider_fields)) + ') ON CONFLICT ON CONSTRAINT unique_event DO NOTHING;'
            # insert_event_sql = 'insert into events_event(' + ','.join(spider_fields) + ') VALUES (' + ','.join(['%s'] * len(spider_fields)) + ');'

            values = []
            for field in spider_fields:
                values.append(item[field])
            self.cur.execute(insert_event_sql,values)
            print('success')
        except Exception as inst:
            # print('failed')
            self.cur.execute("ROLLBACK")

            print(type(inst))  # the exception instance
            print(inst.args)  # arguments stored in .args
            print(inst)
            print('Fail to write to db')

        self.connection.commit()
        return item