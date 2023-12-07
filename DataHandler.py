import pandas as pd
import openpyxl
import tkinter.filedialog
import datetime
import msvcrt
from IPython.display import display

def strip_in_data(data):  # Remove leading and trailing spaces from column names and data.
    data = data.rename(columns={column_name: column_name.strip() for column_name in data.columns})
    data = data.applymap(lambda x: x.strip().strip('¥') if isinstance(x, str) else x)
    return data


def read_data_wx(path):  # 获取微信数据
    d_wx = pd.read_csv(path, header=16, skipfooter=0, encoding='utf-8')  # 数据获取，微信
    d_wx = d_wx.iloc[:, [0, 4, 7, 1, 2, 3, 5]]  # 按顺序提取所需列
    d_wx = strip_in_data(d_wx)  # 去除列名与数值中的空格。
    d_wx.iloc[:, 0] = d_wx.iloc[:, 0].astype('datetime64')  # 数据类型更改
    d_wx.iloc[:, 6] = d_wx.iloc[:, 6].astype('float64')  # 数据类型更改
    d_wx = d_wx.drop(d_wx[d_wx['收/支'] == '/'].index)  # 删除'收/支'为'/'的行
    d_wx.rename(columns={'当前状态': '支付状态', '交易类型': '类型', '金额(元)': '金额'}, inplace=True)  # 修改列名称
    d_wx.insert(1, '来源', "微信", allow_duplicates=True)  # 添加微信来源标识
    len1 = len(d_wx)
    print("Sucessfully Read " + str(len1) + " 「Wechat」bills\n")
    return d_wx


def read_data_zfb(path):  # 获取支付宝数据
    d_zfb = pd.read_csv(path, header=4, skipfooter=7, encoding='gbk')  # 数据获取，支付宝
    d_zfb = d_zfb.iloc[:, [2, 10, 11, 6, 7, 8, 9]]  # 按顺序提取所需列
    d_zfb = strip_in_data(d_zfb)  # 去除列名与数值中的空格。
    d_zfb.iloc[:, 0] = d_zfb.iloc[:, 0].astype('datetime64')  # 数据类型更改
    d_zfb.iloc[:, 6] = d_zfb.iloc[:, 6].astype('float64')  # 数据类型更改
    d_zfb = d_zfb.drop(d_zfb[d_zfb['收/支'] == ''].index)  # 删除'收/支'为空的行
    d_zfb.rename(columns={'交易创建时间': '交易时间', '交易状态': '支付状态', '商品名称': '商品', '金额（元）': '金额'}, inplace=True)  # 修改列名称
    d_zfb.insert(1, '来源', "支付宝", allow_duplicates=True)  # 添加支付宝来源标识
    len2 = len(d_zfb)
    print("Sucessfully Read " + str(len2) + " 「Alipay」bills\n")
    return d_zfb


def add_cols(data):  # 增加3列数据
    # 逻辑1：取值-1 or 1。-1表示支出，1表示收入。
    data.insert(8, '逻辑1', -1, allow_duplicates=True)  # 插入列，默认值为-1
    for index in range(len(data.iloc[:, 2])):  # 遍历第3列的值，判断为收入，则改'逻辑1'为1
        if data.iloc[index, 2] == '收入':
            data.iloc[index, 8] = 1

        # update 2021/12/29: 修复支付宝理财收支逻辑bug
        elif data.iloc[index, 5] == '蚂蚁财富-蚂蚁（杭州）基金销售有限公司' and '卖出' in data.iloc[index, 6]:
            data.iloc[index, 8] = 1
        elif data.iloc[index, 5] == '蚂蚁财富-蚂蚁（杭州）基金销售有限公司' and '转换至' in data.iloc[index, 6]:
            data.iloc[index, 8] = 0
        elif data.iloc[index, 2] == '其他' and '收益发放' in data.iloc[index, 6]:
            data.iloc[index, 8] = 1
        elif data.iloc[index, 2] == '其他' and '现金分红' in data.iloc[index, 6]:
            data.iloc[index, 8] = 1
        elif data.iloc[index, 2] == '其他' and '买入' in data.iloc[index, 6]:
            data.iloc[index, 8] = -1
        elif data.iloc[index, 2] == '其他':
            data.iloc[index, 8] = 0

    # 逻辑2：取值0 or 1。1表示计入，0表示不计入。
    data.insert(9, '逻辑2', 1, allow_duplicates=True)  # 插入列，默认值为1
    for index in range(len(data.iloc[:, 3])):  # 遍历第4列的值，判断为资金流动，则改'逻辑2'为0
        col3 = data.iloc[index, 3]
        if (col3 == '提现已到账') or (col3 == '已全额退款') or (col3 == '已退款') or (col3 == '退款成功') or (col3 == '还款成功') or (
                col3 == '交易关闭'):
            data.iloc[index, 9] = 0

    # 月份
    data.insert(1, '月份', 0, allow_duplicates=True)  # 插入列，默认值为0
    for index in range(len(data.iloc[:, 0])):
        time = data.iloc[index, 0]
        data.iloc[index, 1] = time.month  # 访问月份属性的值，赋给这月份列

    # 乘后金额
    data.insert(11, '乘后金额', 0, allow_duplicates=True)  # 插入列，默认值为0
    for index in range(len(data.iloc[:, 8])):
        money = data.iloc[index, 8] * data.iloc[index, 9] * data.iloc[index, 10]
        data.iloc[index, 11] = money
    return data

if __name__ == '__main__':
    # New bills
    filename = ('Tell me the filename:')
    path = r'D:\Projects\Accounts\Dataloader'
    data_zfb = read_data_zfb(path + r'\\' + filename) 
    _new_part = add_cols(data_zfb)
    _new_part.to_csv(path + r'\\' + 'New_records_alipay.csv')

    new_part = pd.read_csv(path + r'\\' + 'New_records_alipay.csv', index_col=0).fillna('')
    display(new_part)

    # Historic bills
    his_path = r'D:\Projects\Accounts\Dataloader\his\History_records_alipay.csv'
    his_part = pd.read_csv(his_path, index_col=0).fillna('') 

    # Combine and check the duplication
    data_merge = pd.concat([his_part,new_part]).drop_duplicates()
    data_merge.to_csv(r'D:\Projects\Accounts\Dataloader\his\History_records_alipay.csv')
    display(data_merge)
    print('Update finished.')