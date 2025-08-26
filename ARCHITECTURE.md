# Whizzy Bot Architecture Overview

This document provides a comprehensive overview of the Whizzy Bot's architecture, from the high-level application flow down to the core agentic system and other key capabilities.

---

## Part 1: High-Level Application Flow

Here is the 30,000-foot view of the entire application, from user to bot and back again.

```
[User in Slack]
      |
      | 1. Asks a question ("@whizzy ...")
      v
[Slack API]
      |
      | 2. Forwards the message event
      v
[EnhancedWhizzyBot]  <- The "Presentation Layer" (app/enhanced_whizzy_bot.py)
      |
      | 3. Sends query to the "brain" for processing
      v
[EnhancedIntelligentAgenticSystem] <- The "Intelligence Layer" (app/intelligent_agentic_system.py)
      |
      | 4. Returns a structured JSON "Briefing Card"
      v
[EnhancedWhizzyBot]
      |
      | 5. Formats the JSON into Slack Markdown
      v
[Slack API]
      |
      | 6. Posts the formatted message
      v
[User in Slack]
```

#### Key Components:

*   **`EnhancedWhizzyBot` (Presentation Layer):** This is the front door of the application. Its only jobs are to listen for messages from Slack and format the final answer for Slack. It holds no intelligence itself.
*   **`EnhancedIntelligentAgenticSystem` (Intelligence Layer):** This is the "brain." It takes a raw query and is responsible for understanding it, fetching the necessary data, and creating a structured answer.

---

## Part 2: The Four-Agent Pipeline (Inside the "Brain")

This is the core of the new architecture. When the `EnhancedIntelligentAgenticSystem` receives a query, it passes it through this pipeline:

```
[Query] -> (1. Planner) -> [Plan] -> (2. Builder) -> [Blueprint] -> (3. Runner) -> [Data] -> (4. Narrator) -> [JSON Briefing Card]
```

#### Agent 1: The Planner
*   **Input:** Raw user query (`"what's our pipeline coverage?"`).
*   **Action:** Uses GPT-4 to classify the user's intent and extract key entities.
*   **Output (The Plan):** A structured object that understands *what* the user wants (e.g., `intent: 'BUSINESS_INTELLIGENCE'`, `persona: 'VP_SALES'`).

#### Agent 2: The Builder
*   **Input:** The Plan.
*   **Action:** Acts as a query generator. Based on the plan, it determines all the specific data points needed to answer the question.
*   **Output (The Blueprint):** A dictionary of all the SOQL queries required, e.g., `{"pipeline_value": "SELECT...", "win_rate": "SELECT...", ...}`.

#### Agent 3: The Runner
*   **Input:** The Blueprint of queries.
*   **Action:** Executes all the queries against the data source (e.g., Salesforce) in parallel to be fast and efficient.
*   **Output (The Data):** A structured dictionary containing the raw results of all the queries.

#### Agent 4: The Narrator
*   **Input:** The raw Data.
*   **Action:** This is the final, most advanced step. It uses GPT-4 Turbo with a specific prompt that tells it how to be a "VP of Sales Narrator." It analyzes the raw data, calculates final metrics (like percentages), finds insights, and recommends actions.
*   **Output (The Briefing Card):** A single, clean JSON object containing the final, structured answer.

---

## Part 3: Other Core Capabilities

Alongside the main request-response pipeline, the application has several other important features that make it a complete solution.

#### 1. Proactive Briefings & Scheduler
*   **Flow:** `[Scheduler] -> [Briefing Generator] -> [User in Slack]`
*   **How it Works:**
    *   A script, `scripts/run_scheduler.py`, is designed to be run on a schedule (e.g., every morning via a cron job).
    *   It reads a `data/subscriptions.json` file to see which users have subscribed to which briefings.
    *   For each subscriber, it calls the `app/briefings.py` module to generate the content for the briefing.
    *   The generated briefing is then sent directly to the user via Slack DM.
*   **User Commands:** Users can manage their subscriptions with commands like `subscribe`, `unsubscribe`, and `subscriptions`.

#### 2. Tool-Based, Extensible Architecture
*   **Concept:** The system is designed to be easily extended with new capabilities by adding "Tools."
*   **How it Works:**
    *   There is a `app/tools/` directory containing tools like `salesforce_tool.py` and `snowflake_tool.py`.
    *   Each tool adheres to a common `BaseTool` interface.
    *   To add a new capability, one would simply create a new tool file in this directory. The Planner and Builder agents could then be taught to use this new tool.

#### 3. Externalized Prompts for Malleable AI
*   **Concept:** The AI's "personality," instructions, and knowledge are not hardcoded in Python.
*   **How it Works:**
    *   All prompts are stored as plain text files in the `/prompts` directory, organized by type (system, persona, few-shot examples).
    *   This means the AI's behavior can be rapidly changed and improved by non-engineers simply by editing these text files. This is a crucial feature for maintaining and scaling an AI product.
