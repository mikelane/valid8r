Interactive Prompts
===================

This section demonstrates how to use Valid8r's prompting functionality for interactive command-line applications. The prompt module provides a clean interface for collecting and validating user input with integrated error handling.

Basic User Input
----------------

The following examples demonstrate prompting for different types of input:

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from valid8r.core.maybe import Success, Failure

   # Basic string input
   name = prompt.ask("Enter your name: ")
   match name:
       case Success(value):
           print(f"Hello, {value}!")
       case Failure(error):
           print(f"Error: {error}")

   # Integer input
   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       retry=True
   )
   match age:
       case Success(value):
           print(f"You are {value} years old.")
       case Failure(error):
           print(f"Error: {error}")

   # Validated integer input
   score = prompt.ask(
       "Enter a score (0-100): ",
       parser=parsers.parse_int,
       validator=validators.between(0, 100),
       retry=True
   )
   match score:
       case Success(value):
           print(f"Your score: {value}/100")
       case Failure(error):
           print(f"Error: {error}")

   # Boolean input (yes/no)
   confirm = prompt.ask(
       "Continue? (yes/no): ",
       parser=parsers.parse_bool,
       retry=True
   )
   match confirm:
       case Success(value) if value:
           print("Continuing...")
       case Success(_):
           print("Operation cancelled.")
       case Failure(error):
           print(f"Error: {error}")

Using Default Values
--------------------

Default values provide convenient options for users:

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from valid8r.core.maybe import Success, Failure

   # String with default
   username = prompt.ask(
       "Enter username: ",
       default="guest",
       retry=True
   )
   match username:
       case Success(value):
           print(f"Username: {value}")
       case Failure(error):
           print(f"Error: {error}")

   # Integer with default
   port = prompt.ask(
       "Enter port number: ",
       parser=parsers.parse_int,
       validator=validators.between(1, 65535),
       default=8080,
       retry=True
   )
   match port:
       case Success(value):
           print(f"Using port: {value}")
       case Failure(error):
           print(f"Error: {error}")

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
   match expiry_date:
       case Success(value):
           print(f"Expiry date: {value}")
       case Failure(error):
           print(f"Error: {error}")

Controlling Retry Behavior
--------------------------

Valid8r offers flexible retry control for handling invalid input:

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from valid8r.core.maybe import Success, Failure

   # No retries (default)
   value = prompt.ask(
       "Enter a positive number: ",
       parser=parsers.parse_int,
       validator=validators.minimum(0)
   )
   match value:
       case Success(num):
           print(f"Valid number: {num}")
       case Failure(error):
           print(f"Invalid input: {error}")

   # Infinite retries
   value = prompt.ask(
       "Enter a positive number: ",
       parser=parsers.parse_int,
       validator=validators.minimum(0),
       retry=True  # True means infinite retries
   )
   # This will always return Success if it returns at all
   match value:
       case Success(num):
           print(f"You entered: {num}")
       case Failure(_):
           print("This won't happen unless interrupted")

   # Limited retries
   value = prompt.ask(
       "Enter a positive number: ",
       parser=parsers.parse_int,
       validator=validators.minimum(0),
       retry=3  # Allow 3 retry attempts
   )
   match value:
       case Success(num):
           print(f"You entered: {num}")
       case Failure(error):
           print(f"Failed after 3 attempts: {error}")

Custom Error Messages
---------------------

Customize error messages for a better user experience:

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from valid8r.core.maybe import Success, Failure

   # Custom error message for parser
   age = prompt.ask(
       "Enter your age: ",
       parser=lambda s: parsers.parse_int(s, error_message="Age must be a number"),
       retry=True
   )
   match age:
       case Success(value):
           print(f"Age: {value}")
       case Failure(error):
           print(f"Error: {error}")

   # Custom error message for validator
   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       validator=validators.between(
           0, 120, "Age must be between 0 and 120 years"
       ),
       retry=True
   )
   match age:
       case Success(value):
           print(f"Age: {value}")
       case Failure(error):
           print(f"Error: {error}")

   # Custom error message for the prompt itself
   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       error_message="Please enter a valid age between 0 and 120",
       retry=True
   )
   match age:
       case Success(value):
           print(f"Age: {value}")
       case Failure(error):
           print(f"Error: {error}")

Building a Menu System
----------------------

Create interactive menus using prompts:

.. code-block:: python

   from valid8r import prompt, parsers, validators
   from valid8r.core.maybe import Success, Failure
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

           match choice:
               case Success(1):
                   user_menu()
               case Success(2):
                   file_menu()
               case Success(3):
                   settings_menu()
               case Success(4):
                   print("Goodbye!")
                   sys.exit(0)
               case Failure(error):
                   print(f"Error: {error}")

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

           match choice:
               case Success(1):
                   print("Listing users...")
                   # Implementation...
               case Success(2):
                   add_user()
               case Success(3):
                   delete_user()
               case Success(4):
                   return
               case Failure(error):
                   print(f"Error: {error}")

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

       # Process all inputs with pattern matching
       match (username, email, age):
           case (Success(u), Success(e), Success(a)):
               print("\nUser added successfully:")
               print(f"Username: {u}")
               print(f"Email: {e}")
               print(f"Age: {a}")
           case (Failure(error), _, _):
               print(f"Username error: {error}")
           case (_, Failure(error), _):
               print(f"Email error: {error}")
           case (_, _, Failure(error)):
               print(f"Age error: {error}")

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

   from valid8r import prompt, validators, Maybe
   from valid8r.core.maybe import Success, Failure
   from getpass import getpass

   # Custom parser that uses getpass for hidden input
   def password_parser(prompt_text):
       password = getpass(prompt_text)
       return Maybe.success(password)

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

       # Check if passwords match
       match (password, confirm):
           case (Success(pass1), Success(pass2)) if pass1 == pass2:
               return Maybe.success(pass1)
           case (Success(_), Success(_)):
               print("Error: Passwords do not match")
               return Maybe.failure("Passwords do not match")
           case (Failure(error), _):
               return Maybe.failure(error)
           case (_, Failure(error)):
               return Maybe.failure(error)

   # Usage
   password_result = validate_password()
   match password_result:
       case Success(value):
           print("Password set successfully")
           print(f"Password hash: {hash(value)}")  # Don't actually store the password like this
       case Failure(error):
           print(f"Failed to set password: {error}")

Multi-stage Input Flow
----------------------

Complex multi-stage form with validation:

.. code-block:: python

   from valid8r import prompt, parsers, validators, Maybe
   from valid8r.core.maybe import Success, Failure
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
           lambda s: bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", s)),
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
               match result:
                   case Failure(error):
                       print(f"Error: {error}")
                       continue
                   case Success(_):
                       pass

               # Confirm password
               confirm = getpass("Confirm password: ")
               if password != confirm:
                   print("Error: Passwords do not match")
                   continue

               return Maybe.success(password)

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

       # Step 4: Confirmation - process all inputs with pattern matching
       print("\nStep 4: Confirmation")
       print("===================")

       # Collect all inputs
       inputs = (name, email, age, username, password, receive_emails, theme_index)

       # Verify all inputs are valid
       match inputs:
           case (Success(name_val), Success(email_val), Success(age_val),
                 Success(username_val), Success(password_val),
                 Success(receive_val), Success(theme_idx)):
               theme_val = theme_choices[theme_idx - 1]

               # Display confirmation
               print(f"Name: {name_val}")
               print(f"Email: {email_val}")
               print(f"Age: {age_val}")
               print(f"Username: {username_val}")
               print(f"Password: {'*' * len(password_val)}")
               print(f"Receive emails: {receive_val}")
               print(f"Theme: {theme_val}")

               # Ask for final confirmation
               confirm = prompt.ask(
                   "\nConfirm registration? (yes/no): ",
                   parser=parsers.parse_bool,
                   retry=True
               )

               match confirm:
                   case Success(True):
                       print("\nRegistration successful!")
                       return {
                           "name": name_val,
                           "email": email_val,
                           "age": age_val,
                           "username": username_val,
                           "password": password_val,
                           "receive_emails": receive_val,
                           "theme": theme_val
                       }
                   case Success(False):
                       print("\nRegistration cancelled.")
                       return None
                   case Failure(error):
                       print(f"Confirmation error: {error}")
                       return None
           case _:
               print("Some inputs were invalid. Please try again.")
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
   from valid8r.core.maybe import Success, Failure
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
           match host_result:
               case Success(value):
                   host = value
               case Failure(error):
                   print(f"Error: {error}")
                   return

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
           match port_result:
               case Success(value):
                   port = value
               case Failure(error):
                   print(f"Error: {error}")
                   return

       # Get username (with prompt fallback)
       username = args.username
       if username is None:
           username_result = prompt.ask(
               "Enter username: ",
               validator=validators.length(3, 20),
               retry=True
           )
           match username_result:
               case Success(value):
                   username = value
               case Failure(error):
                   print(f"Error: {error}")
                   return

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
   from valid8r.core.maybe import Success, Failure
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

       # Process employee data with pattern matching
       match (employee_id, first_name, last_name, dob, dept_choice):
           case (Success(id_val), Success(first_val), Success(last_val),
                 Success(dob_val), Success(dept_idx)):
               department = departments[dept_idx - 1]

               # Collect additional information
               salary = prompt.ask(
                   "Annual Salary: ",
                   parser=parsers.parse_float,
                   validator=validators.minimum(0),
                   retry=True
               )

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

               full_time = prompt.ask(
                   "Full-time employee? (yes/no): ",
                   parser=parsers.parse_bool,
                   default=True,
                   retry=True
               )

               # Process final data
               match (salary, start_date, full_time):
                   case (Success(salary_val), Success(start_val), Success(ft_val)):
                       # Display summary
                       print("\nEmployee Summary:")
                       print(f"ID: {id_val}")
                       print(f"Name: {first_val} {last_val}")
                       print(f"Date of Birth: {dob_val.isoformat()}")
                       print(f"Department: {department}")
                       print(f"Salary: ${salary_val:,.2f}")
                       print(f"Start Date: {start_val.isoformat()}")
                       print(f"Full-time: {ft_val}")

                       # Save confirmation
                       save = prompt.ask(
                           "\nSave employee record? (yes/no): ",
                           parser=parsers.parse_bool,
                           retry=True
                       )

                       match save:
                           case Success(True):
                               print("Employee record saved successfully!")
                               return {
                                   "id": id_val,
                                   "first_name": first_val,
                                   "last_name": last_val,
                                   "dob": dob_val,
                                   "department": department,
                                   "salary": salary_val,
                                   "start_date": start_val,
                                   "full_time": ft_val
                               }
                           case Success(False):
                               print("Employee record discarded.")
                               return None
                           case Failure(error):
                               print(f"Error: {error}")
                               return None
                   case _:
                       print("Error collecting employee details.")
                       return None
           case _:
               print("Error collecting employee information.")
               return None

   # Usage
   employee = employee_form()
   if employee:
       # Do something with the employee data
       print(f"Added employee: {employee['first_name']} {employee['last_name']}")

In the next sections, we'll explore the API reference for the various components of Valid8r.
