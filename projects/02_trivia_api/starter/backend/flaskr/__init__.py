#!/usr/bin/python
# -*- coding: utf-8 -*-
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

    CORS(app, resources={'/': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories')
    def retrieve_categories():
        categories = Category.query.order_by(Category.id).all()
        categories_data = [category.type for category in categories]

        if len(categories_data) == 0:
            abort(404)

        return jsonify({'success': True, 'categories': categories_data})

    @app.route('/questions')
    def retrieve_questions():
        categories = Category.query.order_by(Category.id).all()
        categories_data = [category.type for category in categories]

        page = request.args.get('page', 1, type=int)

        questions = Question.query.order_by(Question.id).all()
        questions_data = [question.format() for question in questions]

        start = 10 * (page - 1)
        end = start + 10

        if len(questions_data[start:end]) == 0:
            abort(404)

        totalquestions = len(questions)

        return jsonify({
            'success': True,
            'questions': questions_data[start:end],
            'total_questions': totalquestions,
            'categories': categories_data,
            'current_category': 'Science',
            })

    @app.route('/question/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id
                == question_id).one_or_none()

        if question is None:
            abort(404)

        question.delete()

        return jsonify({'success': True})

    @app.route('/questions', methods=['POST'])
    def create_question():

        body = request.get_json()

        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)

        try:
            newquestion = Question(question=question, answer=answer,
                                   difficulty=difficulty,
                                   category=int(category) + 1)
            newquestion.insert()

            return jsonify({'success': True})
        except:

            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_question():

        try:
            body = request.get_json()

            searchTerm = body.get('searchTerm', None)

            questions = \
                Question.query.filter(Question.question.ilike('%'
                    + searchTerm + '%')).all()

            questions_data = [question.format() for question in
                              questions]

            return jsonify({
                'success': True,
                'questions': questions_data,
                'total_questions': len(questions_data),
                'currentCategory': 'Science',
                })
        except:

            abort(422)

    @app.route('/category/<int:id>/questions')
    def retrieve_questionsByCategory(id):
        categories = Category.query.order_by(Category.id).all()
        categories_data = [category.type for category in categories]
        page = request.args.get('page', 1, type=int)

        questions = Question.query.filter_by(category=id
                + 1).order_by(Question.id).all()
        questions_data = [question.format() for question in questions]

        try:
            current_category = Category.query.filter_by(id=id
                    + 1).first().type
        except:
            abort(422)

        start = 10 * (page - 1)
        end = start + 10

        if len(questions_data[start:end]) == 0:
            abort(404)

        totalquestions = len(questions)

        return jsonify({
            'success': True,
            'questions': questions_data[start:end],
            'total_questions': totalquestions,
            'current_category': current_category,
            })

    @app.route('/quizzes', methods=['POST'])
    def take_quiz():

        try:

            body = request.get_json()

            previous_questions = body.get('previous_questions', None)
            quiz_category = body.get('quiz_category', None)

            if quiz_category['type'] == 'click':
                questions = Question.query.all()
            else:
                questions = \
                    Question.query.filter_by(category=int(quiz_category['id'
                        ]) + 1).order_by(Question.id).all()

            questions_data = [question.format() for question in
                              questions]

            listx = questions_data.copy()
            for i in questions_data:
                for j in previous_questions:
                    if i['id'] == j:
                        listx.remove(i)

            if len(listx) == 0:
                return jsonify({'success': True})

            num1 = random.randint(0, len(listx) - 1)

            return jsonify({'success': True, 'question': listx[num1]})
        except:

            abort(422)

    @app.errorhandler(404)
    def not_found(error):
        return (jsonify({'success': False, 'error': 404,
                'message': 'Not found'}), 404)

    @app.errorhandler(422)
    def unprocessable(error):
        return (jsonify({'success': False, 'error': 422,
                'message': 'unprocessable'}), 422)

    return app
