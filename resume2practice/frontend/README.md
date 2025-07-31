# Resume2Practice Frontend

A Flask-based web application that provides an intuitive interface for the Resume2Practice AI-powered career analysis platform.

## Features

- **Modern UI/UX**: Clean, responsive design with Tailwind CSS
- **File Upload Support**: Upload resume and job descriptions as PDF files or paste text directly
- **Interactive Analysis**: Step-by-step process with dynamic question handling
- **Rich Results Display**: Comprehensive scorecard and practice task visualization
- **Real-time Feedback**: Loading states, error handling, and success notifications

## Project Structure

```
frontend/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── templates/            # Jinja2 templates
│   ├── base.html         # Base template with common elements
│   ├── index.html        # Main page for resume/job input
│   ├── results.html      # Results display page
│   └── error.html        # Error page template
└── uploads/              # Directory for temporary file uploads
```

## Setup and Installation

### Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   ```bash
   export FLASK_ENV=development
   export FLASK_DEBUG=true
   export BACKEND_URL=http://localhost:5000
   export SECRET_KEY=your-secret-key
   ```

3. **Run the Application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:8888`

### Docker Development

1. **Build and Run with Docker Compose**
   ```bash
   # From the project root
   docker-compose up --build
   ```

2. **Individual Container Build**
   ```bash
   # Development build
   docker build --target dev -t resume2practice-frontend:dev .
   
   # Production build
   docker build --target prod -t resume2practice-frontend:prod .
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `production` |
| `FLASK_DEBUG` | Enable debug mode | `false` |
| `BACKEND_URL` | Backend API URL | `http://backend:5000` |
| `SECRET_KEY` | Flask session secret key | Required |

### Backend Integration

The frontend communicates with the backend through two main endpoints:

1. **`/analyze`** - Initial analysis with resume and job description
2. **`/resume`** - Submit answers to follow-up questions

## User Flow

1. **Input Phase**: Users provide resume and job description (text or PDF)
2. **Analysis Phase**: Backend processes input and returns clarifying questions
3. **Questions Phase**: Users answer additional questions (optional)
4. **Results Phase**: Display comprehensive scorecard and practice tasks

## UI Components

### Main Page (`index.html`)
- Tabbed interface for text input vs file upload
- Drag-and-drop file upload areas
- Form validation and error handling
- Smooth transitions between sections

### Results Page (`results.html`)
- **Scorecard Section**: Visual readiness score, gap analysis, strengths/weaknesses
- **Practice Tasks**: Card-based layout with expandable task data
- **Print Support**: Clean print stylesheet for reports

### Base Template (`base.html`)
- Responsive navigation
- Loading modals and toast notifications
- Consistent styling and animations
- Error handling utilities

## Styling and Design

- **Framework**: Tailwind CSS for utility-first styling
- **Icons**: Font Awesome for consistent iconography
- **Animations**: CSS transitions and custom animations
- **Responsive**: Mobile-first design approach
- **Theme**: Gradient-based color scheme with blue/purple palette

## API Integration

### Request Handling
```javascript
// Example: Submitting initial analysis
fetch('/analyze', {
    method: 'POST',
    body: formData  // FormData with files and text
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        showQuestions(data.questions);
    }
});
```

### Session Management
- Uses Flask sessions to maintain state between requests
- Stores thread_id, questions data, and results
- Automatic cleanup on new analysis

## Error Handling

- **Client-side**: Form validation, network error handling
- **Server-side**: Backend communication error handling
- **User Feedback**: Toast notifications and error pages
- **Logging**: Comprehensive logging for debugging

## Security Considerations

- **File Upload**: Limited to PDF files only
- **Session Security**: Secure session configuration
- **Input Validation**: Both client and server-side validation
- **CORS**: Proper CORS configuration for backend communication

## Development Tips

1. **Hot Reload**: Set `FLASK_DEBUG=true` for automatic reloading
2. **Template Changes**: Templates reload automatically in debug mode
3. **Static Files**: CSS/JS changes require browser refresh
4. **Backend Communication**: Ensure backend is running on correct port

## Production Deployment

1. **Environment Setup**
   ```bash
   export FLASK_ENV=production
   export FLASK_DEBUG=false
   export SECRET_KEY=secure-random-key
   ```

2. **Security Hardening**
   - Use strong secret keys
   - Configure proper CORS origins
   - Set up SSL/TLS encryption
   - Implement rate limiting

3. **Performance Optimization**
   - Use production WSGI server (gunicorn)
   - Enable static file caching
   - Optimize image and asset loading

## Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Check `BACKEND_URL` environment variable
   - Ensure backend service is running
   - Verify network connectivity

2. **File Upload Errors**
   - Check file size limits
   - Verify PDF file format
   - Ensure uploads directory exists

3. **Session Issues**
   - Check `SECRET_KEY` configuration
   - Clear browser cookies
   - Restart application

### Debug Mode

Enable debug mode for detailed error messages:
```bash
export FLASK_DEBUG=true
python app.py
```

## Contributing

1. Follow the existing code structure and naming conventions
2. Add appropriate error handling for new features
3. Update templates with consistent styling
4. Test both file upload and text input methods
5. Ensure responsive design works on mobile devices

## License

This project is part of the Resume2Practice platform. Please refer to the main project license.