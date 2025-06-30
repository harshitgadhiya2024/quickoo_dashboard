from operations.mongo_operation import mongoOperation
from operations.common_operations import commonOperation
from operations.mail_sending import emailOperation
from utils.constant import constant_dict
import os, json
from flask import (Flask, render_template, request, flash, session, send_file, jsonify, send_from_directory)
from flask_cors import CORS
from datetime import datetime, date
import uuid
from werkzeug.utils import secure_filename, redirect
from utils.html_format import htmlOperation

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
def dashboard():
    try:
        return render_template("index.html")

    except Exception as e:
        print(f"{datetime.now()}: Error in dashboard route: {str(e)}")
        return render_template("index.html")


@app.route("/booking_details", methods=["GET", "POST"])
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

        return render_template("booking-details.html", is_data=is_data, all_data=all_data, status_mapping=status_mapping_dict)

    except Exception as e:
        print(f"{datetime.now()}: Error in booking details route: {str(e)}")
        return render_template("booking-details.html")

@app.route("/add-ride-booking", methods=["POST"])
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
def vendor_details():
    try:
        is_data = True
        all_data = []
        status_mapping_dict = {
            "active": {"color": "btn-success", "status_list": ["deactive"]},
            "deactive": {"color": "btn-danger", "status_list": ["active"]},
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
def add_vender():
    try:
        vendername = request.form.get("vendername", "")
        vatno = request.form.get("vatno", "")
        tax = request.form.get("tax", "")

        if "%" not in tax:
            tax = str(tax) + "%"

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
def edit_vender():
    try:
        uid = request.args.get("id", "")
        vendername = request.form.get("vendername", "")
        vatno = request.form.get("vatno", "")
        tax = request.form.get("tax", "")

        if "%" not in tax:
            tax = str(tax) + "%"

        update_mapping_dict = {
            "vender_name": vendername,
            "vat_no": vatno,
            "tax": tax,
            "updated_at": datetime.utcnow()
        }

        mongoOperation().update_mongo_data(client, "quickoo_uk", "vender_data", {"id": uid}, update_mapping_dict)
        flash("Updated Successfully...", "success")
        return redirect("/vendor_details")

    except Exception as e:
        print(f"{datetime.now()}: Error in edit vender data route: {str(e)}")
        return redirect("/vendor_details")


@app.route("/vender-status-update", methods=["GET"])
def vender_status_update():
    try:
        uid = request.args.get("uid")
        mongoOperation().update_mongo_data(client, "quickoo_uk", "vender_data", {"id": uid}, {"status": "deactive", "updated_at": datetime.utcnow()})
        flash("Status update successfully", "success")
        return redirect("/vendor_details")

    except Exception as e:
        print(f"{datetime.now()}: Error in updating vender status route: {str(e)}")
        return redirect("/vendor_details")


@app.route("/driver_dashboard", methods=["GET", "POST"])
def driver_dashboard():
    try:
        return render_template("driver_dashboard.html")

    except Exception as e:
        print(f"{datetime.now()}: Error in login route: {str(e)}")
        return render_template("driver_dashboard.html")

@app.route("/employee_dashboard", methods=["GET", "POST"])
def employee_dashboard():
    try:
        return render_template("employee_dashboard.html")

    except Exception as e:
        print(f"{datetime.now()}: Error in login route: {str(e)}")
        return render_template("employee_dashboard.html")

@app.route("/employee_dashboard/booking", methods=["GET", "POST"])
def employee_booking():
    try:
        all_vehical_data = (mongoOperation().get_spec_data_from_coll(client, "car_rental", "vehical_data", {"is_ride": False, "is_active": True}))
        updated_vehical_data = []
        for vehical_data in all_vehical_data:
            del vehical_data["_id"]
            updated_vehical_data.append(vehical_data)
        return render_template("employee_booking.html", all_vehical_data=all_vehical_data)

    except Exception as e:
        print(f"{datetime.now()}: Error in employee_booking route: {str(e)}")
        return render_template("employee_booking.html")

@app.route("/vehical_book_now", methods=["GET", "POST"])
def vehical_book_now():
    try:
        employee_id = request.args.get("employee_id", "")
        vehical_id = request.args.get("vehical_id", "")
        pickup = request.args.get("pickup", "")
        drop = request.args.get("drop", "")
        mapping_dict = {
            "employee_id": employee_id,
            "vehical_id": vehical_id,
            "pickup": pickup,
            "drop": drop,
            "is_completed": False,
            "created_at": datetime.utcnow()
        }

        mongoOperation().insert_data_from_coll(client, "car_rental", "ride_booking", mapping_dict)
        return redirect("/employee_dashboard/booking")

    except Exception as e:
        print(f"{datetime.now()}: Error in vehical_book_now route: {str(e)}")
        return redirect("/employee_dashboard/booking")

@app.route("/company_panel/booking_request", methods=["GET", "POST"])
def company_booking_request():
    try:
        all_company_booking_data = list(mongoOperation().get_all_data_from_coll(client, "car_rental", "ride_booking"))
        updated_company_data = []
        for company_data in all_company_booking_data:
            del company_data["_id"]
            updated_company_data.append(company_data)

        all_company_booking_data1 = list(mongoOperation().get_spec_data_from_coll(client, "car_rental", "driver_data", {"is_ride": False, "is_active": True}))
        updated_company_data1 = []
        for company_data1 in all_company_booking_data1:
            del company_data1["_id"]
            updated_company_data1.append(company_data1)

        return render_template("booking_request.html", all_company_booking_data=updated_company_data, all_company_booking_data1=all_company_booking_data1)

    except Exception as e:
        print(f"{datetime.now()}: Error in vehical_book_now route: {str(e)}")
        return render_template("booking_request.html", all_company_booking_data=updated_company_data)

@app.route("/logout", methods=["GET", "POST"])
def logout():
    try:
        session.clear()
        return redirect("/")

    except Exception as e:
        print(f"{datetime.now()}: Error in logout route: {str(e)}")
        return redirect("/")


@app.route("/company_dashboard", methods=["GET", "POST"])
def company_dashboard():
    try:
        return render_template("company_dashboard.html")

    except Exception as e:
        print(f"{datetime.now()}: Error in login route: {str(e)}")
        return render_template("company_dashboard.html")

@app.route("/company", methods=["GET", "POST"])
def company():
    try:
        all_company_data = list(mongoOperation().get_all_data_from_coll(client, "car_rental", "company_data"))
        updated_company_data = []
        for company_data in all_company_data:
            del company_data["_id"]
            updated_company_data.append(company_data)

        if request.method=="POST":
            company_name = request.form.get("company_name")
            email = request.form.get("email")
            phone = request.form.get("phone")
            pancard = request.form.get("pancard")
            gst_no = request.form.get("gst_no")
            password = request.form.get("password")
            address = request.form.get("address")
            company_id = str(uuid.uuid4())
            mapping_dict = {
                "id": company_id,
                "company_name": company_name,
                "email": email,
                "phone": phone,
                "pancard": pancard,
                "gst_no": gst_no,
                "password": password,
                "address": address,
                "is_active": True,
                "type": "company",
                "created_at": datetime.utcnow()
            }
            login_mapping_dict = {
                "id": company_id,
                "email": email,
                "password": password,
                "is_active": True,
                "type": "company",
                "created_at": datetime.utcnow()
            }
            mongoOperation().insert_data_from_coll(client, "car_rental", "company_data", mapping_dict)
            mongoOperation().insert_data_from_coll(client, "car_rental", "login_data", login_mapping_dict)
            return redirect("/company")
        else:
            return render_template("company_data.html", updated_company_data=updated_company_data)

    except Exception as e:
        print(f"{datetime.now()}: Error in company data route: {str(e)}")
        return render_template("company_data.html")

@app.route("/superadmin", methods=["GET", "POST"])
def superadmin():
    try:
        all_superadmin_data = (mongoOperation().get_all_data_from_coll(client, "car_rental", "superadmin_data"))
        updated_superadmin_data = []
        for superadmin_data in all_superadmin_data:
            del superadmin_data["_id"]
            updated_superadmin_data.append(superadmin_data)

        if request.method=="POST":
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")
            superadmin_id = str(uuid.uuid4())
            mapping_dict = {
                "id": superadmin_id,
                "name": name,
                "email": email,
                "password": password,
                "is_active": True,
                "type": "superadmin",
                "created_at": datetime.utcnow()
            }
            login_mapping_dict = {
                "id": superadmin_id,
                "email": email,
                "password": password,
                "is_active": True,
                "type": "superadmin",
                "created_at": datetime.utcnow()
            }
            mongoOperation().insert_data_from_coll(client, "car_rental", "superadmin_data", mapping_dict)
            mongoOperation().insert_data_from_coll(client, "car_rental", "login_data", login_mapping_dict)
            return redirect("/superadmin")
        else:
            return render_template("superadmin.html", updated_superadmin_data=updated_superadmin_data)

    except Exception as e:
        print(f"{datetime.now()}: Error in superadmin data route: {str(e)}")
        return render_template("superadmin.html")

@app.route("/vehical", methods=["GET", "POST"])
def vehical():
    try:
        all_vehical_data = (mongoOperation().get_all_data_from_coll(client, "car_rental", "vehical_data"))
        updated_vehical_data = []
        for vehical_data in all_vehical_data:
            del vehical_data["_id"]
            updated_vehical_data.append(vehical_data)

        if request.method=="POST":
            vehical_name = request.form.get("vehical_name")
            vehical_type = request.form.get("vehical_type")
            number_plat = request.form.get("number_plat")
            seating_capsity = request.form.get("seating_capsity")
            vehical_id = str(uuid.uuid4())
            mapping_dict = {
                "id": vehical_id,
                "vehical_name": vehical_name,
                "vehical_type": vehical_type,
                "number_plat": number_plat,
                "seating_capsity": int(seating_capsity),
                "is_ride": False,
                "is_active": True,
                "type": "vehical",
                "created_at": datetime.utcnow()
            }

            mongoOperation().insert_data_from_coll(client, "car_rental", "vehical_data", mapping_dict)
            return redirect("/vehical")
        else:
            return render_template("vehical.html", updated_vehical_data=updated_vehical_data)

    except Exception as e:
        print(f"{datetime.now()}: Error in vehical data route: {str(e)}")
        return render_template("vehical.html")

@app.route("/driver", methods=["GET", "POST"])
def driver():
    try:
        all_driver_data = (mongoOperation().get_all_data_from_coll(client, "car_rental", "driver_data"))
        updated_driver_data = []
        for driver_data in all_driver_data:
            del driver_data["_id"]
            updated_driver_data.append(driver_data)

        if request.method=="POST":
            driver_name = request.form.get("driver_name")
            email = request.form.get("email")
            phone = request.form.get("phone")
            password = request.form.get("password")
            driving_licence_no = request.form.get("driving_licence_no")

            driver_id = str(uuid.uuid4())
            mapping_dict = {
                "id": driver_id,
                "driver_name": driver_name,
                "email": email,
                "phone": phone,
                "password": password,
                "driving_licence": driving_licence_no,
                "is_ride": False,
                "is_active": True,
                "type": "driver",
                "created_at": datetime.utcnow()
            }
            login_mapping_dict = {
                "id": driver_id,
                "email": email,
                "password": password,
                "is_active": True,
                "type": "driver",
                "created_at": datetime.utcnow()
            }
            mongoOperation().insert_data_from_coll(client, "car_rental", "driver_data", mapping_dict)
            mongoOperation().insert_data_from_coll(client, "car_rental", "login_data", login_mapping_dict)
            return redirect("/driver")
        else:
            return render_template("driver.html", all_driver_data=all_driver_data)

    except Exception as e:
        print(f"{datetime.now()}: Error in driver data route: {str(e)}")
        return render_template("driver.html")

@app.route("/company_panel/employee", methods=["GET", "POST"])
def company_panel():
    try:
        all_company_data = list(mongoOperation().get_all_data_from_coll(client, "car_rental", "employee_data"))
        all_employee_data = []
        for company_data in all_company_data:
            del company_data["_id"]
            all_employee_data.append(company_data)

        if request.method=="POST":
            name = request.form.get("name")
            email = request.form.get("email")
            phone = request.form.get("phone")
            password = request.form.get("password")
            company_id = str(uuid.uuid4())
            mapping_dict = {
                "id": company_id,
                "name": name,
                "email": email,
                "phone": phone,
                "password": password,
                "is_active": True,
                "type": "employee",
                "created_at": datetime.utcnow()
            }
            login_mapping_dict = {
                "id": company_id,
                "email": email,
                "password": password,
                "is_active": True,
                "type": "employee",
                "created_at": datetime.utcnow()
            }
            mongoOperation().insert_data_from_coll(client, "car_rental", "employee_data", mapping_dict)
            mongoOperation().insert_data_from_coll(client, "car_rental", "login_data", login_mapping_dict)
            return redirect("/company_panel/employee")
        else:
            return render_template("employee_data.html", all_employee_data=all_employee_data)

    except Exception as e:
        print(f"{datetime.now()}: Error in all_employee_data data route: {str(e)}")
        return render_template("employee_data.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8060)
