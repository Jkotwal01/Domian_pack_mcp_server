# Domain Pack Authoring System - Frontend

Professional React frontend with backend integration, featuring a clean white theme with cyan/blue primary colors.

## Features

✨ **Modern UI/UX**
- Clean white background with professional color scheme
- Cyan/blue primary (#00BCD4) and orange secondary (#FF9800)
- Responsive design for all screen sizes
- Smooth animations and transitions

🔐 **Authentication**
- JWT-based login/register
- Protected routes
- Automatic token refresh
- Session management

💬 **Chat Interface**
- Real-time messaging with LangGraph backend
- Proposal preview and confirmation
- Message history
- WebSocket support (ready)

📝 **Proposal Management**
- List and view proposals
- Confirm/reject actions
- Diff viewer
- Status tracking

📚 **Version Control**
- Version history timeline
- Diff comparison
- Rollback functionality

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool
- **React Router v6** - Routing
- **Zustand** - State management
- **Axios** - HTTP client
- **TailwindCSS** - Styling
- **Lucide React** - Icons
- **React Hot Toast** - Notifications

## Quick Start

### Install Dependencies

```bash
npm install
```

### Configure Environment

Create `.env` file:
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/api/v1
```

### Run Development Server

```bash
npm run dev
```

Visit `http://localhost:5173`

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
src/
├── api/                    # Backend API integration
│   ├── client.js          # Axios instance with interceptors
│   ├── auth.js            # Auth endpoints
│   ├── chat.js            # Chat endpoints
│   ├── proposals.js       # Proposal endpoints
│   └── versions.js        # Version endpoints
├── components/
│   ├── common/            # Reusable components
│   │   ├── Button.jsx     # Button with variants
│   │   ├── Card.jsx       # Card container
│   │   ├── Input.jsx      # Form input
│   │   ├── Badge.jsx      # Status badge
│   │   └── Spinner.jsx    # Loading spinner
│   └── layout/            # Layout components
│       ├── Header.jsx     # Top header
│       ├── Sidebar.jsx    # Navigation sidebar
│       └── Layout.jsx     # Main layout
├── pages/
│   ├── Login.jsx          # Login page
│   └── Dashboard.jsx      # Dashboard page
├── stores/
│   ├── authStore.js       # Auth state (Zustand)
│   └── chatStore.js       # Chat state (Zustand)
├── App.jsx                # Main app with routing
├── main.jsx               # Entry point
└── index.css              # Global styles
```

## Design System

### Colors

```javascript
Primary (Cyan/Blue):  #00BCD4
Secondary (Orange):   #FF9800
Success:              #4CAF50
Warning:              #FFC107
Error:                #F44336
```

### Components

#### Button
```jsx
<Button variant="primary|secondary|outline|ghost|danger" size="sm|md|lg" loading={bool} icon={Icon}>
  Click me
</Button>
```

#### Card
```jsx
<Card title="Title" subtitle="Subtitle" actions={<Button>Action</Button>} hover>
  Content
</Card>
```

#### Input
```jsx
<Input label="Email" type="email" icon={Mail} error="Error message" />
```

#### Badge
```jsx
<Badge variant="primary|secondary|success|warning|error">Status</Badge>
```

## API Integration

All API calls are handled through modules in `src/api/`:

```javascript
import { authAPI } from './api/auth';
import { chatAPI } from './api/chat';
import { proposalsAPI } from './api/proposals';
import { versionsAPI } from './api/versions';

// Example usage
const result = await authAPI.login(email, password);
const sessions = await chatAPI.getSessions();
const proposal = await proposalsAPI.getProposal(id);
```

## State Management

Using Zustand for global state:

```javascript
import useAuthStore from './stores/authStore';
import useChatStore from './stores/chatStore';

// In component
const { user, login, logout } = useAuthStore();
const { messages, sendMessage } = useChatStore();
```

## Authentication Flow

1. User enters credentials on `/login`
2. `authStore.login()` calls backend `/auth/login`
3. JWT tokens stored in localStorage
4. `apiClient` automatically adds token to requests
5. Protected routes check `isAuthenticated`
6. Token auto-refreshes on 401 responses

## Next Steps

- [ ] Implement Chat page with message interface
- [ ] Create Proposals page with list and detail views
- [ ] Build Versions page with timeline and diff viewer
- [ ] Add WebSocket support for real-time updates
- [ ] Implement Settings page
- [ ] Add comprehensive error handling
- [ ] Write unit tests
- [ ] Optimize performance

## Development Tips

### Adding New Pages

1. Create page component in `src/pages/`
2. Add route in `App.jsx`
3. Add navigation link in `Sidebar.jsx`

### Creating New API Endpoints

1. Add function to appropriate `src/api/*.js` file
2. Use `apiClient` for authenticated requests
3. Handle errors appropriately

### Styling

- Use Tailwind utility classes
- Custom classes defined in `index.css`
- Follow design system colors
- Use `clsx` for conditional classes

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

MIT
