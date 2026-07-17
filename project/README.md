# HealthSync: Personal Health Narrative Generator

HealthSync is an iOS application that transforms fragmented health data into meaningful personal health narratives. It combines Apple Health data with user-logged information to provide insights into health patterns and help users better understand their wellbeing.

## Features

1. **Daily Health Journal**
   - Log mood, energy levels, symptoms, and notes
   - Track custom tags for categorizing triggers and experiences
   - Automatic integration with Apple Health data (sleep, activity, heart rate)

2. **Weekly Health Narratives**
   - AI-generated summaries connecting your lifestyle factors and symptoms
   - Clear visualizations of patterns and correlations
   - Personalized insights based on your unique health journey

3. **Pattern Analysis**
   - Deep analysis of factors associated with specific symptoms
   - Identification of potential triggers and correlations
   - Actionable recommendations based on identified patterns

4. **Doctor Visit Preparation**
   - Concise, data-driven summaries for healthcare appointments
   - Key symptom frequency and severity tracking
   - Organized list of questions for your healthcare provider
   - Easy export/sharing options

## Technical Implementation

### Architecture

This application follows a Model-View-Controller (MVC) pattern with SwiftUI for the user interface:

- **Models**: Data structures for journal entries, symptoms, summaries, and patterns
- **Views**: SwiftUI interfaces for each feature
- **Services**: Logic for data management, HealthKit integration, and AI processing

### Key Components

1. **HealthKitService**: Manages integration with Apple's HealthKit framework
2. **AIService**: Handles communication with the Gemini API for AI-powered insights
3. **DataStore**: Manages data persistence and retrieval

### Data Flow

1. User logs daily health information
2. App combines this with data from Apple Health
3. AI analyzes the combined data to generate insights
4. Insights are presented to the user in an accessible format

## Getting Started

### Prerequisites

- Xcode 15+
- iOS 17+
- Apple Developer account (for HealthKit integration)
- Gemini API key (for production use)

### Installation

1. Clone this repository
2. Open the project in Xcode
3. Add your Gemini API key to `AIService.swift`
4. Build and run on a compatible iOS device

## Next Steps

This MVP demonstrates the core functionality. Future enhancements could include:

- Medication tracking and adherence patterns
- Environmental factor correlation (weather, air quality)
- Deeper machine learning for more personalized insights
- Integration with additional health platforms

## Hackathon Implementation

This project was designed to be implementable within a 16-hour hackathon timeframe by a 4-person team, focusing on demonstrating the core concept and value proposition.

## Credits

Developed for the HooHacks hackathon.
