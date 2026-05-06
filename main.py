import asyncio
from datetime import date, timedelta
from typing import Optional

# ── In-memory data store ───────────────────────────────
books_db: dict[int, dict] = {
    1: {"id": 1, "title": "Clean Code",                "author": "Robert C. Martin", "category": "Programming",        "available": True},
    2: {"id": 2, "title": "Introduction to Algorithms","author": "Thomas H. Cormen", "category": "Computer Science",   "available": True},
    3: {"id": 3, "title": "Design Patterns",           "author": "Gang of Four",     "category": "Software Engineering","available": True},
    4: {"id": 4, "title": "Python Crash Course",       "author": "Eric Matthes",     "category": "Programming",        "available": True},
}

borrows_db: dict[int, dict] = {}
borrow_counter: int = 1

# ── ENDPOINT 1: GET /books ─────────────────────────────
async def get_books(
    title: Optional[str] = None,
    author: Optional[str] = None,
    category: Optional[str] = None
) -> dict:
    await asyncio.sleep(0.05)  # simulate network delay

    results: list[dict] = list(books_db.values())
    if title:    results = [b for b in results if title.lower()    in b["title"].lower()]
    if author:   results = [b for b in results if author.lower()   in b["author"].lower()]
    if category: results = [b for b in results if category.lower() in b["category"].lower()]

    return {"status": 200, "total": len(results), "books": results}


# ── ENDPOINT 2: POST /borrow ───────────────────────────
async def post_borrow(user_id: int, book_id: int) -> dict:
    global borrow_counter
    await asyncio.sleep(0.05)  # simulate network delay

    book: Optional[dict] = books_db.get(book_id)
    if not book:
        return {"status": 404, "error": f"Book ID {book_id} not found."}
    if not book["available"]:
        return {"status": 400, "error": f"'{book['title']}' is not available."}

    book["available"] = False
    due_date: date = date.today() + timedelta(days=14)

    record: dict = {
        "borrow_id":  borrow_counter,
        "user_id":    user_id,
        "book_id":    book_id,
        "title":      book["title"],
        "borrow_date":str(date.today()),
        "due_date":   str(due_date),
        "returned":   False,
        "fine":       0.0,
    }
    borrows_db[borrow_counter] = record
    borrow_counter += 1

    return {"status": 201, "message": "Book borrowed successfully.", "record": record}


# ── ENDPOINT 3: PUT /return ────────────────────────────
async def put_return(borrow_id: int, user_id: int) -> dict:
    await asyncio.sleep(0.05)  # simulate network delay

    record: Optional[dict] = borrows_db.get(borrow_id)
    if not record:
        return {"status": 404, "error": f"Borrow ID {borrow_id} not found."}
    if record["user_id"] != user_id:
        return {"status": 403, "error": "This borrow record does not belong to this user."}
    if record["returned"]:
        return {"status": 400, "error": "This book has already been returned."}

    today: date    = date.today()
    due: date      = date.fromisoformat(record["due_date"])
    fine: float    = round(max(0, (today - due).days) * 1.0, 2)

    record["returned"]    = True
    record["return_date"] = str(today)
    record["fine"]        = fine
    books_db[record["book_id"]]["available"] = True

    return {"status": 200, "message": "Book returned successfully.",
            "fine_amount": f"${fine:.2f}", "record": record}


# ── ENDPOINT 4: GET /overdue ───────────────────────────
async def get_overdue() -> dict:
    await asyncio.sleep(0.05)  # simulate network delay

    today: date = date.today()
    overdue: list[dict] = []

    for record in borrows_db.values():
        if not record["returned"]:
            due: date = date.fromisoformat(record["due_date"])
            if today > due:
                days_late: int  = (today - due).days
                fine: float     = round(days_late * 1.0, 2)
                overdue.append({**record, "days_overdue": days_late,
                                "estimated_fine": f"${fine:.2f}"})

    return {"status": 200, "total_overdue": len(overdue), "overdue_records": overdue}


# ── Helper: print response neatly ──────────────────────
def show(label: str, response: dict) -> None:
    status: int = response.get("status", 0)
    symbol: str = "✓" if status in (200, 201) else "✗"
    print(f"\n  {symbol} [{status}] {label}")
    for key, value in response.items():
        if key == "status":
            continue
        if key == "record":
            print(f"      record:")
            for k, v in value.items():
                print(f"        {k}: {v}")
        elif key == "books":
            print(f"      books ({len(value)} found):")
            for b in value:
                avail = "Available" if b["available"] else "Unavailable"
                print(f"        [{b['id']}] {b['title']} — {b['author']} | {avail}")
        elif key == "overdue_records":
            if value:
                print(f"      overdue_records:")
                for r in value:
                    print(f"        Borrow ID {r['borrow_id']} | {r['title']} | "
                          f"{r['days_overdue']} days late | Fine: {r['estimated_fine']}")
            else:
                print(f"      overdue_records: none")
        else:
            print(f"      {key}: {value}")


# ── MAIN: run all simulations ──────────────────────────
async def main() -> None:
    print("=" * 58)
    print("   LIMKOKWING LIBRARY API — CONSOLE SIMULATION")
    print("   PROG315 | Samuella Mary Kamara")
    print("=" * 58)

    # ── 1. Search books ────────────────────────────────
    print("\n>>> REQUEST: GET /books?category=Programming")
    show("GET /books", await get_books(category="Programming"))

    # ── 2. Borrow books (single) ───────────────────────
    print("\n>>> REQUEST: POST /borrow  {user_id: 101, book_id: 1}")
    show("POST /borrow", await post_borrow(user_id=101, book_id=1))

    print("\n>>> REQUEST: POST /borrow  {user_id: 102, book_id: 2}")
    show("POST /borrow", await post_borrow(user_id=102, book_id=2))

    # ── 3. Try borrowing unavailable book ─────────────
    print("\n>>> REQUEST: POST /borrow  {user_id: 103, book_id: 1}  [already taken]")
    show("POST /borrow", await post_borrow(user_id=103, book_id=1))

    # ── 4. Return a book ──────────────────────────────
    print("\n>>> REQUEST: PUT /return  {borrow_id: 1, user_id: 101}")
    show("PUT /return", await put_return(borrow_id=1, user_id=101))

    # ── 5. Try returning already-returned book ─────────
    print("\n>>> REQUEST: PUT /return  {borrow_id: 1, user_id: 101}  [already returned]")
    show("PUT /return", await put_return(borrow_id=1, user_id=101))

    # ── 6. Overdue check ──────────────────────────────
    print("\n>>> REQUEST: GET /overdue")
    show("GET /overdue", await get_overdue())

    # ── 7. ASYNC — Multiple users at the same time ────
    print("\n" + "=" * 58)
    print("   ASYNC SIMULATION — 4 users borrowing simultaneously")
    print("=" * 58)

    # Reset books for demo
    books_db[3]["available"] = True
    books_db[4]["available"] = True

    print("\n>>> asyncio.gather() — all 4 requests fire at the same time")
    results = await asyncio.gather(
        post_borrow(user_id=201, book_id=3),
        post_borrow(user_id=202, book_id=3),  # same book — should fail
        post_borrow(user_id=203, book_id=4),
        put_return(borrow_id=2, user_id=102),
    )

    labels: list[str] = [
        "User 201 borrows Design Patterns",
        "User 202 borrows Design Patterns (conflict)",
        "User 203 borrows Python Crash Course",
        "User 102 returns Introduction to Algorithms",
    ]
    for label, result in zip(labels, results):
        show(label, result)

    print("\n" + "=" * 58)
    print("   Simulation complete. All endpoints tested.")
    print("=" * 58 + "\n")


asyncio.run(main())
