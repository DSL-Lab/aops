import json
import random
import re

class AOPS:
    def __init__(self, path) -> None:
        """
        path: path to the jl file
        sample > 0 means get sample lines uniformly from the jl file
        create a self.data that contains the list of lines sampled
        """
        random.seed(42)  # Set the seed for reproducibility
        self.path = path
        self._jlines = self._load_data()
        self._j_cache = {}

    def _load_data(self):
        with open(self.path, 'r') as file:
            lines = file.readlines()
        filtered_lines = []
        for line in lines:
            data = json.loads(line)
            if 'response' in data and 'response' in data['response'] and len(data['response']['response']['posts']) > 0:
                filtered_lines.append(line)
            else:
                print("No posts in this thread")
        return filtered_lines

    def _get_parsed_line(self, line_idx):
        if line_idx not in self._j_cache:
            self._j_cache[line_idx] = json.loads(self._jlines[line_idx])
        return self._j_cache[line_idx], self._jlines[line_idx]

    def __getitem__(self, idx):
        """
        Get information from the idx th data
        Return a dict containing the following info: 
            meta_info: topic_id, num_watchers, tags_list: [tags_text]
            posts_info: [{post_id, post_canonical, post_number, thanks_received, nothanks_received, username, num_posts}]
        """
        if idx < 0 or idx >= len(self):
            raise IndexError('Index out of range')

        raw_data, raw_line = self._get_parsed_line(idx)
        if 'raw' in raw_data:
            raw_data = raw_data['raw']
        data = raw_data['response']['response']
        meta_info = {
            'topic_id': data['new_topic_settings']['topic_id'],
            'num_watchers': data['new_topic_settings']['num_watchers'],
            'tags_list': [tag['tag_text'] for tag in data.get('tags', '')]
        }

        posts_info = [{
            'post_id': post['post_id'],
            'post_canonical': post['post_canonical'],
            'post_number': post['post_number'],
            'thanks_received': post['thanks_received'],
            'nothanks_received': post['nothanks_received'],
            'username': post['username'],
            'poster_id': post['poster_id'],
            'user_num_posts': post['num_posts']
        } for post in data.get('posts', [])]
        parsed = {} if 'parsed' not in raw_data else raw_data['parsed']
        if 'question' in raw_data:
            parsed['question'] = raw_data['question']
        if 'answers' in raw_data:
            parsed['answers'] = raw_data['answers']
        data = {}
        # data.update(raw_data)
        data.update({
            'meta': meta_info,
            'posts': posts_info,
            'parsed': parsed
        })
        thread, top_post = self.get_thread(data)
        data['thread'] = thread
        data['top_post'] = top_post
        data['raw'] = raw_data
        data['topic_id'] = meta_info['topic_id']
        return data

    def __len__(self):
        return len(self._jlines)

    def build_posts_reference(self, posts):        
        sorted_posts = sorted(posts, key=lambda x: x['post_number'])
        def locate_post(canonical_post):
            for i, post in enumerate(sorted_posts):
                if post['post_canonical'] == canonical_post:
                    return i
            return -1

        for i, post in enumerate(sorted_posts):
            pattern = r"\[quote=[^]]+\](.*?)\[/quote\]"
            matches = re.finditer(pattern, post['post_canonical'], re.DOTALL)
            quote_post_ids = []
            for match in matches:
                quote_part = match.group(1)
                quote_post_id = locate_post(quote_part)
                assert quote_post_id != -1, f"Post not found: {quote_part}"
                quote_post_ids.append(quote_post_id)
            sorted_posts['quote_post_ids'] = quote_post_ids

    def get_thread(self, data):
        """
        Turns the posts of the data into a continuous thread format.
        
        Returns:
        str: A string representation of the thread with posts in increasing post_number order.
        """
        posts = data['posts']

        # Sort posts by post_number to ensure they're in increasing order
        sorted_posts = sorted(posts, key=lambda x: x['post_number'])

        thread = []
        for post in sorted_posts:
            thread_line = f"Post {post['post_number']} by user {post['username']}: {post['post_canonical']}\n####\n"
            thread.append(thread_line)

        return "\n".join(thread), sorted_posts[0]['post_canonical']

    def _create_index(self):
        self.index_by_topic_id = {}
        for i in range(len(self)):
            post_data = self[i]
            self.index_by_topic_id[post_data['meta']['topic_id']] = i

    # use _create_index first then O(1) get the topic by id
    def get_topic_by_id_new(self, topic_id):
        try:
            return self[self.index_by_topic_id[topic_id]]
        except KeyError:
            raise ValueError(f"Topic with topic_id {topic_id} not found in data.")

    def get_topic_by_id(self, topic_id):
        for i in range(len(self)):
            post_data = self[i]
            if topic_id == post_data['meta']['topic_id']:
                return post_data
        raise ValueError(f"Topic with topic_id {topic_id} not found in data.")

    def get_post_by_number(self, post_number, post_data):
        for post in post_data['posts']:
            if post['post_number'] == post_number:
                return post
        return None


# Example usage
if __name__ == '__main__':
    aops = AOPS('data/aops/items_filtered.jl', sample=10)
    print(aops[0])
