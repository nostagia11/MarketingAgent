import csv
import pickle

import pandas as pd
import streamlit


def load_file(path: str) -> pd.DataFrame:
    with open(path, "rb") as f:
        dataset = csv.load(f)
        return dataset

@streamlit.cache_data
def load_data(folder: str) -> pd.DataFrame:
    all_datasets = [load_file(file) for file in Path(folder).iterdir()]
    df = pd.concat(all_datasets)
    return df