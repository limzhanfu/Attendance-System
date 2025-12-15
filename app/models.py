import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db ,login 
from typing import Optional	
from flask_login import UserMixin
from werkzeug.security import check_password_hash ,generate_password_hash
from datetime import datetime ,date ,time
from enum import Enum

class WeekdayEnum(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5

class Status(Enum):
	PRESENT = 0
	ABSENT = 1
	EXCUSE = 2
	PENDING = 3

class Role(db.Model):
	id: so.Mapped[int] = so.mapped_column(primary_key=True)
	name: so.Mapped[str] = so.mapped_column(sa.String(100) ,unique=True)

	users: so.Mapped["User"] = so.relationship(back_populates="role")

	def __repr__(self):
		return f"id: {self.id} ,name: {self.name}"
	
class User(UserMixin ,db.Model):
	id: so.Mapped[int] = so.mapped_column(primary_key=True)
	first_name: so.Mapped[str] = so.mapped_column(sa.String(100))
	last_name: so.Mapped[str] = so.mapped_column(sa.String(100))
	email: so.Mapped[str] = so.mapped_column(sa.String(256) ,unique=True ,index=True)
	_password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(60))

	role: so.Mapped[Role] = so.relationship(back_populates="users")
	role_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Role.id))
	
	student: so.Mapped["Student"] = so.relationship(back_populates="user")
	teacher: so.Mapped["Teacher"] = so.relationship(back_populates="user")

	def __repr__(self):
		return f"User(id: {self.id} ,name: {self.first_name} {self.last_name} ,roles: {self.role})"
	
	def check_password(self ,password) -> bool:
		return check_password_hash(self._password_hash ,password)
	
	def set_password(self ,password) -> None:
		self._password_hash = generate_password_hash(password)
	

@login.user_loader
def load_user(id):
	u = db.session.get(User ,int(id))
	return u 

class Teacher(db.Model):
	id: so.Mapped[int] = so.mapped_column(primary_key=True)
	allocations: so.Mapped["Allocation"] = so.relationship(back_populates="teacher") 

	user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id) ,unique=True)
	user: so.Mapped[User] = so.relationship(back_populates="teacher")

	def __repr__(self):
		return f"Teacher(id: {self.id} ,{self.user_id})"

class Student(db.Model):
	id: so.Mapped[int] = so.mapped_column(primary_key=True)
	
	group_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("student_group.id") ,index=True)
	group: so.Mapped["StudentGroup"] = so.relationship(back_populates="students")
	
	records: so.Mapped["StudentAttendanceRecord"] = so.relationship(back_populates="student")
	
	user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id) ,unique=True)
	user: so.Mapped[User] = so.relationship(back_populates="student")

	def __repr__(self):
		return f"Student(id: {self.id} ,{self.user_id} ,group: {self.group})"

class Course(db.Model):
	id: so.Mapped[int] = so.mapped_column(primary_key=True)
	allocations: so.Mapped["Allocation"] = so.relationship(back_populates="course")
	name: so.Mapped[str] = so.mapped_column(sa.String(50))
	code: so.Mapped[str] = so.mapped_column(sa.String(10) ,unique=True)

	def __repr__(self):
		return f"Course(id: {self.id} ,name: {self.name} ,code: {self.code})"

class StudentGroup(db.Model):
	id: so.Mapped[int] = so.mapped_column(primary_key=True)
	name: so.Mapped[str] = so.mapped_column(sa.String(50) ,unique=True)
	students: so.Mapped[list[Student]] = so.relationship(back_populates="group")
	allocations: so.Mapped["Allocation"] = so.relationship(back_populates="group")

	def __repr__(self):
		return f"Group(id: {self.id} ,name: {self.name})"
	
class StudentAttendanceRecord(db.Model):	
	id: so.Mapped[int] = so.mapped_column(primary_key=True)
	session_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("class_session.id"))
	session: so.Mapped["ClassSession"] = so.relationship(back_populates="records")
	student_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Student.id))
	student: so.Mapped[Student] = so.relationship(back_populates="records")

	status: so.Mapped[Status] = so.mapped_column(sa.Enum(Status) ,default=Status.PENDING)
	recorded_at: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime())

	has_cancelled: so.Mapped[bool] = so.mapped_column(sa.Boolean())

	def __repr__(self):
		return f"Record(id: {self.id} ,student: {self.student} ,status: {self.status})"

class ClassSession(db.Model):
	id: so.Mapped[int] = so.mapped_column(primary_key=True)
	allocation_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("allocation.id"))
	allocation: so.Mapped["Allocation"] = so.relationship(back_populates="session")
	records: so.Mapped[list[StudentAttendanceRecord]] = so.relationship(back_populates="session") 
	attendance_code: so.Mapped[Optional[str]] = so.mapped_column(sa.String(6) ,index=True)

	start_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime())
	end_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime())

	is_activated: so.Mapped[bool] = so.mapped_column(sa.Boolean())

	def __repr__(self):
		return f"Session(id: {self.id} ,allocation: {self.allocation} ,attendance_code: {self.attendance_code})"

class Allocation(db.Model):
	id: so.Mapped[int] = so.mapped_column(primary_key=True)

	teacher_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Teacher.id))
	teacher: so.Mapped[Teacher] = so.relationship(back_populates="allocations")

	course_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Course.id))
	course: so.Mapped[Course] = so.relationship(back_populates="allocations")

	group_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(StudentGroup.id))
	group: so.Mapped[StudentGroup] = so.relationship(back_populates="allocations")

	session: so.Mapped[ClassSession] = so.relationship(back_populates="allocation")

	weekday: so.Mapped[WeekdayEnum] = so.mapped_column(sa.Enum(WeekdayEnum) ,default=WeekdayEnum.MONDAY)
	start_time: so.Mapped[time] = so.mapped_column(sa.Time())
	end_time: so.Mapped[time] = so.mapped_column(sa.Time())

	semester_start: so.Mapped[date] = so.mapped_column(sa.Date())
	semester_end: so.Mapped[date] = so.mapped_column(sa.Date())	

	def __repr__(self):
		return f"Allocation(id: {self.id} ,teacher: {self.teacher} ,course: {self.course} ,group: {self.group})"


