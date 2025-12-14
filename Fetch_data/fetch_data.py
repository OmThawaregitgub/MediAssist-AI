from .pubmed import PubMedRetriever as pb
import chromadb
from typing import List, Dict, Any
import time
import json

class store_data:
    """
    A class to store the extracted information into the vector database with the meta data in the directory parent.pumed
    """
    def __init__(self, search_topic: str = "Cancer", max_results: int = 50) -> None:
        self.search_topic = search_topic
        self.max_results = max_results
        
        print(f"🔍 Searching PubMed for: '{search_topic}' with max_results={max_results}")
        
        # Add retry logic with delay
        for attempt in range(3):  # Try 3 times
            try:
                self.pmids = pb.search_pubmed_articles(search_topic, max_results=max_results)
                print(f"📊 Found {len(self.pmids)} PubMed IDs")
                
                if self.pmids:
                    break  # Success, exit retry loop
                else:
                    print(f"⚠️ Attempt {attempt + 1}: No PubMed IDs found")
                    if attempt < 2:  # Don't wait on last attempt
                        time.sleep(2)  # Wait 2 seconds before retry
                        
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    time.sleep(2)
                    
        if not self.pmids:
            print(f"🚨 Could not find any PubMed articles for '{search_topic}'")
            # Try with a simpler query as fallback
            print("🔄 Trying fallback search with simpler query...")
            try:
                self.pmids = pb.search_pubmed_articles("cancer treatment", max_results=10)
                print(f"📊 Found {len(self.pmids)} PubMed IDs with fallback query")
            except Exception as e:
                print(f"❌ Fallback search also failed: {e}")

    @staticmethod
    def flatten_abstract(abstract_dict: Dict[str, str]) -> str:
        """
        Flatten the abstract dictionary into a single string.
        :param abstract_dict: Dictionary containing the abstract information.
        :return: String containing the flattened abstract.
        """
        if not abstract_dict:
            return "No abstract available."
        
        # Handle different abstract formats
        if isinstance(abstract_dict, dict):
            # If it's a dict with 'text' key
            if 'text' in abstract_dict:
                return abstract_dict['text']
            # If it's a dict with multiple sections
            return " ".join([f"{k}: {v}" for k, v in abstract_dict.items() if v])
        elif isinstance(abstract_dict, str):
            return abstract_dict
        else:
            return "No abstract available."

    @staticmethod
    def format_authors(authors_data) -> str:
        """
        Format authors list properly.
        :param authors_data: List or string of authors
        :return: Formatted author string
        """
        if not authors_data:
            return "Unknown authors"
        
        # If authors is already a string
        if isinstance(authors_data, str):
            return authors_data
        
        # If authors is a list
        if isinstance(authors_data, list):
            # Check if it's a list of characters (bad parsing)
            if len(authors_data) > 0 and isinstance(authors_data[0], str) and len(authors_data[0]) == 1:
                # This is the broken format - try to reconstruct
                try:
                    # Join characters and split by commas
                    char_string = ''.join(authors_data)
                    # Clean up the string
                    cleaned = char_string.replace(',,', ',').replace('  ', ' ')
                    return cleaned
                except:
                    return " ".join(authors_data)
            else:
                # Proper list of author names
                return ', '.join([str(a) for a in authors_data[:10]])  # Limit to first 10
        
        return str(authors_data)

    def stored_in_chroma(self, records: List[Dict[str, Any]], collection_name: str = "pubmed_collection") -> bool:
        """
        Store the extracted information into the vector database.
        :param records: List of dictionaries containing the extracted information.
        :param collection_name: Name of the collection to store in
        :return: True if successful, False otherwise
        """
        try:
            if not records:
                print("No records to store.")
                return False

            client = chromadb.PersistentClient(path="./pumed")
            collection = client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )

            ids = []
            documents = []
            metadatas = []

            print(f"📝 Processing {len(records)} records for storage in '{collection_name}'...")
            
            for i, rec in enumerate(records):
                try:
                    # Generate a unique ID for each record
                    pmid = rec.get('pmid', '')
                    record_id = f"pubmed_{pmid}" if pmid else f"item_{i}_{hash(str(rec))}"
                    ids.append(record_id)

                    # Create document text
                    title = rec.get('title', 'No Title').strip()
                    abstract_text = self.flatten_abstract(rec.get('abstract', {}))
                    document_text = f"Title: {title}\n\nAbstract: {abstract_text}"
                    documents.append(document_text)

                    # Create metadata with properly formatted authors
                    metadata = {
                        "title": title,
                        "journal": rec.get('journal', 'Unknown Journal'),
                        "authors": self.format_authors(rec.get('authors', [])),
                        "publication_date": rec.get('publication_date', 'Unknown'),
                        "pmid": pmid,
                        "source": "pubmed"
                    }
                    metadatas.append(metadata)
                    
                    # Print progress for first few items
                    if i < 3:
                        print(f"  Sample record {i+1}: {title[:60]}...")
                        print(f"    Authors: {metadata['authors'][:50]}...")
                        
                except Exception as e:
                    print(f"⚠️ Error processing record {i}: {e}")
                    continue

            # Add all records to collection
            print(f"💾 Adding {len(documents)} records to ChromaDB collection '{collection_name}'...")
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            # Verify the insertion
            count = collection.count()
            print(f"✅ Successfully stored {count} articles in ChromaDB collection '{collection_name}'.")
            return True

        except Exception as e:
            print(f"❌ An error occurred while storing data in ChromaDB: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run(self, collection_name: str = "pubmed_collection") -> bool:
        """
        Execute the data fetching and storing pipeline.
        :param collection_name: Name of collection to store in
        :return: True if successful, False otherwise
        """
        try:
            if not self.pmids:
                print("🚨 No PubMed IDs available. Cannot fetch abstracts.")
                return False
            
            print(f"📥 Fetching abstracts for {len(self.pmids)} PubMed articles...")
            abstracts = pb.fetch_pubmed_abstracts(self.pmids)
            
            if not abstracts:
                print("❌ No abstracts fetched from PubMed.")
                return False
            
            print(f"📄 Fetched {len(abstracts)} abstracts. Storing in ChromaDB...")
            success = self.stored_in_chroma(abstracts, collection_name)
            return success
            
        except Exception as e:
            print(f"❌ Error in store_data.run(): {e}")
            import traceback
            traceback.print_exc()
            return False