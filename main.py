from flask import Flask, make_response, jsonify, Response, request
from flask_restful import Api, Resource, reqparse
from scoring import score

app = Flask(__name__)
api = Api()
import db


#@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Headers'] = 'content-type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Content-Security-Policy'] = 'true'
    response.headers['Connection'] = 'keep-alive'
    response.headers['Content-Length'] = '0'
    response.headers['Vary'] = 'Origin'
    response.headers['Vary'] = 'Access-Control-Request-Method'
    response.headers['Vary'] = 'Access-Control-Request-Headers'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response

class Filter():
    def get(self):
        filters = db.get_filters()
        return make_response(jsonify(filters), 200)

class Block():
    def get(self):
        blocks = db.get_blocks()
        return make_response(jsonify(blocks), 200)

class Mortgage(Resource):
    #@app.route('/api/mortgage', methods=['POST'])
    def post(self):
        block_json = request.json
        # with open('block.json', 'w') as f:
        #     f.write(str(block_json))
        mortgage = block_json['mortgage']
        b = db.create_block(mortgage['name'], mortgage['maxSum'], mortgage['percent'], mortgage['years'])
        for field_json in block_json['strategy']:
            # check if field exists
            f = db.create_filter(field_json['name'], field_json['operation'], field_json['value'])
            db.add_filter_to_block(f.id, b.id)
        return make_response(jsonify({'status': 'ok'}), 200)

class Blocks(Resource):
    #@app.route('/api/mortgage', methods=['POST'])
    def get(self):
        blocks = db.get_blocks()
        result = {'status': 'ok', 'result':list(map(db.Block.to_json, blocks))}
        # print(result)
        return make_response(jsonify(result), 200)
    
    def post(self):
        block_json = request.json
        id = int(block_json['id'])
        b = db.get_block_by_id(id)
        if b is None:
            return make_response(jsonify({'status': 'error', 'result': 'block not found'}), 404)
        result = b.to_json()
        filters = db.get_filters_by_block(id)
        result['filters'] = list(map(db.Filter.to_json, filters))
        # print(result)
        return make_response(jsonify({'status': 'ok', 'result': result}), 200)

class Application(Resource):
    #@app.route('/api/mortgage', methods=['POST'])
    def post(self):
        application_json = request.json
        block_id = int(application_json['blockId'])
        filters = db.get_filters_by_block(block_id)
        # list of tuples (filter_id, value, operation, value_const)
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
                            bool_result)
        return make_response(jsonify({'result': bool_result}), 200)
    
    def get(self):
        applications = db.get_user_applications()
        result = {'status': 'ok', 'result':list(map(db.UserApplication.to_json, applications))}
        # print(result)
        return make_response(jsonify(result), 200)

class Test(Resource):
    #@app.route('/api/test', methods=['GET'])
    def get(self):
        return make_response(jsonify ({'status': 'ok'}), 200)

api.add_resource(Mortgage, "/api/mortgage") # post
api.add_resource(Test, "/api/test") # get
api.add_resource(Blocks, "/api/blocks") # get/post
api.add_resource(Application, "/api/application") # get/post
api.init_app(app)
if __name__ == '__main__':
    app.run(debug=True)
