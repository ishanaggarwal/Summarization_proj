# Resume Summarization & Search Pipeline
###by Ishan Aggarwal

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Setup & Installation](#setup--installation)

   * [Local Environment](#local-environment)
   * [Docker Environment](#docker-environment)
6. [API Endpoints & Usage](#api-endpoints--usage)

   * [Upload Endpoint](#upload-endpoint)
   * [Search Endpoint](#search-endpoint)
7. [Operational Details](#operational-details)

   * [File Ingestion & Text Extraction](#file-ingestion--text-extraction)
   * [Field Extraction](#field-extraction)
   * [Embedding & Indexing](#embedding--indexing)
   * [Similarity Search](#similarity-search)
8. [Troubleshooting](#troubleshooting)
9. [Future Directions](#future-directions)
10. [License](#license)

---

## Project Overview

This project implements a minimal, end-to-end pipeline for ingesting resumes in various formats (PDF, DOCX, or images), extracting both raw text and structured information, converting the text into a dense vector embedding, and storing those embeddings in a FAISS vector index alongside metadata. A search API allows clients to submit a free-text query, which is likewise embedded and compared against the indexed resume embeddings to return the most relevant profiles ranked by similarity.

In summary, the pipeline performs the following steps for each uploaded resume:

1. Accept a file upload (PDF, DOCX, or image).
2. Extract the complete textual content.
3. Identify key fields: skills, location, education level, and broad domain.
4. Create a vector embedding of the entire text using a pre-trained sentence transformer.
5. Index that embedding in FAISS along with the extracted metadata.
6. Expose a search endpoint to retrieve top-K similar profiles based on a query embedding.

This approach demonstrates how to combine simple rule- and NLP-based feature extraction with semantic search in a streamlined FastAPI service.

---

## Key Features

* **Multi-format Resume Ingestion**
  ● PDF text extraction via a standard PDF parser.
  ● DOCX parsing for Word documents.
  ● OCR on images (PNG/JPG) using Tesseract.

* **Field Extraction with spaCy**
  ● **Skills**: Matches a small, predefined set of technical and general skill terms.
  ● **Location**: Uses named-entity recognition to find geopolitical entities.
  ● **Education Level**: Pattern-matches bachelor’s, master’s, and PhD degree mentions.
  ● **Domain Classification**: Simple keyword checks identify whether the resume is more “Engineering,” “Product Management,” or “Other.”

* **Semantic Embedding**
  ● Leverages a pre-trained sentence transformer (a 384-dimensional model) to turn the full resume text into a vector.

* **Vector Store with FAISS**
  ● Uses an in-memory FAISS index for maximum-inner-product search.
  ● Maintains a parallel list of metadata dictionaries (ID, skills, location, degree, domain) corresponding to each indexed vector.

* **Search API**
  ● A query string is transformed into an embedding, which is compared to all existing resume embeddings.
  ● Returns the top K profiles, each with its metadata and a similarity score.

* **Dockerized Deployment**
  ● A single Dockerfile installs system dependencies (compiler toolchain, OCR library), Python packages, and the spaCy language model.
  ● Exposes port 8000 to serve the FastAPI application, making it easy to run anywhere without manual environment setup.

---

## Tech Stack

* **Python 3.9** as the runtime for consistency with the chosen sentence-transformer.
* **FastAPI** for its lightweight, asynchronous server capabilities and automatic interactive documentation.
* **Uvicorn** as the ASGI server to host the FastAPI application.
* **spaCy** (small English model) for named-entity recognition and token-level processing.
* **sentence-transformers** (all-MiniLM-L6-v2) to compute 384-dim embeddings on arbitrary text.
* **FAISS-CPU** for a fast, in-memory vector index supporting similarity search.
* **pdfminer.six** and **python-docx** to extract text from PDF and DOCX files, respectively.
* **pytesseract** (Tesseract OCR) plus **Pillow** for image-based text extraction.
* **Docker** to containerize and isolate all dependencies.

---

## Project Structure

* **Dockerfile**
  Defines a single-stage image starting from a minimal Python 3.9 base. It installs C/C++ build tools and library headers (e.g., libffi, libssl, libxml, libxslt) required to compile certain Python wheels. It then copies `requirements.txt`, installs all Python packages (including spaCy and its language model), and finally copies the application code under an `/app` directory. The container exposes port 8000 and launches Uvicorn to serve the API.

* **requirements.txt**
  Lists all Python dependencies, including FastAPI, Uvicorn, spaCy, sentence-transformers, FAISS-CPU, pdfminer.six, python-docx, pytesseract, Pillow, and their related sub-dependencies.

* **app/embedder.py**
  Contains a small wrapper around the sentence-transformer model to produce a fixed-size (384-dimension) embedding for any input string.

* **app/extractor.py**
  Uses spaCy’s `en_core_web_sm` model to tokenize incoming text and perform:

  * Keyword-based skill matching against tiny sets of “tech” and “general” skills.
  * Named-entity recognition to find the first geopolitical entity (interpreted as “location”).
  * Substring matching to detect common degree terms (Bachelor, Master, PhD).
  * Simple keyword checks to categorize the document’s domain into “Engineering,” “Product Management,” or “Other.”

* **app/processor.py**
  Implements three functions for text extraction:

  1. **PDF** extraction, which uses a well-known library to pull all text from each page.
  2. **DOCX** reading, which iterates through all paragraphs of a Word document.
  3. **Image OCR**, which uses Tesseract via `pytesseract` on a PIL-loaded image.

* **app/vectorstore.py**
  Declares:

  * A FAISS `IndexFlatIP` with dimension 384 for maximum-inner-product similarity.
  * A Python list that holds a metadata dictionary (ID, skills, location, degree, domain) for each indexed vector.
  * A function to add one profile: it appends the new embedding to the FAISS index and stores the metadata in the parallel list.
  * A search function that takes a query embedding, retrieves top-K neighbors by FAISS, and returns the corresponding metadata dictionaries augmented with the similarity score.

* **app/main.py**
  Hosts the FastAPI application.

  * Defines a Pydantic schema `Profile` with fields: `id`, `skills`, `location`, `degree`, and `domain`.
  * Provides one POST endpoint (`/upload/`) which accepts a multipart file, saves it temporarily, determines its extension, and calls the appropriate text extraction function. It then runs all field extractors, generates an embedding of the full text, calls the vectorstore to add the profile, and returns the filled `Profile` JSON.
  * Provides one GET endpoint (`/search/`) which accepts query parameters `q` (free-text query) and `k` (number of results). It embeds `q` using the same sentence-transformer, queries FAISS for top K matches, and returns a list of metadata dictionaries with scores.

---

## Setup & Installation

### Local Environment

1. **Clone the repository**
   Ensure you have a recent version of Git installed. Then run:

   * `git clone https://github.com/your_username/Summarization_proj.git`
   * `cd Summarization_proj`

2. **Create & activate a Python virtual environment**
   It is recommended to use a Python 3.9 environment to match dependency expectations:

   * `python3.9 -m venv venv`
   * On macOS/Linux: `source venv/bin/activate`
   * On Windows (PowerShell): `.\venv\Scripts\Activate.ps1`

3. **Upgrade pip & install dependencies**
   Once the venv is active:

   * `pip install --upgrade pip`
   * `pip install -r requirements.txt`
   * This installs FastAPI, Uvicorn, spaCy, sentence-transformers, FAISS-CPU, pdfminer.six, python-docx, pytesseract, Pillow, and all downstream packages.

4. **Download spaCy’s English model**
   After the libraries are installed, run:

   * `python -m spacy download en_core_web_sm`
     This ensures spaCy can load its small English pipeline for field extraction.

5. **Install Tesseract-OCR (for image processing)**

   * **macOS**: `brew install tesseract`
   * **Ubuntu/Debian**: `sudo apt-get update && sudo apt-get install tesseract-ocr`
   * **Windows**: Download the installer from Tesseract’s GitHub, install it, and add the `tesseract.exe` location to your `PATH`.

6. **Environment check**

   * Confirm `python --version` reports 3.9.x (or at least 3.9).
   * Confirm `pip list` shows all required packages.
   * Confirm `tesseract --version` prints Tesseract’s info.

### Docker Environment

A Dockerfile is provided to simplify deployment and avoid manual installation of system packages. It is a single-stage file that:

* Starts from `python:3.9-slim`.
* Installs essential system tools (`build-essential`, `gcc`, `libffi-dev`, `libssl-dev`, `libxml2-dev`, `libxslt1-dev`, `curl`) to ensure that wheels for packages like spaCy and sentence-transformers can compile dependencies (e.g. BLIS).
* Copies `requirements.txt` into the container, upgrades pip, and installs all Python packages (including Tesseract-OCR via OS packages if needed).
* Downloads spaCy’s small English model during build.
* Copies the `app/` directory containing all application code.
* Exposes port 8000 and sets Uvicorn as the default entrypoint.

#### Building & Running the Docker Container

1. **Navigate to the project root (where Dockerfile lives).**

2. **Build the image**

   ```
   docker build -t summarization_proj .
   ```

   This may take a few minutes since it needs to fetch base images, install OS packages, and compile any C dependencies.

3. **Run the container**

   ```
   docker run -d --name resumepipeline -p 8000:8000 summarization_proj
   ```

   * The container will start in detached mode.
   * Port 8000 inside the container is mapped to port 8000 on your host.
   * Uvicorn will launch the FastAPI app, listening on all interfaces at port 8000.

4. **Verify**

   * Run `docker ps` to confirm the `resumepipeline` container is in “Up” status.
   * If it exited immediately, inspect logs with `docker logs resumepipeline` to debug errors (often related to Python version or missing spaCy model).

5. **Stopping & Removing**

   * To stop: `docker stop resumepipeline`
   * To remove: `docker rm resumepipeline`

---

## API Endpoints & Usage

Once the service is running (whether in a local Python environment or via Docker), it listens on HTTP port 8000 by default. FastAPI automatically generates interactive documentation, which can be accessed at:

* **Swagger UI**: `http://localhost:8000/docs`
* **Redoc**: `http://localhost:8000/redoc`

### Upload Endpoint

* **URL**: `/upload/`

* **Method**: POST

* **Request Body**: A single file (multipart form) with key “file.” The file may be a PDF, a DOCX (or `.doc`), or an image (PNG/JPG).

* **Processing**:

  1. The file is temporarily saved under `/tmp/<original_filename>`.
  2. Based on the file extension, a specialized extractor is invoked:

     * PDF → PDF parser
     * DOCX → Word document reader
     * Image → OCR engine
  3. Field extractors run on the resulting full text:

     * Skill matcher scans token by token for known keywords.
     * NER identifies the first geopolitical entity to assign “location.”
     * A simple substring scan captures any bachelor/master/PhD mention.
     * A heuristic classifier picks “Engineering,” “Product Management,” or “Other.”
  4. The entire extracted text is passed through the sentence-transformer to produce a 384-dimensional vector.
  5. The vector and metadata are added to the FAISS index.
  6. A JSON response is returned containing:

     * `id`: the original filename (used as a unique identifier)
     * `skills`: a list of extracted skill tokens
     * `location`: the first detected geographic entity, if any
     * `degree`: the highest‐level degree mention found, if any
     * `domain`: the broad domain classification

* **Response** (example in prose):
  “A JSON object with fields:
  • id: ‘resume\_jane\_doe.pdf’
  • skills: an array of strings such as \[‘python’, ‘leadership’, ‘aws’]
  • location: e.g. ‘Seattle’ or null if none found
  • degree: e.g. ‘Master’ or null if none found
  • domain: one of ‘Engineering’, ‘Product Management’, or ‘Other’”

### Search Endpoint

* **URL**: `/search/`

* **Method**: GET

* **Query Parameters**:

  * `q` (required): an arbitrary free-text query (e.g., “seeking software engineer with AWS experience”).
  * `k` (optional, default = 5): the number of top results to return.

* **Processing**:

  1. The query string `q` is passed to the same sentence-transformer to generate a 384-dimensional embedding.
  2. FAISS’s inner-product search is invoked on the existing index.
  3. The top K nearest neighbors’ indices and similarity scores are retrieved.
  4. For each matched index, the corresponding metadata dictionary from the parallel list is fetched and augmented with a numeric score.
  5. A JSON array of these K metadata objects is returned, each containing:

     * `id` (string)
     * `skills` (array of strings)
     * `location` (string or null)
     * `degree` (string or null)
     * `domain` (string)
     * `score` (floating-point similarity measure)

* **Response** (example in prose):
  “An array of up to K objects. Each object has an `id` (resume filename), an array of `skills` extracted from that resume, a `location` string or null, a `degree` string or null, a `domain` value, and a `score` (floating number between 0 and 1). The list is sorted in descending order by `score` (highest similarity first).”

---

## Operational Details

### File Ingestion & Text Extraction

* **PDF Extraction**:
  Uses a reliable PDF parsing library that extracts all textual content (including running headers, footers, and multi-column pages). This tends to handle most modern resumes correctly, assuming they are not heavily graphical.

* **DOCX Extraction**:
  Leverages a library that reads each paragraph in the Word document, concatenating them with newline characters. Styles, hidden text, and embedded tables are typically ignored, focusing on paragraph text.

* **Image OCR**:
  Through Tesseract, each uploaded image is opened via Pillow (PIL) and fed into the OCR engine. The returned raw ASCII text often requires some cleanup; here we simply trust Tesseract’s output for downstream extraction.

### Field Extraction

All extracted text is lowercased (for skill matching). A small, hardcoded vocabulary is used:

* **Tech Skills**: e.g. “python,” “java,” “react,” “aws.”
* **General Skills**: e.g. “leadership,” “communication,” “teamwork.”

Each token in the spaCy tokenization is checked against those sets. This approach will only catch exact token matches; it does not handle synonyms or multi-word phrases like “machine learning.”

For **location**, spaCy’s English model tags named entities labeled “GPE” (geopolitical entities). The first GPE encountered is reported.

For **degree**, a list of common degree strings (Bachelor, Master, PhD, B.Sc, M.Sc) is searched as substrings (case-insensitive). The first match is taken.

For **domain**, a simple check of keywords in the full text distinguishes “Product Management” (if terms like “product manager” or “roadmap” appear), “Engineering” (if “scalable” or “API” appear), or falls back to “Other.”

### Embedding & Indexing

* **Embedding Model**:
  The chosen model (“all-MiniLM-L6-v2”) produces 384-dimension vectors optimized for semantic similarity. It is lightweight enough to use in real time but still effective for basic semantic matching.

* **Indexing with FAISS**:
  FAISS’s `IndexFlatIP` is used, which performs inner-product search. Since the sentence-transformer produces L2-normalized embeddings by default (or they can be manually normalized), inner product corresponds to cosine similarity. Each new embedding is appended directly; there is no on-disk persistence by default, so everything is in memory. The parallel Python list keeps metadata so that results can be returned with human-readable fields.

### Similarity Search

When a user submits a query string, it is embedded with the same model. FAISS returns the top K results by highest inner-product score. Each of those results is looked up in the metadata list to return a combined JSON object containing fields and the numerical score.

---

## Troubleshooting

1. **Pydantic Type Annotation Error**

   * If running under Python 3.9 or earlier, you may see an error for annotations like `str | None`. Either upgrade to Python 3.10+ or change those annotations to `Optional[str]` from the `typing` module in the code.

2. **SpaCy Model Not Found**

   * If you see an error indicating `en_core_web_sm` is missing, ensure you ran `python -m spacy download en_core_web_sm`. In a Docker build, this is already included, but if running locally you must do it manually.

3. **Tesseract OCR Failure**

   * If you upload an image and receive an error about Tesseract not found, confirm that the `tesseract` binary is installed and in your system `PATH`. On macOS, use Homebrew; on Debian/Ubuntu, use `apt-get install tesseract-ocr`.

4. **FAISS Import or Build Issues**

   * FAISS-CPU wheels are only available for certain CPU architectures. Make sure you install the correct `faiss-cpu` package. If pip tries to compile FAISS from source, ensure you have a GCC toolchain installed. In Docker, the provided image already installs `build-essential` and `gcc`.

5. **Docker Build Errors Related to “blis” or Other C-Based Wheels**

   * This typically indicates that C build tools (gcc, make, etc.) are missing. Ensure your Dockerfile includes installation of `build-essential` (or equivalent) before running `pip install`. The provided Dockerfile already does so, but if you modified requirements.txt to add a new library that has C dependencies, you may need to install extra OS-level headers (e.g., for `libxml2`, `libxslt`, etc.).

6. **Container Exits Immediately**

   * Inspect logs via `docker logs <container_name>`. Common causes:
     • Syntax error or incompatible Python version (check Pydantic annotations).
     • Missing spaCy model (if you removed the `python -m spacy download` step).
     • Missing Tesseract binary (if you rely on OCR and Tesseract is not installed).

7. **Memory Usage on Large Index**

   * Since FAISS is in memory, adding hundreds or thousands of large resumes will consume significant RAM. For production, consider a persistent solution (e.g., a vector database) rather than pure in-memory FAISS.

---

## Future Directions

1. **Persistent Vector Store**
   • Move from in-memory FAISS to a durable store (e.g., disk-backed FAISS, Pinecone, Qdrant, or Weaviate).
   • Enable persistence across container restarts.

2. **Enhanced Field Extraction**
   • Expand the skill vocabulary or integrate an external taxonomy (CSV/JSON of 10k+ skills).
   • Use a fine-tuned named-entity recognition model to extract educational institutions, companies, dates, and other resume fields.
   • Employ a multi-label classifier for domain or role classification rather than simple keyword checks.

3. **Bulk/Batched Processing**
   • Allow uploading a ZIP file of many resumes to process asynchronously.
   • Implement background tasks (e.g., Celery or FastAPI’s background tasks) with progress tracking and status endpoints.

4. **Authentication & Authorization**
   • Secure both upload and search endpoints behind API keys or OAuth2.
   • Implement role-based access (e.g., administrators can delete or re-index profiles).

5. **Improved Search Ranking & Filtering**
   • Incorporate filters on extracted fields (e.g., “only show profiles with Master’s degree in Seattle”).
   • Combine embedding-based ranking with metadata-based boosting (e.g., boost those in the same geography or skill match).

6. **Testing & CI/CD**
   • Develop unit tests for each component (e.g., extractor functions, embedding, vector store).
   • Add integration tests that spin up a test instance of the FastAPI server and run example upload/search flows.
   • Set up a CI pipeline (GitHub Actions, CircleCI, etc.) to automatically run tests and build the Docker image on each commit.

7. **User Interface**
   • Build a minimal web frontend (e.g., simple React app) that allows interactive file upload, displays extracted fields, and renders search results in a user-friendly table.
   • Provide pagination and sorting of search results, and visual indication of field matches (highlighted skills, location, etc.).

8. **Scalability & Monitoring**
   • Containerize behind a production-grade ASGI server (e.g., Gunicorn + Uvicorn workers, or use Kubernetes for orchestration).
   • Instrument request logging and metrics collection (Prometheus/Grafana) to monitor API performance.
   • Add rate limiting to prevent abuse of upload/search endpoints.

---

## License

This project is released under the **MIT License**. See the accompanying LICENSE file for details.

---

**End of Documentation**
