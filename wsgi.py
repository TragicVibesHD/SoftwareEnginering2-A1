import click
import pytest
import sys
from flask import Flask
from flask.cli import AppGroup
from App.database import *
from App.models import *
from App.main import *
from App.controllers import *

app = create_app()
migrate = get_migrate(app)

@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    print('Database initialized.\n')

'''
User Commands
'''
user_cli = AppGroup('user', help='User object commands')

@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    try:
        create_user(username, password)
        print(f'User {username} created!\n')
    except Exception as e:
        print(f"Error: {e}\n")

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    try:
        if format == 'string':
            print(get_all_users() + '\n')
        else:
            print(get_all_users_json() + '\n')
    except Exception as e:
        print(f"Error: {e}\n")

app.cli.add_command(user_cli)

'''
Test Commands
'''
test_cli = AppGroup('test', help='Testing commands')

@test_cli.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    try:
        if type == "unit":
            sys.exit(pytest.main(["-k", "UserUnitTests"]))
        elif type == "int":
            sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
        else:
            sys.exit(pytest.main(["-k", "App"]))
    except Exception as e:
        print(f"Error running tests: {e}\n")

app.cli.add_command(test_cli)

'''
Student Commands
'''
student_cli = AppGroup('student', help='Student commands')

@student_cli.command('create_competition_cli')
def create_competition_cli():
    try:
        name = input("Enter competition name: ")
        date = input("Enter competition date (YYYY-MM-DD): ")
        description = input("Enter competition description (optional): ")
        response = create_competition(name, date, description)
        print_response(response)
    except Exception as e:
        print(f"Error: {e}\n")

@student_cli.command('import_results_cli')
def import_results_cli():
    try:
        competition_input = input("Enter competition ID or name: ").strip()
        use_name = not competition_input.isdigit()

        if not use_name:
            competition_input = int(competition_input)

        num_results = int(input("Enter number of results to import: "))
        results_data = [
            {
                'student_username': input(f"Enter student username for result {i+1}: "),
                'score': float(input(f"Enter score for result {i+1}: "))
            } for i in range(num_results)
        ]

        response = import_results(competition_input, {'results': results_data}, use_name=use_name)
        print_response(response)
    except ValueError:
        print("Invalid input. Please enter the correct data types.\n")
    except Exception as e:
        print(f"Error: {e}\n")

@student_cli.command('import_results_from_file_cli')
@click.argument('competition_id')
@click.argument('file_path')
def import_results_from_file_cli(competition_id, file_path):
    try:
        competition_id = int(competition_id)
        response = import_results_from_file(competition_id, file_path)
        print_response(response)
    except Exception as e:
        print(f"Error: {e}\n")

@student_cli.command('view_competitions_cli')
def view_competitions_cli():
    try:
        response = get_competitions()
        print_response(response)
    except Exception as e:
        print(f"Error: {e}\n")

@student_cli.command('view_competition_results_cli')
def view_competition_results_cli():
    try:
        competition_input = input("Enter competition ID or name: ").strip()
        try:
            competition_id = int(competition_input)
            response = get_competition_results(competition_id=competition_id)
        except ValueError:
            response = get_competition_results(competition_name=competition_input)
        print_response(response)
    except Exception as e:
        print(f"Error: {e}\n")

app.cli.add_command(student_cli)

def print_response(response):
    def ordinal(n):
        return f"{n}{'th' if 11 <= (n % 100) <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"

    if isinstance(response, tuple):
        data, status_code = response
    else:
        data = response
        status_code = 200

    if hasattr(data, 'get_json'):
        output = data.get_json()
    elif hasattr(data, 'get_data'):
        output = data.get_data(as_text=True)
    else:
        output = data

    if isinstance(output, dict) and 'competition_id' in output and 'competition_name' in output:
        print(f"Competition Name: {output['competition_name']}")
        print(f"Competition ID: {output['competition_id']}\n")
        
        results = output.get('results', [])
        for idx, item in enumerate(results, start=1):
            rank_str = ordinal(idx)
            item_display = {k: v for k, v in item.items() if k != 'competition_id'}
            print(f"{rank_str}: {item_display}")
        print()  # Add an extra newline at the end
    else:
        print(output, '\n')
    
    print(f"Status code: {status_code}\n")
