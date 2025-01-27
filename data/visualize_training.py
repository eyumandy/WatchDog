"""
visualize_training.py - Generate training history visualization
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def plot_training_history(history_path="models/training_history.json"):
    # Load training history
    with open(history_path) as f:
        history = json.load(f)
        
    # Convert to lists for plotting
    epochs = [d['epoch'] for d in history]
    train_acc = [d['train_acc'] for d in history]
    val_acc = [d['val_acc'] for d in history]
    train_loss = [d['train_loss'] for d in history]
    val_loss = [d['val_loss'] for d in history]
    
    # Set style
    sns.set_style("whitegrid")
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
    
    # Plot accuracy
    ax1.plot(epochs, train_acc, label='Training Accuracy', marker='o')
    ax1.plot(epochs, val_acc, label='Validation Accuracy', marker='o')
    ax1.set_title('Model Accuracy over Time')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy (%)')
    ax1.legend()
    ax1.grid(True)
    
    # Plot loss
    ax2.plot(epochs, train_loss, label='Training Loss', marker='o')
    ax2.plot(epochs, val_loss, label='Validation Loss', marker='o')
    ax2.set_title('Model Loss over Time')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('training_history.png')
    print("✓ Training visualization saved as 'training_history.png'")

if __name__ == "__main__":
    plot_training_history()