from flask import Flask,render_template,redirect,request,url_for,jsonify
from flask_fontawesome import FontAwesome
from flask_sqlalchemy import SQLAlchemy
import os, json
from ebaysdk.finding import Connection as finding
import time
import ssl
context = ssl.SSLContext()
context.load_cert_chain('cert.pem', 'key.pem')

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///"+os.path.join(app.root_path
,'todos.db')

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False

#print(os.path.join(app.root_path,'todos.db'))

db=SQLAlchemy(app)


"""
Task
- id :int
- name : str
- complete :bool
"""

class Task(db.Model):
    __tablename__ = "task"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String,nullable=False)
    complete=db.Column(db.Integer,default=0)

    def __repr__(self):
        return f'<Task {self.name}>'

class Producto(db.Model):
    __tablename__ = "producto"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String,nullable=False)
    asin=db.Column(db.String(10))
    epid=db.Column(db.String(10))
    am_price = db.Column(db.Float)
    eb_price = db.Column(db.Float)
    img_url = db.Column(db.String)
    def __repr__(self):
        return f'<Producto {self.name}>'

def prod2json(products):
    prod = []
    for product in products:
        temp = {
            'id': str(product.id),
            'name': product.name,
            'asin': product.asin,
            'epid': product.epid,
            'price': {
                'amazon':str(product.am_price),
                'ebay':	str(product.eb_price)
                },
            'img_url': str(product.img_url),
            'same_price': str(product.am_price) == str(product.eb_price)
        }
        prod.append(temp)

    return list(prod)

@app.route('/')
def index():

    tasks=Task.query.order_by(Task.id.desc()).all()
    complete_tasks=Task.query.filter_by(complete=1).count()
    return render_template('productos.html',tasks=tasks,complete_tasks=complete_tasks)

@app.route('/api/products')
def Api():
    products=Producto.query.order_by(Producto.id.desc()).all()
    return prod2json(products)
    #complete_tasks=Task.query.filter_by(complete=1).count()

@app.route('/products')
def Prod():
    product=Producto.query.order_by(Producto.id.desc()).all()
    return render_template('producto.html',products=prod2json(product))

@app.route('/p')
def index2():

    tasks=Task.query.order_by(Task.id.desc()).all()
    complete_tasks=Task.query.filter_by(complete=1).count()
    return render_template('base2.html',tasks=tasks,complete_tasks=complete_tasks)


@app.route('/api/amazon')
def search_in_amazon():
    api_url = "https://api.business.amazon.com/products/2020-08-26/products?keywords=pc"

@app.route('/api/ebay/<keywords>')
def search_in_ebay(keywords):
    api = finding(appid = "JorgeCas-12345-SBX-bca7a963e-56b9795b", siteid="EBAY-DE", config_file=None) # change country with "siteid="
    api_request = { "keywords": keywords, "outputSelector" : "SellerInfo"}
    response = api.execute("findItemsByKeywords", api_request)
    # time.sleep(3)
    soup = BeautifulSoup(response.content, "lxml")
    items = soup.find_all("item")
    for item in items:
         title = item.title.string.lower().strip()
         price = item.currentprice.string
         url = item.viewitemurl.string.lower()
         if item.conditiondisplayname:
            condition = item.conditiondisplayname.string.lower()
         else:
            condition = "n/a"    
         print(title,"\t",condition,"\t",price)
    

    
@app.route('/add',methods=["POST"])
def create_task():
    task=request.form.get('task')

    new_task=Task(name=task)
    db.session.add(new_task)
    db.session.commit()

    return redirect('/')


@app.route('/complete/<int:id>/')
def complete_task(id):

    task_to_update=Task.query.get(id)
    task_to_update.complete=1
    db.session.commit()

    return redirect('/')


@app.route('/delete/<int:id>/')
def delete_task(id):
    task_to_delete=Task.query.get(id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True,host='127.0.0.1', port=5001, ssl_context=context)
    
# @app.before_first_request
# def create_tables():
#     db.create_all()