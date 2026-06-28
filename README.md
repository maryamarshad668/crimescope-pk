
# CrimeScope PK 

A full-stack Pakistan crime intelligence platform that aggregates, processes, and visualizes
crime-related news from major Pakistani media outlets in real time. Built with a modular NLP
pipeline, REST API backend, and an interactive React frontend.

---

# Table of Contents

- Overview
- Features
- System Architecture
- Project Structure
- Tech Stack
- Getting Started
  - Prerequisites
  - Backend Setup
  - Frontend Setup
  - Environment Variables
- Pipeline
- API Reference
- NLP Modules
- Data Sources
- Roadmap
- Author

---

# Overview

CrimeScope PK is a crime intelligence aggregation system designed specifically for the Pakistani news landscape. It scrapes crime-related articles from major Urdu and English news sources, runs them through an NLP/NER pipeline to extract structured entities (people, locations, crime types), geocodes extracted locations to coordinates, stores everything in MongoDB, and serves it through a FastAPI backend to a React dashboard with Leaflet maps and Recharts visualizations.

The goal is to make Pakistan's crime data—scattered across dozens of outlets—queryable, mappable, and analyzable in one place.

---

# Features

- Multi-source news scraping — Scrapes from Dawn, Geo, ARY News, Tribune, Dunya, and more
- NLP/NER pipeline — Extracts named entities (locations, persons, organizations, crime types) from article text
- Geocoding — Converts extracted location strings to lat/lng coordinates for map plotting
- Embeddings & RAG search — Semantic search over stored articles using vector embeddings
- Interactive map — Leaflet-based crime incident map with clustering and filtering
- Dashboard & charts — Recharts-powered visualizations for crime trends, source breakdowns, and timelines
- Scheduled ingestion — Automated scraping scheduler for continuous data updates
- REST API — FastAPI backend exposing all data and search endpoints
- AI features — Crime summarization and analysis routed through OpenRouter

---

# System Architecture

```mermaid
flowchart TD

A[News Sources<br/>Dawn • Geo • ARY • Tribune • Dunya • Samaa • PTV • BOL]

A --> B[NLP Pipeline<br/>NER Extraction<br/>Geocoding<br/>Embeddings]

B --> C[(MongoDB)]

C --> D[FastAPI Backend<br/>REST API<br/>RAG Search<br/>AI Features]

D --> E[React Frontend<br/>Leaflet Maps<br/>Recharts Dashboard<br/>Semantic Search]
````

---

# Tech Stack

| **Layer**  | **Technology**                           |
| ---------- | ---------------------------------------- |
| Frontend   | React, Vite, Leaflet, Recharts           |
| Backend    | FastAPI, Python                          |
| Database   | MongoDB                                  |
| NLP        | spaCy, Custom NER, sentence-transformers |
| AI / LLM   | OpenRouter API                           |
| Scraping   | BeautifulSoup, Requests                  |
| Scheduling | APScheduler                              |
| Dev Tools  | VS Code, Git, Postman                    |

---

# Pipeline

Each execution performs the following:

1. **Scrape** — Fetches latest crime articles.
2. **Extract** — Performs Named Entity Recognition.
3. **Geocode** — Converts locations into coordinates.
4. **Embed** — Generates vector embeddings.
5. **Store** — Saves structured incidents into MongoDB.
6. **Serve** — Exposes everything through FastAPI.

---

# NLP Modules

## extractor.py

Extracts:

* Locations
* Crime Types

## geocoder.py

Resolves extracted location names into latitude and longitude coordinates for visualization.

## embeddings.py

Generates sentence-transformer embeddings for semantic similarity search and RAG.

---

# Data Sources

| **Outlet**  | **Language**   | **Coverage** |
| ----------- | -------------- | ------------ |
| Dawn        | English        | National     |
| The Tribune | English        | National     |
| Geo News    | Urdu / English | National     |
| ARY News    | Urdu / English | National     |
| Dunya News  | Urdu           | National     |

---


# Author

**Maryam Arshad**

```
```
