from App.database import db
from App.models.competition import Competition
from App.models.result import Result
from flask import jsonify
import datetime
import csv
from werkzeug.utils import secure_filename
import os

def create_competition(name, date, description=None):
    try:
        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        competition = Competition(name=name, date=date_obj, description=description)
        db.session.add(competition)
        db.session.commit()
        return jsonify({'message': 'Competition created successfully!', 'competition': competition.to_dict()})
    except ValueError as ve:
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD.'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

def import_results(competition_id, data):
    try:
        competition = Competition.query.get(competition_id)
        if not competition:
            return jsonify({'error': 'Competition not found.'}), 404
        
        results = data.get('results', [])
        for result_data in results:
            result = Result(
                competition_id=competition_id,
                student_id=result_data['student_id'],
                score=result_data['score'],
                rank=result_data['rank']
            )
            db.session.add(result)
        db.session.commit()
        return jsonify({'message': 'Results imported successfully!'}), 200
    except KeyError as ke:
        return jsonify({'error': f'Missing key in input data: {str(ke)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

def import_results_from_file(competition_id, file_path):
    try:
        competition = Competition.query.get(competition_id)
        if not competition:
            return jsonify({'error': 'Competition not found.'}), 404

        filename = secure_filename(file_path)
        if not os.path.exists(filename):
            return jsonify({'error': 'File not found. Please provide a valid file path.'}), 400
        
        results_data = []
        with open(filename, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                try:
                    result_data = {
                        'student_id': int(row['student_id']),
                        'score': float(row['score']),
                        'rank': int(row['rank'])
                    }
                    results_data.append(result_data)
                except ValueError as ve:
                    return jsonify({'error': f'Invalid value in CSV file: {str(ve)}'}), 400
                except KeyError as ke:
                    return jsonify({'error': f'Missing key in CSV file: {str(ke)}'}), 400
        
        response = import_results(competition_id, {'results': results_data})
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def get_competitions():
    competitions = Competition.query.all()
    return jsonify([comp.to_dict() for comp in competitions])

def get_competition_results(competition_id):
    try:
        competition = Competition.query.get(competition_id)
        if not competition:
            return jsonify({'error': 'Competition not found.'}), 404
        
        results = Result.query.filter_by(competition_id=competition_id).all()
        return jsonify([res.to_dict() for res in results])
    except Exception as e:
        return jsonify({'error': str(e)}), 400
