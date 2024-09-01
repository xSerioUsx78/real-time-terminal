# **Real-Time Terminal with Django and Django Channels**

## **Project Overview**

This project is a backend application that powers a real-time terminal interface using Django and Django Channels. The primary purpose is to allow users to interact with a terminal via WebSocket communication, which can be used in various scenarios like remote command execution or real-time monitoring.

## **Key Features**

- **Real-Time WebSocket Communication:** Provides real-time interaction capabilities using Django Channels and WebSockets.
- **Scalable and Efficient:** Handles multiple users and terminal sessions concurrently with minimal latency.
- **Extensible Backend:** Can be easily integrated with different frontends or expanded to include additional functionality.

## **Technologies Used**

### **Backend**

- **[Django](https://www.djangoproject.com/):** A robust Python web framework that simplifies the development of complex web applications.
- **[Django Channels](https://channels.readthedocs.io/en/stable/):** Extends Django to handle asynchronous protocols such as WebSockets, enabling real-time features.
- **[Daphne](https://github.com/django/daphne):** An ASGI server used to serve your Django Channels application.

### **Testing**

- **[Django Test Framework](https://docs.djangoproject.com/en/stable/topics/testing/):** For creating and running tests within the Django ecosystem.

## **Setup and Installation**

### **Prerequisites**

- Python 3.10+

### **Installation**

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/xSerioUsx78/real-time-terminal.git
   cd realtime-terminal-backend
   ```

2. **Set Up a Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**

   Create a `.env` file in the project src folder and add the necessary environment variables:

   ```env
   SECRET_KEY=your-secret-key
   SSH_HOST=your-host
   SSH_USER=your-user
   SSH_PASS=your-pass
   SSH_PORT=your-port
   ```

5. **Apply Migrations:**

   ```bash
   python manage.py migrate
   ```

6. **Start the Development Server:**

   ```bash
   python manage.py runserver
   ```

## **Running Tests**

To run tests and ensure everything is working as expected:

```bash
python manage.py test
```
