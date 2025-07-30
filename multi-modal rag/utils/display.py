import base64
import io
try:
    from IPython.display import Image, display
    IPYTHON_AVAILABLE = True
except ImportError:
    IPYTHON_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def display_base64_image(base64_code):
    """
    Display a base64 encoded image.
    
    Args:
        base64_code (str): Base64 encoded image string
    """
    # Decode the base64 string to binary
    image_data = base64.b64decode(base64_code)
    
    if IPYTHON_AVAILABLE:
        # Use IPython display if available (Jupyter notebooks)
        display(Image(data=image_data))
    elif MATPLOTLIB_AVAILABLE:
        # Use matplotlib if available
        image = mpimg.imread(io.BytesIO(image_data))
        plt.figure(figsize=(10, 8))
        plt.imshow(image)
        plt.axis('off')
        plt.show()
    else:
        print(f"Image available (base64 length: {len(base64_code)} characters)")
        print("Install IPython or matplotlib to display images")


def print_retrieval_results(docs):
    """
    Print retrieval results in a formatted way.
    
    Args:
        docs (list): List of retrieved documents
    """
    for doc in docs:
        print(str(doc) + "\n\n" + "-" * 80)


def print_response_with_context(response):
    """
    Print response along with context sources.
    
    Args:
        response (dict): Response dictionary with 'response' and 'context' keys
    """
    print("Response:", response['response'])
    
    print("\n\nContext:")
    for text in response['context']['texts']:
        print(text.text)
        print("Page number: ", text.metadata.page_number)
        print("\n" + "-" * 50 + "\n")
    
    for image in response['context']['images']:
        display_base64_image(image)