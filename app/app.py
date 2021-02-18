from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse
import vk_api

from vk_coomon.vk_scrap import ScrapVk
from common.classificator_sentiment_analysis import multiply_array
from config import Config, VK_TOKEN


app = Flask(__name__)
cors = CORS(app)
api = Api(app)

app.templates_auto_reload = True
app.config.from_object(Config)


class GetSentimentVk(Resource):
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


api.add_resource(GetSentimentVk, '/sentiment_vk')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
