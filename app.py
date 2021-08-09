
'''
Created on 

Course work: 

@author: Ana & Ishita

Source:
    
'''

# Import necessary modules
from flask import Flask, render_template, request , jsonify
from elasticsearch import Elasticsearch
import pprint
import os,json
from flask.helpers import flash
import imgbbpy
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_PATH = "static/"
app.config['UPLOAD_FOLDER'] = UPLOAD_PATH

es = Elasticsearch(HOST="http://localhost", PORT=9200)
es = Elasticsearch()
path_to_json = 'users/'

app.secret_key = 'enjaamiTale$eFennelda$S'


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/form')
def form():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('form.html' , files = files)


@app.route('/submit', methods = ["POST"])
def get_details():

    name                    = request.values.get("name")
  
    # photo                   = request.values.get("photo") 
    public_hobbies          = request.values.get("p_hobbies")
    public_interests        = request.values.get("p_interests")
    hidden_interests        = request.values.get("interests")
    hidden_hobbies          = request.values.get("h_hobbies")
    challenges              = request.values.get("challenges")
    demographics            = request.values.get("demo")
    experience              = request.values.get("exp")
    frustration             = request.values.get("frust")
    skills                  = request.values.get("skills")
    interpersonal_skills    = request.values.get("i_skills")
    contact_info            = request.values.get("contact")
    channel_meter           = request.values.get("c_meter")
    authentication_meter    = request.values.get("a_meter")
    collected_by            = request.values.get("author")
    miscellaneous           = request.values.get("misc")

    
    my_dict = {}

    my_dict ["Name"]                = name
  
    my_dict ["public_hobbies"]      = public_hobbies
    my_dict ["public_interests"]    = public_interests
    my_dict ["hidden_interests"]    = hidden_interests
    my_dict ["hidden_hobbies"]      = hidden_hobbies
    my_dict ["challenges"]          = challenges
    my_dict ["demographics"]        = demographics
    my_dict ["experience"]          = experience
    my_dict ["frustration"]         = frustration
    my_dict ["skills"]              = skills
    my_dict ["interpersonal_skills"]= interpersonal_skills
    my_dict ["contact_info"]        = contact_info
    my_dict ["channel_meter"]       = channel_meter
    my_dict ["authentication_meter"]= authentication_meter
    my_dict ["collected_by"]        = collected_by
    my_dict ["miscellaneous"]       = miscellaneous


    user_data = get_json('static/users.json')
    user_list = user_data['users']
    current_user_num = max(user_list)+ 1 
    user_list.append(current_user_num)
    updated_user_dict = {
        'users' : user_list
    }

    with open("static/users.json", "w") as outfile:
        outfile.write(json.dumps(updated_user_dict))

    list = get_json('static/usermeta.json')

    # print (my_dict.get('Name'))

    flag = 0

    name_list = list['user_list']

    print (name_list)

    for d in name_list:

        if my_dict.get('Name') in d['name'] :
            single_edit_submit(d['user_id'], my_dict)
            print(d['user_id'])
            flag = 1
            break 
    if flag == 0:
        
        uploaded_file           = request.files['file']

        with open( f"users/{current_user_num}.json", "w") as outfile:
            outfile.write(json.dumps(my_dict))

            user_data  = get_json('static/users.json')

            user_ids = user_data['users']
            
            name = my_dict.get('Name')

            for user in user_ids:
                user_dict = {
                    'user_id': user,
                    'name'   : name
                }
                # print(user)
            user_nameta_list = []
            
            user_nameta_list.append(user_dict)

            
            updated_user_dict = {
                'user_list' : user_nameta_list
            }

            # with open("static/usermeta.json", "w") as outfile:
            #     outfile.write(json.dumps(updated_user_dict))

            # with open( f"users/{current_user_num}.json", "w") as outfile:
            #     outfile.write(json.dumps(my_dict))
            
            with open("static/usermeta.json",'r+') as file:
                # First we load existing data into a dict.
                file_data = json.load(file)
                # Join new_data with file_data inside emp_details
                file_data['user_list'].append(user_dict)
                # Sets file's current position at offset.
                file.seek(0)
                # convert back to json.
                json.dump(file_data, file, indent = 4)

            filename = secure_filename(uploaded_file.filename)
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
                uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            else :
                filename = 'avatar.png'
        
            client = imgbbpy.SyncClient('8f66184d2449eaf6928980d0ce653834')
            image = client.upload(file= 'static/' + filename) 
            # print(image.url)

            img = image.url
            print (img)

            my_dict ["photo"]               = img

    return render_template('form.html')

    

def get_json(FILE_PATH):

    with open(FILE_PATH) as f:
        data = json.load(f)

    return data

def single_edit_submit(id, dict):
    print(id)
    print(dict)
    # new_dict = {}
    # f = open(f'users/{id}.json',)
    
    # new_dict.update(dict)
    # f.seek(0)
    # json.dumps(new_dict)
    with open( f"users/{id}.json", "w") as outfile:
            outfile.write(json.dumps(dict))

    return render_template("form.html")

def view_item():

    result = []
 
    for file_name in [file for file in os.listdir(path_to_json) if file.endswith('.json')]:
        with open(path_to_json + file_name) as json_file:
    
            data = json.load(json_file)

            es.index(index=file_name, id=file_name, body=data)

            body = {

                "query": {
                    
                        "match_all" : {}
    
                },
                "highlight" : {
                    "pre_tags" : [
                        "<b style='color:orange'>"],
                    "post_tags" : [
                        "</b>"
                    ],
                    # "tags_schema" : "styled",
                    "fields":{
                        "*":{}
                    }
                }
            }
       
            es.search(index=file_name, body=body)
 
            result.append(
                    {
                        "location" : file_name,
                        "text"     : data
                       
                })

    return result   


@app.route('/view', methods = ["POST","GET"])
def view():

    result = view_item()

    return render_template("tables.html", result = result)

@app.route('/single/<id>', methods = ["POST","GET"])
def single(id):
    
    f = open(f'users/{id}',)

    data = json.loads(f.read())

    result = view_item()

    return render_template("profile.html", result = data , results= result )

@app.route('/delete/<id>', methods = ["POST","GET"])
def delete(id):

    f = f'users/{id}'
    if os.path.exists(f):
        os.remove(f)

    return render_template('delete.html')


@app.route('/edit/<id>', methods = ["POST","GET"])
def single_edit(id):
    
    f = open(f'users/{id}',)
    data = json.loads(f.read())

    result = view_item()

    return render_template("edit.html", result = data, results= result)

    
def search_item(query_word):
    result1 = []

    for file_name in [file for file in os.listdir(path_to_json) if file.endswith('.json')]:
        with open(path_to_json + file_name) as json_file:
            
            data = json.load(json_file)
            
            es.index(index=file_name, id=file_name, body=data)

            body = {

                "query": {
                    "multi_match" : {
                        "query" : str(query_word)
                        
                    }
                },
                "highlight" : {
                    "pre_tags" : [
                        "<b style='color:orange'>"],
                    "post_tags" : [
                        "</b>"
                    ],
                    # "tags_schema" : "styled",
                    "fields":{
                        "Name":{}
                    }
                }
            }

            res = es.search(index=file_name, body=body)
            
            if len(res['hits']['hits']) != 0:
                high = "<h5>"
                temp=res['hits']['hits'][0]['highlight']
                for v in list(temp.values())[0]:
                    high += v
                print(high)
                # pprint.pprint(res['hits']['hits'])
                high += "...</h4>"
                result1.append(
                    {
                        "location" : file_name,
                        "text" : high
                })
                # print(file_name)
    return result1


@app.route('/search', methods = ["POST","GET"])
def search():
    if request.method == 'POST':
        query_word = request.form.get('query_word')
        search = search_item(query_word)
        return render_template("search.html", result = search)

    return render_template("tables.html")





if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port= 5500)