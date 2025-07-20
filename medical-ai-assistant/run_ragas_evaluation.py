"""
RAGAS Evaluation Runner
Execute comprehensive RAGAS evaluation on Medical RAG system
"""

import sys
import os
import asyncio
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rag.pipeline import get_rag_pipeline
from evaluation.ragas_evaluator import get_ragas_evaluator
from evaluation.test_datasets import get_test_dataset_generator

async def run_full_evaluation():
    """Run complete RAGAS evaluation pipeline"""
    
    print("🏥 Medical AI Assistant - RAGAS Evaluation")
    print("=" * 50)
    
    try:
        # 1. Initialize components
        print("\n🚀 Initializing components...")
        pipeline = get_rag_pipeline()
        pipeline.setup_retriever()
        
        evaluator = get_ragas_evaluator()
        dataset_generator = get_test_dataset_generator()
        
        print("✅ Components initialized successfully")
        
        # 2. Generate or load test dataset
        print("\n📚 Preparing test dataset...")
        
        dataset_file = "data/ragas_test_dataset.json"
        if os.path.exists(dataset_file):
            print("📁 Loading existing test dataset...")
            test_cases = dataset_generator.load_test_dataset()
        else:
            print("🧪 Generating new test dataset...")
            test_cases = dataset_generator.create_test_dataset(pipeline, num_test_cases=10)
            dataset_generator.save_test_dataset(test_cases)
        
        if not test_cases:
            print("❌ No test cases available. Make sure you have ingested documents.")
            return
        
        print(f"✅ Using {len(test_cases)} test cases for evaluation")
        
        # 3. Run RAGAS evaluation
        print("\n📊 Running RAGAS evaluation...")
        
        results = await evaluator.evaluate_test_cases(test_cases)
        
        # 4. Display results
        print("\n🎯 RAGAS Evaluation Results")
        print("=" * 30)
        
        for metric, score in results['metrics'].items():
            print(f"{metric.replace('_', ' ').title()}: {score:.3f}")
        
        # 5. Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"data/ragas_results_{timestamp}.json"
        
        await evaluator.save_results(results, results_file)
        
        # 6. Generate summary report
        generate_summary_report(results, test_cases)
        
        print(f"\n💾 Results saved to: {results_file}")
        print("🎉 RAGAS evaluation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()

def generate_summary_report(results, test_cases):
    """Generate human-readable summary report"""
    
    print("\n📋 RAGAS Evaluation Summary")
    print("=" * 40)
    
    metrics = results['metrics']
    
    # Overall assessment
    overall_score = sum(metrics.values()) / len(metrics)
    
    if overall_score >= 0.8:
        assessment = "🟢 Excellent"
    elif overall_score >= 0.6:
        assessment = "🟡 Good"
    else:
        assessment = "🔴 Needs Improvement"
    
    print(f"Overall Performance: {assessment} ({overall_score:.3f})")
    print()
    
    # Individual metrics analysis
    print("📊 Metric Breakdown:")
    for metric, score in metrics.items():
        if score >= 0.8:
            status = "🟢"
        elif score >= 0.6:
            status = "🟡"
        else:
            status = "🔴"
        
        print(f"  {status} {metric.replace('_', ' ').title()}: {score:.3f}")
    
    print()
    
    # Recommendations
    print("💡 Recommendations:")
    
    if metrics.get('faithfulness', 0) < 0.7:
        print("  • Improve context relevance - consider better chunking strategies")
    
    if metrics.get('answer_relevancy', 0) < 0.7:
        print("  • Enhance answer generation - review prompts and LLM parameters")
    
    if metrics.get('context_precision', 0) < 0.7:
        print("  • Optimize retrieval - adjust embedding model or similarity thresholds")
    
    if metrics.get('context_recall', 0) < 0.7:
        print("  • Increase context coverage - consider retrieving more documents")
    
    print(f"\n📈 Tested on {len(test_cases)} medical research questions")
    print("🔄 Run regularly to monitor system performance")

def run_quick_evaluation():
    """Run quick evaluation with fewer test cases"""
    
    print("🏥 Medical AI Assistant - Quick RAGAS Evaluation")
    print("=" * 50)
    
    try:
        # Initialize
        pipeline = get_rag_pipeline()
        pipeline.setup_retriever()
        evaluator = get_ragas_evaluator()
        
        # Quick test questions
        quick_test_questions = [
            "What are the main side effects of ACE inhibitors?",
            "What treatment protocols showed best outcomes?",
            "What were the key limitations in the studies?"
        ]
        
        print(f"\n🧪 Testing {len(quick_test_questions)} sample questions...")
        
        results = []
        for question in quick_test_questions:
            print(f"🔍 Testing: {question[:50]}...")
            
            # Get answer
            result = pipeline.query(question)
            
            # Simple evaluation (without ground truth)
            score = evaluator.quick_evaluate(question, result['answer'], result['context'])
            
            results.append({
                'question': question,
                'answer': result['answer'],
                'score': score,
                'sources': result.get('sources', [])
            })
        
        # Display results
        avg_score = sum(r['score'] for r in results) / len(results)
        
        print(f"\n📊 Quick Evaluation Results")
        print(f"Average Score: {avg_score:.3f}")
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Question: {result['question'][:60]}...")
            print(f"   Score: {result['score']:.3f}")
            print(f"   Sources: {', '.join(result['sources'])}")
        
        print("\n💡 For comprehensive evaluation, run: python run_ragas_evaluation.py --full")
        
    except Exception as e:
        print(f"❌ Error during quick evaluation: {e}")

def main():
    """Main entry point"""
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        run_quick_evaluation()
    else:
        asyncio.run(run_full_evaluation())

if __name__ == "__main__":
    main() 