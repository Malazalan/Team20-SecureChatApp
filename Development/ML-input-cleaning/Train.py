import torch
import pandas as pd
import os
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator
from torch import nn
import time
from torch.utils.data.dataset import random_split
from torchtext.data.functional import to_map_style_dataset
import gdown

# Making sure CUDA is happy and running on the intended device
if torch.cuda.is_available():
    device = torch.device("cuda")
    print("GPU is available.")
else:
    device = torch.device("cpu")
    print("GPU is not available, using CPU.")
x = torch.rand(3, 3).to(device)
print("Tensor is on:", x.device)

# downloads below dataset if it doesn't exist in folder
# https://www.kaggle.com/datasets/alextrinity/sqli-xss-dataset
if not os.path.exists("SQLInjection_XSS_CommandInjection_MixDataset.1.0.0.csv"):
    file_id = "1xOAp6LHZWhDYSfkymgqJPBG0FgV3dw7d"
    url = f'https://drive.google.com/uc?id={file_id}'
    output = 'SQLInjection_XSS_CommandInjection_MixDataset.1.0.0.csv'
    gdown.download(url, output, quiet=False)

# formats the data if this has never been done
if not os.path.exists("formatted_data.csv"):
    df = pd.read_csv("SQLInjection_XSS_CommandInjection_MixDataset.1.0.0.csv")
    new_rows = []

    # there is probably a faster and better way of doing this.
    # it turns 4 label columns into 1
    for index, row in df.iterrows():
        label = 0
        if row["SQLInjection"] == 1.0:
            label = 1
        if row["XSS"] == 1.0:
            label = 2
        elif row["CommandInjection"] == 1.0:
            label = 3
        elif row["Normal"] == 1.0:
            label = 4
        new_rows.append({"Sentence": row["Sentence"], "Label": label})

    df = pd.DataFrame(new_rows)

    df.to_csv("formatted_data.csv", index=False)

else:
    df = pd.read_csv("formatted_data.csv")

# splits into train test and val sets
train_df, temp_df = train_test_split(df, test_size=0.2, random_state=42)
valid_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42)

# resets indexes to be safe, not sure if this is neccasary
train_df.reset_index(drop=True, inplace=True)
valid_df.reset_index(drop=True, inplace=True)
test_df.reset_index(drop=True, inplace=True)