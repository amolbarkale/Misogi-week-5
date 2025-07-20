"""
Medical AI Assistant - Streamlit Web UI
Interactive interface for querying medical research documents
"""

import streamlit as st
import sys
import os
import asyncio
from pathlib import Path
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rag.pipeline import get_rag_pipeline
from evaluation.ragas_evaluator import get_ragas_evaluator
from evaluation.test_datasets import get_test_dataset_generator

# Page configuration
st.set_page_config(
    page_title="Medical AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}

.source-box {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
    border-left: 4px solid #1f77b4;
}

.answer-box {
    background-color: #e8f4f8;
    padding: 1.5rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
    border-left: 4px solid #28a745;
}

.query-box {
    background-color: #fff3cd;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
    border-left: 4px solid #ffc107;
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'pipeline' not in st.session_state:
        st.session_state.pipeline = None
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'pipeline_initialized' not in st.session_state:
        st.session_state.pipeline_initialized = False
    if 'ragas_results' not in st.session_state:
        st.session_state.ragas_results = None
    if 'show_ragas' not in st.session_state:
        st.session_state.show_ragas = False
    if 'fallback_mode' not in st.session_state:
        st.session_state.fallback_mode = False

def load_pipeline():
    """Load and initialize the RAG pipeline"""
    try:
        if st.session_state.pipeline is None:
            with st.spinner("🚀 Initializing Medical AI Assistant..."):
                st.session_state.pipeline = get_rag_pipeline()
                st.session_state.pipeline.setup_retriever()
                st.session_state.pipeline_initialized = True
            st.success("✅ Medical AI Assistant initialized successfully!")
        return True
    except Exception as e:
        st.error(f"❌ Error initializing pipeline: {e}")
        st.error("💡 Make sure Qdrant is running and you have documents ingested")
        
        # Enable fallback mode
        st.warning("🔄 **Fallback Mode**: Using direct Gemini chat without document retrieval")
        st.session_state.fallback_mode = True
        return False

def run_ragas_evaluation():
    """Run RAGAS evaluation in Streamlit"""
    try:
        with st.spinner("🧪 Running RAGAS evaluation..."):
            # Initialize evaluator
            evaluator = get_ragas_evaluator()
            dataset_generator = get_test_dataset_generator()
            
            # Generate test cases
            test_cases = dataset_generator.create_test_dataset(st.session_state.pipeline, num_test_cases=5)
            
            # Run evaluation
            results = asyncio.run(evaluator.evaluate_test_cases(test_cases))
            
            st.session_state.ragas_results = results
            
            return results
            
    except Exception as e:
        st.error(f"❌ RAGAS evaluation failed: {e}")
        return None

def display_ragas_results():
    """Display RAGAS evaluation results"""
    if st.session_state.ragas_results:
        results = st.session_state.ragas_results
        
        st.subheader("🎯 RAGAS Evaluation Results")
        
        # Overall score
        metrics = results['metrics']
        overall_score = sum(metrics.values()) / len(metrics)
        
        if overall_score >= 0.8:
            st.success(f"🟢 Excellent Performance: {overall_score:.3f}")
        elif overall_score >= 0.6:
            st.warning(f"🟡 Good Performance: {overall_score:.3f}")
        else:
            st.error(f"🔴 Needs Improvement: {overall_score:.3f}")
        
        # Individual metrics
        col1, col2 = st.columns(2)
        
        with col1:
            for i, (metric, score) in enumerate(metrics.items()):
                if i % 2 == 0:
                    if score >= 0.8:
                        st.metric(f"🟢 {metric.replace('_', ' ').title()}", f"{score:.3f}")
                    elif score >= 0.6:
                        st.metric(f"🟡 {metric.replace('_', ' ').title()}", f"{score:.3f}")
                    else:
                        st.metric(f"🔴 {metric.replace('_', ' ').title()}", f"{score:.3f}")
        
        with col2:
            for i, (metric, score) in enumerate(metrics.items()):
                if i % 2 == 1:
                    if score >= 0.8:
                        st.metric(f"🟢 {metric.replace('_', ' ').title()}", f"{score:.3f}")
                    elif score >= 0.6:
                        st.metric(f"🟡 {metric.replace('_', ' ').title()}", f"{score:.3f}")
                    else:
                        st.metric(f"🔴 {metric.replace('_', ' ').title()}", f"{score:.3f}")
        
        # Recommendations
        st.subheader("💡 Recommendations")
        
        if metrics.get('faithfulness', 0) < 0.7:
            st.warning("• Improve context relevance - consider better chunking strategies")
        
        if metrics.get('answer_relevancy', 0) < 0.7:
            st.warning("• Enhance answer generation - review prompts and LLM parameters")
        
        if metrics.get('context_precision', 0) < 0.7:
            st.warning("• Optimize retrieval - adjust embedding model or similarity thresholds")
        
        if metrics.get('context_recall', 0) < 0.7:
            st.warning("• Increase context coverage - consider retrieving more documents")

def display_conversation_history():
    """Display conversation history"""
    if st.session_state.conversation_history:
        st.subheader("💬 Conversation History")
        for i, entry in enumerate(reversed(st.session_state.conversation_history[-5:])):  # Show last 5
            with st.expander(f"Query {len(st.session_state.conversation_history) - i}: {entry['question'][:60]}..."):
                st.markdown(f"**🔍 Question:** {entry['question']}")
                st.markdown(f"**📝 Answer:** {entry['answer']}")
                if entry.get('sources'):
                    st.markdown(f"**📚 Sources:** {', '.join(entry['sources'])}")
                st.markdown(f"**⏰ Time:** {entry.get('timestamp', 'Unknown')}")

def fallback_chat(question):
    """Simple Gemini chat without document retrieval"""
    try:
        import google.generativeai as genai
        import os
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            return "❌ GEMINI_API_KEY not found in environment variables"
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create medical context prompt
        prompt = f"""You are a medical AI assistant. Answer this medical question based on your training knowledge:

Question: {question}

Please provide a helpful, accurate response. If you're unsure about medical advice, recommend consulting healthcare professionals."""
        
        # Generate response
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"❌ Error in fallback chat: {e}"

def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Medical AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown("**Query your medical research documents with AI-powered search and generation**")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Pipeline status
        if st.session_state.pipeline_initialized:
            st.success("✅ Pipeline Ready")
        else:
            st.warning("⏳ Pipeline Not Initialized")
        
        st.markdown("---")
        
        # Settings
        st.subheader("⚙️ Query Settings")
        retrieval_k = st.slider("Number of documents to retrieve", 1, 10, 4)
        show_context = st.checkbox("Show retrieved context", value=False)
        
        st.markdown("---")
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        if st.button("🔄 Reinitialize Pipeline"):
            st.session_state.pipeline = None
            st.session_state.pipeline_initialized = False
            st.rerun()
        
        if st.button("🗑️ Clear History"):
            st.session_state.conversation_history = []
            st.rerun()
        
        # RAGAS Evaluation
        st.markdown("---")
        st.subheader("🧪 RAGAS Evaluation")
        
        if st.button("🎯 Run RAGAS Test", help="Evaluate RAG system quality"):
            if st.session_state.pipeline_initialized:
                run_ragas_evaluation()
                st.session_state.show_ragas = True
                st.rerun()
            else:
                st.error("Initialize pipeline first")
        
        if st.session_state.ragas_results:
            if st.button("📊 View RAGAS Results"):
                st.session_state.show_ragas = True
                st.rerun()
        
        st.markdown("---")
        
        # System info
        st.subheader("ℹ️ System Info")
        st.info("💡 Make sure Qdrant is running on localhost:6333")
        st.info("📚 Ensure you have ingested medical research PDFs")
    
    # Main interface
    if not st.session_state.pipeline_initialized:
        # Try to initialize pipeline first
        if st.button("🚀 Initialize Medical AI Assistant"):
            load_pipeline()
            st.rerun()
        
        # If still not initialized, check for fallback mode
        if not st.session_state.pipeline_initialized and not st.session_state.get('fallback_mode', False):
            st.warning("⚠️ Please initialize the pipeline first")
            return
    
    # Query interface
    st.subheader("🔍 Ask Your Medical Research Question")
    
    # Input methods
    input_method = st.radio("Choose input method:", ["Type question", "Select from examples"])
    
    if input_method == "Type question":
        user_question = st.text_area(
            "Enter your medical research question:",
            placeholder="e.g., What are the side effects of ACE inhibitors mentioned in the studies?",
            height=100
        )
    else:
        example_questions = [
            "What are the main findings about diabetes treatment?",
            "What methodologies were used in cardiovascular studies?",
            "What are the side effects mentioned for hypertension medications?",
            "What are the key limitations mentioned in the research?",
            "What treatment protocols showed the best outcomes?",
            "What are the contraindications mentioned for the medications?",
            "What patient populations were studied?",
            "What statistical methods were used in the analysis?"
        ]
        user_question = st.selectbox("Select an example question:", [""] + example_questions)
    
    # Query execution
    if st.button("🔍 Ask Question", type="primary", disabled=not user_question.strip()):
        if user_question.strip():
            # Check if using fallback mode or full RAG
            if st.session_state.get('fallback_mode', False) and not st.session_state.pipeline_initialized:
                with st.spinner("🤔 Generating response with Gemini..."):
                    try:
                        start_time = time.time()
                        answer = fallback_chat(user_question)
                        end_time = time.time()
                        
                        # Create fallback result format
                        result = {
                            'answer': answer,
                            'chunks_found': 0,
                            'sources': ['Direct Gemini Response'],
                            'context': 'No document context - using general medical knowledge'
                        }
                        
                        # Display fallback mode indicator
                        st.info("🔄 **Fallback Mode**: Answer generated using general medical knowledge (no document retrieval)")
                        
                    except Exception as e:
                        st.error(f"❌ Error in fallback mode: {e}")
                        return
            else:
                with st.spinner("🤔 Searching through medical research documents..."):
                    try:
                        # Execute full RAG query
                        start_time = time.time()
                        result = st.session_state.pipeline.query(user_question, k=retrieval_k)
                        end_time = time.time()
                        
                    except Exception as e:
                        st.error(f"❌ Error during query: {e}")
                        return
            
            # Display results (common for both modes)
            st.markdown('<div class="query-box">', unsafe_allow_html=True)
            st.markdown(f"**🔍 Your Question:** {user_question}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="answer-box">', unsafe_allow_html=True)
            st.markdown("**🤖 AI Assistant Answer:**")
            st.markdown(result['answer'])
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Metadata
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Chunks Found", result['chunks_found'])
            with col2:
                st.metric("📚 Sources", len(result['sources']))
            with col3:
                st.metric("⏱️ Response Time", f"{end_time - start_time:.2f}s")
            
            # Sources
            if result['sources']:
                st.markdown('<div class="source-box">', unsafe_allow_html=True)
                st.markdown("**📚 Sources Referenced:**")
                for source in result['sources']:
                    st.markdown(f"• {source}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Context (if enabled)
            if show_context:
                with st.expander("📄 Retrieved Context (Advanced)"):
                    st.text_area("Raw context used for answer generation:", 
                               value=result['context'], 
                               height=300, 
                               disabled=True)
            
            # Save to history
            st.session_state.conversation_history.append({
                'question': user_question,
                'answer': result['answer'],
                'sources': result['sources'],
                'chunks_found': result['chunks_found'],
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'response_time': f"{end_time - start_time:.2f}s"
            })
    
    # RAGAS Results
    if st.session_state.show_ragas and st.session_state.ragas_results:
        st.markdown("---")
        display_ragas_results()
    
    # Conversation history
    if st.session_state.conversation_history:
        st.markdown("---")
        display_conversation_history()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        🏥 Medical AI Assistant - For Research Purposes Only<br>
        ⚠️ This tool is for informational and research purposes only. Always consult healthcare professionals for medical advice.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 