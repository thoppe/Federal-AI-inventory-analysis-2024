import streamlit as st
import pandas as pd
import numpy as np

import datetime
import json
from pathlib import Path

import src.viz_interface as interface
from bokeh.models import Label


app_text = {
    "title": "Federal AI inventory analysis 2024",
    "footer": "Built by [Travis Hoppe](https://github.com/thoppe/Federal-AI-inventory-analysis-2024).",
}

start_time = datetime.datetime.now()

st.set_page_config(layout="wide")
st.title(app_text["title"])
st.markdown("_Draft viz - Work in progress_")


@st.cache_data
def load_data():
    load_dest = Path("data/processed/")

    embedding = np.load(load_dest / "GPT_umap.npy")
    df_keywords = pd.read_csv(load_dest / "GPT_cluster_keywords.csv")
    clusters = np.load(load_dest / "GPT_clusters.npy")

    key = "1_use_case_id"
    df0 = pd.read_csv("data/cleaned_OMB_inventory.csv")
    df1 = pd.read_csv(load_dest / "summary_text.csv")

    df0 = df0.set_index(key)
    df1 = df1.set_index(key)

    df0["x2_summary_text"] = df1["x2_summary_text"]
    df0["ux"], df0["uy"] = embedding.T

    return df0, df_keywords, clusters


df, df_keywords, clusters = load_data()

n_text_show = st.sidebar.slider(
    "Number of text labels", 0, df_keywords["n_clusters"].max(), 20
)


dept_opt = df.groupby("3_agency").size().sort_values(ascending=False).index.tolist()
dept_opt = ["None"] + sorted(dept_opt)
highlight_department = st.sidebar.selectbox("Highlight Dept/Agency", dept_opt)

highlight_text = st.sidebar.text_input("Word search")
if highlight_text:
    highlight_text = highlight_text.lower()
else:
    highlight_text = "DO NOT MATCH TO ANYTHING"
textword_highlight_idx = df["x2_summary_text"].str.lower().str.find(highlight_text) > -1

## Basic coloring

df["line_width"] = 0
df["color"] = "#3288bd"
df["fill_color"] = df["color"]
df["no_focus"] = 1

colors = ["#05baae", "black", "#e47474", "#e4749c"] * 1000
expand = 1.25
point_size = 5

df["size"] = point_size
df["alpha"] = 0.4

# Custom coloring
text_highlight_idx = df["3_agency"] == highlight_department

if textword_highlight_idx.sum():
    st.sidebar.write(
        f"Highlighting {textword_highlight_idx.sum()} projects using {highlight_text}"
    )

df.loc[textword_highlight_idx, "fill_color"] = colors[1]
df.loc[textword_highlight_idx, "size"] = point_size * expand
df.loc[textword_highlight_idx, "line_width"] = 2
df.loc[textword_highlight_idx, "alpha"] = 0.8

if text_highlight_idx.sum():
    st.sidebar.write(
        f"Highlighting {text_highlight_idx.sum()} projects from {highlight_department}"
    )

df.loc[text_highlight_idx, "fill_color"] = colors[2]
df.loc[text_highlight_idx, "size"] = point_size * expand
df.loc[text_highlight_idx, "line_width"] = 2
df.loc[text_highlight_idx, "alpha"] = 0.8

viz_cols = [
    "3_agency",
    "4_bureau",
    "x2_summary_text",
]

df["line_width"] = 0.1
df["radius_units"] = "screen"

p = interface.plot_data_bokeh(
    df, hover_columns=viz_cols, tooltips=True, height=600, width=800
)

## Add the text labels

df_keywords = df_keywords[df_keywords.n_clusters == n_text_show]

for _, row in df_keywords.iterrows():
    label_args = {
        "x": row["cluster_x"],
        "y": row["cluster_y"],
        "text": row["label_text"],
        "text_color": "black",
        "background_fill_color": "white",
        "background_fill_alpha": 0.25,
    }
    p.add_layout(Label(**label_args))

end_time = datetime.datetime.now()
dt = (end_time - start_time).total_seconds()
st.sidebar.write(f"Compute time {dt:0.3f}")

save_btn = st.sidebar.button("Export HTML Plot")

if save_btn:
    import bokeh
    from bokeh.plotting import show

    f_save = Path("results/vizmap.html")
    f_save.parent.mkdir(exist_ok=True)

    bokeh.io.output_file(f_save, "Fed_AI_2023")
    show(p)
    st.write(f_save)

st.bokeh_chart(p, use_container_width=True)
st.write(app_text["footer"])
