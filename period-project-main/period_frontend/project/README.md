# Menstrual Cycle Irregularity Detection System

A complete React.js frontend application for detecting menstrual cycle irregularities using AI-powered predictions.

## Features

- **User Authentication**: Login and Signup pages with form validation
- **Dashboard**: Central hub with quick access to all features
- **AI Prediction Form**: Comprehensive form with 12 health metrics for cycle analysis
- **Results Display**: Beautiful visualization of predictions with risk levels and detected irregularities
- **Protected Routes**: Secure access to authenticated pages
- **Responsive Design**: Fully responsive UI using TailwindCSS

## Tech Stack

- **React 18** - UI library
- **React Router** - Navigation and routing
- **Axios** - HTTP client for API calls
- **TailwindCSS v3** - Utility-first CSS framework
- **React Scripts** - Build tooling

## Folder Structure

```
project/
├── src/
│   ├── api/
│   │   └── prediction.js          # Axios API configuration
│   ├── components/
│   │   └── ProtectedRoute.jsx     # Route protection component
│   ├── context/
│   │   └── AuthContext.jsx        # Authentication state management
│   ├── pages/
│   │   ├── Login.jsx              # Login page
│   │   ├── Signup.jsx             # Signup page
│   │   ├── Dashboard.jsx          # Dashboard page
│   │   ├── PredictForm.jsx        # Prediction form with 12 inputs
│   │   └── Results.jsx            # Results display page
│   ├── App.js                     # Main app component with routing
│   ├── index.js                   # Entry point
│   └── style.css                  # Global styles with Tailwind
├── public/
│   └── index.html                 # HTML template
├── tailwind.config.js             # Tailwind configuration
├── postcss.config.js              # PostCSS configuration
└── package.json                   # Dependencies and scripts
```

## Setup Instructions

### Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)
- Backend API running at `http://localhost:8000`

### Installation

1. **Clone or download the project**

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```
   The app will open at `http://localhost:3000`

4. **Build for production:**
   ```bash
   npm run build
   ```

## API Configuration

The frontend is configured to connect to your backend at `http://localhost:8000`.

### Changing the Backend URL

To update the API URL, edit `src/api/prediction.js`:

```javascript
const API_BASE_URL = 'http://your-new-backend-url:port';
```

Or use the utility function:

```javascript
import { updateApiBaseUrl } from './api/prediction';

updateApiBaseUrl('http://your-new-backend-url:port');
```

## API Integration

### Expected Backend Response Format

The backend should return predictions in this format:

```json
{
  "prediction": 1,
  "probability": 0.82,
  "irregularity_types": [
    "Oligomenorrhea (Long cycles)",
    "Irregular Cycle Pattern"
  ]
}
```

### Input Fields (12 AI Features)

The prediction form collects these metrics:

1. **age** - Age in years (10-60)
2. **bmi** - Body Mass Index (10-50)
3. **life_stage** - Life stage (reproductive/perimenopausal/postmenopausal/adolescent)
4. **tracking_duration_months** - Tracking duration in months (1-120)
5. **pain_score** - Pain score (0-10)
6. **avg_cycle_length** - Average cycle length in days (15-60)
7. **cycle_length_variation** - Cycle length variation in days (0-30)
8. **avg_bleeding_days** - Average bleeding days (1-15)
9. **bleeding_volume_score** - Bleeding volume score (1-5)
10. **intermenstrual_episodes** - Intermenstrual episodes (0-20)
11. **cycle_variation_coeff** - Cycle variation coefficient (0-1)
12. **pattern_disruption_score** - Pattern disruption score (0-10)

## Pages Overview

### 1. Login Page (`/login`)
- Email and password authentication
- Form validation
- Redirects to dashboard on success

### 2. Signup Page (`/signup`)
- New user registration
- Name, email, password, and confirm password
- Redirects to login after successful signup

### 3. Dashboard (`/dashboard`)
- Protected route (requires authentication)
- Welcome message
- Two main actions:
  - Predict Irregularity
  - View Previous Reports (dummy)

### 4. Prediction Form (`/predict`)
- Protected route
- 12 input fields for health metrics
- Real-time validation
- Submits to backend API
- Navigates to results page

### 5. Results Page (`/results`)
- Protected route
- Displays prediction (Regular/Irregular)
- Shows probability percentage
- Risk level indicator (Low/Medium/High)
- List of detected irregularity types
- Options to create new prediction or return to dashboard

## Available Scripts

### `npm start`
Runs the app in development mode at [http://localhost:3000](http://localhost:3000)

### `npm run build`
Builds the app for production to the `build` folder

### `npm test`
Launches the test runner

### `npm run eject`
**Note: this is a one-way operation!** Ejects from Create React App

## Authentication

The app uses a simple localStorage-based authentication system (dummy authentication for demonstration purposes). In production, replace this with a proper backend authentication system.

## Styling

The application uses TailwindCSS with a custom pink/rose color scheme. The design is:
- Clean and modern
- Fully responsive
- Accessible
- Professional-looking

## Backend Requirements

Your backend must:
1. Run on `http://localhost:8000` (or update the API_BASE_URL)
2. Accept POST requests to `/predict` endpoint
3. Return JSON responses in the expected format

## Troubleshooting

### Backend Connection Error
If you see "Unable to connect to the prediction server":
- Ensure your backend is running at `http://localhost:8000`
- Check that CORS is properly configured on the backend
- Verify the backend `/predict` endpoint is accessible

### Build Errors
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Clear cache: `npm cache clean --force`

### TailwindCSS Not Working
- Ensure `tailwind.config.js` has the correct content paths
- Verify `@tailwind` directives are in `src/style.css`

## License

This project is created for educational purposes as a final-year project.

## Support

For issues related to the frontend, check the browser console for errors.
For backend integration issues, verify the API endpoint and response format.
