import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.linear_model import LinearRegression
from itertools import cycle

# Load CSV file
file_path = ""  # Change this to the actual file path
df = pd.read_csv(file_path)

# Combine "functional" and "basis set" for unique groups
df["method"] = df["functional"] + "/" + df["basis set"]

# Get unique method combinations
methods = df["method"].unique()

# Define colors and linestyles for different methods
colors = cycle(["blue", "red", "green", "purple", "orange"])
linestyles = cycle(["--", "-.", ":"])

# Create figure
plt.figure(figsize=(7, 5))

# Plot data and regression lines for each method
for method, color, linestyle in zip(methods, colors, linestyles):
    subset = df[df["method"] == method]

    # Scatter plot
    plt.scatter(subset["energy"], subset["experimental"], label=method, color=color, alpha=0.7)

    # Fit linear regression
    X = subset["energy"].values.reshape(-1, 1)
    y = subset["experimental"].values
    model = LinearRegression().fit(X, y)
    y_pred = model.predict(X)

    # Regression equation
    slope = model.coef_[0]
    intercept = model.intercept_
    r2 = model.score(X, y)

    # Plot regression line
    x_range = np.linspace(min(df["energy"]), max(df["energy"]), 100)
    y_range = slope * x_range + intercept
    plt.plot(x_range, y_range, linestyle=linestyle, color=color, linewidth=2)

    # Annotate with equation
    plt.text(x_range[-1] - 1, y_range[-1] - 0.5, 
             f"{method}\n$y = {slope:.2f}x {intercept:+.2f}$\n$R^2 = {r2:.2f}$",
             fontsize=10, color=color, fontweight="bold")

# Identity line (y=x for reference)
plt.plot([-0.5, 2.5], [-0.5, 2.5], color="black", linewidth=2)

# Labels and legend
plt.xlabel(r"$E_{calc}$ (V vs. SCE)", fontsize=14)
plt.ylabel(r"$E_{exp}$ (V vs. SCE)", fontsize=14)
plt.legend(loc="upper left", fontsize=10)
plt.grid(True, linestyle="--", alpha=0.5)

# Show plot
plt.show()
