# 🧾 EDGAR EPS Parser
This Python script extracts Earnings Per Share (EPS) data from SEC EDGAR .html filings. It scans each document, scrapes the raw text, and applies multiple regex patterns to identify GAAP and non-GAAP EPS values. Final results are exported to a ParsedEPS.csv file.

# 📦 Features
 - Extracts EPS from .html EDGAR filings
 - Handles GAAP vs Non-GAAP and basic vs diluted distinctions
 - Automatically detects EPS context (net income/loss)
 -GUI folder picker to select your filings
 - Outputs results to a clean CSV file

# 🚀 How to Use
1. Clone the Repository
 - git clone https://github.com/your-username/edgar-eps-parser.git
 - cd edgar-eps-parser
2. Install Requirements
 - Make sure you have Python 3.7+ installed. Install the dependencies:
 - pip install beautifulsoup4
3. Run the Script
 - python EdgarParsingScript.py
A file dialog window will appear — select the folder that contains your .html EDGAR filings.

4. Output
The script will parse each .html file in the selected folder and generate a ParsedEPS.csv file containing:

filename	EPS
---filing1.html	1.23
---filing2.html	-0.45
---filing3.html	EPS not found

📝 Notes
The script looks for .html files only.
It uses several regex patterns to increase EPS detection accuracy which can be adjusted by the user if need be.
EPS values flagged as "non-GAAP" or "adjusted" are deprioritized unless no GAAP values are found.

📂 Example Folder Structure
Copy
Edit
your-edgar-folder/
├── filing1.html
├── filing2.html
└── filing3.html

🤝 Contributing
Contributions are welcome! Feel free to submit issues or pull requests for improvements.

📄 License
MIT License. See LICENSE file for details.
