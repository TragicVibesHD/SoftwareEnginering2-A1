from App.database import db
from App.models.competition import Competition
from App.models.result import Result
from flask import jsonify
import datetime
import csv
from werkzeug.utils import secure_filename
import os

def create_competition(name, date, description=None):
    """
    Creates a competition with the specified name, date, and optional description.
    """
    try:
        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        competition = Competition(name=name, date=date_obj, description=description)
        db.session.add(competition)
        db.session.commit()
        return jsonify({'message': 'Competition created successfully!', 'competition': competition.to_dict()})
    except ValueError:
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD.'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

def import_results(competition_identifier, data, use_name=False):
    """
    Imports results for a specified competition using its ID or name.
    """
    try:
        competition = None
        if use_name:
            competition = Competition.query.filter_by(name=competition_identifier).first()
        else:
            competition = Competition.query.get(competition_identifier)
        
        if not competition:
            return jsonify({'error': 'Competition not found.'}), 404

        results = data.get('results', [])
        if not results:
            return jsonify({'error': 'No results provided to import.'}), 400

        for result_data in results:
            result = Result(
                competition_id=competition.id,
                student_username=result_data['student_username'],
                score=result_data['score']
            )
            db.session.add(result)
        db.session.commit()
        return jsonify({'message': 'Results imported successfully!'}), 200
    except KeyError as ke:
        return jsonify({'error': f'Missing key in input data: {ke}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

def import_results_from_file(competition_identifier, file_path, use_name=False):
    """
    Imports results for a specified competition from a CSV file using its ID or name.
    """
    try:
        competition = None
        if use_name:
            competition = Competition.query.filter_by(name=competition_identifier).first()
        else:
            competition = Competition.query.get(competition_identifier)

        if not competition:
            return jsonify({'error': 'Competition not found.'}), 404

        filename = secure_filename(file_path)
        if not os.path.exists(filename):
            return jsonify({'error': 'File not found. Please provide a valid file path.'}), 400

        # Clear existing results
        Result.query.filter_by(competition_id=competition.id).delete()
        db.session.commit()

        results_data = []
        with open(filename, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                try:
                    results_data.append({
                        'student_username': row['student_username'],
                        'score': float(row['score'])
                    })
                except (ValueError, KeyError) as e:
                    return jsonify({'error': f'Invalid value in CSV file: {e}'}), 400

        return import_results(competition.id, {'results': results_data})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

def get_competitions():
    """
    Retrieves a list of all competitions.
    """
    try:
        competitions = Competition.query.all()
        if not competitions:
            return jsonify({'error': 'No competitions found.'}), 404
        return jsonify([comp.to_dict() for comp in competitions]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def get_competition_results(competition_id=None, competition_name=None):
    """
    Retrieves the results of a competition by its ID or name.
    """
    try:
        competition = None
        if competition_id:
            competition = Competition.query.get(competition_id)
        elif competition_name:
            competition = Competition.query.filter_by(name=competition_name).first()

        if not competition:
            return jsonify({'error': 'Competition not found.'}), 404

        results = Result.query.filter_by(competition_id=competition.id).order_by(Result.score.desc()).all()
        if not results:
            return jsonify({'error': 'No results found for this competition.'}), 404

        return jsonify({
            'competition_id': competition.id,
            'competition_name': competition.name,
            'results': [res.to_dict() for res in results]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
