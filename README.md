# Skilltree 🌳

A graph-powered learning-path planner that helps you answer three simple questions:

- **What should I learn next?**
- **What do I need to learn before a target skill?**
- **Which course should I take for each skill?**

Skilltree uses a prerequisite graph to understand the relationship between skills and courses. Tell it what you already know, choose a target skill, and it calculates an ordered learning path to reach that target.

---

## 🚀 Live Demo

[**Open Skilltree**](https://skilltree-f0u5.onrender.com/)

The application is deployed on Render and backed by **CognoDB**, using the Neo4j Python driver and openCypher over Bolt.

> The free Render instance may take a few seconds to wake up after inactivity.

---

## ✨ Features

### 1. Interactive Skill Graph

Explore relationships between skills through an interactive graph.

Each skill can be:

- 🟢 **Known**
- 🟡 **Ready to learn**
- ⚫ **Locked**
- 🔵 **Target**

The graph makes prerequisite relationships visually understandable instead of presenting them as a flat course list.

### 2. Personalized Learning Path

Select a target skill and tell Skilltree what you already know.

The application:

1. Finds the prerequisite subgraph.
2. Removes skills you already know.
3. Orders the remaining skills using topological sorting.
4. Recommends a suitable course for each step.

### 3. "What Can I Learn Next?"

Skilltree identifies skills whose prerequisites are already satisfied.

For example:

    Python Syntax
          ↓
    Programming Basics
          ↓
    Python Data Structures
          ↓
    NumPy & Pandas
          ↓
    Data Visualization

### 4. Skill Details

Click any skill in the graph to see:

- Description
- Direct prerequisites
- Skills it unlocks
- Available courses

---

## 🧠 Why a Graph Database?

Prerequisite relationships are the core of Skilltree, and they do not have a fixed depth.

For example:

    Arithmetic
        ↓
    Algebra
        ↓
    Linear Algebra
        ↓
    Probability & Statistics
        ↓
    Machine Learning Basics
        ↓
    Deep Learning

A relational database can model these relationships, but multi-hop prerequisite traversal, prerequisite intersections, and dynamically finding newly available skills become more natural as graph queries.

Skilltree uses openCypher variable-length traversals such as:

```cypher
MATCH (ancestor:Skill)-[:PREREQUISITE_OF*1..8]->(target:Skill {id: $id})

For finding skills that are immediately learnable:

MATCH (s:Skill)
WHERE NOT s.id IN $known
  AND NOT EXISTS {
        MATCH (p:Skill)-[:PREREQUISITE_OF]->(s)
        WHERE NOT p.id IN $known
      }

This makes the graph structure directly express the learning rules.

🗂️ Data Model
Nodes
Skill
Skill {
    id,
    name,
    category,
    description
}

The project contains 46 seeded skills across:

Mathematics
Programming Fundamentals
Web Development
Data Science
DevOps
Systems
Course
Course {
    id,
    title,
    provider,
    level,
    duration_hours,
    description
}

The project contains 34 seeded courses.

Relationships
(:Skill)-[:PREREQUISITE_OF]->(:Skill)

(:Course)-[:TEACHES]->(:Skill)

(:Course)-[:REQUIRES]->(:Skill)

The prerequisite graph forms a DAG (Directed Acyclic Graph).

🔍 Backend Queries

All Cypher queries are parameterized through the Neo4j Python driver.

No user input is directly inserted into Cypher query strings.

Query	Purpose
get_prerequisite_chain	Finds prerequisite skills at multiple depths
get_frontier_skills	Finds skills that can be learned immediately
get_missing_prereq_subgraph	Finds skills still required before a target
get_common_ancestors	Finds prerequisites shared by two target skills
get_best_course_for_skill	Finds a suitable course for a skill
get_skill_detail	Gets prerequisites, dependents and courses

The graph query identifies the required subgraph, while backend/pathing.py performs a topological sort to produce the final ordered learning path.

🏗️ Project Structure
skilltree/
│
├── backend/
│   ├── main.py
│   ├── db.py
│   ├── queries.py
│   ├── pathing.py
│   ├── seed_data.py
│   ├── requirements.txt
│   │
│   └── data/
│       ├── skills.json
│       └── courses.json
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   └── lib/
│
├── docs/
│   ├── screenshot-graph.png
│   ├── screenshot-path.png
│   └── screenshot-detail.png
│
├── render.yaml
├── Procfile
├── .env.example
├── .gitignore
└── README.md
⚙️ Tech Stack
Backend
Python
FastAPI
Uvicorn
Neo4j Python Driver
openCypher
CognoDB
Frontend
HTML
CSS
JavaScript
vis-network
Deployment
Render
GitHub
🛠️ Local Setup
1. Clone the repository
git clone https://github.com/kshtiijbajpai99/skilltree.git
cd skilltree
2. Configure environment variables

Copy the example environment file:

cp .env.example .env

Then configure:

COGNODB_URI=bolt+s://<your-instance>.databases.cognodb.cloud
COGNODB_USER=cognodb
COGNODB_PASSWORD=<your-password>
3. Install dependencies
cd backend
pip install -r requirements.txt
4. Seed the graph
python seed_data.py

The seed operation is designed to be safe to run again.

5. Run the application
uvicorn main:app --reload --port 8000

Open:

http://localhost:8000

The FastAPI application serves both the API and frontend from the same service.

🌐 API Endpoints
Endpoint	Purpose
GET /api/health	Health and graph counts
GET /api/skills	List available skills
GET /api/graph	Get the full skill graph
GET /api/skill/{skill_id}	Get skill details
GET /api/skill/{skill_id}/chain	Get prerequisite chain
GET /api/next	Find immediately learnable skills
GET /api/path	Generate a learning path
GET /api/common-ancestors	Find shared prerequisites
🚀 Deployment

The project includes a render.yaml Blueprint configuration.

The deployed service uses:

Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT

The following values are configured as environment variables on Render:

COGNODB_URI
COGNODB_USER
COGNODB_PASSWORD

Secrets are not committed to the repository.

📸 Screenshots
Interactive Skill Graph

Personalized Learning Path

Skill Details

🛡️ Error Handling

If CognoDB becomes unreachable or the credentials are invalid, the backend converts the database failure into a clean 503 Service Unavailable response.

The frontend displays a user-friendly error state with a Retry button instead of exposing a backend stack trace.

🤖 AI-Assisted Development

This project was developed with AI-assisted coding.

The code, data model, graph queries, and application architecture were reviewed and can be explained and defended.

🎯 Assignment Context

Skilltree was built for the Wexa AI take-home assignment.

The project demonstrates how a graph database can be used to solve prerequisite and learning-path problems involving multi-hop relationships and graph traversal.

📊 Project Statistics
46 Skills
34 Courses
~55 Prerequisite relationships
~40 Course → Skill relationships
~55 Course → Requirement relationships
🔗 Links
Live Demo: https://skilltree-f0u5.onrender.com/
GitHub: https://github.com/kshtiijbajpai99/skilltree
👤 Author

Kshitij Bajpai

Built as a graph-powered learning-path planner using FastAPI, JavaScript, CognoDB and openCypher.


**Important:** Is version mein section 3 ka example **indented text** hai, nested triple-backtick nahi. Isliye Markdown formatting break nahi hogi aur **Section 4 + baaki pura README properly continue karega.**

Ab **poora replace karke save karo**. Uske baad bas `done` bolo.
