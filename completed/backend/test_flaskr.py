import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'udacity', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.new_book = {
            'question': 'What is your name?',
            'answer': 'Abdullah Alessa',
            'difficulty': 5,
            'category': 6
        }
        self.new_book_error = {
            'question': 'What is your name?',
            'difficulty': 5,
            'category': 6
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """


    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_get_paginated_books(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
    
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    def test_get_book_search_with_results(self):
        res = self.client().post('/questions/searchresult', json={'searchTerm': 'Whose'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions']>0,True)
        self.assertIsNotNone((data['questions']))
    
    def test_get_book_search_without_results(self):
        res = self.client().post('/questions/searchresult', json={'searchTerm': 'abcdefghigklmno'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions']==0,True)
        self.assertIsNotNone((data['questions']))

    def test_get_book_search_error(self):

        res = self.client().post('/questions/searchresults', json={'searchTerm': 'c',})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_questions_based_on_category(self):
        res = self.client().get('/categories/3/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone((data['questions']))
        self.assertTrue((data['total_questions'] > 0 , True))
        self.assertTrue((data['current_category'] == 3,True))

    def test_questions_based_on_category_error(self):
        res = self.client().get('/categories/category/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_quiz(self):
        new_quiz = {'quiz_category': {'type': 'Entertainment', 'id': 5},'previous_questions': []}

        res = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_quiz_error(self):
        new_quiz = {'quiz_category': {'type': 'Entertainment', 'id': 5}}
        res = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_delete_book(self):
        newQuestion = Question(question='what is your name', answer='Abdullah Alessa',difficulty=5 , category=6)
        newQuestion.insert()
        res = self.client().delete(f'/questions/{newQuestion.id}')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == newQuestion.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_question'], (newQuestion.id))
        self.assertEqual(question, None)
    

    def test_404_if_book_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
    
    def test_create_new_book(self):
        res = self.client().post('/questions', json=self.new_book)
        data = json.loads(res.data)
 
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'] > 0,True)
        
    
    def test_422_if_book_creation_fails(self):
        res = self.client().post('/questions', json=self.new_book_error)
        data = json.loads(res.data)
       
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()