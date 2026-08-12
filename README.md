# Skilltree 🌳

A graph-powered learning-path planner that helps learners answer three simple questions:

* **What should I learn next?**
* **What do I need to learn before a target skill?**
* **Which course should I take for each skill?**

Skilltree uses a prerequisite graph to understand relationships between skills and courses. Tell it what you already know, choose a target skill, and it calculates an ordered learning path to reach your target.

---

## 🚀 Live Demo

[**Open Skilltree**](https://skilltree-f0u5.onrender.com/)

The application is hosted on **Render** using a free hosting tier and backed by **CognoDB**, with the Neo4j Python driver and openCypher over Bolt.

> **Note:** The free Render instance may take a few seconds to wake up after inactivity.

🎥 **Screen Recording:**
[**Watch the Skilltree Demo**](screen-recording-link)

---

## 📦 GitHub Repository

This repository contains the complete Skilltree implementation, including:

* Full application source code
* Data-loading scripts
* Cypher/openCypher queries
* Graph database setup
* Frontend/UI implementation
* Documentation and screenshots
* Instructions for running the application locally

**Repository:** [GitHub Repository](github-repository-link)

> If the repository is private, access will be provided to the reviewers upon request.

---

## 🎯 Use Case

Learning resources are often presented as independent courses or skill lists. However, many skills have prerequisites.

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

A learner who already knows Python should not have to start from the beginning. They need a system that understands **which skills they already have, which prerequisites are missing, and what they should learn next**.

Skilltree solves this problem by representing skills and their dependencies as a graph.

The learner provides:

1. Their existing skills.
2. A target skill they want to achieve.

Skilltree then calculates the missing prerequisites, orders them into a valid learning sequence, and recommends courses for each step.

---

## 🧠 Why a Graph Database?

A graph database is a natural fit for Skilltree because the core of the application is about **relationships and dependencies**.

A traditional relational approach could store skills and prerequisites in tables, but traversing multiple levels of prerequisites can become increasingly complex.

With a graph database, relationships are first-class entities.

For example:

```text
Python
  ↓ requires
Data Structures
  ↓ requires
Algorithms
  ↓ requires
Machine Learning
```

This allows Skilltree to efficiently answer questions such as:

* What are all prerequisites of a skill?
* Which prerequisites does a learner already know?
* What skills are currently available to learn?
* What is the dependency path between two skills?
* Which course is associated with a particular skill?

### Advantages of the Graph Approach

**1. Natural representation**

Skills and prerequisites map directly to nodes and relationships.

**2. Multi-level traversal**

A target skill may have prerequisites several levels deep. Graph traversal makes these relationships straightforward to query.

**3. Flexible data model**

New skills, courses, and relationships can be added without redesigning a large relational schema.

**4. Relationship-focused queries**

The application's most important questions are fundamentally graph questions, making Cypher/openCypher a natural query language.

---

## 🗺️ Data Model

The core graph consists of **Skill** and **Course** nodes connected by relationships.

```text
┌──────────────┐
│    Skill     │
└──────────────┘
       │
       │ REQUIRES
       ▼
┌──────────────┐
│    Skill     │
└──────────────┘

┌──────────────┐
│    Skill     │
└──────────────┘
       │
       │ HAS_COURSE
       ▼
┌──────────────┐
│    Course    │
└──────────────┘
```

A simplified graph looks like:

```text
Skill: Python
      │
      │ REQUIRES
      ▼
Skill: Data Structures
      │
      │ REQUIRES
      ▼
Skill: Algorithms
      │
      │ REQUIRES
      ▼
Skill: Machine Learning

Skill: Algorithms
      │
      │ HAS_COURSE
      ▼
Course: Algorithms Course
```

### Main Entities

| Entity     | Description                                        |
| ---------- | -------------------------------------------------- |
| **Skill**  | A concept or competency that a learner can acquire |
| **Course** | A learning resource associated with a skill        |

### Main Relationships

| Relationship | Meaning                                        |
| ------------ | ---------------------------------------------- |
| `REQUIRES`   | One skill is a prerequisite for another        |
| `HAS_COURSE` | A course teaches or is associated with a skill |

---

## ✨ Features

### 1. Interactive Skill Graph

Explore relationships between skills through an interactive graph.

Each skill can be:

* 🟢 **Known** — a skill the learner already has
* 🟡 **Ready to Learn** — all prerequisites are satisfied
* ⚫ **Locked** — one or more prerequisites are missing
* 🔵 **Target** — the skill the learner wants to reach

The graph makes prerequisite relationships visually understandable instead of presenting them as a flat course list.

### 2. Personalized Learning Path

Select a target skill and tell Skilltree what you already know.

The application:

1. Finds the prerequisite subgraph.
2. Removes skills the learner already knows.
3. Orders the remaining skills using topological sorting.
4. Recommends a suitable course for each step.

### 3. What Can I Learn Next?

Skilltree identifies skills whose prerequisites are already satisfied.

This allows learners to discover their next possible learning opportunities without manually checking every prerequisite.

### 4. Course Recommendations

Each learning step can be associated with a course, allowing the application to answer both:

> **What should I learn?**

and:

> **What course should I take?**

---

## 🔍 Main Graph Queries

Skilltree uses Cypher/openCypher to query the graph.

### Find Prerequisites

The application can traverse prerequisite relationships to find the skills required for a target skill.

Conceptually:

```cypher
MATCH path = (prerequisite:Skill)-[:REQUIRES*]->(target:Skill)
RETURN path
```

This allows Skilltree to discover multi-level dependencies instead of only direct prerequisites.

### Find Skills Ready to Learn

A skill is considered ready when its prerequisites are already satisfied by the learner's known skills.

Conceptually, the query checks:

```text
Candidate Skill
      ↓
Check Prerequisites
      ↓
All prerequisites known?
      ↓
Yes → Ready to Learn
No  → Locked
```

### Find Courses for a Skill

Courses associated with a skill can be retrieved through the `HAS_COURSE` relationship.

Conceptually:

```cypher
MATCH (skill:Skill)-[:HAS_COURSE]->(course:Course)
RETURN skill, course
```

### Generate a Learning Path

The application combines graph traversal with topological sorting:

```text
Target Skill
     ↓
Find Prerequisites
     ↓
Remove Known Skills
     ↓
Resolve Dependencies
     ↓
Topological Sort
     ↓
Learning Path
     ↓
Course Recommendations
```

The actual Cypher/openCypher queries used by the application are included in the repository.

---

## 🗄️ CognoDB

Skilltree uses **CognoDB** as its graph database.

The application connects to CognoDB using:

* Neo4j Python Driver
* openCypher
* Bolt

### Creating a CognoDB Instance

1. Create or sign in to your CognoDB account.
2. Create a new graph/database instance.
3. Note the database connection details.
4. Obtain the Bolt connection URI and credentials.
5. Add them to the application's environment variables.
6. Run the provided data-loading scripts to populate the graph.
7. Start the Skilltree application.

Example environment configuration:

```env
COGNODB_URI=<your-bolt-uri>
COGNODB_USERNAME=<your-username>
COGNODB_PASSWORD=<your-password>
```

> Use the exact environment-variable names configured in the application.

---

## 🛠️ Setup and Run Locally

### Prerequisites

* Python 3.x
* A CognoDB graph database instance
* Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd skilltree
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Database

Create a `.env` file containing your CognoDB connection details:

```env
COGNODB_URI=<your-bolt-uri>
COGNODB_USERNAME=<your-username>
COGNODB_PASSWORD=<your-password>
```

### 4. Load the Data

Run the included data-loading script:

```bash
python <data-loader-script>.py
```

This creates the skills, prerequisite relationships, courses, and course relationships required by Skilltree.

### 5. Run the Application

```bash
python app.py
```

Open the local URL displayed by the application.

---

## 📸 Screenshots

### Skill Graph

![Skill Graph](screenshots/skill-graph.png)

The interactive graph visualizes skills, prerequisites, and their current learning status.

### Personalized Learning Path

![Learning Path](screenshots/learning-path.png)

The learning-path view shows the ordered skills required to reach the selected target.

### Course Recommendations

![Course Recommendations](screenshots/course-recommendations.png)

Courses are displayed alongside the relevant skills in the generated learning path.

> Add the actual UI screenshots to the `screenshots/` directory before submitting the repository.

---

## 🏗️ Project Structure

```text
skilltree/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
│
├── data/
│   └── ...
│
├── scripts/
│   └── ...
│
├── queries/
│   └── ...
│
├── screenshots/
│   ├── skill-graph.png
│   ├── learning-path.png
│   └── course-recommendations.png
│
└── ...
```

The repository includes the application source code, graph data/loading scripts, and Cypher/openCypher queries used by Skilltree.

---

## 🎥 Demo & Submission Requirements

This project includes the required submission components:

* ✅ **Full source code** — application, data-loading scripts, and Cypher queries
* ✅ **README** — use case and motivation for using a graph database
* ✅ **Data model** — graph structure and relationships documented above
* ✅ **Setup instructions** — including CognoDB instance creation and configuration
* ✅ **Main queries** — explained with examples
* ✅ **UI screenshots** — included in the repository
* ✅ **Hosted application demo** — [Skilltree on Render](https://skilltree-f0u5.onrender.com/)
* 🎥 **Short screen recording** — [Watch the Skilltree Demo](screen-recording-link)

### Private Repository

If the GitHub repository is private, access will be provided to the reviewers so that the complete source code and supporting files can be evaluated.

---

## 🤝 Contributing

Contributions and suggestions are welcome.

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Test the changes.
5. Submit a pull request.

---

## 📄 License

Add the project's license information here.

---

## 🌳 Why Skilltree?

Traditional learning platforms often present courses as a list.

Skilltree treats learning as a **graph of connected skills**.

By combining a learner's existing knowledge with prerequisite relationships, Skilltree transforms:

**What I know → What I need → What I should learn next → Which course can help me get there.**

> **Learning is a graph, not a list.**
