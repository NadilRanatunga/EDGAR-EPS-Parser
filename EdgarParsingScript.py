# Simple EdgarParsingScript.py
# Nadil Ranatunga  

# Imports 
import os                                   
from bs4 import BeautifulSoup               
import re                                   
import csv                                  
import tkinter as tk                       
from tkinter import filedialog

# Choose Folder w Edgar Filings
root = tk.Tk()
root.withdraw()  
directory = filedialog.askdirectory(title="Select EDGAR Filings Folder")

if not directory:
    print("No folder selected. Exiting...")
    exit()

results = []


# Extract Pure Text from Filings
def ParseText(pureEdgarFiling):
    # Parse script and style elements
    soup = BeautifulSoup(pureEdgarFiling, 'html.parser')
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Make text readable
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    return text

# Main EPS Extraction Function
def GetEPS(EdgarFiling):
    # Open Filing + Extract Text
    with open(EdgarFiling, 'r', encoding='utf-8', errors='ignore') as file:
        pureEdgarFiling = file.read()
    
    # Purge HTML 
    text = ParseText(pureEdgarFiling)
    
    # Place to store EPS values to sort through
    FoundEPS = []

    # Regex patterns to extract EPS values from text
    eps_patterns = [
        # "Basic $X.XX" - used for simpleEPS tables
        r'(?:basic|Basic)\s*\$?\s*([\(-]?[0-9]+\.[0-9]+)\)?',
        # "Net income/loss/earnings ... or $X per share" - bigger / more general sentences
        r'[Nn]et\s+(?:loss|income|earnings)[^$]*?\$[^$]*?or\s*\$([0-9.-]+)\s*per\s*(basic|diluted)?\s*share',
        # "EPS was $X (basic|diluted)" 
        r'(?:basic|diluted)?\s*(?:EPS|E\.P\.S\.)\s*(?:was|of|at|is)?\s*\$?([0-9.-]+)(?:\s*\(?(?:basic|diluted)\)?)?',
        # Loss per share was $X"
        r'loss\s+(?:per|of)\s+(?:basic|diluted)?\s*share\s+(?:were|was|of|is)?\s*\$?([0-9.-]+)',
        # "$X per share" - captures the rest of the patterns not found so far
        r'\$?([0-9.-]+)\s+per\s+(?:basic|diluted)?\s*share',
    ]
    
    # Iterate through each pattern
    for pattern in eps_patterns:

        # Find all matches for the pattern & ignore case
        matches = re.finditer(pattern, text, re.IGNORECASE)

        # Iterate through each match
        for match in matches:
            try:
                # Extract EPS value, type, and context
                eValue = match.group(1)
                matchedText = match.group(0).lower()
                eType = 'basic' if 'basic' in matchedText else 'diluted' if 'diluted' in matchedText else 'unspecified'
                context = text[max(0, match.start() - 30):min(len(text), match.end() + 30)]
                
                # Skip if this is a duplicate of an EPS we found already
                if any(abs(eps['value'] - float(eValue)) < 0.001 for eps in FoundEPS):
                    continue
                
                # Check GAAP or Non-GAAP
                is_gaap = not any(term in context.lower() for term in ['non-gaap', 'non gaap', 'adjusted'])
                
                # Check if the context has loss
                is_loss = any(term in context.lower() for term in ['loss', 'deficit', 'negative'])
                
                # Convert to float and make negative if needed
                try:
                    if eValue.startswith('-') or (eValue.startswith('(') and eValue.endswith(')')):
                        eValue = -abs(float(eValue.strip('()')))
                    else:
                        eValue = float(eValue)
                
                    # If we determined loss, but val is positive, make it negative
                    if is_loss and eValue > 0:
                        eValue = -eValue

                except ValueError:
                    # Skip invalid EPS values
                    continue
                
                # Add to found EPS list
                FoundEPS.append({
                    'value': eValue,
                    'pattern': pattern,
                    'type': eType,
                    'is_gaap': is_gaap,
                    'is_net': 'net' in context.lower(),
                    'context': context
                })

            except (ValueError, TypeError):
                # Skip invalid EPS values
                continue
    
    if not FoundEPS:
        return None
    
    # Determining EPS Value Breakdown :
    # 1. First, filter for GAAP 
    gaap_values = [eps for eps in FoundEPS if eps['is_gaap']]
    if gaap_values:
        # 2. Then, prioritize basic EPS over diluted
        basic_values = [eps for eps in gaap_values if eps['type'] == 'basic']
        if basic_values:
            print("Basic Value Breakdown : " + str(basic_values[0]))
            print(" ")
            return basic_values[0]['value']
            
        # 3. If no basic EPS in GAAP, prioritize net/total EPS
        net_values = [eps for eps in gaap_values if eps['is_net']]
        if net_values:
            print("Net Value Breakdown : " + str(net_values[0]))
            print(" ")
            return net_values[0]['value']
            
        # 4. Otherwise use first GAAP value
        print("No GAAP Distinction Value Breakdown : " + str(gaap_values[0]))
        print(" ")
        return gaap_values[0]['value']
    
    # If no GAAP values, try basic values from any source
    basic_values = [eps for eps in FoundEPS if eps['type'] == 'basic']
    if basic_values:
        print("Basic Value No GAAP Distinction : " + str(basic_values[0]))
        print(" ")
        return basic_values[0]['value']
        
    # Last resort - if we have any values, return the first one
    if FoundEPS:
        print("Last Resort Value Breakdown : " + str(FoundEPS[0]))
        print(" ")
        return FoundEPS[0]['value']
        
    return None

# Main function
def ProcessEdgarFilings():
    # Output File
    output_path = 'ParsedEPS.csv'
    results = []

    # Process Edgar Filings
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            EdgarFiling = os.path.join(directory, filename)
            eps = GetEPS(EdgarFiling)
            results.append((filename, eps if eps is not None else 'EPS not found'))

    print(results)

    # Write to CSV
    with open(output_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['filename', 'EPS'])
        for row in results:
            writer.writerow(row)

# Run the script
if __name__ == "__main__":
    ProcessEdgarFilings()