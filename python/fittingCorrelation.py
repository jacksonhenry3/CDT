import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def RSquared(data,fitData):
	ybar = np.mean(data)
	SSTot = np.sum([(y-ybar)**2 for y in data])
	SSRes = np.sum([(y-fitData[i])**2 for i,y in enumerate(data)])
	return(1-SSRes/SSTot)




# Potential fitting functions

# power laws
def func(x, a, b, c):
	return a*(np.abs(x)+b)**(-c)-a*(b)**(-c)+1

def func(x,   a,b):
	return (x+b)**(-a)-b**(-a)+1

# Exponentials
# Exponentials from most to fewest parameters
def func(x, a, b, c):
	return ((1-c)*a**b*(np.abs(x)+a)**(-b)+c)

# # remove one parameter by garunteeing the maximum is 1 (if you switch to this change titling )
# def func(x, a, b):
# 	return (a+(1-a)*np.e**(-b*np.abs(x)))


# # remove one parameter by assuming the exponent is just x
# def func(x,  a):
# 	return (a+(1-a)*np.e**(-np.abs(x)))


data = np.loadtxt("VolumeCorrelation1.csv")
data = np.roll(data,int(len(data)/2)) #Center zero
nts  = len(data) # num time slices

x = np.array([index if index<nts-index else index-nts for index in range(nts)])
x = np.sort(x)



popt, pcov = curve_fit(func, x, data,maxfev=10000)
fitData = func(x,  popt[0], popt[1],popt[2]);

plt.plot(x,data,".")
# plt.plot(x,fitData,"-")
plt.xlabel("time seperation in latice spaces")
plt.ylabel("Correlation")
# plt.title("One Parameter Best Fit of Volume Correlation "+r'${0:.3f}+(1-{0:.3f})'.format(popt[0])+r'e^{-|x|}$')
# plt.title('{1}'.format(popt[0]))
plt.show()
# plt.plot(x,data-fitData,"*")
# plt.show()
print(RSquared(data,fitData))
# print(popt)
