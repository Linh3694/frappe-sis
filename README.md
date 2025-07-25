# Parent Portal Backend

Wellspring's Parent Portal app is a Frappe app that provides backend API and services for the Parent Portal system. It is designed to be used in conjunction with the Wellspring School Management System.

**Note**: The frontend has been separated into a standalone repository for independent deployment. See: [frappe-pp](https://github.com/Linh3694/frappe-pp)

## Features

- **Student Information System Integration**: Access to student data, grades, attendance
- **Communication APIs**: Messaging system between parents and teachers
- **Attendance Management**: Real-time attendance tracking and reporting
- **Academic Calendar**: School events and important dates
- **Document Management**: Access to student documents and reports
- **Multi-language Support**: Vietnamese and English interface

## API Documentation

This app provides RESTful APIs for the frontend application:

- `/api/method/parent_portal.api.*` - Custom API methods
- `/api/resource/*` - Frappe REST API resources
- Authentication via Frappe session management
- CORS support for cross-origin requests

## Dev Setup

### Setting up Docker Container

Clone `frappe-docker`:

```bash
git clone https://github.com/frappe/frappe_docker.git
cd frappe_docker
cp -R devcontainer-example .devcontainer
cp -R development/vscode-example development/.vscode
```

Open VSCode `code .` and choose to reopen in container. The Docker container will be built.

### Setting up Frappe Bench

```bash
bench init --skip-redis-config-generation --frappe-branch version-15 frappe-bench
cd frappe-bench
```

Configure database and Redis:

```bash
bench set-config -g db_host mariadb
bench set-config -g redis_cache redis://redis-cache:6379
bench set-config -g redis_queue redis://redis-queue:6379
bench set-config -g redis_socketio redis://redis-queue:6379
```

### Creating a new site

```bash
bench new-site development.localhost
```

Change to development mode (only for development):

```bash
bench --site development.localhost set-config developer_mode 1
bench --site development.localhost clear-cache
bench use development.localhost
```

**Important for API access**: Configure CORS and CSRF:

```bash
# Turn off CSRF checking for development
bench --site development.localhost set-config ignore_csrf 1

# Or add to sites/common_site_config.json:
{
  "ignore_csrf": 1,
  "allow_cors": "*",
  "cors_headers": [
    "Authorization",
    "Content-Type",
    "X-Frappe-CSRF-Token",
    "X-Frappe-CMD"
  ]
}
```

### Installing Parent Portal app

```bash
bench get-app https://github.com/Linh3694/frappe-sis.git
bench --site development.localhost install-app parent_portal
```

Update and build:

```bash
bench update --requirements --patch --build
```

Start the development server:

```bash
bench start
```

Go to `http://development.localhost:8000` for Frappe desk.

## Site Management Commands

- List of commands: `bench --site development.localhost --help`
- Python console: `bench --site development.localhost console`
- MariaDB console: `bench --site development.localhost mariadb`

## Frontend Integration

The separated frontend application connects to this backend via:

1. **API Proxy**: Development server proxies `/api/*` calls to this backend
2. **Authentication**: Uses Frappe session cookies for auth
3. **CORS**: Backend configured to accept cross-origin requests
4. **WebSocket**: Real-time features via Frappe's built-in socketio

Frontend repository: [frappe-pp](https://github.com/Linh3694/frappe-pp)

## Production Deployment

### Backend (This App)

- Deploy on Frappe/ERPNext compatible hosting
- Configure CORS for frontend domain
- Set up SSL/TLS certificates
- Configure environment variables

### Frontend (Separate Repo)

- Deploy as static files on CDN/static hosting
- Configure `VITE_BACKEND_URL` to point to this backend
- Set up reverse proxy for API calls if needed

## License

ISC License - Digital Learning Team, Wellspring Saigon
