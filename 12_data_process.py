#read csv file
import pandas as pd
data = pd.read_csv('summary_statistics.csv')



#make a ihstogram of the mean temperature
data['mean_temp'].hist(bins=50)
import matplotlib.pyplot as plt
plt.xlabel('Mean Temperature')
plt.ylabel('Frequency')
plt.title('Histogram of Mean Temperature')
plt.show()

#compute average mean temperature of all buildings
mean_temp = data['mean_temp'].mean()
print(f'Average Mean Temperature: {mean_temp:.2f}')
#avd std deviation
std_temp = data['std_temp'].mean()
print(f'Average Standard Deviation: {std_temp:.2f}')
#how many buidings have at least 50% of the area above 18 degrees
above_18 = data[data['pct_above_18'] > 50].shape[0]
print(f'Number of buildings with more than 50% of the area above 18 degrees: {above_18}')
#how many buidings have at least 50% of the area below 15 degrees
below_15 = data[data['pct_below_15'] > 50].shape[0]
print(f'Number of buildings with more than 50% of the area below 15 degrees: {below_15}')