import multiprocessing
from functools import partial

from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse
import vk_api
from icecream import ic

from common.nlp_utils import preprocess_text, lemmatization
from vk_coomon.vk_scrap import ScrapVk
from common.classificator_sentiment_analysis import multiply_array
from config import Config, VK_TOKEN


app = Flask(__name__)
cors = CORS(app)
api = Api(app)

app.templates_auto_reload = True
app.config.from_object(Config)


class SentimentVk(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=str, help='user_id vk')
        parser.add_argument('post_count', type=int, help='count posts vk')
        args = parser.parse_args()
        if args['user_id'] and args['post_count']:

            user_id, post_count = args['user_id'], args['post_count']
            vk_scrap = ScrapVk(VK_TOKEN)
            try:
                info_data = vk_scrap.get_info(user_id=user_id)
                if info_data and info_data[0]['can_see_all_posts']:
                    info_data = info_data[0]

                    user_id = info_data['id']
                    posts, likes, count_posts, post_dict = vk_scrap.get_post_by_date(user_id=user_id, COUNT=int(post_count))
                    info_data['count_posts'] = count_posts
                    info_data['count_likes'] = likes
                    sentiment_data_posts, sentiment_data_binary, sentiment_data_table = multiply_array(posts, post_dict)
                    return {'data_info': info_data, 'data_posts': sentiment_data_posts,
                            'data_binary': sentiment_data_binary, 'data_table': sentiment_data_table}
                return {'data_info': info_data[0], 'data_posts': None, 'data_binary': None, 'data_table': None}
            except vk_api.exceptions.ApiError:
                return {'error': 'Invalid Id'}, 404

        else:
            return {'error': 'bad request'}, 404

class TematicVk(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=str, help='user_id vk')
        parser.add_argument('post_count', type=int, help='count posts from group vk')
        args = parser.parse_args()
        if args['user_id'] and args['post_count']:
            user_id, post_count = args['user_id'], args['post_count']
            vk_scrap = ScrapVk(VK_TOKEN)
            try:
                info_data = vk_scrap.get_info(user_id=user_id)
                if info_data and info_data[0]['can_see_all_posts']:
                    groups = vk_scrap.get_groups_user(user_id=user_id, num=10)
                    # groups_id = [item['id'] for item in groups]
                    result = []
                    for gr in groups:
                        ic(gr['id'])
                        group_posts = vk_scrap.get_n_post_of_group(group_id=gr['id'], post_n=10)
                        result.append(group_posts)
                    ic(preprocess_text(result))

                    # pool = multiprocessing.Pool(processes=1)
                    # prod_x = partial(vk_scrap.get_n_post_of_group, vk_session=vk_scrap.vk_session_group, post_n=10)  # prod_x has only one argument x (y is fixed to 10)
                    # ic(prod_x)
                    # result_list = pool.map(prod_x, groups_id)
                    # ic(result_list)
                    return {'data_group_posts': groups, 'text_data': result}
                return {'data_info': info_data[0], 'data_posts': None, 'data_binary': None, 'data_table': None}
            # except vk_api.exceptions.ApiError:
            except IndexError:
                return {'error': 'Invalid Id'}, 404

            else:
                return {'error': 'bad request'}, 404


api.add_resource(SentimentVk, '/sentiment_vk')
api.add_resource(TematicVk, '/tematic_vk')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
