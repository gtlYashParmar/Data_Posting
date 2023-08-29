## Data Posting

### How to run 
- Create a virtual environment and install all necessary modules
```bash
python3 -m venv venv
pip install -r requirements.txt
```

- Change Authentication token
```python
# change token in datapost.py (if you want to run in thread change in datapostthread.py)
TOKEN="YOUR_TOKEN"
```

- run
```bash
python datapost.py
```