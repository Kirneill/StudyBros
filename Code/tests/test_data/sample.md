# Machine Learning Fundamentals

Machine Learning (ML) is a branch of artificial intelligence that focuses on building systems that learn from data.

## Types of Machine Learning

### Supervised Learning

In supervised learning, the model learns from labeled training data. The algorithm makes predictions based on input-output pairs.

**Common Algorithms:**
- Linear Regression
- Logistic Regression
- Decision Trees
- Random Forest
- Support Vector Machines
- Neural Networks

**Use Cases:**
- Email spam classification
- Credit score prediction
- Medical diagnosis
- Image recognition

### Unsupervised Learning

Unsupervised learning works with unlabeled data. The algorithm discovers hidden patterns without explicit guidance.

**Common Algorithms:**
- K-Means Clustering
- Hierarchical Clustering
- Principal Component Analysis (PCA)
- Autoencoders

**Use Cases:**
- Customer segmentation
- Anomaly detection
- Topic modeling
- Dimensionality reduction

### Reinforcement Learning

The agent learns by interacting with an environment and receiving rewards or penalties.

**Key Concepts:**
- Agent: The learner/decision maker
- Environment: What the agent interacts with
- Action: What the agent can do
- Reward: Feedback signal
- Policy: Strategy for choosing actions

## Model Evaluation

### Classification Metrics

- **Accuracy**: Correct predictions / Total predictions
- **Precision**: True Positives / (True Positives + False Positives)
- **Recall**: True Positives / (True Positives + False Negatives)
- **F1 Score**: Harmonic mean of precision and recall
- **AUC-ROC**: Area under the receiver operating characteristic curve

### Regression Metrics

- **MSE**: Mean Squared Error
- **RMSE**: Root Mean Squared Error
- **MAE**: Mean Absolute Error
- **R²**: Coefficient of determination

## Common Challenges

1. **Overfitting**: Model memorizes training data
2. **Underfitting**: Model is too simple
3. **Data Quality**: Garbage in, garbage out
4. **Feature Engineering**: Creating meaningful inputs
5. **Bias**: Unfair or skewed predictions

## Best Practices

- Split data into train/validation/test sets
- Use cross-validation for robust evaluation
- Start with simple models before complex ones
- Monitor for data drift in production
- Document your experiments and results
