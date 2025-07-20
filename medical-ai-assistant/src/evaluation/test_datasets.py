"""
RAGAS Test Dataset Generation
Generate test questions and ground truth for evaluation
"""

import json
import asyncio
from typing import List, Dict, Any
from pathlib import Path
from dataclasses import dataclass
from core.gemini_client import get_gemini_client

@dataclass
class TestCase:
    """Single test case for RAGAS evaluation"""
    question: str
    ground_truth: str
    contexts: List[str]
    answer: str = ""
    metadata: Dict[str, Any] = None

class TestDatasetGenerator:
    """Generate test datasets for medical RAG evaluation"""
    
    def __init__(self):
        self.gemini_client = get_gemini_client()
        
    def generate_medical_questions(self, contexts: List[str], num_questions: int = 5) -> List[str]:
        """Generate medical research questions from contexts"""
        
        prompt = f"""
        Based on the following medical research contexts, generate {num_questions} specific, answerable questions.
        
        Requirements:
        - Questions should be specific and factual
        - Focus on medical findings, treatments, side effects, methodologies
        - Avoid yes/no questions
        - Make questions that require information from the provided context
        
        Contexts:
        {chr(10).join([f"Context {i+1}: {ctx[:500]}..." for i, ctx in enumerate(contexts[:3])])}
        
        Generate exactly {num_questions} questions, one per line, numbered:
        """
        
        try:
            response = self.gemini_client.chat(prompt)
            questions = []
            
            for line in response.split('\n'):
                line = line.strip()
                if line and any(char.isdigit() for char in line[:3]):
                    # Remove numbering and clean up
                    question = line.split('.', 1)[-1].strip()
                    if question and len(question) > 10:
                        questions.append(question)
            
            return questions[:num_questions]
            
        except Exception as e:
            print(f"Error generating questions: {e}")
            return self._get_fallback_questions()
    
    def generate_ground_truth(self, question: str, contexts: List[str]) -> str:
        """Generate ground truth answer for a question"""
        
        context_text = "\n\n".join(contexts)
        
        prompt = f"""
        Based ONLY on the provided medical research context, answer the following question accurately and concisely.
        
        Context:
        {context_text}
        
        Question: {question}
        
        Instructions:
        - Answer only based on the provided context
        - Be specific and factual
        - If the context doesn't contain enough information, state that clearly
        - Focus on medical accuracy
        - Keep answer concise but complete
        
        Answer:
        """
        
        try:
            return self.gemini_client.chat(prompt)
        except Exception as e:
            print(f"Error generating ground truth: {e}")
            return "Unable to generate ground truth answer."
    
    def create_test_dataset(self, pipeline, num_test_cases: int = 10) -> List[TestCase]:
        """Create a complete test dataset"""
        
        print(f"🧪 Generating {num_test_cases} test cases for RAGAS evaluation...")
        
        test_cases = []
        
        # Sample queries to get diverse contexts
        sample_queries = [
            "diabetes treatment approaches",
            "cardiovascular medication side effects", 
            "hypertension management protocols",
            "clinical trial methodologies",
            "patient safety considerations",
            "drug interactions and contraindications",
            "therapeutic effectiveness measures",
            "adverse events reporting"
        ]
        
        for i, query in enumerate(sample_queries[:num_test_cases]):
            try:
                print(f"📝 Creating test case {i+1}/{num_test_cases}: {query}")
                
                # Get relevant contexts
                chunks = pipeline.search_documents(query, k=4)
                contexts = [chunk.page_content for chunk in chunks]
                
                if not contexts:
                    continue
                
                # Generate questions from contexts
                questions = self.generate_medical_questions(contexts, num_questions=2)
                
                for question in questions[:1]:  # Take first question
                    # Generate ground truth
                    ground_truth = self.generate_ground_truth(question, contexts)
                    
                    # Get RAG answer
                    result = pipeline.query(question)
                    
                    test_case = TestCase(
                        question=question,
                        ground_truth=ground_truth,
                        contexts=contexts,
                        answer=result['answer'],
                        metadata={
                            'sources': result.get('sources', []),
                            'chunks_found': result.get('chunks_found', 0),
                            'original_query': query
                        }
                    )
                    
                    test_cases.append(test_case)
                    
                    if len(test_cases) >= num_test_cases:
                        break
                        
            except Exception as e:
                print(f"Error creating test case {i+1}: {e}")
                continue
        
        print(f"✅ Generated {len(test_cases)} test cases successfully!")
        return test_cases
    
    def save_test_dataset(self, test_cases: List[TestCase], filename: str = "ragas_test_dataset.json"):
        """Save test dataset to JSON file"""
        
        data = []
        for tc in test_cases:
            data.append({
                'question': tc.question,
                'ground_truth': tc.ground_truth,
                'contexts': tc.contexts,
                'answer': tc.answer,
                'metadata': tc.metadata or {}
            })
        
        filepath = Path("data") / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Test dataset saved to: {filepath}")
        return filepath
    
    def load_test_dataset(self, filename: str = "ragas_test_dataset.json") -> List[TestCase]:
        """Load test dataset from JSON file"""
        
        filepath = Path("data") / filename
        
        if not filepath.exists():
            print(f"❌ Test dataset not found: {filepath}")
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        test_cases = []
        for item in data:
            test_case = TestCase(
                question=item['question'],
                ground_truth=item['ground_truth'],
                contexts=item['contexts'],
                answer=item.get('answer', ''),
                metadata=item.get('metadata', {})
            )
            test_cases.append(test_case)
        
        print(f"📁 Loaded {len(test_cases)} test cases from: {filepath}")
        return test_cases
    
    def _get_fallback_questions(self) -> List[str]:
        """Fallback questions if generation fails"""
        return [
            "What are the main side effects mentioned in the studies?",
            "What treatment protocols were most effective?",
            "What were the key limitations of the research?",
            "What patient populations were studied?",
            "What statistical methods were used in the analysis?"
        ]

# Global instance
_generator = None

def get_test_dataset_generator():
    global _generator
    if _generator is None:
        _generator = TestDatasetGenerator()
    return _generator 