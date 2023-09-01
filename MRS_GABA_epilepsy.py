import numpy as np
import pandas as pd
import scipy.stats as stats
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.stats.anova import AnovaRM
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# Set a random seed for reproducibility
np.random.seed(0)

# Define constants
N = 30
GABA_increase = 1.8  # Adjusted Topiramate effect

# Create synthetic dataset
healthy_gaba = np.random.uniform(8, 10.5, N)
healthy_glutamate = np.random.uniform(5, 9, N)

#  antiepileptic drug only impacts GABA
epileptic_gaba = np.random.uniform(10, 12, N) + GABA_increase  # Adjusted the range
epileptic_glutamate = np.random.uniform(5, 9, N)

parkinsons_gaba = np.random.uniform(8, 10.5, N)
parkinsons_glutamate = np.random.uniform(5, 9, N)

# Combine data into DataFrame
df = pd.DataFrame({
    'Group': ['Healthy']*N + ['Epileptic']*N + ['Parkinsons']*N,
    'GABA': np.concatenate([healthy_gaba, epileptic_gaba, parkinsons_gaba]),
    'Glutamate': np.concatenate([healthy_glutamate, epileptic_glutamate, parkinsons_glutamate])
})

# Descriptive stats
print(df.groupby('Group').describe())

# Check for homogeneity of variance
_, p_gaba = stats.bartlett(healthy_gaba, epileptic_gaba, parkinsons_gaba)
_, p_glutamate = stats.bartlett(healthy_glutamate, epileptic_glutamate, parkinsons_glutamate)
print(f"P-value for GABA variance homogeneity: {p_gaba:.4f}")
print(f"P-value for Glutamate variance homogeneity: {p_glutamate:.4f}")

# ANOVA test
fvalue_gaba, pvalue_gaba = stats.f_oneway(healthy_gaba, epileptic_gaba, parkinsons_gaba)
fvalue_glutamate, pvalue_glutamate = stats.f_oneway(healthy_glutamate, epileptic_glutamate, parkinsons_glutamate)

print(f"F-value for GABA: {fvalue_gaba:.4f} and P-value: {pvalue_gaba:.4f}")
print(f"F-value for Glutamate: {fvalue_glutamate:.4f} and P-value: {pvalue_glutamate:.4f}")

# Function to calculate eta-squared
def eta_squared(ANOVA_table):
    return ANOVA_table['sum_sq'][0] / (ANOVA_table['sum_sq'][0] + ANOVA_table['sum_sq'][1])

#  Effect size for GABA
SS_total_gaba = np.sum((df['GABA'] - df['GABA'].mean())**2)
SS_between_gaba = ((len(healthy_gaba) * (healthy_gaba.mean() - df['GABA'].mean())**2) + 
                   (len(epileptic_gaba) * (epileptic_gaba.mean() - df['GABA'].mean())**2) + 
                   (len(parkinsons_gaba) * (parkinsons_gaba.mean() - df['GABA'].mean())**2))
eta_squared_gaba = SS_between_gaba / SS_total_gaba
print(f"Effect size (eta-squared) for GABA: {eta_squared_gaba:.4f}")

# Effect size for Glutamate
SS_total_glutamate = np.sum((df['Glutamate'] - df['Glutamate'].mean())**2)
SS_between_glutamate = ((len(healthy_glutamate) * (healthy_glutamate.mean() - df['Glutamate'].mean())**2) + 
                        (len(epileptic_glutamate) * (epileptic_glutamate.mean() - df['Glutamate'].mean())**2) + 
                        (len(parkinsons_glutamate) * (parkinsons_glutamate.mean() - df['Glutamate'].mean())**2))
eta_squared_glutamate = SS_between_glutamate / SS_total_glutamate
print(f"Effect size (eta-squared) for Glutamate: {eta_squared_glutamate:.4f}")


# Visualisation with jittered data points

# GABA Levels across Groups
sns.boxplot(x='Group', y='GABA', data=df, palette="pastel", boxprops=dict(alpha=.3))
sns.stripplot(x='Group', y='GABA', data=df, jitter=True, marker='o', alpha=0.5, color='black')
plt.title('GABA Levels across Groups')
plt.show()

# Glutamate Levels across Groups
sns.boxplot(x='Group', y='Glutamate', data=df, palette="pastel", boxprops=dict(alpha=.3))
sns.stripplot(x='Group', y='Glutamate', data=df, jitter=True, marker='o', alpha=0.5, color='black')
plt.title('Glutamate Levels across Groups')
plt.show()

#Correlations

# Convert Group to dummy variables
df_dummies = pd.get_dummies(df['Group'])

# Compute and print point-biserial correlation for each group vs GABA and Glutamate
for group in df_dummies.columns:
    pb_corr_gaba, p_gaba = stats.pointbiserialr(df_dummies[group], df['GABA'])
    pb_corr_glutamate, p_glutamate = stats.pointbiserialr(df_dummies[group], df['Glutamate'])
    
    print(f"Point-biserial correlation between {group} and GABA: {pb_corr_gaba:.4f} (p-value: {p_gaba:.4f})")
    print(f"Point-biserial correlation between {group} and Glutamate: {pb_corr_glutamate:.4f} (p-value: {p_glutamate:.4f})")
    print("-" * 50)

# Storing correlation values
correlation_data = {
    'GABA': [],
    'Glutamate': []
}

# Compute point-biserial correlation for each group vs GABA and Glutamate
for group in df_dummies.columns:
    pb_corr_gaba, _ = stats.pointbiserialr(df_dummies[group], df['GABA'])
    pb_corr_glutamate, _ = stats.pointbiserialr(df_dummies[group], df['Glutamate'])
    
    correlation_data['GABA'].append(pb_corr_gaba)
    correlation_data['Glutamate'].append(pb_corr_glutamate)

# Convert correlation data to DataFrame
correlation_df = pd.DataFrame(correlation_data, index=df_dummies.columns)

# Heatmap
plt.figure(figsize=(10, 6))
sns.heatmap(correlation_df, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
plt.title("Point-biserial Correlations between Groups and Neurotransmitter Levels")
plt.show()

