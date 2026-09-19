# Epstein Suite

> A searchable transparency database for DOJ Epstein Files, providing public access to documents, emails, flight logs, and AI-powered search.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![PHP Version](https://img.shields.io/badge/PHP-8.4+-purple.svg)](https://www.php.net/)
[![MySQL Version](https://img.shields.io/badge/MySQL-8.0+-blue.svg)](https://www.mysql.com/)

🌐 **Live Site:** [epsteinsuite.com](https://epsteinsuite.com)

---

## 📋 Table of Contents

- [About](#about)
- [Features](#features)
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Database Schema](#database-schema)
- [Data Pipeline](#data-pipeline)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## 🎯 About

Epstein Suite is a web application that makes public records related to the Epstein case searchable and accessible. It combines traditional document management with modern AI-powered features to help researchers, journalists, and the public explore this important dataset.

### Why This Exists

After the DOJ released thousands of pages of Epstein-related documents, they were difficult to search and navigate. This project makes them:

- ✅ **Searchable** - Full-text search across all documents and OCR'd pages
- ✅ **Organized** - Entity extraction (people, organizations, locations)
- ✅ **Interactive** - AI-powered Q&A interface
- ✅ **Transparent** - Open source code, public mission

### Production Site Stats

The live site at [epsteinsuite.com](https://epsteinsuite.com) currently indexes:
- 4,700+ documents from DOJ, FBI Vault, House Oversight
- Millions of OCR'd pages with full-text search
- Thousands of extracted entities (people, organizations, locations)
- Flight logs with geographic mapping
- Email threads with relationship analysis

---

## ✨ Features

### Search & Discovery
- **Full-Text Search** - MySQL FULLTEXT search across documents and OCR'd pages
- **Entity Browser** - Explore people, organizations, and locations
- **Advanced Filters** - Filter by source, date, file type, status
- **Document Timeline** - Chronological view of documents

### AI-Powered Features
- **Ask AI** - Natural language Q&A powered by OpenAI GPT-5-nano
- **Document Summaries** - AI-generated summaries for complex documents
- **Entity Extraction** - Automatic identification of key people/organizations
- **Semantic Search** - Vector embeddings for similarity-based search

### Specialized Views
- **Flight Logs** - Searchable flight manifests with map visualization
- **Email Client** - Thread view for email collections
- **Photo Gallery** - Media browser with metadata
- **Network Graphs** - Entity relationship visualizations with D3.js

### Technical Features
- **File-Based Caching** - Fast page loads with intelligent cache invalidation
- **Responsive Design** - Mobile-first UI with TailwindCSS
- **Admin Dashboard** - Operations console for monitoring
- **API Endpoints** - JSON APIs for integrations

---

## 📸 Screenshots

> **Note:** Add screenshots of your live site here once you've added them to the repo

![Homepage Search](docs/images/homepage.png)
![Document View](docs/images/document-view.png)
![AI Chat Interface](docs/images/ai-chat.png)
![Flight Log Map](docs/images/flight-map.png)

---

## 🛠️ Tech Stack

### Backend
- **PHP 8.4** - Strict typing, PSR-12 coding standard
- **MySQL 8.0** - InnoDB engine, FULLTEXT indexes, utf8mb4
- **Apache/PHP-FPM** - Production web server

### Frontend
- **TailwindCSS 3.4** - Utility-first CSS framework
- **Vanilla JavaScript** - No framework dependencies
- **D3.js** - Network graph visualizations
- **Leaflet.js** - Flight log mapping

### AI/ML
- **OpenAI GPT-5-nano** - Document summaries, entity extraction, Q&A
- **text-embedding-3-small** - Vector embeddings for semantic search
- **PHP Vector Search** - Cosine similarity computed in PHP

### Architecture
- **Flat PHP Routing** - No framework, direct file-to-URL mapping
- **PDO Singleton** - Centralized database access
- **File-Based Cache** - Simple, fast caching layer

---

## 🚀 Getting Started

### Prerequisites

- PHP 8.4 or higher
- MySQL 8.0 or higher
- Git
- (Optional) OpenAI API key for AI features

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/epstein-suite.git
   cd epstein-suite
   ```

2. **Create database**
   ```bash
   mysql -u root -p
   CREATE DATABASE epstein_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   exit
   ```

3. **Import database schema**
   ```bash
   mysql -u root -p epstein_db < config/schema.sql
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   nano .env
   ```

   Minimum required settings:
   ```ini
   DB_HOST=localhost
   DB_NAME=epstein_db
   DB_USERNAME=root
   DB_PASSWORD=your_password
   ADMIN_PASSWORD=your_admin_password
   ```

5. **Start development server**
   ```bash
   php -S localhost:8000
   ```

6. **Visit http://localhost:8000**

### Development with Sample Data

The production database is not included. For local development, you can:

**Option A: Work with empty database**
- Good for UI/UX development
- Test edge cases with no data

**Option B: Create test data**
```sql
-- Create sample documents
INSERT INTO documents (title, description, status, file_url, source, created_at) VALUES
('Sample Document 1', 'A test document for development', 'processed', 'https://example.com/doc1.pdf', 'TEST', NOW()),
('Sample Document 2', 'Another test document', 'processed', 'https://example.com/doc2.pdf', 'TEST', NOW());

-- Create sample entities
INSERT INTO entities (name, type, created_at) VALUES
('John Doe', 'PERSON', NOW()),
('Acme Corporation', 'ORG', NOW()),
('New York', 'LOCATION', NOW());

-- Link entities to documents
INSERT INTO document_entities (document_id, entity_id) VALUES
(1, 1), (1, 2), (2, 1), (2, 3);
```

### Production Deployment

For production deployment:

1. Configure `.env` with production credentials
2. Set up Apache/Nginx with PHP-FPM
3. Enable HTTPS with Let's Encrypt
4. Configure file permissions:
   ```bash
   chmod 755 *.php
   chmod 775 cache/
   ```
5. Set up admin authentication (HTTP Basic Auth)
6. Configure caching headers in `.htaccess`

See `TECH.md` for detailed production setup (if you include it).

---

## 🗄️ Database Schema

The application uses these core tables:

### Documents (`documents`)
Main document metadata with full lifecycle tracking:
```sql
- id, title, description, file_url, source
- status (pending → downloaded → processed)
- ai_summary, created_at, updated_at
```

### Pages (`pages`)
OCR text per page with FULLTEXT index:
```sql
- document_id, page_number, ocr_text
- FULLTEXT INDEX(ocr_text)
```

### Entities (`entities`)
People, organizations, locations:
```sql
- id, name, type (PERSON/ORG/LOCATION)
- created_at
```

### Relationships (`document_entities`)
Many-to-many document-entity relationships:
```sql
- document_id, entity_id
```

### Other Tables
- `emails` - Email threads (FULLTEXT indexed)
- `flight_logs` - Flight manifest records
- `passengers` - Flight passenger details
- `ai_sessions` - AI chat session tracking
- `ai_messages` - AI conversation history
- `ai_citations` - Document citations in AI responses

See `config/schema.sql` for complete schema definition.

---

## 🔄 Data Pipeline

**Note:** The data ingestion pipeline is **not included** in this open source release.

The production site uses a proprietary pipeline that:
1. Discovers documents from DOJ, FBI Vault, and House Oversight sources
2. Downloads and OCRs PDF documents (pdf2image + Tesseract)
3. Generates AI summaries and extracts entities (OpenAI GPT-5-nano)
4. Analyzes flight logs for significance scoring
5. Generates vector embeddings for semantic search

To use this application with your own data, you'll need to:
- Populate the `documents` table with your dataset
- Run your own OCR/processing pipeline
- Generate AI summaries and entity extractions
- Follow the database schema in `config/schema.sql`

The web application works with any dataset that follows the schema structure.

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Start

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test locally: `php -S localhost:8000`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Areas We Need Help

- 🎨 UI/UX improvements (mobile, accessibility, dark mode)
- 🔍 Search enhancements (better filters, faceted search)
- ⚡ Performance optimizations
- 📊 Data visualizations
- 🧪 Automated testing (we have none!)
- 📚 Documentation improvements

### Code Standards

- Follow PSR-12 coding standard
- Use strict typing: `declare(strict_types=1);`
- Always use PDO prepared statements
- Test your changes locally

---

## 📜 License

This project is licensed under the **GNU Affero General Public License v3.0** (AGPL-3.0).

This means:
- ✅ You can use, modify, and distribute this code
- ✅ If you run a modified version as a web service, you must release your source code
- ✅ All derivative works must also be AGPL-3.0 licensed
- ✅ You must credit the original project

**Data Pipeline Exception:** The data ingestion pipeline, scrapers, and automation scripts are proprietary and not included in this release.

See [LICENSE](LICENSE) for full details.

---

## 👤 Author

**Kevin Champlin**
- Website: [kevinchamplin.com](https://kevinchamplin.com)
- Email: info@epsteinsuite.com
- Production Site: [epsteinsuite.com](https://epsteinsuite.com)

---

## 🙏 Acknowledgments

- DOJ, FBI, and House Oversight for releasing these public records
- OpenAI for GPT-5 and embedding APIs
- The open source community for tools like TailwindCSS, D3.js, and Leaflet.js
- Tesseract OCR project
- Everyone committed to transparency and accountability

---

## 📞 Support

- **Bug Reports:** [Open an issue](https://github.com/YOUR_USERNAME/epstein-suite/issues)
- **Feature Requests:** [Open an issue](https://github.com/YOUR_USERNAME/epstein-suite/issues) with [FEATURE] tag
- **Security Issues:** Email info@epsteinsuite.com privately
- **General Questions:** [GitHub Discussions](https://github.com/YOUR_USERNAME/epstein-suite/discussions)

---

## 🔒 Privacy & Safety

This project is designed with strict privacy protections:
- AI prompts explicitly forbid un-redacting victim names
- All data sources are already-public records
- Focus is on investigative leads, not victim identification
- Victim privacy is paramount

---

## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub!

---

**Built for transparency. Designed for accountability.**
