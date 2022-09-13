# %%
# IMPORT Thư viện
#  pip install numpy pandas jupyter notebook openpyxl xlrd
# Python: https://www.python.org/ftp/python/3.10.7/python-3.10.7-amd64.exe
import pandas as pd
import os
import openpyxl
import xlrd
import numpy as np

# %%
# IMPORT Tổng hợp nhập xuất tồn -> RENAME 
Data_Ton = pd.read_excel("Tổng hợp Nhập - Xuất - Tồn YTD.xls",usecols="A,F,K:L",skipfooter=1,header=5)
Data_Ton=Data_Ton.rename(columns={"Unnamed: 0":"ID","Unnamed: 5":"ID_Category","Số lượng.2":"Số lượng xuất", "Giá trị.2":"Giá trị xuất" })

#Import Quotation
Data_Request=pd.read_excel("Request Quotation.xlsx",usecols="B:H")

#Import Báo cáo giá bán tồn kho
Data_GiaBanTonKho=pd.read_excel("Báo cáo giá bán, tồn kho.xls",usecols="C,F",header=4,skipfooter=1)
Data_GiaBanTonKho=Data_GiaBanTonKho.rename(columns={"Mã số":"ID"})
Data_GiaBanTonKho.dropna(how='all',inplace=True)


#Import Sổ chi tiết bán hàng
Data_BanHang=pd.read_excel("Sổ chi tiết bán hàng.xls",usecols="F,M",skipfooter=1,header=6)
Data_BanHang=Data_BanHang.rename(columns={"Unnamed: 0":"Ngày bán","Unnamed: 5":"ID" ,"Giá bán":"Giá bán giảm"})

#Import Báo cáo giá bán tồn kho
Data_TonKho=pd.read_excel("Báo cáo tồn kho.xls",usecols="A,D",header=5,skipfooter=1)
Data_TonKho=Data_TonKho.rename(columns={"Unnamed: 0":"ID","Số lượng":"Số lượng tồn"})

#Import Sổ chi tiết mua hàng
Data_MuaHang=pd.read_excel("Sổ chi tiết mua hàng (2).xls",usecols="A,C,E:F,I",header=5,skipfooter=1)
Data_MuaHang=Data_MuaHang.rename(columns={"Unnamed: 0":"Ngày nhập",
                                        "Unnamed: 2":"Nhà cung cấp",
                                        "Unnamed: 4":"Mã nhóm hàng",
                                        "Unnamed: 5":"ID",
                                        "Số lượng":"Số lượng nhập"})


# %%
# Calcuation on Tong Hop Ton Kho -------------------------------------------

# Gia Von= Gia Tri Xuat/SL Xuat * 1.05
Data_Ton['Giá vốn']=np.around(Data_Ton['Giá trị xuất']/Data_Ton['Số lượng xuất']*1.05,0)


# %%
# Merge Request -> Gia Von
Data_Request= pd.merge(Data_Request,Data_Ton[['ID','Giá vốn']],on='ID', how='left')
# Merge Giá bán (Báo cáo nhập xuất tồn)
Data_Request=pd.merge(Data_Request,Data_GiaBanTonKho[['ID','Giá bán']],how='left',on='ID')
# Merge Giá bán hàng
Data_Request=pd.merge(Data_Request,Data_BanHang,how='left',on='ID')
# Merge Số lượng tồn
Data_Request=pd.merge(Data_Request,Data_TonKho,how='left',on='ID')
# Merge Giá mua hàng
Data_Request=pd.merge(Data_Request,Data_MuaHang,how='left',on='ID')

# %%
# Calcuation on Request -------------------------------------------

#VND/US=24,000; he so = 1.13
Data_Request['Unit Price VND'] = np.around(Data_Request['Unit price']*24000*1.13,0)
Data_Request['Giá vốn chênh lệch %'] = np.around((Data_Request['Unit Price VND']-Data_Request['Giá vốn'])/Data_Request['Giá vốn']*100,2)
#SHOW KET QUA
Data_Request=Data_Request.iloc[:,[0,1,2,3,4,5,6,15,7,16,8,9,10,11,12,13,14]]

# %%

# EXPORT FILE DATA
with pd.ExcelWriter('Report Quotation Request.xlsx') as writer:
    Data_Request.to_excel(writer, sheet_name='Data')
  




