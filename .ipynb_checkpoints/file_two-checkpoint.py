# https://www.freecodecamp.org/news/if-name-main-python-example/
# Python files are called modules and they are identified by the .py file extension. 
# A module can define functions, classes, and variables. 
# Python file one module
print("File two __name__ is set to: {}" .format(__name__))

def function_three():
    print("Function three is executed")
def function_four(): 
    print("Function four is executed")


if __name__ == "__main__":
    print("File two executed when ran directly")
else:
    print("File two executed when imported")

