# Swing Sensei

Swing Sensei is a personal AI-powered badminton coach that makes training more accessible, interactive, and actionable. It helps players improve even without access to a coach, training partner, or formal lessons by providing live, targeted feedback on form and an AI-generated summary after each session.

## Devpost
[Devpost Submission cmd-f 2026 - Swing Sensei](https://devpost.com/software/swing-sensei?_gl=1*5csmcu*_gcl_au*MTg2NTY1OTg5Ni4xNzcwNjgyMzgw*_ga*MTM0NjMxMjIyMy4xNzU5NjM3Mzc4*_ga_0YHJK3Y10M*czE3NzYwNTg2MzYkbzM1JGcxJHQxNzc2MDU4NjQ4JGo0OCRsMCRoMA..)

## Inspiration

Badminton is a fast and technical sport, but quality coaching is not always easy to access. Newer players often do not know what to correct, and even experienced players can struggle to notice small mistakes in their own form without outside feedback.

Swing Sensei was inspired by the idea of making coaching more accessible through computer vision and AI. We wanted to create a tool that feels like a supportive training partner: one that watches your swing, gives you real-time guidance, and helps you improve over time.

## What It Does

Swing Sensei offers two main experiences:

- A landing page that introduces the project and provides training resources
- A live training mode where users can log in, practice their swing, and receive AI-powered feedback

Users can create an account or log in with email. During a live session, the camera tracks the user’s motion and analyzes their swing in real time. Swing Sensei then gives immediate feedback such as:

- “Lift arm”
- “Good swing”

After the session, movement data is sent to Gemini to generate a more detailed coaching summary. This gives users both instant corrections during practice and more reflective feedback afterward.

## Features

- Live badminton swing analysis
- Real-time voice feedback
- Post-session AI-generated coaching summary
- User authentication with account persistence
- Resource landing page and training interface
- Focused feedback on form areas such as arm or elbow

## How We Built It

### Frontend
We used **React** to build the main user-facing interface, including the landing page, login flow, and navigation between resources and live training.

### Motion Analysis
We used **Streamlit** for the live motion-analysis pipeline and embedded it into the React experience to connect a polished frontend with a functional computer vision backend.

### Authentication and Backend
We used **Supabase** for authentication and account management, allowing users to sign up, log in, and return for future sessions.

### Computer Vision
We used **MediaPipe** to extract body landmarks from the live camera feed. From those landmarks, we calculated joint angles and wrist motion velocity to evaluate swing quality.

### AI and Voice Feedback
We used the **Gemini API** to turn session movement data into a natural-language coaching summary. We also used **ElevenLabs** to provide spoken feedback during training sessions, making the experience feel more interactive and coach-like.

## Challenges We Ran Into

One of the biggest challenges was integrating multiple parts of the project into one smooth experience:

- React frontend
- Streamlit live analysis
- Supabase authentication
- MediaPipe pose tracking
- Gemini summarization

We also had to figure out how to turn raw pose data into meaningful feedback. Detecting landmarks is one thing, but deciding what makes a swing strong or weak required careful thinking about arm angle, elbow position, and motion speed.

## Accomplishments We’re Proud Of

We are proud that Swing Sensei creates a full coaching loop:

1. The user signs in  
2. Practices live  
3. Receives real-time voice feedback  
4. Gets a post-session AI summary

We are also proud that the project brought together UI design, authentication, computer vision, geometry, and generative AI into one practical tool.

## What We Learned

This project taught us a lot about building full-stack systems under hackathon time pressure. We learned how to:

- Connect React and Streamlit into one product flow
- Use Supabase for login and account persistence
- Work with MediaPipe pose landmarks for motion analysis
- Translate technical measurements into user-friendly feedback with Gemini

We also learned that a strong AI product is not just about technical accuracy — it is about giving users advice they can actually understand and use.

## What’s Next

We would love to expand Swing Sensei further by:

- Supporting more shot types such as clears, drops, and smashes
- Adding long-term progress tracking for users
- Generating personalized drills based on repeated mistakes
- Improving feedback accuracy with more motion features and training data
- Polishing the platform for real-world use

Our long-term vision is to make Swing Sensei feel like a true AI training companion for badminton players at any level.

## Tech Stack

- React
- Streamlit
- Supabase
- MediaPipe
- Gemini API
- ElevenLabs
- JavaScript / TypeScript
- Python
- HTML/CSS

## Built With

`react` `streamlit` `supabase` `mediapipe` `gemini` `elevenlabs` `javascript` `typescript` `python` `html` `css`
<!-- 
## Team

_Add team member names here_

## Demo

_Add demo link here_

## Screenshots

_Add screenshots or GIFs here_

## License

_Add license here_
-->
