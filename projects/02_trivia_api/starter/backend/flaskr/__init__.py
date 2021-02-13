import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @(DONE)TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={'/': {'origins': '*'}})

  '''
  @(DONE)TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @(DONE)TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def retrieve_categories():
    categories = Category.query.order_by(Category.id).all()
    categories_data= [category.type for category in categories]

    print (categories_data)

    if len(categories_data) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': categories_data
    })



  '''
  @(DONE)TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for two pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions')
  def retrieve_questions():
    categories = Category.query.order_by(Category.id).all()
    categories_data= [category.type for category in categories]
    
    page = request.args.get('page', 1, type=int)

    questions = Question.query.order_by(Question.id).all()
    questions_data= [question.format() for question in questions]

    start=10*(page-1)
    end=start+10
    
    if len(questions_data[start:end]) == 0:
      abort(404)
    
    print(start)
    print(end)
    totalquestions=len(questions)

    return jsonify({
      'success': True,
      'questions': questions_data[start:end],
      'total_questions': totalquestions,
      'categories': categories_data,
      'current_category': "Science"
    })


  '''
  @(DONE)TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/question/<int:question_id>',methods=['DELETE'])
  def delete_question(question_id):
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()

      return jsonify({
        'success': True,
      })

  '''
  @(DONE)TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''


  @app.route('/questions', methods=['POST'])
  def create_question():
    
    body = request.get_json()

    question = body.get('question', None)
    answer = body.get('answer', None)
    difficulty = body.get('difficulty', None)
    category = body.get('category', None)

    print(type(category))

    

    try:
      newquestion = Question(question=question, answer=answer, difficulty=difficulty ,category=int(category)+1)
      newquestion.insert()

      return jsonify({
        'success': True,
      })

    except:
      abort(422)



  '''
  @(DONE)TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions/search', methods=['POST'])
  def search_question():

    try:  
      body = request.get_json()

      searchTerm = body.get('searchTerm', None)

      questions=Question.query.filter(Question.question.ilike("%"+searchTerm+"%")).all()

      questions_data= [question.format() for question in questions]

      return jsonify({
        'success': True,
        'questions': questions_data,
        'total_questions': len(questions_data),
        'currentCategory': "Science"
      })

    except:
      abort(422)




  '''
  @(DONE)TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/category/<int:id>/questions')
  def retrieve_questionsByCategory(id):
    categories = Category.query.order_by(Category.id).all()
    categories_data= [category.type for category in categories]
    page = request.args.get('page', 1, type=int)

    questions = Question.query.filter_by(category=id+1).order_by(Question.id).all()
    questions_data= [question.format() for question in questions]

    current_category=Category.query.filter_by(id=id+1).first().type

    start=10*(page-1)
    end=start+10
    
    if len(questions_data[start:end]) == 0:
      abort(404)
    
    totalquestions=len(questions)

    return jsonify({
      'success': True,
      'questions': questions_data[start:end],
      'total_questions': totalquestions,
      'current_category': current_category
    })



  '''
  @(DONE)TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def take_quiz():
    
    try:

      body = request.get_json()

      previous_questions = body.get('previous_questions', None)
      quiz_category = body.get('quiz_category', None)

      print((previous_questions))

      questions = Question.query.filter_by(category=int(quiz_category['id'])+1).order_by(Question.id).all()
      questions_data= [question.format() for question in questions]

      listx=questions_data.copy()
      for i in questions_data:
        for j in previous_questions:
          if i['id']==j:
            print(i)
            print(j)
            listx.remove(i)

      
      if(len(listx)==0):
        return jsonify({
          'success':True
        })

      num1 = random.randint(0, len(listx)-1)


      return jsonify({
        'success':True,
        'question':listx[num1]
      })

    except:
      abort(422)


  '''
  @(DONE)TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Not found"
        }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
        }), 422

  
  return app

    