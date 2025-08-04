<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Python Reverse Proxy Tool Specification

## 1. Overview

### 1.1 Purpose

A high-performance, configuration-driven reverse proxy tool built in Python that enables developers to easily route HTTP requests from custom domain names to different backend services running on localhost ports.

### 1.2 Key Objectives

- **Simplicity**: Single configuration file setup
- **Performance**: Fast localhost routing
- **Ease of Use**: Minimal setup for local development


### 1.3 Target Use Cases

- Local development environment setup
- Simple routing between local services


## 2. System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        B[Browser/Client]
        C[curl/Postman]
    end
    
    subgraph "Proxy Layer"
        P[Reverse Proxy Server]
        CM[Configuration Manager]
        LM[Logging Manager]
        HM[Health Monitor]
    end
    
    subgraph "Backend Services"
        S1[Frontend :3000]
        S2[API Server :8080]
        S3[Admin Panel :9000]
        S4[Database API :5432]
    end
    
    subgraph "Configuration"
        CF[Config File<br/>JSON/YAML]
        HF[Hosts File]
    end
    
    B --> P
    C --> P
    P --> S1
    P --> S2
    P --> S3
    P --> S4
    
    CM --> CF
    P --> CM
    P --> LM
    P --> HM
    
    HF -.-> B
    HF -.-> C
```


## 3. Request Flow Architecture

```mermaid
sequenceDiagram
    participant C as Client
    participant DNS as DNS/Hosts
    participant P as Proxy Server
    participant R as Route Manager
    participant B as Backend Service
    
    C->>DNS: Resolve api.local
    DNS-->>C: 127.0.0.1
    
    C->>P: HTTP Request to api.local:8080
    P->>R: Extract host header
    R->>R: Lookup route mapping
    R-->>P: Target: http://127.0.0.1:8080
    
    P->>B: Forward request
    B-->>P: Response
    P-->>C: Proxied response
    
    P->>P: Log request/response
```


## 4. Configuration Specification

### 4.1 Configuration Structure

```mermaid
graph TD
    subgraph "Configuration Schema"
        A[Root Configuration]
        A --> B[Proxy Settings]
        A --> C[Route Definitions]
        A --> D[Default Route]
        A --> E[Logging Config]
        A --> F[Security Settings]
        
        B --> B1[Host/Port Binding]
        B --> B2[Timeout Settings]
        B --> B3[Connection Limits]
        
        C --> C1[Domain Mappings]
        C --> C2[Target URLs]
        C --> C3[Route Metadata]
        
        D --> D1[Fallback Target]
        D --> D2[Error Pages]
        
        E --> E1[Log Level]
        E --> E2[Log Format]
        E --> E3[Log Destination]
        
        F --> F1[CORS Settings]
        F --> F2[Rate Limiting]
        F --> F3[Auth Headers]
    end
```


### 4.2 Configuration Format

- **JSON format** for simple, widely supported configuration

### 4.3 Configuration Validation Rules

- **Required Fields**: `proxy.port`, `routes`, `default.target`
- **Optional Fields**: All logging, security, and advanced settings
- **Port Validation**: 1-65535 range, privilege warnings for <1024
- **URL Validation**: Valid HTTP/HTTPS URLs for targets
- **Host Validation**: Valid domain names or IP addresses


## 5. Core Features Specification

### 5.1 Routing Engine

- **Host-based routing** via HTTP Host header
- **Simple domain to port mapping**


### 5.2 Connection Management

- **Basic connection handling** for localhost services
- **Simple error handling** for unavailable backends


### 5.3 Basic Monitoring

- **Simple status endpoint** for proxy health
- **Basic logging** of requests and errors


## 6. Performance Specifications

### 6.1 Performance Targets

| Metric | Target |
| :-- | :-- |
| Request Latency | Fast localhost routing |
| Memory Usage | Minimal footprint |
| Configuration Reload | Quick hot reload |

### 6.2 Architecture

- **Simple async I/O** for handling requests
- **Basic request processing** for local development


## 7. Security Specification

### 7.1 Security Features

- **Basic input validation** for requests
- **Simple header handling** for local development


### 7.2 Security Controls

- **Basic request validation** for local development
- **Simple error handling** for malformed requests


## 8. Error Handling Architecture

```mermaid
flowchart TD
    A[Incoming Request] --> B{Valid Route?}
    B -->|No| C[404 Not Found]
    B -->|Yes| D{Upstream Available?}
    D -->|No| E[502 Bad Gateway]
    D -->|Yes| F{Timeout?}
    F -->|Yes| G[504 Gateway Timeout]
    F -->|No| H[Forward Request]
    H --> I{Upstream Error?}
    I -->|Yes| J[502/503 Response]
    I -->|No| K[Success Response]
    
    C --> L[Log Error]
    E --> L
    G --> L
    J --> L
    L --> M[Return to Client]
```


### 8.1 Error Categories

- **Configuration Errors**: Invalid config, missing files
- **Network Errors**: Connection failures, timeouts
- **Upstream Errors**: Backend service failures


## 9. Command Line Interface

### 9.1 CLI Commands

| Command | Purpose | Example |
| :-- | :-- | :-- |
| `start` | Start proxy server | `proxy start` |
| `validate` | Validate configuration | `proxy validate` |

### 9.2 CLI Options

| Option | Description | Default |
| :-- | :-- | :-- |
| `--config`, `-c` | Configuration file path | `config.json` |
| `--port`, `-p` | Override proxy port | From config |
| `--host`, `-h` | Override bind host | From config |

## 10. Local Development Setup

### 10.1 Installation

- **pip install** for Python ecosystem integration
- **Direct Python execution** for quick testing
- **Git clone** for development and customization

### 10.2 Usage

- **Non-privileged ports** (1024+) for easy local testing
- **Local configuration files** for route definitions
- **Direct command line execution** for immediate feedback
- **Hot reload** for configuration changes during development


## 11. Monitoring and Observability

### 11.1 Basic Metrics

- **Request count** and status codes
- **Simple error logging**


### 11.2 Logging Standards

- **Simple request logging** with basic information
- **Error logging** for debugging


This specification provides a comprehensive blueprint for building a production-ready, high-performance reverse proxy tool that balances simplicity with powerful features, making it suitable for both development and production environments.

