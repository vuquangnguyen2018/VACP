# %%
# IMPORT Thư viện
#  pip install numpy pandas jupyter notebook openpyxl xlrd
import pandas as pd
import os
import openpyxl
import xlrd
import numpy as np

# %%
# IMPORT CÁC FILE (5 FILES): TỔNG NHẬP XUẤT TỒN ; GIÁ BÁN; MUA HÀNG ; BÁN HÀNG; INPUT

# IMPORT 1 Tổng hợp nhập xuất tồn -> RENAME 
Data_Ton = pd.read_excel("Tổng hợp Nhập - Xuất - Tồn YTD.xls",usecols="A,F,K:L",skipfooter=1,header=5)
Data_Ton=Data_Ton.rename(columns={"Unnamed: 0":"ID",
                                "Unnamed: 5":"ID_Category",
                                "Số lượng.2":"Tổng xuất", 
                                "Giá trị.2":"Giá trị xuất" })

#Import INPUT Quotation
Data_Request=pd.read_excel("Input.xlsx",usecols="B:H")

#Import 2: Báo cáo giá bán tồn kho
Data_GiaBanTonKho=pd.read_excel("Báo cáo giá bán, tồn kho.xls",usecols="C,F,J",header=4,skipfooter=1)
Data_GiaBanTonKho=Data_GiaBanTonKho.rename(columns={"Mã số":"ID"})
Data_GiaBanTonKho.dropna(how='all',inplace=True)


#Import 3: Sổ chi tiết bán hàng
Data_BanHang=pd.read_excel("Sổ chi tiết bán hàng.xls",usecols="F,M",skipfooter=1,header=6)
Data_BanHang=Data_BanHang.rename(columns={"Unnamed: 0":"Ngày bán",
                                        "Unnamed: 5":"ID" ,
                                        "Giá bán":"Giá bán giảm"})


#Import 4: Sổ chi tiết mua hàng
Data_MuaHang=pd.read_excel("Sổ chi tiết mua hàng (2).xls",usecols="A,C,F,I:J",header=5,skipfooter=1)
Data_MuaHang=Data_MuaHang.rename(columns={"Unnamed: 0":"Ngày nhập",
                                        "Unnamed: 2":"Nhà cung cấp",
                                        "Unnamed: 5":"ID",
                                        "Số lượng":"Tổng nhập",
                                        "Đơn giá":"Đơn giá nhập"})


# %%
# TẠO BỘ LỌC CHO SỔ MUA HÀNG: GIÁ NHẬP NHỎ NHẤT; NGÀY NHẬP GẦN NHẤT
# FILTER: Đơn giá nhập >0; Tổng nhập > 0; 
Data_MuaHang=Data_MuaHang.loc[(Data_MuaHang['Đơn giá nhập']>0) & (Data_MuaHang['Tổng nhập']>0)].sort_values('Đơn giá nhập')
# Tạo giá nhập nhỏ nhất
Min_value=Data_MuaHang.groupby('ID')['Đơn giá nhập'].min()
Data_MuaHang=Data_MuaHang.merge(Min_value,on='ID',suffixes=('', '_min'))
# -> Filter theo ID có đơn giá nhập nhỏ nhất
Data_MuaHang = Data_MuaHang[Data_MuaHang['Đơn giá nhập']==Data_MuaHang['Đơn giá nhập_min']].drop('Đơn giá nhập_min', axis=1)

#-> Filter Mã hàng có ngày nhập gần nhất
Date_max=Data_MuaHang.groupby('ID')['Ngày nhập'].max()
Data_MuaHang=Data_MuaHang.merge(Date_max,on='ID',suffixes=('', '_max'))
# -> Filter theo ID có đơn giá nhập nhỏ nhất
Data_MuaHang = Data_MuaHang[Data_MuaHang['Ngày nhập']==Data_MuaHang['Ngày nhập_max']].drop('Ngày nhập_max', axis=1)


# Data_MuaHang.loc[Data_MuaHang['ID']=="90913-02105"]
# Data_MuaHang.loc[Data_MuaHang['ID']=="T24NC50WB"]

# %%
# TẠO BỘ LỌC CHO SỔ BÁN HÀNG: GIÁ GIẢM NHỎ NHẤT;
Data_BanHang = Data_BanHang[Data_BanHang['Giá bán giảm'] == Data_BanHang.groupby('ID')['Giá bán giảm'].transform('min')]
Data_BanHang = Data_BanHang.drop_duplicates(['ID','Giá bán giảm'], keep="first")


# %%
# TÍNH TOÁN GIÁ VỐN
# Calcuation on Tong Hop Ton Kho -------------------------------------------

# Gia Von= Gia Tri Xuat/SL Xuat * 1.05
Data_Ton['Giá vốn']=np.around(Data_Ton['Giá trị xuất']/Data_Ton['Tổng xuất']*1.05,0)


# %%
# TỔNG HỢP DỮ LIỆU

# Merge Request -> Gia Von
Data_Request= pd.merge(Data_Request,Data_Ton[['ID','Giá vốn']],on='ID', how='left')
# # Merge  (Báo cáo nhập xuất tồn)
Data_Request=pd.merge(Data_Request,Data_GiaBanTonKho[['ID','Giá bán','Tổng tồn']],how='left',on='ID')
# # # # Merge Giá bán hàng
Data_Request=pd.merge(Data_Request,Data_BanHang,how='inner',on='ID')
# # Merge Giá mua hàng
Data_Request=pd.merge(Data_Request,Data_MuaHang,how='left',on='ID')


# %%
# TÍNH TOÁN CÁC HỆ SỐ
# Calcuation on Request -------------------------------------------

#VND/US=24,000; he so = 1.13
Data_Request['Unit Price VND'] = np.around(Data_Request['Unit price']*24000*1.13,0)
Data_Request['Tỷ lệ Giá vốn chênh lệch'] = np.around((Data_Request['Unit Price VND']-Data_Request['Giá vốn'])/Data_Request['Giá vốn'],2)

# %%
# MẶC CẢ GIÁ VỚI NHÀ CUNG CẤP; RATE = 15%
RateDeal=0.15
RateVNDUSD=24000

# GIÁ MẶC CẢ VND
Data_Request['Giá mặc cả VND']=np.around(Data_Request.loc[Data_Request['Tỷ lệ Giá vốn chênh lệch']<0.0000]['Giá vốn'],0)
Data_Request['Giá mặc cả VND']=np.around(Data_Request[Data_Request['Giá vốn']>=0.0]['Giá vốn']*(1-RateDeal),0)
Data_Request.sort_values(by='Giá mặc cả VND', ascending=False)

#GIÁ MẶC CẢ USD
Data_Request['Giá mặc cả USD']=np.around(Data_Request['Giá mặc cả VND']/RateVNDUSD,2)

# Data_Request.head()


# %%
#SHOW KET QUA
Data_Request=Data_Request.iloc[:,[0,1,2,3,4,5,6,15,7,16,8,10,11,12,14,13,9,17,18]]
#Unit Price, Unit VND, Giá vốn, %chênh lệch VND, Giá bán, giá giảm, Ngày nhập, Nhà cung cấp, đơn giá nhập, tổng nhập, tổng tồn
# Data_Request.head()

# Data_Request.loc[Data_Request['ID']=="T24VG4WS"]


# %%
# EXPORT FILE DATA
with pd.ExcelWriter('Report.xlsx') as writer:
    Data_Request.to_excel(writer, sheet_name='Data')
  



# %%
Data_Request


