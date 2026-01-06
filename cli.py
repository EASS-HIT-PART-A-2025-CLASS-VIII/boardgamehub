import typer
from sqlmodel import SQLModel, Session, select

from app.database import engine, create_db_and_tables
from app.models import BoardGame

app = typer.Typer(help="BoardGameHub CLI (seed/reset/export)")

SAMPLE_GAMES = [
    ("Catan", "Klaus Teuber", 1995, 2, 4, 60, 2.0, 7.0),
    ("Carcassonne", "Klaus-Jürgen Wrede", 2000, 2, 5, 45, 1.9, 7.4),
    ("Terraforming Mars", "Jacob Fryxelius", 2016, 1, 5, 120, 3.3, 8.2),
    ("7 Wonders", "Antoine Bauza", 2010, 2, 7, 30, 2.3, 7.7),
    ("Azul", "Michael Kiesling", 2017, 2, 4, 40, 1.8, 7.8),
]


@app.command()
def reset(yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")) -> None:
    """Drop + recreate tables (DANGEROUS for persistent DB)."""
    if not yes:
        ok = typer.confirm("This will DELETE all data. Continue?")
        if not ok:
            typer.echo("Cancelled.")
            raise typer.Exit(code=0)

    # ודא שהמודלים נטענו ל-metadata
    from app import models  # noqa: F401

    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    typer.echo("✅ Database reset complete.")


@app.command()
def seed(sample: int = typer.Option(5, "--sample", "-s", min=1, max=50)) -> None:
    """Seed sample board games (idempotent-ish: skips if DB already has data)."""
    create_db_and_tables()

    with Session(engine) as session:
        existing = session.exec(select(BoardGame)).first()
        if existing:
            typer.echo("ℹ️ Database already has data. Skipping seed.")
            raise typer.Exit(code=0)

        for row in SAMPLE_GAMES[:sample]:
            name, designer, year, min_p, max_p, play_min, complexity, rating = row
            session.add(
                BoardGame(
                    name=name,
                    designer=designer,
                    year_published=year,
                    min_players=min_p,
                    max_players=max_p,
                    play_time_min=play_min,
                    complexity=complexity,
                    rating=rating,
                )
            )
        session.commit()

    typer.echo(f"✅ Seeded {min(sample, len(SAMPLE_GAMES))} games.")


@app.command()
def export() -> None:
    """Print all games to the console."""
    create_db_and_tables()
    with Session(engine) as session:
        games = session.exec(select(BoardGame)).all()
        if not games:
            typer.echo("No games found.")
            raise typer.Exit(code=0)

        for g in games:
            typer.echo(f"{g.id}: {g.name} | {g.designer} | rating={g.rating}")


if __name__ == "__main__":
    app()
