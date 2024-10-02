.. _api_endpoints:

API Endpoints
=============

This section provides a detailed description of the URL patterns and the expected payloads for various API endpoints in the E-Procurement. The examples include payload structures for both requests and responses.

Admin and Schema Documentation
------------------------------

   **Endpoint:** `/admin/`

   **Method:** `GET`

   **Admin site**

   **Purpose:** Access the Django admin interface.

   **Endpoint:** `/api/schema/`

   **Method:** `GET`

   **API schema**

   **Purpose:** Access the API schema documentation.

   **Endpoint:** `/api/docs/`

   **Method:** `GET`

   **API documentation**

   **Purpose:** Access the API documentation.


.. Authentication and Registration
.. -------------------------------

..    **Endpoint:** `/register/`

..    **Method:** `POST`

..    **Customer Registration**

..    **Request Payload:**

..    .. code-block:: json

..       {
        
..         "email": "user1@example.com",
..         "role": "procurement officer"
..         "password": "password123"
..       }


..    **Response:**

..    .. code-block:: json

..       {
..         "message": "User registered successfully",
..         "user": {
..           "id": 1,
..           "role": "procurement officer",
..           "email": "user1@example.com"
..         }
..       }



..    **Endpoint:** `/login/`

..    **Method:** `POST`

..    **Customer Login**

..    **Request Payload:**

..    .. code-block:: json

..       {
..         "username": "user1",
..         "password": "password123"
..       }

..    **Response:**

..    .. code-block:: json

..       {
..         "access": "eyJhbGciOiJIUzI1NiIsInR...",
..         "refresh": "eyJhbGciOiJIUzI1NiIsInR..."
..       }


.. Tender
.. ------


..    **Endpoint:** `/tenders/`

..    **Method:** `POST`

..    **Create Tender**

..    **Response:**

..    .. code-block:: json

..       {
..         "title": "Construction Tender",
..         "description": "Request for construction of a new building",
..         "deadline": "2024-09-30T12:00:00Z"
..       }

Authentication
--------------

- `POST /register/`: Register a new user.
- `POST /login/`: Authenticate a user and return a JWT token.
- `POST /token/refresh/`: Refresh an expired access token.

Tender Management
-----------------

- `GET /tenders/`: List all tenders.
- `POST /tenders/`: Create a new tender.
- `GET /tenders/<id>/`: Retrieve details of a specific tender.
- `PATCH /tenders/<id>/`: Update a tender.
- `DELETE /tenders/<id>/`: Delete a tender.

Bid Management
--------------

- `GET /bids/`: List all bids.
- `POST /bids/`: Submit a new bid.
- `GET /bids/<id>/`: Retrieve bid details.
- `PATCH /bids/<id>/`: Update a bid.
- `DELETE /bids/<id>/`: Delete a bid.

Contract Management
-------------------

- `GET /contracts/`: List all contracts.
- `POST /contracts/`: Create a new contract.
- `GET /contracts/<id>/`: Retrieve contract details.
- `PATCH /contracts/<id>/`: Update contract details.
- `DELETE /contracts/<id>/`: Delete a contract.

Vendor Performance
------------------

- `GET /vendor-performance/`: List vendor performance reviews.
- `POST /vendor-performance/`: Create a new performance review.
- `GET /vendor-performance/<id>/`: Retrieve performance review details.
- `PATCH /vendor-performance/<id>/`: Update a performance review.
- `DELETE /vendor-performance/<id>/`: Delete a performance review.

Approval Workflow
-----------------

- `GET /approval-workflows/`: List all approval workflows.
- `POST /approval-workflows/`: Create a new workflow.
- `GET /approval-workflows/<id>/`: Retrieve a workflow.
- `PATCH /approval-workflows/<id>/`: Update a workflow.
- `DELETE /approval-workflows/<id>/`: Delete a workflow.

Notifications
-------------

- `GET /notifications/`**: List all notifications.
- `POST /notifications/`: Create a new notification.
- `GET /notifications/<id>/`: Retrieve notification details.
- `PATCH /notifications/<id>/`: Update notification details.
- `DELETE /notifications/<id>/`: Delete a notification.

  ..  **Endpoint:** `/vendor/pickup-requests/<int:vendor_id>/`

  ..  **Method:** `GET`

  ..  **Vendor Pickup Requests**

  ..  **Response:**

  ..  .. code-block:: json

  ..     {
  ..       "pickup_requests": [
  ..         {
  ..           "customer_id": 1,
  ..           "pickup_request_id": 2,
  ..           "customer_name": "John Doe",
  ..           "customer_mobile_no": 697967590,
  ..           "latitude": 30.0,
  ..           "longitude": 27.0,
  ..           "status": "pending",
  ..           "remarks": ""
  ..         }
  ..       ]
  ..     }


  ..  **Endpoint:** `/customer/<int:customer_id>/pickup-request/`

  ..  **Method:** `GET`

  ..  **Customer Pickup Request**

  ..  **Response:**

  ..  .. code-block:: json

  ..     {
  ..       "pickup_request_id": 1,      
  ..       "vendor_details": {
  ..         "vendor_name": "Doe Enterprises",
  ..         "vendor_mobile_no": "123098876",

  ..       }
  ..     }
