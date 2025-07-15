from operations.mongo_operation import mongoOperation
from operations.common_operations import commonOperation
from operations.mail_sending import emailOperation
from utils.constant import constant_dict
import os, json
from flask import (Flask, render_template, request, flash, session, send_file, jsonify, send_from_directory, url_for)
from flask_cors import CORS
from datetime import datetime, date
import uuid
from werkzeug.utils import secure_filename, redirect
from utils.html_format import htmlOperation
from functools import wraps

app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = constant_dict.get("secreat_key")
UPLOAD_FOLDER = 'static/uploads/'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Utility to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


client = mongoOperation().mongo_connect(get_mongourl=constant_dict.get("mongo_url"))

def token_required(func):
    # decorator factory which invoks update_wrapper() method and passes decorated function as an argument
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
        if request.method=="POST":
            email = request.form["email"]
            password = request.form["password"]
            all_data = list(mongoOperation().get_spec_data_from_coll(client, "quickoo_uk", "login_mapping", {"email": email, "password": password}))
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
        return render_template("login.html")

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    try:
        if request.method=="POST":
            email = request.form["email"]
            email_condition_dict = {"email": email}
            email_data = mongoOperation().get_spec_data_from_coll(client, "quickoo_uk", "login_mapping", email_condition_dict)
            if email_data:
                if email_data[0]["is_active"]:
                    forgot_password_link = f"http://127.0.0.1:5000/reset-password?email={email}"
                    html_format = htmlOperation().forgot_password_mail_template(forgot_password_link)
                    emailOperation().send_email(email, "Quickoo: Your Account Verification Code", html_format)
                    flash("Reset link sent successfully. Please check your mail", "success")
                    return redirect("/")
                else:
                    flash("Your account was disabled, Contact administration", "danger")
                    return redirect("/forgot-password")
            else:
                flash("Account not exits", "danger")
                return redirect("/forgot-password")
        else:
            return render_template("forgot-password.html")

    except Exception as e:
        print(f"{datetime.now()}: Error in forgot-password route: {str(e)}")
        return render_template("forgot-password.html")

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    try:
        email = request.args.get("email")
        if request.method=="POST":
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")
            if password==confirm_password:
                # mongoOperation().update_mongo_data(client, "quickoo_uk", "user_data", {"user_id":user_id}, {"password": password})
                mongoOperation().update_mongo_data(client, "quickoo_uk", "login_mapping", {"email":email}, {"password": password})
                flash("Password updated", "success")
                return redirect("/")
            else:
                flash("Password doesn't match", "danger")
                return redirect(f"/reset-password?email={email}")
        else:
            return render_template("reset-password.html", email = email)

    except Exception as e:
        print(f"{datetime.now()}: Error in reset-password route: {str(e)}")
        return render_template("reset-password.html")


@app.route("/dashboard", methods=["GET", "POST"])
@token_required
def dashboard():
    try:
        return render_template("index.html")

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

        all_driver_data = list(mongoOperation().get_spec_data_from_coll(client, "quickoo_uk", "driver_data", {"status": "active", "is_assign": False}))
        all_updated_data = []
        for driver in all_driver_data:
            all_updated_data.append({"id": driver["id"], "name": driver["drivername"]})

        return render_template("booking-details.html", is_data=is_data, all_data=all_data, status_mapping=status_mapping_dict, all_driver=all_updated_data)

    except Exception as e:
        print(f"{datetime.now()}: Error in booking details route: {str(e)}")
        return render_template("booking-details.html")

@app.route("/assign-driver", methods=["GET"])
@token_required
def assign_driver():
    try:
        ride_id = request.args.get("rideid")
        driver_id = request.args.get("driverid")
        mongoOperation().update_mongo_data(client, "quickoo_uk", "booking_data", {"id": ride_id}, {"driver_id": driver_id, "updated_at": datetime.utcnow()})
        mongoOperation().update_mongo_data(client, "quickoo_uk", "driver_data", {"id": driver_id}, {"is_assign": True, "updated_at": datetime.utcnow()})
        flash("Driver assign successfully...", "success")
        return {"message": "driver assign successfully"}

    except Exception as e:
        print(f"{datetime.now()}: Error in assign driver route: {str(e)}")
        return render_template("booking-details.html")

@app.route("/add-ride-booking", methods=["POST"])
@token_required
def add_book_riding():
    try:
        full_name = request.form.get("fullname", "")
        phone = request.form.get("phone", "")
        email = request.form.get("email", "")
        service_type = request.form.get("service_type", "")
        pickup = request.form.get("pickup", "")
        drop = request.form.get("drop", "")
        shoffr_class = request.form.get("shoffr_class", "")
        pickupdate = request.form.get("pickupdate", "")
        pickuptime = request.form.get("pickuptime", "")
        flightinfo = request.form.get("flightinfo", "")
        baginfo = request.form.get("baginfo", "")
        note = request.form.get("note", "")

        if "+31" not in phone:
            phone = "+31 " + str(phone)

        all_company_booking_data = list(mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "booking_data"))
        allids = [booking_data["id"] for booking_data in all_company_booking_data]
        uid = str(uuid.uuid4())

        flag = True
        while flag:
            uid = str(uuid.uuid4())
            if uid not in allids:
                flag = False

        mapping_dict = {
            "id": uid,
            "driver_id": "",
            "full_name": full_name,
            "phone": phone,
            "email": email,
            "pickup": pickup,
            "drop": drop,
            "date": pickupdate,
            "time": pickuptime,
            "service_type": service_type,
            "shoffr_class": shoffr_class,
            "flight_info": flightinfo,
            "bag_info": baginfo,
            "note": note,
            "status": "waiting",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        mongoOperation().insert_data_from_coll(client, "quickoo_uk", "booking_data", mapping_dict)
        flash("Booking successfully...", "success")
        return redirect("/booking_details")

    except Exception as e:
        print(f"{datetime.now()}: Error in add booking data route: {str(e)}")
        return redirect("/booking_details")

@app.route("/ride-status-update", methods=["GET"])
@token_required
def ride_status_update():
    try:
        uid = request.args.get("uid")
        status = request.args.get("status")
        print(uid, status)
        mongoOperation().update_mongo_data(client, "quickoo_uk", "booking_data", {"id": uid}, {"status": status, "updated_at": datetime.utcnow()})
        flash("Status update successfully", "success")
        return redirect("/booking_details")

    except Exception as e:
        print(f"{datetime.now()}: Error in updating booking status route: {str(e)}")
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

        return render_template("vender-details.html", all_data=all_data, is_data=is_data, status_mapping=status_mapping_dict)

    except Exception as e:
        print(f"{datetime.now()}: Error in vender details route: {str(e)}")
        return render_template("vender-details.html")

@app.route("/add-vender", methods=["POST"])
@token_required
def add_vender():
    try:
        vendername = request.form.get("vendername", "")
        vatno = request.form.get("vatno", "")
        tax = request.form.get("tax", "")
        phone = request.form.get("phone", "")
        email = request.form.get("email", "")

        if "%" not in tax:
            tax = str(tax) + "%"

        if "+31" not in phone:
            phone = "+31" + str(phone)

        all_vender_data = list(mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "vender_data"))
        allids = [vender_data["id"] for vender_data in all_vender_data]
        uid = str(uuid.uuid4())

        flag = True
        while flag:
            uid = str(uuid.uuid4())
            if uid not in allids:
                flag = False

        mapping_dict = {
            "id": uid,
            "vender_name": vendername,
            "vat_no": vatno,
            "tax": tax,
            "email": email,
            "phone": phone,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        mongoOperation().insert_data_from_coll(client, "quickoo_uk", "vender_data", mapping_dict)
        flash("Added successfully...", "success")
        return redirect("/vendor_details")

    except Exception as e:
        print(f"{datetime.now()}: Error in add vender data route: {str(e)}")
        return redirect("/vendor_details")

@app.route("/edit-vender", methods=["POST"])
@token_required
def edit_vender():
    try:
        uid = request.args.get("id", "")
        vendername = request.form.get("vendername", "")
        vatno = request.form.get("vatno", "")
        tax = request.form.get("tax", "")
        phone = request.form.get("phone", "")
        email = request.form.get("email", "")

        if "%" not in tax:
            tax = str(tax) + "%"

        update_mapping_dict = {
            "vender_name": vendername,
            "vat_no": vatno,
            "tax": tax,
            "email": email,
            "phone": phone,
            "updated_at": datetime.utcnow()
        }

        mongoOperation().update_mongo_data(client, "quickoo_uk", "vender_data", {"id": uid}, update_mapping_dict)
        flash("Updated Successfully...", "success")
        return redirect("/vendor_details")

    except Exception as e:
        print(f"{datetime.now()}: Error in edit vender data route: {str(e)}")
        return redirect("/vendor_details")

@app.route("/vender-status-update", methods=["GET"])
@token_required
def vender_status_update():
    try:
        uid = request.args.get("uid")
        status = request.args.get("status")
        mongoOperation().update_mongo_data(client, "quickoo_uk", "vender_data", {"id": uid}, {"status": status, "updated_at": datetime.utcnow()})
        flash("Status update successfully", "success")
        return redirect("/vendor_details")

    except Exception as e:
        print(f"{datetime.now()}: Error in updating vender status route: {str(e)}")
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

        return render_template("driver-details.html", all_data=all_data, is_data=is_data, status_mapping=status_mapping_dict)

    except Exception as e:
        print(f"{datetime.now()}: Error in driver details route: {str(e)}")
        return render_template("driver-details.html")

@app.route("/add-driver", methods=["POST"])
@token_required
def add_driver():
    try:
        if request.method == 'POST':
            # Save file and return public URL
            def save_all_file(field):
                file = request.files.get(field)
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    return url_for('static', filename=f"uploads/{filename}", _external=True)
                return None

            driver_data = {
                'drivername': request.form.get('drivername'),
                'email': request.form.get('email'),
                'phone': request.form.get('phone'),
                'pco_licence_number': request.form.get('pco_licence_number'),
                'national_insurance_number': request.form.get('national_insurance_number'),
                'pco_vehicle_licence': request.form.get('pco_vehicle_licence'),
                'car_register_number': request.form.get('car_register_number'),
                'pco_expire_date': request.form.get('pco_expire_date'),
                'pco_vehicle_expire_date': request.form.get('pco_vehicle_expire_date'),
                'driving_licence_url': save_all_file('driving_licence'),
                'insurance_certificate_url': save_all_file('insurance_certificate'),
                'vehicle_photos_urls': []
            }

            phone = request.form.get('phone')
            if "+31" not in phone:
                phone = "+31" + phone
                driver_data["phone"] = phone

            # Handle multiple vehicle photos
            vehicle_photos = request.files.getlist('vehicle_photos')
            for file in vehicle_photos:
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    public_url = url_for('static', filename=f"uploads/{filename}", _external=True)
                    driver_data['vehicle_photos_urls'].append(public_url)

            all_driver_data = list(mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "driver_data"))
            allids = [driver_data["id"] for driver_data in all_driver_data]
            uid = str(uuid.uuid4())

            flag = True
            while flag:
                uid = str(uuid.uuid4())
                if uid not in allids:
                    flag = False

            driver_data["id"] = uid
            driver_data["is_assign"] = False
            driver_data["status"] = "active"
            driver_data["created_at"] = datetime.utcnow()
            driver_data["updated_at"] = datetime.utcnow()

            mongoOperation().insert_data_from_coll(client, "quickoo_uk", "driver_data", driver_data)
            flash("Added successfully...", "success")
            return redirect("/driver_details")

    except Exception as e:
        print(f"{datetime.now()}: Error in add driver data route: {str(e)}")
        return redirect("/driver_details")

@app.route("/edit-driver", methods=["POST"])
@token_required
def edit_driver():
    try:
        uid = request.args.get("id", "")

        driver_data = {
            'drivername': request.form.get('drivername'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'pco_licence_number': request.form.get('pco_licence_number'),
            'national_insurance_number': request.form.get('national_insurance_number'),
            'pco_vehicle_licence': request.form.get('pco_vehicle_licence'),
            'car_register_number': request.form.get('car_register_number'),
            "updated_at": datetime.utcnow()
        }

        if request.form.get('pco_expire_date'):
            driver_data["pco_expire_date"] = request.form.get('pco_expire_date')

        if request.form.get('pco_vehicle_expire_date'):
            driver_data["pco_vehicle_expire_date"] = request.form.get('pco_vehicle_expire_date')


        phone = request.form.get('phone')
        if "+31" not in phone:
            phone = "+31" + phone
            driver_data["phone"] = phone

        mongoOperation().update_mongo_data(client, "quickoo_uk", "driver_data", {"id": uid}, driver_data)
        flash("Updated Successfully...", "success")
        return redirect("/driver_details")

    except Exception as e:
        print(f"{datetime.now()}: Error in edit driver data route: {str(e)}")
        return redirect("/driver_details")

@app.route("/driver-status-update", methods=["GET"])
@token_required
def driver_status_update():
    try:
        uid = request.args.get("uid")
        status = request.args.get("status")
        mongoOperation().update_mongo_data(client, "quickoo_uk", "driver_data", {"id": uid}, {"status": status, "updated_at": datetime.utcnow()})
        flash("Status update successfully", "success")
        return redirect("/driver_details")

    except Exception as e:
        print(f"{datetime.now()}: Error in updating driver status route: {str(e)}")
        return redirect("/driver_details")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8060, debug=True)
