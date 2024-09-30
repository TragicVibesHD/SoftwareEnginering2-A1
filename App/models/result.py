from App.database import db

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_username = db.Column(db.String(80), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)

    def __init__(self, student_username, competition_id, score):
        self.student_username = student_username
        self.competition_id = competition_id
        self.score = score

    def to_dict(self):
        return {
            'id': self.id,
            'student_username': self.student_username,
            'competition_id': self.competition_id,
            'score': self.score
        }
