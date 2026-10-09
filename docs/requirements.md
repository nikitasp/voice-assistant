# Product Requirements Document

## Voice Concierge
*for The Meridian Casino & Resort*

*Software Engineer Take-Home Assessment*

**CONFIDENTIAL**

## Overview
The Meridian Casino & Resort is a luxury destination in Las Vegas. We need a voice-based concierge system that allows guests to ask questions and receive instant, spoken answers about our property, amenities, and services. The system should capture questions we can't answer so our team can continuously improve coverage.

This assessment consists of a core assignment and a bonus challenge. The core assignment focuses on building the voice agent and backend infrastructure. The bonus challenge adds an admin panel for content management.

## Problem Statement
Our concierge desk and phone lines are overwhelmed with repetitive questions — hours, restaurant reservations, game availability, room types. Guests expect instant answers at 3 AM when they want to know if the poker room is open. Meanwhile, we have no visibility into what guests are asking that we can't help with, meaning we miss opportunities to improve our service.

## Goals
### Core Goals
- Provide 24/7 instant voice support for common guest questions
- Capture unanswered questions for later review
- Maintain the luxury, personalized feel guests expect from The Meridian
- Provide a playground interface to test the voice concierge

### Bonus Goals
- Allow staff to manage FAQ content through an admin panel
- Review and convert unanswered questions to FAQs
- Configure voice personality through the admin interface
- Integrate the playground into the admin panel

## User Personas
### Guest (Core)
- Staying at the hotel or visiting the casino
- Wants quick, accurate information without waiting on hold
- Expects a polished, professional experience befitting a luxury property
- May ask about gaming, dining, accommodations, entertainment, or local partners

### Concierge Manager (Bonus)
- Manages FAQ content and ensures accuracy
- Reviews questions the system couldn't answer
- Adds new information based on guest inquiries
- Configures voice personality to match brand standards
- Tests the concierge experience before deploying changes

## Functional Requirements: Core
### Voice Concierge

| ID | Requirement |
| --- | --- |
| VC-1 | Guest can speak to the concierge through a web interface |
| VC-2 | Concierge understands natural language questions |
| VC-3 | Concierge searches knowledge base to find relevant answers |
| VC-4 | Concierge responds verbally with the answer when found |
| VC-5 | When no answer exists, concierge apologizes gracefully and confirms the question has been noted |
| VC-6 | Tone should be warm, professional, and consistent with luxury hospitality |

### Knowledge Base

| ID | Requirement |
| --- | --- |
| KB-1 | Store FAQ items covering all property information |
| KB-2 | Support natural language matching (not just keywords) |
| KB-3 | Store unanswered questions with timestamp |
| KB-4 | Track frequency of each unanswered question |
| KB-5 | Seed with provided Meridian property information |

### Backend API
The backend should expose endpoints for the voice agent to interact with the knowledge base.

| ID | Requirement |
| --- | --- |
| API-1 | Endpoint to search FAQ items by question/query |
| API-2 | Endpoint to record an unanswered question |
| API-3 | FAQ search should return the best matching answer or indicate no match found |

### Playground Interface
A simple web interface to test the voice concierge. This can be the LiveKit Agents Playground or a custom implementation.

| ID | Requirement |
| --- | --- |
| PG-1 | Web-based interface accessible via browser |
| PG-2 | Microphone input to speak to the concierge |
| PG-3 | Audio output to hear concierge responses |
| PG-4 | Visual indicator showing connection/conversation status |
| PG-5 | Ability to start and end conversations |

*Note: The LiveKit Agents Playground ([LiveKit Agents Playground](https://agents-playground.livekit.io)) can be used as the playground interface, or you may build a custom one.*

## Functional Requirements: Bonus
The following requirements are optional bonus challenges. Complete the core requirements first.

### Voice Configuration

| ID | Requirement |
| --- | --- |
| VX-1 | System supports 4 distinct voice options |
| VX-2 | Admin can select active voice from admin panel |
| VX-3 | Voice change takes effect immediately for new conversations |
| VX-4 | Admin can preview each voice before selecting |

#### Voice Options

| Voice ID | Name | Description |
| --- | --- | --- |
| 1 | James | Male, mature, warm British accent. Professional and refined. |
| 2 | Sofia | Female, friendly, subtle European accent. Welcoming and elegant. |
| 3 | Marcus | Male, American, confident and energetic. Modern and approachable. |
| 4 | Elena | Female, American, calm and reassuring. Sophisticated and clear. |

*Note: Actual voice implementation will depend on TTS provider capabilities. These descriptions represent the target personality for each voice.*

### Admin Panel
A React-based admin panel for managing the concierge system.

#### FAQ Management

| ID | Requirement |
| --- | --- |
| AP-1 | View all FAQ items |
| AP-2 | Add new FAQ item |
| AP-3 | Edit existing FAQ item |
| AP-4 | Delete FAQ item |

#### Unanswered Questions

| ID | Requirement |
| --- | --- |
| AP-5 | View unanswered questions queue |
| AP-6 | See frequency count for each unanswered question |
| AP-7 | Convert unanswered question to FAQ by providing an answer |
| AP-8 | Dismiss irrelevant questions |

#### Voice Configuration UI

| ID | Requirement |
| --- | --- |
| AP-9 | View available voice options with descriptions |
| AP-10 | Select active voice for the concierge |
| AP-11 | Preview button to hear sample from each voice |
| AP-12 | Display which voice is currently active |

#### Integrated Playground

| ID | Requirement |
| --- | --- |
| AP-13 | Embedded voice interface to test the concierge within the admin panel |
| AP-14 | Playground uses current voice and FAQ configuration |
| AP-15 | Allows admin to have full voice conversation with the concierge |
| AP-16 | Clearly labeled as "Test Mode" or "Playground" |

## Functional Requirements: Additional (internal)
*Added by the implementation team; not part of the original PRD. Purpose: make the concierge's behaviour easy to check question by question.*

### Text Chat

| ID | Requirement |
| --- | --- |
| TC-1 | Guest can type a question in the playground instead of speaking |
| TC-2 | Concierge replies to typed questions; the playground shows a transcript of both sides of the conversation |
| TC-3 | Text and voice use the same agent, prompt, tools and knowledge base — no separate chat implementation |
| TC-4 | The agent can run a text-only session without STT/TTS, used by automated tests |
| TC-5 | A command-line tool sends a question (or a file of questions) to the agent in text mode and prints the reply and the tools it called |

## Property Information (Seed Data)
### General Information

| Topic | Details |
| --- | --- |
| Property Name | The Meridian Casino & Resort |
| Location | Las Vegas Strip, Nevada |
| Casino Hours | 24 hours, 7 days a week |
| Hotel Check-in | 4:00 PM (early check-in subject to availability) |
| Hotel Check-out | 11:00 AM (late checkout available for suite guests) |
| Valet Parking | Complimentary for hotel guests, $25 for visitors |
| Self Parking | Free for all guests |
| Dress Code | Smart casual throughout property; formal attire required at Aurelia restaurant and Eclipse Lounge |
| Age Requirement | 21+ for casino floor and bars; all ages welcome in hotel and family restaurants |
| Wi-Fi | Complimentary throughout property; premium high-speed available in suites |

### Casino Gaming

| Game/Area | Details |
| --- | --- |
| Slot Machines | Over 2,000 machines ranging from $0.01 to $1,000 per spin. Includes latest video slots, classic reels, and progressive jackpots. Largest jackpot currently at $4.2 million. |
| Blackjack | 40 tables, minimums from $25 to $10,000. Single deck, 6-deck, and Spanish 21 available. |
| Poker Room | 24/7 operation. Texas Hold'em (No Limit and Limit), Omaha, and Seven Card Stud. Daily tournaments at 11 AM and 7 PM. $200 buy-in for daily tournaments. |
| Roulette | 12 tables including American, European, and French roulette. Minimums from $15. |
| Baccarat | 8 tables in main casino, private high-limit salon with 4 tables. Minimums from $50, high-limit from $5,000. |
| Craps | 6 tables, minimums from $15. Lessons available daily at 10 AM. |
| Sports Book | 80-seat theater with 40-foot screen. Full bar service. Mobile betting available throughout property via Meridian app. |
| High Limit Salon | Private gaming area with dedicated hosts. By invitation or $50,000 credit line. Private restrooms, complimentary dining, personal butler service. |
| Players Club | Meridian Rewards program. Earn points on all play. Tiers: Gold, Platinum, Diamond, and invite-only Black. |

### Accommodations

| Room Type | Details |
| --- | --- |
| Deluxe Room | 450 sq ft. King or two queens. City or pool view. From $299/night. |
| Premier Room | 550 sq ft. King bed, sitting area. Strip view. From $449/night. |
| Luxury Suite | 900 sq ft. Separate living room, marble bathroom with soaking tub. From $799/night. |
| Penthouse Suite | 1,800 sq ft. Two bedrooms, dining room, butler's pantry, private terrace. From $2,500/night. |
| Chairman's Villa | 4,500 sq ft. Three bedrooms, private pool, personal chef available, 24-hour butler. By inquiry only. |
| Accessible Rooms | Available in all categories. Roll-in showers, lowered amenities, visual alerts. Request at booking. |

### On-Property Restaurants

| Restaurant | Details |
| --- | --- |
| Aurelia | Fine dining. Modern French cuisine by Chef Marcus Webb (2 Michelin stars). Tasting menu $285 per person, à la carte available. Dinner only, 6 PM - 10 PM. Reservations required. Formal attire. |
| Silk Road | Pan-Asian cuisine. Sushi bar, robata grill, dim sum. Open 11 AM - 11 PM daily. Reservations recommended for dinner. Smart casual. Prices $40-80 per person. |
| The Steakhouse | Classic American steakhouse. Dry-aged beef, fresh seafood. Open 5 PM - 11 PM. Reservations recommended. Smart casual. Prices $70-150 per person. |
| Café Meridian | Casual all-day dining. Breakfast buffet 7-11 AM ($45). Lunch and dinner menu until midnight. No reservations needed. |
| Pool Bar & Grill | Poolside casual. Burgers, salads, cocktails. 10 AM - 6 PM (seasonal). Hotel guests only. |

### Bars & Lounges

| Venue | Details |
| --- | --- |
| Eclipse Lounge | Rooftop bar with Strip views. Craft cocktails, champagne menu. Open 5 PM - 2 AM. Formal attire after 8 PM. |
| The Vault | Whiskey and cigar lounge. 400+ whiskey selections. Humidor with premium cigars. Open 4 PM - 2 AM. 21+. |
| Casino Floor Bars | 6 bars throughout casino. Complimentary drinks for active players. Full service available. |

### Entertainment & Amenities

| Amenity | Details |
| --- | --- |
| Meridian Spa | Full-service spa and salon. Massage, facials, body treatments. Couples suites available. Open 8 AM - 8 PM. Book 24 hours in advance recommended. |
| Fitness Center | 24-hour access for hotel guests. Personal training available. Peloton bikes, free weights, yoga studio. |
| Pool Complex | Three pools including adults-only infinity pool. Cabanas from $300/day (includes $100 food credit). Open 8 AM - 8 PM. |
| Meridian Theater | 1,200-seat venue. Current residency: internationally acclaimed artists (check website for schedule). Tickets from $95. VIP packages available. |
| Nightclub - NOVA | Premier nightclub. Open Friday and Saturday, 10:30 PM - 4 AM. Cover $50 general, tables from $2,000. Guest list available for hotel guests. |

### Celebrations & Special Events

| Service | Details |
| --- | --- |
| Weddings | Multiple venues from intimate chapel to grand ballroom. Packages from $5,000 to $150,000. Wedding coordinator included in all packages. |
| Private Events | Meeting rooms and ballrooms from 500 to 15,000 sq ft. Full catering and AV services. Corporate rates available. |
| Birthday/Anniversary | Celebration packages include room upgrade, champagne, custom cake, and dinner credit. From $500 additional. 72-hour advance notice required. |
| Bachelor/Bachelorette | VIP packages including suite, nightclub table, pool cabana, and spa credits. Starting at $3,000. Must book 1 week in advance. |

### Partner Discounts (Show Room Key)

| Partner | Discount |
| --- | --- |
| Carbone (Italian fine dining, 5 min away) | 15% off food, priority reservations |
| Omega Mart (Immersive art experience) | $10 off admission |
| Helicopter Tours - Vegas Nights Aviation | 20% off Strip tours, complimentary champagne |
| Top Golf Las Vegas | Free hour with 2-hour booking |
| Spa Aquae at JW Marriott | 10% off treatments (when Meridian Spa fully booked) |
| Fremont Street Experience | VIP SlotZilla pass, skip the line |

## Example Conversations
#### Scenario 1: Gaming Question
Guest: "Is the poker room open right now?"
Concierge: "Yes, our poker room is open 24 hours a day, 7 days a week. We offer Texas Hold'em, Omaha, and Seven Card Stud. There's also a tournament starting at 7 PM tonight with a $200 buy-in if you're interested."

#### Scenario 2: Dining Recommendation
Guest: "What's your best restaurant?"
Concierge: "Our signature restaurant is Aurelia, featuring modern French cuisine by Chef Marcus Webb — it holds two Michelin stars. It's open for dinner from 6 to 10 PM and does require reservations and formal attire. If you'd prefer something more casual, Silk Road offers excellent Pan-Asian cuisine and The Steakhouse is perfect for classic American dining."

#### Scenario 3: Unknown Question
Guest: "Can I bring my dog to the hotel?"
Concierge: "I don't have information about pet policies at the moment, but I've noted your question for our team. You can also reach our front desk directly at extension 0. Is there anything else I can help you with?"

#### Scenario 4: Partner Discount
Guest: "Are there any good restaurants nearby you'd recommend?"
Concierge: "Absolutely. Carbone is an excellent Italian fine dining option about five minutes away, and Meridian guests receive 15% off and priority reservations — just show your room key. We also have three restaurants on property if you'd prefer to stay in."

#### Scenario 5: Celebration Planning
Guest: "I want to propose to my girlfriend this weekend. Can you help?"
Concierge: "How exciting! We have several special options. Our celebration packages start at $500 and include a room upgrade, champagne, and dinner credit. For something more elaborate, Eclipse Lounge offers private terrace reservations with stunning Strip views. I'd recommend speaking with our concierge desk to plan the perfect moment — would you like their direct number?"

## Non-Functional Requirements

| ID | Requirement |
| --- | --- |
| NF-1 | Voice response should feel conversational and prompt |
| NF-2 | System should run locally via Docker for evaluation |
| NF-3 | Admin panel should be usable on desktop browsers |
| NF-4 | Concierge tone should reflect luxury hospitality brand |
| NF-5 | Voice selection change should apply without system restart |

## Out of Scope
- Actual reservation booking (just provide information)
- Payment processing
- Integration with property management systems
- User authentication for admin panel
- Guest-facing standalone website (guests use playground in admin for this exercise)
- Mobile app
- Multi-language support

## Technical Constraints
Required for compatibility with existing infrastructure:

#### Core

| Component | Allowed Technologies |
| --- | --- |
| Backend API | .NET, Java, Node.js/JavaScript, or Python (any framework) |
| Voice Agent | Python or JavaScript/TypeScript |
| Voice Infrastructure | LiveKit |
| Playground | LiveKit Agents Playground or custom implementation |

#### Bonus

| Component | Allowed Technologies |
| --- | --- |
| Admin Panel | React |

All other technical decisions (database, search approach, LLM provider, architecture patterns, communication protocols) are at implementer's discretion.

## Provided Resources
- LiveKit API credentials
- LLM API key
- STT/TTS service credentials (supporting multiple voices)

## Deliverables
### Core (Required)
- Working voice agent that answers FAQ questions
- Backend API with FAQ search and unanswered question recording
- Database seeded with Meridian property information
- Playground interface to test the voice concierge
- System launchable with a single command (e.g., docker-compose up)
- README with setup instructions
- Brief document explaining key technical decisions

### Bonus (Optional)
- React admin panel with FAQ management
- Unanswered questions queue with convert-to-FAQ functionality
- Voice configuration UI with 4 voice options and preview
- Integrated playground within the admin panel

## Success Criteria
### Core (Required)

| Area | Criteria |
| --- | --- |
| Voice Conversation | Can have natural voice conversation about Meridian property |
| FAQ Lookup | Returns accurate, relevant answers from knowledge base |
| Unknown Questions | Records unanswered questions to database |
| Playground | Can test the voice concierge through a web interface |
| Overall Experience | Feels like speaking with a knowledgeable, professional concierge |

### Bonus (Optional)

| Area | Criteria |
| --- | --- |
| FAQ Management | Admin can view, add, edit, delete FAQ items |
| Question Queue | Admin can review and convert unanswered questions to FAQs |
| Voice Selection | Admin can choose between 4 voices, change applies immediately |
| Voice Preview | Admin can hear sample of each voice before selecting |
| Integrated Playground | Admin can test full voice experience within the admin panel |

---

## Questions?

Contact us:

- jenya@rocketdreams.co
- +972 54-524-1285

