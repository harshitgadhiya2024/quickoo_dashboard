from operations.mongo_operation import mongoOperation
from operations.common_operations import commonOperation
from operations.mail_sending import emailOperation
from utils.constant import constant_dict
import os, json, re
from flask import (Flask, render_template, request, flash, session, send_file, jsonify, send_from_directory, url_for)
from flask_cors import CORS
from datetime import datetime, date
import uuid
from werkzeug.utils import secure_filename, redirect
from utils.html_format import htmlOperation
from functools import wraps
import phonenumbers
from phonenumbers import NumberParseException
from email_validator import validate_email, EmailNotValidError
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = constant_dict.get("secreat_key")
UPLOAD_FOLDER = 'static/uploads/'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


class UKDataValidator:
    """
    Comprehensive data validation class for UK-specific requirements
    """

    @staticmethod
    def validate_email(email):
        """Validate email format"""
        try:
            if not email or not email.strip():
                return False, "Email is required"

            email = email.strip().lower()
            valid = validate_email(email)
            return True, valid.email
        except EmailNotValidError:
            return False, "Invalid email format"

    @staticmethod
    def validate_uk_phone(phone):
        """Validate UK phone number format"""
        try:
            if not phone or not phone.strip():
                return False, "Phone number is required"

            phone = phone.strip()

            # Parse phone number with UK as default region
            parsed_number = phonenumbers.parse(phone, "GB")

            # Check if it's a valid UK number
            if not phonenumbers.is_valid_number(parsed_number):
                return False, "Invalid UK phone number"

            # Format the number in international format
            formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

            return True, formatted_number

        except NumberParseException:
            return False, "Invalid phone number format"

    @staticmethod
    def validate_dutch_phone(phone):
        """Validate Dutch phone number format (for existing +44 numbers)"""
        try:
            if not phone or not phone.strip():
                return False, "Phone number is required"

            phone = phone.strip()

            # If it starts with +44, validate as Dutch number
            if phone.startswith('+44') or phone.startswith('0031'):
                parsed_number = phonenumbers.parse(phone, "NL")
                if phonenumbers.is_valid_number(parsed_number):
                    formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                    return True, formatted_number

            return False, "Invalid Dutch phone number format"

        except NumberParseException:
            return False, "Invalid phone number format"

    @staticmethod
    def validate_postcode(postcode):
        """Validate UK postcode format"""
        if not postcode or not postcode.strip():
            return False, "Postcode is required"

        postcode = postcode.strip().upper().replace(" ", "")

        # UK postcode regex pattern
        uk_postcode_pattern = r'^[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}$'

        if re.match(uk_postcode_pattern, postcode):
            # Format postcode properly (add space)
            if len(postcode) == 6:
                formatted_postcode = postcode[:3] + " " + postcode[3:]
            elif len(postcode) == 7:
                formatted_postcode = postcode[:4] + " " + postcode[4:]
            else:
                formatted_postcode = postcode

            return True, formatted_postcode

        return False, "Invalid UK postcode format"

    @staticmethod
    def validate_name(name, field_name="Name"):
        """Validate name fields"""
        if not name or not name.strip():
            return False, f"{field_name} is required"

        name = name.strip()

        if len(name) < 2:
            return False, f"{field_name} must be at least 2 characters long"

        if len(name) > 50:
            return False, f"{field_name} must be less than 50 characters"

        # Allow letters, spaces, hyphens, and apostrophes
        if not re.match(r"^[a-zA-Z\s\-']+$", name):
            return False, f"{field_name} can only contain letters, spaces, hyphens, and apostrophes"

        return True, name.title()

    @staticmethod
    def validate_vat_number(vat_number):
        """Validate UK VAT number format"""
        if not vat_number or not vat_number.strip():
            return False, "VAT number is required"

        vat_number = vat_number.strip().replace(" ", "").upper()

        # UK VAT number pattern: GB followed by 9 or 12 digits
        uk_vat_pattern = r'^GB\d{9}(\d{3})?$'

        if re.match(uk_vat_pattern, vat_number):
            return True, vat_number

        return False, "Invalid UK VAT number format (should be GB followed by 9 or 12 digits)"

    @staticmethod
    def validate_national_insurance(ni_number):
        """Validate UK National Insurance number format"""
        if not ni_number or not ni_number.strip():
            return False, "National Insurance number is required"

        ni_number = ni_number.strip().upper().replace(" ", "")

        # UK NI number pattern: 2 letters, 6 digits, 1 letter
        ni_pattern = r'^[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z]\d{6}[A-D]$'

        if re.match(ni_pattern, ni_number):
            # Format with spaces for readability
            formatted_ni = ni_number[:2] + " " + ni_number[2:4] + " " + ni_number[4:6] + " " + ni_number[6:8] + " " + \
                           ni_number[8]
            return True, formatted_ni

        return False, "Invalid UK National Insurance number format"

    @staticmethod
    def validate_uk_driving_licence(licence_number):
        """Validate UK driving licence number format"""
        if not licence_number or not licence_number.strip():
            return False, "Driving licence number is required"

        licence_number = licence_number.strip()

        # UK driving licence pattern: complex format with surname encoded
        # Simplified validation for basic format checking
        if len(licence_number) == 16 and licence_number.replace(" ", "").isalnum():
            return True, licence_number.upper()

        return False, "Invalid UK driving licence number format"

    @staticmethod
    def validate_vehicle_registration(reg_number):
        """Validate UK vehicle registration number"""
        if not reg_number or not reg_number.strip():
            return False, "Vehicle registration is required"

        reg_number = reg_number.strip().upper().replace(" ", "")

        # UK registration patterns (simplified)
        patterns = [
            r'^[A-Z]{2}\d{2}[A-Z]{3}$',  # Current format: AB12 CDE
            r'^[A-Z]\d{1,3}[A-Z]{3}$',  # Older format: A123 BCD
            r'^[A-Z]{3}\d{1,3}[A-Z]$',  # Older format: ABC 123D
        ]

        for pattern in patterns:
            if re.match(pattern, reg_number):
                return True, reg_number

        return False, "Invalid UK vehicle registration format"

    @staticmethod
    def validate_date(date_str, field_name="Date"):
        """Validate date format and ensure it's not in the past (for expiry dates)"""
        if not date_str or not date_str.strip():
            return False, f"{field_name} is required"

        try:
            date_obj = datetime.strptime(date_str.strip(), '%Y-%m-%d')

            # For expiry dates, ensure they're in the future
            if "expire" in field_name.lower() or "expiry" in field_name.lower():
                if date_obj.date() <= datetime.now().date():
                    return False, f"{field_name} must be in the future"

            return True, date_str.strip()

        except ValueError:
            return False, f"Invalid {field_name.lower()} format (YYYY-MM-DD required)"

    @staticmethod
    def validate_percentage(percentage):
        """Validate percentage format"""
        if not percentage or not percentage.strip():
            return False, "Percentage is required"

        percentage = percentage.strip()

        # Remove % if present
        if percentage.endswith('%'):
            percentage = percentage[:-1]

        try:
            value = float(percentage)
            if 0 <= value <= 100:
                return True, f"{value}%"
            else:
                return False, "Percentage must be between 0 and 100"

        except ValueError:
            return False, "Invalid percentage format"

    @staticmethod
    def validate_service_type(service_type):
        """Validate service type"""
        valid_services = ['standard', 'premium', 'luxury', 'airport_transfer', 'corporate']

        if not service_type or service_type not in valid_services:
            return False, f"Service type must be one of: {', '.join(valid_services)}"

        return True, service_type


def validate_form_data(data, validation_rules):
    """
    Generic form validation function

    Args:
        data: Dictionary of form data
        validation_rules: Dictionary of field_name -> validation_function pairs

    Returns:
        tuple: (is_valid, validated_data, errors)
    """
    errors = []
    validated_data = {}

    for field_name, validator_func in validation_rules.items():
        field_value = data.get(field_name, '')
        is_valid, result = validator_func(field_value)

        if is_valid:
            validated_data[field_name] = result
        else:
            errors.append(f"{field_name.replace('_', ' ').title()}: {result}")

    return len(errors) == 0, validated_data, errors


# Utility to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


client = mongoOperation().mongo_connect(get_mongourl=constant_dict.get("mongo_url"))


def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        login_dict = session.get("login_dict", {})
        if login_dict:
            pass
        else:
            flash("Please login first...", "danger")
            return redirect("/")
        return func(*args, **kwargs)

    return decorated


@app.route("/", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            # Validate email
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "").strip()

            if not email or not password:
                flash("Email and password are required", "danger")
                return redirect("/")

            is_valid_email, validated_email = UKDataValidator.validate_email(email)
            if not is_valid_email:
                flash(validated_email, "danger")
                return redirect("/")

            all_data = list(mongoOperation().get_spec_data_from_coll(client, "quickoo_uk", "login_mapping",
                                                                     {"email": validated_email, "password": password}))
            if all_data:
                is_active = all_data[0]["is_active"]
                if is_active:
                    session["login_dict"] = {"id": all_data[0]["user_id"]}
                    return redirect("/dashboard")
                else:
                    flash("Please activate your account", "danger")
                    return redirect("/")
            else:
                flash("Please enter correct credentials", "danger")
                return redirect("/")
        else:
            return render_template("login.html")

    except Exception as e:
        print(f"{datetime.now()}: Error in login route: {str(e)}")
        flash("An error occurred during login", "danger")
        return render_template("login.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    try:
        if request.method == "POST":
            email = request.form.get("email", "").strip()

            is_valid_email, validated_email = UKDataValidator.validate_email(email)
            if not is_valid_email:
                flash(validated_email, "danger")
                return redirect("/forgot-password")

            email_condition_dict = {"email": validated_email}
            email_data = mongoOperation().get_spec_data_from_coll(client, "quickoo_uk", "login_mapping",
                                                                  email_condition_dict)
            if email_data:
                if email_data[0]["is_active"]:
                    forgot_password_link = f"http://127.0.0.1:5000/reset-password?email={validated_email}"
                    html_format = htmlOperation().forgot_password_mail_template(forgot_password_link)
                    emailOperation().send_email(validated_email, "Quickoo: Your Account Verification Code", html_format)
                    flash("Reset link sent successfully. Please check your mail", "success")
                    return redirect("/")
                else:
                    flash("Your account was disabled, Contact administration", "danger")
                    return redirect("/forgot-password")
            else:
                flash("Account not found", "danger")
                return redirect("/forgot-password")
        else:
            return render_template("forgot-password.html")

    except Exception as e:
        print(f"{datetime.now()}: Error in forgot-password route: {str(e)}")
        flash("An error occurred during password reset", "danger")
        return render_template("forgot-password.html")


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    try:
        email = request.args.get("email")
        if request.method == "POST":
            password = request.form.get("password", "").strip()
            confirm_password = request.form.get("confirm_password", "").strip()

            if not password or not confirm_password:
                flash("Both password fields are required", "danger")
                return redirect(f"/reset-password?email={email}")

            if len(password) < 8:
                flash("Password must be at least 8 characters long", "danger")
                return redirect(f"/reset-password?email={email}")

            if password == confirm_password:
                mongoOperation().update_mongo_data(client, "quickoo_uk", "login_mapping", {"email": email},
                                                   {"password": password})
                flash("Password updated successfully", "success")
                return redirect("/")
            else:
                flash("Passwords don't match", "danger")
                return redirect(f"/reset-password?email={email}")
        else:
            return render_template("reset-password.html", email=email)

    except Exception as e:
        print(f"{datetime.now()}: Error in reset-password route: {str(e)}")
        flash("An error occurred during password reset", "danger")
        return render_template("reset-password.html")


@app.route("/dashboard", methods=["GET", "POST"])
@token_required
def dashboard():
    try:
        driver_data = list(mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "driver_data"))[::-1]
        booking_data = list(mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "booking_data"))[::-1]
        vender_data = list(mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "vender_data"))[::-1]
        updated_driver_data = [{"name": data["drivername"], "email": data["email"], "phone": data["phone"], "status": data["status"]} for data in driver_data[:3]]
        updated_booking_data = [{"name": data["full_name"], "email": data["email"], "phone": data["phone"], "status": data["status"]} for data in booking_data[:3]]
        updated_vender_data = [{"name": data["vender_name"], "email": data["email"], "phone": data["phone"], "status": data["status"]} for data in vender_data[:3]]

        return render_template("index.html", driver_len=len(driver_data), booking_len=len(booking_data), vender_len=len(vender_data), driver_data=updated_driver_data,
        vender_data=updated_vender_data, booking_data=updated_booking_data)
    except Exception as e:
        print(f"{datetime.now()}: Error in dashboard route: {str(e)}")
        return render_template("index.html")


@app.route("/booking_details", methods=["GET", "POST"])
@token_required
def booking_details():
    try:
        is_data = True
        all_data = []
        status_mapping_dict = {
            "waiting": {"color": "btn-secondary", "status_list": ["not_started", "on_way", "completed", "cancel"]},
            "not_started": {"color": "btn-warning", "status_list": ["waiting", "on_way", "completed", "cancel"]},
            "on_way": {"color": "btn-primary", "status_list": ["waiting", "not_started", "completed", "cancel"]},
            "completed": {"color": "btn-success", "status_list": ["waiting", "not_started", "on_way", "cancel"]},
            "cancel": {"color": "btn-danger", "status_list": ["waiting", "not_started", "on_way", "completed"]}
        }

        all_booking_data = list(mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "booking_data"))
        if all_booking_data:
            for data in all_booking_data:
                del data["_id"]
                all_data.append(data)
        else:
            is_data = False

        all_driver_data = list(mongoOperation().get_spec_data_from_coll(client, "quickoo_uk", "driver_data",
                                                                        {"status": "active", "is_assign": False}))
        all_updated_data = []
        for driver in all_driver_data:
            all_updated_data.append({"id": driver["id"], "name": driver["drivername"]})

        return render_template("booking-details.html", is_data=is_data, all_data=all_data,
                               status_mapping=status_mapping_dict, all_driver=all_updated_data)

    except Exception as e:
        print(f"{datetime.now()}: Error in booking details route: {str(e)}")
        return render_template("booking-details.html")


@app.route("/assign-driver", methods=["GET"])
@token_required
def assign_driver():
    try:
        ride_id = request.args.get("rideid")
        driver_id = request.args.get("driverid")

        if not ride_id or not driver_id:
            flash("Missing ride ID or driver ID", "danger")
            return {"error": "Missing required parameters"}

        mongoOperation().update_mongo_data(client, "quickoo_uk", "booking_data", {"id": ride_id},
                                           {"driver_id": driver_id, "updated_at": datetime.utcnow()})
        mongoOperation().update_mongo_data(client, "quickoo_uk", "driver_data", {"id": driver_id},
                                           {"is_assign": True, "updated_at": datetime.utcnow()})
        flash("Driver assigned successfully", "success")
        return {"message": "driver assigned successfully"}

    except Exception as e:
        print(f"{datetime.now()}: Error in assign driver route: {str(e)}")
        return {"error": "Failed to assign driver"}


@app.route("/add-ride-booking", methods=["POST"])
@token_required
def add_book_riding():
    try:
        # Define validation rules for booking
        validation_rules = {
            'full_name': lambda x: UKDataValidator.validate_name(x, "Full Name"),
            'phone': UKDataValidator.validate_uk_phone,
            'email': UKDataValidator.validate_email,
            'pickup': lambda x: (True, x.strip()) if x and x.strip() else (False, "Pickup location is required"),
            'drop': lambda x: (True, x.strip()) if x and x.strip() else (False, "Drop location is required"),
            'pickupdate': lambda x: UKDataValidator.validate_date(x, "Pickup Date"),
            'pickuptime': lambda x: (True, x.strip()) if x and x.strip() else (False, "Pickup time is required"),
        }

        # Get form data
        form_data = {
            'full_name': request.form.get("fullname", ""),
            'phone': request.form.get("phone", ""),
            'email': request.form.get("email", ""),
            'pickup': request.form.get("pickup", ""),
            'drop': request.form.get("drop", ""),
            'pickupdate': request.form.get("pickupdate", ""),
            'pickuptime': request.form.get("pickuptime", ""),
        }

        # Validate form data
        is_valid, validated_data, errors = validate_form_data(form_data, validation_rules)

        if not is_valid:
            for error in errors:
                flash(error, "danger")
            return redirect("/booking_details")

        # Optional fields (no validation required but can be validated)
        service_type = request.form.get("service_type", "standard")
        shoffr_class = request.form.get("shoffr_class", "")
        flightinfo = request.form.get("flightinfo", "")
        baginfo = request.form.get("baginfo", "")
        note = request.form.get("note", "")

        # Generate unique ID
        all_company_booking_data = list(mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "booking_data"))
        allids = [booking_data["id"] for booking_data in all_company_booking_data]

        uid = str(uuid.uuid4())
        while uid in allids:
            uid = str(uuid.uuid4())

        mapping_dict = {
            "id": uid,
            "driver_id": "",
            "full_name": validated_data['full_name'],
            "phone": validated_data['phone'],
            "email": validated_data['email'],
            "pickup": validated_data['pickup'],
            "drop": validated_data['drop'],
            "date": validated_data['pickupdate'],
            "time": validated_data['pickuptime'],
            "service_type": service_type,
            "shoffr_class": shoffr_class,
            "flight_info": flightinfo,
            "bag_info": baginfo,
            "note": note,
            "status": "waiting",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        booking_template = htmlOperation().booking_confirmation_process(mapping_dict)
        emailOperation().send_email(
            validated_data["email"], "Quickoo - Booking Confirmation", booking_template
        )
        mongoOperation().insert_data_from_coll(client, "quickoo_uk", "booking_data", mapping_dict)
        flash("Booking created successfully", "success")
        return redirect("/booking_details")

    except Exception as e:
        print(f"{datetime.now()}: Error in add booking data route: {str(e)}")
        flash("An error occurred while creating booking", "danger")
        return redirect("/booking_details")


@app.route("/ride-status-update", methods=["GET"])
@token_required
def ride_status_update():
    try:
        uid = request.args.get("uid")
        status = request.args.get("status")

        if not uid or not status:
            flash("Missing ride ID or status", "danger")
            return redirect("/booking_details")

        valid_statuses = ["waiting", "not_started", "on_way", "completed", "cancel"]
        if status not in valid_statuses:
            flash("Invalid status", "danger")
            return redirect("/booking_details")

        mongoOperation().update_mongo_data(client, "quickoo_uk", "booking_data", {"id": uid},
                                           {"status": status, "updated_at": datetime.utcnow()})
        flash("Status updated successfully", "success")
        return redirect("/booking_details")

    except Exception as e:
        print(f"{datetime.now()}: Error in updating booking status route: {str(e)}")
        flash("An error occurred while updating status", "danger")
        return redirect("/booking_details")


@app.route("/vendor_details", methods=["GET", "POST"])
@token_required
def vendor_details():
    try:
        is_data = True
        all_data = []
        status_mapping_dict = {
            "active": {"color": "btn-success", "status_list": ["deactive"], "status": "deactive"},
            "deactive": {"color": "btn-danger", "status_list": ["active"], "status": "active"},
        }

        all_vender_data = list(mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "vender_data"))
        if all_vender_data:
            for data in all_vender_data:
                del data["_id"]
                all_data.append(data)
        else:
            is_data = False

        return render_template("vender-details.html", all_data=all_data, is_data=is_data,
                               status_mapping=status_mapping_dict)

    except Exception as e:
        print(f"{datetime.now()}: Error in vender details route: {str(e)}")
        return render_template("vender-details.html")


@app.route("/add-vender", methods=["POST"])
@token_required
def add_vender():
    try:
        # Define validation rules for vendor
        validation_rules = {
            'vender_name': lambda x: UKDataValidator.validate_name(x, "Vendor Name"),
            'vat_no': UKDataValidator.validate_vat_number,
            'tax': UKDataValidator.validate_percentage,
            'phone': UKDataValidator.validate_uk_phone,
            'email': UKDataValidator.validate_email,
        }

        # Get form data
        form_data = {
            'vender_name': request.form.get("vendername", ""),
            'vat_no': request.form.get("vatno", ""),
            'tax': request.form.get("tax", ""),
            'phone': request.form.get("phone", ""),
            'email': request.form.get("email", ""),
        }

        # Validate form data
        is_valid, validated_data, errors = validate_form_data(form_data, validation_rules)

        if not is_valid:
            for error in errors:
                flash(error, "danger")
            return redirect("/vendor_details")

        # Generate unique ID
        all_vender_data = list(mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "vender_data"))
        allids = [vender_data["id"] for vender_data in all_vender_data]

        uid = str(uuid.uuid4())
        while uid in allids:
            uid = str(uuid.uuid4())

        mapping_dict = {
            "id": uid,
            "vender_name": validated_data['vender_name'],
            "vat_no": validated_data['vat_no'],
            "tax": validated_data['tax'],
            "email": validated_data['email'],
            "phone": validated_data['phone'],
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        mongoOperation().insert_data_from_coll(client, "quickoo_uk", "vender_data", mapping_dict)
        flash("Vendor added successfully", "success")
        return redirect("/vendor_details")

    except Exception as e:
        print(f"{datetime.now()}: Error in add vender data route: {str(e)}")
        flash("An error occurred while adding vendor", "danger")
        return redirect("/vendor_details")


@app.route("/edit-vender", methods=["POST"])
@token_required
def edit_vender():
    try:
        uid = request.args.get("id", "")
        if not uid:
            flash("Vendor ID is required", "danger")
            return redirect("/vendor_details")

        # Define validation rules for vendor editing
        validation_rules = {
            'vender_name': lambda x: UKDataValidator.validate_name(x, "Vendor Name"),
            'vat_no': UKDataValidator.validate_vat_number,
            'tax': UKDataValidator.validate_percentage,
            'phone': UKDataValidator.validate_uk_phone,
            'email': UKDataValidator.validate_email,
        }

        # Get form data
        form_data = {
            'vender_name': request.form.get("vendername", ""),
            'vat_no': request.form.get("vatno", ""),
            'tax': request.form.get("tax", ""),
            'phone': request.form.get("phone", ""),
            'email': request.form.get("email", ""),
        }

        # Validate form data
        is_valid, validated_data, errors = validate_form_data(form_data, validation_rules)

        if not is_valid:
            for error in errors:
                flash(error, "danger")
            return redirect("/vendor_details")

        update_mapping_dict = {
            "vender_name": validated_data['vender_name'],
            "vat_no": validated_data['vat_no'],
            "tax": validated_data['tax'],
            "email": validated_data['email'],
            "phone": validated_data['phone'],
            "updated_at": datetime.utcnow()
        }

        mongoOperation().update_mongo_data(client, "quickoo_uk", "vender_data", {"id": uid}, update_mapping_dict)
        flash("Vendor updated successfully", "success")
        return redirect("/vendor_details")

    except Exception as e:
        print(f"{datetime.now()}: Error in edit vender data route: {str(e)}")
        flash("An error occurred while updating vendor", "danger")
        return redirect("/vendor_details")


@app.route("/vender-status-update", methods=["GET"])
@token_required
def vender_status_update():
    try:
        uid = request.args.get("uid")
        status = request.args.get("status")

        if not uid or not status:
            flash("Missing vendor ID or status", "danger")
            return redirect("/vendor_details")

        if status not in ["active", "deactive"]:
            flash("Invalid status", "danger")
            return redirect("/vendor_details")

        mongoOperation().update_mongo_data(client, "quickoo_uk", "vender_data", {"id": uid},
                                           {"status": status, "updated_at": datetime.utcnow()})
        flash("Status updated successfully", "success")
        return redirect("/vendor_details")

    except Exception as e:
        print(f"{datetime.now()}: Error in updating vender status route: {str(e)}")
        flash("An error occurred while updating status", "danger")
        return redirect("/vendor_details")


@app.route("/driver_details", methods=["GET", "POST"])
@token_required
def driver_details():
    try:
        is_data = True
        all_data = []
        status_mapping_dict = {
            "active": {"color": "btn-success", "status_list": ["deactive"], "status": "deactive"},
            "deactive": {"color": "btn-danger", "status_list": ["active"], "status": "active"},
        }

        all_driver_data = list(mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "driver_data"))
        if all_driver_data:
            for data in all_driver_data:
                del data["_id"]
                all_data.append(data)
        else:
            is_data = False

        return render_template("driver-details.html", all_data=all_data, is_data=is_data,
                               status_mapping=status_mapping_dict)

    except Exception as e:
        print(f"{datetime.now()}: Error in driver details route: {str(e)}")
        return render_template("driver-details.html")


@app.route("/add-driver", methods=["POST"])
@token_required
def add_driver():
    try:
        if request.method == 'POST':
            # Define validation rules for driver
            validation_rules = {
                'drivername': lambda x: UKDataValidator.validate_name(x, "Driver Name"),
                'email': UKDataValidator.validate_email,
                'phone': UKDataValidator.validate_uk_phone,
                'pco_expire_date': lambda x: UKDataValidator.validate_date(x, "PCO Expiry Date"),
                'pco_vehicle_expire_date': lambda x: UKDataValidator.validate_date(x, "PCO Vehicle Expiry Date"),
            }

            # Get form data
            form_data = {
                'drivername': request.form.get('drivername', ''),
                'email': request.form.get('email', ''),
                'phone': request.form.get('phone', ''),
                'pco_expire_date': request.form.get('pco_expire_date', ''),
                'pco_vehicle_expire_date': request.form.get('pco_vehicle_expire_date', ''),
            }

            # Validate form data
            is_valid, validated_data, errors = validate_form_data(form_data, validation_rules)

            if not is_valid:
                for error in errors:
                    flash(error, "danger")
                return redirect("/driver_details")

            # File upload handling with validation
            def save_all_file(field):
                file = request.files.get(field)
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    return url_for('static', filename=f"uploads/{filename}", _external=True)
                return None

            # Validate required files
            driving_licence = request.files.get('driving_licence')
            insurance_certificate = request.files.get('insurance_certificate')
            pco_licence_number = request.files.get('pco_licence_number')
            pco_vehicle_licence = request.files.get('pco_vehicle_licence')
            driver_photo = request.files.get('driver_photo')

            if not driving_licence or not driving_licence.filename:
                flash("Driving licence document is required", "danger")
                return redirect("/driver_details")

            if not insurance_certificate or not insurance_certificate.filename:
                flash("Insurance certificate document is required", "danger")
                return redirect("/driver_details")

            if not pco_licence_number or not pco_licence_number.filename:
                flash("PCO licence document is required", "danger")
                return redirect("/driver_details")

            if not pco_vehicle_licence or not pco_vehicle_licence.filename:
                flash("PCO vehicle licence document is required", "danger")
                return redirect("/driver_details")

            if not driver_photo or not driver_photo.filename:
                flash("Driver photo is required", "danger")
                return redirect("/driver_details")

            driver_data = {
                'drivername': validated_data['drivername'],
                "photo":save_all_file("driver_photo"),
                'email': validated_data['email'],
                'phone': validated_data['phone'],
                'pco_licence_number': save_all_file('pco_licence_number'),
                'national_insurance_number': request.form['national_insurance_number'],
                'pco_vehicle_licence': save_all_file('pco_vehicle_licence'),
                'car_register_number': request.form.get('car_register_number', ''),
                'pco_expire_date': validated_data['pco_expire_date'],
                'pco_vehicle_expire_date': validated_data['pco_vehicle_expire_date'],
                'driving_licence_url': save_all_file('driving_licence'),
                'insurance_certificate_url': save_all_file('insurance_certificate'),
                'vehicle_photos_urls': []
            }

            # Handle multiple vehicle photos
            vehicle_photos = request.files.getlist('vehicle_photos')
            for file in vehicle_photos:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    public_url = url_for('static', filename=f"uploads/{filename}", _external=True)
                    driver_data['vehicle_photos_urls'].append(public_url)

            # Generate unique ID
            all_driver_data = list(mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "driver_data"))
            allids = [driver_data_item["id"] for driver_data_item in all_driver_data]

            uid = str(uuid.uuid4())
            while uid in allids:
                uid = str(uuid.uuid4())

            driver_data["id"] = uid
            driver_data["is_assign"] = False
            driver_data["status"] = "active"
            driver_data["created_at"] = datetime.utcnow()
            driver_data["updated_at"] = datetime.utcnow()

            mongoOperation().insert_data_from_coll(client, "quickoo_uk", "driver_data", driver_data)
            flash("Driver added successfully", "success")
            return redirect("/driver_details")

    except Exception as e:
        print(f"{datetime.now()}: Error in add driver data route: {str(e)}")
        flash("An error occurred while adding driver", "danger")
        return redirect("/driver_details")


@app.route("/edit-driver", methods=["POST"])
@token_required
def edit_driver():
    try:
        uid = request.args.get("id", "")
        if not uid:
            flash("Driver ID is required", "danger")
            return redirect("/driver_details")

        # Define validation rules for driver editing
        validation_rules = {
            'drivername': lambda x: UKDataValidator.validate_name(x, "Driver Name"),
            'email': UKDataValidator.validate_email,
            'phone': UKDataValidator.validate_uk_phone,
            'national_insurance_number': UKDataValidator.validate_national_insurance,
            'car_register_number': UKDataValidator.validate_vehicle_registration,
        }

        # Get form data
        form_data = {
            'drivername': request.form.get('drivername', ''),
            'email': request.form.get('email', ''),
            'phone': request.form.get('phone', ''),
            'national_insurance_number': request.form.get('national_insurance_number', ''),
            'car_register_number': request.form.get('car_register_number', ''),
        }

        # Validate form data
        is_valid, validated_data, errors = validate_form_data(form_data, validation_rules)

        if not is_valid:
            for error in errors:
                flash(error, "danger")
            return redirect("/driver_details")

        driver_data = {
            'drivername': validated_data['drivername'],
            'email': validated_data['email'],
            'phone': validated_data['phone'],
            'national_insurance_number': validated_data['national_insurance_number'],
            'car_register_number': validated_data['car_register_number'],
            "updated_at": datetime.utcnow()
        }

        # Optional date fields with validation
        pco_expire_date = request.form.get('pco_expire_date', '').strip()
        if pco_expire_date:
            is_valid_date, validated_date = UKDataValidator.validate_date(pco_expire_date, "PCO Expiry Date")
            if is_valid_date:
                driver_data["pco_expire_date"] = validated_date
            else:
                flash(validated_date, "danger")
                return redirect("/driver_details")

        pco_vehicle_expire_date = request.form.get('pco_vehicle_expire_date', '').strip()
        if pco_vehicle_expire_date:
            is_valid_date, validated_date = UKDataValidator.validate_date(pco_vehicle_expire_date,
                                                                          "PCO Vehicle Expiry Date")
            if is_valid_date:
                driver_data["pco_vehicle_expire_date"] = validated_date
            else:
                flash(validated_date, "danger")
                return redirect("/driver_details")

        mongoOperation().update_mongo_data(client, "quickoo_uk", "driver_data", {"id": uid}, driver_data)
        flash("Driver updated successfully", "success")
        return redirect("/driver_details")

    except Exception as e:
        print(f"{datetime.now()}: Error in edit driver data route: {str(e)}")
        flash("An error occurred while updating driver", "danger")
        return redirect("/driver_details")


@app.route("/driver-status-update", methods=["GET"])
@token_required
def driver_status_update():
    try:
        uid = request.args.get("uid")
        status = request.args.get("status")

        if not uid or not status:
            flash("Missing driver ID or status", "danger")
            return redirect("/driver_details")

        if status not in ["active", "deactive"]:
            flash("Invalid status", "danger")
            return redirect("/driver_details")

        mongoOperation().update_mongo_data(client, "quickoo_uk", "driver_data", {"id": uid},
                                           {"status": status, "updated_at": datetime.utcnow()})
        flash("Status updated successfully", "success")
        return redirect("/driver_details")

    except Exception as e:
        print(f"{datetime.now()}: Error in updating driver status route: {str(e)}")
        flash("An error occurred while updating status", "danger")
        return redirect("/driver_details")


# Additional utility routes for validation
@app.route("/validate-phone", methods=["POST"])
@token_required
def validate_phone_ajax():
    """AJAX endpoint for real-time phone validation"""
    try:
        phone = request.json.get('phone', '')
        is_valid, result = UKDataValidator.validate_uk_phone(phone)
        return jsonify({
            'valid': is_valid,
            'message': result if not is_valid else 'Valid UK phone number',
            'formatted': result if is_valid else phone
        })
    except Exception as e:
        return jsonify({'valid': False, 'message': 'Validation error occurred'})


@app.route("/validate-email", methods=["POST"])
@token_required
def validate_email_ajax():
    """AJAX endpoint for real-time email validation"""
    try:
        email = request.json.get('email', '')
        is_valid, result = UKDataValidator.validate_email(email)
        return jsonify({
            'valid': is_valid,
            'message': result if not is_valid else 'Valid email address',
            'formatted': result if is_valid else email
        })
    except Exception as e:
        return jsonify({'valid': False, 'message': 'Validation error occurred'})


@app.route("/validate-postcode", methods=["POST"])
@token_required
def validate_postcode_ajax():
    """AJAX endpoint for real-time postcode validation"""
    try:
        postcode = request.json.get('postcode', '')
        is_valid, result = UKDataValidator.validate_postcode(postcode)
        return jsonify({
            'valid': is_valid,
            'message': result if not is_valid else 'Valid UK postcode',
            'formatted': result if is_valid else postcode
        })
    except Exception as e:
        return jsonify({'valid': False, 'message': 'Validation error occurred'})


@app.route("/validate-vat", methods=["POST"])
@token_required
def validate_vat_ajax():
    """AJAX endpoint for real-time VAT number validation"""
    try:
        vat = request.json.get('vat', '')
        is_valid, result = UKDataValidator.validate_vat_number(vat)
        return jsonify({
            'valid': is_valid,
            'message': result if not is_valid else 'Valid UK VAT number',
            'formatted': result if is_valid else vat
        })
    except Exception as e:
        return jsonify({'valid': False, 'message': 'Validation error occurred'})


@app.route("/validate-ni", methods=["POST"])
@token_required
def validate_ni_ajax():
    """AJAX endpoint for real-time National Insurance validation"""
    try:
        ni = request.json.get('ni', '')
        is_valid, result = UKDataValidator.validate_national_insurance(ni)
        return jsonify({
            'valid': is_valid,
            'message': result if not is_valid else 'Valid UK National Insurance number',
            'formatted': result if is_valid else ni
        })
    except Exception as e:
        return jsonify({'valid': False, 'message': 'Validation error occurred'})


@app.route("/validate-vehicle-reg", methods=["POST"])
@token_required
def validate_vehicle_reg_ajax():
    """AJAX endpoint for real-time vehicle registration validation"""
    try:
        reg = request.json.get('reg', '')
        is_valid, result = UKDataValidator.validate_vehicle_registration(reg)
        return jsonify({
            'valid': is_valid,
            'message': result if not is_valid else 'Valid UK vehicle registration',
            'formatted': result if is_valid else reg
        })
    except Exception as e:
        return jsonify({'valid': False, 'message': 'Validation error occurred'})


# Error handlers
@app.errorhandler(400)
def bad_request(error):
    flash("Bad request - please check your input", "danger")
    return redirect("/dashboard")


@app.errorhandler(404)
def not_found(error):
    flash("Page not found", "danger")
    return redirect("/dashboard")


@app.errorhandler(500)
def internal_error(error):
    flash("An internal error occurred", "danger")
    return redirect("/dashboard")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8060, debug=True)