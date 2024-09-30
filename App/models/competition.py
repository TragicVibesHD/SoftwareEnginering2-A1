from App.database import db

class Competition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)

    results = db.relationship('Result', backref='competition', lazy=True)

    def __init__(self, name, date, description=None):
        self.name = name
        self.date = date
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date.isoformat(),
            'description': self.description
        }


