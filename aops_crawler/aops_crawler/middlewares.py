# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import time
import threading
from scrapy import signals
import requests
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
import logging
from aops_crawler.spiders.aops_spider import CustomRequest

class AopsCrawlerSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class AopsCrawlerDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self):
        self.aopssid, self.aops_session_id = self._get_session_keys()
        self._is_spider_closed = False
        def update_keys_forever():
            while True:
                if self._is_spider_closed:
                    return
                time.sleep(60)
                try:
                    aopssid, aops_session_id = self._get_session_keys()
                    self.aopssid, self.aops_session_id = aopssid, aops_session_id
                except ValueError:
                    logging.warning("Failed in updating session ids.")
                    pass
        threading.Thread(target=update_keys_forever).start()

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        if isinstance(request, CustomRequest):
            request.replace_cookie('aopssid', self.aopssid)
            request.replace_form_data('aops_session_id', self.aops_session_id)
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    def spider_closed(self, spider):
        self._is_spider_closed = True

    def _get_session_keys(self):
        response = requests.get('https://artofproblemsolving.com/community')
        aopssid = response.cookies.get('aopssid')
        
        response_content = response.content.decode()
        session_id_start = response_content.find("AoPS.session =")+22
        aops_session_id = response_content[session_id_start:session_id_start+32]
        print(f"The aops session id is: {aops_session_id}")
        return aopssid, aops_session_id
