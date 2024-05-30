#!/usr/bin/env python
# coding: utf-8

# In[9]:


import sqlite3

# Verbinden mit der Datenbank (wird erstellt, wenn sie nicht existiert)
conn = sqlite3.connect('world_population_DB.db')

# Erstellen eines Cursors-Objekts, um Befehle auszuführen
c = conn.cursor()

# Erstellen einer Tabelle
c.execute('''CREATE TABLE IF NOT EXISTS population (
          Rank INTEGER,
          CCA3 STRING,
          Country_Territory STRING,
          Capital STRING,
          Continent STRING,
          Population_2022 INTEGER,
          Population_2020 INTEGER,
          Population_2015 INTEGER,
          Population_2010 INTEGER,
          Population_2000 INTEGER,
          Population_1990 INTEGER,
          Population_1980 INTEGER,
          Population_1970 INTEGER,
          Area_km2 INTEGER,
          Density_per_km2 FLOAT,
          Growth_Rate FLOAT,
          World_Population_Percentage FLOAT
            )''')

# Transaktionen abschließen
conn.commit()

# Schließen der Verbindung
conn.close()


# ## Requirement 1 - Collection of real-world data

# In[3]:


# Libraries
import os
import json
import numpy as np
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr

# API credentials for Kaggle
with open('kaggle.json') as f:
    data = json.load(f)

os.environ['KAGGLE_USERNAME'] = data['username']
os.environ['KAGGLE_KEY'] = data['key']

from kaggle.api.kaggle_api_extended import KaggleApi

# Ignore warnings
import warnings
warnings.filterwarnings('ignore')

# Show current working directory
print(os.getcwd())


# Initialize API
api = KaggleApi()
api.authenticate()

# Download file
api.dataset_download_file('iamsouravbanerjee/world-population-dataset', 'world_population.csv', force=True)

# Read data to pandas data frame
df = pd.read_csv('world_population.csv', sep=',',on_bad_lines='skip')

print("World Population Dataframe:")
print(df.to_string())




# In[11]:


import sqlite3
import pandas as pd

# Load the CSV data into a DataFrame
file_path = 'world_population.csv'
df = pd.read_csv(file_path)

# Connect to the SQLite database
conn = sqlite3.connect('world_population_DB.db')
c = conn.cursor()

# Prepare the DataFrame to match the table schema
df.columns = ['Rank', 'CCA3', 'Country_Territory', 'Capital', 'Continent', 
              'Population_2022', 'Population_2020', 'Population_2015', 'Population_2010', 
              'Population_2000', 'Population_1990', 'Population_1980', 'Population_1970', 
              'Area_km2', 'Density_per_km2', 'Growth_Rate', 'World_Population_Percentage']

# Insert the data into the SQLite table
df.to_sql('population', conn, if_exists='append', index=False)

# Commit the transaction
conn.commit()

# Close the connection
conn.close()


# ## Requirement 2 - Data preparation (e.g. strings to numerical using regular expressions)

# In[4]:


string_columns = df.select_dtypes(include=['object']).columns
df[string_columns] = df[string_columns].astype('string')

print(df.dtypes)

df['Density_per_km2'] = df['Density_per_km2'].round(2)
df['Growth_Rate'] = df['Growth_Rate'].round(2)

print("\nDataFrame with rounded columns:")
print(df[['Density_per_km2', 'Growth_Rate']].head())

print(df.to_string())


# ## Requirement 3 - Use of Python built-in data structures (lists, dictionaries, sets, tuples) and pandas data frames

# In[5]:


# Extract specific columns into lists
countries = df['Country_Territory'].tolist()
populations = df['Population_2022'].tolist()

# Create a dictionary from a subset of the data
country_population_dict = dict(zip(countries, populations))

print(country_population_dict)


# In[6]:


# Use sets to find unique values
continents = set(df['Continent'])

# Utilize tuples for specific operations
country_population_tuples = list(zip(countries, populations))

print(country_population_tuples)


# In[7]:


country_population_tuples = list(zip(countries, populations))

# Displaying the extracted lists, dictionary, set, and tuples
print("\nList of countries:")
print(countries[:10])  # Display first 10 countries for brevity

print("\nList of populations:")
print(populations[:10])  # Display first 10 populations for brevity

print("\nDictionary of country and population:")
print(list(country_population_dict.items())[:10])  # Display first 10 items for brevity


# In[8]:


print("\nSet of unique continents:")
print(continents)


# In[9]:


print("\nList of tuples (country, population):")
print(country_population_tuples[:10])  # Display first 10 tuples for brevity


# ## Requirement 4 - Use of conditional statements, loop control statements and loops

# In[10]:


class PopulationData:
    def __init__(self, dataframe):
        self.df = dataframe

    def categorize_population(self, population):
        if population < 1_000_000:
            return 'Small'
        elif population < 10_000_000:
            return 'Medium'
        else:
            return 'Large'

    def add_population_category(self):
        self.df['Population Category'] = self.df['Population_2022'].apply(self.categorize_population)

    def calculate_continent_summary(self):
        self.continent_population_summary = {}
        for continent in self.df['Continent'].unique():
            continent_data = self.df[self.df['Continent'] == continent]
            total_population = continent_data['Population_2022'].sum()
            average_population = int(np.ceil(continent_data['Population_2022'].mean()))  # Round up and convert to int
            self.continent_population_summary[continent] = {
                'Total Population': total_population,
                'Average Population': average_population
            }

    def get_continent_summary(self):
        return self.continent_population_summary

    def filter_countries_by_population(self, threshold):
        filtered_countries = []
        for index, row in self.df.iterrows():
            if row['Population_2022'] > threshold:
                filtered_countries.append(row['Country_Territory'])
        return filtered_countries

# Usage example:

# Step 1: Initialize the PopulationData class with the DataFrame
population_data = PopulationData(df)

# Step 2: Add population category
population_data.add_population_category()

# Step 3: Print the DataFrame to see the output
print("\nDataFrame with Population Category:")
print(population_data.df[['Country_Territory', 'Population_2022', 'Population Category']].head())

# Step 4: Calculate and print continent population summary
population_data.calculate_continent_summary()
continent_summary = population_data.get_continent_summary()
print("\nContinent Population Summary:")
for continent, summary in continent_summary.items():
    print(f"{continent}: Total Population = {summary['Total Population']}, Average Population = {summary['Average Population']}")

# Step 5: Filter countries by population threshold and print them
population_threshold = 5_000_000
filtered_countries = population_data.filter_countries_by_population(population_threshold)
print(f"\nCountries with population greater than {population_threshold}:")
print(filtered_countries)


# ## Requirement 6 - Use of tables, vizualizations/graphics for data exploration

# In[12]:


# Step 1: Initialize the PopulationData class with the DataFrame
population_data = PopulationData(df)

# Step 2: Add population category
population_data.add_population_category()

# Step 3: Calculate continent population summary
population_data.calculate_continent_summary()
continent_summary = population_data.get_continent_summary()

# Step 4: Display continent summary as a table
table = [[continent, summary['Total Population'], summary['Average Population']] for continent, summary in continent_summary.items()]
print("\nContinent Population Summary Table:")
print(tabulate(table, headers=['Continent', 'Total Population', 'Average Population'], tablefmt='pretty'))

# Step 5: Bar plot of total population by continent
continent_df = pd.DataFrame(continent_summary).T.reset_index().rename(columns={'index': 'Continent'})
plt.figure(figsize=(10, 6))
sns.barplot(data=continent_df, x='Continent', y='Total Population')
plt.title('Total Population by Continent')
plt.xlabel('Continent')
plt.ylabel('Total Population')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Step 6: Histogram of country populations
plt.figure(figsize=(10, 6))
sns.histplot(df['Population_2022'], bins=30, kde=True)
plt.title('Distribution of Country Populations')
plt.xlabel('Population')
plt.ylabel('Frequency')
plt.tight_layout()
plt.show()

# Step 7: Pie chart of population categories
category_counts = df['Population Category'].value_counts()
plt.figure(figsize=(8, 8))
plt.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
plt.title('Proportion of Countries by Population Category')
plt.show()


# ## Requirement 7 - Integration of a statistical analyses (e.g. correlation analysis, statistical test); must contain a p-value.

# In[13]:


# Select numerical columns for correlation analysis
numerical_columns = ['Population_2022', 'Density_per_km2', 'Growth_Rate']

# Calculate correlation coefficients and p-values
correlation_results = {}
for col in numerical_columns:
    if col != 'Population_2022':
        corr, p_value = pearsonr(df['Population_2022'], df[col])
        correlation_results[col] = {'Correlation Coefficient': corr, 'P-value': p_value}

# Display the correlation results
print("\nCorrelation Analysis with 'Population_2022':")
for col, results in correlation_results.items():
    print(f"{col}:")
    print(f"  Correlation Coefficient: {results['Correlation Coefficient']:.4f}")
    print(f"  P-value: {results['P-value']:.4e}")

# Visualization of correlation
plt.figure(figsize=(12, 6))

# Scatter plot for '2022 Population' vs 'Density (per km²)'
plt.subplot(1, 2, 1)
sns.scatterplot(x=df['Population_2022'], y=df['Density_per_km2'])
plt.title(f"Population vs. Density (per km²)\nCorrelation: {correlation_results['Density_per_km2']['Correlation Coefficient']:.4f}, P-value: {correlation_results['Density_per_km2']['P-value']:.4e}")
plt.xlabel('Population_2022')
plt.ylabel('Density_per_km2')

# Scatter plot for '2022 Population' vs 'Growth Rate'
plt.subplot(1, 2, 2)
sns.scatterplot(x=df['Population_2022'], y=df['Growth_Rate'])
plt.title(f"Population vs. Growth Rate\nCorrelation: {correlation_results['Growth_Rate']['Correlation Coefficient']:.4f}, P-value: {correlation_results['Growth_Rate']['P-value']:.4e}")
plt.xlabel('Population_2022')
plt.ylabel('Growth_Rate')

plt.tight_layout()
plt.show()
