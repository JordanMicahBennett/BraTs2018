import nibabel as nib
import numpy as np
import pandas as pd
import os
#from mha import *
#from mha2 import *


def npanalysis(path, predict_prefix, out_path, file_name=''):

    # path = '/media/bmi/varkey/new_n4/Recon_2013_data/N4_zscore_testing_t1_t1c_hist_match/'
    # predict_prefix = 'new_n4_ub_zc_log'
    if file_name=='':
        file_name=predict_prefix+'.csv'
    keyword = 'wt'

    Folder = []
    Truth = []
    Prediction = []

    t = pd.DataFrame(columns=['Patient','Whole Tumor Dice', 'Tumor Core Dice', 'Active Tumor Dice', 'Pixel Count TC', 'Pixel Count AT'])

    for subdir, dirs, files in os.walk(path):
    #     if len(Folder)==1:
    #         break
        for file1 in files:
            if file1[-6:-3] == 'nii' and 'seg' in file1:
                Truth.append(file1)
                Folder.append(subdir+'/')
            elif file1[-6:-3] == 'nii' and predict_prefix in file1 and keyword not in file1:
                Prediction.append(file1)

    num_of_patients = len(Folder)
    print ('Number of Patients : ', num_of_patients)
    print ('Number of Truth Images : ', len(Truth))
    print ('Number of Prediction Images : ', len(Prediction))
    for iterator in range(num_of_patients):
        print ('Iteration : ', iterator+1)
        print ('look', Folder[iterator]+Prediction[iterator])
        predict = nib.load(Folder[iterator]+Prediction[iterator])
        predict = predict.get_data()
        try:
            truth = nib.load(Folder[iterator]+Truth[iterator])
        except:
            truth=nib.load(Folder[iterator]+Truth[iterator])
        truth = truth.get_data()

        class1 = np.sum((truth==1).astype('int'))
        class2 = np.sum((truth==2).astype('int'))
        class3 = np.sum((truth==3).astype('int'))
        class4 = np.sum((truth==4).astype('int'))


        tot = class1+class2+class3+class4

        class1_p = 100*class1/tot
        class2_p = 100*class2/tot
        class3_p = 100*class3/tot
        class4_p = 100*class4/tot

        classtc = class1+class3+class4
        classtc_p = 100*classtc/tot


        WT_truth = np.copy(truth)
        WT_truth[WT_truth>0] = 1
        WT_predict = np.copy(predict)
        WT_predict[WT_predict>0] = 1
        WT_dice = np.sum(WT_predict[WT_truth==1])*2.0/(np.sum(WT_predict)+np.sum(WT_truth))
        del WT_truth
        del WT_predict

        TC_truth = np.copy(truth)
        TC_truth[TC_truth==2] = 0

        TC_truth[TC_truth>0] = 1
        TC_predict = np.copy(predict)
        TC_predict[TC_predict==2] = 0
        TC_predict[TC_predict>0] = 1
        TC_dice = np.sum(TC_predict[TC_truth==1])*2.0/(np.sum(TC_predict)+np.sum(TC_truth))
        del TC_truth
        del TC_predict

        AT_truth = np.copy(truth)
        print (np.unique(AT_truth))
        AT_truth[AT_truth<=3] = 0
        AT_truth[AT_truth>0] = 1
        AT_predict = np.copy(predict)
        print (np.unique(AT_predict))
        AT_predict[AT_predict<=3]=0
        AT_predict[AT_predict>0] = 1
        AT_dice = np.sum(AT_predict[AT_truth==1])*2.0/(np.sum(AT_predict)+np.sum(AT_truth))
        del AT_truth
        del AT_predict


        t.loc[len(t)] = [Folder[iterator].split('/')[-2],WT_dice,TC_dice,AT_dice, classtc, class4]
    print (t.describe())
    t.to_csv(out_path+file_name,index=False)


if __name__ == '__main__':
    path = '/home/uavws/pranjal/MICCAI_BraTS_2018_Data_Training/test/LGG'
    predict_prefix = '3D_Tiramisu_103.nii.gz'
    out_path = '/home/uavws/pranjal/tiramisu/performance_csvs/'
    file_name = '3D_Tiramisu_103.csv'
    npanalysis(path, predict_prefix, out_path, file_name)
