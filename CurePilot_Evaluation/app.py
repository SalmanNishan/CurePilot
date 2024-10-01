from flask import Flask, request, redirect, url_for, render_template, flash, jsonify
from pymongo import MongoClient
import requests
from collections import defaultdict

class LLMApp:
    def __init__(self, secret_key, db_uri, db_name, collection_name):
        self.app = Flask(__name__)
        self.app.secret_key = secret_key
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.setup_routes()
        self.add_template_globals()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/submit', methods=['POST'])
        def submit():
            try:
                name = request.form.get('data_name')
                if self.collection.find_one({'Name': name}):
                    flash(f"The name '{name}' already exists. Please use a different name.", 'error')
                    return redirect(url_for('index'))
                
                inputs = request.form.getlist('data_field')
                outputs = self.process_inputs(inputs)

                entries = [{
                    'input': inp,
                    'output': out,
                    'CurePilot_rating': {
                        'Explanation Depth': "0",
                        'Conciseness': "0",
                        'Tone Appropriateness': "0",
                        'Overall Helpfulness': "0",
                        'Suggestions': ""
                    }
                } for inp, out in zip(inputs, outputs)]
                
                document = {'Name': name, 'entries': entries}
                self.collection.insert_one(document)
                return redirect(url_for('index'))
            
            except Exception as e:
                print("Error during submission:", str(e))  # Log the error
                flash("An error occurred while submitting the data. Please try again.", 'error')
                return redirect(url_for('index'))

        @self.app.route('/results')
        def results():
            data_names = self.collection.distinct('Name')
            selected_name = request.args.get('data_name', '')
            document = self.collection.find_one({'Name': selected_name}) if selected_name else None
            return render_template('results_1.html', data_names=data_names, document=document, selected_name=selected_name)

        @self.app.route('/update_rating', methods=['POST'])
        def update_rating():
            try:
                data_name = request.form['data_name']
                document = self.collection.find_one({'Name': data_name})

                if document:
                    entry_ratings = defaultdict(dict)
                    for key, value in request.form.items():
                        if '[' in key and ']' in key:
                            rating_type, entry_index = key.split('[')
                            entry_index = int(entry_index.split(']')[0])
                            entry_ratings[entry_index][rating_type] = value
                        elif key.startswith('Suggestions'):
                            entry_index = int(key.split('[')[1].split(']')[0])
                            entry_ratings[entry_index]['Suggestions'] = value

                    updated_entries = []
                    for i in range(len(document['entries'])):
                        entry = document['entries'][i]
                        if i in entry_ratings:
                            entry['CurePilot_rating'] = entry_ratings[i]
                        updated_entries.append(entry)

                    self.collection.update_one({'_id': document['_id']}, {'$set': {'entries': updated_entries}})
                    print("Document updated successfully")

                return redirect(url_for('results', data_name=data_name))

            except Exception as e:
                print("Error during update:", str(e))
                flash("An error occurred while updating the data. Please try again.", 'error')
                return redirect(url_for('results', data_name=data_name))

    def process_inputs(self, inputs):
        outputs = []
        for input in inputs:
            try:
                response = requests.post(
                    "http://172.16.101.171:8020/start-chat",
                    json={
                        'userId': 'Evaluation_Testing',
                        'chatId': '5ecd764c-f26d-439b-9f64-43a3bbd85402',
                        'prompt': input
                    }
                ).json()
                outputs.append(response.get('response', ''))
            except:
                outputs.append('')
        return outputs

    def add_template_globals(self):
        @self.app.context_processor
        def inject_enumerate():
            return dict(enumerate=enumerate)

    def run(self, debug=False, host='0.0.0.0', port=5002):
        self.app.run(debug=debug, host=host, port=port)

if __name__ == '__main__':
    llm_app = LLMApp(secret_key='LLM', db_uri='mongodb://localhost:27017/', db_name='CurePilot', collection_name='CurePilot_Evaluation')
    llm_app.run(debug=False)