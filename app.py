import io
import os
import secrets
import pandas as pd
import random

from flask import (
    Flask,
    Response,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
    jsonify
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import func
from flask_migrate import Migrate  # Import Flask-Migrate
from flask_cors import CORS

from wtforms import (
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    ValidationError,
    validators,
)
from wtforms.validators import DataRequired

from flask_sslify import SSLify  # Use SSLify to enable HTTPS

# from faker import Faker

# ==============================================================================
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///registrations.db'
db = SQLAlchemy(app)
app.secret_key = secrets.token_hex(16)  # Generates a 32-character (16 bytes) hexadecimal key
migrate = Migrate(app, db)  # Initialize Flask-Migrate

# fake = Faker()
CORS(app)
sslify = SSLify(app)  # Enable SSL/TLS

# ==============================================================================
# ''' Models '''
# ==============================================================================

# Define the Registration model for the database table
class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone_number = db.Column(db.Text, unique=True)
    first_name = db.Column(db.Text)
    family_name = db.Column(db.Text)
    father_name = db.Column(db.Text)
    first_grand_name = db.Column(db.Text)
    second_grand_name = db.Column(db.Text)
    third_grand_name = db.Column(db.Text)
    relation = db.Column(db.Text)
    age = db.Column(db.Text)
    gender = db.Column(db.Text)
    city = db.Column(db.Text)
    attendance = db.Column(db.Text)
    ideas = db.Column(db.Text)
    registration_number = db.Column(db.Text)
    prize_id = db.Column(db.Integer, db.ForeignKey('prize.id'))


# Define the Prize model
class Prize(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    guest_registration_number = db.Column(db.String(3), unique=True)

    def __init__(self, name, description=None, guest_registration_number=None):
        self.name = name
        self.description = description
        self.guest_registration_number = guest_registration_number

# ==============================================================================
#   ''' Database and Tables '''
# ==============================================================================

# Create the database and tables if they don't exist
with app.app_context():
    db.create_all()

    # Loop to create 50 fake records
    # for _ in range(50):
    #     record = Registration(
    #         phone_number=fake.phone_number(),
    #         first_name=fake.first_name(),
    #         family_name=fake.last_name(),
    #         father_name=fake.last_name(),
    #         first_grand_name=fake.last_name(),
    #         second_grand_name=fake.last_name(),
    #         third_grand_name=fake.last_name(),
    #         relation=fake.word(),
    #         age=str(fake.random_int(18, 80)),  # Assuming age between 18 and 80
    #         gender=fake.random_element(["Male", "Female"]),
    #         city=fake.city(),
    #         attendance=fake.random_element(["Yes", "No"]),
    #         ideas=fake.text(),
    #         registration_number=str(fake.random_int(100, 999))  # Unique 3-digit registration number
    #         # Add prize_id if needed
    #     )
    #     db.session.add(record)

    # Commit the changes
    db.session.commit()

# ==============================================================================
# ''' Forms '''
# ==============================================================================

def validate_non_family_name(form, field):
  if form.family_name.data == 'أخرى' and not field.data:
      raise ValidationError('من فضلك أدخل البيان المطلوب')

# Model for the registration form
class RegistrationForm(FlaskForm):
    phone_number = StringField('رقم الهاتف الجوال', validators=[validators.DataRequired()])
    first_name = StringField('إسمك الأول', validators=[validators.InputRequired()])
    family_name = SelectField('إسم العائلة', choices=[('السديس', 'السديس'), ('أخرى', 'أخرى')], validators=[validators.InputRequired()])
    custom_family_name = StringField('إسم العائلة غير أسرة السديس', validators=[validate_non_family_name])
    relation = StringField('إن لم تكن من أسرة السديس فلطفاً حدد نوع العلاقة', validators=[validate_non_family_name])
    father_name = StringField('إسم الأب', validators=[validators.InputRequired()])
    first_grand_name = StringField('إسم الجد الأول', validators=[validators.InputRequired()])
    second_grand_name = StringField('إسم الجد الثاني', validators=[validators.InputRequired()])
    third_grand_name = StringField('إسم الجد الثالث/فرع الأسرة', validators=[validators.InputRequired()])
    age = SelectField('ماهي فئتك العمرية', choices=[('أقل من 19 سنة', 'أقل من 19 سنة'), ('من 20 سنة حتى 50 سنة', 'من 20 سنة حتى 50 سنة'), ('أعلى من 50 سنة', 'أعلى من 50 سنة')], validators=[validators.InputRequired()])
    gender = SelectField('الجنس', choices=[('ذكر', 'ذكر'), ('أنثى', 'أنثى')], validators=[validators.InputRequired()])
    city = StringField('مدينة العنوان الدائم لك', validators=[validators.InputRequired()])
    attendance = SelectField('هل ستحضر اللقاء', choices=[('سوف أحضر باذن الله', 'سوف أحضر باذن الله'), ('أعتذر عن الحضور', 'أعتذر عن الحضور')], validators=[validators.InputRequired()])
    ideas = TextAreaField ('هل لديك مشاركة أو فكرة تود تقديمها في الحفل ؟ نسعد بمعرفة ذلك')
    submit = SubmitField('تسجيل')


# Form for adding a new prize
class AddPrizeForm(FlaskForm):
    name = StringField('إسم الهدية', validators=[DataRequired()])
    description = TextAreaField('الوصف')
    # guest_registration_number = StringField('Guest Registration Number', validators=[DataRequired()])


# Form for editing an existing prize
class EditPrizeForm(FlaskForm):
    name = StringField('إسم الهدية', validators=[DataRequired()])
    description = TextAreaField('الوصف')
    # guest_registration_number = StringField('Guest Registration Number', validators=[DataRequired()])

# ==============================================================================
# ''' Helper Functions '''
# ==============================================================================

# Helper function to generate a unique registration number
def generate_registration_number():
    import random
    return str(random.randint(100, 999))


def is_registered(phone_number):
    return Registration.query.filter_by(phone_number=phone_number).first() is not None


def get_user_data(phone_number):
  if not phone_number:
    users = Registration.query.all()
    users_data=[]
    for user in users:
      user_data = {
            'phone_number': user.phone_number,
            'first_name': user.first_name,
            'family_name': user.family_name,
            'father_name': user.father_name,
            'first_grand_name': user.first_grand_name,
            'second_grand_name': user.second_grand_name,
            'third_grand_name': user.third_grand_name,
            'relation': user.relation,
            'age': user.age,
            'gender': user.gender,
            'city': user.city,
            'attendance': user.attendance,
            'ideas': user.ideas,
            'registration_number': user.registration_number
        }
      users_data.append(user_data)
    return users_data
  else:
    user=Registration.query.filter_by(phone_number=phone_number).first()
    if user:
      return {
          'phone_number': user.phone_number,
          'first_name': user.first_name,
          'family_name': user.family_name,
          'father_name': user.father_name,
          'first_grand_name': user.first_grand_name,
          'second_grand_name': user.second_grand_name,
          'third_grand_name': user.third_grand_name,
          'relation': user.relation,
          'age': user.age,
          'gender': user.gender,
          'city': user.city,
          'attendance': user.attendance,
          'ideas': user.ideas,
          'registration_number': user.registration_number
      }
    else:
      return {}


def create_image(content):
    # Create an image with a white background
    width, height = 800, 600  # Set the image size as needed
    image = Image.new('RGB', (width, height), color='white')
    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Define additional styles (e.g., colors)
    text_color = 'black'
    background_color = 'white'
    top_stripe_color = (8, 94, 157)
    bottom_stripe_color=(88, 88, 86)
    font_size = 36

    static_dir = os.path.join(os.path.dirname(__file__), "static")
    font_file_path = os.path.join(static_dir, "fonts", "Cairo-Bold.ttf")
    # Set the font and font size (you may need to download and specify an Arabic font)
    font = ImageFont.truetype(font_file_path, size=font_size)

    # Split content into lines
    lines = content.split('\n')

    # Calculate the total height of all lines
    total_height = len(lines) * font_size

    # Calculate the vertical position (centered)
    y = (height - total_height) // 2

    # Draw a background rectangle with a specified color
    draw.rectangle([0, 0, width, height], fill=background_color)

    # Draw the horizontal stripe at the top of the image
    draw.rectangle([0, 0, width, 15], fill=top_stripe_color)
    draw.rectangle([0, height - 15, width, height], fill=bottom_stripe_color)

    # Draw each line with specified styles, centered horizontally
    idx=0
    for line in lines:
        idx+=1
        print(f'Line no. ({idx}): ', line)
        print('BBox: ', font.getmask(line).getbbox())
        if idx == 8: break
        if not line or line.isspace() or line == '\n' or line == '\r' or line == '\r\n' or line == '\n\r':
            continue
        text_color = 'red' if idx in (3,5,7) else 'black'
        left, top, right, bottom = font.getmask(line).getbbox()
        text_width, text_height = right - left, bottom - top
        x = (width - text_width) // 2  # Calculate horizontal position for center alignment
        draw.text((x, y), line, fill=text_color, font=font)
        y += font_size+20  # Adjust vertical position for the next line


    # # Set the position to start drawing
    # x, y = 10, 10
    # # Draw the content onto the image
    # draw.text((x, y), content, fill='black', font=font)
    return image


# ==============================================================================
# ''' Routes '''
# ==============================================================================

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    form = RegistrationForm()  # Create an instance of the RegistrationForm
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        if not is_registered(phone_number):
            return redirect(url_for('register', phone_number=phone_number))
            # return render_template('register.html', phone_number=phone_number, form=form)
        # user_data = get_user_data(phone_number)
        return redirect(url_for('registered', phone_number=phone_number))
        # return render_template('registered.html', phone_number=phone_number)
    return render_template('index.html', form=form)  # Pass the form instance to the template


# Route for the admin page
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Number of logs per page

    guests=Registration.query.paginate(page=page, per_page=per_page)
    return render_template('admin.html', guests=guests)


# Delete Guest
@app.route('/delete_guest/<string:guest_phoneno>', methods=['GET', 'POST'])
def delete_guest(guest_phoneno):
    try:
        guest = Registration.query.filter_by(phone_number=guest_phoneno).first()
        db.session.delete(guest)
        db.session.commit()
        flash('تم حذف بيانات الضيف بنجاح', 'success')
        return redirect(url_for('admin'))
    except:
        flash('فشلت عملية الحذف', 'danger')
        return redirect(url_for('admin'))
  

# Route for the registration form
@app.route('/register/<phone_number>', methods=['POST', 'GET'])
def register(phone_number):
    existing_registration = Registration.query.filter_by(phone_number=phone_number).first()
    # Create the form instance and load data if it exists
    form = RegistrationForm(obj=existing_registration)
    form.phone_number.data = phone_number
    if existing_registration:
        if existing_registration.family_name not in ('أخرى','السديس'):
            form.custom_family_name.data = existing_registration.family_name
            form.family_name.data = 'أخرى'
    if request.method == 'POST':
        if form.validate_on_submit():
            if existing_registration:
                # Update the existing registration with form data
                form.populate_obj(existing_registration)
                db.session.commit()
            else:
                new_registration = Registration()
                form.populate_obj(new_registration)
                if form.family_name.data == 'أخرى':
                    new_registration.family_name = form.custom_family_name.data
                else:
                    new_registration.family_name = form.family_name.data
                new_registration.phone_number = phone_number
                new_registration.registration_number = generate_registration_number()
                db.session.add(new_registration)
                db.session.commit()
                flash('تم التسجيل بنجاح', 'success')
            # Redirect to a success page or the landing page
            return redirect(url_for('registered', phone_number=phone_number))
        else:
            # Handle errors
            flash('حدث خطأ ما', 'error')
            flash(form.errors, 'error')
            return render_template('register.html', phone_number=phone_number, form=form, keep=True)
    return render_template('register.html', phone_number=phone_number, form=form, keep= bool(form.custom_family_name.data))


@app.route('/registered/<phone_number>', methods=['POST', 'GET'])
def registered(phone_number):
    user_data = get_user_data(phone_number)
    if user_data:
        return render_template('registered.html', user_data=user_data)
    else:
        flash('رقم الجوال غير مسجل من قبل', 'error')
        return redirect(url_for('index'))


@app.route('/delete/<phone_number>', methods=['GET'])
def delete(phone_number):
    try:
        existing_registration = Registration.query.filter_by(phone_number=phone_number).first()
        db.session.delete(existing_registration)
        db.session.commit()
        flash('تم حذف البيانات بنجاح', 'success')
        return redirect(url_for('index'))
    except:
        flash('فشلت محاولة حذف البيانات', 'danger')
        return redirect(url_for('registered', phone_number=phone_number))


@app.route('/convert_to_image', methods=['POST'])
def convert_to_image():
    # Get the content from the request (e.g., JSON or form data)
    content = request.form['content']
    # Create an image with the content
    image = create_image(content)
    # Save the image to a byte stream
    image_stream = io.BytesIO()
    image.save(image_stream, format='PNG')
    image_stream.seek(0)
    # Return the image as a response
    return Response(image_stream, content_type='image/png')


@app.route('/export_to_excel')
def export_to_excel():
    items = get_user_data(None)
    if not items:
        return None

    df = pd.DataFrame(items)
    excel_file_path = 'registeration.xlsx'
    df.to_excel(excel_file_path, index=False)
    return send_file(excel_file_path, as_attachment=True)
 

# Route for the home page
@app.route('/qr', methods=['GET', 'POST'])
def qr():
    return render_template('qr_scanner.html')

# ------------------------------------------------------------------------------
# ''' Prizes Routes '''
# ------------------------------------------------------------------------------

# Create route for displaying a list of prizes
@app.route('/prizes', methods=['GET'])
def list_prizes():
    prizes = Prize.query.all()
    return render_template('prizes.html', prizes=prizes)

# Create route for adding a new prize
@app.route('/prizes/add', methods=['GET', 'POST'])
def add_prize():
    form = AddPrizeForm()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        prize = Prize(name=name, description=description)
        db.session.add(prize)
        db.session.commit()

        flash('Prize added successfully!', 'success')
        return redirect(url_for('list_prizes'))

    return render_template('add_prize.html',form=form)

# Create route for editing a prize
@app.route('/prizes/edit/<int:id>', methods=['GET', 'POST'])
def edit_prize(id):
    prize = Prize.query.get(id)
    form = EditPrizeForm(obj=prize)

    if request.method == 'POST':
        prize.name = request.form['name']
        prize.description = request.form['description']
        db.session.commit()

        flash('Prize updated successfully!', 'success')
        return redirect(url_for('list_prizes'))

    return render_template('edit_prize.html',form=form, prize=prize)

# Create route for deleting a prize
@app.route('/prizes/delete/<int:id>', methods=['POST'])
def delete_prize(id):
    prize = Prize.query.get(id)
    db.session.delete(prize)
    db.session.commit()

    flash('Prize deleted successfully!', 'success')
    return redirect(url_for('list_prizes'))

# Route to withdraw a prize
@app.route('/withdraw_prize', methods=['GET', 'POST'])
def withdraw_prize():
    # Logic to select a random registration number
    if request.method == 'POST':
        return render_template('withdraw_prize.html')
    return render_template('withdraw_prize.html')

# Route to get random registration number
@app.route('/shuffle_numbers', methods=['GET'])
def shuffle_numbers():
    rnd_reg_no_text='000'

    # Fetch all registration numbers not associated with a prize
    registrations_without_prize = Registration.query.filter_by(prize_id=None).all()

    # If there are registrations without a prize
    if registrations_without_prize:
        # Randomly select one registration number
        selected_registration = random.choice(registrations_without_prize)
        rnd_reg_no= selected_registration.registration_number
    else:
        rnd_reg_no=0
    
    rnd_reg_no_text=str(rnd_reg_no).zfill(3)
    # Return a response (if needed)
    return jsonify({'message': f'{rnd_reg_no_text}'})
# ==============================================================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    # app.run(host='0.0.0.0',ssl_context=('cert.pem', 'key.pem'), debug=True)
