"""
Course 2: AI & Machine Learning Foundations
Seed content for the Agentic AI LMS. See content/seed/SCHEMA.md for the
field-by-field contract this file must follow.
"""

COURSE = {
    "slug": "ai-ml-foundations",
    "title": "AI & Machine Learning Foundations",
    "subtitle": "The ML concepts underneath every model you'll later prompt, embed, or fine-tune.",
    "description": (
        "A grounded introduction to artificial intelligence and machine learning for people headed "
        "toward building AI agents, not toward becoming ML researchers. You'll learn how models "
        "learn from data, how to evaluate them honestly, and how embeddings turn meaning into "
        "numbers — the last topic being your direct bridge into the LLM and RAG courses ahead."
    ),
    "learning_outcomes": [
        "Explain the relationship between AI, machine learning, and deep learning",
        "Describe the end-to-end machine learning workflow from data to deployed model",
        "Differentiate supervised and unsupervised learning and choose the right approach for a problem",
        "Evaluate models honestly using appropriate metrics and avoid overfitting traps",
        "Engineer and encode features that make models perform better",
        "Explain what embeddings are and why they let computers reason about meaning",
        "Describe how a neural network learns through forward passes and backpropagation",
    ],
    "order_index": 2,
    "estimated_hours": 16,
    "level": "beginner",
    "icon": "brain",
    "modules": [
        {
            "slug": "ai-fundamentals",
            "title": "AI Fundamentals",
            "description": "What artificial intelligence actually means in practice, and how it relates to machine learning and deep learning.",
            "order_index": 1,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "what-is-artificial-intelligence",
                    "title": "What is Artificial Intelligence?",
                    "description": "A working definition of AI, its major subfields, and why 'AI' has meant different things across different decades.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Define artificial intelligence in terms of task performance rather than hype",
                        "Distinguish narrow AI from the general AI ambitions still unrealized today",
                        "Identify AI's major subfields: ML, NLP, computer vision, robotics, planning",
                        "Explain where large language models and agents fit within this landscape",
                    ],
                    "content_markdown": """
## Why this matters

You're about to spend the rest of this program building things people call "AI agents." Before
writing a line of agent code, it's worth being precise about what that word actually promises,
because the gap between "AI" the marketing term and AI the engineering discipline is where most
unrealistic expectations come from — yours and your future users'.

## A working definition

Artificial intelligence is the field of building systems that perform tasks which normally require
human intelligence: recognizing patterns, understanding language, making decisions under
uncertainty, planning multi-step actions. Note this definition is about **task performance**, not
about a system being conscious or "understanding" in some deep sense — a chess engine that beats
every human alive is AI by this definition even though nobody claims it's sentient.

## Narrow AI vs general AI

Almost everything you'll build in this program is **narrow AI**: a system that is very good at a
specific class of tasks (answering questions, retrieving documents, calling tools) but has no
capability outside that class. **General AI** (or AGI) — a system with human-like flexibility across
essentially any task — remains a research goal, not something shipping in products today. When you
hear "AI agent," you're hearing about a narrow-AI system, built from an LLM, that has been given
tools and a loop, not a general intelligence.

## The major subfields

- **Machine learning (ML)** — systems that improve at a task by learning patterns from data, rather
  than being explicitly programmed with rules. This is the foundation for almost everything else on
  this list, and the subject of the rest of this course.
- **Natural language processing (NLP)** — understanding and generating human language; large
  language models are today's dominant NLP technology, covered starting in Course 3.
- **Computer vision** — interpreting images and video; outside this program's scope but built on
  the same neural network foundations you'll meet in this course's final module.
- **Robotics and planning** — physical or abstract multi-step action sequences toward a goal; the
  "planning" skill you'll build agents around in Course 9 borrows directly from this subfield.

## Where LLMs and agents fit

A large language model is a machine learning model (specifically, a deep neural network trained on
huge amounts of text) applied to the NLP subfield. An "AI agent" is not a new kind of model — it's
an LLM wrapped in a software loop that gives it memory, tools, and the ability to take multiple
steps toward a goal. Understanding that an agent is an application layer built *on top of* an ML
model, rather than a fundamentally different technology, will make the rest of this program's
architecture much easier to reason about.

## Looking ahead

Course 3 zooms all the way into the "NLP" box above and stays there for the rest of the program.
Everything in this module and the next is context that keeps you from over- or under-estimating
what an LLM-based agent can actually do.
""",
                    "examples": [
                        {
                            "title": "Example: Classifying a system as narrow AI",
                            "code": "# A spam filter that only classifies email as spam/not-spam\n# is narrow AI: excellent at one task, no ability to do anything else.\nis_narrow_ai = True\ncan_generalize_to_new_tasks = False",
                            "explanation": "Illustrates the narrow-vs-general distinction with a concrete, familiar example most people have direct experience with.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "List three AI systems you use in daily life and classify each as narrow AI, explaining briefly what specific task each one performs.",
                            "difficulty": "easy",
                            "hint": "Think about recommendation systems, voice assistants, spam filters, or navigation apps.",
                        },
                        {
                            "prompt": "In 2-3 sentences, explain why calling a large language model 'general intelligence' would be inaccurate given the narrow-vs-general distinction from this lesson.",
                            "difficulty": "medium",
                            "hint": "Consider what an LLM can and cannot do without being given external tools.",
                        },
                        {
                            "prompt": "Sketch (in words) where an 'AI agent' that books flights would sit in the AI subfield diagram: which subfields does it combine?",
                            "difficulty": "medium",
                            "hint": "It likely combines NLP (understanding requests) with planning (multi-step booking actions).",
                        },
                    ],
                    "resources": [
                        {"title": "Stanford Encyclopedia of Philosophy: Artificial Intelligence", "url": "https://plato.stanford.edu/entries/artificial-intelligence/", "resource_type": "reference"},
                    ],
                    "skills": [{"slug": "ai-ml", "weight": 1.0}],
                },
                {
                    "slug": "ai-vs-ml-vs-deep-learning",
                    "title": "AI vs ML vs Deep Learning",
                    "description": "Understanding these three terms as nested subsets, and where today's LLMs sit inside that nesting.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain the nested relationship between AI, ML, and deep learning",
                        "Distinguish rule-based systems from learned models",
                        "Identify why deep learning specifically enabled the current generation of LLMs",
                        "Correctly place a given system into the right layer of the nesting",
                    ],
                    "content_markdown": """
## Why this matters

These three terms get used almost interchangeably in casual conversation, but precision here
prevents real confusion later — when you hear "fine-tuning a model" or "training a neural network,"
you need to know exactly which layer of this stack that operation touches.

## Three nested circles

Think of it as three concentric circles:

- **Artificial Intelligence** (outermost) — any system performing tasks that require intelligence,
  covered in the previous lesson.
- **Machine Learning** (inside AI) — AI systems that improve by learning patterns from data, rather
  than following hand-written rules.
- **Deep Learning** (inside ML) — machine learning using neural networks with many layers, capable
  of learning far more complex patterns than traditional ML algorithms.

Every deep learning system is a machine learning system, and every machine learning system is an AI
system — but the reverse isn't true. A simple rule-based chatbot ("if the message contains 'refund',
reply with the refund policy") is AI but not ML, because it never learns from data.

## Rule-based systems vs learned models

```python
# Rule-based (NOT machine learning): a human wrote every branch explicitly
def classify_sentiment_rules(text):
    if "love" in text or "great" in text:
        return "positive"
    elif "hate" in text or "terrible" in text:
        return "negative"
    return "neutral"

# Machine learning: the classifier LEARNED these patterns from labeled examples,
# rather than a human enumerating every keyword by hand.
# model.predict(["This product exceeded my expectations"])  -> "positive"
```

The rule-based version breaks the moment someone writes "not bad at all" or uses sarcasm the rules
didn't anticipate. A learned model, trained on enough labeled examples, can pick up subtler patterns
no human explicitly wrote down — that generalization is the core value proposition of ML over
hand-written rules.

## Why deep learning specifically enabled LLMs

Traditional ML algorithms (covered in this course's Supervised and Unsupervised Learning modules)
work well on structured, tabular data but struggle to capture the messy, long-range patterns in raw
text. Deep neural networks, especially the transformer architecture you'll study in depth in Course
3, can learn extremely rich representations of language directly from raw text at massive scale.
Large language models are, technically, very large deep learning models — nothing more mystical than
that, though the scale changes what becomes possible in practice.

## Placing systems correctly

- A spam filter using hand-coded keyword rules → AI, not ML.
- A spam filter trained on thousands of labeled emails using logistic regression → AI and ML, not
  deep learning.
- Claude, GPT-style models, and other LLMs → AI, ML, and deep learning, all three circles.

## Looking ahead

The next module walks through exactly how that middle circle — machine learning — actually learns
from data, using the classic supervised/unsupervised split. By the end of this course you'll be able
to place any AI system you encounter, including every model in this program, into the right layer of
this nesting without hesitation.
""",
                    "examples": [
                        {
                            "title": "Example: Sorting technologies into the right circle",
                            "code": "systems = {\n    \"hand-coded chess rules\": \"AI only\",\n    \"linear regression predicting house prices\": \"AI + ML\",\n    \"a convolutional network classifying images\": \"AI + ML + Deep Learning\",\n    \"an LLM like Claude\": \"AI + ML + Deep Learning\",\n}\nfor system, layer in systems.items():\n    print(f\"{system}: {layer}\")",
                            "explanation": "Applies the nested-circles framework to concrete, varied examples to make the classification concrete rather than abstract.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "For each of: a thermostat with a fixed temperature rule, a recommendation engine trained on purchase history, and a self-driving car's vision system — classify each into AI-only, AI+ML, or AI+ML+Deep Learning.",
                            "difficulty": "medium",
                            "hint": "Ask whether the system learns from data, and if so, whether it uses many-layered neural networks.",
                        },
                        {
                            "prompt": "Write a short rule-based function (no ML) that tries to detect whether a sentence is a question, and describe one case where your rules would fail.",
                            "difficulty": "easy",
                            "hint": "A simple rule might check for a trailing '?', which fails on rhetorical statements or questions missing punctuation.",
                        },
                        {
                            "prompt": "Explain in 2-3 sentences why 'deep learning' is a strict subset of 'machine learning' rather than a separate, unrelated field.",
                            "difficulty": "easy",
                            "hint": "Consider whether deep learning models still learn from data rather than following hard-coded rules.",
                        },
                    ],
                    "resources": [
                        {"title": "scikit-learn: An introduction to machine learning with scikit-learn", "url": "https://scikit-learn.org/stable/tutorial/basic/tutorial.html", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "ai-ml", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "machine-learning-fundamentals",
            "title": "Machine Learning Fundamentals",
            "description": "The standard workflow every ML project follows, from raw data to a model you can trust.",
            "order_index": 2,
            "estimated_hours": 2.0,
            "lessons": [
                {
                    "slug": "the-machine-learning-workflow",
                    "title": "The Machine Learning Workflow",
                    "description": "The repeatable pipeline of collecting data, training, evaluating, and deploying a model.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "List the stages of a typical machine learning workflow in order",
                        "Explain why data quality dominates model quality",
                        "Describe what 'training' a model actually means mechanically",
                        "Connect this workflow to how foundation models like LLMs are themselves trained",
                    ],
                    "content_markdown": """
## Why this matters

Even though you won't train a foundation model from scratch in this program, you will fine-tune,
evaluate, and build retrieval systems around models — and every one of those activities borrows
vocabulary and structure directly from the standard ML workflow. Knowing this workflow means you can
read an ML paper's methodology section, or a model card, and actually understand what happened.

## The stages

1. **Problem definition** — what exactly are we predicting, and what does success look like?
2. **Data collection** — gathering examples relevant to the task.
3. **Data preparation** — cleaning, transforming, and splitting data (covered in the Feature
   Engineering module).
4. **Model training** — the algorithm adjusts its internal parameters to fit the training data.
5. **Evaluation** — measuring performance on data the model did NOT train on (the Model Evaluation
   module covers this in depth).
6. **Deployment** — putting the trained model where real users or systems can call it.
7. **Monitoring** — watching for the model's real-world performance degrading over time ("drift").

## Data quality dominates everything downstream

A common saying in ML: "garbage in, garbage out." A sophisticated model trained on biased,
mislabeled, or unrepresentative data will confidently produce biased, wrong predictions — the
sophistication of the algorithm cannot compensate for bad data. This is exactly as true for LLMs:
their behavior is a direct reflection of the (enormous) text corpus they were trained on, which is
why prompt engineering (Course 4) and RAG (Course 5) exist partly to compensate for gaps and biases
in what a model learned during training.

## What "training" mechanically means

```python
# Conceptual sketch of what training loops do, using plain Python (not a real ML library)
weights = [0.0, 0.0]  # the model's learnable parameters, start at zero

def predict(x, weights):
    return weights[0] * x[0] + weights[1] * x[1]

def update_weights(weights, x, true_value, learning_rate=0.01):
    prediction = predict(x, weights)
    error = true_value - prediction
    # nudge each weight a little in the direction that reduces the error
    weights[0] += learning_rate * error * x[0]
    weights[1] += learning_rate * error * x[1]
    return weights

# Repeating update_weights over many examples is, at its core, what "training" means.
```

This tiny loop is a simplified skeleton of gradient-based learning: look at how wrong the current
prediction is, nudge the parameters slightly to reduce that error, and repeat over many examples
until performance stabilizes. Neural networks (covered later in this course) do the same thing at a
vastly larger scale with far more parameters.

## How this connects to foundation models

Training an LLM follows the exact same numbered workflow above, just at an enormous scale: the
"data" is a large fraction of the public internet plus curated sources, the "model" has billions of
parameters instead of two, and "evaluation" involves benchmarks across reasoning, coding, and
safety. You will never run this training loop yourself in this program — but recognizing that GPT-
and Claude-style models are the product of exactly this workflow, scaled up, demystifies a lot of
what otherwise sounds like magic.

## Looking ahead

The next lesson digs into step 3 and step 5 specifically — how data gets split into training,
validation, and test sets, and why skipping that split is one of the most common and damaging
mistakes in applied ML.
""",
                    "examples": [
                        {
                            "title": "Example: A minimal training loop over multiple examples",
                            "code": "weights = [0.0, 0.0]\ndata = [((1, 2), 5), ((2, 0), 4), ((0, 3), 3)]  # (features, true_value) pairs\n\nfor epoch in range(100):\n    for x, true_value in data:\n        weights = update_weights(weights, x, true_value)\n\nprint(weights)  # learned approximate coefficients",
                            "explanation": "Runs the earlier update_weights function repeatedly over a small dataset, each full pass called an 'epoch' -- the same term used when training neural networks.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "List the seven ML workflow stages from this lesson in order, and for each one write one sentence describing what would go wrong if that stage were skipped entirely.",
                            "difficulty": "medium",
                            "hint": "For example, skipping evaluation means you'd deploy a model with no idea how well it actually performs.",
                        },
                        {
                            "prompt": "Modify the update_weights function so it also tracks and prints the total squared error across the dataset once per epoch, so you can observe the error decreasing.",
                            "difficulty": "hard",
                            "hint": "Accumulate (true_value - predict(x, weights)) ** 2 for each example within the epoch loop.",
                        },
                        {
                            "prompt": "Explain in 2-3 sentences why 'garbage in, garbage out' applies just as much to a RAG system's retrieved documents as it does to a model's training data.",
                            "difficulty": "medium",
                            "hint": "Think about what an LLM does with irrelevant or wrong context it's given at inference time.",
                        },
                    ],
                    "resources": [
                        {"title": "Google Developers: Machine Learning Crash Course", "url": "https://developers.google.com/machine-learning/crash-course", "resource_type": "tutorial"},
                    ],
                    "skills": [{"slug": "ai-ml", "weight": 1.0}],
                },
                {
                    "slug": "training-validation-and-test-sets",
                    "title": "Training, Validation, and Test Sets",
                    "description": "Why you must never evaluate a model on the data it trained on, and how to split data correctly.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain the purpose of training, validation, and test splits",
                        "Split a dataset into these three sets using standard proportions",
                        "Identify data leakage and explain why it inflates apparent performance",
                        "Apply this same discipline to evaluating LLM-based systems",
                    ],
                    "content_markdown": """
## Why this matters

This is, arguably, the single most important discipline in all of applied machine learning — and
directly the discipline underneath your Course 12 evaluation harness for AI agents. Get this wrong
and every metric you report is a lie, even if you never intend to lie.

## Why one dataset isn't enough

If you train a model on a dataset and then measure its accuracy on that *same* dataset, you're
measuring how well it memorized the answers, not how well it generalizes to new, unseen cases. A
model can achieve 99% "accuracy" this way while being nearly useless on real, new inputs — this
failure mode is common enough that it has a name: overfitting, covered in depth in the Model
Evaluation module.

## The three-way split

```python
import random

def split_dataset(data, train_ratio=0.7, val_ratio=0.15, seed=42):
    shuffled = data[:]
    random.Random(seed).shuffle(shuffled)
    n = len(shuffled)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)
    return shuffled[:train_end], shuffled[train_end:val_end], shuffled[val_end:]

data = list(range(100))  # stand-in for 100 labeled examples
train, val, test = split_dataset(data)
print(len(train), len(val), len(test))  # roughly 70, 15, 15
```

- **Training set** — the data the model actually learns from; its parameters are adjusted to fit
  this data.
- **Validation set** — used *during development* to tune choices like model architecture or
  hyperparameters, and to check for overfitting, without touching the test set.
- **Test set** — touched exactly once, at the very end, to report a final, honest performance
  number. If you keep going back to the test set and adjusting your model based on it, it quietly
  becomes a second validation set and stops being a trustworthy final measure.

## Data leakage

Data leakage happens when information from outside the training set — often accidentally — leaks
into it, inflating apparent performance in a way that won't hold up in production. Common causes:
duplicate rows split across train and test, features that indirectly encode the label, or
normalizing/scaling the *entire* dataset (including test data) before splitting instead of after.

```python
# WRONG: fitting a scaler on the full dataset before splitting leaks test statistics into training
# scaler.fit(full_data)
# train, test = split(full_data)

# RIGHT: split first, fit the scaler only on the training set
train, val, test = split_dataset(data)
# scaler.fit(train)
# scaler.transform(val); scaler.transform(test)
```

## Applying this discipline to LLM systems

You will not train an LLM from scratch, but you will build and evaluate RAG pipelines and agents in
later courses. The same discipline applies directly: your Course 12 evaluation set of test questions
must be kept separate from any examples you used to iterate on your prompts or retrieval logic — if
you keep tweaking your prompt based on how it performs on your "eval set," that set has effectively
become a validation set, and you need a genuinely held-out test set to report honest final numbers.

## Looking ahead

The Model Evaluation module later in this course builds directly on this split to define concepts
like overfitting and cross-validation. Course 12 (Evaluation & Safety) reuses this exact
train/validation/test discipline, just applied to prompts, retrieval configs, and agent behaviors
instead of model weights.
""",
                    "examples": [
                        {
                            "title": "Example: A leakage-free preprocessing pipeline order",
                            "code": "train, val, test = split_dataset(list(range(200)))\n\n# Fit any transformation (scaling, encoding) ONLY on train\nmean_train = sum(train) / len(train)\n\n# Apply that same transformation to val and test, never refit on them\nval_transformed = [x - mean_train for x in val]\ntest_transformed = [x - mean_train for x in test]",
                            "explanation": "Demonstrates the correct order of operations: split first, then fit any statistics-based transformation only on the training portion.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Using the split_dataset function, split a list of 500 items into train/val/test with a 60/20/20 ratio and print the size of each split.",
                            "difficulty": "easy",
                            "hint": "Pass train_ratio=0.6, val_ratio=0.2 as arguments.",
                        },
                        {
                            "prompt": "Describe a realistic data leakage scenario in a project that classifies support tickets as urgent/not-urgent, where the same customer's tickets appear in both train and test sets.",
                            "difficulty": "medium",
                            "hint": "Consider whether a model could learn to recognize a specific customer's writing style rather than genuine urgency signals.",
                        },
                        {
                            "prompt": "Explain why touching the test set repeatedly while tuning a model is problematic, using your own words and a concrete example of how it could mislead a team about production readiness.",
                            "difficulty": "hard",
                            "hint": "Think about what happens if you pick the model configuration that happens to score highest on the test set purely by chance.",
                        },
                    ],
                    "resources": [
                        {"title": "scikit-learn: Cross-validation - evaluating estimator performance", "url": "https://scikit-learn.org/stable/modules/cross_validation.html", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "ai-ml", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "supervised-learning",
            "title": "Supervised Learning",
            "description": "Learning from labeled examples: regression for continuous outputs and classification for discrete categories.",
            "order_index": 3,
            "estimated_hours": 2.5,
            "lessons": [
                {
                    "slug": "regression-algorithms",
                    "title": "Regression Algorithms",
                    "description": "Predicting continuous numeric values with linear regression, and reading the resulting model's coefficients.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Explain what regression predicts and when it applies",
                        "Fit a simple linear regression model using scikit-learn",
                        "Interpret model coefficients and predictions",
                        "Identify regression-shaped problems in AI system design",
                    ],
                    "content_markdown": """
## Why this matters

Regression is the simplest, most interpretable form of supervised learning, and understanding it
builds the intuition you'll need for every more complex model in this course, including the
underlying math behind how a neural network's output layer often works.

## What regression predicts

Regression predicts a **continuous numeric value** — a price, a temperature, a probability, a
count. Contrast this with classification (next lesson), which predicts a **discrete category**.
"How many tokens will this response use?" is a regression-shaped question; "is this response safe or
unsafe?" is a classification-shaped question.

## Linear regression in practice

```python
from sklearn.linear_model import LinearRegression
import numpy as np

# Features: [square_footage, num_bedrooms], Target: price in thousands
X = np.array([[1000, 2], [1500, 3], [2000, 3], [2500, 4]])
y = np.array([200, 300, 350, 450])

model = LinearRegression()
model.fit(X, y)

print(model.coef_)        # learned weight for each feature
print(model.intercept_)   # baseline value when all features are 0

prediction = model.predict([[1800, 3]])
print(prediction)  # estimated price for an 1800 sqft, 3-bedroom house
```

`model.fit(X, y)` is where training happens: scikit-learn finds the coefficients that minimize the
squared error between predictions and true values across the training data — mechanically similar to
the tiny hand-written training loop from the previous module, just solved directly rather than by
iterative nudging.

## Interpreting coefficients

Each coefficient in `model.coef_` tells you how much the prediction changes for a one-unit increase
in that feature, holding others constant. This interpretability is a major advantage of linear
regression over more complex models — you can explain *why* the model predicted what it did, which
matters when a model's decision needs to be justified to a human.

## Measuring error

```python
from sklearn.metrics import mean_squared_error

predictions = model.predict(X)
mse = mean_squared_error(y, predictions)
print(mse)  # average squared difference between predicted and true prices
```

Lower is better; this metric, and others like it, are the subject of the dedicated Model Evaluation
module later in this course.

## Where regression shows up in AI systems

- Predicting how many tokens a prompt will consume before sending it, to stay within budget.
- A reranking model in Course 5 that outputs a continuous relevance score for each retrieved
  document, rather than a strict yes/no label.
- Predicting latency or cost of a given LLM call based on prompt length and model choice, useful for
  the production cost-control work in Course 13.

## Looking ahead

The next lesson covers classification, regression's counterpart for discrete outputs, and together
they form the two pillars of supervised learning that the rest of this course's evaluation and
feature engineering material assumes you understand.
""",
                    "examples": [
                        {
                            "title": "Example: Predicting response length from prompt length",
                            "code": "from sklearn.linear_model import LinearRegression\nimport numpy as np\n\nprompt_lengths = np.array([[50], [120], [300], [500]])\nresponse_lengths = np.array([80, 150, 400, 600])\n\nmodel = LinearRegression()\nmodel.fit(prompt_lengths, response_lengths)\nprint(model.predict([[200]]))",
                            "explanation": "A minimal single-feature regression predicting a rough relationship between prompt length and expected response length, a real heuristic used for budget estimation.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Using scikit-learn's LinearRegression, fit a model on a small synthetic dataset of your own (at least 5 examples) with one feature, and print the learned coefficient and intercept.",
                            "difficulty": "easy",
                            "hint": "Reuse the structure from the lesson's main code example with your own X and y arrays.",
                        },
                        {
                            "prompt": "Compute the mean squared error of your fitted model's predictions on its own training data, and explain in one sentence why this number alone doesn't tell you how the model will perform on new data.",
                            "difficulty": "medium",
                            "hint": "Recall the training/validation/test lesson -- this MSE is measured on data the model already saw.",
                        },
                        {
                            "prompt": "Give one example of an AI-agent-related quantity that could be predicted using regression, and explain what features you'd use to predict it.",
                            "difficulty": "medium",
                            "hint": "Consider things like estimated API cost, latency, or token usage.",
                        },
                    ],
                    "resources": [
                        {"title": "scikit-learn: Linear Models", "url": "https://scikit-learn.org/stable/modules/linear_model.html", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "ai-ml", "weight": 1.0}],
                },
                {
                    "slug": "classification-algorithms",
                    "title": "Classification Algorithms",
                    "description": "Predicting discrete categories with logistic regression and decision trees, and reading class probabilities.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Explain what classification predicts and when it applies",
                        "Fit a logistic regression classifier and a decision tree using scikit-learn",
                        "Interpret predicted class probabilities, not just hard labels",
                        "Identify classification-shaped problems relevant to AI agents",
                    ],
                    "content_markdown": """
## Why this matters

Classification is everywhere in AI agent systems: is this input a duplicate question, is this
output safe, does this document match the query's intent well enough to retrieve? Understanding how
a classifier works — and that it usually outputs a probability, not a certainty — is directly
relevant to building guardrails and evaluators in Course 12.

## What classification predicts

Classification predicts a **discrete category** from a fixed set of options: spam/not-spam,
positive/neutral/negative, or one of many document topics. Binary classification has exactly two
classes; multi-class classification has more than two.

## Logistic regression

Despite the name, logistic regression is a classification algorithm, not a regression algorithm — it
predicts the *probability* of belonging to a class.

```python
from sklearn.linear_model import LogisticRegression
import numpy as np

# Features: [word_count, exclamation_marks], Target: 1 = spam, 0 = not spam
X = np.array([[10, 0], [50, 5], [8, 0], [60, 8], [12, 1]])
y = np.array([0, 1, 0, 1, 0])

model = LogisticRegression()
model.fit(X, y)

probabilities = model.predict_proba([[45, 4]])
print(probabilities)   # e.g. [[0.2, 0.8]] -> 80% chance of class 1 (spam)

hard_label = model.predict([[45, 4]])
print(hard_label)      # [1]
```

`predict_proba` returns a probability for each class; `predict` applies a threshold (0.5 by default)
to turn that probability into a hard label. Always prefer looking at `predict_proba` when you need
to make a judgment call about confidence, such as deciding whether an agent should ask a clarifying
question instead of acting on a low-confidence classification.

## Decision trees

Decision trees classify by learning a series of if/else splits on feature values:

```python
from sklearn.tree import DecisionTreeClassifier

tree_model = DecisionTreeClassifier(max_depth=3)
tree_model.fit(X, y)
print(tree_model.predict([[45, 4]]))
```

`max_depth` limits how many splits deep the tree can go — an important control against overfitting,
since an unconstrained tree can grow deep enough to perfectly memorize the training data (echoing
the overfitting warning from the earlier evaluation lesson).

## Why probabilities matter more than hard labels

A classifier that says "80% spam" and one that says "51% spam" both round to the same hard label,
but they represent very different levels of confidence. Systems that only look at the hard label
throw away information you'll often want — for example, an agent's safety classifier might route
anything below 70% confidence to a human reviewer instead of auto-approving or auto-rejecting.

## Where classification shows up in AI systems

- A guardrail model classifying whether a user's message is a jailbreak attempt (Course 12).
- A relevance classifier deciding whether a retrieved chunk actually answers the query (Course 5).
- An intent classifier routing a user's message to the right specialized agent in a multi-agent
  system (Course 12: Multi-Agent Systems).

## Looking ahead

The Model Evaluation module immediately following this one teaches you precision, recall, and F1 —
the metrics specifically designed to evaluate classifiers like the ones in this lesson, especially
when classes are imbalanced (e.g., spam is rare compared to legitimate messages).
""",
                    "examples": [
                        {
                            "title": "Example: Using predicted probability for a confidence threshold",
                            "code": "probabilities = model.predict_proba([[45, 4], [8, 0]])\nfor p in probabilities:\n    spam_confidence = p[1]\n    if spam_confidence > 0.9:\n        print(\"auto-flag as spam\")\n    elif spam_confidence > 0.5:\n        print(\"route to human review\")\n    else:\n        print(\"allow\")",
                            "explanation": "Shows a realistic three-tier decision policy built on top of predicted probabilities rather than a single blunt threshold.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Fit a LogisticRegression classifier on a small synthetic dataset with two features and a binary label, then print predict_proba for two new examples.",
                            "difficulty": "medium",
                            "hint": "Model your dataset after the spam example, with at least 6-8 labeled rows for a more stable fit.",
                        },
                        {
                            "prompt": "Fit a DecisionTreeClassifier with max_depth=2 on the same dataset and compare its predictions to the logistic regression model's predictions on the same new examples.",
                            "difficulty": "medium",
                            "hint": "Both models expose .predict() with the same call signature, so you can compare outputs directly.",
                        },
                        {
                            "prompt": "Describe a three-tier confidence policy (like the example) for an agent's tool-selection classifier, explaining what should happen at high, medium, and low confidence.",
                            "difficulty": "hard",
                            "hint": "Think about auto-execute, ask-for-confirmation, and refuse-and-ask-clarifying-question tiers.",
                        },
                    ],
                    "resources": [
                        {"title": "scikit-learn: Logistic Regression", "url": "https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "ai-ml", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "unsupervised-learning",
            "title": "Unsupervised Learning",
            "description": "Finding structure in data without labels: clustering similar items and reducing dimensionality for visualization and efficiency.",
            "order_index": 4,
            "estimated_hours": 2.0,
            "lessons": [
                {
                    "slug": "clustering-with-k-means",
                    "title": "Clustering with K-Means",
                    "description": "Grouping unlabeled data points by similarity, and choosing a reasonable number of clusters.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Explain the difference between supervised and unsupervised learning",
                        "Run k-means clustering on a small dataset using scikit-learn",
                        "Choose a reasonable value of k using the elbow method",
                        "Connect clustering to grouping similar embeddings later in the program",
                    ],
                    "content_markdown": """
## Why this matters

Not all data comes with labels. Clustering discovers structure in data on its own, which is exactly
what you'll rely on later when grouping similar document embeddings, discovering topics in a corpus,
or identifying duplicate questions in a support ticket dataset — none of which come pre-labeled.

## Supervised vs unsupervised, concretely

Supervised learning (the previous module) needs labeled examples: "here are 1,000 emails, each
marked spam or not-spam." Unsupervised learning works with **unlabeled** data and looks for
structure on its own: "here are 1,000 emails; find natural groupings" — with no one having told the
algorithm what the groups should be.

## K-means clustering

K-means partitions data into `k` groups by repeatedly assigning each point to its nearest cluster
center, then recomputing each center as the mean of its assigned points, until the assignments stop
changing.

```python
from sklearn.cluster import KMeans
import numpy as np

# Points representing, e.g., 2D compressed embeddings of short texts
X = np.array([
    [1, 2], [1.5, 1.8], [1, 0.6],      # cluster A
    [10, 9], [10.5, 8.5], [9.8, 9.2],  # cluster B
])

kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
kmeans.fit(X)

print(kmeans.labels_)             # which cluster each point was assigned to
print(kmeans.cluster_centers_)    # the learned center of each cluster

new_point = np.array([[1.2, 1.5]])
print(kmeans.predict(new_point))  # which cluster the new point is closest to
```

`n_clusters=2` is a choice you make up front — k-means doesn't discover the "right" number of
clusters on its own, which is both its main limitation and the subject of the next section.

## Choosing k with the elbow method

```python
inertias = []
k_values = range(1, 6)
for k in k_values:
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    model.fit(X)
    inertias.append(model.inertia_)  # sum of squared distances to nearest center

# Plot k_values vs inertias; look for the "elbow" where adding more
# clusters stops meaningfully reducing inertia.
```

As `k` increases, inertia (a measure of how tightly packed each cluster is) always decreases — in
the extreme, `k` equal to the number of points gives zero inertia. The "elbow method" looks for the
point where increasing `k` further gives diminishing returns, as a practical heuristic for choosing
a reasonable cluster count.

## Where clustering shows up in AI systems

- Grouping similar user queries to discover common intents without hand-labeling every one.
- Clustering document embeddings (Course 6) to auto-discover topics in a large corpus before you
  build a RAG index over it.
- Detecting duplicate or near-duplicate content before indexing it, since near-identical chunks
  waste retrieval slots without adding information.

## Looking ahead

Course 6 (Embeddings Introduction) turns text into exactly the kind of numeric vectors k-means
operates on here — clustering embeddings is one of the most common first things people do with them
to sanity-check that "similar" texts really do land near each other in vector space.
""",
                    "examples": [
                        {
                            "title": "Example: Clustering short numeric feature vectors",
                            "code": "from sklearn.cluster import KMeans\nimport numpy as np\n\nX = np.array([[1, 1], [1.2, 0.9], [8, 8], [8.3, 7.8], [1.1, 1.3]])\nmodel = KMeans(n_clusters=2, random_state=0, n_init=10)\nmodel.fit(X)\nprint(model.labels_)",
                            "explanation": "A minimal end-to-end clustering run showing that the three points near (1,1) and the two near (8,8) are correctly grouped without ever being told which group they belong to.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Create a synthetic 2D dataset with three visually distinct clusters (at least 4 points each) and fit KMeans with n_clusters=3, then print the resulting labels.",
                            "difficulty": "medium",
                            "hint": "Space out three groups of points far apart from each other, e.g. around (0,0), (10,10), and (0,10).",
                        },
                        {
                            "prompt": "Run the elbow method code from the lesson on your dataset for k=1 through 5 and identify which k looks like the elbow point based on the inertia values.",
                            "difficulty": "medium",
                            "hint": "Look for where the drop in inertia from k to k+1 becomes noticeably smaller than earlier drops.",
                        },
                        {
                            "prompt": "Explain in 2-3 sentences a scenario where clustering document embeddings would be more useful than manually reading and labeling every document.",
                            "difficulty": "easy",
                            "hint": "Think about scale: clustering thousands of unlabeled support tickets by topic.",
                        },
                    ],
                    "resources": [
                        {"title": "scikit-learn: K-Means Clustering", "url": "https://scikit-learn.org/stable/modules/clustering.html#k-means", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "ai-ml", "weight": 1.0}],
                },
                {
                    "slug": "dimensionality-reduction",
                    "title": "Dimensionality Reduction",
                    "description": "Compressing high-dimensional data down to fewer dimensions for visualization, speed, and noise reduction.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain why high-dimensional data is hard to work with directly",
                        "Describe what PCA does at a conceptual level",
                        "Apply PCA using scikit-learn to reduce a dataset's dimensions",
                        "Connect dimensionality reduction to visualizing and speeding up embedding-based systems",
                    ],
                    "content_markdown": """
## Why this matters

Text embeddings you'll generate starting in Course 6 typically have hundreds or thousands of
dimensions. You cannot plot a 768-dimensional vector on a chart, and searching through millions of
high-dimensional vectors is computationally expensive. Dimensionality reduction is the standard tool
for both problems.

## The curse of dimensionality, briefly

As the number of dimensions grows, data points tend to become sparse and roughly equidistant from
each other, which makes distance-based comparisons (like the similarity search you'll rely on for
retrieval) less reliable and more expensive to compute. This isn't just a theoretical curiosity — it
directly motivates techniques used later, like reducing embedding dimensions before indexing them
for faster retrieval.

## Principal Component Analysis (PCA)

PCA finds new axes (called principal components) that capture the most variance in the data, and
lets you project your data onto just the first few of these axes while losing as little information
as possible.

```python
from sklearn.decomposition import PCA
import numpy as np

# 5 samples, 4 features each
X = np.array([
    [2.5, 2.4, 1.0, 0.5],
    [0.5, 0.7, 0.2, 0.1],
    [2.2, 2.9, 1.1, 0.6],
    [1.9, 2.2, 0.9, 0.4],
    [3.1, 3.0, 1.4, 0.7],
])

pca = PCA(n_components=2)
X_reduced = pca.fit_transform(X)

print(X_reduced.shape)               # (5, 2) -- from 4 dimensions down to 2
print(pca.explained_variance_ratio_) # how much of the original variance each component keeps
```

`explained_variance_ratio_` tells you how much information you kept — if the first two components
explain 95% of the variance, you've compressed the data to half its original size while losing only
5% of the information, a very favorable trade-off.

## Visualizing high-dimensional data

Reducing embeddings to 2 or 3 dimensions with PCA (or the more visualization-focused t-SNE/UMAP
techniques) is the standard way to actually *look* at a cluster of document embeddings on a chart,
sanity-checking that semantically similar documents land near each other before you trust the
embedding model in a production RAG pipeline.

## Speed and storage benefits

Fewer dimensions means less memory per vector and faster similarity computations at search time.
Some production vector databases apply dimensionality reduction (or related quantization techniques)
specifically to make retrieval over millions of vectors fast enough for real-time use.

## Looking ahead

When you generate your first embeddings in Course 6, one of the very first sanity checks you'll run
is a PCA (or UMAP) plot of a handful of embeddings, confirming visually that "dog" and "puppy" land
closer together than "dog" and "spreadsheet" — dimensionality reduction is what makes that
visualization possible at all.
""",
                    "examples": [
                        {
                            "title": "Example: Checking how much variance is preserved",
                            "code": "from sklearn.decomposition import PCA\nimport numpy as np\n\nX = np.random.RandomState(0).rand(10, 6)  # 10 samples, 6 features\npca = PCA(n_components=3)\npca.fit(X)\nprint(round(sum(pca.explained_variance_ratio_), 3))  # fraction of variance kept",
                            "explanation": "Sums explained_variance_ratio_ across the kept components to report a single 'how much information survived compression' number.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Create a small numpy array with 6 samples and 5 features, apply PCA to reduce it to 2 dimensions, and print the shape of the result to confirm it changed from (6,5) to (6,2).",
                            "difficulty": "easy",
                            "hint": "pca = PCA(n_components=2); X_reduced = pca.fit_transform(X)",
                        },
                        {
                            "prompt": "For the same dataset, try n_components=1, 2, 3, and 4, printing the total explained variance ratio at each setting, and describe the trend you observe.",
                            "difficulty": "medium",
                            "hint": "Total explained variance should increase (or stay the same) as n_components increases.",
                        },
                        {
                            "prompt": "In 2-3 sentences, explain why you would want to reduce 768-dimensional text embeddings down to 2 dimensions before plotting them, but NOT before storing them in a production vector database for retrieval.",
                            "difficulty": "hard",
                            "hint": "Consider the tradeoff between human-interpretable visualization and retrieval accuracy/information loss.",
                        },
                    ],
                    "resources": [
                        {"title": "scikit-learn: Decomposing signals (PCA)", "url": "https://scikit-learn.org/stable/modules/decomposition.html#pca", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "ai-ml", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "model-evaluation",
            "title": "Model Evaluation",
            "description": "Measuring model quality honestly with the right metrics, and recognizing overfitting before it reaches production.",
            "order_index": 5,
            "estimated_hours": 2.0,
            "lessons": [
                {
                    "slug": "evaluation-metrics-for-classification",
                    "title": "Evaluation Metrics for Classification",
                    "description": "Accuracy, precision, recall, and F1 — and why accuracy alone is often misleading.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Compute accuracy, precision, recall, and F1 score for a classifier",
                        "Explain why accuracy is misleading on imbalanced datasets",
                        "Choose the right metric to optimize for a given real-world cost tradeoff",
                        "Apply a confusion matrix to understand a classifier's specific error patterns",
                    ],
                    "content_markdown": """
## Why this matters

You will evaluate far more than traditional ML classifiers in this program — you'll evaluate
whether a RAG system retrieved the right document, whether an agent's tool call was correct, whether
a guardrail correctly flagged unsafe output. All of that evaluation borrows precision, recall, and
F1 directly from classical ML, covered here for the first time.

## Why accuracy alone can lie to you

Imagine a dataset where 95% of messages are legitimate and 5% are spam. A classifier that always
predicts "not spam," regardless of input, achieves 95% accuracy while being completely useless —
it catches zero spam. This is exactly the trap of relying on accuracy for imbalanced classes, which
describes most real safety and moderation classifiers.

## Precision and recall

```python
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

y_true = [1, 0, 1, 1, 0, 1, 0, 0]   # 1 = spam, 0 = not spam
y_pred = [1, 0, 0, 1, 0, 1, 1, 0]   # model's predictions

print("accuracy:", accuracy_score(y_true, y_pred))
print("precision:", precision_score(y_true, y_pred))
print("recall:", recall_score(y_true, y_pred))
print("f1:", f1_score(y_true, y_pred))
```

- **Precision** — of everything the model flagged as spam, what fraction actually was spam? High
  precision means few false alarms.
- **Recall** — of everything that actually was spam, what fraction did the model catch? High recall
  means few missed cases.

These two usually trade off against each other: a model that flags everything as spam has perfect
recall (catches all spam) but terrible precision (drowns you in false alarms).

## F1 score: balancing the two

```python
# F1 is the harmonic mean of precision and recall, punishing extreme imbalance between them
f1 = f1_score(y_true, y_pred)
```

F1 is useful when you want one number that penalizes a model for being extreme in either direction,
rather than picking precision or recall alone.

## Choosing the right metric for the real cost tradeoff

- A spam filter: false positives (blocking real email) are very annoying, so precision often matters
  more.
- A safety guardrail catching harmful agent outputs: missing a harmful output (false negative) is
  often far worse than an occasional false alarm, so recall often matters more.
- There is no universally "correct" metric — the right choice depends on which kind of error costs
  more in your specific application, a judgment call you'll make explicitly when designing
  evaluation criteria in Course 12.

## The confusion matrix

```python
from sklearn.metrics import confusion_matrix

matrix = confusion_matrix(y_true, y_pred)
print(matrix)
# [[true_negatives, false_positives],
#  [false_negatives, true_positives]]
```

The confusion matrix breaks down exactly *which* kinds of mistakes a classifier makes, which is far
more actionable than a single summary number when you're debugging why a guardrail keeps letting
certain unsafe outputs through.

## Looking ahead

Course 12's agent evaluation harness reuses precision/recall/F1 directly — for example, measuring
whether a RAG system's retrieved documents are actually relevant (precision) and whether it found
all the relevant documents available (recall).
""",
                    "examples": [
                        {
                            "title": "Example: Comparing two classifiers with the same accuracy but different tradeoffs",
                            "code": "from sklearn.metrics import precision_score, recall_score\n\n# Classifier A: cautious, flags fewer things\ny_pred_a = [1, 0, 0, 1, 0, 0, 0, 0]\n# Classifier B: aggressive, flags more things\ny_pred_b = [1, 0, 1, 1, 1, 1, 1, 0]\ny_true =    [1, 0, 1, 1, 0, 1, 0, 0]\n\nfor name, pred in [(\"A\", y_pred_a), (\"B\", y_pred_b)]:\n    print(name, \"precision:\", precision_score(y_true, pred), \"recall:\", recall_score(y_true, pred))",
                            "explanation": "Contrasts a cautious classifier (higher precision, lower recall) with an aggressive one (lower precision, higher recall) using the same ground truth.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Given y_true = [1,1,0,1,0,0,1,0] and y_pred = [1,0,0,1,0,1,1,0], compute accuracy, precision, recall, and F1 using scikit-learn and print all four.",
                            "difficulty": "easy",
                            "hint": "Import all four functions from sklearn.metrics and call each with (y_true, y_pred).",
                        },
                        {
                            "prompt": "Construct a confusion matrix for the predictions above and explain, in words, what each of the four cells represents in the context of a spam classifier.",
                            "difficulty": "medium",
                            "hint": "Use sklearn.metrics.confusion_matrix and map its 4 numbers to true/false positive/negative.",
                        },
                        {
                            "prompt": "For a medical safety classifier flagging potentially harmful agent outputs for human review, argue whether recall or precision should be weighted more heavily, and justify your answer in 2-3 sentences.",
                            "difficulty": "hard",
                            "hint": "Consider the real-world cost of missing a harmful output versus the cost of an unnecessary human review.",
                        },
                    ],
                    "resources": [
                        {"title": "scikit-learn: Classification metrics", "url": "https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "ai-ml", "weight": 1.0}],
                },
                {
                    "slug": "overfitting-underfitting-and-regularization",
                    "title": "Overfitting, Underfitting, and Regularization",
                    "description": "Recognizing when a model has memorized noise versus failed to learn the pattern at all, and how regularization helps.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Distinguish overfitting from underfitting using training vs validation performance",
                        "Explain the bias-variance tradeoff conceptually",
                        "Apply basic regularization to reduce overfitting",
                        "Recognize overfitting-like failure modes in prompt engineering and RAG design",
                    ],
                    "content_markdown": """
## Why this matters

Overfitting isn't just a classical-ML concept — you'll see its cousin everywhere in this program: a
prompt tuned so specifically to your five test examples that it fails on the sixth, or a RAG system
tuned to retrieve perfectly for the exact questions you tested with but poorly for anything phrased
differently. The diagnosis and fix pattern here transfers directly.

## Overfitting

A model overfits when it performs very well on training data but poorly on validation/test data —
it has memorized noise and specific quirks of the training examples rather than learning the
underlying, generalizable pattern.

```python
train_accuracy = 0.99
val_accuracy = 0.68
gap = train_accuracy - val_accuracy
print(f"Overfitting gap: {gap:.2f}")  # a large gap signals overfitting
```

A large, persistent gap between training and validation performance is the standard signal.

## Underfitting

A model underfits when it performs poorly on *both* training and validation data — it hasn't
learned enough of the pattern in the first place, often because it's too simple for the problem or
wasn't trained long enough.

```python
train_accuracy = 0.55
val_accuracy = 0.53
# Both low -- this model needs more capacity, better features, or more training, not less
```

## The bias-variance tradeoff, briefly

- **High bias** (underfitting) — the model makes overly simplistic assumptions and misses real
  patterns.
- **High variance** (overfitting) — the model is overly sensitive to the specific training data it
  saw, including its noise.

Model complexity sits on a dial between these two failure modes: too simple underfits, too complex
overfits, and the goal is to land somewhere in the middle that generalizes well.

## Regularization: a direct fix for overfitting

Regularization adds a penalty for model complexity, discouraging the model from relying too heavily
on any single feature or fitting noise too precisely.

```python
from sklearn.linear_model import LogisticRegression

# Smaller C = stronger regularization = simpler, less overfit-prone model
strongly_regularized = LogisticRegression(C=0.1)
weakly_regularized = LogisticRegression(C=10.0)
```

In scikit-learn's `LogisticRegression`, the `C` parameter is inversely related to regularization
strength — a smaller `C` means a stronger penalty on complexity, generally reducing overfitting at
the cost of potentially underfitting if pushed too far.

## Other practical fixes

- **More training data** — often the single most effective fix for overfitting, since noise
  averages out with more examples.
- **Simpler models** — fewer features, shallower decision trees (recall `max_depth` from the earlier
  classification lesson).
- **Early stopping** — for models trained iteratively, stop training once validation performance
  stops improving even if training performance keeps climbing.

## Recognizing this pattern beyond classical ML

When you hand-craft a prompt that nails your five test cases perfectly but breaks on realistic user
phrasing, you've essentially overfit your prompt to your test set — the fix is the same in spirit as
here: test on a larger, more diverse held-out set (Course 12), and prefer simpler, more general
prompt instructions over ones with many special-cased edge conditions.

## Looking ahead

Course 12's evaluation module explicitly calls out "prompt overfitting" as a named failure mode
using this exact vocabulary — recognizing it here first means you won't be learning the concept from
scratch under pressure with a live agent in front of you.
""",
                    "examples": [
                        {
                            "title": "Example: Detecting overfitting from a train/val accuracy log",
                            "code": "history = [\n    {\"epoch\": 1, \"train_acc\": 0.70, \"val_acc\": 0.68},\n    {\"epoch\": 5, \"train_acc\": 0.85, \"val_acc\": 0.80},\n    {\"epoch\": 10, \"train_acc\": 0.97, \"val_acc\": 0.74},\n]\nfor row in history:\n    gap = row[\"train_acc\"] - row[\"val_acc\"]\n    flag = \"overfitting risk\" if gap > 0.15 else \"ok\"\n    print(row[\"epoch\"], gap, flag)",
                            "explanation": "Simulates a training log where the gap between training and validation accuracy widens over epochs, a classic overfitting signature you'd want to catch and stop early.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Given a table of train_acc and val_acc across 5 epochs of your own choosing, identify at which epoch (if any) overfitting begins, and justify your answer.",
                            "difficulty": "medium",
                            "hint": "Look for the point where val_acc plateaus or drops while train_acc keeps rising.",
                        },
                        {
                            "prompt": "Fit two LogisticRegression models with C=0.01 and C=100 on the same small dataset, and compare their coefficients -- which one has larger coefficient magnitudes, and why?",
                            "difficulty": "medium",
                            "hint": "Stronger regularization (smaller C) generally shrinks coefficient magnitudes toward zero.",
                        },
                        {
                            "prompt": "Describe, in 2-3 sentences, a real example of 'prompt overfitting' you could imagine happening when someone tunes a prompt against only 3 example questions.",
                            "difficulty": "hard",
                            "hint": "Think about overly specific wording or examples baked into the prompt that don't generalize to differently-phrased questions.",
                        },
                    ],
                    "resources": [
                        {"title": "scikit-learn: Underfitting vs. Overfitting", "url": "https://scikit-learn.org/stable/auto_examples/model_selection/plot_underfitting_overfitting.html", "resource_type": "tutorial"},
                    ],
                    "skills": [{"slug": "ai-ml", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "feature-engineering",
            "title": "Feature Engineering",
            "description": "Cleaning, transforming, and encoding raw data into the numeric features models actually consume.",
            "order_index": 6,
            "estimated_hours": 2.0,
            "lessons": [
                {
                    "slug": "cleaning-and-transforming-features",
                    "title": "Cleaning and Transforming Features",
                    "description": "Handling missing values and scaling numeric features so models train reliably.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Identify and handle missing values in a dataset",
                        "Explain why feature scaling matters for many ML algorithms",
                        "Apply standardization and normalization using scikit-learn",
                        "Connect data cleaning discipline to preparing documents for RAG chunking",
                    ],
                    "content_markdown": """
## Why this matters

Models are only ever as good as the features you feed them, and real-world data always has missing
values, wildly different scales across features, and noise. Feature engineering is where you
translate messy raw data into a form a model can actually learn from — the same instinct you'll
apply to cleaning documents before chunking and embedding them in Course 5.

## Handling missing values

```python
import numpy as np
import pandas as pd

data = pd.DataFrame({
    "age": [25, np.nan, 35, 40, np.nan],
    "income": [50000, 60000, np.nan, 80000, 55000],
})

print(data.isnull().sum())  # count of missing values per column

# Option 1: drop rows with any missing values (only safe if few rows are affected)
dropped = data.dropna()

# Option 2: fill with a reasonable statistic (mean, median, or a sentinel value)
filled = data.fillna(data.mean(numeric_only=True))
```

Dropping rows is simple but wastes data and can bias your dataset if missingness isn't random.
Filling with the mean or median is a common default, though for skewed data the median is often
safer than the mean.

## Why scale matters

Many algorithms (including k-means clustering from earlier in this course, and gradient-based models
like neural networks) are sensitive to the scale of input features. A feature ranging from 0 to
1,000,000 will dominate a feature ranging from 0 to 1 purely because of its scale, not because it's
actually more important.

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import numpy as np

X = np.array([[25, 50000], [30, 60000], [35, 80000], [40, 55000]])

# Standardization: mean 0, standard deviation 1
standard_scaler = StandardScaler()
X_standardized = standard_scaler.fit_transform(X)

# Normalization: squashes values into [0, 1]
minmax_scaler = MinMaxScaler()
X_normalized = minmax_scaler.fit_transform(X)

print(X_standardized)
```

## Fitting scalers correctly (avoiding leakage)

Recall the data leakage lesson: fit the scaler only on training data, then apply (not re-fit) that
same transformation to validation and test data.

```python
scaler = StandardScaler()
scaler.fit(X_train)              # learn mean/std from training data only
X_train_scaled = scaler.transform(X_train)
X_val_scaled = scaler.transform(X_val)   # reuse training statistics, don't refit
```

## Connecting this to document preparation for RAG

Cleaning text documents before chunking — stripping boilerplate headers/footers, normalizing
whitespace, fixing encoding issues — is the text-data equivalent of handling missing values and
scaling numeric features here. In both cases, the principle is the same: inconsistent or noisy raw
input degrades everything built downstream of it, whether that's a trained model or a retrieval
index.

## Looking ahead

Course 5's document loaders apply exactly this "clean before you process" discipline to raw text
files, and Course 6's embedding pipeline assumes text has already been normalized the way this
lesson normalizes numeric features.
""",
                    "examples": [
                        {
                            "title": "Example: A full clean-then-scale pipeline",
                            "code": "import pandas as pd\nfrom sklearn.preprocessing import StandardScaler\n\ndata = pd.DataFrame({\"age\": [22, None, 41, 36], \"score\": [0.8, 0.6, None, 0.9]})\ncleaned = data.fillna(data.mean(numeric_only=True))\n\nscaler = StandardScaler()\nscaled = scaler.fit_transform(cleaned)\nprint(scaled)",
                            "explanation": "Runs missing-value imputation first, then scaling second -- the standard order of operations in a feature preparation pipeline.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Create a small pandas DataFrame with at least one missing value in two different columns, then fill missing values with each column's median instead of its mean.",
                            "difficulty": "easy",
                            "hint": "data.fillna(data.median(numeric_only=True))",
                        },
                        {
                            "prompt": "Apply StandardScaler to a dataset with two features on very different scales (e.g. age in years and income in dollars), and print the resulting means and standard deviations to confirm they are approximately 0 and 1.",
                            "difficulty": "medium",
                            "hint": "After fit_transform, use .mean(axis=0) and .std(axis=0) on the result to verify.",
                        },
                        {
                            "prompt": "Explain, in 2-3 sentences, why fitting a StandardScaler on your full dataset before splitting into train/test would be a data leakage mistake, referencing the earlier lesson on train/val/test splits.",
                            "difficulty": "hard",
                            "hint": "Consider that the scaler's mean/std would then reflect information from the test set the model shouldn't have access to during training.",
                        },
                    ],
                    "resources": [
                        {"title": "scikit-learn: Preprocessing data", "url": "https://scikit-learn.org/stable/modules/preprocessing.html", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "ai-ml", "weight": 1.0}],
                },
                {
                    "slug": "encoding-categorical-data",
                    "title": "Encoding Categorical Data",
                    "description": "Turning text categories into numbers models can use, with one-hot and label encoding.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Explain why models need numeric input, not raw category labels",
                        "Apply one-hot encoding and label encoding using scikit-learn",
                        "Choose the appropriate encoding for ordinal vs nominal categories",
                        "Connect categorical encoding conceptually to how tokens are represented for LLMs",
                    ],
                    "content_markdown": """
## Why this matters

Nearly all ML algorithms operate on numbers, not raw text labels like "red," "blue," or "green."
Categorical encoding is the bridge between human-readable categories and the numeric input a model
actually consumes — and the same core idea, turning discrete symbols into numeric representations,
is exactly what tokenization does for LLMs in Course 3, just at much greater scale and sophistication.

## Nominal vs ordinal categories

- **Nominal** — categories with no inherent order: color, country, tool name. "Red" isn't greater or
  less than "blue."
- **Ordinal** — categories with a meaningful order: difficulty level (easy < medium < hard), rating
  stars. The order carries real information a model should be able to use.

Choosing the wrong encoding for the wrong type of category is a common and costly mistake — treating
an ordinal feature as nominal throws away real information about order.

## One-hot encoding (for nominal categories)

```python
import pandas as pd

data = pd.DataFrame({"tool": ["search", "calculator", "search", "translator"]})
one_hot = pd.get_dummies(data["tool"])
print(one_hot)
#    calculator  search  translator
# 0       False    True       False
# 1        True   False       False
# 2       False    True       False
# 3       False   False        True
```

Each category becomes its own binary column. This avoids implying a false ordering between
categories (unlike simply assigning search=0, calculator=1, translator=2, which would falsely imply
translator > calculator > search).

## Label encoding (for ordinal categories)

```python
from sklearn.preprocessing import LabelEncoder

difficulty = ["easy", "hard", "medium", "easy", "hard"]
encoder = LabelEncoder()
encoded = encoder.fit_transform(difficulty)
print(encoded)           # e.g. [0 1 2 0 1] -- alphabetical by default, often needs manual reordering
print(encoder.classes_)  # ['easy' 'hard' 'medium'] -- the order LabelEncoder assigned

# For genuinely ordinal data, it's often safer to define the order explicitly:
order_map = {"easy": 0, "medium": 1, "hard": 2}
manual_encoding = [order_map[d] for d in difficulty]
print(manual_encoding)   # [0, 2, 1, 0, 2] -- correctly reflects easy < medium < hard
```

Note that scikit-learn's `LabelEncoder` assigns integers alphabetically by default, which does *not*
guarantee the correct ordinal order — for genuinely ordered categories, defining your own explicit
mapping (as shown above) is usually safer than trusting the default.

## Why one-hot encoding can explode dimensionality

A "country" feature with 195 possible values becomes 195 new columns under one-hot encoding, most of
them zero for any given row. This sparsity is a real practical cost, and is conceptually similar to
why LLM vocabularies (covered in Course 3's Tokens module) use subword tokenization rather than a
single one-hot column per possible word — a naive one-hot vocabulary of every English word would be
enormous and mostly empty for any given piece of text.

## Looking ahead

When you reach Course 3's Tokens module, you'll see that turning text into numbers a model can
process is a much older, more general problem than LLMs — one-hot and label encoding are the
simplest instances of it, and tokenization plus embeddings (Course 6) are far more sophisticated
solutions to the same underlying need.
""",
                    "examples": [
                        {
                            "title": "Example: One-hot encoding a categorical feature for a classifier",
                            "code": "import pandas as pd\n\ndata = pd.DataFrame({\n    \"tool_used\": [\"search\", \"calculator\", \"search\", \"code_exec\"],\n    \"success\": [1, 1, 0, 1],\n})\nencoded = pd.get_dummies(data, columns=[\"tool_used\"])\nprint(encoded)",
                            "explanation": "Encodes the 'tool_used' column into separate binary columns while keeping the numeric 'success' column untouched, ready to feed into a classifier.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Create a DataFrame with a nominal categorical column of at least 4 unique values and apply pd.get_dummies to it, printing the resulting columns.",
                            "difficulty": "easy",
                            "hint": "pd.get_dummies(df, columns=['your_column'])",
                        },
                        {
                            "prompt": "Given an ordinal feature 'priority' with values ['low', 'high', 'medium', 'low', 'high'], write an explicit order_map and encode it manually rather than relying on LabelEncoder's default alphabetical order.",
                            "difficulty": "medium",
                            "hint": "Define order_map = {'low': 0, 'medium': 1, 'high': 2} then use a list comprehension.",
                        },
                        {
                            "prompt": "Explain in 2-3 sentences why one-hot encoding a 'country' feature with 195 categories could cause problems for a model trained on only a few hundred rows of data.",
                            "difficulty": "hard",
                            "hint": "Consider sparsity: most rows will have almost all-zero values across 195 new columns, and many countries may appear only once or not at all in training.",
                        },
                    ],
                    "resources": [
                        {"title": "scikit-learn: Encoding categorical features", "url": "https://scikit-learn.org/stable/modules/preprocessing.html#encoding-categorical-features", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "ai-ml", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "embeddings-introduction",
            "title": "Embeddings Introduction",
            "description": "The first look at turning meaning into numbers -- your direct bridge from classical ML into the LLM and RAG courses ahead.",
            "order_index": 7,
            "estimated_hours": 2.0,
            "lessons": [
                {
                    "slug": "what-are-embeddings",
                    "title": "What Are Embeddings?",
                    "description": "Numeric vector representations of meaning, and why they let computers reason about similarity between concepts.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Define an embedding as a dense numeric vector representing meaning",
                        "Explain why embeddings place semantically similar items near each other in vector space",
                        "Generate a text embedding using a real embedding model",
                        "Preview how embeddings enable retrieval, covered fully in Course 6",
                    ],
                    "content_markdown": """
## Why this matters

Everything from here through the RAG course depends on one idea: meaning can be represented as a
list of numbers, positioned in space such that similar meanings sit near each other. This lesson is
a first, gentle introduction; Course 6 (Embeddings) goes far deeper into the mechanics, models, and
production use of exactly this idea.

## From one-hot encoding to embeddings

Recall one-hot encoding from the previous module: each category becomes its own sparse, mostly-zero
column, with no notion of similarity between categories — "cat" and "dog" are just as different from
each other as "cat" and "spreadsheet" under one-hot encoding. Embeddings fix this: they represent
each item as a dense vector of, typically, hundreds of numbers, learned such that semantically
related items land close together in that vector space.

```python
# Conceptual illustration only -- real embeddings come from trained models,
# not hand-picked numbers like this.
embeddings = {
    "cat":   [0.9, 0.1, 0.0],
    "dog":   [0.8, 0.2, 0.0],
    "puppy": [0.75, 0.25, 0.05],
    "car":   [0.0, 0.1, 0.9],
}
```

Here `"cat"`, `"dog"`, and `"puppy"` are numerically close to each other, and all far from `"car"` —
that geometric closeness *is* the model's learned notion of semantic similarity.

## Generating a real embedding

```python
# Requires: pip install sentence-transformers
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
sentences = ["The cat sat on the mat.", "A dog lay on the rug.", "The stock market fell today."]
embeddings = model.encode(sentences)

print(embeddings.shape)  # (3, 384) -- 3 sentences, each a 384-dimensional vector
```

Each sentence becomes a 384-number vector. Sentences about pets on furniture will land closer to
each other in this 384-dimensional space than either lands to the sentence about the stock market —
without anyone explicitly programming a rule that says "pets and furniture are related."

## Measuring similarity: cosine similarity, briefly

```python
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

sim_cat_dog = cosine_similarity(embeddings[0], embeddings[1])
sim_cat_stock = cosine_similarity(embeddings[0], embeddings[2])
print(sim_cat_dog, sim_cat_stock)  # expect sim_cat_dog notably higher
```

Cosine similarity measures the angle between two vectors, ignoring their magnitude — a standard way
to quantify "how similar are these two pieces of text," and the exact metric Course 6's retrieval
systems use to rank documents by relevance to a query.

## Why this is the bridge to everything ahead

Embeddings are the technology that makes RAG possible: instead of keyword-matching a user's query
against documents, you embed both the query and every document, then retrieve whichever documents
are numerically closest to the query's embedding. That single idea — represent meaning as a vector,
compare vectors — is the foundation of Courses 5 through 7.

## Looking ahead

Course 6 dedicates an entire course to embeddings: different embedding models and their tradeoffs,
chunking strategies that affect embedding quality, and the vector databases that store and search
millions of embeddings efficiently. This lesson's job was only to make the core idea click.
""",
                    "examples": [
                        {
                            "title": "Example: Comparing similarity across related and unrelated sentences",
                            "code": "from sentence_transformers import SentenceTransformer\nimport numpy as np\n\nmodel = SentenceTransformer(\"all-MiniLM-L6-v2\")\ntexts = [\"How do I reset my password?\", \"I forgot my login credentials\", \"What's the weather today?\"]\nvectors = model.encode(texts)\n\ndef cos_sim(a, b):\n    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))\n\nprint(cos_sim(vectors[0], vectors[1]))  # high -- both about login/password\nprint(cos_sim(vectors[0], vectors[2]))  # low -- unrelated topics",
                            "explanation": "Shows that two differently-worded but semantically related sentences score much higher similarity than an unrelated sentence, the core mechanic that will power retrieval in Course 5.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Using sentence-transformers, embed 4 sentences (two related pairs on different topics) and print the shape of the resulting embedding array.",
                            "difficulty": "medium",
                            "hint": "model.encode(list_of_sentences) returns a 2D array with shape (num_sentences, embedding_dim).",
                        },
                        {
                            "prompt": "Compute the cosine similarity between all pairs among your 4 sentences and confirm that the two related pairs score higher than cross-topic pairs.",
                            "difficulty": "medium",
                            "hint": "Loop over all pairs with itertools.combinations, or just compute each pair manually for 4 sentences.",
                        },
                        {
                            "prompt": "Explain in 2-3 sentences why one-hot encoding 'cat' and 'dog' as arbitrary category columns fails to capture that they're more similar to each other than either is to 'spreadsheet', while embeddings succeed at this.",
                            "difficulty": "hard",
                            "hint": "Revisit the one-hot encoding lesson: one-hot columns are equidistant from each other by construction, with no learned notion of meaning.",
                        },
                    ],
                    "resources": [
                        {"title": "Sentence-Transformers documentation", "url": "https://www.sbert.net/", "resource_type": "docs"},
                    ],
                    "skills": [
                        {"slug": "ai-ml", "weight": 0.7},
                        {"slug": "embeddings", "weight": 0.6},
                    ],
                },
                {
                    "slug": "measuring-similarity-with-vectors",
                    "title": "Measuring Similarity with Vectors",
                    "description": "Cosine similarity, Euclidean distance, and dot product -- the three standard ways to compare embedding vectors.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Compute cosine similarity, Euclidean distance, and dot product between vectors",
                        "Explain when each similarity measure is appropriate",
                        "Rank a set of candidate vectors by similarity to a query vector",
                        "Preview how this ranking becomes retrieval in a RAG system",
                    ],
                    "content_markdown": """
## Why this matters

Every retrieval system you'll build starting in Course 5 boils down to one operation, repeated many
times: given a query vector, rank a set of candidate vectors by similarity, and return the top few.
This lesson makes sure that operation, and the choice of similarity measure behind it, is second
nature before you meet it wrapped inside a vector database's `.similarity_search()` method.

## Three common similarity/distance measures

```python
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def euclidean_distance(a, b):
    return np.linalg.norm(a - b)

def dot_product(a, b):
    return np.dot(a, b)

a = np.array([1.0, 2.0, 3.0])
b = np.array([2.0, 3.0, 4.0])

print("cosine:", cosine_similarity(a, b))
print("euclidean:", euclidean_distance(a, b))
print("dot:", dot_product(a, b))
```

- **Cosine similarity** — measures the angle between vectors, ignoring their length. Ranges from -1
  to 1 (or 0 to 1 for typical embeddings), and is the most common choice for text embedding
  similarity because it's insensitive to how "long" a piece of text is.
- **Euclidean distance** — straight-line distance between two points; smaller means more similar.
  Sensitive to vector magnitude, which can be a problem if embeddings aren't normalized.
- **Dot product** — related to cosine similarity but also sensitive to vector magnitude; some
  embedding models are specifically trained to be compared with dot product rather than cosine.

## Ranking candidates by similarity to a query

```python
query = np.array([0.9, 0.1, 0.0])
candidates = {
    "doc_a": np.array([0.85, 0.15, 0.0]),
    "doc_b": np.array([0.0, 0.2, 0.9]),
    "doc_c": np.array([0.8, 0.2, 0.05]),
}

scores = {name: cosine_similarity(query, vec) for name, vec in candidates.items()}
ranked = sorted(scores.items(), key=lambda pair: pair[1], reverse=True)
print(ranked)  # most similar documents first
```

This exact loop — score every candidate against the query, then sort descending — is what a naive,
unoptimized retrieval system does. Real vector databases (Course 6) use specialized indexes so this
doesn't require scanning every candidate one by one at large scale, but the underlying math is
identical to what you just wrote.

## Which measure should you use?

In practice, check your embedding model's documentation — most modern text embedding models
(including the ones you'll use in Course 6) are specifically trained and benchmarked for cosine
similarity, so that's the safe default unless a model's docs say otherwise. Consistency matters more
than the specific choice: never mix similarity measures between training/benchmarking and production
use.

## Looking ahead

Course 6 wraps this exact ranking logic inside a vector database, adding efficient indexing (so you
don't compare against every single document every time) and metadata filtering (so you can narrow
candidates before scoring). But the core operation — score, sort, take the top-k — is precisely what
you practiced in this lesson.
""",
                    "examples": [
                        {
                            "title": "Example: Top-k retrieval from a small candidate pool",
                            "code": "import numpy as np\n\ndef cosine_similarity(a, b):\n    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))\n\ndef top_k(query, candidates, k=2):\n    scored = [(name, cosine_similarity(query, vec)) for name, vec in candidates.items()]\n    scored.sort(key=lambda pair: pair[1], reverse=True)\n    return scored[:k]\n\nquery = np.array([1.0, 0.0, 0.0])\ncandidates = {\n    \"a\": np.array([0.9, 0.1, 0.0]),\n    \"b\": np.array([0.0, 1.0, 0.0]),\n    \"c\": np.array([0.8, 0.2, 0.1]),\n}\nprint(top_k(query, candidates, k=2))",
                            "explanation": "A reusable top_k function -- the exact pattern used inside real vector database client libraries, just without their internal indexing optimizations.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write a function that computes both cosine similarity and Euclidean distance between two numpy vectors, and demonstrate on a pair of vectors that they can disagree on which of two OTHER candidates is 'closer' when magnitudes differ significantly.",
                            "difficulty": "hard",
                            "hint": "Try a query vector and two candidates where one candidate is a scaled-up version of the other (same direction, different magnitude).",
                        },
                        {
                            "prompt": "Implement top_k(query, candidates, k) from scratch (without looking at the example) and test it on a candidate pool of at least 5 vectors.",
                            "difficulty": "medium",
                            "hint": "Score every candidate, sort descending by score, then slice the first k results.",
                        },
                        {
                            "prompt": "Explain in 2-3 sentences why cosine similarity is generally preferred over Euclidean distance for comparing text embeddings, focusing on the role of vector magnitude.",
                            "difficulty": "medium",
                            "hint": "Cosine similarity normalizes away magnitude, focusing purely on direction/meaning, while Euclidean distance treats a 'longer' vector as automatically farther away.",
                        },
                    ],
                    "resources": [
                        {"title": "NumPy docs: numpy.linalg.norm", "url": "https://numpy.org/doc/stable/reference/generated/numpy.linalg.norm.html", "resource_type": "docs"},
                    ],
                    "skills": [
                        {"slug": "ai-ml", "weight": 0.7},
                        {"slug": "embeddings", "weight": 0.6},
                    ],
                },
            ],
        },
        {
            "slug": "neural-network-fundamentals",
            "title": "Neural Network Fundamentals",
            "description": "How layered networks of simple units learn complex patterns -- the foundation underneath every transformer you'll study in Course 3.",
            "order_index": 8,
            "estimated_hours": 2.0,
            "lessons": [
                {
                    "slug": "perceptrons-and-layers",
                    "title": "Perceptrons and Layers",
                    "description": "The basic unit of a neural network, and how stacking layers of them enables learning complex, non-linear patterns.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Describe a perceptron's structure: weights, bias, and activation function",
                        "Explain why non-linear activation functions are necessary for deep networks",
                        "Describe how stacking layers builds increasingly abstract representations",
                        "Connect this structure forward to the transformer architecture in Course 3",
                    ],
                    "content_markdown": """
## Why this matters

Large language models are, at their core, enormous neural networks. Before Course 3's transformer
architecture makes sense, you need the building block underneath it: a single artificial neuron, and
why stacking many of them in layers is so powerful.

## The perceptron: a single artificial neuron

```python
def perceptron(inputs, weights, bias):
    weighted_sum = sum(i * w for i, w in zip(inputs, weights)) + bias
    return 1 if weighted_sum > 0 else 0  # a simple step activation

inputs = [1.0, 0.5, 0.2]
weights = [0.4, -0.6, 0.9]
bias = 0.1

output = perceptron(inputs, weights, bias)
print(output)
```

A perceptron takes several numeric inputs, multiplies each by a learned weight, sums them with a
bias term, and passes the result through an activation function to produce an output. This is the
exact same "weighted sum" idea from the linear regression lesson earlier in this course — a
perceptron is essentially a tiny linear model with one extra step: the activation function.

## Why activation functions matter

Without a non-linear activation function, stacking many layers of perceptrons would mathematically
collapse into being equivalent to a single linear layer — no matter how many layers you stack, you'd
only ever be able to learn straight-line relationships. Non-linear activations (like ReLU, sigmoid,
or tanh) are what let deep networks learn genuinely complex, curved decision boundaries.

```python
import numpy as np

def relu(x):
    return max(0, x)

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

print(relu(-2), relu(3))       # 0, 3
print(sigmoid(-2), sigmoid(3)) # squashed toward 0, squashed toward 1
```

`ReLU` (Rectified Linear Unit) is the most common activation in modern deep networks: it's simple,
fast to compute, and works well in practice. `sigmoid` squashes any input into the range (0, 1),
useful when you want an output interpretable as a probability.

## Stacking perceptrons into layers

A single perceptron can only learn simple, linearly-separable patterns. A **layer** is a group of
perceptrons operating on the same input; stacking multiple layers (a "multi-layer perceptron" or
MLP) lets the network build up increasingly abstract representations, layer by layer.

```python
# Conceptual sketch: one hidden layer of 3 neurons feeding into 1 output neuron
def layer(inputs, weight_matrix, biases, activation):
    return [activation(sum(i * w for i, w in zip(inputs, neuron_weights)) + b)
            for neuron_weights, b in zip(weight_matrix, biases)]

hidden_output = layer([1.0, 0.5], weight_matrix=[[0.2, 0.4], [0.1, -0.3], [0.5, 0.5]], biases=[0.1, 0.0, -0.1], activation=relu)
print(hidden_output)  # 3 numbers, the hidden layer's activations
```

Early layers in a deep network tend to learn simple patterns; later layers combine those into more
abstract, task-specific concepts. In an image model, early layers might detect edges, later layers
detect shapes, and the final layers detect entire objects — an analogous kind of abstraction-building
happens in language models with linguistic and semantic patterns instead of visual ones.

## Looking ahead

Course 3's transformer architecture is a specific, highly sophisticated arrangement of layers like
these, combined with an attention mechanism that lets the network decide which earlier words in a
sentence matter most for understanding the current word. The weights-times-inputs-plus-bias
mechanic in this lesson is the atomic building block that everything in Course 3 is built from.
""",
                    "examples": [
                        {
                            "title": "Example: A perceptron acting as a simple binary classifier",
                            "code": "def perceptron(inputs, weights, bias):\n    weighted_sum = sum(i * w for i, w in zip(inputs, weights)) + bias\n    return 1 if weighted_sum > 0 else 0\n\n# Classify whether a simplified (length, complexity) pair looks like a 'hard' question\nexamples = [(0.9, 0.8), (0.1, 0.1), (0.8, 0.9), (0.2, 0.3)]\nweights, bias = [0.6, 0.6], -0.5\nfor length, complexity in examples:\n    print((length, complexity), \"->\", perceptron([length, complexity], weights, bias))",
                            "explanation": "Applies a hand-set (not learned) perceptron to classify simplified feature pairs, illustrating the mechanic before worrying about how weights would actually be learned.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement the relu and sigmoid functions from scratch and apply each to the list [-3, -0.5, 0, 0.5, 3], printing both sets of results side by side.",
                            "difficulty": "easy",
                            "hint": "Use a list comprehension calling relu(x) and sigmoid(x) for each value in the list.",
                        },
                        {
                            "prompt": "Hand-pick weights and a bias for a perceptron that correctly classifies these 4 (x1, x2) pairs into 2 classes: (5,5)->1, (1,1)->0, (4,6)->1, (0,2)->0. Verify your perceptron gets all 4 correct.",
                            "difficulty": "hard",
                            "hint": "A weighted sum like 0.5*x1 + 0.5*x2 with a bias around -4 or -5 may separate these groups; experiment.",
                        },
                        {
                            "prompt": "In 2-3 sentences, explain why a network with 5 layers but NO non-linear activation functions between them would behave identically to a single linear layer.",
                            "difficulty": "medium",
                            "hint": "Consider that composing linear functions (matrix multiplications) always produces another linear function.",
                        },
                    ],
                    "resources": [
                        {"title": "3Blue1Brown: But what is a neural network?", "url": "https://www.3blue1brown.com/lessons/neural-networks", "resource_type": "video"},
                    ],
                    "skills": [{"slug": "ai-ml", "weight": 1.0}],
                },
                {
                    "slug": "backpropagation-and-gradient-descent",
                    "title": "Backpropagation and Gradient Descent",
                    "description": "How a neural network actually learns: computing gradients and nudging weights to reduce error.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Explain the intuition behind gradient descent as 'walking downhill' on an error surface",
                        "Describe what backpropagation computes and why it's needed for multi-layer networks",
                        "Explain the role of the learning rate in training stability and speed",
                        "Connect this training process to how LLMs are trained at massive scale",
                    ],
                    "content_markdown": """
## Why this matters

You will never hand-implement backpropagation for a real project in this program — frameworks handle
it entirely. But knowing what it does demystifies phrases like "the model learned this from data,"
"training loss," and "learning rate" that you'll encounter constantly when reading about how LLMs
are built and fine-tuned.

## Gradient descent: walking downhill

Imagine the model's total error as a landscape with hills and valleys, where each point in the
landscape corresponds to a specific setting of the model's weights. Training means finding a low
point (low error) in that landscape. Gradient descent does this by repeatedly checking which
direction is "downhill" from the current position (the gradient) and taking a small step that way.

```python
# A tiny gradient descent example minimizing a simple function by hand,
# standing in for the (vastly more complex) error landscape of a real model.
def f(x):
    return (x - 3) ** 2  # minimum at x = 3

def gradient(x):
    return 2 * (x - 3)   # derivative of f

x = 0.0            # starting guess
learning_rate = 0.1

for step in range(20):
    grad = gradient(x)
    x = x - learning_rate * grad   # move against the gradient, i.e. downhill

print(round(x, 3))  # converges toward 3.0
```

This tiny loop captures the entire idea: compute how the error changes with respect to the current
parameter, then nudge the parameter in the direction that reduces error. Real models do this for
millions or billions of parameters simultaneously.

## Backpropagation: computing gradients efficiently through many layers

A neural network with many layers has many, many parameters. Backpropagation is the algorithm that
efficiently computes how much each individual weight in every layer contributed to the final error,
by propagating the error signal backward from the output layer through each earlier layer using the
chain rule from calculus. Without backpropagation, computing these gradients for a deep network would
be computationally infeasible.

The practical takeaway, without the calculus: backpropagation answers the question "if I nudge this
one specific weight slightly, how much does the final error change?" for every single weight in the
network, all in one efficient backward pass.

## The learning rate

```python
# Too large a learning rate can overshoot the minimum and fail to converge
learning_rate_too_large = 1.5
# Too small a learning rate converges correctly but very slowly
learning_rate_too_small = 0.0001
```

The learning rate controls how big each step is. Too large, and training can overshoot the minimum
and oscillate or diverge entirely; too small, and training converges so slowly it may not finish in
any reasonable amount of time. Choosing (and often dynamically adjusting) the learning rate is one of
the most impactful decisions in training any neural network.

## Training loss over time

```python
losses = [2.5, 1.8, 1.2, 0.9, 0.7, 0.65, 0.6, 0.61, 0.59]
# A steadily decreasing, then plateauing loss curve is the expected healthy pattern.
# A loss that suddenly spikes upward often signals a learning rate that's too high.
```

## How this connects to training LLMs at scale

Training a large language model runs exactly this gradient descent + backpropagation loop, just
across billions of parameters, using massive amounts of text and enormous computational resources
(many GPUs running in parallel for weeks or months). The mechanism is identical to the tiny example
above; only the scale changes.

## Looking ahead

You'll never need to reimplement this training loop yourself in this program, but Course 3 assumes
you understand that a transformer's billions of parameters were set by exactly this process —
gradient descent guided by backpropagation, run over a colossal amount of text, until the loss curve
flattens out at a useful level of language understanding.
""",
                    "examples": [
                        {
                            "title": "Example: Watching gradient descent converge on a 2-parameter problem",
                            "code": "def f(w1, w2):\n    return (w1 - 2) ** 2 + (w2 + 1) ** 2\n\ndef gradients(w1, w2):\n    return 2 * (w1 - 2), 2 * (w2 + 1)\n\nw1, w2 = 0.0, 0.0\nlr = 0.1\nfor step in range(30):\n    g1, g2 = gradients(w1, w2)\n    w1 -= lr * g1\n    w2 -= lr * g2\n\nprint(round(w1, 2), round(w2, 2))  # converges toward (2.0, -1.0)",
                            "explanation": "Extends the single-variable example to two parameters at once, mirroring (at tiny scale) how real training simultaneously updates many weights each step.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Modify the single-variable gradient descent example to minimize f(x) = (x + 5) ** 2 instead, and verify x converges toward -5.",
                            "difficulty": "easy",
                            "hint": "The gradient of (x + 5) ** 2 is 2 * (x + 5); adjust the gradient function accordingly.",
                        },
                        {
                            "prompt": "Run the same gradient descent loop with learning_rate = 1.5 instead of 0.1 and observe what happens to x over the iterations. Explain the result in 1-2 sentences.",
                            "difficulty": "medium",
                            "hint": "Print x at every step -- with too large a learning rate you should see it oscillate or diverge instead of settling near 3.",
                        },
                        {
                            "prompt": "In your own words (2-3 sentences), explain why backpropagation is necessary for a network with many layers, rather than just computing each layer's gradient independently and separately.",
                            "difficulty": "hard",
                            "hint": "Consider that an early layer's weights affect the final error only indirectly, through every layer that comes after it -- the chain rule is what connects that indirect effect back to a usable gradient.",
                        },
                    ],
                    "resources": [
                        {"title": "3Blue1Brown: Backpropagation, intuitively", "url": "https://www.3blue1brown.com/lessons/backpropagation", "resource_type": "video"},
                    ],
                    "skills": [{"slug": "ai-ml", "weight": 1.0}],
                },
            ],
        },
    ],
}

COURSE_EXAM = {
    "title": "AI & Machine Learning Foundations: Course Assessment",
    "description": "Checks readiness to move from ML foundations into LLM Fundamentals.",
    "assessment_type": "course_exam",
    "passing_score": 0.7,
    "time_limit_minutes": 35,
    "questions": [
        {
            "question_type": "mcq",
            "prompt": "Which statement correctly describes the relationship between AI, machine learning, and deep learning?",
            "options": [
                {"id": "a", "text": "They are three unrelated, independent fields"},
                {"id": "b", "text": "Deep learning is a subset of machine learning, which is a subset of AI"},
                {"id": "c", "text": "AI is a subset of machine learning"},
                {"id": "d", "text": "Machine learning is a subset of deep learning"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "The three form nested circles: every deep learning system is machine learning, and every machine learning system is AI, but not the reverse.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "ai-ml",
        },
        {
            "question_type": "mcq",
            "prompt": "Why is it important to keep a test set completely separate from data used to tune a model during development?",
            "options": [
                {"id": "a", "text": "It speeds up training"},
                {"id": "b", "text": "Reusing it for tuning turns it into a de facto validation set, making the final reported performance unreliable"},
                {"id": "c", "text": "scikit-learn requires it by default"},
                {"id": "d", "text": "It reduces the amount of data needed overall"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "A test set only gives an honest final performance estimate if it was never used to influence model or hyperparameter choices; otherwise the model has effectively 'seen' it.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "ai-ml",
        },
        {
            "question_type": "multi_select",
            "prompt": "Which of the following are examples of unsupervised learning tasks? (Select all that apply.)",
            "options": [
                {"id": "a", "text": "Grouping unlabeled customer support tickets by topic using k-means"},
                {"id": "b", "text": "Predicting house prices from labeled square-footage and price data"},
                {"id": "c", "text": "Reducing 300-dimensional embeddings to 2 dimensions with PCA for visualization"},
                {"id": "d", "text": "Classifying emails as spam or not-spam using labeled training data"},
            ],
            "correct_answer": {"choices": ["a", "c"]},
            "explanation": "Clustering and dimensionality reduction work on unlabeled data. Predicting house prices and classifying spam both require labeled examples, making them supervised learning tasks.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "ai-ml",
        },
        {
            "question_type": "mcq",
            "prompt": "A spam classifier that always predicts 'not spam' achieves 95% accuracy on a dataset where 95% of messages are legitimate. What does this scenario illustrate?",
            "options": [
                {"id": "a", "text": "The model is excellent and ready for production"},
                {"id": "b", "text": "Accuracy alone can be misleading on imbalanced datasets, and metrics like recall or precision are needed"},
                {"id": "c", "text": "95% accuracy is impossible to achieve without real learning"},
                {"id": "d", "text": "The dataset must be mislabeled"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "This is the classic imbalanced-class trap: a trivial always-predict-majority-class model can score high accuracy while being useless at the actual task, which is why precision and recall matter.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "ai-ml",
        },
        {
            "question_type": "mcq",
            "prompt": "A model achieves 98% training accuracy but only 65% validation accuracy. What does this pattern most likely indicate?",
            "options": [
                {"id": "a", "text": "Underfitting"},
                {"id": "b", "text": "Overfitting"},
                {"id": "c", "text": "Data leakage in the training set only"},
                {"id": "d", "text": "The model is perfectly calibrated"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "A large gap between high training performance and much lower validation performance is the standard signature of overfitting: the model memorized training-specific noise rather than learning generalizable patterns.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "ai-ml",
        },
        {
            "question_type": "coding",
            "prompt": "Using scikit-learn, write code that fits a StandardScaler on a training set X_train and correctly applies (without refitting) that same scaling to a separate X_val set.",
            "options": [],
            "correct_answer": {
                "expected_behavior": "Calls scaler.fit(X_train) or scaler.fit_transform(X_train) exactly once on the training data, then calls scaler.transform(X_val) on the validation data without calling fit again on X_val.",
                "sample_solution": "from sklearn.preprocessing import StandardScaler\n\nscaler = StandardScaler()\nX_train_scaled = scaler.fit_transform(X_train)\nX_val_scaled = scaler.transform(X_val)",
            },
            "explanation": "Fitting the scaler only on training data and reusing those statistics on validation/test data avoids data leakage, a core discipline covered in the Feature Engineering module.",
            "difficulty": "medium",
            "points": 2.0,
            "skill_slug": "ai-ml",
        },
        {
            "question_type": "mcq",
            "prompt": "Why is one-hot encoding generally preferred over simple integer label encoding for a NOMINAL categorical feature like 'tool_name' (search, calculator, translator)?",
            "options": [
                {"id": "a", "text": "One-hot encoding uses less memory"},
                {"id": "b", "text": "Integer labels would falsely imply an ordering between categories that don't actually have one"},
                {"id": "c", "text": "One-hot encoding is required by all ML libraries"},
                {"id": "d", "text": "Integer labels cannot be used with scikit-learn"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Assigning arbitrary integers to nominal categories (e.g. search=0, calculator=1, translator=2) implies a false numeric ordering; one-hot encoding avoids that by giving each category its own independent binary column.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "ai-ml",
        },
        {
            "question_type": "mcq",
            "prompt": "What does an embedding represent, at a conceptual level?",
            "options": [
                {"id": "a", "text": "A compressed image file"},
                {"id": "b", "text": "A dense numeric vector positioned so that semantically similar items land close together in vector space"},
                {"id": "c", "text": "A lookup table mapping words to their dictionary definitions"},
                {"id": "d", "text": "A hash of the original text used only for deduplication"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Embeddings turn meaning into geometry: items with similar meaning are learned to be numerically close together, which is what enables similarity-based retrieval.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "embeddings",
        },
        {
            "question_type": "mcq",
            "prompt": "Why is cosine similarity typically preferred over Euclidean distance when comparing text embeddings?",
            "options": [
                {"id": "a", "text": "Cosine similarity is always faster to compute"},
                {"id": "b", "text": "Cosine similarity focuses on the direction (meaning) of vectors and ignores their magnitude"},
                {"id": "c", "text": "Euclidean distance cannot be computed for vectors with more than 3 dimensions"},
                {"id": "d", "text": "Cosine similarity is the only measure supported by NumPy"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Most text embedding models are trained and benchmarked using cosine similarity because it captures directional (semantic) similarity independent of vector length, which Euclidean distance does not.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "embeddings",
        },
        {
            "question_type": "scenario",
            "prompt": "You've embedded a query and a set of 10,000 candidate documents, and you want to retrieve the 5 documents most relevant to the query. Describe, step by step, how you would do this using the similarity concepts from this course, and explain why real production systems don't literally compare the query against all 10,000 documents one by one.",
            "options": [],
            "correct_answer": {
                "expected": "Compute the cosine similarity between the query embedding and every candidate document embedding, sort the results in descending order of similarity, and return the top 5. In production, brute-force comparison against every document doesn't scale, so vector databases use specialized indexing structures (covered in the RAG course) to approximate this top-k search much faster than a full linear scan.",
            },
            "explanation": "This scenario checks that the student can connect the top-k ranking pattern practiced in the Embeddings module to the real-world scaling challenge that motivates vector databases in Course 6.",
            "difficulty": "hard",
            "points": 2.0,
            "skill_slug": "embeddings",
        },
        {
            "question_type": "mcq",
            "prompt": "Why are non-linear activation functions (like ReLU or sigmoid) necessary between layers of a neural network?",
            "options": [
                {"id": "a", "text": "They make the network train faster on any hardware"},
                {"id": "b", "text": "Without them, stacking multiple layers would mathematically collapse into a single linear function, unable to learn complex patterns"},
                {"id": "c", "text": "They are only needed for image data, not text"},
                {"id": "d", "text": "They eliminate the need for a bias term"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Composing purely linear layers always yields another linear function no matter how many layers are stacked; non-linear activations are what let deep networks represent genuinely complex, curved patterns.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "ai-ml",
        },
        {
            "question_type": "short_answer",
            "prompt": "In your own words, explain what gradient descent does and what role the learning rate plays in the process.",
            "options": [],
            "correct_answer": {
                "expected": "Gradient descent iteratively adjusts a model's parameters in the direction that reduces error (the negative gradient), repeating this process until error is minimized. The learning rate controls the size of each adjustment step: too large risks overshooting or diverging, too small makes training very slow.",
                "keywords": ["gradient", "learning rate", "error", "minimize", "step size"],
            },
            "explanation": "This captures the core mental model needed before encountering training and fine-tuning discussions in later courses, without requiring the underlying calculus.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "ai-ml",
        },
        {
            "question_type": "mcq",
            "prompt": "What does backpropagation compute in a multi-layer neural network?",
            "options": [
                {"id": "a", "text": "The final output of the network for a given input"},
                {"id": "b", "text": "How much each individual weight across all layers contributed to the final error, by propagating the error signal backward"},
                {"id": "c", "text": "The optimal number of layers a network should have"},
                {"id": "d", "text": "A random initialization for the network's weights"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Backpropagation efficiently computes gradients for every weight in every layer by propagating the error backward through the network using the chain rule, making gradient descent feasible for deep networks.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "ai-ml",
        },
        {
            "question_type": "mcq",
            "prompt": "A decision tree classifier with no max_depth limit is trained on a small dataset and achieves 100% training accuracy but performs poorly on new data. What is the most direct fix suggested by this course's Model Evaluation module?",
            "options": [
                {"id": "a", "text": "Increase the tree's max_depth further"},
                {"id": "b", "text": "Limit max_depth (or otherwise regularize the model) and evaluate using a held-out validation set"},
                {"id": "c", "text": "Remove the test set entirely"},
                {"id": "d", "text": "Switch to reporting only training accuracy going forward"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "An unconstrained tree that perfectly fits training data is a textbook overfitting case; limiting depth (regularization) and checking validation performance is the standard remedy covered in this course.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "ai-ml",
        },
    ],
}
