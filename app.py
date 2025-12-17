from app import app ,db
from app.models import *

def initialize():
	database = Course(name="Database" ,code="AMS1103")
	sdf = Course(name="Software Development Fundamental" ,code="AMS1012")

	group1 = StudentGroup(name="Group 1")
	group2 = StudentGroup(name="Group 2")

	student_role = Role(name="Student")
	teacher_role = Role(name="Teacher")

	db.session.add_all([database ,sdf ,group1 ,group2 ,student_role ,teacher_role])


	# Create User
	user1 = User(first_name="Tan" ,last_name="Susan" ,email="susan@gmail.com")
	user1.roles = teacher_role
	user2 = User(first_name="Wong" ,last_name="John" ,email="john@gmail.com")
	user2.roles = student_role
	user3 = User(first_name="Lim" ,last_name="Sein" ,email="lim@gmail.com")
	user3.roles = student_role

	student1 = Student(group=group1 ,user=user2)
	student2 = Student(group=group2 ,user=user3)

	teacher = Teacher(user=user1)
	
	db.session.add_all([user1 ,user2 ,user3 ,student1 ,student2 ,teacher])
	

	allocation1 = Allocation(teacher=teacher ,course=database ,group=group1)
	session1 = ClassSession(allocation=allocation1 ,attendance_code=123456)

	allocation2 = Allocation(teacher=teacher ,course=sdf ,group=group2)
	session2 = ClassSession(allocation=allocation2 ,attendance_code=456789)

	db.session.add_all([allocation1 ,allocation2 ,session1 ,session2])
	
	
	db.session.commit()

if(__name__ == "__main__"):
	with app.app_context():
		# query = sa.delete(User)
		# query2 = sa.delete(Student)
		# query3= sa.delete(Teacher)
		# db.session.execute(query)
		# db.session.execute(query2)
		# db.session.execute(query)

		# role1 = Role(name="Admin")
		# role2 = Role(name="Student")
		# role3 = Role(name="Teacher")

		# group1 = StudentGroup(name="Group 1")

		# group2 = StudentGroup(name="Group 2")

		# db.session.add_all([role1 ,role2 ,role3 ,group1 ,group2])
		# db.session.commit()
		# database = Course(name="Introduction to Database" ,code="AMS1100")
		# sdf = Course(name="Software Development Fundamental" ,code="AMS1000")
		
		# db.session.add_all([database ,sdf ])
		# db.session.commit()

		# a.weekday = WeekdayEnum.MONDAY
		print(db.session.scalars(sa.select(StudentAttendanceRecord)).all())

		pass

