from flask import Flask,render_template,request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
logging.basicConfig(filename="scrapper.log",level = logging.INFO)

app = Flask(__name__)

@app.route("/",methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review",methods = ['GET','POST'])
def index():
    if request.method == 'POST':
        try:
            searchstring = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchstring
            uclient  = uReq(flipkart_url)   
            flipkartpage = uclient.read()

            uclient.close()
            flipkart_html = bs(flipkartpage,"html.parser")
            bigboxes = flipkart_html.findAll("div",{'class':"_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            product_link =  "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(product_link)
            prodRes.encoding = 'utf-8'
            prod_html = bs(prodRes.text,"html.parser")
            print(prod_html)
            commentboxes = prod_html.find_all('div',{'class':"_16PBlm"})


            filename  = searchstring + '.csv'
            fw = open(filename,"w")
            headers = "Product,customer,name,rating,heading,comment \n"

            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all("p",{"class":'_2sc7ZR _2V5EHH'})[0].text 
                
                except:
                    name = "no name"
                    logging.info(name)

                try:
                    rating = commentbox.div.div.div.div.text 

                except:
                    rating = "no rating"
                    logging.info(rating)

                try:
                    commentHead = commentbox.div.div.div.p.text 

                except:

                    commentHead = "no comment heading"
                    logging.info(commentHead)

                try:
                    comtag = commentbox.div.div.find_all("div",{"class":''})
                    custComment =  comtag[0].div.text 

                except Exception as e:
                    logging.info(e) 

                mydict = {"Product":searchstring,"Name":name,"Rating":rating,"CommentHead":commentHead,"Comment":custComment}
                reviews.append(mydict)
            logging.info("log my final result {}".format(reviews))    

            return render_template('result.html',reviews = reviews[0:(len(reviews)-1)] )
        except Exception as e:
            logging.info(e)
            return 'something is wrong'
            

    else:
        return render_template('index.html')        


if __name__=="__main__":
    app.run(host="0.0.0.0",port = 5000)
