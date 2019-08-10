## synonym:current
- current price
- current stock price

## synonym:open
- open price
- open stock price

## synonym:aws
- amazon
- AWS

## synonym:information
- info 

## regex:zipcode
- [0-9]{5}
  
## regex:greet
- [Hh]ey[^\\s]*
- [Hh]i[^\\s]*
- [Hh]ello[^\\s]*

## intent:greet
- hey
- howdy
- hey there
- hello
- hi
- good morning
- good evening
- dear sir

## intent:affirm
- yes
- yep
- yeah
- indeed
- that's right
- ok
- great
- right, thank you
- correct
- great choice
- sounds really good

## intent:robot_intro
- I'm a robot to help you search for stock information
- i am your robot which can help you stock searching
  
## intent:stock_search
- i wanna search for some stock info
- Which company would you like to know about?
- Could you tell me something about [Alibaba](company:alibaba) company
- [Apple](company:apple) company
- [Google](company:google) company
- [IBM](company:ibm) stock
- i want to  know [APPL](stock_code) [open price](stock_term) 
- What kind of stock information for [AAPL](stock_code) would you like to see?
- [Current price](stock_term)
- [Current Stock price](stock_term) is 34131 
- What about today's [volume](stock_term)
- Tell me about the [volume](stock_term)
- how about the [open price](stock_term]?
- Today's [volume](stock_term) is 123456
- so the [market cap](stock_term)?
- tell me the [market cap](stock_term)
- And cound you please provide me with historical information for [google](company)?
- [Google](company:google) stock info
- what about the stock's [open price](stock_term)
- I wanna know something about [alibaba](company) instead of [jd](company)
- I prefer the [google](company) to the [apple](company)
- I prefer [google](company) to [apple](company)
- [Tesla](company:tesla) company

## intent:goodbye
- bye
- goodbye
- good bye
- end
- Bye bye

## intent:thank
- thanks
- thx 
- thank you 

