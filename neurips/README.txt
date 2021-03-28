# Scrape all PDFs from NeurIPS (main conference)

1. download_index.py: get an index of urls for for each year
2. download_papers.py: download the individual pdfs and associated files
3. convert_pdfs_to_text.py: convert the downloaded pdfs to text
4. check_conversion.py: print summary statistics of the number of files successfully converted


### Requirements

- tqdm
- pywget
- requests
- beautifulsoup4