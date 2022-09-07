from celery import Celery
from app import create_app
import json
from datetime import date
from config import Config
from datetime import datetime, timedelta
from app import db
#from app.models import TimeZone
#from app.services.crud import CRUD 
from constants import BOARD_NAME, COLUMN_LIST, LEADER_COLUMN, DAILY_QUOTE_COLUMN, MENTORS_COLUMN
from app.services import monday_get_boards, monday_get_board_data, monday_create_group, create_item, monday_add_item_file, \
    create_item_with_values, monday_create_column, monday_create_board , CRUD, delete_column, monday_send_notification, change_board_name
from app.models import BoardInfo, Quizzes, DidYouKnow, InitialFlag

app = create_app()
app.app_context().push()
app = Celery('tasks', broker=Config.REDIS_URL)
crud = CRUD()
today = datetime.today()


BROKER_CONNECTION_RETRY = True  # will make it retry whenever it fails
BROKER_CONNECTION_MAX_RETRIES = 0  # will disable the retry limit.
BROKER_CONNECTION_TIMEOUT = 120
app.conf.beat_schedule = {
    'task1': {
        'task': 'app.tasks.start_processing',
        'schedule': timedelta(minutes=1)
    },
    # 'options': {
    #     'expires': 15.0  # beat scheduled tasks will be removed automatically
    # }
}
app.conf.timezone = 'UTC'

@app.task
def background_job_one(region: str, org_id: int, stored_resources: dict):
    return True


@app.task
def second_function():
    job_three.delay("<params>")
    return True


@app.task
def job_three(**kwargs):
    return True

@app.task
def start_processing():
    job_three.delay()

@app.task    
def monday_initial_setup(api_key, board_id):
    check_flag = InitialFlag.query.filter_by(board_id = board_id).first()
    if check_flag.status == False:
        change_board_name(board_id, "Awareness", api_key)
        check_flag.status = True
        db.session.commit()
        boards = monday_get_boards(api_key)
        leader_status = False
        mentors_status = False
        quotes_status = False
        for i in boards.get('data').get('boards'):
            if i.get('name') == 'Leader Board':
                #leader_board_id = i.get('id') 
                leader_status = True
            if i.get('name') == 'Mentors Board':
                #mentors_board_id = i.get('id') 
                mentors_status = True
            if i.get('name') == 'Did You Know':
                quotes_board_id = i.get('id') 
                quotes_status = True

        board_data = monday_get_board_data(board_id, api_key)
        grp_names =[]
        for grp in board_data['data']['boards'][0]['groups']:
            grp_names.append(grp['title'])
        print('grp_names', grp_names)
        grp_list = Quizzes.query.filter_by(disabled = False).all()
        grp_list.reverse()
        #delete existing columns
        for i in grp_list:
            if i.title not in grp_names:
                for i in board_data.get('data', {}).get('boards')[0].get('columns'):
                    print('delete column id ', i['id']) 
                    delete_column(i['id'], board_id, api_key)
                # for i in COLUMN_LIST:
                #     print(i["title"], i["column_type"])
                #     column = monday_create_column(api_key, board_id, i["title"], i["column_type"])
                break
        for i in grp_list:
            print('i in GROUP_LIST', i.title, board_id)
            if i.title not in grp_names:
                print('grp added')
                grp =monday_create_group(board_id, i.title, api_key)
                for n, g in enumerate(i.questions):
                    q_item =create_item(board_id, g.title, api_key)
                    print('board_id', board_id)
                    print('grp id ', grp.get('data').get('create_group').get('id'))
                    print('item_id' , n, q_item.get('data').get('create_item').get('id'))
                    board_info = board_id + '/' + grp.get('data').get('create_group').get('id') + '/' + q_item.get('data').get('create_item').get('id')
                    print('adding Ids to db', board_info)
                    crud.create(BoardInfo, {"board_info": board_info, "source_id": str(g.id)})
        

                    
        if leader_status:
            pass
        else:
            print('create leader board')
            board_data = monday_create_board(api_key, 'Leader Board')
            print('board_data', board_data)
            print('board id', board_data.get('data').get('create_board').get('id'))
            for i in LEADER_COLUMN:
                print(i["title"], i["column_type"])
                column = monday_create_column(api_key, board_data.get('data').get('create_board').get('id'), i["title"], i["column_type"])
                if i["title"] == 'Badges':
                    column_id = column.get('data').get('create_column').get('id')
            for n, i in enumerate(['Student', 'Scholar', 'Researcher', 'Fellowship', 'Admirer']):
                print('create leader GROUP', i)
                grp = monday_create_group(board_data.get('data').get('create_board').get('id'), i, api_key)
                print(grp)
                if i == 'Student':   
                    board = monday_get_board_data(board_data.get('data').get('create_board').get('id'), api_key)
                    for g in board.get('data').get('boards')[0].get('subscribers'):
                        item =create_item(board_data.get('data').get('create_board').get('id'), g.get('name'), api_key)
                        print('create_item LEADER', item)
                        #add_badge = monday_add_item_file(api_key, item.get('data').get('create_item').get('id'), 'student_badge.png', 'app/static/images/student_badge.png', column_id)
                        #print('add_badge', add_badge)
                        board_info = board_data.get('data').get('create_board').get('id') + '/' + grp.get('data').get('create_group').get('id') + '/' + item.get('data').get('create_item').get('id')
                        print('adding Ids to db', board_info)
                        crud.create(BoardInfo, {"board_info": board_info, "board_type": 1, "source_id": str(g.get('id'))})
                else:
                    board_info = board_data.get('data').get('create_board').get('id') + '/' + grp.get('data').get('create_group').get('id')
                    print('adding Ids to db', board_info, board_data.get('data').get('create_board').get('id'), type (board_data.get('data').get('create_board').get('id')), len(board_data.get('data').get('create_board').get('id')))
                    crud.create(BoardInfo, {"board_info": board_info, "board_type": n + 1, "source_id": board_id})
        if mentors_status:
            pass
        else:
            print('create menters board')
            board_data = monday_create_board(api_key, 'Mentors Board')
            print('board_data', board_data)
            print('board id', board_data.get('data').get('create_board').get('id'))
            for i in MENTORS_COLUMN:
                print(i["title"], i["column_type"])
                column = monday_create_column(api_key, board_data.get('data').get('create_board').get('id'), i["title"], i["column_type"])
            grp = monday_create_group(board_data.get('data').get('create_board').get('id'), "Basics", api_key)
            print(grp)
            board_info = board_data.get('data').get('create_board').get('id') + '/' + grp.get('data').get('create_group').get('id')
            print('adding Ids to db', board_info, board_data.get('data').get('create_board').get('id'), type (board_data.get('data').get('create_board').get('id')), len(board_data.get('data').get('create_board').get('id')))
            crud.create(BoardInfo, {"board_info": board_info, "board_type": 6, "source_id": board_id})
        if quotes_status:
            q_board = monday_get_board_data(quotes_board_id, api_key)
            for i in q_board.get('data', {}).get('boards')[0].get('columns'):
                if i['title']=='Day':
                    column_id = i['id']
            query = DidYouKnow.query.filter_by(date = today, status= False).first()
            if query:
                col = create_item_with_values(api_key, quotes_board_id, query.quotes, column_id, 'date', today.strftime("%Y-%d-%b"))
                print("did u know col", col)
                query.status = True
                db.session.commit()
                msg = f"Did You know...!  {query.quotes}"
                print('message', msg)
                for i in board_data.get('data', {}).get('boards')[0].get('subscribers'):
                    monday_send_notification(api_key, i['id'], board_id, msg)
                
        else:
            print('create Did You Know board')
            board_data = monday_create_board(api_key, 'Did You Know')
            print('board_data', board_data)
            print('board id', board_data.get('data').get('create_board').get('id'))
            for i in DAILY_QUOTE_COLUMN:
                print(i["title"], i["column_type"])
                column = monday_create_column(api_key, board_data.get('data').get('create_board').get('id'), i["title"], i["column_type"])
                if i["title"] == 'Day':
                    column_id = column.get('data').get('create_column').get('id')
            
            grp = monday_create_group(board_data.get('data').get('create_board').get('id'), today.strftime("%B"), api_key)
            #item =create_item(board_data.get('data').get('create_board').get('id'), "Did You Know", api_key)
            query = DidYouKnow.query.filter_by(date = today, status= False).first()
            print('did you know', query, today)
            if query:
                col = create_item_with_values(api_key, board_data.get('data').get('create_board').get('id'), query.quotes, column_id, 'date', today.strftime("%Y-%d-%b"))
                print("did u know col", col)
                query.status = True
                db.session.commit()
                msg = f"Did You know...!  {query.quotes}"
                print('message', msg)
                for i in board_data.get('data', {}).get('boards')[0].get('subscribers'):
                    monday_send_notification(api_key, i['id'], board_id, msg)
        check_flag.status = False
        db.session.commit()

    return True
