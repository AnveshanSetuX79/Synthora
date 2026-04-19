# Pages Directory Structure

This directory is organized by user type and access level for better maintainability.

## Directory Structure

```
pages/
├── admin/                    # Admin-only pages
│   ├── AdminDashboard.jsx
│   ├── AdminAnalyticsPage.jsx
│   └── AdminPanelPage.jsx
│
├── business-owner/           # Business owner pages
│   ├── BusinessOwnerDashboard.jsx
│   ├── BusinessOwnerOnboarding.jsx
│   └── BusinessOwnerDealDetailPage.jsx
│
├── freelancer/               # Freelancer-only pages
│   ├── FreelancerDashboard.jsx
│   ├── AnalyticsPage.jsx
│   ├── LeadsPage.jsx
│   ├── LeadDetailPage.jsx
│   ├── MyLeadsPage.jsx
│   ├── DiscoverLeadsPage.jsx
│   ├── OutreachPage.jsx
│   ├── KYCPage.jsx
│   └── OnboardingPage.jsx
│
├── shared/                   # Pages accessible by multiple user types
│   ├── DashboardPage.jsx     # Main dashboard router
│   ├── DealsPage.jsx
│   ├── DealDetailPage.jsx
│   ├── CreateDealPage.jsx
│   ├── PaymentPage.jsx
│   ├── ProfilePage.jsx
│   └── MessagesPage.jsx
│
└── public/                   # Public pages (no auth required)
    ├── HomePage.jsx
    ├── LoginPage.jsx
    └── RegisterPage.jsx
```

## Page Categories

### Admin Pages (`/admin`)
- **AdminDashboard.jsx**: Main admin landing page with links to analytics and panel
- **AdminAnalyticsPage.jsx**: Platform-wide metrics, revenue, conversion rates
- **AdminPanelPage.jsx**: User management, KYC approval, dispute resolution

**Routes**: `/admin/dashboard`, `/admin/analytics`, `/admin/panel`

### Business Owner Pages (`/business-owner`)
- **BusinessOwnerDashboard.jsx**: Business info, freelancer list, deals
- **BusinessOwnerOnboarding.jsx**: First-time user onboarding flow
- **BusinessOwnerDealDetailPage.jsx**: Deal details with milestone tracking

**Routes**: `/business-dashboard`, `/business-onboarding`, `/business-deals/:id`

### Freelancer Pages (`/freelancer`)
- **FreelancerDashboard.jsx**: Freelancer main dashboard
- **AnalyticsPage.jsx**: ROI metrics, conversion funnel
- **LeadsPage.jsx**: Browse all available leads
- **LeadDetailPage.jsx**: Individual lead details
- **MyLeadsPage.jsx**: Claimed leads
- **DiscoverLeadsPage.jsx**: Discover new leads by location
- **OutreachPage.jsx**: Send messages to leads
- **KYCPage.jsx**: KYC document submission
- **OnboardingPage.jsx**: Freelancer onboarding

**Routes**: `/freelancer-dashboard`, `/analytics`, `/leads`, `/my-leads`, etc.

### Shared Pages (`/shared`)
Pages that can be accessed by multiple user types:
- **DashboardPage.jsx**: Router that redirects to role-specific dashboard
- **DealsPage.jsx**: List of deals (freelancers and business owners)
- **DealDetailPage.jsx**: Deal details (all roles)
- **CreateDealPage.jsx**: Create new deal (freelancers)
- **PaymentPage.jsx**: Payment processing (all roles)
- **ProfilePage.jsx**: User profile settings (all roles)
- **MessagesPage.jsx**: Chat interface (all roles)

**Routes**: `/dashboard`, `/deals`, `/profile`, `/messages/:id`, etc.

### Public Pages (`/public`)
Pages accessible without authentication:
- **HomePage.jsx**: Landing page
- **LoginPage.jsx**: User login
- **RegisterPage.jsx**: User registration

**Routes**: `/`, `/login`, `/register`

## Benefits of This Structure

1. **Clear Separation**: Easy to identify which pages belong to which user type
2. **Better Maintainability**: Changes to one user type don't affect others
3. **Easier Navigation**: Developers can quickly find the page they need
4. **Scalability**: Easy to add new pages for each user type
5. **Access Control**: Clear visibility of which pages require which roles
6. **Reduced Clutter**: No more scrolling through 25+ files in one directory

## Import Examples

```javascript
// Admin pages
import AdminDashboard from './pages/admin/AdminDashboard'

// Business owner pages
import BusinessOwnerDashboard from './pages/business-owner/BusinessOwnerDashboard'

// Freelancer pages
import FreelancerDashboard from './pages/freelancer/FreelancerDashboard'

// Shared pages
import ProfilePage from './pages/shared/ProfilePage'

// Public pages
import HomePage from './pages/public/HomePage'
```

## Notes

- All imports in `App.jsx` have been updated automatically
- Internal imports within pages have been updated by the smartRelocate tool
- If you add a new page, place it in the appropriate directory based on access level
