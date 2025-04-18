# AgentZero

A team of AI agents designed to identify and evaluate great products to sell online, leveraging Google's Vertex AI Agent Engine capabilities.

## Project Overview

AgentZero is an experimental project that demonstrates the capabilities of Google's Vertex AI Agent Engine through a team of specialized agents working together to identify and evaluate potential products for online sales.

## Architecture

The system consists of five main components:

1. **Orchestrator Agent** - Manages workflow and coordinates specialized agents
2. **Product Research Agent** - Handles document retrieval and analysis using RAG
3. **Market Analysis Agent** - Performs web research and market trend analysis
4. **Sales Opportunity Agent** - Evaluates sales potential and profit margins
5. **Product Evaluation Agent** - Provides comprehensive product evaluation

## Setup

### Prerequisites

- Google Cloud account with Vertex AI API enabled
- Node.js (v18 or higher)
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AgentZero.git
cd AgentZero
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Google Cloud credentials
```

## Development

### Running Tests

```bash
npm test
```

### Building the Project

```bash
npm run build
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 