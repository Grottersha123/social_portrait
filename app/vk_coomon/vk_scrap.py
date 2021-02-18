import base64
from datetime import datetime
from icecream import ic
import vk_api

from config import phone, password

COUNT = 200
MAX_COUNT_SIZE = 100
VIDEO_COUNT = 100


class ScrapVk():
    @staticmethod
    def dict_filter(dictlist: list, key: str, value: str) -> list:
        return list(filter(lambda x: x.get(key) == value, dictlist))

    def __init__(self, VK_TOKEN):
        # starting session
        vk_session = vk_api.VkApi(token=VK_TOKEN)
        self.session_api = vk_session.get_api()

        vk_session = vk_api.VkApi(base64.b64decode(phone).decode(), base64.b64decode(password).decode())
        vk_session.auth()

        self.vk_session_group = vk_session.get_api()

    def get_info(self, user_id='', uniq_name=''):
        return self.session_api.users.get(user_ids=user_id,
                                          fields='sex,bdate,about,interests,followers_count, books, games, about, quotes, can_post, can_see_audio, can_send_friend_request, is_favorite, friend_status, career, military,connections,photo_400_orig,can_see_all_posts')

    def get_post_by_date(self, date_begin='', date_end='', user_id='', uniq_name='', COUNT=COUNT):
        """
            :type date_begin: дата конца
            :type date_end: дата конца
        """
        all_count = 0
        posts_lst = []
        post_dict = []
        count_like = 0
        for index in range(0, COUNT // MAX_COUNT_SIZE + 1):
            posts = self.session_api.wall.get(owner_id=user_id, count=MAX_COUNT_SIZE, offset=index * MAX_COUNT_SIZE)
            for post in posts['items']:
                post_date = post['date']
                text_repost = ''
                # if (post_date >= date_begin) and (date_end >= post_date):
                if 'copy_history' in post:
                    text_repost = post['copy_history'][0]['text']
                    if len(text_repost) > 5 and len(text_repost) < 70:
                        posts_lst.append(text_repost)
                        post_dict.append({'date': datetime.utcfromtimestamp(int(post_date)).strftime('%Y-%m-%d'),
                                          'post': text_repost})
                likes = post['likes']['count']
                count_like += likes
                all_count += 1
                if len(post['text']) > 2 and len(post['text']) < 100:
                    posts_lst.append(post['text'])
                    post_dict.append(
                        {'date': datetime.utcfromtimestamp(int(post_date)).strftime('%Y-%m-%d'), 'post': post['text']})
        return posts_lst, count_like, all_count, post_dict

    def get_groups_posts(self, date_begin='', date_end='', user_id=''):
        pass

    def get_video_by_date(self, date_begin='', date_end='', user_id='', uniq_name=''):
        user_id = user_id if user_id else vk_api.users.get(user_ids=uniq_name)[0]['id']

        text = ''
        video_lst = []
        for index in range(1, COUNT // MAX_COUNT_SIZE + 1):
            videos = self.session_api.video.get(owner_id=user_id, count=VIDEO_COUNT, offset=index * MAX_COUNT_SIZE)
            for video in videos['items']:
                video_date = video['date']
                # if (video_date >= date_begin) and (date_end >= video_date):
                title = video['title']
                description = video['description']
                text += title + description
                video_lst.append(text)
        return video_lst

    def get_groups_user(self, user_id):
        groups = self.vk_session_group.groups.get(owner_id=user_id, extended=1,
                                                  fields='description,status,is_closed,name ')
        print(groups)
        return self.dict_filter(groups['items'], 'is_closed', 0)

    def get_n_post_of_group(self, group_id, post=50):
        pass

# if __name__ == '__main__':
#     vk_scrap = ScrapVk(VK_TOKEN)
#     print(vk_scrap.get_info(user_id='zeroai'))
#     vk_scrap.get_post_by_date(user_id=46099694)
