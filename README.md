# 🤖Chatbot RAG with LlamaIndex 🦙
---
## Settings
### 1. Clone this repository
```bash
https://github.com/krphat/RAG_with_LlamaIndex.git
```
### 2. Create virtual environment
Open Terminal and run the following command line:

- Go to project folder:

```bash
cd <name of the project>
```
- Type:
```bash
python -m venv .venv
```
- Activate virtual environment:
  - MacOS/Linux:
    ```bash
    source venv/bin/activate
    ```
  - Windows:
    ```bash
    .venv\Scripts\activate.bat
    ```
### 3. Install Libraries
- Upgrade pip:
```bash
python.exe -m pip install --upgrade pip
```
- Install Libraries:
```bash
pip install -r requirements.txt
```
---
## Quick start
Open Terminal and run the following command line:
- Go to project folder
```bash
cd <name of the project>
```
 - Run code
```bash
streamlit run Home.py
```
---
## Use API
Open Terminal and run the following command line:
- Go to **APIs** folder
```bash
cd APIs
```
- Run code
```bash
uvicorn app:app
```
View APIs document at: `http://127.0.0.1:8000/api/v1/docs`



