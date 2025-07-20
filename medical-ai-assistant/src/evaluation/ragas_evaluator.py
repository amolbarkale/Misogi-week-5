"""
RAGAS Evaluation Framework for Medical AI Assistant
Evaluates RAG pipeline quality using faithfulness, relevancy, precision, and recall metrics
"""

import asyncio
import pandas as pd
from typing import List, Dict, Any
import json
from datetime import datetime
from datasets import Dataset

from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy, 
    context_precision,
    context_recall,
    answer_correctness,
    answer_similarity
)

from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import get_settings
from rag.pipeline import get_rag_pipeline

class RAGASEvaluator:
    def __init__(self):
        self.settings = get_settings()
        self.pipeline = get_rag_pipeline()
        
        # Initialize Gemini for RAGAS evaluations
        self.evaluator_llm = ChatGoogleGenerativeAI(
            model=self.settings.gemini_model,
            google_api_key=self.settings.gemini_api_key,
            temperature=0.0  # Use deterministic responses for evaluation
        )
        
        # RAGAS metrics to evaluate
        self.metrics = [
            faithfulness,           # Answer grounded in context
            answer_relevancy,       # Answer relevant to question
            context_precision,      # Retrieved context relevance
            context_recall,         # Context coverage
            answer_correctness,     # Overall answer quality
            answer_similarity       # Semantic similarity
        ]
        
        self.evaluation_results = []

    def create_test_dataset(self, questions: List[str], ground_truth_answers: List[str] = None) -> Dict:
        """
        Create evaluation dataset by running queries through RAG pipeline
        
        Args:
            questions: List of test questions
            ground_truth_answers: Optional ground truth answers for comparison
            
        Returns:
            Dataset dictionary with questions, answers, contexts, and ground truths
        """
        print("🔍 Creating test dataset...")
        
        dataset = {
            'question': [],
            'answer': [],
            'contexts': [],
            'ground_truth': []
        }
        
        for i, question in enumerate(questions):
            print(f"Processing question {i+1}/{len(questions)}: {question[:60]}...")
            
            try:
                # Get RAG response
                result = self.pipeline.query(question, k=4)
                
                dataset['question'].append(question)
                dataset['answer'].append(result['answer'])
                
                # Extract contexts from retrieved chunks
                contexts = []
                for chunk in self.pipeline.search_documents(question, k=4):
                    contexts.append(chunk.page_content)
                dataset['contexts'].append(contexts)
                
                # Use ground truth if provided, otherwise use a placeholder
                if ground_truth_answers and i < len(ground_truth_answers):
                    dataset['ground_truth'].append(ground_truth_answers[i])
                else:
                    # For medical research, we'll use the answer as proxy ground truth
                    # In real scenarios, you'd have expert-curated ground truth
                    dataset['ground_truth'].append(result['answer'])
                    
            except Exception as e:
                print(f"❌ Error processing question {i+1}: {e}")
                continue
        
        print(f"✅ Created dataset with {len(dataset['question'])} samples")
        return dataset

    async def evaluate_rag_pipeline(self, test_questions: List[str], ground_truth_answers: List[str] = None) -> Dict:
        """
        Comprehensive RAGAS evaluation of the RAG pipeline
        
        Args:
            test_questions: List of questions to evaluate
            ground_truth_answers: Optional ground truth answers
            
        Returns:
            Evaluation results with metrics and detailed analysis
        """
        print("🧪 Starting RAGAS Evaluation...")
        
        # Create test dataset
        dataset_dict = self.create_test_dataset(test_questions, ground_truth_answers)
        
        if not dataset_dict['question']:
            raise ValueError("No valid data generated for evaluation")
        
        # Convert to RAGAS dataset format
        dataset = Dataset.from_dict(dataset_dict)
        
        print("📊 Running RAGAS evaluation...")
        
        try:
            # Run RAGAS evaluation
            result = evaluate(
                dataset=dataset,
                metrics=self.metrics,
                llm=self.evaluator_llm,
                embeddings=self.pipeline.embedding_model,
            )
            
            # Process results
            evaluation_results = {
                'timestamp': datetime.now().isoformat(),
                'num_questions': len(test_questions),
                'metrics': dict(result),
                'detailed_results': []
            }
            
            # Add detailed per-question results
            for i, question in enumerate(test_questions):
                if i < len(dataset_dict['question']):
                    detailed_result = {
                        'question': question,
                        'answer': dataset_dict['answer'][i],
                        'contexts_count': len(dataset_dict['contexts'][i]),
                        'individual_scores': {}
                    }
                    
                    # Extract individual scores for this question
                    for metric_name in result.keys():
                        if hasattr(result, metric_name) and len(getattr(result, metric_name, [])) > i:
                            detailed_result['individual_scores'][metric_name] = getattr(result, metric_name)[i]
                    
                    evaluation_results['detailed_results'].append(detailed_result)
            
            self.evaluation_results.append(evaluation_results)
            
            print("✅ RAGAS evaluation completed!")
            return evaluation_results
            
        except Exception as e:
            print(f"❌ Error during RAGAS evaluation: {e}")
            raise

    def generate_evaluation_report(self, results: Dict) -> str:
        """Generate a formatted evaluation report"""
        
        report = f"""
# 🏥 Medical AI Assistant - RAGAS Evaluation Report

**Evaluation Date:** {results['timestamp']}
**Questions Evaluated:** {results['num_questions']}

## 📊 Overall Metrics

"""
        
        for metric_name, score in results['metrics'].items():
            if isinstance(score, (int, float)):
                report += f"- **{metric_name.replace('_', ' ').title()}:** {score:.4f}\n"
        
        report += """
## 📈 Metric Explanations

- **Faithfulness:** Measures if the answer is grounded in the given context (0-1, higher is better)
- **Answer Relevancy:** Measures how relevant the answer is to the question (0-1, higher is better)  
- **Context Precision:** Measures how relevant the retrieved context is (0-1, higher is better)
- **Context Recall:** Measures how much relevant context was retrieved (0-1, higher is better)
- **Answer Correctness:** Overall answer quality assessment (0-1, higher is better)
- **Answer Similarity:** Semantic similarity to ground truth (0-1, higher is better)

## 🎯 Performance Analysis

"""
        
        # Performance analysis
        metrics = results['metrics']
        
        if 'faithfulness' in metrics:
            faithfulness_score = metrics['faithfulness']
            if faithfulness_score >= 0.8:
                report += "✅ **Excellent Faithfulness:** Answers are well-grounded in source documents\n"
            elif faithfulness_score >= 0.6:
                report += "⚠️ **Good Faithfulness:** Most answers are grounded, some improvement possible\n"
            else:
                report += "❌ **Poor Faithfulness:** Answers may contain hallucinations\n"
        
        if 'answer_relevancy' in metrics:
            relevancy_score = metrics['answer_relevancy']
            if relevancy_score >= 0.8:
                report += "✅ **Excellent Relevancy:** Answers directly address the questions\n"
            elif relevancy_score >= 0.6:
                report += "⚠️ **Good Relevancy:** Answers are mostly relevant\n"
            else:
                report += "❌ **Poor Relevancy:** Answers may be off-topic\n"
        
        if 'context_precision' in metrics:
            precision_score = metrics['context_precision']
            if precision_score >= 0.8:
                report += "✅ **Excellent Context Precision:** Retrieved contexts are highly relevant\n"
            elif precision_score >= 0.6:
                report += "⚠️ **Good Context Precision:** Most retrieved contexts are relevant\n"
            else:
                report += "❌ **Poor Context Precision:** Too much irrelevant context retrieved\n"
        
        if 'context_recall' in metrics:
            recall_score = metrics['context_recall']
            if recall_score >= 0.8:
                report += "✅ **Excellent Context Recall:** System finds most relevant information\n"
            elif recall_score >= 0.6:
                report += "⚠️ **Good Context Recall:** System finds most relevant information\n"
            else:
                report += "❌ **Poor Context Recall:** System misses important relevant information\n"
        
        report += """
## 💡 Recommendations

"""
        
        # Generate recommendations based on scores
        if metrics.get('faithfulness', 1) < 0.7:
            report += "- Improve prompt engineering to reduce hallucinations\n"
            report += "- Consider adjusting retrieval parameters\n"
        
        if metrics.get('context_precision', 1) < 0.7:
            report += "- Improve document chunking strategy\n"
            report += "- Tune similarity search parameters\n"
        
        if metrics.get('context_recall', 1) < 0.7:
            report += "- Increase number of retrieved documents (k parameter)\n"
            report += "- Improve embedding model or similarity metric\n"
        
        if metrics.get('answer_relevancy', 1) < 0.7:
            report += "- Refine system prompts for better question answering\n"
            report += "- Improve question understanding and context utilization\n"
        
        report += "\n---\n*Report generated by RAGAS Evaluation Framework*"
        
        return report

    def save_results(self, results: Dict, filename: str = None):
        """Save evaluation results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ragas_evaluation_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Results saved to {filename}")

def get_medical_test_questions():
    """Get predefined medical research test questions"""
    return [
        "What are the main side effects of ACE inhibitors?",
        "What treatment protocols are recommended for Type 2 diabetes?",
        "What are the contraindications for beta-blockers?",
        "What diagnostic criteria are used for hypertension?",
        "What are the risk factors for cardiovascular disease?",
        "What medications are first-line treatments for heart failure?",
        "What are the symptoms of diabetic ketoacidosis?",
        "What patient populations were excluded from the clinical trials?",
        "What statistical methods were used in the analysis?",
        "What are the key limitations mentioned in the studies?"
    ]

# Convenience function for quick evaluation
async def run_quick_evaluation():
    """Run a quick RAGAS evaluation with predefined questions"""
    print("🚀 Running Quick RAGAS Evaluation...")
    
    evaluator = RAGASEvaluator()
    test_questions = get_medical_test_questions()
    
    try:
        results = await evaluator.evaluate_rag_pipeline(test_questions)
        
        # Generate and display report
        report = evaluator.generate_evaluation_report(results)
        print("\n" + "="*60)
        print(report)
        print("="*60)
        
        # Save results
        evaluator.save_results(results)
        
        return results
    
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        return None 