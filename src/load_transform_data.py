# this script contains class to load, split, and encode data
# available encoding scheme are: one-hot, labelEncoder, and
# labelBinarizer
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, LabelBinarizer

class TransformXY:
    def __init__(self, data_dir='../data/clean_data/baseline_input.csv'):
        self.data = pd.read_csv(data_dir)
        self.data = self.data.fillna(value=' ', axis=1)
        self.data[['citation_teo', 'citation_man']] = self.data[['citation_teo', 'citation_man']].astype(str)

    def slice_idx(self, model, start, end):
        return model[:, start:end]

    def transform_data(self, y_enc):
        mandarin_df = self.data[['citation_man', 'initial_man', 'final_man']].copy()
        teochew_df = self.data[['citation_teo', 'initial_teo', 'final_teo']].copy()
        train_x, test_x = train_test_split(mandarin_df, test_size=0.2, random_state=42)
        train_y, test_y = train_test_split(teochew_df, test_size=0.2, random_state=42)

        # convert categorical values to one-hot encoding
        self.encX = OneHotEncoder(handle_unknown='ignore')
        X_train = self.encX.fit_transform(train_x).toarray()
        X_test = self.encX.transform(test_x).toarray()

        # handles train
        man_tone_unique = mandarin_df['citation_man'].nunique()

        man_initial_unique = mandarin_df['initial_man'].nunique()

        man_final_unique = mandarin_df['final_man'].nunique()

        man_unique = mandarin_df['citation_man'].nunique() + \
        mandarin_df['initial_man'].nunique() + mandarin_df['final_man'].nunique()

        # handles train
        self.X_train_tone = self.slice_idx(X_train, 0, man_tone_unique)
        self.X_train_initial = self.slice_idx(X_train, man_tone_unique, man_tone_unique+man_initial_unique)
        self.X_train_final = self.slice_idx(X_train, man_tone_unique+man_initial_unique, man_unique)

        # handles test
        self.X_test_tone = self.slice_idx(X_test, 0, man_tone_unique)
        self.X_test_initial = self.slice_idx(X_test, man_tone_unique, man_tone_unique+man_initial_unique)
        self.X_test_final = self.slice_idx(X_test, man_tone_unique+man_initial_unique, man_unique)

        if y_enc == 'LabelEncoder':
            # LabelEncoder for Y
            self.encT = LabelEncoder()
            self.encI = LabelEncoder()
            self.encF = LabelEncoder()

            self.encT.fit(teochew_df['citation_teo'].values.tolist())
            self.encI.fit(teochew_df['initial_teo'].values.tolist())
            self.encF.fit(teochew_df['final_teo'].values.tolist())

            self.Y_train_tone = self.encT.transform(train_y['citation_teo'].values.tolist())
            self.Y_train_initial = self.encI.transform(train_y['initial_teo'].values.tolist())
            self.Y_train_final = self.encF.transform(train_y['final_teo'].values.tolist())

            self.Y_test_tone = self.encT.transform(test_y['citation_teo'].values.tolist())
            self.Y_test_initial = self.encI.transform(test_y['initial_teo'].values.tolist())
            self.Y_test_final = self.encF.transform(test_y['final_teo'].values.tolist())

        elif y_enc == 'LabelBinarizer':
            self.encT = LabelBinarizer()
            self.encI = LabelBinarizer()
            self.encF = LabelBinarizer()

            self.Y_train_tone = np.array(train_y['citation_teo'].values.tolist()).reshape(-1, 1)
            self.Y_train_initial = np.array(train_y['initial_teo'].values.tolist()).reshape(-1, 1)
            self.Y_train_final = np.array(train_y['final_teo'].values.tolist()).reshape(-1, 1)

            self.encT.fit(self.Y_train_tone)
            self.encI.fit(self.Y_train_initial)
            self.encF.fit(self.Y_train_final)

            self.Y_train_tone = self.encT.transform(self.Y_train_tone)
            self.Y_train_initial = self.encI.transform(self.Y_train_initial)
            self.Y_train_final = self.encF.transform(self.Y_train_final)

            self.Y_test_tone = self.encT.transform(test_y['citation_teo'].values.tolist())
            self.Y_test_initial = self.encI.transform(test_y['initial_teo'].values.tolist())
            self.Y_test_final = self.encF.transform(test_y['final_teo'].values.tolist())





