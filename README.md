# WhatsApp AI Message Automation

A production-ready desktop application that automates personalized WhatsApp messaging using AI. Perfect for final-year engineering projects demonstrating AI integration, automation, and software development best practices.

## 🌟 Features

- **Excel Integration**: Upload and process contact lists from Excel files
- **AI-Powered Message Generation**: Improve and personalize messages using Claude or GPT models
- **Dynamic Column Selection**: Intelligently select name, phone, and message columns
- **Custom AI Prompts**: Define your own prompts for message generation
- **Real-time Preview**: Review all generated messages before sending
- **WhatsApp Automation**: Automated sending via WhatsApp Web with safe delays
- **Status Tracking**: Real-time delivery status for each message
- **Robust Error Handling**: Comprehensive logging and error recovery
- **Professional GUI**: Clean, intuitive Tkinter interface

## 📋 Requirements

- Python 3.8 or higher
- Google Chrome browser (for WhatsApp Web automation)
- Active internet connection
- Anthropic Claude API key or OpenAI API key

## 🚀 Installation

### Step 1: Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd whatsapp_ai_automation

# Or download and extract the ZIP file
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure API Keys

1. Copy `.env.example` to `.env`:
   ```bash
   # Windows
   copy .env.example .env
   
   # Linux/Mac
   cp .env.example .env
   ```

2. Edit `.env` and add your API key(s):
   ```
   ANTHROPIC_API_KEY=your_key_here
   # or
   OPENAI_API_KEY=your_key_here
   ```

3. Get API keys:
   - **Anthropic Claude**: https://console.anthropic.com/
   - **OpenAI GPT**: https://platform.openai.com/

## 📖 Usage

### Running the Application

```bash
python main.py
```

### Step-by-Step Guide

1. **Upload Excel File**
   - Click "Browse" and select your Excel file
   - Supported formats: `.xlsx`, `.xls`
   - File should contain contact names and phone numbers

2. **Select Columns**
   - **Name Column**: Required - column containing contact names
   - **Phone Column**: Required - column with phone numbers (with country code)
   - **Message Column**: Optional - existing messages to improve

3. **Configure AI**
   - Select AI model (Claude Sonnet 4, Claude Haiku 4, GPT-4, or GPT-3.5)
   - Customize the AI prompt (use `{name}` for personalization, `{message}` for original)
   - Example: "Improve this message and make it more professional: {message}"

4. **Generate Messages**
   - Click "Generate Messages"
   - Wait for AI to process all contacts
   - View progress and statistics in the status area

5. **Preview Messages**
   - Click "Preview Messages" to review all generated content
   - Export to Excel if needed

6. **Send via WhatsApp**
   - Click "Send via WhatsApp"
   - Browser will open to WhatsApp Web
   - Scan QR code with your phone
   - Application will automatically send messages with safe delays

## 📁 Project Structure

```
whatsapp_ai_automation/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # Documentation
├── .env.example               # Environment variables template
│
├── src/
│   ├── gui/                   # GUI components
│   │   ├── main_window.py    # Main application window
│   │   ├── preview_window.py # Message preview dialog
│   │   └── styles.py         # UI styling
│   │
│   ├── core/                  # Core business logic
│   │   ├── excel_handler.py  # Excel processing
│   │   ├── ai_generator.py   # AI integration
│   │   ├── message_processor.py # Message generation
│   │   └── validator.py      # Data validation
│   │
│   ├── automation/            # WhatsApp automation
│   │   └── whatsapp_sender.py
│   │
│   └── utils/                 # Utilities
│       ├── logger.py         # Logging system
│       ├── config.py         # Configuration
│       └── helpers.py        # Helper functions
│
├── logs/                      # Application logs
└── data/                      # Sample data files
```

## 🏗️ Architecture

### Design Patterns Used

1. **Separation of Concerns**: Clear separation between GUI, business logic, and automation
2. **Modular Architecture**: Each component is independent and reusable
3. **Dependency Injection**: Components receive dependencies rather than creating them
4. **Observer Pattern**: Progress callbacks for real-time updates
5. **Factory Pattern**: AI generator initialization based on model selection

### Key Components

- **ExcelHandler**: Manages Excel file operations and data validation
- **AIMessageGenerator**: Interfaces with Claude/GPT APIs for message generation
- **MessageProcessor**: Orchestrates message generation for multiple contacts
- **WhatsAppSender**: Automates WhatsApp Web using Selenium
- **Validator**: Ensures data integrity before processing
- **Logger**: Centralized logging with file and console output

## 🛠️ Building Executable (.exe)

### Using PyInstaller

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Create executable:
   ```bash
   pyinstaller --onefile --windowed --name "WhatsApp AI Automation" --icon=icon.ico main.py
   ```

3. Find executable in `dist/` folder

### Alternative: Using Auto-py-to-exe (GUI Tool)

1. Install:
   ```bash
   pip install auto-py-to-exe
   ```

2. Run GUI:
   ```bash
   auto-py-to-exe
   ```

3. Configure:
   - Script Location: `main.py`
   - Onefile: One File
   - Console Window: Window Based (hide console)
   - Icon: Select icon file (optional)
   - Additional Files: Add `.env`, `data/` folder

4. Click "Convert .py to .exe"

## 📝 Sample Excel Format

Your Excel file should have these columns:

| Name          | Phone          | Message (Optional)              |
|---------------|----------------|---------------------------------|
| John Doe      | 919876543210  | Thanks for your interest        |
| Jane Smith    | 919876543211  | Welcome to our community        |
| Bob Johnson   | 919876543212  | We appreciate your support      |

**Important Notes:**
- Phone numbers should include country code (e.g., 91 for India)
- Name column is required
- Phone column is required for sending
- Message column is optional (AI can generate from scratch)

## ⚙️ Configuration

Edit `src/utils/config.py` to customize:

- Message delays (to avoid WhatsApp blocking)
- Browser timeout settings
- Maximum contacts per batch
- Default AI prompts
- Logging levels

## 🔍 Troubleshooting

### Common Issues

1. **"No module named 'src'"**
   - Ensure you're in the project root directory
   - Reinstall dependencies: `pip install -r requirements.txt`

2. **"API key not found"**
   - Check `.env` file exists and contains valid API keys
   - Restart the application after adding keys

3. **WhatsApp login fails**
   - Ensure stable internet connection
   - Try closing and reopening browser
   - Check if WhatsApp Web is accessible in your browser

4. **Messages not sending**
   - Verify phone numbers include country code
   - Check WhatsApp Web is still logged in
   - Review logs in `logs/app.log`

5. **Chrome driver issues**
   - Update Chrome browser to latest version
   - Clear Chrome cache
   - Reinstall selenium: `pip install --upgrade selenium`

## 📊 Logging

All application activities are logged to:
- **File**: `logs/app.log` (detailed logs)
- **Console**: Real-time status updates
- **GUI**: Status window in application

Log levels: DEBUG, INFO, WARNING, ERROR

## 🔒 Security Considerations

- **API Keys**: Never commit `.env` file to version control
- **WhatsApp**: Use responsibly, avoid spam
- **Rate Limiting**: Built-in delays to prevent blocking
- **Data Privacy**: Contact data stays on your machine

## 🎓 Academic Use

This project demonstrates:
- **AI Integration**: Real-world API usage
- **Software Architecture**: Clean, modular design
- **Automation**: Browser automation with Selenium
- **GUI Development**: Professional Tkinter interface
- **Error Handling**: Robust error recovery and logging
- **Data Processing**: Excel manipulation with Pandas
- **Best Practices**: PEP 8, documentation, type hints

## 📄 License

This project is for educational purposes. Please ensure compliance with:
- WhatsApp Terms of Service
- Anthropic/OpenAI API usage policies
- Local data protection regulations

## 🤝 Contributing

For improvements:
1. Fork the repository
2. Create feature branch
3. Make changes with proper documentation
4. Submit pull request

## 📧 Support

For issues:
1. Check troubleshooting section
2. Review logs in `logs/app.log`
3. Create issue with error details

## 🙏 Acknowledgments

- **Anthropic Claude**: AI message generation
- **OpenAI GPT**: Alternative AI model
- **Selenium**: Browser automation
- **Pandas**: Data processing
- **Tkinter**: GUI framework

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: January 2026

## 📚 Additional Resources

- [Anthropic Documentation](https://docs.anthropic.com/)
- [OpenAI Documentation](https://platform.openai.com/docs)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [Tkinter Tutorial](https://docs.python.org/3/library/tkinter.html)