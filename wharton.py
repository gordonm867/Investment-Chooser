# Import necessary classes
import multiprocessing
import time
import sys # To get the user-provided data
from selenium import webdriver # Automated browser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options # Options for automated browser
from selenium.webdriver.common.keys import Keys # Send keys to webpages

negWords = ['fall', 'plummet', 'collapse', 'decrease', 'down', 'recession', 'bankrupt', 'negative', 'dip', 'sue'] # Indicate a negative outlook
posWords = ['rise', 'soar', 'up', 'increase', 'profit', 'climb', 'positive', 'recover', 'well'] # Indicate a positive outlook
chromeOpts = Options() # Define variable storing options
chromeOpts.add_argument("--headless") # Make Chrome invisible
open('data.txt', 'w').close()

sys.argv.pop(0) # Remove script name from list

class init(str):
    def init(self):
        self.stockName = "NOT FOUND"
        self.yearLow = 0
        self.yearHigh = 0
        self.yearVolatility = 0
        self.currentPrice = 0
        self.currentEPS = 0
        self.currentPE = 0
        self.market = "NOT FOUND"
        self.EPSGrowthRate = 0
        self.outlook = 0
        self.intrinsicValue = 0
        return self

for x in range(0, len(sys.argv)): # Convert the entire list to objects with useful attributes
    sys.argv[x] = init(sys.argv[x]).init()

def getProfitabilityOutlook(stock, chromeOpts): # Gets media outlook
    testBrowser = webdriver.Chrome(chrome_options=chromeOpts) # Open invisible Chrome
    testBrowser.get("https://news.google.com") # Go to Google News
    delay = WebDriverWait(testBrowser, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="gb"]/div[2]/div[2]/div/form/div[1]/div/div/div/div/div[1]/input[2]')))
    testBrowser.find_element_by_xpath('//*[@id="gb"]/div[2]/div[2]/div/form/div[1]/div/div/div/div/div[1]/input[2]').clear() # Clear the search bar
    testBrowser.find_element_by_xpath('//*[@id="gb"]/div[2]/div[2]/div/form/div[1]/div/div/div/div/div[1]/input[2]').send_keys(stock) # Type the stock name into the search bar
    testBrowser.find_element_by_xpath('//*[@id="gb"]/div[2]/div[2]/div/form/div[1]/div/div/div/div/div[1]/input[2]').send_keys(Keys.RETURN) # Press "Enter"
    testBrowser.refresh() # Refresh the page to ensure it has fully loaded
    src = testBrowser.page_source # Get the page source
    negCoeff = 0
    posCoeff = 0
    for x in range(0, len(negWords)): # Find the number of words indicating a negative outlook
        negCoeff += (len(src.split(negWords[x])) - 1)
    for x in range(0, len(posWords)): # Find the number of words indicating a positive outlook
        posCoeff += (len(src.split(posWords[x])) - 1)
    testBrowser.quit() # Quit the browser; we have the values we need
    return(posCoeff - negCoeff) # Return the difference between the number of "positive" words and "negative" words

def generateData(x):
    data = ("\nStock: " + sys.argv[x].stockName + " (" + sys.argv[x] + ")")
    data += "\n"
    data += ("Market: " + sys.argv[x].market)
    data += "\n"
    data += ("52 Week Low: $%.2f" % sys.argv[x].yearLow)
    data += "\n"
    data += ("52 Week High: $%.2f" % sys.argv[x].yearHigh)
    data += "\n"
    data += ("Volatility Percentage: " + str(sys.argv[x].yearVolatility) + "%")
    data += "\n"
    data += ("EPS: $%.2f per share" % sys.argv[x].currentEPS)
    data += "\n"
    data += ("P/E Ratio: " + str(sys.argv[x].currentPE))
    data += "\n"
    data += ("Current Price: $%.2f" % sys.argv[x].currentPrice)
    data += "\n"
    data += ("Outlook: " + str(sys.argv[x].outlook))
    data += "\n"
    data += ("Intrinsic Value: " + str(sys.argv[x].intrinsicValue))
    txtFile = open("data.txt","a")
    txtFile.write(str(x) + "\n" + str(sys.argv[x].intrinsicValue / sys.argv[x].currentPrice) + "\n" + str(sys.argv[x].yearVolatility) + "\n" + sys.argv[x].stockName + "\n")
    print data

def getData(x):
    step = 0;
    try:
        browser = webdriver.Chrome(chrome_options=chromeOpts) # Open invisible Chrome
        browser.get("https://www.cnbc.com/quotes/?symbol=" + sys.argv[x]) # Open CNBC Finance and get relevant statistics
        delay = WebDriverWait(browser, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="cnbc-contents"]/div/div[3]/div[3]/div[1]/div[2]/div/div[1]/div/table/tbody/tr[5]/td[1]/span[1]')))
        while sys.argv[x].currentPrice == 0:
            sys.argv[x].currentPrice = float(str(browser.find_element_by_xpath('//*[@id="cnbc-contents"]/div/div[3]/div[3]/div[1]/div[2]/div/div[1]/div/table/tbody/tr[5]/td[1]/span[1]').get_attribute("innerText")).replace(',', '').replace('--', '0')) # Get the current price per share of the stock
        step += 1
        sys.argv[x].stockName = str(browser.find_element_by_xpath('//*[@id="quote_title_and_chart"]/div/h1/span[1]').get_attribute("innerText")) # Get name of company
        step += 1
        try:
            sys.argv[x].yearLow = float(str(browser.find_element_by_xpath('//*[@id="quote_key_stats_bucket"]/table/tbody/tr[3]/td[2]/span[2]').get_attribute("innerText")).replace(',', '').replace('--', '0')) # Get 52 week low of stock
        except Exception as e:
            browser.refresh()
            time.sleep(25)
            sys.argv[x].yearLow = float(str(browser.find_element_by_xpath('//*[@id="quote_key_stats_bucket"]/table/tbody/tr[3]/td[2]/span[2]').get_attribute("innerText")).replace(',', '').replace('--', '0')) # Get 52 week low of stock
        step += 1
        try:
            sys.argv[x].yearHigh = float(str(browser.find_element_by_xpath('//*[@id="quote_key_stats_bucket"]/table/tbody/tr[1]/td[2]/span[2]').get_attribute("innerText")).replace(',', '').replace('--', '0')) # Get 52 week high of stock
        except Exception as e:
            browser.refresh()
            time.sleep(25)
            sys.argv[x].yearHigh = float(str(browser.find_element_by_xpath('//*[@id="quote_key_stats_bucket"]/table/tbody/tr[1]/td[2]/span[2]').get_attribute("innerText")).replace(',', '').replace('--', '0')) # Get 52 week high of stock
        step += 1
        try:
            sys.argv[x].yearVolatility = 100 * (sys.argv[x].yearHigh - sys.argv[x].yearLow) / ((sys.argv[x].yearHigh + sys.argv[x].yearLow) / 2) # Find the stock's volatility over the past year
        except Exception as e:
            browser.refresh()
            time.sleep(25)
            sys.argv[x].yearVolatility = 100 * (sys.argv[x].yearHigh - sys.argv[x].yearLow) / ((sys.argv[x].yearHigh + sys.argv[x].yearLow) / 2) # Find the stock's volatility over the past year
        step += 1
        try:
            sys.argv[x].currentEPS = float(str(browser.find_element_by_xpath('//*[@id="quote_ratios/profitability_bucket"]/table/tbody/tr[1]/td[1]/span[2]').get_attribute("innerText")).replace(',', '').replace('--', '0')) # Get the stock's earnings per share
        except Exception as e:
            browser.refresh()
            time.sleep(25)
            sys.argv[x].currentEPS = float(str(browser.find_element_by_xpath('//*[@id="quote_ratios/profitability_bucket"]/table/tbody/tr[1]/td[1]/span[2]').get_attribute("innerText")).replace(',', '').replace('--', '0')) # Get the stock's earnings per share
        step += 1
        try:
            sys.argv[x].currentPE = float(str(browser.find_element_by_xpath('//*[@id="quote_ratios/profitability_bucket"]/table/tbody/tr[2]/td[1]/span[2]').get_attribute("innerText")).replace('%', '').replace('--', '0')) # Get the stock's PE ratio
        except Exception as e:
            browser.refresh()
            time.sleep(25)
            sys.argv[x].currentPE = float(str(browser.find_element_by_xpath('//*[@id="quote_ratios/profitability_bucket"]/table/tbody/tr[2]/td[1]/span[2]').get_attribute("innerText")).replace('%', '').replace('--', '0')) # Get the stock's PE ratio
        step += 1
        try:
            sys.argv[x].market = str(browser.find_element_by_xpath('//*[@id="quote_title_and_chart"]/div/h1/span[3]').get_attribute("innerText")) # Get the market on which the stock is traded
        except Exception as e:
            try:
                browser.refresh()
                time.sleep(25)
                sys.argv[x].market = str(browser.find_element_by_xpath('//*[@id="quote_title_and_chart"]/div/h1/span[3]').get_attribute("innerText")) # Get the market on which the stock is traded
            except Exception as e:
                pass
        browser.get("https://www.reuters.com/finance/stocks/financial-highlights/" + sys.argv[x]) # Open Reuters finance to access the next statistic
        delay = WebDriverWait(browser, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="content"]/div[3]/div/div[2]/div[1]/div[8]/div[2]/table/tbody/tr[6]/td[2]')))
        step += 1
        try:
            sys.argv[x].EPSGrowthRate = float(str(browser.find_element_by_xpath('//*[@id="content"]/div[3]/div/div[2]/div[1]/div[8]/div[2]/table/tbody/tr[6]/td[2]').get_attribute("innerText").replace('%', '').replace(',', '').replace('--', '0'))) + 100 # Get the revenue growth rate
        except Exception as e:
            browser.refresh()
            time.sleep(25)
            sys.argv[x].EPSGrowthRate = float(str(browser.find_element_by_xpath('//*[@id="content"]/div[3]/div/div[2]/div[1]/div[8]/div[2]/table/tbody/tr[6]/td[2]').get_attribute("innerText").replace('%', '').replace(',', '').replace('--', '0'))) + 100 # Get the revenue growth rate
        step += 1
        sys.argv[x].outlook = getProfitabilityOutlook(sys.argv[x], chromeOpts) # Get media outlook
        step += 1
        sys.argv[x].intrinsicValue = ((sys.argv[x].currentEPS * (sys.argv[x].currentPE + (2 * sys.argv[x].EPSGrowthRate))) + (0.25 * sys.argv[x].outlook)) # Estimate the stock's intrinsic value
        generateData(x)
        browser.quit() # Close the browser
    except Exception as e:
        browser.execute_script("window.scrollTo(0, 275)")
        browser.save_screenshot("pic.png")
        browser.quit()
        print(e)
        raise ValueError("Pages not cooperating; crash at step " + str(step) + " :(")

def parseFile():
    parser = open("data.txt", "r")
    contents = parser.read().split("\n")
    while (len(contents)) < (4 * len(sys.argv)):
        time.sleep(25)
        contents = parser.read().split("\n")
    for x in range(0, len(sys.argv)):
        k = x * 4
        if (k + 1) <= len(contents):
            sys.argv[int(contents[k])].intrinsicValue = float(contents[k + 1])
            sys.argv[int(contents[k])].yearVolatility = float(contents[k + 2])
            sys.argv[int(contents[k])].stockName = contents[k + 3]

num = 0
nums = []
for x in range(0, len(sys.argv)):
    nums.append(num)
    num += 1
if __name__ == '__main__':
    pool = multiprocessing.Pool()
    pool.map(getData, nums)

parseFile()
sys.argv.sort(key=lambda x: x.intrinsicValue, reverse=True)

if(sys.argv[0].intrinsicValue < 0):
    if(float(sys.argv[0].yearVolatility) > 75):
        print("\nBased on our methodology, we predict that all of the listed companies will fall, and would highly advise alternate stocks.  If you still choose to invest in one of these, however, we would recommend " + sys.argv[0].stockName + " as the best available choice.  Please note, however, that the stock is very volatile, and heavy care is advised for best profitability.")
    else:
        print("\nBased on our methodology, we predict that all of the listed companies will fall, and would highly advise alternate stocks.  If you still choose to invest in one of these, however, we would recommend " + sys.argv[0].stockName + " as the best available choice.")
else:
    if(float(sys.argv[0].yearVolatility) > 75):
        print("\nBased on our methodology, we predict that " + sys.argv[0].stockName + " (" +  str(sys.argv[0]) + ") is the best investment choice from the stocks under consideration.  Please note, however, that this stock is very volatile, and we would advise heavy care be taken with this investment to ensure the greatest possible profitability.")
    else:
        print("\nBased on our methodology, we predict that " + sys.argv[0].stockName + " (" +  str(sys.argv[0]) + ") is the best investment choice from the stocks under consideration.")

print("\n")
pool.terminate()
