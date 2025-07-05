# Ecommerce-Demo  
Full-Stack Web App with Docker Support | Built with Flask | Live on AWS

## 📌 About  
This is a full-stack web application designed as a professional portfolio and demo site for a web development team. It features custom routes, user authentication, resume uploads, and a database-driven project showcase — all built with Python (Flask) and now fully containerized using Docker.

This project highlights our growing dev team's capability to build and deploy scalable, modern applications.

---

## 🚀 Live Deployment

The application is live and hosted on **AWS Elastic Beanstalk** using a custom Docker environment.

🌐 View Live Site:  
http://dev-portfolio-env.eba-ui3fempc.us-west-1.elasticbeanstalk.com

✅ Hosted on:  
- AWS EC2 via Elastic Beanstalk  
- Docker container (Amazon Linux 2023)  
- Flask web server  
- Managed using the EB CLI

---

## 🧰 Features  
- Responsive design for desktop, tablet, and mobile  
- Python Flask backend with SQLite database  
- User authentication and resume upload  
- Docker-ready for cloud deployment (AWS, Render, DigitalOcean)  
- Semantic HTML templates and modern CSS  
- Seeded database for portfolio projects  

---

## 🧪 Running Locally with Docker (Recommended)

Clone the repository and build the Docker image:

    git clone https://github.com/Mreigel/Website-Development.git
    cd Website-Development
    git checkout Website

Build and run the app:

    docker build -t ecommerce-demo .
    docker run -p 5000:5000 ecommerce-demo

Then open your browser and go to:

    http://localhost:5000

---

## 🛠️ Running Without Docker

If you prefer a traditional local setup:

    pip install -r requirements.txt
    python app.py

---

## 📁 Branches  
- `Website` – Main working branch  
- `WebDev` – Developer branch  

---

## 📬 Contact

**Michael Reigel**  
[LinkedIn](#) | [GitHub](https://github.com/Mreigel)

**Joe Lima**  
[LinkedIn](#) | [GitHub](#)
