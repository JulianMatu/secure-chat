# Secure Chat

A minimal secure chat application with confidentiality and digital signature.

## Info
Read report [here](https://docs.google.com/document/d/1SDoUvNfmX-oCw7u1Q_yQ-UPZG-T1pPRTAQ-arWttA3I/edit?usp=sharing)            
Github is hosted [here](https://github.com/JulianMatu/secure-chat)

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/JulianMatu/secure-chat
cd secure-chat
```

2. Create and activate virtual environment: 
```bash
python -m venv venv 
source venv/bin/activate # On Windows: venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Copy the `.env_default` file to `.env` and update the `MASTER_KEY` value to your own 256 bit AES key:
```bash
cp .env_default .env
```
5. Run the application:
```bash
python app.py
```

6. Open your browser and navigate to `http://localhost:5000`.
