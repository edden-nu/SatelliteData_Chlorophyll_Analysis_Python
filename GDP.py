import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 正確讀檔方式
df = pd.read_csv('gdp_chla_data.csv', encoding='utf-8')

x_column = 'GDP Growth Rate(%)'
y_column = 'Chlorophyll Concentration(μg/L)'

plt.figure(figsize=(8, 6))
plt.scatter(df[x_column], df[y_column], label='City Name')

# 計算相關係數
correlation = df[x_column].corr(df[y_column])

# 線性回歸
fit = np.polyfit(df[x_column], df[y_column], 1)
line = np.poly1d(fit)

plt.plot(df[x_column], line(df[x_column]),
         color='red', linestyle='--',
         label=f'Correlation: {correlation:.2f}')

# 標籤
plt.xlabel(x_column)
plt.ylabel(y_column)
plt.title(f'Correlation between GDP and Coastal Pollution (Correlation: {correlation:.2f})')

# 城市名稱標註
for i, row in df.iterrows():
    plt.text(row[x_column], row[y_column], row['City Name'],
             fontsize=10, ha='right')

plt.legend()
plt.tight_layout()
plt.show()