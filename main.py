from doctest import debug

from operations.mongo_operation import mongoOperation
from operations.common_operations import commonOperation
from utils.constant import constant_dict
import os, json
from flask import (Flask, render_template, request, flash, session, send_file, jsonify, send_from_directory)
from flask_cors import CORS
from datetime import datetime, date
import uuid
from werkzeug.utils import secure_filename, redirect

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

#
# @app.route("/quickoo/register-user", methods=["POST"])
# def register_user():
#     try:
#         first_name = request.form["first_name"]
#         dob = request.form["dob"]
#         gender = request.form["gender"]
#         password = request.form["password"]
#         email = request.form.get("email", "")
#         phone_number = request.form.get("phone_number", "")
#         if email:
#             is_email = True
#         else:
#             is_email = False
#
#         if phone_number:
#             is_phone = True
#         else:
#             is_phone = False
#
#         get_all_user_data = mongoOperation().get_all_data_from_coll(client, "quickoo", "user_data")
#         all_userids = [user_data["user_id"] for user_data in get_all_user_data]
#
#         flag = True
#         user_id = ""
#         while flag:
#             user_id = str(uuid.uuid4())
#             if user_id not in all_userids:
#                 flag = False
#
#         mapping_dict = {
#             "user_id": user_id,
#             "first_name": first_name,
#             "profile_url": "",
#             "dob": dob,
#             "gender": gender,
#             "password": password,
#             "email": email,
#             "phone_number": phone_number,
#             "bio": "",
#             "vehicle_details": {},
#             "payment_details": {},
#             "is_profile": False,
#             "is_vehicle": False,
#             "is_email": is_email,
#             "is_bio": False,
#             "is_phone": is_phone,
#             "is_payment": False,
#             "is_verified": False,
#             "is_active": True,
#             "type": "email",
#             "created_at": datetime.utcnow(),
#             "updated_at": datetime.utcnow()
#         }
#
#         mongoOperation().insert_data_from_coll(client, "quickoo", "user_data", mapping_dict)
#         response_data_msg = commonOperation().get_success_response(200, {"user_id": mapping_dict["user_id"]})
#         return response_data_msg
#
#     except Exception as e:
#         response_data = commonOperation().get_error_msg("Please try again..")
#         print(f"{datetime.utcnow()}: Error in register user data route: {str(e)}")
#         return response_data
#
#
# @app.route("/quickoo/google-auth", methods=["POST"])
# def google_auth():
#     try:
#         first_name = request.form.get("first_name", "")
#         profile_url = request.form.get("profile_url", "")
#         email = request.form.get("email", "")
#         if profile_url:
#             is_profile = True
#         else:
#             is_profile = False
#
#         get_all_user_data = mongoOperation().get_all_data_from_coll(client, "quickoo", "user_data")
#         all_userids = [user_data["user_id"] for user_data in get_all_user_data]
#         for user_data in get_all_user_data:
#             if email == user_data["email"]:
#                 response_data_msg = commonOperation().get_success_response(200, {"user_id": user_data["user_id"]})
#                 return response_data_msg
#
#         flag = True
#         user_id = ""
#         while flag:
#             user_id = str(uuid.uuid4())
#             if user_id not in all_userids:
#                 flag = False
#
#         mapping_dict = {
#             "user_id": user_id,
#             "first_name": first_name,
#             "profile_url": profile_url,
#             "dob": "",
#             "gender": "",
#             "password": "",
#             "email": email,
#             "phone_number": "",
#             "bio": "",
#             "vehicle_details": {},
#             "payment_details": {},
#             "is_profile": is_profile,
#             "is_vehicle": False,
#             "is_email": True,
#             "is_bio": False,
#             "is_phone": False,
#             "is_payment": False,
#             "is_verified": False,
#             "is_active": True,
#             "type": "google",
#             "created_at": datetime.utcnow(),
#             "updated_at": datetime.utcnow()
#         }
#
#         mongoOperation().insert_data_from_coll(client, "quickoo", "user_data", mapping_dict)
#         response_data_msg = commonOperation().get_success_response(200, {"user_id": mapping_dict["user_id"]})
#         return response_data_msg
#
#     except Exception as e:
#         response_data = commonOperation().get_error_msg("Please try again..")
#         print(f"{datetime.utcnow()}: Error in register user data route: {str(e)}")
#         return response_data
#
#
# @app.route("/quickoo/get-user-data", methods=["POST"])
# def get_user_data():
#     try:
#         user_id = request.form["user_id"]
#         get_all_user_data = list(
#             mongoOperation().get_spec_data_from_coll(client, "quickoo", "user_data", {"user_id": user_id}))
#         response_data = get_all_user_data[0]
#         del response_data["_id"]
#         del response_data["created_at"]
#         del response_data["updated_at"]
#         response_data_msg = commonOperation().get_success_response(200, response_data)
#         return response_data_msg
#
#     except Exception as e:
#         response_data = commonOperation().get_error_msg("Please try again..")
#         print(f"{datetime.utcnow()}: Error in register user data route: {str(e)}")
#         return response_data
#
#
# @app.route("/quickoo/otp-email-verification", methods=["POST"])
# def otp_email_verification():
#     try:
#         otp = request.form["otp"]
#         email = request.form["email"]
#         get_all_user_data = mongoOperation().get_all_data_from_coll(client, "quickoo", "user_data")
#         all_emails = [user_data["email"] for user_data in get_all_user_data]
#         if email in all_emails:
#             return commonOperation().get_error_msg("Email already registered...")
#
#         html_format = htmlOperation().otp_verification_process(otp)
#         emailOperation().send_email(email, "Quickoo: Your Account Verification Code", html_format)
#         response_data = commonOperation().get_success_response(200, {"message": "Mail sent successfully..."})
#         return response_data
#
#     except Exception as e:
#         response_data = commonOperation().get_error_msg("Please try again...")
#         print(f"{datetime.now()}: Error in otp email verification: {str(e)}")
#         return response_data
#
#

@app.route("/", methods=["GET", "POST"])
def login():
    try:
        if request.method=="POST":
            email = request.form["email"]
            password = request.form["password"]
            all_data = list(mongoOperation().get_spec_data_from_coll(client, "car_rental", "login_data", {"email": email, "password": password}))
            if all_data:
                is_active = all_data[0]["is_active"]
                if is_active:
                    user_type = all_data[0]["type"]
                    if user_type=="company":
                        return redirect("/company_dashboard")
                    elif user_type=="driver":
                        return redirect("/driver_dashboard")
                    elif user_type=="employee":
                        return redirect("/employee_dashboard")
                    else:
                        return redirect("/dashboard")
                else:
                    flash("Please active your account")
                    return redirect("/")
            else:
                flash("Please enter correct credentials")
                return redirect("/")
        else:
            return render_template("login.html")

    except Exception as e:
        print(f"{datetime.now()}: Error in login route: {str(e)}")
        return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    try:
        return render_template("index.html")

    except Exception as e:
        print(f"{datetime.now()}: Error in login route: {str(e)}")
        return render_template("index.html")

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
        all_company_data = (mongoOperation().get_all_data_from_coll(client, "car_rental", "company_data"))
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


#
# @app.route("/quickoo/forgot-password", methods=["POST"])
# def forgot_password():
#     try:
#         email = request.form["email"]
#         otp = request.form["otp"]
#         email_condition_dict = {"email": email}
#         email_data = mongoOperation().get_spec_data_from_coll(client, "quickoo", "user_data", email_condition_dict)
#         if email_data:
#             if email_data[0]["is_active"]:
#                 html_format = htmlOperation().otp_verification_process(otp)
#                 emailOperation().send_email(email, "Quickoo: Your Account Verification Code", html_format)
#                 return commonOperation().get_success_response(200, {"message": "Account Exits..",
#                                                                     "user_id": email_data[0]["user_id"]})
#             else:
#                 return commonOperation().get_error_msg("Your account was disabled, Contact administration")
#         else:
#             response_data = commonOperation().get_error_msg("Account not exits..")
#         return response_data
#
#     except Exception as e:
#         response_data = commonOperation().get_error_msg("Please try again...")
#         print(f"{datetime.now()}: Error in forgot password route: {str(e)}")
#         return response_data
#
#
# @app.route("/quickoo/change-password", methods=["POST"])
# def change_password():
#     try:
#         password = request.form["password"]
#         confirm_password = request.form["confirm_password"]
#         user_id = request.args.get("user_id")
#         if password == confirm_password:
#             mongoOperation().update_mongo_data(client, "quickoo", "user_data", {"user_id": user_id},
#                                                {"password": password})
#             return commonOperation().get_success_response(200, {"message": "Password updated"})
#         else:
#             return commonOperation().get_error_msg("Password doesn't match...")
#
#     except Exception as e:
#         response_data = commonOperation().get_error_msg("Please try again...")
#         print(f"{datetime.now()}: Error in change password route: {str(e)}")
#         return response_data
#
#
# @app.route("/quickoo/update-user-data", methods=["POST"])
# def update_user_data():
#     try:
#         first_name = request.form.get("first_name")
#         dob = request.form.get("dob")
#         email = request.form.get("email", "")
#         phone_number = request.form.get("phone_number", "")
#         user_id = request.form.get("user_id", "")
#
#         if first_name:
#             mongoOperation().update_mongo_data(client, "quickoo", "user_data", {"user_id": user_id},
#                                                {"first_name": first_name})
#             return commonOperation().get_success_response(200, {"message": "Name updated successfully..."})
#         elif dob:
#             mongoOperation().update_mongo_data(client, "quickoo", "user_data", {"user_id": user_id}, {"dob": dob})
#             return commonOperation().get_success_response(200, {"message": "Date of birth updated successfully..."})
#         elif email:
#             mongoOperation().update_mongo_data(client, "quickoo", "user_data", {"user_id": user_id},
#                                                {"email": email, "is_email": True})
#             return commonOperation().get_success_response(200, {"message": "Email updated successfully..."})
#         elif phone_number:
#             mongoOperation().update_mongo_data(client, "quickoo", "user_data", {"user_id": user_id},
#                                                {"phone_number": phone_number, "is_phone": True})
#             return commonOperation().get_success_response(200, {"message": "Phone number updated successfully..."})
#         else:
#             return commonOperation().get_error_msg("Something won't wrong!")
#
#     except Exception as e:
#         response_data = commonOperation().get_error_msg("Please try again...")
#         print(f"{datetime.now()}: Error in updare user data route: {str(e)}")
#         return response_data
#
#
# @app.route("/quickoo/get-cities-for-location", methods=["POST"])
# def get_cities_for_locations():
#     try:
#         from_location = request.form.get("from")
#         to_location = request.form.get("to")
#         cities = MapsIntegration().find_cities_along_route(from_location, to_location, sample_points=20)
#         return commonOperation().get_success_response(200, cities)
#
#     except Exception as e:
#         response_data = commonOperation().get_error_msg("Please try again...")
#         print(f"{datetime.now()}: Error in updare user data route: {str(e)}")
#         return response_data

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
