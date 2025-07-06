# Ecommerce-Demo  
Full-Stack Web App with Docker Support | Built with Flask | Live on AWS

## 🧠 Project Overview
This full-stack web application serves as a professional portfolio and demonstration site for our web development team. Built with Python (Flask) and fully containerized using Docker, it showcases our ability to architect secure, scalable, and modern applications. Key features include custom routing, secure user authentication, resumè file uploads, and a dynamic, database-driven project showcase — all backed by a clean and responsive frontend.

## 🚀 Live Deployment
The application is deployed on AWS Elastic Beanstalk using a custom Docker environment, reverse-proxied through Amazon CloudFront with SSL/TLS encryption via AWS Certificate Manager. Domain routing is managed with Amazon Route 53.
## 🌐 View Live Site:  
**https://c2cwebsolutions.com** (Primary domain)  
Redirects from **.org**, **.net**, and `www.` versions are all configured for instant redirection.

## ✅ Hosted & Secured Using:  
- AWS EC2 via Elastic Beanstalk  
- Docker container (Amazon Linux 2023)  
- Flask web server + Gunicorn  
- CloudFront CDN for caching and performance  
- ACM (AWS Certificate Manager) for HTTPS + SSL  
- Route 53 DNS Management  
- S3 Static Buckets for redirect and domain routing  
- VPC (Virtual Private Cloud) for environment isolation

---

## 🧰 Key Features  
- 🔒 Secure login authentication w/ session management  
- 📄 Resume upload + admin-only dashboard  
- 🖼️ Multi-image product/project galleries  
- 📬 Project inquiry form with step-by-step UX  
- 📱 Fully responsive UI (mobile-first design)  
- 💾 SQLite database integration w/ seed data  
- 🐳 Dockerized for full portability  
- 📂 Clean and semantic Jinja templating  
- 🧠 Admin backend and custom CMS-like tools (in progress)  

---

## 🔧 Developer Tools & Stack

- **Frontend**: HTML5, CSS3, Swiper.js, custom styling  
- **Backend**: Python Flask, Jinja2 templating  
- **Database**: SQLite (locally), AWS RDS ready  
- **Containerization**: Docker + custom `Dockerfile`  
- **Deployment**: Elastic Beanstalk w/ EB CLI  
- **CI/CD**: Manual via Git & EB CLI  
- **Cloud Infrastructure**:  
  - Amazon S3 (static hosting + routing redirects)  
  - Route 53 (custom domain routing + cert validation)  
  - ACM (certs for `.com`, `.net`, `.org`, with/without `www`)  
  - CloudFront (CDN + HTTPS offload + www redirect)  
  - EC2 (via EB-managed environment)  
  - VPC (network segmentation)

---

## 🔄 Domain Routing Setup (via AWS)

All purchased domains (`.com`, `.net`, `.org`) are managed through **Route 53**, with S3 static redirect buckets sending `.net` and `.org` traffic (with or without `www`) to the `.com` root.

- **HTTPS** via **ACM** using SAN cert  
- **Instant redirects** via CloudFront + S3  
- **No www conflicts** – fully normalized domain routing

---

## 🧪 Running Locally with Docker (Recommended)

Clone the repository and build the Docker image:

```bash
git clone https://github.com/Mreigel/Website-Development.git
cd Website-Development
git checkout Website
docker build -t ecommerce-demo .
docker run -p 5000:5000 ecommerce-demo
```

Open your browser and visit:

    http://localhost:5000

---

## 🛠️ Running Without Docker

If you prefer a non-containerized setup:

```bash
pip install -r requirements.txt
python app.py
```

---

## 📁 Branches  
- `Website` – Main production-ready branch  
- `WebDev` – Experimental development branch  

---


## 📢 Closing Notes

We've built this from the ground up using AWS-native tools, Docker, and Flask — configuring every routing layer, SSL cert, and deployment strategy manually. This project serves as a launchpad for freelance opportunities, agency contracts, or further production SaaS development.Thank you and please feel free to send us feedback.



## 📬 Contact

**Michael Reigel**  
[LinkedIn](#) | [GitHub](https://github.com/Mreigel)

**Joe Lima**  
[LinkedIn](#) | [GitHub](#)
