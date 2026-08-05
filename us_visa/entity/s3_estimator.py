import glob
import os
import sys

from pandas import DataFrame

from us_visa.cloud_storage.aws_storage import SimpleStorageService
from us_visa.entity.estimator import USvisaModel
from us_visa.exception import USvisaException
from us_visa.logger import logging
from us_visa.utils.main_utils import load_object


class USvisaEstimator:
    """
    This class is used to save and retrieve us_visas model in S3 bucket and to do prediction.
    When S3 credentials are unavailable, it falls back to a locally saved model artifact.
    """

    def __init__(self, bucket_name, model_path):
        """
        :param bucket_name: Name of your model bucket
        :param model_path: Location of your model in bucket
        """
        self.bucket_name = bucket_name
        self.s3 = SimpleStorageService()
        self.model_path = model_path
        self.loaded_model: USvisaModel = None

    def _resolve_local_model_path(self) -> str | None:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

        candidate_paths = []
        if os.path.exists(self.model_path):
            candidate_paths.append(self.model_path)

        candidate_paths.extend(
            glob.glob(os.path.join(project_root, "artifact", "**", "model_trainer", "trained_model", "model.pkl"), recursive=True)
        )
        candidate_paths.extend(
            glob.glob(os.path.join(project_root, "**", "model_trainer", "trained_model", "model.pkl"), recursive=True)
        )
        candidate_paths.extend(
            glob.glob(os.path.join(project_root, "model.pkl"), recursive=False)
        )

        unique_candidates = [path for path in dict.fromkeys(candidate_paths) if os.path.exists(path)]
        if not unique_candidates:
            return None

        return max(unique_candidates, key=lambda path: os.path.getmtime(path))

    def is_model_present(self, model_path):
        try:
            return self.s3.s3_key_path_available(bucket_name=self.bucket_name, s3_key=model_path)
        except Exception:
            return self._resolve_local_model_path() is not None

    def load_model(self) -> USvisaModel:
        """
        Load the model from the model_path or fall back to a local model artifact.
        :return:
        """
        if self.loaded_model is not None:
            return self.loaded_model

        try:
            if self.s3 is None or getattr(self.s3, "s3_resource", None) is None or getattr(self.s3, "s3_client", None) is None:
                raise Exception("AWS S3 client is not available")
            self.loaded_model = self.s3.load_model(self.model_path, bucket_name=self.bucket_name)
            return self.loaded_model
        except Exception as e:
            local_model_path = self._resolve_local_model_path()
            if local_model_path is not None:
                logging.info(f"Falling back to local model artifact: {local_model_path}")
                self.loaded_model = load_object(local_model_path)
                return self.loaded_model
            raise USvisaException(e, sys) from e

    def save_model(self,from_file,remove:bool=False)->None:
        """
        Save the model to the model_path
        :param from_file: Your local system model path
        :param remove: By default it is false that mean you will have your model locally available in your system folder
        :return:
        """
        try:
            self.s3.upload_file(from_file,
                                to_filename=self.model_path,
                                bucket_name=self.bucket_name,
                                remove=remove
                                )
        except Exception as e:
            raise USvisaException(e, sys)


    def predict(self,dataframe:DataFrame):
        """
        :param dataframe:
        :return:
        """
        try:
            if self.loaded_model is None:
                self.loaded_model = self.load_model()
            return self.loaded_model.predict(dataframe=dataframe)
        except Exception as e:
            raise USvisaException(e, sys)