from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import ValidationError
from schoolgram.models import User

#define RegistrationForm class
class RegistrationForm(FlaskForm):
    # Check if field data exists
    def data_required(self, field):
        if not field.data:
            raise ValidationError('[This field is required]')

    # Check if username length is within range
    def validate_username_length(self, field):
        min_length = 4
        max_length = 20
        if len(field.data) < min_length or len(field.data) > max_length:
            raise ValidationError(f'[Username must be between {min_length} and {max_length} characters long]')

    # Check if email is valid school email
    def validate_lydiard_email(self, field):
        if '@lydiardparkacademy.org.uk' not in field.data:
            raise ValidationError('[Invalid email, please use your school email]')

    # Check if password and confirm_password fields match
    def validate_passwords_match(self, field):
        if self.password.data != field.data:
            raise ValidationError('[Passwords must match]')

    # Check if teacher registration key is valid
    def validate_teacher_reg_key(self, field):
        if self.role.data == 'teacher':
            # Check if the field is empty
            if not field.data:
                # If the error message for empty field is not already present, append it to the error list
                if '[Please enter your teacher registration key]' not in field.errors:
                    field.errors.append('[Please enter your teacher registration key]')
            # Check if the registration key entered is incorrect
            elif field.data != 'TCHR786':
                # If the error message for invalid key is not already present, append it to the error list
                if '[Invalid teacher registration key]' not in field.errors:
                    field.errors.append('[Invalid teacher registration key]')
        else:
            # Teacher role is not selected, so registration key is not required
            pass

    # Check if moderator registration key is valid
    def validate_moderator_reg_key(self, field):
        if self.role.data == 'moderator':
            # Check if the field is empty
            if not field.data:
                # If the error message for empty field is not already present, append it to the error list
                if '[Please enter your moderator registration key]' not in field.errors:
                    field.errors.append('[Please enter your moderator registration key]')
            # Check if the registration key entered is incorrect
            elif field.data != 'MDRTR987':
                # If the error message for invalid key is not already present, append it to the error list
                if '[Invalid moderator registration key]' not in field.errors:
                    field.errors.append('[Invalid moderator registration key]')
        else:
            # Moderator role is not selected, so registration key is not required
            pass

    # Define form fields with validators
    username = StringField('Username', validators=[data_required, validate_username_length])
    email = StringField('Email', validators=[data_required, validate_lydiard_email])
    password = PasswordField('Password', validators=[data_required])
    confirm_password = PasswordField('Confirm Password', validators=[data_required, validate_passwords_match])
    role = SelectField('Sign Up As', choices=[('student', 'Student'), ('teacher', 'Teacher'), ('moderator', 'Moderator')], validators=[data_required])
    teacher_reg_key = StringField('Teacher Registration Key', validators=[validate_teacher_reg_key])
    moderator_reg_key = StringField('Moderator Registration Key', validators=[validate_moderator_reg_key])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        # Query the database for a user with the provided username
        user = User.query.filter_by(username=username.data).first()
        # If a user with the username already exists, raise a validation error
        if user:
            raise ValidationError('[Username is already taken. Please choose a different one]')

    def validate_email(self, email):
        # Query the database for a user with the provided email
        user = User.query.filter_by(email=email.data).first()
        # If a user with the email already exists, raise a validation error
        if user:
            raise ValidationError('[Email is already taken. Please choose a different one]')

class LoginForm(FlaskForm):
    def data_required(self, field):
        if not field.data:
            raise ValidationError('This field is required')

    def validate_lydiard_email(self, field):
        if '@lydiardparkacademy.org.uk' not in field.data:
            raise ValidationError('Invalid email, please use your school email')

    email = StringField('Email', validators=[data_required, validate_lydiard_email])
    password = PasswordField('Password', validators=[data_required])
    submit = SubmitField('Login')