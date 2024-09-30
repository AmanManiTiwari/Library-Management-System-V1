from flask import Flask,render_template,request,redirect,url_for,flash,session,jsonify
from flask_restful import Resource,Api,reqparse,fields,marshal_with,abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

app=Flask(__name__,template_folder='templates',static_folder='static')

app.config['SECRET_KEY']='123456789'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']='false'


db=SQLAlchemy(app)


# =====================================models
class User(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    email=db.Column(db.String(),nullable=False,unique=True)
    password=db.Column(db.String(),nullable=False)
    name=db.Column(db.String(),nullable=False)
    is_librarian=db.Column(db.Boolean,nullable=False,default=False)

    users=db.relationship('Issue',backref='User',lazy=True)
    user_request=db.relationship('Request',backref='User',lazy=True)

class Section(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    name=db.Column(db.String(),nullable=False,unique=True)
    date=db.Column(db.String(), nullable = False)
    books=db.relationship('Book',backref='Section',lazy=True,cascade='all, delete-orphan')


class Book(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    name=db.Column(db.String(),nullable=False,unique=True)
    author_name=db.Column(db.String(),nullable=False)
    date=db.Column(db.String(), nullable = False)
    content=db.Column(db.String(),nullable=False)
    section_id=db.Column(db.Integer, db.ForeignKey('section.id'),nullable=False)

    books=db.relationship('Issue',backref='Book',lazy=True,cascade='all, delete-orphan')

class Issue(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id=db.Column(db.Integer(),db.ForeignKey('user.id'),nullable=False)
    book_id=db.Column(db.Integer(),db.ForeignKey('book.id'),nullable=False)

class Request(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id=db.Column(db.Integer(),db.ForeignKey('user.id'),nullable=False)
    book_id=db.Column(db.Integer(),db.ForeignKey('book.id'),nullable=False)

class Feedback(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id=db.Column(db.Integer(),db.ForeignKey('user.id'),nullable=False)
    book_id=db.Column(db.Integer(),db.ForeignKey('book.id'),nullable=False)
    content=db.Column(db.String(),nullable=False)

with app.app_context():
    db.create_all()

    # it will create librarian by default
    librarian=User.query.filter_by (is_librarian=True).first()
    if not librarian:
        librarian=User(email='admin@gmailcom',password='0',name='Librarian',is_librarian=True)
        db.session.add(librarian)
        db.session.commit()


# ===========================routes
        
def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' in session:
            return func(*args, **kwargs)
        else:
            flash('Please login to continue')
            return redirect(url_for('login'))
    return inner

def librarian_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue')
            return redirect(url_for('userlogin'))
        user = User.query.get(session['user_id'])
        if not user.is_librarian:
            flash('You are not authorized to access this page')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return inner

                                                   

@app.route('/userlogin',methods=['GET','POST'])                       #login
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        name=request.form.get('name')

        if not email or not password or not name:
            flash("Please fill out all fields")
            return redirect(url_for('login'))
            
        user=User.query.filter_by(email=email).first()
        if not user:
            flash("User not found")
            return redirect(url_for('login'))
            
        if user.password!=password:
            flash("Please enter correct password")
            return redirect(url_for('login'))
            
        if user.is_librarian==True: #checking user is admin or not 
            session['user_id']=user.id
            flash('Login Successfully')
            return redirect(url_for('adminDashboard'))
        
        session['user_id']=user.id
        flash('Login Successfully')
        return redirect(url_for('index'))
    

    return render_template('userLogin.html')

#################################################################################
                         
                                                       

@app.route('/userregister',methods=['GET','POST'])                          #register
def register():
    if request.method=='POST':
        name=request.form.get('name')
        email=request.form.get('email')
        password=request.form.get('password')

        if not name or not email or not password:
            flash("Please fill out all fields")
            return redirect(url_for('register'))
        else:
            user=User.query.filter_by(email=email).first()
            if user:
                return redirect(url_for('register'))
            else:
                newUser=User(email=email,password=password,name=name)
                db.session.add(newUser)
                db.session.commit()
                return redirect(url_for('login'))
    return render_template('userRegister.html')


# ??????????????????????????????????????????????????????????????????????????
                                                        


@app.route('/userlogout')                                            #logout
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))



#############################################################################

                                                              

@app.route('/admin')                                                #admin
@librarian_required
def adminDashboard():
    sections=Section.query.all()
    return render_template('admin.html',sections=sections)

                                                #crud on section

@app.route('/section/add',methods=['GET','POST'])                   #add section
@librarian_required
def addSection():
    todaysDate = datetime.now().strftime('%Y-%m-%d')
    if request.method=='POST':
        name = request.form.get('name')
        date = request.form.get('date')

        if not name or not date:
            flash('Please fill out all fields')
            return redirect(url_for('addSection'))
        else:
            section=Section.query.filter_by(name=name).first()
            if section:
                flash('Section already exist')
                return redirect(url_for('addSection'))
            else:

                addsection =Section(name=name,date=date)
                db.session.add(addsection)
                db.session.commit()
        
                flash('Section added successfully')
                return redirect(url_for('adminDashboard'))
    
    return render_template('/section/addSection.html',todaysDate=todaysDate)


@app.route('/section/<int:id>/')                                         #view section
@librarian_required
def viewSection(id):
    section = Section.query.get(id)
    if not section:
        flash('Section does not exist')
        return redirect(url_for('adminDashboard'))
    else:
        return render_template('section/viewSection.html',section=section)

@app.route('/section/<int:id>/update',methods=['GET','POST'])                #update section
@librarian_required
def updateSection(id):
    section = Section.query.get(id)
    if request.method=='POST':
        
        if not section:
            flash('Section does not exist')
            return redirect(url_for('admin'))
        else:
            name = request.form.get('name')
            date= request.form.get('date')
            if not name:
                flash('Please fill out all fields')
                return redirect(url_for('updateSection', id=id))
            section.name = name
            section.date=date
            db.session.commit()
            flash('Section updated successfully')
            return redirect(url_for('adminDashboard'))

    else:
        if not  section:
            flash(' Section does not exist')
            return redirect(url_for('adminDashboard'))
        return render_template('section/updateSection.html',section=section)


@app.route('/section/<int:id>/delete',methods=['GET','POST'])                        #delete section
@librarian_required
def deleteSection(id):
     section = Section.query.get(id)
     if request.method=='POST':
         
         if not section:
            flash('Section does not exist')
            return redirect(url_for('adminDashboard'))
         else:
            
            db.session.delete(section)
            db.session.commit()
            flash('Section deleted successfully')
            return redirect(url_for('adminDashboard'))
     else:
         if not section:
            flash('Section does not exist')
            return redirect(url_for('adminDashboard'))
         return render_template('section/deleteSection.html', section=section)


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
                                                            #Book crud
     
@app.route('/book/add/<int:section_id>',methods=['GET','POST'])                #add book
@librarian_required
def addBook(section_id):
    todaysDate = datetime.now().strftime('%Y-%m-%d')
    sections=Section.query.all()
    section = Section.query.get(section_id)
    if not section:
            flash('Section does not exist')
            return redirect(url_for('adminDashboard'))
    else:
        if request.method=='POST':
            name = request.form.get('name')
            author_name=request.form.get('author_name')
            date = request.form.get('date')
            section_id=request.form.get('section_id')
            content=request.form.get('content')

        
            if not name or not author_name or not date or not section_id:
                flash('Please fill out all fields')
                return redirect(url_for('addBook'))
            else:
                
                book=Book.query.filter_by(name=name).first()
                if book:
                    flash('Book name already exist')
                    return redirect(url_for('addBook'))
                else:

                    addbook =Book(name=name,author_name=author_name,date=date, section_id= section_id,content=content)
                    db.session.add(addbook)
                    db.session.commit()
                    
                    flash('Book added successfully')
                    return redirect(url_for('viewSection',id=section_id))
    
        return render_template('/book/addBook.html',section=section ,sections=sections,todaysDate=todaysDate)


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

@app.route('/book/<int:id>/update',methods=['GET','POST'])                      #update book
@librarian_required
def updateBook(id):
    sections=Section.query.all()
    book = Book.query.get(id)
    if request.method=='POST':
        name = request.form.get('name')
        author_name=request.form.get('author_name')
        date = request.form.get('date')
        section_id=request.form.get('section_id')
        
        section = Section.query.get(section_id)
        if not section:
            flash('Section does not exist')
            return redirect(url_for('adminDashboard'))
        else:
            if not name or not author_name or not date or not section_id:
                flash('Please fill out all fields')
                return redirect(url_for('updateBook'))
            else:
                book.name=name
                book.author_name=author_name
                book.date=date
                book.section_id=section_id
                db.session.commit()

                flash('Book edited successfully')
                return redirect(url_for('viewSection', id=section_id))
    return render_template('book/updateBook.html', sections=sections,book=book)

@app.route('/book/<int:id>/delete',methods=['GET','POST'])                        #delete book
@librarian_required
def deleteBook(id):
    book = Book.query.get(id)
    if not book:
        flash('Book does not exist')
        return redirect(url_for('adminDashboard'))
    else:
        if request.method=='POST':
            section_id = book.section_id
            db.session.delete(book)
            db.session.commit()

            flash('Book deleted successfully')
            return redirect(url_for('viewSection', id=section_id))
        return render_template('book/deleteBook.html', book=book)
    
@app.route('/bookrequest')                                      #rendering book request page
@librarian_required
def bookRequested():
   requests=Request.query.all()
   return render_template('bookRequest.html',requests=requests)

@app.route('/reject/<int:id>')                                   #rejecting a book request
@librarian_required
def rejectRequest(id):
    request=Request.query.get(id)
    db.session.delete(request)
    db.session.commit()
    requests=Request.query.all()
    flash('Book Request Rejected Successfully')
    return render_template('bookRequest.html',requests=requests)

@app.route('/accept/<int:id>')                              #accepting a book request
def acceptRequest(id):
    request=Request.query.get(id)
    issue=Issue(user_id=request.user_id,book_id=request.book_id)
    db.session.delete(request)
    db.session.commit()
    db.session.add(issue)
    db.session.commit()
    requests=Request.query.all()
    flash('Book Request Acepted Successfully')
    return render_template('bookRequest.html',requests=requests)

@app.route('/bookstatus')                             #showing all book issued      
@librarian_required
def bookStatus():
   books=Book.query.all()
   issues=Issue.query.all()
   return render_template('revokeBook.html',books=books,issues=issues)

@app.route('/revoke/<int:id>')                         #revoking book
@librarian_required
def revokeBook(id):
    issue=Issue.query.get(id)
    db.session.delete(issue)
    db.session.commit()

    books = Book.query.all()
    issues=Issue.query.all()
    flash('Book Revoked Successfully')
    return render_template('revokeBook.html',books=books,issues=issues)

@app.route('/stats')
@librarian_required
def stats():
    books=Book.query.all()
    sections=Section.query.all()
    issues=Issue.query.all()
    requests=Request.query.all()
    categories = ['Sections','Books',  'Books Requested', 'Books Issued']
    counts = [len(sections), len(books), len(requests),len(issues)]
    plt.clf()
    plt.bar(categories, counts, color='skyblue')
    plt.savefig('static/img1.png')
    plt.xlabel('Categories')
    plt.ylabel('Count')
    plt.title('Summary')

    return render_template('stats.html',books=books,sections=sections,issues=issues,requests=requests)
# ========================================================================================?

                                            #user

@app.route('/')                                              #user dashboard
@login_required
def index():
    user = User.query.get(session['user_id'])
    if user.is_librarian:
        return redirect(url_for('adminDashboard'))
    else:
        sections = Section.query.all()
        books=Book.query.all()
        sectionName = request.args.get('search') or ''
        authorName = request.args.get('search') or ''
        if sectionName:
            sections = Section.query.filter(Section.name.ilike(f'%{sectionName}%')).all()
            if sections==[]:
                sectionName=''
                sections = Section.query.all()
        if authorName:
            books = Book.query.filter(Book.author_name.ilike(f'%{authorName}%')).all()
            if books==[]:
                authorName=''
                books=Book.query.all()
        return render_template('userDashboard.html',sections=sections,user=user,sectionName=sectionName,authorName=authorName,books=books)
        

@app.route('/request/<int:id>')                               #requesting a book
@login_required
def requestBook(id):
    user = User.query.get(session['user_id'])
    book=Book.query.filter_by(id=id).first()
    prev_request=Request.query.filter_by(user_id=user.id).count()
    if prev_request>4:
        flash('You can request max 5 books at a time')
        sections = Section.query.all()
        return render_template('userDashboard.html',sections=sections,userName=user.name)
    else:
        request=Request(user_id=user.id,book_id=book.id)
        db.session.add(request)
        db.session.commit()
        flash('Book requested successfully')
        sections = Section.query.all()
        return render_template('userDashboard.html',sections=sections,userName=user.name)

        
@app.route('/issued')                                    #showing issued book
@login_required
def issuedbook():
    books = Book.query.all()
    user = User.query.get(session['user_id'])
    issues=Issue.query.filter_by(user_id=user.id).all()
    return render_template('issuedBook.html',books=books,issues=issues,user=user)


@app.route('/return/<int:id>')                            #returning book
@login_required
def returnBook(id):
    issue=Issue.query.get(id)
    db.session.delete(issue)
    db.session.commit()
    
    books = Book.query.all()
    user = User.query.get(session['user_id'])
    issues=Issue.query.filter_by(user_id=user.id).all()
    flash('Book Returned Successfully')
    return render_template('issuedBook.html',books=books,issues=issues)

@app.route('/buy/<int:id>')
@login_required
def buyBook(id):
    book=Book.query.get(id)
    buffer = io.BytesIO()
    pdfFilename = f"{book.name}.pdf"
    content = canvas.Canvas(pdfFilename, pagesize=letter)
    content.drawString(100, 750, book.content)
    content.showPage()
    content.save()
    buffer.seek(0)
    return buffer

@app.route('/feedback/<int:id>')
@login_required
def feedback(id):
    user = User.query.get(session['user_id'])
    return render_template('feedback.html',user_id=user.id,book_id=id)

@app.route('/submitFeedback',methods=['POST'])
@login_required
def submitFeedback():
    user_id=request.form.get('user_id')
    book_id=request.form.get('book_id')
    content=request.form.get('content')
    if not user_id or not book_id or not content:
        flash('Please fill out all details')
        return render_template('feedback.html',user_id=user_id,book_id=book_id)
    feedback=Feedback( user_id= user_id,book_id=book_id,content=content)
    db.session.add(feedback)
    db.session.commit()
    flash('Send feedback successfully')
    return redirect(url_for('issuedbook'))



###############################################################################################################
                                                   #api endpints

api=Api(app) 

parser = reqparse.RequestParser()
parser.add_argument("name")
parser.add_argument("date")

update_parser= reqparse.RequestParser()
update_parser.add_argument("name")
update_parser.add_argument("date")

resource_fields={
    'id': fields.Integer,
    'name': fields.String,
    'date': fields.String
}

class AllsectionApi(Resource):             # to view all section
    @marshal_with(resource_fields)
    def get(self):
        sections = Section.query.all()
        return sections, 200
api.add_resource(AllsectionApi,'/api')


class SectionApi(Resource):
    @marshal_with(resource_fields)
    def get(self,section_id):                                    # to view particular section with section_id
        section = Section.query.filter_by(id=section_id).first()
        if not section:
            abort(404, message=f"Section with ID {section_id} not found")
        return section, 200

    
    def delete(self,section_id):                                    # to delete particular section with section_id
        section=Section.query.filter_by(id=section_id).first()
        if not section:
            abort(404, message=f"Section with ID {section_id} not found")
        db.session.delete(section)
        db.session.commit()
        return "Section Deleted", 204
    
    @marshal_with(resource_fields)
    def put(self,section_id):                  # to update existing section
        args=update_parser.parse_args()
        section=Section.query.filter_by(id=section_id).first()
        if not section:
            abort(404, message=f"Section with ID {section_id} not found")
        if args['name']:
            section.name=args['name']
        if args['date']:
            section.date=args['date']
        db.session.commit()
        return section


api.add_resource(SectionApi,'/api/<int:section_id>')

class AddsectionApi(Resource):
    def post(self):                        #to add new section
        section_data = parser.parse_args()
        new_section=Section(name=section_data["name"],date=section_data["date"])
        db.session.add(new_section)
        db.session.commit()
        return "section created succesfully", 201
    
    
api.add_resource(AddsectionApi,'/api/addSection')

book_parser = reqparse.RequestParser()
book_parser.add_argument("name")
book_parser.add_argument("author_name")
book_parser.add_argument("date")
book_parser.add_argument("content")

book_update_parser= reqparse.RequestParser()
book_update_parser.add_argument("name")
book_update_parser.add_argument("author_name")
book_update_parser.add_argument("date")
book_update_parser.add_argument("content")

book_fields={
    'id': fields.Integer,
    'name': fields.String,
    'author_name': fields.String,
    'date': fields.String,
    'content': fields.String
}
class AllbookApi(Resource):
    def get(self,section_id):                  # to view all book related to particular section with section_id
        books=Book.query.filter_by(section_id=section_id).all()
        if not books:
            abort(404,message=f"Could not find book with section_id: {section_id}")
        section_book=[]
        for book in books:
            book_details={}
            book_details["id"]=book.id
            book_details["name"]=book.name
            book_details["author_name"]=book.author_name
            book_details["date"]=book.date
            book_details["content"]=book.content
            section_book.append(book_details)
        return section_book
    
    def post(self,section_id):
        book_data = book_parser.parse_args()
        # book=Book.query.filter_by(name=book_data["name"],section_id=section_id).first()
        # if book:
        #     abort(409,message=f"book with same name exist in the section_id: {section_id}")
        new_book=Book(name=book_data["name"],author_name=book_data["author_name"],date=book_data["date"],content=book_data["content"],section_id=section_id)
       
        db.session.add(new_book)
        db.session.commit()
        return "book created succesfully", 201
        
api.add_resource(AllbookApi,'/api/<int:section_id>/book')


class BookApi(Resource):
    def get(self,section_id,book_id):
        book=Book.query.filter_by(section_id=section_id ,id=book_id).first()
        list=[]
        book_details={}
        book_details["id"]=book.id
        book_details["name"]=book.name
        book_details["author_name"]=book.author_name
        book_details["date"]=book.date
        book_details["content"]=book.content
        list.append(book_details)
        return list
    

    def delete(self,section_id,book_id):
        book=Book.query.filter_by(section_id=section_id ,id=book_id).first()
        if not book:
            abort(404, message=f"Book with ID {book_id} not found")
        db.session.delete(book)
        db.session.commit()
        return "Book Deleted", 204
    
    @marshal_with(book_fields)
    def put(self,section_id,book_id):
        args=book_update_parser.parse_args()
        book=Book.query.filter_by(section_id=section_id ,id=book_id).first()
        if not book:
            abort(404, message=f"Book with ID {book_id} not found")
        if args['name']:
            book.name=args['name']
        if args['author_name']:
            book.name=args['author_name']
        if args['date']:
            book.date=args['date']
        if args['content']:
            book.name=args['content']
        db.session.commit()
        return book
api.add_resource(BookApi,'/api/book/<int:section_id>/<int:book_id>')


    


# =============================================================================
if __name__=='__main__':
    app.run(debug=True)
    