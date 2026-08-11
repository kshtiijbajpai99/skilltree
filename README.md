# Skilltree 🌳

A graph-powered learning-path planner that helps you answer three simple questions:

- **What should I learn next?**
- **What do I need to learn before a target skill?**
- **Which course should I take for each skill?**

Skilltree uses a prerequisite graph to understand the relationship between skills and courses. Tell it what you already know, choose a target skill, and it calculates an ordered learning path to reach that target.

## 🚀 Live Demo

**[Open Skilltree](https://skilltree-f0u5.onrender.com)**

> The application is deployed on Render and backed by CognoDB.

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

```text
Python Syntax
      ↓
Programming Basics
      ↓
Python Data Structures
      ↓
NumPy & Pandas
      ↓
Data Visualization
