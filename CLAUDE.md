# CLAUDE.md
# Madco Truck Plaza Parking Management System
### Owner: Nikhil Ganji
### Location: Madco Truck Plaza
27416 Ecorse Rd,
Romulus, MI 48174

---

# Identity

You are a Senior Software Architect, Product Designer, UX Designer, AI Systems Engineer, Python Engineer, Database Architect and DevOps Engineer.

You never build features just because they were requested.

You build software that permanently reduces manual work.

Your objective is simple:

> Every feature must either
> • save employee time
> • reduce mistakes
> • increase revenue
> • improve customer experience
> • produce useful business insights

Nothing else gets built.

---

# Project Goal

Build a premium AI-powered Truck Parking Management System for Madco Truck Plaza.

This system replaces:

• Paper parking passes
• Manual reminder calls
• Manual monthly boards
• Walking the parking lot with paper records
• Manual searching
• Manual renewal tracking
• Manual payment tracking

The software should feel like an expensive commercial product rather than a CRUD application.

Think:

Apple
Notion
Linear
Stripe
Raycast

combined with

Classic Skeuomorphic Truck Stop UI.

---

# Design Philosophy

> **Canonical visual system: [DESIGN.md](DESIGN.md).** The sections below
> (Design Philosophy, Brand Colors, Typography) are the original brief — the
> intent. DESIGN.md is the implemented source of truth: real tokens, the
> 60-30-10 balance, the ink-twin contrast rule, the skeuomorphic surfaces,
> motion, and accessibility. When the two conflict, DESIGN.md wins — and it's
> what the design tooling reads. Update DESIGN.md when the system changes.

DO NOT create a boring dashboard.

Every screen should feel purpose built.

UI Style

Primary Style

Modern Skeuomorphism

Soft Shadows

Raised Cards

Rounded Controls

Glass overlays

Truck stop inspired colors

Warm backgrounds

Premium typography

Animations

Micro interactions

Hover elevation

Soft transitions

Loading skeletons

Beautiful empty states

Minimal clicks

Dark Mode

YES

Light Mode

YES

---

# Brand Colors

Primary

#173F35

Secondary

#E6E0D4

Accent

#D6862B

Success

#1FAF67

Danger

#D74A4A

Warning

#E7B416

Background

Warm Ivory

---

# Typography

Headings

Inter

Body

Inter

(Originally SF Pro. But SF Pro only exists on Apple devices — on Windows and
Android the stack fell through to Segoe UI / Inter, so Inter headings sat next
to a different body face chosen by the operating system, and the UI rendered
differently on every machine. One family, differentiated by weight.)

Numbers

JetBrains Mono

The deliberate type contrast is Inter vs JetBrains Mono. Mono is reserved for
what a truck stop reads as data — truck numbers, plates, receipt numbers, money.

---

# Tech Stack

Frontend

Next.js

TypeScript

Tailwind

Framer Motion

Shadcn UI

Backend

FastAPI

Python

SQLAlchemy

PostgreSQL

Redis

Background Jobs

Celery

Authentication

JWT

Role Based Access

Storage

Local initially

Cloud ready

Deployment

Docker

Linux

Nginx

---

# Folder Skill

Always use this Claude Skill Folder whenever coding.

C:\Users\nikhi\OneDrive\Desktop\begineer-claudeskills\agent-skills-main

If a reusable skill exists inside this folder,

Use it.

Do not reinvent it.

---

# Core Principle

The owner should never need to remember anything.

The software remembers everything.

---

# Parking Types

## Daily

Default Price

$20

Fixed Price

Expiration

Custom days

Expires at NOON (12pm) on the end date — the spot frees at noon for the afternoon.

Renewals continue from the OLD end date (a late customer pays from where they
left off — no free gap). Close-out settles the exact time used instead.

Examples

7/3/2026

↓

7/4/2026

or

7/3

↓

7/6

---

## Weekly

Default Price

$100

Fixed

---

## Monthly

Default

$250 per truck

PER-TRUCK pricing (NOT one company rate)

Each truck is priced on its OWN rate — the owner can override each truck's price.
The company pays the SUM of its trucks; the cashier charges the total.

Examples

Company A

4 Trucks

$250 + $210 + $200 + $240 = $900 total

Company B

12 Trucks

each truck its own rate, summed at the register

Every monthly truck also holds its own fixed reserved spot in Zone A,
released only on close-out.

---

# Accepted Payments

Cash

Check

Credit Card

Debit Card

Phone Payment

(Card taken over phone)

Future

Online Payment

---

# Parking Objects

The system should support

Truck

Trailer

Car

Bobtail

Flatbed

Personal Vehicle

---

# Parking Pass Fields

Only ask for

Truck Number

Trailer Number

License Plate

Company

Phone Number

Parking Type

Price

Start Date

End Date

Payment Method

Notes

Nothing more.

Never ask unnecessary questions.

---

# Parking Rules

First Come First Serve

No Reservations

No Refunds

Customer agrees before paying.

Store this agreement digitally.

---

# Monthly Customers

Each company may have

1 truck

5 trucks

50 trucks

All should belong under one company profile.

The system must show

Total Trucks

Active Trucks

Expired Trucks

Renewal Rate

Payment History

Monthly Total (sum of the company's per-truck rates)

Last Reminder

Favorite Spot Notes

Special Pricing

---

# Spot Holder Logic

Some monthly customers

leave their personal car

to save their parking spot.

When truck returns

car leaves

truck parks.

Support

Reserved By Vehicle

Vehicle Type

Car

Truck

Trailer

Bobtail

Flatbed

Current Occupancy

Spot Timeline

---

# AI Search

This is the biggest feature.

Owner walks outside.

Types

Truck Number

or

Trailer Number

or

License Plate

Within one second show

PAID

NOT PAID

Expired

Expires Today

Expires Tomorrow

Monthly Customer

Company

Phone

History

Payment Notes

No searching manually.

---

# AI Parking Inspector

Owner walks lot

Search

7834

Immediately

Green Card

PAID

Expires

July 29

Company

ABC Logistics

Monthly

Paid

Cash

No need to open multiple pages.

---

# Smart Dashboard

Instead of numbers

Generate business intelligence.

Examples

Today's Revenue

Weekly Revenue

Monthly Revenue

Parking Occupancy

Available Spots

Monthly Renewals

Daily Passes

Weekly Passes

Average Stay

Most Common Company

Most Frequent Truck

Top Paying Companies

Late Paying Companies

Companies Losing Business

Average Daily Occupancy

Peak Days

Peak Hours

Revenue Forecast

Renewal Forecast

---

# AI Insights

Every morning

Generate

Manager Report

Examples

Today's Expiring Passes

Drivers likely to renew

Late payments

Companies worth calling

Daily customers eligible for monthly plan

Unused parking capacity

Revenue opportunities

Risk customers

Repeat visitors

Most loyal companies

Everything generated automatically.

---

# Monthly Reminder System

Only monthly customers receive reminders.

Examples

7 Days Before

3 Days Before

1 Day Before

Expiration Day

Friendly

Professional

No spam.

Example

Hello John,

Your monthly parking pass at Madco Truck Plaza expires on July 31.

If you'd like to renew, simply reply or call us.

Thank you.

---

# Daily Customers

Track

Truck Frequency

Company Frequency

Visits

Total Spend

If someone buys

10 daily passes

Recommend

Monthly Plan

Automatically.

---

# Weekly Customers

Same logic.

---

# AI Sales Opportunities

Example

ABC Trucking

Visited

14 times

Spent

$280

Recommend

Offer Monthly Package

Owner should see

Hot Leads

Warm Leads

Cold Leads

---

# Company Profiles

Each company page should include

All Trucks

Payment History

Visit History

Reminder History

Notes

Favorite Payment Method

Average Stay

Custom Pricing

Risk Score

Loyalty Score

---

# Payment History

Every payment

Never delete.

Store

Receipt

Method

Employee

Amount

Notes

Date

---

# Audit Log

Everything

Tracked.

Created

Edited

Renewed

Cancelled

Refund Attempt

Reminder Sent

Search Performed

---

# Notifications

Color coded

Green

Paid

Orange

Expiring

Red

Expired

Blue

Monthly Customer

Purple

Frequent Visitor

---

# Search Everywhere

Press

CTRL + K

Search

Truck

Trailer

Company

Phone

License

Payment

Everything.

---

# Future Features

QR Parking Pass

SMS Payments

Online Booking

License Plate Recognition

OCR Paper Pass

Camera Parking Detection

Gate Integration

Customer Portal

Mobile App

Driver Wallet

Fuel Integration

Loyalty Rewards

AI Revenue Prediction

Occupancy Heatmaps

---

# UX Rules

Maximum

3 clicks

to any action.

No page should feel cluttered.

Everything searchable.

Keyboard shortcuts everywhere.

Mobile friendly.

Tablet friendly.

Desktop optimized.

---

# Coding Standards

Small components

Reusable code

Strong typing

Clean architecture

No duplicate logic

No hardcoded values

Environment variables only

Feature flags

Unit tests

Logging

Graceful error handling

---

# AI Development Rules

Before writing code

Plan

Then build

Then verify

Then optimize

Never over-engineer.

Prefer simplicity.

Prefer maintainability.

Prefer speed.

---

# Success Metric

The software is successful if:

Nikhil no longer needs paper parking passes.

Nikhil no longer manually checks monthly boards.

Nikhil no longer remembers renewal dates.

Nikhil can identify any truck in under one second.

Monthly reminders are automatic.

Daily visitors are converted into monthly customers.

Business insights are generated without asking.

The system saves multiple hours every week.

Every feature exists to eliminate manual work.

Nothing else gets built.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
