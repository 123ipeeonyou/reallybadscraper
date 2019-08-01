from bs4 import BeautifulSoup
from selenium import webdriver
import datetime
import numpy

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10b.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko)'
                         'Chrome/70.0.3538.110 Safari/537.36'}

print("N/A means no StockX link is up yet. Could mean that the release is too far away"
      " or the shoe is a GR")


def javascript_unrender(url):
    #scrapes javascript rendered pages
    browser = webdriver.Chrome()
    browser.get(url)
    innerHTML = browser.execute_script("return document.body.innerHTML")
    soupedhtml = BeautifulSoup(innerHTML, 'html.parser')
    return soupedhtml


def url_scraper():

    #scrapes front page for all upcoming sneaker releases
    urls = []
    main_url = "http://www.solelinks.com"
    pagesoup = javascript_unrender(main_url)
    for line in pagesoup.findAll('div',{"class":"shoes-details"}):
        a_tag = line.find("a", {})
        current_url = a_tag.get("href")
        name_span = str(line.find("span", {"class": "shoes-name"}))
        name = name_span[name_span.index(">")+1:name_span.index(">")+name_span[name_span.index(">"):].index("<")]
        urls.append([(main_url + str(current_url)),name])
    return urls

    # now we have all the urls, we can use
    # shoe detail function to find attributes individually~


def get_shoe_details(shoe_url):

    attrs = {"Price":0,"Release-Date":0, "SKU": 0, "Color": 0}
    retailers = {}
    soup = javascript_unrender(shoe_url)
    # GET ATTRIBUTES
    for line in soup.findAll("ul",{"class":"show-info"}):

        for s in line.findAll("li"):
            a = str(s)

            #find price
            if "$" in a:
                start = a.index("$")
                end = a[start:].index("<")
                attrs["Price"] = a[start:start+end]
            #find release date
            elif "Release Date:" in a:
                start = (a.index("-") - 2)
                end = a[start:].index("<")
                attrs["Release-Date"] = a[start:start+end]
            #find SKU
            elif "Style Code" in a:
                start = a.index("</span><span>") + 13
                end = a[start:].index("<")
                attrs["SKU"] = a[start:start+end]
            #find product color
            elif "Color" in a:
                start = a.index("</span><span>") + 13
                end = a[start:].index("<")
                attrs["Color"] = a[start:start+end]
    #GET RETAILERS
    times = []
    for line in soup.findAll("ul", {"class": "ret-list"}):
        time = line.li.string
        times.append(time) # if dict has no time, its a raffle
    j = 0
    for line in soup.findAll("div", {"class":"heading-holder"}):
        i = line.h3.string       #.h3 gets text between tag,.string converts to str and removes
        retailers[i] = [line.a.get("href"),times[j]]
        j = j + 1
    if retailers == {}:
        print("No retailers found yet")
    return attrs,retailers


def text_between_tags(html):
    string = str(html)
    return string[string.index(">") + 1:string.index("</")]

def stockx_fee(x):
    return (x*.91)*.97



def profitability_calculator(shoe_url):
    attributes,retailers = get_shoe_details(shoe_url)
    print(attributes)
    retail_price = attributes["Price"]
    retail_price_taxed = int(retail_price[1:]) * 1.08875
    if "STOCKX" not in retailers.keys():
        return "profitability: N/A"
    else:
        stockx_url = retailers["STOCKX"][0]
    buys = {}
    stockx_soup = javascript_unrender(stockx_url)
    for line in stockx_soup.findAll("div", {"class": "inset"}):
        """
        Problem: How to get size between the tags:
        <div class="title">11.5</div>
        needs to return 11.5
        """
        size = (text_between_tags(line.find("div",{"class":"title"})))
        """
        current solution: brute force string manipulation
        """
        price = (text_between_tags(line.find("div",{"class":"subtitle"})))
        if price == "Bid":
            buys[size] = 0
        else:
            a = (price[1:]).replace(",","")
            buys[size] = stockx_fee(int(a)) - retail_price_taxed
    sorted_profits = sorted(buys.items(), key= lambda x : x[1])
    values = []
    for i in range(len(sorted_profits)):
        if (sorted_profits[i][1] != 0) and (sorted_profits[i][1] < 5000):
            values.append(sorted_profits[i][1])
    average = numpy.mean(values)
    median = numpy.median(values)
    stdev = numpy.std(values)
    if stockx_fee(median) >= (median -retail_price_taxed)* 1.5:
        profitability = "High resell across all sizes"
    elif stockx_fee(median) <= 10:
        profitability = "Seems this pair is probably not profitable"
    elif stockx_fee(median) >= (median- retail_price_taxed) * 1.2:
        profitability = "profitable pair, dont sleep"
    elif stockx_fee(median) >= (median- retail_price_taxed) + 20:
        profitability = "pocket money to be made"
    else:
        profitability = "N/A"
    profit_attributes = {"average": average, "median": median, "stdev" : stdev, "profitablility": profitability}
    return profit_attributes


#print(profitability_calculator("http://www.solelinks.com/releases/3418zx"))
def automater(shoesnum):

    # checks all upcoming releases up to shoesnum range

    upcoming_urls = []
    urls = url_scraper()
    a = list(urls)
    for i in range(shoesnum):
        upcoming_urls.append(a[i])
    for shoes in upcoming_urls:
        print(profitability_calculator(shoes[0]))


print(automater(9)) 

