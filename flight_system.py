#import necessary libraries
import json
import os

# main classes for flight booking system

# create a flight system class
class FlightSystem:
    def __init__(self):
        self.flights = {}
        self.passengers = {}
        self.flights_file = "flights.json"
        self.bookings_file = "bookings.json"
        
        # Load existing data when system starts
        self.load_flights()
        self.load_bookings()

    def load_flights(self):
        """Load flights from file if exists"""
        if os.path.exists(self.flights_file):
            try:
                with open(self.flights_file, 'r', encoding='utf-8') as f:
                    flights_data = json.load(f)
                    for flight_number, data in flights_data.items():
                        # Create Flight object and add to flights dictionary
                        flight = Flight(flight_number, data['destination'], data['seats'])
                        flight.booked_passengers = data.get('booked_passengers', [])
                        self.flights[flight_number] = flight
                print(f"Loaded {len(self.flights)} flights from file")
            except Exception as e:
                print(f"Error loading flights: {e}")
        else:
            print("No flights file found, will create a new one")

    def save_flights(self):
        """Save flights to file"""
        try:
            flights_data = {}
            for flight_number, flight in self.flights.items():
                flights_data[flight_number] = {
                    'destination': flight.destination,
                    'seats': flight.seats,
                    'booked_passengers': flight.booked_passengers
                }
            
            with open(self.flights_file, 'w', encoding='utf-8') as f:
                # convert the flights data to JSON file
                json.dump(flights_data, f, ensure_ascii=False, indent=2)
            print("Flights data saved successfully")
        except Exception as e:
            print(f"Error saving flights: {e}")

    def load_bookings(self):
        """Load passenger bookings from file if exists"""
        if os.path.exists(self.bookings_file):
            try:
                with open(self.bookings_file, 'r', encoding='utf-8') as f:
                    bookings_data = json.load(f)
                    for passenger_name, bookings in bookings_data.items():
                        passenger = Passenger(passenger_name)
                        passenger.bookings = bookings
                        self.passengers[passenger_name] = passenger
                print(f"Loaded bookings for {len(self.passengers)} passengers from file")
            except Exception as e:
                print(f"Error loading bookings: {e}")
        else:
            print("No bookings file found, will create a new one")

    def save_bookings(self):
        """Save passenger bookings to file"""
        try:
            bookings_data = {}
            for passenger_name, passenger in self.passengers.items():
                bookings_data[passenger_name] = passenger.bookings
            
            with open(self.bookings_file, 'w', encoding='utf-8') as f:
                json.dump(bookings_data, f, ensure_ascii=False, indent=2)
            print("Bookings data saved successfully")
        except Exception as e:
            print(f"Error saving bookings: {e}")

    def add_flight(self, flight_number, destination, seats):
        if flight_number not in self.flights:
            self.flights[flight_number] = Flight(flight_number, destination, seats)
            self.save_flights()  # Save after adding
            return True
        return False

    def delete_flight(self, flight_number):
        """Delete a flight and remove all associated bookings"""
        if flight_number in self.flights:
            # Get list of passengers who booked this flight
            booked_passengers = self.flights[flight_number].booked_passengers.copy()
            
            # Remove the flight
            del self.flights[flight_number]
            
            # Remove this flight from all passengers' booking lists
            passengers_to_remove = []
            for passenger_name in booked_passengers:
                if passenger_name in self.passengers:
                    self.passengers[passenger_name].remove_booking(flight_number)
                    # If passenger has no more bookings, remove them completely
                    if not self.passengers[passenger_name].bookings:
                        passengers_to_remove.append(passenger_name)
            
            # Remove passengers with no bookings
            for passenger_name in passengers_to_remove:
                del self.passengers[passenger_name]
            
            # Save both files after deletion
            self.save_flights()
            self.save_bookings()
            return True
        return False

    def view_flights(self):
        return {flight_number: {'destination': flight.destination, 'available_seats': flight.seats} 
                for flight_number, flight in self.flights.items()}

    def book_ticket(self, flight_number, passenger_name):
        if flight_number in self.flights:
            result = self.flights[flight_number].book_ticket(passenger_name)
            if result:
                # Create or update passenger object and add booking
                if passenger_name not in self.passengers:
                    self.passengers[passenger_name] = Passenger(passenger_name)
                self.passengers[passenger_name].add_booking(flight_number)
                
                # Save both files after booking
                self.save_flights()
                self.save_bookings()
            return result
        return False

    def cancel_booking(self, flight_number, passenger_name):
        if flight_number in self.flights:
            result = self.flights[flight_number].cancel_booking(passenger_name)
            if result:
                # Remove booking from passenger object if exists
                if passenger_name in self.passengers:
                    self.passengers[passenger_name].remove_booking(flight_number)
                    # Remove passenger if no bookings left
                    if not self.passengers[passenger_name].bookings:
                        del self.passengers[passenger_name]
                
                # Save both files after cancellation
                self.save_flights()
                self.save_bookings()
            return result
        return False

    def view_passenger_bookings(self, passenger_name):
        # Return all bookings for a passenger
        if passenger_name in self.passengers:
            return self.passengers[passenger_name].bookings
        return []

    def get_flight_details(self, flight_number):
        """Get detailed information about a specific flight"""
        if flight_number in self.flights:
            flight = self.flights[flight_number]
            return {
                'flight_number': flight.flight_number,
                'destination': flight.destination,
                'available_seats': flight.seats,
                'booked_passengers': flight.booked_passengers,
                'total_bookings': len(flight.booked_passengers)
            }
        return None

# create a flight class
class Flight:
    def __init__(self, flight_number, destination, seats):
        self.flight_number = flight_number
        self.destination = destination
        self.seats = seats
        self.booked_passengers = []

    def book_ticket(self, passenger_name):
        if self.seats > 0 and passenger_name not in self.booked_passengers:
            self.booked_passengers.append(passenger_name)
            self.seats -= 1
            return True
        return False

    def cancel_booking(self, passenger_name):
        if passenger_name in self.booked_passengers:
            self.booked_passengers.remove(passenger_name)
            self.seats += 1
            return True
        return False

#### not used ####
    def view_bookings(self):
        return self.booked_passengers
    
# Update Passenger class (capitalize class name for convention)
class Passenger:
    def __init__(self, name):
        self.name = name
        self.bookings = []

    def add_booking(self, flight_number):
        if flight_number not in self.bookings:
            self.bookings.append(flight_number)

    def remove_booking(self, flight_number):
        if flight_number in self.bookings:
            self.bookings.remove(flight_number)

# create an admin class
class Admin:
    def __init__(self, name):
        self.name = name

    def add_flight(self, flight_system, flight_number, destination, seats):
        return flight_system.add_flight(flight_number, destination, seats)
    
    def delete_flight(self, flight_system, flight_number):
        return flight_system.delete_flight(flight_number)

#### not used ####
    def view_flights(self, flight_system):
        return flight_system.view_flights()




#main function to run the flight booking system

# 1- view available flights flow
def view_available_flights(flight_system):
    flights = flight_system.view_flights()
    if flights:
        print("\n--- Available Flights ---")
        for flight_number, info in flights.items():
            print(f"Flight Number: {flight_number}")
            print(f"Destination: {info['destination']}")
            print(f"Available Seats: {info['available_seats']}")
            print("-" * 30)
    else:
        print("No flights available.")

# 2- book ticket flow
def book_ticket_flow(flight_system):    
    print("\n--- Book Ticket ---")
    flight_number = input("Enter flight number to book: ")
    passenger_name = input("Enter your name: ")
    
    if flight_system.book_ticket(flight_number, passenger_name):
        print(f"Ticket booked successfully for {passenger_name} on flight {flight_number}.")
    else:
        print("Booking failed. Flight may be full or does not exist, or you already have a booking on this flight.")

# 3- cancel booking flow
def cancel_booking_flow(flight_system):
    print("\n--- Cancel Booking ---")
    flight_number = input("Enter flight number to cancel booking: ")
    passenger_name = input("Enter your name: ")
    
    if flight_system.cancel_booking(flight_number, passenger_name):
        print(f"Booking cancelled successfully for {passenger_name} on flight {flight_number}.")
    else:
        print("Cancellation failed. Booking may not exist.")

# 4- view passenger bookings flow
def view_passenger_bookings_flow(flight_system):
    print("\n--- View Passenger Bookings ---")
    passenger_name = input("Enter passenger name to view bookings: ")
    bookings = flight_system.view_passenger_bookings(passenger_name)
    
    if bookings:
        print(f"Passenger {passenger_name} has bookings on flights: {', '.join(bookings)}")
    else:
        print(f"No bookings found for passenger {passenger_name}.")

# 5- add new flight flow (admin functionality)
def add_new_flight_flow(admin, flight_system):
    print("\n--- Add New Flight (Admin Only) ---")
    admin_password = input("Enter admin password: ")
    
    if admin_password == "123":  # Simple password check
        flight_number = input("Enter new flight number: ")
        destination = input("Enter destination: ")
        try:
            seats = int(input("Enter number of seats: "))
            if admin.add_flight(flight_system, flight_number, destination, seats):
                print(f"Flight {flight_number} added successfully.")
            else:
                print("Flight already exists or could not be added.")
        except ValueError:
            print("Error: Please enter a valid number for seats.")
    else:
        print("Incorrect password. You do not have permission to add flights.")

# 6- delete flight flow (admin functionality)
def delete_flight_flow(admin, flight_system):
    print("\n--- Delete Flight (Admin Only) ---")
    admin_password = input("Enter admin password: ")
    
    if admin_password == "123":  # Simple password check
        # Show available flights first
        flights = flight_system.view_flights()
        if not flights:
            print("No flights available to delete.")
            return
        
        print("\nAvailable flights:")
        for flight_number, info in flights.items():
            flight_details = flight_system.get_flight_details(flight_number)
            print(f"Flight {flight_number}: {info['destination']} - {info['available_seats']} seats available, {flight_details['total_bookings']} bookings")
        
        flight_number = input("\nEnter flight number to delete: ")
        
        # Check if flight exists
        if flight_number not in flights:
            print("Flight does not exist.")
            return
        
        # Get flight details before deletion
        flight_details = flight_system.get_flight_details(flight_number)
        
        # Warn if there are existing bookings
        if flight_details['total_bookings'] > 0:
            print(f"\nWarning: This flight has {flight_details['total_bookings']} existing booking(s).")
            print(f"Passengers affected: {', '.join(flight_details['booked_passengers'])}")
            confirm = input("Are you sure you want to delete this flight? (yes/no): ").lower()
            if confirm != 'yes':
                print("Flight deletion cancelled.")
                return
        
        if admin.delete_flight(flight_system, flight_number):
            print(f"Flight {flight_number} deleted successfully.")
            if flight_details['total_bookings'] > 0:
                print(f"All {flight_details['total_bookings']} booking(s) have been cancelled.")
        else:
            print("Flight deletion failed.")
    else:
        print("Incorrect password. You do not have permission to delete flights.")

# 7- admin menu flow
def admin_menu_flow(admin, flight_system):
    print("\n--- Admin Panel ---")
    admin_password = input("Enter admin password: ")
    
    if admin_password == "123":  # Simple password check
        while True:
            print("\n" + "="*30)
            print("Admin Menu:")
            print("1. Add New Flight")
            print("2. Delete Flight")
            print("3. View All Flights (with details)")
            print("4. Back to Main Menu")
            print("="*30)
            
            admin_choice = input("Enter your choice: ")
            
            if admin_choice == '1':
                flight_number = input("Enter new flight number: ")
                destination = input("Enter destination: ")
                try:
                    seats = int(input("Enter number of seats: "))
                    if admin.add_flight(flight_system, flight_number, destination, seats):
                        print(f"Flight {flight_number} added successfully.")
                    else:
                        print("Flight already exists or could not be added.")
                except ValueError:
                    print("Error: Please enter a valid number for seats.")
            
            elif admin_choice == '2':
                # Show available flights first
                flights = flight_system.view_flights()
                if not flights:
                    print("No flights available to delete.")
                    continue
                
                print("\nAvailable flights:")
                for flight_number, info in flights.items():
                    flight_details = flight_system.get_flight_details(flight_number)
                    print(f"Flight {flight_number}: {info['destination']} - {info['available_seats']} seats available, {flight_details['total_bookings']} bookings")
                
                flight_number = input("\nEnter flight number to delete: ")
                
                # Check if flight exists
                if flight_number not in flights:
                    print("Flight does not exist.")
                    continue
                
                # Get flight details before deletion
                flight_details = flight_system.get_flight_details(flight_number)
                
                # Warn if there are existing bookings
                if flight_details['total_bookings'] > 0:
                    print(f"\nWarning: This flight has {flight_details['total_bookings']} existing booking(s).")
                    print(f"Passengers affected: {', '.join(flight_details['booked_passengers'])}")
                    confirm = input("Are you sure you want to delete this flight? (yes/no): ").lower()
                    if confirm != 'yes':
                        print("Flight deletion cancelled.")
                        continue
                
                if admin.delete_flight(flight_system, flight_number):
                    print(f"Flight {flight_number} deleted successfully.")
                    if flight_details['total_bookings'] > 0:
                        print(f"All {flight_details['total_bookings']} booking(s) have been cancelled.")
                else:
                    print("Flight deletion failed.")
            
            elif admin_choice == '3':
                flights = flight_system.view_flights()
                if flights:
                    print("\n--- All Flights (Detailed View) ---")
                    for flight_number, info in flights.items():
                        flight_details = flight_system.get_flight_details(flight_number)
                        print(f"Flight Number: {flight_number}")
                        print(f"Destination: {info['destination']}")
                        print(f"Available Seats: {info['available_seats']}")
                        print(f"Total Bookings: {flight_details['total_bookings']}")
                        if flight_details['booked_passengers']:
                            print(f"Booked Passengers: {', '.join(flight_details['booked_passengers'])}")
                        print("-" * 50)
                else:
                    print("No flights available.")
            
            elif admin_choice == '4':
                break
            
            else:
                print("Invalid choice. Please try again.")
    else:
        print("Incorrect password. You do not have admin access.")


# main function to run the flight booking system
def main():
    print("Welcome to the Flight Booking System\n")
    print("Loading data...")
    
    flight_system = FlightSystem()
    admin = Admin("Admin")
    
    while True:
        print("\n" + "="*40)
        print("Main Menu:")
        print("1. View Available Flights")
        print("2. Book a Ticket")
        print("3. Cancel a Booking")
        print("4. View Passenger Bookings")
        print("5. Admin Panel")
        print("6. Exit")
        print("="*40)

        choice = input("Enter your choice: ")

        if choice == '1':
            view_available_flights(flight_system)
        elif choice == '2':
            book_ticket_flow(flight_system)
        elif choice == '3':
            cancel_booking_flow(flight_system)
        elif choice == '4':
            view_passenger_bookings_flow(flight_system)
        elif choice == '5':
            admin_menu_flow(admin, flight_system)
        elif choice == '6':
            print("Thank you for using the system!")
            break
        else:
            print("Invalid choice. Please try again.")


# run the main function if this script is executed
if __name__ == "__main__":
    main()