# 🚀 AI-Driven Sentiment Analysis for Social Media & Market Trends

## 📌 Project Overview

This project builds a **real-time AI-powered sentiment analysis system** to track **social media trends** and **consumer sentiment**.  
It **ingests Twitter & Reddit data**, applies **sentiment analysis**, and generates **automated trend reports** using **GPT-based content generation**.

🔹 **Use Case:**

- Brands & marketers can **track sentiment shifts** over time.
- Automated **weekly reports** help businesses **understand consumer perception**.
- Interactive **dashboard to filter & visualize trends**.

---

## 📊 Tech Stack

| **Component**               | **Technology Used**                         |
| --------------------------- | ------------------------------------------- |
| **Data Ingestion**          | Twitter API (Tweepy), Reddit API (PRAW)     |
| **Streaming**               | Azure Event Hub (Real-time processing)      |
| **Storage**                 | Azure Blob Storage (Data Lake)              |
| **Processing**              | Apache Spark (Azure Synapse)                |
| **Sentiment Analysis**      | Hugging Face Pre-trained Models             |
| **Trend Retrieval (RAG)**   | FAISS Vector Search + Historical Data       |
| **Report Generation (CAG)** | GPT-based summarization (Llama2/OpenAI API) |
| **Dashboard**               | Streamlit / Dash for visualization          |
| **Automation**              | GitHub Actions (Runs every 6 hours)         |

---

## 📥 Data Collection Pipeline

✅ **Fetches Twitter & Reddit data every 6 hours**  
✅ **Stores raw data in Azure Blob Storage**  
✅ **Sends real-time data to Azure Event Hub for Spark Processing**

### 🔹 **GitHub Actions Workflow** (Runs every 6 hours)

1. Fetches **latest tweets & subreddit posts**
2. Stores JSON data in **Azure Blob Storage**
3. Streams live data into **Azure Event Hub**
4. Spark job processes **sentiment scores & trends**

---

## 🛠 Spark Processing & Sentiment Analysis

✅ **Runs PySpark Job on Azure Synapse**  
✅ **Applies Sentiment Models** (`distilbert-base-uncased`)  
✅ **Stores sentiment scores in Azure Storage**

### 🔹 **Spark Job Pipeline**

1. Reads **real-time Event Hub messages**
2. Cleans & pre-processes **text data**
3. Runs **sentiment analysis model**
4. Stores **processed data in Azure Storage**

---

## 🔍 Trend Retrieval & Report Generation

✅ **Retrieves past trends using RAG (FAISS)**  
✅ **Generates Weekly Reports using GPT-based CAG**

### 🔹 **How It Works**

1. Uses **historical sentiment embeddings**
2. **Finds similar past discussions & trends**
3. GPT generates **trend summaries & insights**

---

## 📊 Interactive Dashboard

✅ **Filters sentiment data by date & topic**  
✅ **Visualizes trend shifts using charts**

### 🔹 **Built With**

- **Streamlit or Dash** for UI
- **Matplotlib / Plotly** for data visualization

---

## 🚀 Deployment & Automation

✅ **Runs every 6 hours via GitHub Actions**  
✅ **Data stored in Azure Data Lake**  
✅ **Sentiment processing with Azure Synapse**

---

## 📌 How to Set Up

### 1️⃣ **Clone the Repository**

```sh
git clone https://github.com/asif256000/social-trend-analysis.git
cd social-trend-analysis
```

### 2️⃣ **Set Up Azure Services**

- Create **Azure Synapse Workspace**
- Set up **Azure Event Hub**
- Configure **Azure Blob Storage**

### 3️⃣ **Add GitHub Secrets**

- **TWITTER_BEARER_TOKEN**
- **REDDIT_CLIENT_ID**
- **AZURE_STORAGE_CONNECTION**
- **AZURE_EVENT_HUB_CONNECTION**

### 4️⃣ **Run GitHub Actions**

Push the code and let GitHub Actions **fetch & store data**.

---

## 📌 Roadmap

✅ **Step 1: Data Ingestion (Twitter & Reddit APIs) ✔**  
🚀 **Step 2: Spark-based Sentiment Analysis (In Progress)**  
📊 **Step 3: Dashboard & Trend Visualization**

---

## 🤝 Contributing

Want to contribute? Fork the repo & submit a PR!

📩 **Contact:** [asif256000@gmail.com]

---

## 📜 License

MIT License
