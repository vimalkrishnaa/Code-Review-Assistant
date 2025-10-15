# Code Review Assistant

A comprehensive web application that automatically reviews source code using AI/LLM technology. Built with FastAPI backend and React frontend, featuring advanced code analysis, PDF report generation, and a complete dashboard with review history.

## 🚀 Features

### 🤖 AI-Powered Code Analysis
- **Multi-Language Support**: Python, JavaScript, Java, C++, C, TypeScript, Go, Rust, PHP, Ruby, and text files
- **Google Gemini Integration**: Advanced AI analysis using Google's Gemini API
- **Comprehensive Reviews**: Readability, modularity, bug detection, and improvement suggestions
- **Line-by-Line Analysis**: Detailed issue identification with specific line numbers
- **Severity Classification**: Critical, High, Medium, and Low priority issues

### 📊 Advanced Reporting
- **Structured JSON Reports**: Detailed analysis with quality metrics
- **PDF Report Generation**: Professional PDF reports for documentation and sharing
- **Quality Scoring**: Overall score calculation (1-10) based on code quality
- **Issue Categorization**: Grouped by severity and type for easy understanding

### 📈 Dashboard & Analytics
- **Review History**: Complete history of all code reviews performed
- **Statistics Dashboard**: Total reviews, average scores, issue counts, and trends
- **Language Distribution**: Visual breakdown of reviews by programming language
- **Real-time Updates**: Dashboard refreshes automatically with new reviews

### 🗄️ Data Persistence
- **SQLite Database**: All reviews stored locally for future reference
- **Review Management**: View, search, and manage past reviews
- **Data Analytics**: Historical trends and performance metrics
- **Export Capabilities**: Download individual reviews or generate reports

### 🎨 Modern UI/UX
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Dark Mode Support**: Built-in dark/light theme toggle
- **Smooth Animations**: Powered by Framer Motion
- **Tab Navigation**: Easy switching between upload and dashboard views
- **Real-time Status**: Live server connection monitoring

## 🏗️ Project Structure

```
code-review-assistant/
├── backend/                     # FastAPI backend
│   ├── main.py                 # Main application file
│   ├── config.env              # Environment variables
│   ├── requirements.txt        # Python dependencies
│   ├── reviews.db              # SQLite database (auto-generated)
│   ├── reports/                # Generated PDF reports
│   ├── database/               # Database configuration
│   │   ├── __init__.py
│   │   └── db.py              # SQLAlchemy setup
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── review_model.py    # Pydantic models
│   │   └── db_models.py       # SQLAlchemy models
│   ├── routes/                 # API routes
│   │   ├── __init__.py
│   │   ├── review.py          # Code review endpoints
│   │   └── history.py         # History management endpoints
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── llm_review.py      # AI review service
│   │   └── report_formatter.py # Report formatting
│   └── utils/                  # Utilities
│       ├── __init__.py
│       └── pdf_generator.py   # PDF generation
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── App.jsx            # Main React component
│   │   ├── main.jsx           # React entry point
│   │   ├── index.css          # Global styles with TailwindCSS
│   │   └── lib/
│   │       └── utils.js       # Utility functions
│   ├── index.html             # HTML template
│   ├── package.json           # Node.js dependencies
│   ├── vite.config.js         # Vite configuration
│   ├── tailwind.config.js     # TailwindCSS configuration
│   ├── postcss.config.js      # PostCSS configuration
│   └── components.json        # shadcn/ui configuration
└── README.md                  # This file
```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **Google Gemini**: Advanced AI/LLM integration for code analysis
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **SQLite**: Lightweight, file-based database
- **ReportLab**: PDF generation library
- **Pydantic**: Data validation and settings management
- **Python-multipart**: File upload support
- **Aiofiles**: Async file operations

### Frontend
- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **shadcn/ui**: Beautiful, accessible UI components
- **Framer Motion**: Smooth animations
- **Lucide React**: Beautiful icons
- **Axios**: HTTP client for API calls

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (recommended: Python 3.11+)
- **Node.js 18+** (recommended: Node.js 20+)
- **npm** or **yarn**
- **Google Gemini API Key** (free tier available)

### 1. Clone and Setup

```bash
# Navigate to the project directory
cd code-review-assistant

# Setup backend
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Setup environment variables
cp env.example config.env
# Edit config.env file with your Google Gemini API key

# Setup frontend
cd ../frontend
npm install
```

### 2. Configure Environment

Edit `backend/config.env`:

```env
# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Server Configuration
HOST=127.0.0.1
PORT=8002
DEBUG=True

# LLM Configuration
DEFAULT_MODEL=gemini-1.5-flash
MAX_FILE_SIZE_KB=200
```

### 3. Run the Application

#### Start Backend Server
```bash
cd backend
# Make sure virtual environment is activated
python -m uvicorn main:app --host 127.0.0.1 --port 8002 --reload
```
The backend will be available at: `http://localhost:8002`

#### Start Frontend Development Server
```bash
cd frontend
npm run dev
```
The frontend will be available at: `http://localhost:5173`

### 4. Verify Setup

1. Open your browser and go to `http://localhost:5173`
2. You should see the "Code Review Assistant" interface with two tabs
3. The server status should show "Connected to server" with a green checkmark
4. Test the API directly at `http://localhost:8002/ping`

## 📡 API Endpoints

### Health & Info
- **GET** `/ping` - Returns server status
- **GET** `/` - Returns API information and available endpoints

### Code Review
- **POST** `/api/upload` - Upload and review a single code file
- **POST** `/api/upload-multiple` - Upload and review multiple files
- **GET** `/api/supported-formats` - Get list of supported file formats
- **GET** `/api/health` - Review service health check

### History Management
- **GET** `/api/history/` - Get paginated review history
- **GET** `/api/history/{id}` - Get specific review by ID
- **DELETE** `/api/history/{id}` - Delete a review record
- **GET** `/api/history/stats/summary` - Get review statistics

### PDF Reports
- **GET** `/api/download-pdf/{filename}` - Download generated PDF report

### Example API Usage

#### Upload a file for review:
```bash
curl -X POST "http://localhost:8002/api/upload" \
  -F "file=@your_code.py" \
  -F "export_pdf=true"
```

#### Get review history:
```bash
curl -X GET "http://localhost:8002/api/history/"
```

## 🎯 Usage Guide

### 1. Upload & Review Code
1. Navigate to the "Upload & Review" tab
2. Click "Choose File" and select your code file
3. Optionally check "Generate PDF report" for a downloadable PDF
4. Click "Review Code" to start the analysis
5. View the detailed review results with scores, issues, and suggestions

### 2. View Dashboard
1. Click the "Dashboard" tab
2. View statistics cards showing:
   - Total reviews performed
   - Average quality score
   - Total issues found
   - Recent review activity
3. See language distribution of your reviews
4. Browse complete review history with filtering options

### 3. Review Analysis Features
- **Overall Score**: 1-10 quality rating
- **Detailed Analysis**: Readability, modularity, and bug assessment
- **Issue Breakdown**: Categorized by severity (Critical, High, Medium, Low)
- **Improvement Suggestions**: Actionable recommendations
- **Quality Metrics**: Complexity and maintainability scores

## 🔧 Configuration

### Backend Environment Variables

The `config.env` file supports the following variables:

```env
# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Server Configuration
HOST=127.0.0.1
PORT=8002
DEBUG=True

# LLM Configuration
DEFAULT_MODEL=gemini-1.5-flash
MAX_FILE_SIZE_KB=200
```

### Frontend Configuration

The frontend connects to the backend at `http://localhost:8002`. You can modify the `API_BASE_URL` in `src/App.jsx` if needed.

## 🗄️ Database Schema

The application uses SQLite with the following main table:

### ReviewRecord
- `id`: Primary key
- `filename`: Original filename
- `review_json`: Complete review data (JSON)
- `overall_score`: Quality score (1-10)
- `language`: Detected programming language
- `file_size`: File size in MB
- `processing_time`: Analysis time in seconds
- `total_issues`: Total number of issues found
- `critical_issues`, `high_issues`, `medium_issues`, `low_issues`: Issue counts by severity
- `created_at`, `updated_at`: Timestamps

## 🎨 UI Components

The application features a modern, responsive interface with:

- **Tab Navigation**: Easy switching between upload and dashboard
- **Statistics Cards**: Visual metrics with icons and color coding
- **Review History**: Sortable list with detailed information
- **File Upload**: Drag-and-drop interface with progress indicators
- **Dark Mode**: Automatic theme detection with manual toggle
- **Responsive Design**: Optimized for all screen sizes
- **Loading States**: Smooth loading animations and indicators

## 🚀 Production Deployment

### Backend Deployment

1. **Set up production server** (Ubuntu, CentOS, etc.)
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables** for production
4. **Use production ASGI server**:
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```
5. **Set up reverse proxy** with Nginx
6. **Configure SSL** for secure connections

### Frontend Deployment

1. **Build production bundle**:
   ```bash
   cd frontend
   npm run build
   ```
2. **Deploy to static hosting** (Vercel, Netlify, etc.)
3. **Update API URL** in production configuration
4. **Configure environment variables** for production backend

### Docker Deployment (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8002:8002"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./backend/reports:/app/reports
      - ./backend/reviews.db:/app/reviews.db

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
```

## 🔒 Security Considerations

- **API Key Protection**: Store API keys in environment variables
- **File Upload Limits**: Configured file size and type restrictions
- **CORS Configuration**: Properly configured for production domains
- **Input Validation**: All inputs validated using Pydantic models
- **Error Handling**: Graceful error handling without exposing sensitive data

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Manual Testing
1. Test file upload with various file types
2. Verify PDF generation works correctly
3. Check dashboard updates with new reviews
4. Test error handling with invalid files
5. Verify responsive design on different devices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m 'Add new feature'`
5. Push to the branch: `git push origin feature/new-feature`
6. Submit a pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React code
- Write tests for new features
- Update documentation for API changes
- Ensure responsive design for UI changes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **CORS Errors**: 
   - Ensure backend is running on correct port
   - Check CORS configuration in `main.py`

2. **API Key Issues**:
   - Verify Gemini API key is correctly set in `config.env`
   - Check API key has sufficient quota

3. **Database Issues**:
   - Ensure SQLite database file is writable
   - Check database initialization on startup

4. **File Upload Issues**:
   - Verify file size is under 200KB limit
   - Check file extension is supported
   - Ensure file is valid UTF-8 encoded

5. **PDF Generation Issues**:
   - Check `reports/` directory exists and is writable
   - Verify ReportLab is properly installed

### Getting Help

- Check browser console for frontend errors
- Check backend logs for API errors
- Verify all dependencies are installed correctly
- Ensure both servers are running simultaneously
- Check network connectivity between frontend and backend

### Performance Optimization

- **Database**: Consider indexing frequently queried fields
- **File Processing**: Implement file caching for repeated uploads
- **API Responses**: Add response caching for static data
- **Frontend**: Implement lazy loading for large review histories

## 🎉 Features Roadmap

### Planned Enhancements
- [ ] User authentication and multi-user support
- [ ] Advanced filtering and search in dashboard
- [ ] Code comparison between different versions
- [ ] Integration with popular code repositories (GitHub, GitLab)
- [ ] Custom review templates and rules
- [ ] Team collaboration features
- [ ] Advanced analytics and reporting
- [ ] Mobile app development

### Recent Updates
- ✅ Complete database integration with SQLite
- ✅ PDF report generation
- ✅ Comprehensive dashboard with analytics
- ✅ Google Gemini AI integration
- ✅ Enhanced UI with tab navigation
- ✅ Review history management
- ✅ Quality metrics and scoring system

---

**Happy Coding! 🎉**

*Built with ❤️ using FastAPI, React, and Google Gemini AI*