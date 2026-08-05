import os
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from us_visa.entity.s3_estimator import USvisaEstimator


def test_load_model_uses_local_artifact_when_s3_credentials_are_missing(monkeypatch):
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)

    estimator = USvisaEstimator(bucket_name="dummy-bucket", model_path="model.pkl")
    model = estimator.load_model()

    assert model is not None
    assert hasattr(model, "predict")
