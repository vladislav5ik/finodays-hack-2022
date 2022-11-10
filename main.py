from flask import Flask, make_response, jsonify, Response, request
from flask_restful import Api, Resource, reqparse
from scoring import score, calculate_limit

app = Flask(__name__)
api = Api()
import db


class Filter():
    def get(self):
        """Получение списка фильтров"""
        filters = db.get_filters()
        return make_response(jsonify(filters), 200)

class Block():
    def get(self):
        """Получение полного списка блоков (продуктов банка)"""
        blocks = db.get_blocks()
        return make_response(jsonify(blocks), 200)

class Mortgage(Resource):
    def post(self):
        """Добавление конфигурации ипотеки"""
        block_json = request.json
        mortgage = block_json['mortgage']
        b = db.create_block(mortgage['name'], mortgage['maxSum'], mortgage['percent'], mortgage['years'])
        for field_json in block_json['strategy']:
            f = db.create_filter(field_json['name'], field_json['operation'], field_json['value'])
            db.add_filter_to_block(f.id, b.id)
        return make_response(jsonify({'status': 'ok'}), 200)
    
    def put(self):
        """Изменение конфигурации ипотеки"""
        block_json = request.json
        mortgage = block_json['mortgage']
        b = db.update_block(mortgage['name'], mortgage['maxSum'], mortgage['percent'], mortgage['years'])
        for field_json in block_json['strategy']:
            f = db.create_filter(field_json['name'], field_json['operation'], field_json['value'])
            db.add_filter_to_block(f.id, b.id)
        return make_response(jsonify({'status': 'ok'}), 200)

class Blocks(Resource):
    def get(self):
        """Получение полного списка блоков (продуктов банка)"""
        blocks = db.get_blocks()
        result = {'status': 'ok', 'result':list(map(db.Block.to_json, blocks))}
        return make_response(jsonify(result), 200)
    
    def post(self):
        """Получение блока (продукта банка) по id"""
        block_json = request.json
        id = int(block_json['id'])
        b = db.get_block_by_id(id)
        if b is None:
            return make_response(jsonify({'status': 'error', 'result': 'block not found'}), 404)
        result = b.to_json()
        filters = db.get_filters_by_block(id)
        result['filters'] = list(map(db.Filter.to_json, filters))
        return make_response(jsonify({'status': 'ok', 'result': result}), 200)

class Application(Resource):
    """Подаётся заявки на ипотеку, возвращает результат проверки и лимит"""
    def post(self):
        application_json = request.json
        block_id = int(application_json['blockId'])
        filters = db.get_filters_by_block(block_id)
        filter_values = dict()
        for filter in application_json['additionalFields']:
            filter_values[filter['id']] = filter['value']
        bool_result, text_result = score(filters, filter_values)

        u = db.create_user_application(block_id,
                            application_json['firstName'],
                            application_json['lastName'],
                            application_json['middleName'],
                            application_json['phoneNumber'],
                            text_result,
                            bool_result,
                            application_json['salary'],
                            application_json['credit_request'])
        limit = calculate_limit(int(application_json['salary']),
                                db.get_max_sum_by_block(block_id),
                                int(application_json['credit_request']))
        return make_response(jsonify({'result': bool_result, 'limit': limit}), 200)
    
    def get(self):
        """Получение списка заявок"""
        applications = db.get_user_applications()
        result = {'status': 'ok', 'result':list(map(db.UserApplication.to_json, applications))}
        return make_response(jsonify(result), 200)

class Test(Resource):
    def get(self):
        return make_response(jsonify ({'status': 'ok'}), 200)

api.add_resource(Mortgage, "/api/mortgage") # post
api.add_resource(Test, "/api/test") # get
api.add_resource(Blocks, "/api/blocks") # get/post
api.add_resource(Application, "/api/application") # get/post
api.init_app(app)
ы
if __name__ == '__main__':
    app.run(debug=True)
