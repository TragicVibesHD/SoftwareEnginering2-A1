from App.database import db
from App.models.competition import Competition
from App.models.result import Result
from flask import jsonify
import datetime
import csv
from werkzeug.utils import secure_filename

def create_competition(name, date, description=None):
    try:
        # Validate date format
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
        # Validate competition existence
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

def import_results_cli():
    try:
        competition_id = int(input("Enter competition ID: "))
        num_results = int(input("Enter number of results to import: "))
        
        results_data = []
        for _ in range(num_results):
            student_id = int(input("Enter student ID: "))
            score = float(input("Enter score: "))
            rank = int(input("Enter rank: "))
            results_data.append({
                'student_id': student_id,
                'score': score,
                'rank': rank
            })
        
        # Call the import_results function
        response = import_results(competition_id, {'results': results_data})
        
        # Unpack the response
        if isinstance(response, tuple):
            response_body, status_code = response
        else:
            response_body = response
            status_code = 200  # Assume 200 if not specified
        
        # Extract data from the response
        if isinstance(response_body, str):
            data = response_body
        else:
            data = response_body.get_json()
        
        print(f"Response: {data}, Status Code: {status_code}")
    except ValueError:
        print("Invalid input. Please enter the correct data types.")
    except Exception as e:
        print(f"Error: {str(e)}")

def import_results_from_file(competition_id, file_path):
    try:
        # Validate competition existence
        competition = Competition.query.get(competition_id)
        if not competition:
            return jsonify({'error': 'Competition not found.'}), 404
        
        # Secure filename to avoid directory traversal attacks
        filename = secure_filename(file_path)
        
        results_data = []
        with open(filename, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Assume CSV has columns: student_id, score, rank
                result_data = {
                    'student_id': int(row['student_id']),
                    'score': float(row['score']),
                    'rank': int(row['rank'])
                }
                results_data.append(result_data)
        
        # Use the existing import_results function to handle the database insertion
        response = import_results(competition_id, {'results': results_data})
        return response
    except FileNotFoundError:
        return jsonify({'error': 'File not found. Please provide a valid file path.'}), 400
    except KeyError as ke:
        return jsonify({'error': f'Missing key in CSV file: {str(ke)}'}), 400
    except ValueError as ve:
        return jsonify({'error': f'Invalid value in CSV file: {str(ve)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def get_competitions():
    competitions = Competition.query.all()
    return jsonify([comp.to_dict() for comp in competitions])

def get_competition_results(competition_id):
    try:
        # Validate competition existence
        competition = Competition.query.get(competition_id)
        if not competition:
            return jsonify({'error': 'Competition not found.'}), 404
        
        results = Result.query.filter_by(competition_id=competition_id).all()
        return jsonify([res.to_dict() for res in results])
    except Exception as e:
        return jsonify({'error': str(e)}), 400