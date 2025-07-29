![SOCCER CENTRAL](soccer-central-web-app/static/images/soccer-central.png)

# Soccer Central Web App

Soccer Central is an innovative, data-driven organization that leverages the power of information to unlock the full potential of its academy. With a consistent focus on player development, training strategies, and performance optimization, data is used to drive informed decisions, personalized experiences, and a culture of excellence both on and off the field.

## Project Description
The project led by Soccer Central aims to gain a comprehensive understanding of the physical and tactical performance of academy players participating in the "MLS Next" league, which represents the pinnacle of youth male soccer competition in the United States and features the country's top teams and players. To achieve this, the academy has access to a variety of data sources that allow for tracking player and team behaviors and performance. However, the goal is to optimize the analysis and decision-making process in an integrated manner.

## Project Goal
To facilitate the performance analysis of Soccer Central academy players through the creation of a normalized database based on data relevance, along with the use of visualizations and customized reports to support continuous improvement in decision-making among stakeholders, to be developed over a 10-week period.

## Specific Objectives
1. **Data Centralization**: Create a structured database that centralizes all relevant player information, including performance, injuries, body composition, and academic data.
2. **Process Improvement**: Professionalize the use of data by implementing acquisition, control, and audit processes, avoiding the disorganized use of multiple spreadsheets.
3. **Data Analysis**: Conduct in-depth analysis of available data to identify patterns and areas for improvement in player performance.
4. **Report Generation**: Automate the creation of standardized and visual reports (PDF, dashboards), improving communication and enabling quick decision-making across key departments.
5. **Digital Culture**: Promote a digital culture based on advanced tools that streamline processes and support strategic decision-making with reliable data.
6. **Interdepartmental Collaboration**: Strengthen synergy between analysis, methodology, and physical preparation teams to align objectives and maximize sports performance.
7. **Tool Development**: Evaluate and select appropriate technological tools for data analysis and visualization, considering team comfort and user experience.
8. **Results Presentation**: Establish a consistent format and design for presenting results, aligned with the institution's identity.

## Methodology
The methodology used in this study follows a structured approach based on the CRISP-DM (Cross-Industry Standard Process for Data Mining), which has become one of the most effective frameworks for the development and application of data mining projects. This approach is divided into several key phases that guide the process from initial problem understanding to the implementation of data-based solutions.

1. **Business Understanding**: In this phase, the research problem is defined, project goals are set, and the key questions guiding the data analysis are formulated.
2. **Data Understanding**: Here, an initial overview of the characteristics of the data provided by suppliers is obtained, along with an assessment of their advantages and limitations.
3. **Data Preparation**: This stage involves data cleaning, integration, and transformation. Inconsistencies are removed, missing values are handled, and different sources are consolidated to ensure the data is comparable and ready for analysis.
4. **Modeling**: A comparative analysis of the different data providers is conducted using various analytical techniques. Performance metrics are generated, key event distributions are visualized, and meaningful patterns are identified to offer valuable insights for decision-making in soccer.
5. **Evaluation**: The results obtained from the comparative analysis are validated to ensure that the findings are relevant and applicable in the context of soccer performance.
6. **Deployment**: Finally, results are presented using interactive visual tools such as dashboards and graphs to enable clear and accessible understanding of the findings.

## Current Implementation Features

### Core Functionality
- **Player Directory**: Browse and search through all registered players
- **Player Details**: View comprehensive information about individual players including:
  - Personal information (name, birth date, nationality, etc.)
  - Playing information (position, roles, captain status)
  - Physical attributes (height, weight, shoe size)
  - Contract details (value, club value, agent value)
  - Education information
  - Biography and background
- **Real-time Data**: Live integration with Iterpro API for up-to-date player information
- **Responsive Design**: Modern, mobile-friendly interface that works on all devices

### Technical Features
- **RESTful API**: Clean API endpoints for data retrieval
- **Error Handling**: Comprehensive error handling and user feedback
- **Loading States**: Smooth loading animations and progress indicators
- **Navigation**: Intuitive navigation between player list and detail views

## API Endpoints

### Players
- `GET /players` - Retrieve all players
- `GET /players/<player_id>` - Get detailed information about a specific player

### Pages
- `GET /` - Main page with player directory
- `GET /player?id=<player_id>` - Player details page

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation
1. Clone the repository
2. Create a virtual environment: `python3 -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate`
4. Upgrade pip: `pip install --upgrade pip`
5. Install dependencies: `pip install -r requirements.txt`

### Environment Configuration
1. Copy the environment template: `cp .env.template .env`
2. Edit the `.env` file and add your Iterpro API credentials:
   - `BASE_URL`: The base URL for the Iterpro API (default: https://api.iterpro.com/api/v1)
   - `API_KEY`: Your Iterpro API key from the dashboard
   - `AUTH_HEADER`: Your HTTP Basic Authentication header (format: `Basic base64(username:password)`)
     - To generate: `echo -n "username:password" | base64`
     - Example: `Basic dXNlcm5hbWU6cGFzc3dvcmQ=`

### Running the Application
Run the Flask application: `python app.py`

The application will be available at `http://127.0.0.1:5000`

## Usage

### Browsing Players
1. Navigate to the main page (`/`)
2. View the list of all available players
3. Each player card shows basic information (name, position, nationality)
4. Click "View Profile" to see detailed information

### Viewing Player Details
1. From the player list, click "View Profile" on any player card
2. The system will navigate to a dedicated player details page
3. View comprehensive information organized in sections:
   - **Personal Information**: Name, birth details, nationality, preferred foot
   - **Playing Information**: Position, roles, captain status, current status
   - **Physical Information**: Height, weight, shoe size
   - **Contract Information**: Value, club value, agent value, team dates
   - **Education**: Education level and school information
   - **Biography**: Player background and story

### Navigation
- Use the "Back to Players" button to return to the main player list
- The interface is fully responsive and works on mobile devices

## API Integration

The application integrates with the Iterpro API using:
- **HTTP Basic Authentication** for the `Authorization` header
- **API Key** in the `x-iterpro-api-key` header
- **RESTful endpoints** following the OpenAPI 3.0 specification

### Authentication
The system uses two authentication methods as required by the Iterpro API:
1. **API Key**: Static credential for API identification (x-iterpro-api-key header)
2. **HTTP Basic Authentication**: Username and password encoded in base64 format (Authorization header)
   - Format: `Basic base64(username:password)`
       - Example: `Basic dXNlcm5hbWU6cGFzc3dvcmQ=`

## File Structure

```
soccer-central-web-app/
├── app.py                 # Main Flask application
├── iterpro_client.py      # API client for Iterpro integration
├── requirements.txt       # Python dependencies
├── .env.template         # Environment variables template
├── api-json.json         # OpenAPI specification
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Main page template
│   └── player_details.html # Player details page template
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   ├── js/
│   │   └── main.js       # Main JavaScript file
│   └── images/           # Static images
└── test_player_details.html # Test page for functionality
```

## Development

### Adding New Features
1. Follow the existing code structure and patterns
2. Use the established API client pattern in `iterpro_client.py`
3. Add appropriate error handling and loading states
4. Update CSS for responsive design
5. Test on multiple screen sizes

### Testing
- Use the provided `test_player_details.html` file to test API endpoints
- Verify both the player list and individual player detail functionality
- Test error scenarios (invalid player IDs, network issues)

## Troubleshooting

### Common Issues
1. **API Authentication Errors**: 
   - Verify your `.env` file contains correct credentials
   - Ensure AUTH_HEADER uses the format: `Basic base64(username:password)`
   - Generate base64 encoding: `echo -n "username:password" | base64`
2. **Player Not Found**: Ensure the player ID exists in the Iterpro system
3. **Network Issues**: Check your internet connection and API endpoint availability

### Debug Information
The application provides debug logging for API calls:
- URL and headers are logged for each request
- Error messages are displayed to users
- Console logs provide additional debugging information

## How to Contribute
To contribute, first create a branch that describes the change, e.g., `feature-update-readme`, and then create a *Pull Request* to the `master` branch of this repository.

Ideally, the *Pull Request* description should state if it resolves a numbered issue and include a link to it. If not, it should contain a description of the tests performed for the implementation as well as a textual summary of the change.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
1. Check the troubleshooting section above
2. Review the API documentation in `api-json.json`
3. Verify your environment configuration
4. Contact the development team for additional assistance
