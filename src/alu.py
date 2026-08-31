class Alu:
    def execute(self, op, a, b):
        if op == "ADD" :
            return a + b 
        elif op == "SUB":
            return a- b 
        elif op == "MUL":
            return a* b 
        elif op == "DIV":
            return a/b 

        elif op == "CMP":
            diff = a-b 
            return (diff < 0, diff ==0 , diff >0)
        