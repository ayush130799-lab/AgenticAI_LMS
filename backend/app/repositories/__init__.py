# Query logic for this project lives directly in app/services/*.py (each
# service owns its own SQLAlchemy queries against the async session). A
# separate repository layer was deliberately skipped to avoid an indirection
# that added no value at this project's size — services already isolate the
# database from the API layer. This package is kept so the structure matches
# the documented architecture and is a natural place to extract repositories
# into if/when multiple services need to share complex queries.
