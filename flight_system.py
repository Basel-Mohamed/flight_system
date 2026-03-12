from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from flight_system import FlightSystem, Admin

app = Flask(__name__)
CORS(app)

flight_system = FlightSystem()
admin = Admin("Admin")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/flights', methods=['GET'])
def get_flights():
    try:
        flights = flight_system.view_flights()
        return jsonify({'success': True, 'flights': flights})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/flights', methods=['POST'])
def add_flight():
    try:
        data = request.get_json()
        if data.get('admin_password') != '123':
            return jsonify({'success': False, 'error': 'Incorrect admin password'}), 401
        
        flight_number = data.get('flight_number')
        destination = data.get('destination')
        seats = int(data.get('seats'))
        
        if not all([flight_number, destination, seats]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        result = admin.add_flight(flight_system, flight_number, destination, seats)
        if result:
            return jsonify({'success': True, 'message': f'Flight {flight_number} added successfully'})
        else:
            return jsonify({'success': False, 'error': 'Flight already exists or could not be added'}), 400
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid number of seats'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/book', methods=['POST'])
def book_ticket():
    try:
        data = request.get_json()
        flight_number = data.get('flight_number')
        passenger_name = data.get('passenger_name')
        
        if not all([flight_number, passenger_name]):
            return jsonify({'success': False, 'error': 'Missing flight number or passenger name'}), 400
        
        result = flight_system.book_ticket(flight_number, passenger_name)
        if result:
            return jsonify({'success': True, 'message': f'Ticket booked successfully for {passenger_name} on flight {flight_number}'})
        else:
            return jsonify({'success': False, 'error': 'Booking failed.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cancel', methods=['DELETE'])
def cancel_booking():
    try:
        data = request.get_json()
        flight_number = data.get('flight_number')
        passenger_name = data.get('passenger_name')
        
        if not all([flight_number, passenger_name]):
            return jsonify({'success': False, 'error': 'Missing flight number or passenger name'}), 400
        
        result = flight_system.cancel_booking(flight_number, passenger_name)
        if result:
            return jsonify({'success': True, 'message': f'Booking cancelled successfully for {passenger_name} on flight {flight_number}'})
        else:
            return jsonify({'success': False, 'error': 'Cancellation failed. Booking may not exist'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/flights/<flight_number>', methods=['DELETE'])
def delete_flight(flight_number):
    try:
        data = request.get_json()
        if data.get('admin_password') != '123':
            return jsonify({'success': False, 'error': 'Incorrect admin password'}), 401
        
        flight_details = flight_system.get_flight_details(flight_number)
        if not flight_details:
            return jsonify({'success': False, 'error': 'Flight does not exist'}), 404
        
        result = admin.delete_flight(flight_system, flight_number)
        if result:
            message = f'Flight {flight_number} deleted successfully'
            if flight_details['total_bookings'] > 0:
                message += f'. {flight_details["total_bookings"]} booking(s) have been cancelled'
            return jsonify({'success': True, 'message': message, 'affected_passengers': flight_details['booked_passengers']})
        else:
            return jsonify({'success': False, 'error': 'Flight deletion failed'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/flights/<flight_number>/details', methods=['GET'])
def get_flight_details(flight_number):
    try:
        flight_details = flight_system.get_flight_details(flight_number)
        if flight_details:
            return jsonify({'success': True, 'flight': flight_details})
        else:
            return jsonify({'success': False, 'error': 'Flight not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/passenger/<passenger_name>/bookings', methods=['GET'])
def get_passenger_bookings(passenger_name):
    try:
        bookings = flight_system.view_passenger_bookings(passenger_name)
        return jsonify({'success': True, 'passenger_name': passenger_name, 'bookings': bookings})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Vercel handles execution, but this allows you to still test locally
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)