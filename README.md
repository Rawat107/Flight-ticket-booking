# Running the Flight Booking System

This guide provides instructions on how to run the Flight Booking System, a Flask application for managing flight bookings.

## Prerequisites

Before running the application, ensure that you have the following installed:

- Python 3
- pip (Python package manager)

## Installation

1. Clone the repository to your local machine:

    ```bash
    git clone <repository_url>
    ```

2. Navigate to the project directory:

    ```bash
    cd <project_directory>
    ```

3. Install the required Python packages using pip:

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Before running the application, you may need to configure the database URI in the `config.py` file. By default, the application uses SQLite.

## Running the Application

To run the application, execute the following command:

```bash
python flight-booking.py
```
The Flask development server will start, and you should see output indicating that the server is running.

## Accessing the API

Once the application is running, you can access the API endpoints using an HTTP client such as Postman or cURL. Here are some example endpoints:

- User Signup: `POST http://localhost:5000/user/signup`
- User Login: `POST http://localhost:5000/user/login`
- Search Flights: `GET http://localhost:5000/flights/search`
- Book Flight: `POST http://localhost:5000/flights/book`
- User Bookings: `GET http://localhost:5000/user/bookings`
- Admin Login: `POST http://localhost:5000/admin/login`
- Add Flight: `POST http://localhost:5000/admin/flights/add`
- Remove Flight: `POST http://localhost:5000/admin/flights/remove`
- Admin Bookings: `GET http://localhost:5000/admin/bookings`

Ensure you provide the necessary parameters and headers as required by each endpoint.

## Stopping the Application

To stop the Flask development server, press `Ctrl + C` in the terminal where the server is running.
