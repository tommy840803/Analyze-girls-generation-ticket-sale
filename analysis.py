
# coding: utf-8

# In[5]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import seaborn as sns
get_ipython().magic(u'matplotlib inline')


# In[6]:


df = pd.read_csv("girlgenerationutf8-1.csv")


# In[7]:




# 時間處理 12小時轉格式為24小時
dr = df["CREATE_DATE"]
for index in range(len(dr)):
    t = dr.loc[index].split(" ")
    if(t[1]=="p.m."):               
        time = t[0] + " " + t[2] #去掉am pm，依照 年月日 時分秒 合併      
        dtime = datetime.strptime(time, '%Y/%m/%d %H:%M:%S.') + timedelta(hours=12)  #如果為pm 新增12小時
        dr.loc[index] = dtime
        #print(dtime)       
    else:
        time = t[0] + " " + t[2]
        dr.loc[index] = datetime.strptime(time, '%Y/%m/%d %H:%M:%S.')


# In[8]:


# 修正df的CREATE_DATE欄位為轉換後的
df["CREATE_DATE"]=dr

# 備份修改後的資料
new_dataset = df

# 顯示
df.head()


# In[9]:


# dt為需要的欄位

dt = df[["ORDER_ID","IDENTITY","T_STANDARD_TICKET_TYPE_NAME","SEAT_REGION_NAME","CREATE_DATE","SEX"]].sort_values("CREATE_DATE")
dt.head(10)


# In[10]:


# 觀看重複 IDENTITY，同個使用者不同時間有在訂票
dt["IDENTITY"].value_counts(dropna=False).head(10)


# In[11]:


# 觀看IDENTITY，總使用者有多少
dt["IDENTITY"].value_counts(dropna=False).count()


# In[12]:


dt.groupby([dt["IDENTITY"],df["T_STANDARD_TICKET_TYPE_NAME"]]).count()


# In[13]:


# 觀看重複 ORDER_ID 送出請求到資料表，一般來說使用者一次最多只能訂4張票
dt["ORDER_ID"].value_counts(dropna=False).head(10)


# In[14]:


# 觀看重複 CREATE_DATE 同一個時間的請求數量
dt["CREATE_DATE"].value_counts(dropna=False).head(10)


# In[15]:


# 查詢 H12366 這個身分的訂票時間，可看出此用戶不同時間都有訂資料
dt.groupby("IDENTITY").get_group("H12366")


# In[16]:


# 計算多少人同一個人不同時間買不同的票
dt.groupby([dt["IDENTITY"],df["ORDER_ID"]]).count()


# In[17]:


# 將資料集拆成 member & non-member
member_type=dt[dt["T_STANDARD_TICKET_TYPE_NAME"]=="member"]
nonmember_type=dt[dt["T_STANDARD_TICKET_TYPE_NAME"]=="non-member"]

# 去掉member & nonmember重複 IDENTITY 計算人數
member_type = member_type.drop_duplicates(subset=["IDENTITY"],keep='first')
nonmember_type = nonmember_type.drop_duplicates(subset=["IDENTITY"],keep='first')

# 計算出來會員購買人數 共2421人
member_type.groupby(member_type["IDENTITY"]).sum()

# 計算出來非會員購買人數 共438人
nonmember_type.groupby(nonmember_type["IDENTITY"]).sum().head()


# In[43]:


member_type.head()


# In[19]:


#最長時間與最短時間相減，在計算區間
# time  = (member_type["CREATE_DATE"].max() - member_type["CREATE_DATE"].min()).seconds
time1 = (nonmember_type["CREATE_DATE"].max() - nonmember_type["CREATE_DATE"].min()).seconds


# In[20]:


# time / 60 /60
nonmember_type["CREATE_DATE"].max()


# In[21]:


nonmember_type["CREATE_DATE"].max() - nonmember_type["CREATE_DATE"].min()


# In[22]:


time1 /60/60


# In[23]:


# # 會員平均每小時的上線數量
# round(len(member_type)/(time/3600),2)


# In[24]:


# # 非會員平均每小時的上線數量
# round(len(nonmember_type)/(time1/3600),2)


# In[25]:


#member_type[member_type["CREATE_DATE"]<"2010-09-18 13:30:58"]
# 按照 "天" 分组 得知 9/18日有2393人購買 9/19日僅有28人購買
member_type.groupby(member_type["CREATE_DATE"].apply(lambda x:x.day)).count()


# In[26]:


member_type.head()


# In[27]:


# 會員資料清理
# 按照 "小時"分组 
# 要區分開所以應該會有兩筆新資料集
# 拆成兩個欄位後，轉成datetim

member_type["newDate"] = [d.date() for d in member_type["CREATE_DATE"]]
member_type["newDate"] = pd.to_datetime(member_type["newDate"], format="%Y-%m-%d")

# 參考 https://stackoverflow.com/questions/45623799/why-do-i-get-1900-01-01-in-my-time-column-in-pandas
# 避免 pd.to_datetime 時分秒會有 1990-1-1增加在前面的問題
member_type["newTime"] = [d.time() for d in member_type["CREATE_DATE"]]
member_type["newTime"] = pd.to_datetime(member_type.newTime, format="%H:%M:%S").dt.time

member_type.head()


# In[28]:


# 重新整理資料集，減少欄位 => member
member = member_type[["IDENTITY","CREATE_DATE","newDate","newTime","SEX"]]
member.sort_values("CREATE_DATE")
member.head()


# In[29]:


# 將member 拆成兩個時間 0918 & 0919
member0918 = member_type[member_type["newDate"]=="2010-09-18"]
member0919 = member_type[member_type["newDate"]=="2010-09-19"]

# 查看是否為0918資料
member0918.head(10)


# In[30]:


# 計算出 0918 每小時的人數
member0918_tmp = member0918.groupby(member0918["CREATE_DATE"].apply(lambda x:x.hour)).count()

# 格式化資料格式，並將index name修改為 hour
member0918_plot = pd.DataFrame(member0918_tmp["IDENTITY"])
member0918_plot.rename(columns={"IDENTITY":"0918_count"},inplace=True)
member0918_plot.index.name = "hour"
member0918_plot


# In[31]:


# 0918 圖表
fig0918, ax = plt.subplots()
ax = member0918_plot["0918_count"].plot(kind="bar", title ="0918 Number of people", figsize=(15,10), legend=True, fontsize=12,color="#1f77b4")
ax.set_xlabel("Hour", fontsize=12)
ax.set_ylabel("count", fontsize=12)
plt.show()


# In[32]:


# 計算出 0919 每小時的人數
member0919_tmp = member0919.groupby(member0919["CREATE_DATE"].apply(lambda x:x.hour)).count()

# 格式化資料格式，並將index name修改為 hour
member0919_plot = pd.DataFrame(member0919_tmp["IDENTITY"])
member0919_plot.rename(columns={"IDENTITY":"0919_count"},inplace=True)
member0919_plot.index.name = "hour"

# 0918 圖表
fig0919, ax = plt.subplots()
ax = member0919_plot["0919_count"].plot(kind="bar", title ="0919 Number of people", figsize=(15,10), legend=True, fontsize=12,color="#1f77b4",width=0.03)
ax.set_xlabel("Hour", fontsize=12)
ax.set_ylabel("count", fontsize=12)
plt.show()


# In[33]:


# 非會員資料清理
# 按照 "小時"分组 
# 要區分開 9/18 9/19所以應該會有兩筆新資料集
# 拆成兩個欄位後，轉成datetime

nonmember_type["newDate"] = [d.date() for d in nonmember_type["CREATE_DATE"]]
nonmember_type["newDate"] = pd.to_datetime(nonmember_type["newDate"], format="%Y-%m-%d")

# 參考 https://stackoverflow.com/questions/45623799/why-do-i-get-1900-01-01-in-my-time-column-in-pandas
# 避免 pd.to_datetime 時分秒會有 1990-1-1增加在前面的問題
nonmember_type["newTime"] = [d.time() for d in nonmember_type["CREATE_DATE"]]
nonmember_type["newTime"] = pd.to_datetime(nonmember_type.newTime, format="%H:%M:%S").dt.time

nonmember_type.head()


# In[34]:


# 重新整理資料集，減少欄位 => member
nonmember = nonmember_type[["IDENTITY","CREATE_DATE","newDate","newTime","SEX"]]
nonmember.sort_values("CREATE_DATE")
nonmember.head()


# In[35]:


# 非會員
# 查看newDate的唯一值

tmp = nonmember_type.drop_duplicates(subset=["newDate"],keep='first')
tmp


# In[36]:


# 將member 拆成每個時段
nonmember1009 = nonmember[nonmember_type["newDate"]=="2010-10-09"]
nonmember1010 = nonmember[nonmember_type["newDate"]=="2010-10-10"]
nonmember1011 = nonmember[nonmember_type["newDate"]=="2010-10-11"]
nonmember1012 = nonmember[nonmember_type["newDate"]=="2010-10-12"]
nonmember1013 = nonmember[nonmember_type["newDate"]=="2010-10-13"]
nonmember1014 = nonmember[nonmember_type["newDate"]=="2010-10-14"]
nonmember1009.head()


# In[37]:


# 計算出 10/09 每小時的人數
nonmember1009_tmp = nonmember1009.groupby(nonmember1009["CREATE_DATE"].apply(lambda x:x.hour)).count()

# 格式化資料格式，並將index name修改為 hour
nonmember1009_plot = pd.DataFrame(nonmember1009_tmp["IDENTITY"])
nonmember1009_plot.rename(columns={"IDENTITY":"1009_count"},inplace=True)
nonmember1009_plot.index.name = "hour"

# 10/09 人數計算
fig1009, ax = plt.subplots()
ax = nonmember1009_plot["1009_count"].plot(kind="bar", title ="10/09 Number of people", figsize=(15,10), legend=True, fontsize=12,color="#3d9b2e")
ax.set_xlabel("Hour", fontsize=12)
ax.set_ylabel("count", fontsize=12)
plt.show()



# In[38]:


# 計算出 10/10 每小時的人數
nonmember1010_tmp = nonmember1010.groupby(nonmember1010["CREATE_DATE"].apply(lambda x:x.hour)).count()

# 格式化資料格式，並將index name修改為 hour
nonmember1010_plot = pd.DataFrame(nonmember1010_tmp["IDENTITY"])
nonmember1010_plot.rename(columns={"IDENTITY":"1010_count"},inplace=True)
nonmember1010_plot.index.name = "hour"

# 10/10 人數計算
fig1010, ax = plt.subplots()
ax = nonmember1010_plot["1010_count"].plot(kind="bar", title ="10/10 Number of people", figsize=(15,10), legend=True, fontsize=12,color="#3d9b2e")
ax.set_xlabel("Hour", fontsize=12)
ax.set_ylabel("count", fontsize=12)
ax.set_ylim([0,100])
plt.show()


# In[39]:


# 計算出 10/11 每小時的人數
nonmember1011_tmp = nonmember1011.groupby(nonmember1011["CREATE_DATE"].apply(lambda x:x.hour)).count()

# 格式化資料格式，並將index name修改為 hour
nonmember1011_plot = pd.DataFrame(nonmember1011_tmp["IDENTITY"])
nonmember1011_plot.rename(columns={"IDENTITY":"1011_count"},inplace=True)
nonmember1011_plot.index.name = "hour"

# 10/11 人數計算
fig1009, ax = plt.subplots()
ax = nonmember1011_plot["1011_count"].plot(kind="bar", title ="10/11 Number of people", figsize=(15,10), legend=True, fontsize=12,color="#3d9b2e")
ax.set_xlabel("Hour", fontsize=12)
ax.set_ylabel("count", fontsize=12)
ax.set_ylim([0,100])
plt.show()


# In[40]:


# 計算出 10/12 每小時的人數
nonmember1012_tmp = nonmember1012.groupby(nonmember1012["CREATE_DATE"].apply(lambda x:x.hour)).count()

# 格式化資料格式，並將index name修改為 hour
nonmember1012_plot = pd.DataFrame(nonmember1012_tmp["IDENTITY"])
nonmember1012_plot.rename(columns={"IDENTITY":"1012_count"},inplace=True)
nonmember1012_plot.index.name = "hour"

# 10/12 人數計算
fig1012, ax = plt.subplots()
ax = nonmember1012_plot["1012_count"].plot(kind="bar", title ="10/12 Number of people", figsize=(15,10), legend=True, fontsize=12,color="#3d9b2e")
ax.set_xlabel("Hour", fontsize=12)
ax.set_ylabel("count", fontsize=12)
ax.set_ylim([0,100])
plt.show()


# In[41]:


# 計算出 10/13 每小時的人數
nonmember1013_tmp = nonmember1013.groupby(nonmember1013["CREATE_DATE"].apply(lambda x:x.hour)).count()

# 格式化資料格式，並將index name修改為 hour
nonmember1013_plot = pd.DataFrame(nonmember1013_tmp["IDENTITY"])
nonmember1013_plot.rename(columns={"IDENTITY":"1013_count"},inplace=True)
nonmember1013_plot.index.name = "hour"

# 10/13 人數計算
fig1013, ax = plt.subplots()
ax = nonmember1013_plot["1013_count"].plot(kind="bar", title ="10/13 Number of people", figsize=(15,10), legend=True, fontsize=12,color="#3d9b2e")
ax.set_xlabel("Hour", fontsize=12)
ax.set_ylabel("count", fontsize=12)
ax.set_ylim([0,100])
plt.show()


# In[42]:


# 計算出 10/14 每小時的人數
nonmember1014_tmp = nonmember1014.groupby(nonmember1014["CREATE_DATE"].apply(lambda x:x.hour)).count()

# 格式化資料格式，並將index name修改為 hour
nonmember1014_plot = pd.DataFrame(nonmember1014_tmp["IDENTITY"])
nonmember1014_plot.rename(columns={"IDENTITY":"1014_count"},inplace=True)
nonmember1014_plot.index.name = "hour"

# 10/14 人數計算
fig1014, ax = plt.subplots()
ax = nonmember1014_plot["1014_count"].plot(kind="bar", title ="10/14 Number of people", figsize=(15,10), legend=True, fontsize=12,color="#3d9b2e")
ax.set_xlabel("Hour", fontsize=12)
ax.set_ylabel("count", fontsize=12)
ax.set_ylim([0,100])
plt.show()

