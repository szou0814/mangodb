import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import os
import numpy as np

class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(5, 16)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(16, 1)

    def forward(self, x):
        return self.fc2(self.relu(self.fc1(x)))

class CovidModels:
    def __init__(self):
        self.inf_model = None
        self.death_model = None
        self.inf_stats = None
        self.death_stats = None

    def train(self, data_dir="data", epochs=50):

        # parse svi data
        svi_df = pd.read_csv(os.path.join(data_dir, "SVI_2020_US_county.csv"))
        state_stats = svi_df.groupby("STATE").apply(
            lambda x: pd.Series({
                "vulnerability": x["RPL_THEMES"][x["RPL_THEMES"]>=0].mean()
            })
        ).reset_index()
        state_stats.rename(columns={"STATE": "state"}, inplace=True)

        # parse state_trends
        trends_df = pd.read_csv(os.path.join(data_dir, "state_trends.csv"))
        pop_map = dict(zip(trends_df["state"], trends_df["population"]))
        density_map = dict(zip(trends_df["state"], trends_df["pop_density"]))

        state_stats["population"] = state_stats["state"].map(pop_map)
        state_stats["density"] = state_stats["state"].map(density_map)

        # parse covid data
        covid_df = pd.read_csv(os.path.join(data_dir, "us-states.csv"))
        covid_df["date"] = pd.to_datetime(covid_df["date"])
        covid_df = covid_df.groupby(["state", pd.Grouper(key="date", freq="W")]).max().reset_index()
        covid_df.sort_values(["state", "date"], inplace=True)

        covid_df["new_cases"] = covid_df.groupby("state")["cases"].diff().fillna(0)
        covid_df["new_deaths"] = covid_df.groupby("state")["deaths"].diff().fillna(0)

        covid_df["current_infected"] = covid_df.groupby("state")["new_cases"].shift(1).fillna(0) + covid_df.groupby("state")["new_cases"].shift(2).fillna(0)
        covid_df["target_new_cases"] = covid_df.groupby("state")["new_cases"].shift(-1).fillna(0)
        covid_df["target_new_deaths"] = covid_df.groupby("state")["new_deaths"].shift(-1).fillna(0)

        # parse stringency data
        ox_df = pd.read_csv(os.path.join(data_dir, "OxCGRT_US_latest.csv"), dtype={"Date": str})
        ox_df = ox_df.dropna(subset=["RegionName"])
        ox_df["date"] = pd.to_datetime(ox_df["Date"])
        ox_weekly = ox_df.groupby(["RegionName", pd.Grouper(key="date", freq="W")]).agg({
            "StringencyIndex": "mean"
        }).reset_index()
        ox_weekly.rename(columns={"RegionName": "state", "StringencyIndex": "stringency"}, inplace=True)

        df = pd.merge(covid_df, state_stats, on="state", how="inner")
        df = pd.merge(df, ox_weekly, on=["state", "date"], how="inner")
        df = df.dropna()

        X = df[["population", "density", "current_infected", "vulnerability", "stringency"]].values.astype(np.float32)
        y_inf = df[["target_new_cases"]].values.astype(np.float32)
        y_death = df[["target_new_deaths"]].values.astype(np.float32)

        def _train_internal(X_data, y_data):
            model = SimpleModel()
            criterion = nn.MSELoss()
            optimizer = optim.Adam(model.parameters(), lr=0.01)

            X_mean = X_data.mean(axis=0)
            X_std = X_data.std(axis=0) + 1e-8
            X_norm = (X_data - X_mean) / X_std

            y_mean = y_data.mean(axis=0)
            y_std = y_data.std(axis=0) + 1e-8
            y_norm = (y_data - y_mean) / y_std

            tensor_X = torch.tensor(X_norm.tolist())
            tensor_y = torch.tensor(y_norm.tolist())

            for epoch in range(epochs):
                optimizer.zero_grad()
                outputs = model(tensor_X)
                loss = criterion(outputs, tensor_y)
                loss.backward()
                optimizer.step()

            return model, (X_mean, X_std, y_mean, y_std)

        self.inf_model, self.inf_stats = _train_internal(X, y_inf)
        self.death_model, self.death_stats = _train_internal(X, y_death)

    def load(self, model_path="models.pth"):
        data = torch.load(model_path, weights_only = False)
        self.inf_model = SimpleModel()
        self.inf_model.load_state_dict(data['inf_model'])
        self.inf_model.eval()
        self.inf_stats = data['inf_stats']

        self.death_model = SimpleModel()
        self.death_model.load_state_dict(data['death_model'])
        self.death_model.eval()
        self.death_stats = data['death_stats']

    def save(self, model_path="models.pth"):
        torch.save({
            'inf_model': self.inf_model.state_dict(),
            'inf_stats': self.inf_stats,
            'death_model': self.death_model.state_dict(),
            'death_stats': self.death_stats
        }, model_path)

    def _predict(self, model, stats, population, density, current_infected, vulnerability, stringency):
        x_mean, x_std, y_mean, y_std = stats
        x_input = [float(population), float(density), float(current_infected), float(vulnerability), float(stringency)]
        x_norm = [(x_input[i] - x_mean[i]) / x_std[i] for i in range(5)]
        tensor_x = torch.tensor([x_norm], dtype=torch.float32)

        with torch.no_grad():
            output_norm = model(tensor_x).item()

        output = output_norm * y_std[0] + y_mean[0]
        return max(0, output)

    def predict_new_infections(self, population, density, current_infected, vulnerability, stringency):
        pred = self._predict(self.inf_model, self.inf_stats, population, density, current_infected, vulnerability, stringency)
        return max(float(current_infected) * 0.05, pred)

    def predict_deaths(self, population, density, current_infected, vulnerability, stringency):
        pred = self._predict(self.death_model, self.death_stats, population, density, current_infected, vulnerability, stringency)
        return max(float(current_infected) * 0.0015, pred)

def get_models():
    models = CovidModels()
    model_path = os.path.join(os.path.dirname(__file__), "models.pth")
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

    if os.path.exists(model_path):
        models.load(model_path)
    else:
        print(f"gyat to train first")
        models.train(data_dir=data_dir)
        models.save(model_path)
        print(f"finished and saved to {model_path}")

    return models

if __name__ == "__main__":
    get_models()
