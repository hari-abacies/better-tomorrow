import requests, json, time
from config import Config
from app import db

apiUrl = "https://api.monday.com/v2"
headers = {"Authorization" : Config.MONDAY_API_KEY}

def monday_get_boards(api_key):
    query = '{ boards {name id} }'
    data = {'query' : query}
    headers = {"Authorization" : api_key}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    print('board data', r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return None

def monday_check_board(board_id):
    query9 = "query { boards (ids: %s) { name state board_folder_id owner { id }}}"%board_id
    data = {'query' : query9}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    print(r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return None

def monday_get_board_data(board_id, api_key):
    query9 = "query { boards (ids: %s) { name state columns { id type title } groups { id title } items { id name } owner { id } subscribers{ id name email}}}"%board_id
    data = {'query' : query9}
    headers = {"Authorization" : api_key}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    print(r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return None

def monday_check_group(board_id):
    # Group fields
    query14 = "query { boards (ids: %s) { groups (ids: status){ title color position }}}"%board_id
    data = {'query' : query14}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    print(r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return None

def monday_check_items(item_id):
    # Querying items
    query15 = "query { items (ids: [%s,]) { name } }"%item_id
    data = {'query' : query15}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    print(r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return None

def monday_create_group(board_id, group_name, api_key):
    query39 = 'mutation { create_group (board_id: %s, group_name: \"%s\") { id title } }' % (board_id, group_name)
    data = {'query' : query39}
    headers = {"Authorization" : api_key}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    print(r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return None

def monday_create_item(board_id, group_id, item_name, clmn_value):
    # Create item
    query42 = "mutation { create_item (board_id: %s, group_id: \"%s\", item_name: \"%s\", column_values: \"{\\\"text\\\":\\\"%s\\\"}\") { id }}" % (board_id, group_id, item_name, clmn_value)
    data = {'query' : query42}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    print(r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return None
def monday_get_me(api_key):
    query9 = "query { me { is_guest created_at name id location}}"
    data = {'query' : query9}
    headers = {"Authorization" : api_key}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    print(r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return {}
def monday_create_board(api_key, board_name):
    query39 = "mutation { create_board (board_name: \"%s\", board_kind: public) { id }}" % board_name
    data = {'query' : query39}
    headers = {"Authorization" : api_key}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    print(r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return None


def monday_create_column(api_key, board_id, title, column_type):
    query39 = "mutation { create_column(board_id: %s, title: \"%s\", column_type: %s) {id}}" % (board_id, title, column_type)
    print(query39)
    data = {"query" : query39}
    print(data)
    headers = {"Authorization" : api_key}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    print(r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return None    

def create_item(board_id, item_name, api_key):
    query3 = 'mutation{ create_item (board_id:%s, item_name:\"%s\") { id } }'%(board_id, item_name)
    data = {'query' : query3}
    print('create item data--', data)
    headers = {"Authorization" : api_key}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    if r.status_code == 429:
        print('!!!!!!!! monday Complexity budget exhausted !!!!!!')
        time.sleep(62)
        r = requests.post(url=apiUrl, json=data, headers=headers)
    print(r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return None

def monday_check_item_data(item_id, api_key):
    # Querying items
    query15 = "query { items (ids: [%s,]) { name group { id title } column_values { id } } }" %item_id
    data = {'query' : query15}
    headers = {"Authorization" : api_key}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    print(r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return None

def monday_add_item_file(api_key, item_id, file_name, file_path, column_id):
    url = "https://api.monday.com/v2/file"

    mutation = 'mutation add_file($file: File!, $item_id: Int!, $column_id: String!) {add_file_to_column (item_id: $item_id, column_id: $column_id, file: $file) {id}}'
    variables = '{"item_id":%s, "column_id": \"%s\"}'%(item_id, column_id)
    map_img = '{"image":"variables.file"}'
    payload = {"query" : mutation, 'variables': variables, 'map':  map_img }
    files=[('image',(file_name,open(file_path,'rb'),'application/octet-stream'))]
    headers = {"Authorization" : api_key}
    r = requests.post(url, data=payload, headers=headers, files=files) # make request
    print(r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return None

def create_item_with_values(api_key, board_id, item_name, column_id, column_type, column_value):
    query5 = 'mutation ($myItemName: String!, $columnVals: JSON!) { create_item (board_id:%s, item_name:$myItemName, column_values:$columnVals) { id } }' % board_id
    vars = { 'myItemName' : item_name, 'columnVals' : json.dumps({column_id : {column_type : column_value} }) }
    data = {'query' : query5, 'variables' : vars}
    headers = {"Authorization" : api_key}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    print(r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return None

def monday_send_notification(api_key, user_id, board_id, msg):    
    query5 = "mutation {create_notification (user_id: %s, target_id: %s, text: \"%s\", target_type: Project) { text }}" % (user_id, board_id, msg)
    data = {"query" : query5}
    print(data)
    headers = {"Authorization" : api_key}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    print(r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return None

def create_leader_board_item(board_id, group_id, item_name, rating_id, rating, people_id, user_id, api_key):
    query9 = "mutation { create_item (board_id: %s, group_id: \"%s\", item_name: \"%s\" column_values: \"{\\\"%s\\\" : {\\\"rating\\\" : \\\"%s\\\"}, \\\"%s\\\" : {\\\"personsAndTeams\\\":[{\\\"id\\\":%s,\\\"kind\\\":\\\"person\\\"}]}}\")  { id }}" % (board_id, group_id, item_name, rating_id, rating, people_id, user_id)
    data = {'query' : query9}
    print('leader board data mutation -----', data)
    headers = {"Authorization" : api_key}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    print(r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return None

def create_mentor_board_item(board_id, group_id, item_name, people_cmn_id, user_id, mentoer_cmn_id, mentor_id, api_key):
    query9 = "mutation { create_item (board_id: %s, group_id: \"%s\", item_name: \"%s\" column_values: \"{\\\"%s\\\" : {\\\"personsAndTeams\\\":[{\\\"id\\\":%s,\\\"kind\\\":\\\"person\\\"}]}, \\\"%s\\\" : {\\\"personsAndTeams\\\":[{\\\"id\\\":%s,\\\"kind\\\":\\\"person\\\"}]}}\")  { id }}" % (board_id, group_id, item_name, people_cmn_id, user_id, mentoer_cmn_id, mentor_id)
    data = {'query' : query9}
    headers = {"Authorization" : api_key}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    print(r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return None

def rate_student_board(item_id, board_id, column_id, api_key):
    query9 = "mutation{change_multiple_column_values(item_id:%s, board_id:%s, column_values:\"{\\\"%s\\\" : {\\\"rating\\\" : 1}}\"){ id name }}" %(item_id, board_id, column_id)
    data = {'query' : query9}
    headers = {"Authorization" : api_key}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    print(r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return None

def delete_column(column_id, board_id, api_key):
    query9 = "mutation{delete_column (column_id: \"%s\", board_id: %s){ id }}" % (column_id, board_id)
    data = {'query' : query9}
    headers = {"Authorization" : api_key}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    print(r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return None

def change_board_name(board_id, name, api_key):
    query9 = "mutation {\n  update_board(board_id: %s, board_attribute: name, new_value: \"%s\")\n}"% (board_id, name)
    data = {'query' : query9}
    headers = {"Authorization" : api_key}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    print(r.json())
    if r.status_code ==200:
        return r.json()
    else:
        return None