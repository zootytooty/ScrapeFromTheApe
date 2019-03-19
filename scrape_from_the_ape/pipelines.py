# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import yaml
import psycopg2
import MySQLdb as mysql
import dateparser

class ScrapeFromTheApePipeline(object):

    def open_spider(self, spider):

        conf = yaml.load(open('conf.yaml', 'r'))

        hostname = conf['hostname']
        username = conf['username']
        password = conf['password']
        database = conf['database']
        dbtype = conf['dbtype']

        if dbtype == 'postgres':
          self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        elif dbtype == 'mysql':
          self.connection = mysql.connect(host=hostname, user=username, passwd=password, db=database, charset='utf8')
        else:
          raise Exception('[ScrapeFromTheApePipeline] Database type not recognised or empty, please provide dbtype key:value in conf.yaml')

        self.cur = self.connection.cursor()


    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()


    def process_item(self, item, spider):
        parsed_date = dateparser.parse(item['date'])
        str_date = '0000-00-00'
        if parsed_date is not None:
            str_date = "{}-{}-{}".format(parsed_date.year,parsed_date.month,parsed_date.day)
			
        insert_qry = """
            insert into gig_guide (venue, title, music_starts, doors_open, performance_date, price, description, url, image_url) 
            values('{}','{}','{}','{}', '{}' ,'{}','{}','{}','{}')
            """.format(
                item['venue'],
                item['title'].replace("'",""),
                item['music_starts'],
                item['doors_open'].replace("'",""),
                str_date,
                item['price'],
                item['desc'].replace("'",""),
                item['url'],
                item['image_url']
            )

        try:
            self.cur.execute(insert_qry)
            self.connection.commit()
        except:
            print(" ")
            print(insert_qry)

        
        return item
