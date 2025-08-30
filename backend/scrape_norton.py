import requests
from bs4 import BeautifulSoup
import csv
import time
import re

def scrape_norton_u():
    base_url = "https://www.norton-u.com"
    
    # Define headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Based on the screenshot, these are the main navigation items
    main_nav_items = [
        "",  # home page
        "about", 
        "academics", 
        "admissions", 
        "publication"
    ]
    
    # Additional pages that might contain useful information
    additional_pages = [
        "admission/under-graduate",
        "staff",
        "blog",
        "about/why-nu",
        "about/rector-message",
        "about/nu-structure",
        "about/mission-vision",
        "about/internationalization",
        "about/government-recognition",
        "about/library-facility",
        "about/campus",
        "about/contact-us"
    ]
    
    all_pages = []
    
    # Create URLs for main navigation
    for item in main_nav_items:
        if item == "":
            all_pages.append(base_url)
        else:
            all_pages.append(f"{base_url}/{item}")
    
    # Create URLs for additional pages
    for page in additional_pages:
        all_pages.append(f"{base_url}/{page}")
    
    # Remove duplicates
    all_pages = list(set(all_pages))
    
    # Scrape content from each page
    faq_data = []
    
    for url in all_pages:
        try:
            print(f"Scraping: {url}")
            page_response = requests.get(url, headers=headers, timeout=10)
            page_response.raise_for_status()
            
            page_soup = BeautifulSoup(page_response.content, 'html.parser')
            
            # Remove unwanted elements (nav, footer, scripts, styles)
            for element in page_soup(['nav', 'footer', 'header', 'script', 'style', 'aside']):
                element.decompose()
            
            # Extract text content
            text_content = page_soup.get_text(separator=' ', strip=True)
            text_content = re.sub(r'\s+', ' ', text_content)  # Normalize whitespace
            
            # Extract page title
            page_title = ""
            title_tag = page_soup.find('title')
            if title_tag:
                page_title = title_tag.get_text().strip()
            
            # Strategy 1: Look for FAQ sections specifically
            faq_selectors = [
                '.faq', '.faq-item', '.faq-question', '.faq-answer',
                '.accordion', '.accordion-item', '.accordion-title', '.accordion-content',
                '[class*="faq"]', '[class*="accordion"]',
                'dt', 'dd'  # definition lists are often used for FAQs
            ]
            
            for selector in faq_selectors:
                elements = page_soup.select(selector)
                for element in elements:
                    element_class = element.get('class', [])
                    class_str = ' '.join(element_class).lower() if element_class else ''
                    
                    # Check if this looks like a question element
                    if any(keyword in class_str for keyword in ['question', 'title', 'ask', 'q-']):
                        question_text = element.get_text().strip()
                        
                        # Try to find the answer (next sibling or paired element)
                        answer = find_answer_for_question(element, page_soup)
                        
                        if question_text and answer:
                            faq_data.append({
                                'question': question_text,
                                'answer': answer[:500],  # Limit answer length
                                'source': url
                            })
            
            # Strategy 2: Extract headings and their following content
            headings = page_soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for heading in headings:
                question = heading.get_text().strip()
                
                if len(question.split()) > 3:  # Reasonable question length
                    answer = extract_content_after_heading(heading)
                    
                    if answer and len(answer) > 20:  # Reasonable answer length
                        faq_data.append({
                            'question': question,
                            'answer': answer[:500],
                            'source': url
                        })
            
            # Strategy 3: Look for question-like patterns in text
            question_patterns = [
                r'(?:What|Who|Where|When|Why|How|Can|Could|Would|Should|Is|Are|Does|Do)\s+[^?.]+\?',
                r'[^.!?]*\?'
            ]
            
            for pattern in question_patterns:
                potential_questions = re.findall(pattern, text_content)
                for pq in potential_questions:
                    if len(pq) > 10 and len(pq) < 100:  # Reasonable question length
                        # Try to find answer near the question
                        answer = find_answer_near_question(pq, text_content)
                        
                        if answer:
                            faq_data.append({
                                'question': pq,
                                'answer': answer[:500],
                                'source': url
                            })
            
            time.sleep(1)  # Be polite with requests
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            continue
    
    # If we didn't find enough structured data, extract key information
    if len(faq_data) < 10:
        print("Not enough structured FAQ data found, extracting key information...")
        
        # Re-scrape main pages for general content extraction
        for url in [base_url, f"{base_url}/aboutus", f"{base_url}/academics"]:
            try:
                page_response = requests.get(url, headers=headers, timeout=10)
                page_soup = BeautifulSoup(page_response.content, 'html.parser')
                
                # Remove unwanted elements
                for element in page_soup(['nav', 'footer', 'header', 'script', 'style', 'aside']):
                    element.decompose()
                
                text_content = page_soup.get_text(separator=' ', strip=True)
                text_content = re.sub(r'\s+', ' ', text_content)
                
                # Extract informative sentences
                sentences = re.split(r'[.!?]', text_content)
                informative_sentences = [s.strip() for s in sentences 
                                       if len(s.split()) > 5 and len(s.split()) < 30]
                
                # Create Q&A pairs from informative content
                for i in range(0, min(15, len(informative_sentences)), 2):
                    if i+1 < len(informative_sentences):
                        question = f"Tell me about {informative_sentences[i]}"
                        faq_data.append({
                            'question': question,
                            'answer': informative_sentences[i+1][:500],
                            'source': url
                        })
                        
            except Exception as e:
                print(f"Error in fallback scraping {url}: {e}")
                continue
    
    # Remove duplicates
    unique_faqs = []
    seen_questions = set()
    for item in faq_data:
        if item['question'] not in seen_questions:
            unique_faqs.append(item)
            seen_questions.add(item['question'])
    
    return unique_faqs

def find_answer_for_question(question_element, soup):
    """Find the answer element associated with a question element"""
    # Check if next sibling is the answer
    next_sib = question_element.next_sibling
    while next_sib:
        if next_sib.name and next_sib.name in ['p', 'div']:
            return next_sib.get_text().strip()
        next_sib = next_sib.next_sibling
    
    # Check parent's next sibling
    parent = question_element.parent
    if parent:
        next_parent_sib = parent.next_sibling
        while next_parent_sib:
            if next_parent_sib.name and next_parent_sib.name in ['p', 'div']:
                return next_parent_sib.get_text().strip()
            next_parent_sib = next_parent_sib.next_sibling
    
    return None

def extract_content_after_heading(heading):
    """Extract content that follows a heading"""
    content = []
    next_element = heading.next_sibling
    
    while next_element and next_element.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        if next_element.name == 'p':
            content.append(next_element.get_text().strip())
        elif next_element.name is None and isinstance(next_element, str):
            text = str(next_element).strip()
            if text:
                content.append(text)
        
        next_element = next_element.next_sibling
        if next_element is None:
            break
    
    return ' '.join(content) if content else None

def find_answer_near_question(question, full_text):
    """Find text that might answer the question"""
    # Find the position of the question in the text
    start_pos = full_text.find(question)
    if start_pos == -1:
        return None
    
    # Look for text after the question
    after_text = full_text[start_pos + len(question):start_pos + 500]  # Look at next 500 chars
    sentences = re.split(r'[.!?]', after_text)
    
    if sentences and len(sentences[0].strip()) > 10:
        return sentences[0].strip()
    
    return None

def save_to_csv(faq_data, filename="data/faqs.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['question', 'answer'])
        writer.writeheader()
        for item in faq_data:
            writer.writerow({'question': item['question'], 'answer': item['answer']})
    
    print(f"Saved {len(faq_data)} FAQs to {filename}")

if __name__ == "__main__":
    print("Starting to scrape Norton University website...")
    faqs = scrape_norton_u()
    
    if faqs:
        save_to_csv(faqs)
        print("Scraping completed successfully!")
        
        # Also update the training data
        try:
            from prepare_dataset import csv_to_txt
            csv_to_txt("data/faqs.csv", "train.txt")
            print("Training data updated!")
        except Exception as e:
            print(f"Error updating training data: {e}")
    else:
        print("No data was scraped. Using fallback FAQs.")
        
        # Create a fallback FAQ file with basic information
        fallback_faqs = [
            {"question": "What is Norton University?", "answer": "Norton University is a leading educational institution in Cambodia, offering various undergraduate and graduate programs."},
            {"question": "How to contact Norton University?", "answer": "You can contact Norton University through their website contact form, email, or phone number listed on their official website."},
            {"question": "What programs does Norton University offer?", "answer": "Norton University offers various undergraduate and graduate programs across different faculties including Business, IT, and more."},
            {"question": "How to apply to Norton University?", "answer": "You can apply to Norton University through their online application system on their website or by visiting the admissions office."},
            {"question": "What are the tuition fees at Norton University?", "answer": "For detailed information about tuition fees, please visit the Norton University website or contact their admissions office directly."},
            {"question": "Does Norton University offer scholarships?", "answer": "Norton University may offer scholarships and financial aid programs. Please check their website or contact the financial aid office for current opportunities."},
            {"question": "What are the admission requirements?", "answer": "Admission requirements vary by program. Generally, you'll need to submit academic transcripts, identification documents, and possibly pass an entrance examination."},
            {"question": "Where is Norton University located?", "answer": "Norton University is located in Phnom Penh, Cambodia. The exact address can be found on their official website."}
        ]
        
        save_to_csv(fallback_faqs)
        
        # Update training data
        try:
            from prepare_dataset import csv_to_txt
            csv_to_txt("data/faqs.csv", "train.txt")
            print("Fallback FAQs created and training data updated!")
        except Exception as e:
            print(f"Error updating training data: {e}")