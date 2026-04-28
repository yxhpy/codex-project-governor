---
version: alpha
name: Example Technical SaaS
colors:
  primary: "#0B0F17"
  secondary: "#64748B"
  accent: "#047857"
  surface: "#FFFFFF"
  surface-muted: "#F8FAFC"
  border: "#E2E8F0"
  danger: "#DC2626"
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: -0.03em
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: 600
    lineHeight: 1.2
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
rounded:
  sm: 6px
  md: 12px
  lg: 18px
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.surface}"
    rounded: "{rounded.md}"
    padding: 12px
  card-default:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.primary}"
    rounded: "{rounded.lg}"
    padding: 24px
---

# Example Technical SaaS

## Overview

Precise, technical, calm, and low-noise. The interface should feel like a serious developer tool, not a generic marketing template.

## Colors

Accent green is reserved for primary action, success, and active technical indicators. Neutral surfaces do most of the work.

## Typography

Headlines use Inter with tight spacing. Technical labels and metrics may use JetBrains Mono.

## Layout

Use contained sections and clear information hierarchy. Avoid decorative gradients unless they clarify status or product narrative.

## Components

Cards are quiet and spacious. Primary buttons use the accent token only.

## Do's and Don'ts

Do not use arbitrary blue or purple Tailwind classes. Do not create new shadows without adding elevation rationale.
