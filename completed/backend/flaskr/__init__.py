import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_cats(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  category = [question.format() for question in selection]
  current_cat = category[start:end]

  return current_cat

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)


  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories') # no need to specify methods by defult it is GET
  def get_all_categories():
    selection =  Category.query.all()
    #categories = [category.format() for category in selection]
    categories = {cat.id:cat.type for cat in selection}
    if len(selection) == 0:
      abort(404)
    return jsonify({
      "success": True,
      "categories": categories
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 


  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')# no need to specify methods by defult it is GET
  def get_all_questions():
    selection = Question.query.all()
    current_cats = paginate_cats(request, selection)
    cats = Category.query.all()
    #category = list(map(Category.format, cats)) or [category.format() for category in selection]
    category = {cat.id:cat.type for cat in cats} # only this worked
    if len(current_cats) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_cats,
      'total_questions': len(selection),
      'categories':category,
      'current_category':None # i have no idea what you mean about that ?
    })

    


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_book(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_cats = paginate_cats(request, selection)

      return jsonify({
        'success': True,
        'deleted_question':question_id
      })

    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions' , methods=['POST'])
  def create_question():
    body = request.get_json()
    newquestion = body.get('question',None)
    newanswer = body.get('answer',None)
    newdifficulty = body.get('difficulty',None)
    newcategory =body.get('category',None )
    if not newquestion:
      abort(422)
    if not newquestion:
      abort(422)
    if not newanswer:
      abort(422)
    if not newdifficulty:
      abort(422)
    if not newcategory:
      abort(422)
    try:
      ques = Question(question=newquestion, answer=newanswer, difficulty=newdifficulty,category=newcategory)
      ques.insert()

      selection = Question.query.order_by(Question.id).all()
      current_cat = paginate_cats(request, selection)

      return jsonify({
        'success': True,
        'total_questions':len(selection)
        
      })

    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/searchresult' , methods=['POST'])
  def get_specific_question():
    body = request.get_json()
    search = body.get('searchTerm', None)

    try:
      if search:
        selection = Question.query.filter(Question.question.ilike('%{}%'.format(search))).all()
        #selection = Book.query.order_by(Book.id).filter(or_(Book.title.ilike('%{}%'.format(search)), Book.author.ilike('%{}%'.format(search))))
        current_cat = [question.format() for question in selection]
       #cats = Category.query.all()
       #category = {cat.id:cat.type for cat in cats}

        return jsonify({
          'success': True,
          'questions':current_cat,
          'total_questions': len(selection),
         # 'categories': category,
          'current_category':None # i have no idea what you mean about that ?
        })

    except:
      abort(422)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')#no need to specify methods by defult it is GET
  def questions_based_on_category(category_id):


    try:
      selection = Question.query.filter(Question.category == str(category_id)).all()
      cats = [question.format() for question in selection]
      
      return jsonify({
        'success': True,
        'questions':cats,
        'total_questions': len(selection),
        'current_category':category_id
      })
    except:
      abort(404)


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes',methods=['POST'])
  def quiz():
    try:

      body = request.get_json()
      quiz_category = body.get('quiz_category')
      previous_questions = body.get('previous_questions')
      if (not 'quiz_category' in body and not 'previous_questions' in body):
        abort(422)

      if ( quiz_category['id']):
        questions = Question.query.filter_by(category=quiz_category['id']).filter(Question.id.notin_((previous_questions))).all()
      else:
        questions = Question.query.filter(Question.id.notin_((previous_questions))).all()
      if len(questions) > 0:
        generate_questions = questions[random.randrange(0, len(questions))].format()
        return jsonify({
          'success': True,
          'question': generate_questions
        })
      else:
        return jsonify({
          'success': True,
          'question': None
        })

    except:
        abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400
  
  return app

    