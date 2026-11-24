def fetch_detail():
    name=input('enter your name:')
    mail=input('enter your mail id :')
    city=input('Enter your City:')
    gender=input('Enter your gender:')
    position=input('Enter your Position:')
    salary=float(input('Enter your Salary:'))
    return (name,mail,city,gender,position,salary)