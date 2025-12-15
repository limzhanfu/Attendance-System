from flask_wtf import FlaskForm
import wtforms as wtf
from wtforms.validators import DataRequired ,Email ,EqualTo ,ValidationError
from app import db
from app.models import *
import sqlalchemy as sa 
from datetime import timedelta

def get_dates_at_weekday_from_range(weekday ,start ,end):
	current_date = start
	one_day = timedelta(days=1)
	arr = []

	while(not current_date > end):
		current_date += one_day
		if(current_date.weekday() == weekday):
			arr.append(current_date)
	return arr

class LoginForm(FlaskForm):	
	email = wtf.EmailField("Email" ,validators=[DataRequired() ,Email()])
	password = wtf.PasswordField("Password" ,validators=[DataRequired()])
	submit = wtf.SubmitField("Submit")

class RegistrationForm(FlaskForm):
    first_name = wtf.StringField('First name' ,validators=[DataRequired()])
    last_name = wtf.StringField('Last name' ,validators=[DataRequired()])
    email = wtf.EmailField('Email', validators=[DataRequired(), Email()])
    password = wtf.PasswordField('Password', validators=[DataRequired()])
    password2 = wtf.PasswordField('Repeat Password', validators=[DataRequired(),
                 EqualTo('password')])

    role = wtf.SelectField("Role" ,validators=[DataRequired()] ,coerce=int)
    submit = wtf.SubmitField('Register')

    def set_role_choices(self):
        roles = db.session.scalars(sa.select(Role)).all()
        self.role.choices = [(r.id ,r.name) for r in roles] if(roles) else [(0 ,"None Option")]
        
    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')

class AllocationForm(FlaskForm):
    dates = []
    teacher = wtf.SelectField("Teacher" ,validators=[DataRequired()] ,coerce=int)
    course = wtf.SelectField("Course" ,validators=[DataRequired()] ,coerce=int)
    group = wtf.SelectField("Group" ,validators=[DataRequired()] ,coerce=int)
    start_date = wtf.DateField("Start Date" ,validators=[DataRequired()])
    end_date = wtf.DateField("End Date" ,validators=[DataRequired()])
    weekday = wtf.SelectField("Weekday" ,validators=[DataRequired()] ,coerce=str)
    start_time = wtf.TimeField("Start Time" ,validators=[DataRequired()])
    end_time = wtf.TimeField("End Time" ,validators=[DataRequired()])

    delete = wtf.SubmitField("Delete")
    
    submit = wtf.SubmitField("Create")

    def initialize(self):
        teachers = db.session.scalars(sa.select(Teacher)).all()
        self.teacher.choices = [(t.id ,t.user.first_name + " " + t.user.last_name) for t in teachers] \
        if(teachers) else [(0 ,"None")]

        courses = db.session.scalars(sa.select(Course)).all()
        self.course.choices = [(c.id ,c.name) for c in courses] \
        if(courses) else [(0 ,"None")]

        groups = db.session.scalars(sa.select(StudentGroup)).all()
        self.group.choices = [(g.id ,g.name) for g in groups] \
        if(groups) else [(0 ,"None")]

        self.weekday.choices = [(w.value ,w.name.capitalize()) for w in WeekdayEnum]

    def validate_end_date(self ,end_date):
        if(end_date.data < self.start_date.data):
            raise ValidationError("Invalid dates ,end is before start")
        elif(end_date.data == self.start_date.data):
            raise ValidationError("Invalid dates ,start and end is equal")
        
    def validate_end_time(self ,end_time):
        if(end_time.data < self.start_time.data):
            raise ValidationError("Invalid time ,end is before start")
        elif(end_time.data == self.start_time.data):
            raise ValidationError("Invalid time ,start and end is equal")
        
    def validate_weekday(self ,weekday):
        
        dates = get_dates_at_weekday_from_range(int(weekday.data) ,self.start_date.data ,self.end_date.data)

        if(dates == []):
            raise ValidationError(f"""There have no {WeekdayEnum(int(weekday.data)).name.capitalize()}
                                  between {self.start_date.data} and {self.end_date.data}""")
        else:
             self.dates = dates

class MarkAttendanceForm(FlaskForm):
     checkboxes = []
     submit = wtf.SubmitField("Submit") 

     def generate_checkbox(self ,session_id ,student_id):
          checkbox = wtf.BooleanField("CheckBox")
          self.checkboxes.append((checkbox ,session_id ,student_id))
          return checkbox