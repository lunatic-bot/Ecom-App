# E-commerce Web App

This is an e-commerce platform built using **FastAPI** for the backend and **PostgreSQL** as the database. The app will include features for managing users, products, orders, and payment processing.

## Technologies

- **FastAPI**: High-performance web framework for building APIs with Python.
- **PostgreSQL**: Relational database for data storage.

## Features (In Progress)

- User registration and authentication.
- Product catalog management.
- Order creation and tracking.

## Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/lunatic-bot/Ecom-App.git
   cd ecommerce-app
   ```

2. Set up a virtual environment and install dependencies:

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the PostgreSQL database and configure the connection.

4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## To-Do

- Implement user authentication.
- Create product and order models.
- Integrate payment processing.

Stay tuned for updates as the app evolves!
