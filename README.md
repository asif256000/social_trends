# 🚀 AI-Driven Sentiment Analysis for Social Media & Market Trends

## 📌 Project Overview

This project builds a **real-time AI-powered sentiment analysis system** to track **social media trends** and **consumer sentiment**.  
It **ingests Twitter & Reddit data**, applies **advanced sentiment analysis**, and provides **interactive trend visualizations** via a **public Streamlit dashboard**.

🔹 **Use Case:**

- Brands & marketers can **track sentiment shifts** over time.
- Interactive **dashboard to filter & visualize trends**.
- Potential **automated reports based on insights**.

---

## 📊 Tech Stack

| **Component**          | **Technology Used**                                                                  |
| ---------------------- | ------------------------------------------------------------------------------------ |
| **Data Ingestion**     | Twitter API (Tweepy), Reddit API (PRAW)                                              |
| **Storage**            | Azure Blob Storage (Data Lake)                                                       |
| **Processing**         | Databricks (PySpark)                                                                 |
| **Sentiment Analysis** | Hugging Face Pre-trained Models (`nlptown/bert-base-multilingual-uncased-sentiment`) |
| **Dashboard**          | Streamlit (Hosted on Azure App Service)                                              |
| **Automation**         | GitHub Actions & Databricks Job Scheduler (Runs every 12 hours)                      |

---

## 📥 Data Collection Pipeline

✅ **Fetches Twitter & Reddit data every 12 hours**  
✅ **Stores raw JSON data in Azure Blob Storage**

### 🔹 **GitHub Actions Workflow** (Runs every 12 hours)

1. Fetches **latest tweets & subreddit posts**.
2. Stores JSON data in **Azure Blob Storage**.

---

## 🛠 Databricks Sentiment Processing

✅ **Runs PySpark Job on Azure Databricks**  
✅ **Applies Sentiment Models** (`nlptown/bert-base-multilingual-uncased-sentiment`)  
✅ **Stores sentiment scores in Azure Storage (Partitioned Parquet format)**

### 🔹 **Databricks Notebook Pipeline**

1. Reads **raw JSON data** from Azure Blob Storage.
2. Extracts **timestamp from filename** to track when data was fetched.
3. Runs **sentiment analysis model**:
   - **Fine-grained sentiment (1-5 stars)**
   - **Polarity (-1 to 1) & Subjectivity (0 to 1)**
4. Stores **processed data in partitioned Parquet format** in Azure Storage.

---

## 📊 Interactive Dashboard (Live on Azure)

✅ **Filters sentiment data by date & topic**  
✅ **Visualizes trend shifts using charts**

### 🔹 **Built With**

- **Streamlit** for UI
- **Matplotlib / Plotly** for data visualization
- **Azure Blob Storage** for storing & retrieving sentiment data

### 🔹 **Deployment**

- Hosted on **Azure App Service**
- Securely retrieves **processed sentiment data from Azure Blob Storage**
- Fetches **latest available sentiment scores** dynamically

📌 **Live Demo:** [coming soon](https://social-sentiment-dashboard-djhxd4gpbtb8ccgv.eastus2-01.azurewebsites.net/)

---

## 🚀 Deployment & Automation

✅ **Data fetching automated with GitHub Actions (Runs every 12 hours)**  
✅ **Sentiment processing automated via Databricks Job Scheduler**  
✅ **Dashboard deployed on Azure App Service**

---

## 📌 How to Set Up Locally

### 1️⃣ **Clone the Repository**

```sh
git clone https://github.com/asif256000/social-trend-analysis.git
cd social-trend-analysis
```

### 2️⃣ **Set Up Azure Services**

- Create **Azure Storage Account** (for raw & processed data storage).
- Create **Azure Databricks Workspace**.
- Deploy **Streamlit Dashboard** on Azure App Service.

### 3️⃣ **Set Up GitHub Secrets**

Add the following secrets to **GitHub Actions Secrets**:

- **TWITTER_BEARER_TOKEN** → Twitter API authentication token.
- **REDDIT_CLIENT_ID & REDDIT_CLIENT_SECRET** → Reddit API credentials.
- **AZURE_STORAGE_CONNECTION_STRING** → Azure Blob Storage access.
- **DATABRICKS_TOKEN** → Authentication token for running Databricks jobs.
- **DATABRICKS_HOST** → URL for the Databricks workspace.

### 4️⃣ **Run GitHub Actions**

Push the code and let GitHub Actions **fetch & store data**.

---

## 📌 Roadmap

✅ **Step 1: Data Ingestion (Twitter & Reddit APIs) ✔**  
✅ **Step 2: Databricks-based Sentiment Analysis ✔**  
🚀 **Step 3: Streamlit Dashboard (Deployed & Live) ✔**  
📊 **Step 4: Trend Analysis & Advanced Reports (Next Feature!)**

---

## 🤝 Contributing

Want to contribute? Fork the repo & submit a PR!

📩 **Contact:** [asif256000@gmail.com]

---

## 📜 License

MIT License
