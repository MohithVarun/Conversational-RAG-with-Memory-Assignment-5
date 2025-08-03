import json
import os
import pickle
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import numpy as np
from collections import defaultdict
import logging
import hashlib
import re

# Try to import advanced embedding models
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_MODEL_AVAILABLE = True
except ImportError:
    EMBEDDING_MODEL_AVAILABLE = False
    logger.warning("sentence-transformers not available, using simple embeddings")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedKnowledgeBase:
    """
    Advanced knowledge base with embedding models, vector database,
    effective chunking strategies, and relevance scoring.
    """
    
    def __init__(self, knowledge_db_path: str = "./advanced_knowledge_db"):
        self.knowledge_db_path = knowledge_db_path
        os.makedirs(knowledge_db_path, exist_ok=True)
        
        # Knowledge storage
        self.documents = []  # Raw documents
        self.chunks = []  # Processed chunks
        self.embeddings = {}  # Document embeddings
        self.metadata = {}  # Document metadata
        
        # Embedding model
        self.embedding_model = None
        self.embedding_dimension = 384  # Default dimension
        
        # Chunking configuration
        self.chunk_size = 512  # Characters per chunk
        self.chunk_overlap = 50  # Overlap between chunks
        self.max_chunks_per_document = 10
        
        # Relevance scoring
        self.relevance_threshold = 0.6
        self.similarity_weights = {
            'semantic': 0.7,
            'keyword': 0.2,
            'category': 0.1
        }
        
        # Initialize embedding model
        self._initialize_embedding_model()
        
        # Load existing knowledge
        self._load_knowledge()
    
    def _initialize_embedding_model(self):
        """Initialize the embedding model."""
        if EMBEDDING_MODEL_AVAILABLE:
            try:
                # Use a lightweight but effective model
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.embedding_dimension = self.embedding_model.get_sentence_embedding_dimension()
                logger.info(f"✅ Successfully initialized advanced embedding model with dimension {self.embedding_dimension}")
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}")
                self.embedding_model = None
        else:
            logger.info("Using simple embedding fallback")
            self.embedding_model = None
    
    def _load_knowledge(self):
        """Load existing knowledge from disk."""
        try:
            # Load documents
            docs_file = os.path.join(self.knowledge_db_path, "documents.pkl")
            if os.path.exists(docs_file):
                with open(docs_file, 'rb') as f:
                    self.documents = pickle.load(f)
            
            # Load chunks
            chunks_file = os.path.join(self.knowledge_db_path, "chunks.pkl")
            if os.path.exists(chunks_file):
                with open(chunks_file, 'rb') as f:
                    self.chunks = pickle.load(f)
            
            # Load embeddings
            embeddings_file = os.path.join(self.knowledge_db_path, "embeddings.pkl")
            if os.path.exists(embeddings_file):
                with open(embeddings_file, 'rb') as f:
                    self.embeddings = pickle.load(f)
            
            # Load metadata
            metadata_file = os.path.join(self.knowledge_db_path, "metadata.pkl")
            if os.path.exists(metadata_file):
                with open(metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)
                    
            logger.info(f"📚 Loaded {len(self.documents)} documents, {len(self.chunks)} chunks with advanced embeddings")
        except Exception as e:
            logger.error(f"Error loading knowledge: {e}")
    
    def _save_knowledge(self):
        """Save knowledge to disk."""
        try:
            # Save documents
            docs_file = os.path.join(self.knowledge_db_path, "documents.pkl")
            with open(docs_file, 'wb') as f:
                pickle.dump(self.documents, f)
            
            # Save chunks
            chunks_file = os.path.join(self.knowledge_db_path, "chunks.pkl")
            with open(chunks_file, 'wb') as f:
                pickle.dump(self.chunks, f)
            
            # Save embeddings
            embeddings_file = os.path.join(self.knowledge_db_path, "embeddings.pkl")
            with open(embeddings_file, 'wb') as f:
                pickle.dump(self.embeddings, f)
            
            # Save metadata
            metadata_file = os.path.join(self.knowledge_db_path, "metadata.pkl")
            with open(metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)
                
            logger.info("Knowledge saved successfully")
        except Exception as e:
            logger.error(f"Error saving knowledge: {e}")
    
    def add_document(self, title: str, content: str, category: str = "general", 
                    source: str = "manual", tags: List[str] = None):
        """Add a document to the knowledge base with advanced processing."""
        document_id = self._generate_document_id(title, content)
        
        # Create document entry
        document = {
            "id": document_id,
            "title": title,
            "content": content,
            "category": category,
            "source": source,
            "tags": tags or [],
            "added_at": datetime.now().isoformat(),
            "word_count": len(content.split()),
            "char_count": len(content)
        }
        
        # Add to documents
        self.documents.append(document)
        
        # Process document into chunks
        chunks = self._chunk_document(document)
        
        # Generate embeddings for chunks
        chunk_embeddings = self._generate_chunk_embeddings(chunks)
        
        # Store chunks and embeddings
        for i, chunk in enumerate(chunks):
            chunk_id = f"{document_id}_chunk_{i}"
            chunk['id'] = chunk_id
            chunk['document_id'] = document_id
            chunk['chunk_index'] = i
            
            self.chunks.append(chunk)
            self.embeddings[chunk_id] = chunk_embeddings[i]
        
        # Store metadata
        self.metadata[document_id] = {
            "num_chunks": len(chunks),
            "categories": [category],
            "tags": tags or [],
            "processing_timestamp": datetime.now().isoformat()
        }
        
        # Save to disk
        self._save_knowledge()
        
        logger.info(f"Added document '{title}' with {len(chunks)} chunks")
        return document_id
    
    def _chunk_document(self, document: Dict) -> List[Dict]:
        """Chunk document using effective strategies tailored to content type."""
        content = document['content']
        title = document['title']
        category = document['category']
        
        chunks = []
        
        # Different chunking strategies based on content type
        if category in ['medical_condition', 'treatment', 'symptom']:
            # Medical content: chunk by sentences and paragraphs
            chunks = self._chunk_medical_content(content, title)
        elif category in ['general', 'wellness', 'prevention']:
            # General health: chunk by paragraphs
            chunks = self._chunk_general_content(content, title)
        else:
            # Default: chunk by fixed size with overlap
            chunks = self._chunk_fixed_size(content, title)
        
        return chunks[:self.max_chunks_per_document]
    
    def _chunk_medical_content(self, content: str, title: str) -> List[Dict]:
        """Chunk medical content by sentences and paragraphs."""
        chunks = []
        
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        
        for para_idx, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                continue
            
            # Split paragraph into sentences
            sentences = re.split(r'[.!?]+', paragraph)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            current_chunk = ""
            sentence_count = 0
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) > self.chunk_size:
                    if current_chunk:
                        chunks.append({
                            "content": current_chunk.strip(),
                            "title": title,
                            "chunk_type": "medical_paragraph",
                            "sentence_count": sentence_count
                        })
                        current_chunk = sentence
                        sentence_count = 1
                    else:
                        # Single long sentence
                        chunks.append({
                            "content": sentence,
                            "title": title,
                            "chunk_type": "medical_sentence",
                            "sentence_count": 1
                        })
                else:
                    current_chunk += " " + sentence
                    sentence_count += 1
            
            # Add remaining chunk
            if current_chunk:
                chunks.append({
                    "content": current_chunk.strip(),
                    "title": title,
                    "chunk_type": "medical_paragraph",
                    "sentence_count": sentence_count
                })
        
        return chunks
    
    def _chunk_general_content(self, content: str, title: str) -> List[Dict]:
        """Chunk general content by paragraphs."""
        chunks = []
        
        paragraphs = content.split('\n\n')
        
        for para_idx, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                continue
            
            # If paragraph is too long, split it
            if len(paragraph) > self.chunk_size:
                sub_chunks = self._split_long_paragraph(paragraph, title)
                chunks.extend(sub_chunks)
            else:
                chunks.append({
                    "content": paragraph.strip(),
                    "title": title,
                    "chunk_type": "general_paragraph",
                    "paragraph_index": para_idx
                })
        
        return chunks
    
    def _chunk_fixed_size(self, content: str, title: str) -> List[Dict]:
        """Chunk content by fixed size with overlap."""
        chunks = []
        
        start = 0
        while start < len(content):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(content):
                # Look for sentence ending
                for i in range(end, max(start, end - 100), -1):
                    if content[i] in '.!?':
                        end = i + 1
                        break
            
            chunk_content = content[start:end].strip()
            if chunk_content:
                chunks.append({
                    "content": chunk_content,
                    "title": title,
                    "chunk_type": "fixed_size",
                    "start_pos": start,
                    "end_pos": end
                })
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(content):
                break
        
        return chunks
    
    def _split_long_paragraph(self, paragraph: str, title: str) -> List[Dict]:
        """Split a long paragraph into smaller chunks."""
        chunks = []
        
        # Split by sentences
        sentences = re.split(r'[.!?]+', paragraph)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        current_chunk = ""
        sentence_count = 0
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.chunk_size:
                if current_chunk:
                    chunks.append({
                        "content": current_chunk.strip(),
                        "title": title,
                        "chunk_type": "split_paragraph",
                        "sentence_count": sentence_count
                    })
                    current_chunk = sentence
                    sentence_count = 1
                else:
                    # Single long sentence
                    chunks.append({
                        "content": sentence,
                        "title": title,
                        "chunk_type": "long_sentence",
                        "sentence_count": 1
                    })
            else:
                current_chunk += " " + sentence
                sentence_count += 1
        
        # Add remaining chunk
        if current_chunk:
            chunks.append({
                "content": current_chunk.strip(),
                "title": title,
                "chunk_type": "split_paragraph",
                "sentence_count": sentence_count
            })
        
        return chunks
    
    def _generate_chunk_embeddings(self, chunks: List[Dict]) -> List[np.ndarray]:
        """Generate embeddings for chunks."""
        if self.embedding_model:
            # Use sentence transformers
            texts = [chunk['content'] for chunk in chunks]
            embeddings = self.embedding_model.encode(texts)
            return embeddings.tolist()
        else:
            # Simple fallback embedding
            return [self._simple_embedding(chunk['content']) for chunk in chunks]
    
    def _simple_embedding(self, text: str) -> List[float]:
        """Simple embedding fallback using TF-IDF-like approach."""
        # Simple bag-of-words with normalization
        words = text.lower().split()
        word_freq = defaultdict(int)
        
        for word in words:
            if len(word) > 2:  # Skip short words
                word_freq[word] += 1
        
        # Create fixed-size vector
        vector = [0.0] * self.embedding_dimension
        
        # Hash words to vector positions
        for word, freq in word_freq.items():
            hash_val = hash(word) % self.embedding_dimension
            vector[hash_val] += freq
        
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = [v / norm for v in vector]
        
        return vector
    
    def search_knowledge(self, query: str, limit: int = 5, 
                        category_filter: str = None) -> List[Dict]:
        """Search knowledge base with semantic similarity and relevance scoring."""
        # Generate query embedding
        if self.embedding_model:
            query_embedding = self.embedding_model.encode([query])[0]
        else:
            query_embedding = self._simple_embedding(query)
        
        # Calculate similarities
        similarities = []
        for chunk in self.chunks:
            chunk_id = chunk['id']
            chunk_embedding = self.embeddings.get(chunk_id)
            
            if chunk_embedding is None:
                continue
            
            # Calculate semantic similarity
            semantic_sim = self._cosine_similarity(query_embedding, chunk_embedding)
            
            # Calculate keyword similarity
            keyword_sim = self._keyword_similarity(query, chunk['content'])
            
            # Calculate category similarity
            category_sim = self._category_similarity(query, chunk)
            
            # Combined similarity score
            combined_sim = (
                semantic_sim * self.similarity_weights['semantic'] +
                keyword_sim * self.similarity_weights['keyword'] +
                category_sim * self.similarity_weights['category']
            )
            
            # Apply category filter
            if category_filter and chunk.get('category') != category_filter:
                combined_sim *= 0.5  # Penalize non-matching categories
            
            similarities.append({
                'chunk': chunk,
                'similarity_score': combined_sim,
                'semantic_similarity': semantic_sim,
                'keyword_similarity': keyword_sim,
                'category_similarity': category_sim
            })
        
        # Sort by similarity and filter by threshold
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        relevant_results = [
            result for result in similarities
            if result['similarity_score'] >= self.relevance_threshold
        ]
        
        # Format results
        formatted_results = []
        for result in relevant_results[:limit]:
            chunk = result['chunk']
            formatted_results.append({
                'content': chunk['content'],
                'title': chunk['title'],
                'category': chunk.get('category', 'general'),
                'chunk_type': chunk.get('chunk_type', 'unknown'),
                'relevance_score': result['similarity_score'],
                'semantic_score': result['semantic_similarity'],
                'keyword_score': result['keyword_similarity'],
                'category_score': result['category_similarity'],
                'document_id': chunk.get('document_id'),
                'chunk_id': chunk['id']
            })
        
        return formatted_results
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception:
            return 0.0
    
    def _keyword_similarity(self, query: str, content: str) -> float:
        """Calculate keyword-based similarity."""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        # Remove stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        query_words = query_words - stop_words
        content_words = content_words - stop_words
        
        if not query_words or not content_words:
            return 0.0
        
        intersection = query_words & content_words
        union = query_words | content_words
        
        return len(intersection) / len(union) if union else 0.0
    
    def _category_similarity(self, query: str, chunk: Dict) -> float:
        """Calculate category-based similarity."""
        query_lower = query.lower()
        chunk_category = chunk.get('category', '').lower()
        chunk_title = chunk.get('title', '').lower()
        
        # Check if query contains category-related terms
        category_terms = {
            'medical_condition': ['condition', 'disease', 'illness', 'symptom'],
            'treatment': ['treatment', 'therapy', 'medication', 'cure'],
            'prevention': ['prevention', 'prevent', 'avoid', 'protection'],
            'wellness': ['wellness', 'health', 'fitness', 'lifestyle']
        }
        
        if chunk_category in category_terms:
            relevant_terms = category_terms[chunk_category]
            matches = sum(1 for term in relevant_terms if term in query_lower)
            return min(1.0, matches / len(relevant_terms))
        
        return 0.0
    
    def _generate_document_id(self, title: str, content: str) -> str:
        """Generate unique document ID."""
        combined = f"{title}:{content[:100]}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    def add_comprehensive_healthcare_data(self):
        """Add comprehensive healthcare data for demonstration."""
        healthcare_data = [
            {
                "title": "Hypertension Management",
                "category": "medical_condition",
                "content": """Hypertension, commonly known as high blood pressure, is a chronic medical condition characterized by elevated blood pressure in the arteries. It affects approximately 1.13 billion people worldwide and is a major risk factor for cardiovascular diseases.

The condition is typically diagnosed when blood pressure readings consistently exceed 140/90 mmHg. Risk factors include age, family history, obesity, physical inactivity, high salt intake, and excessive alcohol consumption.

Management strategies include lifestyle modifications such as regular exercise, weight management, reduced salt intake, and stress management. Medical treatment often involves antihypertensive medications prescribed by healthcare professionals.

Regular monitoring is essential, and patients should work closely with their healthcare team to develop personalized treatment plans. Early detection and management can significantly reduce the risk of complications such as heart disease, stroke, and kidney problems."""
            },
            {
                "title": "Diabetes Prevention and Management",
                "category": "medical_condition",
                "content": """Diabetes mellitus is a group of metabolic disorders characterized by high blood sugar levels over a prolonged period. Type 2 diabetes, the most common form, can often be prevented through lifestyle modifications.

Prevention strategies include maintaining a healthy weight, engaging in regular physical activity, following a balanced diet rich in fruits and vegetables, and avoiding tobacco use. Early detection through regular screening is crucial, especially for individuals with risk factors such as family history, obesity, or sedentary lifestyle.

Management of diabetes involves blood sugar monitoring, medication adherence, dietary modifications, and regular exercise. Patients should work with healthcare professionals to develop comprehensive care plans that address both glycemic control and prevention of complications.

Complications can include cardiovascular disease, kidney damage, nerve damage, and eye problems. Regular check-ups and proactive management are essential for maintaining quality of life and preventing long-term complications."""
            },
            {
                "title": "Common Cold Treatment and Management",
                "category": "treatment",
                "content": """The common cold is a viral infection of the upper respiratory tract, primarily caused by rhinoviruses. It is one of the most frequent illnesses affecting people worldwide, with adults typically experiencing 2-3 colds per year and children 6-8 colds per year.
 
Common cold symptoms include runny or stuffy nose, sore throat, cough (dry or productive), sneezing, mild fatigue, mild headache, and occasionally a low-grade fever. Symptoms typically develop gradually over 1-3 days and peak around days 3-5, with most colds resolving within 7-10 days.
 
Treatment for the common cold focuses on symptom management since there is no cure for the viral infection. Effective management includes adequate rest, increased fluid intake, humidification to ease congestion, saltwater gargles for sore throat relief, and over-the-counter medications such as decongestants and pain relievers. Nasal irrigation with saline solutions can help clear nasal passages, while steam inhalation may provide temporary relief from congestion.
 
Prevention strategies are crucial in reducing the frequency of colds. These include frequent hand washing, avoiding touching the face, maintaining distance from sick individuals, getting adequate sleep, maintaining good nutrition, and considering annual flu vaccination. While the flu vaccine doesn't prevent colds, it helps distinguish between cold and flu symptoms and prevents complications.
 
It's important to note that antibiotics are not effective against viral infections like the common cold and should only be used when a bacterial infection is confirmed. Overuse of antibiotics can lead to antibiotic resistance and other complications. Medical attention should be sought if symptoms persist beyond 10 days, if a high fever develops, or if severe symptoms such as difficulty breathing or severe pain occur."""
            },
            {
                "title": "Seasonal Influenza Management",
                "category": "treatment",
                "content": """Seasonal influenza, commonly known as the flu, is a highly contagious respiratory illness caused by influenza viruses. It affects millions of people worldwide each year, with peak activity typically occurring during fall and winter months.

Flu symptoms are more severe than cold symptoms and include sudden onset of high fever (100-102°F), severe body aches and muscle pain, extreme fatigue, dry cough, sore throat, headache, and sometimes gastrointestinal symptoms like nausea and vomiting. Symptoms typically last 1-2 weeks, with fatigue potentially persisting longer.

Treatment focuses on symptom management and includes rest, increased fluid intake, over-the-counter fever reducers and pain relievers, and antiviral medications if prescribed within 48 hours of symptom onset. Antiviral drugs like oseltamivir (Tamiflu) can reduce severity and duration when taken early.

Prevention is crucial and includes annual flu vaccination, frequent hand washing, avoiding close contact with sick individuals, covering coughs and sneezes, and maintaining good overall health. The flu vaccine is recommended for everyone 6 months and older, especially high-risk groups like young children, elderly adults, pregnant women, and those with chronic health conditions.

Complications can include pneumonia, bronchitis, sinus infections, and worsening of existing medical conditions. High-risk individuals should seek medical attention promptly if flu symptoms develop. Emergency warning signs include difficulty breathing, persistent chest pain, severe muscle pain, and signs of dehydration."""
            },
            {
                "title": "Seasonal Allergies and Hay Fever",
                "category": "medical_condition",
                "content": """Seasonal allergies, also known as hay fever or allergic rhinitis, affect approximately 20-30% of the population worldwide. These allergies occur when the immune system overreacts to environmental allergens such as pollen from trees, grasses, and weeds.

Symptoms typically include sneezing, runny or stuffy nose, itchy and watery eyes, itchy throat and ears, postnasal drip, and fatigue. Symptoms can range from mild to severe and often interfere with daily activities and sleep quality. Seasonal allergies are most common during spring and fall when pollen counts are highest.

Management strategies include avoiding allergens when possible, using over-the-counter antihistamines, decongestants, and nasal sprays, and considering prescription medications for more severe cases. Immunotherapy (allergy shots or sublingual tablets) can provide long-term relief for some individuals.

Prevention measures include monitoring pollen counts, keeping windows closed during high pollen periods, using air purifiers, showering after outdoor activities, and wearing sunglasses to protect eyes from pollen. Regular cleaning and vacuuming can also help reduce indoor allergens.

While seasonal allergies are not life-threatening, they can significantly impact quality of life and may trigger or worsen other conditions like asthma. Individuals with severe symptoms or those whose symptoms don't respond to over-the-counter treatments should consult healthcare professionals for personalized management strategies."""
            },
            {
                "title": "Gastroenteritis and Food Poisoning",
                "category": "medical_condition",
                "content": """Gastroenteritis, commonly known as stomach flu or food poisoning, is inflammation of the stomach and intestines that affects millions of people annually. It can be caused by viruses (most common), bacteria, parasites, or food toxins.

Symptoms typically include nausea, vomiting, diarrhea, abdominal cramps, fever, and sometimes headache and muscle aches. Symptoms usually develop within 1-3 days of exposure and can last from 24 hours to several days. Dehydration is the most serious complication, especially in young children and elderly adults.

Treatment focuses on preventing dehydration by drinking plenty of fluids, including oral rehydration solutions for severe cases. Rest is essential, and a bland diet (BRAT diet: bananas, rice, applesauce, toast) can help once vomiting subsides. Over-the-counter anti-diarrheal medications may provide relief but should be used cautiously.

Prevention strategies include proper hand washing, safe food handling and preparation, avoiding undercooked foods, drinking clean water, and maintaining good hygiene practices. Travelers should be especially careful about food and water safety in areas with different sanitation standards.

Most cases resolve on their own, but medical attention should be sought if symptoms are severe, persistent, or accompanied by signs of dehydration such as decreased urination, dry mouth, dizziness, or confusion. High fever, bloody stools, or severe abdominal pain also warrant medical evaluation."""
            },
            {
                "title": "Urinary Tract Infections",
                "category": "medical_condition",
                "content": """Urinary tract infections (UTIs) are among the most common bacterial infections, affecting millions of people annually, particularly women. UTIs occur when bacteria enter the urinary tract and multiply, most commonly affecting the bladder (cystitis) but potentially spreading to the kidneys (pyelonephritis).

Symptoms of a bladder infection include frequent, urgent urination, burning sensation during urination, cloudy or strong-smelling urine, pelvic pain, and sometimes blood in the urine. Kidney infections may cause additional symptoms like high fever, back pain, nausea, and vomiting.

Treatment typically involves antibiotics prescribed by healthcare professionals. The specific antibiotic and duration depend on the type of bacteria and severity of infection. Pain relievers and increased fluid intake can help manage symptoms while antibiotics take effect.

Prevention strategies include drinking plenty of water, urinating frequently, wiping from front to back after using the bathroom, urinating after sexual activity, avoiding irritating feminine products, and wearing cotton underwear. Cranberry products may help prevent recurrent UTIs in some individuals.

Risk factors include being female, sexual activity, certain types of birth control, menopause, urinary tract abnormalities, and suppressed immune systems. Recurrent UTIs may require further evaluation to identify underlying causes. Untreated UTIs can lead to serious complications, so prompt treatment is essential."""
            },
            {
                "title": "Skin Conditions and Dermatitis",
                "category": "medical_condition",
                "content": """Skin conditions are among the most common health concerns, affecting people of all ages. Common skin conditions include eczema (atopic dermatitis), contact dermatitis, acne, psoriasis, and fungal infections. These conditions can cause significant discomfort and impact quality of life.

Eczema is characterized by dry, itchy, inflamed skin that can appear anywhere on the body. It often runs in families and may be triggered by environmental factors, stress, or certain foods. Management includes gentle skin care, moisturizing regularly, avoiding triggers, and using prescribed medications when needed.

Contact dermatitis occurs when the skin reacts to irritants or allergens, causing redness, itching, and sometimes blisters. Common triggers include soaps, detergents, metals, plants, and cosmetics. Treatment involves identifying and avoiding triggers, using gentle skin care products, and applying prescribed creams or ointments.

Acne affects people of all ages but is most common during adolescence due to hormonal changes. It can range from mild blackheads and whiteheads to severe inflammatory acne with cysts and nodules. Treatment options include over-the-counter products, prescription medications, and lifestyle modifications.

Prevention and management strategies include gentle skin care, avoiding harsh products, protecting skin from sun damage, maintaining good hygiene, and seeking professional treatment for persistent or severe conditions. Many skin conditions can be effectively managed with proper care and treatment."""
            },
            {
                "title": "Headaches and Migraines",
                "category": "medical_condition",
                "content": """Headaches are one of the most common health complaints, affecting nearly everyone at some point in their lives. They can range from mild tension headaches to severe migraines that significantly impact daily functioning.

Tension headaches are the most common type, characterized by a dull, aching pain that feels like a tight band around the head. They're often caused by stress, poor posture, lack of sleep, or eye strain. Management includes stress reduction, regular exercise, good posture, adequate sleep, and over-the-counter pain relievers.

Migraines are more severe and typically cause intense, throbbing pain on one side of the head, often accompanied by nausea, vomiting, sensitivity to light and sound, and sometimes visual disturbances (auras). Triggers can include certain foods, stress, hormonal changes, lack of sleep, and environmental factors.

Treatment options for migraines include over-the-counter pain relievers, prescription medications, lifestyle modifications, and preventive treatments for frequent sufferers. Keeping a headache diary can help identify triggers and patterns.

Prevention strategies include maintaining regular sleep patterns, eating regular meals, staying hydrated, managing stress, avoiding known triggers, and getting regular exercise. Some individuals may benefit from preventive medications prescribed by healthcare professionals.

While most headaches are not serious, medical attention should be sought for severe, sudden headaches, headaches with fever or stiff neck, or headaches that worsen over time. These could indicate underlying medical conditions requiring immediate attention."""
            },
            {
                "title": "Back Pain and Musculoskeletal Issues",
                "category": "medical_condition",
                "content": """Back pain is one of the most common health problems, affecting up to 80% of adults at some point in their lives. It can range from mild, temporary discomfort to severe, chronic pain that significantly impacts daily activities and quality of life.

Acute back pain typically lasts less than 6 weeks and is often caused by muscle strains, ligament sprains, or poor posture. Most cases resolve with rest, gentle stretching, over-the-counter pain relievers, and gradual return to normal activities. Chronic back pain persists for more than 12 weeks and may require more comprehensive treatment.

Common causes include poor posture, heavy lifting, repetitive movements, obesity, stress, and underlying medical conditions. Prevention strategies include maintaining good posture, regular exercise to strengthen core muscles, proper lifting techniques, maintaining a healthy weight, and ergonomic workplace setup.

Treatment options range from conservative measures like physical therapy, exercise, and pain management to more invasive procedures for severe cases. Alternative therapies like acupuncture, chiropractic care, and massage may provide relief for some individuals.

Most back pain improves with time and conservative treatment. However, medical attention should be sought for severe pain, pain that radiates down the legs, numbness or weakness, or pain accompanied by fever or weight loss. These symptoms could indicate more serious underlying conditions."""
            },
            {
                "title": "Mental Health and Wellness",
                "category": "wellness",
                "content": """Mental health is an integral component of overall well-being, encompassing emotional, psychological, and social aspects of health. It affects how we think, feel, and act, influencing our ability to handle stress, relate to others, and make choices.

Maintaining good mental health involves practicing stress management techniques, maintaining social connections, getting adequate sleep, and engaging in regular physical activity. Mindfulness practices, meditation, and therapy can be valuable tools for mental wellness.

Recognizing signs of mental health challenges is crucial for early intervention. Symptoms may include persistent sadness, changes in sleep or appetite, withdrawal from social activities, and difficulty concentrating. Professional help should be sought when these symptoms persist or interfere with daily functioning.

Building resilience through healthy coping mechanisms, maintaining supportive relationships, and practicing self-care are essential for long-term mental health. Remember that seeking help is a sign of strength, and mental health professionals are trained to provide support and guidance."""
            },
            {
                "title": "Nutrition and Preventive Care",
                "category": "prevention",
                "content": """Proper nutrition plays a fundamental role in preventive healthcare and overall well-being. A balanced diet provides essential nutrients that support immune function, maintain healthy body weight, and reduce the risk of chronic diseases.

Key components of a healthy diet include adequate intake of fruits and vegetables, whole grains, lean proteins, and healthy fats. Limiting processed foods, added sugars, and excessive salt intake is important for maintaining optimal health.

Regular preventive care, including annual check-ups and age-appropriate screenings, is essential for early detection of health issues. Vaccinations, dental care, and vision exams are important components of comprehensive preventive healthcare.

Lifestyle factors such as regular exercise, adequate sleep, stress management, and avoiding tobacco and excessive alcohol use complement good nutrition in maintaining overall health. These preventive measures can significantly reduce the risk of developing chronic conditions and improve quality of life."""
            }
        ]
        
        for data in healthcare_data:
            self.add_document(
                title=data['title'],
                content=data['content'],
                category=data['category'],
                source='comprehensive_dataset',
                tags=['healthcare', 'medical', 'wellness']
            )
        
        logger.info(f"Added {len(healthcare_data)} comprehensive healthcare documents")
    
    def get_knowledge_stats(self) -> Dict:
        """Get comprehensive knowledge base statistics."""
        total_chunks = len(self.chunks)
        total_documents = len(self.documents)
        
        # Category distribution
        categories = defaultdict(int)
        for chunk in self.chunks:
            category = chunk.get('category', 'unknown')
            categories[category] += 1
        
        # Chunk type distribution
        chunk_types = defaultdict(int)
        for chunk in self.chunks:
            chunk_type = chunk.get('chunk_type', 'unknown')
            chunk_types[chunk_type] += 1
        
        # Average chunk size
        avg_chunk_size = sum(len(chunk['content']) for chunk in self.chunks) / total_chunks if total_chunks > 0 else 0
        
        return {
            "total_documents": total_documents,
            "total_chunks": total_chunks,
            "categories": dict(categories),
            "chunk_types": dict(chunk_types),
            "average_chunk_size": round(avg_chunk_size, 2),
            "embedding_dimension": self.embedding_dimension,
            "embedding_model_available": self.embedding_model is not None,
            "relevance_threshold": self.relevance_threshold,
            "last_updated": datetime.now().isoformat()
        }
    
    def export_knowledge(self, filepath: str):
        """Export knowledge base for backup or analysis."""
        export_data = {
            "documents": self.documents,
            "chunks": self.chunks,
            "metadata": self.metadata,
            "stats": self.get_knowledge_stats(),
            "export_timestamp": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"Knowledge base exported to {filepath}")
    
    def clear_knowledge(self):
        """Clear all knowledge base data."""
        self.documents = []
        self.chunks = []
        self.embeddings = {}
        self.metadata = {}
        
        # Remove files
        for filename in ['documents.pkl', 'chunks.pkl', 'embeddings.pkl', 'metadata.pkl']:
            filepath = os.path.join(self.knowledge_db_path, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        
        logger.info("Knowledge base cleared") 