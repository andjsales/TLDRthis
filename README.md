API Url: https://rapidapi.com/tldrthishq-tldrthishq-default/api/tldrthis

# TLDRthis - Summary Generator Website

## Overview

TLDRthis is a web application designed to provide quick and concise summaries of lengthy content. It's the perfect tool for users who want to grasp the main points of an article, blog post, or any web-based content without spending too much time reading!

## Features

- Summarize Content: Users can submit a URL, and the app returns a summarized version of the content.
- User Authentication: Features a secure user authentication system for signup, login, and logout.
- Profile Management: Users can view their profile, edit details, and delete their account.
- Folder System: Organize summaries into custom folders for easy access and management.
- History: Users can view their history of generated summaries.
- Responsive Design: Accessible across various devices with a user-friendly interface.

## Setup

1. `pip install requirements.txt`
2. `brew install postgresql`
3. `createdb tldrthis_db`

4. Make sure to set environment variables:

```bash
export DATABASE_URL="postgresql://username:password@localhost/tldrthis_db"
export SECRET_KEY="your_secret_key
```

5. Initialize database: `flask db upgrade`
6. `flask run`

## Features

- **Summarize Content**: Users can submit URLs, and the application returns a summarized version of the content.
- **User Authentication**: Secure system for signup, login, and logout.
- **Profile Management**: Users can view and edit their profiles, and delete their accounts.
- **Folder System**: Allows users to organize summaries into custom folders.
- **History**: Users can view their history of generated summaries.
- **Responsive Design**: The interface is user-friendly and accessible on various devices.

## User Flow

1. **Homepage**: Visitors are greeted with a form to input a URL for summarization.
2. **Signup/Login**: Users can create an account or log in to access personalized features.
3. **Summarization**: Authenticated users can start summarizing content.
4. **Folders**: Users can create, view, and manage folders to organize their summaries.
5. **Profile Management**: Users can edit their profile details or delete their account.

## API Usage

The application utilizes an API to provide reliable and quick content analysis and summarization.

## Technology Stack

- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Backend**: Python, Flask
- **Database**: PostgreSQL
- **Additional Tools**: SQLAlchemy, Flask-WTF, Jinja2
