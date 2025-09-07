# Project Setup
## important rules
- always follow these rules
- always use 'uv' to manage dependecies and manage the project. Do not use poetry or pip.
- before implementing any feature, ask for clarification if something is not clear. Always check the contents of the .github/memory/ directory for context about the project.
- your knowledge is outdated. Search the internet using the tools you have to get the latest information and documentation on the libraries.
- only use the libraries mentioned in this file. If you need to use another library, ask for permission first.
- only implement the features that are asked. Do not add extra features. Only implement one feature at a time. After major changes or implementation of new features, create or update files in the .github/memory/ directory to help copilot understand the project better.
- all the tests will be in the tests/ directory. Write tests for every feature you implement.
- document the code using docstrings and comments where necessary.

## libraries
- use fastapi for the backend. url: https://fastapi.tiangolo.com
- use sqlalchemy and sqlmodel for the database
- use pydantic for data validation. Always use pydantic V2. url: https://docs.pydantic.dev/latest/
- use alembic for database migrations
- use pytest and pytest-cov for testing
- use httpx for making HTTP requests
- use icecream for debugging and logging
- use ruff for linting
- use taskipy for task management and shortcuts
- use python-dotenv for environment variable management

## Project Structure
- Use the 'src/' directory for the source code.
- use a 'src/models/' directory for the database models.
- use a 'src/schemas/' directory for the pydantic schemas.
- Use a 'tests/' directory for the tests.
- Use a 'migrations/' directory for the alembic migrations.
- Use a '.github/' directory for GitHub-related files.

## the fastapi app
- the app instance is created in src/api.py
- name the functions using a CRUD style. For example, for a user resource, use create_user, get_user, update_user, delete_user.


## database
- use a local sqlite database for development and testing
- the database design is in the file ./dbdesign . It is a dbdiagram.io file. IMPORTANT: do not change the database design without permission. Always follow the design in that file. Follow the tables, the names and the relationships.
- the database connection string is in the .env file. Use python-dotenv to load the environment variables from the .env file.
- use sqlmodel for the database models. The models should be in the src/models/ directory.
- use alembic for database migrations. The alembic configuration file is in the root directory.