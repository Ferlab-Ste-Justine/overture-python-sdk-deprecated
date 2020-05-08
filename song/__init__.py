"""
Package to abstract away SONG API calls
"""

import logging
import requests

from song.original_song_cli.entities import Study, Donor, Specimen, Sample, File, SequencingRead

from song.original_song_cli.tools import SimplePayloadBuilder
from song.original_song_cli.client import Api, StudyClient, ManifestClient
from song.original_song_cli.model import ApiConfig

def _get_logger():
    return logging.getLogger(__name__)

# pylint: disable=R0913
class SongClient:
    """
    Class to abstract away client calls to SONG.

    The constructor takes the following parameters:
    base_url: Uri if your SONG which is prepended to each url (ex: https://song)
    token: Auth token to use when making SONG requests
    verify_certificate: Whether the tls certificate should be validated to ensure it was
    signed by a valid CA
    """
    schemas_url = '{base_url}/schemas'
    studies_list_url = '{base_url}/studies/all'
    submit_url = '{base_url}/submit/{studyId}'
    analyses_url = '{base_url}/studies/{studyId}/analysis?analysisStates={publication_status}'

    def __init__(self, base_url, token, verify_certificate=True):
        self.base_url = base_url
        self.token = token
        self.verify_certificate = verify_certificate

    def create_study(
            self,
            study_id,
            name,
            description,
            organization
    ):
        """
        Create a new study
        """
        api = Api(
            ApiConfig(self.base_url, study_id, self.token, debug=True)
        )
        study_client = StudyClient(api)
        study_client.create(
            Study.create(
                study_id,
                name,
                description,
                organization
            )
        )

    def create_analysis(
            self,
            study_id,
            donor,
            specimen,
            sample,
            files,
            experiment
    ):
        """
        Create a new analysis using the two pre-existing analysis SONG supports

        Takes types defined in the legacy SONG client.

        This method will probably be deprecated in the future.
        """
        logger = _get_logger()
        api = Api(
            ApiConfig(self.base_url, study_id, self.token, debug=True)
        )

        donor.studyId = study_id
        for file in files:
            file.studyId = study_id

        builder = SimplePayloadBuilder(donor, specimen, sample, files, experiment, study_id)
        payload = builder.to_dict()
        logger.debug("Analysis creation payload: %s", payload)

        upload_response = api.upload(json_payload=payload, is_async_validation=False)
        logger.debug("upload response: %s", upload_response)
        return upload_response

    def create_custom_analysis(
            self,
            study_id,
            payload
    ):
        """
        Create a new analysis with a custom analysis format you defined
        """
        logger = _get_logger()
        logger.debug("Analysis creation payload: %s", payload)
        res = requests.post(
            self.submit_url.format(base_url=self.base_url, studyId=study_id),
            data=payload,
            verify=self.verify_certificate,
            headers={
                'Authorization': 'Bearer {token}'.format(token=self.token),
                'Content-Type': 'application/json'
            }
        )
        logger.debug('upload status code: %s', res.status_code)
        logger.debug('upload response: %s', res.content)
        assert res.status_code == 200
        return res.json()

    def get_analysis_manifest(
            self,
            study_id,
            analysis_id,
            source_dir
    ):
        """
        Get a manifest string for a given analysis
        """
        return ManifestClient(
            Api(
                ApiConfig(self.base_url, study_id, self.token, debug=True)
            )
        ).create_manifest(source_dir, analysis_id)

    def publish_analysis(
            self,
            study_id,
            analysis_id
    ):
        """
        Publish a yet to be published analysis
        """
        return Api(
            ApiConfig(self.base_url, study_id, self.token, debug=True)
        ).publish(analysis_id)

    def get_schemas(self):
        """
        Get the list of analysis schemas that are defined (the two pre-existing ones plus
        any custom ones you defined)
        """
        return Api(
            ApiConfig(self.base_url, None, self.token, debug=True)
        ).list_schemas()

    def create_schema(self, schema):
        """
        Create a new analysis type in SONG
        """
        logger = _get_logger()
        logger.debug("Schema creation payload: %s", schema)
        res = requests.post(
            self.schemas_url.format(base_url=self.base_url),
            data=schema,
            verify=self.verify_certificate,
            headers={
                'Authorization': 'Bearer {token}'.format(token=self.token),
                'Content-Type': 'application/json'
            }
        )
        logger.debug('schema creation status code: %s', res.status_code)
        logger.debug('schema creation response: %s', res.content)
        assert res.status_code == 200

    def get_studies_list(self):
        """
        Get a list of studies currently in SONG
        """
        logger = _get_logger()
        res = requests.get(
            self.studies_list_url.format(base_url=self.base_url),
            verify=self.verify_certificate,
            headers={
                'Authorization': 'Bearer {token}'.format(token=self.token)
            }
        )
        logger.debug('Get studies list status code: %s', res.status_code)
        assert res.status_code == 200
        return res.json()

    def get_analyses(
            self,
            study_id,
            publication_status
    ):
        """
        Get the existing analyses for a given study in SONG
        """
        logger = _get_logger()
        res = requests.get(
            self.analyses_url.format(
                base_url=self.base_url,
                studyId=study_id,
                publication_status=publication_status
            ),
            verify=self.verify_certificate,
            headers={
                'Authorization': 'Bearer {token}'.format(token=self.token)
            }
        )
        logger.debug('Get analyses status code: %s', res.status_code)
        assert res.status_code == 200
        return res.json()
