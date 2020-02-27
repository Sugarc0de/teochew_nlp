# this script is to build a neural network in Pytorch that takes in
# multi input of mandarin features and output multi outputs for teochew
import torch
from torch import nn
from torch.utils import data
import numpy as np
import pandas as pd

class Dataset(data.Dataset):
    'Characterizes a dataset for PyTorch'
    def __init__(self, trans, name="train"):
        self.encX = trans.encX
        self.encT = trans.encT
        self.encI = trans.encI
        self.encF = trans.encF
        self.le_dict = trans.le_dict
        self.teochew_df = trans.teochew_df

        if name=='train':
            self.X_tone = trans.X_train_tone
            self.X_initial = trans.X_train_initial
            self.X_final = trans.X_train_final
            self.Y_tone = trans.Y_train_tone
            self.Y_initial = trans.Y_train_initial
            self.Y_final = trans.Y_train_final

        elif name=='test':
            self.X_tone = trans.X_test_tone
            self.X_initial = trans.X_test_initial
            self.X_final = trans.X_test_final
            self.Y_tone = trans.Y_test_tone
            self.Y_initial = trans.Y_test_initial
            self.Y_final = trans.Y_test_final

    def __len__(self):
        'Denotes the total number of samples'
        return self.X_tone.shape[0]

    def __getitem__(self, index):
        'Generates one sample of data'
        # Select sample
        X = torch.tensor(np.concatenate((self.X_tone[index,:], self.X_initial[index,:], self.X_final[index,:]),\
                          axis=None))
        return X, torch.tensor(self.Y_tone[index]), \
    torch.tensor(self.Y_initial[index]), torch.tensor(self.Y_final[index])
    
#     def __getitem__(self, index):
#         'Generates one sample of data'
#         # Select sample
#         X = torch.tensor(np.concatenate((self.X_tone[index,:], self.X_initial[index,:], self.X_final[index,:]),\
#                           axis=None))
#         Y = (torch.tensor(np.where(self.Y_tone[index, :]==1)[0]),\
#              torch.tensor(np.where(self.Y_initial[index, :]==1)[0]),\
#              torch.tensor(np.where(self.Y_final[index, :]==1)[0]))
#         return X, Y[0].squeeze(), Y[1].squeeze(), Y[2].squeeze()
