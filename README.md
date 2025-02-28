

---

# **CDP Documentation API**

This project provides a **Customer Data Platform (CDP) Documentation API** that allows users to search, compare, and get advanced guidance on various CDPs like Segment, mParticle, Lytics, and Zeotap. The project consists of a **backend** built with FastAPI and a **frontend** built with Streamlit.

---

## **Features**

### **Backend (FastAPI)**
1. **Search Documentation (`/ask`)**:
   - Retrieve relevant documentation for a specific CDP based on user queries.
   - Supports natural language queries and keyword-based searches.
   - Provides suggestions if no relevant information is found.

2. **Compare CDPs (`/compare`)**:
   - Compare two CDPs based on specific aspects like ease of use, pricing, integrations, and data governance.
   - Handles ambiguous queries and suggests focus areas.

3. **Advanced How-To Guidance (`/advanced`)**:
   - Provides step-by-step guidance for advanced CDP features like tracking plans, identity resolution, and compliance workflows.

4. **Health Check (`/health`)**:
   - A simple endpoint to check the health and status of the API.

5. **Caching**:
   - Uses `lru_cache` to store scraped documentation and avoid repeated requests.

6. **Error Handling**:
   - Gracefully handles invalid queries, ambiguous requests, and server errors.

---

### **Frontend (Streamlit)**
1. **User-Friendly Interface**:
   - Provides a simple and intuitive interface for users to interact with the API.
   - Supports all backend features (search, compare, advanced guidance).

2. **Dynamic Responses**:
   - Displays API responses in a clean and readable format.

3. **Error Handling**:
   - Shows appropriate error messages for invalid or ambiguous queries.

---

## **Project Structure**

```
Assignment_2/
├── backend/
│   ├── main.py               # FastAPI backend code
│   ├── requirements.txt      # Backend dependencies
├── frontend/
│   ├── app.py                # Streamlit frontend code
│   ├── requirements.txt      # Frontend dependencies
├── README.md                 # This file
```

---

## **Setup Instructions**

### **1. Clone the Repository**
```bash
git clone <repository-url>
cd Assignment_2
```

---

### **2. Set Up the Backend**

#### Install Dependencies
Navigate to the `backend` folder and install the required packages:
```bash
cd backend
pip install -r requirements.txt
```

#### Run the Backend
Start the FastAPI server using the following command:
```bash
python -m uvicorn main:app --reload
```

- The backend will be available at `http://127.0.0.1:8000`.
- You can access the interactive API documentation at `http://127.0.0.1:8000/docs`.

---

### **3. Set Up the Frontend**

#### Install Dependencies
Navigate to the `frontend` folder and install the required packages:
```bash
cd ../frontend
pip install -r requirements.txt
```

#### Run the Frontend
Start the Streamlit app using the following command:
```bash
streamlit run app.py
```

- The frontend will be available at `http://localhost:8501`.

---

## **Commands Summary**

| Task                  | Command                                      |
|-----------------------|----------------------------------------------|
| Run Backend           | `python -m uvicorn main:app --reload`        |
| Run Frontend          | `streamlit run app.py`                       |

---

## **API Endpoints**

### **Backend Endpoints**
1. **Search Documentation**:
   - **Endpoint**: `POST /ask`
   - **Example Query**: `{"question": "How do I set up tracking in Segment?"}`

2. **Compare CDPs**:
   - **Endpoint**: `POST /compare`
   - **Example Query**: `{"question": "Compare Segment and mParticle."}`

3. **Advanced How-To Guidance**:
   - **Endpoint**: `POST /advanced`
   - **Example Query**: `{"question": "How do I implement a tracking plan in Segment?"}`

4. **Health Check**:
   - **Endpoint**: `GET /health`

---

## **Frontend Features**

1. **Search Documentation**:
   - Enter a question about a specific CDP and get relevant documentation.

2. **Compare CDPs**:
   - Compare two CDPs based on specific aspects like ease of use, pricing, and integrations.

3. **Advanced How-To Guidance**:
   - Get step-by-step guidance for advanced CDP features.

---

## **Example Queries**

### **Search Documentation**
- "How do I set up tracking in Segment?"
- "What are the best practices for data governance in mParticle?"

### **Compare CDPs**
- "Compare Segment and mParticle."
- "What are the differences in data governance between Segment and mParticle?"

### **Advanced How-To Guidance**
- "How do I implement a tracking plan in Segment?"
- "How do I set up cross-device tracking in Zeotap?"

---

## **Dependencies**

### **Backend**
- FastAPI
- Uvicorn
- Requests
- BeautifulSoup
- Selenium
- difflib
- lru_cache

### **Frontend**
- Streamlit
- Requests

---

## **Contributing**
Feel free to contribute to this project by opening issues or submitting pull requests.

---

## **License**
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

This **README.md** provides a comprehensive guide to your project, including setup instructions, features, and usage examples. You can customize it further based on your specific requirements.