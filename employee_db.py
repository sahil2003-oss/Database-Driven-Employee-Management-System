import mysql.connector as sql
mydb=sql.connect(
    host='localhost',
    user='root',
    password='Lihas@2003',
    database='employee_management_system'
)

cursor=mydb.cursor()
def create_Employee_table():
    cursor.execute('''create table if not exists Employee 
    (E_id int primary key AUTO_INCREMENT ,name varchar(20), email varchar(50),City varchar(20)
    , gender char(1),Position varchar(50), Salary DECIMAL(10, 2))''')

def create_promotion_table():
    cursor.execute("""CREATE TABLE IF NOT EXISTS Promotions (
        promo_id INT PRIMARY KEY AUTO_INCREMENT,
        E_id INT,
        old_position VARCHAR(20),
        new_position VARCHAR(20),
        old_salary DECIMAL(10, 2),
        new_salary DECIMAL(10, 2),
        FOREIGN KEY (E_id) REFERENCES Employee(E_id) ON DELETE CASCADE
    );""")


mydb.commit()

if __name__=='__main__':
    create_Employee_table()
    create_promotion_table()