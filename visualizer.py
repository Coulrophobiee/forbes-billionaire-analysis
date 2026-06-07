import pandas as pd 
import plotly.express as px
import sqlite3
import ast

class Visualizer():

    def __init__(self, database_name:str, table_name):
        self.connect = sqlite3.connect(database_name)
        self.df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.connect)

    def visualize_business_industries(self):
        self.df["business_industries"] = self.df["business_industries"].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        )
        self.df = self.df.explode("business_industries")
        self.df["business_industries"] = self.df["business_industries"].str.strip()

        industry_counts = self.df["business_industries"].value_counts().reset_index()
        industry_counts.columns = ["business_industries", "count"]
        fig = px.bar(
            industry_counts, 
            x="business_industries", 
            y="count",
            title="Business Industry Distribution",
            template="plotly_white",
            color="count",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(
            xaxis_title = "Industry",
            yaxis_title = "Number of Billionaires",
            height=600,
            xaxis_tickangle=-45,
            showlegend=False
        )

        fig.show()

    def visualize_billionaire_count(self, interval="year"):
        """
        interval: "year" or "month"
        """
        if interval == "year":
            billionaire_count = self.df.groupby("year").size().reset_index(name="count")
            x_col = "year"
            x_title = "year"

        elif interval == "month":
            self.df["year_month"] = self.df["year"].astype(str) + "-" + self.df["month"].astype(str).str.zfill(2)
            billionaire_count = self.df.groupby("year_month").size().reset_index(name="count")
            x_col = "year_month"
            x_title = "Year-Month"

        fig = px.line(
            billionaire_count,
            x=x_col,
            y="count",
            title=f"Billionaire Count Over Time ({interval.capitalize()})",
            template="plotly_white",
            markers=True,
            line_shape="linear"
        )

        fig.update_layout(
            xaxis_title=x_title,
            yaxis_title="Number of Billionaires",
            height=600,
            hovermode="x unified"
        )

        fig.show()

    def visualize_mean_and_median_age_over_time(self):
        age_stats = self.df.groupby("year")["age"].agg(["mean", "median"]).reset_index()
        age_stats.columns = ["year", "mean_age", "median_age"]

        fig = px.line(
            age_stats,
            x="year",
            y=["mean_age", "median_age"],
            title="Mean vs Median Age of Billionaires Over Time",
            template="plotly_white",
            markers=True,
            labels={
                "value": "Age",
                "variable": "Metric"
            }
        )
        
        fig.update_traces(
            line=dict(width=3),
            hovertemplate="<b>Year: %{x}</b><br>Age: %{y:.1f}<extra></extra>"
        )
        fig.data[0].line.color = "#1f77b4"
        fig.data[1].line.color = "#FF6B6B"

        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Age",
            height=600,
            hovermode="x unified",
            legend=dict(
                x=0.02,
                y=0.98,
                bgcolor="rgba(255, 255, 255, 0.8)"
            )
        )

        fig.show()

    def visualize_age_distribution(self):
        fig = px.histogram(self.df, x="age", nbins=30,
                        title="Age Distribution of Billionaires",
                        template="plotly_white")
        fig.show()

    def visualize_self_made_distribution(self):
        self_made = self.df["self_made"].value_counts().reset_index()
        self_made.columns = ["self_made", "count"]
        
        self_made["self_made"] = self_made["self_made"].map({
            0: "Inherited Wealth",
            1: "Self-Made",
            False: "Inherited Wealth",
            True: "Self-Made"
        })
        
        fig = px.pie(
            self_made,
            names="self_made",
            values="count",
            title="Self-Made vs Inherited Wealth",
            template="plotly_white",
            color_discrete_map={
                "Self-Made": "#1f77b4",
                "Inherited Wealth": "#FF6B6B"
            }
        )
        
        fig.update_layout(height=600)
        fig.show()

    def visualize_age_vs_wealth(self):
        df_clean = self.df[["age", "net_worth"]].copy()
        
        df_clean["net_worth"] = df_clean["net_worth"].astype(str).str.replace(" B", "").str.strip()
        df_clean["net_worth"] = pd.to_numeric(df_clean["net_worth"], errors="coerce")
        
        df_clean["age"] = pd.to_numeric(df_clean["age"], errors="coerce")
        
        df_clean = df_clean.dropna()
        
        print(f"Plotting {len(df_clean)} points")
        print(f"Age range: {df_clean["age"].min()} - {df_clean["age"].max()}")
        print(f"Net worth range: {df_clean["net_worth"].min()} - {df_clean["net_worth"].max()}")
        
        fig = px.scatter(
            df_clean,
            x="age",
            y="net_worth",
            size="net_worth",
            color="age",
            title="Age vs Net Worth",
            template="plotly_white",
            opacity=0.6,
            size_max=50
        )
        
        fig.update_layout(
            height=600,
            yaxis_title="Net Worth ($ Billions)",
            xaxis_title="Age"
        )
        fig.show()

    def visualize_gender_distribution(self):
        gender_counts = self.df["gender"].value_counts().reset_index()
        gender_counts.columns = ["gender", "count"]
        fig = px.pie(gender_counts, names="gender", values="count",
                    title="Billionaires by Gender")
        fig.show()

    def visualize_top_countries(self, top_n=15):
        country_counts = self.df["country_of_citizenship"].value_counts().head(top_n).reset_index()
        country_counts.columns = ["country", "count"]
        fig = px.bar(country_counts, x="count", y="country", 
                    title=f"Top {top_n} Countries by Billionaire Count",
                    orientation="h")
        fig.show()