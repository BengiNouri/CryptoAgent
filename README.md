# 🚀 Crypto Insight Agent

A sophisticated AI-powered cryptocurrency analysis assistant built with RAG (Retrieval-Augmented Generation) architecture.

## ✨ Features

### 💬 Intelligent Chat Agent
- **Natural Language Queries**: Ask questions in plain English about crypto markets
- **Tool Integration**: Automatically calls specialized functions for data analysis
- **Context-Aware**: Uses RAG to provide informed responses based on stored data
- **Real-time Analysis**: Get up-to-date insights on cryptocurrency trends

### 📊 Interactive Dashboard
- **Live Market Data**: Real-time price tracking for Bitcoin, Ethereum, and Solana
- **Price Charts**: Interactive 30-day price trend visualizations
- **Market Share Analysis**: Visual breakdown of cryptocurrency distribution
- **Data Tables**: Clean, organized display of latest prices and dates

### 🔍 Advanced Analytics
- **Statistical Analysis**: Average, min, max prices with volatility calculations
- **Volatility Tracking**: Visual representation of price stability across coins
- **Historical Trends**: Deep dive into price movements and patterns
- **Performance Metrics**: Comprehensive data points for informed decisions

### ⚡ Quick Actions
- **One-Click Analysis**: Instant access to top movers and market trends
- **Preset Queries**: Common analysis tasks available via sidebar buttons
- **Smart Suggestions**: Example queries to help users get started
- **Export Ready**: Data formatted for easy sharing and reporting

## 🛠️ Technology Stack

- **Frontend**: Streamlit with custom CSS styling
- **AI/ML**: OpenAI GPT-4o-mini with LangChain
- **Database**: PostgreSQL with Alembic migrations
- **Data Visualization**: Plotly for interactive charts
- **Data Processing**: Pandas for analysis and manipulation
- **API Integration**: CoinGecko for real-time crypto data
- **Containerization**: Docker with Docker Compose

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key
- CoinGecko API key (optional, for enhanced data)

### Setup
1. **Clone and Configure**
   ```bash
   git clone <repository>
   cd crypto-insight-agent
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Start Services**
   ```bash
   docker-compose up -d
   ```

3. **Initialize Database**
   ```bash
   docker exec crypto-insight-agent-app-1 python manage.py migrate
   ```

4. **Load Sample Data**
   ```bash
   docker exec crypto-insight-agent-app-1 python manage.py load-data 30
   ```

5. **Access the App**
   - Open http://localhost:8501 in your browser
   - Start chatting with the AI agent!

## 💡 Usage Examples

### Chat Queries
- "Show me the top 5 movers over 7 days"
- "Plot Bitcoin price for the last 30 days"
- "What's driving the crypto market today?"
- "Compare Ethereum and Solana performance"

### Dashboard Features
- **Navigation**: Use the sidebar to switch between Chat, Dashboard, and Analytics
- **Quick Actions**: Click preset buttons for instant analysis
- **Interactive Charts**: Hover and zoom on price charts
- **Real-time Stats**: Monitor live coin counts and data points

## 🔧 Management Commands

```bash
# Run database migrations
python manage.py migrate

# Load crypto price data (default: 30 days)
python manage.py load-data [days]

# Alternative ETL execution
python -m app.etl.load_prices
```

## 📁 Project Structure

```
crypto-insight-agent/
├── app/
│   ├── agents/          # AI agent logic and tools
│   ├── context/         # RAG embedding system
│   ├── etl/            # Data extraction and loading
│   ├── prompts/        # AI prompt templates
│   └── ui/             # Streamlit interface
├── alembic/            # Database migrations
├── docker-compose.yml  # Container orchestration
├── manage.py          # Management commands
└── README.md          # This file
```

## 🎨 UI Features

### Modern Design
- **Gradient Headers**: Eye-catching visual design
- **Responsive Layout**: Works on desktop and mobile
- **Custom Styling**: Professional color scheme and typography
- **Interactive Elements**: Smooth animations and transitions

### User Experience
- **Intuitive Navigation**: Clear page structure with sidebar menu
- **Loading States**: Visual feedback during AI processing
- **Error Handling**: Graceful error messages and recovery
- **Accessibility**: Screen reader friendly and keyboard navigable

## 🔒 Security & Configuration

- **12-Factor App**: Environment-based configuration
- **API Key Management**: Secure credential handling
- **Database Security**: Parameterized queries and connection pooling
- **Container Isolation**: Secure Docker deployment

## 📈 Performance

- **Efficient Queries**: Optimized database indexes
- **Caching**: Smart data caching for faster responses
- **Async Processing**: Non-blocking UI updates
- **Resource Management**: Memory-efficient data handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4o-mini
- CoinGecko for cryptocurrency data
- Streamlit team for the amazing framework
- LangChain for RAG capabilities