import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_csv('data/news_results_15_min.csv')
data = data.loc[data['Sentiment'] != 0]

# Calculate the correlation between sentiment and price change
corr = data['Sentiment'].corr(data['Price Change'])

# Plot the data
sns.regplot(x='Sentiment', y='Price Change', data=data)
plt.title(f"Correlation: {corr:.2f}")
plt.show()


