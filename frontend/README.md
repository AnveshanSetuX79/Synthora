# LocalAI Leads - Frontend

React + Vite frontend application for the LocalAI Leads platform.

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **TanStack Query** - Server state management
- **Zustand** - Client state management
- **Tailwind CSS** - Utility-first CSS framework

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── components/     # Reusable UI components
├── pages/          # Page components
├── services/       # API services
├── store/          # Zustand stores
├── hooks/          # Custom React hooks
├── utils/          # Utility functions
├── App.jsx         # Main app component with routing
├── main.jsx        # Entry point
└── index.css       # Global styles
```

## Environment Variables

Create a `.env` file in the root directory:

```
VITE_API_URL=http://localhost:8000
```

## Features

- Protected routes with authentication
- Role-based access control
- JWT token management
- API client with interceptors
- Persistent auth state
- Responsive design with Tailwind CSS

## Development

The dev server runs on `http://localhost:3000` and proxies API requests to the backend at `http://localhost:8000`.
