from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import ValidationError, Optional

class RegistrationForm(FlaskForm):
    def data_required(self, field):
        if not field.data:
            raise ValidationError('This field is required')

    def validate_username_length(self, field):
        min_length = 6
        max_length = 20
        if len(field.data) < min_length or len(field.data) > max_length:
            raise ValidationError(f'Username must be between {min_length} and {max_length} characters long')

    def validate_lydiard_email(self, field):
        if '@lydiardparkacademy.org.uk' not in field.data:
            raise ValidationError('Invalid email, please use your school email')

    def validate_passwords_match(self, field):
        if self.password.data != field.data:
            raise ValidationError('Passwords must match')

    def validate_teacher_reg_key(self, field):
        if self.role.data == 'teacher':
            if field.data != 'TCHR786':
                raise ValidationError('Invalid teacher registration key.')
        elif self.role.data != 'teacher' and field.data:
            raise ValidationError('This field is only applicable to teachers')

    def validate_moderator_reg_key(self, field):
        if self.role.data == 'moderator':
            if field.data != 'MDRTR987':
                raise ValidationError('Invalid moderator registration key.')
        elif self.role.data != 'teacher' and field.data:
            raise ValidationError('This field is only applicable to moderators')

    username = StringField('Username', validators=[data_required, validate_username_length])
    email = StringField('Email', validators=[data_required, validate_lydiard_email])
    password = PasswordField('Password', validators=[data_required])
    confirm_password = PasswordField('Confirm Password', validators=[data_required, validate_passwords_match])
    role = SelectField('Sign Up As', choices=[('student', 'Student'), ('teacher', 'Teacher'), ('moderator', 'Moderator')], validators=[data_required])
    teacher_reg_key = StringField('Teacher Registration Key', validators=[validate_teacher_reg_key, data_required, Optional()])
    moderator_reg_key = StringField('Moderator Registration Key', validators=[validate_moderator_reg_key, data_required, Optional()])
