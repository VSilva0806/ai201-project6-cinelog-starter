import pytest
from app import create_app, db
from models import User, Film, WatchlistEntry
from services.watchlist_service import (
    add_to_watchlist,
    remove_from_watchlist,
    get_watchlist,
    FilmNotFoundError,
    AlreadyInCollectionError,
    NotInCollectionError,
)

@pytest.fixture
def app():
    """Create an isolated test app with an in-memory database."""
    app = create_app(config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_user(app):
    """A user to use in tests."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        db.session.add(user)
        db.session.commit()
        return user.id
    
@pytest.fixture
def sample_film(app):
    """A film to use in tests."""
    with app.app_context():
        film = Film(title="Paddington 2", year=2017, genre="Comedy")
        db.session.add(film)
        db.session.commit()
        return film.id
    ___________________________________________________________________________________________________
    
def test_add_to_watchlist_nonexistent_film_raises(app, sample_user):
    """
    Adding a film_id that doesn't exist in the database should raise
    FilmNotFoundError, not a database integrity error.
    """
    with app.app_context():
        fake_film_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(FilmNotFoundError):
            add_to_watchlist(user_id=sample_user, film_id=fake_film_id)


def test_add_to_watchlist_duplicate_raises(app, sample_user, sample_film):
    """
    Adding the same film twice should raise AlreadyInCollectionError,
    not silently create a duplicate entry.
    """
    with app.app_context():
        add_to_watchlist(user_id=sample_user, film_id=sample_film)

        with pytest.raises(AlreadyInCollectionError):
            add_to_watchlist(user_id=sample_user, film_id=sample_film)

        # Confirm only one entry exists
        count = WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).count()
        assert count == 1


def test_add_to_watchlist_explicit_public_false(app, sample_user, sample_film):
    """
    Passing public=False should override the default and persist as private.
    """
    with app.app_context():
        entry = add_to_watchlist(user_id=sample_user, film_id=sample_film, public=False)
        assert entry.public is False

        in_db = WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).first()
        assert in_db.public is False


def test_remove_from_watchlist_removes_entry(app, sample_user, sample_film):
    """
    Removing a film that is on the watchlist should delete its entry.
    """
    with app.app_context():
        add_to_watchlist(user_id=sample_user, film_id=sample_film)

        removed = remove_from_watchlist(user_id=sample_user, film_id=sample_film)
        assert removed is True

        # Confirm no entry remains
        in_db = WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).first()
        assert in_db is None


def test_remove_from_watchlist_not_present_raises(app, sample_user, sample_film):
    """
    Removing a film that isn't on the watchlist should raise
    NotInCollectionError, not silently succeed.
    """
    with app.app_context():
        with pytest.raises(NotInCollectionError):
            remove_from_watchlist(user_id=sample_user, film_id=sample_film)


def test_get_watchlist_sorts_by_date_added_desc(app, sample_user):
    """The watchlist should return the most recently added film first."""
    with app.app_context():
        first_film = Film(title="A First Film", year=2000)
        second_film = Film(title="Z Second Film", year=2020)
        db.session.add_all([first_film, second_film])
        db.session.commit()

        add_to_watchlist(user_id=sample_user, film_id=first_film.id)
        add_to_watchlist(user_id=sample_user, film_id=second_film.id)

        titles = [film["title"] for film in get_watchlist(sample_user)]
        assert titles == ["Z Second Film", "A First Film"]


def test_get_watchlist_search_filters_by_title(app, sample_user):
    """Searching should return only films whose title matches, case-insensitively."""
    with app.app_context():
        paddington = Film(title="Paddington 2", year=2017)
        other = Film(title="The Matrix", year=1999)
        db.session.add_all([paddington, other])
        db.session.commit()

        add_to_watchlist(user_id=sample_user, film_id=paddington.id)
        add_to_watchlist(user_id=sample_user, film_id=other.id)

        results = get_watchlist(sample_user, search="paddington")
        assert [film["title"] for film in results] == ["Paddington 2"]


def test_get_watchlist_search_no_matches_returns_empty_list(app, sample_user):
    """A search with no matching films should return an empty list, not an error."""
    with app.app_context():
        film = Film(title="Paddington 2", year=2017)
        db.session.add(film)
        db.session.commit()

        add_to_watchlist(user_id=sample_user, film_id=film.id)

        results = get_watchlist(sample_user, search="nonexistent title")
        assert results == []