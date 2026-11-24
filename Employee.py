from employee_db import *
class Emp:
    def __init__(self,name=None,mail=None,city=None,gender=None,position=None,salary=None,id=None):
        self.name,self.mail,self.city,self.gender,self.position,self.salary=name,mail,city,gender,position,salary

    def make_entry(self):
        cursor.execute('insert into employee(name,email,City,gender,position,salary) values(%s,%s,%s,%s,%s,%s)',(self.name,self.mail,self.city,self.gender,self.position,self.salary))
        mydb.commit()

    def deletion(self,target_id):
        cursor.execute("delete from employee where E_id=%s",(target_id,))
        mydb.commit()

    def show_all_employee(self):
        cursor.execute('select * from employee')
        records=cursor.fetchall()
        mydb.commit()
        return records

    def promote_employee(self,e_id, new_position, new_salary):
    # 1. Fetch current position and salary
        cursor.execute("SELECT Position, Salary FROM Employee WHERE E_id = %s", (e_id,))
        current = cursor.fetchone()

        if current:
            old_position,old_salary = current

    # 2. Log the change in Promotions history
        cursor.execute("""INSERT INTO Promotions (E_id, old_position, new_position, old_salary, new_salary)
        VALUES (%s, %s, %s, %s, %s)
                        """,
        (e_id, old_position,new_position, old_salary,new_salary))

    # 3. Update the Employee's current status
        cursor.execute("""UPDATE Employee SET Position = %s, Salary = %s WHERE E_id = %s""",(new_position, new_salary, e_id))

        mydb.commit()

        