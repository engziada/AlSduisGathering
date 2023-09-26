from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, validators, ValidationError
import secrets
from flask_sqlalchemy import SQLAlchemy
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///registrations.db'
db = SQLAlchemy(app)
# app.config['DATABASE'] = 'database.db'
app.secret_key = secrets.token_hex(16)  # Generates a 32-character (16 bytes) hexadecimal key



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

# Create the database and tables if they don't exist
with app.app_context():
    db.create_all()


# ==============================================================================
# ''' Forms '''
# ==============================================================================

def validate_non_family_name(form, field):
  if form.family_name.data == 'أخرى':
    if not field.data:
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
    # Fetch user data based on the phone number from the database
    user = Registration.query.filter_by(phone_number=phone_number).first()
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

    # Set the font and font size (you may need to download and specify an Arabic font)
    font = ImageFont.truetype('\\static\\fonts\\Cairo-Bold.ttf', size=font_size)

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


# Route for the registration form
@app.route('/register/<phone_number>', methods=['POST', 'GET'])
def register(phone_number):
    existing_registration = Registration.query.filter_by(phone_number=phone_number).first()
    # Create the form instance and load data if it exists
    form = RegistrationForm(obj=existing_registration)
    form.phone_number.data = phone_number
    if existing_registration:
        if existing_registration.family_name not in ('أخرى','السديس'):
            keep=True
            form.custom_family_name.data = existing_registration.family_name
            form.family_name.data = 'أخرى'
    if request.method == 'POST':
        if form.validate_on_submit():
            if existing_registration:
                # Update the existing registration with form data
                form.populate_obj(existing_registration)
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
            # Add the new registration to the database
            db.session.add(new_registration)
            db.session.commit()
            # Flash a success message
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


# ==============================================================================
if __name__ == '__main__':
    app.run(debug=True)
