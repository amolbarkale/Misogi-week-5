from unstructured.partition.pdf import partition_pdf


def extract_pdf_elements(file_path, output_path="./content/"):
    """
    Extract elements from PDF including tables, text, and images.
    
    Args:
        file_path (str): Path to the PDF file
        output_path (str): Output directory path
        
    Returns:
        list: List of extracted chunks
    """
    chunks = partition_pdf(
        filename=file_path,
        infer_table_structure=True,
        strategy="hi_res",
        extract_image_block_types=["Image"],
        extract_image_block_to_payload=True,
        chunking_strategy="by_title",
        max_characters=10000,
        combine_text_under_n_chars=2000,
        new_after_n_chars=6000,
    )
    return chunks


def separate_elements(chunks):
    """
    Separate extracted elements into tables, texts, and images.
    
    Args:
        chunks (list): List of extracted chunks
        
    Returns:
        tuple: (tables, texts, images)
    """
    tables = []
    texts = []
    
    
    for chunk in chunks:
        if "Table" in str(type(chunk)):
            tables.append(chunk)
        if "CompositeElement" in str(type(chunk)):
            texts.append(chunk)
    
    images = get_images_base64(chunks)
    print(f"Extracted {len(tables)} tables, {len(texts)} text elements, and {len(images)} images.")
    print(texts[:2])  # Print first two text elements for debugging
    print(images[:2])  # Print first two images for debugging
    return tables, texts, images


def get_images_base64(chunks):
    """
    Extract base64 encoded images from chunks.
    
    Args:
        chunks (list): List of extracted chunks
        
    Returns:
        list: List of base64 encoded images
    """
    images_b64 = []
    for chunk in chunks:
        if "CompositeElement" in str(type(chunk)):
            chunk_els = chunk.metadata.orig_elements
            for el in chunk_els:
                if "Image" in str(type(el)):
                    images_b64.append(el.metadata.image_base64)
    return images_b64