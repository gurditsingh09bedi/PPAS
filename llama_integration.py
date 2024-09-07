import torch
from transformers import GPT2Tokenizer, GPT2ForSequenceClassification
import logging

logging.basicConfig(filename='gpt2_model_loading.log', level=logging.ERROR)

def load_gpt2_model(model_name="gpt2"):

    try:
        print(f"Attempting to load model: {model_name}")
        tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        print("Tokenizer loaded successfully.")
        model = GPT2ForSequenceClassification.from_pretrained(model_name, num_labels=3)
        print("Model loaded successfully.")
        model.eval()  # Set model to evaluation mode
        return tokenizer, model
    except OSError as e:
        logging.error(f"OSError: {e}")
        print(f"OSError: {e}")
        return None, None
    except ValueError as e:
        logging.error(f"ValueError: {e}")
        print(f"ValueError: {e}")
        return None, None
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        return None, None

def predict_specialty_gpt2(model, tokenizer, input_text):

    try:
        # Tokenize the input text and convert it to tensor format
        inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
        
    
        with torch.no_grad():
            outputs = model(inputs)
        
        # Get the index of the predicted class (specialty)
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()

        # Map the predicted class index to a specialty.
        specialty_mapping = {
            0: "General Practitioner",
            1: "Cardiologist",
            2: "Dermatologist",
            3: "Pediatrics",
            4: "Oncology",
            5: "Neurology",
            6: "Orthopedics",
        }
        
        # Return the specialty name corresponding to the predicted class
        return specialty_mapping.get(predicted_class, "Unknown Specialty")
    except Exception as e:
        logging.error(f"Error in predicting specialty: {e}")
        print(f"Error in predicting specialty: {e}")
        return "Unknown Specialty"
