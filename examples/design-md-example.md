---
version: alpha
name: Heritage
colors:
  primary: "#1A1C1E"
  secondary: "#6C7278"
  tertiary: "#B8422E"
  neutral: "#F7F5F2"
  on-primary: "#FFFFFF"
typography:
  h1:
    fontFamily: Public Sans
    fontSize: 48px
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: -0.02em
  body-md:
    fontFamily: Public Sans
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
rounded:
  sm: 4px
  md: 8px
spacing:
  sm: 8px
  md: 16px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.sm}"
    padding: 12px
---

## Overview

Architectural Minimalism meets Journalistic Gravitas.

## Colors

Use deep ink for primary text, warm limestone for surfaces, and Boston Clay for the main call to action.

## Typography

Use Public Sans for headings and body copy.

## Layout

Use an 8px spacing scale.

## Components

Primary buttons use the `button-primary` component token.

## Do's and Don'ts

- Do use the primary color for core text and the most important action.
- Don't introduce unregistered raw colors in UI code.
