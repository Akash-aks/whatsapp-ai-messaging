# Flowcharts & Diagrams for Project Documentation

This guide provides all the flowcharts and diagrams needed for this project design.

---

## 📊 DIAGRAM 1: System Architecture

**Purpose:** Shows overall system components and data flow

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                        │
│  ┌──────────┐  ┌───────────┐  ┌─────────┐  ┌────────────┐  │
│  │ File     │  │ Column    │  │ AI      │  │ Preview &  │  │
│  │ Upload   │→ │ Selection │→ │ Config  │→ │ Send       │  │
│  └──────────┘  └───────────┘  └─────────┘  └────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      CORE PROCESSING LAYER                   │
│  ┌──────────────┐    ┌─────────────────┐                    │
│  │ Excel        │    │ Message         │                    │
│  │ Handler      │ ←→ │ Processor       │                    │
│  └──────────────┘    └────────┬────────┘                    │
│                               │                              │
│                               ↓                              │
│  ┌──────────────────────────────────────────┐               │
│  │         AI Generator                     │               │
│  │  ┌─────────┐  ┌────────┐  ┌──────────┐ │               │
│  │  │ Groq    │  │ Gemini │  │ Ollama   │ │               │
│  │  └─────────┘  └────────┘  └──────────┘ │               │
│  └──────────────────────────────────────────┘               │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    AUTOMATION LAYER                          │
│  ┌───────────────────────────────────────────┐              │
│  │   WhatsApp Sender (Selenium)              │              │
│  │   • Retry Logic (3 attempts)              │              │
│  │   • Duplicate Prevention                  │              │
│  │   • Delivery Tracking                     │              │
│  └───────────────────────────────────────────┘              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     OUTPUT & REPORTING                       │
│  ┌──────────────┐          ┌──────────────┐                 │
│  │ WhatsApp     │          │ Delivery     │                 │
│  │ Messages     │          │ Report.xlsx  │                 │
│  │ (Sent)       │          │ (Auto-gen)   │                 │
│  └──────────────┘          └──────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

**Tools to create this:**
- draw.io (https://app.diagrams.net/) — FREE
- Lucidchart (https://www.lucidchart.com/) — FREE tier available
- Microsoft Visio (if you have access)

---

## 📊 DIAGRAM 2: Main Application Flow

**Purpose:** Shows complete user journey from start to finish

```
START
  │
  ↓
┌─────────────────────┐
│ Launch Application  │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ Upload Excel File   │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐      ┌──────────────┐
│ Validate File?      │─NO──→│ Show Error   │
└──────────┬──────────┘      └──────────────┘
          YES
           │
           ↓
┌─────────────────────┐
│ Select Columns:     │
│ • Name              │
│ • Phone             │
│ • Message (opt)     │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ Choose AI Model     │
│    OR               │
│ Enable "Skip AI"    │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ Click "Generate     │
│ Messages"           │
└──────────┬──────────┘
           │
           ↓
      ┌────────┐
      │Skip AI?│
      └───┬────┘
         YES│    NO
            │    │
            │    ↓
            │  ┌──────────────────┐
            │  │ Call AI API      │
            │  │ for each contact │
            │  └────────┬─────────┘
            │           │
            ↓           ↓
      ┌──────────────────────┐
      │ Populate             │
      │ "generated_message"  │
      │ column               │
      └──────────┬───────────┘
                 │
                 ↓
      ┌──────────────────┐
      │ Preview Messages │
      └──────────┬───────┘
                 │
                 ↓
      ┌──────────────────┐
      │ Click "Send via  │
      │ WhatsApp"        │
      └──────────┬───────┘
                 │
                 ↓
      ┌──────────────────┐
      │ Open Chrome      │
      │ WhatsApp Web     │
      └──────────┬───────┘
                 │
                 ↓
      ┌──────────────────┐      ┌──────────────┐
      │ Scan QR Code?    │─NO──→│ Timeout Exit │
      └──────────┬───────┘      └──────────────┘
                YES
                 │
                 ↓
      ┌──────────────────────────┐
      │ For Each Contact:        │
      │ ┌──────────────────────┐ │
      │ │ Check if already     │ │
      │ │ in sent_successfully │ │
      │ └─────────┬────────────┘ │
      │          YES│      NO     │
      │             │      │      │
      │           SKIP     ↓      │
      │      ┌─────────────────┐ │
      │      │ Try Send (retry │ │
      │      │ up to 3 times)  │ │
      │      └────────┬────────┘ │
      │              SUCCESS│FAIL│
      │                 │    │   │
      │                 ↓    ↓   │
      │      ┌──────────────────┐│
      │      │ Log to delivery  ││
      │      │ report data      ││
      │      └──────────────────┘│
      └──────────────┬───────────┘
                     │
                     ↓
      ┌──────────────────────────┐
      │ Generate Delivery Report │
      │ (Excel file)             │
      └──────────┬───────────────┘
                 │
                 ↓
      ┌──────────────────┐
      │ Show Summary     │
      │ Popup            │
      └──────────┬───────┘
                 │
                 ↓
               END
```

---

## 📊 DIAGRAM 3: Retry Mechanism Detailed Flow

**Purpose:** Shows how the 3-attempt retry logic works

```
┌─────────────────────────┐
│ send_message(phone, msg)│
└───────────┬─────────────┘
            │
            ↓
       ┌─────────┐
       │attempt=0│
       └────┬────┘
            │
            ↓
    ┌───────────────┐
    │ attempt <= 2? │─NO──→ Return FAILED
    └───────┬───────┘
           YES
            │
            ↓
    ┌──────────────────┐
    │ Navigate to chat │
    └────────┬─────────┘
             │
             ↓
    ┌──────────────────┐
    │ Wait for message │
    │ input box        │
    └────────┬─────────┘
             │
             ↓
         ┌───────┐
         │Success?│
         └───┬───┘
            YES│   NO
               │   │
               │   ↓
               │ ┌──────────────────┐
               │ │ Check if invalid │
               │ │ number error?    │
               │ └───────┬──────────┘
               │        YES│   NO
               │           │   │
               │           ↓   │
               │     Return    │
               │     INVALID   │
               │               │
               │               ↓
               │      ┌────────────────┐
               │      │ attempt++      │
               │      │ Wait 3 seconds │
               │      └────────┬───────┘
               │               │
               │               ↓
               │      ┌────────────────┐
               │      │ Log retry msg  │
               │      └────────┬───────┘
               │               │
               │               │
               └───────┬───────┘
                       │
                       ↓ (loop back)
                  
    ┌──────────────────┐
    │ Send message     │
    │ (ENTER key)      │
    └────────┬─────────┘
             │
             ↓
    ┌──────────────────┐
    │ Wait 2s to       │
    │ confirm sent     │
    └────────┬─────────┘
             │
             ↓
      Return SUCCESS
```

---

## 📊 DIAGRAM 4: Duplicate Prevention Logic

**Purpose:** Shows how sent_successfully set prevents duplicates

```
App Startup
     │
     ↓
┌──────────────────────┐
│ Initialize           │
│ sent_successfully={} │
│ (empty set)          │
└──────────┬───────────┘
           │
           ↓
User loads Excel, generates messages
           │
           ↓
User clicks "Send via WhatsApp"
           │
           ↓
┌──────────────────────────────────┐
│ For each row in Excel:           │
│   1. Get phone number            │
│   2. Clean phone number          │
│   3. Check: phone in set?        │
│      │                            │
│      ├─ YES → Skip this contact  │
│      │                            │
│      └─ NO → Add to send queue   │
└──────────┬───────────────────────┘
           │
           ↓
┌──────────────────────────────────┐
│ Send all queued messages         │
│                                   │
│ After each successful send:      │
│   sent_successfully.add(phone)   │
└──────────┬───────────────────────┘
           │
           ↓
Sending complete
           │
           ↓
User clicks "Send" again (e.g., after internet issue)
           │
           ↓
Filter step repeats:
  - Contacts already in set → SKIPPED
  - New contacts → SENT

           │
           ↓
User loads NEW Excel file
           │
           ↓
┌──────────────────────┐
│ Clear set:           │
│ sent_successfully={} │
└──────────────────────┘
```

---

## 📊 DIAGRAM 5: Data Flow Diagram (DFD Level 0)

**Purpose:** Shows data flow between components

```
                    ┌────────────┐
                    │   USER     │
                    └──────┬─────┘
                           │
              Excel File,  │  Delivery Report,
              Selections   │  Status Updates
                           │
                           ↓
    ┌──────────────────────────────────────────────┐
    │                                              │
    │        WhatsApp AI Messaging System          │
    │                                              │
    │  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
    │  │  Excel   │  │  Message │  │ WhatsApp  │ │
    │  │ Handler  │→ │Processor │→ │  Sender   │ │
    │  └──────────┘  └────┬─────┘  └─────┬─────┘ │
    │                     │                │       │
    │                     ↓                │       │
    │              ┌────────────┐          │       │
    │              │ AI         │          │       │
    │              │ Generator  │          │       │
    │              └────────────┘          │       │
    │                                      │       │
    └──────────────────────────────────────┼───────┘
                                           │
                     API Requests          │  Messages
                          │                │
                          ↓                ↓
              ┌────────────────┐  ┌──────────────┐
              │  AI Providers  │  │  WhatsApp    │
              │  (Groq/Gemini) │  │  Web         │
              └────────────────┘  └──────────────┘
```

---

## 📊 DIAGRAM 6: Class Diagram (UML)

**Purpose:** Shows object-oriented structure

```
┌─────────────────────────┐
│   MainWindow            │
├─────────────────────────┤
│ - excel_handler         │
│ - ai_generator          │
│ - message_processor     │
│ - whatsapp_sender       │
│ - sent_successfully:set │
├─────────────────────────┤
│ + setup_ui()            │
│ + browse_file()         │
│ + generate_messages()   │
│ + send_messages()       │
│ + on_closing()          │
└────────┬────────────────┘
         │ uses
         │
    ┌────┴─────────────────┬────────────────┬─────────────────┐
    │                      │                │                 │
    ↓                      ↓                ↓                 ↓
┌──────────────┐  ┌────────────────┐  ┌────────────┐  ┌──────────────┐
│ExcelHandler  │  │MessageProcessor│  │AIGenerator │  │WhatsAppSender│
├──────────────┤  ├────────────────┤  ├────────────┤  ├──────────────┤
│-dataframe    │  │-ai_generator   │  │-provider   │  │-driver       │
│-file_path    │  │-processed_count│  │-client     │  │-is_logged_in │
├──────────────┤  ├────────────────┤  ├────────────┤  ├──────────────┤
│+load_file()  │  │+process_       │  │+generate_  │  │+send_message │
│+get_columns()│  │ contacts()     │  │ message()  │  │ (retry logic)│
│+export_      │  │+get_           │  │+_call_groq │  │+send_bulk_   │
│ delivery_    │  │ statistics()   │  │+_call_     │  │ messages()   │
│ report()     │  │                │  │ gemini()   │  │              │
└──────────────┘  └────────────────┘  └────────────┘  └──────────────┘
```

---

## 📊 DIAGRAM 7: Deployment Diagram

**Purpose:** Shows how components are deployed on the system

```
┌────────────────────────────────────────────────┐
│         User's Computer (Windows)              │
│                                                │
│  ┌──────────────────────────────────────────┐ │
│  │   Python Runtime Environment              │ │
│  │                                           │ │
│  │  ┌─────────────────────────────────────┐ │ │
│  │  │  WhatsApp AI Messaging App          │ │ │
│  │  │  • main.py                          │ │ │
│  │  │  • GUI (Tkinter)                    │ │ │
│  │  │  • Core modules                     │ │ │
│  │  └──────────┬──────────────────────────┘ │ │
│  │             │                             │ │
│  │             │ Controls                    │ │
│  │             ↓                             │ │
│  │  ┌─────────────────────────────────────┐ │ │
│  │  │  Selenium WebDriver                 │ │ │
│  │  │  • ChromeDriver                     │ │ │
│  │  └──────────┬──────────────────────────┘ │ │
│  │             │                             │ │
│  └─────────────┼─────────────────────────────┘ │
│                │                               │
│                │ Launches                      │
│                ↓                               │
│  ┌──────────────────────────────────────────┐ │
│  │   Google Chrome Browser                   │ │
│  │   • WhatsApp Web                         │ │
│  └──────────────────────────────────────────┘ │
│                                                │
└────────────────┬───────────────────────────────┘
                 │
                 │ HTTPS
                 ↓
        ┌────────────────┐
        │   Internet     │
        └────────┬───────┘
                 │
         ┌───────┴────────────┐
         │                    │
         ↓                    ↓
┌──────────────────┐  ┌──────────────────┐
│ WhatsApp Servers │  │ AI API Providers │
│ (Meta)           │  │ • Groq           │
│                  │  │ • Google Gemini  │
└──────────────────┘  └──────────────────┘
```

---

## 🛠️ RECOMMENDED TOOLS FOR CREATING DIAGRAMS

### 1. **Draw.io** (FREE, Best for flowcharts)
- Website: https://app.diagrams.net/
- Export: PNG, PDF, SVG
- Templates: Flowchart, UML, Architecture

### 2. **Lucidchart** (FREE tier available)
- Website: https://www.lucidchart.com/
- Best for: Professional-looking diagrams
- Export: PNG, PDF

### 3. **PlantUML** (FREE, Code-based)
- Website: https://plantuml.com/
- Best for: UML diagrams, Class diagrams
- Write diagram as code, auto-generates image

### 4. **Microsoft Visio** (Paid, if available)
- Best for: All diagram types
- Export: PNG, PDF, SVG

### 5. **Mermaid** (FREE, Markdown-based)
- Website: https://mermaid.live/
- Best for: Quick flowcharts in Markdown
- Can embed in documentation

---
