SECURE PASS RxQ — MASTER PRODUCT & DEVELOPMENT PROMPT

ROLE

Act as a complete senior product and engineering team consisting of:

- Product Manager
- Product Architect
- UI/UX Designer
- Mobile Application Engineer
- Backend Engineer
- Database Architect
- API Architect
- Cybersecurity Engineer
- Payment Systems Engineer
- Telecom/Recharge Integration Engineer
- QA Engineer
- Automation Engineer
- DevOps Engineer
- Cloud Engineer
- Performance Engineer
- Technical Writer

Your task is to design and build a production-quality application called “Secure Pass RxQ.”

Do not treat this as a simple demo, college project, or basic CRUD application.

Build it as a real-world, secure, scalable, reliable, modern mobile platform.

---

1. PRODUCT NAME

Brand Name

Secure Pass RxQ

Short Name

Secure Pass

Concept

Secure Pass RxQ is a platform designed to make it easy for a user to purchase and send a mobile-data pack to another person's mobile number, including recipients using supported telecom operators.

The application should provide a simple and secure experience:

Enter Number → Detect Operator → Select Data Pack → Confirm → Pay → Recharge → Track → Complete

---

2. IMPORTANT BUSINESS RULE

The application must clearly distinguish between:

Data balance transfer

User's existing mobile data
          ↓
Transfer existing GB
          ↓
Another person's SIM

and:

Data-pack gifting/recharge

Sender
   ↓
Select recipient
   ↓
Select data pack
   ↓
Make payment
   ↓
Authorized recharge provider
   ↓
Recipient's mobile number
   ↓
Data pack activated

The application must not claim that it can directly transfer an existing Jio/Airtel/Vi/BSNL data balance unless an authorized operator API explicitly provides that capability.

Use only:

- Authorized telecom APIs
- Authorized recharge APIs
- Licensed payment providers
- Legitimate third-party service integrations

If a production API is unavailable, create a clearly labeled MOCK integration for development.

Never bypass telecom systems or manipulate operator balances without authorization.

---

3. PRODUCT VISION

Create a product that feels:

- Secure
- Premium
- Modern
- Fast
- Simple
- Reliable
- Professional
- Trustworthy

The user should not need technical knowledge.

The primary flow should be extremely simple:

OPEN APP
   ↓
SEND DATA
   ↓
ENTER NUMBER
   ↓
VERIFY RECIPIENT
   ↓
SELECT DATA PACK
   ↓
REVIEW
   ↓
PAY
   ↓
RECHARGE
   ↓
SUCCESS

---

4. CORE FEATURES

Implement the following major capabilities.

Authentication

- Mobile-number authentication
- OTP verification
- Secure sessions
- Logout
- Session expiration
- Device/session management
- Optional biometric authentication

Recipient Management

- Enter mobile number
- Validate number
- Detect operator where supported
- Detect circle/region where supported
- Confirm recipient
- Save frequent recipients
- Rename saved recipients

Data Packs

Display:

- Data amount
- Price
- Validity
- Benefits
- Pack category
- Availability

Example:

2 GB
28 Days
₹X
Data Pack

Never hard-code production plan information.

Retrieve plans from an authorized provider when available.

---

5. SEND DATA FLOW

Implement the following complete journey.

Step 1 — Home

User selects:

Send Data

Step 2 — Recipient

User enters:

+91 XXXXX XXXXX

Step 3 — Validation

Validate:

- Number format
- Country code
- Supported operator
- Provider availability

Step 4 — Operator Detection

Display:

Mobile Number
Operator
Circle

Ask the user to confirm before continuing.

Step 5 — Data Packs

Retrieve available plans.

Show them in an easy-to-understand layout.

Step 6 — Selection

User selects a plan.

Step 7 — Order Review

Display:

Recipient
Operator
Data
Validity
Price
Taxes/fees if applicable
Total

Step 8 — Payment

User chooses an available payment method.

Step 9 — Payment Verification

The backend verifies the payment.

Step 10 — Recharge

Create the recharge request.

Step 11 — Status Tracking

Show:

Payment successful
Recharge processing
Recharge successful

Step 12 — Completion

Show a professional success screen.

Provide:

- Transaction ID
- Recipient
- Data pack
- Amount
- Date/time
- Status

---

6. TRANSACTION STATE MACHINE

Implement a robust transaction state machine.

CREATED
   ↓
PAYMENT_PENDING
   ↓
PAYMENT_SUCCESS
   ↓
RECHARGE_PENDING
   ↓
SUCCESS

Failure states:

PAYMENT_FAILED
RECHARGE_FAILED
REFUND_PENDING
REFUNDED
CANCELLED
EXPIRED

Every transition must be validated.

Do not allow invalid state transitions.

---

7. DUPLICATE TRANSACTION PROTECTION

This is extremely important.

The user must never be charged twice because of:

- Double tapping
- Slow internet
- App restart
- API retry
- Duplicate webhook
- Backend retry
- Provider timeout

Use:

- Idempotency keys
- Unique transaction IDs
- Database constraints
- Transaction locking
- Safe retry logic

---

8. PAYMENT SYSTEM

Integrate only legitimate payment providers.

Support available methods such as:

- UPI
- Cards
- Net banking
- Other supported methods

Implement:

- Payment creation
- Payment verification
- Server-side verification
- Webhooks
- Webhook signature verification
- Timeout handling
- Retry handling
- Refund handling
- Duplicate-payment protection

Never store:

- CVV
- Raw card numbers
- UPI PIN
- Banking passwords
- Payment authentication secrets

Never hard-code payment credentials.

---

9. TELECOM/RECHARGE ARCHITECTURE

Use an adapter-based architecture.

OperatorAdapter
       │
       ├── JioAdapter
       ├── AirtelAdapter
       ├── ViAdapter
       ├── BSNLAdapter
       │
       └── MockOperatorAdapter

Each adapter should expose appropriate functions such as:

validateNumber()
detectOperator()
getPlans()
createRecharge()
getRechargeStatus()
handleFailure()

The system must allow new operators/providers to be added without rewriting the entire application.

---

10. MOCK DEVELOPMENT MODE

The application must work locally without real telecom or payment credentials.

Create:

- Mock payment provider
- Mock operator provider
- Mock recharge service
- Mock plans
- Test users
- Test transactions

Clearly display that these are development/mock services.

Never represent mock services as real production integrations.

---

11. UI/UX DESIGN

Create a premium mobile-first UI/UX.

The application must NOT look like a generic AI-generated application.

Use:

- Excellent typography
- Consistent spacing
- Strong hierarchy
- Modern cards
- Clear CTA buttons
- Professional icons
- Accessible colors
- Smooth animations
- Skeleton loading
- Empty states
- Error states
- Success states
- Confirmation states

Avoid:

- Excessive gradients
- Excessive animations
- Clutter
- Tiny buttons
- Inconsistent spacing
- Unnecessary screens
- Confusing navigation

---

12. REQUIRED SCREENS

Create and implement:

Onboarding

- Splash screen
- Welcome screen
- Introduction
- Login
- OTP verification

Main Application

- Home
- Send Data
- Recipient entry
- Operator detection
- Plan selection
- Order review
- Payment
- Payment processing
- Recharge processing
- Success
- Failure
- Refund status

User Account

- Profile
- Saved recipients
- Transaction history
- Transaction details
- Notifications
- Security settings
- Help & support
- Privacy
- Terms and conditions

---

13. HOME SCREEN

Design the home screen around the primary action.

Example:

SECURE PASS RxQ

Good morning 👋

What would you like to do?

[ Send Data ]

Recent Transactions
-------------------
Airtel • 2 GB
₹XX • Successful

Jio • 1 GB
₹XX • Successful

Keep the interface simple.

---

14. ERROR HANDLING

Every failure must have a useful message.

Never use generic:

«Something went wrong.»

Instead:

Example

«Payment was successful, but the recharge is still processing. Please don't make another payment. We'll update the transaction automatically.»

Other cases:

- Invalid number
- Unsupported operator
- Plan unavailable
- Payment failed
- Payment timeout
- Recharge pending
- Recharge failed
- Refund pending
- Provider unavailable
- Network error
- Session expired

---

15. BACKEND

Use a professional backend such as:

Python + FastAPI

or

Node.js + NestJS

The architecture should support:

- REST APIs
- API versioning
- Authentication
- Authorization
- Validation
- Rate limiting
- Structured errors
- Logging
- Background jobs
- Webhooks
- Database transactions

Example:

/api/v1/auth
/api/v1/users
/api/v1/recipients
/api/v1/operators
/api/v1/plans
/api/v1/orders
/api/v1/payments
/api/v1/recharges
/api/v1/transactions
/api/v1/refunds
/api/v1/notifications

---

16. DATABASE

Use PostgreSQL.

Create appropriate schemas/tables for:

users
sessions
recipients
operators
circles
plans
orders
payments
recharges
refunds
transactions
notifications
audit_logs
idempotency_keys

Implement:

- Primary keys
- Foreign keys
- Unique constraints
- Indexes
- Transactions
- Timestamps
- Data retention
- Appropriate soft deletion

---

17. SECURITY

Security is a first-class requirement.

Follow OWASP secure-development practices.

Implement:

- HTTPS/TLS
- Secure authentication
- OTP rate limiting
- API rate limiting
- Input validation
- Output encoding
- SQL injection prevention
- Authorization
- Secure sessions
- Secret management
- Environment variables
- Webhook verification
- Audit logging
- Fraud prevention
- Abuse prevention
- Secure error handling

Never expose:

- API keys
- Database credentials
- Payment secrets
- Authentication tokens
- Internal stack traces

---

18. PRIVACY

Minimize personal-data collection.

Mask phone numbers where appropriate.

Implement:

- Privacy policy
- Terms of service
- Data retention
- Account deletion where applicable
- Consent mechanisms where required

Consider applicable Indian privacy, telecom, and payment requirements before production deployment.

---

19. NOTIFICATIONS

Support appropriate notifications for:

- Payment successful
- Recharge successful
- Recharge pending
- Recharge failed
- Refund initiated
- Refund completed
- Security events

Use push notifications and other channels only where appropriate and authorized.

---

20. TRANSACTION HISTORY

Show:

Transaction ID
Recipient
Operator
Data Pack
Amount
Date
Payment Status
Recharge Status
Refund Status

Mask sensitive information.

Provide a transaction timeline.

---

21. RELIABILITY

Design for real-world failures.

Implement:

- Timeouts
- Retry policies
- Exponential backoff
- Idempotency
- Background jobs
- Queues
- Transaction locking
- Reconciliation
- Status polling where appropriate
- Circuit breakers where appropriate

Never create duplicate payments or recharges.

---

22. PERFORMANCE

Design for scalability.

Use where appropriate:

- PostgreSQL indexes
- Connection pooling
- Redis
- Background workers
- Queues
- Horizontal scaling
- Efficient APIs
- Caching

Do not over-engineer unnecessarily.

---

23. OBSERVABILITY

Implement:

- Structured logging
- Metrics
- Health checks
- Error tracking
- API monitoring
- Payment monitoring
- Recharge monitoring
- Database monitoring
- Alerts

Monitor:

- Transaction volume
- Success rate
- Failure rate
- Payment failures
- Recharge failures
- Refunds
- API latency
- Error rate

---

24. TESTING

Testing is mandatory.

Create:

Unit Tests

Business logic and services.

Integration Tests

- Database
- Authentication
- Payment mock
- Operator mock
- Recharge workflow

API Tests

- Authentication
- Authorization
- Validation
- Rate limiting
- Error handling

UI Tests

Test the complete user journey.

Security Tests

Test for:

- SQL injection
- IDOR
- Authentication bypass
- Authorization issues
- XSS where applicable
- CSRF where applicable
- Rate-limit bypass
- Sensitive-data exposure

Failure Tests

Test:

Payment success + recharge failure
Payment success + recharge timeout
Duplicate payment webhook
Duplicate recharge request
Network disconnect
Provider unavailable
App closed during payment
Server restart during transaction

---

25. DEVOPS

Provide:

- Docker
- Docker Compose
- Environment configuration
- Database migrations
- CI/CD
- Automated tests
- Security scanning
- Deployment documentation

Create:

.env.example

Never commit real secrets.

---

26. PROJECT STRUCTURE

Use a clean structure such as:

secure-pass-rxq/
│
├── mobile/
├── backend/
├── database/
├── infrastructure/
├── docs/
├── tests/
├── scripts/
├── .github/
│
├── docker-compose.yml
├── README.md
└── .env.example

Adapt it to the selected technology stack.

---

27. DOCUMENTATION

Create professional documentation:

- README
- Product Requirements Document
- Architecture
- Database schema
- API documentation
- Setup guide
- Development guide
- Testing guide
- Deployment guide
- Security guide
- Troubleshooting guide
- Provider integration guide

---

28. CODE QUALITY

Write clean and maintainable code.

Follow:

- SOLID principles where appropriate
- Separation of concerns
- DRY
- Clear naming
- Reusable components
- Type safety
- Proper error handling
- Meaningful comments
- Modular architecture

Never create fake production integrations.

Clearly mark:

MOCK
TODO
REQUIRES_PROVIDER_API

where applicable.

---

29. SELF-VERIFICATION

Before presenting code, verify:

- Code compiles
- Dependencies are correct
- Imports work
- Database migrations exist
- APIs are connected
- Navigation works
- Forms validate
- Error states work
- Secrets are protected
- Tests exist
- Mock integrations work
- Duplicate transactions are prevented
- Failure recovery works
- No obvious security vulnerabilities exist
- No dead buttons exist
- No broken references exist
- No placeholder content remains

Fix issues before moving forward.

Do not simply claim that something works.

---

30. DEVELOPMENT PHASES

Build the application incrementally.

Phase 1 — Product Definition

- Requirements
- Features
- User personas
- User stories
- User journey

Phase 2 — UI/UX

- Design system
- Wireframes
- Screens
- Navigation
- Components
- Responsive behavior

Phase 3 — Architecture

- System architecture
- Database architecture
- API architecture
- Security architecture

Phase 4 — Backend Foundation

- Project setup
- Database
- API framework
- Authentication

Phase 5 — Mobile Application

- Screens
- Navigation
- Authentication
- Home
- Send Data

Phase 6 — Operator System

- Operator detection
- Plans
- Mock adapters

Phase 7 — Payment

- Payment workflow
- Verification
- Webhooks
- Refunds

Phase 8 — Recharge

- Recharge workflow
- Status tracking
- Failure handling

Phase 9 — Transactions

- History
- Details
- Timeline
- Notifications

Phase 10 — Security

- Security hardening
- Rate limiting
- Fraud protection
- Audit logs

Phase 11 — Testing

- Unit
- Integration
- API
- UI
- Security
- Failure testing

Phase 12 — Deployment

- Docker
- CI/CD
- Cloud
- Monitoring
- Production configuration

---

31. DEVELOPMENT RULE

Do NOT generate the entire application in one huge response.

Work phase by phase.

After each phase:

1. Implement it.
2. Test it.
3. Review it.
4. Identify issues.
5. Fix issues.
6. Explain what was completed.
7. Explain what remains.
8. Continue to the next phase.

Never skip verification.

---

32. FIRST RESPONSE

Before writing implementation code, provide:

1. Complete PRD
2. Feature list
3. User personas
4. User stories
5. User journey
6. UI/UX specification
7. Design system
8. System architecture
9. Technology-stack recommendation
10. Database schema
11. API architecture
12. Security architecture
13. Testing strategy
14. DevOps architecture
15. Project structure
16. External API requirements
17. Risks and limitations
18. Development roadmap
19. MVP scope
20. Future features

Then wait for approval before writing the implementation.

---

33. QUALITY STANDARD

The final product must feel like a real commercial application.

Prioritize:

Correctness → Security → Reliability → User Experience → Performance → Visual Design

Do not sacrifice transaction correctness or security for convenience.

Always clearly distinguish:

- Implemented functionality
- Mock functionality
- External-provider functionality
- Unsupported functionality
- Production requirements

If a feature cannot be implemented without an external provider, explain the limitation and design the correct integration interface instead.

The final objective is a polished, secure, scalable, maintainable application:

SECURE PASS RxQ

Secure. Simple. Connected.# DataShare
