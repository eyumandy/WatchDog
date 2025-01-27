"""
model_inference.py - Violence detection using fine-tuned ResNet50

This script contains the ViolenceDetector class, which:
1. Initializes a ResNet50 model (pre-trained on ImageNet) and replaces its final layer.
2. Loads model weights from a checkpoint.
3. Applies necessary transforms to input frames for inference.
4. Predicts whether a given frame indicates violence and returns the probability.
"""

import torch
import torch.nn as nn
from torchvision import models, transforms
import numpy as np
import cv2
from typing import Tuple

class ViolenceDetector:
    """
    A class for detecting violence in video frames using a fine-tuned ResNet50 model.

    Attributes:
        device (torch.device): The device ('cuda' or 'cpu') to run the model on.
        model (nn.Module): The ResNet50 model, customized for violence classification.
        transform (transforms.Compose): Preprocessing operations applied to input frames.
    """

    def __init__(self, model_path: str):
        """
        Initializes the ViolenceDetector with a specified model checkpoint.

        Args:
            model_path (str): Path to the saved model checkpoint (e.g., 'model_best.pth').
        """
        # Determine which hardware to use (GPU if available, otherwise CPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load a pre-trained ResNet50 backbone (pre-trained on ImageNet)
        # Changing 'weights' can switch the base initialization of ResNet
        self.model = models.resnet50(weights='IMAGENET1K_V1')

        # Extract the number of features from the last fully connected layer (FC) of ResNet50
        num_ftrs = self.model.fc.in_features

        # Replace the final FC layer with a new classification head for 2 classes (violent / non-violent)
        # Changing the number of units in these layers modifies model capacity.
        self.model.fc = nn.Sequential(
            nn.Linear(num_ftrs, 256),  # Changing 256 affects the intermediate feature dimension
            nn.ReLU(),                 # Using ReLU for non-linearity
            nn.Dropout(0.5),           # Dropout rate of 0.5 helps prevent overfitting
            nn.Linear(256, 2)          # Final layer outputs 2 logits for the 2 classes
        )

        # Load the saved model checkpoint
        # If you change 'map_location', you can force loading on CPU or GPU
        checkpoint = torch.load(model_path, map_location=self.device)

        # Extract the model weights from the checkpoint
        state_dict = checkpoint['model_state_dict']

        # Adjust keys in the state_dict to match the current model definition
        # If your saved model used DistributedDataParallel, 'module.' may be prefixed.
        new_state_dict = {}
        for k, v in state_dict.items():
            if 'fc.' in k:
                # Keep 'fc.' in keys to match the new FC definitions
                new_state_dict[k] = v
            else:
                # Remove 'module.' from keys if present
                new_state_dict[k.replace('module.', '')] = v

        # Load the adjusted state_dict into the ResNet50 model
        self.model.load_state_dict(new_state_dict)

        # Switch the model to evaluation mode (e.g., disables dropout)
        self.model.eval()

        # Move the model to the appropriate device (GPU or CPU)
        self.model.to(self.device)

        # Define a sequence of data transforms for preprocessing frames before inference
        # Changing the Resize or Normalize parameters affects how the input is scaled and normalized.
        self.transform = transforms.Compose([
            transforms.ToPILImage(),                # Convert numpy array (OpenCV) to PIL
            transforms.Resize((224, 224)),          # Resize to 224x224, the default size for ResNet
            transforms.ToTensor(),                  # Convert PIL Image to a PyTorch tensor
            transforms.Normalize(mean=[0.485, 0.456, 0.406],  # Standard mean for ImageNet
                                 std=[0.229, 0.224, 0.225])   # Standard std for ImageNet
        ])

    def predict(self, frame: np.ndarray) -> Tuple[bool, float]:
        """
        Predicts whether a frame contains violent activity and returns the probability.

        Args:
            frame (np.ndarray): A single video frame in BGR format (OpenCV default).

        Returns:
            Tuple[bool, float]:
                - bool: True if the frame is predicted as violent, False otherwise.
                - float: The final probability of violence after transformations.
        """
        # Convert the BGR frame (OpenCV) to RGB for consistency with PIL
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Apply the pre-processing transform
        img_tensor = self.transform(rgb_frame)

        # Add batch dimension (1, C, H, W) and move to the same device as the model
        img_tensor = img_tensor.unsqueeze(0).to(self.device)

        # Disable gradient calculations for inference
        with torch.no_grad():
            # Forward pass
            outputs = self.model(img_tensor)

            # Print raw model outputs (logits) for debugging
            print("Raw logits:", outputs[0].cpu().numpy())  # shape [2] for 2 classes

            # Temperature scaling
            outputs = outputs / 1.5

            # Print logits after temperature scaling
            print("Logits after temperature scaling:", outputs[0].cpu().numpy())

            # Convert logits to probabilities
            probabilities = torch.softmax(outputs, dim=1)
            print("Probabilities:", probabilities[0].cpu().numpy())  # shape [2] for 2 classes

            # Probability of 'violent' class (index 1)
            violence_prob = probabilities[0][1].item()
            print("Violence Probability:", violence_prob)

            # Apply the custom sigmoid scaling
            violence_prob = 1 / (1 + np.exp(-5 * (violence_prob - 0.5)))
            print("Violence Probability (after custom sigmoid):", violence_prob)

        # A threshold of 0.1 to decide if a frame is violent
        # Lowering the threshold (e.g., 0.05) will produce more "violent" predictions,
        # while raising it (e.g., 0.2) will produce fewer.
        is_violent = violence_prob > 0.7

        return is_violent, violence_prob
