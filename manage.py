from flask_migrate import Migrate, MigrateCommand
from ext import db
from flask_script import Manager
from app import createApp
from database.models.Labels import Labels

app = createApp()
manager = Manager(app)
Migrate(app, db)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
