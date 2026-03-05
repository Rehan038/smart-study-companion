# 🎓 Smart Study Companion

An AI-powered learning platform designed to streamline study workflows through intelligent document analysis, automatic summarization, and dynamic roadmap generation.

## 🚀 Features

-   **User Authentication**: Secure multi-role (Student/Admin) access system.
-   **Intelligent Document Processing**: Extract, clean, and analyze text from PDF study materials.
-   **AI Summarization**: Condense long documents into concise, actionable summaries.
-   **Dynamic Roadmap Builder**: Generate week-by-week learning plans based on document keywords and specific topics.
-   **Interactive Visualizations**: Graphical learning paths powered by Plotly and NetworkX.
-   **Student Analytics**: Track learning progress and study habits.
-   **Admin Panel**: Comprehensive dashboard for system management and feedback review.

## 🛠️ Tech Stack

-   **Frontend**: [Streamlit](https://streamlit.io/)
-   **Language**: [Python 3.x](https://www.python.org/)
-   **NLP & PDF**: NLTK, PyMuPDF (fitz)
-   **Data Visuals**: Plotly, Matplotlib, NetworkX
-   **Database**: SQLite
-   **External API**: Wikipedia (via `wikipedia-api`)

## 📦 Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/Rehan038/smart-study-companion.git
    cd smart-study-companion
    ```

2.  **Set up Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download NLTK Data**:
    ```python
    import nltk
    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('stopwords')
    ```

## 🖥️ Usage

1.  **Run the Application**:
    ```bash
    streamlit run smart_learning_companion/app.py
    ```
2.  **Login**: Use student or admin credentials to access the dashboard.
3.  **Process Documents**: Upload a PDF in the Student Dashboard to start the AI analysis.
4.  **Generate Roadmap**: Enter a topic and get a visualized learning plan.

## 📁 Project Structure

```text
Smart-StudyCompanion/
├── smart_learning_companion/
│   ├── admin/             # Admin management modules
│   ├── analytics/         # Student & Admin dashboard logic
│   ├── auth/              # Login/Logout & Role management
│   ├── data/              # Storage for uploads and local data
│   ├── database/          # SQLite schema and DB operations
│   ├── document_analysis/ # PDF extraction, NLP, and Summarization
│   ├── roadmap/           # Roadmap logic and Graphing
│   └── app.py             # Main entry point
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
