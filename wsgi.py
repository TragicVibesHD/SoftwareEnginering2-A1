import click, pytest, sys
from flask import Flask
from flask.cli import with_appcontext, AppGroup
from App.database import *
from App.models import *
from App.main import *
from App.controllers import *

# This commands file allows you to create convenient CLI commands for testing controllers
app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    print('database intialized')

'''
User Commands
'''

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password)
    print(f'{username} created!')

# this command will be : flask user create bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli) # add the group to the cli

'''
Test Commands
'''

test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")

def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))

mod_cli = AppGroup('Moderator', help='Moderator commands')

mod_cli.command('create_competition_cli')
def create_competition_cli():
    name = input("Enter competition name: ")
    date = input("Enter competition date (YYYY-MM-DD): ")
    description = input("Enter competition description (optional): ")
    response = create_competition(name, date, description)
    print(response.get_data(as_text=True))

mod_cli.command('import_results_cli')
def import_results_cli():
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

    response = import_results(competition_id, {'results': results_data})
    print_response(response)

mod_cli.command('view_competitions_cli')
def view_competitions_cli():
    response = get_competitions()
    print(response.get_data(as_text=True))

mod_cli.command('view_competition_results_cli')
def view_competition_results_cli():
    competition_id = int(input("Enter competition ID: "))
    response = get_competition_results(competition_id)
    print_response(response)

app.cli.add_command(mod_cli)  # Add the moderator commands to the CLI

@mod_cli.command('import_results_from_file_cli')
@click.argument('competition_id')
@click.argument('file_path')
def import_results_from_file_cli(competition_id, file_path):
    try:
        competition_id = int(competition_id)
        response = import_results_from_file(competition_id, file_path)
        
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
    except Exception as e:
        print(f"Error: {str(e)}")

@mod_cli.command('view_competitions_cli')
def view_competitions_cli():
    try:
        response = get_competitions()
        print_response(response)
    except Exception as e:
        print(f"Error: {str(e)}")

@mod_cli.command('view_competition_results_cli')
def view_competition_results_cli():
    try:
        competition_id = int(input("Enter competition ID: "))
        response = get_competition_results(competition_id)
        print_response(response)
    except ValueError:
        print("Invalid competition ID. Please enter a valid integer.")
    except Exception as e:
        print(f"Error: {str(e)}")

app.cli.add_command(mod_cli)

def print_response(response):
    if isinstance(response, tuple):
        data, status_code = response
    else:
        data = response
        status_code = 200

    if hasattr(data, 'get_json'):
        print(data.get_json())
    elif hasattr(data, 'get_data'):
        print(data.get_data(as_text=True))
    else:
        print(data)
    print(f"Status code: {status_code}")