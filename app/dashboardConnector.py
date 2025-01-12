import base64
import io
from flask import Blueprint, render_template, flash, redirect, url_for, session
from pyzbar.pyzbar import decode
from PIL import Image
from app.utils import get_cursor, close_db_connection

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    user_role = session.get('user_role')
    if user_role == 'admin':
        adminID = session.get('adminID')
        if not adminID:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('auth.login'))
        return render_template('dashboard.html', user_role=user_role)
    elif user_role == 'user':
        info_id = session.get('infoID')
        if not info_id:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('auth.login'))
        
        user_firstname = session.get('user_firstname')
        
        cursor, connection = get_cursor()
        try:
            sql_get_user_info = "SELECT studno,lastname,firstname,email,contactnumber FROM userinfo WHERE infoID = %s"
            cursor.execute(sql_get_user_info, (info_id,))
            user_info = cursor.fetchone()
            print("User Info:", user_info) 

            sql_get_vehicle_info = "SELECT * FROM vehicle WHERE userID = (SELECT userID FROM user WHERE infoID = %s)"
            cursor.execute(sql_get_vehicle_info, (info_id,))
            vehicle_info = cursor.fetchone()
            print("Vehicle Info:", vehicle_info) 

            sql_get_qr_code = "SELECT qr_code_image FROM qr_codes WHERE userID = (SELECT userID FROM user WHERE infoID = %s)"
            cursor.execute(sql_get_qr_code, (info_id,))
            qr_code_image_base64 = cursor.fetchone()[0]
            #print("QR Code Image:", qr_code_image_base64)  

            decoded_objects = decode(Image.open(io.BytesIO(base64.b64decode(qr_code_image_base64))))
            decoded_data = [obj.data.decode('utf-8') for obj in decoded_objects]
            print("Decoded Data:", decoded_data)  

        except Exception as e:
            flash(f'Error: {e}', 'danger')
            return redirect(url_for('auth.login'))
        finally:
            cursor.close()
            close_db_connection(connection)
        
        return render_template('dashboard.html', user_role=user_role, user_firstname=user_firstname, user_info=user_info, vehicle_info=vehicle_info, qr_code_image=qr_code_image_base64, decoded_data=decoded_data)
    else:
        flash('Please log in to access this page', 'danger')
        return redirect(url_for('auth.login'))
