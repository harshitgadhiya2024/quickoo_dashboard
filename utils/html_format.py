from datetime import datetime


class htmlOperation():

    def __init__(self):
        pass

    def otp_verification_process(self, otp):
        try:
            otp_verification = """
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Quickoo - Your OTP Verification</title>
                    <style>
                        body {
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            margin: 0;
                            padding: 0;
                            background-color: #f5f5f5;
                        }
                        .container {
                            max-width: 600px;
                            margin: 0 auto;
                            padding: 20px;
                            background-color: #f2f2f2;
                            box-shadow: 1px 1px 5px #2c3e50;
                        }
                        .header {
                            text-align: center;
                            padding: 20px 0;
                            border-bottom: 1px solid #eeeeee;
                        }
                        .logo {
                            font-size: 32px;
                            font-weight: bold;
                            color: #2c3e50;
                        }
                        .logo span {
                            color: #e74c3c;
                        }
                        .content {
                            padding: 30px 20px;
                            color: #333333;
                        }
                        .otp-container {
                            margin: 30px 0;
                            text-align: center;
                        }
                        .otp-code {
                            font-size: 32px;
                            font-weight: bold;
                            letter-spacing: 8px;
                            padding: 15px 25px;
                            background-color: #f8f9fa;
                            border-radius: 8px;
                            color: #2c3e50;
                            display: inline-block;
                        }
                        .footer {
                            padding: 20px;
                            text-align: center;
                            font-size: 12px;
                            color: #777777;
                            border-top: 1px solid #eeeeee;
                        }
                        .social-icons {
                            margin: 15px 0;
                        }
                        .social-icon {
                            display: inline-block;
                            margin: 0 10px;
                            width: 30px;
                            height: 30px;
                            background-color: #2c3e50;
                            border-radius: 50%;
                            color: white;
                            line-height: 30px;
                            text-align: center;
                        }
                        .note {
                            padding: 15px;
                            background-color: #f8f9fa;
                            border-left: 4px solid #e74c3c;
                            margin: 20px 0;
                        }
                        @media only screen and (max-width: 600px) {
                            .container {
                                width: 100%;
                            }
                            .otp-code {
                                font-size: 24px;
                            }
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <div class="logo">Quick<span>oo</span></div>
                        </div>
                        <div class="content">
                            <h2>Verify Your Account</h2>
                            <p>Hello there,</p>
                            <p>Thank you for choosing Quickoo! Please use the verification code below to complete your account verification process:</p>

                            <div class="otp-container">
                                <div class="otp-code">""" + otp + """</div>
                            </div>

                            <p>This code will expire in <strong>10 minutes</strong>.</p>

                            <div class="note">
                                <p><strong>Security Note:</strong> If you didn't request this code, please ignore this email or contact our support team immediately.</p>
                            </div>

                            <p>If you have any questions or need assistance, our customer support team is always here to help.</p>

                            <p>Best Regards,<br>The Quickoo Team</p>
                        </div>
                        <div class="footer">
                            <p>&copy; 2025 Quickoo. All rights reserved.</p>
                            <p>This is an automated message, please do not reply to this email.</p>
                        </div>
                    </div>
                </body>
                </html>
                """

            return otp_verification

        except Exception as e:
            print(f"{datetime.now()}: Error in getting otp verification html format: {str(e)}")

    def forgot_password_mail_template(self, reset_link):
        try:
            forgot_password_html = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Quickoo - Reset Your Password</title>
                    <style>
                        body {{
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            margin: 0;
                            padding: 0;
                            background-color: #f5f5f5;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 0 auto;
                            padding: 20px;
                            background-color: #f2f2f2;
                            box-shadow: 1px 1px 5px #2c3e50;
                        }}
                        .header {{
                            text-align: center;
                            padding: 20px 0;
                            border-bottom: 1px solid #eeeeee;
                        }}
                        .logo {{
                            font-size: 32px;
                            font-weight: bold;
                            color: #2c3e50;
                        }}
                        .logo span {{
                            color: #e74c3c;
                        }}
                        .content {{
                            padding: 30px 20px;
                            color: #333333;
                        }}
                        .button {{
                            display: inline-block;
                            padding: 12px 25px;
                            background-color: #2c3e50;
                            color: #ffffff;
                            border-radius: 5px;
                            text-decoration: none;
                            font-weight: bold;
                            margin-top: 20px;
                        }}
                        .footer {{
                            padding: 20px;
                            text-align: center;
                            font-size: 12px;
                            color: #777777;
                            border-top: 1px solid #eeeeee;
                        }}
                        .note {{
                            padding: 15px;
                            background-color: #f8f9fa;
                            border-left: 4px solid #e74c3c;
                            margin: 20px 0;
                        }}
                        @media only screen and (max-width: 600px) {{
                            .container {{
                                width: 100%;
                            }}
                            .button {{
                                padding: 10px 20px;
                            }}
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <div class="logo">Quick<span>oo</span></div>
                        </div>
                        <div class="content">
                            <h2>Reset Your Password</h2>
                            <p>Hello,</p>
                            <p>We received a request to reset your password for your Quickoo account. Click the button below to reset your password:</p>

                            <a href="{reset_link}" class="button">Reset Password</a>

                            <p>This link will expire in <strong>30 minutes</strong>.</p>

                            <div class="note">
                                <p><strong>Security Note:</strong> If you didn't request a password reset, please ignore this email or contact our support team immediately.</p>
                            </div>

                            <p>If you have any questions or need help, feel free to contact our support team.</p>

                            <p>Best Regards,<br>The Quickoo Team</p>
                        </div>
                        <div class="footer">
                            <p>&copy; 2025 Quickoo. All rights reserved.</p>
                            <p>This is an automated message, please do not reply to this email.</p>
                        </div>
                    </div>
                </body>
                </html>
            """
            return forgot_password_html
        except Exception as e:
            print(f"{datetime.now()}: Error in getting forgot password HTML format: {str(e)}")

    def booking_confirmation_process(self, booking_data):
        try:
            booking_confirmation = """
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Quickoo - Booking Confirmation</title>
                    <style>
                        body {
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            margin: 0;
                            padding: 0;
                            background-color: #f5f5f5;
                        }
                        .container {
                            max-width: 600px;
                            margin: 0 auto;
                            padding: 20px;
                            background-color: #f2f2f2;
                            box-shadow: 1px 1px 5px #2c3e50;
                        }
                        .header {
                            text-align: center;
                            padding: 20px 0;
                            border-bottom: 1px solid #eeeeee;
                        }
                        .logo {
                            font-size: 32px;
                            font-weight: bold;
                            color: #2c3e50;
                        }
                        .logo span {
                            color: #e74c3c;
                        }
                        .content {
                            padding: 30px 20px;
                            color: #333333;
                        }
                        .booking-id-container {
                            margin: 30px 0;
                            text-align: center;
                        }
                        .booking-id {
                            font-size: 24px;
                            font-weight: bold;
                            letter-spacing: 2px;
                            padding: 15px 25px;
                            background-color: #f8f9fa;
                            border-radius: 8px;
                            color: #2c3e50;
                            display: inline-block;
                        }
                        .booking-details {
                            background-color: #ffffff;
                            padding: 25px;
                            border-radius: 8px;
                            margin: 20px 0;
                            border-left: 4px solid #e74c3c;
                        }
                        .detail-row {
                            display: flex;
                            justify-content: space-between;
                            margin: 10px 0;
                            padding: 8px 0;
                            border-bottom: 1px solid #f0f0f0;
                        }
                        .detail-label {
                            font-weight: bold;
                            color: #2c3e50;
                            flex: 1;
                        }
                        .detail-value {
                            flex: 2;
                            text-align: right;
                            color: #555555;
                        }
                        .status-badge {
                            display: inline-block;
                            padding: 5px 15px;
                            background-color: #f39c12;
                            color: white;
                            border-radius: 20px;
                            font-size: 12px;
                            font-weight: bold;
                            text-transform: uppercase;
                        }
                        .footer {
                            padding: 20px;
                            text-align: center;
                            font-size: 12px;
                            color: #777777;
                            border-top: 1px solid #eeeeee;
                        }
                        .note {
                            padding: 15px;
                            background-color: #f8f9fa;
                            border-left: 4px solid #e74c3c;
                            margin: 20px 0;
                        }
                        .important-info {
                            background-color: #e8f5e8;
                            border-left: 4px solid #27ae60;
                            padding: 15px;
                            margin: 20px 0;
                        }
                        @media only screen and (max-width: 600px) {
                            .container {
                                width: 100%;
                            }
                            .detail-row {
                                flex-direction: column;
                            }
                            .detail-value {
                                text-align: left;
                                margin-top: 5px;
                            }
                            .booking-id {
                                font-size: 18px;
                            }
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <div class="logo">Quick<span>oo</span></div>
                        </div>
                        <div class="content">
                            <h2>Booking Confirmed!</h2>
                            <p>Hello """ + booking_data['full_name'] + """,</p>
                            <p>Thank you for choosing Quickoo! Your booking has been successfully confirmed. Here are your booking details:</p>

                            <div class="booking-id-container">
                                <div class="booking-id">Booking ID: """ + booking_data['id'] + """</div>
                            </div>

                            <div class="booking-details">
                                <div class="detail-row">
                                    <div class="detail-label">Full Name:</div>
                                    <div class="detail-value">""" + booking_data['full_name'] + """</div>
                                </div>
                                <div class="detail-row">
                                    <div class="detail-label">Phone:</div>
                                    <div class="detail-value">""" + booking_data['phone'] + """</div>
                                </div>
                                <div class="detail-row">
                                    <div class="detail-label">Email:</div>
                                    <div class="detail-value">""" + booking_data['email'] + """</div>
                                </div>
                                <div class="detail-row">
                                    <div class="detail-label">Pickup Location:</div>
                                    <div class="detail-value">""" + booking_data['pickup'] + """</div>
                                </div>
                                <div class="detail-row">
                                    <div class="detail-label">Drop Location:</div>
                                    <div class="detail-value">""" + booking_data['drop'] + """</div>
                                </div>
                                <div class="detail-row">
                                    <div class="detail-label">Date:</div>
                                    <div class="detail-value">""" + str(booking_data['date']) + """</div>
                                </div>
                                <div class="detail-row">
                                    <div class="detail-label">Time:</div>
                                    <div class="detail-value">""" + booking_data['time'] + """</div>
                                </div>
                                <div class="detail-row">
                                    <div class="detail-label">Service Type:</div>
                                    <div class="detail-value">""" + booking_data['service_type'] + """</div>
                                </div>
                                <div class="detail-row">
                                    <div class="detail-label">Class:</div>
                                    <div class="detail-value">""" + booking_data['shoffr_class'] + """</div>
                                </div>
                                """ + (f'''<div class="detail-row">
                                    <div class="detail-label">Flight Info:</div>
                                    <div class="detail-value">{booking_data['flight_info']}</div>
                                </div>''' if booking_data.get('flight_info') else '') + """
                                """ + (f'''<div class="detail-row">
                                    <div class="detail-label">Bag Info:</div>
                                    <div class="detail-value">{booking_data['bag_info']}</div>
                                </div>''' if booking_data.get('bag_info') else '') + """
                                """ + (f'''<div class="detail-row">
                                    <div class="detail-label">Note:</div>
                                    <div class="detail-value">{booking_data['note']}</div>
                                </div>''' if booking_data.get('note') else '') + """
                                <div class="detail-row">
                                    <div class="detail-label">Status:</div>
                                    <div class="detail-value"><span class="status-badge">""" + booking_data['status'] + """</span></div>
                                </div>
                            </div>

                            <div class="important-info">
                                <p><strong>What's Next?</strong></p>
                                <p>• We will assign a driver to your booking shortly</p>
                                <p>• You will receive driver details and contact information once assigned</p>
                                <p>• Please be ready 5 minutes before your scheduled pickup time</p>
                            </div>

                            <div class="note">
                                <p><strong>Important:</strong> If you need to modify or cancel your booking, please contact our support team at least 2 hours before your scheduled pickup time.</p>
                            </div>

                            <p>If you have any questions or need assistance, our customer support team is always here to help.</p>

                            <p>Thank you for choosing Quickoo for your transportation needs!</p>

                            <p>Best Regards,<br>The Quickoo Team</p>
                        </div>
                        <div class="footer">
                            <p>&copy; 2025 Quickoo. All rights reserved.</p>
                            <p>This is an automated message, please do not reply to this email.</p>
                            <p>For support, contact us at support@quickoo.com</p>
                        </div>
                    </div>
                </body>
                </html>
                """

            return booking_confirmation

        except Exception as e:
            print(f"{datetime.now()}: Error in getting booking confirmation html format: {str(e)}")
            return None
