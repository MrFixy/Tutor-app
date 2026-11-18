import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import content_loader, models, study_plan
from app.db import Base


@pytest.fixture
def phase_db(tmp_path, monkeypatch):
    catalog = [
        {"slug": "00-setup-and-tooling", "number": 0, "title": "Setup and Tooling", "lessons": []},
        {"slug": "01-math-foundations", "number": 1, "title": "Math Foundations", "lessons": []},
        {"slug": "02-ml-fundamentals", "number": 2, "title": "ML Fundamentals", "lessons": []},
        {"slug": "03-deep-learning-core", "number": 3, "title": "Deep Learning Core", "lessons": []},
    ]
    catalog_file = tmp_path / "curriculum.json"
    catalog_file.write_text(json.dumps(catalog), encoding="utf-8")
    monkeypatch.setattr(content_loader, "CURRICULUM_FILE", catalog_file)

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()
    yield db
    db.close()


@pytest.mark.asyncio
async def test_goal_roadmap_uses_only_existing_ai_engineering_phases(phase_db, monkeypatch):
    async def fake_generate_json(*args, **kwargs):
        return {"topics": [
            {"phase_slug": "01-math-foundations"},
            {"phase_slug": "02-ml-fundamentals"},
            {"phase_slug": "03-deep-learning-core"},
        ]}

    monkeypatch.setattr(study_plan, "generate_json", fake_generate_json)
    result = await study_plan.generate_topic_list(phase_db, "I want to learn deep learning")

    assert [item.phase_slug for item in result.topics] == [
        "01-math-foundations", "02-ml-fundamentals", "03-deep-learning-core"
    ]
    assert result.topics[-1].title == "Deep Learning Core"


def test_plan_round_trip_persists_only_phase_items(phase_db):
    user = models.User(id=17, username="learner")
    phase_db.add(user)
    phase_db.commit()

    topics = study_plan._validate_topics({"topics": [
        {"phase_slug": "00-setup-and-tooling"},
        {"phase_slug": "01-math-foundations"},
        {"phase_slug": "02-ml-fundamentals"},
    ]})
    created = study_plan.create_plan(phase_db, 17, "Learn AI Engineering", topics.topics)
    listed = study_plan.list_plans(phase_db, 17)

    assert created.id == listed[0].id
    assert [item.phase_slug for item in listed[0].items] == [
        "00-setup-and-tooling", "01-math-foundations", "02-ml-fundamentals"
    ]
    assert all(item.title for item in listed[0].items)
