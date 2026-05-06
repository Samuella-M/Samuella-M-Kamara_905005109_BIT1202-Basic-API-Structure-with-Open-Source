# Limkokwing Library API

**PROG315 — Object-Oriented Programming 2**
Limkokwing University of Creative Technology — Sierra Leone
Student: Samuella Mary Kamara

---

## Description

A console-based Python simulation of a RESTful library management API for Limkokwing University. Demonstrates async/await programming, type annotations, and concurrent user handling using only Python's standard library.

---

## How to Run

```bash
python main.py
```

No external libraries needed. Requires Python 3.11+.

---

## Endpoints Simulated

| Function | Simulates | Description |
|---|---|---|
| `get_books()` | GET /books | Search by title, author, or category |
| `post_borrow()` | POST /borrow | Borrow a book, sets 14-day due date |
| `put_return()` | PUT /return | Return a book, calculates overdue fine |
| `get_overdue()` | GET /overdue | List all overdue books with fines |

---

## Features

- Full type annotations on all functions
- `async/await` on every endpoint handler
- `asyncio.gather()` simulates multiple concurrent users
- Race condition handling (two users borrowing same book)
- HTTP-style status codes (200, 201, 400, 403, 404)
- Runs entirely in the terminal — no server required

---

## SDG Alignment

**SDG 4 — Quality Education**: Digitising library access removes barriers for students across Sierra Leone.

---

## License

MIT License