"""
finetune.py - ResNet-50 model fine-tuning for violence detection

Handles model training, validation, and checkpoint management with detailed logging
and progress tracking. Uses PyTorch for training and monitoring.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
import json
from pathlib import Path
import cv2
import numpy as np
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
import logging
from datetime import datetime

# Initialize rich console and logging
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('training.log'), logging.StreamHandler()]
)

class ViolenceDataset(Dataset):
    """Dataset class for violence detection frames"""
    def __init__(self, split_data, transform=None):
        self.samples = split_data
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = cv2.imread(str(img_path))
        if image is None:
            raise ValueError(f"Failed to load image: {img_path}")
            
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if self.transform:
            image = self.transform(image)
        return image, label

class ModelTrainer:
    """Handles ResNet-50 fine-tuning and training management"""
    
    def __init__(self, models_path="models", batch_size=32, num_workers=4):
        self.models_path = Path(models_path)
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.logger = logging.getLogger(__name__)
        
        # Log initialization parameters
        self.logger.info("Initializing ModelTrainer:")
        self.logger.info(f"  Device: {self.device}")
        self.logger.info(f"  Batch size: {batch_size}")
        self.logger.info(f"  Workers: {num_workers}")
        
        # Load and verify data splits
        with open(self.models_path / 'splits.json', 'r') as f:
            self.splits = json.load(f)
            
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                              std=[0.229, 0.224, 0.225])
        ])

    def setup_model(self):
        """Initialize and modify ResNet-50 for binary classification"""
        self.logger.info("Setting up ResNet-50 model...")
        model = models.resnet50(pretrained=True)
        
        # Freeze early layers
        for param in list(model.parameters())[:-20]:
            param.requires_grad = False
            
        # Modify final layer for binary classification
        num_ftrs = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Linear(num_ftrs, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, 2)
        )
        
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        self.logger.info(f"Trainable parameters: {trainable_params:,}")
        
        return model.to(self.device)

    def train_epoch(self, model, dataloader, criterion, optimizer, epoch):
        """Train for one epoch"""
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with Progress(SpinnerColumn(),
                     *Progress.get_default_columns(),
                     TimeElapsedColumn(),
                     console=console) as progress:
            
            task = progress.add_task(f"[cyan]Epoch {epoch} Training...",
                                   total=len(dataloader))
            
            for inputs, labels in dataloader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
                loss.backward()
                optimizer.step()
                
                running_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
                
                progress.advance(task)
                
        return running_loss / len(dataloader), 100. * correct / total

    def validate(self, model, dataloader, criterion, epoch):
        """Validate model performance"""
        model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad(), Progress(SpinnerColumn(),
                                     *Progress.get_default_columns(),
                                     TimeElapsedColumn(),
                                     console=console) as progress:
            
            task = progress.add_task(f"[yellow]Epoch {epoch} Validation...",
                                   total=len(dataloader))
            
            for inputs, labels in dataloader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
                running_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
                
                progress.advance(task)
                
        return running_loss / len(dataloader), 100. * correct / total

    def train(self, epochs=10):
        """Execute complete training pipeline"""
        console.print("\n[bold cyan]═══ Starting Model Training ═══")
        
        # Setup datasets
        train_dataset = ViolenceDataset(self.splits['train'], self.transform)
        val_dataset = ViolenceDataset(self.splits['val'], self.transform)
        
        self.logger.info(f"Training samples: {len(train_dataset)}")
        self.logger.info(f"Validation samples: {len(val_dataset)}")
        
        train_loader = DataLoader(train_dataset, 
                                batch_size=self.batch_size,
                                shuffle=True, 
                                num_workers=self.num_workers)
        val_loader = DataLoader(val_dataset, 
                              batch_size=self.batch_size,
                              shuffle=False, 
                              num_workers=self.num_workers)
        
        # Initialize training components
        model = self.setup_model()
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, 'min', patience=2, verbose=True
        )
        
        best_val_acc = 0
        train_history = []
        
        # Training loop
        for epoch in range(1, epochs + 1):
            epoch_start = datetime.now()
            
            train_loss, train_acc = self.train_epoch(
                model, train_loader, criterion, optimizer, epoch
            )
            val_loss, val_acc = self.validate(
                model, val_loader, criterion, epoch
            )
            
            epoch_time = datetime.now() - epoch_start
            
            # Log metrics
            metrics = {
                'epoch': epoch,
                'train_loss': train_loss,
                'train_acc': train_acc,
                'val_loss': val_loss,
                'val_acc': val_acc,
                'time': str(epoch_time)
            }
            train_history.append(metrics)
            
            self.logger.info(
                f"Epoch {epoch:3d} | "
                f"Train Loss: {train_loss:.4f} | "
                f"Train Acc: {train_acc:6.2f}% | "
                f"Val Loss: {val_loss:.4f} | "
                f"Val Acc: {val_acc:6.2f}% | "
                f"Time: {epoch_time}"
            )
            
            scheduler.step(val_loss)
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                checkpoint = {
                    'epoch': epoch,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'val_acc': val_acc,
                }
                torch.save(checkpoint, self.models_path / 'best_model.pth')
                self.logger.info(f"✓ Saved new best model (val_acc: {val_acc:.2f}%)")
            
        # Save training history
        with open(self.models_path / 'training_history.json', 'w') as f:
            json.dump(train_history, f, indent=2)
            
        console.print("[bold green]Training completed successfully!")

if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.train(epochs=10)