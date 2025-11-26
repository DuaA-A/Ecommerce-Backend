<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; max-width: 1100px; margin:auto; padding: 20px;">

<h1 style="color:#2c3e50; font-weight:700;">E-Commerce Backend</h1>
<p>
<strong>Ecommerce_Backend</strong> is a backend system built using a microservices architecture implemented with <strong>Python Flask</strong>. It supports an e-commerce platform by handling core backend operations such as order processing, inventory management, pricing calculations, customer management, and notification dispatching. Each service is independent, modular, and communicates through RESTful APIs.
</p>

<hr>

<h2>1. Project Overview</h2>
<p>
The backend provides the foundational business logic for an E-Commerce Order Management System. It consists of five standalone microservices, each responsible for a distinct domain. The system is designed for scalability, service isolation, and clean separation of concerns.
</p>

<hr>

<h2>2. Technologies Used</h2>
<ul>
  <li>Python 3.x</li>
  <li>Flask Microframework</li>
  <li>REST API Architecture</li>
  <li>MySQL Database</li>
  <li>Virtual Environments (per-service)</li>
</ul>

<hr>

<h2>3. Microservices Architecture</h2>
<p>Each microservice runs independently and communicates over HTTP.</p>

<h3>3.1 Services and Ports</h3>
<ul>
  <li><strong>Order Service</strong> – Port 5001</li>
  <li><strong>Inventory Service</strong> – Port 5002</li>
  <li><strong>Pricing Service</strong> – Port 5003</li>
  <li><strong>Customer Service</strong> – Port 5004</li>
  <li><strong>Notification Service</strong> – Port 5005</li>
</ul>

<h3>3.2 Responsibilities Summary</h3>
<ul>
  <li><strong>Order Service:</strong> Order creation, validation, order retrieval, order item handling.</li>
  <li><strong>Inventory Service:</strong> Product catalog, stock checks, stock updates.</li>
  <li><strong>Pricing Service:</strong> Price calculation, discount policies, tax application.</li>
  <li><strong>Customer Service:</strong> Customer profile management, order history retrieval, loyalty point updates.</li>
  <li><strong>Notification Service:</strong> Notification generation, service aggregation, log management.</li>
</ul>

<hr>

<h2>4. Project Structure</h2>
<pre style="background:#f4f4f4; padding:15px; border:1px solid #ddd; border-radius:5px;">
Ecommerce_Backend/
│── customer_service/
│── inventory_service/
│── notification_service/
│── order_service/
│── pricing_service/
│── SQL script.txt
│── steps_for_each_service_to_create.txt
</pre>

<hr>

<h2>5. Database Schema</h2>
<p>The system uses a centralized MySQL database. The schema includes customer records, inventory data, pricing rules, tax rates, orders, and notifications.</p>

<pre style="background:#f4f4f4; padding:15px; border:1px solid #ddd; border-radius:5px; white-space:pre-wrap;">
-- Core tables: customers, inventory, pricing_rules, tax_rates
-- Order system tables: orders, order_items
-- Logging: notification_log

(Full SQL schema is included in this repository under "SQL script.txt")
</pre>

<hr>

<h2>6. Running the Backend</h2>
<h3>6.1 Setup</h3>
<ol>
  <li>Create and activate a virtual environment inside each microservice folder.</li>
  <li>Install dependencies using the provided <em>requirements.txt</em>.</li>
  <li>Configure environment variables via each service’s <em>.env</em> file.</li>
  <li>Ensure MySQL is running and import the provided SQL script.</li>
</ol>

<h3>6.2 Starting Services</h3>
<pre style="background:#f4f4f4; padding:15px; border:1px solid #ddd; border-radius:5px;">python app.py</pre>
<p>Run this command inside each microservice directory.</p>

<hr>

<h2>7. Service Interaction (High-Level)</h2>
<p>The following is the simplified workflow for processing an order:</p>
<ol>
  <li>Order Service receives the order request.</li>
  <li>Pricing Service calculates the total amount.</li>
  <li>Inventory Service validates and updates stock.</li>
  <li>Customer Service updates loyalty points.</li>
  <li>Notification Service sends a confirmation message.</li>
</ol>

<hr>

<h2>8. Purpose of This Repository</h2>
<p>
This backend implementation demonstrates clean microservice separation, database-driven service design, and inter-service communication following modern backend architecture standards. It is intended for academic, learning, and demonstration purposes.
</p>

<hr>

<footer>
<p style="color:#7f8c8d;">© 2025 Ecommerce_Backend — Backend System Documentation</p>
</footer>

</body>
</html>
