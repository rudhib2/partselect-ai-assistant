```md
# PartSelect Parts Assistant

This project implements a chat-based assistant for the PartSelect e-commerce platform focused on **refrigerator and dishwasher parts**.

The assistant helps customers:
- find replacement parts
- check compatibility between parts and appliance models
- troubleshoot appliance issues
- view installation guidance

The system is designed as a **tool-driven assistant architecture** where user queries are classified and routed to specialized backend tools.

---

# Use Cases

The assistant supports queries such as:

• How can I install part number PS11752778?  
• Is this part compatible with my WDT780SAEM1 model?  
• The ice maker on my Whirlpool fridge is not working  
• Find a dishwasher rack wheel

The interface presents results as **product cards with pricing, ratings, and quick actions** for compatibility checks and installation guidance.

---

# Architecture

## Backend

The backend is implemented using **FastAPI** and follows a tool-based routing architecture.

User queries are first classified into intents using an LLM:

- search
- compatibility
- troubleshoot
- install

Each intent is routed to a deterministic tool:

- `search_parts` — product search
- `check_compatibility` — model compatibility verification
- `get_troubleshooting_guide` — appliance issue diagnosis
- `get_install_guide` — installation instructions

All interactions are logged and aggregated to generate **business insights** such as search demand, common appliance failures, and unavailable product requests.

---

## Frontend

The frontend is a **React chat interface** designed to simulate a customer support experience.

Key features:

- conversational chat interface
- product cards with reviews and pricing
- suggested follow-up prompts
- quick actions for compatibility and installation
- analytics dashboard showing assistant usage insights

---

# Design Choices

**Scoped assistant**

The agent only responds to refrigerator and dishwasher parts queries to ensure reliability and avoid hallucinations.

**Tool-based architecture**

Instead of generating answers directly, the assistant routes queries to deterministic tools, improving accuracy and extensibility.

**Insight logging**

Every interaction is logged and aggregated into a dashboard that surfaces business insights such as popular parts, common symptoms, and missing catalog items.

---

# Running the Project

Backend


cd backend
uvicorn main:app --reload


Frontend

npm install
npm start
