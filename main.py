# driver code -: Employee Management System
from user_input import fetch_detail
from Employee import *
print('Welcome to Employee Management System')

while True:
    print('Enter 1 for Adding Employee')
    print('Enter 2 for Removing Employee')
    print('Enter 3 for Promoting Employee')
    print('Enter 4 for Display Employee')
    print('Enter 5 for Exit')
    try:
        choice=int(input('enter your choice'))
        if choice==1:
            # logic for adding employee using Add_Employee() function
            details=fetch_detail()
            add_emp_obj=Emp(details[0],details[1],details[2],details[3],details[4],details[5])
            add_emp_obj.make_entry()
            print('successfully inserted row for new employee')

        elif choice==2:
            # logic for removing employee delete from employee where condition;
            target_id_to_delete=int(input('enter the id for which you want to delete the entry :'))
            del_emp_obj=Emp(id=target_id_to_delete)
            del_emp_obj.deletion(target_id_to_delete)
            print('successfully deleted row specific to the passed unique key id')

        elif choice==3:
            # logic for promoting employee
            id=int(input('Enter the id :'))
            new_position=input('enter the new designation:')
            new_salary=float(input('enter new salary'))
            promote_emp_obj=Emp(id=id)
            promote_emp_obj.promote_employee(id,new_position,new_salary)
            
        elif choice==4:
            # logic for displaying employee
            show_all_emp_obj=Emp()
            records=show_all_emp_obj.show_all_employee()
            print(records)
            
        elif choice==5:
            # make exit
            break
        else:
            print('kindly put input among the following options given -:1,2,3,4 and 5')
    except ValueError:
        print('invalid value typed! kindly ensure to give valid inputs only-:1,2,3,4,5')
