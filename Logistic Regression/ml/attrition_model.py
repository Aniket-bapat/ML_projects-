import pandas as pd
import pickle

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression

# ================= input data  =================
df = pd.read_csv("employee_attrition.csv")

X = df.drop("Attrition", axis=1)
y = df["Attrition"]

# ================= Feature segreation =================
num_features = ["Age","MonthlyIncome","YearsAtCompany","JobLevel"]
cat_features = ["Gender","Department","OverTime"]
# ================= preprocessor  =================
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), num_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_features)
    ]
)

# ================= implement pipeline  =================
pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", LogisticRegression(max_iter=1000))
    ]
)

# ================= Traning of model  =================
pipeline.fit(X, y)

# ================= pickle file dump hogaya =================
with open("attrition_model.pkl", "wb") as f:
    pickle.dump(pipeline, f)

print("Logistic Regression pipeline saved successfully")
