#Query 1
#queryVar = ['Fraud']
#evidenceVar = []
#evidenceValues = []
#hiddenVar = ['Trav']

# Query 2
queryVar = []
evidenceVar = ['Fraud','FP','IP','CRP']
evidenceValues = ['T', 'T','F','T']
hiddenVar = ['Trav','OC']

# Whether the query is a joint table or not
isJoint = True;


import pandas as pd

class factor:
    def __init__(self, path=None, table=None):
        if path:
            self.table = pd.read_csv(path)
        else:
            self.table=table
       
    def __str__(self):
        return self.table.to_string()
    
    def sumOfTable(self):
        return sum(self.table['value'])
    
        
def product(fact1, fact2):
    fact1 = fact1.table.rename(columns={'value': 'factor_left'}, inplace=False)
    fact2 = fact2.table.rename(columns={'value': 'factor_right'}, inplace=False)
    new_factor = fact1.merge(fact2)
    new_values = []
    for index, row in new_factor.iterrows():
        new_values.append(row['factor_left']*row['factor_right'])

    new_factor['value'] = new_values
    new_factor=new_factor.drop(columns=['factor_left','factor_right'])

    print("\n\n\n------------ Created new factor----------------")
    print(new_factor)

    return factor(table=new_factor)

def containsVariable(var,factor):
    return var in factor.table.columns
    
def printFactorList(l):
    for i in l:
        print("\n")
        print(i.table.to_string())

    
def observe(factor, variable, value):
    
    tableFilter = factor.table[variable] == value
    factor.table = factor.table[tableFilter]    
    return factor

def normalize(factor):
    columnSum = factor.table['value'].sum()
    factor.table['value'] = factor.table['value'].mul(1.0 / columnSum)
    return factor

def findAndObserveFactor(factorList,variable,value):
    for factor in factorList :
        if(factor.table.columns[0] == variable):
            observe(factor, variable, value)
    

    
def sumOut(factor, variable):
    table = factor.table
    new_factor_table = table.drop(columns=['value',variable], inplace=False).drop_duplicates()

    
    new_values = []
    
    for index, r in new_factor_table.iterrows():
        row=new_factor_table.filter(items = [index], axis=0)
        sum_rows = table.merge(row)
        new_values.append(sum_rows['value'].sum())

    
    new_factor_table['value'] = new_values
    factor.table = new_factor_table

    print("\n\n\n------------ Summed out " + variable + " to create new factor ----------------")
    print(factor.table)

    return factor
    
def joins(factorList,orderedListOfHiddenVariables, joinOrder):

    for var in joinOrder:
        #partition our factors
        joinList = [x for x in factorList if containsVariable(var,x)]
        factorList = [x for x in factorList if not containsVariable(var,x)]

        currFactor = joinList.pop(0)

        while(len(joinList) > 0):
            join_in = joinList.pop(0)
            currFactor = product(currFactor, join_in)

        if var in orderedListOfHiddenVariables:
            currFactor = sumOut(currFactor,var)



        factorList.append(currFactor)

    return currFactor

def getVariables():
    
    new_factor_list = []
    
    file = open('config.txt', 'r')
    factors = file.readlines()[0].split(',')
    for f in factors:
        new_factor_list.append(factor(path= f+".txt"))
    return (new_factor_list, factors)
    
factorList, variables = getVariables()


def inQuery(var,queryVar, evidenceVar, hiddenVar):
    
    if var in queryVar:
        return True
    elif var in evidenceVar:
        return True
    elif var in hiddenVar:
        return True
    return False

def filterFactors(factorList,queryVar, evidenceVar, hiddenVar):
    factorList = [x for x in factorList if inQuery(x.table.columns[0],queryVar, evidenceVar, hiddenVar)]
    return factorList

def inference(factorList, queryVar, evidenceVar, hiddenVar):

    joinOrder = [x for x in variables if inQuery(x,queryVar, evidenceVar, hiddenVar)] # figure out join order
    factorList = filterFactors(factorList, queryVar, evidenceVar, hiddenVar) # get rid of factors we don't need in the query

    # Fix our evidence factors
    for index, evidence in enumerate(evidenceVar):
        print("Fixed " + evidenceVar[index] + " to observed value of " + evidenceValues[index])
        findAndObserveFactor(factorList, evidenceVar[index],evidenceValues[index])

    #Join factors together
    result = joins(factorList, hiddenVar, joinOrder)

    #If the resulting table is a conditional table (not a joint), normalize it
    if(isJoint == False):
        result = normalize(result)

    return result
    

resultFactor = inference(factorList, queryVar, evidenceVar, hiddenVar)


print("\n\n\n------------ Inference Result----------------")
print(resultFactor.table)
