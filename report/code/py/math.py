#math formula which give the number of tweet to take
def math_formula(mini,maxi,ratio):
    inte = round(1+19*(ratio-mini)/(maxi-mini))
    return inte