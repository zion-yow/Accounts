import pandas as pd
import openai
import typer

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
        # txt_eles:str,
        # head_txts:str,
        # tail_txts:str
        ):
        '''
        Categorization by row.
        '''
        self.row = row
        self.txt_eles = row.loc[['交易时间','交易对方','商品','金额']].values
        self.head_txts = '这是我的交易记录:' 
        self.txts = f'在{self.txt_eles[0]}, 我花费了{self.txt_eles[-1] }元人民币向{self.txt_eles[1]} 购买了{self.txt_eles[2]}。'
        self.tail_txts = \
        '''请帮我将这笔订单记录分类, 在以下类别 ['必要性食品','非必要性食品','交通','一般耐用品','电子耐用品','订阅类信息服务或娱乐产品','线下娱乐或休闲'] 中，上面这个订单属于哪一类?只需要回答所属类别名称。'''
        
        self.asking_texts = self.head_txts + self.txts + self.tail_txts
    
    # classifier
    def classify_expense(self):
        # try:
        response = openai.chat.completions.create(
            model='gpt-3.5-turbo-instruct-0914',#"gpt-4.0",
            messages=[{"role": "system", "content": "你是一个根据订单记录对订单进行分类的智能助力。"},
                    {"role": "user", "content": self.tail_txts}],
            max_tokens=2048
        )
        return response['choices'][0]['message']['content']
        # except Exception as e:
        #     print(f"Error: {e}")
        #     return "Categorization Failed!."

@app.command()
def classfying():
    cates = {}
    for idx, rcd in bill_df.iterrows():
        one_bill = Bill(rcd)
    print(one_bill.classify_expense())


if __name__ ==  '__main__':
    app()
