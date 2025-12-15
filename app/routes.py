from app import app ,db
from flask import render_template ,flash ,redirect ,url_for ,flash ,request ,abort
from flask_login import login_required ,login_user ,current_user ,logout_user
from .forms import *
import sqlalchemy as sa
from app.models import *
from authentication import role_required
import random
from datetime import datetime
from wtforms import BooleanField

@app.route('/')
@login_required
def index():
	return render_template("index.html" ,user=current_user)

@app.route('/login' ,methods=["POST" ,"GET"])
def login():
	if(current_user.is_authenticated):
		return redirect(url_for("index"))

	login_form = LoginForm()
	if(login_form.validate_on_submit()):
		user = db.session.scalar(sa.select(User).where(User.email == login_form.email.data))

		if(not user is None):
			if(not user.check_password(login_form.password.data)):
				flash("Invalid id or password" ,"error")	
				return render_template("login.html" ,form=login_form)
				

			login_user(user)
			flash("Login Successfully" ,"success")	
			return redirect(url_for("index"))

	return render_template("login.html" ,form=login_form)

@app.route('/logout')
def logout():
	logout_user()
	flash("Logout Successfully" ,"info")
	return redirect(url_for("index"))


@app.route('/register', methods=['GET', 'POST'])
def register():
	if(current_user.is_authenticated):
		return redirect(url_for('index'))
	
	form = RegistrationForm()
	form.set_role_choices()

	if(form.validate_on_submit()):
		
		first_name = form.first_name.data
		last_name = form.last_name.data
		email = form.email.data
		role = db.session.get(Role ,form.role.data)

		user = User(email=email ,first_name=first_name ,last_name= last_name)

		if(not role == None):
			user.role = role

		user.set_password(form.password.data)
		db.session.add(user)
		db.session.flush()

		if(user.role.name == "Student"):
			groups = db.session.scalars(sa.select(StudentGroup)).all()

			my_group = random.choice(groups)
			student = Student(group=my_group ,user_id=user.id)
			db.session.add(student)

		elif(user.role.name == "Teacher"):
			teacher = Teacher(user_id=user.id)
			db.session.add(teacher)

		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/teachers')
@login_required
@role_required('Admin')
def teachers():
	teachers = db.session.scalars(sa.select(Teacher))
	return render_template("teachers.html" ,teachers=teachers)

@app.route('/users')
@login_required
@role_required('Admin')
def users():
	users = db.session.scalars(sa.select(User))
	return render_template("users.html" ,users=users)

@app.route('/schedules')
@login_required
@role_required('Teacher')
def schedules():
	schedules = db.session.scalars(sa.select(Allocation).where(Allocation.teacher_id == current_user.teacher.id))
	return render_template("schedules.html" ,schedules=schedules)
	

@app.route('/admin/allocations')
@login_required
@role_required('Admin')
def view_allocations():
	allocations = db.session.scalars(sa.select(Allocation)).all()
	return render_template("admin/allocations.html" ,allocations=allocations)

@app.route('/admin/create_allocation' ,methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def create_allocation():
	form = AllocationForm()
	form.initialize()

	if(form.validate_on_submit()):
		allocation = Allocation(
						teacher_id=form.teacher.data,
						course_id=form.course.data,
						group_id=form.group.data,
						weekday=WeekdayEnum(int(form.weekday.data)),
						start_time=form.start_time.data,
						end_time=form.end_time.data,
						semester_start=form.start_date.data,
						semester_end=form.end_date.data
					)
		sessions = [ClassSession(
			allocation=allocation,
			start_at=datetime.combine(i ,allocation.start_time),
			end_at=datetime.combine(i ,allocation.end_time),
			is_activated=False
			) for i in form.dates]
		 
		db.session.add(allocation)
		db.session.add_all(sessions)
		db.session.commit()
		return redirect(url_for("view_allocations"))

	return render_template("admin/create_allocation.html" ,form=form)

@app.route('/admin/allocations/<int:id>/delete' ,methods=['GET' ,'POST'])
@login_required
@role_required('Admin')
def delete_allocation(id):
	if(request.method == "POST"):
		a = db.session.get(Allocation ,id)
		if(a):
			db.session.execute(sa.delete(ClassSession).where(ClassSession.allocation_id == a.id))
			db.session.delete(a)
			db.session.commit()
	return redirect(url_for("view_allocations"))

@app.route('/admin/allocations/<int:id>/sessions')
@login_required
@role_required('Admin')
def view_sessions(id):
	sessions = db.session.scalars(sa.select(ClassSession).where(ClassSession.allocation_id == id)).all()

	if(sessions):
		return render_template("admin/sessions.html" ,sessions=sessions)
	else:
		return abort(404)
	
@app.route("/teacher/sessions")
@login_required
@role_required("Teacher")
def teacher_timetable():
    stmt = (
        sa.select(ClassSession)
        .join(ClassSession.allocation)
        .where(Allocation.teacher_id == current_user.teacher.id)
        .order_by(ClassSession.start_at)
    )

    sessions = db.session.scalars(stmt).all()
    return render_template("teacher/timetable.html", sessions=sessions)

@app.route("/teacher/sessions/<int:session_id>/attendance",methods=["GET", "POST"])
@login_required
@role_required("Teacher")
def mark_attendance(session_id):
	session = db.session.get(ClassSession ,session_id)
	if(not session):
		abort(404)	
	
	if(not session.is_activated):
		session.is_activated = True

		session.attendance_code = session.attendance_code = f"{random.randint(0, 999999):06d}"
		records = [StudentAttendanceRecord(
			session=session,
			has_cancelled=False,
			status=Status.ABSENT,
			student_id=s.id
		)for s in session.allocation.group.students]

		db.session.add_all(records)
		db.session.commit()

	return render_template("teacher/attendance.html" ,session=session)
	

