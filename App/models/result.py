from App.database import db

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    rank = db.Column(db.Integer, nullable=False)

    def __init__(self, student_id, competition_id, score, rank):
        self.student_id = student_id
        self.competition_id = competition_id
        self.score = score
        self.rank = rank

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'competition_id': self.competition_id,
            'score': self.score,
            'rank': self.rank
        }
