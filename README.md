# Meta Ads AI Analyzer

A full-stack web application that allows users to upload Meta Ads CSV files and receive AI-powered analysis, insights, and recommendations.

## Features

- **User Authentication**: Secure registration and login system
- **CSV Upload**: Upload Meta Ads CSV files (up to 200MB)
- **AI Analysis**: Powered by OpenAI GPT-4 for comprehensive campaign analysis
- **Queue System**: Handle multiple file uploads with background processing
- **Email Delivery**: Automatic email notifications with results
- **PDF Reports**: Download analysis as professional PDF reports
- **Dashboard**: View analysis history and results in an intuitive interface

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Database for user and analysis data
- **Celery + Redis**: Background task queue for processing
- **OpenAI API**: AI-powered analysis
- **Resend**: Email delivery service
- **ReportLab**: PDF generation

### Frontend
- **React**: UI framework
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **React Dropzone**: File upload interface
- **React Hot Toast**: Notifications

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Utilities
│   │   └── schemas/         # Pydantic schemas
│   ├── config.py            # Configuration
│   ├── main.py              # FastAPI app
│   └── requirements.txt     # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── components/      # React components
    │   ├── pages/          # Page components
    │   ├── services/       # API services
    │   ├── context/        # React context
    │   └── styles/         # CSS files
    └── package.json        # Node dependencies
```

## Setup Instructions

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Fill in the required values:
     ```env
     SECRET_KEY=your-secret-key
     JWT_SECRET_KEY=your-jwt-secret
     DATABASE_URL=postgresql://user:password@localhost:5432/metaads_analyzer
     OPENAI_API_KEY=your-openai-api-key
     RESEND_API_KEY=your-resend-api-key
     FROM_EMAIL=noreply@yourdomain.com
     REDIS_URL=redis://localhost:6379/0
     FRONTEND_URL=http://localhost:3000
     ```

5. **Set up PostgreSQL database**
   - Create a PostgreSQL database named `metaads_analyzer`
   - Update `DATABASE_URL` in `.env`

6. **Run database migrations**
   ```bash
   alembic init alembic
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

7. **Start Redis** (required for Celery)
   ```bash
   redis-server
   ```

8. **Start Celery worker** (in a new terminal)
   ```bash
   celery -A app.services.celery_app worker --loglevel=info
   ```

9. **Start FastAPI server**
   ```bash
   uvicorn main:app --reload
   ```

   Backend will be running at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Update the API URL:
     ```env
     REACT_APP_API_URL=http://localhost:8000
     ```

4. **Start development server**
   ```bash
   npm start
   ```

   Frontend will be running at `http://localhost:3000`

## Deployment

### Deploy Backend to Render

1. **Push code to GitHub**

2. **Create new Web Service on Render**
   - Connect your GitHub repository
   - Use `backend` as the root directory
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Create PostgreSQL database on Render**

4. **Create Redis instance on Render**

5. **Add environment variables** in Render dashboard

6. **Create Celery worker service**
   - Use same repository
   - Start command: `celery -A app.services.celery_app worker --loglevel=info`

### Deploy Frontend to Vercel

1. **Push code to GitHub**

2. **Import project on Vercel**
   - Select your repository
   - Set root directory to `frontend`
   - Framework preset: Create React App

3. **Add environment variable**
   ```
   REACT_APP_API_URL=https://your-backend-url.onrender.com
   ```

4. **Deploy**

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### Upload
- `POST /api/upload/csv` - Upload CSV file
- `GET /api/upload/queue-status` - Get queue status

### Analysis
- `GET /api/analysis/history` - Get analysis history
- `GET /api/analysis/{id}` - Get specific analysis
- `GET /api/analysis/{id}/results` - Get analysis results
- `GET /api/analysis/{id}/download-pdf` - Download PDF report
- `DELETE /api/analysis/{id}` - Delete analysis

## Environment Variables

### Backend
- `SECRET_KEY`: Secret key for Flask sessions
- `JWT_SECRET_KEY`: Secret for JWT tokens
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key
- `RESEND_API_KEY`: Resend email service API key
- `FROM_EMAIL`: Sender email address
- `REDIS_URL`: Redis connection URL
- `FRONTEND_URL`: Frontend URL for CORS

### Frontend
- `REACT_APP_API_URL`: Backend API URL

## Usage

1. **Register/Login**: Create an account or login
2. **Upload CSV**: Navigate to upload page and drag & drop your Meta Ads CSV
3. **Wait for Processing**: File will be queued and processed by AI
4. **View Results**: Check dashboard for completed analyses
5. **Download PDF**: Export your analysis as a PDF report
6. **Email**: Receive results automatically via email

## Meta Ads CSV Format

The application accepts Meta Ads export CSV files with typical columns like:
- Impressions
- Clicks
- Spend
- Conversions
- CTR (Click-through Rate)
- CPC (Cost Per Click)
- Date
- Ad Name / Campaign Name

## AI Analysis Output

The AI generates:
1. **Performance Report**: Key metrics and trends
2. **AI Insights**: 5-7 actionable insights
3. **Next Ad Plan**: Campaign recommendations
4. **30-Day Content Strategy**: Week-by-week plan
5. **Creative Prompts**: 5-10 ad creative ideas
6. **Captions & Hashtags**: Ready-to-use content

## Troubleshooting

### Backend Issues
- Ensure PostgreSQL and Redis are running
- Check all environment variables are set
- Verify OpenAI API key is valid
- Check Celery worker is running for background tasks

### Frontend Issues
- Ensure `REACT_APP_API_URL` points to correct backend
- Clear browser cache if seeing old data
- Check browser console for errors

