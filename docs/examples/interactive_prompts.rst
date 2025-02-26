Interactive Prompts
===================

This section demonstrates how to use Valid8r's prompting functionality for interactive command-line applications.

Basic User Input
----------------

Simple examples of prompting for different types of input:

.. code-block:: python

   from valid8r import prompt, parsers, validators

   # Basic string input
   name = prompt.ask("Enter your name: ")
   if name.is_just():
       print(f"Hello, {name.value()}!")

   # Integer input
   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       retry=True
   )
   if age.is_just():
       print(f"You are {age.value()} years old.")

   # Validated integer input
   score = prompt.ask(
       "Enter a score (0-100): ",
       parser=parsers.parse_int,
       validator=validators.between(0, 100),
       retry=True
   )
   if score.is_just():
       print(f"Your score: {score.value()}/100")

   # Boolean input (yes/no)
   confirm = prompt.ask(
       "Continue? (yes/no): ",
       parser=parsers.parse_bool,
       retry=True
   )
   if confirm.is_just() and confirm.value():
       print("Continuing...")
   else:
       print("Operation cancelled.")

Using Default Values
--------------------

Provide default values for prompts:

.. code-block:: python

   from valid8r import prompt, parsers, validators

   # String with default
   username = prompt.ask(
       "Enter username: ",
       default="guest",
       retry=True
   )
   print(f"Username: {username.value()}")

   # Integer with default
   port = prompt.ask(
       "Enter port number: ",
       parser=parsers.parse_int,
       validator=validators.between(1, 65535),
       default=8080,
       retry=True
   )
   print(f"Using port: {port.value()}")

   # Date with default
   from datetime import date

   def date_parser(s):
       return parsers.parse_date(s)

   expiry_date = prompt.ask(
       "Enter expiry date (YYYY-MM-DD): ",
       parser=date_parser,
       default=date.today().isoformat(),
       retry=True
   )
   print(f"Expiry date: {expiry_date.value()}")

Controlling Retry Behavior
--------------------------

Specify how many retries are allowed:

.. code-block:: python

   from valid8r import prompt, parsers, validators

   # No retries (default)
   value = prompt.ask(
       "Enter a positive number: ",
       parser=parsers.parse_int,
       validator=validators.minimum(0)
   )
   if value.is_nothing():
       print(f"Invalid input: {value.error()}")

   # Infinite retries
   value = prompt.ask(
       "Enter a positive number: ",
       parser=parsers.parse_int,
       validator=validators.minimum(0),
       retry=True  # True means infinite retries
   )
   print(f"You entered: {value.value()}")

   # Limited retries
   value = prompt.ask(
       "Enter a positive number: ",
       parser=parsers.parse_int,
       validator=validators.minimum(0),
       retry=3  # Allow 3 retry attempts
   )

   if value.is_just():
       print(f"You entered: {value.value()}")
   else:
       print(f"Failed after 3 attempts: {value.error()}")

Custom Error Messages
---------------------

Customize error messages for better user experience:

.. code-block:: python

   from valid8r import prompt, parsers, validators

   # Custom error message for parser
   age = prompt.ask(
       "Enter your age: ",
       parser=lambda s: parsers.parse_int(s, error_message="Age must be a number"),
       retry=True
   )

   # Custom error message for validator
   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       validator=validators.between(
           0, 120, "Age must be between 0 and 120 years"
       ),
       retry=True
   )

   # Custom error message for the prompt itself
   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       error_message="Please enter a valid age between 0 and 120",
       retry=True
   )

Building a Menu System
----------------------

Create interactive menus using prompts:

.. code-block:: python

   from valid8r import prompt, parsers, validators
   import sys

   def main_menu():
       while True:
           print("\nMain Menu")
           print("=========")
           print("1. User Management")
           print("2. File Operations")
           print("3. Settings")
           print("4. Exit")

           choice = prompt.ask(
               "\nEnter choice (1-4): ",
               parser=parsers.parse_int,
               validator=validators.between(1, 4),
               retry=True
           )

           if choice.value() == 1:
               user_menu()
           elif choice.value() == 2:
               file_menu()
           elif choice.value() == 3:
               settings_menu()
           else:  # 4
               sys.exit(0)

   def user_menu():
       while True:
           print("\nUser Management")
           print("==============")
           print("1. List Users")
           print("2. Add User")
           print("3. Delete User")
           print("4. Back to Main Menu")

           choice = prompt.ask(
               "\nEnter choice (1-4): ",
               parser=parsers.parse_int,
               validator=validators.between(1, 4),
               retry=True
           )

           if choice.value() == 1:
               print("Listing users...")
               # Implementation...
           elif choice.value() == 2:
               add_user()
           elif choice.value() == 3:
               delete_user()
           else:  # 4
               return

   def add_user():
       print("\nAdd User")
       print("========")

       # Get username
       username = prompt.ask(
           "Enter username: ",
           validator=validators.length(3, 20),
           retry=True
       )

       # Get email
       import re

       def is_valid_email(s):
           return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", s))

       email = prompt.ask(
           "Enter email: ",
           validator=validators.predicate(is_valid_email, "Invalid email format"),
           retry=True
       )

       # Get age
       age = prompt.ask(
           "Enter age: ",
           parser=parsers.parse_int,
           validator=validators.between(0, 120),
           retry=True
       )

       print(f"\nUser added successfully:")
       print(f"Username: {username.value()}")
       print(f"Email: {email.value()}")
       print(f"Age: {age.value()}")

   # Implementation of other functions...
   def file_menu():
       print("File Operations menu...")
       # Implementation...

   def settings_menu():
       print("Settings menu...")
       # Implementation...

   def delete_user():
       print("Delete user...")
       # Implementation...

   # Run the program
   if __name__ == "__main__":
       main_menu()

Custom Input Masking
--------------------

Password input with masking:

.. code-block:: python

   from valid8r import prompt, Maybe, validators
   from getpass import getpass

   # Custom parser that uses getpass for hidden input
   def password_parser(prompt_text):
       password = getpass(prompt_text)
       return Maybe.just(password)

   # Password validation
   def validate_password():
       # Password must:
       # 1. Be at least 8 characters
       # 2. Contain at least one uppercase letter
       # 3. Contain at least one digit

       password_validator = (
           validators.length(8, 100, "Password must be at least 8 characters") &
           validators.predicate(
               lambda p: any(c.isupper() for c in p),
               "Password must contain at least one uppercase letter"
           ) &
           validators.predicate(
               lambda p: any(c.isdigit() for c in p),
               "Password must contain at least one digit"
           )
       )

       password = prompt.ask(
           "Enter password: ",
           parser=lambda _: password_parser("Password: "),
           validator=password_validator,
           retry=True
       )

       # Confirm password
       confirm = prompt.ask(
           "Confirm password: ",
           parser=lambda _: password_parser("Confirm password: "),
           retry=True
       )

       if password.value() != confirm.value():
           print("Error: Passwords do not match")
           return Maybe.nothing("Passwords do not match")

       return password

   # Usage
   password_result = validate_password()
   if password_result.is_just():
       print("Password set successfully")
   else:
       print(f"Failed to set password: {password_result.error()}")

Multi-stage Input Flow
----------------------

Complex multi-stage form with validation:

.. code-block:: python

   from valid8r import prompt, parsers, validators, Maybe
   import re

   def register_user():
       # Step 1: Basic Information
       print("Step 1: Basic Information")
       print("========================")

       name = prompt.ask(
           "Full name: ",
           validator=validators.length(1, 100),
           retry=True
       )

       email_validator = validators.predicate(
           lambda s: bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", s)),
           "Invalid email format"
       )

       email = prompt.ask(
           "Email address: ",
           validator=email_validator,
           retry=True
       )

       age = prompt.ask(
           "Age: ",
           parser=parsers.parse_int,
           validator=validators.between(18, 120),
           retry=True
       )

       # Step 2: Account Details
       print("\nStep 2: Account Details")
       print("======================")

       username_validator = validators.length(3, 20) & validators.predicate(
           lambda s: s.isalnum() or '_' in s,
           "Username must contain only letters, numbers, and underscores"
       )

       username = prompt.ask(
           "Username: ",
           validator=username_validator,
           retry=True
       )

       password_validator = (
           validators.length(8, 100) &
           validators.predicate(
               lambda p: any(c.isupper() for c in p),
               "Password must contain at least one uppercase letter"
           ) &
           validators.predicate(
               lambda p: any(c.islower() for c in p),
               "Password must contain at least one lowercase letter"
           ) &
           validators.predicate(
               lambda p: any(c.isdigit() for c in p),
               "Password must contain at least one digit"
           )
       )

       # Custom password input with confirmation
       def get_password():
           from getpass import getpass

           while True:
               password = getpass("Password: ")

               # Validate password
               result = password_validator(password)
               if result.is_nothing():
                   print(f"Error: {result.error()}")
                   continue

               # Confirm password
               confirm = getpass("Confirm password: ")
               if password != confirm:
                   print("Error: Passwords do not match")
                   continue

               return Maybe.just(password)

       password = prompt.ask(
           "Enter password: ",
           parser=lambda _: get_password(),
           retry=False  # We handle retries in get_password
       )

       # Step 3: Preferences
       print("\nStep 3: Preferences")
       print("==================")

       receive_emails = prompt.ask(
           "Receive promotional emails? (yes/no): ",
           parser=parsers.parse_bool,
           default=False,
           retry=True
       )

       theme_choices = ["Light", "Dark", "System"]

       print("Available themes:")
       for i, theme in enumerate(theme_choices, 1):
           print(f"{i}. {theme}")

       theme_index = prompt.ask(
           "Select theme (1-3): ",
           parser=parsers.parse_int,
           validator=validators.between(1, len(theme_choices)),
           default=3,
           retry=True
       )

       # Step 4: Confirmation
       print("\nStep 4: Confirmation")
       print("===================")
       print(f"Name: {name.value()}")
       print(f"Email: {email.value()}")
       print(f"Age: {age.value()}")
       print(f"Username: {username.value()}")
       print(f"Password: {'*' * len(password.value())}")
       print(f"Receive emails: {receive_emails.value()}")
       print(f"Theme: {theme_choices[theme_index.value() - 1]}")

       confirm = prompt.ask(
           "\nConfirm registration? (yes/no): ",
           parser=parsers.parse_bool,
           retry=True
       )

       if confirm.value():
           print("\nRegistration successful!")
           return {
               "name": name.value(),
               "email": email.value(),
               "age": age.value(),
               "username": username.value(),
               "password": password.value(),
               "receive_emails": receive_emails.value(),
               "theme": theme_choices[theme_index.value() - 1]
           }
       else:
           print("\nRegistration cancelled.")
           return None

   # Usage
   user_data = register_user()
   if user_data:
       print(f"Registered user: {user_data['username']}")

Command-line Arguments with Fallback to Prompts
-----------------------------------------------

Combine command-line parsing with interactive prompts:

.. code-block:: python

   from valid8r import prompt, parsers, validators
   import argparse
   import sys

   def get_arguments():
       parser = argparse.ArgumentParser(description='Process some data.')
       parser.add_argument('--host', help='Server hostname')
       parser.add_argument('--port', type=int, help='Server port')
       parser.add_argument('--username', help='Username')
       parser.add_argument('--debug', action='store_true', help='Enable debug mode')

       return parser.parse_args()

   def main():
       # Parse command-line args
       args = get_arguments()

       # Get host (with prompt fallback)
       host = args.host
       if host is None:
           host_result = prompt.ask(
               "Enter host: ",
               default="localhost",
               retry=True
           )
           host = host_result.value()

       # Get port (with prompt fallback)
       port = args.port
       if port is None:
           port_result = prompt.ask(
               "Enter port: ",
               parser=parsers.parse_int,
               validator=validators.between(1, 65535),
               default=8080,
               retry=True
           )
           port = port_result.value()

       # Get username (with prompt fallback)
       username = args.username
       if username is None:
           username_result = prompt.ask(
               "Enter username: ",
               validator=validators.length(3, 20),
               retry=True
           )
           username = username_result.value()

       # Debug mode from args
       debug_mode = args.debug

       # Display configuration
       print("\nConfiguration:")
       print(f"Host: {host}")
       print(f"Port: {port}")
       print(f"Username: {username}")
       print(f"Debug mode: {debug_mode}")

       # Continue with application...
       print("\nConnecting to server...")

   if __name__ == "__main__":
       main()

Interactive Data Entry Form
---------------------------

Build a complete data entry form with validation:

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from datetime import date

   def employee_form():
       print("Employee Information Form")
       print("========================")

       # Employee ID
       employee_id = prompt.ask(
           "Employee ID: ",
           parser=parsers.parse_int,
           validator=validators.minimum(1000),
           retry=True
       )

       # Name
       first_name = prompt.ask(
           "First Name: ",
           validator=validators.length(1, 50),
           retry=True
       )

       last_name = prompt.ask(
           "Last Name: ",
           validator=validators.length(1, 50),
           retry=True
       )

       # Date of Birth
       dob = prompt.ask(
           "Date of Birth (YYYY-MM-DD): ",
           parser=parsers.parse_date,
           validator=validators.predicate(
               lambda d: d < date.today(),
               "Date of birth must be in the past"
           ),
           retry=True
       )

       # Department
       departments = ["Engineering", "Marketing", "Sales", "HR", "Finance"]
       print("\nDepartments:")
       for i, dept in enumerate(departments, 1):
           print(f"{i}. {dept}")

       dept_choice = prompt.ask(
           "Department (1-5): ",
           parser=parsers.parse_int,
           validator=validators.between(1, len(departments)),
           retry=True
       )

       department = departments[dept_choice.value() - 1]

       # Salary
       salary = prompt.ask(
           "Annual Salary: ",
           parser=parsers.parse_float,
           validator=validators.minimum(0),
           retry=True
       )

       # Start Date
       start_date = prompt.ask(
           "Start Date (YYYY-MM-DD): ",
           parser=parsers.parse_date,
           validator=validators.predicate(
               lambda d: d <= date.today(),
               "Start date cannot be in the future"
           ),
           default=date.today().isoformat(),
           retry=True
       )

       # Full-time status
       full_time = prompt.ask(
           "Full-time employee? (yes/no): ",
           parser=parsers.parse_bool,
           default=True,
           retry=True
       )

       # Display summary
       print("\nEmployee Summary:")
       print(f"ID: {employee_id.value()}")
       print(f"Name: {first_name.value()} {last_name.value()}")
       print(f"Date of Birth: {dob.value().isoformat()}")
       print(f"Department: {department}")
       print(f"Salary: ${salary.value():,.2f}")
       print(f"Start Date: {start_date.value().isoformat()}")
       print(f"Full-time: {full_time.value()}")

       # Save confirmation
       save = prompt.ask(
           "\nSave employee record? (yes/no): ",
           parser=parsers.parse_bool,
           retry=True
       )

       if save.value():
           print("Employee record saved successfully!")
           return {
               "id": employee_id.value(),
               "first_name": first_name.value(),
               "last_name": last_name.value(),
               "dob": dob.value(),
               "department": department,
               "salary": salary.value(),
               "start_date": start_date.value(),
               "full_time": full_time.value()
           }
       else:
           print("Employee record discarded.")
           return None

   # Usage
   employee = employee_form()
   if employee:
       # Do something with the employee data
       print(f"Added employee: {employee['first_name']} {employee['last_name']}")

In the next sections, we'll explore the API reference for the various components of Valid8r.