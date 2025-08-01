import pytest
from app import create_app
from app.utils.extensions import db

@pytest.fixture(scope='session')
def app():
    """Create a new app instance for each test session."""
    app = create_app('development')  # Menggunakan konfigurasi development untuk tes
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # Gunakan database in-memory
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture()
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """
    Yields a database session for a single test function.
    Rolls back any changes after the test is complete.
    """
    connection = db.engine.connect()
    transaction = connection.begin()

    # bind an individual session to the connection
    # The method is private in Flask-SQLAlchemy 3.x, but it's what's needed here.
    session = db._make_scoped_session(options={'bind': connection})

    db.session = session

    yield session

    session.remove()
    transaction.rollback()
    connection.close()
