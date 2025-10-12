# Pandas Bot Miniapp

A React + Vite based Telegram mini app for interactive Python learning with pandas.

## Overview

This miniapp provides an interactive learning environment for Python and pandas within Telegram. Users can practice coding, submit solutions, and receive instant feedback.

## Features

- Interactive Monaco code editor with Python syntax highlighting
- Real-time code execution and testing
- Progress tracking and task management
- Responsive design optimized for mobile devices
- Integration with Telegram Web App SDK

## Tech Stack

- **React 19** - UI framework
- **Vite** - Build tool and dev server
- **Monaco Editor** - Code editor component
- **Pyodide** - Python runtime in the browser
- **Telegram Web App SDK** - Telegram integration
- **Axios** - HTTP client for API requests

## Development

### Prerequisites

- Node.js 16+ and npm
- Access to Django backend API

### Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The dev server will start at `http://localhost:5173`

### Environment Variables

Create `.env.production` for production builds:

```env
VITE_API_URL=/api
```

## Building for Production

```bash
# Build the application
npm run build

# Preview production build locally
npm preview
```

Build output is generated in the `dist/` directory.

## Deployment

See [MINIAPP_DEPLOYMENT.md](../docs/MINIAPP_DEPLOYMENT.md) for complete deployment instructions.

Quick deployment:
```bash
# From project root
./scripts/deploy_miniapp.sh
```

## Project Structure

```
webapp/
├── src/
│   ├── components/        # React components
│   │   └── PythonTask.jsx # Main task interface
│   ├── config.js          # Configuration
│   └── main.jsx           # Application entry point
├── public/                # Static assets
├── dist/                  # Production build output
└── package.json           # Dependencies and scripts
```

## API Integration

The miniapp communicates with the Django backend through these endpoints:

- `GET /api/code/task/?user_id={id}` - Fetch a task
- `POST /api/code/submit/` - Submit code solution

API base URL is configured via `VITE_API_URL` environment variable.

## Nginx Configuration

The miniapp is served through nginx with:
- Static file serving from `/opt/pandas_bot/webapp/dist`
- SPA routing with fallback to `index.html`
- API proxy to Django backend
- Gzip compression for assets
- Long-term caching for JS/CSS bundles

Current deployment: https://pandadev.taras.rocks/

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Troubleshooting

### Blank page after deployment

Check browser console for errors and verify:
1. API endpoint configuration
2. Django backend is running
3. Nginx configuration is correct

### API requests failing

Verify:
1. Backend URL in config.js
2. Nginx proxy configuration
3. CORS settings in Django

## Contributing

When making changes:
1. Test locally with `npm run dev`
2. Build and test production bundle
3. Deploy using the deployment script
4. Verify in Telegram miniapp

## Related Documentation

- [Miniapp Deployment Guide](../docs/MINIAPP_DEPLOYMENT.md)
- [VPS Quick Check](../docs/VPS_QUICK_CHECK.md)
