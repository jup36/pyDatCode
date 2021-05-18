# Fibonacci numbers module
def fib(n): # write Fibonacci series up to n
    a, b = 0, 1 # initialize
    while a < n:
        print(a, end=' ') # end the line with space - let the numbers print in a row
        a, b = b, a+b
    print()
        
def fib2(n): # return Fibonacci series up to n
    rez = []
    a, b = 0, 1 # initialize
    while a < n: 
        rez.append(a)
        a, b = b, a+b
    return rez
    
if __name__ == "__main__": # this part enables a direct execution like $ python fibo.py 
    import sys
    fib(int(sys.argv[1]))
    