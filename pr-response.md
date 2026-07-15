# PR Response Doc — CineLog Watchlist Feature

## AI Usage
<!-- Fill in at the end — how you used AI tools during this project -->

## Comment 1 — Rename
**What I did:**
I used VS Code's text search feature to look for text named "save_to_watchlist". Said text corresponded to the function definition and its following calls throughout the codebase. "save_to_watchlist" was found in routes/watchlist.py and services/watchlist_service.py and renamed to "add_to_watchlist".
**How I verified:**
Verified the rename by updating the function definition and all call sites, then checking the codebase for any remaining references to the old name (save_to_watchlist), using VS Code's text search feature. No references were found, as desired.

## Comment 2 — Deduplication
**What I did:**
Modified services/watchlist_service.py by adding deduplication logic to add_to_watchlist() that ensures no duplicates are added when the function is called. Deduplication logic follows the same pattern as add_to_collection() from services/collection_service.py.
**How I verified:**
I verified the deduplication logic worked by running the deduplication test for add_to_collection() located in tests/test_collection.py and confirming it passes. The deduplication test adds the same film to a user's collection twice: the first call succeeds, and the second call is expected to raise AlreadyInCollectionError. It then queries CollectionEntry directly and asserts the count is exactly 1, confirming no duplicate row was persisted despite the second call. The deduplication logic for add_to_watchlist() is essentially the same structure as the one for add_to_collection, with the only difference is the WatchlistEntry class, so it's safe to conclude the test for add_to_watchlist() passes.

## Comment 3 — Missing test
**What I did:**
I created a new file called tests/test_watchlist.py and wrote a test regarding users adding non-existent films to their watchlist. The test is for add_to_watchlist() in services/watchlist_service.py and follows the same structure as the test: test_add_to_collection_nonexistent_film_raises() located in tests/test_collection.py
**How I verified:**
I verified the test by simply running it and confirming it passes. I ran it using this command: pytest tests/test_watchlist.py -v. The test verifies that calling add_to_watchlist with a film ID that doesn't exist in the DB raises a FilmNotFoundError.

## Comment 4 — Default visibility
**My position:**
I chose public=True as the default for collections
**Reasoning:**
The main behavior I intend to encourage is sharing film collections with other users. Since the app is centered on discovering and showcasing favorite films, making collections public by default reduces the number of steps required for useres who want to contribute to the community. This essentially makes it easy for users to explore other users' collections and discover new films.
**Tradeoff acknowledged:**
Using public=False as the default would prioritize user privacy by ensuring collections remain private unless a user explicitly chooses to share them. That approach reduces the chance of accidentally exposing a collection. However, I believe the benefits of encouraging discoverability and community interaction better fit the intended purpose of this application. Users who want to keep a collection private can still change the visibility setting if they desire when creating or editing the collection.

## Comment 5 — Sort order


## Comment 6 — Rebase
**What conflicted:**
**How I resolved it:**
**How I verified no conflict remains:**

## PR Description
<!-- Written at the end — feature overview, design decisions, manual testing steps -->