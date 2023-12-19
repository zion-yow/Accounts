import pandas as pd
import openai
import typer
from random import randint
import time

app = typer.Typer()

# read api key
with open(r'D:\accounts_key.txt','r') as key_file:
    OPENAI_API_KEY = key_file.readline()

openai.api_key = OPENAI_API_KEY

# read bills record
bill_df = pd.read_csv(r'D:\Projects\Accounts\Dataloader\his\History_records_alipay.csv', index_col=0)


# Bill
class Bill(object):
    def __init__(
        self,
        row:pd.core.series.Series,
        ):
        '''
        Categorization by row.
        '''
        self.row = row
        self.txt_eles = row.loc[['交易时间','交易对方','商品','金额']].values
        self.head_txts = '这是我的交易记录:' 
        self.txts = f'在{self.txt_eles[0]}, 我花费了{self.txt_eles[-1] }元人民币向{self.txt_eles[1]} 购买了{self.txt_eles[2]}。'
        self.tail_txts = \
        '''请帮我将这笔订单记录分类（只返回类别名称，如果难以判断则归类为“其他”），在以下类别 [食品,交通,耐用品,订阅类信息服务或娱乐产品,线下娱乐或休闲,理财] 中，上面这个订单属于哪一类?'''
        self.asking_texts = self.head_txts + self.txts + self.tail_txts
    
    # classifier
    def classify_expense(self):
        # try:
        response = openai.ChatCompletion.create(
            model='gpt-4-1106-preview',
            messages=[{"role": "system", "content": "你是一个根据订单记录对订单进行分类的智能助力，你言简意赅。你擅长结合交易对方的名称，交易发生的时间，交易金额判断支出类型。"},
                    {"role": "user", "content": self.asking_texts}],
            max_tokens=16
        )
        return response['choices'][0]['message']['content']

@app.command()
def classfying():
    # read bills record
    bill_df = pd.read_csv(r'\Dataloader\his\History_records_alipay.csv', index_col=0)

    # copy a datetime column
    bill_df['时间'] =bill_df['交易时间'].copy() 
    Bills_df = bill_df.set_index('时间').sort_index()

    # dict to accept the result
    cates = {}
    for idx, rcd in tqdm(Bills_df.iterrows()):
        if idx in cates.keys():
            continue
        
        one_bill = Bill(rcd)
        cates[idx] = one_bill.classify_expense()
        print(rcd['商品'],cates[idx])
        time.sleep(randint(1,2))

    # concat the category
    Bills_df['cate'] = pd.Series(cates)

    # output
    Bills_df.to_excel('CateFinishedBill.xlsx')

if __name__ ==  '__main__':
    app()
