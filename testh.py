class Test():
    
    def out(self, execute = False):
        con = True
        if execute == False:
            print("ut")
        if execute == True or con == True:
            print("inn")


Cl = Test()
Cl.out()
#Cl.out(execute=True)

