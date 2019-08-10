# 与telegram集成的股票查询会话机器人

1. 需安装以下python包
- `iexfinance`, `openstock` 用于获取美股数据
- `rasa`, `spacy` 用于nlp, ner
- `python-telegram-bot` 用于和telegram-bot交互会话


2. 申请一个 telegram-bot token

    [python-telegram-bot reference](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API)

3. 核心代码

- 美股数据API
  ```python
  # 获取实时行情
  def get_stock_quote(stock_code):
    stock_quote = stock_client.get_stock_quote(query=[stock_code])
    return stock_quote
  ```

- 使用rasa训练数据
  ```python
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
  ```
- 上下文否定式会话
  ```python
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

  ```

- 用于记忆会话上下文中的股票信息
  ```python
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
  ```

- 状态机
  ```python
  INIT = 0
  ROBOT_INTRO = 1
  ASK_COMPANY = 2
  ASK_ITEM = 3
  ASK_RANDOM = 4
  THANK = 5


  policy_rules = {
      (INIT, "none"): INIT,
      (INIT, "greet"): ROBOT_INTRO,
      (ROBOT_INTRO, "specify_company"): ASK_COMPANY,
      (ASK_COMPANY, "specify_company"): ASK_ITEM,
      (ASK_ITEM, "query_item"): ASK_RANDOM,
      (ASK_RANDOM, "query_item"): ASK_RANDOM, 
      (ASK_RANDOM, "query_item"): ASK_RANDOM, 
  }

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
  ```
