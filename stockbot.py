
from iexfinance.stocks import Stock
iex_token = "sk_8f26edc50f42482d9d122a1fd4ee34bb"

# ---------------
# 采用iexfinance 获取美股股票信息代码
# ---------------

# 获取开盘价
def get_stock_open(stock_code):
    s = Stock(stock_code, token=iex_token)
    return s.get_open()

# 获取成交量volume
def get_stock_volume(stock_code):
    s = Stock(stock_code, token=iex_token)
    return s.get_volume()

# 获取股票市值
def get_stock_market_cup(stock_code):
    s = Stock(stock_code, token=iex_token)
    return s.get_market_cap()

# ---------------
# 采用 openstock 获取美股股票信息
# ---------------

openstock_token = "8d080d3e04efa541"
from openstock.stock.client import StockClient
stock_client = StockClient(openstock_token)

# 获取实时行情
def get_stock_quote(stock_code):
    stock_quote = stock_client.get_stock_quote(query=[stock_code])
    return stock_quote

company_code_maps = {
    'google':'GOOG',
    'apple': 'APPL',
    'alibaba': 'BABA',
    'jd': 'JD',
    'ibm': 'IBM',
    'aws': 'AMZN',
    'tesla': 'TSLA'
}

def find_stock_code_from_company(company):
    return company_code_maps[company.lower()]


# ---------------
# rasa训练数据
# ---------------

def train(config_file,train_data):
    import warnings
    warnings.filterwarnings('ignore')
    # Import necessary modules
    from rasa.nlu.training_data import load_data
    from rasa.nlu.config import RasaNLUModelConfig
    from rasa.nlu.model import Trainer
    from rasa.nlu import config

    # Create a trainer that uses this config
    trainer = Trainer(config.load(config_file))

    # Load the training data
    training_data = load_data(train_data)

    # Create an interpreter by training the model
    interpreter = trainer.train(training_data)
    return interpreter

interpreter = train("config_spacy.yml","stock-rasa.md")

# Define negated_ents()
import re
negated_patterns = [
    re.compile(".* prefer (?:the)?\s*(\w+) to (?:the)?\s*(\w+)"),
    re.compile(r"(\w+) instead of (\w+)"),
    re.compile(".* (\w+), not (?:the)?\s*(\w+)")
]

def negated_ents(phrase):
    for pattern in negated_patterns:
        group = pattern.search(phrase)
        if group and (len(group.groups()) >= 2):
            return True,group.groups()

    return False,None

def parse_entities(message):
    entities = interpreter.parse(message)['entities']
    params = {}
    # Fill the dictionary with entities
    for ent in entities:
        params[ent["entity"]] = str(ent["value"])   
    return params

def parse_intent(message):
    intent = interpreter.parse(message)['intent']
    params = {}
    params[intent['name']] = intent['confidence']
    return params

def find_stock_code_from_message(message):
    entities = parse_entities(message)
    
    if 'company' in entities:
        return find_stock_code_from_company(entities['company'])
    if 'stock_code' in entities:
        return entities['stock_code'].upper()
    return none

# ---------------
# 实现多轮对话
# ---------------
import random
robot_sentences = {
    "robot_intro": [
        "Welcome, I am your robot which can help you stock searching",
        "lalala, I am a robot to help you search for stock information"
    ],
    "specify_company": [
        "So, What kind of stock information would you like to see for {}",
        "~~~ What kind of stock info would you prefer to known for {}",
        "biu biu, so what kind of info would you hope me offer for {}",
    ],
    "reply_open": "Stock open price: {}",
    "reply_volume": "Stock Volume: {}",
    "reply_cap": "Stock Market cap: {}",
    "reply_current": "Current Stock price: {}",
    "reply_all": "Current Stock Info: {}",
    "default": "I'm sorry - I'm not sure how to help you"
}


user_sentences = {
    "ask_open": [
        "what about open price?",
        "how about the open price?"
    ],
    "ask_volume": [
        "what is the stock volume?"
    ],
    "ask_cap": [
        "so the market cap"
    ],
    "ask_all": [
        "tell me {} company current stock station?"
    ],
    "specify_company": [
        "tell me something about {} stock info?"
    ],
    "thank": ["thank you",
             "you are greet"
    ]
}

INIT = 0
ROBOT_INTRO = 1
ASK_COMPANY = 2
ASK_ITEM = 3
ASK_RANDOM = 4
THANK = 5


policy_rules = {
    (INIT, "none"): INIT,
    (INIT, "greet"): ROBOT_INTRO,
    (ASK_RANDOM, "greet"): ASK_COMPANY,
    (ROBOT_INTRO, "specify_company"): ASK_COMPANY,
    (ASK_COMPANY, "specify_company"): ASK_ITEM,
    (ASK_COMPANY, "query_item"): ASK_RANDOM,
    (ASK_ITEM, "query_item"): ASK_RANDOM,
    (ASK_RANDOM, "query_item"): ASK_RANDOM, 
    (ASK_RANDOM, "query_item"): ASK_RANDOM, 
}

# remember state 
class StockMemory(object):
    def __init__(self):
        self.remembered_stock_code = None
        self.remembered_item = None

    def update_remembered_code(self,stock_code):
        self.remembered_stock_code = stock_code

    def get_remembered_code(self):
        return self.remembered_stock_code


    def update_remembered_item(self,query_item):
        self.remembered_item = query_item

    def get_remembered_item(self):
        return self.remembered_item


stockmemory = StockMemory()


import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
## Implementing a state machine
def send_message(policy, state, message):
    print("USER : {}".format(message))
    new_state, response = respond(policy, state, message)
    print("BOT : {}".format(response))
    return new_state

def respond(policy, state, message):
    command = interpret(message)
    new_state = policy[(state, command)]
    response = "enen"
    
    if command == 'none':
        response = robot_sentences['default'] 
    if command == 'greet':
        response = random.choice(robot_sentences['robot_intro'])
        
    if command == 'specify_company':
        response = random.choice(robot_sentences['specify_company']).format(stockmemory.get_remembered_code())
        
    if command == 'query_item':
        item = stockmemory.get_remembered_item()
        quote = get_stock_quote(stockmemory.get_remembered_code())[0]
        if item == 'open price' or item == 'open':
            response = robot_sentences['reply_open'].format(quote['open'])
        if item =='current price' or item == 'current':
            response = robot_sentences['reply_current'].format(quote['latest_price'])
        if item == 'volume':
            response = robot_sentences['reply_volume'].format(quote['volume'])
    return new_state, response

def interpret(message):
    intent = parse_intent(message)
    if 'greet' in intent:
        return 'greet'
    nega_flag, nega_ents = negated_ents(message)
    if nega_flag:
        stockmemory.update_remembered_code(find_stock_code_from_company(nega_ents[0]))
        logging.info("remebered_stock_code: "+ stockmemory.get_remembered_code())
        return 'specify_company'
    
    ents = parse_entities(message)
    if 'stock_code' in ents:
        stockmemory.update_remembered_code(ents['stock_code'])
        logging.info("remebered_stock_code: "+ stockmemory.get_remembered_code())
        return 'specify_company'
    elif 'company' in ents:
        stockmemory.update_remembered_code(find_stock_code_from_company(ents['company']))
        logging.info("remebered_stock_code: "+ stockmemory.get_remembered_code())
        return 'specify_company'
    if 'stock_term' in ents:
        stockmemory.update_remembered_item(ents['stock_term'])
        logging.info("remembered_item: " + stockmemory.get_remembered_item())
        return 'query_item'
    return 'none'



# ---------------
# Telegram
# ---------------
from telegram.ext import Updater
updater = Updater(token='965249366:AAHg3IIvjJJ0EwlOV-9qDYbh3A5WNwAQeg0')

dispatcher = updater.dispatcher


class StateMachine(object):
    def __init__(self):
        self.state = 0
    def get_state(self):
        return self.state
    def set_state(self, new_state):
        self.state = new_state

stateMachine = StateMachine()
def echo(bot, update):
    input_msg = update.message.text
    logging.info(input_msg)
    # respond(policy,state,message)
    new_state, response = respond(policy_rules, stateMachine.get_state(), input_msg)
    stateMachine.set_state(new_state)
    bot.send_message(chat_id=update.message.chat_id, text=response)


from telegram.ext import MessageHandler, Filters
echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)


updater.start_polling()