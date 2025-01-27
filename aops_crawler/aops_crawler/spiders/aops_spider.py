import os
import time
import json
import scrapy
from scrapy import FormRequest
from scrapy.http.request.form import _urlencode
from tqdm import tqdm
import datetime

class AOPSSpider(scrapy.Spider):
        name = 'aops'
        MAX_TOPICS = 3_600_000
        # start_urls = [f'https://artofproblemsolving.com/community/c6h{i}' for i in range(1, 500)]

        def __init__(self, total_spiders=None, spider_idx=None, start_date='2000-01', test_mode=False, **kwargs):
            self.start_date = datetime.datetime.strptime(start_date, "%Y-%m")
            self.test_mode = test_mode
            super().__init__(**kwargs)

        @property
        def _items_file(self):
            return self.settings['FEED_URI']

        def parse(self, response, topic_idx):
            response_json = response.json()
            self._filter_out_post_renders(response_json)
            yield {'response': response_json, 'topic_id': topic_idx}


        def start_requests(self):
            # for topic_idx in range(self.spider_idx, AOPSSpider.MAX_TOPICS, self.total_spiders):
            for topic_idx in self._get_new_crawling_topic_idxs():
                url = 'https://artofproblemsolving.com/m/community/ajax.php'
                cookies = {
                        'aopsuid': '1',
                        'aopssid': '', # Filled in middleware
                }
                headers = {
                        'authority': 'artofproblemsolving.com',
                        'accept': 'application/json, text/javascript, */*; q=0.01',
                        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                }
                data = {
                        'topic_fetch': 'initial',
                        'new_topic_id': str(topic_idx),
                        'fetch_first': '1',
                        'fetch_all': '1',
                        'a': 'change_focus_topic',
                        'aops_logged_in': 'false',
                        'aops_user_id': '1',
                        'aops_session_id': '', # Filled in middleware
                }
                yield CustomRequest(url, dont_filter=True, callback=self.parse, method="POST", headers=headers, cookies=cookies, formdata=data ,cb_kwargs={'topic_idx': topic_idx})

        def _filter_out_post_renders(self, reponse_json):
            try:
                for post in reponse_json['response']['posts']:
                    del post['post_rendered']
            except:
                pass
        
        def _get_new_crawling_topic_idxs(self):
            crawled = set()
            # we assume topic_id increases monotonically
            def find_earliest_time_stamp(all_posts):
                first_post = all_posts[0]
                # for post in all_posts:
                post_time = datetime.datetime.fromtimestamp(first_post['post_time'])
                # if post_time < earlist_post_time:
                #     earlist_post_time = post_time
                return post_time

            if os.path.exists(self._items_file):
                print("Reading existing items file")
                with open(self._items_file, 'r') as f:
                    for l in tqdm(f):
                        try:
                            data = json.loads(l)
                            topic_idx = int(data['topic_id'])
                            if 'response' in data['response'] \
                                    and 'initialization_time' in data['response']['response']\
                                    and 'error_code' not in data['response'] \
                                    and len(data['response']['response']['posts']) != 0:
                                init_time = data['response']['response']['initialization_time']
                                init_time = datetime.datetime.fromtimestamp(init_time)
                                post_time = find_earliest_time_stamp(data['response']['response']['posts'])
                                # print(post_time, " - > ", self.start_date)
                                if post_time > self.start_date:
                                    break
                        except:
                            print(l)
                            raise
                        crawled.add(topic_idx)
            last_topic_idx = max(crawled) if len(crawled) != 0 else 0
            self.logger.info(f"Last crawled topic: {last_topic_idx}")
            if len(crawled) != 0:
                self.logger.info(f"Continuing crawling, so far crawled {len(crawled)}")
            max_topic_idx = max(last_topic_idx + 50000, AOPSSpider.MAX_TOPICS)
            for i in range(last_topic_idx, max_topic_idx):
                if i not in crawled:
                    yield i
            return


class CustomRequest(FormRequest):
    def __init__(self, *args, formdata = None, **kwargs) -> None:
        super().__init__(*args, formdata=formdata, **kwargs)
        self._formdata = formdata

    def replace_form_data(self, key, value):
        assert self.method == 'POST'
        self._formdata[key] = value
        items = self._formdata.items() if isinstance(self._formdata, dict) else self._formdata
        form_query_str = _urlencode(items, self.encoding)
        self._set_body(form_query_str)

    def replace_cookie(self, key, value):
        self.cookies[key] = value

