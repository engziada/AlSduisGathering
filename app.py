import io
import os
import random
import secrets

import arabic_reshaper
import pandas as pd
import requests
from bidi.algorithm import get_display
from bs4 import BeautifulSoup
from flask import (
    Flask,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import and_, or_
from wtforms import (
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
    ValidationError,
    validators,
    widgets,
)
from wtforms.validators import DataRequired

# ==============================================================================

# Initialize Flask
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///registrations.db"
app.secret_key = secrets.token_hex(16)  

# Initialize Flask-SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

# Initialize Flask-CORS
CORS(app)

# Google spreadsheet details
SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRaFYu_tsagGZ16_B9ku1LurJxfe4JtN-6vW5a1_cAEEWkVsV7Wy9hm0lttiYTeBCnjOmnHJjTV6MNd/pubhtml'
GUESTS_SHEET_NAME = 'Sheet1'

# ==============================================================================
# ''' Models '''
# ==============================================================================


# Define the Registration model for the database table
class Registration(db.Model):
    __tablename__ = "registration"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone_number = db.Column(db.String(16), unique=True, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    family_name = db.Column(db.Text, nullable=False)
    father_name = db.Column(db.Text)
    first_grand_name = db.Column(db.Text)
    second_grand_name = db.Column(db.Text)
    third_grand_name = db.Column(db.Text)
    relation = db.Column(db.Text)
    age = db.Column(db.String(3))
    gender = db.Column(db.String(15))
    city = db.Column(db.Text)
    attendance = db.Column(db.Text, nullable=False)
    ideas = db.Column(db.Text)
    registration_number = db.Column(db.String(4), unique=True)
    prize_id = db.Column(db.Integer, db.ForeignKey("prize.id", name="fk_reg_prize_id"))
    is_attended = db.Column(db.Boolean, default=False)


# Define the Prize model
class Prize(db.Model):
    __tablename__ = "prize"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    guest_registration_number = db.Column(db.String(4))
    allowed_families = db.Column(db.String(100))
    allowed_age_range = db.Column(db.String(100))
    allowed_gender = db.Column(db.String(100))
    is_next = db.Column(db.Boolean, default=False)

    def __init__(
        self,
        name,
        description=None,
        guest_registration_number=None,
        allowed_families=None,
        allowed_age_range=None,
        allowed_gender=None,
        is_next=False,
    ):
        self.name = name
        self.description = description
        self.guest_registration_number = guest_registration_number
        self.allowed_families = allowed_families
        self.allowed_age_range = allowed_age_range
        self.allowed_gender = allowed_gender
        self.is_next = is_next


# ==============================================================================
#   ''' Database and Tables '''
# ==============================================================================

# Create the database and tables if they don't exist

# Initialize Flask-Faker
# from faker import Faker
# fake = Faker()

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
# ''' Helper Functions '''
# ==============================================================================

def validate_non_family_name(form, field):
    if form.family_name.data == "أخرى" and not field.data:
        raise ValidationError("من فضلك أدخل البيان المطلوب")

# Helper function to generate a unique registration number
def generate_registration_number():
    return str(random.randint(1000, 9999))


def is_registered(phone_number):
    return Registration.query.filter_by(phone_number=phone_number).first() is not None


def get_user_data(phone_number):
    if not phone_number:
        users = Registration.query.all()
        users_data = []
        for user in users:
            user_data = {
                "phone_number": user.phone_number,
                "first_name": user.first_name,
                "family_name": user.family_name,
                "father_name": user.father_name,
                "first_grand_name": user.first_grand_name,
                "second_grand_name": user.second_grand_name,
                "third_grand_name": user.third_grand_name,
                "relation": user.relation,
                "age": user.age,
                "gender": user.gender,
                "city": user.city,
                "attendance": user.attendance,
                "ideas": user.ideas,
                "registration_number": user.registration_number,
            }
            users_data.append(user_data)
        return users_data
    else:
        user = Registration.query.filter_by(phone_number=phone_number).first()
        if user:
            return {
                "phone_number": user.phone_number,
                "first_name": user.first_name,
                "family_name": user.family_name,
                "father_name": user.father_name,
                "first_grand_name": user.first_grand_name,
                "second_grand_name": user.second_grand_name,
                "third_grand_name": user.third_grand_name,
                "relation": user.relation,
                "age": user.age,
                "gender": user.gender,
                "city": user.city,
                "attendance": user.attendance,
                "ideas": user.ideas,
                "registration_number": user.registration_number,
            }
        else:
            return {}


def create_image(content):
    # Create an image with a white background
    width, height = 800, 600  # Set the image size as needed
    image = Image.new("RGB", (width, height), color="white")
    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Define additional styles (e.g., colors)
    text_color = "black"
    background_color = "white"
    top_stripe_color = (8, 94, 157)
    bottom_stripe_color = (88, 88, 86)
    font_size = 36

    static_dir = os.path.join(os.path.dirname(__file__), "static")
    font_file_path = os.path.join(static_dir, "fonts", "Cairo-Bold.ttf")
    # Set the font and font size (you may need to download and specify an Arabic font)
    font = ImageFont.truetype(font_file_path, size=font_size)

    # Split content into lines
    lines = content.split("\n")

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
    idx = 0
    for line in lines:
        idx += 1
        print(f"Line no. ({idx}): ", line)
        print("BBox: ", font.getmask(line).getbbox())
        if idx == 8:
            break
        if (
            not line
            or line.isspace()
            or line == "\n"
            or line == "\r"
            or line == "\r\n"
            or line == "\n\r"
        ):
            continue
        
        reshaped_text = arabic_reshaper.reshape(line)
        bidi_text = get_display(reshaped_text)
        
        text_color = "red" if idx in (3, 5, 7) else "black"
        left, top, right, bottom = font.getmask(line).getbbox()
        text_width, text_height = right - left, bottom - top
        x = (
            width - text_width
        ) // 2  # Calculate horizontal position for center alignment
        
        draw.text((x, y), bidi_text, fill=text_color, font=font)
        # draw.text((x, y), line, fill=text_color, font=font)
        y += font_size + 20  # Adjust vertical position for the next line

    # # Set the position to start drawing
    # x, y = 10, 10
    # # Draw the content onto the image
    # draw.text((x, y), content, fill='black', font=font)
    return image

# Function to check if a value exists in a specific sheet
def is_value_in_sheet(spreadsheet_url, sheet_name, target_value):
    # Make a request to fetch the sheet data
    response = requests.get(spreadsheet_url)
    if response.status_code == 200:
        # Parse the HTML response
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find the table corresponding to the sheet
        tables = soup.find('table')
        # Check if the table exists
        if tables:
            # Check if the target value exists in any cell
            for row in tables.find_all('tr'):
                if target_value in [cell.text.strip() for cell in row.find_all('td')]:
                    return True
            return False
        else:
            print(f"Sheet '{sheet_name}' not found.")
            return False
    else:
        print(f"Error fetching data from Spreadsheet. Status code: {response.status_code}")
        return False


# ==============================================================================
# ''' Forms '''
# ==============================================================================
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


# Model for the registration form
class RegistrationForm(FlaskForm):
    phone_number = StringField(
        "رقم الهاتف الجوال",
        validators=[
            validators.DataRequired(),
            validators.Regexp(
                "^[+]?\d{10,15}$",
            ),
        ],
    )
    first_name = StringField("اسمك الأول", validators=[validators.InputRequired()])
    family_name = SelectField(
        "اسم العائلة",
        choices=[("السديس", "السديس"), ("أخرى", "أخرى")],
        validators=[validators.InputRequired()],
    )
    custom_family_name = StringField(
        "اسم العائلة غير أسرة السديس", validators=[validate_non_family_name]
    )
    relation = StringField(
        "إن لم تكن من أسرة السديس فلطفاً حدد نوع العلاقة",
        validators=[validate_non_family_name],
    )
    father_name = StringField("اسم الأب", validators=[validators.InputRequired()])
    first_grand_name = StringField(
        "اسم الجد الأول", validators=[validators.InputRequired()]
    )
    second_grand_name = StringField(
        "اسم الجد الثاني", validators=[validators.InputRequired()]
    )
    third_grand_name = StringField(
        "اسم الجد الثالث/فرع الأسرة", validators=[validators.InputRequired()]
    )
    age = SelectField(
        "ماهي فئتك العمرية",
        choices=[
            ("", ""),
            ("أقل من 10 سنوات", "أقل من 10 سنوات"),
            ("من 11 سنة حتى 20 سنة", "من 11 سنة حتى 20 سنة"),
            ("من 21 سنة حتى 40 سنة", "من 21 سنة حتى 40 سنة"),
            ("من 41 سنة حتى 60 سنة", "من 41 سنة حتى 60 سنة"),
            ("من 60 سنة فاكثر", "من 60 سنة فاكثر"),
        ],
        validators=[validators.InputRequired()],
    )
    gender = SelectField(
        "الجنس",
        choices=[
            ("", ""),
            ("ذكر", "ذكر"), 
            ("أنثى", "أنثى")
            ],
        validators=[validators.InputRequired()],
    )
    city = StringField(
        "مدينة العنوان الدائم لك", validators=[validators.InputRequired()]
    )
    attendance = SelectField(
        "هل ستحضر اللقاء",
        choices=[
            ("", ""),
            ("سوف أحضر باذن الله", "سوف أحضر باذن الله"),
            ("أعتذر عن الحضور", "أعتذر عن الحضور"),
        ],
        validators=[validators.InputRequired()],
    )
    ideas = TextAreaField(
        "هل لديك مشاركة أو فكرة تود تقديمها في الحفل ؟ نسعد بمعرفة ذلك"
    )
    submit = SubmitField("تسجيل")


# Form for adding a new prize
class PrizeForm(FlaskForm):
    name = StringField("اسم الهدية", validators=[DataRequired()])
    description = TextAreaField("الوصف")
    allowed_families = StringField("العائلات المسموح لها")
    allowed_age_range = SelectField(
        "العمر المسموح به",
        choices=[
            ("الكل", "الكل"),
            ("أقل من 10 سنوات", "أقل من 10 سنوات"),
            ("من 11 سنة حتى 20 سنة", "من 11 سنة حتى 20 سنة"),
            ("من 21 سنة حتى 40 سنة", "من 21 سنة حتى 40 سنة"),
            ("من 41 سنة حتى 60 سنة", "من 41 سنة حتى 60 سنة"),
            ("من 60 سنة فاكثر", "من 60 سنة فاكثر"),
        ],
    )
    allowed_gender = SelectField(
        "الجنس المسموح به", choices=[("الكل", "الكل"), ("ذكر", "ذكر"), ("أنثى", "أنثى")]
    )
    # guest_registration_number = StringField('Guest Registration Number', validators=[DataRequired()])


# Model for the filter form
class FilterForm(FlaskForm):
    family_name = MultiCheckboxField(
        "اسم العائلة", choices=[("السديس", "السديس"), ("أخرى", "أخرى")]
    )
    age = MultiCheckboxField(
        "الفئة العمرية",
        choices=[
            ("أقل من 10 سنوات", "أقل من 10 سنوات"),
            ("من 11 سنة حتى 20 سنة", "من 11 سنة حتى 20 سنة"),
            ("من 21 سنة حتى 40 سنة", "من 21 سنة حتى 40 سنة"),
            ("من 41 سنة حتى 60 سنة", "من 41 سنة حتى 60 سنة"),
            ("من 60 سنة فاكثر", "من 60 سنة فاكثر"),
        ],
    )
    gender = MultiCheckboxField("الجنس", choices=[("ذكر", "ذكر"), ("أنثى", "أنثى")])
    prize_id = IntegerField("الهدية", validators=[DataRequired()])
    submit = SubmitField("بحث")


# ==============================================================================
# ''' Routes '''
# ==============================================================================

# Route for the home page
@app.route("/", methods=["GET", "POST"])
def index():
    form = RegistrationForm()  # Create an instance of the RegistrationForm
    if request.method == "POST":
        phone_number = request.form["phone_number"]
        # Check if the number is in the spreadsheet
        if not is_value_in_sheet(
            spreadsheet_url=SPREADSHEET_URL,
            sheet_name=GUESTS_SHEET_NAME,
            target_value=phone_number if phone_number[0]!='0' else phone_number[1:],
        ):
            # If the number is not in the spreadsheet, redirect to the error page
            return render_template("not_in_sheet.html")
        
        # Check if the phone number is not registered
        if not is_registered(phone_number):
            return redirect(url_for("register", phone_number=phone_number))
        # Check if the phone number is alerady registered
        return redirect(url_for("registered", phone_number=phone_number))
    return render_template("index.html", form=form)


# Route for the admin page
@app.route("/admin", methods=["GET", "POST"])
def admin():
    page = request.args.get("page", 1, type=int)
    per_page = 50  # Number of logs per page
    guests_query = Registration.query
    guests_page = guests_query.paginate(page=page, per_page=per_page)
    guests_count = guests_query.count()
    guest_attendance = guests_query.filter(
        Registration.attendance == "سوف أحضر باذن الله"
    ).count()
    guest_not_attendance = guests_query.filter(
        Registration.attendance == "أعتذر عن الحضور"
    ).count()
    guest_is_attended = guests_query.filter(Registration.is_attended == True).count()
    guest_male = guests_query.filter(Registration.gender == "ذكر").count()
    guest_female = guests_query.filter(Registration.gender == "أنثى").count()
    return render_template(
        "admin.html",
        guests=guests_page,
        guests_count=guests_count,
        guest_attendance=guest_attendance,
        guest_not_attendance=guest_not_attendance,
        guest_is_attended=guest_is_attended,
        guest_male=guest_male,
        guest_female=guest_female,
    )


# Delete Guest
@app.route("/delete_guest/<string:guest_phoneno>", methods=["GET", "POST"])
def delete_guest(guest_phoneno):
    try:
        guest = Registration.query.filter_by(phone_number=guest_phoneno).first()
        db.session.delete(guest)
        db.session.commit()
        flash("تم حذف بيانات الضيف بنجاح", "success")
        return redirect(url_for("admin"))
    except:
        flash("فشلت عملية الحذف", "danger")
        return redirect(url_for("admin"))


# Route for the registration form
@app.route("/register/<phone_number>", methods=["POST", "GET"])
def register(phone_number):
    existing_registration = Registration.query.filter_by(
        phone_number=phone_number
    ).first()
    # Create the form instance and load data if it exists
    form = RegistrationForm(obj=existing_registration)
    form.phone_number.data = phone_number

    if existing_registration and existing_registration.family_name not in (
        "أخرى",
        "السديس",
    ):
        form.custom_family_name.data = existing_registration.family_name
        form.family_name.data = "أخرى"

    if request.method == "POST":
        if form.validate_on_submit():
            if existing_registration:
                # Update the existing registration with form data
                form.populate_obj(existing_registration)
                db.session.commit()
            else:
                new_registration = Registration()
                form.populate_obj(new_registration)

                if form.family_name.data == "أخرى":
                    new_registration.family_name = form.custom_family_name.data
                else:
                    new_registration.family_name = form.family_name.data

                new_registration.phone_number = phone_number
                new_registration.registration_number = generate_registration_number()
                db.session.add(new_registration)
                db.session.commit()
                flash("تم التسجيل بنجاح", "success")

            # Redirect to a success page or the landing page
            return redirect(url_for("registered", phone_number=phone_number))
        else:
            # Handle errors
            flash("حدث خطأ ما", "error")
            flash(form.errors, "error")
            return render_template(
                "register.html", phone_number=phone_number, form=form, keep=True
            )

    return render_template(
        "register.html",
        phone_number=phone_number,
        form=form,
        keep=bool(form.custom_family_name.data),
    )


@app.route("/registered/<phone_number>", methods=["POST", "GET"])
def registered(phone_number):
    user_data = get_user_data(phone_number)
    if user_data:
        return render_template("registered.html", user_data=user_data)
    else:
        flash("رقم الجوال غير مسجل من قبل", "error")
        return redirect(url_for("index"))


@app.route("/delete/<phone_number>", methods=["GET"])
def delete(phone_number):
    try:
        existing_registration = Registration.query.filter_by(
            phone_number=phone_number
        ).first()
        db.session.delete(existing_registration)
        db.session.commit()
        flash("تم حذف البيانات بنجاح", "success")
        return redirect(url_for("index"))
    except Exception:
        flash("فشلت محاولة حذف البيانات", "danger")
        return redirect(url_for("registered", phone_number=phone_number))


@app.route("/convert_to_image", methods=["POST"])
def convert_to_image():
    # Get the content from the request (e.g., JSON or form data)
    content = request.form["content"]
    # Create an image with the content
    image = create_image(content)
    # Save the image to a byte stream
    image_stream = io.BytesIO()
    image.save(image_stream, format="PNG")
    image_stream.seek(0)
    # Return the image as a response
    return Response(image_stream, content_type="image/png")


@app.route("/export_to_excel")
def export_to_excel():
    items = get_user_data(None)
    if not items:
        return None

    df = pd.DataFrame(items)
    excel_file_path = "registeration.xlsx"
    df.to_excel(excel_file_path, index=False)
    return send_file(excel_file_path, as_attachment=True)


# ------------------------------------------------------------------------------
# ''' Prizes Routes '''
# ------------------------------------------------------------------------------


# Create route for displaying a list of prizes
@app.route("/prizes", methods=["GET", "POST"])
def list_prizes():
    prizes = Prize.query.all()
    filters = FilterForm()
    if request.method == "POST" and filters.validate_on_submit():
        # Get filter from user
        allowed_families = filters.family_name.data
        allowed_age_range = filters.age.data
        allowed_gender = filters.gender.data
        prize_id = request.form["prize_id"]

        # Set filter on the next prize
        prize = Prize.query.get(prize_id)
        prize.allowed_families = ",".join(allowed_families)
        prize.allowed_age_range = ",".join(allowed_age_range)
        prize.allowed_gender = ",".join(allowed_gender)

        # Set is_next to the selected prize only
        Prize.query.update({"is_next": False})  # Remove the flag from all other prizes
        prize.is_next = True

        # Commit
        db.session.commit()

    return render_template("prizes.html", prizes=prizes, filters=filters)


# Create route for adding a new prize
@app.route("/prizes/add", methods=["GET", "POST"])
def add_prize():
    form = PrizeForm()
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        allowed_families = request.form["allowed_families"]
        allowed_age_range = request.form["allowed_age_range"]
        allowed_gender = request.form["allowed_gender"]

        prize = Prize(
            name=name,
            description=description,
            allowed_families=allowed_families,
            allowed_age_range=allowed_age_range,
            allowed_gender=allowed_gender,
        )
        db.session.add(prize)
        db.session.commit()

        flash("Prize added successfully!", "success")
        return redirect(url_for("list_prizes"))

    return render_template("add_prize.html", form=form)


# Create route for editing a prize
@app.route("/prizes/edit/<int:id>", methods=["GET", "POST"])
def edit_prize(id):
    prize = Prize.query.get(id)
    form = PrizeForm(obj=prize)

    if request.method == "POST":
        prize.name = request.form["name"]
        prize.description = request.form["description"]
        prize.allowed_families = request.form["allowed_families"]
        prize.allowed_age_range = request.form["allowed_age_range"]
        prize.allowed_gender = request.form["allowed_gender"]

        db.session.commit()

        flash("Prize updated successfully!", "success")
        return redirect(url_for("list_prizes"))

    return render_template("edit_prize.html", form=form, prize=prize)


# Create route for deleting a prize
@app.route("/prizes/delete/<int:id>", methods=["POST"])
def delete_prize(id):
    prize = Prize.query.get(id)
    db.session.delete(prize)
    db.session.commit()
    flash("Prize deleted successfully!", "success")
    return redirect(url_for("list_prizes"))


# Create route to delete registration number from the prize and search for registration
# number in 'Registeration' table and delete 'prize_id'
@app.route("/prizes/reset/<int:id>", methods=["POST"])
def reset_prize(id):
    sel_prize = Prize.query.get(id)
    sel_regno=sel_prize.guest_registration_number
    sel_prize.guest_registration_number = None
    sel_reg= Registration.query.filter_by(registration_number=sel_regno).first()
    sel_reg.prize_id=None
    db.session.commit()
    flash("Registration number deleted successfully!", "success")
    return redirect(url_for("list_prizes"))

# ------------------------------------------------------------------------------
# ''' Withdrawal Routes '''
# ------------------------------------------------------------------------------


# Route to withdraw a prize
@app.route("/withdraw_prize", methods=["GET", "POST"])
def withdraw_prize():
    sel_prize = Prize.query.filter_by(
        is_next=True, guest_registration_number=None
    ).first()

    # Fetch all registration numbers not associated with a prize
    return render_template("withdraw_prize.html", prize=sel_prize)


def get_filtered_reg_no(prize_id: int):
    # Get sel prize filters
    sel_prize = Prize.query.filter_by(id=prize_id).first()
    allowed_families = sel_prize.allowed_families
    allowed_age_range = sel_prize.allowed_age_range
    allowed_gender = sel_prize.allowed_gender

    # Base query to filter records without a prize_id
    base_query = Registration.query.filter(
        Registration.prize_id == None, Registration.is_attended == True
    )

    # Build the filter conditions dynamically
    filter_conditions = []

    # Check if allowed_families is not empty
    if allowed_families and "أخرى" not in allowed_families:
        families = allowed_families.split(",")
        family_condition = or_(
            *[Registration.family_name.contains(family) for family in families]
        )
        filter_conditions.append(family_condition)

    # Check if allowed_age_range is not 'الكل'
    if allowed_age_range:
        age_ranges = allowed_age_range.split(",")
        age_range_condition = or_(
            *[Registration.age.contains(age_range) for age_range in age_ranges]
        )
        filter_conditions.append(age_range_condition)

    # Check if allowed_gender is not 'الكل'
    if allowed_gender:
        genders = allowed_gender.split(",")
        gender_condition = or_(
            *[Registration.gender.contains(gender) for gender in genders]
        )
        filter_conditions.append(gender_condition)

    # Apply the filter conditions
    if filter_conditions:
        final_query = base_query.filter(and_(*filter_conditions))
    else:
        final_query = base_query

    # Execute the query to get the filtered records
    registrations_without_prize = final_query.all()
    return registrations_without_prize


# Route to get random registration number
@app.route("/shuffle_numbers/<int:id>", methods=["GET", "POST"])
def shuffle_numbers(id):
    registrations_without_prize = get_filtered_reg_no(prize_id=id)
    # registrations_without_prize = Registration.query.filter_by(prize_id=None).all()
    random.shuffle(registrations_without_prize)

    # If there are registrations without a prize
    if registrations_without_prize and len(registrations_without_prize) > 1:
        # Randomly select one registration number
        selected_registration = random.choice(registrations_without_prize)
        # rnd_reg_no = selected_registration.registration_number
        # Reomve the select winner and move it to 2nd place
        registrations_without_prize.remove(selected_registration)
        registrations_without_prize.insert(1, selected_registration)

        regno_list = [
            reg.registration_number.zfill(4) for reg in registrations_without_prize[:10]
        ]

        # Return a response (if needed)
        return jsonify(
            regno_list=regno_list,
            winner=registrations_without_prize[1].registration_number,
            winner_name=registrations_without_prize[1].first_name
            + " "
            + registrations_without_prize[1].family_name,
        )
    else:
        return jsonify(regno_list=[], winner="", winner_name="")


@app.route("/confirm_prize/<int:prize_id>/<int:reg_no>", methods=["GET", "POST"])
def confirm_prize(prize_id, reg_no):
    # Get the sel prize object and update it
    sel_prize = Prize.query.filter_by(id=prize_id).first()
    sel_prize.guest_registration_number = reg_no
    sel_prize.is_next = False
    # Update the registeration table
    db.session.query(Registration).filter(
        Registration.registration_number == reg_no
    ).update({Registration.prize_id: prize_id})
    # Commit the changes
    db.session.commit()
    return jsonify("Success")


# ------------------------------------------------------------------------------
# ''' Attendence confirmation Routes '''
# ------------------------------------------------------------------------------


# Route for attendence confirmation
@app.route("/confirm_attendence", methods=["GET", "POST"])
def confirm_attendence():
    form = RegistrationForm()  # Create an instance of the RegistrationForm
    if request.method == "POST":
        phone_number = request.form["phone_number"]
        sel_reg = Registration.query.filter_by(phone_number=phone_number).first()
        if sel_reg:
            sel_reg.is_attended = True
            db.session.commit()
            return render_template(
                "confirm_attendence.html",
                form=form,
                result="success",
                reg_no=sel_reg.registration_number,
            )
        else:
            return render_template(
                "confirm_attendence.html", form=form, result="failed"
            )
    return render_template(
        "confirm_attendence.html", form=form, result=""
    )  # Pass the form instance to the template


# ==============================================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
