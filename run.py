import click
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User

app = create_app()

@app.cli.command("create-admin")
@click.option("--email", prompt="Admin email", help="The email for the admin account.")
@click.option("--password", prompt="Admin password", hide_input=True, confirmation_prompt=True,
              help="The password for the admin account.")
def create_admin(email, password):
    """Create an admin user."""
    if User.query.filter_by(email=email).first():
        click.echo("Admin user already exists!")
        return

    hashed_password = generate_password_hash(password)
    admin_user = User(email=email, password=hashed_password, is_admin=True)
    db.session.add(admin_user)
    db.session.commit()
    click.echo(f"Admin user {email} created successfully!")


if __name__ == "__main__":
    app.run(debug=True)
