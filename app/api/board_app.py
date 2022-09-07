from app.api import bp
from flask import jsonify, request
from flask import render_template
from config import Config
from app.models import Authenticated, Question, User, Submission, BoardInfo, board_info, InitialFlag
from app.services import monday_get_boards, monday_check_item_data, CRUD, monday_send_notification, create_leader_board_item, create_mentor_board_item, \
    rate_student_board
import requests, json
from constants import BADGE, BADGE_PATH
from app.tasks import *

crud = CRUD()

@bp.route('/monday/index', methods=['GET'])
def monday_oauth_index():
    print("///////////.........INDEX.........///////////////")
    print('...args....', request.args)
    print('board_id', request.args.get('boardId'))
    auth =Authenticated.query.filter_by(board_id = request.args.get('boardId')).first()
    print('auth', auth)
    if not auth:
        return render_template("redirect.html", board_id=request.args.get('boardId'), client_id = Config.MONDAY_CLIENT_ID)
    else:
        check_flag = InitialFlag.query.filter_by(board_id = request.args.get('boardId')).first()
        if check_flag:
            if check_flag.status == False:
                monday_initial_setup.delay(auth.api_key, request.args.get('boardId'))
        else:
            flag =crud.create(InitialFlag, {"board_id": request.args.get('boardId')})
            print(flag)
            monday_initial_setup.delay(auth.api_key, request.args.get('boardId'))
    return render_template("home_page.html", api_key = auth.api_key)




@bp.route('/monday/oauth/redirect', methods=['GET'])
def monday_oauth_redirect():
    print("///////////.........OAUTH REDIRECT..........///////////////")
    print('...args....', request.args)
    #print('board_id', request.args.get('board_id'))
    code = request.args.get('code')
    print(code)
    url="https://auth.monday.com/oauth2/token"
    payload=f'client_id={Config.MONDAY_CLIENT_ID}&client_secret={Config.MONDAY_CLIENT_SECRET}&code={code}&redirect_uri=https%3A%2F%2Fdaily-quotes-monday.herokuapp.com%2Fv1%2Fmonday%2Foauth%2Fredirect'
    headers={'Content-Type':'application/x-www-form-urlencoded'}

    response=requests.request("POST",url,headers=headers,data=payload)
    print(response.json())
    response = response.json()
    api_key = response.get("access_token")
    print("api_key", api_key)
    boards = monday_get_boards(api_key)
    for i in boards.get('data').get('boards'):
        print('board id', i.get('id'))
        auth =crud.create(Authenticated, {"board_id": i.get('id'), "api_key": api_key})
        print("token added to db", auth)
    #monday_initial_setup.delay(api_key)
    return render_template("home_page.html", api_key = auth.api_key)

@bp.route('/monday/item/load-quiz', methods=['GET'])
def item_load_quiz():
    print('...args....', request.args)
    item_id = request.args.get('itemId')
    board_id = request.args.get('boardId')
    auth = Authenticated.query.filter_by(board_id = board_id).first()
    if auth:
        api_key =auth.api_key
    item = monday_check_item_data(item_id, api_key)
    board_info = board_id + '/' + item.get('data', {}).get('items')[0].get('group').get('id') + '/' + item_id
    print('---------board_info-------', board_info)
    qus = BoardInfo.query.filter_by(board_info =board_info).first()    
    quiz = Question.query.filter_by(id= int(qus.source_id)).first()
    #print(qus, quiz, quiz.title, quiz.title, quiz.details, quiz.id, quiz.question, json.loads(quiz.answer.choices), quiz.description, quiz.quiz_id)
    details = (quiz.details).replace('/n', '').replace('{{', '<img src="').replace('}}', '" />').replace('{iframe}', quiz.interactive_console)
    print('details----', details)
    description = (quiz.description).replace('/n', '')
    print('description----', description)
    return render_template("quiz.html",api_key = api_key, title = quiz.title , details = details, qus_id = quiz.id, question = quiz.question, options= json.loads(quiz.answer.choices), description = description, quiz_id = quiz.quiz_id, iframe = quiz.interactive_console)

@bp.route('/monday/item/load-iframe', methods=['GET'])
def item_load_iframe():
    print('...args....', request.args)
    return render_template("iframe.html")

@bp.route('/monday/quiz/validate/<int:quiz_id>/<int:qus_id>', methods=['POST'])
def quiz_validate_answer(quiz_id, qus_id):
    print('//// Check Answer ////')
    print('quiz_id', quiz_id, 'qus_id', qus_id)
    answer= request.json
    print(answer)
    monday_user_id = answer.get('user_id')
    user = User.query.filter_by(monday_user_id = monday_user_id).first()
    quiz = Question.query.filter_by(id=qus_id).first()
    check_submission = Submission.query.filter_by(quiz_id = quiz_id, user_id = user.id).first()
    if quiz:
        if answer.get('answer') == quiz.correct_answer:
            print('Correct answer')
            response = 'Correct answer'
            if check_submission:
                submitted = json.loads(check_submission.q_and_a)
                print('answer submitted', submitted)
                if quiz.id not in submitted:
                    print('pass')
                    submitted.append(quiz.id)
                    point = user.point_count
                    user.point_count = point + 10
                    check_submission.q_and_a = json.dumps(submitted)
                    check_quiz = Quizzes.query.filter_by(id = quiz_id).first()
                    quiz_compleated = True
                    db.session.commit()
                    for i in check_quiz.questions:
                        if len(i.question )>1 and i.id not in submitted:
                            quiz_compleated = False
                            print('quiz not compleated')
                    if quiz_compleated:
                        print('quiz completed')
                        check_submission.status = True
                        db.session.commit()
                        check_sub = Submission.query.filter_by(status = True, user_id = user.id).all()
                        total_quiz = Quizzes.query.filter_by(disabled = False).all()
                        auth = Authenticated.query.filter_by(board_id = str(answer.get('bord_id'))).first()
                        print('auth', auth)
                        if auth:
                                msg = f'Congratulations....!, {user.name} compleated {check_quiz.title} quiz.'
                                print(msg)
                                monday_send_notification(auth.api_key, monday_user_id, answer.get('bord_id'), msg)
                        percentage = (len(check_sub)/len(total_quiz))* 100
                        if len(total_quiz) == len(check_sub):
                            badge = 5
                        elif percentage >= 90:
                            badge = 4
                        elif percentage >= 75:
                            badge = 3
                        elif percentage >= 50:
                            badge = 2
                        elif percentage >= 20:
                            badge = 1
                        else:
                            badge = 0
                        if user.badge != badge:
                            print('new badge added')
                            user.badge = badge
                            db.session.commit()
                            if auth:
                                msg = f'Congratulations....!, {user.name} earned {BADGE[badge]} badge.'
                                monday_send_notification(auth.api_key, monday_user_id, answer.get('bord_id'), msg)
                            if badge == 1:
                                board_info = BoardInfo.query.filter_by(source_id = monday_user_id).first()
                                ids = (board_info.board_info).split('/')
                                board_info.board_type = 1
                                db.session.commit()
                                item = monday_check_item_data(ids[2], auth.api_key)
                                column_ids = item.get('data', {}).get('items')[0].get('column_values')
                                rate_student_board(ids[2], ids[0], column_ids[2]['id'], auth.api_key)
                                add_badge = monday_add_item_file(auth.api_key, ids[2], 'student_badge.png', 'app/static/images/student_badge.png', column_ids[2]['id'])
                            if badge == 5:
                                # mentors board
                                board_info = BoardInfo.query.filter_by(source_id = str(answer.get('bord_id')), board_type = 6).first()
                                ids = (board_info.board_info).split('/')
                                board_data = monday_get_board_data(ids[0], auth.api_key)
                                column_ids = board_data.get('data', {}).get('boards')[0].get('columns')
                                #create_item_with_values(auth.api_key, ids[0], user.name, column_ids[1], 'person', monday_user_id)
                                create_mentor_board_item(ids[0], ids[1], user.name, column_ids[1]['id'], monday_user_id, column_ids[2]['id'], monday_user_id, auth.api_key)
                            
                            # Add to Leader board
                            board_grp = BoardInfo.query.filter_by(source_id = str(answer.get('bord_id')), board_type = badge).first()
                            ids = (board_grp.board_info).split('/')
                            board_data = monday_get_board_data(ids[0], auth.api_key)
                            column_ids = board_data.get('data', {}).get('boards')[0].get('columns')
                            item = create_leader_board_item(ids[0], ids[1], user.name, column_ids[2]['id'], badge, column_ids[1]['id'], monday_user_id, auth.api_key)
                            add_badge = monday_add_item_file(auth.api_key, item.get('data').get('create_item').get('id'), BADGE_PATH.get(badge).get('name'), BADGE_PATH.get(badge).get('path'), column_ids[2]['id'])
                            #delete prvs item
            else:
                print('add submission')
                point = user.point_count
                user.point_count = point + 10
                q_and_a = [qus_id]
                s = Submission(q_and_a = json.dumps(q_and_a), quiz_id = quiz_id, user_id = user.id)
                db.session.add(s)
                db.session.commit()

        else:
            response = 'Wrong answer'
            print('Wrong answer')
    return jsonify({"status": 200, "data": response})

@bp.route('/monday/redirect/board-setup', methods=['POST'])
def redirect_board_setup():
    print('//// Board setup ////')
    print('...args....', request.args)
    board_id = request.args.get('board_id')
    auth = Authenticated.query.filter_by(board_id = board_id).first()
    if auth:
        check_flag = InitialFlag.query.filter_by(board_id = board_id).first()
        if check_flag:
            if check_flag.status == False:
                monday_initial_setup.delay(auth.api_key, board_id)
        else:
            flag =crud.create(InitialFlag, {"board_id": board_id})
            print(flag)
            monday_initial_setup.delay(auth.api_key, board_id)
        return jsonify({"status": 200, "message": "ok"})
    else:
        print("no api key in  db")
        return render_template("redirect.html", board_id= board_id, client_id = Config.MONDAY_CLIENT_ID)

@bp.route('/monday/user', methods=['POST'])
def monday_get_user_data():
    print(request.json)
    print('---------------------User--------------')
    data = request.json
    user = User.query.filter_by(monday_user_id= str(data.get('user_id'))).first()
    if user:
        print('user', user, user.submission)
        return jsonify({"status": 2000, "message": ""})
    else:
        # auth =Authenticated.query.filt0, "meer_by(board_id = data.get('board_id')).first()
        # if auth:
        user = crud.create(User, {"name": data.get('name'), "email":data.get('email'), "monday_user_id": str(data.get('user_id'))})
        # submissions=[]
        # for i in user.submission:
        #     submissions.append({"quiz_id": i.quiz_id, "status": i.status})
        print("new user added", user)
        return jsonify({"status": 200, "message": "new user added"})

@bp.route('/monday/quiz/user-status/<int:user_id>/<int:qus_id>', methods=['POST'])
def monday_quiz_user_status(user_id, qus_id):
    print('---------------quiz------User-----status---------')
    print(user_id, qus_id, type(user_id), type(qus_id))
    user = User.query.filter_by(monday_user_id = str(user_id)).first()
    quiz = Question.query.filter_by(id=qus_id).first()
    check_submission = Submission.query.filter_by(quiz_id = quiz.quiz_id, user_id = user.id).first()
    if check_submission:
        submitted = json.loads(check_submission.q_and_a)
        print('answer submitted', submitted)
        if quiz.id in submitted:
            print('pass')
            return jsonify({"status": 200, "quiz_status": 1})
    return jsonify({"status": 200, "quiz_status": 0})
