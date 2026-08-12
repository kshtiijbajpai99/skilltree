# Skilltree 🌳

A graph-powered learning-path planner that helps you answer three simple questions:

* **What should I learn next?**
* **What do I need to learn before a target skill?**
* **Which course should I take for each skill?**

Skilltree uses a prerequisite graph to understand the relationships between skills and courses. Tell it what you already know, choose a target skill, and it calculates an ordered learning path to help you reach that target.

---

## 🚀 Live Demo

[**Open Skilltree**](https://skilltree-f0u5.onrender.com/)

Skilltree is deployed on Render and backed by **CognoDB**, using the Neo4j Python driver and openCypher over Bolt.

> **Note:** The free Render instance may take a few seconds to wake up after inactivity.

---

## ✨ Features

### 1. Interactive Skill Graph

Explore relationships between skills through an interactive graph.

Each skill can be:

* 🟢 **Known** — a skill you already have
* 🟡 **Ready to Learn** — all prerequisites are satisfied
* ⚫ **Locked** — one or more prerequisites are missing
* 🔵 **Target** — the skill you want to reach

The graph makes prerequisite relationships visually understandable instead of presenting them as a flat course list.

### 2. Personalized Learning Path

Select a target skill and tell Skilltree what you already know.

The application:

1. Finds the prerequisite subgraph for the target.
2. Removes skills you already know.
3. Orders the remaining skills using topological sorting.
4. Recommends a suitable course for each learning step.

This produces a personalized, dependency-aware learning path.

### 3. What Can I Learn Next?

Skilltree identifies skills whose prerequisites are already satisfied.

For example, if you already know:

```text
Python → Data Structures
```

and **Algorithms** requires Data Structures, Skilltree can identify **Algorithms** as ready to learn.

This helps learners continuously discover their next possible skills without manually checking every prerequisite.

### 4. Course Recommendations

Skilltree connects skills with courses so that each step of a learning path can include a practical course recommendation.

Instead of simply telling you *what* to learn, Skilltree also helps answer *where to learn it*.

### 5. Graph-Based Prerequisite Reasoning

The application models learning as a graph rather than a simple ordered list.

For example:

```text
Python
   ↓
Data Structures
   ↓
Algorithms
   ↓
Machine Learning
```

This allows Skilltree to reason about dependencies and generate paths based on what a learner already knows.

---

## 🧠 How It Works

Skilltree represents skills and their prerequisites as a directed graph.

A simplified model looks like:

```text
Skill ──requires──> Skill
Skill ──has course──> Course
```

When a learner selects a target skill, Skilltree traverses the prerequisite graph to determine everything required to reach that target.

The resulting skills are then filtered against the learner's existing knowledge and sorted into a valid learning order.

### Learning Path Algorithm

```text
Known Skills + Target Skill
            ↓
   Find Prerequisite Graph
            ↓
   Remove Known Skills
            ↓
   Topological Sort
            ↓
   Ordered Learning Path
            ↓
    Course Recommendations
```

---

## 🗄️ Database

Skilltree uses **CognoDB** as its graph database layer.

The application communicates with the database using:

* **Neo4j Python Driver**
* **openCypher**
* **Bolt**

The graph database allows Skilltree to efficiently represent and query relationships between skills, prerequisites, and courses.

---

## 🛠️ Tech Stack

* **Python**
* **Neo4j Python Driver**
* **openCypher**
* **Bolt**
* **CognoDB**
* **Render**

---

## 🚀 Getting Started

### Prerequisites

Make sure you have Python installed on your system.

### Clone the Repository

```bash
git clone <repository-url>
cd skilltree
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file and add the required database configuration:

```env
NEO4J_URI=<your-bolt-uri>
NEO4J_USERNAME=<your-username>
NEO4J_PASSWORD=<your-password>
```

Use the appropriate environment variable names required by your application.

### Run Locally

Start the application using the project's entry point.

For example:

```bash
python app.py
```

Then open the local URL shown in your terminal.

---

## 📁 Project Structure

```text
skilltree/
├── app.py
├── requirements.txt
├── README.md
├── .env
└── ...
```

The exact structure may vary depending on the current implementation.

---

## 🎯 Example

Suppose a learner already knows:

```text
Python
```

and wants to learn:

```text
Machine Learning
```

Skilltree might determine that the learner needs to follow a path such as:

```text
Python
  ↓
Data Structures
  ↓
Algorithms
  ↓
Statistics
  ↓
Machine Learning
```

Because Python is already known, it is removed from the remaining learning path:

```text
1. Data Structures
2. Algorithms
3. Statistics
4. Machine Learning
```

Skilltree can then associate courses with each step.

---

## 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Test your changes.
5. Submit a pull request.

---

## 📄 License

Add the project's license information here.

---

## 🌳 Why Skilltree?

Traditional course platforms often show learners a list of courses and leave them to decide what to learn first.

Skilltree takes a different approach:

> **Learning is a graph, not a list.**

By understanding prerequisites and existing knowledge, Skilltree helps learners find a logical path from **what they know** to **what they want to learn**.
