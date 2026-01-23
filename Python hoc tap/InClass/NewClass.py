class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def introduce(self):
        print(f"Hello, my name is {self.name} and I am {self.age} years old.")

# Sử dụng lớp Person
person1 = Person("Alice", 25)
person1.introduce()

person2 = Person("Bob", 30)
person2.introduce()
