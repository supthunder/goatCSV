from bs4 import BeautifulSoup
import requests
import json
import time
import csv
import getpass
from termcolor import cprint

def parseFile(goatDATA):
	orders = []
	total = ["Total Sales:",0.00]
	print("-"*70)
	for order in goatDATA["orders"]:
		eachOrder = []
		data = str(order["product"]["productTemplate"]["name"])
		eachOrder.append(data)
		sold = str(order["sellerAmountMadeCents"])[:-2]+ "." + str(order["sellerAmountMadeCents"])[-2:]
		eachOrder.append(sold)
		cprint(data,"yellow",end='')
		if 60-len(data) > 0:
			print(" "*(60-len(data)),end='')
		cprint(" - ","yellow",end='')
		cprint(sold+"\n","green")
		orders.append(eachOrder)
		total[1] += float(sold)

	print("-"*70)

	with open('goat.csv', 'w',newline='') as csv_file:
	    writer = csv.writer(csv_file,delimiter = ',')
	    writer.writerows(orders)
	    writer.writerow(total)
	cprint("Saved to goat.csv!","green")

def sales(s, token):
	url = "https://www.airgoat.com/api/v1/orders?filter=sell&page=1"
	user = {
		"Accept":"*/*",
		"Connection":"keep-alive",
		"User-Agent":"GOAT/1.7.1 (iPhone; iOS 10.2.1; Scale/3.00)",
		"Accept-Language":"en-US;q=1, ar-US;q=0.9, ta-US;q=0.8, ja-JP;q=0.7",
		"Authorization":'Token token="'+token+'"',
		"Accept-Encoding":"gzip, deflate"
	}
	cprint("Getting sold JSON...","red")
	stock = s.get(url, headers=user, timeout=5,cookies=s.cookies)
	if str(stock.status_code) != "200":
		print("Goat.com log in temporarily banned! - "+str(stock.status_code))
		exit()
	stock = stock.json()
	cprint("Saving goat.json...","red")
	with open("goat.json", 'w') as outfile:
		json.dump(stock, outfile, indent=4, sort_keys=True)
	parseFile(stock)


def logIn(userName, password):
	s = requests.Session()
	url = "https://www.goat.com/api/v1/users/sign_in"
	header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"}
	payload = {
		"user[login]":userName,
		"user[password]":password
	}

	cprint("Getting X-CSRF-Token...","red")
	r = s.get("https://www.goat.com/",headers=header,timeout=5)
	data = r.text
	soup = BeautifulSoup(data,"html.parser")

	csrfToken = str(soup.find('meta',{"name":"csrf-token"}).get('content'))
	header["X-CSRF-Token"] = csrfToken
	header["X-Requested-With"] = "XMLHttpRequest"

	cprint("Posting Log In...","red")
	r = s.post(url,headers=header,timeout=5,params=payload,cookies=s.cookies)

	cprint("Getting session cookies and authToken...","red")
	r = s.get("https://www.goat.com/",headers=header,timeout=5,cookies=s.cookies)

	data = r.text
	soup = BeautifulSoup(data,"html.parser")
	goatToken = json.loads(soup.find(class_="js-react-on-rails-component").get('data-props'))
	token = str(goatToken["currentUser"]["authToken"])
	sales(s,token)

def main():
	userName = input("Enter Username: ")
	password = getpass.getpass("Enter Password: ")

	logIn(userName, password)

if __name__ == '__main__':
	main()
